# -*- coding: utf-8 -*-
"""HOME 메뉴 배너·아이콘 한글화 → work/exefs/banner.bin, icon.bin (CIA 재빌드용)

  python tools/build_banner.py

- banner(CBMD): 일본(JPN_JP)·한국(KOR_KO) 칸의 CGFX 에만 있는 가타카나 제목·부제 텍스처
  `EverOasis_logo_JP`(256x64 RGBA4)를 한글로 다시 그린다. 영문 로고(`EverOasis_logo_JP_2`)는 모든 지역이 같아 그대로 둔다.
  한국판 본체의 HOME 메뉴는 KOR_KO 칸을 쓴다.
- icon(SMDH): 12개 언어 칸 모두 한국어 제목으로. 게시자는 원본 그대로.
LayeredFS 로는 바뀌지 않으며 CIA 를 다시 만들어야 적용된다.
"""
import sys, os, struct
sys.path.insert(0, os.path.dirname(__file__))
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import lz11, banner, etc1

SRC = 'extract/jp/exefs'
DST = 'work/exefs'
FONT = 'C:/Windows/Fonts/NotoSerifKR-VF.ttf'
TEX = 'EverOasis_logo_JP'
PATCH_REGIONS = ('JPN_JP', 'KOR_KO')
BLUE = (0, 0, 170); GREEN = (0, 119, 0)       # 원본 글자 색
TITLE = '에버 오아시스'
SUB = '～ 정령과 씨앗족의 신기루 ～'
SHORT = '에버 오아시스'
LONG = '에버 오아시스\n정령과 씨앗족의 신기루'
SS = 4


def text_mask(text, weight, height, max_w):
    """글자 높이 height(px)에 맞춘 알파 마스크. max_w 를 넘으면 전체 축소."""
    f = ImageFont.truetype(FONT, 64 * SS); f.set_variation_by_axes([weight])
    bb = f.getbbox(text)
    t = Image.new('L', (bb[2] - bb[0] + 8, bb[3] - bb[1] + 8), 0)
    ImageDraw.Draw(t).text((4 - bb[0], 4 - bb[1]), text, font=f, fill=255)
    t = t.crop(t.getbbox())
    w = int(round(t.width * height / t.height))
    if w > max_w: height = int(round(height * max_w / w)); w = max_w
    return t.resize((w, height), Image.LANCZOS)


def put(img, mask, color, x, y):
    layer = Image.new('RGBA', mask.size, color + (0,)); layer.putalpha(mask)
    img.alpha_composite(layer, (x, y))


def draw_logo(w, h):
    """원본 배치: 제목은 왼쪽 정렬 2~29행, 부제는 35~62행(후리가나 포함) 가로 전체."""
    img = Image.new('RGBA', (w, h), (0, 0, 0, 0))
    t = text_mask(TITLE, 900, 27, 210)
    put(img, t, BLUE, 2, 2 + (27 - t.height) // 2)
    s = text_mask(SUB, 900, 22, 252)
    put(img, s, GREEN, (w - s.width) // 2, 38 + (22 - s.height) // 2)
    return img


def patch_banner(b):
    secs = banner.sections(b)
    cwav = struct.unpack_from('<I', b, 0x84)[0]
    blobs = {}; before = after = None
    for reg, a, e in secs:
        blob = b[a:e]
        if reg in PATCH_REGIONS:
            cgfx = bytearray(lz11.decompress(blob))
            t = next(t for t in banner.textures(cgfx) if t[0] == TEX)
            name, w, h, fmt, data, size = t
            assert (w, h, fmt) == (256, 64, 4), t
            if before is None: before = banner.decode(cgfx, t)
            logo = draw_logo(w, h); enc = etc1.encode_rgba4(logo); assert len(enc) == size
            cgfx[data:data + size] = enc
            after = banner.decode(cgfx, t)
            comp = lz11.compress(bytes(cgfx)); assert lz11.decompress(comp) == bytes(cgfx)
            blob = comp
            print('  %s %s 교체, CGFX %d -> %d 바이트' % (reg, TEX, e - a, len(comp)))
        blobs[a] = blob
    # 원래 순서대로 이어 붙이고 오프셋 표를 다시 쓴다
    out = bytearray(b[:0x88]); new = {}
    for a in sorted(blobs):
        new[a] = len(out); out += blobs[a]
    offs = struct.unpack_from('<17I', b, 0x08)
    struct.pack_into('<17I', out, 0x08, *[new[o] if o else 0 for o in offs])
    out += b'\0' * ((-len(out)) % 0x20)
    struct.pack_into('<I', out, 0x84, len(out))
    out += b[cwav:]
    return bytes(out), before, after


def patch_smdh(icon):
    out = bytearray(icon); assert out[:4] == b'SMDH'
    def put_s(off, text, chars):
        raw = text.encode('utf-16-le'); assert len(raw) < chars * 2, text
        out[off:off + chars * 2] = raw + b'\0' * (chars * 2 - len(raw))
    for i in range(12):
        base = 8 + i * 0x200
        put_s(base, SHORT, 0x40); put_s(base + 0x80, LONG, 0x80)
        if not out[base + 0x180:base + 0x182].strip(b'\0'):
            put_s(base + 0x180, 'Nintendo', 0x40)
    return bytes(out)


def main():
    os.makedirs(DST, exist_ok=True)
    b = open(os.path.join(SRC, 'banner.bin'), 'rb').read()
    nb, before, after = patch_banner(b)
    open(os.path.join(DST, 'banner.bin'), 'wb').write(nb)
    before.save(os.path.join(DST, 'logo_before.png')); after.save(os.path.join(DST, 'logo_after.png'))
    open(os.path.join(DST, 'logo_rgba4.bin'), 'wb').write(etc1.encode_rgba4(draw_logo(256, 64)))
    ic = patch_smdh(open(os.path.join(SRC, 'icon.bin'), 'rb').read())
    open(os.path.join(DST, 'icon.bin'), 'wb').write(ic)
    # 다시 읽어 검증
    for reg, a, e in banner.sections(nb):
        cg = lz11.decompress(nb[a:e]); assert banner.textures(cg)
    print('banner.bin %d -> %d 바이트, icon.bin 제목 %r → %s' % (len(b), len(nb), LONG, DST))


if __name__ == '__main__':
    main()
