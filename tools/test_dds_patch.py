import os
import shutil
import numpy as np
from PIL import Image, ImageFont, ImageDraw
from test_cell_encoder import encode_cell_dxt5

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FONT_TTF = os.path.join(BASE_DIR, "Pridi", "Pridi-Bold.ttf")
DDS_PATH = os.path.join(BASE_DIR, "workspace", "tex_340", "entry_340.TEX0.dxt5.dds")
TEST_DDS = os.path.join(BASE_DIR, "workspace", "test_patch_340.dds")

# Copy DDS to test_patch_340.dds
shutil.copyfile(DDS_PATH, TEST_DDS)

# Render 'ก' into 36x36 cell
cell = Image.new('RGBA', (36, 36), (0, 0, 0, 0))
draw = ImageDraw.Draw(cell)
font = ImageFont.truetype(FONT_TTF, 30)
draw.text((18, 27), 'ก', font=font, fill=(255, 255, 255, 255), anchor="ms")

# Encode cell to 9 rows of DXT5 data
cell_dxt_rows = encode_cell_dxt5(cell)

# Row 3, Col 69
r = 3
c = 69
CELL_SIZE = 36
WIDTH = 4096
BLOCKS_PER_ROW = WIDTH // 4 # 1024
BLOCK_BYTES = 16
SCANBAND_BYTES = BLOCKS_PER_ROW * BLOCK_BYTES # 16384 bytes
DDS_HEADER_SIZE = 128

bx = c * 9
by = r * 9

with open(TEST_DDS, "r+b") as f:
    for dy in range(9):
        block_row = by + dy
        band_offset = DDS_HEADER_SIZE + block_row * SCANBAND_BYTES
        offset = band_offset + bx * BLOCK_BYTES
        f.seek(offset)
        f.write(cell_dxt_rows[dy])

print(f"Patched Row {r}, Col {c} with 'ก'!")

# Read back with PIL to verify!
reloaded = Image.open(TEST_DDS)
readback_cell = np.array(reloaded.crop((c*36, r*36, (c+1)*36, (r+1)*36)))[:, :, 3]
cnt = np.count_nonzero(readback_cell > 30)
print(f"Readback alpha pixel count: {cnt}")
for y in range(0, 36, 2):
    line = ''.join(['#' if readback_cell[y, x] > 50 else '.' for x in range(0, 36, 2)])
    if '#' in line:
        print(f"{y:2d}: {line}")
