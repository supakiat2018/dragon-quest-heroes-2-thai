from PIL import Image
import numpy as np

img = Image.open('backup/entry_342_original.png')

def show(r, c, title=""):
    cell = np.array(img.crop((c*36, r*36, (c+1)*36, (r+1)*36)))[:, :, 3]
    print(f"=== {title} (R={r}, C={c}) ===")
    for y in range(0, 36, 2):
        line = ''.join(['#' if cell[y, x] > 50 else '.' for x in range(0, 36, 2)])
        if '#' in line:
            print(f"{y:2d}: {line}")

show(12, 14, "Row 12, Col 14")
show(12, 15, "Row 12, Col 15")
show(13, 0, "Row 13, Col 0")
show(15, 14, "Row 15, Col 14")
show(15, 15, "Row 15, Col 15")
show(16, 0, "Row 16, Col 0")
