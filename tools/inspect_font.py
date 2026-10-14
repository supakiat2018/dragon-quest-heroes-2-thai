import os
from PIL import Image
import numpy as np

img = Image.open('workspace/tex_340/entry_340.TEX0.dxt5.dds')

def print_brief(r, c):
    cell = np.array(img.crop((c*36, r*36, (c+1)*36, (r+1)*36)))[:, :, 3]
    cnt = np.count_nonzero(cell > 30)
    lines = []
    for y in range(4, 32, 5):
        line = ''.join(['#' if cell[y, x] > 50 else '.' for x in range(4, 32, 2)])
        lines.append(line)
    print(f"R={r:2d}, C={c:2d} (cnt={cnt:3d}): {' | '.join(lines)}")

print("=== First column of Rows 0..15 ===")
for r in range(16):
    print_brief(r, 0)
