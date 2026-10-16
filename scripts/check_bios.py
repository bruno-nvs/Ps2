#!/usr/bin/env python3
"""Verifica um dump de BIOS de PS2 antes de usar no AetherSX2.

Confere tamanho, a tabela ROMDIR (todos os módulos dentro do arquivo), a versão
(ROMVER), a região e os módulos essenciais. Não modifica o arquivo.
Uso: check_bios.py <bios.bin> [...]"""
import hashlib
import struct
import sys

REGIONS = {"J": "Japão (NTSC-J)", "A": "EUA (NTSC-U)", "E": "Europa (PAL)", "H": "Ásia (NTSC)",
           "C": "China", "T": "T10K/devkit", "X": "Test/QA"}
REQUIRED = ("RESET", "ROMDIR", "ROMVER", "IOPBOOT", "EELOAD", "OSDSYS", "KERNEL")
VALID_SIZES = (4 << 20, 8 << 20, 12 << 20)  # 4 MiB (comum), 8/12 MiB (DTL/consoles com DVD player)


def check(path):
    d = open(path, "rb").read()
    problems = []
    print(f"== {path}")
    print(f"tamanho: {len(d)} bytes")
    if len(d) not in VALID_SIZES:
        problems.append("tamanho incomum (dump incompleto ou com cabeçalho extra?)")
    for name, h in (("MD5", hashlib.md5), ("SHA-1", hashlib.sha1), ("SHA-256", hashlib.sha256)):
        print(f"{name}: {h(d).hexdigest()}")

    p = d.find(b"RESET\0\0\0\0\0")
    if p < 0:
        problems.append("tabela ROMDIR não encontrada: não é uma BIOS de PS2 válida")
        return report(problems)

    entries, off = {}, 0
    while p + 16 <= len(d):
        name = d[p:p + 10].rstrip(b"\0").decode("latin1")
        if not name:
            break
        _ext, size = struct.unpack("<HI", d[p + 10:p + 16])
        entries.setdefault(name, (off, size))
        off += (size + 15) & ~15
        p += 16
    print(f"módulos no ROMDIR: {len(entries)}  fim do último módulo: {off:#x}")
    if off > len(d):
        problems.append(f"ROMDIR aponta além do fim do arquivo ({off:#x} > {len(d):#x}): dump truncado")
    missing = [m for m in REQUIRED if m not in entries]
    if missing:
        problems.append("módulos essenciais ausentes: " + ", ".join(missing))

    if "ROMVER" in entries:
        o, s = entries["ROMVER"]
        rv = d[o:o + s].split(b"\n")[0].decode("latin1")
        print(f"ROMVER: {rv}")
        if len(rv) >= 14:
            ver = f"{int(rv[0:2])}.{rv[2:4]}"
            kind = {"C": "console", "D": "devkit"}.get(rv[5], rv[5])
            date = f"{rv[6:10]}-{rv[10:12]}-{rv[12:14]}"
            print(f"versão {ver}, região {REGIONS.get(rv[4], rv[4])}, {kind}, data {date}")
        else:
            problems.append("ROMVER malformado")
    if "VERSTR" in entries:
        o, s = entries["VERSTR"]
        print("VERSTR:", d[o:o + s].replace(b"\0", b" ").decode("latin1").strip().split("  ")[0])
    if "DECKARD" in entries:
        print("contém DECKARD (IOP PowerPC): modelo Slim SCPH-75000 ou posterior")
    return report(problems)


def report(problems):
    if problems:
        for pr in problems:
            print("PROBLEMA:", pr)
        return False
    print("OK: estrutura íntegra")
    return True


if __name__ == "__main__":
    ok = all([check(f) for f in sys.argv[1:]])
    sys.exit(0 if ok else 1)
