from PIL import Image
import numpy as np

img = Image.open('workspace/user_uploaded_menu.png')
# Convert to grayscale / lightness
arr = np.array(img.convert('L'))

# In the top area, find the first menu option "開始冒險"
# Let's crop y=0..100
top_crop = arr[0:100, :]

# Find bright pixels (text is yellow or white/golden with shadow)
# Let's inspect RGB values of characters
rgb_arr = np.array(img)
# Sample some lines
for y in range(20, 80, 5):
    bright_x = np.where(rgb_arr[y, :, 0] > 180)[0]
    if len(bright_x) > 0:
        print(f"y={y:2d}: bright x min={bright_x.min()}, max={bright_x.max()}, count={len(bright_x)}")
