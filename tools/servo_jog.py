#!/usr/bin/env python3
"""Move the power-button servo from the keyboard to calibrate it (Windows).

  a / d   -5 / +5 degrees
  z / c   -1 / +1 degree
  space   back to the saved rest angle
  r       save the current angle as rest
  p       save the current angle as press
  t       test click with the saved angles (this really presses the button)
  q       go to rest, release the servo, quit

An arm left on the button keeps it held: press space right after it clicks,
or the PS3 will be forced off.
"""
import msvcrt

from ps3_power_button import Servo

STEPS = {'a': -5, 'd': 5, 'z': -1, 'c': 1}


def main():
    servo = Servo()
    status = servo.send('STATUS')           # OK STATUS rest=.. press=.. pwm=..
    cal = dict(word.split('=') for word in status.split()[2:])
    rest, press = int(cal['rest']), int(cal['press'])
    angle = rest
    print(__doc__)
    try:
        while True:
            print(f'\rangle={angle:3d}  rest={rest:3d}  press={press:3d}   ', end='', flush=True)
            key = msvcrt.getwch().lower()
            if key in STEPS:
                angle = max(0, min(180, angle + STEPS[key]))
                servo.send(f'ANGLE {angle}')
            elif key == ' ':
                angle = rest
                servo.send(f'ANGLE {angle}')
            elif key == 'r':
                servo.send(f'SET REST {angle}')
                rest = angle
            elif key == 'p':
                servo.send(f'SET PRESS {angle}')
                press = angle
            elif key == 't':
                servo.send('PRESS 300')
                angle = rest
            elif key in ('q', '\x03', '\x1b'):
                break
    finally:
        print()
        print(servo.send('REST'))


if __name__ == '__main__':
    main()
