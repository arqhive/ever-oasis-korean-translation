# -*- coding: utf-8 -*-
"""batch 파일 전체에서 표기를 일괄 교체하고 해당 묶음을 다시 반영한다.

  python tools/fix_terms.py "파라플라워=파라 플라워" "시드볼=시드 볼"
"""
import sys, os, glob, subprocess
pairs = [a.split('=', 1) for a in sys.argv[1:]]
touched = []
for p in sorted(glob.glob('translation/batches/batch*.py')):
    s = open(p, encoding='utf8').read(); t = s
    for a, b in pairs: t = t.replace(a, b)
    if t != s:
        open(p, 'w', encoding='utf8').write(t)
        name = os.path.basename(p)[5:-3]
        touched.append(name)
        print('수정:', p, sum(s.count(a) for a, _ in pairs), '곳')
# 보정층(원본 번역 위에 덮는 묶음)은 원본을 다시 반영한 뒤 항상 마지막에 다시 덮는다
OVERRIDES = ['_brother', '_punct', '_review1']
order = [n for n in touched if n not in OVERRIDES] + [n for n in OVERRIDES if os.path.exists('translation/batches/batch%s.py' % n)]
for n in order:
    r = subprocess.run([sys.executable, 'tools/apply_batch.py', n], capture_output=True, text=True, encoding='utf8')
    print('  재반영', n, (r.stdout.strip().splitlines() or ['?'])[-1])
