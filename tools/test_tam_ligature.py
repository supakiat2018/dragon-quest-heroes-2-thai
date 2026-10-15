import os
import sys
import numpy as np
from PIL import Image, ImageFont, ImageDraw

base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FONT_TTF = os.path.join(base_dir, 'Pridi', 'Pridi-Bold.ttf')
CELL_SIZE = 36
TARGET_BASELINE = 31

font = ImageFont.truetype(FONT_TTF, 30)

# We want 'ต่ำ' as a single unified ligature
cell = Image.new('RGBA', (CELL_SIZE, CELL_SIZE), (0, 0, 0, 0))
draw = ImageDraw.Draw(cell)
draw.text((2, TARGET_BASELINE), 'ต่ำ', font=font, fill=(255, 255, 255, 255), anchor='ls')

arr = np.array(cell)[:, :, 3]
coords = np.argwhere(arr > 20)
min_y, min_x = coords.min(axis=0)
max_y, max_x = coords.max(axis=0)
w = max_x - min_x + 1
h = max_y - min_y + 1
print(f"'ต่ำ' rendered bounds: {w}x{h} px (x={min_x}..{max_x}, y={min_y}..{max_y})")

out_path = os.path.join(base_dir, 'workspace', 'tam_ligature.png')
cell.save(out_path)
print(f"Saved to {out_path}")
