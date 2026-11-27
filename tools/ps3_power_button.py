#!/usr/bin/env python3
"""Press the PS3 front power button with the Pico servo (pico-servo/main.py).

Commands:
  status                 console state (webMAN HTTP + Tapo watts) and servo calibration
  press [ms]             raw short press (default 300 ms) - no state check
  hold [ms]              raw long press (default 10000 ms) - no state check
  on                     power on, only if the console looks OFF; waits for webMAN
  off --yes              force-off hold (10 s), for a frozen console; waits for low watts
  recover --yes          off (hold) -> wait -> on -> wait for webMAN
  angle <deg>            move servo and stay (calibration)
  set rest|press <deg>   store calibration on the Pico
  rest                   return to rest angle and release

State rules (same as tools/ps3_run_monitor.py): HTTP up = XMB; HTTP down and
>30 W = running (PS2 mode or frozen); HTTP down and <15 W = OFF.
A short press on a running PS3 turns it off, so `on` refuses unless OFF.
"""
from __future__ import annotations

import argparse
import asyncio
import json
import os
import sys
import time
import urllib.request

import serial
import serial.tools.list_ports

HOST = '192.168.0.169'
PICO_VID = 0x2E8A


def http_up(timeout=3):
    try:
        urllib.request.urlopen(f'http://{HOST}/', timeout=timeout)
        return True
    except Exception:
        return False


def watts():
    """Tapo P115 power in W, or None if unavailable."""
    try:
        from tapo import ApiClient
    except ImportError:
        return None
    cfg = None
    # ~/tapo_config.json is the one ps3_power_manager.py maintains (current plug IP).
    for path in (os.path.expanduser('~/tapo_config.json'), 'local_only/tapo_config.json'):
        if os.path.exists(path):
            cfg = json.load(open(path))
            break
    if not cfg:
        return None

    async def read():
        client = ApiClient(cfg['email'], cfg['password'])
        plug = await asyncio.wait_for(client.p115(cfg['ip']), timeout=8)
        # get_energy_usage() reports current_power in milliwatts.
        return (await asyncio.wait_for(plug.get_energy_usage(), timeout=6)).current_power / 1000
    try:
        return asyncio.run(read())
    except Exception:
        return None


def console_state():
    up = http_up()
    w = watts()
    if up:
        state = 'XMB'
    elif w is None:
        state = 'UNKNOWN'
    elif w > 30:
        state = 'RUNNING'
    elif w < 15:
        state = 'OFF'
    else:
        state = 'UNKNOWN'
    return state, up, w


class Servo:
    def __init__(self, port=None):
        if port is None:
            ports = [p.device for p in serial.tools.list_ports.comports() if p.vid == PICO_VID]
            if len(ports) != 1:
                raise SystemExit(f'Expected one Pico (VID 2E8A) serial port, found {ports}')
            port = ports[0]
        self.ser = serial.Serial(port, 115200, timeout=0.2)
        time.sleep(0.2)
        self.ser.reset_input_buffer()

    def send(self, command, timeout=6.0):   # a slow 180 deg move takes ~4 s
        self.ser.write((command + '\r\n').encode())
        deadline = time.monotonic() + timeout
        while time.monotonic() < deadline:
            line = self.ser.readline().decode('utf-8', 'ignore').strip()
            if line.startswith(('OK', 'ERR')) and not line.startswith('OK BOOT'):
                return line
        raise SystemExit(f'No reply from Pico to {command!r}')


def wait_for(predicate, seconds, step=3):
    deadline = time.monotonic() + seconds
    while time.monotonic() < deadline:
        if predicate():
            return True
        time.sleep(step)
    return False


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('command', choices=('status', 'press', 'hold', 'on', 'off', 'recover',
                                            'angle', 'set', 'rest'))
    parser.add_argument('args', nargs='*')
    parser.add_argument('--yes', action='store_true', help='confirm force-off actions')
    parser.add_argument('--port', help='Pico serial port (auto-detected by VID 2E8A)')
    a = parser.parse_args()

    if a.command == 'status':
        state, up, w = console_state()
        print(f'console={state} http={"up" if up else "down"} watts={w}')
        try:
            print(Servo(a.port).send('STATUS'))
        except SystemExit as exc:
            print('servo:', exc)
        return 0

    servo = Servo(a.port)
    if a.command == 'press':
        ms = int(a.args[0]) if a.args else 300
        print(servo.send(f'PRESS {ms}', timeout=ms / 1000 + 9))
    elif a.command == 'hold':
        ms = int(a.args[0]) if a.args else 10000
        print(servo.send(f'HOLD {ms}', timeout=ms / 1000 + 9))
    elif a.command == 'angle':
        print(servo.send(f'ANGLE {int(a.args[0])}'))
    elif a.command == 'set':
        print(servo.send(f'SET {a.args[0].upper()} {int(a.args[1])}'))
    elif a.command == 'rest':
        print(servo.send('REST'))
    elif a.command in ('off', 'recover'):
        if not a.yes:
            raise SystemExit('Force-off holds the power button 10 s. Re-run with --yes.')
        state, up, w = console_state()
        print(f'before: console={state} watts={w}')
        if state == 'OFF':
            print('already OFF, no hold')
        else:
            print(servo.send('HOLD 10000', timeout=19))
            off = wait_for(lambda: console_state()[0] == 'OFF', 30)
            print('console OFF' if off else 'WARNING: console did not reach OFF within 30 s')
            if not off:
                return 1
        if a.command == 'recover':
            time.sleep(5)
    if a.command in ('on', 'recover'):
        state, up, w = console_state()
        if state != 'OFF':
            raise SystemExit(f'Refusing to press: console looks {state} (http={up}, watts={w}); '
                             'a press would turn a running PS3 off.')
        # RULE (owner 2026-11-27): keep pressing until it turns on. One press can
        # miss; a panic needs a double press. Retry press+verify up to 5 cycles.
        for attempt in range(1, 6):
            print(f'press attempt {attempt}/5:', servo.send('PRESS 300', timeout=9))
            if wait_for(http_up, 45, step=4):
                print(f'webMAN online: console booted (attempt {attempt})')
                return 0
            s2, u2, w2 = console_state()
            print(f'  not up yet (http={u2}, watts={w2}); retrying' if attempt < 5 else
                  f'  still off after {attempt} attempts (http={u2}, watts={w2})')
        print('WARNING: console did not boot after 5 servo press cycles; press the power button by hand')
        return 1
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
