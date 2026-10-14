from PIL import Image, ImageFont
import os
import sys

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(BASE_DIR, "tools"))
from exact_cyrillic_table import CYR_MAP

FONT_TTF = os.path.join(BASE_DIR, "Pridi", "Pridi-Bold.ttf")
font = ImageFont.truetype(FONT_TTF, 32)

consonants_44 = [
    'ก', 'ข', 'ฃ', 'ค', 'ฅ', 'ฆ', 'ง',
    'จ', 'ฉ', 'ช', 'ซ', 'ฌ', 'ญ', 'ฎ',
    'ฏ', 'ฐ', 'ฑ', 'ฒ', 'ณ', 'ด', 'ต',
    'ถ', 'ท', 'ธ', 'น', 'บ', 'ป', 'ผ',
    'ฝ', 'พ', 'ฟ', 'ภ', 'ม', 'ย', 'ร',
    'ล', 'ว', 'ศ', 'ษ', 'ส', 'ห', 'ฬ',
    'อ', 'ฮ'
]
vowels = ['เ', 'า']
all_tokens = consonants_44 + vowels

print(f"Total tokens to map: {len(all_tokens)}")

for t in all_tokens:
    bbox = font.getbbox(t)
    gw = bbox[2] - bbox[0]
    gh = bbox[3] - bbox[1]
    print(f"'{t}': w={gw:2d}, h={gh:2d}, bbox={bbox}")
