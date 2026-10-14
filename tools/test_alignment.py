from PIL import Image
import numpy as np

img = Image.open('workspace/tex_340/entry_340.TEX0.dxt5.dds')

def show(r, c, title=""):
    cell = np.array(img.crop((c*36, r*36, (c+1)*36, (r+1)*36)))[:, :, 3]
    print(f"=== {title} (R={r}, C={c}) ===")
    for y in range(0, 36, 2):
        line = ''.join(['#' if cell[y, x] > 50 else '.' for x in range(0, 36, 2)])
        if '#' in line:
            print(f"{y:2d}: {line}")

# If index 110 is R=0, C=110, in Big5 index 110 is 0xA1D0: '－' (Minus sign)
show(0, 110, "Index 110 (Expected: －)")
# Index 111 is 0xA1D1: '×' (Multiply sign)
show(0, 111, "Index 111 (Expected: ×)")
# Index 112 is 0xA1D2: '÷' (Divide sign)
show(0, 112, "Index 112 (Expected: ÷)")
# Index 113 is R=1, C=0 (Expected: ±)
show(1, 0, "Index 113 (Expected: ±)")
# Index 114 is R=1, C=1 (Expected: √)
show(1, 1, "Index 114 (Expected: √)")
