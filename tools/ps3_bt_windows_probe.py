"""Read Barrot identity through the original Windows Bluetooth driver.

No driver changes, address writes, pairing or console connections. Requires an
administrator terminal because Microsoft's vendor IOCTL requires SeLoadDriverPrivilege.
The worker process has a 12-second deadline, including all native calls.

References: Microsoft's IOCTL_BTH_HCI_VENDOR_COMMAND / BTH_VENDOR_SPECIFIC_COMMAND
documentation, and tryger/barrot-tools doc/hci_vsc/Communication.md.
"""

from __future__ import annotations

import ctypes as ct
from contextlib import contextmanager
import os
from pathlib import Path
import struct
import subprocess
import sys
import uuid

from ps3_bt_probe import BARROT, BARROT_OPCODE, ProbeError, mac, parse_complete, windows_dongle_status


class Address(ct.Union):
    _fields_ = [('value', ct.c_uint64), ('octets', ct.c_ubyte * 6)]


class RadioInfo(ct.Structure):
    _fields_ = [('size', ct.c_uint32), ('address', Address),
                ('name', ct.c_wchar * 248), ('class_of_device', ct.c_uint32),
                ('lmp_subversion', ct.c_uint16), ('manufacturer', ct.c_uint16)]


def vendor_read_packet(command):
    """Packed BTH_VENDOR_SPECIFIC_COMMAND; only identity/address reads allowed."""
    if command not in (1, 5):
        raise ProbeError('Only Barrot chip-version and address reads are allowed')
    payload = struct.pack('<H', command)
    return struct.pack('<IBBHB', BARROT, 0, 0, BARROT_OPCODE, len(payload)) + payload


def vendor_address_packet(address_le):
    """Barrot BD_PARAM modifies RAM only; callers must restore the old address."""
    address_le = bytes(address_le)
    mac(address_le[::-1])
    payload = struct.pack('<H', 5) + address_le
    return struct.pack('<IBBHB', BARROT, 0, 0, BARROT_OPCODE, len(payload)) + payload


def vendor_hci_reset_packet():
    """Exact Barrot HCI reset (type 4); no hardware/ROM/software reset selector."""
    payload = struct.pack('<HB', 0, 4)
    return struct.pack('<IBBHB', BARROT, 0, 0, BARROT_OPCODE, len(payload)) + payload


def native_event(raw, local_address):
    """Accept a raw HCI event or the documented BTH_VENDOR_EVENT_INFO wrapper."""
    raw = bytes(raw)
    if len(raw) >= 2 and raw[0] == 0x0E and len(raw) == raw[1] + 2:
        event = raw
    elif len(raw) >= 14:
        address, size = struct.unpack_from('<QI', raw)
        if address != local_address or len(raw) != 12 + size:
            raise ProbeError('Unrecognized Windows vendor-event wrapper')
        event = raw[12:]
    else:
        raise ProbeError('Unrecognized Windows vendor-event layout')
    return event


def standard_address_packet():
    """Standard HCI Read_BD_ADDR 0x1009; no command parameters."""
    return struct.pack('<IBBHB', BARROT, 0, 0, 0x1009, 0)


def standard_address_reply(raw, local_address):
    body = parse_complete(native_event(raw, local_address), 0x1009)
    if body is None or len(body) != 6:
        raise ProbeError('Standard HCI address response must contain exactly six bytes')
    mac(body[::-1])
    return body


def vendor_reply(raw, command, local_address):
    body = parse_complete(native_event(raw, local_address), BARROT_OPCODE)
    if body is None or len(body) < 2 or int.from_bytes(body[:2], 'little') != command:
        raise ProbeError('Vendor event does not match the requested Barrot read')
    return body[2:]


def radio_path(instance):
    from ctypes import wintypes as wt

    cfg = ct.WinDLL('cfgmgr32')
    guid = (ct.c_ubyte * 16).from_buffer_copy(
        uuid.UUID('0850302a-b344-4fda-9be9-90576b8d46f0').bytes_le)
    cfg.CM_Get_Device_Interface_List_SizeW.argtypes = [
        ct.POINTER(wt.ULONG), ct.c_void_p, wt.LPCWSTR, wt.ULONG]
    cfg.CM_Get_Device_Interface_List_SizeW.restype = wt.ULONG
    cfg.CM_Get_Device_Interface_ListW.argtypes = [
        ct.c_void_p, wt.LPCWSTR, wt.LPWSTR, wt.ULONG, wt.ULONG]
    cfg.CM_Get_Device_Interface_ListW.restype = wt.ULONG
    count = wt.ULONG()
    rc = cfg.CM_Get_Device_Interface_List_SizeW(ct.byref(count), ct.byref(guid), instance, 0)
    if rc or count.value < 2:
        raise ProbeError(f'No Windows Bluetooth interface for this dongle (CM status {rc})')
    paths = ct.create_unicode_buffer(count.value)
    rc = cfg.CM_Get_Device_Interface_ListW(ct.byref(guid), instance, paths, count.value, 0)
    if rc:
        raise ProbeError(f'Cannot list Windows Bluetooth interfaces (CM status {rc})')
    found = [p for p in paths[:].split('\0') if p]
    if len(found) != 1:
        raise ProbeError(f'Expected one Windows radio interface; found {len(found)}')
    return found[0]


@contextmanager
def radio_session(*, allow_address_change=False, allow_hci_reset=False):
    if os.name != 'nt':
        raise ProbeError('This probe requires Windows')
    from ctypes import wintypes as wt

    devices = windows_dongle_status()
    if devices is None or len(devices) != 1:
        raise ProbeError('Cannot identify exactly one connected external 0A12:0001 dongle')
    device = devices[0]
    if device['problem'] or device['service'].lower() != 'bthusb':
        raise ProbeError(f"Restore Microsoft's Bluetooth driver first: current service "
                         f"{device['service']}, Device Manager Code {device['problem']}")

    kernel = ct.WinDLL('kernel32', use_last_error=True)
    advapi = ct.WinDLL('advapi32', use_last_error=True)
    bluetooth = ct.WinDLL('bthprops.cpl')

    class Luid(ct.Structure):
        _fields_ = [('low', wt.DWORD), ('high', wt.LONG)]

    class Privilege(ct.Structure):
        _fields_ = [('count', wt.DWORD), ('luid', Luid), ('attributes', wt.DWORD)]

    kernel.CreateFileW.argtypes = [wt.LPCWSTR, wt.DWORD, wt.DWORD, ct.c_void_p,
                                   wt.DWORD, wt.DWORD, wt.HANDLE]
    kernel.CreateFileW.restype = wt.HANDLE
    kernel.CloseHandle.argtypes = [wt.HANDLE]
    kernel.CloseHandle.restype = wt.BOOL
    kernel.GetCurrentProcess.restype = wt.HANDLE
    kernel.DeviceIoControl.argtypes = [wt.HANDLE, wt.DWORD, ct.c_void_p, wt.DWORD,
                                      ct.c_void_p, wt.DWORD, ct.POINTER(wt.DWORD), ct.c_void_p]
    kernel.DeviceIoControl.restype = wt.BOOL
    bluetooth.BluetoothGetRadioInfo.argtypes = [wt.HANDLE, ct.POINTER(RadioInfo)]
    bluetooth.BluetoothGetRadioInfo.restype = wt.DWORD
    advapi.OpenProcessToken.argtypes = [wt.HANDLE, wt.DWORD, ct.POINTER(wt.HANDLE)]
    advapi.OpenProcessToken.restype = wt.BOOL
    advapi.LookupPrivilegeValueW.argtypes = [wt.LPCWSTR, wt.LPCWSTR, ct.POINTER(Luid)]
    advapi.LookupPrivilegeValueW.restype = wt.BOOL
    advapi.AdjustTokenPrivileges.argtypes = [wt.HANDLE, wt.BOOL, ct.POINTER(Privilege),
                                           wt.DWORD, ct.POINTER(Privilege), ct.POINTER(wt.DWORD)]
    advapi.AdjustTokenPrivileges.restype = wt.BOOL

    handle = None
    token = wt.HANDLE()
    previous = Privilege()
    previous_length = wt.DWORD()
    privilege_changed = False
    try:
        if not advapi.OpenProcessToken(kernel.GetCurrentProcess(), 0x28, ct.byref(token)):
            raise ct.WinError(ct.get_last_error())
        privilege = Privilege()
        privilege.count, privilege.attributes = 1, 2
        if not advapi.LookupPrivilegeValueW(None, 'SeLoadDriverPrivilege', ct.byref(privilege.luid)):
            raise ct.WinError(ct.get_last_error())
        ct.set_last_error(0)
        success = advapi.AdjustTokenPrivileges(token, False, ct.byref(privilege),
                    ct.sizeof(previous), ct.byref(previous), ct.byref(previous_length))
        error = ct.get_last_error()
        if not success or error:
            raise ProbeError(f'Cannot enable vendor-query privilege (Windows error {error}); '
                             'run PowerShell as administrator')
        privilege_changed = True

        advapi.GetTokenInformation.argtypes = [wt.HANDLE, ct.c_int, ct.c_void_p, wt.DWORD, ct.POINTER(wt.DWORD)]
        advapi.GetTokenInformation.restype = wt.BOOL
        size = wt.DWORD()
        advapi.GetTokenInformation(token, 3, None, 0, ct.byref(size))
        data = ct.create_string_buffer(size.value)
        if not advapi.GetTokenInformation(token, 3, data, len(data), ct.byref(size)):
            raise ct.WinError(ct.get_last_error())
        count = struct.unpack_from('<I', data.raw)[0]
        entries = struct.iter_unpack('<IiI', data.raw[4:4 + count * 12])
        enabled = any(low == privilege.luid.low and high == privilege.luid.high and (attributes & 2)
                      for low, high, attributes in entries)
        print(f'SeLoadDriverPrivilege enabled: {enabled}', flush=True)
        if not enabled:
            raise ProbeError('Vendor-query privilege did not become effective')

        # Open after enabling the privilege, so captured handle security includes it.
        handle = kernel.CreateFileW(radio_path(device['instance']), 0xC0000000, 3, None, 3, 0, None)
        if handle == ct.c_void_p(-1).value:
            handle = None
            raise ct.WinError(ct.get_last_error())
        info = RadioInfo()
        info.size = ct.sizeof(info)
        rc = bluetooth.BluetoothGetRadioInfo(handle, ct.byref(info))
        if rc:
            raise ct.WinError(rc)
        print(f'Windows driver: BTHUSB; manufacturer: {info.manufacturer}', flush=True)
        print(f'Dongle Bluetooth address: {mac(bytes(info.address.octets)[::-1])}', flush=True)
        if info.manufacturer != BARROT:
            raise ProbeError('Unexpected manufacturer; no vendor command sent')

        def query(command, *, address=None, hci_reset=False):
            if hci_reset:
                if not allow_hci_reset or command != 0 or address is not None:
                    raise ProbeError('HCI reset is disabled or its arguments are invalid')
                packet = vendor_hci_reset_packet()
            elif address is None:
                packet = standard_address_packet() if command == 0x1009 else vendor_read_packet(command)
            else:
                if not allow_address_change or command != 5:
                    raise ProbeError('Address changes are disabled in this radio session')
                packet = vendor_address_packet(address)
            request = ct.create_string_buffer(packet)
            response = ct.create_string_buffer(512)
            returned = wt.DWORD()
            operation = 'HCI reset' if hci_reset else ('read' if address is None else 'RAM address write')
            print(f'Barrot command 0x{command:02X}: {operation}', flush=True)
            success = kernel.DeviceIoControl(handle, 0x410050, request, len(packet),
                    response, ct.sizeof(response), ct.byref(returned), None)
            ioctl_error = ct.get_last_error()
            raw = response.raw[:returned.value]
            print(f'Windows IOCTL result: {bool(success)}; RX: {raw.hex(" ")}', flush=True)
            if not success:
                raise ct.WinError(ioctl_error)
            if command == 0x1009:
                return standard_address_reply(raw, info.address.value)
            return vendor_reply(raw, command, info.address.value)

        yield info, query
    finally:
        if handle:
            kernel.CloseHandle(handle)
        if privilege_changed:
            advapi.AdjustTokenPrivileges(token, False, ct.byref(previous), 0, None, None)
        if token:
            kernel.CloseHandle(token)


def worker():
    with radio_session() as (info, query):
        for command in (1, 5):
            body = query(command)
            if command == 1:
                if len(body) < 26 or body[:3] != b'BRT':
                    raise ProbeError('Barrot chip-version format unrecognized')
                print(f'Barrot chip code: 0x{int.from_bytes(body[4:8], "little"):08X}', flush=True)
                if len(body) > 26:
                    print(f'Uninterpreted chip-info extension: {body[26:].hex(" ")}', flush=True)
            else:
                if body != bytes(info.address.octets):
                    raise ProbeError('Barrot and Windows Bluetooth addresses disagree')
                print(f'Barrot address query: {mac(body[::-1])}', flush=True)
        print('PROVEN: read-only Barrot queries work through the Windows driver.', flush=True)
        print('UNKNOWN: address changing and PS3 wake; neither was attempted.', flush=True)


def main():
    if len(sys.argv) == 2 and sys.argv[1] == '--worker':
        try:
            worker()
            return 0
        except (ProbeError, OSError) as exc:
            print(f'STOP: {exc}', file=sys.stderr, flush=True)
            return 1
    if len(sys.argv) != 1:
        print('Usage: python ps3_bt_windows_probe.py', file=sys.stderr)
        return 1
    try:
        result = subprocess.run([sys.executable, '-B', str(Path(__file__).resolve()), '--worker'],
                                timeout=12, check=False)
        return result.returncode
    except subprocess.TimeoutExpired:
        print('STOP: Windows query exceeded 12 seconds; its worker was stopped. '
              'No address writes or console connections were requested.', file=sys.stderr)
        return 1


if __name__ == '__main__':
    raise SystemExit(main())
