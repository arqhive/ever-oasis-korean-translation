# 에버 오아시스 (3DS) 한글 패치

*Ever Oasis* (닌텐도 3DS, 일본판 `CTR-P-BAGJ` / `0004000000164A00`) 비공식 한국어 팬 패치입니다.
대사는 일본어판 원문을 기준으로 번역했습니다.

**제작: arqhive** · **최신 버전: [v0.4](../../releases/tag/v0.4)**

- 게임 내 문구 8,503개를 모두 번역했습니다(대사, 의뢰, 메뉴, 아이템·특기 설명, 도움말, 할 일·동료 기록, 크레디트).
- 본문 폰트의 한자·가나 칸을 비워 한글 1,774자를 넣었습니다(Gothic A1 Bold 기반, 원본과 같은 테두리).
- 지역·던전 이름 17종, 레벨 업·랭크·클리어 등 팝 글씨, 타이틀 로고까지 그림 글씨 79장을 한글로 새로 그렸습니다.
- 주인공의 성별에 따라 형/오빠, 누나/언니처럼 호칭이 바뀌도록 했습니다.
- HOME 메뉴 배너와 게임 이름도 한글화했습니다. 이 부분은 패처로 만든 한글판 CIA를 설치할 때 적용됩니다.
- 배포본은 romfs 파일 57개를 덮어씌우는 LayeredFS 패치와, 일본판 CIA 또는 3DS 파일을 한글판으로 바꾸는 패처 두 가지입니다. 둘 중 하나만 쓰면 됩니다.

> 이 저장소에는 **게임 데이터(롬·디스크 이미지, 추출한 원문 대사, 그래픽, 스크린샷)가 들어 있지 않습니다.**
> 패치를 만들거나 적용하려면 본인이 소유한 게임에서 직접 덤프한 원본이 필요합니다.

## 사용자용: 패치 적용

### 준비물

- 일본판 소프트(타이틀 ID `0004000000164A00`). 북미판·유럽판(`00040000001A4800` 등)에는 적용할 수 없습니다.
- 3DS 실기에서는 Luma3DS, 에뮬레이터에서는 Azahar.
- 방법마다 필요한 것은 아래 비교표를 참고하세요.

### 적용 방법

게임 내 한글은 두 방법이 같습니다. [배포 페이지](../../releases/latest)에서 **둘 중 하나만** 골라 받으면 됩니다.

| | 방법 A. LayeredFS | 방법 B. 패처로 한글판 CIA·3DS 만들기 |
|---|---|---|
| 받는 파일 | `EverOasis_KO_v0.4_LayeredFS.zip` | `EverOasis_KO_v0.4_Patcher.zip` |
| 게임 내 한글 | 적용 | 적용 |
| HOME 메뉴 게임 이름·배너 | 일본어 그대로 | 한글 |
| 필요한 것 | 이미 설치된 일본판, Luma3DS 게임 패치 설정 | 일본판 파일 하나(3DS 실기 설치용이면 `.cia`, 에뮬레이터·플래시카트용이면 `.3ds`), 윈도우 PC, 암호화된 원본이면 `boot9.bin`·`seeddb.bin` |
| 걸리는 시간 | 파일 복사 몇 초 | 패치 약 30초 + CIA 설치 |
| 되돌리기 | SD 카드의 폴더만 지우면 원래대로 | 원본 CIA를 다시 설치 |
| 에뮬레이터 | Azahar 모드 폴더에 복사 | 만든 3DS·CIA를 바로 실행 |

설치된 게임을 그대로 두고 간단히 쓰려면 A, HOME 메뉴까지 한글로 보고 싶거나 에뮬레이터용 한글판 파일이 필요하면 B를 고르세요.

#### 방법 A. LayeredFS

1. 3DS 실기: ZIP 안의 `luma` 폴더를 SD 카드 루트에 복사합니다. 파일은 `sd:/luma/titles/0004000000164A00/romfs/data/Region_JP/...`에 놓입니다.
   Luma3DS 설정(본체를 켤 때 SELECT)에서 **Enable game patching**을 켜고 게임을 실행합니다.
2. Azahar: 게임을 오른쪽 클릭해 **Open Mods Location**을 열고, ZIP 안의 `luma/titles/0004000000164A00/romfs` 폴더를 그곳에 복사합니다.

예전에 다른 패치를 넣은 적이 있다면 `sd:/luma/titles/0004000000164A00/` 폴더를 지우고 새로 복사합니다.

#### 방법 B. 패처로 한글판 CIA·3DS 만들기

1. 쓰려는 곳에 맞는 일본판 파일 하나를 준비합니다. 3DS 실기에 설치하려면 `.cia`, 에뮬레이터나 플래시카트에서 쓰려면 `.3ds`입니다. 결과는 넣은 파일과 같은 형식으로 나옵니다.
2. ZIP을 폴더째 풀고, 준비한 파일을 `패치하기.bat`에 끌어다 놓습니다.
3. 원본과 같은 폴더에 `원래 이름_KO.cia` 또는 `원래 이름_KO.3ds`가 생깁니다. 원본 파일은 바뀌지 않습니다.
4. 3DS 실기에는 만든 CIA를 설치합니다. 이미 설치된 일본판에 덮어 설치해도 세이브는 유지됩니다. 3DS 파일은 복호화된 상태라 에뮬레이터·플래시카트용입니다.

패처는 원본을 풀어 게임 내 한글 파일 23개와 HOME 메뉴 배너·게임 이름을 바꾼 뒤 다시 묶습니다. 넣은 파일이 일본판 본편인지, 바꿀 파일이 원본 그대로인지 먼저 확인합니다. 파이썬이 함께 들어 있어 따로 설치할 것은 없습니다.
이 방법으로 설치했다면 방법 A의 LayeredFS 폴더는 필요 없습니다. 둘을 함께 넣어도 같은 파일이라 문제는 없습니다.

자세한 방법은 [`README_한국어.txt`](release/README_한국어.txt)를 참고하세요.

### 실행 환경

- **확인함**: 3DS + Luma3DS(LayeredFS), 3DS(패처로 만든 CIA 설치), Azahar.

### 알려진 문제

- LayeredFS로는 HOME 메뉴의 제목과 배너가 바뀌지 않습니다. 3DS가 설치된 타이틀의 메타데이터에서 읽기 때문이며, 패처로 만든 CIA를 설치하면 바뀝니다.
- 주인공 이름 입력에서 한글을 쓸 수 있는지는 확인하지 않았습니다.

## 개발자용: 직접 빌드

### 요구 사항

- Python 3.10 이상과 [`requirements.txt`](requirements.txt)의 패키지(pyctr, Pillow, NumPy, etcpak).
- 일본판 CIA와 복호화용 `boot9.bin`, `seeddb.bin`. Azahar를 쓰면 `%APPDATA%\Azahar\sysdata\`에 있는 파일을 자동으로 씁니다.
- CIA·3DS 재빌드에는 `3dstool`, `makerom`(`tools/bin`)이 추가로 필요합니다.
- 폰트: [Gothic A1](https://fonts.google.com/specimen/Gothic+A1) Bold → `tools/fonts/GothicA1-Bold.ttf`, [Jua](https://fonts.google.com/specimen/Jua) → `tools/fonts/Jua.ttf`, [나눔스퀘어라운드](https://hangeul.naver.com/font) ExtraBold → `tools/fonts/nsr/NanumSquareRoundEB.ttf`, Noto Serif KR → `C:\Windows\Fonts\NotoSerifKR-VF.ttf`.

### 빌드

```bash
python tools/extract.py "일본판.cia"    # extract/jp 에 원본 romfs·배너·아이콘 추출
python tools/extract.py "일본판.cia" --cxi   # Azahar 테스트용 CXI (한글은 build_all 이 채우는 모드 폴더로 덮임)
python tools/text_io.py extract         # work/text/messages.json 생성 (번역은 translation/ko.json 에서 채움)
python tools/build_all.py               # 폰트·텍스트·그림 글씨 빌드 → release/luma, Azahar 모드 폴더
python tools/build_banner.py            # HOME 메뉴 배너 제목 그림 → work/exefs
python tools/build_cia.py --cia "일본판.cia" --out "한글판.cia"   # 전부 들어간 CIA (.3ds 도 가능)
python tools/make_patcher.py v0.4 --python <임베디드 파이썬 zip 또는 폴더>   # release/patcher·python 채우기
python tools/make_release.py v0.4       # release/EverOasis_KO_v0.4_LayeredFS.zip, _Patcher.zip
```

같은 원본과 폰트로 빌드하면 배포본과 바이트 단위로 같은 파일이 나옵니다.
CIA·3DS 처리는 `tools/eopatch.py` 한 곳에 있고, `build_cia.py`와 배포 패처(`release/patcher/patch.py`)가 함께 씁니다. pyctr로 콘텐츠를 복호화(seed 포함)한 뒤 ExeFS의 배너·아이콘과 romfs 파일을 바꾸고, 3dstool로 CXI를 다시 싸서 makerom으로 CIA나 3DS를 묶습니다. 한국판 본체의 HOME 메뉴는 배너의 한국 칸을 읽으므로 일본·한국 칸을 모두 바꾸고, 제목은 12개 언어 칸 모두 한국어로 씁니다.

### 번역 수정

- 번역 원본은 [`translation/ko.json`](translation/ko.json)입니다. 키는 메시지 ID, 값은 제어 코드를 포함한 번역문입니다. `build_all.py`가 빌드할 때마다 `messages.json`의 번역을 이 파일에 다시 씁니다.
- 번역은 구간별 묶음 [`translation/batches/`](translation/batches)로 만들었습니다. `python tools/apply_batch.py <이름>`이 태그·줄 폭을 검사해 반영하고, `python tools/fix_terms.py "A=B"`가 모든 묶음의 표기를 한꺼번에 바꿉니다.
- `python tools/lint.py`가 고유명사 표기, 폰트에 없는 글자, 문장 끝 부호, 직역투를 검사합니다.
- 용어와 인명은 [`translation/GLOSSARY.md`](translation/GLOSSARY.md), [`translation/NAMES.md`](translation/NAMES.md), [`translation/terms.json`](translation/terms.json)을 따릅니다. 문체 규칙은 [`docs/STYLE_GUIDE.md`](docs/STYLE_GUIDE.md)에 있습니다.

### 폴더 구조

```
release/       사용자 설명서, 패처(패치하기.bat, patcher/patch.py). 빌드하면 luma/, python/, 배포 ZIP 이 생김
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
- 그림 글씨(지역·던전 이름, 팝 글씨, 타이틀, 배너)는 원본 디자인을 따라 새로 그렸습니다. 폰트로 그리는 예전 방식은 `tools/` 안에 남아 있으며 [나눔스퀘어라운드](https://hangeul.naver.com/font), [Jua](https://fonts.google.com/specimen/Jua), [Noto Serif KR](https://fonts.google.com/noto/specimen/Noto+Serif+KR)(모두 SIL Open Font License 1.1)를 씁니다.

## 면책

비공식 팬 번역이며 Nintendo와 관련이 없습니다. 「에버 오아시스」 관련 상표·저작권은 Nintendo에 있습니다.
패치를 적용한 게임 파일의 배포를 금지합니다.
