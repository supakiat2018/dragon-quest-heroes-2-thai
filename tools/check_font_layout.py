from PIL import Image
import numpy as np

img = Image.open('workspace/tex_340/entry_340.TEX0.dxt5.dds')

# Let's inspect the first 10 characters of Row 0, Row 1, Row 2, Row 3, Row 4
# Let's see what is at:
# R=0, C=0..5
# R=1, C=0..5
# R=2, C=0..5
# R=3, C=0..5
# R=4, C=0..5

# In Big5:
# 0xA140 is space (0xA140 in Big5 is IDEOGRAPHIC SPACE \u3000)
# Notice R=0, C=0 was 0 pixels! (CNT = 0). IDEOGRAPHIC SPACE!
# 0xA141 is \uFF0C (Fullwidth Comma ，)
# 0xA142 is \u3001 (Ideographic Comma 、)
# 0xA143 is \u3002 (Ideographic Full Stop 。)

# In Row 3:
# What was at R=3, C=0?
# Earlier we found R=3, C=0 was Ψ (0xA35A)!
# Why is Ψ at R=3, C=0?
# Let's check:
# 0xA1 has how many characters in this font?
# 0xA2 has how many characters?
# 0xA3 has how many characters?
# Let's inspect Row 1, Col 0 and Row 2, Col 0 to see what Big5 codes they correspond to!

def get_cell(r, c):
    return np.array(img.crop((c*36, r*36, (c+1)*36, (r+1)*36)))[:, :, 3]

# Let's print which Big5 symbol matches R=0, C=1, C=2, C=3
print("R=0, C=0 is empty (Space 0xA140)")
print("R=0, C=1 count:", np.count_nonzero(get_cell(0, 1) > 30))
print("R=0, C=2 count:", np.count_nonzero(get_cell(0, 2) > 30))
print("R=0, C=3 count:", np.count_nonzero(get_cell(0, 3) > 30))

# What is at R=0, C=112?
print("R=0, C=112 count:", np.count_nonzero(get_cell(0, 112) > 30))

# What is at R=1, C=0?
print("R=1, C=0 count:", np.count_nonzero(get_cell(1, 0) > 30))
