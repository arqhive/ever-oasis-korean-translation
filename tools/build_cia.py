# -*- coding: utf-8 -*-
"""사용자가 가진 일본판 CIA 로 HOME 메뉴 배너·게임 이름을 한글로 바꾼 CIA 를 만든다.

  python tools/build_banner.py                                  # 먼저 work/exefs/banner.bin, icon.bin 생성
  python tools/build_cia.py --cia "일본판.cia" --out "한글판.cia"

게임 안 텍스트는 LayeredFS 패치(release/luma)로 입히고, 이 CIA 는 ExeFS 의 배너·아이콘만 바꾼다.
romfs 는 원본 그대로 옮긴다.

준비물
  * 일본판 CIA (0004000000164A00)
  * 3dstool, makerom — tools/bin 에 두거나 --tools 로 폴더 지정
  * boot9.bin, seeddb.bin — 이 게임은 seed 암호화라 ctrtool 대신 pyctr 로 복호화한다.
    Azahar 의 %APPDATA%\\Azahar\\sysdata\\ 에 있으면 자동으로 쓴다(BOOT9_PATH·SEEDDB_PATH 로 지정 가능).
  * 디스크 여유 약 3GB

겪어 본 함정 (페더레이션 포스·각성 기록)
  * CXI 를 --not-encrypt 로 만들어야 makerom 이 exheader 를 읽어 meta 영역까지 만든다.
  * makerom 에 -ignoresign 이 없으면 "Content 0 Is Corrupt", -content 는 <파일>:<인덱스>:<ID> 세 칸.
  * makerom 은 TMD 버전을 exheader 의 remaster version 으로 쓴다 → 원본 TMD 버전으로 되돌린다.
  * 외부 도구는 '/' 와 '\\' 가 섞인 경로를 거부하므로 os.path.normpath 로 맞춘다.
  * ExeFS 의 .code 는 압축된 블롭 그대로 옮기므로 exheader 의 CompressExefsCode 는 그대로 둔다.
"""
import argparse, hashlib, os, shutil, struct, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
TID = '0004000000164a00'

sysdata = os.path.join(os.environ.get('APPDATA', ''), 'Azahar', 'sysdata')
for var, name in (('BOOT9_PATH', 'boot9.bin'), ('SEEDDB_PATH', 'seeddb.bin')):
    if var not in os.environ and os.path.exists(os.path.join(sysdata, name)):
        os.environ[var] = os.path.join(sysdata, name)
from pyctr.type.cia import CIAReader
from pyctr.type.ncch import NCCHSection


def run(cmd, log):
    with open(log, 'wb') as f:
        r = subprocess.run(cmd, stdout=f, stderr=subprocess.STDOUT)
    if r.returncode:
        print(open(log, encoding='utf-8', errors='replace').read()[-2000:])
        raise SystemExit('실패: %s  (로그 %s)' % (' '.join(cmd), log))


def rebuild_exefs(d, patches):
    """ExeFS 블롭에서 patches({이름: 내용})만 바꿔 다시 쓴다. 헤더의 오프셋·크기·SHA-256 을 다시 계산."""
    entries = []
    for i in range(10):
        name, off, size = struct.unpack_from('<8sII', d, i * 16)
        if not size: continue
        key = name.rstrip(b'\0').decode()
        entries.append((name, key, patches.get(key, d[0x200 + off:0x200 + off + size])))
    hdr = bytearray(0x200); blob = bytearray()
    for i, (name, key, body) in enumerate(entries):
        struct.pack_into('<8sII', hdr, i * 16, name, len(blob), len(body))
        hdr[0x200 - (i + 1) * 32:0x200 - i * 32] = hashlib.sha256(body).digest()
        blob += body
        blob += b'\0' * ((-len(blob)) % 0x200)
        print('  [%d] %-8s %s' % (i, key, '교체' if key in patches else '원본'))
    return bytes(hdr) + bytes(blob)


def tmd_version_offset(f):
    """CIA 파일에서 TMD 타이틀 버전 필드의 절대 위치."""
    al = lambda x: (x + 63) & ~63
    f.seek(0); hdr = f.read(0x20)
    hsize, _t, _v, clen, tlen, tmdlen, _m = struct.unpack_from('<IHHIIII', hdr, 0)
    off = al(al(al(hsize) + clen) + tlen)
    f.seek(off); sig = struct.unpack('>I', f.read(4))[0]
    SIG = {0x10000: 0x23C, 0x10001: 0x13C, 0x10002: 0x7C, 0x10003: 0x23C, 0x10004: 0x13C, 0x10005: 0x7C}
    return off + 4 + SIG[sig] + 0x9C


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--cia', required=True, help='일본판 CIA')
    ap.add_argument('--out', required=True, help='만들 CIA')
    ap.add_argument('--tools', default=os.path.join(HERE, 'bin'), help='3dstool·makerom 폴더')
    ap.add_argument('--exefs', default=os.path.join(ROOT, 'work', 'exefs'), help='한글 banner.bin·icon.bin 폴더')
    ap.add_argument('--work', default=os.path.join(ROOT, 'work', 'cia'))
    ap.add_argument('--keep', action='store_true', help='작업 폴더를 지우지 않는다')
    a = ap.parse_args()
    np = os.path.normpath
    tool = lambda n: np(os.path.join(a.tools, n + '.exe' if os.name == 'nt' else n))
    W = a.work; os.makedirs(W, exist_ok=True)
    P = lambda n: np(os.path.join(W, n)); L = lambda n: P(n + '.log')

    # 1) 콘텐츠 복호화 (pyctr, seed 포함)
    with CIAReader(a.cia) as c:
        ver = c.tmd.title_version
        recs = [(r.cindex, r.id) for r in c.tmd.chunk_records]
        print('원본 CIA: 타이틀 버전 %s, 콘텐츠 %s' % (ver, recs))
        if str(c.contents[0].program_id).lower() != TID:
            raise SystemExit('일본판 본편(%s)이 아닙니다: %s' % (TID, c.contents[0].program_id))
        for idx, _cid in recs:
            dst = P('c%d.ncch' % idx)
            print('콘텐츠 %d 복호화 → %s' % (idx, dst))
            with c.contents[idx].open_raw_section(NCCHSection.FullDecrypted) as f, open(dst, 'wb') as o:
                shutil.copyfileobj(f, o, 1 << 24)

    # 2) 본편 CXI 펼치기 (romfs 는 펼치지 않고 통째로 옮긴다)
    parts = ['--header', P('ncchheader.bin'), '--exh', P('exheader.bin'), '--logo', P('logo.bin'),
             '--plain', P('plain.bin'), '--exefs', P('exefs.bin'), '--romfs', P('romfs.bin')]
    print('CXI 펼치기 (3dstool)')
    run([tool('3dstool'), '-xvtf', 'cxi', P('c0.ncch')] + parts, L('xcxi'))

    # 3) 배너·아이콘 교체
    print('ExeFS 배너·아이콘 교체')
    ex = open(P('exefs.bin'), 'rb').read()
    patches = {n: open(os.path.join(a.exefs, n + '.bin'), 'rb').read() for n in ('banner', 'icon')}
    open(P('exefs.bin'), 'wb').write(rebuild_exefs(ex, patches))

    # 4) CXI 다시 싸기 → CIA 묶기
    print('CXI 재빌드 (--not-encrypt)')
    run([tool('3dstool'), '-cvtf', 'cxi', P('ko.cxi')] + parts + ['--not-encrypt'], L('ccxi'))
    print('CIA 묶기 (makerom -ignoresign)')
    cmd = [tool('makerom'), '-f', 'cia', '-o', np(a.out), '-ignoresign']
    for idx, cid in recs:
        cmd += ['-content', '%s:%d:%d' % (P('ko.cxi') if idx == 0 else P('c%d.ncch' % idx), idx, int(cid, 16))]
    run(cmd, L('makerom'))

    # 5) TMD 버전을 원본 값으로
    want = int(str(ver).split('.')[0]) << 10 | int(str(ver).split('.')[1]) << 4 | int(str(ver).split('.')[2])
    with open(a.out, 'r+b') as f:
        o = tmd_version_offset(f); f.seek(o); cur = struct.unpack('>H', f.read(2))[0]
        if cur != want: f.seek(o); f.write(struct.pack('>H', want)); print('TMD 버전 %d -> %d' % (cur, want))
    print('\n완료: %s (%s 바이트)' % (a.out, format(os.path.getsize(a.out), ',')))
    if not a.keep: shutil.rmtree(W, ignore_errors=True)


if __name__ == '__main__':
    main()
