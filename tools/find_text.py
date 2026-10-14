import struct
import zlib
import os
import sys

idx_path = r"C:\Program Files (x86)\Steam\steamapps\common\DRAGON QUEST HEROES™ II\LINKDATA.IDX"
bin_path = r"C:\Program Files (x86)\Steam\steamapps\common\DRAGON QUEST HEROES™ II\LINKDATA.BIN"

targets = [
    b"Venture Forth",
    b"Create Adventure Log",
    b"Graphics Settings",
    b"Keyboard Settings",
    b"Exit Game"
]

print("Reading LINKDATA.IDX...", flush=True)
with open(idx_path, "rb") as f_idx:
    entries = []
    while True:
        buf = f_idx.read(32)
        if len(buf) < 32:
            break
        entries.append(struct.unpack("<QQQQ", buf))

print(f"Total entries: {len(entries)}", flush=True)

def decompress_entry(f_bin, off, size, zsize, zip_flag):
    if size == 0:
        return b""
    if zip_flag == 0:
        f_bin.seek(off)
        return f_bin.read(size)
    
    f_bin.seek(off)
    chunk_size, chunks, full_size = struct.unpack("<III", f_bin.read(12))
    mode = 1 if chunk_size == 0xffffffff else 0
    effective_chunk_size = 0x10000 if mode == 1 else chunk_size
    
    chunk_zsizes = [struct.unpack("<I", f_bin.read(4))[0] for _ in range(chunks)]
    
    out = bytearray()
    padding_offset = off
    for x in range(chunks):
        # padding 0x80 relative to padding_offset
        pos = f_bin.tell()
        rel = pos - padding_offset
        pad = (128 - (rel % 128)) % 128
        f_bin.seek(pad, os.SEEK_CUR)
        padding_offset = f_bin.tell()
        
        chunk_zsize = chunk_zsizes[x]
        if len(out) + chunk_zsize == full_size:
            # uncompressed chunk
            out.extend(f_bin.read(chunk_zsize))
        else:
            if mode == 0:
                chunk_zsize = struct.unpack("<I", f_bin.read(4))[0]
            zdata = f_bin.read(chunk_zsize)
            if mode == 0:
                decomp = zlib.decompress(zdata)
            else:
                decomp = zlib.decompress(zdata, -zlib.MAX_WBITS)
            out.extend(decomp)
    return bytes(out)

if __name__ == "__main__":
    matches = []

    with open(bin_path, "rb") as f_bin:
        for i, (off, size, zsize, zip_flag) in enumerate(entries):
            if size == 0:
                continue
            if size > 30 * 1024 * 1024:
                continue
            try:
                data = decompress_entry(f_bin, off, size, zsize, zip_flag)
                found_any = False
                for t in targets:
                    if t in data:
                        print(f"MATCH: Entry {i} contains '{t.decode()}' (size={len(data)})", flush=True)
                        matches.append((i, t))
                        found_any = True
                if found_any:
                    out_name = f"entry_{i}.bin"
                    with open(out_name, "wb") as f_out:
                        f_out.write(data)
                    print(f"Dumped entry {i} to {out_name}", flush=True)
            except Exception as e:
                pass
            if i % 1000 == 0:
                print(f"Progress: scanned {i}/{len(entries)} entries...", flush=True)

    print("Finished scanning. Matches found:", matches, flush=True)
