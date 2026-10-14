import os
from PIL import Image, ImageFont, ImageDraw

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FONT_TTF = os.path.join(BASE_DIR, "Pridi", "Pridi-Bold.ttf")

# Let's simulate the 7 menu items rendered in Chinese CJK spacing vs Thai natural spacing
menu_items = [
    ("เริ่มการเดินทาง", ["เ", "ริ่", "ม", "ก", "า", "ร", "เ", "ดิ", "น", "ท", "า", "ง"]),
    ("สร้างบันทึก", ["ส", "ร้", "า", "ง", "บั", "น", "ทึ", "ก"]),
    ("ลบบันทึก", ["ล", "บ", "บั", "น", "ทึ", "ก"]),
    ("ตั้งค่ากราฟิก", ["ตั้", "ง", "ค่", "า", "ก", "ร", "า", "ฟิ", "ก"]),
    ("ตั้งค่าคีย์บอร์ด", ["ตั้", "ง", "ค่", "า", "คี", "ย์", "บ", "อ", "ร์", "ด"]),
    ("ตั้งค่าเมาส์", ["ตั้", "ง", "ค่", "า", "เ", "ม", "า", "ส์"]),
    ("ออกจากเกม", ["อ", "อ", "ก", "จ", "า", "ก", "เ", "ก", "ม"])
]

# We will test two rendering styles in the 36x36 cell:
# Style A: Each character centered in 36x36 cell (Standard CJK monospace)
# Style B: Left-aligned with natural width (if CJK is strict monospace, spacing might look like monospace Thai)

# Let's render Style A (Standard CJK monospace 36px per character)
font = ImageFont.truetype(FONT_TTF, 30)

W = 600
H = 36 * len(menu_items) * 2
img = Image.new('RGBA', (W, H), (20, 24, 32, 255))
draw = ImageDraw.Draw(img)

y = 20
for text, clusters in menu_items:
    # Monospace CJK simulation (advance = 36px per cluster)
    draw.text((20, y - 15), f"{text} (CJK Monospace - {len(clusters)} chars):", fill=(150, 180, 220, 255))
    x = 20
    for cl in clusters:
        # Draw box
        draw.rectangle([x, y, x + 35, y + 35], outline=(60, 70, 90, 255))
        # Draw cluster centered
        draw.text((x + 18, y + 27), cl, font=font, fill=(255, 255, 255, 255), anchor="ms")
        x += 36
    y += 70

out_p = os.path.join(BASE_DIR, "workspace", "cjk_thai_menu_simulation.png")
img.save(out_p)
print(f"Saved menu simulation to: {out_p}")
