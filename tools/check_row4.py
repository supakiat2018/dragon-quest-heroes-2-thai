from PIL import Image
import numpy as np

img = Image.open('workspace/tex_340/entry_340.TEX0.dxt5.dds')

# Row 4 is lead byte 0xA5
# Let's inspect columns 60, 61, 62, 63, 64, 65...
# In Big5:
# 0x40 + 62 = 0x7E
# 0x7E is the last byte of range 1!
# What character is at 0xA57E?
ch_7e = bytes([0xA5, 0x7E]).decode('cp950', errors='replace')
print(f"Big5 0xA57E: {ch_7e}")

# What character is at 0xA5A1? (first byte of range 2)
ch_a1 = bytes([0xA5, 0xA1]).decode('cp950', errors='replace')
print(f"Big5 0xA5A1: {ch_a1}")

# What character is at 0xA5FE? (last byte of range 2)
ch_fe = bytes([0xA5, 0xFE]).decode('cp950', errors='replace')
print(f"Big5 0xA5FE: {ch_fe}")

# Let's check non-empty columns in Row 4
row4 = np.array(img.crop((0, 4*36, 4096, 5*36)))[:, :, 3]
counts = [np.count_nonzero(row4[:, c*36:(c+1)*36] > 30) for c in range(114)]
non_empty = [(c, cnt) for c, cnt in enumerate(counts) if cnt > 30]
print(f"Row 4 non-empty count: {len(non_empty)}, max col: {non_empty[-1]}")

# Also check Row 5, Row 6
