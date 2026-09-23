# -*- coding: utf-8 -*-
"""시험용 빌드: main.gzf 에 한글 글리프를 추가하고 main.gmsg 의 몇 문장을 교체한다."""
import os,sys,struct
from PIL import Image,ImageFont,ImageDraw
sys.path.insert(0,os.path.dirname(__file__))
import gzf,gmsg,hangul

JP='extract/jp/romfs/data/Region_JP'
OUT='work/romfs/data/Region_JP'
FONT='tools/fonts/GothicA1-Bold.ttf'
SIZE=14
WEIGHT=None
ADV=16                      # 글자 폭(원본 한자는 14)
BAND=(1,17)                 # 셀 안에서 글자가 들어갈 세로 구간
SAMPLE='가힣핑뷁률온를것의피부색을골라주세요게임시작눈'

TRANS={
 4419:'{17}새로 시작{00}',
 4420:'{17}이어서 하기{00}',
 332 :'{17}{08}\x01|게임 시작{00}',
 336 :'{17}게임 시작{00}',
 333 :'{17}세이브 데이터 선택{00}',
 337 :'{17}데이터 삭제{00}',
 334 :'이름{00}',
 335 :'{17}새로 게임을 시작할까요?{05}||{00}',
 339 :'세이브 데이터를 삭제했습니다.{03}{00}',
 4132:'{17}피부색을 골라 주세요.{05}||{00}',
 4133:'{17}눈 색을 골라 주세요.{05}|||{00}',
}



def main():
    hdr,ents,atlas=gzf.load(JP+'/main.gzf')
    have={c for c,a,x,col,row in ents}
    need=sorted({ch for t in TRANS.values() for ch in t
                 if ord(ch)>0x7f and ord(ch) not in have and not ch.isspace()})
    print('추가할 글자',len(need),''.join(need))
    glyphs=[]
    for i,(c,a,x,col,row) in enumerate(ents):
        cx,cy=gzf.cell(i); glyphs.append((c,a,x,atlas.crop((cx,cy,cx+gzf.BOX,cy+gzf.BOX))))
    font,dx,dy,ink=hangul.plan(FONT,SIZE,WEIGHT,ADV)
    print('본체 %dx%d, 오프셋'%ink,dx,dy)
    for ch in need: glyphs.append((ord(ch),ADV,3,hangul.glyph(ch,font,dx,dy)))
    glyphs.sort(key=lambda g:g[0])
    os.makedirs(OUT+'/Japanese',exist_ok=True)
    n,toff=gzf.save(OUT+'/main.gzf',hdr,glyphs)
    print('글리프',n,'행',(n+gzf.COLS-1)//gzf.COLS,'텍스처오프셋',hex(toff))

    d,E=gmsg.load(JP+'/Japanese/main.gmsg')
    size=gmsg.save(OUT+'/Japanese/main.gmsg',d,E,TRANS)
    print('gmsg',size)

    # 미리보기
    _,e2,at2=gzf.load(OUT+'/main.gzf')
    idx={c:i for i,(c,a,x,col,row) in enumerate(e2)}
    prev=Image.new('L',(len(need)*gzf.PW,gzf.PH),0)
    for k,ch in enumerate(need):
        cx,cy=gzf.cell(idx[ord(ch)]); prev.paste(at2.crop((cx,cy,cx+gzf.BOX,cy+gzf.BOX)),(k*gzf.PW,0))
    prev.resize((prev.width*3,prev.height*3),Image.NEAREST).save('analysis/hangul_preview.png')

main()
