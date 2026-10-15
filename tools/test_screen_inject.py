import sys
import os
import csv

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__))))
from export_all_text_csv import parse_message_entry

base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
orig_path = os.path.join(base_dir, 'backup', 'entry_204_original.bin')
csv_path = os.path.join(base_dir, 'text_csv', 'categories', 'entry_00204_Menus_UI_Settings.csv')

with open(orig_path, 'rb') as f:
    orig_data = f.read()

orig = {idx: raw for idx, p, s, raw in parse_message_entry(orig_data)}
screen_indices = [1019, 1149, 1702, 1703, 1704, 1705, 1706, 1707, 1724, 1725, 1726, 1727, 1728, 1799, 1800, 1803]

with open(csv_path, 'r', encoding='utf-8-sig') as f:
    for row in csv.DictReader(f):
        idx = int(row['StringIndex'])
        if idx in screen_indices:
            en = orig[idx]
            th = row['ThaiTranslation']
            ptr = row['PointerOffset']
            print(f"idx={idx:4d}, ptr={ptr:5s}: EN ({len(en):2d}B) {en.decode('latin-1'):28s} -> TH: {th}")
