import os
import sys

base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(base_dir, 'tools'))

from exact_cyrillic_table import CYR_MAP
from test_full_graphics_plan import full_graphics_strings

# We have 66 Russian Cyrillic characters available:
# 33 UPPER + 33 LOWER
# Let's define the comprehensive mapping table for all characters/ligatures:

FULL_SLOTS = {
    # 1. Standard base characters & single vowels
    'เ':  {'char': '\u0433', 'cell': (14,  3), 'w': 11.0}, # г (11px)
    'า':  {'char': '\u0435', 'cell': (14,  5), 'w': 15.0}, # е (15px)
    'ก':  {'char': '\u0430', 'cell': (14,  0), 'w': 19.0}, # а (19px)
    'จ':  {'char': '\u0432', 'cell': (14,  2), 'w': 17.0}, # в (17px)
    'ด':  {'char': '\u043A', 'cell': (14, 11), 'w': 19.0}, # к (19px)
    'บ':  {'char': '\u0434', 'cell': (14,  4), 'w': 19.0}, # д (19px)
    'ล':  {'char': '\u043B', 'cell': (14, 12), 'w': 18.0}, # л (18px)
    'น':  {'char': '\u0438', 'cell': (14,  9), 'w': 19.0}, # и (19px)
    'ท':  {'char': '\u043D', 'cell': (14, 14), 'w': 19.0}, # н (19px)
    'ม':  {'char': '\u043E', 'cell': (14, 15), 'w': 19.0}, # о (19px)
    'ง':  {'char': '\u0431', 'cell': (14,  1), 'w': 17.0}, # б (17px)
    'ส':  {'char': '\u0440', 'cell': (15,  1), 'w': 19.0}, # р (19px)
    'อ':  {'char': '\u0443', 'cell': (15,  4), 'w': 18.0}, # у (18px)
    'ร':  {'char': '\u044C', 'cell': (15, 13), 'w': 16.0}, # ь (16px)
    'ใ':  {'char': '\u0437', 'cell': (14,  8), 'w': 14.0}, # з (14px)
    'แ':  {'char': '\u041D', 'cell': (11, 14), 'w': 17.0}, # Н (17px)
    'โ':  {'char': '\u0424', 'cell': (12,  5), 'w': 14.0}, # Ф (14px)
    'ไ':  {'char': '\u0425', 'cell': (12,  6), 'w': 15.0}, # Х (15px)
    'ะ':  {'char': '\u041E', 'cell': (11, 15), 'w': 14.0}, # О (14px)
    'ว':  {'char': '\u0444', 'cell': (15,  5), 'w': 14.0}, # ф (14px)
    'ห':  {'char': '\u042E', 'cell': (12, 15), 'w': 18.0}, # Ю (18px)
    'ย':  {'char': '\u0428', 'cell': (12,  9), 'w': 18.0}, # Ш (18px)
    'ป':  {'char': '\u042B', 'cell': (12, 12), 'w': 18.0}, # Ы (18px)
    'ต':  {'char': '\u0439', 'cell': (14, 10), 'w': 17.0}, # й (17px)
    'ค':  {'char': '\u0429', 'cell': (12, 10), 'w': 18.0}, # Щ (18px)
    'พ':  {'char': '\u041A', 'cell': (11, 11), 'w': 18.0}, # К (18px)
    'ฟ':  {'char': '\u0426', 'cell': (12,  7), 'w': 18.0}, # Ц (18px)
    'ภ':  {'char': '\u0419', 'cell': (11, 10), 'w': 18.0}, # Й (18px)
    'ณ':  {'char': '\u0418', 'cell': (11,  9), 'w': 24.0}, # И (24px)
    'ช':  {'char': '\u041F', 'cell': (12,  0), 'w': 18.0}, # П (18px)
    'ฉ':  {'char': '\u043C', 'cell': (14, 13), 'w': 18.0}, # м (18px)
    'ผ':  {'char': '\u0423', 'cell': (12,  4), 'w': 18.0}, # У (18px)
    'ศ':  {'char': '\u0427', 'cell': (12,  8), 'w': 18.0}, # Ч (18px)
    'ธ':  {'char': '\u042D', 'cell': (12, 14), 'w': 18.0}, # Э (18px)
    'ข':  {'char': '\u0414', 'cell': (11,  4), 'w': 18.0}, # Д (18px)
    'ญ':  {'char': '\u0416', 'cell': (11,  7), 'w': 24.0}, # Ж (24px)
    'ถ':  {'char': '\u0417', 'cell': (11,  8), 'w': 18.0}, # З (18px)

    # 2. Pre-composed syllables with Sara Am (แก้ปัญหาสระ ำ ไม่ให้แยกเป็นวงกลมลอย!)
    'ต่ำ': {'char': '\u042C', 'cell': (12, 13), 'w': 26.0}, # Ь (26px) - ต + ่ + ำ สมบูรณ์แบบ
    'ลำ':  {'char': '\u0421', 'cell': (12,  2), 'w': 26.0}, # С (26px) - ล + ำ สมบูรณ์แบบ
    'จำ':  {'char': '\u0422', 'cell': (12,  3), 'w': 25.0}, # Т (25px) - จ + ำ สมบูรณ์แบบ
    'กำ':  {'char': '\u042A', 'cell': (12, 11), 'w': 26.0}, # Ъ (26px) - ก + ำ สมบูรณ์แบบ

    # 3. Pre-composed syllables with tone marks & stacked vowels
    'ตั้': {'char': '\u044A', 'cell': (15, 11), 'w': 20.0}, # ъ (20px)
    'ริ่': {'char': '\u044D', 'cell': (15, 14), 'w': 16.0}, # э (16px)
    'ดิ':  {'char': '\u0411', 'cell': (11,  1), 'w': 19.0}, # Б (19px)
    'ค่':  {'char': '\u0413', 'cell': (11,  3), 'w': 19.0}, # Г (19px)
    'คี':  {'char': '\u0412', 'cell': (11,  2), 'w': 19.0}, # В (19px)
    'ฟิ':  {'char': '\u0415', 'cell': (11,  5), 'w': 19.0}, # Е (19px)
    'ทึ':  {'char': '\u0447', 'cell': (15,  8), 'w': 19.0}, # ч (19px)
    'บั':  {'char': '\u0420', 'cell': (12,  1), 'w': 20.0}, # Р (20px)
    'ย์':  {'char': '\u0410', 'cell': (11,  0), 'w': 20.0}, # А (20px)
    'ส์':  {'char': '\u0448', 'cell': (15,  9), 'w': 20.0}, # ш (20px)
    'ต้':  {'char': '\u0445', 'cell': (15,  6), 'w': 19.0}, # х (19px)
    'ช่':  {'char': '\u0451', 'cell': (14,  6), 'w': 18.0}, # ё (18px)
    'ร้':  {'char': '\u0441', 'cell': (15,  2), 'w': 17.0}, # с (17px)
    'ร์':  {'char': '\u0442', 'cell': (15,  3), 'w': 17.0}, # т (17px)
    'ยื':  {'char': '\u044E', 'cell': (15, 15), 'w': 18.0}, # ю (18px)
    'ยั':  {'char': '\u0401', 'cell': (11,  6), 'w': 19.0}, # Ё (19px)
    'คื':  {'char': '\u0436', 'cell': (14,  7), 'w': 18.0}, # ж (18px)
    'คุ':  {'char': '\u0446', 'cell': (15,  7), 'w': 18.0}, # ц (18px)
    'มิ':  {'char': '\u0449', 'cell': (15, 10), 'w': 18.0}, # щ (18px)
    'ติ':  {'char': '\u044B', 'cell': (15, 12), 'w': 18.0}, # ы (18px)
    'ปิ':  {'char': '\u044F', 'cell': (16,  0), 'w': 18.0}, # я (18px)
    'สู':  {'char': '\u042F', 'cell': (13,  0), 'w': 18.0}, # Я (18px)
    'ทิ':  {'char': '\u041C', 'cell': (11, 13), 'w': 19.0}, # М (19px)
    'นุ':  {'char': '\u041B', 'cell': (11, 12), 'w': 18.0}, # Л (18px)
    'จุ':  {'char': '\u043F', 'cell': (15,  0), 'w': 16.0}, # п (16px)
}

print(f"Total tokens defined in FULL_SLOTS: {len(FULL_SLOTS)}")

# Verify all Cyrillic characters are unique
cyr_chars = [v['char'] for v in FULL_SLOTS.values()]
assert len(cyr_chars) == len(set(cyr_chars)), "Duplicate Cyrillic characters found!"
print("[+] All Cyrillic character mappings are 100% unique!")

SORTED_TOKENS = sorted(FULL_SLOTS.keys(), key=len, reverse=True)

def encode_thai(text):
    res = []
    i = 0
    while i < len(text):
        matched = False
        for t in SORTED_TOKENS:
            if text.startswith(t, i):
                res.append(FULL_SLOTS[t]['char'])
                i += len(t)
                matched = True
                break
        if not matched:
            res.append(text[i])
            i += 1
    return "".join(res)

# Test encoding on all graphics strings
print("\n--- Testing Encoding of All Target Strings ---")
unmatched = []
for ptr, s in full_graphics_strings.items():
    enc = encode_thai(s)
    rem = [c for c in enc if '\u0e00' <= c <= '\u0e7f']
    if rem:
        print(f"[-] Ptr {ptr}: '{s}' -> Missing: {rem}")
        unmatched.extend(rem)
    else:
        print(f"[OK] Ptr {ptr}: '{s}' -> {len(enc)} chars")

if not unmatched:
    print("\n[SUCCESS] 100% of all target strings encoded cleanly without any missing characters!")
else:
    print(f"\n[-] Unmatched characters count: {len(set(unmatched))}: {sorted(set(unmatched))}")
