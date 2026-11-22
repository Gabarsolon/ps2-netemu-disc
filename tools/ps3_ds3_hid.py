"""Offline DS3 Bluetooth HID protocol helper; no sockets or hardware access.

INFERRED compatibility: independently expressed from functional wire layouts in
https://github.com/matlo/GIMX/blob/master/core/connectors/sixaxis.c
https://github.com/matlo/GIMX/blob/master/shared/gimxcontroller/include/ds3.h
https://github.com/matlo/GIMX/blob/master/shared/gimxcontroller/src/ds3.c
Console wake with this helper is UNKNOWN until a physical console test.

Captured F2/F5 arguments are complete USB feature reports, beginning with the
report ID, without a Bluetooth HID header. They are returned verbatim under an
A3 header, never modified or written back. No address-bearing report is invented.
"""

from __future__ import annotations


class DS3Hid:
    SUCCESS = b"\x00"
    INVALID_REPORT = b"\x02"
    UNSUPPORTED = b"\x03"
    INVALID_PARAMETER = b"\x04"

    def __init__(self, *, captured_f2: bytes | None = None,
                 captured_f5: bytes | None = None) -> None:
        self.reporting_enabled = False
        self.shutdown_requested = False
        self._ef_byte_6 = 0xB0
        self._captured = {}
        for report_id, captured in ((0xF2, captured_f2), (0xF5, captured_f5)):
            if captured is not None:
                report = bytes(captured)
                if not 2 <= len(report) <= 255 or report[0] != report_id:
                    raise ValueError("Captured feature must start with its report ID")
                self._captured[report_id] = report

    def input_report(self, ps_pressed: bool = False) -> bytes:
        """Return A1 + 49-byte report 01; PS is packet byte 5, bit zero."""
        report = bytearray(50)
        report[0:2] = bytes((0xA1, 0x01))
        report[5] = int(bool(ps_pressed))
        report[7:11] = bytes((128, 128, 128, 128))
        # Not charging, full battery, Bluetooth transport with rumble disabled.
        report[30:33] = bytes((3, 5, 0x16))
        report[37:42] = bytes((0x33, 0xFA, 0x77, 1, 0xC0))
        # Big-endian motion values: centered X/Y/gyro; stationary Z.
        report[42:50] = bytes((2, 0, 2, 0, 1, 0x90, 2, 0))
        return bytes(report)

    def _feature_report(self, report_id: int) -> bytes | None:
        if report_id in self._captured:
            return self._captured[report_id]
        if report_id == 0x01:
            # GIMX's fixed feature-01 protocol data, for controller index zero.
            body = bytes.fromhex(
                "01 03 00 04 0c 01 02 18 18 18 18 09 0a 10 11 12 "
                "13 00 00 00 00 04 00 02 02 02 02 00 00 00 04 04 "
                "04 04 00 00 02 01 02 00 64 00 17 00 00 00 00 00")
        elif report_id == 0xEF:
            body = bytearray(48)
            body[:7] = bytes((0xEF, 4, 0, 5, 3, 1, self._ef_byte_6))
            body[16:24] = bytes((2, 0, 0, 0, 2, 0, 3, 0xFF))
            body[47] = 4
            body = bytes(body)
        elif report_id == 0xF7:
            body = bytes.fromhex("00 02 e4 02 a9 01 05 ff 14 23 00")
        elif report_id == 0xF8:
            body = bytes((1, 0, 0, 0))
        else:
            return None
        return bytes((report_id,)) + body

    def handle_control(self, payload: bytes) -> bytes | None:
        """Handle one complete HID control SDU, returning its response SDU.

        Only supported report transactions alter local state. Unknown reports
        return invalid-report-ID; malformed frames return invalid-parameter.
        Received handshakes need no response. SET_REPORT and DATA received on
        control are acknowledged, matching GIMX. This function is not an
        interrupt-channel packet handler.
        """
        packet = bytes(payload)
        if not packet:
            return self.INVALID_PARAMETER
        transaction, parameter = packet[0] >> 4, packet[0] & 0x0F
        if transaction == 0:
            return None if len(packet) == 1 else self.INVALID_PARAMETER
        if transaction not in (4, 5, 10):
            return self.UNSUPPORTED
        allowed = 0x0B if transaction == 4 else 0x03
        report_type = parameter & 3
        if parameter & ~allowed or report_type == 0 or len(packet) < 2:
            return self.INVALID_PARAMETER
        report_id = packet[1]

        if transaction == 4:  # GET_REPORT, optionally with a 16-bit buffer size.
            sized = bool(parameter & 8)
            if len(packet) != (4 if sized else 2):
                return self.INVALID_PARAMETER
            if report_type == 1 and report_id == 1:
                report = self.input_report()[1:]
            elif report_type == 3:
                report = self._feature_report(report_id)
            else:
                report = None
            if report is None:
                return self.INVALID_REPORT
            if sized and int.from_bytes(packet[2:4], "little") < len(report):
                # Conservatively reject short buffers rather than truncate a
                # feature report whose contents may include paired addresses.
                return self.INVALID_PARAMETER
            return bytes((0xA0 | report_type,)) + report

        body = packet[2:]
        if report_type == 2 and report_id == 1:
            return self.SUCCESS if len(body) == 48 else self.INVALID_PARAMETER
        if report_type != 3 or report_id not in (0xEF, 0xF4):
            return self.INVALID_REPORT
        if report_id == 0xEF:
            if len(body) < 7:
                return self.INVALID_PARAMETER
            self._ef_byte_6 = body[6]
        else:
            # These are the two bytes GIMX consumes; never read a short frame.
            if len(body) < 2:
                return self.INVALID_PARAMETER
            if body[1] == 8:
                self.shutdown_requested = True
                self.reporting_enabled = False
            elif not self.shutdown_requested:
                self.reporting_enabled = True
        return self.SUCCESS
