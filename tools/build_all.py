# -*- coding: utf-8 -*-
"""전체 빌드: 폰트(배포용) + 텍스트 + 이미지 → work/romfs, 그리고 Azahar 모드 폴더·Luma LayeredFS 폴더로 복사.

  python tools/build_all.py            # 빌드 + Azahar 모드 반영
  python tools/build_all.py --dev      # 일본어 글리프를 남기는 개발용 폰트(번역 안 된 곳 확인용)
"""
import sys, os, json, shutil
sys.path.insert(0, os.path.dirname(__file__))
import build_font, text_io, build_titles, build_title_logo, build_pop

TID = '0004000000164A00'
FILES = ['data/Region_JP/main.gzf', 'data/Region_JP/Japanese/main.gmsg'] + \
        ['data/Region_JP/Japanese/font_dg%02d.gar' % i for i in range(17)] + \
        ['data/Region_JP/Japanese/%s.gar' % g for g in ('ui_title', 'ui_town', 'ui_field', 'ui_keep')] + \
        ['data/async/font_dangname_%02d%s.gar' % (i, x) for i in range(17) for x in ('', 'ext')]

def main():
    dev = '--dev' in sys.argv
    rows = json.load(open(text_io.OUT, encoding='utf8'))
    ko = ''.join(r['ko'] for r in rows if r['ko'])
    build_font.build('dev' if dev else 'release', extra_text=ko)
    text_io.apply_(); text_io.check(); text_io.save()
    build_titles.main(); build_title_logo.main(); build_pop.main()
    mods = os.path.join(os.environ['APPDATA'], 'Azahar', 'load', 'mods', TID, 'romfs')
    luma = os.path.join('release', 'luma', 'titles', TID, 'romfs')
    for base in (mods, luma):
        for f in FILES:
            dst = os.path.join(base, f); os.makedirs(os.path.dirname(dst), exist_ok=True)
            shutil.copyfile(os.path.join('work', 'romfs', f), dst)
    done = sum(1 for r in rows if r['ko'])
    print('빌드 완료: 번역 %d / %d개, 파일 %d개 → Azahar 모드, %s' % (done, len(rows), len(FILES), luma))

if __name__ == '__main__':
    main()
