# -*- coding: utf-8 -*-
"""한글화 대상 이미지의 원본을 PNG 로 모은다 → work/원본이미지/

  python tools/dump_images.py

번역완료/ : 이미 한글로 바꾼 이미지의 원본(지역·던전 이름, 타이틀 로고, 팝 글씨, HOME 배너)
미번역/   : 아직 안 바꾼 이미지(data/async 의 던전 이름 한 벌)
"""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))
from PIL import Image
import ctxb, lz11, banner
from build_title_logo import chunks
from build_titles import NAMES
from build_pop import POP, GUARD

SRC = 'extract/jp/romfs/data/Region_JP/Japanese'
ASYNC = 'extract/jp/romfs/data/async'
EXEFS = 'extract/jp/exefs'
OUT = 'work/원본이미지'
DONE, TODO = os.path.join(OUT, '번역완료'), os.path.join(OUT, '미번역')


def save(im, path):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    im.save(path)


def from_chunk(d, key):
    off, ln, w, h, pf, dt = chunks(d)[key]
    return ctxb.decode(bytes(d[off:off + ln]), w, h, pf, dt)


def main():
    n = 0
    # 1) 지역·던전 이름 17종 (본체 + 발광)
    for i, name in enumerate(NAMES):
        d = open('%s/font_dg%02d.gar' % (SRC, i), 'rb').read()
        for k, (off, ln, w, h, pf, dt) in enumerate(sorted(chunks(d).items())[:2] and
                                                    [(v) for _, v in sorted(chunks(d).items())]):
            save(ctxb.decode(d[off:off + ln], w, h, pf, dt),
                 '%s/지역·던전 이름/font_dg%02d_%d %s.png' % (DONE, i, k, name)); n += 1
    # 2) 타이틀 로고
    d = open('%s/ui_title.gar' % SRC, 'rb').read()
    for key, label in [(0x6bb00, '글자판'), (0x8bb80, '로고 합성본')]:
        save(from_chunk(d, key), '%s/타이틀/ui_title_%x %s.png' % (DONE, key, label)); n += 1
    # 3) 팝 글씨
    for gar, items in POP.items():
        d = open('%s/%s.gar' % (SRC, gar), 'rb').read()
        for key, text, _ in items:
            save(from_chunk(d, key), '%s/팝 글씨/%s_%x %s.png' % (DONE, gar, key, text)); n += 1
    d = open('%s/%s.gar' % (SRC, GUARD[0]), 'rb').read()
    save(from_chunk(d, GUARD[1]), '%s/팝 글씨/%s_%x %s.png' % (DONE, GUARD[0], GUARD[1], GUARD[2])); n += 1
    # 4) HOME 배너 제목 그림(일본 칸·한국 칸)
    b = open('%s/banner.bin' % EXEFS, 'rb').read()
    for reg, a, e in banner.sections(b):
        if reg not in ('JPN_JP', 'KOR_KO'): continue
        cg = lz11.decompress(b[a:e])
        for t in banner.textures(cg):
            if t[0] == 'EverOasis_logo_JP':
                save(banner.decode(cg, t), '%s/HOME 배너/banner_%s %s.png' % (DONE, reg, t[0])); n += 1
    print('번역완료 원본 %d장 → %s' % (n, DONE))
    # 5) 미번역: async 던전 이름
    m = 0
    for f in sorted(os.listdir(ASYNC)):
        d = open(os.path.join(ASYNC, f), 'rb').read()
        for off, ln, w, h, pf, dt in [v for _, v in sorted(chunks(d).items())]:
            save(ctxb.decode(d[off:off + ln], w, h, pf, dt), '%s/%s.png' % (TODO, f[:-4])); m += 1
    print('미번역 원본 %d장 → %s' % (m, TODO))


if __name__ == '__main__':
    main()
