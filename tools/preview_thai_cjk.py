import os
from PIL import Image, ImageFont, ImageDraw

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FONT_TTF = os.path.join(BASE_DIR, "Pridi", "Pridi-Bold.ttf")

CELL_SIZE = 36
# Font size for 36x36 cell
# In Pridi, a 28-30pt font gives ~24-28px height, leaving room for upper and lower vowels!
font = ImageFont.truetype(FONT_TTF, 28)

test_glyphs = [
    'ก', 'ง', 'จ', 'ด', 'ท', 'น', 'บ', 'ม', 'ย', 'ร', 'ล', 'ส', 'อ',
    'เ', 'า',
    'ริ่', 'ดิ', 'ร้', 'บั', 'ทึ', 'ตั้', 'ค่', 'ฟิ', 'คี', 'ย์', 'ร์', 'ส์'
]

# Create a preview image of all glyphs
preview = Image.new('RGBA', (CELL_SIZE * len(test_glyphs), CELL_SIZE), (40, 40, 40, 255))
draw = ImageDraw.Draw(preview)

for i, g in enumerate(test_glyphs):
    x_offset = i * CELL_SIZE
    # Draw grid box
    draw.rectangle([x_offset, 0, x_offset + CELL_SIZE - 1, CELL_SIZE - 1], outline=(100, 100, 100, 255))
    
    # Calculate text bounding box to center it nicely
    bbox = font.getbbox(g)
    # bbox is (left, top, right, bottom)
    gw = bbox[2] - bbox[0]
    gh = bbox[3] - bbox[1]
    
    # Baseline around Y=26
    # Let's align on baseline Y=26
    tx = x_offset + (CELL_SIZE - gw) // 2 - bbox[0]
    ty = 26 - bbox[3] + (bbox[3] - bbox[1]) // 2 # or fixed baseline
    
    # Let's use fixed baseline Y=26 for consonants
    # For glyphs with upper vowels, bbox extends upwards
    # Baseline at y=27
    tx = x_offset + max(2, (CELL_SIZE - gw) // 2 - bbox[0])
    ty = 27 - bbox[3] if bbox[3] > 20 else 27 - 20
    
    # Actually, PIL font.getmask or draw.text with anchor
    draw.text((x_offset + CELL_SIZE // 2, 26), g, font=font, fill=(255, 255, 255, 255), anchor="ms")

out_path = os.path.join(BASE_DIR, "workspace", "preview_thai_cjk_glyphs.png")
preview.save(out_path)
print(f"Saved preview to: {out_path}")
