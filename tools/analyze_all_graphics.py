import os
import sys

base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(base_dir, 'tools'))

from exact_cyrillic_table import CYR_MAP
from mod_en_thai_menus import SLOTS
from test_new_tokens import to_add, mapping_new

# Let's inspect all strings we want to encode:
all_graphics_strings = [
    # Main 7
    'เริ่มการเดินทาง',
    'สร้างบันทึก',
    'ลบบันทึก',
    'ตั้งค่ากราฟิก',
    'ตั้งค่าคีย์บอร์ด',
    'ตั้งค่าเมาส์',
    'ออกจากเกม',
    # Dialogue prompts
    'ต้องการสร้างบันทึกการเดินทางในช่องใด?',
    # Graphics settings full list
    'แสดงผลแบบเต็มจอ',
    'ความละเอียดหน้าจอ',
    'เฟรมเรต',
    'คุณภาพกราฟิก',
    '  จำนวนตัวละครบนหน้าจอ',
    '  ระยะการเรนเดอร์ภาพ',
    '  พื้นผิวภาพ',
    '  คุณภาพเงา',
    '  มิติแสงเงา',
    '  การสะท้อนแสง',
    '  ลำแสงส่องกระทบ',
    '  ละอองอนุภาค',
    '  แสงธรรมชาติรอบทิศทาง',
    'เลือกว่าจะแสดงผลแบบเต็มหน้าจอหรือแบบหน้าต่าง',
    'เปิด',
    'ปิด',
    'สูง',
    'ปานกลาง',
    'ต่ำ',
    'กำหนดเอง',
    '  หมอกเชิงปริมาตร',
    '  เงาจากแสงเฉพาะจุด',
    'เปลี่ยนความละเอียดหน้าจอ',
    'ยืนยันการตั้งค่ากราฟิก',
    'คืนค่าเริ่มต้น',
    'ยืนยัน'
]

chars = set(''.join(all_graphics_strings))
print(f"Total unique characters across all graphics screen items: {len(chars)}")
print(sorted(chars))
