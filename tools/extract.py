# -*- coding: utf-8 -*-
"""일본판 CIA 에서 빌드에 필요한 romfs 파일을 뽑는다 → extract/jp/romfs/data/Region_JP/...

  python tools/extract.py "일본판.cia"
  python tools/extract.py "일본판.cia" --all        # romfs 전체

pyctr 가 복호화에 쓸 boot9.bin 과 seeddb.bin(이 게임은 seed 암호화)이 필요하다.
Azahar 를 쓰면 %APPDATA%\\Azahar\\sysdata\\ 에 있으므로 자동으로 그 경로를 쓴다.
다른 곳에 있으면 환경 변수 BOOT9_PATH, SEEDDB_PATH 로 지정한다.
"""
import sys, os
TID = 0x0004000000164A00
NEED = 'data/Region_JP'   # 폰트·텍스트·그림 글씨가 전부 여기 있다
OUT = 'extract/jp/romfs'

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


def main():
    cia = sys.argv[1]; top = '/' if '--all' in sys.argv else '/' + NEED
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
    print('%d개 파일 → %s' % (n, OUT))


if __name__ == '__main__':
    main()
