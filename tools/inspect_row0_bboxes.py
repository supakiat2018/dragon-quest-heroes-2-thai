from PIL import Image, ImageFont, ImageDraw
import numpy as np

img = Image.open('workspace/tex_340/entry_340.TEX0.dxt5.dds')

# Let's inspect R=0, C=0 to C=20
# Print pixel bounding box (min_x, min_y, max_x, max_y) and count for each cell in Row 0
print("Row 0 cells 0..20:")
for c in range(20):
    cell = np.array(img.crop((c*36, 0, (c+1)*36, 36)))[:, :, 3]
    cnt = np.count_nonzero(cell > 30)
    coords = np.argwhere(cell > 30)
    if len(coords) > 0:
        y0, x0 = coords.min(axis=0)
        y1, x1 = coords.max(axis=0)
        print(f"Col {c:2d}: count={cnt:3d}, bbox=({x0:2d},{y0:2d},{x1:2d},{y1:2d})")
    else:
        print(f"Col {c:2d}: EMPTY")
