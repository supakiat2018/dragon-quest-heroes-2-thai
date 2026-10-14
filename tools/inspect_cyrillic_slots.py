from PIL import Image
import numpy as np

img = Image.open('workspace/tex_342/entry_342.png')
CELL_SIZE = 36
COLS = 16

# In entry_342, let's inspect Row 11 to 16
print("Row 11..16 original Cyrillic glyph bounding boxes:")
for r in range(11, 17):
    row_info = []
    for c in range(16):
        cell = np.array(img.crop((c*CELL_SIZE, r*CELL_SIZE, (c+1)*CELL_SIZE, (r+1)*CELL_SIZE)))[:, :, 3]
        coords = np.argwhere(cell > 30)
        if len(coords) > 0:
            y0, x0 = coords.min(axis=0)
            y1, x1 = coords.max(axis=0)
            w = x1 - x0 + 1
            h = y1 - y0 + 1
            row_info.append((c, x0, y0, w, h))
        else:
            row_info.append((c, -1, -1, 0, 0))
    print(f"Row {r:2d}:")
    for c, x0, y0, w, h in row_info:
        if w > 0:
            print(f"  Col {c:2d}: x0={x0:2d}, y0={y0:2d}, w={w:2d}, h={h:2d}")
