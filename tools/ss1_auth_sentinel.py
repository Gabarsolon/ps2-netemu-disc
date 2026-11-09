"""Temporary, fixed-address diagnostic: make an auth helper return 0x5A.

This deliberately reports failure, performs no authentication, and writes only
RAM. A matching reply is positive evidence that this helper instance executed.
An unchanged reply does not by itself prove when or why a patch disappeared.
Exact 4.93 bytes and offline ABI proof: docs/P16_AUTH_ANALYSIS.md and
docs/P16_SERVICE_CONTEXT.md. Both target addresses are fixed and preflighted.
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
TARGETS = {
    'ps2': (ADDRESS, STOCK, FOLLOWING),
    'gameos': (0x7147e8, bytes.fromhex('f821ff617c0802a6'), bytes.fromhex('fb8100807c7c1b78')),
}


def request(path):
    with urllib.request.urlopen('http://' + HOST + path, timeout=8) as response:
        return response.read().decode('utf-8', errors='replace')


def check(target='ps2'):
    address, stock, following = TARGETS[target]
    value = extract_bytes(request(f'/peek.lv1?{address:x}'), address, 16)
    if value is None:
        return 'UNKNOWN'
    raw = bytes.fromhex(value)
    if raw == stock + following:
        return 'STOCK'
    if raw == SENTINEL + following:
        return 'SENTINEL'
    return 'UNKNOWN'


def set_state(wanted, target='ps2'):
    address, stock, _ = TARGETS[target]
    state = check(target)
    if state == wanted:
        print('Already ' + wanted + '; no write.')
        return True
    if state not in ('STOCK', 'SENTINEL'):
        print('Unknown helper bytes; refusing to write.')
        return False
    value = SENTINEL if wanted == 'SENTINEL' else stock
    request(f'/poke.lv1?{address:x}={value.hex()}')
    state = check(target)
    print('Read-back state:', state)
    return state == wanted


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--target', choices=TARGETS, default='ps2',
                        help='ps2: opcode 5005 helper; gameos: opcode 5004 helper')
    actions = parser.add_mutually_exclusive_group()
    actions.add_argument('--check', action='store_true')
    actions.add_argument('--apply', action='store_true')
    actions.add_argument('--revert', action='store_true')
    args = parser.parse_args()
    if args.apply:
        return 0 if set_state('SENTINEL', args.target) else 1
    if args.revert:
        return 0 if set_state('STOCK', args.target) else 1
    state = check(args.target)
    print(f'Helper 0x{TARGETS[args.target][0]:08x}: {state}')
    return 0 if state != 'UNKNOWN' else 1


if __name__ == '__main__':
    try:
        sys.exit(main())
    except (OSError, ValueError) as error:
        print('Operation failed:', error)
        sys.exit(1)
