# 에버 오아시스 (3DS) 한글 패치

*Ever Oasis* (닌텐도 3DS, 일본판 `CTR-P-BAGJ` / `0004000000164A00`) 비공식 한국어 팬 패치입니다.
대사는 일본어판 원문을 기준으로 번역했습니다.

**제작: arqhive** · **최신 버전: [v0.1](../../releases/tag/v0.1)**

- 게임 안 문구 8,503개를 모두 번역했습니다(대사, 의뢰, 메뉴, 아이템·특기 설명, 도움말, 할 일·동료 기록, 크레디트).
- 본문 폰트의 한자·가나 칸을 비워 한글 1,774자를 넣었습니다(Gothic A1 Bold 기반, 원본과 같은 테두리).
- 지역·던전 이름 17종, 레벨 업·랭크·클리어 등 팝 글씨, 타이틀 로고까지 그림 글씨 26종을 한글화했습니다.
- 주인공의 성별에 따라 형/오빠, 누나/언니처럼 호칭이 바뀌도록 했습니다.
- HOME 메뉴 배너와 게임 이름도 한글화했습니다. 이 부분은 CIA를 직접 다시 만들 때만 적용됩니다.
- 배포본은 romfs 파일 23개를 덮어씌우는 LayeredFS 패치입니다.

> 이 저장소에는 **게임 데이터(롬·디스크 이미지, 추출한 원문 대사, 그래픽, 스크린샷)가 들어 있지 않습니다.**
> 패치를 만들거나 적용하려면 본인이 소유한 게임에서 직접 덤프한 원본이 필요합니다.

## 사용자용: 패치 적용

### 준비물

- 일본판 소프트(타이틀 ID `0004000000164A00`). 북미판·유럽판(`00040000001A4800` 등)에는 적용할 수 없습니다.
- 3DS 실기에서는 게임 패치(LayeredFS)를 켠 Luma3DS, 에뮬레이터에서는 Azahar.

### 적용 방법

1. [배포 페이지](../../releases/latest)에서 `EverOasis_KO_v0.1.zip`을 받습니다.
2. 3DS 실기: ZIP 안의 `luma` 폴더를 SD 카드 루트에 복사합니다. 다음과 같이 파일이 놓입니다.

   ```
   sd:/luma/titles/0004000000164A00/locale.txt
   sd:/luma/titles/0004000000164A00/romfs/data/Region_JP/...
   ```

   Luma3DS 설정(본체를 켤 때 SELECT)에서 **Enable game patching**을 켜고 게임을 실행합니다.
3. Azahar: 게임을 오른쪽 클릭해 **Open Mods Location**을 열고, ZIP 안의 `luma/titles/0004000000164A00/romfs` 폴더를 그곳에 복사합니다.
4. 바뀐 파일의 확인값을 아래 표와 비교합니다.

`locale.txt`(내용 `JPN JP`)는 빼지 않습니다. 한국판·북미판처럼 일본판이 아닌 본체에서도 게임을 일본 지역으로 실행하게 합니다.
예전에 다른 패치를 넣은 적이 있다면 `sd:/luma/titles/0004000000164A00/` 폴더를 지우고 새로 복사합니다.

HOME 메뉴의 제목과 배너까지 한글로 바꾸려면 본인이 가진 일본판 CIA로 한글판 CIA를 직접 만듭니다.

```bash
python tools/build_banner.py
python tools/build_cia.py --cia "일본판.cia" --out "한글판.cia"
```

이 CIA는 배너와 아이콘만 바꾸고 romfs는 원본 그대로 둡니다. 게임 안 한글은 위의 LayeredFS 패치로 입힙니다.
`3dstool`, `makerom`(`tools/bin`에 두거나 `--tools`로 지정)과 복호화용 `boot9.bin`, `seeddb.bin`이 필요합니다.

자세한 방법은 [`README_한국어.txt`](release/README_한국어.txt)를 참고하세요.

### 파일 확인값

LayeredFS 패치라 롬 전체가 아니라 바뀌는 파일을 비교합니다. 23개 중 대사와 폰트 두 파일의 값입니다.

| 항목 | 원본 `main.gmsg` | 원본 `main.gzf` | 패치 `main.gmsg` (v0.1) | 패치 `main.gzf` (v0.1) |
|---|---|---|---|---|
| 크기 | 1,241,448 바이트 | 547,968 바이트 | 854,892 바이트 | 552,576 바이트 |
| CRC32 | `AFAA4A68` | `D389459D` | `CB6E5F04` | `B73A55EB` |
| MD5 | `14ef7cc7b25fd82a9a74507c01fe2504` | `0dc228499d87941431844c5bc0a9a3bb` | `2be686174c999e3341f4a2f1e45a964c` | `cbf4273cecba2102fd5354ff67853529` |
| SHA-1 | `1c6983e549ea10997cfd1fb4cde6cc819b59a3b5` | `ad67fdb8ce6137356037520b5c5d43a006114cdd` | `271d933066b0dd75083aa44693baabe4ba213a9a` | `3b7ead602c01626fe8cdc1ba0119e850e1579969` |

원본 파일 위치: 일본판 romfs의 `data/Region_JP/Japanese/main.gmsg`, `data/Region_JP/main.gzf`.

### 실행 환경

- **확인함**: Azahar.

### 알려진 문제

- LayeredFS로는 HOME 메뉴의 제목과 배너가 바뀌지 않습니다. 3DS가 설치된 타이틀의 메타데이터에서 읽기 때문이며, 한글판 CIA를 직접 만들면 바뀝니다.
- 주인공 이름 입력에서 한글을 쓸 수 있는지는 확인하지 않았습니다.

## 개발자용: 직접 빌드

### 요구 사항

- Python 3.10 이상과 [`requirements.txt`](requirements.txt)의 패키지(pyctr, Pillow, NumPy, etcpak).
- 일본판 CIA와 복호화용 `boot9.bin`, `seeddb.bin`. Azahar를 쓰면 `%APPDATA%\Azahar\sysdata\`에 있는 파일을 자동으로 씁니다.
- CIA 재빌드에는 `3dstool`, `makerom`이 추가로 필요합니다.
- 폰트: [Gothic A1](https://fonts.google.com/specimen/Gothic+A1) Bold → `tools/fonts/GothicA1-Bold.ttf`, [Jua](https://fonts.google.com/specimen/Jua) → `tools/fonts/Jua.ttf`, [나눔스퀘어라운드](https://hangeul.naver.com/font) ExtraBold → `tools/fonts/nsr/NanumSquareRoundEB.ttf`, Noto Serif KR → `C:\Windows\Fonts\NotoSerifKR-VF.ttf`.

### 빌드

```bash
python tools/extract.py "일본판.cia"    # extract/jp/romfs 에 원본 추출
python tools/text_io.py extract         # work/text/messages.json 생성 (번역은 translation/ko.json 에서 채움)
python tools/build_all.py               # 폰트·텍스트·그림 글씨 빌드 → release/luma, Azahar 모드 폴더
python tools/make_release.py v0.1       # release/EverOasis_KO_v0.1.zip
python tools/build_banner.py            # HOME 메뉴 배너·아이콘 → work/exefs/banner.bin, icon.bin
python tools/build_cia.py --cia "일본판.cia" --out "한글판.cia"   # 배너·아이콘만 바꾼 CIA
```

같은 원본과 폰트로 빌드하면 배포본과 바이트 단위로 같은 파일이 나옵니다.
`build_cia.py`는 pyctr로 콘텐츠를 복호화(seed 포함)한 뒤 ExeFS의 배너·아이콘만 바꾸고, 3dstool로 CXI를 다시 싸서 makerom으로 CIA를 묶습니다. 한국판 본체의 HOME 메뉴는 배너의 한국 칸을 읽으므로 일본·한국 칸을 모두 바꾸고, 제목은 12개 언어 칸 모두 한국어로 씁니다.

### 번역 수정

- 번역 원본은 [`translation/ko.json`](translation/ko.json)입니다. 키는 메시지 ID, 값은 제어 코드를 포함한 번역문입니다. `build_all.py`가 빌드할 때마다 `messages.json`의 번역을 이 파일에 다시 씁니다.
- 번역은 구간별 묶음 [`translation/batches/`](translation/batches)로 만들었습니다. `python tools/apply_batch.py <이름>`이 태그·줄 폭을 검사해 반영하고, `python tools/fix_terms.py "A=B"`가 모든 묶음의 표기를 한꺼번에 바꿉니다.
- `python tools/lint.py`가 고유명사 표기, 폰트에 없는 글자, 문장 끝 부호, 직역투를 검사합니다.
- 용어와 인명은 [`translation/GLOSSARY.md`](translation/GLOSSARY.md), [`translation/NAMES.md`](translation/NAMES.md), [`translation/terms.json`](translation/terms.json)을 따릅니다. 문체 규칙은 [`docs/STYLE_GUIDE.md`](docs/STYLE_GUIDE.md)에 있습니다.

### 폴더 구조

```
release/       사용자 설명서 (빌드하면 luma/ 와 배포 ZIP 이 생김)
translation/   번역 원본(ko.json), 구간별 묶음(batches/), 화자 정보(speakers/), 용어집·인명표
tools/         추출, GMSG·GZFX·GAR·ctxb 읽기·쓰기, 폰트·그림 글씨 빌드, 번역 검사, 배포 도구
docs/          기술 문서, 문체 규칙, QA 체크리스트, 릴리즈 노트 사본(docs/releases/)
```

### 기술 문서

GMSG·GZFX·GAR·ctxb·배너(CBMD) 형식과 패치 방식은 [`docs/TECHNICAL.md`](docs/TECHNICAL.md)에 정리했습니다.

## 변경 내역

전체 내역은 [`CHANGELOG.md`](CHANGELOG.md)에 있습니다.

## 크레딧·라이선스

- 이 저장소의 도구 코드, 한국어 번역문, 문서: [MIT License](LICENSE) (© 2026 arqhive).
- 본문 한글 글리프는 [Gothic A1](https://fonts.google.com/specimen/Gothic+A1)(SIL Open Font License 1.1)로 그렸습니다.
- 그림 글씨는 [나눔스퀘어라운드](https://hangeul.naver.com/font)(SIL Open Font License 1.1), [Jua](https://fonts.google.com/specimen/Jua)(SIL Open Font License 1.1), [Noto Serif KR](https://fonts.google.com/noto/specimen/Noto+Serif+KR)(SIL Open Font License 1.1)로 그렸습니다.

## 면책

비공식 팬 번역이며 Nintendo와 관련이 없습니다. 「에버 오아시스」 관련 상표·저작권은 Nintendo에 있습니다.
패치를 적용한 게임 파일의 배포를 금지합니다.
