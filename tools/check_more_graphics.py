import os
import sys

base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(base_dir, 'tools'))

from test_encode_graphics import ALL_SLOTS

# Target strings to translate
new_menu_strings = [
    'แสดงผลแบบเต็มจอ',
    'ความละเอียดหน้าจอ',
    'เฟรมเรต',
    'คุณภาพกราฟิก',
    '  จำนวนตัวละครบนหน้าจอ',
    '  ระยะการเรนเดอร์ภาพ',
    '  พื้นผิวภาพ',
    'กำหนดเอง',
    'เปลี่ยนความละเอียดหน้าจอ',
    'เลือกว่าจะแสดงผลแบบเต็มหน้าจอหรือแบบหน้าต่าง'
]

chars = set(''.join(new_menu_strings))
print("Unique characters in new menu strings:", sorted(chars))

# Let's see which characters or syllables are not yet in ALL_SLOTS
# Remember ALL_SLOTS has:
# SLOTS (29) + mapping_new (33) = 62 tokens
print(f"Current tokens in ALL_SLOTS: {len(ALL_SLOTS)}")

# Let's check remaining Thai characters
rem = []
for s in new_menu_strings:
    i = 0
    while i < len(s):
        matched = False
        for t in sorted(ALL_SLOTS.keys(), key=len, reverse=True):
            if s.startswith(t, i):
                i += len(t)
                matched = True
                break
        if not matched:
            rem.append(s[i])
            i += 1

print("Unmatched characters:", sorted(set(rem)))
