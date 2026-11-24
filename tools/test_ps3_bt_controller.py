"""Wire-level regression cases; no USB, WSL, sockets, or console access."""
import contextlib
import io
import struct
from pathlib import Path
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import patch

import ps3_bt_controller as controller
from ps3_bt_controller import AclReceiver, L2capHid, button_report
from ps3_bt_probe import ProbeError
from ps3_ds3_hid import DS3Hid


def sig(code, identifier, payload):
    return struct.pack('<BBH', code, identifier, len(payload)) + payload


class ControllerTests(unittest.TestCase):
    def setUp(self):
        self.quiet = contextlib.redirect_stdout(io.StringIO())
        self.quiet.__enter__()
        self.addCleanup(self.quiet.__exit__, None, None, None)

    def configured_control(self):
        link = L2capHid(DS3Hid())
        link.connect(0x11)
        self.assertEqual(link.outgoing.popleft(), (1, bytes.fromhex('02 01 04 00 11 00 40 00')))
        link.receive(1, bytes.fromhex('03 01 08 00 70 00 40 00 00 00 00 00'))
        self.assertEqual(link.outgoing.popleft(), (1, bytes.fromhex('04 02 08 00 70 00 00 00 01 02 00 04')))
        # Peer uses a different CID and identifier; each direction must retain its own.
        link.receive(1, bytes.fromhex('04 4a 08 00 40 00 00 00 01 02 a0 02'))
        self.assertEqual(link.outgoing.popleft(), (1, bytes.fromhex('05 4a 06 00 70 00 00 00 00 00')))
        self.assertFalse(link.ready(0x11))
        link.receive(1, bytes.fromhex('05 02 06 00 40 00 00 00 00 00'))
        self.assertTrue(link.ready(0x11))
        return link

    def test_bidirectional_configuration_and_hid_enable(self):
        link = self.configured_control()
        link.receive(0x40, bytes.fromhex('53 f4 42 03 00 00'))
        self.assertTrue(link.hid.reporting_enabled)
        self.assertEqual(link.outgoing.popleft(), (0x70, b'\x00'))

    def test_pending_connection_does_not_configure_early(self):
        link = L2capHid(DS3Hid())
        link.connect(0x11)
        link.outgoing.clear()
        link.receive(1, bytes.fromhex('03 01 08 00 00 00 40 00 01 00 01 00'))
        self.assertFalse(link.outgoing)
        self.assertIsNone(link.channels[0x40]['remote'])

    def test_unknown_mandatory_option_rejected_then_valid_retry(self):
        link = self.configured_control()
        link.receive(1, bytes.fromhex('04 0a 07 00 40 00 00 00 07 01 ff'))
        self.assertFalse(link.ready(0x11))
        self.assertEqual(link.outgoing.popleft(), (1, bytes.fromhex('05 0a 09 00 70 00 00 00 03 00 07 01 ff')))
        link.receive(1, bytes.fromhex('04 0b 04 00 40 00 00 00'))
        self.assertTrue(link.ready(0x11))

    def test_wrong_config_response_and_truncation_rejected(self):
        for packet in ('05 02 06 00 70 00 00 00 00 00', '03 01 08 00 70', '08 00 00 00'):
            link = L2capHid(DS3Hid())
            link.connect(0x11)
            link.receive(1, bytes.fromhex('03 01 08 00 70 00 40 00 00 00 00 00'))
            with self.subTest(packet=packet), self.assertRaises(ProbeError):
                link.receive(1, bytes.fromhex(packet))

    def test_acl_usb_splits_l2cap_fragments_and_multiple_packets(self):
        received = []
        receiver = AclReceiver(0x123, lambda cid, data: received.append((cid, data)))
        # L2CAP SDU split across two ACL packets; USB read splits first HCI header.
        first = bytes.fromhex('23 21 05 00 06 00 40 00 53')
        second = bytes.fromhex('23 11 05 00 f4 42 03 00 00')
        receiver.feed(first[:3])
        receiver.feed(first[3:] + second)
        self.assertEqual(received, [(0x40, bytes.fromhex('53 f4 42 03 00 00'))])

    def test_acl_wrong_peer_or_orphan_or_oversize_rejected(self):
        for packet in ('24 21 04 00 00 00 01 00', '23 11 01 00 ff',
                       '23 21 04 00 ff 7f 01 00', '23 21 05 00 00 00 01 00 ff'):
            with self.subTest(packet=packet), self.assertRaises(ProbeError):
                AclReceiver(0x123, lambda *_: None).feed(bytes.fromhex(packet))

    def test_button_bits_and_pressure_preserve_neutral(self):
        hid = DS3Hid()
        right = button_report(hid, 'right')
        self.assertEqual(right[3], 0x20)
        self.assertEqual(right[16], 255)
        cross = button_report(hid, 'cross')
        self.assertEqual(cross[4], 0x40)
        self.assertEqual(cross[25], 255)
        self.assertEqual(button_report(hid, 'ps'), hid.input_report(ps_pressed=True))
        self.assertEqual(button_report(hid), hid.input_report())

    def frontend(self, outcome, restored):
        import ps3_bt_power as power
        stack = contextlib.ExitStack()
        self.addCleanup(stack.close)
        temp = stack.enter_context(tempfile.TemporaryDirectory())
        stack.enter_context(patch.object(controller, 'ROOT', Path(temp)))
        stack.enter_context(patch.object(power, '_exclusive_radio', return_value=contextlib.nullcontext()))
        stack.enter_context(patch.object(power, 'ensure_backend'))
        stack.enter_context(patch.object(power, '_linux_worker_path', return_value='/proven/wake.py'))
        recovery = stack.enter_context(patch.object(power, '_worker', return_value=int(not restored)))
        stack.enter_context(patch.object(power, '_run', side_effect=[
            SimpleNamespace(returncode=0, stdout=b'/private/controller.py\n'), outcome]))
        return recovery

    def test_worker_failure_still_runs_independent_recovery(self):
        recovery = self.frontend(RuntimeError('worker failed'), True)
        with self.assertRaisesRegex(RuntimeError, 'worker failed'):
            controller.windows_main(SimpleNamespace(seconds=5, duration=0.15, button=None))
        self.assertEqual(recovery.call_args.args[:2], ('/proven/wake.py', '--restore-only'))

    def test_recovery_failure_cannot_report_controller_success(self):
        self.frontend(SimpleNamespace(returncode=0), False)
        result = controller.windows_main(SimpleNamespace(seconds=5, duration=0.15, button='right'))
        self.assertEqual(result, 1)

    def test_pad_state_commands_and_timed_release(self):
        pad, hid = controller.PadState(), DS3Hid()
        self.assertEqual(pad.command('PRESS x 100', 0.0), 'OK PRESS cross 100')
        self.assertEqual(pad.command('DOWN up', 0.0), 'OK DOWN up')
        self.assertEqual(pad.command('STICK R 0 255', 0.0), 'OK STICK')
        self.assertTrue(pad.command('PRESS cross 5', 0.0).startswith('ERR'))
        self.assertTrue(pad.command('STICK L 300 0', 0.0).startswith('ERR'))
        report = pad.report(hid, 0.05)
        self.assertEqual((report[3], report[4], report[25], report[9], report[10]),
                         (16, 64, 255, 0, 255))
        report = pad.report(hid, 0.2)  # cross expired, up still held
        self.assertEqual((report[3], report[4]), (16, 0))
        self.assertEqual(pad.command('RELEASE', 0.2), 'OK RELEASE')
        self.assertEqual(pad.report(hid, 0.3), DS3Hid().input_report())
        self.assertEqual(pad.command('QUIT', 0.3), 'OK QUIT')
        self.assertTrue(pad.quit)

    def test_f2_padded_to_gimx_length(self):
        captured = bytes.fromhex('f2 ff ff 00 04 76 6e 8b 47 e4 00 03 50 81 d8 01 8a')
        reply = DS3Hid(captured_f2=captured).handle_control(bytes.fromhex('4b f2 40 00'))
        self.assertEqual(reply, b'\xa3' + captured + b'\x09')


if __name__ == '__main__':
    unittest.main()
