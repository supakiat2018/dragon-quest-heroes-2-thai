# -*- coding: utf-8 -*-
"""
translate_controls.py
Translates entry_00323_Keyboard_Gamepad_Controls.csv (116 lines)
"""

import csv

CONTROLS_THAI = {
    1: 'Esc',
    2: '1',
    3: '2',
    4: '3',
    5: '4',
    6: '5',
    7: '6',
    8: '7',
    9: '8',
    10: '9',
    11: '0',
    12: '-',
    13: '=',
    14: 'Backspace',
    15: 'Tab',
    16: 'Q',
    17: 'W',
    18: 'E',
    19: 'R',
    20: 'T',
    21: 'Y',
    22: 'U',
    23: 'I',
    24: 'O',
    25: 'P',
    26: '[',
    27: ']',
    28: 'Enter',
    29: 'Ctrl ซ้าย',
    30: 'A',
    31: 'S',
    32: 'D',
    33: 'F',
    34: 'G',
    35: 'H',
    36: 'J',
    37: 'K',
    38: 'L',
    39: '<FJ>',
    40: "'",
    41: '`',
    42: 'Shift ซ้าย',
    43: '# (UK) / แบ็กสแลช (US)',
    44: 'Z',
    45: 'X',
    46: 'C',
    47: 'V',
    48: 'B',
    49: 'N',
    50: 'M',
    51: ',',
    52: '.',
    53: 'สแลช (/)',
    54: 'Shift ขวา',
    55: 'Numpad *',
    56: 'Alt ซ้าย',
    57: 'Space',
    58: 'Caps Lock',
    59: 'F1',
    60: 'F2',
    61: 'F3',
    62: 'F4',
    63: 'F5',
    64: 'F6',
    65: 'F7',
    66: 'F8',
    67: 'F9',
    68: 'F10',
    69: 'Num Lock',
    70: 'Scroll Lock',
    71: 'Numpad 7',
    72: 'Numpad 8',
    73: 'Numpad 9',
    74: 'Numpad -',
    75: 'Numpad 4',
    76: 'Numpad 5',
    77: 'Numpad 6',
    78: 'Numpad +',
    79: 'Numpad 1',
    80: 'Numpad 2',
    81: 'Numpad 3',
    82: 'Numpad 0',
    83: 'Numpad .',
    86: 'แบ็กสแลช (UK)',
    87: 'F11',
    88: 'F12',
    100: 'F13',
    101: 'F14',
    102: 'F15',
    112: 'Kana',
    115: 'ABNT_C1',
    121: 'Convert',
    123: 'Non-Convert',
    125: '\\',
    144: '^',
    145: '@',
    146: '<FI>',
    156: 'Numpad Enter',
    157: 'Ctrl ขวา',
    181: 'Numpad /',
    183: 'Print Screen',
    184: 'Alt ขวา',
    197: 'Pause/Break',
    199: 'Home',
    200: 'ลูกศรขึ้น',
    201: 'Page Up',
    203: 'ลูกศรซ้าย',
    205: 'ลูกศรขวา',
    207: 'End',
    208: 'ลูกศรลง',
    209: 'Page Down',
    210: 'Insert',
    211: 'Delete',
    219: 'Win ซ้าย',
    220: 'Win ขวา',
    221: 'ปุ่มเมนู',
}

def apply_translation():
    file_path = "text_csv/categories/entry_00323_Keyboard_Gamepad_Controls.csv"
    with open(file_path, "r", encoding="utf-8-sig") as f:
        rows = list(csv.DictReader(f))
        fieldnames = rows[0].keys()

    updated = 0
    for row_idx, thai_text in CONTROLS_THAI.items():
        if row_idx < len(rows):
            rows[row_idx]["ThaiTranslation"] = thai_text
            updated += 1

    with open(file_path, "w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    print(f"[SUCCESS] Updated {updated} controls keys in {file_path}")

if __name__ == "__main__":
    apply_translation()
