"""Offline checks for direct USB command layout and actual HCI event handling."""
import unittest
from unittest.mock import Mock

from ps3_bt_linux import LinuxRadio, connection_event, connection_packet, controller_page
from ps3_bt_probe import ProbeError
from ps3_bt_wake import mac_bytes

CONSOLE = '78:DD:08:8D:37:F4'


class LinuxPacketTests(unittest.TestCase):
    def test_create_connection_uses_upstream_r2_no_clock_hint(self):
        self.assertEqual(connection_packet(CONSOLE).hex(), '05040df4378d08dd7818cc0200000001')

    def test_command_accepted_waits_for_connection_complete(self):
        self.assertIsNone(connection_event(bytes.fromhex('0f0400010504'), mac_bytes(CONSOLE)))

    def test_immediate_command_rejection_is_not_success(self):
        self.assertEqual(connection_event(bytes.fromhex('0f040c010504'), mac_bytes(CONSOLE)), (12, None))

    def test_actual_console_rejection_is_decoded(self):
        raw = bytes.fromhex('030b0f8100f4378d08dd780100')
        self.assertEqual(connection_event(raw, mac_bytes(CONSOLE)), (15, None))

    def test_successful_acl_requires_matching_console(self):
        raw = bytes.fromhex('030b008100f4378d08dd780100')
        self.assertEqual(connection_event(raw, mac_bytes(CONSOLE)), (0, 0x81))
        self.assertIsNone(connection_event(raw, bytes.fromhex('010203040506')))

    def test_truncated_event_is_not_accepted(self):
        with self.assertRaises(ProbeError):
            connection_event(bytes.fromhex('030b008100'), mac_bytes(CONSOLE))

    def test_only_captured_addresses_can_be_written(self):
        radio = object.__new__(LinuxRadio)
        radio.allowed_addresses = {mac_bytes('04:7F:0E:0C:E5:80')}
        radio._exchange = Mock()
        with self.assertRaises(ProbeError):
            radio.address(5, address=bytes.fromhex('010203040506'))
        radio._exchange.assert_not_called()

    def test_standard_reset_has_no_proprietary_parameters(self):
        radio = object.__new__(LinuxRadio)
        radio._exchange = Mock(return_value=b'')
        radio.reset()
        radio._exchange.assert_called_once_with(0x0C03, b'')


    def test_wake_verifies_controller_class_and_holds_the_link(self):
        radio = Mock()
        radio.class_of_device.side_effect = [None, bytes.fromhex('080500')]
        radio.page.return_value = 0
        self.assertEqual(controller_page(radio, 'local', CONSOLE), 0)
        radio.page.assert_called_once_with('local', CONSOLE, hold_seconds=3)
        self.assertEqual(radio.class_of_device.call_args_list[0].args, (bytes.fromhex('080500'),))

    def test_ignored_device_class_write_stops_before_paging(self):
        radio = Mock()
        radio.class_of_device.side_effect = [None, bytes(3)]
        with self.assertRaisesRegex(ProbeError, 'did not verify'):
            controller_page(radio, 'local', CONSOLE)
        radio.page.assert_not_called()

    def test_only_saved_or_controller_class_can_be_written(self):
        radio = object.__new__(LinuxRadio)
        radio.class_values = {bytes(3), bytes.fromhex('080500')}
        radio._exchange = Mock(return_value=b'')
        with self.assertRaises(ProbeError):
            radio.class_of_device(bytes.fromhex('010203'))
        radio._exchange.assert_not_called()
        radio.class_of_device(bytes(3))
        radio._exchange.assert_called_once_with(0x0C24, bytes(3))

    def test_invalid_class_read_is_not_used_as_a_restore_target(self):
        radio = object.__new__(LinuxRadio)
        radio._exchange = Mock(return_value=b'')
        with self.assertRaises(ProbeError):
            radio.class_of_device()


if __name__ == '__main__':
    unittest.main()
