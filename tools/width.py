# -*- coding: utf-8 -*-
"""문구 폭 계산 — 원문보다 넓어지는 번역을 찾는다.

한글은 advance 16, 나머지는 폰트 엔트리의 advance 를 쓴다. 제어코드는 0 으로 친다.
치환 자리({11} 숫자 등)는 폭을 알 수 없으므로 제외한다.
"""
import sys,os,re
sys.path.insert(0,os.path.dirname(__file__))
import gzf
TAG=re.compile(r'\{[0-9a-f]{2}(?::[0-9a-f]{8})?\}')
_adv=None
def adv_table():
    global _adv
    if _adv is None:
        _adv={c:a for c,a,x,col,row in gzf.load('extract/jp/romfs/data/Region_JP/main.gzf')[1]}
    return _adv
# 버튼 아이콘 {08:xx} 은 화면에서 약 20px(실기 사진 실측, 83015 「✚✚ 버튼으로 바꾸고 Ⓐ 버튼을 누르면」 10/10).
# 예전엔 0 으로 쳐서 아이콘 든 줄이 창에 닿아도 검사를 통과했다. 줄 안에서는 ICON_CH 한 글자로 바꿔 센다.
ICON_W = 20
ICON_CH = ''
ICON = re.compile(r'\{08:[0-9a-f]{8}\}')
def width(t,hangul_adv=16):
    a=adv_table(); w=0; mx=0
    for ch in TAG.sub('',ICON.sub(ICON_CH,t)).replace('{z}',''):
        if ch=='\n': mx=max(mx,w); w=0; continue
        if ch in '�￿': continue
        if ch==ICON_CH: w+=ICON_W; continue
        c=ord(ch)
        w+= hangul_adv if 0xAC00<=c<=0xD7A3 else a.get(c,14)
    return max(mx,w)
def lines(t):
    return [l for l in TAG.sub('',t).replace('{z}','').split('\n')]

# ── 대사창 한도 ───────────────────────────────────────────────
# 원본 일본어 15,416줄을 전수 측정해 얻은 값(성별 분기는 긴 쪽만 센다).
#   입력 대기({03} 직전, 다음 줄 화살표가 뜬다) 332px
#   메시지 끝({00} 직전)                        326px
#   중간 줄({01}·{02} 직전)                     333px
# 332px 를 넘으면 화살표 UI 가 마지막 글자를 덮는다(ID 90024 제보, 360px).
LIMITS = {'03': 332, '00': 326, '01': 333, '02': 333, '--': 333}
LIMIT = 332          # 종류를 가리지 않는 안전선
_ANY = re.compile(r'\{([0-9a-z]{2})(?::[0-9a-f]{8})?\}')
_BRANCH = re.compile(r'\{15\}([^{]*)\{z\}\{16\}([^{]*)\{z\}')


def one_branch(t):
    """성별 분기 {15}A{z}{16}B{z} 는 한 번에 한쪽만 보이므로 긴 쪽만 남긴다."""
    return _BRANCH.sub(lambda m: m.group(1) if width(m.group(1)) >= width(m.group(2))
                       else m.group(2), t)


def seglines(t):
    """(줄 텍스트, 줄을 끝낸 코드) 목록. 코드는 LIMITS 의 열쇠."""
    t = one_branch(t); out = []; cur = ''; i = 0
    while i < len(t):
        m = _ANY.match(t, i)
        if m:
            c = m.group(1)
            if c in ('01', '02', '03', '00'): out.append((cur, c)); cur = ''
            elif c == '08': cur += ICON_CH
            i = m.end(); continue
        if t[i] not in '﻿�': cur += t[i]
        i += 1
    if cur.strip(): out.append((cur, '--'))
    return out


def over(t):
    """한도를 넘은 줄 [(폭, 한도, 코드, 줄)]."""
    bad = []
    for line, c in seglines(t):
        w = width(line); lim = LIMITS.get(c, 333)
        if w > lim: bad.append((w, lim, c, line))
    return bad
