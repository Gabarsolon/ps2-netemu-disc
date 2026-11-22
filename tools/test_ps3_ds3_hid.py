"""Offline packet/state checks; never opens an adapter or contacts a console."""

import unittest

from ps3_ds3_hid import DS3Hid


class DS3HidTests(unittest.TestCase):
    def test_input_press_release(self):
        hid = DS3Hid()
        neutral = hid.input_report()
        pressed = hid.input_report(ps_pressed=True)
        self.assertEqual(len(neutral), 50)
        self.assertEqual(neutral[:2], bytes((0xA1, 1)))
        self.assertEqual(neutral[7:11], bytes((128,) * 4))
        self.assertEqual(neutral[42:], bytes((2, 0, 2, 0, 1, 0x90, 2, 0)))
        self.assertEqual([i for i in range(50) if neutral[i] != pressed[i]], [5])
        self.assertEqual(pressed[5], 1)
        self.assertEqual(hid.input_report(), neutral)

    def test_get_reports(self):
        hid = DS3Hid()
        self.assertEqual(hid.handle_control(bytes((0x41, 1))), hid.input_report())
        self.assertEqual(hid.handle_control(bytes((0x49, 1, 64, 0))), hid.input_report())
        for report_id, expected_length in ((1, 50), (0xEF, 50), (0xF7, 13), (0xF8, 6)):
            with self.subTest(report_id=report_id):
                reply = hid.handle_control(bytes((0x43, report_id)))
                self.assertEqual(reply[:2], bytes((0xA3, report_id)))
                self.assertEqual(len(reply), expected_length)
        self.assertEqual(hid.handle_control(bytes((0x43, 0xF2))), b"\x02")
        self.assertEqual(hid.handle_control(bytes((0x43, 0xF5))), b"\x02")

    def test_captures_are_read_only(self):
        f2, f5 = bytes((0xF2, 10, 20)), bytes((0xF5, 30, 40))
        hid = DS3Hid(captured_f2=f2, captured_f5=f5)
        for report in (f2, f5):
            self.assertEqual(hid.handle_control(bytes((0x43, report[0]))), b"\xa3" + report)
            self.assertEqual(hid.handle_control(bytes((0x53,)) + report), b"\x02")
            self.assertEqual(hid.handle_control(bytes((0x43, report[0]))), b"\xa3" + report)
        for bad in (b"", b"\xf2", b"\xa3\xf2\x00"):
            with self.assertRaises(ValueError):
                DS3Hid(captured_f2=bad)

    def test_f4_enable_shutdown_and_short_rejection(self):
        hid = DS3Hid()
        self.assertFalse(hid.reporting_enabled)
        self.assertFalse(hid.shutdown_requested)
        self.assertEqual(hid.handle_control(bytes((0x53, 0xF4, 0x42))), b"\x04")
        self.assertFalse(hid.reporting_enabled)
        self.assertEqual(hid.handle_control(bytes((0x53, 0xF4, 0x42, 3, 0, 0))), b"\x00")
        self.assertTrue(hid.reporting_enabled)
        self.assertEqual(hid.handle_control(bytes((0xA3, 0xF4, 0x42, 8, 0, 0))), b"\x00")
        self.assertTrue(hid.shutdown_requested)
        self.assertFalse(hid.reporting_enabled)
        hid.handle_control(bytes((0x53, 0xF4, 0x42, 3)))
        self.assertFalse(hid.reporting_enabled)

    def test_output_and_ef(self):
        hid = DS3Hid()
        for transaction in (0x52, 0xA2):
            self.assertEqual(hid.handle_control(bytes((transaction, 1)) + bytes(48)), b"\x00")
            self.assertEqual(hid.handle_control(bytes((transaction, 1)) + bytes(47)), b"\x04")
        self.assertEqual(hid.handle_control(bytes((0x53, 0xEF)) + bytes(6)), b"\x04")
        self.assertEqual(hid.handle_control(bytes((0x53, 0xEF)) + bytes(6) + b"\x73"), b"\x00")
        self.assertEqual(hid.handle_control(bytes((0x43, 0xEF)))[8], 0x73)

    def test_invalid_and_unsupported(self):
        hid = DS3Hid()
        for packet in (b"", b"\x41", b"\x40\x01", b"\x45\x01",
                       b"\x49\x01\x40", b"\x49\x01\x01\x00",
                       b"\x41\x01\x00", b"\x00\x00", b"\x5b\xf4\x42\x03"):
            with self.subTest(packet=packet):
                self.assertEqual(hid.handle_control(packet), b"\x04")
        self.assertEqual(hid.handle_control(b"\x43\x99"), b"\x02")
        self.assertEqual(hid.handle_control(b"\x51\x01\x00"), b"\x02")
        self.assertEqual(hid.handle_control(b"\x60"), b"\x03")
        self.assertIsNone(hid.handle_control(b"\x00"))
        self.assertIsNone(hid.handle_control(b"\x03"))
        self.assertFalse(hid.reporting_enabled)


if __name__ == "__main__":
    unittest.main()
