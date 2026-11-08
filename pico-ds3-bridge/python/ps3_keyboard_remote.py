import pygame
import serial
import sys
import time

PORT = "COM9"
BAUD = 115200

print(f"Connecting to PS3 Controller Bridge on {PORT}...")
try:
    ser = serial.Serial(PORT, BAUD, timeout=0.1)
    time.sleep(0.2)
    ser.reset_input_buffer()
except Exception as e:
    print(f"ERROR: Could not open {PORT}: {e}")
    sys.exit(1)

def send_cmd(cmd):
    try:
        ser.write((cmd.strip() + "\r\n").encode("utf-8"))
    except Exception as e:
        print("Serial error:", e)

pygame.init()
WIDTH, HEIGHT = 640, 480
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("PS3 Keyboard Remote (Pico 2 Bridge)")
clock = pygame.time.Clock()

font = pygame.font.SysFont("Segoe UI", 16)
title_font = pygame.font.SysFont("Segoe UI", 22, bold=True)
hud_font = pygame.font.SysFont("Consolas", 14)

# Key mappings to DS3 button names
KEY_MAP = {
    # D-pad
    pygame.K_UP: "UP",
    pygame.K_DOWN: "DOWN",
    pygame.K_LEFT: "LEFT",
    pygame.K_RIGHT: "RIGHT",

    # Face Buttons
    pygame.K_RETURN: "CROSS",
    pygame.K_k: "CROSS",
    pygame.K_x: "CROSS",

    pygame.K_BACKSPACE: "CIRCLE",
    pygame.K_l: "CIRCLE",
    pygame.K_c: "CIRCLE",

    pygame.K_j: "SQUARE",
    pygame.K_z: "SQUARE",

    pygame.K_i: "TRIANGLE",
    pygame.K_v: "TRIANGLE",

    # Shoulders
    pygame.K_q: "L1",
    pygame.K_e: "R1",
    pygame.K_1: "L2",
    pygame.K_2: "R2",

    # System
    pygame.K_SPACE: "START",
    pygame.K_TAB: "SELECT",
    pygame.K_ESCAPE: "PS",
    pygame.K_p: "PS",
}

active_buttons = set()
lx, ly = 128, 128

running = True
print("\n" + "="*50)
print("PS3 KEYBOARD REMOTE ACTIVE!")
print("Controls:")
print("  D-Pad:         Arrow Keys")
print("  Left Stick:    W / A / S / D")
print("  Cross (X):     Enter, K, or X")
print("  Circle (O):    Backspace, L, or C")
print("  Square:        J or Z")
print("  Triangle:      I or V")
print("  L1 / R1:       Q / E")
print("  L2 / R2:       1 / 2")
print("  Start / Select:Space / Tab")
print("  PS Button:     Escape or P")
print("="*50 + "\n")

# Send initial status
send_cmd("STATUS")

while running:
    stick_changed = False

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        elif event.type == pygame.KEYDOWN:
            if event.key in KEY_MAP:
                btn = KEY_MAP[event.key]
                if btn not in active_buttons:
                    active_buttons.add(btn)
                    send_cmd(f"DOWN {btn}")

        elif event.type == pygame.KEYUP:
            if event.key in KEY_MAP:
                btn = KEY_MAP[event.key]
                if btn in active_buttons:
                    active_buttons.remove(btn)
                    send_cmd(f"UP {btn}")

    # Read Left Analog Stick state from W, A, S, D
    keys = pygame.key.get_pressed()
    new_lx = 128
    new_ly = 128

    if keys[pygame.K_w]:
        new_ly = 0
    elif keys[pygame.K_s]:
        new_ly = 255

    if keys[pygame.K_a]:
        new_lx = 0
    elif keys[pygame.K_d]:
        new_lx = 255

    if new_lx != lx or new_ly != ly:
        lx, ly = new_lx, new_ly
        send_cmd(f"STICK L {lx} {ly}")

    # Read any serial feedback
    while ser.in_waiting:
        line = ser.readline().decode("utf-8", errors="ignore").strip()
        if line:
            print(f"[Pico] {line}")

    # Draw UI
    screen.fill((25, 28, 36))

    title = title_font.render("PS3 Controller Remote (Pico 2 Bridge)", True, (255, 255, 255))
    screen.blit(title, (20, 20))

    sub = font.render(f"Connected to {PORT} @ {BAUD} baud | Status: Active", True, (80, 220, 100))
    screen.blit(sub, (20, 55))

    # Instructions box
    instructions = [
        "CONTROLS:",
        "  Arrows   : D-Pad Up / Down / Left / Right",
        "  W,A,S,D  : Left Analog Stick",
        "  Enter / K: Cross (X)",
        "  Backsp / L: Circle (O)",
        "  J / Z    : Square ([ ])",
        "  I / V    : Triangle (/\\)",
        "  Q / E    : L1 / R1",
        "  1 / 2    : L2 / R2",
        "  Space    : Start",
        "  Tab      : Select",
        "  Esc / P  : PS (Home) Button",
    ]

    y_pos = 95
    for inst in instructions:
        txt = hud_font.render(inst, True, (180, 190, 200))
        screen.blit(txt, (25, y_pos))
        y_pos += 22

    # Active Buttons Display Box
    pygame.draw.rect(screen, (35, 40, 52), (370, 95, 240, 340), border_radius=8)
    lbl = font.render("Active Buttons:", True, (255, 220, 100))
    screen.blit(lbl, (385, 110))

    by = 145
    all_btns = ["UP", "DOWN", "LEFT", "RIGHT", "CROSS", "CIRCLE", "SQUARE", "TRIANGLE", "L1", "R1", "L2", "R2", "START", "SELECT", "PS"]
    for b in all_btns:
        is_active = b in active_buttons
        color = (100, 255, 120) if is_active else (80, 90, 105)
        prefix = "[●] " if is_active else "[ ] "
        btxt = hud_font.render(prefix + b, True, color)
        screen.blit(btxt, (390, by))
        by += 18

    # Analog stick HUD
    stxt = hud_font.render(f"L-Stick: ({lx}, {ly})", True, (150, 200, 255))
    screen.blit(stxt, (390, by + 10))

    pygame.display.flip()
    clock.tick(60)

# Cleanup on exit
send_cmd("RELEASE")
ser.close()
pygame.quit()
print("Exited cleanly.")
