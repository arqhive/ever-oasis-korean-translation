# -*- coding: utf-8 -*-
"""번역 작업 파일 만들기/되돌리기.

  python tools/text_io.py extract   # work/text/messages.json 생성 (일본어+영어+번역칸)
  python tools/text_io.py apply     # ko 가 채워진 항목으로 main.gmsg 빌드
  python tools/text_io.py check     # 태그 보존·폰트 누락 검사
  python tools/text_io.py save      # messages.json 의 번역을 translation/ko.json 에 저장

번역 원본은 translation/ko.json({ID: 번역문})이다. messages.json 은 원문이 들어 있어 커밋하지 않으며,
없을 때 extract 하면 번역칸을 translation/ko.json 에서 채운다. 영어판(EN)은 참고용이라 없어도 된다.
"""
import sys,os,json,re,collections
sys.path.insert(0,os.path.dirname(__file__))
import gmsg

JP='extract/jp/romfs/data/Region_JP/Japanese/main.gmsg'
EN='extract/us_upd/romfs/data/Region_US/English/main.gmsg'
OUTDIR='work/text'; OUT=OUTDIR+'/messages.json'
KO_JSON='translation/ko.json'
BUILT='work/romfs/data/Region_JP/Japanese/main.gmsg'

TAG=re.compile(r'\{([0-9a-f]{2})(?::([0-9a-f]{8}))?\}')
RUBY=re.compile(r'\{1a\}(.*?)\{z\}(.*?)\{1b\}')

def plain(t):
    """읽기용: 후리가나는 본문만 남기고 태그 제거."""
    t=RUBY.sub(lambda m:m.group(2),t)
    t=t.replace('{01}','\n').replace('{02}','\n\n').replace('{z}','')
    return TAG.sub('',t)

def strip_ruby(t):
    return RUBY.sub(lambda m:m.group(2),t)

def codes(t):
    return [m.group(0) for m in TAG.finditer(t)]

def extract():
    old={}
    if os.path.exists(OUT):
        old={r['id']:r.get('ko','') for r in json.load(open(OUT,encoding='utf8'))}
    elif os.path.exists(KO_JSON):
        old={int(k):v for k,v in json.load(open(KO_JSON,encoding='utf8')).items()}
    dj,Ej,ej,Tj=gmsg.texts(JP)
    en={}
    if os.path.exists(EN):
        du,Eu,eu,Tu=gmsg.texts(EN)
        en={a:Tu[i] for i,(a,b,o,l) in enumerate(Eu)}
    rows=[]
    for i,(a,b,o,l) in enumerate(Ej):
        rows.append({'idx':i,'id':a,'style':b,
                     'jp':Tj[i],'jp_plain':plain(Tj[i]),
                     'en':en.get(a,''),'en_plain':plain(en.get(a,'')),
                     'ko':old.get(a,'')})
    os.makedirs(OUTDIR,exist_ok=True)
    json.dump(rows,open(OUT,'w',encoding='utf8'),ensure_ascii=False,indent=1)
    n_ruby=sum(1 for r in rows if '{1a}' in r['jp'])
    chars=sum(len(r['jp_plain'].replace('\n','')) for r in rows)
    print('메시지 %d개 → %s'%(len(rows),OUT))
    print('후리가나 포함 %d개 / 읽을 글자 %d자'%(n_ruby,chars))
    return rows

def apply_():
    rows=json.load(open(OUT,encoding='utf8'))
    ko={r['id']:r['ko'] for r in rows if r['ko'].strip()}
    d,E,enc=gmsg.load(JP)
    os.makedirs(os.path.dirname(BUILT),exist_ok=True)
    size=gmsg.save(BUILT,d,E,enc,ko)
    print('번역 %d개 반영 → %s (%d바이트)'%(len(ko),BUILT,size))
    return ko

def save():
    rows=json.load(open(OUT,encoding='utf8'))
    ko={str(r['id']):r['ko'] for r in rows if r['ko'].strip()}
    os.makedirs(os.path.dirname(KO_JSON),exist_ok=True)
    with open(KO_JSON,'w',encoding='utf8',newline='') as f:
        json.dump(ko,f,ensure_ascii=False,indent=0)
    print('번역 %d개 → %s'%(len(ko),KO_JSON))

def check():
    rows=json.load(open(OUT,encoding='utf8'))
    import gzf
    have={c for c,a,x,col,row in gzf.load('work/romfs/data/Region_JP/main.gzf')[1]} \
          if os.path.exists('work/romfs/data/Region_JP/main.gzf') else set()
    bad=collections.Counter(); miss=collections.Counter()
    for r in rows:
        if not r['ko'].strip(): continue
        cj=[c for c in codes(strip_ruby(r['jp'])) if c not in ('{1a}','{1b}')]
        ck=codes(r['ko'])
        # 원문에 없던 성별 분기 {15}..{z}{16}..{z} 추가는 허용(형/오빠 등)
        ex=ck.count('{15}')-cj.count('{15}')
        if ex>0 and ck.count('{16}')-cj.count('{16}')==ex:
            ck=[c for c in ck]; [ck.remove('{15}') or ck.remove('{16}') for _ in range(ex)]
        if collections.Counter(cj)!=collections.Counter(ck):
            bad['태그 불일치']+=1
            if bad['태그 불일치']<=5: print('  태그 불일치 id%d\n    원문 %s\n    번역 %s'%(r['id'],cj,ck))
        for ch in plain(r['ko']):
            if ch not in '\n ' and have and ord(ch) not in have: miss[ch]+=1
    print('검사 완료:',dict(bad) or '태그 이상 없음')
    if miss: print('폰트에 없는 글자 %d종: %s'%(len(miss),''.join(miss)))

if __name__=='__main__':
    {'extract':extract,'apply':apply_,'check':check,'save':save}[sys.argv[1]]()
