"""Exercise cleanup against a simulated dongle; never touches hardware/network."""

import unittest
from unittest.mock import Mock

from ps3_bt_probe import ProbeError
from ps3_bt_wake import mac_bytes, spoof_and_page
from ps3_bt_windows_probe import vendor_address_packet, vendor_hci_reset_packet

PAIR = {'adapter_mac': '04:7F:0E:0C:E5:80', 'controller_mac': '04:76:6E:8B:47:E4',
        'console_mac': '78:DD:08:8D:37:F4'}


class Dongle:
    def __init__(self):
        self.address = mac_bytes(PAIR['adapter_mac'])
        self.writes = []
        self.reject_spoof = False
        self.fail_after_spoof = False
        self.reject_restore = False

    def query(self, command, *, address=None):
        assert command == 5
        if address is None:
            return self.address
        self.writes.append(address)
        spoof = address == mac_bytes(PAIR['controller_mac'])
        if (spoof and self.reject_spoof) or (not spoof and self.reject_restore):
            return b''
        self.address = address
        if spoof and self.fail_after_spoof:
            raise OSError('device changed address but command reply failed')
        return b''


class WakeCleanupTests(unittest.TestCase):
    def test_address_packet_is_ram_bd_param_in_little_endian(self):
        raw = vendor_address_packet(mac_bytes(PAIR['controller_mac']))
        self.assertEqual(raw.hex(), 'e7080000000080fc080500e4478b6e7604')

    def test_verified_spoof_pages_only_captured_host_then_restores(self):
        dongle, page = Dongle(), Mock()
        spoof_and_page(dongle.query, PAIR, page)
        page.assert_called_once_with(PAIR['adapter_mac'], PAIR['console_mac'])
        self.assertEqual(dongle.address, mac_bytes(PAIR['adapter_mac']))
        self.assertEqual(dongle.writes, [mac_bytes(PAIR['controller_mac']), mac_bytes(PAIR['adapter_mac'])])

    def test_no_page_when_write_is_ignored(self):
        dongle, page = Dongle(), Mock()
        dongle.reject_spoof = True
        with self.assertRaisesRegex(ProbeError, 'did not verify'):
            spoof_and_page(dongle.query, PAIR, page)
        page.assert_not_called()
        self.assertEqual(dongle.address, mac_bytes(PAIR['adapter_mac']))

    def test_restore_when_command_applied_but_reply_failed(self):
        dongle, page = Dongle(), Mock()
        dongle.fail_after_spoof = True
        with self.assertRaises(OSError):
            spoof_and_page(dongle.query, PAIR, page)
        page.assert_not_called()
        self.assertEqual(dongle.address, mac_bytes(PAIR['adapter_mac']))

    def test_restore_when_paging_raises(self):
        dongle = Dongle()
        with self.assertRaises(TimeoutError):
            spoof_and_page(dongle.query, PAIR, Mock(side_effect=TimeoutError()))
        self.assertEqual(dongle.address, mac_bytes(PAIR['adapter_mac']))

    def test_unexpected_initial_address_stops_without_writes(self):
        dongle, page = Dongle(), Mock()
        dongle.address = bytes.fromhex('112233445566')
        with self.assertRaisesRegex(ProbeError, 'expected original'):
            spoof_and_page(dongle.query, PAIR, page)
        page.assert_not_called()
        self.assertEqual(dongle.writes, [])

    def test_failed_restoration_is_reported_as_failure(self):
        dongle = Dongle()
        dongle.reject_restore = True
        with self.assertRaisesRegex(ProbeError, 'restoration did not verify'):
            spoof_and_page(dongle.query, PAIR, Mock())


    def test_reset_packet_selects_only_hci_type_four(self):
        self.assertEqual(vendor_hci_reset_packet().hex(), 'e7080000000080fc03000004')

    def test_reset_activates_spoof_and_restoration(self):
        dongle = Dongle()
        activated = []
        def activate():
            activated.append(dongle.address)
        def page(*args):
            self.assertEqual(activated, [mac_bytes(PAIR['controller_mac'])])
        spoof_and_page(dongle.query, PAIR, page, activate=activate)
        self.assertEqual(activated, [mac_bytes(PAIR['controller_mac']), mac_bytes(PAIR['adapter_mac'])])

    def test_reset_losing_spoof_stops_page_and_restores(self):
        dongle, page = Dongle(), Mock()
        def lose_address():
            dongle.address = mac_bytes(PAIR['adapter_mac'])
        with self.assertRaisesRegex(ProbeError, 'did not retain'):
            spoof_and_page(dongle.query, PAIR, page, activate=lose_address)
        page.assert_not_called()
        self.assertEqual(dongle.address, mac_bytes(PAIR['adapter_mac']))

    def test_failed_activation_still_resets_original_address(self):
        dongle, page = Dongle(), Mock()
        activated = []
        def activate():
            activated.append(dongle.address)
            if len(activated) == 1:
                raise OSError('reset applied but reply failed')
        with self.assertRaisesRegex(OSError, 'reply failed'):
            spoof_and_page(dongle.query, PAIR, page, activate=activate)
        page.assert_not_called()
        self.assertEqual(activated, [mac_bytes(PAIR['controller_mac']), mac_bytes(PAIR['adapter_mac'])])

    def test_failed_final_activation_is_reported(self):
        dongle = Dongle()
        activate = Mock(side_effect=[None, OSError('original identity activation failed')])
        with self.assertRaisesRegex(OSError, 'activation failed'):
            spoof_and_page(dongle.query, PAIR, Mock(), activate=activate)


if __name__ == '__main__':
    unittest.main()
