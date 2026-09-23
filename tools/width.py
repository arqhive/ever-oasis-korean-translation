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
def width(t,hangul_adv=16):
    a=adv_table(); w=0; mx=0
    for ch in TAG.sub('',t).replace('{z}',''):
        if ch=='\n': mx=max(mx,w); w=0; continue
        if ch in '�￿': continue
        c=ord(ch)
        w+= hangul_adv if 0xAC00<=c<=0xD7A3 else a.get(c,14)
    return max(mx,w)
def lines(t):
    return [l for l in TAG.sub('',t).replace('{z}','').split('\n')]
