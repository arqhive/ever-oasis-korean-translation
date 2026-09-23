# -*- coding: utf-8 -*-
"""번역 일관성·문체 점검 (전 구간).

  python tools/lint.py            # 요약
  python tools/lint.py --detail   # 항목별 예시까지

- 고유명사: 원문에 용어사전의 고유명사가 있는데 번역에 사전 표기가 없는 메시지
- 배포 폰트에 없는 글자
- 문장 끝 부호 없음: 원문 페이지 끝이 문장형(히라가나·。！？…)인데 번역 페이지 끝이
  종결어미로 끝나고 부호가 없는 곳. 이름·아이템 목록, 할 일·기록 제목, 선택지는 제외
- 그녀/그들, 물결표 뒤 부호, 줄임표+마침표, 대사 속 전각 공백, 직역투
"""
import sys, os, json, re, collections
sys.path.insert(0, os.path.dirname(__file__))
from text_io import plain, strip_ruby, OUT

TAG = re.compile(r'\{[0-9a-f]{2}(?::[0-9a-f]{8})?\}')
BRANCH = re.compile(r'\{15\}([^{]*)\{z\}\{16\}([^{]*)\{z\}')
# 이름·아이템 목록, 할 일·기록 제목, 크레디트, 선택지·명사 메뉴
NOPUNCT_EXCL = (set(range(1000, 3000)) | set(range(5000, 6000)) | set(range(84000, 86000)) |
                set(range(99000, 100000)) |
                {4246, 4254, 4298, 4356, 4359, 4360, 4361, 4362, 6827, 94147, 94148})
KO_END = re.compile(r'(니다|세요|요|죠|까|다|해|줘|자|지|야|어|아|네|군|구나|구먼|거든|는데|걸|렴|래|게|니|라|오|소|구려|노라|리라|거라)$')
JP_SENT = re.compile(r'[ぁ-ん]$|[。！？…]$')


def body(t):
    return plain(strip_ruby(t))


def page_lasts(t):
    """페이지({03}·{02}·{00} 로 끝나는 덩어리)마다 마지막 줄 텍스트. 성별 분기는 앞쪽만 본다."""
    t = BRANCH.sub(lambda m: m.group(1), t).replace('{z}', '')
    out = []
    for seg in re.split(r'\{03\}|\{02\}|\{00\}', t):
        ls = [l.strip() for l in TAG.sub('\n', seg.replace('{01}', '\n')).split('\n') if l.strip()]
        if ls: out.append(ls[-1])
    return out


def main():
    detail = '--detail' in sys.argv
    rows = [r for r in json.load(open(OUT, encoding='utf8')) if r['ko']]
    term = json.load(open('translation/terms.json', encoding='utf8'))
    names = {j: k for j, k in term.items()
             if (re.fullmatch(r'[ァ-ヴー・]{3,}', j) or
                 re.fullmatch(r'.*(族|砂漠|樹海|丘陵|大峡谷|岩山|遺跡|墓場|迷宮|聖域|洞穴|洞くつ|トンネル)', j))
             and len(k) >= 2}
    miss = collections.defaultdict(list)
    for r in rows:
        j = body(r['jp']); k = body(r['ko'])
        for jt, kt in names.items():
            if jt in j and kt not in k:
                if any(jt != o and jt in o and o in j for o in names): continue
                miss[(jt, kt)].append(r['id'])

    import gzf, build_font
    kept = {c for c, a, x, col, row in gzf.load('extract/jp/romfs/data/Region_JP/main.gzf')[1]
            if not build_font.drop_group(c)}
    nofont = collections.Counter()
    for r in rows:
        for ch in body(r['ko']):
            c = ord(ch)
            if ch not in '\n ' and not (0xAC00 <= c <= 0xD7A3) and c not in kept: nofont[ch] += 1

    style = collections.defaultdict(list)
    pats = [('그녀·그들', re.compile(r'그녀|그들')),
            ('물결표 뒤 부호', re.compile(r'[~～][.,]')),
            ('줄임표+마침표', re.compile(r'…\.(?!\S)')),
            ('직역투 "이 내가"', re.compile(r'이 내가')),
            ('직역투 "~하는 것이다"', re.compile(r'는 것이다'))]
    for r in rows:
        k = body(r['ko'])
        for name, p in pats:
            if p.search(k): style[name].append(r['id'])
        if r['id'] >= 40000 and '{18}' not in r['ko'] and '　' in TAG.sub('', r['ko']):
            style['대사 속 전각 공백'].append(r['id'])
        if r['id'] in NOPUNCT_EXCL: continue
        kp = page_lasts(r['ko']); jp = page_lasts(strip_ruby(r['jp']))
        for i, kl in enumerate(kp):
            if re.search(r'[.!?…~♪」』)）,]$', kl) or not KO_END.search(kl): continue
            jl = jp[i] if i < len(jp) else (jp[-1] if jp else '')
            if JP_SENT.search(jl):
                style['문장 끝 부호 없음'].append(r['id']); break

    print('점검 대상 %d개' % len(rows))
    print('\n[고유명사 표기 누락] %d종' % len(miss))
    for (jt, kt), ids in sorted(miss.items(), key=lambda x: -len(x[1]))[:40 if detail else 15]:
        print('  %-12s → %-10s %3d건  %s' % (jt, kt, len(ids), ids[:6]))
    print('\n[배포 폰트에 없는 글자] %s' % (dict(nofont) or '없음'))
    print('\n[문체]')
    for name, ids in style.items():
        print('  %-22s %4d건  %s' % (name, len(ids), ids[:12]))
    if not style: print('  이상 없음')


if __name__ == '__main__':
    main()
