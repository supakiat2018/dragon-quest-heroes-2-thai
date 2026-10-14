import struct
import numpy as np
from PIL import Image

def encode_cell_dxt5(cell_img):
    """
    Encode a 36x36 RGBA PIL image to 9 rows of 9 DXT5 blocks (144 bytes per row).
    Returns list of 9 byte strings, each 144 bytes (9 blocks * 16 bytes).
    """
    assert cell_img.size == (36, 36)
    arr = np.array(cell_img)
    alpha = arr[:, :, 3]
    
    # Color block for white glyph: RGB (255, 255, 255)
    color_block = b'\xff\xff\xff\xff\x00\x00\x00\x00'
    pal = np.array([255, 0, 219, 182, 146, 109, 73, 36])
    
    rows_dxt = []
    for by in range(9):
        row_bytes = bytearray(9 * 16)
        for bx in range(9):
            blk = alpha[by*4:(by+1)*4, bx*4:(bx+1)*4].flatten()
            if not blk.any():
                # Completely transparent block
                # Alpha 0 for all pixels: endpoints (0, 0), indices all 0
                alpha_block = b'\x00\x00\x00\x00\x00\x00\x00\x00'
                block_data = alpha_block + color_block
            else:
                diff = np.abs(blk[:, None] - pal[None, :])
                indices = np.argmin(diff, axis=1)
                bits = 0
                for p in range(16):
                    bits |= (int(indices[p]) & 7) << (3 * p)
                alpha_block = struct.pack('<BB', 255, 0) + bits.to_bytes(6, 'little')
                block_data = alpha_block + color_block
            row_bytes[bx*16:(bx+1)*16] = block_data
        rows_dxt.append(bytes(row_bytes))
    return rows_dxt

# Test encode_cell_dxt5 with a blank image
blank = Image.new('RGBA', (36, 36), (0, 0, 0, 0))
res = encode_cell_dxt5(blank)
print(f"Encoded 36x36 blank cell: {len(res)} rows, {len(res[0])} bytes per row (total={len(res)*len(res[0])})")
