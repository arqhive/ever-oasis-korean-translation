# -*- coding: utf-8 -*-
"""번역문을 게임 글꼴로 그려 종류별 미리보기 시트를 만든다 → work/텍스트미리보기.png

  python tools/preview_text.py            # 종류별 대표 몇 개
  python tools/preview_text.py 70000 70010   # ID 구간을 그대로

빌드된 폰트(work/romfs/.../main.gzf)의 글리프를 그대로 쓰므로 실제 화면과 글자 모양·너비가 같다.
제어 코드는 줄바꿈·페이지·색만 반영하고, 이름·아이템처럼 게임이 끼워 넣는 자리는 [  ] 로 보인다.
"""
import sys, os, re, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import gzf

FONT = 'work/romfs/data/Region_JP/main.gzf'
MSG = 'work/text/messages.json'
OUT = 'work/텍스트미리보기.png'
BG, INK = (247, 238, 214), (60, 40, 25)
# {19:xxxxxxxx} 색. 2·4·5 는 대사 94022(하늘색·노랑·분홍을 그 색으로 쓴 문장)에서 확인했고
# 나머지는 쓰이는 자리로 미루어 본 값이라 실제 화면 색과 다를 수 있다.
COLORS = {2: (205, 130, 20), 4: (60, 120, 190), 5: (200, 90, 150),    # 확인
          1: (200, 60, 50), 3: (90, 110, 60), 0: (120, 95, 60),       # 추정
          7: (150, 90, 40), 13: (70, 95, 165), 14: (150, 70, 120)}
TAG = re.compile(r'\{([0-9a-f]{2})(?::([0-9a-f]{8}))?\}')
SLOT = {'0d': '[주인공]', '0e': '[동료]', '0f': '[가게]', '10': '[아이템]',
        '11': '[숫자]', '12': '[값]', '13': '[대상]', '08': '[버튼]', '14': '[날짜]'}


def load_font():
    hdr, ents, atlas = gzf.load(FONT)
    g = {}
    for i, (code, adv, x, col, row) in enumerate(ents):
        cx, cy = gzf.cell(i)
        g[code] = (atlas.crop((cx, cy, cx + gzf.BOX, cy + gzf.BOX)), adv, x)
    return g


def tokens(t):
    """(글자, 색) 목록과 줄바꿈·페이지 구분을 담은 줄 목록으로 바꾼다."""
    t = re.sub(r'\{1a\}.*?\{z\}(.*?)\{1b\}', r'\1', t)        # 후리가나는 본문만
    t = re.sub(r'\{15\}([^{]*)\{z\}\{16\}[^{]*\{z\}', r'\1', t)  # 성별 분기는 남자 쪽
    pages = [[]]; line = []; color = INK
    i = 0
    while i < len(t):
        m = TAG.match(t, i)
        if not m:
            if t[i] != '\ufeff': line.append((t[i], color))
            i += 1; continue
        code, arg = m.group(1), m.group(2)
        i = m.end()
        if code == '01': pages[-1].append(line); line = []
        elif code == '02':                                  # 페이지 넘김
            pages[-1].append(line); line = []; pages.append([])
        elif code == '19':
            v = int(arg, 16) if arg else 0xffffffff
            color = INK if v == 0xffffffff else COLORS.get(v, (120, 80, 160))
        elif code in SLOT:
            for ch in SLOT[code]: line.append((ch, (130, 120, 110)))
        elif code == 'z':
            pass
    pages[-1].append(line)
    return [[l for l in p] for p in pages if any(p)]


MARGIN = 8          # 글리프를 왼쪽으로 당겨 그리므로 왼쪽에 여유를 둔다


def draw_line(chars, font, y, img):
    """글리프의 x 는 '왼쪽으로 당겨 그리는 보정값'이다.
    예: 쉼표는 advance 5 인데 칸 안 잉크가 6~12 에 있고 x 가 7 이라 -1~5 에 놓인다."""
    x = MARGIN
    for ch, col in chars:
        g = font.get(ord(ch))
        if g is None:
            x += 16; continue
        gl, adv, gx = g
        layer = Image.new('RGBA', gl.size, col + (0,))
        layer.putalpha(gl)
        img.alpha_composite(layer, (x - gx, y))
        x += adv
    return x


def render(text, font, width=460):
    """페이지({02})마다 사이를 띄워 화면이 넘어가는 자리를 보이게 한다."""
    pages = tokens(text)
    rows = []
    for n, p in enumerate(pages):
        if n: rows.append(None)                 # 페이지 사이 빈 줄
        rows += p
    h = max(1, len(rows)) * 22 + 6
    img = Image.new('RGBA', (width, h), (0, 0, 0, 0))
    w = 0
    for n, l in enumerate(rows):
        if l is None: continue
        w = max(w, draw_line(l, font, n * 22 + 2, img))
    out = img.crop((MARGIN, 0, max(w + 4, 60), h))
    if len(pages) > 1:                          # 페이지 경계에 옅은 선
        d = ImageDraw.Draw(out); y = 0
        for n, p in enumerate(pages):
            if n:
                d.line([(0, y * 22 + 11), (out.width, y * 22 + 11)], fill=(190, 175, 150, 255))
                y += 1
            y += len(p)
    return out


def kind(i):
    if i < 1000: return '시스템'
    if i < 3000: return '이름'
    if i < 5000: return '메뉴'
    if i < 6000: return '아이템 이름'
    if i < 7000: return '아이템 설명'
    if i < 10000: return '특기'
    if 60000 <= i < 66000: return '시스템'
    if 80000 <= i < 81000: return '소문·인물 소개'
    if 83000 <= i < 84000: return '도움말'
    if 84000 <= i < 85000: return '할 일'
    if 85000 <= i < 86000: return '동료 기록'
    if i >= 99000: return '크레디트'
    return '대사'


SAMPLES = {
    '시스템': [305, 816, 988], '이름': [1171, 1013, 1500], '메뉴': [4028, 4313, 4501],
    '아이템 이름': [5083, 5339, 5668], '아이템 설명': [6555, 6621, 6799],
    '특기': [9003, 9126, 9270], '대사': [70016, 71869, 73569, 94185],
    '소문·인물 소개': [80235, 80309], '도움말': [83013, 83166, 83181],
    '할 일': [84154, 84223], '동료 기록': [85017, 85116], '크레디트': [99001, 99010],
}


def main():
    os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    font = load_font()
    rows = json.load(open(MSG, encoding='utf8'))
    by = {r['id']: r for r in rows if r['ko']}
    if len(sys.argv) > 2:
        lo, hi = int(sys.argv[1]), int(sys.argv[2])
        groups = [('ID %d~%d' % (lo, hi), [i for i in sorted(by) if lo <= i <= hi][:40])]
    else:
        cnt = {}
        for i in by: cnt[kind(i)] = cnt.get(kind(i), 0) + 1
        groups = [('%s  (%d개)' % (k, cnt.get(k, 0)), [i for i in v if i in by])
                  for k, v in SAMPLES.items()]
    f1 = ImageFont.truetype('C:/Windows/Fonts/malgunbd.ttf', 19)
    f2 = ImageFont.truetype('C:/Windows/Fonts/malgun.ttf', 14)
    blocks = []
    for title, ids in groups:
        items = []
        for i in ids:
            im = render(by[i]['ko'], font)
            items.append((i, im))
        blocks.append((title, items))
    PAD, W = 18, 980
    H = sum(34 + sum(im.height + 22 for _, im in items) for _, items in blocks) + PAD * 2 + 30
    s = Image.new('RGB', (W, H), (250, 250, 252))
    d = ImageDraw.Draw(s); y = PAD
    d.text((PAD, y), '게임 글꼴로 그린 미리보기 · 가로선 = 화면이 넘어가는 자리 · [  ] = 게임이 끼워 넣는 값',
           font=f2, fill=(120, 120, 130)); y += 24
    for title, items in blocks:
        d.text((PAD, y), title, font=f1, fill=(150, 40, 40)); y += 30
        for i, im in items:
            d.text((PAD, y), str(i), font=f2, fill=(150, 150, 150))
            box = Image.new('RGB', (im.width + 12, im.height + 6), BG)
            box.paste(im, (6, 3), im)
            s.paste(box, (PAD + 54, y)); y += box.height + 14
        y += 6
    s.save(OUT)
    print('%s  %dx%d' % (OUT, s.width, s.height))


if __name__ == '__main__':
    main()
