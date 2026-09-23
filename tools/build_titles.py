# -*- coding: utf-8 -*-
"""지역·던전 이름 이미지(font_dg00~16.gar)를 한글로 교체한다. 텍스처 크기가 같아 GAR 안에서 제자리 교체."""
import sys, os, struct
sys.path.insert(0, os.path.dirname(__file__))
import numpy as np
import ctxb, etc1, title_render as T

SRC = 'extract/jp/romfs/data/Region_JP/Japanese'
DST = 'work/romfs/data/Region_JP/Japanese'
FONT = 'tools/fonts/nsr/NanumSquareRoundEB.ttf'
NAMES = ['이루마의 항아리', '바다짐승의 무덤', '잃어버린 숲', '시련의 유적', '사막의 미궁', '수해의 미궁',
         '대협곡의 미궁', '카오스의 큰 구멍', '카라 사막', '바할 구릉', '카라하리 수해', '와쿠토 대협곡',
         '세르케족 마을', '리코스족 마을', '우아족 마을', '대현자의 방', '빛의 성역']

def textures(d):
    """(데이터 절대 오프셋, 길이, w, h, pf, dt) 목록"""
    out = []; i = 0
    while True:
        i = d.find(b'ctxb', i)
        if i < 0: return out
        size, cnt, _, coff, toff = struct.unpack_from('<5I', d, i + 4)
        c = i + coff
        if d[c:c + 4] == b'tex ':
            n = struct.unpack_from('<I', d, c + 8)[0]
            for k in range(n):
                e = c + 12 + k * 36
                ln, a, b, w, h, pf, dt, off = struct.unpack_from('<I6HI', d, e)
                out.append((i + toff + off, ln, w, h, pf, dt))
        i += 4

def main():
    os.makedirs(DST, exist_ok=True)
    for n, name in enumerate(NAMES):
        src = '%s/font_dg%02d.gar' % (SRC, n)
        d = bytearray(open(src, 'rb').read())
        tx = textures(d); assert len(tx) == 2, (src, len(tx))
        L0, L1 = T.render(name, FONT, T.measure(src))
        for (off, ln, w, h, pf, dt), img in zip(tx, (L0, L1)):
            assert (w, h, pf) == (256, 32, 0x675b)
            enc = etc1.encode(img, alpha=True); assert len(enc) == ln
            d[off:off + ln] = enc
        open('%s/font_dg%02d.gar' % (DST, n), 'wb').write(bytes(d))
        print('font_dg%02d  %s' % (n, name))

if __name__ == '__main__':
    main()
