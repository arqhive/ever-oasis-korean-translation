# -*- coding: utf-8 -*-
"""일본판 CIA/3DS 로 한글판 CIA/3DS 를 만든다 (개발용). 배포 패처(release/패치하기.bat)와 같은 eopatch 를 쓴다.

  python tools/build_all.py && python tools/build_banner.py     # 한글 romfs 와 배너 제목 그림
  python tools/build_cia.py --cia "일본판.cia" --out "한글판.cia"
  python tools/build_cia.py --cia "일본판.3ds" --out "한글판.3ds"

게임 내 한글(romfs 23개)과 HOME 메뉴 배너·게임 이름이 모두 들어간다. 결과 형식은 --out 확장자로 정한다.
3dstool·makerom 은 tools/bin, 키(boot9.bin·seeddb.bin)는 Azahar sysdata 등에서 찾는다(eopatch.key_dirs).
"""
import argparse, os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
import eopatch, make_patcher


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--cia', required=True, help='일본판 .cia 또는 .3ds')
    ap.add_argument('--out', required=True, help='만들 .cia 또는 .3ds')
    ap.add_argument('--tools', default=os.path.join(HERE, 'bin'))
    ap.add_argument('--work', default=os.path.join(ROOT, 'work', 'cia'))
    ap.add_argument('--keep', action='store_true', help='작업 폴더를 지우지 않는다')
    a = ap.parse_args()
    os.chdir(ROOT)
    payload = os.path.join('work', 'payload')
    n = make_patcher.build_payload(payload, 'dev')
    print('payload: romfs 파일 %d개' % n)
    eopatch.patch(os.path.abspath(a.cia), os.path.abspath(a.out), payload, a.tools, os.path.abspath(a.work), keep=a.keep)
    print('완료: %s (%s 바이트)' % (a.out, format(os.path.getsize(a.out), ',')))


if __name__ == '__main__':
    main()
