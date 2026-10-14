from PIL import Image
import numpy as np

img = Image.open('backup/entry_342_original.png')

# In Russian alphabet WITH 'ё' (33 letters):
# 0: а
# 1: б
# 2: в
# 3: г
# 4: д
# 5: е
# 6: ё
# 7: ж
# 8: з
# 9: и
# 10: й
# 11: к
# 12: л
# 13: м
# 14: н
# 15: о
# --- Row 15 ---
# 16: п
# 17: р
# 18: с
# 19: т
# 20: у
# 21: ф
# 22: х
# 23: ц
# 24: ч
# 25: ш
# 26: щ
# 27: ъ
# 28: ы
# 29: ь
# 30: э
# 31: ю
# --- Row 16 ---
# 32: я

# Let's verify!
# In Row 14:
# Col 6: is it 'ё' (e with 2 dots)?
# In Row 15:
# Col 0: is it 'п' (p)?
# Col 13: is it 'ь' (soft sign)?
# Col 14: is it 'э'?
# Col 15: is it 'ю'?
# In Row 16:
# Col 0: is it 'я'?

def show(r, c, title=""):
    cell = np.array(img.crop((c*36, r*36, (c+1)*36, (r+1)*36)))[:, :, 3]
    print(f"=== {title} (R={r}, C={c}) ===")
    for y in range(0, 36, 2):
        line = ''.join(['#' if cell[y, x] > 50 else '.' for x in range(0, 36, 2)])
        if '#' in line:
            print(f"{y:2d}: {line}")

show(14, 6, "Row 14, Col 6 (Expected: ё)")
show(15, 0, "Row 15, Col 0 (Expected: п)")
show(15, 13, "Row 15, Col 13 (Expected: ь)")
show(15, 14, "Row 15, Col 14 (Expected: э)")
show(15, 15, "Row 15, Col 15 (Expected: ю)")
show(16, 0, "Row 16, Col 0 (Expected: я)")
