import os
import sys
import numpy as np
from PIL import Image, ImageFont, ImageDraw

base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(base_dir, 'tools'))

from test_new_tokens import to_add
FONT_TTF = os.path.join(base_dir, 'Pridi', 'Pridi-Bold.ttf')
CELL_SIZE = 36
TARGET_BASELINE = 31

font = ImageFont.truetype(FONT_TTF, 30)

print(f"Testing glyph rendering for {len(to_add)} tokens...")
for token in to_add:
    cell = Image.new('RGBA', (CELL_SIZE, CELL_SIZE), (0, 0, 0, 0))
    draw = ImageDraw.Draw(cell)
    bbox = font.getbbox(token)
    draw_x = 2 - min(0, bbox[0])
    draw.text((draw_x, TARGET_BASELINE), token, font=font, fill=(255, 255, 255, 255), anchor='ls')
    
    arr = np.array(cell)[:, :, 3]
    coords = np.argwhere(arr > 20)
    if len(coords) == 0:
        print(f"[FAIL] '{token}' rendered 0 pixels!")
    else:
        min_y, min_x = coords.min(axis=0)
        max_y, max_x = coords.max(axis=0)
        w = max_x - min_x + 1
        h = max_y - min_y + 1
        print(f"[OK] '{token:>3s}' -> size {w:2d}x{h:2d} px, bounds x={min_x}..{max_x}, y={min_y}..{max_y}")

print("\n[SUCCESS] All tokens rendered with non-zero pixels!")
