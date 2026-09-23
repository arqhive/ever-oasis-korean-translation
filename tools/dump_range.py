# -*- coding: utf-8 -*-
"""번역할 원문을 구간별로 뽑는다(후리가나 제거, 태그 유지, 영어판 참고 포함).

  python tools/dump_range.py 70000 70999           # 미번역만
  python tools/dump_range.py 70000 70999 --all     # 번역된 것도
출력: ID<TAB>일본어(태그)<TAB>영어판
"""
import sys, os, json
sys.path.insert(0, os.path.dirname(__file__))
from text_io import strip_ruby, OUT
lo, hi = int(sys.argv[1]), int(sys.argv[2]); allr = '--all' in sys.argv
sys.stdout.reconfigure(encoding='utf-8')
for r in json.load(open(OUT, encoding='utf8')):
    if lo <= r['id'] <= hi and r['jp_plain'].strip() and (allr or not r['ko']):
        print('%d\t%s\t%s' % (r['id'], strip_ruby(r['jp']), r['en_plain'].replace('\n', ' / ')))
