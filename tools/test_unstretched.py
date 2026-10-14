from PIL import Image, ImageFont, ImageDraw
import numpy as np
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FONT_TTF = os.path.join(BASE_DIR, "Pridi", "Pridi-Bold.ttf")
ORIG_PNG = os.path.join(BASE_DIR, "backup", "entry_342_original.png")

font = ImageFont.truetype(FONT_TTF, 32)
target_baseline = 32

def render_thai_slot(token, slot_info):
    cell = Image.new('RGBA', (36, 36), (0, 0, 0, 0))
    draw = ImageDraw.Draw(cell)
    
    # Draw text using anchor
    bbox = font.getbbox(token)
    draw_x = 2 - bbox[0]
    draw_y = target_baseline - bbox[3]
    draw.text((draw_x, draw_y), token, font=font, fill=(255, 255, 255, 255))
    
    arr = np.array(cell)[:, :, 3]
    coords = np.argwhere(arr > 20)
    if len(coords) == 0:
        return cell
        
    min_y, min_x = coords.min(axis=0)
    max_y, max_x = coords.max(axis=0)
    gw = max_x - min_x + 1
    gh = max_y - min_y + 1
    
    cropped = cell.crop((min_x, min_y, max_x + 1, max_y + 1))
    
    target_w = slot_info['orig_w']
    x0 = slot_info['x0']
    
    # Center within slot without any stretching!
    paste_x = x0 + max(0, (target_w - gw) // 2)
    
    out_cell = Image.new('RGBA', (36, 36), (0, 0, 0, 0))
    out_cell.paste(cropped, (paste_x, min_y), cropped)
    return out_cell, gw, gh, paste_x

# Test rendering a few key tokens
test_slots = {
    'เ':  {'char': '\u0433', 'cell': (14,  3), 'orig_w': 16, 'x0': 2},
    'า':  {'char': '\u0435', 'cell': (14,  5), 'orig_w': 18, 'x0': 1},
    'ก':  {'char': '\u0430', 'cell': (14,  0), 'orig_w': 20, 'x0': 1},
    'ริ่': {'char': '\u043C', 'cell': (14, 13), 'orig_w': 24, 'x0': 2},
    'ตั้': {'char': '\u044E', 'cell': (15, 12), 'orig_w': 26, 'x0': 2},
}

for t, s in test_slots.items():
    c, gw, gh, px = render_thai_slot(t, s)
    print(f"Token '{t}': gw={gw}, slot_w={s['orig_w']}, paste_x={px}, gh={gh}")
