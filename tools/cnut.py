# -*- coding: utf-8 -*-
"""Squirrel 3 바이트코드(.gsb) 읽기 — 에버오아시스 스크립트용. SQInteger 4바이트."""
import struct
OT_NULL, OT_INT, OT_FLOAT, OT_BOOL, OT_STR = 0x01000001, 0x05000002, 0x05000004, 0x01000008, 0x08000010
OPS = ['LINE','LOAD','LOADINT','LOADFLOAT','DLOAD','TAILCALL','CALL','PREPCALL','PREPCALLK','GETK','MOVE',
       'NEWSLOT','DELETE','SET','GET','EQ','NE','ADD','SUB','MUL','DIV','MOD','BITW','RETURN','LOADNULLS',
       'LOADROOT','LOADBOOL','DMOVE','JMP','JCMP','JZ','SETOUTER','GETOUTER','NEWOBJ','APPENDARRAY',
       'COMPARITH','INC','INCL','PINC','PINCL','CMP','EXISTS','INSTANCEOF','AND','OR','NEG','NOT','BWNOT',
       'CLOSURE','YIELD','RESUME','FOREACH','POSTFOREACH','CLONE','TYPEOF','PUSHTRAP','POPTRAP','THROW',
       'NEWSLOTA','GETBASE','CLOSE']

class R:
    def __init__(s, d, p=0): s.d = d; s.p = p
    def u32(s): v = struct.unpack_from('<I', s.d, s.p)[0]; s.p += 4; return v
    def i32(s): v = struct.unpack_from('<i', s.d, s.p)[0]; s.p += 4; return v
    def f32(s): v = struct.unpack_from('<f', s.d, s.p)[0]; s.p += 4; return v
    def tag(s):
        t = s.d[s.p:s.p + 4]; s.p += 4
        assert t == b'TRAP', (hex(s.p), t)
    def obj(s):
        t = s.u32()
        if t == OT_STR:
            n = s.u32(); v = s.d[s.p:s.p + n].decode('utf8', 'replace'); s.p += n; return v
        if t == OT_INT: return s.i32()
        if t == OT_FLOAT: return s.f32()
        if t == OT_BOOL: return bool(s.u32())
        if t == OT_NULL: return None
        raise ValueError('객체 타입 %x @%x' % (t, s.p))

def func(r):
    r.tag(); src = r.obj(); name = r.obj(); r.tag()
    nlit, npar, nout, nloc, nline, ndef, nins, nfun = [r.u32() for _ in range(8)]
    r.tag(); lits = [r.obj() for _ in range(nlit)]
    r.tag(); pars = [r.obj() for _ in range(npar)]
    r.tag(); outs = [(r.u32(), r.obj(), r.obj()) for _ in range(nout)]
    r.tag(); locs = []
    for _ in range(nloc):
        n = r.obj(); pos, so, eo = r.u32(), r.u32(), r.u32(); locs.append((n, pos, so, eo))
    r.tag(); lines = [(r.i32(), r.i32()) for _ in range(nline)]
    r.tag(); defs = [r.i32() for _ in range(ndef)]
    r.tag(); ins = []
    for _ in range(nins):
        a1 = struct.unpack_from('<i', r.d, r.p)[0]; op, a0, a2, a3 = r.d[r.p + 4:r.p + 8]; r.p += 8
        ins.append((op, a0, a1, a2, a3))
    r.tag(); funs = [func(r) for _ in range(nfun)]
    stack = r.u32(); gen = r.d[r.p]; var = r.d[r.p + 1]; r.p += 2
    return dict(name=name, lits=lits, pars=pars, outs=outs, locs=locs, ins=ins, funs=funs)

def load(path):
    d = open(path, 'rb').read()
    assert d[:2] == b'\xfa\xfa' and d[2:6] == b'RIQS'
    r = R(d, 10)   # FAFA RIQS u32(1)
    return func(r)

def walk(f, path=''):
    p = (path + '.' if path else '') + str(f['name'])
    yield p, f
    for g in f['funs']: yield from walk(g, p)
