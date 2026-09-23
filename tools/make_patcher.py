# -*- coding: utf-8 -*-
"""CIA·3DS 패처 꾸리기 → release/patcher (payload·lib·bin) + release/python(임베디드 파이썬)

  python tools/build_all.py && python tools/build_banner.py   # 먼저 한글 romfs 와 배너 제목 그림을 만든다
  python tools/make_patcher.py v0.2 [--python <임베디드 파이썬 zip 또는 폴더>]

payload 에는 한글 romfs 파일, 배너 제목 그림(logo_rgba4.bin), 게임 이름, 원본 파일 MD5 만 담는다.
배너·아이콘은 사용자 파일 안의 것을 고쳐 쓰므로 원본 게임 데이터는 들어가지 않는다.
lib 에는 eopatch·lz11 과 pyctr·pycryptodomex(설치된 것 복사), bin 에는 3dstool·makerom 을 넣는다.
"""
import sys, os, json, shutil, hashlib, zipfile
sys.path.insert(0, os.path.dirname(__file__))
import build_banner

TID = '0004000000164A00'
LUMA_ROMFS = os.path.join('release', 'luma', 'titles', TID, 'romfs')
ORIG_ROMFS = os.path.join('extract', 'jp', 'romfs')
PATCHER = os.path.join('release', 'patcher')


def build_payload(dst, version):
    if os.path.exists(dst): shutil.rmtree(dst)
    shutil.copytree(LUMA_ROMFS, os.path.join(dst, 'romfs'))
    src_md5 = {}
    for root, _, files in os.walk(LUMA_ROMFS):
        for f in files:
            rel = os.path.relpath(os.path.join(root, f), LUMA_ROMFS).replace(os.sep, '/')
            src_md5[rel] = hashlib.md5(open(os.path.join(ORIG_ROMFS, rel), 'rb').read()).hexdigest()
    shutil.copyfile(os.path.join('work', 'exefs', 'logo_rgba4.bin'), os.path.join(dst, 'logo_rgba4.bin'))
    json.dump({'short': build_banner.SHORT, 'long': build_banner.LONG},
              open(os.path.join(dst, 'titles.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    json.dump({'version': version, 'title_id': TID, 'source_md5': src_md5},
              open(os.path.join(dst, 'manifest.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    return len(src_md5)


def main():
    ver = sys.argv[1]
    py = sys.argv[sys.argv.index('--python') + 1] if '--python' in sys.argv else None
    n = build_payload(os.path.join(PATCHER, 'payload'), ver)
    lib = os.path.join(PATCHER, 'lib'); os.makedirs(lib, exist_ok=True)
    for f in ('eopatch.py', 'lz11.py'):
        shutil.copyfile(os.path.join('tools', f), os.path.join(lib, f))
    import pyctr, Cryptodome
    for m in (pyctr, Cryptodome):
        d = os.path.join(lib, m.__name__)
        if os.path.exists(d): shutil.rmtree(d)
        shutil.copytree(os.path.dirname(m.__file__), d, ignore=shutil.ignore_patterns('__pycache__', '*.pyi', 'SelfTest'))
    b = os.path.join(PATCHER, 'bin'); os.makedirs(b, exist_ok=True)
    for f in ('3dstool.exe', 'makerom.exe'):
        shutil.copyfile(os.path.join('tools', 'bin', f), os.path.join(b, f))
    if py:
        dst = os.path.join('release', 'python')
        if os.path.exists(dst): shutil.rmtree(dst)
        if os.path.isdir(py): shutil.copytree(py, dst)
        else:
            with zipfile.ZipFile(py) as z:
                for i in z.infolist():
                    if i.is_dir(): continue
                    parts = i.filename.replace('\\', '/').split('/')
                    if 'python' not in parts[:-1]: continue      # 다른 배포 ZIP 에서 python/ 폴더만 꺼낸다
                    rel = parts[parts.index('python') + 1:]
                    out = os.path.join(dst, *rel); os.makedirs(os.path.dirname(out), exist_ok=True)
                    open(out, 'wb').write(z.read(i))
    print('패처 준비 완료: payload 파일 %d개, lib·bin → %s%s' % (n, PATCHER, ', 파이썬 → release/python' if py else ''))


if __name__ == '__main__':
    main()
