# -*- coding: utf-8 -*-
"""타이틀 로고 글자(ui_title.gar 의 0x6bb00 글자판, 0x8bb80 로고 합성본)를 한글로 교체."""
import sys, os, struct
sys.path.insert(0, os.path.dirname(__file__))
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import ctxb, etc1, gptimg

SRC = 'extract/jp/romfs/data/Region_JP/Japanese/ui_title.gar'
DST = 'work/romfs/data/Region_JP/Japanese/ui_title.gar'
FONT = 'C:/Windows/Fonts/NotoSerifKR-VF.ttf'
BLUE = (1, 1, 168); GREEN = (0, 112, 13)
KANA = '에버 오아시스'
SUB = '～ 정령과 씨앗족의 신기루 ～'
SS = 4

def chunks(d):
    out = {}; i = 0
    while True:
        i = d.find(b'ctxb', i)
        if i < 0: return out
        size, cnt, _, coff, toff = struct.unpack_from('<5I', d, i + 4)
        c = i + coff
        if d[c:c + 4] == b'tex ':
            ln, a, b, w, h, pf, dt, off = struct.unpack_from('<I6HI', d, c + 12)
            out[i] = (i + toff + off, ln, w, h, pf, dt)
        i += 4

def draw_text(img, text, color, box, weight=700, height=None):
    """box=(x0,y0,x1,y1) 안에 가운데 맞춤. 높이는 box 높이, 넓으면 전체 축소."""
    x0, y0, x1, y1 = box; bw, bh = x1 - x0, y1 - y0
    f = ImageFont.truetype(FONT, 64 * SS); f.set_variation_by_axes([weight])
    bb = f.getbbox(text)
    t = Image.new('L', (bb[2] - bb[0] + 8, bb[3] - bb[1] + 8), 0)
    ImageDraw.Draw(t).text((4 - bb[0], 4 - bb[1]), text, font=f, fill=255)
    t = t.crop(t.getbbox())
    h = height or bh; w = int(round(t.width * h / t.height))
    if w > bw: h = int(round(h * bw / w)); w = bw
    t = t.resize((w, h), Image.LANCZOS)
    layer = Image.new('RGBA', (w, h), color + (0,)); layer.putalpha(t)
    img.alpha_composite(layer, (x0 + (bw - w) // 2, y0 + (bh - h) // 2))

def main():
    d = bytearray(open(SRC, 'rb').read()); ch = chunks(d)
    # 1) 글자판 0x6bb00: 전부 지우고 다시 쓴다
    off, ln, w, h, pf, dt = ch[0x6bb00]
    g = gptimg.load('타이틀/ui_title_6bb00.png')
    if g is not None:
        img = gptimg.place(g, ctxb.decode(bytes(d[off:off + ln]), w, h, pf, dt))
    else:
        img = Image.new('RGBA', (w, h), (0, 0, 0, 0))
        draw_text(img, KANA, BLUE, (100, 72, 212, 86), weight=600)
        draw_text(img, SUB, GREEN, (92, 134, 324, 152), weight=700)
    enc = etc1.encode(img, alpha=True); assert len(enc) == ln; d[off:off + ln] = enc
    # 2) 로고 합성본 0x8bb80: 가타카나 칸과 부제 띠만 지우고 다시 쓴다
    off, ln, w, h, pf, dt = ch[0x8bb80]
    img = ctxb.decode(bytes(d[off:off + ln]), w, h, pf, dt)
    g = gptimg.load('타이틀/ui_title_8bb80.png')
    if g is not None:                      # GPT 가 영문 로고까지 포함해 그려 준 합성본
        img = gptimg.place(g, img)      # 원본 로고가 있던 자리·크기에 맞춘다
    else:
        a = np.array(img); a[13:28, 76:173] = 0; a[75:, :] = 0
        img = Image.fromarray(a, 'RGBA')
        draw_text(img, KANA, BLUE, (78, 14, 172, 26), weight=600)
        draw_text(img, SUB, GREEN, (60, 82, 300, 100), weight=700)
    enc = etc1.encode(img, alpha=True); assert len(enc) == ln; d[off:off + ln] = enc
    os.makedirs(os.path.dirname(DST), exist_ok=True)
    open(DST, 'wb').write(bytes(d)); print('ui_title.gar 갱신')

if __name__ == '__main__':
    main()
