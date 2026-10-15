# -*- coding: utf-8 -*-
"""
translate_weapon_categories.py
Translates entry_00064_Weapon_Categories.csv (119 lines)
"""

import csv

WEAPON_CATEGORIES_THAI = {
    # Twin swords
    0: "ดาบคู่",
    1: "ดาบคู่",
    3: "ดาบคู่",

    # Sword
    8: "ดาบมือเดียว",
    9: "ดาบมือเดียว",
    11: "ดาบมือเดียว",

    # Greatsword
    16: "ดาบใหญ่",
    17: "ดาบใหญ่",
    19: "ดาบใหญ่",

    # Axe
    24: "ขวาน",
    25: "ขวาน",
    27: "ขวาน",

    # Gauntlets
    32: "สนับมือ",
    33: "สนับมือ",
    35: "สนับมือ",

    # Spear
    40: "หอก",
    41: "หอก",
    43: "หอก",

    # Abacus
    48: "ลูกคิด",
    49: "ลูกคิด",
    51: "ลูกคิด",

    # Cards
    56: "ไพ่ทาโรต์",
    57: "ไพ่ทาโรต์",
    59: "ไพ่ทาโรต์",

    # Fans
    64: "พัด",
    65: "พัด",
    67: "พัด",

    # Boomerang
    72: "บูมเมอแรง",
    73: "บูมเมอแรง",
    75: "บูมเมอแรง",

    # Claws
    80: "กรงเล็บ",
    81: "กรงเล็บ",
    83: "กรงเล็บ",

    # Bow
    88: "ธนู",
    89: "ธนู",
    91: "ธนู",

    # Whip
    96: "แส้",
    97: "แส้",
    99: "แส้",

    # Wand
    104: "คทาเวท",
    105: "คทาเวท",
    107: "คทาเวท",

    # Heavy wand
    112: "คทาหนัก",
    113: "คทาหนัก",
    115: "คทาหนัก",

    # Staff
    120: "ไม้เท้า",
    121: "ไม้เท้า",
    123: "ไม้เท้า",

    # Shield
    128: "โล่",
    129: "โล่",
    131: "โล่",
}

def apply_translation():
    file_path = "text_csv/categories/entry_00064_Weapon_Categories.csv"
    with open(file_path, "r", encoding="utf-8-sig") as f:
        rows = list(csv.DictReader(f))
        fieldnames = rows[0].keys()

    updated = 0
    for row_idx, thai_text in WEAPON_CATEGORIES_THAI.items():
        if row_idx < len(rows):
            rows[row_idx]["ThaiTranslation"] = thai_text
            updated += 1

    with open(file_path, "w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    print(f"[SUCCESS] Updated {updated} weapon categories in {file_path}")

if __name__ == "__main__":
    apply_translation()
