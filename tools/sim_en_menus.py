import os
from PIL import Image, ImageFont, ImageDraw
import numpy as np

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FONT_TTF = os.path.join(BASE_DIR, "Pridi", "Pridi-Bold.ttf")

# Cyrillic slots mapping
# slot_info: (char, (row, col), orig_w, orig_x0)
SLOTS = {
    'เ':  {'char': '\u0433', 'cell': (14,  3), 'orig_w': 16, 'x0': 2}, # г
    'า':  {'char': '\u0435', 'cell': (14,  5), 'orig_w': 18, 'x0': 1}, # е
    'ร':  {'char': '\u044C', 'cell': (15, 14), 'orig_w': 17, 'x0': 2}, # ь
    'ร้': {'char': '\u0441', 'cell': (15,  2), 'orig_w': 18, 'x0': 1}, # с
    'ร์': {'char': '\u0442', 'cell': (15,  3), 'orig_w': 19, 'x0': 2}, # т
    'จ':  {'char': '\u0432', 'cell': (14,  2), 'orig_w': 18, 'x0': 2}, # в
    'ก':  {'char': '\u0430', 'cell': (14,  0), 'orig_w': 20, 'x0': 1}, # а
    'ม':  {'char': '\u043E', 'cell': (14, 15), 'orig_w': 20, 'x0': 2}, # о
    'น':  {'char': '\u0438', 'cell': (14,  9), 'orig_w': 20, 'x0': 1}, # и
    'ด':  {'char': '\u043A', 'cell': (14, 11), 'orig_w': 21, 'x0': 2}, # к
    'ท':  {'char': '\u043D', 'cell': (14, 14), 'orig_w': 21, 'x0': 1}, # н
    'ง':  {'char': '\u043F', 'cell': (15,  0), 'orig_w': 21, 'x0': 1}, # п
    'ส':  {'char': '\u0440', 'cell': (15,  1), 'orig_w': 20, 'x0': 2}, # р
    'ล':  {'char': '\u043B', 'cell': (14, 12), 'orig_w': 22, 'x0': 1}, # л
    'บ':  {'char': '\u0434', 'cell': (14,  4), 'orig_w': 22, 'x0': 2}, # д
    'อ':  {'char': '\u0443', 'cell': (15,  4), 'orig_w': 22, 'x0': 1}, # у
    'ริ่': {'char': '\u043C', 'cell': (14, 13), 'orig_w': 24, 'x0': 2}, # м
    'ดิ': {'char': '\u0411', 'cell': (11,  1), 'orig_w': 23, 'x0': 1}, # Б
    'ค่': {'char': '\u0415', 'cell': (11,  5), 'orig_w': 23, 'x0': 1}, # Е
    'คี': {'char': '\u0412', 'cell': (11,  2), 'orig_w': 23, 'x0': 2}, # В
    'ฟิ': {'char': '\u0401', 'cell': (11,  6), 'orig_w': 24, 'x0': 1}, # Ё
    'ตั้': {'char': '\u044E', 'cell': (15, 12), 'orig_w': 26, 'x0': 2}, # ю
    'บั': {'char': '\u044F', 'cell': (15, 15), 'orig_w': 26, 'x0': 2}, # я
    'ทึ': {'char': '\u0447', 'cell': (15,  9), 'orig_w': 27, 'x0': 1}, # ч
    'ย์': {'char': '\u0410', 'cell': (11,  0), 'orig_w': 28, 'x0': 1}, # А
    'ส์': {'char': '\u0448', 'cell': (15, 10), 'orig_w': 28, 'x0': 1}, # ш
}

font = ImageFont.truetype(FONT_TTF, 30)

# Simulate menu strings
menus = [
    ("เริ่มการเดินทาง", ['เ', 'ริ่', 'ม', 'ก', 'า', 'ร', 'เ', 'ดิ', 'น', 'ท', 'า', 'ง']),
    ("สร้างบันทึก",     ['ส', 'ร้', 'า', 'ง', 'บั', 'น', 'ทึ', 'ก']),
    ("ลบบันทึก",       ['ล', 'บ', 'บั', 'น', 'ทึ', 'ก']),
    ("ตั้งค่ากราฟิก",   ['ตั้', 'ง', 'ค่', 'า', 'ก', 'ร', 'า', 'ฟิ', 'ก']),
    ("ตั้งค่าคีย์บอร์ด", ['ตั้', 'ง', 'ค่', 'า', 'คี', 'ย์', 'บ', 'อ', 'ร์', 'ด']),
    ("ตั้งค่าเมาส์",     ['ตั้', 'ง', 'ค่', 'า', 'เ', 'ม', 'า', 'ส์']),
    ("ออกจากเกม",     ['อ', 'อ', 'ก', 'จ', 'า', 'ก', 'เ', 'ก', 'ม']),
]

sim_img = Image.new('RGBA', (500, 350), (20, 24, 32, 255))
draw = ImageDraw.Draw(sim_img)

y = 20
for title, tokens in menus:
    x = 20
    for t in tokens:
        slot = SLOTS[t]
        orig_w = slot['orig_w']
        x0 = slot['x0']
        
        # In engine proportional rendering:
        # The character is drawn at x, and the cursor advances by orig_w + tracking (e.g. 1px)
        bbox = font.getbbox(t)
        gw = bbox[2] - bbox[0]
        # Align within orig_w
        glyph_x = x + max(0, (orig_w - gw) // 2)
        draw.text((glyph_x, y), t, font=font, fill=(255, 255, 255, 255))
        x += orig_w + 1 # advance width!
    y += 45

out_p = os.path.join(BASE_DIR, "workspace", "preview_en_proportional_menus.png")
sim_img.save(out_p)
print(f"Saved simulated menu to: {out_p}")
