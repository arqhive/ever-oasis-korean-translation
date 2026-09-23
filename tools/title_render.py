# -*- coding: utf-8 -*-
"""던전·지역 이름 이미지(font_dgXX.gar, 256x32 ETC1A4 두 장)를 한글로 다시 그린다.

아래층(0): 금색 그라데이션 글자 + 갈색 테두리 + 반투명 검은 그림자
위층(1): 연노랑 그라데이션 하이라이트 글자
색은 원본 텍스처에서 행별로 측정해 그대로 쓴다.
"""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import ctxb

SS = 4

def measure(gar_path):
    d = open(gar_path, 'rb').read()
    L0, L1 = [np.array(ctxb.decode(data, w, h, pf, dt)).astype(float)
              for off, k, w, h, pf, dt, data in ctxb.iter_ctxb(d)]
    m1 = L1[..., 3] > 200; m0 = L0[..., 3] > 200
    def rowcol(img, mask):
        out = np.full((32, 3), np.nan)
        for y in range(32):
            if mask[y].sum() >= 3: out[y] = img[y][mask[y]][:, :3].mean(0)
        idx = np.where(~np.isnan(out[:, 0]))[0]
        for c in range(3): out[:, c] = np.interp(np.arange(32), idx, out[idx, c])
        return out
    return dict(g1=rowcol(L1, m1), g0=rowcol(L0, m1 & m0), edge=rowcol(L0, m0 & ~m1))

def text_mask(text, font_path, px, width=256, height=32, top=4, maxw=244, weight=None):
    f = ImageFont.truetype(font_path, px * SS)
    if weight:
        try: f.set_variation_by_axes([weight])
        except Exception: pass
    bb = f.getbbox(text)
    tw, th = bb[2] - bb[0], bb[3] - bb[1]
    im = Image.new('L', (tw + 8 * SS, th + 8 * SS), 0)
    ImageDraw.Draw(im).text((4 * SS - bb[0], 4 * SS - bb[1]), text, font=f, fill=255)
    im = im.crop(im.getbbox())
    tw_px = im.width / SS; th_px = im.height / SS
    sx = min(1.0, maxw / tw_px)                       # 너무 길면 가로만 줄인다
    tgt_h = 22
    sy = tgt_h / th_px
    nw = max(1, int(round(tw_px * sx * (sy if sx == 1.0 else sy))))
    nw = min(nw, maxw)
    small = im.resize((nw, tgt_h), Image.LANCZOS)
    canvas = Image.new('L', (width, height), 0)
    canvas.paste(small, ((width - nw) // 2, top))
    return np.array(canvas).astype(float) / 255.0

RINGS = [((112, 94, 28), 1.00), ((30, 18, 1), 0.85), ((0, 0, 0), 0.38), ((0, 0, 0), 0.16)]  # 원본 실측

def render(text, font_path, colors, px=22, weight=None):
    m = text_mask(text, font_path, px, weight=weight)
    g1, g0 = colors['g1'], colors['g0']
    H, W = m.shape
    L1 = np.zeros((H, W, 4)); L1[..., :3] = g1[:, None, :]; L1[..., 3] = m * 255
    # 아래층: 글자 둘레를 1px씩 넓혀 가며 실측 색·알파의 링을 두른다(바깥부터 칠함)
    hi = Image.fromarray((m * 255).astype(np.uint8)).resize((W * SS, H * SS), Image.LANCZOS)
    layers = []; prev = hi
    for col, a in RINGS:
        cur = prev.filter(ImageFilter.MaxFilter(2 * SS + 1))
        layers.append((col, a, cur)); prev = cur
    L0 = np.zeros((H, W, 4))
    def over(dst, rgb, a):
        out_a = a + dst[..., 3] * (1 - a)
        rgb_o = (rgb * a[..., None] + dst[..., :3] * dst[..., 3:4] * (1 - a[..., None])) / np.maximum(out_a[..., None], 1e-6)
        dst[..., :3] = rgb_o; dst[..., 3] = out_a
    for col, a, cur in reversed(layers):
        cov = np.array(cur.resize((W, H), Image.BOX)).astype(float) / 255 * a
        over(L0, np.broadcast_to(np.array(col, float), (H, W, 3)), cov)
    over(L0, np.broadcast_to(g0[:, None, :], (H, W, 3)), m)
    L0[..., 3] *= 255
    to_img = lambda a: Image.fromarray(np.clip(a, 0, 255).astype(np.uint8), 'RGBA')
    return to_img(L0), to_img(L1)
