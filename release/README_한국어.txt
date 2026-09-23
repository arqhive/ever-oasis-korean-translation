에버 오아시스 (3DS) 한글 패치 v0.1
제작: arqhive

「에버 오아시스 정령과 씨앗족의 신기루」(닌텐도 3DS, 일본판) 비공식 한국어 팬 패치입니다.
게임 파일을 바꾸지 않고, Luma3DS의 게임 패치(LayeredFS) 기능이나 에뮬레이터의 모드 폴더로 덮어씌웁니다.


[준비물]

- 일본판 「エバーオアシス 精霊とタネビトの蜃気楼」(타이틀 ID 0004000000164A00).
  북미판·유럽판(Ever Oasis)에는 적용할 수 없습니다.
- 3DS 실기: Luma3DS가 설치된 본체와 SD 카드.
- 에뮬레이터: Azahar.


[3DS 실기 (Luma3DS) 적용 방법]

1. EverOasis_KO_v0.1.zip 안의 luma 폴더를 SD 카드 루트에 그대로 복사합니다.
   다음과 같이 파일이 놓이면 됩니다.

     sd:/luma/titles/0004000000164A00/locale.txt
     sd:/luma/titles/0004000000164A00/romfs/data/Region_JP/...

2. 본체를 켤 때 SELECT를 누른 채로 두면 Luma3DS 설정 화면이 나옵니다.
   "Enable game patching"을 켜고 저장합니다.
3. 게임을 실행합니다.

- locale.txt(내용 "JPN JP")는 빼지 마세요. 한국판·북미판처럼 일본판이 아닌 본체에서
  게임을 일본 지역·일본어로 실행하게 합니다.
- 예전에 다른 패치를 넣은 적이 있다면 sd:/luma/titles/0004000000164A00/ 폴더를 지운 뒤 새로 복사하세요.
  옛 파일과 섞이면 글자가 나오지 않거나 게임이 멈출 수 있습니다.


[Azahar 적용 방법]

1. 게임 목록에서 에버 오아시스를 오른쪽 클릭하고 "Open Mods Location"을 누릅니다.
2. 열린 폴더(…/load/mods/0004000000164A00/)에 ZIP 안의
   luma/titles/0004000000164A00/romfs 폴더를 통째로 복사합니다.

     …/load/mods/0004000000164A00/romfs/data/Region_JP/...

3. 게임을 실행합니다.


[바뀌는 파일 확인값]

대사 파일 romfs/data/Region_JP/Japanese/main.gmsg

  원본      크기 1,241,448 바이트, MD5 14ef7cc7b25fd82a9a74507c01fe2504
  패치 후   크기   854,892 바이트, MD5 2be686174c999e3341f4a2f1e45a964c


[알려진 문제]

- HOME 메뉴의 게임 제목과 배너는 일본어로 나옵니다. LayeredFS로는 바꿀 수 없습니다.
- 주인공 이름 입력에서 한글을 쓸 수 있는지는 확인하지 않았습니다.


[면책]

비공식 팬 번역이며 Nintendo, Grezzo와 관련이 없습니다.
「에버 오아시스」 관련 상표·저작권은 Nintendo에 있습니다.
패치를 적용한 게임 파일의 배포를 금지합니다.
