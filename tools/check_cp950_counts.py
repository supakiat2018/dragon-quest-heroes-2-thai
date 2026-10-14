from PIL import Image
import numpy as np

img = Image.open('workspace/tex_340/entry_340.TEX0.dxt5.dds')

# Let's inspect:
# Where does 0xA1 start and end?
# Where does 0xA2 start and end?
# Where does 0xA3 start and end?
# Where does 0xA4 start and end?
# Where does 0xA5 start and end?

# We know:
# Row 0, Col 0 is 0xA140.
# Row 4, Col 0 is 0xA540.
# That means from 0xA140 to 0xA540 is exactly 4 * 113 = 452 cells!
# But in standard Big5, 4 lead bytes * 157 = 628 characters!
# Why are there 452 cells instead of 628?
# Did some lead bytes not have 157 characters?
# For example:
# Does 0xA1 have only symbols (A140 to A1FE)?
# Does 0xA2 have only A240 to A2FE?
# Does 0xA3 have only A340 to A3FE?
# Does 0xA4 have 0xA440 to 0xA4FE?
# Wait! In standard Big5:
# 0xA1: 0xA140-0xA17E (63) + 0xA1A1-0xA1FE (94) = 157
# 0xA2: 0xA240-0xA27E (63) + 0xA2A1-0xA2FE (94) = 157?
# But wait! In Big5, 0xA2 has only A240-A27E (63) and A2A1-0xA2C1 (33) = 96 characters! (A2C2-A2FE is undefined!)
# In 0xA3, A340-A37E (63) and A3A1-A3BF (31) = 94 characters! (A3C0-A3FE is undefined!)
# Let's check!
print("Checking undefined characters in CP950:")
for b1 in [0xA1, 0xA2, 0xA3, 0xA4]:
    valid = 0
    for b2 in list(range(0x40, 0x7F)) + list(range(0xA1, 0xFF)):
        try:
            bytes([b1, b2]).decode('cp950')
            valid += 1
        except:
            pass
    print(f"0x{b1:02X} has {valid} valid CP950 characters")
