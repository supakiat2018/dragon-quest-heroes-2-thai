import os
import sys
import struct
import subprocess
import numpy as np
from PIL import Image, ImageFont, ImageDraw

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(BASE_DIR, "tools"))

from draw_thai_glyphs import encode_dxt5_white, make_dds_file
from inject_inplace import pack_entry_chunks
from test_cell_encoder import encode_cell_dxt5

GAME_DIR = r"C:\Program Files (x86)\Steam\steamapps\common\DRAGON QUEST HEROES™ II"
OUT_ADDON = os.path.join(GAME_DIR, "dqh2_font_addons.bin")
TEX_DIR = os.path.join(BASE_DIR, "workspace", "tex_342")
OUT_DDS = os.path.join(TEX_DIR, "entry_342.TEX0.dxt5.dds")
OUT_G1T = os.path.join(TEX_DIR, "out", "entry_342.g1t")
ORIG_PNG = os.path.join(BASE_DIR, "backup", "entry_342_original.png")
FONT_TTF = os.path.join(BASE_DIR, "Pridi", "Pridi-Bold.ttf")
FONT_TAHOMA = r"C:\Windows\Fonts\tahomabd.ttf"

CELL_SIZE = 36
TARGET_BASELINE = 31
FONT_SIZE = 30

# =========================================================================
# 1. On-Screen Hero Naming Keyboard Mappings (5x5 grid in Block 2 & Block 4)
# Mapped in clean, alphabetical order: ก to ฮ followed by common vowels!
# =========================================================================

# Block 2 (24 uppercase European keys: Rows 1..5)
KEYBOARD_BLOCK_2 = [
    # Row 1: ก ข ค ง จ
    ('\u00C0', ( 8,  7), 'ก'),
    ('\u00C1', ( 9,  8), 'ข'),
    ('\u00C2', ( 8,  8), 'ค'),
    ('\u00C4', ( 7,  0), 'ง'),
    ('\u00C6', (17,  8), 'จ'),
    # Row 2: ฉ ช ซ ฌ ญ
    ('\u00C7', ( 7,  7), 'ฉ'),
    ('\u00C8', ( 8, 10), 'ช'),
    ('\u00C9', ( 7,  8), 'ซ'),
    ('\u00CA', ( 8, 11), 'ฌ'),
    ('\u00CB', ( 8, 12), 'ญ'),
    # Row 3: ฎ ฏ ฐ ฑ ฒ
    ('\u00CC', ( 9,  2), 'ฎ'),
    ('\u00CD', ( 9, 10), 'ฏ'),
    ('\u00CE', ( 8, 13), 'ฐ'),
    ('\u00CF', ( 8, 14), 'ฑ'),
    ('\u00D1', ( 9,  6), 'ฒ'),
    # Row 4: ณ ด ต ถ ท
    ('\u00D2', ( 9,  4), 'ณ'),
    ('\u00D3', ( 9, 12), 'ด'),
    ('\u00D4', ( 8, 15), 'ต'),
    ('\u00D6', ( 7,  1), 'ถ'),
    ('\u0152', ( 8,  9), 'ท'),
    # Row 5: ธ น บ ป (Key 24 is blank on the UI)
    ('\u00D9', ( 9,  0), 'ธ'),
    ('\u00DA', ( 9, 14), 'น'),
    ('\u00DB', ( 9,  1), 'บ'),
    ('\u00DC', ( 7,  2), 'ป'),
]

# Block 4 (25 lowercase European keys: Rows 1..5)
KEYBOARD_BLOCK_4 = [
    # Row 1: ผ ฝ พ ฟ ภ
    ('\u00E0', ( 7, 10), 'ผ'),
    ('\u00E1', ( 9,  9), 'ฝ'),
    ('\u00E2', ( 7, 11), 'พ'),
    ('\u00E4', ( 7,  3), 'ฟ'),
    ('\u00E6', (17,  9), 'ภ'),
    # Row 2: ม ย ร ล ว
    ('\u00E7', ( 7,  9), 'ม'),
    ('\u00E8', ( 7, 12), 'ย'),
    ('\u00E9', ( 7, 13), 'ร'),
    ('\u00EA', ( 7, 14), 'ล'),
    ('\u00EB', ( 7, 15), 'ว'),
    # Row 3: ศ ษ ส ห ฬ
    ('\u00EC', ( 9,  3), 'ศ'),
    ('\u00ED', ( 9, 11), 'ษ'),
    ('\u00EE', ( 8,  0), 'ส'),
    ('\u00EF', ( 8,  1), 'ห'),
    ('\u00F1', ( 9,  7), 'ฬ'),
    # Row 4: อ ฮ ะ า ำ
    ('\u00F2', ( 9,  5), 'อ'),
    ('\u00F3', ( 9, 13), 'ฮ'),
    ('\u00F4', ( 8,  2), 'ะ'),
    ('\u00F6', ( 7,  4), 'า'),
    ('\u0153', ( 8,  5), 'ำ'),
    # Row 5: เ แ โ ใ ไ
    ('\u00F9', ( 8,  4), 'เ'),
    ('\u00FA', ( 9, 15), 'แ'),
    ('\u00FB', ( 8,  3), 'โ'),
    ('\u00FC', ( 7,  5), 'ใ'),
    ('\u00DF', ( 7,  6), 'ไ'),
]

# =========================================================================
# 2. Safe Dialogue & UI Slots (Cyrillic + Safe Non-Latin Symbols)
# 100% IMMUNE TO AUTO-CAPITALIZATION AND ZERO KEYBOARD CONFLICT!
# =========================================================================
CYR_UPPER = [
    ('\u0410', (11,  0)), ('\u0411', (11,  1)), ('\u0412', (11,  2)), ('\u0413', (11,  3)),
    ('\u0414', (11,  4)), ('\u0415', (11,  5)), ('\u0401', (11,  6)), ('\u0416', (11,  7)),
    ('\u0417', (11,  8)), ('\u0418', (11,  9)), ('\u0419', (11, 10)), ('\u041A', (11, 11)),
    ('\u041B', (11, 12)), ('\u041C', (11, 13)), ('\u041D', (11, 14)), ('\u041E', (11, 15)),
    ('\u041F', (12,  0)), ('\u0420', (12,  1)), ('\u0421', (12,  2)), ('\u0422', (12,  3)),
    ('\u0423', (12,  4)), ('\u0424', (12,  5)), ('\u0425', (12,  6)), ('\u0426', (12,  7)),
    ('\u0427', (12,  8)), ('\u0428', (12,  9)), ('\u0429', (12, 10)), ('\u042A', (12, 11)),
    ('\u042B', (12, 12)), ('\u042C', (12, 13)), ('\u042D', (12, 14)), ('\u042E', (12, 15)),
    ('\u042F', (13,  0)),
]

CYR_LOWER = [
    ('\u0430', (14,  0)), ('\u0431', (14,  1)), ('\u0432', (14,  2)), ('\u0433', (14,  3)),
    ('\u0434', (14,  4)), ('\u0435', (14,  5)), ('\u0451', (14,  6)), ('\u0436', (14,  7)),
    ('\u0437', (14,  8)), ('\u0438', (14,  9)), ('\u0439', (14, 10)), ('\u043A', (14, 11)),
    ('\u043B', (14, 12)), ('\u043C', (14, 13)), ('\u043D', (14, 14)), ('\u043E', (14, 15)),
    ('\u043F', (15,  0)), ('\u0440', (15,  1)), ('\u0441', (15,  2)), ('\u0442', (15,  3)),
    ('\u0443', (15,  4)), ('\u0444', (15,  5)), ('\u0445', (15,  6)), ('\u0446', (15,  7)),
    ('\u0447', (15,  8)), ('\u0448', (15,  9)), ('\u0449', (15, 10)), ('\u044A', (15, 11)),
    ('\u044B', (15, 12)), ('\u044C', (15, 13)), ('\u044D', (15, 14)), ('\u044E', (15, 15)),
    ('\u044F', (16,  0)),
]

SYMBOLS = [
    ('\u2019', (17,  2)), ('\u201D', (17,  3)), ('\u2018', (17,  5)), ('\u201C', (17,  6)), ('\u201E', (17,  7)),
    ('\u2460', (18,  0)), ('\u2461', (18,  1)), ('\u2462', (18,  2)), ('\u2463', (18,  3)), ('\u2464', (18,  4)),
    ('\u2465', (18,  5)), ('\u2466', (18,  6)), ('\u2467', (18,  7)), ('\u2468', (18,  8)), ('\u2469', (18,  9)),
    ('\uFF0F', (18, 10)),
    ('\u2606', (19,  0)), ('\u2605', (19,  1)), ('\u203B', (19,  2)), ('\u25B2', (19,  3)), ('\u25BC', (19,  4)),
    ('\u25B3', (19,  5)), ('\u25BD', (19,  6)), ('\u25A0', (19,  7)), ('\u25A1', (19,  8)), ('\u25CF', (19,  9)),
    ('\u25CB', (19, 10)), ('\u2103', (19, 11)), ('\u2642', (19, 12)), ('\u2640', (19, 13)),
    ('\u21D4', (20,  4)), ('\u21D2', (20,  5)),
]

SAFE_TOKENS_LIST = [
    # 1. Multi-level stacked clusters & high-frequency ligatures (matched first!)
    'ตั้', 'ริ่', 'ชื่', 'พื้', 'เนื้', 'เต็', 'เข้', 'เอ',
    'ต่ำ', 'ลำ', 'จำ', 'กำ', 'คำ', 'ทำ', 'นำ',
    'ที่', 'นี้', 'ผู้', 'ขึ้น', 'ให้', 'ได้', 'ไม่',
    'ดิ', 'ยื', 'คื', 'บั', 'ทึ', 'ชิ', 'ภั', 'ม่', 'ห้', 'ด้',
    'ลื', 'ล้', 'คุ', 'ปิ', 'ฟิ', 'ร้', 'สู', 'ส่', 'ส์',
    # 2. Vowels & signs
    'ะ', 'า', 'ำ', 'เ', 'แ', 'โ', 'ใ', 'ไ', 'ๆ', 'ฯ',
    # 3. Base consonants (42)
    'ก', 'ข', 'ค', 'ฆ', 'ง', 'จ', 'ฉ', 'ช', 'ซ', 'ฌ', 'ญ',
    'ฎ', 'ฏ', 'ฐ', 'ฑ', 'ฒ', 'ณ', 'ด', 'ต', 'ถ', 'ท', 'ธ',
    'น', 'บ', 'ป', 'ผ', 'ฝ', 'พ', 'ฟ', 'ภ', 'ม', 'ย', 'ร',
    'ล', 'ว', 'ศ', 'ษ', 'ส', 'ห', 'ฬ', 'อ', 'ฮ'
]

SAFE_SLOTS = CYR_UPPER + CYR_LOWER + SYMBOLS
assert len(SAFE_TOKENS_LIST) <= len(SAFE_SLOTS), f"Too many tokens: {len(SAFE_TOKENS_LIST)} > {len(SAFE_SLOTS)}"

DIALOGUE_SLOTS = {}
for i, tok in enumerate(SAFE_TOKENS_LIST):
    ch, cell = SAFE_SLOTS[i]
    DIALOGUE_SLOTS[tok] = {'char': ch, 'cell': cell}

SORTED_DIALOGUE_TOKENS = sorted(DIALOGUE_SLOTS.keys(), key=len, reverse=True)

# Combined slots for font texture generation & width lookup
ALL_SLOTS_TO_RENDER = {}

# 1. Keyboard slots (Block 2 & Block 4)
for ch, cell, tok in KEYBOARD_BLOCK_2 + KEYBOARD_BLOCK_4:
    ALL_SLOTS_TO_RENDER[f"KB_{ch}"] = {'char': ch, 'cell': cell, 'token': tok, 'is_kb': True}

# 2. Dialogue slots (Cyrillic & Safe Symbols)
for tok, slot in DIALOGUE_SLOTS.items():
    ALL_SLOTS_TO_RENDER[f"DIAG_{slot['char']}"] = {'char': slot['char'], 'cell': slot['cell'], 'token': tok, 'is_kb': False}

print(f"[+] Total slots to render in atlas: {len(ALL_SLOTS_TO_RENDER)}")
print(f"[+] Dialogue tokens mapped: {len(DIALOGUE_SLOTS)} (100% safe from auto-capitalization)")

def encode_thai_string(s):
    res = []
    i = 0
    while i < len(s):
        matched = False
        for t in SORTED_DIALOGUE_TOKENS:
            if s.startswith(t, i):
                res.append(DIALOGUE_SLOTS[t]['char'])
                i += len(t)
                matched = True
                break
        if not matched:
            res.append(s[i])
            i += 1
    return "".join(res)

def render_token_glyph(font, token, is_kb=False):
    cell = Image.new('RGBA', (CELL_SIZE, CELL_SIZE), (0, 0, 0, 0))
    d = ImageDraw.Draw(cell)
    
    # Use Tahoma Bold for โ and ใ to ensure 100% crisp, unmistakable distinction
    if token in ('โ', 'ใ'):
        f_tahoma = ImageFont.truetype(FONT_TAHOMA, 28)
        bbox = f_tahoma.getbbox(token)
        draw_x = 2 - min(0, bbox[0])
        d.text((draw_x, 29), token, font=f_tahoma, fill=(255, 255, 255, 255), anchor='ls')
        return cell

    # Custom rendering for multi-level stacked clusters to prevent overlapping
    if token == 'ตั้':
        d.text((0, TARGET_BASELINE), 'ตั', font=font, fill=(255, 255, 255, 255), anchor='ls')
        f_tone = ImageFont.truetype(FONT_TTF, 18)
        temp_t = Image.new('RGBA', (50, 50), (0, 0, 0, 0))
        d_t = ImageDraw.Draw(temp_t)
        d_t.text((25, 25), '้', font=f_tone, fill=(255, 255, 255, 255))
        arr_t = np.array(temp_t)[:, :, 3]
        coords = np.argwhere(arr_t > 20)
        min_y, min_x = coords.min(axis=0)
        max_y, max_x = coords.max(axis=0)
        crop_tho = temp_t.crop((min_x, min_y, max_x + 1, max_y + 1))
        cell.paste(crop_tho, (12, 0), crop_tho)
    elif token == 'ริ่':
        d.text((0, TARGET_BASELINE), 'ริ', font=font, fill=(255, 255, 255, 255), anchor='ls')
        f_tone = ImageFont.truetype(FONT_TTF, 18)
        temp_ek = Image.new('RGBA', (50, 50), (0, 0, 0, 0))
        d_ek = ImageDraw.Draw(temp_ek)
        d_ek.text((25, 25), '่', font=f_tone, fill=(255, 255, 255, 255))
        arr_ek = np.array(temp_ek)[:, :, 3]
        coords = np.argwhere(arr_ek > 20)
        min_y, min_x = coords.min(axis=0)
        max_y, max_x = coords.max(axis=0)
        crop_ek = temp_ek.crop((min_x, min_y, max_x + 1, max_y + 1))
        cell.paste(crop_ek, (9, 2), crop_ek)
    elif token == 'ชื่':
        d.text((0, TARGET_BASELINE), 'ชื', font=font, fill=(255, 255, 255, 255), anchor='ls')
        f_tone = ImageFont.truetype(FONT_TTF, 18)
        temp_ek = Image.new('RGBA', (50, 50), (0, 0, 0, 0))
        d_ek = ImageDraw.Draw(temp_ek)
        d_ek.text((25, 25), '่', font=f_tone, fill=(255, 255, 255, 255))
        arr_ek = np.array(temp_ek)[:, :, 3]
        coords = np.argwhere(arr_ek > 20)
        min_y, min_x = coords.min(axis=0)
        max_y, max_x = coords.max(axis=0)
        crop_ek = temp_ek.crop((min_x, min_y, max_x + 1, max_y + 1))
        cell.paste(crop_ek, (11, 0), crop_ek)
    elif token == 'พื้':
        d.text((0, TARGET_BASELINE), 'พื', font=font, fill=(255, 255, 255, 255), anchor='ls')
        f_tone = ImageFont.truetype(FONT_TTF, 18)
        temp_t = Image.new('RGBA', (50, 50), (0, 0, 0, 0))
        d_t = ImageDraw.Draw(temp_t)
        d_t.text((25, 25), '้', font=f_tone, fill=(255, 255, 255, 255))
        arr_t = np.array(temp_t)[:, :, 3]
        coords = np.argwhere(arr_t > 20)
        min_y, min_x = coords.min(axis=0)
        max_y, max_x = coords.max(axis=0)
        crop_tho = temp_t.crop((min_x, min_y, max_x + 1, max_y + 1))
        cell.paste(crop_tho, (12, 0), crop_tho)
    elif token == 'เนื้':
        d.text((0, TARGET_BASELINE), 'เนื', font=font, fill=(255, 255, 255, 255), anchor='ls')
        f_tone = ImageFont.truetype(FONT_TTF, 18)
        temp_t = Image.new('RGBA', (50, 50), (0, 0, 0, 0))
        d_t = ImageDraw.Draw(temp_t)
        d_t.text((25, 25), '้', font=f_tone, fill=(255, 255, 255, 255))
        arr_t = np.array(temp_t)[:, :, 3]
        coords = np.argwhere(arr_t > 20)
        min_y, min_x = coords.min(axis=0)
        max_y, max_x = coords.max(axis=0)
        crop_tho = temp_t.crop((min_x, min_y, max_x + 1, max_y + 1))
        cell.paste(crop_tho, (16, 0), crop_tho)
    elif token == 'ำ':
        bbox = font.getbbox(token)
        draw_x = 0 - min(0, bbox[0])
        d.text((draw_x, TARGET_BASELINE), token, font=font, fill=(255, 255, 255, 255), anchor='ls')
    else:
        bbox = font.getbbox(token)
        draw_x = 0 - min(0, bbox[0])
        d.text((draw_x, TARGET_BASELINE), token, font=font, fill=(255, 255, 255, 255), anchor='ls')
    return cell

def get_token_width(font, token):
    if token == 'เ': return 9.0
    if token == 'แ': return 17.0
    if token == 'โ': return 11.0
    if token == 'ใ': return 11.0
    if token == 'ไ': return 10.0
    if token == 'า': return 13.0
    if token == 'ะ': return 13.0
    if token == 'ำ': return 14.0
    if token == 'เอ': return 26.0
    
    w = float(font.getlength(token))
    return round(w, 1)

def build_entry_342():
    print("[*] Building Entry 342 (Menu Font Atlas with 100% Thai Keyboard & Precomposed Clusters)...")
    img = Image.open(ORIG_PNG).convert("RGBA")
    font = ImageFont.truetype(FONT_TTF, FONT_SIZE)

    for key, slot in ALL_SLOTS_TO_RENDER.items():
        row, col = slot['cell']
        x0 = col * CELL_SIZE
        y0 = row * CELL_SIZE

        glyph_cell = render_token_glyph(font, slot['token'], is_kb=slot['is_kb'])

        blank = Image.new('RGBA', (CELL_SIZE, CELL_SIZE), (0, 0, 0, 0))
        img.paste(blank, (x0, y0))
        img.paste(glyph_cell, (x0, y0), glyph_cell)

    preview_path = os.path.join(TEX_DIR, "entry_342_universal_thai.png")
    img.save(preview_path)
    print(f"[+] Saved atlas preview: {preview_path}")

    dxt_bytes = encode_dxt5_white(img)
    dds_bytes = make_dds_file(dxt_bytes, img.width, img.height)
    with open(OUT_DDS, "wb") as f:
        f.write(dds_bytes)

    out_dir = os.path.join(TEX_DIR, "out")
    os.makedirs(out_dir, exist_ok=True)
    cmd = [sys.executable, os.path.join(BASE_DIR, "tools", "g1t_tool.py"), "import", TEX_DIR, out_dir]
    res = subprocess.run(cmd, capture_output=True, text=True)
    assert res.returncode == 0, f"g1t_tool error: {res.stderr}"

    with open(OUT_G1T, "rb") as f:
        g1t_data = f.read()

    packed = pack_entry_chunks(g1t_data)
    print(f"[+] Entry 342 packed size: {len(packed)} bytes")
    return packed

def build_entry_204():
    print("[*] Building Entry 204 with 100% Tight Thai & Zero Pointer Collisions...")
    with open(os.path.join(BASE_DIR, "backup", "entry_204_original.bin"), "rb") as f:
        data = bytearray(f.read())

    ORIG_SIZE = len(data) # 86768

    # 1. Yes / No Dialog (Safe Unused block 66620..66850)
    yes_no_opts = [
        {'off': 3244, 'text': 'ใช่', 'suffix': b'\x00'},
        {'off': 3248, 'text': 'ไม่ใช่', 'suffix': b'\x00'},
    ]
    cur_pos = 66620
    for opt in yes_no_opts:
        cyr_str = encode_thai_string(opt['text'])
        raw_b = cyr_str.encode('utf-8') + opt.get('suffix', b'\x00')
        data[cur_pos : cur_pos + len(raw_b)] = raw_b
        struct.pack_into("<I", data, opt['off'], cur_pos - 0x20)
        cur_pos = (cur_pos + len(raw_b) + 1) & ~1
    assert cur_pos <= 66850, f"Exceeded Yes/No block: {cur_pos} > 66850"

    # 2. Graphics Settings Options & Values in SAFE Unused block (68076..68700)
    graphics_options = [
        {'off': 4108, 'text': 'ยืนยัน', 'suffix': b'\x00'},
        {'off': 4628, 'text': 'คืนค่าเริ่มต้น', 'suffix': b'\x00'},
        {'off': 6812, 'text': 'แสดงผลเต็มจอ', 'suffix': b'\x00'},
        {'off': 6816, 'text': 'ความละเอียด', 'suffix': b'\x00'},
        {'off': 6820, 'text': 'เฟรมเรต', 'suffix': b'\x00'},
        {'off': 6824, 'text': 'คุณภาพกราฟิก', 'suffix': b'\x00'},
        {'off': 6828, 'text': '  จำนวนตัวละคร', 'suffix': b'\x00'},
        {'off': 6832, 'text': '  ระยะแสดงผล', 'suffix': b'\x00'},
        {'off': 6836, 'text': '  คุณภาพพื้นผิว', 'suffix': b'\x00'},
        {'off': 6840, 'text': '  คุณภาพเงา', 'suffix': b'\x00'},
        {'off': 6844, 'text': '  มิติแสงเงา', 'suffix': b'\x00'},
        {'off': 6848, 'text': '  การสะท้อนแสง', 'suffix': b'\x00'},
        {'off': 6852, 'text': '  ลำแสงส่องกระทบ', 'suffix': b'\x00'},
        {'off': 6856, 'text': '  ละอองอนุภาค', 'suffix': b'\x00'},
        {'off': 6860, 'text': '  แสงธรรมชาติรอบทิศทาง', 'suffix': b'\x00'},
        {'off': 6864, 'text': 'เลือกว่าจะแสดงผลแบบเต็มหน้าจอหรือแบบหน้าต่าง', 'suffix': b'\x00'},
        {'off': 6928, 'text': 'เปิด', 'suffix': b'\x00'},
        {'off': 6932, 'text': 'ปิด', 'suffix': b'\x00'},
        {'off': 6936, 'text': 'สูง', 'suffix': b'\x00'},
        {'off': 6940, 'text': 'ปานกลาง', 'suffix': b'\x00'},
        {'off': 6944, 'text': 'ต่ำ', 'suffix': b'\x00'},
        {'off': 6948, 'text': 'กำหนดเอง', 'suffix': b'\x00'},
        {'off': 7192, 'text': 'เปลี่ยนความละเอียด', 'suffix': b'\x00'},
        {'off': 7228, 'text': '  หมอกเชิงปริมาตร', 'suffix': b'\x00'},
        {'off': 7232, 'text': '  เงาจากแสงเฉพาะจุด', 'suffix': b'\x00'},
        {'off': 7244, 'text': 'ยืนยันการตั้งค่ากราฟิก', 'suffix': b'\x00'},
    ]
    cur_pos = 68076
    for opt in graphics_options:
        cyr_str = encode_thai_string(opt['text'])
        raw_b = cyr_str.encode('utf-8') + opt.get('suffix', b'\x00')
        data[cur_pos : cur_pos + len(raw_b)] = raw_b
        struct.pack_into("<I", data, opt['off'], cur_pos - 0x20)
        cur_pos = (cur_pos + len(raw_b) + 1) & ~1
    assert cur_pos <= 68700, f"Exceeded graphics block: {cur_pos} > 68700"

    # 3. Adventure Log, Hero Descriptions & Hero Naming screen UI (block 68736..69300)
    naming_and_log_ui = [
        {'off': 4044, 'text': 'บันทึกการเดินทาง', 'suffix': b'\x00'},
        {'off': 4048, 'text': 'เวลาเล่น', 'suffix': b'\x00'},
        {'off': 4052, 'text': 'วันที่บันทึก', 'suffix': b'\x00'},
        {'off': 4056, 'text': 'สิ่งที่ต้องทำ', 'suffix': b'\x00'},
        {'off': 4060, 'text': 'ว่าง', 'suffix': b'\x00'},
        {'off': 4064, 'text': 'อัศวินฝึกหัดหนุ่มเลือดร้อน ผู้มุ่งมั่นทำในสิ่งที่ถูกต้องโดยไม่ยอมแพ้', 'suffix': b'\x00'},
        {'off': 4068, 'text': 'อัศวินฝึกหัดสาวผู้สุขุมเยือกเย็น เป็นผู้นำด้วยสติปัญญาและพรสวรรค์', 'suffix': b'\x00'},
        {'off': 4072, 'text': 'โปรดเลือกชื่อให้แก่ผู้กล้าของคุณ', 'suffix': b'\x00'},
        {'off': 4076, 'text': 'โปรดเลือกชื่อให้แก่ญาติของผู้กล้า', 'suffix': b'\x00'},
        {'off': 4080, 'text': 'ผู้กล้า', 'suffix': b'\x00'},
        {'off': 4084, 'text': 'ญาติ', 'suffix': b'\x00'},
        {'off': 4088, 'text': 'รูปแบบการควบคุม', 'suffix': b'\x00'},
        {'off': 4092, 'text': 'ควบคุมทุกการเคลื่อนไหวด้วยตนเอง\x1bMVเหมาะสำหรับผู้เล่นที่เน้นกลยุทธ์\x1bFG', 'suffix': b'\x00'},
        {'off': 4096, 'text': 'เล่นด้วยการกดปุ่มแบบง่าย\x1bMVเหมาะสำหรับผู้ที่ต้องการความสนุกอย่างรวดเร็ว\x1bFG', 'suffix': b'\x00'},
        {'off': 4100, 'text': 'สารภาพบาป (บันทึก)', 'suffix': b'\x00'},
        {'off': 4104, 'text': 'สิ้นสุดการผจญภัย', 'suffix': b'\x00'},
    ]
    cur_pos = 68736
    for opt in naming_and_log_ui:
        cyr_str = encode_thai_string(opt['text'])
        raw_b = cyr_str.encode('utf-8') + opt.get('suffix', b'\x00')
        data[cur_pos : cur_pos + len(raw_b)] = raw_b
        struct.pack_into("<I", data, opt['off'], cur_pos - 0x20)
        cur_pos = (cur_pos + len(raw_b) + 1) & ~1
    assert cur_pos <= 69310, f"Exceeded naming UI block: {cur_pos} > 69310"

    # 4. Save Prompts & Hero Selection & Confirmation Dialogues (block 7632..8600)
    hero_and_save_dialogues = [
        {'off': 32,   'text': 'ต้องการสร้างบันทึกการเดินทางในช่องใด', 'suffix': b'\x1bFH\x00'},
        {'off': 36,   'text': 'ต้องการลบบันทึกการเดินทางนี้และสร้างบันทึกใหม่แทนที่ใช่หรือไม่', 'suffix': b'\x1bFH\x00'},
        {'off': 40,   'text': 'เอาล่ะ โปรดเลือกผู้กล้าที่จะควบคุมในการผจญภัยในโลกนี้ การเลือกนี้จะไม่มีผลต่อเนื้อหาที่จะเข้าถึงได้ในเกม', 'suffix': b'\x00'},
        {'off': 44,   'text': 'โปรดเลือกผู้กล้า', 'suffix': b'\x00'},
        {'off': 48,   'text': 'ต่อไป โปรดตั้งชื่อให้แก่ผู้กล้าที่จะร่วมเดินทางไปด้วยกัน', 'suffix': b'\x00'},
        {'off': 52,   'text': 'ชื่อที่ป้อนมีตัวอักษรที่ไม่สามารถใช้ได้ โปรดใช้ชื่ออื่น', 'suffix': b'\x00'},
        {'off': 56,   'text': 'ต้องการเริ่มการเดินทางด้วยผู้กล้าทั้งสองนี้ใช่หรือไม่', 'suffix': b'\x1bFH\x00'},
        {'off': 60,   'text': 'สุดท้ายนี้ โปรดเลือกรูปแบบการควบคุมและการตั้งค่ากล้อง ซึ่งสามารถเปลี่ยนได้ตลอดเวลาในระหว่างเล่นเกม', 'suffix': b'\x00'},
        {'off': 64,   'text': 'การเปิดใช้งานคุณสมบัติออนไลน์จะทำให้คุณเข้าถึงเนื้อหาออนไลน์ที่น่าตื่นเต้นมากมาย ต้องการเปิดใช้งานตอนนี้หรือไม่', 'suffix': b'\x1bFH\x00'},
        {'off': 68,   'text': 'เกมนี้มีระบบบันทึกอัตโนมัติ กรุณาอย่าปิดเครื่องขณะกำลังบันทึกข้อมูล ระบบบันทึกอัตโนมัติจะใช้ช่องบันทึกข้อมูลเพียงช่องเดียว', 'suffix': b'\x00'},
        {'off': 72,   'text': 'กำลังบันทึก...', 'suffix': b'\x00'},
        {'off': 76,   'text': 'สร้างบันทึกการเดินทางสำเร็จแล้ว', 'suffix': b'\x00'},
        {'off': 80,   'text': 'โปรดเลือกบันทึกการเดินทาง', 'suffix': b'\x00'},
    ]
    cur_pos = 7632
    for opt in hero_and_save_dialogues:
        cyr_str = encode_thai_string(opt['text'])
        raw_b = cyr_str.encode('utf-8') + opt.get('suffix', b'\x00')
        data[cur_pos : cur_pos + len(raw_b)] = raw_b
        struct.pack_into("<I", data, opt['off'], cur_pos - 0x20)
        print(f"    [+] Ptr {opt['off']:4d}: '{opt['text'][:28]}...' -> pos={cur_pos} ({len(raw_b)}B)")
        cur_pos = (cur_pos + len(raw_b) + 1) & ~1
    assert cur_pos <= 8602, f"Exceeded save dialogue block: {cur_pos} > 8602"

    # 5. Title Menus 1, 2, 3 (block 79264..79332)
    menus_123 = [
        {'off': 4032, 'text': 'เริ่มการเดินทาง'},
        {'off': 4036, 'text': 'สร้างบันทึก'},
        {'off': 4040, 'text': 'ลบบันทึก'},
    ]
    cur_off = 79264
    for m in menus_123:
        cyr_str = encode_thai_string(m['text'])
        utf8 = cyr_str.encode('utf-8') + b"\x00"
        data[cur_off : cur_off + len(utf8)] = utf8
        struct.pack_into("<I", data, m['off'], cur_off - 0x20)
        cur_off = (cur_off + len(utf8) + 1) & ~1

    # 6. Streaming & Multiplayer Notice at Bottom Right of Title Screen (block 79590..79645)
    notices = [
        {'off': 6108, 'text': 'ประกาศเกี่ยวกับการถ่ายทอดสด', 'prefix': b'\x1bPH '},
        {'off': 6112, 'text': 'ข้อตกลงการเล่นหลายคน', 'prefix': b'\x1bPH '},
    ]
    cur_off = 79590
    for n in notices:
        cyr_str = encode_thai_string(n['text'])
        raw_b = n.get('prefix', b'') + cyr_str.encode('utf-8') + b"\x00"
        data[cur_off : cur_off + len(raw_b)] = raw_b
        struct.pack_into("<I", data, n['off'], cur_off - 0x20)
        cur_off = (cur_off + len(raw_b) + 1) & ~1
    assert cur_off <= 79646, f"Exceeded notices block: {cur_off} > 79646"

    # 7. Title Menus 4, 5, 6, 7 (block 86672..86768)
    menus_4567 = [
        {'off': 6800, 'text': 'ตั้งค่ากราฟิก'},
        {'off': 6804, 'text': 'ตั้งค่าคีย์บอร์ด'},
        {'off': 7092, 'text': 'ตั้งค่าเมาส์'},
        {'off': 6808, 'text': 'ออกจากเกม'},
    ]
    cur_off = 86672
    for m in menus_4567:
        cyr_str = encode_thai_string(m['text'])
        utf8 = cyr_str.encode('utf-8') + b"\x00"
        data[cur_off : cur_off + len(utf8)] = utf8
        struct.pack_into("<I", data, m['off'], cur_off - 0x20)
        cur_off = (cur_off + len(utf8) + 1) & ~1

    assert len(data) == ORIG_SIZE, f"Size changed: {len(data)} != {ORIG_SIZE}"
    print(f"[+] Entry 204 successfully created ({len(data)} bytes, 100% clean and non-colliding)")
    return bytes(data)

def generate_cpp_code():
    print("[*] Generating C++ GetThaiCharWidth switch table...")
    font = ImageFont.truetype(FONT_TTF, FONT_SIZE)
    lines = []
    lines.append("// Auto-generated Proportional Thai Character Spacing Table")
    lines.append("float GetThaiCharWidth(uint32_t code)")
    lines.append("{")
    lines.append("    switch (code) {")
    
    seen_codes = set()
    for key, slot in ALL_SLOTS_TO_RENDER.items():
        ch = slot['char']
        utf8_b = ch.encode('utf-8')
        if len(utf8_b) == 2:
            code = (utf8_b[0] << 8) | utf8_b[1]
        elif len(utf8_b) == 3:
            code = (utf8_b[0] << 16) | (utf8_b[1] << 8) | utf8_b[2]
        else:
            continue
            
        if code in seen_codes:
            continue
        seen_codes.add(code)
        
        w = get_token_width(font, slot['token'])
        lines.append(f"        case 0x{code:06X}: return {w:.1f}f; // {slot['token']}")
        
    lines.append("        default:")
    lines.append("            return -1.0f;")
    lines.append("    }")
    lines.append("}")
    return "\n".join(lines)

def main():
    print("=================================================================")
    print("[*] Generating 100% Universal Tight Thai Addon (All Menus & UI)")
    print("=================================================================")

    data_204 = build_entry_204()
    data_342 = build_entry_342()

    # Load original 341 from backup
    with open(os.path.join(BASE_DIR, "backup", "entry_341_original.g1t"), "rb") as f:
        g1t_341 = f.read()
    data_341 = pack_entry_chunks(g1t_341)

    pad_341 = 1539328 - len(data_341)
    if pad_341 > 0:
        data_341 = data_341 + b'\x00' * pad_341

    pad_342 = 47616 - len(data_342)
    if pad_342 > 0:
        data_342 = data_342 + b'\x00' * pad_342

    entries = [
        (204, 2250752, 86768, data_204),
        (341, 45149440, 1539328, data_341),
        (342, 46688768, 47616, data_342)
    ]

    buf = bytearray()
    buf.extend(b"DQH2THAI")
    buf.extend(struct.pack("<I", len(entries)))

    for eid, off, sz, d in entries:
        buf.extend(struct.pack("<IQQQ", eid, off, sz, len(d)))
        buf.extend(d)

    with open(OUT_ADDON, "wb") as f:
        f.write(buf)

    print(f"\n[SUCCESS] Generated: {OUT_ADDON} ({len(buf)} bytes, ~{len(buf)/1024/1024:.2f} MB)")

    # Save generated C++ function
    cpp_fn = generate_cpp_code()
    with open(os.path.join(BASE_DIR, "tools", "thai_char_widths.inl"), "w", encoding="utf-8") as f:
        f.write(cpp_fn)
    print("[+] Exported C++ code to tools/thai_char_widths.inl")

if __name__ == "__main__":
    main()
