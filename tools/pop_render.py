# -*- coding: utf-8 -*-
"""무지개색 팝 글자(クリア！·レベルアップ！·ランク·超大成功 등)를 한글로 다시 그린다.

원본에서 측정: 채움 영역(채도 높은 픽셀)의 가로 위치별 위/아래 색, 채움 둘레 1px씩의 링 색·알파.
한글: 굵은 둥근 서체를 기울여 그리고, 같은 색 배치·링을 입힌다.
"""
import numpy as np, colorsys
from PIL import Image, ImageDraw, ImageFont, ImageFilter

SS = 4

def _sat(a):
    rgb = a[..., :3] / 255.0
    mx = rgb.max(-1); mn = rgb.min(-1)
    return np.where(mx > 0, (mx - mn) / np.maximum(mx, 1e-6), 0)

def measure(img, sat_thr=0.35, nrings=5, white=False):
    a = np.array(img.convert('RGBA')).astype(float)
    if white:   # 흰 글자: 밝은 불투명 픽셀이 채움
        fill = (a[..., 3] > 200) & (a[..., :3].mean(-1) > 170)
    else:
        fill = (a[..., 3] > 200) & (_sat(a) > sat_thr)
    ys, xs = np.where(fill)
    box = (xs.min(), ys.min(), xs.max() + 1, ys.max() + 1)
    x0, y0, x1, y1 = box
    cols = []
    for x in range(x0, x1):
        m = fill[:, x]
        if m.sum() < 2: cols.append(None); continue
        yy = np.where(m)[0]; c = a[yy, x, :3]
        k = max(1, len(yy) // 4)
        cols.append((c[:k].mean(0), c[-k:].mean(0)))
    # 빈 열은 이웃으로 채운다
    last = None
    for i in range(len(cols)):
        if cols[i] is None: cols[i] = last
        else: last = cols[i]
    first = next(c for c in cols if c is not None)
    cols = [c if c is not None else first for c in cols]
    rings = []; prev = Image.fromarray((fill * 255).astype(np.uint8))
    for r in range(nrings):
        cur = prev.filter(ImageFilter.MaxFilter(3))
        ring = (np.array(cur) > 0) & (np.array(prev) == 0)
        px = a[ring]
        rings.append((px[:, :3].mean(0) if len(px) else np.zeros(3), (px[:, 3].mean() / 255) if len(px) else 0))
        prev = cur
    return dict(box=box, cols=cols, rings=rings, size=img.size)

RINGS_POP = [((240, 240, 236), 1.0), ((222, 224, 220), 0.9), ((30, 32, 45), 0.40), ((30, 32, 45), 0.15)]
RINGS_WHITE = [((35, 25, 20), 1.0), ((35, 25, 20), 0.85), ((0, 0, 0), 0.35), ((0, 0, 0), 0.12)]

def _vivid(rgb, smin=0.78, vmin=0.0):
    h, s, v = colorsys.rgb_to_hsv(*(np.clip(np.array(rgb), 0, 255) / 255.0))
    r, g, b = colorsys.hsv_to_rgb(h, max(s, smin), max(v, vmin))
    return np.array([r, g, b]) * 255

def palette_at(meas, u, win=30):
    """글자 중심 부근(좁은 창)의 위·아래 색을 뽑아 채도를 원본 수준으로 올린다."""
    cols = meas['cols']; n = len(cols); i = int(round(min(max(u, 0), 1) * (n - 1)))
    lo = max(0, i - n // win); hi = min(n, i + n // win + 1)
    top = np.median([c[0] for c in cols[lo:hi]], 0); bot = np.median([c[1] for c in cols[lo:hi]], 0)
    return _vivid(top, 0.62, 0.95), _vivid(bot, 0.85, 0.70)

def layout(text, font_path, box, size, shear=0.18, fill_h=0.92, spacing=0.0):
    """글자별 마스크를 기울여 배치. 반환: 전체 마스크, 글자 번호 지도, 글자별 (가로 중심 u)"""
    x0, y0, x1, y1 = box; W, H = size; bh = y1 - y0; bw = x1 - x0
    f = ImageFont.truetype(font_path, 200)
    gl = []
    for ch in text:
        if ch == ' ': gl.append(None); continue
        gb = f.getbbox(ch)
        im = Image.new('L', (gb[2] - gb[0] + 40, 260), 0)
        ImageDraw.Draw(im).text((20 - gb[0], 20), ch, font=f, fill=255)
        bb = im.getbbox(); gl.append((im.crop((bb[0], 0, bb[2], im.height)), bb))
    top = min(g[1][1] for g in gl if g); bot = max(g[1][3] for g in gl if g)
    gh = bot - top; gap = int(200 * (0.06 + spacing)); sp = int(200 * 0.28)
    tw = sum((g[0].width if g else sp) for g in gl) + gap * (len(gl) - 1) + int(shear * gh) + 4
    canvas = np.zeros((gh, tw)); label = np.full((gh, tw), -1); x = int(shear * gh); k = 0; centers = []
    for g in gl:
        if g is None: x += sp; continue
        a = np.array(g[0].crop((0, top, g[0].width, bot))).astype(float) / 255
        canvas[:, x:x + a.shape[1]] = np.maximum(canvas[:, x:x + a.shape[1]], a)
        label[:, x:x + a.shape[1]][a > 0.02] = k; centers.append(x + a.shape[1] / 2); k += 1
        x += a.shape[1] + gap
    # 기울이기: 위쪽 행을 오른쪽으로
    sh = np.zeros_like(canvas); sl = np.full_like(label, -1)
    for y in range(gh):
        d = int(round(shear * (gh - 1 - y)))
        sh[y, d:] = canvas[y, :tw - d]; sl[y, d:] = label[y, :tw - d]
    nz = np.where(sh.max(0) > 0)[0]; sh = sh[:, nz.min():nz.max() + 1]; sl = sl[:, nz.min():nz.max() + 1]
    # 원본 상자에 비율 유지로 맞춤
    th = int(round(bh * fill_h)); tw2 = int(round(sh.shape[1] * th / sh.shape[0]))
    if tw2 > bw * 1.06:
        tw2 = int(bw * 1.06); th = int(round(sh.shape[0] * tw2 / sh.shape[1]))
    tw2 = min(tw2, W - 6)
    mimg = Image.fromarray((sh * 255).astype(np.uint8)).resize((tw2, th), Image.LANCZOS)
    limg = Image.fromarray((sl + 1).astype(np.uint8)).resize((tw2, th), Image.NEAREST)
    ox = (x0 + x1) // 2 - tw2 // 2; oy = (y0 + y1) // 2 - th // 2
    ox = max(3, min(ox, W - 3 - tw2))
    M = np.zeros((H, W)); Lb = np.full((H, W), -1)
    M[oy:oy + th, ox:ox + tw2] = np.array(mimg) / 255; Lb[oy:oy + th, ox:ox + tw2] = np.array(limg).astype(int) - 1
    # 라벨이 없는 가장자리 픽셀은 가까운 라벨로
    from scipy import ndimage  # noqa
    return M, Lb, (ox, oy, ox + tw2, oy + th), [c / sh.shape[1] for c in centers]

def render(text, font_path, meas, shear=0.18, fill_h=0.92, spacing=0.0, rings=None, colors=None, white=False, letters=None):
    """colors: 글자별 (위색, 아래색) 목록. 없으면 원본에서 글자 중심 위치의 색을 뽑는다."""
    from scipy import ndimage
    W, H = meas['size']
    M, Lb, (x0, y0, x1, y1), centers = layout(text, font_path, meas['box'], meas['size'], shear, fill_h, spacing)
    # 라벨 없는 잉크 픽셀에 가장 가까운 라벨
    idx = ndimage.distance_transform_edt(Lb < 0, return_distances=False, return_indices=True)
    Lb = Lb[idx[0], idx[1]]
    if colors is None:
        if letters:   # 원본 글자 수로 구간을 나눠 k번째 한글 글자 ← 대응하는 원본 글자 색
            N = len(centers)
            js = [round(k * (letters - 1) / max(1, N - 1)) for k in range(N)]
            colors = [palette_at(meas, (j + 0.5) / letters) for j in js]
        else:
            colors = [palette_at(meas, u) for u in centers]
    fill = np.zeros((H, W, 3))
    for y in range(H):
        v = min(max((y - y0) / max(1, (y1 - y0 - 1)), 0), 1)
        for k, (top, bot) in enumerate(colors):
            sel = Lb[y] == k
            fill[y, sel] = np.array(top) * (1 - v) + np.array(bot) * v
    if white: fill[:] = np.array(colors[0][0]) if colors else 255
    out = np.zeros((H, W, 4))
    def over(dst, rgb, a):
        oa = a + dst[..., 3] * (1 - a)
        dst[..., :3] = (rgb * a[..., None] + dst[..., :3] * dst[..., 3:4] * (1 - a[..., None])) / np.maximum(oa[..., None], 1e-6)
        dst[..., 3] = oa
    hi = Image.fromarray((M * 255).astype(np.uint8)).resize((W * SS, H * SS), Image.LANCZOS)
    layers = []; prev = hi
    for col, a in (rings or RINGS_POP):
        cur = prev.filter(ImageFilter.MaxFilter(2 * SS + 1)); layers.append((col, a, cur)); prev = cur
    for i, (col, a, cur) in enumerate(reversed(layers)):
        cov = np.array(cur.resize((W, H), Image.BOX)).astype(float) / 255 * a
        if i < 2:   # 바깥 그림자 두 겹은 아래로 1px 내린다
            cov = np.roll(cov, 1, axis=0)
        over(out, np.broadcast_to(np.array(col, float), (H, W, 3)), cov)
    over(out, fill, M)
    out[..., 3] *= 255
    return Image.fromarray(np.clip(out, 0, 255).astype(np.uint8), 'RGBA')
