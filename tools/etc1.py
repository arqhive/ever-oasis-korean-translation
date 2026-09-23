# -*- coding: utf-8 -*-
"""3DS ETC1 / ETC1A4 인코더 (etcpak 으로 블록 압축 후 3DS 배치로 변환).

3DS 배치: 8x8 타일(행 우선) 안에 4x4 블록 4개를 (0,0)(4,0)(0,4)(4,4) 순서로.
색 블록 8바이트는 표준 ETC1(빅엔디언)을 뒤집은 순서, ETC1A4 는 앞에 알파 8바이트
(4bpp, 블록 안 열 우선: 픽셀 번호 = x*4+y).
"""
import numpy as np
import etcpak
from PIL import Image

def _std_blocks(rgba):
    h, w = rgba.shape[:2]
    raw = etcpak.compress_etc1_rgb(np.ascontiguousarray(rgba).tobytes(), w, h)
    return np.frombuffer(raw, dtype=np.uint8).reshape(h // 4, w // 4, 8)

def encode(img, alpha=True):
    im = img.convert('RGBA'); w, h = im.size
    a = np.array(im)
    rgb = a.copy()
    blocks = _std_blocks(rgb)
    out = bytearray()
    for ty in range(0, h, 8):
        for tx in range(0, w, 8):
            for sb in range(4):
                sx = tx + (sb & 1) * 4; sy = ty + (sb >> 1) * 4
                if alpha:
                    v = 0
                    for x in range(4):
                        for y in range(4):
                            q = (int(a[sy + y, sx + x, 3]) * 15 + 127) // 255
                            v |= q << ((x * 4 + y) * 4)
                    out += v.to_bytes(8, 'little')
                out += bytes(blocks[sy // 4, sx // 4][::-1])
    return bytes(out)

def encode_rgba4(img):
    """3DS RGBA4444(0x6752/0x8033): 8x8 타일 안 모턴 순서, 픽셀 u16 = R<<12|G<<8|B<<4|A (리틀엔디언)."""
    a = np.array(img.convert('RGBA')).astype(int); h, w = a.shape[:2]
    q = (a * 15 + 127) // 255
    out = bytearray()
    for ty in range(0, h, 8):
        for tx in range(0, w, 8):
            for i in range(64):
                x = (i & 1) | ((i >> 1) & 2) | ((i >> 2) & 4)
                y = ((i >> 1) & 1) | ((i >> 2) & 2) | ((i >> 3) & 4)
                r, g, b, al = q[ty + y, tx + x]
                out += int((r << 12) | (g << 8) | (b << 4) | al).to_bytes(2, 'little')
    return bytes(out)
