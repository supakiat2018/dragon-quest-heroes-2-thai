from PIL import Image
import numpy as np

img = Image.open('workspace/tex_340/entry_340.TEX0.dxt5.dds')

# Let's verify how Big5 characters map to linear indices.
# We know:
# Row 0, Col 0 is 0xA140 (Linear index 0).
# Row 3, Col 69 is 0xA440 (Linear index 3 * 113 + 69 = 408).
# 408 characters between 0xA140 and 0xA440!
# Let's count how many characters are in 0xA1, 0xA2, 0xA3 in standard Big5:
# In Big5:
# Symbols are in 0xA140..0xA3BF:
# A140..A17E = 63
# A1A1..A1FE = 94 -> Total A1 = 157
# A240..A27E = 63
# A2A1..A2FE = 94? Wait, standard Big5 has A2A1..A2C1 (33)?
# Let's see: how many characters in A1, A2, A3 to make exactly 408 characters?
# 157 (A1) + ? (A2) + ? (A3) = 408!
# Let's check!

def get_glyph_pixel_count(r, c):
    cell = np.array(img.crop((c*36, r*36, (c+1)*36, (r+1)*36)))[:, :, 3]
    return np.count_nonzero(cell > 30)

# Let's check linear indices 400..415:
print("Linear indices around 408 (Row 3, Col 69):")
for idx in range(405, 415):
    r = idx // 113
    c = idx % 113
    cnt = get_glyph_pixel_count(r, c)
    print(f"Linear {idx} (R={r:2d}, C={c:2d}): cnt={cnt}")
