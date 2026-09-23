# -*- coding: utf-8 -*-
"""에버오아시스 main.gmsg (Grezzo GMSG v3) 읽기/쓰기.

헤더: 0x08 인코딩(1=UTF-16LE 일본판, 2=1바이트 북미판), 0x0C 메시지 수, 0x10 테이블 오프셋.
엔트리 16B {u32 id, u32 스타일, u32 절대오프셋, u32 바이트길이}.
제어코드: 0x7F + (2바이트 정렬) + u16 코드, 아래 ARG1 에 든 13개는 뒤에 u32 인자 하나.
8,515개 전부에서 이 문법이 성립함을 확인했다.
"""
import struct

ARG1={0x04,0x05,0x06,0x08,0x09,0x0a,0x0e,0x0f,0x10,0x11,0x12,0x13,0x19}
ENT=16

def load(path):
    d=open(path,'rb').read()
    enc,n,toff=struct.unpack_from('<III',d,8)
    ents=[list(struct.unpack_from('<4I',d,toff+i*ENT)) for i in range(n)]
    return d,ents,enc

def tokens(s,enc):
    """→ [('t',문자열) | ('c',코드,인자 또는 None)]"""
    cw=2 if enc==1 else 1
    out=[]; i=0; buf=[]
    while i<len(s):
        if (s[i] if cw==1 else struct.unpack_from('<H',s,i)[0])==0x7f:
            if buf: out.append(('t',''.join(buf))); buf=[]
            i+=1 if cw==1 else 2
            if cw==1 and i%2: i+=1                      # 코드는 2바이트 정렬
            c=struct.unpack_from('<H',s,i)[0]; i+=2
            a=None
            if c in ARG1:
                if i%2: i+=1
                a=struct.unpack_from('<I',s,i)[0]; i+=4
            out.append(('c',c,a))
        else:
            if cw==1: buf.append(chr(s[i])); i+=1
            else: buf.append(chr(struct.unpack_from('<H',s,i)[0])); i+=2
    if buf: out.append(('t',''.join(buf)))
    return out

def build(toks,enc):
    cw=2 if enc==1 else 1
    out=bytearray()
    for tk in toks:
        if tk[0]=='t':
            for ch in tk[1]:
                out+=struct.pack('<H',ord(ch)) if cw==2 else bytes([ord(ch)&0xff])
        else:
            out+=b'\x7f' if cw==1 else struct.pack('<H',0x7f)
            if cw==1 and len(out)%2: out+=b'\x00'
            out+=struct.pack('<H',tk[1])
            if tk[2] is not None: out+=struct.pack('<I',tk[2])
    return bytes(out)

def to_str(toks):
    """편집용 문자열: 제어코드는 {xx} 또는 {xx:인자8자리}, NUL 은 {z}."""
    r=[]
    for tk in toks:
        if tk[0]=='t': r.append(tk[1].replace('\0','{z}'))
        elif tk[2] is None: r.append('{%02x}'%tk[1])
        else: r.append('{%02x:%08x}'%(tk[1],tk[2]))
    return ''.join(r)

def from_str(t):
    toks=[]; buf=[]; i=0
    while i<len(t):
        if t[i]=='{':
            j=t.index('}',i); body=t[i+1:j]; i=j+1
            if body=='z': buf.append('\0'); continue
            if buf: toks.append(('t',''.join(buf))); buf=[]
            if ':' in body:
                c,a=body.split(':'); toks.append(('c',int(c,16),int(a,16)))
            else: toks.append(('c',int(body,16),None))
        else:
            buf.append(t[i]); i+=1
    if buf: toks.append(('t',''.join(buf)))
    return toks

def texts(path):
    d,E,enc=load(path)
    return d,E,enc,[to_str(tokens(d[o:o+l],enc)) for a,b,o,l in E]

def save(path,d,ents,enc,newtexts):
    """newtexts: {메시지 id: 편집 문자열}"""
    tbl=bytearray(); body=bytearray()
    base=struct.unpack_from('<I',d,16)[0]+len(ents)*ENT
    for a,b,o,l in ents:
        s=build(from_str(newtexts[a]),enc) if a in newtexts else d[o:o+l]
        tbl+=struct.pack('<4I',a,b,base+len(body),len(s))
        body+=s
        while len(body)%4: body+=b'\0'
    out=bytearray(d[:struct.unpack_from('<I',d,16)[0]])+tbl+body
    open(path,'wb').write(bytes(out))
    return len(out)
