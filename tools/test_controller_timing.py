"""Simulate the Pico's immediate ACK and delayed button release; no hardware."""
from pathlib import Path
import sys
import unittest
from unittest.mock import Mock, patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'pico-ds3-bridge/python'))
from ps3_controller import PS3Controller


class TimingTests(unittest.TestCase):
    def setUp(self):
        self.now = 0.0
        self.deadline = None
        self.cancelled = False
        self.ctl = PS3Controller.__new__(PS3Controller)
        self.ctl.ser = Mock()
        self.ctl.send_cmd = self.command
        self.sleep = patch('ps3_controller.time.sleep', side_effect=self.advance)
        self.sleep.start()
        self.addCleanup(self.sleep.stop)

    def advance(self, seconds):
        self.now += seconds

    def command(self, text):
        if text.startswith('PRESS '):
            self.deadline = self.now + int(text.split()[2]) / 1000.0
            return 'OK ' + text
        if text == 'RELEASE':
            self.cancelled = self.deadline is not None and self.now < self.deadline
            return 'OK RELEASE'
        return 'ERR UNKNOWN'

    def test_close_after_tap_does_not_cancel_it(self):
        self.ctl.press('CROSS', 100)
        self.ctl.close()
        self.assertFalse(self.cancelled)
        self.assertGreaterEqual(self.now, 0.1)
        self.ctl.ser.close.assert_called_once()

    def test_ps_helpers_complete_before_close(self):
        self.ctl.ps_button(300)
        self.ctl.hold_ps_button(2000)
        self.ctl.close()
        self.assertFalse(self.cancelled)
        self.assertGreaterEqual(self.now, 2.3)

    def test_minimum_duration_matches_firmware(self):
        self.ctl.press('CROSS', 1)
        self.ctl.close()
        self.assertFalse(self.cancelled)
        self.assertGreaterEqual(self.now, 0.02)

    def test_rejected_command_does_not_wait(self):
        self.ctl.send_cmd = Mock(return_value='ERR UNKNOWN_BUTTON')
        self.assertEqual(self.ctl.press('INVALID'), 'ERR UNKNOWN_BUTTON')
        self.assertEqual(self.now, 0)


if __name__ == '__main__':
    unittest.main()
