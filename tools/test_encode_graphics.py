import os
import sys

base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(base_dir, 'tools'))

from mod_en_thai_menus import SLOTS
from test_new_tokens import mapping_new

# Combine SLOTS and mapping_new
ALL_SLOTS = {}
for k, v in SLOTS.items():
    ALL_SLOTS[k] = v['char']
for k, v in mapping_new.items():
    ALL_SLOTS[k] = v['char']

print(f"Total tokens in ALL_SLOTS: {len(ALL_SLOTS)}")

# Sort tokens by length descending for greedy tokenization
sorted_tokens = sorted(ALL_SLOTS.keys(), key=len, reverse=True)

def encode_thai_string(s):
    res = []
    i = 0
    while i < len(s):
        matched = False
        for t in sorted_tokens:
            if s.startswith(t, i):
                res.append(ALL_SLOTS[t])
                i += len(t)
                matched = True
                break
        if not matched:
            res.append(s[i]) # English / space / punctuation
            i += 1
    return "".join(res)

test_strings = [
    'ยืนยัน',
    'คืนค่าเริ่มต้น',
    '  คุณภาพเงา',
    '  มิติแสงเงา',
    '  การสะท้อนแสง',
    '  ลำแสงส่องกระทบ',
    '  ละอองอนุภาค',
    '  แสงธรรมชาติรอบทิศทาง',
    'เปิด',
    'ปิด',
    'สูง',
    'ปานกลาง',
    'ต่ำ',
    '  หมอกเชิงปริมาตร',
    '  เงาจากแสงเฉพาะจุด',
    'ยืนยันการตั้งค่ากราฟิก'
]

print("\n--- Test String Encoding ---")
all_good = True
for s in test_strings:
    encoded = encode_thai_string(s)
    # Check if any Thai character was left unencoded
    remaining_thai = [c for c in encoded if '\u0e00' <= c <= '\u0e7f']
    if remaining_thai:
        print(f"[FAIL] '{s}' has remaining Thai: {remaining_thai}")
        all_good = False
    else:
        print(f"[OK] '{s}' -> len={len(encoded)} cyr chars ({len(encoded.encode('utf-8'))} UTF-8 bytes)")

if all_good:
    print("\n[SUCCESS] All 16 strings successfully and cleanly encoded into Cyrillic!")
