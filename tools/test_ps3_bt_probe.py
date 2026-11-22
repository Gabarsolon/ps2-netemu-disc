"""Protocol/error checks with synthetic HCI events; no hardware access."""

import struct
import unittest
from unittest.mock import Mock, patch
from types import SimpleNamespace

import ps3_bt_probe as probe


def complete(opcode, body=b'', status=0):
    payload = b'\x01' + struct.pack('<H', opcode) + bytes([status]) + body
    return bytes([0x0E, len(payload)]) + payload


class ProtocolTests(unittest.TestCase):
    def test_real_usb_pairing_reports_with_f5_payload_header_01(self):
        pair = probe.ds3_pairing(bytes.fromhex('f2 ff ff 00 04 76 6e 8b 47 e4 00 03 50 81 d8 01 8a'),
                                 bytes.fromhex('01 00 78 dd 08 8d 37 f4'))
        self.assertEqual(pair, {'controller_mac': '04:76:6E:8B:47:E4',
                                'console_mac': '78:DD:08:8D:37:F4'})

    def test_failed_driver_is_not_reported_as_unplugged(self):
        with patch.object(probe, 'windows_dongle_status', return_value=[
                {'instance': 'external', 'problem': 10, 'service': 'WinUSB'}]):
            with self.assertRaisesRegex(probe.ProbeError, 'driver WinUSB.*Code 10'):
                probe.check_windows_dongle()

    def test_absent_device_is_reported_separately(self):
        with patch.object(probe, 'windows_dongle_status', return_value=[]):
            with self.assertRaisesRegex(probe.ProbeError, 'does not see a connected'):
                probe.check_windows_dongle()

    def test_healthy_libusbk_is_allowed_and_stock_bluetooth_is_blocked(self):
        for service in ('WinUSB', 'libusbK', 'BTHUSB'):
            with self.subTest(service=service), patch.object(probe, 'windows_dongle_status',
                    return_value=[{'instance': 'external', 'problem': 0, 'service': service}]):
                if service == 'BTHUSB':
                    with self.assertRaisesRegex(probe.ProbeError, 'BTHUSB'):
                        probe.check_windows_dongle()
                else:
                    probe.check_windows_dongle()

    def test_sco_audio_interface_is_not_confused_with_hci(self):
        class Interface(list):
            bAlternateSetting = 0
            bInterfaceClass, bInterfaceSubClass, bInterfaceProtocol = 0xE0, 1, 1

        event = SimpleNamespace(bmAttributes=3, bEndpointAddress=0x81)
        hci = Interface([event, SimpleNamespace(bmAttributes=2, bEndpointAddress=0x04),
                         SimpleNamespace(bmAttributes=2, bEndpointAddress=0x82)])
        hci.bInterfaceNumber = 0
        audio = Interface([SimpleNamespace(bmAttributes=1, bEndpointAddress=0x05),
                           SimpleNamespace(bmAttributes=1, bEndpointAddress=0x83)])
        audio.bInterfaceNumber = 1
        self.assertEqual(probe.hci_interface([hci, audio]), (hci, event))

    def test_no_hci_event_endpoint_is_rejected(self):
        with self.assertRaises(probe.ProbeError):
            probe.hci_interface([])

    def test_standard_identity_response(self):
        version = bytes.fromhex('0a 01 00 0a e7 08 87 00')
        self.assertEqual(probe.parse_complete(complete(0x1001, version), 0x1001), version)

    def test_barrot_reply_has_status_then_subcommand_then_address(self):
        response = bytes.fromhex('05 00 80 e5 0c 0e 7f 04')
        self.assertEqual(probe.parse_complete(complete(0xFC80, response), 0xFC80), response)

    def test_unsupported_vendor_command_is_failure(self):
        with self.assertRaisesRegex(probe.ProbeError, 'status 0x01'):
            probe.parse_complete(complete(0xFC80, status=1), 0xFC80)

    def test_command_accepted_is_not_command_completed(self):
        self.assertIsNone(probe.parse_complete(bytes.fromhex('0f 04 00 01 80 fc'), 0xFC80))
        with self.assertRaisesRegex(probe.ProbeError, 'rejected'):
            probe.parse_complete(bytes.fromhex('0f 04 0c 01 80 fc'), 0xFC80)

    def test_unrelated_event_does_not_complete_query(self):
        self.assertIsNone(probe.parse_complete(complete(0x1009, bytes(6)), 0x1001))

    def test_truncated_event_rejected(self):
        with self.assertRaises(probe.ProbeError):
            probe.parse_complete(complete(0x1001)[:-1], 0x1001)

    def test_address_writer_and_reset_are_blocked_before_usb_access(self):
        reader = probe.HciReader.__new__(probe.HciReader)
        reader.dev = Mock()
        for opcode, parameters in ((0xFC80, bytes.fromhex('05 00 80 e5 0c 0e 7f 04')),
                                   (0x0C03, b''), (0x0405, bytes(13))):
            with self.assertRaisesRegex(probe.ProbeError, 'only permits identity reads'):
                reader.query(opcode, parameters)
        reader.dev.ctrl_transfer.assert_not_called()

    def test_usb_write_does_not_suffice_without_event_reply(self):
        reader = probe.HciReader.__new__(probe.HciReader)
        reader.dev = Mock()
        reader.dev.ctrl_transfer.return_value = 3
        reader.usb = Mock()
        reader.usb.USBTimeoutError = TimeoutError
        reader.events = Mock()
        reader.events.read.side_effect = TimeoutError()
        with self.assertRaisesRegex(probe.ProbeError, 'No reply'):
            reader.query(probe.READ_VERSION)

    def test_invalid_pairing_addresses_rejected(self):
        for raw in (b'', bytes(6), bytes([255]) * 6):
            with self.assertRaises(probe.ProbeError):
                probe.mac(raw)


    def test_linux_usb_claim_restores_previous_kernel_binding(self):
        import usb.core
        import usb.util
        dev = Mock()
        dev.is_kernel_driver_active.return_value = True
        with patch.object(probe, 'check_windows_dongle'), \
             patch.object(probe.sys, 'platform', 'linux'), \
             patch.object(usb.core, 'find', return_value=[dev]), \
             patch.object(probe, 'hci_interface', return_value=(SimpleNamespace(bInterfaceNumber=0), Mock())), \
             patch.object(usb.util, 'claim_interface') as claim, \
             patch.object(usb.util, 'release_interface') as release, \
             patch.object(usb.util, 'dispose_resources'):
            reader = probe.HciReader()
            dev.detach_kernel_driver.assert_called_once_with(0)
            claim.assert_called_once_with(dev, 0)
            reader.close()
            release.assert_called_once_with(dev, 0)
            dev.attach_kernel_driver.assert_called_once_with(0)

    def test_failed_linux_claim_reattaches_kernel_driver(self):
        import usb.core
        import usb.util
        dev = Mock()
        dev.is_kernel_driver_active.return_value = True
        with patch.object(probe, 'check_windows_dongle'), \
             patch.object(probe.sys, 'platform', 'linux'), \
             patch.object(usb.core, 'find', return_value=[dev]), \
             patch.object(probe, 'hci_interface', return_value=(SimpleNamespace(bInterfaceNumber=0), Mock())), \
             patch.object(usb.util, 'claim_interface', side_effect=OSError('claim failed')), \
             patch.object(usb.util, 'dispose_resources'):
            with self.assertRaisesRegex(probe.ProbeError, 'claim failed'):
                probe.HciReader()
            dev.attach_kernel_driver.assert_called_once_with(0)


if __name__ == '__main__':
    unittest.main()
