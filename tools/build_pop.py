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
# 글자 잉크를 이 세로 범위(텍셀) 안으로 줄여 넣을 텍스처(가로 가운데 유지). 지금은 없음.
# (10/9 「레벨 업!」 의 「벨」 이 잘려 보인 건 가림이 아니라 GPT 글자 모양 탓이라 쓰지 않음)
FIT = {}

# 레이아웃이 텍스처를 가로로 잘라 판 두 장에 나눠 붙이는 경우: 글자 덩어리를 경계 양쪽으로 옮긴다(그림은 그대로).
# 레벨 업 화면 3종(dl_level_up_town_u·_hanamise_u·_u .ibb)은 level_up_eff_01(256×64)을 u=114/256 에서 잘라
# 왼쪽(0~114)·오른쪽(114~256, 폭 138 로 눌러 담음) 판에 붙이고, 두 판이 화면에서 약 8px 겹친다.
# 그래서 106~114px 띠가 사라져 「벨」 가운데가 날아갔다(10/9). → 앞 n 개 덩어리는 left_max 이하, 나머지는 right_min 이상.
SPLIT = {}   # 10/9 시험: 판 위치를 고쳐 겹침을 없애면 필요 없음. 안 되면 {('ui_town', 0x26800): (2, 105, 117)} 로 되돌림

# 레이아웃 판 위치 고치기: (gar, ibb 이름) → [(ibb 안 판 기록 오프셋, 원래 x, 새 x)]
# 오른쪽 판(배율 0.9, 폭 138)이 왼쪽 판과 약 5px 겹쳐 텍스처 106~114px 띠가 가려진다 → 오른쪽 판을 5px 오른쪽으로.
IBB_X = {('ui_town', 'dl_level_up_town_u.ibb'): [(0x24a4, 62, 67)],
         ('ui_town', 'dl_level_up_hanamise_u.ibb'): [(0x3208, 62, 67)],
         ('ui_town', 'dl_level_up_u.ibb'): [(0x35f8, 62, 67)]}


def gar_files(d):
    import struct
    nt, nf, tto, fto, dto = struct.unpack_from('<HHIII', d, 8)
    out = {}
    for f in range(nf):
        sz, dof, no, fo = struct.unpack_from('<IIII', d, fto + f * 16)
        out[bytes(d[fo:d.index(bytes(1), fo)]).decode().split(chr(92))[-1]] = (dof, sz)
    return out


def patch_ibb(d, gar):
    import struct
    fs = None
    for (g, name), edits in IBB_X.items():
        if g != gar: continue
        fs = fs or gar_files(d)
        o = fs[name][0]
        for off, x0, x1 in edits:
            assert struct.unpack_from('<h', d, o + off)[0] == x0, (name, hex(off))
            struct.pack_into('<h', d, o + off, x1)


def split_move(img, n_left, left_max, right_min):
    import numpy as np
    from PIL import Image
    from scipy import ndimage
    a = np.asarray(img.convert('RGBA'))
    lab, n = ndimage.label(a[..., 3] > 20)                 # 덩어리는 진한 픽셀로 나누고
    idx = ndimage.distance_transform_edt(lab == 0, return_distances=False, return_indices=True)
    lab = np.where(a[..., 3] > 0, lab[idx[0], idx[1]], 0)    # 옅은 픽셀은 가장 가까운 덩어리에 붙인다
    objs = sorted([(s[1].start, s[1].stop, i + 1) for i, s in enumerate(ndimage.find_objects(lab)) if s])
    L, R = objs[:n_left], objs[n_left:]
    dl = min(0, left_max + 1 - max(e for s, e, i in L))
    dr = right_min - min(s for s, e, i in R)
    out = np.zeros_like(a)
    for grp, dx in ((L, dl), (R, dr)):
        for s, e, i in grp:
            ys, xs = np.nonzero(lab == i)
            out[ys, xs + dx] = a[ys, xs]
    return Image.fromarray(out, 'RGBA')


def fit(img, y0, y1):
    from PIL import Image
    b = img.getbbox()
    g = img.crop(b); sc = (y1 - y0) / g.height
    if sc >= 1: return img
    g = g.resize((round(g.width * sc), y1 - y0), Image.LANCZOS)
    out = Image.new('RGBA', img.size, (0, 0, 0, 0))
    out.alpha_composite(g, (round((b[0] + b[2] - g.width) / 2), y0))
    return out

def render_target(d, key, text, letters=None, white=False, gar=None):
    off, ln, w, h, pf, dt = chunks(d)[key]
    orig = ctxb.decode(bytes(d[off:off + ln]), w, h, pf, dt)
    g = gptimg.load('%s_%x.png' % (gar, key)) if gar else None
    if g is not None:                       # GPT 가 그려 준 글자를 원본 자리에 넣는다
        # 텍스처와 같은 크기로 그려 온 것은 이미 자리가 맞으므로 그대로 쓴다.
        # place() 를 태우면 원본 글자 영역에 다시 맞추느라 가로로 늘어난다.
        img = gptimg.quantize(g) if g.size == orig.size else gptimg.place(g, orig)
        if (gar, key) in FIT: img = gptimg.quantize(fit(img, *FIT[(gar, key)]))
        if (gar, key) in SPLIT: img = split_move(img, *SPLIT[(gar, key)])
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
        patch_ibb(d, gar)
        open('%s/%s.gar' % (DST, gar), 'wb').write(bytes(d)); print(gar, '갱신')
    return shots

if __name__ == '__main__':
    main()
