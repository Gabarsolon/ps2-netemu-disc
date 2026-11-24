# Pico 2 (RP2350) MicroPython: SG90 servo that presses the PS3 power button.
#
# Wiring: servo brown -> pin 38 GND, red -> pin 40 VBUS (5 V from PC USB),
#         orange -> pin 20 GP15.
# The Pico is powered from the PC, so it stays alive while the PS3 is off.
#
# Line commands over the USB serial port (115200 is ignored by USB CDC):
#   PING                      -> OK PONG
#   PRESS [ms]                -> press for ms (default 300), back to rest
#   HOLD <ms>                 -> same, 1000..15000 ms (force-off hold ~10000)
#   ANGLE <deg>               -> move and stay there (calibration), PWM kept on
#   REST                      -> go to rest angle, then PWM off
#   SET REST <deg> | SET PRESS <deg>  -> store calibration in cal.json
#   STATUS                    -> OK STATUS rest=.. press=..
#   RELEASE                   -> PWM off immediately
import json
import sys
import time
from machine import PWM, Pin

SERVO_PIN = 15
MIN_US, MAX_US = 500, 2400          # SG90 pulse range for ~0..180 deg
TRAVEL_MS = 450                     # time for a full move before PWM off
CAL_FILE = 'cal.json'

cal = {'rest': 90, 'press': 60}
try:
    with open(CAL_FILE) as f:
        cal.update(json.load(f))
except (OSError, ValueError):
    pass

led = Pin('LED', Pin.OUT)
pwm = None


def pulse_ns(deg):
    deg = max(0, min(180, deg))
    return int((MIN_US + (MAX_US - MIN_US) * deg / 180) * 1000)


def move(deg):
    global pwm
    if pwm is None:
        pwm = PWM(Pin(SERVO_PIN))
        pwm.freq(50)
    pwm.duty_ns(pulse_ns(deg))


def release():
    global pwm
    if pwm is not None:
        pwm.deinit()
        pwm = None
    Pin(SERVO_PIN, Pin.OUT).value(0)


def press(ms):
    led.value(1)
    move(cal['press'])
    time.sleep_ms(ms)
    move(cal['rest'])
    time.sleep_ms(TRAVEL_MS)
    release()
    led.value(0)


def save():
    with open(CAL_FILE, 'w') as f:
        json.dump(cal, f)


def handle(line):
    words = line.strip().split()
    if not words:
        return None
    cmd = words[0].upper()
    try:
        if cmd == 'PING':
            return 'OK PONG'
        if cmd == 'PRESS':
            ms = int(words[1]) if len(words) > 1 else 300
            if not 50 <= ms <= 15000:
                return 'ERR PRESS_MS 50..15000'
            press(ms)
            return 'OK PRESS %d' % ms
        if cmd == 'HOLD' and len(words) == 2:
            ms = int(words[1])
            if not 1000 <= ms <= 15000:
                return 'ERR HOLD_MS 1000..15000'
            press(ms)
            return 'OK HOLD %d' % ms
        if cmd == 'ANGLE' and len(words) == 2:
            deg = int(words[1])
            if not 0 <= deg <= 180:
                return 'ERR ANGLE 0..180'
            move(deg)
            return 'OK ANGLE %d' % deg
        if cmd == 'REST':
            move(cal['rest'])
            time.sleep_ms(TRAVEL_MS)
            release()
            return 'OK REST %d' % cal['rest']
        if cmd == 'SET' and len(words) == 3 and words[1].upper() in ('REST', 'PRESS'):
            deg = int(words[2])
            if not 0 <= deg <= 180:
                return 'ERR ANGLE 0..180'
            cal[words[1].lower()] = deg
            save()
            return 'OK SET %s %d' % (words[1].upper(), deg)
        if cmd == 'STATUS':
            return 'OK STATUS rest=%d press=%d pwm=%d' % (cal['rest'], cal['press'], pwm is not None)
        if cmd == 'RELEASE':
            release()
            return 'OK RELEASE'
    except ValueError:
        pass
    return 'ERR ' + line.strip()[:40]


release()
print('OK BOOT pico-servo rest=%d press=%d' % (cal['rest'], cal['press']))
while True:
    line = sys.stdin.readline()
    if line:
        answer = handle(line)
        if answer:
            print(answer)
