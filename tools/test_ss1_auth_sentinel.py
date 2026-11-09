"""Offline tests for the exact-address auth sentinel's preflight/read-back."""
import contextlib
import io
from pathlib import Path
import sys
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parent))
import ss1_auth_sentinel as sentinel


class SentinelTests(unittest.TestCase):
    def setUp(self):
        self.data = bytearray(bytes(8) + sentinel.STOCK + sentinel.FOLLOWING + bytes(8))
        self.writes = []
        self.drop = False
        self.stack = contextlib.ExitStack()
        self.addCleanup(self.stack.close)
        self.stack.enter_context(contextlib.redirect_stdout(io.StringIO()))
        self.stack.enter_context(patch.object(sentinel, 'request', side_effect=self.request))

    def request(self, path):
        if path.startswith('/poke.'):
            self.writes.append(path)
            if not self.drop:
                data = bytes.fromhex(path.split('=')[1])
                self.data[8:8 + len(data)] = data
        rows = []
        for offset in (0, 16):
            rows.append(f'{0x714630 + offset:08X}  {self.data[offset:offset + 16].hex(" ")}  ................')
        return '<div>Close</div><pre>' + '<br>'.join(rows) + '</pre>'

    def test_roundtrip_preserves_neighbor_bytes(self):
        original = bytes(self.data)
        self.assertTrue(sentinel.set_state('SENTINEL'))
        self.assertEqual(self.data[8:16], sentinel.SENTINEL)
        self.assertTrue(sentinel.set_state('STOCK'))
        self.assertEqual(bytes(self.data), original)
        self.assertTrue(all(path.startswith('/poke.lv1?714638=') for path in self.writes))

    def test_unknown_entry_or_neighbor_never_writes(self):
        for offset in range(8, 24):
            with self.subTest(offset=offset):
                self.data[offset] ^= 1
                self.assertFalse(sentinel.set_state('SENTINEL'))
                self.assertFalse(sentinel.set_state('STOCK'))
                self.assertEqual(self.writes, [])
                self.data[offset] ^= 1

    def test_dropped_write_returns_failure(self):
        self.drop = True
        self.assertFalse(sentinel.set_state('SENTINEL'))
        self.assertEqual(sentinel.check(), 'STOCK')

    def test_already_installed_is_read_only(self):
        self.data[8:16] = sentinel.SENTINEL
        self.assertTrue(sentinel.set_state('SENTINEL'))
        self.assertEqual(self.writes, [])

    def test_malformed_read_never_writes(self):
        with patch.object(sentinel, 'request', return_value='<pre>unavailable</pre>'):
            self.assertFalse(sentinel.set_state('SENTINEL'))
        self.assertEqual(self.writes, [])


if __name__ == '__main__':
    unittest.main()
