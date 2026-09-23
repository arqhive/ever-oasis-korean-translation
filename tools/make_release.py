# -*- coding: utf-8 -*-
"""배포 ZIP 두 개 만들기.

  python tools/build_all.py && python tools/build_banner.py
  python tools/make_patcher.py v0.2 [--python <임베디드 파이썬>]      # release/patcher·release/python 채우기
  python tools/make_release.py v0.2

release/EverOasis_KO_<버전>_LayeredFS.zip
  luma/titles/0004000000164A00/romfs/...   SD 카드 루트에 푸는 LayeredFS 패치
  README_한국어.txt, LICENSE.txt
release/EverOasis_KO_<버전>_Patcher.zip
  EverOasis_KO_<버전>_Patcher/패치하기.bat, patcher/, python/   일본판 CIA·3DS 를 한글판으로 만드는 패처
  README_한국어.txt, LICENSE.txt
"""
import sys, os, zipfile

TID = '0004000000164A00'
LUMA = os.path.join('release', 'luma')


def add_tree(z, src, arc):
    n = 0
    for root, dirs, files in os.walk(src):
        dirs[:] = [d for d in dirs if d != '__pycache__']
        for f in sorted(files):
            p = os.path.join(root, f)
            z.write(p, (arc + '/' + os.path.relpath(p, src).replace(os.sep, '/')).lstrip('/')); n += 1
    return n


def main():
    ver = sys.argv[1]
    if not os.path.isdir(os.path.join(LUMA, 'titles', TID, 'romfs')):
        sys.exit('release/luma 가 비어 있습니다. 먼저 python tools/build_all.py 를 실행하세요.')
    if not os.path.isdir(os.path.join('release', 'python')) or not os.path.isdir(os.path.join('release', 'patcher', 'payload')):
        sys.exit('패처가 준비되지 않았습니다. 먼저 python tools/make_patcher.py %s 를 실행하세요.' % ver)
    docs = [(os.path.join('release', 'README_한국어.txt'), 'README_한국어.txt'), ('LICENSE', 'LICENSE.txt')]

    a = os.path.join('release', 'EverOasis_KO_%s_LayeredFS.zip' % ver)
    with zipfile.ZipFile(a, 'w', zipfile.ZIP_DEFLATED) as z:
        n = add_tree(z, LUMA, 'luma')
        for p, name in docs: z.write(p, name)
    print('%s: LayeredFS 파일 %d개 (%s 바이트)' % (a, n, format(os.path.getsize(a), ',')))

    b = os.path.join('release', 'EverOasis_KO_%s_Patcher.zip' % ver)
    top = 'EverOasis_KO_%s_Patcher' % ver
    with zipfile.ZipFile(b, 'w', zipfile.ZIP_DEFLATED) as z:
        z.write(os.path.join('release', '패치하기.bat'), top + '/패치하기.bat')
        n = add_tree(z, os.path.join('release', 'patcher'), top + '/patcher')
        n += add_tree(z, os.path.join('release', 'python'), top + '/python')
        for p, name in docs: z.write(p, top + '/' + name)
    print('%s: 파일 %d개 (%s 바이트)' % (b, n + 3, format(os.path.getsize(b), ',')))


if __name__ == '__main__':
    main()
