# -*- coding: utf-8 -*-
"""전체 텍스트 JSON 내보내기: id, kind, speaker, speaker_source, jp, ko.

speaker_source: 'script' = 게임 스크립트의 대화 호출에서 확정, 'guess' = 문맥 추정, None = 대사가 아님
  python tools/export_json.py
"""
import sys, os, json, glob
sys.path.insert(0, os.path.dirname(__file__))
from text_io import strip_ruby, OUT

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

def main():
    rows = json.load(open(OUT, encoding='utf8'))
    exact = {int(k): v for k, v in json.load(open('translation/speakers/exact.json', encoding='utf8')).items()}
    guess = {}
    for p in sorted(glob.glob('translation/speakers/guess_*.json')):
        guess.update({int(k): v for k, v in json.load(open(p, encoding='utf8')).items()})
    out = []; stat = {'script': 0, 'guess': 0, 'none': 0, 'missing': 0}
    for r in rows:
        if not r['jp_plain'].strip(): continue
        i = r['id']; k = kind(i); sp = None; src = None
        if k == '대사':
            if i in exact: sp, src = exact[i], 'script'
            elif i in guess: sp, src = guess[i], 'guess'
            else: stat['missing'] += 1
        if src: stat[src] += 1
        else: stat['none'] += 1
        out.append({'id': i, 'kind': k, 'speaker': sp, 'speaker_source': src,
                    'jp': strip_ruby(r['jp']), 'ko': r['ko']})
    dst = 'work/에버오아시스_전체텍스트.json'
    json.dump(out, open(dst, 'w', encoding='utf8'), ensure_ascii=False, indent=1)
    print('%d개 → %s' % (len(out), dst), stat)

if __name__ == '__main__':
    main()
