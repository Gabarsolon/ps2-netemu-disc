"""Native Windows packet checks; no Windows calls, hardware or subprocesses."""

import struct
import unittest

import ps3_bt_windows_probe as native
from ps3_bt_probe import ProbeError


def event(command, body=b'', status=0):
    payload = struct.pack('<BHBH', 1, 0xFC80, status, command) + body
    return bytes([0x0E, len(payload)]) + payload


class NativeProtocolTests(unittest.TestCase):
    def test_real_br8051a01_reply_retains_uninterpreted_extension(self):
        raw = bytes.fromhex('0e 22 01 80 fc 00 01 00 42 52 54 01 01 1a 05 08 '
                            'd8 a6 6a 7d 02 00 00 00 00 00 00 00 00 00 00 00 12 85 00 00')
        body = native.vendor_reply(raw, 1, 0)
        self.assertEqual(body[:3], b'BRT')
        self.assertEqual(int.from_bytes(body[4:8], 'little'), 0x08051A01)
        self.assertEqual(body[26:], b'\0\0')

    def test_vendor_request_matches_sdk_packed_structure(self):
        self.assertEqual(native.vendor_read_packet(5), bytes.fromhex('e7 08 00 00 00 00 80 fc 02 05 00'))

    def test_no_writing_commands_can_be_constructed(self):
        for command in (0, 2, 6, 9, 0x10, 0x11):
            with self.assertRaises(ProbeError):
                native.vendor_read_packet(command)

    def test_raw_event_decodes_and_matches_subcommand(self):
        address = bytes.fromhex('80 e5 0c 0e 7f 04')
        self.assertEqual(native.vendor_reply(event(5, address), 5, 0), address)
        with self.assertRaises(ProbeError):
            native.vendor_reply(event(1, address), 5, 0)

    def test_documented_event_wrapper_checks_radio_identity_and_size(self):
        raw = event(5, b'123456')
        wrapped = struct.pack('<QI', 123, len(raw)) + raw
        self.assertEqual(native.vendor_reply(wrapped, 5, 123), b'123456')
        with self.assertRaises(ProbeError):
            native.vendor_reply(wrapped, 5, 124)
        with self.assertRaises(ProbeError):
            native.vendor_reply(wrapped[:-1], 5, 123)

    def test_unsupported_command_stays_a_failure(self):
        with self.assertRaisesRegex(ProbeError, 'status 0x01'):
            native.vendor_reply(event(1, status=1), 1, 0)

    def test_unknown_layout_is_not_assumed_to_be_a_response(self):
        with self.assertRaises(ProbeError):
            native.vendor_reply(b'OK', 1, 0)


    def test_standard_address_read_has_no_vendor_subcommand(self):
        self.assertEqual(native.standard_address_packet().hex(), 'e70800000000091000')
        raw = bytes.fromhex('0e 0a 01 09 10 00 80 e5 0c 0e 7f 04')
        self.assertEqual(native.standard_address_reply(raw, 0), bytes.fromhex('80e50c0e7f04'))

    def test_standard_address_read_rejects_vendor_event_and_invalid_addresses(self):
        with self.assertRaises(ProbeError):
            native.standard_address_reply(event(5, bytes.fromhex('80e50c0e7f04')), 0)
        for addr in ('000000000000', 'ffffffffffff', '80e50c0e7f'):
            raw = bytes.fromhex('01091000' + addr)
            raw = bytes([0x0E, len(raw)]) + raw
            with self.assertRaises(ProbeError):
                native.standard_address_reply(raw, 0)


if __name__ == '__main__':
    unittest.main()
