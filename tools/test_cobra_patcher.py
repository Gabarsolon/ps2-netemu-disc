"""Offline fault injection for the live Cobra patcher; never contacts a PS3."""
import contextlib
import io
from pathlib import Path
import sys
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parent))
import patch_cobra_netemu_disc as cobra


class FakeConsole:
    def __init__(self, active=False):
        self.memory = bytearray(0x20000)
        self.writes = []
        self.drop = None
        self.put(cobra.SIGNATURE_ADDR, cobra.EXPECTED_SIGNATURE)
        self.put(cobra.HOOK_CALL_ADDR, cobra.STOCK_CALL_BYTES)
        if active:
            self.put(cobra.HOOK_CALL_ADDR, cobra.PATCH_CALL_BYTES)
            for address, value in cobra.HOOK_CODE_WORDS + cobra.HOOK_DATA_WORDS:
                self.put(address, value)

    def put(self, address, value):
        data = bytes.fromhex(value)
        offset = address - 0x520000
        self.memory[offset:offset + len(data)] = data

    def peek(self, address):
        # Match webMAN's 16-byte aligned rows and highlighted individual bytes.
        base = address & ~15
        rows = []
        for start in range(base, base + 512, 16):
            data = self.memory[start - 0x520000:start - 0x520000 + 16]
            values = ' '.join(f'<font color=#ff0>{v:02X}</font>' for v in data)
            rows.append(f'{start:08X}  {values}  ................')
        return '<pre>' + '<br>'.join(rows) + '</pre>'

    def poke(self, address, value):
        self.writes.append((address, value))
        if address != self.drop:
            self.put(address, value)


class PatcherTests(unittest.TestCase):
    def setUp(self):
        self.console = FakeConsole()
        self.stack = contextlib.ExitStack()
        self.addCleanup(self.stack.close)
        self.stack.enter_context(contextlib.redirect_stdout(io.StringIO()))
        self.stack.enter_context(patch.object(cobra, 'peek_lv2', self.console.peek))
        self.stack.enter_context(patch.object(cobra, 'poke_lv2', self.console.poke))

    def test_unaligned_read_uses_displayed_row_address(self):
        html = self.console.peek(cobra.SIGNATURE_ADDR + 8)
        self.assertEqual(cobra.extract_bytes(html, cobra.SIGNATURE_ADDR + 8, 8),
                         '39 29 00 a0 2b 89 00 01')

    def test_missing_row_is_rejected(self):
        self.assertIsNone(cobra.extract_bytes(self.console.peek(0x5308b0), 0x5308a8, 8))

    def test_duplicate_row_is_rejected(self):
        html = self.console.peek(0x5308b0)
        html = html.replace('</pre>', html.removeprefix('<pre>'))
        self.assertIsNone(cobra.extract_bytes(html, 0x5308b0, 8))

    def test_navigation_text_does_not_hide_first_row(self):
        html = '<div>Close</div>' + self.console.peek(cobra.SIGNATURE_ADDR)
        self.assertEqual(cobra.extract_bytes(html, cobra.SIGNATURE_ADDR, 16),
                         cobra.EXPECTED_SIGNATURE)

    def test_apply_and_revert(self):
        self.assertEqual(cobra.check_status(), 'STOCK')
        self.assertTrue(cobra.apply_patch())
        self.assertEqual(cobra.check_status(), 'ACTIVE')
        self.assertEqual(self.console.writes[-1][0], cobra.HOOK_CALL_ADDR)
        self.assertTrue(cobra.revert_patch())
        self.assertEqual(cobra.check_status(), 'STOCK')

    def test_already_active_is_read_only(self):
        self.console.__init__(active=True)
        self.assertTrue(cobra.apply_patch())
        self.assertEqual(self.console.writes, [])

    def test_bad_signature_never_writes(self):
        self.console.put(cobra.SIGNATURE_ADDR, 'ffffffff')
        self.assertFalse(cobra.apply_patch())
        self.assertFalse(cobra.revert_patch())
        self.assertEqual(self.console.writes, [])

    def test_unknown_callsite_never_writes(self):
        self.console.put(cobra.HOOK_CALL_ADDR, '6000000060000000')
        self.assertFalse(cobra.apply_patch())
        self.assertFalse(cobra.revert_patch())
        self.assertEqual(self.console.writes, [])

    def test_occupied_slot_never_writes(self):
        self.console.put(cobra.HOOK_CODE_ADDR + 0x40, '12345678')
        self.assertFalse(cobra.apply_patch())
        self.assertEqual(self.console.writes, [])

    def test_every_corrupt_payload_byte_is_detected(self):
        for offset in range(160):
            with self.subTest(offset=offset):
                self.console.__init__(active=True)
                self.console.memory[cobra.HOOK_CODE_ADDR - 0x520000 + offset] ^= 1
                self.assertEqual(cobra.check_status(), 'UNKNOWN')
                self.assertFalse(cobra.apply_patch())
                self.assertFalse(cobra.revert_patch())
                self.assertEqual(self.console.writes, [])

    def test_dropped_payload_write_does_not_activate(self):
        for address, _ in cobra.HOOK_CODE_WORDS + cobra.HOOK_DATA_WORDS:
            with self.subTest(address=hex(address)):
                self.console.__init__()
                self.console.drop = address
                self.assertFalse(cobra.apply_patch())
                self.assertNotIn(cobra.HOOK_CALL_ADDR, [a for a, _ in self.console.writes])

    def test_dropped_activation_is_failure(self):
        self.console.drop = cobra.HOOK_CALL_ADDR
        self.assertFalse(cobra.apply_patch())

    def test_failed_unhook_retains_payload(self):
        self.console.__init__(active=True)
        self.console.drop = cobra.HOOK_CALL_ADDR
        self.assertFalse(cobra.revert_patch())
        self.assertEqual(len(self.console.writes), 1)
        self.assertEqual(cobra.check_status(), 'ACTIVE')

    def test_incomplete_response_never_writes(self):
        with patch.object(cobra, 'peek_lv2', return_value='<pre>unavailable</pre>'):
            self.assertFalse(cobra.apply_patch())
            self.assertFalse(cobra.revert_patch())
        self.assertEqual(self.console.writes, [])

    def test_callsite_change_during_preparation_does_not_activate(self):
        def poke(address, value):
            self.console.poke(address, value)
            self.console.put(cobra.HOOK_CALL_ADDR, '6000000060000000')
        with patch.object(cobra, 'poke_lv2', side_effect=poke):
            self.assertFalse(cobra.apply_patch())
        self.assertNotIn(cobra.HOOK_CALL_ADDR, [a for a, _ in self.console.writes])

    def test_cli_returns_failure_for_unknown_state(self):
        self.console.put(cobra.HOOK_CALL_ADDR, '6000000060000000')
        for action in ('--apply', '--revert', '--check'):
            with self.subTest(action=action), patch.object(sys, 'argv', ['patcher', action]):
                self.assertEqual(cobra.main(), 1)
        self.assertEqual(self.console.writes, [])


if __name__ == '__main__':
    unittest.main()
