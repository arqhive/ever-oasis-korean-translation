"""GZFX 폰트(에버오아시스) 읽기/쓰기. 셀 피치 = (20, 22), 51열."""
import struct
from PIL import Image
COLS=51; PW,PH=20,22; BOX=20

def load(path):
    d=open(path,'rb').read()
    n=struct.unpack_from('<I',d,0x14)[0]
    toff=struct.unpack_from('<I',d,0x30)[0]
    w,h=struct.unpack_from('<HH',d,0x34)
    ents=[struct.unpack_from('<IIHBB',d,0x38+i*12) for i in range(n)]  # code, adv, x, col, row
    atlas=decode_a4(d[toff:],w,h)
    return d[:0x38], ents, atlas

def decode_a4(data,w,h):
    im=Image.new('L',(w,h)); px=im.load(); p=0
    for ty in range(0,h,8):
        for tx in range(0,w,8):
            for i in range(64):
                x=((i&1)|((i>>1)&2)|((i>>2)&4)); y=(((i>>1)&1)|((i>>2)&2)|((i>>3)&4))
                v=(data[p>>1]>>((p&1)*4))&15; p+=1
                px[tx+x,ty+y]=v*17
    return im

def encode_a4(im):
    w,h=im.size; px=im.load(); out=bytearray(w*h//2); p=0
    for ty in range(0,h,8):
        for tx in range(0,w,8):
            for i in range(64):
                x=((i&1)|((i>>1)&2)|((i>>2)&4)); y=(((i>>1)&1)|((i>>2)&2)|((i>>3)&4))
                v=(px[tx+x,ty+y]*15+127)//255
                if p&1: out[p>>1]|=v<<4
                else: out[p>>1]=v
                p+=1
    return bytes(out)

def cell(i): return (i%COLS)*PW,(i//COLS)*PH

def save(path, hdr, glyphs, texw=1024, texh=1024):
    """glyphs: [(code, adv, x, Image('L') BOX×BOX)] — 코드 오름차순으로 들어와야 한다."""
    atlas=Image.new('L',(texw,texh),0)
    tbl=bytearray()
    for i,(code,adv,xo,im) in enumerate(glyphs):
        cx,cy=cell(i)
        assert cy+BOX<=texh, f'아틀라스 초과: {i}번째 글리프'
        atlas.paste(im,(cx,cy))
        tbl+=struct.pack('<IIHBB',code,adv,xo,i%COLS,i//COLS)
    h=bytearray(hdr)
    struct.pack_into('<I',h,0x14,len(glyphs))
    toff=(0x38+len(tbl)+127)//128*128
    struct.pack_into('<I',h,0x30,toff)
    struct.pack_into('<HH',h,0x34,texw,texh)
    out=bytearray(h+tbl); out+=b'\0'*(toff-len(out)); out+=encode_a4(atlas)
    open(path,'wb').write(bytes(out))
    return len(glyphs),toff
