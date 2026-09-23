# -*- coding: utf-8 -*-
"""Grezzo GAR v5 풀기: 헤더(u32 크기, u16 타입수, u16 파일수, u32 타입표, u32 파일표, u32 데이터), 파일표 16B {u32 크기, u32 오프셋, u32 이름, u32 전체이름}."""
import struct
def files(path):
    d = open(path, 'rb').read()
    size, nt, nf, toff, foff, doff = struct.unpack_from('<IHHIII', d, 4)
    out = []
    for i in range(nf):
        sz, off, no, fo = struct.unpack_from('<4I', d, foff + i * 16)
        name = d[fo:d.index(b'\0', fo)].decode('ascii', 'replace') if fo else ''
        out.append((name, d[off:off + sz]))
    return out
