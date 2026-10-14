import struct
import os

for idx in range(343, 350):
    p = f"workspace/entry_{idx}.bin"
    if os.path.exists(p):
        with open(p, "rb") as f:
            data = f.read()
        print(f"=== Entry {idx} (size={len(data)}) ===")
        # Print first 64 bytes
        print("Hex:", data[:64].hex(' '))
        # Print integers
        count = min(16, len(data) // 4)
        ints = struct.unpack(f"<{count}I", data[:count*4])
        print("Ints:", ints)
