from PIL import Image
import numpy as np

img = Image.open('workspace/tex_340/entry_340.TEX0.dxt5.dds')

def big5_to_index(b1, b2):
    if b1 == 0xA1:
        return (b2 - 0x40) if b2 <= 0x7E else (63 + b2 - 0xA1)
    elif b1 == 0xA2:
        return 157 + ((b2 - 0x40) if b2 <= 0x7E else (63 + b2 - 0xA1))
    elif b1 == 0xA3:
        return 314 + ((b2 - 0x40) if b2 <= 0x7E else (63 + b2 - 0xA1))
    else:
        base = 408 + (b1 - 0xA4) * 157
        offset = (b2 - 0x40) if b2 <= 0x7E else (63 + b2 - 0xA1)
        return base + offset

def char_to_coord(ch):
    b = ch.encode('cp950')
    if len(b) == 1:
        # ASCII character?
        # In this texture, ASCII is NOT in Big5 0xA1. Where is ASCII?
        # Let's check!
        return None
    b1, b2 = b[0], b[1]
    idx = big5_to_index(b1, b2)
    row = idx // 113
    col = idx % 113
    return row, col, idx

# Test some known characters:
test_chars = ['一', '乙', '世', '申', '共', '開', '始', '冒', '險', '建', '立', '之', '書', '結', '束', '遊', '戲']
for ch in test_chars:
    res = char_to_coord(ch)
    if res:
        r, c, idx = res
        cell = np.array(img.crop((c*36, r*36, (c+1)*36, (r+1)*36)))[:, :, 3]
        cnt = np.count_nonzero(cell > 30)
        print(f"'{ch}' ({ch.encode('cp950').hex(' ')}): idx={idx:5d} -> Row {r:3d}, Col {c:3d} (pixels={cnt:3d})")
