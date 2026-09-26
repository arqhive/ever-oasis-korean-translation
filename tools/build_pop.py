# -*- coding: utf-8 -*-
"""무지개 팝 글자·가드 이미지를 한글로 교체(ui_town / ui_field / ui_keep, 제자리 교체)."""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))
from PIL import Image
import ctxb, etc1, gptimg, pop_render as P
from build_title_logo import chunks

SRC = 'extract/jp/romfs/data/Region_JP/Japanese'
DST = 'work/romfs/data/Region_JP/Japanese'
JUA = 'tools/fonts/Jua.ttf'
NSR = 'tools/fonts/nsr/NanumSquareRoundEB.ttf'
# gar: [(ctxb 오프셋, 한글, 원본 글자 수)]
POP = {
    'ui_town': [(0x26800, '레벨 업!', 7), (0x2a880, '레벨 업!', 7), (0x2b900, '랭크', 3), (0x2d980, '초대성공', 4)],
    'ui_field': [(0x46e00, '클리어!', 4)],
    'ui_keep': [(0xd8f80, '클리어!', 4)],
}
GUARD = ('ui_field', 0x31300, '가드')

def render_target(d, key, text, letters=None, white=False, gar=None):
    off, ln, w, h, pf, dt = chunks(d)[key]
    orig = ctxb.decode(bytes(d[off:off + ln]), w, h, pf, dt)
    g = gptimg.load('%s_%x.png' % (gar, key)) if gar else None
    if g is not None:                       # GPT 가 그려 준 글자를 원본 자리에 넣는다
        img = gptimg.place(g, orig)
        enc = etc1.encode_rgba4(img) if (pf, dt) == (0x6752, 0x8033) else etc1.encode(img, alpha=(pf == 0x675b))
        assert len(enc) == ln, (key, len(enc), ln)
        d[off:off + ln] = enc
        return orig, img
    if white:
        me = P.measure(orig, white=True)
        img = P.render(text, NSR, me, shear=0.12, fill_h=0.95, rings=P.RINGS_WHITE,
                       colors=[((240, 232, 228), (224, 214, 210))] * len(text.replace(' ', '')))
    else:
        me = P.measure(orig)
        img = P.render(text, JUA, me, letters=letters)
    if pf == 0x6752 and dt == 0x8033: enc = etc1.encode_rgba4(img)
    else: enc = etc1.encode(img, alpha=(pf == 0x675b))
    assert len(enc) == ln, (key, len(enc), ln)
    d[off:off + ln] = enc
    return orig, img

def main(preview=None):
    os.makedirs(DST, exist_ok=True); shots = []
    for gar, items in POP.items():
        d = bytearray(open('%s/%s.gar' % (SRC, gar), 'rb').read())
        for key, text, n in items: shots.append(render_target(d, key, text, letters=n, gar=gar))
        if gar == GUARD[0]: shots.append(render_target(d, GUARD[1], GUARD[2], white=True, gar=gar))
        open('%s/%s.gar' % (DST, gar), 'wb').write(bytes(d)); print(gar, '갱신')
    return shots

if __name__ == '__main__':
    main()
