"""Temporary, fixed-address diagnostic: make the PS2 auth helper return 0x5A.

This deliberately reports failure, performs no authentication, and writes only
RAM. A matching reply is positive evidence that this helper instance executed.
An unchanged reply does not by itself prove when or why a patch disappeared.
Exact 4.93 bytes and offline ABI proof: docs/P16_AUTH_ANALYSIS.md.
"""
import argparse
from pathlib import Path
import sys
import urllib.request

sys.path.insert(0, str(Path(__file__).resolve().parent))
from patch_cobra_netemu_disc import extract_bytes

HOST = '192.168.0.169'
ADDRESS = 0x714638
STOCK = bytes.fromhex('f821ff517c0802a6')
SENTINEL = bytes.fromhex('3860005a4e800020')  # li r3,0x5a; blr (before prologue)
FOLLOWING = bytes.fromhex('fba10098fbc100a0')


def request(path):
    with urllib.request.urlopen('http://' + HOST + path, timeout=8) as response:
        return response.read().decode('utf-8', errors='replace')


def check():
    value = extract_bytes(request(f'/peek.lv1?{ADDRESS:x}'), ADDRESS, 16)
    if value is None:
        return 'UNKNOWN'
    raw = bytes.fromhex(value)
    if raw == STOCK + FOLLOWING:
        return 'STOCK'
    if raw == SENTINEL + FOLLOWING:
        return 'SENTINEL'
    return 'UNKNOWN'


def set_state(wanted):
    state = check()
    if state == wanted:
        print('Already ' + wanted + '; no write.')
        return True
    if state not in ('STOCK', 'SENTINEL'):
        print('Unknown helper bytes; refusing to write.')
        return False
    value = SENTINEL if wanted == 'SENTINEL' else STOCK
    request(f'/poke.lv1?{ADDRESS:x}={value.hex()}')
    state = check()
    print('Read-back state:', state)
    return state == wanted


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    actions = parser.add_mutually_exclusive_group()
    actions.add_argument('--check', action='store_true')
    actions.add_argument('--apply', action='store_true')
    actions.add_argument('--revert', action='store_true')
    args = parser.parse_args()
    if args.apply:
        return 0 if set_state('SENTINEL') else 1
    if args.revert:
        return 0 if set_state('STOCK') else 1
    state = check()
    print(f'Helper 0x{ADDRESS:08x}: {state}')
    return 0 if state != 'UNKNOWN' else 1


if __name__ == '__main__':
    try:
        sys.exit(main())
    except (OSError, ValueError) as error:
        print('Operation failed:', error)
        sys.exit(1)
