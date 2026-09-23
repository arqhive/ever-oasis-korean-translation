# -*- coding: utf-8 -*-
"""스크립트(.gsb)에서 대사 호출(msg_*)마다 (대사 ID, 함수, 화자 핸들)을 뽑는다."""
import sys, os, glob, json, collections
sys.path.insert(0, os.path.dirname(__file__))
import cnut

def extract(ids):
    out = []   # (msgid, func, [handles], file, fnpath)
    for p in sorted(glob.glob('extract/scripts/*.gsb')):
        root = cnut.load(p); fname = os.path.basename(p).split('__')[0]
        for fp, f in cnut.walk(root):
            lits = f['lits']; cur = None; anim = None   # 직전에 동작·표정을 준 액터
            regsym = {}
            def local_name(reg, pc):
                for n, pos, so, eo in f['locs']:
                    if pos == reg and so <= pc <= eo: return n
                return None
            for pc, (op, a0, a1, a2, a3) in enumerate(f['ins']):
                nm = cnut.OPS[op] if op < len(cnut.OPS) else None
                if nm == 'PREPCALLK':
                    fn = lits[a1] if 0 <= a1 < len(lits) else None
                    cur = dict(fn=fn, base=a0, args={}) if isinstance(fn, str) else None
                    continue
                if cur is None: continue
                if nm == 'LOADINT': cur['args'][a0] = ('int', a1)
                elif nm == 'GETK': cur['args'][a0] = ('sym', lits[a1] if 0 <= a1 < len(lits) else None)
                elif nm == 'LOAD': cur['args'][a0] = ('sym', lits[a1] if 0 <= a1 < len(lits) else None)
                elif nm == 'MOVE': cur['args'][a0] = ('sym', local_name(a1, pc))
                elif nm == 'GETOUTER': cur['args'][a0] = ('sym', f['outs'][a1][2] if a1 < len(f['outs']) else None)
                elif nm == 'CALL':
                    vals = [cur['args'][k] for k in sorted(cur['args'])]
                    syms = [v for t, v in vals if t == 'sym' and isinstance(v, str)]
                    if 'msg' in cur['fn'] or 'talk' in cur['fn'].lower():
                        ints = [v for t, v in vals if t == 'int' and v in ids]
                        for m in ints: out.append((m, cur['fn'], syms, fname, fp, anim))
                        anim = None
                    elif any(w in cur['fn'] for w in ('actor_motion', 'actor_facial')) and syms:
                        anim = syms[0]
                    cur = None
    return out

if __name__ == '__main__':
    rows = json.load(open('work/text/messages.json', encoding='utf8'))
    ids = {r['id'] for r in rows if r['id'] >= 40000 and r['jp_plain'].strip()}
    res = extract(ids)
    json.dump(res, open('work/text/_speakers_raw.json', 'w', encoding='utf8'), ensure_ascii=False)
    got = {x[0] for x in res}
    print('화자 후보가 잡힌 대사', len(got), '/', len(ids))
    print('대사 함수', collections.Counter(x[1] for x in res).most_common(10))
    hc = collections.Counter(tuple(x[2]) for x in res)
    print('핸들 조합 %d종' % len(hc))
    for h, n in hc.most_common(70): print('  %4d %s' % (n, h))
