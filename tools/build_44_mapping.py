import os
import sys
from PIL import Image
import numpy as np

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(BASE_DIR, "tools"))
from exact_cyrillic_table import CYR_MAP

img = Image.open(os.path.join(BASE_DIR, "backup", "entry_342_original.png"))

# Get bounding box and orig_w, x0 for all 66 Cyrillic slots
slots_info = {}
for ch, (r, c) in CYR_MAP.items():
    cell = np.array(img.crop((c*36, r*36, (c+1)*36, (r+1)*36)))[:, :, 3]
    coords = np.argwhere(cell > 30)
    if len(coords) > 0:
        x0 = coords[:, 1].min()
        x1 = coords[:, 1].max()
        w = x1 - x0 + 1
    else:
        x0 = 1
        w = 20
    slots_info[ch] = {'char': ch, 'cell': (r, c), 'orig_w': w, 'x0': x0}

# Already assigned (fixed from previous success):
assigned = {
    'เ': 'г', # \u0433 (16px)
    'า': 'е', # \u0435 (18px)
    'ก': 'а', # \u0430 (20px)
    'จ': 'в', # \u0432 (18px)
    'ด': 'к', # \u043A (21px)
    'บ': 'д', # \u0434 (22px)
    'ล': 'л', # \u043B (22px)
    'น': 'и', # \u0438 (20px)
    'ท': 'н', # \u043D (21px)
    'ม': 'о', # \u043E (20px)
    'ง': 'п', # \u043F (21px)
    'ส': 'р', # \u0440 (20px)
    'อ': 'у', # \u0443 (22px)
    'ร': 'ь', # \u044C (19px)
}

used_cyr = set(assigned.values())

# Consonants still to assign (30 consonants)
consonants_44 = [
    'ก', 'ข', 'ฃ', 'ค', 'ฅ', 'ฆ', 'ง',
    'จ', 'ฉ', 'ช', 'ซ', 'ฌ', 'ญ', 'ฎ',
    'ฏ', 'ฐ', 'ฑ', 'ฒ', 'ณ', 'ด', 'ต',
    'ถ', 'ท', 'ธ', 'น', 'บ', 'ป', 'ผ',
    'ฝ', 'พ', 'ฟ', 'ภ', 'ม', 'ย', 'ร',
    'ล', 'ว', 'ศ', 'ษ', 'ส', 'ห', 'ฬ',
    'อ', 'ฮ'
]
unassigned_thai = [t for t in consonants_44 if t not in assigned]
print(f"Unassigned Thai consonants: {len(unassigned_thai)}")

# Available Cyrillic slots
avail_slots = [ch for ch in CYR_MAP.keys() if ch not in used_cyr]
print(f"Available Cyrillic slots: {len(avail_slots)}")

# Assign remaining Thai to available Cyrillic slots
for t in unassigned_thai:
    ch = avail_slots.pop(0)
    assigned[t] = ch

print(f"Total assigned tokens: {len(assigned)}")
for t in consonants_44:
    cyr = assigned[t]
    s = slots_info[cyr]
    print(f"'{t}' -> Cyr '{cyr}' ({ord(cyr):04X}) -> Row {s['cell'][0]:2d}, Col {s['cell'][1]:2d} (w={s['orig_w']}px)")
