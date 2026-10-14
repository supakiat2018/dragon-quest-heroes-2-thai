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

show(29, 18, "開 (Row 29, Col 18)")
show(10, 107, "始 (Row 10, Col 107)")
show(27, 106, "結 (Row 27, Col 106)")
show(9, 8, "束 (Row 9, Col 8)")
