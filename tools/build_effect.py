# -*- coding: utf-8 -*-
"""연출 글씨(3D 모델 CMB 안의 텍스처)를 한글로 바꾼다.

모델은 글자 하나를 사각형 판 하나에 띄운다. 판마다 텍스처의 한 칸(UV 영역)을 읽고,
판의 크기·위치는 일본어 글자에 맞춰져 있다(작은 ッ·ー 자리는 판이 작고 촘촘하다).
그래서 텍스처만 바꾸면 한글 글자 크기와 간격이 들쭉날쭉해진다.

여기서는 텍스처와 판 정점을 함께 고친다.
  1. 글자를 판의 UV 영역에 꽉 차게(FILL) 그린다.
  2. 판 정점을 다시 계산해, 모든 글자가 같은 높이 H 로 보이게 한다(텍셀당 길이 = H / 글자 텍셀 높이).
  3. 위치: 'line' 은 한 줄에 같은 간격으로 늘어놓는다(판이 모두 한 평면에 있는 모델).
     'nudge' 는 판 자리는 그대로 두고 실기 사진에서 잰 만큼만 옮긴다(꽃상점: 글자마다
     본이 따로 있고 애니메이션이 자리를 정해서 화면 위치를 계산으로 알 수 없다).

  python tools/build_effect.py --write   # work/romfs 의 gar 에 써넣는다(build_all 은 바로 쓴다)
  python tools/build_effect.py           # 쓰지 않고 비교 시트·배치 미리보기만 만든다
"""
import sys, os, re, struct
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.stdout.reconfigure(encoding='utf8')
from PIL import Image, ImageDraw, ImageFont
import numpy as np
import ctxb, etc1

SRC = 'extract/jp/romfs/data/Region_JP/Japanese'
DST = 'work/romfs/data/Region_JP/Japanese'
GPT = 'work/GPT_연출글씨/결과'

# 텍스처 칸을 읽는 순서 = 원본 글자 순서. 슬롯 번호는 이 목록의 인덱스다.
A = 'congra_a'; B = 'congra_b'
JOBS = {
    'nakama':   {'gar': 'eff_town',   'tex': {'main': ('eff_nakama_01', 'nakama_text2', 3)},
                 'order': [('main', (0, 0)), ('main', (1, 0)), ('main', (2, 0)), ('main', (0, 1)),
                           ('main', (1, 1)), ('main', (2, 1)), ('main', (0, 2))]},
    'building': {'gar': 'eff_demo01', 'tex': {'main': ('eff_building_01', 'building_text', 3)},
                 'order': [('main', (0, 0)), ('main', (1, 0)), ('main', (2, 0)), ('main', (0, 1)),
                           ('main', (1, 1)), ('main', (2, 1)), ('main', (0, 2)), ('main', (1, 2)),
                           ('main', (2, 2))]},
    'rankup':   {'gar': 'eff_town',   'tex': {'main': ('eff_rankup_01', 'rankup_text', 3)},
                 'order': [('main', (0, 0)), ('main', (1, 0)), ('main', (2, 0)), ('main', (0, 1)),
                           ('main', (1, 1)), ('main', (2, 1)), ('main', (0, 2))]},
    'quest':    {'gar': 'eff_town',   'tex': {'main': ('eff_quest_01', 'quest_text', 3)},
                 'order': [('main', (0, 0)), ('main', (1, 1)), ('main', (2, 0)), ('main', (0, 1)),
                           ('main', (1, 0)), ('main', (2, 1)), ('main', (0, 2)), ('main', (2, 2))]},
    'congra':   {'gar': 'eff_demo02',
                 'tex': {A: ('eff_congra_01', 'congra_text_a', 3),
                         B: ('eff_congra_01', 'congra_text_b', 2)},
                 'order': [(A, (0, 0)), (A, (1, 0)), (A, (2, 0)), (A, (0, 1)), (A, (1, 2)),
                           (A, (2, 1)), (A, (0, 2)), (A, (1, 1)), (B, (0, 0)), (A, (2, 2)),
                           (B, (1, 0))]},
}
# congra 는 판 묶음(sepd) 0 이 congra_text_a, 1 이 congra_text_b 를 쓴다(mshs → mats).
SEPD_TEX = {'congra': {0: A, 1: B}}

# 글자 → 슬롯. 줄마다 [슬롯...] (글자 순서대로). 「!」 는 원본 「！」 의 좁은 칸에 넣는다.
LAYOUT = {
    # 동→ナ 료→マ 획→ッ 득→ゲ !→！ : ゲ 만 앞줄(본 1)이라 뒷줄 평면으로 옮겨 온다.
    'nakama':   {'mode': 'line', 'lines': [[0, 2, 4, 3, 6]]},
    'rankup':   {'mode': 'line', 'lines': [[0, 1, 2, 6]]},
    'quest':    {'mode': 'line', 'lines': [[0, 1, 2, 3, 4, 7]]},
    # 두 줄: 위 オアシス 4칸 = 오아시스, 아래 レベルアップ！ 7칸 중 3칸 + ！ = 레벨업!
    'congra':   {'mode': 'line', 'lines': [[0, 1, 2, 3], [4, 5, 6, 10]]},
    # 꽃상점오픈! → ミセオープン 자리. H 와 옮길 양(로컬 단위, +x 오른쪽 +y 위)은 화면에서 쟀다:
    # 1차(10/9 실기 사진) 글자가 전부 닿고 오(ー 자리)가 0.7 낮음 → 2차(10/9 Azahar 정지 화면, 가로 약 22.6px/단위)
    # 빈틈 12·30·15·1·11px 을 양 끝을 고정하고 14px 로 고르게, 오를 아치 높이로 5px 더 올림.
    # 3차(10/9 Azahar) 상이 꽃·점을 잇는 아치보다 약 7px 높아 0.35 내림.
    'building': {'mode': 'nudge', 'slots': [2, 3, 4, 5, 6, 7], 'H': 3.9,
                 'move': [(-0.52, 0), (-0.15, -0.35), (-0.67, 0), (-0.02, 0.94), (0.97, 0), (0.54, 0)]},
}
FILL = 0.92        # 글자가 UV 영역에서 차지하는 비율(압축 경계에서 잘리지 않게)
SIZE = 0.95        # 한글 높이 = 원본 글자 높이(중앙값) × SIZE
GAP = 0.18         # 글자 사이 빈틈 = 높이 × GAP
SPAN = 1.1         # 줄 폭은 원본 줄 폭의 이 배까지(넘으면 크기를 줄인다)


# ── CMB 읽기 ──────────────────────────────────────────────

def cmbs(d):
    """gar 안의 CMB 들 → {모델이름: (시작, tex섹션, 텍스처데이터시작)}"""
    out = {}
    for m in re.finditer(rb'cmb ', d):
        i = m.start()
        try:
            name = d[i + 0x10:i + 0x20].split(b'\0')[0].decode('latin1')
            offs = struct.unpack_from('<10I', d, i + 0x24)
            tex, texdata = i + offs[3], i + offs[8]
            if d[tex:tex + 4] == b'tex ': out[name] = (i, tex, texdata)
        except Exception:
            pass
    return out


def tex_entry(d, tex, want):
    cnt = struct.unpack_from('<I', d, tex + 8)[0]
    for k in range(cnt):
        o = tex + 12 + k * 0x24
        dl, ml, et, w, h, fmt, off = struct.unpack_from('<IHHHHII', d, o)
        if d[o + 20:o + 36].split(b'\0')[0].decode('latin1') == want:
            return dl, w, h, fmt, off
    raise KeyError(want)


def bones(d, i):
    """skl → 본마다 (부모 번호, 부모 기준 변환 행렬(바인드 자세), z 회전)."""
    skl = i + struct.unpack_from('<10I', d, i + 0x24)[0]
    out = []
    for b in range(struct.unpack_from('<I', d, skl + 8)[0]):
        v = struct.unpack_from('<Hh9f', d, skl + 16 + b * 0x2C)
        sx, sy, sz, rx, ry, rz, tx, ty, tz = v[2:]
        cz, snz = np.cos(rz), np.sin(rz)
        m = np.eye(4)
        m[:3, :3] = np.array([[cz, -snz, 0], [snz, cz, 0], [0, 0, 1]]) @ np.diag([sx, sy, sz])
        m[:3, 3] = (tx, ty, tz)
        out.append((v[1], m, rz))
    return out


def rel(bns, b, ref):
    """본 b 의 로컬 좌표 → 본 ref 의 로컬 좌표 행렬. (ref 는 b 자신이거나 조상)"""
    m = np.eye(4)
    while b != ref:
        par, mb, _ = bns[b]
        m = mb @ m; b = par
        if b < 0: raise ValueError('ref 가 조상이 아님')
    return m


def quads(d, model, texsize, job):
    """모델의 판(사각형)마다 정점 위치·UV·본·텍스처키.

    판 묶음(sepd)마다 UV 배율이 따로 저장돼 있다(+0x94). 정점 4개가 판 하나.
    """
    i = cmbs(d)[model][0]
    size = struct.unpack_from('<I', d, i + 4)[0]
    offs = struct.unpack_from('<10I', d, i + 0x24)
    vatr = i + offs[6]
    psz, poff = struct.unpack_from('<2I', d, vatr + 12)
    usz, uoff = struct.unpack_from('<2I', d, vatr + 12 + 4 * 8)
    seps = [i + m.start() for m in re.finditer(rb'sepd', d[i:i + size])]
    starts = [struct.unpack_from('<I', d, s + 0x24)[0] for s in seps] + [psz]
    out = []
    for n, s in enumerate(seps):
        key = SEPD_TEX.get(job, {}).get(n, 'main')
        S = texsize[key][0]
        pst, psc = struct.unpack_from('<If', d, s + 0x24)
        assert psc == 1.0 and struct.unpack_from('<H', d, s + 0x2c)[0] == 5126   # float32 위치
        ust, usc, utyp = struct.unpack_from('<IfH', d, s + 0x94)
        p = d.find(b'prm ', s)
        bone = struct.unpack_from('<H', d, p - 4)[0]
        nv = (starts[n + 1] - pst) // 12
        base = vatr + poff + pst
        pos = np.frombuffer(bytes(d[base:base + nv * 12]), dtype='<f4').reshape(-1, 3).astype(float)
        dt = '<i2' if utyp == 5122 else '<u2'
        uv = np.frombuffer(bytes(d[vatr + uoff + ust:vatr + uoff + ust + nv * 4]), dtype=dt).reshape(-1, 2) * usc
        for q in range(nv // 4):
            t = uv[q * 4:q * 4 + 4]
            px = np.stack([t[:, 0] * S, (1 - t[:, 1]) * S], 1)       # 텍스처 이미지 좌표
            out.append({'sepd': n, 'bone': bone, 'key': key, 'S': S, 'voff': base + q * 48,
                        'pos': pos[q * 4:q * 4 + 4].copy(), 'px': px,
                        'box': (px[:, 0].min(), px[:, 1].min(), px[:, 0].max(), px[:, 1].max())})
    return out


def slot_quads(qs, spec, texsize):
    """슬롯 번호 → 그 칸을 읽는 판들(UV 가운데가 칸 안). 같은 칸을 두 판이 읽기도 한다(congra 의 ！)."""
    out = {}
    for q in qs:
        S, g = texsize[q['key']]
        c = S / g
        mx, my = (q['box'][0] + q['box'][2]) / 2, (q['box'][1] + q['box'][3]) / 2
        cell = (int(mx // c), int(my // c))
        if (q['key'], cell) in spec['order']:
            out.setdefault(spec['order'].index((q['key'], cell)), []).append(q)
    return out


def letters(path):
    """GPT 가 그린 한 줄 이미지를 글자별로 자른다."""
    im = Image.open(path).convert('RGBA')
    a = np.asarray(im)[..., 3]
    col = (a > 40).sum(axis=0)
    out = []; cur = None
    for i, v in enumerate(col):
        if v > 0 and cur is None: cur = i
        elif v == 0 and cur is not None: out.append((cur, i)); cur = None
    if cur is not None: out.append((cur, len(col)))
    out = [(s, e) for s, e in out if e - s >= im.width * 0.01]
    res = []
    for s, e in out:
        g = im.crop((s, 0, e, im.height))
        b = g.getbbox()
        res.append(g.crop(b) if b else g)
    return res


def ink_h(im, box):
    """원본 텍스처의 판 영역 안 글자 잉크 높이(텍셀)."""
    x0, y0, x1, y1 = [int(round(v)) for v in box]
    a = np.asarray(im.convert('RGBA'))[max(0, y0):y1, max(0, x0):x1, 3]
    ys = np.nonzero((a > 30).any(axis=1))[0]
    return (ys[-1] - ys[0] + 1) if len(ys) else None


# ── 배치 ──────────────────────────────────────────────────

def draw(canvas, gl, box, S):
    """글자를 UV 영역(텍스처 밖은 잘라 낸 영역)에 꽉 차게 그린다 → (가운데 x, y, 텍셀 너비, 높이)"""
    x0, y0, x1, y1 = max(0, box[0]), max(0, box[1]), min(S, box[2]), min(S, box[3])
    sc = min((x1 - x0) * FILL / gl.width, (y1 - y0) * FILL / gl.height)
    im = gl.resize((max(1, round(gl.width * sc)), max(1, round(gl.height * sc))), Image.LANCZOS)
    x = round((x0 + x1 - im.width) / 2); y = round((y0 + y1 - im.height) / 2)
    canvas.alpha_composite(im, (x, y))
    return x + im.width / 2, y + im.height / 2, im.width, im.height


def set_quad(q, gx, gy, k, center, z, tolocal):
    """판 정점을 다시 계산: 글자 가운데(gx, gy 텍셀)가 center(기준 평면 좌표)에 오고, 텍셀당 k."""
    pts = []
    for (px, py) in q['px']:
        p = np.array([center[0] + (px - gx) * k, center[1] - (py - gy) * k, z, 1.0])
        pts.append((tolocal @ p)[:3])
    q['new'] = np.array(pts)


def layout_line(job, glyphs, slots, qs, bns, origs, texsize):
    lay = LAYOUT[job]
    ref = slots[lay['lines'][0][0]][0]['bone']
    toref = {q['bone']: rel(bns, q['bone'], ref) for q in qs}
    def refpos(q): return (toref[q['bone']] @ np.c_[q['pos'], np.ones(4)].T).T[:, :3]
    lines = []; gi = 0
    allslots = sorted(slots)
    for n, line in enumerate(lay['lines']):
        # 이 줄에 속한 원본 칸: 이 줄 첫 슬롯 ~ 다음 줄 첫 슬롯 전
        lo = line[0] if n else 0
        hi = lay['lines'][n + 1][0] if n + 1 < len(lay['lines']) else max(allslots) + 1
        own = [s for s in allslots if lo <= s < hi]
        hs = []; xs = []; ys = []
        for s in own:
            for q in slots[s]:
                p = refpos(q)
                xs += [p[:, 0].min(), p[:, 0].max()]
                ys.append((p[:, 1].min() + p[:, 1].max()) / 2)
                h = ink_h(origs[q['key']], q['box'])
                if h: hs.append(h * (p[:, 1].max() - p[:, 1].min()) / (q['box'][3] - q['box'][1]))
        lines.append({'slots': line, 'gl': glyphs[gi:gi + len(line)], 'H': np.median(hs) * SIZE,
                      'span': (min(xs), max(xs)), 'y': float(np.median(ys)),
                      'z': float(refpos(slots[line[0]][0])[:, 2].mean())})
        gi += len(line)
    assert gi == len(glyphs), (job, gi, len(glyphs))
    H = min(l['H'] for l in lines)             # 줄이 둘이면 같은 크기로
    for l in lines:                            # 줄 폭이 원본 폭(× SPAN)을 넘으면 줄인다
        asp = sum(g.width / g.height for g in l['gl'])
        H = min(H, (l['span'][1] - l['span'][0]) * SPAN / (asp + GAP * (len(l['gl']) - 1)))
    canvas = {k2: Image.new('RGBA', (w, w), (0, 0, 0, 0)) for k2, (w, g) in texsize.items()}
    report = []
    for l in lines:
        ws = [H * g.width / g.height for g in l['gl']]
        total = sum(ws) + H * GAP * (len(ws) - 1)
        x = (l['span'][0] + l['span'][1]) / 2 - total / 2
        for s, gl, w in zip(l['slots'], l['gl'], ws):
            q0 = slots[s][0]
            gx, gy, tw, th = draw(canvas[q0['key']], gl, q0['box'], q0['S'])
            k = H / th
            set_quad(q0, gx, gy, k, (x + w / 2, l['y']), l['z'], np.linalg.inv(toref[q0['bone']]))
            for q in slots[s][1:]:          # 같은 칸을 읽는 판이 또 있으면(congra 의 ！！) 점으로 접어 숨긴다
                c = toref[q0['bone']] @ np.r_[q0['new'].mean(0), 1.0]
                q['new'] = (np.linalg.inv(toref[q['bone']]) @ c)[:3] * np.ones((4, 1))
            report.append((s, round(x + w / 2, 2), round(w, 2)))
            x += w + H * GAP
    return canvas, H, report


def layout_nudge(job, glyphs, slots, qs, bns, texsize):
    lay = LAYOUT[job]
    canvas = {k2: Image.new('RGBA', (w, w), (0, 0, 0, 0)) for k2, (w, g) in texsize.items()}
    report = []
    for s, gl, (dx, dy) in zip(lay['slots'], glyphs, lay['move']):
        q = slots[s][0]
        gx, gy, tw, th = draw(canvas[q['key']], gl, q['box'], q['S'])
        k = lay['H'] / th
        # 원래 판에서 글자 가운데였던 점(=UV 영역 가운데)의 로컬 위치
        c = q['pos'].mean(0)
        a = -bns[q['bone']][2]                       # 본이 기울어져 있으면 화면 가로로 옮기도록 되돌린다
        ldx = dx * np.cos(a) - dy * np.sin(a); ldy = dx * np.sin(a) + dy * np.cos(a)
        set_quad(q, gx, gy, k, (c[0] + ldx, c[1] + ldy), c[2], np.eye(4))
        report.append((s, round(dx, 2), round(dy, 2)))
    return canvas, lay['H'], report


# ── 미리보기 ──────────────────────────────────────────────

def preview(slots, used, texs, bns, ref):
    """판을 기준 평면에 정사영으로 그린다(새 정점·새 텍스처 그대로). ref 가 None 이면 본마다 로컬 그대로."""
    items = []
    for s in used:
        for q in slots[s]:
            m = rel(bns, q['bone'], ref) if ref is not None else np.eye(4)
            p = (m @ np.c_[q['new'], np.ones(4)].T).T
            items.append((q, p[:, :2]))
    allp = np.concatenate([p for q, p in items])
    x0, y0 = allp.min(0) - 2; x1, y1 = allp.max(0) + 2
    sc = 900 / max(x1 - x0, (y1 - y0) * 2.2)
    W, Hh = int((x1 - x0) * sc), int((y1 - y0) * sc)
    im = Image.new('RGBA', (W, Hh), (60, 70, 110, 255))
    for q, p in items:
        bx = q['box']
        tex = texs[q['key']].crop((int(round(bx[0])), int(round(bx[1])), int(round(bx[2])), int(round(bx[3]))))
        qx0, qx1 = p[:, 0].min(), p[:, 0].max(); qy0, qy1 = p[:, 1].min(), p[:, 1].max()
        tex = tex.resize((max(1, int((qx1 - qx0) * sc)), max(1, int((qy1 - qy0) * sc))), Image.LANCZOS)
        im.alpha_composite(tex, (int((qx0 - x0) * sc), int((y1 - qy1) * sc)))
    return im


def main(write=True):
    shots = []; views = []
    for job, spec in JOBS.items():
        gar = spec['gar']
        src = os.path.join(SRC, gar + '.gar')
        cur = os.path.join(DST, gar + '.gar')
        d = bytearray(open(cur if os.path.exists(cur) else src, 'rb').read())
        sd = open(src, 'rb').read()               # 판·원본 텍스처는 항상 원본에서 읽는다
        models = cmbs(sd)
        texsize = {}; meta = {}; origs = {}
        for key, (model, tname, g) in spec['tex'].items():
            i, tex, texdata = models[model]
            dl, w, h, fmt, off = tex_entry(sd, tex, tname)
            texsize[key] = (w, g); meta[key] = (texdata + off, dl, w, h, fmt)
            origs[key] = ctxb.decode(bytes(sd[texdata + off:texdata + off + dl]), w, h, fmt, 0)
        model = list(spec['tex'].values())[0][0]
        assert cmbs(d)[model][0] == models[model][0]     # 고친 gar 와 원본의 배치가 같아야 한다
        bns = bones(sd, models[model][0])
        qs = quads(sd, model, texsize, job)
        slots = slot_quads(qs, spec, texsize)
        gl = letters(os.path.join(GPT, job + '.png'))
        lay = LAYOUT[job]
        if lay['mode'] == 'line':
            canvas, H, report = layout_line(job, gl, slots, qs, bns, origs, texsize)
            used = [s for l in lay['lines'] for s in l]; ref = slots[used[0]][0]['bone']
        else:
            canvas, H, report = layout_nudge(job, gl, slots, qs, bns, texsize)
            used = lay['slots']; ref = None
        texs = {}
        for key, im in canvas.items():
            o, dl, w, h, fmt = meta[key]
            enc = etc1.encode(im, alpha=(fmt == 0x675b))
            assert len(enc) == dl, (job, key, len(enc), dl)
            if write: d[o:o + dl] = enc
            texs[key] = ctxb.decode(enc, w, h, fmt, 0)      # 실제로 들어가는 압축 결과로 본다
            shots.append(('%s / %s' % (job, key), origs[key], texs[key]))
        for s in used:
            for q in slots[s]:
                if write: d[q['voff']:q['voff'] + 48] = q['new'].astype('<f4').tobytes()
        if lay['mode'] == 'line':                     # 꽃상점은 화면 자리를 계산할 수 없어 뺀다
            views.append((job, preview(slots, used, texs, bns, ref)))
        if write:
            os.makedirs(DST, exist_ok=True)
            open(cur, 'wb').write(bytes(d))
        print('%-9s 글자 %d개  높이 %.2f  %s%s' % (job, len(gl), H, report, '  (기록함)' if write else ''))

    try:
        f = ImageFont.truetype('C:/Windows/Fonts/malgun.ttf', 15)
    except OSError:
        return
    CW = 270
    sheet = Image.new('RGB', (CW * 2 + 30, (CW + 26) * len(shots)), (250, 250, 252))
    dr = ImageDraw.Draw(sheet)
    for n, (name, a, b) in enumerate(shots):
        y = n * (CW + 26)
        dr.text((8, y + 4), name, font=f, fill=(150, 40, 40))
        for m, im in enumerate((a, b)):
            bg = Image.new('RGBA', im.size, (40, 40, 48, 255)); bg.alpha_composite(im)
            bg = bg.resize((CW - 16, CW - 16), Image.LANCZOS)
            sheet.paste(bg, (10 + m * CW, y + 24))
        dr.text((10, y + 24 + CW - 18), '전', font=f, fill=(90, 90, 110))
        dr.text((10 + CW, y + 24 + CW - 18), '후', font=f, fill=(90, 90, 110))
    sheet.save('work/연출글씨_비교.png')
    Wv = max(v.width for j, v in views) + 20
    pv = Image.new('RGB', (Wv, sum(v.height + 30 for j, v in views)), (250, 250, 252))
    dr = ImageDraw.Draw(pv); y = 0
    for j, v in views:
        dr.text((8, y + 6), j, font=f, fill=(150, 40, 40))
        pv.paste(v.convert('RGB'), (10, y + 26)); y += v.height + 30
    pv.save('work/연출글씨_배치.png')
    print('work/연출글씨_비교.png, work/연출글씨_배치.png')


if __name__ == '__main__':
    main('--write' in sys.argv)
