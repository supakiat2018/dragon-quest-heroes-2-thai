import os
import sys
import numpy as np
from PIL import Image, ImageFont, ImageDraw

base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(base_dir, 'tools'))

from exact_cyrillic_table import CYR_MAP
from mod_en_thai_menus import SLOTS, render_unstretched_glyph, FONT_TTF, CELL_SIZE, TARGET_BASELINE

# List of all tokens needed for Graphics Settings screen:
# 1. ยืนยัน: 'ยื', 'น', 'ยั', 'น'
# 2. คืนค่าเริ่มต้น: 'คื', 'น', 'ค่', 'า', 'เ', 'ริ่', 'ม', 'ต้', 'น'
# 3. คุณภาพเงา: 'คุ', 'ณ', 'ภ', 'า', 'พ', 'เ', 'ง', 'า'
# 4. มิติแสงเงา: 'มิ', 'ติ', 'แ', 'ส', 'ง', 'เ', 'ง', 'า'
# 5. การสะท้อนแสง: 'ก', 'า', 'ร', 'ส', 'ะ', 'ท้', 'อ', 'น', 'แ', 'ส', 'ง'
# 6. ลำแสงส่องกระทบ: 'ลำ', 'แ', 'ส', 'ง', 'ส่', 'อ', 'ง', 'ก', 'ร', 'ะ', 'ท', 'บ'
# 7. ละอองอนุภาค: 'ล', 'ะ', 'อ', 'อ', 'ง', 'อ', 'นุ', 'ภ', 'า', 'ค'
# 8. แสงธรรมชาติรอบทิศทาง: 'แ', 'ส', 'ง', 'ธ', 'ร', 'ร', 'ม', 'ช', 'า', 'ติ', 'ร', 'อ', 'บ', 'ทิ', 'ศ', 'ท', 'า', 'ง'
# 9. เปิด / ปิด: 'เ', 'ปิ', 'ด' / 'ปิ', 'ด'
# 10. สูง / ปานกลาง / ต่ำ: 'สู', 'ง' / 'ป', 'า', 'น', 'ก', 'ล', 'า', 'ง' / 'ต่', 'ำ'
# 11. หมอกเชิงปริมาตร: 'ห', 'ม', 'อ', 'ก', 'เ', 'ชิ', 'ง', 'ป', 'ริ', 'ม', 'า', 'ต', 'ร'
# 12. เงาจากแสงเฉพาะจุด: 'เ', 'ง', 'า', 'จ', 'า', 'ก', 'แ', 'ส', 'ง', 'เ', 'ฉ', 'พ', 'า', 'ะ', 'จุ', 'ด'
# 13. ยืนยันการตั้งค่ากราฟิก: 'ยื', 'น', 'ยั', 'น', 'ก', 'า', 'ร', 'ตั้', 'ง', 'ค่', 'า', 'ก', 'ร', 'า', 'ฟิ', 'ก'

needed_new_tokens = [
    'ยื', 'ยั', 'คื', 'คุ', 'ณ', 'ภ', 'พ', 'มิ', 'ติ', 'แ', 'ะ', 'ท้',
    'ลำ', 'ส่', 'นุ', 'ค', 'ธ', 'ช', 'ทิ', 'ศ', 'ปิ', 'สู', 'ป', 'ต่', 'ำ',
    'ห', 'เ', 'ชิ', 'ริ', 'ต', 'ฉ', 'จุ', 'ว', 'วั'
]

# Filter out tokens already in SLOTS
to_add = [t for t in needed_new_tokens if t not in SLOTS]
print(f"Total new tokens to add: {len(to_add)}")
print(to_add)

# Find free Cyrillic characters
used_chars = set(v['char'] for v in SLOTS.values())
free_cyr = []
for ch, cell in sorted(CYR_MAP.items(), key=lambda x: (x[1][0], x[1][1])):
    if ch not in used_chars:
        free_cyr.append((ch, cell))

print(f"Available free Cyrillic slots: {len(free_cyr)}")
assert len(to_add) <= len(free_cyr), f"Too many tokens ({len(to_add)} > {len(free_cyr)})"

mapping_new = {}
for i, token in enumerate(to_add):
    ch, cell = free_cyr[i]
    mapping_new[token] = {'char': ch, 'cell': cell}
    print(f"Mapped token '{token:>3s}' -> Cyrillic '{ch}' ({ord(ch):#06x}), Row {cell[0]}, Col {cell[1]}")
