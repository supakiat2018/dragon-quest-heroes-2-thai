from PIL import Image
import numpy as np

img = Image.open('workspace/tex_340/entry_340.TEX0.dxt5.dds')

def show_cell(r, c):
    cell = np.array(img.crop((c*36, r*36, (c+1)*36, (r+1)*36)))[:, :, 3]
    print(f"=== R={r}, C={c} ===")
    for y in range(0, 36, 2):
        line = ''.join(['#' if cell[y, x] > 50 else '.' for x in range(0, 36, 2)])
        if '#' in line:
            print(f"{y:2d}: {line}")

print("Col 62 in Row 4 (Expected 0xA57E: 外):")
show_cell(4, 62)

print("Col 63 in Row 4 (Is it 0xA5A1: 央?):")
show_cell(4, 63)

print("Col 112 in Row 4 (What is at col 112?):")
show_cell(4, 112)
