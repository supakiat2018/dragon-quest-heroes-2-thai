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

CELL_SIZE = 36
TARGET_BASELINE = 31
FONT_SIZE = 30

# 1. 66 Russian Cyrillic characters in entry_342
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

# 2. 52 European Accented Characters in Rows 7..10
EUR_CHARS = [
    ('\u00C4', ( 7,  0)), ('\u00D6', ( 7,  1)), ('\u00DC', ( 7,  2)), ('\u00E4', ( 7,  3)),
    ('\u00F6', ( 7,  4)), ('\u00FC', ( 7,  5)), ('\u00DF', ( 7,  6)), ('\u00C7', ( 7,  7)),
    ('\u00C9', ( 7,  8)), ('\u00E7', ( 7,  9)), ('\u00E0', ( 7, 10)), ('\u00E2', ( 7, 11)),
    ('\u00E8', ( 7, 12)), ('\u00E9', ( 7, 13)), ('\u00EA', ( 7, 14)), ('\u00EB', ( 7, 15)),
    ('\u00EE', ( 8,  0)), ('\u00EF', ( 8,  1)), ('\u00F4', ( 8,  2)), ('\u00FB', ( 8,  3)),
    ('\u00F9', ( 8,  4)), ('\u0153', ( 8,  5)), ('\u00BA', ( 8,  6)), ('\u00C0', ( 8,  7)),
    ('\u00C2', ( 8,  8)), ('\u0152', ( 8,  9)), ('\u00C8', ( 8, 10)), ('\u00CA', ( 8, 11)),
    ('\u00CB', ( 8, 12)), ('\u00CE', ( 8, 13)), ('\u00CF', ( 8, 14)), ('\u00D4', ( 8, 15)),
    ('\u00D9', ( 9,  0)), ('\u00DB', ( 9,  1)), ('\u00CC', ( 9,  2)), ('\u00EC', ( 9,  3)),
    ('\u00D2', ( 9,  4)), ('\u00F2', ( 9,  5)), ('\u00D1', ( 9,  6)), ('\u00F1', ( 9,  7)),
    ('\u00C1', ( 9,  8)), ('\u00E1', ( 9,  9)), ('\u00CD', ( 9, 10)), ('\u00ED', ( 9, 11)),
    ('\u00D3', ( 9, 12)), ('\u00F3', ( 9, 13)), ('\u00DA', ( 9, 14)), ('\u00FA', ( 9, 15)),
    ('\u00BF', (10,  0)), ('\u00A1', (10,  1)), ('\u00D8', (10,  2)), ('\u00F8', (10,  3)),
]

ALL_AVAILABLE_SLOTS = CYR_UPPER + CYR_LOWER + EUR_CHARS
assert len(ALL_AVAILABLE_SLOTS) == 118, f"Expected 118 slots, got {len(ALL_AVAILABLE_SLOTS)}"

# 3. All 63 Stacked Clusters
CLUSTERS = [
    'ต่ำ', 'ลำ', 'จำ', 'กำ', # Sara Am
    'กั', 'ก่', 'ข้', 'คี', 'คื', 'คุ', 'ค่', 'จุ', 'ชิ', 'ชื่', 'ช่',
    'ดิ', 'ด้', 'ตั', 'ตั้', 'ติ', 'ต็', 'ต่', 'ต้', 'ถึ', 'ทิ', 'ที่',
    'ทึ', 'ท้', 'นี้', 'นื้', 'นุ', 'น้', 'บั', 'ปิ', 'ผิ', 'ผู้', 'พื้',
    'ฟิ', 'ภั', 'มิ', 'มี', 'ม่', 'ยั', 'ยื', 'ย์', 'ริ', 'ริ่', 'รื',
    'ร่', 'ร้', 'ร์', 'ลี่', 'ลื', 'ล่', 'ล้', 'ว่', 'สู', 'ส่', 'ส์',
    'ห้', 'อี', 'เข้', 'เนื้', 'ไม่', 'ได้'
]

# 4. Base Consonants (35 consonants used in target texts)
CONSONANTS = [
    'ก', 'ข', 'ค', 'ง', 'จ', 'ฉ', 'ช', 'ญ', 'ณ', 'ด',
    'ต', 'ถ', 'ท', 'ธ', 'น', 'บ', 'ป', 'ผ', 'ฝ', 'พ',
    'ฟ', 'ภ', 'ม', 'ย', 'ร', 'ล', 'ว', 'ศ', 'ส', 'ห',
    'ฬ', 'อ', 'ฮ'
]

# 5. Standalone Front & Back Vowels
VOWELS = ['ะ', 'า', 'เ', 'แ', 'โ', 'ใ', 'ไ']

# Combine all target tokens
ALL_TOKENS_LIST = CLUSTERS + CONSONANTS + VOWELS
assert len(ALL_TOKENS_LIST) <= len(ALL_AVAILABLE_SLOTS), f"Too many tokens: {len(ALL_TOKENS_LIST)} > {len(ALL_AVAILABLE_SLOTS)}"
print(f"[+] Total target tokens to map: {len(ALL_TOKENS_LIST)} (Available slots: {len(ALL_AVAILABLE_SLOTS)})")

SLOTS = {}
for i, tok in enumerate(ALL_TOKENS_LIST):
    ch, cell = ALL_AVAILABLE_SLOTS[i]
    SLOTS[tok] = {
        'char': ch,
        'cell': cell,
    }

SORTED_TOKENS = sorted(SLOTS.keys(), key=len, reverse=True)

def encode_thai_string(s):
    res = []
    i = 0
    while i < len(s):
        matched = False
        for t in SORTED_TOKENS:
            if s.startswith(t, i):
                res.append(SLOTS[t]['char'])
                i += len(t)
                matched = True
                break
        if not matched:
            res.append(s[i])
            i += 1
    return "".join(res)

def render_token_glyph(font, token):
    cell = Image.new('RGBA', (CELL_SIZE, CELL_SIZE), (0, 0, 0, 0))
    d = ImageDraw.Draw(cell)
    
    # Custom rendering for multi-level stacked clusters to prevent overlapping
    if token == 'ตั้':
        d.text((2, TARGET_BASELINE), 'ตั', font=font, fill=(255, 255, 255, 255), anchor='ls')
        f_tone = ImageFont.truetype(FONT_TTF, 18)
        temp_t = Image.new('RGBA', (50, 50), (0, 0, 0, 0))
        d_t = ImageDraw.Draw(temp_t)
        d_t.text((25, 25), '้', font=f_tone, fill=(255, 255, 255, 255))
        arr_t = np.array(temp_t)[:, :, 3]
        coords = np.argwhere(arr_t > 20)
        min_y, min_x = coords.min(axis=0)
        max_y, max_x = coords.max(axis=0)
        crop_tho = temp_t.crop((min_x, min_y, max_x + 1, max_y + 1))
        cell.paste(crop_tho, (14, 0), crop_tho)
    elif token == 'ริ่':
        d.text((2, TARGET_BASELINE), 'ริ', font=font, fill=(255, 255, 255, 255), anchor='ls')
        f_tone = ImageFont.truetype(FONT_TTF, 18)
        temp_ek = Image.new('RGBA', (50, 50), (0, 0, 0, 0))
        d_ek = ImageDraw.Draw(temp_ek)
        d_ek.text((25, 25), '่', font=f_tone, fill=(255, 255, 255, 255))
        arr_ek = np.array(temp_ek)[:, :, 3]
        coords = np.argwhere(arr_ek > 20)
        min_y, min_x = coords.min(axis=0)
        max_y, max_x = coords.max(axis=0)
        crop_ek = temp_ek.crop((min_x, min_y, max_x + 1, max_y + 1))
        cell.paste(crop_ek, (11, 2), crop_ek)
    elif token == 'ชื่':
        d.text((2, TARGET_BASELINE), 'ชื', font=font, fill=(255, 255, 255, 255), anchor='ls')
        f_tone = ImageFont.truetype(FONT_TTF, 18)
        temp_ek = Image.new('RGBA', (50, 50), (0, 0, 0, 0))
        d_ek = ImageDraw.Draw(temp_ek)
        d_ek.text((25, 25), '่', font=f_tone, fill=(255, 255, 255, 255))
        arr_ek = np.array(temp_ek)[:, :, 3]
        coords = np.argwhere(arr_ek > 20)
        min_y, min_x = coords.min(axis=0)
        max_y, max_x = coords.max(axis=0)
        crop_ek = temp_ek.crop((min_x, min_y, max_x + 1, max_y + 1))
        cell.paste(crop_ek, (13, 0), crop_ek)
    elif token == 'พื้':
        d.text((2, TARGET_BASELINE), 'พื', font=font, fill=(255, 255, 255, 255), anchor='ls')
        f_tone = ImageFont.truetype(FONT_TTF, 18)
        temp_t = Image.new('RGBA', (50, 50), (0, 0, 0, 0))
        d_t = ImageDraw.Draw(temp_t)
        d_t.text((25, 25), '้', font=f_tone, fill=(255, 255, 255, 255))
        arr_t = np.array(temp_t)[:, :, 3]
        coords = np.argwhere(arr_t > 20)
        min_y, min_x = coords.min(axis=0)
        max_y, max_x = coords.max(axis=0)
        crop_tho = temp_t.crop((min_x, min_y, max_x + 1, max_y + 1))
        cell.paste(crop_tho, (14, 0), crop_tho)
    elif token == 'เนื้':
        d.text((2, TARGET_BASELINE), 'เนื', font=font, fill=(255, 255, 255, 255), anchor='ls')
        f_tone = ImageFont.truetype(FONT_TTF, 18)
        temp_t = Image.new('RGBA', (50, 50), (0, 0, 0, 0))
        d_t = ImageDraw.Draw(temp_t)
        d_t.text((25, 25), '้', font=f_tone, fill=(255, 255, 255, 255))
        arr_t = np.array(temp_t)[:, :, 3]
        coords = np.argwhere(arr_t > 20)
        min_y, min_x = coords.min(axis=0)
        max_y, max_x = coords.max(axis=0)
        crop_tho = temp_t.crop((min_x, min_y, max_x + 1, max_y + 1))
        cell.paste(crop_tho, (18, 0), crop_tho)
    else:
        bbox = font.getbbox(token)
        draw_x = 2 - min(0, bbox[0])
        d.text((draw_x, TARGET_BASELINE), token, font=font, fill=(255, 255, 255, 255), anchor='ls')
    return cell

def get_token_width(font, token):
    if token == 'เ': return 11.0
    if token == 'แ': return 17.0
    if token == 'โ': return 14.0
    if token == 'ใ': return 14.0
    if token == 'ไ': return 15.0
    if token == 'า': return 15.0
    if token == 'ะ': return 14.0
    if token == 'ร': return 16.0
    if token == 'ว': return 14.0
    if token == 'ง': return 17.0
    if token == 'จ': return 17.0
    if token == 'ต': return 17.0
    if token == 'ร้': return 17.0
    if token == 'ร์': return 17.0
    if token == 'ริ่': return 16.0
    
    bbox = font.getbbox(token)
    w = float(bbox[2] - bbox[0] + 4)
    # Clamp bounds for clean kerning
    return min(max(w, 16.0), 32.0)

def build_entry_342():
    print("[*] Building Entry 342 (Menu Font Atlas with 112 Universal Tight Thai Glyphs)...")
    img = Image.open(ORIG_PNG).convert("RGBA")
    font = ImageFont.truetype(FONT_TTF, FONT_SIZE)

    for token, slot in SLOTS.items():
        row, col = slot['cell']
        x0 = col * CELL_SIZE
        y0 = row * CELL_SIZE

        glyph_cell = render_token_glyph(font, token)

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

    # 1. Title Menus 1, 2, 3 (block 79264..79332)
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

    # 2. Title Menus 4, 5, 6, 7 (block 86672..86768)
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

    # 3. Save Prompts & Hero Selection in their ORIGINAL slot (7632..8140)
    # This prevents ANY collision with 66850 (Play Time / Recorded Date)!
    hero_and_save_options = [
        {'off': 32,   'pos': 7632, 'text': 'ต้องการสร้างบันทึกการเดินทางในช่องใด?', 'suffix': b'\x1bFH\x00'},
        {'off': 40,   'pos': 7751, 'text': 'เอาล่ะ โปรดเลือกผู้กล้าที่จะควบคุมในการผจญภัยในโลกนี้ การเลือกนี้จะไม่มีผลต่อเนื้อหาที่จะเข้าถึงได้ในเกม', 'suffix': b'\x00'},
        {'off': 44,   'pos': 7872, 'text': 'โปรดเลือกผู้กล้า', 'suffix': b'\x00'},
        {'off': 48,   'pos': 7894, 'text': 'ต่อไป โปรดตั้งชื่อให้แก่ผู้กล้าที่จะร่วมเดินทางไปด้วยกัน', 'suffix': b'\x00'},
    ]
    # In original file, the string block 7632 to 8140 has 508 bytes
    # Write them sequentially starting at 7632
    cur_pos = 7632
    for opt in hero_and_save_options:
        cyr_str = encode_thai_string(opt['text'])
        suffix = opt.get('suffix', b'\x00')
        raw_b = cyr_str.encode('utf-8') + suffix
        data[cur_pos : cur_pos + len(raw_b)] = raw_b
        struct.pack_into("<I", data, opt['off'], cur_pos - 0x20)
        print(f"    [+] Ptr {opt['off']:4d}: '{opt['text'][:30]}...' -> pos={cur_pos} ({len(raw_b)}B)")
        cur_pos = (cur_pos + len(raw_b) + 1) & ~1
    assert cur_pos <= 8140, f"Exceeded slot at {cur_pos} > 8140"

    # 4. All Graphics Settings Options & Values in SAFE Unused block (68076..68700)
    # This block is 100% UNUSED (624 bytes of 未使用) and does NOT overlap ANY active UI pointers!
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
        suffix = opt.get('suffix', b'\x00')
        raw_b = cyr_str.encode('utf-8') + suffix
        data[cur_pos : cur_pos + len(raw_b)] = raw_b
        struct.pack_into("<I", data, opt['off'], cur_pos - 0x20)
        print(f"    [+] Ptr {opt['off']:4d}: '{opt['text']}' -> pos={cur_pos} ({len(raw_b)}B)")
        cur_pos = (cur_pos + len(raw_b) + 1) & ~1

    assert cur_pos <= 68700, f"Exceeded unused block: {cur_pos} > 68700"
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
    for token, slot in SLOTS.items():
        ch = slot['char']
        utf8_b = ch.encode('utf-8')
        code = (utf8_b[0] << 8) | utf8_b[1]
        w = get_token_width(font, token)
        lines.append(f"        case 0x{code:04X}: return {w:.1f}f; // {token}")
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

