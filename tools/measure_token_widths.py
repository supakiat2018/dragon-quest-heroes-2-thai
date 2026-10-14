from PIL import Image, ImageFont, ImageDraw
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FONT_TTF = os.path.join(BASE_DIR, "Pridi", "Pridi-Bold.ttf")

tokens = [
    'เ', 'ริ่', 'ม', 'ก', 'า', 'ร', 'ดิ', 'น', 'ท', 'ง',
    'ส', 'ร้', 'บั', 'ทึ', 'ล', 'บ', 'ตั้', 'ค่', 'ฟิ', 'คี',
    'ย์', 'อ', 'ร์', 'ด', 'ส์', 'จ', 'ค'
]

# Test font size 32 and 34
for fsize in [30, 32, 34]:
    font = ImageFont.truetype(FONT_TTF, fsize)
    print(f"=== Font size {fsize} ===")
    for t in tokens:
        bbox = font.getbbox(t)
        gw = bbox[2] - bbox[0]
        gh = bbox[3] - bbox[1]
        print(f"'{t:>3s}': w={gw:2d}, h={gh:2d}, bbox={bbox}")
