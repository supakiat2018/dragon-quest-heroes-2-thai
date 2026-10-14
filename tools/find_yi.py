from PIL import Image
import numpy as np

img = Image.open('workspace/tex_340/entry_340.TEX0.dxt5.dds')

# Where is 0xA440 ('一')?
# '一' has only 1 horizontal stroke around y=16..20, with almost no other pixels.
candidates = []
for r in range(5):
    for c in range(113):
        cell = np.array(img.crop((c*36, r*36, (c+1)*36, (r+1)*36)))[:, :, 3]
        cnt = np.count_nonzero(cell > 30)
        if 80 < cnt < 180:
            coords = np.argwhere(cell > 30)
            if len(coords) > 0:
                y0, x0 = coords.min(axis=0)
                y1, x1 = coords.max(axis=0)
                h = y1 - y0 + 1
                w = x1 - x0 + 1
                if h <= 6 and w >= 20: # horizontal bar
                    candidates.append((r, c, cnt, w, h, y0))

print(f"Candidates for '一' (horizontal bar):")
for cand in candidates:
    print(f"  Row {cand[0]}, Col {cand[1]}: w={cand[3]}, h={cand[4]}, y={cand[5]}")
