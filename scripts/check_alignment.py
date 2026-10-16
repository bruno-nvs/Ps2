#!/usr/bin/env python3
"""Confere se as .so não comprimidas estão alinhadas em 4 KiB (necessário com extractNativeLibs=false)."""
import struct
import sys
import zipfile

ok = True
for path in sys.argv[1:]:
    with zipfile.ZipFile(path) as z, open(path, "rb") as f:
        for info in z.infolist():
            if not info.filename.endswith(".so"):
                continue
            f.seek(info.header_offset)
            hdr = f.read(30)
            name_len, extra_len = struct.unpack("<HH", hdr[26:30])
            data = info.header_offset + 30 + name_len + extra_len
            good = info.compress_type == zipfile.ZIP_STORED and data % 4096 == 0
            ok &= good
            print(f"{'OK ' if good else 'ERRO'} {info.filename} offset={data} stored={info.compress_type == 0}")
sys.exit(0 if ok else 1)
