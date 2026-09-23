# -*- coding: utf-8 -*-
"""페이지 끝 문장에 빠진 마침표(또는 이어지는 문장의 쉼표)를 넣는 batch 를 만든다."""
import sys, os, json, re
sys.path.insert(0, os.path.dirname(__file__))
from text_io import OUT

CODE = re.compile(r'\{[0-9a-f]{2}(?::[0-9a-f]{8})?\}|\{z\}')
TERM = re.compile(r'\{03\}|\{02\}|\{00\}')

def page_ends(t):
    """(페이지 번호, 마지막 보이는 글자 끝 위치) — 보이는 글자가 있는 페이지만"""
    out = []; start = 0
    for m in TERM.finditer(t):
        seg = t[start:m.start()]
        # 보이는 글자 위치 찾기(제어코드 제외, 성별 분기 {15}..{16}.. 는 둘 다 글자로 친다)
        vis = [i for i in range(len(seg))]
        spans = [(x.start(), x.end()) for x in CODE.finditer(seg)]
        mask = [True] * len(seg)
        for a, b in spans:
            for i in range(a, b): mask[i] = False
        idx = [i for i in range(len(seg)) if mask[i] and not seg[i].isspace()]
        if idx: out.append(start + idx[-1] + 1)
        start = m.end()
    return out

def main():
    cand = json.load(open('work/text/_nopunct.json', encoding='utf8'))
    rows = {r['id']: r for r in json.load(open(OUT, encoding='utf8'))}
    EXCL = set(range(1000, 3000)) | set(range(5000, 6000)) | set(range(84000, 86000)) | {
        4246, 4254, 4298, 4356, 4359, 4360, 4361, 4362, 6827, 94097, 94236, 94241, 94147, 94148,
        70908, 70922, 70933, 70953, 70955, 70971}
    COMMA = {70065, 70149, 70567, 70594, 79081, 82512, 73291}
    import importlib.util
    # 대상 메시지별로, 부호 없는 페이지 끝 위치에 부호 삽입
    targets = sorted({c[0] for c in cand if c[0] not in EXCL})
    KO = {}
    for i in targets:
        t = rows[i]['ko']; ends = page_ends(t); new = t
        for pos in sorted(ends, reverse=True):
            ch = new[pos - 1]
            if re.match(r'[가-힣]', ch):
                # 문장형 끝(명사 끝은 건드리지 않도록 후보 문장만)
                line = re.sub(r'\{[^}]*\}', '\n', new[:pos]).split('\n')[-1].strip()
                if any(line.endswith(c[1]) or c[1].endswith(line) for c in cand if c[0] == i):
                    new = new[:pos] + (',' if i in COMMA else '.') + new[pos:]
        if new != t: KO[i] = new
    lines = ['# -*- coding: utf-8 -*-', '"""페이지 끝 문장 부호 보충(마침표, 이어지는 문장은 쉼표)."""', '', 'KO = {']
    for i in sorted(KO): lines.append('%d: %r,' % (i, KO[i]))
    lines.append('}')
    open('translation/batches/batch_punct.py', 'w', encoding='utf8').write('\n'.join(lines) + '\n')
    for i in sorted(KO):
        a = re.sub(r'\{[^}]*\}', ' ', rows[i]['ko']).split(); b = re.sub(r'\{[^}]*\}', ' ', KO[i]).split()
        diff = [(x, y) for x, y in zip(a, b) if x != y]
        print('%6d  %s' % (i, '  '.join('%s→%s' % d for d in diff)))
    print('총', len(KO), '개')

if __name__ == '__main__':
    main()
