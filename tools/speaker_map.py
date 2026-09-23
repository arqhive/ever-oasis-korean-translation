# -*- coding: utf-8 -*-
"""스크립트 화자 핸들 → 인물 이름(한국어). 핸들 이름만 보고 짐작하지 않고 실제 대사 내용으로 확인한 것만 적는다.
None = 누구인지 특정할 수 없는 일반 핸들(대상 NPC, 액터 배열 등)."""
H = {}
def put(names, who):
    for n in names.split(): H[n] = who
put('h_spirit h_spirit_talk h_talk_spirit h_spirit_talk_1 h_spirit_talk_2 h_spirit_talk_3 h_spirit_talk_4 h_isuna_talk h_scarab_and_isuna', '이스나')
put('h_osa_talk h_osa osa', '니아카')                 # 프롤로그의 촌장(주인공의 형/오빠) — DemoSet_C1·Event_dounyu 에서만 쓰임
put('h_manager_talk h_manager', '사후라')
put('h_miu_talk h_miu', '미우')
put('h_tuefa_talk h_tuefa', '체파')
put('h_salurmu_talk', '살람')                         # 「ボクは　サラーム。リコス族の　サラームさ～」
put('h_ain_talk', '사루루')                           # 간사이 사투리 「にいちゃんおじょうちゃん」
put('h_ebio_talk', '에비오')
put('h_vendor_talk h_vendor', '행상인')
put('h_lebi_talk h_lebi', '레비')
put('h_worker_talk h_worker', '세르케 작업원')
put('h_maraia_talk h_mara_talk', '마라이아')
put('h_syuto_talk h_syuto', '슈토')
put('h_arunevit_talk h_rikos_talk', '아르네베트')     # h_rikos_talk 도 「この　アルネヴェト様が」
put('h_loht_talk h_loht h_roto_talk', '로토')
put('h_etha_talk h_etha', '이사')                     # 말 더듬기 「そそそその…　エ　エンバ…」
put('h_toth_talk', '대현자 토스')
put('h_gadd_talk', '가도')
put('h_kaarotha_talk h_kaarotha h_kaaro_talk h_karo_talk', '카로타')
put('h_shallara_talk', '샤라라')
put('h_oldman_ua_talk', '우아족 장로')
put('h_ceruke_talk', '세르케족 장로')
put('h_oldman_rikos_talk', '리코스족 장로')
put('h_pami_talk h_pami', '파미')
put('h_saro_talk', '살로메')
put('h_bel_talk h_bell_talk', '벨초니')
put('h_zyasu_talk', '재스퍼')
put('h_jamirefu_talk', '자미레프')
put('h_holu_talk h_hol_talk', '호루아하')
put('h_nine_talk', '니네체르')
put('h_sai_talk', '사이이드')                         # 「その声は…　親父！？」
put('h_sahi_talk', '사이라스')                        # 「…ルツ…　だいじょうぶか」
put('h_ank_talk', '아노크사베')
put('h_hos_talk', '호스니')
put('h_hana_talk', '하노크')                          # 「ホルアハ！　言ってくれるじゃねぇか！」
put('h_naa_talk', '나아마')
put('h_saikinna_talk h_seki_talk', '세키나')
put('h_ririsya_talk h_ririsya_talk_2 h_ririsya', '리리샤')
put('h_den_talk h_daen_talk', '덴')
put('h_pote_talk', '포테파르')
put('h_rut_talk', '루츠')
put('h_mol_talk', '모르테바')
put('h_sess_talk h_cess_talk h_cessien_talk', '세셴')
put('h_waf_talk', '와파')
put('h_hua_talk', '파라프')                           # 「あら　ワファーじゃない」
put('h_mag_talk', '마그달레나')
put('h_aziza_talk', '아지자')
put('h_nubi_talk h_nubb_talk', '누비토')
put('h_sebi_talk', '세비티')
put('h_riko_talk', '정보상')
put('h_rara_talk', '라라크')
put('h_teppo_talk', '텟포')
put('h_jaruje_talk', '자르제')
put('h_em_talk', '엠셰레')
put('h_men_talk', '메누우')
put('h_player_talk', '주인공')
GENERIC = {'htarget', 'htarget_', 'h_talk_target', 'h_talk_actors', 'chara_id', 'item_id', 'h_tane_talk',
           'h_ua_talk', 'h_ua', 'h_ser_talk', 'h_gyou_talk', 'h_gyosho_talk', 'h_aya_talk', 'h_jona_talk',
           'h_cya_talk', 'h_mau_talk', 'h_mana_talk', 'h_kal_talk', 'h_tahe_talk', 'h_cha_talk', 'h_mae_talk',
           'h_rico_talk', 'h_isu_talk', 'h_chr', 'h_opePlayer', 'h_sha_talk', 'h_eseherc_talk'}
