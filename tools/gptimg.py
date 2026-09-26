# -*- coding: utf-8 -*-
"""GPT 가 그려 준 글자 이미지를 게임 텍스처에 맞춰 넣는다.

`work/GPT결과/` 에 원본과 같은 이름의 PNG 가 있으면 빌드 도구들이 그것을 쓴다.
없으면 기존 폰트 렌더링으로 돌아간다(도구마다 처리).

  - place() : GPT 이미지의 글자 부분을 원본 글자와 같은 크기·자리에 놓는다.
  - glow()  : 본체에서 밝은 곳을 뽑아 발광(겹쳐 그리는 하이라이트) 레이어를 만든다.
"""
import os
import numpy as np
from PIL import Image

DIR = 'work/GPT결과'


def path(name):
    """GPT결과 안의 파일 경로(없으면 None). name 은 하위 폴더를 포함할 수 있다."""
    p = os.path.join(DIR, name)
    return p if os.path.exists(p) else None


def load(name):
    p = path(name)
    return Image.open(p).convert('RGBA') if p else None


def inkbox(im, thr=16):
    """글자가 실제로 그려진 영역(알파 > thr)."""
    a = np.array(im.convert('RGBA'))[..., 3]
    ys, xs = np.nonzero(a > thr)
    if not len(xs): return None
    return int(xs.min()), int(ys.min()), int(xs.max()) + 1, int(ys.max()) + 1


def quantize(im, levels=15):
    """알파를 게임 형식(4비트 = 16단계)에 맞춰 반올림."""
    a = np.array(im.convert('RGBA'))
    a[..., 3] = (np.round(a[..., 3] / 255 * levels) / levels * 255).astype(np.uint8)
    return Image.fromarray(a)


def place(gpt, orig, size=None, box=None):
    """gpt 의 글자를 orig 의 글자와 같은 크기·자리에 놓는다.

    orig  : 원본 텍스처(PIL) — 글자 위치를 여기서 잰다.
    size  : 결과 크기(기본 orig 크기)
    box   : 원본 글자 영역을 직접 줄 때 (x0, y0, x1, y1)
    """
    size = size or orig.size
    ob = box or inkbox(orig)
    gb = inkbox(gpt)
    if ob is None or gb is None:
        return quantize(gpt.resize(size, Image.LANCZOS))
    ox0, oy0, ox1, oy1 = ob
    crop = gpt.crop(gb)
    tw, th = ox1 - ox0, oy1 - oy0
    sc = min(tw / crop.width, th / crop.height)
    nw, nh = max(1, round(crop.width * sc)), max(1, round(crop.height * sc))
    crop = crop.resize((nw, nh), Image.LANCZOS)
    out = Image.new('RGBA', size, (0, 0, 0, 0))
    out.paste(crop, (ox0 + (tw - nw) // 2, oy0 + (th - nh) // 2))
    return quantize(out)


def glow(body, ref=None, lo=120, span=100):
    """본체에서 밝은 부분을 뽑아 발광 레이어를 만든다.

    원본은 '본체(글자·테두리) + 발광(밝은 하이라이트)' 두 장을 겹쳐 그린다.
    ref 를 주면 그 색을 쓰고, 없으면 원본 지역 이름과 같은 노란빛을 쓴다.
    """
    a = np.array(body.convert('RGBA')).astype(float)
    al = a[..., 3]
    lum = a[..., 0] * 0.4 + a[..., 1] * 0.5 + a[..., 2] * 0.1
    m = np.clip((lum - lo) / span, 0, 1) * (al / 255)
    if ref is not None:
        r = np.array(ref.convert('RGBA')).astype(float)
        sel = r[..., 3] > 128
        col = r[sel][:, :3].mean(0) if sel.any() else np.array([255., 247., 90.])
    else:
        col = np.array([255., 247., 90.])
    out = np.zeros_like(a)
    out[..., 0], out[..., 1], out[..., 2] = col
    out[..., 3] = m * 255
    return quantize(Image.fromarray(out.clip(0, 255).astype(np.uint8)))
