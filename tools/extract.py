# -*- coding: utf-8 -*-
"""일본판 CIA 에서 빌드에 필요한 romfs 파일과 HOME 메뉴 배너·아이콘을 뽑는다.
  → extract/jp/romfs/data/Region_JP/..., extract/jp/exefs/banner.bin, icon.bin

  python tools/extract.py "일본판.cia"
  python tools/extract.py "일본판.cia" --all        # romfs 전체
  python tools/extract.py "일본판.cia" --cxi        # Azahar 테스트용 복호화 CXI → emu/EverOasis_JP.cxi
                                                     (한글은 build_all.py 가 채우는 Azahar 모드 폴더로 덮인다)

pyctr 가 복호화에 쓸 boot9.bin 과 seeddb.bin(이 게임은 seed 암호화)이 필요하다.
Azahar 를 쓰면 %APPDATA%\\Azahar\\sysdata\\ 에 있으므로 자동으로 그 경로를 쓴다.
다른 곳에 있으면 환경 변수 BOOT9_PATH, SEEDDB_PATH 로 지정한다.
"""
import sys, os
TID = 0x0004000000164A00
NEED = 'data/Region_JP'   # 폰트·텍스트·그림 글씨가 전부 여기 있다
OUT = 'extract/jp/romfs'
EXEFS = 'extract/jp/exefs'

sysdata = os.path.join(os.environ.get('APPDATA', ''), 'Azahar', 'sysdata')
for var, name in (('BOOT9_PATH', 'boot9.bin'), ('SEEDDB_PATH', 'seeddb.bin')):
    if var not in os.environ and os.path.exists(os.path.join(sysdata, name)):
        os.environ[var] = os.path.join(sysdata, name)

from pyctr.type.cia import CIAReader


def walk(romfs, path):
    info = romfs.get_info_from_path(path)
    if hasattr(info, 'contents'):
        for name in info.contents:
            yield from walk(romfs, path.rstrip('/') + '/' + name)
    else:
        yield path


def make_cxi(cia, dst='emu/EverOasis_JP.cxi'):
    import shutil
    from pyctr.type.ncch import NCCHSection
    os.makedirs(os.path.dirname(dst), exist_ok=True)
    with CIAReader(cia) as c, c.contents[0].open_raw_section(NCCHSection.FullDecrypted) as f, open(dst, 'wb') as o:
        shutil.copyfileobj(f, o, 1 << 24)
    print('CXI → %s (%s 바이트)' % (dst, format(os.path.getsize(dst), ',')))


def main():
    cia = sys.argv[1]; top = '/' if '--all' in sys.argv else '/' + NEED
    if '--cxi' in sys.argv:
        return make_cxi(cia)
    n = 0
    with CIAReader(cia) as c:
        ncch = c.contents[0]
        if int(str(ncch.program_id), 16) != TID:
            sys.exit('일본판 본편(%016X)이 아닙니다: %016X' % (TID, int(str(ncch.program_id), 16)))
        romfs = ncch.romfs
        for p in walk(romfs, top):
            dst = os.path.join(OUT, p.lstrip('/'))
            os.makedirs(os.path.dirname(dst), exist_ok=True)
            with romfs.open(p) as f, open(dst, 'wb') as o:
                o.write(f.read())
            n += 1
        os.makedirs(EXEFS, exist_ok=True)
        for name in ('banner', 'icon'):
            with ncch.exefs.open(name) as f, open(os.path.join(EXEFS, name + '.bin'), 'wb') as o:
                o.write(f.read())
    print('%d개 파일 → %s, 배너·아이콘 → %s' % (n, OUT, EXEFS))


if __name__ == '__main__':
    main()
