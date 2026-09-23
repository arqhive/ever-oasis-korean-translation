# -*- coding: utf-8 -*-
"""배포 ZIP 만들기. 먼저 python tools/build_all.py 로 release/luma 를 채운다.

  python tools/make_release.py v0.1

release/EverOasis_KO_<버전>.zip 에 다음을 담는다.
  luma/titles/0004000000164A00/locale.txt, romfs/...  (SD 카드 루트에 푸는 LayeredFS 패치)
  README_한국어.txt, LICENSE.txt
그리고 README 확인값 표에 쓰는 main.gmsg·main.gzf 의 원본·패치 확인값을 출력한다.
"""
import sys, os, zipfile, hashlib, zlib

TID = '0004000000164A00'
LUMA = os.path.join('release', 'luma')
KEY = ['data/Region_JP/Japanese/main.gmsg', 'data/Region_JP/main.gzf']


def sums(p):
    d = open(p, 'rb').read()
    return [f'{len(d):,} 바이트', '`%08X`' % (zlib.crc32(d) & 0xFFFFFFFF),
            '`%s`' % hashlib.md5(d).hexdigest(), '`%s`' % hashlib.sha1(d).hexdigest()]


def main():
    ver = sys.argv[1]
    base = os.path.join(LUMA, 'titles', TID)
    if not os.path.exists(os.path.join(base, 'locale.txt')):
        sys.exit('release/luma 가 비어 있습니다. 먼저 python tools/build_all.py 를 실행하세요.')
    dst = os.path.join('release', 'EverOasis_KO_%s.zip' % ver)
    n = 0
    with zipfile.ZipFile(dst, 'w', zipfile.ZIP_DEFLATED) as z:
        for root, _, files in os.walk(LUMA):
            for f in sorted(files):
                p = os.path.join(root, f)
                z.write(p, os.path.relpath(p, 'release').replace(os.sep, '/')); n += 1
        z.write(os.path.join('release', 'README_한국어.txt'), 'README_한국어.txt')
        z.write('LICENSE', 'LICENSE.txt')
    print('%s: 패치 파일 %d개 (%d바이트)' % (dst, n, os.path.getsize(dst)))
    rows = ['크기', 'CRC32', 'MD5', 'SHA-1']
    for k in KEY:
        a = sums(os.path.join('extract', 'jp', 'romfs', k)); b = sums(os.path.join(base, 'romfs', k))
        print('\n' + k)
        for r, x, y in zip(rows, a, b): print('| %s | %s | %s |' % (r, x, y))


if __name__ == '__main__':
    main()
