# -*- coding: utf-8 -*-
"""한글 폰트 시안 시트: 게임과 같은 배색(흰 글자+어두운 테두리 / 어두운 글자+밝은 테두리)으로 그린다."""
import sys,os
sys.path.insert(0,os.path.dirname(__file__))
from PIL import Image,ImageFont,ImageDraw,ImageFilter
import numpy as np, gzf

HDR,ENTS,ATLAS=gzf.load('extract/jp/romfs/data/Region_JP/main.gzf')
E={c:(a,x,i) for i,(c,a,x,col,row) in enumerate(ENTS)}
SAMPLE='가힣핑뷁률온를것의피부색을골라주세요게임시작눈'

def mkfont(path,size,w=None):
    f=ImageFont.truetype(path,size)
    if w:
        try: f.set_variation_by_axes([w])
        except Exception: pass
    return f

def raw(ch,f):
    t=Image.new('L',(72,72),0)
    ImageDraw.Draw(t).text((20,48),ch,font=f,fill=255,anchor='ls')
    return t

def plan(path,size,w,adv,tl=2,tt=2):
    f=mkfont(path,size,w); L=T=999;R=B=-999
    for ch in SAMPLE:
        a=np.array(raw(ch,f)); ys,xs=np.where(a>=40)
        L=min(L,xs.min());T=min(T,ys.min());R=max(R,xs.max());B=max(B,ys.max())
    iw,ih=R-L+1,B-T+1
    return f,tl+(adv-iw)//2-(L-20),tt+((16-ih)//2)-(T-48),(iw,ih)

def glyph(ch,f,dx,dy,r=1.0,gain=2.0,cap=0.55,boost=1.35):
    c=np.array(raw(ch,f).crop((20-dx,48-dy,20-dx+20,48-dy+20)),dtype=np.float32)
    c=np.clip(c*boost,0,255)
    b=np.array(Image.fromarray(c.astype(np.uint8)).filter(ImageFilter.GaussianBlur(r)),dtype=np.float32)*gain
    return np.maximum(c,np.clip(b,0,cap*255)).clip(0,255)

def alpha_line(s,f,dx,dy,adv,**kw):
    """한글은 새 폰트, 반각(ASCII)은 원본 폰트 그대로 — 실제 게임과 같은 간격."""
    W=len(s)*adv+24
    im=np.zeros((20,W),np.float32); pen=0
    for ch in s:
        c=ord(ch)
        if ch==' ': pen+=E[0x20][0]; continue
        if c<0x80 and c in E:
            a,x,i=E[c]; cx,cy=gzf.cell(i)
            g=np.array(ATLAS.crop((cx,cy,cx+20,cy+20)),dtype=np.float32)
            im[:,pen:pen+20]=np.maximum(im[:,pen:pen+20],g); pen+=a
        else:
            g=glyph(ch,f,dx,dy,**kw)
            im[:,pen:pen+20]=np.maximum(im[:,pen:pen+20],g); pen+=adv
    return im[:,:pen+6]

def alpha_jp(s):
    W=sum(E[ord(c)][0] for c in s)+24
    im=np.zeros((20,W),np.float32); pen=0
    for ch in s:
        a,x,i=E[ord(ch)]; cx,cy=gzf.cell(i)
        g=np.array(ATLAS.crop((cx,cy,cx+20,cy+20)),dtype=np.float32)
        im[:,pen:pen+20]=np.maximum(im[:,pen:pen+20],g); pen+=a
    return im[:,:pen+6]

def colorize(a,bg,fill,edge,thr=0.55):
    """알파 → 게임식 배색: 진한 속은 fill, 후광은 edge."""
    A=a/255.0
    col=np.zeros(a.shape+(3,),np.float32)
    m=(A>=thr)[...,None]
    col=np.where(m,np.array(fill,np.float32),np.array(edge,np.float32))
    out=np.array(bg,np.float32)*(1-A[...,None])+col*A[...,None]
    return out.clip(0,255).astype(np.uint8)
