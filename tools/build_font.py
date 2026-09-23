# -*- coding: utf-8 -*-
"""한글 폰트(main.gzf) 빌드.

칸이 2,346개뿐이라(51열 × 46행) 쓰지 않는 일본어·그리스·키릴·라틴확장 글리프를 빼고
그 자리에 한글을 넣는다. 넣을 음절은 지난 한글패치 번역문의 빈도 순서를 따른다.

  python tools/build_font.py dev      # 일본어 글리프 유지 + 필요한 한글만 (작업 중 확인용)
  python tools/build_font.py release  # 일본어 제거 + 한글 최대치
"""
import sys,os,json
sys.path.insert(0,os.path.dirname(__file__))
import gzf,hangul

JP='extract/jp/romfs/data/Region_JP/main.gzf'
OUT='work/romfs/data/Region_JP/main.gzf'
FONT='tools/fonts/GothicA1-Bold.ttf'; SIZE=14; WEIGHT=None; ADV=16
FREQ='tools/data/syllable_freq.json'

def drop_group(c):
    """한글판에서 필요 없는 글리프."""
    if c in (0x30FB, 0x30FC):       # 가운뎃점 ・ 과 장음 ー 는 한국어 번역에도 쓰인다
        return False
    return (0x4E00<=c<0xA000        # 한자
         or 0x3040<=c<0x3100        # 가나
         or 0x0370<=c<0x0500        # 그리스·키릴
         or 0x0100<=c<0x0250)       # 라틴 확장

def ksx1001():
    out=[]
    for c in range(0xAC00,0xD7A4):
        try: chr(c).encode('euc-kr')
        except UnicodeEncodeError: continue
        out.append(c)
    return out

def build(mode='release', extra_text='', verbose=True):
    hdr,ents,atlas=gzf.load(JP)
    keep=[(c,a,x,i) for i,(c,a,x,col,row) in enumerate(ents)
          if mode=='dev' or not drop_group(c)]
    free=gzf.COLS*(1024//gzf.PH)-len(keep)
    freq=[ord(ch) for ch in json.load(open(FREQ,encoding='utf8'))] if os.path.exists(FREQ) else []
    need=[ord(ch) for ch in dict.fromkeys(extra_text) if 0xAC00<=ord(ch)<=0xD7A3]
    order=list(dict.fromkeys(need+freq+ksx1001()))
    add=order[:free]
    if verbose:
        print('유지 글리프 %d, 남는 칸 %d, 넣을 한글 %d'%(len(keep),free,len(add)))
        miss=[chr(c) for c in need if c not in add]
        if miss: print('!! 자리 부족으로 빠진 글자:',''.join(miss))
    font,dx,dy,ink=hangul.plan(FONT,SIZE,WEIGHT,ADV)
    glyphs=[]
    for c,a,x,i in keep:
        cx,cy=gzf.cell(i); glyphs.append((c,a,x,atlas.crop((cx,cy,cx+gzf.BOX,cy+gzf.BOX))))
    for c in add:
        glyphs.append((c,ADV,3,hangul.glyph(chr(c),font,dx,dy)))
    glyphs.sort(key=lambda g:g[0])
    os.makedirs(os.path.dirname(OUT),exist_ok=True)
    n,toff=gzf.save(OUT,hdr,glyphs)
    if verbose: print('글리프 %d개, %d행 사용, 텍스처 오프셋 %s → %s'%(n,(n+gzf.COLS-1)//gzf.COLS,hex(toff),OUT))
    return n

if __name__=='__main__':
    build(sys.argv[1] if len(sys.argv)>1 else 'release')
