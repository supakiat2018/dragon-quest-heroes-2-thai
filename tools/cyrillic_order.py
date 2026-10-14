from PIL import Image
import numpy as np

# Russian alphabet:
# А Б В Г Д Е Ж З И Й К Л М Н О П (16)
# Р С Т У Ф Х Ц Ч Ш Щ Ъ Ы Ь Э Ю Я (17) -> total 33

# Let's map each letter to its exact (row, col) in entry_342
upper_cyr = "АБВГДЕЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯ"
lower_cyr = "абвгдежзийклмнопрстуфхцчшщъыьэюя"

upper_coords = {}
for i, ch in enumerate(upper_cyr):
    if i < 16:
        r, c = 11, i
    elif i < 32:
        r, c = 12, i - 16
    else:
        r, c = 13, i - 32
    upper_coords[ch] = (r, c)

lower_coords = {}
for i, ch in enumerate(lower_cyr):
    if i < 16:
        r, c = 14, i
    elif i < 32:
        r, c = 15, i - 16
    else:
        r, c = 16, i - 32
    lower_coords[ch] = (r, c)

print("Lowercase Cyrillic exact positions in entry_342:")
for ch, (r, c) in lower_coords.items():
    print(f"'{ch}' ({ord(ch):04X}): Row {r:2d}, Col {c:2d}")
