# -*- coding: utf-8 -*-
"""화자 추정용 문맥 추출: ID<TAB>[확정 화자 또는 ?]<TAB>초상코드<TAB>일본어<TAB>한국어 번역
  python tools/dump_speaker_ctx.py 70000 70999
확정 화자는 스크립트에서 뽑은 것(정확). '?' 가 추정해야 할 줄."""
import sys, os, json, re
sys.path.insert(0, os.path.dirname(__file__))
from text_io import plain, strip_ruby, OUT
lo, hi = int(sys.argv[1]), int(sys.argv[2])
sys.stdout.reconfigure(encoding='utf-8')
exact = {int(k): v for k, v in json.load(open('translation/speakers/exact.json', encoding='utf8')).items()}
for r in json.load(open(OUT, encoding='utf8')):
    if lo <= r['id'] <= hi and r['jp_plain'].strip():
        m = re.search(r'\{09:([0-9a-f]{8})\}', r['jp'])
        j = plain(strip_ruby(r['jp'])).replace('\n', ' / ')
        k = plain(r['ko']).replace('\n', ' / ')
        print('%d\t%s\t%s\t%s\t%s' % (r['id'], exact.get(r['id'], '?'), m.group(1) if m else '', j, k))
