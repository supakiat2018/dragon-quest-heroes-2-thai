import os
import sys

base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(base_dir, 'tools'))

from exact_cyrillic_table import CYR_MAP

# 66 Cyrillic characters list
CYR_CHARS = list(CYR_MAP.keys())
print(f"Total available Cyrillic characters: {len(CYR_CHARS)}")

# All 25 Graphics Settings screen strings
graphics_screen_strings = {
    # 7 Main menus
    4032: 'เริ่มการเดินทาง',
    4036: 'สร้างบันทึก',
    4040: 'ลบบันทึก',
    6800: 'ตั้งค่ากราฟิก',
    6804: 'ตั้งค่าคีย์บอร์ด',
    7092: 'ตั้งค่าเมาส์',
    6808: 'ออกจากเกม',
    
    # Dialogue prompt
    32: 'ต้องการสร้างบันทึกการเดินทางในช่องใด?',
    
    # Graphics settings full list
    6812: 'แสดงผลเต็มจอ',
    6816: 'ความละเอียด',
    6820: 'เฟรมเรต',
    6824: 'คุณภาพกราฟิก',
    6828: '  จำนวนตัวละคร',
    6832: '  ระยะแสดงผล',
    6836: '  คุณภาพพื้นผิว',
    6840: '  คุณภาพเงา',
    6844: '  มิติแสงเงา',
    6848: '  การสะท้อนแสง',
    6852: '  ลำแสงส่องกระทบ',
    6856: '  ละอองอนุภาค',
    6860: '  แสงรอบทิศทาง',
    6864: 'เลือกว่าจะแสดงผลแบบเต็มจอหรือหน้าต่าง',
    6928: 'เปิด',
    6932: 'ปิด',
    6936: 'สูง',
    6940: 'ปานกลาง',
    6944: 'ต่ำ',
    6948: 'กำหนดเอง',
    7192: 'เปลี่ยนความละเอียด',
    7228: '  หมอกเชิงปริมาตร',
    7232: '  เงาแสงเฉพาะจุด',
    4628: 'คืนค่าเริ่มต้น',
    4108: 'ยืนยัน',
    7244: 'ยืนยันการตั้งค่ากราฟิก',
}

# Tokens definition:
# We carefully order and choose tokens so that:
# 1. 'ต่ำ' is ONE SINGLE TOKEN (no more 'ต่ ำ'!)
# 2. 'ลำ' is ONE SINGLE TOKEN
# 3. 'จำ' is ONE SINGLE TOKEN
# 4. 'กำ' is ONE SINGLE TOKEN
# 5. Composite tone syllables are ONE SINGLE TOKEN

TOKENS_LIST = [
    # Sara Am (ำ) unified tokens:
    ('ต่ำ', 26.0),
    ('ลำ', 26.0),
    ('จำ', 25.0),
    ('กำ', 26.0),
    
    # Stacked tone syllables:
    ('ตั้', 20.0),
    ('ริ่', 16.0),
    ('ดิ', 19.0),
    ('ค่', 19.0),
    ('คี', 19.0),
    ('ฟิ', 19.0),
    ('ทึ', 19.0),
    ('บั', 20.0),
    ('ย์', 20.0),
    ('ส์', 20.0),
    ('ต้', 19.0),
    ('ช่', 18.0),
    ('ร้', 17.0),
    ('ร์', 17.0),
    ('ยื', 18.0),
    ('ยั', 19.0),
    ('คื', 18.0),
    ('คุ', 18.0),
    ('มิ', 18.0),
    ('ติ', 18.0),
    ('ปิ', 18.0),
    ('สู', 18.0),
    ('ทิ', 19.0),
    ('นุ', 18.0),
    ('จุ', 16.0),
    ('เต็', 20.0),
    ('เอี', 24.0),
    ('ตั', 18.0),
    ('พื้', 20.0),
    ('ผิ', 18.0),
    ('เลื', 22.0),
    ('น้', 18.0),
    ('ว่', 16.0),
    ('ต่', 18.0),
    ('ชิ', 18.0),
    ('ริ', 18.0),
    ('ท้', 19.0),
    ('ส่', 18.0),
    ('วั', 18.0),
    
    # Single base characters & vowels:
    ('เ', 11.0),
    ('า', 15.0),
    ('ก', 19.0),
    ('จ', 17.0),
    ('ด', 19.0),
    ('บ', 19.0),
    ('ล', 18.0),
    ('น', 19.0),
    ('ท', 19.0),
    ('ม', 19.0),
    ('ง', 17.0),
    ('ส', 19.0),
    ('อ', 18.0),
    ('ร', 16.0),
    ('ใ', 14.0),
    ('แ', 17.0),
    ('ะ', 14.0),
    ('ว', 14.0),
    ('ห', 18.0),
    ('ย', 18.0),
    ('ป', 18.0),
    ('ต', 17.0),
    ('ค', 18.0),
    ('พ', 18.0),
    ('ฟ', 18.0),
    ('ภ', 18.0),
    ('ณ', 24.0),
    ('ผ', 18.0),
]

print(f"Total tokens defined: {len(TOKENS_LIST)} (available slots: {len(CYR_CHARS)})")
assert len(TOKENS_LIST) <= len(CYR_CHARS), f"Too many tokens ({len(TOKENS_LIST)} > {len(CYR_CHARS)})"

# Build mapping
FINAL_MAP = {}
for i, (tok, w) in enumerate(TOKENS_LIST):
    ch = CYR_CHARS[i]
    cell = CYR_MAP[ch]
    FINAL_MAP[tok] = {
        'char': ch,
        'cell': cell,
        'w': w
    }

SORTED_TOKENS = sorted(FINAL_MAP.keys(), key=len, reverse=True)

def encode_text(s):
    res = []
    i = 0
    while i < len(s):
        matched = False
        for t in SORTED_TOKENS:
            if s.startswith(t, i):
                res.append(FINAL_MAP[t]['char'])
                i += len(t)
                matched = True
                break
        if not matched:
            res.append(s[i])
            i += 1
    return "".join(res)

print("\n--- Verifying All Graphics Screen Strings ---")
all_ok = True
for ptr, s in graphics_screen_strings.items():
    enc = encode_text(s)
    rem = [c for c in enc if '\u0e00' <= c <= '\u0e7f']
    if rem:
        print(f"[-] Ptr {ptr}: '{s}' -> Missing: {rem}")
        all_ok = False
    else:
        print(f"[OK] Ptr {ptr:4d}: '{s}' -> {len(enc)} chars ({len(enc.encode('utf-8'))} bytes)")

if all_ok:
    print("\n[SUCCESS] 100% OF ALL GRAPHICS SCREEN STRINGS ENCODED FLAWLESSLY!")
