# -*- coding: utf-8 -*-
"""database.gar 안의 .bdb 표 읽기. 헤더: 'bdb\0', u32 ?, u16 ver, u16 필드수, u16 레코드크기, u16 레코드수, ... 0x20부터 필드(u16 타입, u16 오프셋)."""
import struct
SZ = {1: 1, 2: 1, 3: 1, 4: 2, 5: 4, 6: 4, 0x0e: 4, 7: 4, 8: 4}
FMT = {1: 'B', 2: 'b', 3: 'B', 4: 'H', 5: 'I', 6: 'f', 0x0e: 'I', 7: 'i', 8: 'I'}
def load(path):
    d = open(path, 'rb').read()
    ver, nf, rs, nr = struct.unpack_from('<HHHH', d, 8)
    fields = [struct.unpack_from('<HH', d, 0x20 + i * 4) for i in range(nf)]
    base = 0x20 + nf * 4
    recs = []
    for r in range(nr):
        o = base + r * rs; row = []
        for t, off in fields:
            f = FMT.get(t, 'I')
            row.append(struct.unpack_from('<' + f, d, o + off)[0])
        recs.append(row)
    return fields, recs, d, base + nr * rs
