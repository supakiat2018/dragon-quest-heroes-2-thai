import os
import numpy as np
from PIL import Image, ImageFont, ImageDraw

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FONT_TTF = os.path.join(BASE_DIR, "Pridi", "Pridi-Bold.ttf")

CELL_SIZE = 36
font = ImageFont.truetype(FONT_TTF, 30)

THAI_TOKENS = [
    'เ', 'ริ่', 'ม', 'ก', 'า', 'ร', 'ดิ', 'น', 'ท', 'ง',
    'ส', 'ร้', 'บั', 'ทึ', 'ล', 'บ', 'ตั้', 'ค่', 'ฟิ', 'คี',
    'ย์', 'อ', 'ร์', 'ด', 'ส์', 'จ'
]

print(f"Total tokens: {len(THAI_TOKENS)}")

cells = []
for t in THAI_TOKENS:
    c = Image.new('RGBA', (CELL_SIZE, CELL_SIZE), (0, 0, 0, 0))
    d = ImageDraw.Draw(c)
    # anchor="ms" aligns middle horizontally, baseline vertically
    d.text((CELL_SIZE // 2, 27), t, font=font, fill=(255, 255, 255, 255), anchor="ms")
    
    arr = np.array(c)[:, :, 3]
    coords = np.argwhere(arr > 30)
    if len(coords) > 0:
        y0, x0 = coords.min(axis=0)
        y1, x1 = coords.max(axis=0)
        h = y1 - y0 + 1
        w = x1 - x0 + 1
        print(f"'{t:>3s}': y=({y0:2d}..{y1:2d}) h={h:2d}, x=({x0:2d}..{x1:2d}) w={w:2d}")
    cells.append(c)

# Save preview grid of all 26
preview = Image.new('RGBA', (CELL_SIZE * len(THAI_TOKENS), CELL_SIZE), (30, 30, 30, 255))
for i, c in enumerate(cells):
    preview.paste(c, (i * CELL_SIZE, 0), c)

out_p = os.path.join(BASE_DIR, "workspace", "preview_26_thai_menu_tokens.png")
preview.save(out_p)
print(f"Saved preview: {out_p}")
