from PIL import Image
import numpy as np

img = Image.open(r"C:\Users\Supakiat\.gemini\antigravity\brain\ab5bc3db-774b-46d7-96ba-65470fc9eb39\.user_uploaded\media_1791953123013_908ffa50.png")
print("User screenshot size:", img.size)

# The menu is centered on screen.
# Let's crop the center area around y=300..800, x=500..1400 (if 1920x1080)
w, h = img.size
crop = img.crop((int(w * 0.35), int(h * 0.3), int(w * 0.65), int(h * 0.85)))
crop.save("workspace/user_chinese_menu_crop.png")
print("Saved user_chinese_menu_crop.png")
