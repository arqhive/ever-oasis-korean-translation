# -*- coding: utf-8 -*-
"""한글 글리프 렌더링.

원본 글리프는 '또렷한 본체 + 반투명 테두리'(게임이 테두리를 어두운 색으로 칠한다) 구조다.
블러로 만들면 가장자리 값이 들쭉날쭉해 지저분해 보여서, 고해상도 마스크를 1픽셀씩
확장해 50% → 23% 두 겹으로 두른다.

**테두리는 글자 속 빈 공간(ㅇ·ㅁ·ㅂ 안쪽)에도 똑같이 두른다.** 예전에는 구멍이 메워질까 봐
바깥에만 둘렀는데, 그러면 안쪽만 배경색 그대로 남아 같은 글자인데 안팎 밝기가 달라 보였다.
원본 글리프(口·日 등)도 안쪽에 170 → 119 → 85 로 테두리가 들어가 있다.
"""
from PIL import Image,ImageFont,ImageDraw,ImageFilter
import numpy as np
SAMPLE='가힣핑뷁률온를것의피부색을골라주세요게임시작눈'
BOX=20; SS=4; LEVELS=(0.55,0.23)

def mkfont(path,size,w=None):
    f=ImageFont.truetype(path,size)
    if w:
        try: f.set_variation_by_axes([w])
        except Exception: pass
    return f

def _draw(ch,f,scale=1):
    t=Image.new('L',(72*scale,72*scale),0)
    ImageDraw.Draw(t).text((20*scale,48*scale),ch,font=f,fill=255,anchor='ls')  # 왼쪽 기준선 고정
    return t

def plan(path,size,w,adv,tl=2,tt=2):
    """대표 글자들의 공통 잉크 박스로 전역 오프셋 결정(자간·행간이 흔들리지 않게)."""
    f=mkfont(path,size,w); L=T=999;R=B=-999
    for ch in SAMPLE:
        a=np.array(_draw(ch,f)); ys,xs=np.where(a>=40)
        L=min(L,xs.min());T=min(T,ys.min());R=max(R,xs.max());B=max(B,ys.max())
    iw,ih=R-L+1,B-T+1
    dx=tl+(adv-iw)//2-(L-20); dy=tt+((16-ih)//2)-(T-48)
    return mkfont(path,size*SS,w),dx,dy,(iw,ih)

def holes(g):
    """글자 속 닫힌 빈 공간(ㅇ·ㅁ 안쪽) 마스크 — 채워졌는지 검사할 때 쓴다."""
    inv=g.point(lambda v:0 if v else 255)
    ff=inv.copy()
    for pt in [(0,0),(ff.width-1,0),(0,ff.height-1),(ff.width-1,ff.height-1)]:
        if ff.getpixel(pt)==255: ImageDraw.floodfill(ff,pt,128)
    return np.array(ff)==255

def glyph(ch,f_hi,dx,dy,levels=LEVELS):
    t=_draw(ch,f_hi,SS).crop(((20-dx)*SS,(48-dy)*SS,(20-dx+BOX)*SS,(48-dy+BOX)*SS))
    m=t.point(lambda v:255 if v>=128 else 0)
    out=np.array(m,dtype=np.float32); prev=m
    for lv in levels:
        prev=prev.filter(ImageFilter.MaxFilter(2*SS+1))          # 최종 1픽셀만큼 확장
        out=np.maximum(out,np.array(prev,dtype=np.float32)*lv)   # 안쪽 빈 공간에도 두른다
    im=Image.fromarray(out.clip(0,255).astype(np.uint8)).resize((BOX,BOX),Image.BOX)
    a=np.round(np.array(im,dtype=np.float32)/255*15)/15*255      # A4(4비트)에 맞춰 양자화
    return Image.fromarray(a.astype(np.uint8))
