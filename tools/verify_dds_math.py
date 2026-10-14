import os
import struct
import numpy as np
from PIL import Image

# Verify block offset calculation
CELL_SIZE = 36
BLOCKS_PER_CELL = CELL_SIZE // 4 # 9
WIDTH = 4096
HEIGHT = 8192
BLOCKS_PER_ROW = WIDTH // 4 # 1024
BLOCK_BYTES = 16
SCANBAND_BYTES = BLOCKS_PER_ROW * BLOCK_BYTES # 16384 bytes
DDS_HEADER_SIZE = 128

def get_cell_block_offsets(row, col):
    x = col * CELL_SIZE
    y = row * CELL_SIZE
    bx = x // 4
    by = y // 4
    offsets = []
    for dy in range(BLOCKS_PER_CELL):
        block_row = by + dy
        band_offset = DDS_HEADER_SIZE + block_row * SCANBAND_BYTES
        row_start_offset = band_offset + bx * BLOCK_BYTES
        offsets.append(row_start_offset)
    return offsets

# Let's test with Row 5, Col 0 (世)
offsets = get_cell_block_offsets(5, 0)
print(f"Row 5, Col 0 block rows: {len(offsets)}, first offset: {offsets[0]}, last offset: {offsets[-1]}")
total_file_size = DDS_HEADER_SIZE + (HEIGHT // 4) * SCANBAND_BYTES
print(f"Calculated DDS total size: {total_file_size} bytes (matches 33554560: {total_file_size == 33554560})")
