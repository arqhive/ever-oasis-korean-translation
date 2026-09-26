# -*- coding: utf-8 -*-
"""지역·던전 이름 이미지를 한글로 교체한다. 텍스처 크기가 같아 GAR 안에서 제자리 교체.

대상은 두 벌이다(내용이 완전히 같다).
  - Region_JP/Japanese/font_dg00~16.gar   : 각 2장(본체 + 발광)
  - async/font_dangname_00~16.gar         : 본체 1장
    async/font_dangname_00~16ext.gar      : 발광 1장

`work/GPT결과/font_dgNN.png` 가 있으면 그 그림을 쓰고, 발광은 본체에서 만든다.
없으면 기존 폰트 렌더링(title_render)으로 그린다.
"""
import sys, os, struct
sys.path.insert(0, os.path.dirname(__file__))
import numpy as np
from PIL import Image
import ctxb, etc1, gptimg, title_render as T

SRC = 'extract/jp/romfs/data/Region_JP/Japanese'
DST = 'work/romfs/data/Region_JP/Japanese'
ASRC = 'extract/jp/romfs/data/async'
ADST = 'work/romfs/data/async'
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


def put(d, tx, img):
    off, ln, w, h, pf, dt = tx
    enc = etc1.encode(img, alpha=True)
    assert len(enc) == ln, (len(enc), ln)
    d[off:off + ln] = enc


def layers(n, name, src):
    """(본체, 발광) 두 장을 만든다."""
    d = open(src, 'rb').read()
    tx = textures(d)
    ob = ctxb.decode(d[tx[0][0]:tx[0][0] + tx[0][1]], *tx[0][2:])
    og = ctxb.decode(d[tx[1][0]:tx[1][0] + tx[1][1]], *tx[1][2:]) if len(tx) > 1 else None
    g = gptimg.load('font_dg%02d.png' % n)
    if g is None:
        return T.render(name, FONT, T.measure(src)) + (False,)
    body = gptimg.place(g, ob)
    return body, gptimg.glow(body, og), True


def main():
    os.makedirs(DST, exist_ok=True); os.makedirs(ADST, exist_ok=True)
    for n, name in enumerate(NAMES):
        src = '%s/font_dg%02d.gar' % (SRC, n)
        body, glow, used_gpt = layers(n, name, src)
        d = bytearray(open(src, 'rb').read())
        tx = textures(d); assert len(tx) == 2, (src, len(tx))
        for t, img in zip(tx, (body, glow)):
            assert (t[2], t[3], t[4]) == (256, 32, 0x675b)
            put(d, t, img)
        open('%s/font_dg%02d.gar' % (DST, n), 'wb').write(bytes(d))
        # async 쪽 같은 이름(본체 / ext = 발광)
        for suffix, img in (('', body), ('ext', glow)):
            p = '%s/font_dangname_%02d%s.gar' % (ASRC, n, suffix)
            if not os.path.exists(p): continue
            a = bytearray(open(p, 'rb').read())
            at = textures(a)
            if not at: continue
            put(a, at[0], img)
            open('%s/font_dangname_%02d%s.gar' % (ADST, n, suffix), 'wb').write(bytes(a))
        print('font_dg%02d  %-12s %s' % (n, name, 'GPT 그림' if used_gpt else '폰트 렌더링'))


if __name__ == '__main__':
    main()
