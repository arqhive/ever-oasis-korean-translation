# -*- coding: utf-8 -*-
"""번역 묶음(translation/batches/batchN.py 의 KO 사전)을 검증해 messages.json 에 넣고 대조표를 만든다.

  python tools/apply_batch.py 2          # batch2 검증 + 반영 + work/대조표_2차.md
  python tools/apply_batch.py 2 --check  # 검증만

검사: 없는 ID, 원문과 제어코드(개수까지)·NUL 개수 불일치, U+FFFF 잔존,
      줄 폭 400px 초과(대사창 한도), 이미 다른 묶음에서 번역한 ID 덮어쓰기.
"""
import sys, os, json, re, collections, importlib.util
sys.path.insert(0, os.path.dirname(__file__))
from text_io import strip_ruby, codes, plain, RUBY, OUT
from width import width

LIMIT = 400   # 대사창 한도(원문 최대 399px)
WARN = 360    # 원문 99.9%가 331px 이하
NAME = {'0d': '[주인공]', '0e': '[이름]', '0f': '[가게]', '10': '[아이템]', '11': '[숫자]',
        '12': '[값]', '13': '[대상]', '08': '[버튼]'}
TAG = re.compile(r'\{([0-9a-f]{2})(?::([0-9a-f]{8}))?\}')


def show(t):
    t = RUBY.sub(lambda m: m.group(2), t)
    t = t.replace('{01}', ' ⏎ ').replace('{02}', ' ⏎⏎ ').replace('{z}', '')
    t = TAG.sub(lambda m: NAME.get(m.group(1), ''), t)
    return t.replace('|', '｜').strip()


def maxw(t):
    return max([width(l) for l in plain(strip_ruby(t)).split('\n')] + [0])


def load_batch(n):
    p = 'translation/batches/batch%s.py' % n
    spec = importlib.util.spec_from_file_location('batch%s' % n, p)
    m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
    return m.KO


def main():
    n = sys.argv[1]; only_check = '--check' in sys.argv
    KO = load_batch(n)
    rows = json.load(open(OUT, encoding='utf8'))
    by = {r['id']: r for r in rows}
    err = collections.defaultdict(list); wide = []
    for i, ko in KO.items():
        if i not in by: err['없는 ID'].append(i); continue
        jp = strip_ruby(by[i]['jp'])
        cj = collections.Counter(c for c in codes(jp) if c not in ('{1a}', '{1b}'))
        ck = collections.Counter(codes(ko))
        # 성별 분기 {15}A{z}{16}B{z} 는 원문에 없던 자리에도 추가할 수 있다(형/오빠 등)
        extra = ck['{15}'] - cj['{15}']
        if extra > 0 and ck['{16}'] - cj['{16}'] == extra:
            ck['{15}'] -= extra; ck['{16}'] -= extra
        else:
            extra = 0
        if cj != ck: err['태그 불일치'].append(i)
        if jp.count('{z}') + 2 * extra != ko.count('{z}'): err['NUL 개수'].append(i)
        if '￿' in ko: err['U+FFFF'].append(i)
        if by[i]['ko'] and by[i]['ko'] != ko and not only_check:
            err['다른 번역 덮어씀(경고)'].append(i)
        w = maxw(ko)
        if w > LIMIT: err['줄 폭 %dpx 초과' % LIMIT].append((i, w))
        elif w > WARN: wide.append((i, w))
    print('묶음 %s: %d개' % (n, len(KO)))
    fatal = False
    for k, v in err.items():
        print('  %s %d건: %s' % (k, len(v), v[:15]))
        if '경고' not in k: fatal = True
    if wide: print('  (경고) %dpx 초과 %d건: %s' % (WARN, len(wide), wide[:15]))
    if fatal:
        print('!! 오류가 있어 반영하지 않았다'); sys.exit(1)
    if only_check: print('검사 통과'); return
    for i, ko in KO.items(): by[i]['ko'] = ko
    json.dump(rows, open(OUT, 'w', encoding='utf8'), ensure_ascii=False, indent=1)
    out = ['# %s차 대조표 (%d개)' % (n, len(KO)), '',
           '`⏎` 줄바꿈, 대괄호는 게임이 값을 끼워 넣는 자리. `폭` 은 가장 긴 줄의 픽셀 폭(원문→번역).', '',
           '| ID | 일본어 원문 | 번역 | 폭 | 영어판 |', '|---|---|---|---|---|']
    for i in sorted(KO):
        r = by[i]; wj = maxw(r['jp']); wk = maxw(KO[i])
        out.append('| %d | %s | **%s** | %d→%s | %s |' % (
            i, show(r['jp']), show(KO[i]), wj, ('**%d**' % wk) if wk > 330 else wk, show(r['en'])[:60]))
    os.makedirs('work/대조표', exist_ok=True)
    open('work/대조표/%s차.md' % n, 'w', encoding='utf8').write('\n'.join(out))
    done = sum(1 for r in rows if r['ko'])
    print('반영 완료. 전체 번역 %d / %d개 → work/대조표/%s차.md' % (done, len(rows), n))


if __name__ == '__main__':
    main()
