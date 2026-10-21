"""Built rooms' art (MODELS.md, "Inner walls, doors and furniture (built rooms)"), one set per location kit.

His ruling, 2026-10-21 (GDD 5.4, A.12): rooms are no longer whole models. The player draws inner walls on
half-cell edges, puts a door in one and furnishes the room on the 3-stud grid. So each location kit gets:

    Wall_Half           one 6-stud half edge, 0.4 thick centred on the edge, 17 tall, both faces alike
    Wall_Door           the same half edge with an open arched doorway (clear x -2..2, y 0..7.2), `Door`, `Sign`
    Wall_Post           the 0.6 square post the code puts on every joint that is not a straight run
    Furniture_<Id>      every Pieces row with `furniture = true` of the location (and, in Haunted Manor, the
                        location-0 rows, "for any room"), on its w x d 3-stud squares, with `Use` and its `Pose`

Sets: blender/rooms/haunted_manor/ (location 1 and 0, the Manor's palette and dress) and
blender/rooms/frostfang_lodge/ (location 2, the Lodge's). The look reuses the approved room models' shapes
(tools/build_hotel_haunted_manor.py, build_hotel_frostfang_lodge.py): their beds, coffin, sarcophagus,
nests, counters and the pipe organ, re-authored in the furniture frame (origin the footprint's centre on the
floor, front -Z) with the faces that met in one plane moved a hair apart (decor's coplanar check).

The contract is enforced here (MODELS.md, "Checks"): the walls' exact boxes, the opening clear, nothing outside
the frame, the piece the same turned 180 degrees about Y, no coplanar faces; furniture through the kit's decor
checks (footprint, 0.4 inset, layer, seats, coplanar faces, w/d/layer from Pieces.luau) plus `Use`: its Pose,
a Lie or Sit point on the surface it names with nothing over it, a Stand point 1.5 in front of the front edge, the
5-stud person lying on a Lie point (lie_faults), a bar stool's seat at 2.4-2.8, and no shell floating.
Pieces.luau's `height` against the model's top is recorded as a finding (validation.json `height_findings`),
not refused: those heights are the blockouts' placeholders, and this session may not touch src/.

    blender -b --python-exit-code 1 -P tools/build_built_rooms.py [-- sets haunted_manor] [-- only Bed,Wall_Half]
                                                                  [-- nopreview]

Writes blender/rooms/<set>/: fbx/*.fbx, manifest.json, validation.json, import_fixup.luau (with each Use's
Pose attribute), the .blend, and review/ (Workbench sheets on light grey: the walls assembled round a room
corner with a T and a free end, the joints close up, the door piece alone, the furniture on its squares beside
a 5-stud person, floor-level elevations of every piece from the front and the side, and every Lie piece from above
and from the side with the 5-stud person lying on its Use).
"""
import ast
import json
import math
import sys
from pathlib import Path

import bpy
import numpy as np
from mathutils import Matrix, Vector

sys.path.insert(0, str(Path(__file__).resolve().parent))
import hotel_kit as K  # noqa: E402
from hotel_kit import (begin, finish, box, span, cyl, lathe, sphere, prism, attach, declare, at,  # noqa: E402
                       arch_points, round_arch_points, WALL)

TOOLS = Path(__file__).resolve().parent
ARGS = K.ARGS
SETS_ARG = set(ARGS[ARGS.index('sets') + 1].split(',')) if 'sets' in ARGS else None

# --- The contract (MODELS.md, "Inner walls, doors and furniture") -------------------------------------

HALF = 3.0                      # a half edge is 6 studs: x -3..3
TH = 0.2                        # the wall is 0.4 thick, centred on the edge
PROUD = 0.08                    # dressing proud of a face at most this (|z| <= 0.28)
POST = 0.3                      # the post: 0.6 square on the vertex
POST_TOP = WALL + 0.02          # 0.02 into the slab above: never the walls' top plane
OPEN_X, OPEN_Y = 2.0, 7.2       # the doorway's clear opening: x -2..2, y 0..7.2
ARCH_APEX = 8.4                 # the arch's head over the opening (visual; the Lintel's box starts at OPEN_Y)
SIGN = (0.0, 9.6, -0.5)         # the room plaque: above the arch, 0.3 in front of the -Z face
RAIL_Y = K.RAIL_Y               # the picture rail, as the rooms had it
BODY = {'Wall_Half': ('Wall',), 'Wall_Door': ('Wall_Left', 'Wall_Right', 'Wall_Lintel'), 'Wall_Post': ('Post',)}
BOXES = {   # each colliding part exactly (lo, hi)
    'Wall': ((-HALF, 0, -TH), (HALF, WALL, TH)),
    'Wall_Left': ((-HALF, 0, -TH), (-OPEN_X, WALL, TH)),
    'Wall_Right': ((OPEN_X, 0, -TH), (HALF, WALL, TH)),
    'Wall_Lintel': ((-OPEN_X, OPEN_Y, -TH), (OPEN_X, WALL, TH)),
    'Post': ((-POST, 0, -POST), (POST, POST_TOP, POST)),
}
WALL_BUDGET, POST_BUDGET = 1200, 200
POSES = ('Lie', 'Sit', 'Stand')
USE_SURFACE_TOL = 0.15          # a Lie/Sit point lies on its surface to this
USE_CLEAR = 1.5                 # nothing over a Lie/Sit point for this far
PROXY_IF = (2, 4.0)             # a furniture piece gets LOD_Proxy when wider than 2 squares or over 4 tall


def _lift(path, names, ns):
    """Top-level functions and literal assignments called `names` from another script, without running it."""
    src = path.read_text(encoding='utf8')
    for node in ast.parse(src).body:
        if isinstance(node, ast.FunctionDef) and node.name in names:
            exec(compile(ast.Module([node], []), str(path), 'exec'), ns)
        elif isinstance(node, ast.Assign) and getattr(node.targets[0], 'id', None) in names:
            ns[node.targets[0].id] = ast.literal_eval(node.value)
    missing = [n for n in names if n not in ns]
    assert not missing, f'{path.name}: {missing} not found'
    return ns


HM_PALETTE = list(K.PALETTE)    # the kit's default is the Haunted Manor's
FF_PALETTE = _lift(TOOLS / 'build_hotel_frostfang_lodge.py', ['PALETTE'], {})['PALETTE']
_REV = {'bpy': bpy, 'K': K, 'Vector': Vector, 'np': np}
_lift(TOOLS / 'build_cosmetics_hotel.py', ['_flat', '_block', '_person'], _REV)
_lift(TOOLS / 'build_facades.py', ['_compose'], _REV)


def furniture_rows():
    """{id: {w, d, layer, height, location, keyFor}} for every Pieces.luau decor row with furniture = true."""
    import re
    src = (K.ROOT / 'src' / 'shared' / 'Pieces.luau').read_text(encoding='utf8')
    start = src.index('local decor: { Decor } = {')
    body = src[start:src.index('\nPieces.DecorList', start)]
    rows = {}
    for blk in re.split(r'\n\t\{\n', body)[1:]:
        def get(k):
            m = re.search(rf'^\t\t{k} = "?([^",\n]+)"?,', blk, re.M)
            return m.group(1) if m else None
        if get('furniture') != 'true':
            continue
        key = re.search(r'^\t\tkeyFor = \{([^}]*)\}', blk, re.M)
        rows[get('id')] = {'w': int(get('w')), 'd': int(get('d')), 'layer': get('layer'),
                           'height': float(get('height')), 'location': int(get('location')),
                           'keyFor': re.findall(r'"(\w+)"', key.group(1)) if key else []}
    return rows


ROWS = furniture_rows()
FINDINGS = {}                   # Furniture_<Id> -> the height finding (Pieces.luau's height against the model)


def want(name):
    return K.ONLY is None or name in K.ONLY or name.replace('Furniture_', '') in K.ONLY


# --- The kit, extended from here (other sessions may be editing hotel_kit.py) ------------------------

_check_piece = K.check_piece


def check_piece(piece, boxes, tris, faults):
    """Furniture: the kit's decor rules (its lookups use Decor_<Id>; Pieces' height is a finding, not a
    fault). Walls: the kit's generic rules through kind Cosmetic (names, Root, the envelope, budgets),
    then wall_boxes()."""
    if piece.kind == 'Decor' and piece.name.startswith('Furniture_'):
        real = piece.name
        piece.name = 'Decor_' + real[len('Furniture_'):]
        sub = []
        try:
            total = _check_piece(piece, boxes, tris, sub)
        finally:
            piece.name = real
        for f in sub:
            if f.startswith("Pieces.luau's height"):
                FINDINGS[real] = f
            else:
                faults.append(f)
        return total
    if piece.kind != 'Wall':
        return _check_piece(piece, boxes, tris, faults)
    saved = K.BUDGET['Cosmetic']
    piece.kind, K.BUDGET['Cosmetic'] = 'Cosmetic', piece.budget
    sub = []
    try:
        total = _check_piece(piece, boxes, tris, sub)
    finally:
        piece.kind, K.BUDGET['Cosmetic'] = 'Wall', saved
    faults += [f.replace('the Cosmetic budget', 'the wall piece budget') for f in sub
               if not f.startswith('a cosmetic collides')]
    faults += wall_boxes(piece, boxes)
    return total


K.check_piece = check_piece


def _same_box(lo, hi, want_lo, want_hi, tol=0.01):
    return all(abs(lo[i] - want_lo[i]) <= tol and abs(hi[i] - want_hi[i]) <= tol for i in range(3))


def wall_boxes(piece, boxes):
    """MODELS.md, "Walls": the colliding parts exactly, nothing else colliding, the doorway clear, the
    door's attachments where the contract puts them."""
    f, body = [], BODY[piece.name]
    for p in body:
        if p not in boxes:
            f.append(f'missing {p}')
            continue
        lo, hi, col = boxes[p]
        if not col:
            f.append(f'{p} does not collide')
        if not _same_box(lo, hi, *BOXES[p]):
            f.append(f'{p} is {K.v3(lo)}..{K.v3(hi)}, the contract has {BOXES[p][0]}..{BOXES[p][1]}')
    extra = [p for p, (lo, hi, col) in boxes.items() if col and p not in body]
    if extra:
        f.append(f'colliding parts the contract does not name: {extra}')
    if piece.name == 'Wall_Door':
        olo, ohi = Vector((-OPEN_X, 0.15, -1.0)), Vector((OPEN_X, OPEN_Y, 1.0))
        hits = [p for p, (lo, hi, col) in boxes.items() if col and K._overlap(lo, hi, olo, ohi)]
        if hits:
            f.append(f'the doorway {2 * OPEN_X:g} x {OPEN_Y:g} is blocked by {hits}')
        for name, pos in (('Door', (0, 0, 0)), ('Sign', SIGN)):
            got = piece.att.get(name)
            if got is None or (got[0] - Vector(pos)).length > 1e-3 or got[1] is None \
                    or (got[1] - Vector((0, 0, -1))).length > 1e-3:
                f.append(f'attachment {name} not at {pos} looking -Z: {got}')
    elif piece.att:
        f.append(f'{piece.name} carries attachments {sorted(piece.att)}; none are in its contract')
    return f


def turned_twin_faults(piece):
    """MODELS.md: a wall piece is the same turned 180 degrees about Y (both faces alike). Every part's
    faces and colours, turned, are its own (Wall_Left answers to Wall_Right)."""
    out = []
    for name, (verts, faces, cols) in piece.parts.items():
        if name in ('Root', 'LOD_Proxy'):
            continue
        other = K._swap_side(name)
        if other not in piece.parts:
            out.append(f'{name}: no {other} to turn into')
            continue
        tv = [Vector((0.0 - v.x, v.y, 0.0 - v.z)) for v in verts]
        ov, of, oc = piece.parts[other]
        if K._faces_key(tv, faces, cols) != K._faces_key(ov, of, oc):
            out.append(f'{name} turned 180 degrees is not {other}')
    return out


def coplanar_faults(objs, wall_z=None):
    """The kit's coplanar check on a finished piece's objects (renamed to their part names for it)."""
    names = {ob: ob.name for ob in objs}
    for ob in objs:
        ob.name = ob.name.split('__', 1)[1]
    try:
        cop = K.coplanar_shells(objs, wall_z)
    finally:
        for ob, n in names.items():
            ob.name = n
    return [f'coplanar faces, will z-fight: {n} faces at {K.v3(K.bl2rb(Vector(at_)), 2)}'
            for n, at_ in list(cop.values())[:6]]


def _drop_built(name):
    """Take a refused piece back out of the set (finish() already recorded it)."""
    for i, (p, rec, objs) in enumerate(K.BUILT):
        if p.name == name:
            for ob in objs:
                bpy.data.objects.remove(ob)
            del K.BUILT[i]
            return


# --- Walls --------------------------------------------------------------------------------------------

def wpiece(name):
    if name == 'Wall_Post':
        p = begin(name, 'Wall', (2 * POST, 0.2, 2 * POST))
        p.allowed = ((-POST, 0.0, -POST), (POST, POST_TOP, POST))
        p.budget = POST_BUDGET
    else:
        p = begin(name, 'Wall', (2 * HALF, 0.2, 2 * TH))
        p.allowed = ((-HALF, 0.0, -TH - PROUD), (HALF, WALL, TH + PROUD))
        p.budget = WALL_BUDGET
    K.BUDGET['Wall'] = p.budget
    for b in BODY[name]:
        declare(b, True)
    return p


def wfinish(note):
    piece = K.P
    faults = turned_twin_faults(piece)
    if faults:
        raise K.Refused(f'{piece.name} REFUSED:\n  ' + '\n  '.join(faults))
    rec = finish(proxy=piece.name != 'Wall_Post', note=note)
    objs = K.BUILT[-1][2]
    faults = coplanar_faults(objs)
    if faults:
        _drop_built(piece.name)
        raise K.Refused(f'{piece.name} REFUSED:\n  ' + '\n  '.join(faults))
    rec['wall'] = {'frame': 'origin the half edge middle on the walking surface, the edge along X (x -3..3), '
                            'centred on it 0.4 thick, both faces alike (the same turned 180 degrees)',
                   'dressing_max_proud': PROUD}
    return rec


def wall_body(part, x0, x1, bands, ends=None):
    """The wall slab x0..x1 in colour bands [(y0, y1, colour)], flat (a straight run of half walls meets
    with no seam: no chamfer at the ends). `ends`: {'left'|'right': colour} for an end face (the reveal)."""
    for y0, y1, c in bands:
        col = {'rest': c}
        if ends:
            col.update(ends)
        span(part, (x0, y0, -TH), (x1, y1, TH), col)


def both_faces(fn):
    """Run fn(s) for the +Z face (s = 1) and the -Z face (s = -1)."""
    for s in (1, -1):
        fn(s)


def zs(s, p, base=TH):
    """The z range of a strip proud p on face s."""
    a, b = s * base, s * (base + p)
    return min(a, b), max(a, b)


def strip(part, x0, x1, y0, y1, p, col, s, bevel=0.0):
    z0, z1 = zs(s, p)
    span(part, (x0, y0, z0), (x1, y1, z1), col, bevel=bevel)


def rails(st, lower, upper):
    """Skirting and the chair rail on the x ranges `lower` (beside a doorway they stop at its trim), the
    picture rail and the crown on `upper`, on both faces (MODELS.md: proud at most 0.08)."""
    def face(s):
        for x0, x1 in lower:
            strip('Dressing', x0, x1, 0.0, 0.5, 0.05, st['skirting'], s)
            strip('Dressing', x0, x1, 3.05, 3.38, 0.07, st['chair'], s)
        for x0, x1 in upper:
            strip('Dressing', x0, x1, RAIL_Y, RAIL_Y + 0.3, 0.05, st['picture'], s)
            strip('Dressing', x0, x1, WALL - 0.55, WALL, PROUD, st['crown'], s)
    both_faces(face)


def wall_half(st):
    wpiece('Wall_Half')
    wall_body('Wall', -HALF, HALF, st['body'])
    rails(st, [(-HALF, HALF)], [(-HALF, HALF)])
    wfinish(f"a half wall: {st['wall_note']}")


def arch(st, x0, x1, apex):
    return (round_arch_points(x0, x1, OPEN_Y, apex, n=6) if st['arch'] == 'round'
            else arch_points(x0, x1, OPEN_Y, apex, n=4))


def _arch_y(pts, x):
    for (xa, ya), (xb, yb) in zip(pts, pts[1:]):
        if xa - 1e-9 <= x <= xb + 1e-9:
            return ya if xb == xa else ya + (x - xa) / (xb - xa) * (yb - ya)
    return pts[-1][1]


def _cross(pts, y):
    """Where the arch outline crosses height y (x values)."""
    out = []
    for (xa, ya), (xb, yb) in zip(pts, pts[1:]):
        if (ya - y) * (yb - y) < 0:
            out.append(xa + (y - ya) / (yb - ya) * (xb - xa))
    return out


def lintel(st, pts):
    """Wall_Lintel: the wall's bands over the opening (x -2..2, y 7.2..17), the arch's head cut into the
    bands it crosses. Each band crossing the arch is a polygon (or two, either side of the head)."""
    apex = max(y for _, y in pts)
    for y0, y1, c in st['body']:
        if y1 <= OPEN_Y + 1e-9:
            continue
        ya = max(y0, OPEN_Y)
        if ya >= apex - 1e-9:
            span('Wall_Lintel', (-OPEN_X, ya, -TH), (OPEN_X, y1, TH), c)
            continue
        xs = sorted({-OPEN_X, OPEN_X} | {x for x, _ in pts} | set(_cross(pts, ya)) | set(_cross(pts, y1)))
        low = [(x, max(ya, _arch_y(pts, x))) for x in xs]
        runs, cur, prev = [], None, None
        for x, y in low:
            if y < y1 - 1e-6:
                if cur is None:
                    cur = [] if prev is None else [(prev[0], y1)]
                cur.append((x, y))
            elif cur is not None:
                cur.append((x, y1))
                runs.append(cur)
                cur = None
            prev = (x, y)
        if cur is not None:
            runs.append(cur)
        for run in runs:
            poly = run + [(run[-1][0], y1), (run[0][0], y1)]
            clean = []
            for p in poly:
                if not clean or (abs(p[0] - clean[-1][0]) > 1e-6 or abs(p[1] - clean[-1][1]) > 1e-6):
                    clean.append(p)
            if abs(clean[0][0] - clean[-1][0]) < 1e-6 and abs(clean[0][1] - clean[-1][1]) < 1e-6:
                clean.pop()
            if len(clean) >= 3:
                prism('Wall_Lintel', clean, -TH, TH, {'front': c, 'back': c, 'rest': st['reveal']})


def wall_door(st):
    wpiece('Wall_Door')
    wall_body('Wall_Left', -HALF, -OPEN_X, st['body'], ends={'right': st['reveal']})
    wall_body('Wall_Right', OPEN_X, HALF, st['body'], ends={'left': st['reveal']})
    inner = arch(st, -OPEN_X, OPEN_X, ARCH_APEX)
    lintel(st, inner)
    trim = OPEN_X + 0.42
    outer = arch(st, -trim, trim, ARCH_APEX + 0.5)

    def face(s):
        z0, z1 = zs(s, 0.06)
        for sx in (-1, 1):      # the jambs' trim and a plinth block at their feet
            xa, xb = sorted((sx * OPEN_X, sx * trim))
            span('Dressing', (xa, 0.72, z0), (xb, OPEN_Y, z1), st['trim'])
            # The plinth (blind review 2026-10-21: an uncapped grey block): the frame's own wood, a little
            # wider than the casing on its outer side, a chamfered body under a prouder moulded cap the
            # casing lands on. Its inner end stays on the jamb's line (x = +-2, the opening clear).
            pa, pb = zs(s, PROUD - 0.012)
            ca, cb = zs(s, PROUD)
            bx = sorted((sx * OPEN_X, sx * (trim + 0.07)))
            cx = sorted((sx * OPEN_X, sx * (trim + 0.1)))
            span('Dressing', (bx[0], 0.0, pa), (bx[1], 0.6, pb), st['trim'], bevel=0.02)
            span('Dressing', (cx[0], 0.6, ca), (cx[1], 0.74, cb), st['trim'], bevel=0.03)
        prism('Dressing', outer + list(reversed(inner)), z0, z1, st['trim'])
        ka, kb = zs(s, PROUD - 0.005, base=TH + 0.005)    # the keystone, prouder than the trim, its back in it
        top = _arch_y(outer, 0.0)
        prism('Dressing', [(-0.3, top - 0.75), (0.3, top - 0.75), (0.38, top), (-0.38, top)],
              ka, kb, st['keystone'])
    both_faces(face)
    rails(st, [(-HALF, -trim), (trim, HALF)], [(-HALF, HALF)])
    attach('Door', (0, 0, 0), (0, 0, -1))
    attach('Sign', SIGN, (0, 0, -1))
    wfinish(f"a half wall with an open {st['arch']}-arched doorway (clear 4 x 7.2): {st['door_note']}")


def wall_post(st):
    wpiece('Wall_Post')
    for y0, y1, c in st['post']:
        span('Post', (-POST, y0, -POST), (POST, y1, POST), c)
    wfinish(f"the joint post, 0.6 square, 17.02 tall: {st['post_note']}")


# --- Furniture ----------------------------------------------------------------------------------------

def furn(id_):
    """Begin Furniture_<id_> on its Pieces row's w x d squares and layer (MODELS.md, "Furniture")."""
    row = ROWS[id_]
    p = K.decor(id_, row['w'], row['d'], row['layer'])
    p.name = f'Furniture_{id_}'
    p.row = row
    p.pose = None
    p.lie = None
    p.checks.append(use_check)
    p.checks.append(grounded_check)
    return p


PERSON = 5.0                    # the 5-stud person (CLAUDE.md, "The scale of a person"), lying: head top to feet
LIE_RISE = (0.45, 0.8)          # over the body, the most a surface may rise above a Lie point: under the legs and
                                # torso (a footboard any higher is through the feet), under the head (its pillow)
LIE_DROP = 0.6                  # the most the surface may fall under the body (more, and it hangs off an end)
HEAD = 1.2                      # the head's end of the body, where the pillow is


def use(pos, look, pose, rise=None, waive=None):
    """`rise`: (legs and torso, head) when a piece's lying surface is not flat (a hammock's sling rises to its
    ends); `waive`: the reason a Lie piece cannot hold the 5-stud person straight (a finding, recorded)."""
    assert pose in POSES, pose
    attach('Use', pos, look)
    K.P.pose = pose
    K.P.lie = {'rise': tuple(rise or LIE_RISE), 'waived': waive} if pose == 'Lie' else None


def surface_y(x, z, above=20.0):
    """The top of the piece built so far at (x, z) (for a Use point on a curved or stretched surface)."""
    tris = []
    for n, (vs, fs, _) in K.P.parts.items():
        if n in ('Root', 'LOD_Proxy'):
            continue
        for f in fs:
            for i in range(1, len(f) - 1):
                tris.append((vs[f[0]], vs[f[i]], vs[f[i + 1]]))
    return round(max(K._ray_down(tris, x, z, above)), 3)


def lie_faults(piece, allt, pos, look, tag):
    """MODELS.md, "Furniture" (`Lie`, at the middle of where the body lies): the 5-stud person centred on Use,
    the head toward -LookVector, lies on the piece: every point of the body's line (and the legs' lines) is in
    the footprint, on something no more than LIE_DROP below the Lie point, and under nothing that rises more
    than the piece's rise (legs and torso; the head's last HEAD on its pillow) within USE_CLEAR."""
    f = []
    a = Vector((look.x, 0, look.z)).normalized()
    b = Vector((-a.z, 0, a.x))
    body, head = piece.lie['rise']
    hx, hz = 1.5 * piece.fw, 1.5 * piece.fd
    n = 40
    for i in range(n + 1):
        t = -PERSON / 2 + 0.05 + (PERSON - 0.1) * i / n
        lines = (0.0, -0.45, 0.45) if t > 0.5 else (0.0,)
        for s in lines:
            q = pos + a * t + b * s
            where = f'{"head" if t < 0 else "feet"} {abs(t):.2f} from Use' + (f', leg line {s:+.2f}' if s else '')
            if abs(q.x) > hx + 1e-6 or abs(q.z) > hz + 1e-6:
                f.append(f'{tag}: the lying person leaves the footprint ({where})')
                return f
            hits = K._ray_down(allt, q.x, q.z, pos.y + USE_CLEAR)
            top = max(hits, default=None)
            rise = head if t < -PERSON / 2 + HEAD else body
            if top is None or top < pos.y - LIE_DROP:
                f.append(f'{tag}: the lying person hangs off the piece ({where}: '
                         f'{"nothing" if top is None else f"{top:.2f}"} under it, the Lie point at {pos.y:.2f})')
                return f
            if top > pos.y + rise + 1e-6:
                f.append(f'{tag}: something at {top:.2f} goes through the lying person ({where}; the Lie point at '
                         f'{pos.y:.2f}, at most {rise} higher)')
                return f
    return f


def stand():
    """The Stand point: the square in front of the front edge's middle, facing the piece."""
    use((0, 0, -1.5 * K.P.fd - 1.5), (0, 0, 1), 'Stand')


def use_check(piece, tris, stage):
    f = []
    if 'Use' not in piece.att or piece.pose not in POSES:
        return [f'no Use attachment with a Pose ({POSES})']
    pos, look = piece.att['Use']
    tag = f'Use ({stage})'
    if look is None or abs(look.y) > 1e-3:
        f.append(f'{tag}: its LookVector {look} is not level')
    if piece.pose == 'Stand':
        want = Vector((0, 0, -1.5 * piece.fd - 1.5))
        if (pos - want).length > 0.01 or (look - Vector((0, 0, 1))).length > 1e-3:
            f.append(f'{tag}: a Stand point is {K.v3(want)} looking +Z, not {K.v3(pos)} looking {look}')
        return f
    hx, hz = 1.5 * piece.fw, 1.5 * piece.fd
    if abs(pos.x) > hx or abs(pos.z) > hz:
        f.append(f'{tag}: {K.v3(pos)} leaves the footprint')
    allt = [t for p, ts in tris.items() if p not in ('Root', 'LOD_Proxy') for t in ts]
    top = max(K._ray_down(allt, pos.x, pos.z, pos.y + 0.5), default=None)
    if top is None or abs(top - pos.y) > USE_SURFACE_TOL:
        f.append(f'{tag}: the surface under {K.v3(pos)} is at {top}, not within {USE_SURFACE_TOL} of it')
    over = [h for h in K._ray_down(allt, pos.x, pos.z, pos.y + USE_CLEAR) if h > pos.y + 0.2]
    if over:
        f.append(f'{tag}: something over the {piece.pose} point at {max(over):.2f}')
    if piece.pose == 'Sit':
        inside = [s for s in piece.seats if s['x'][0] <= pos.x <= s['x'][1] and s['z'][0] <= pos.z <= s['z'][1]]
        if not inside:
            f.append(f'{tag}: a Sit point not on a declared seat (rule 6)')
    if piece.pose == 'Lie' and not piece.lie['waived']:
        f += lie_faults(piece, allt, pos, look, tag)
    return f


GROUND_TOL = 0.03               # a shell touching the floor or a grounded shell's box within this is held


def grounded_check(piece, tris, stage):
    """Nothing floats (blind review 2026-10-21; floor-level elevations found an organ's pipes, finials, mug
    handles and a blanket standing on nothing): every shell (a connected solid, joined by shared corners) of
    the body stands on the floor or touches a shell that does, box to box within GROUND_TOL."""
    boxes = []
    for part, ts in tris.items():
        if part in ('Root', 'LOD_Proxy'):
            continue
        parent = {}

        def find(k):
            while parent.setdefault(k, k) != k:
                parent[k] = parent[parent[k]]
                k = parent[k]
            return k
        for t in ts:
            ks = [(round(v.x, 3), round(v.y, 3), round(v.z, 3)) for v in t]
            for k in ks[1:]:
                a, b = find(ks[0]), find(k)
                if a != b:
                    parent[b] = a
        shells = {}
        for k in list(parent):
            shells.setdefault(find(k), []).append(k)
        for pts in shells.values():
            boxes.append((tuple(min(p[i] for p in pts) for i in range(3)), tuple(max(p[i] for p in pts) for i in range(3))))
    held = [lo[1] <= GROUND_TOL for lo, _ in boxes]
    grew = True
    while grew:
        grew = False
        for i, (lo, hi) in enumerate(boxes):
            if held[i]:
                continue
            for j, (lo2, hi2) in enumerate(boxes):
                if held[j] and all(lo[k] <= hi2[k] + GROUND_TOL and lo2[k] <= hi[k] + GROUND_TOL for k in range(3)):
                    held[i] = grew = True
                    break
    loose = [b for b, h in zip(boxes, held) if not h]
    return [f'floats ({stage}): a shell {K.v3(lo, 2)}..{K.v3(hi, 2)} stands on nothing' for lo, hi in loose[:4]]


BAR_SEAT_Y = (2.4, 2.8)         # a bar stool's seat, at a counter 3.4-3.8 (MODELS.md, "Furniture")


def bar_seat(x0, x1, z0, z1, y):
    """A bar stool's seat: rule 6's checks with its top at BAR_SEAT_Y instead of 1.5-2.0 (the 5-stud person
    sits high at a counter, feet on the stool's ring)."""
    K.seat(x0, x1, z0, z1, y, narrow=None)
    K.P.seats[-1]['bar'] = True
    K.P.checks.remove(K._seat_check)
    K.P.checks.append(_bar_seat_check)


def _bar_seat_check(piece, tris, stage):
    saved = K.SEAT_Y
    K.SEAT_Y = BAR_SEAT_Y
    try:
        return K._seat_check(piece, tris, stage)
    finally:
        K.SEAT_Y = saved


def _body_bounds(piece):
    pts = [v for n, (vs, _, _) in piece.parts.items() if n not in ('Root', 'LOD_Proxy') for v in vs]
    return K._bounds(pts)


def done(note):
    """LOD_Proxy where the contract asks, finish(), the furniture record."""
    piece = K.P
    lo, hi = _body_bounds(piece)
    proxy = max(piece.fw, piece.fd) > PROXY_IF[0] or hi.y > PROXY_IF[1]
    if proxy:
        box('LOD_Proxy', (lo + hi) / 2, hi - lo, 'grey', collide=False)
    rec = finish(proxy=False, note=note)
    rec['furniture'] = {'id': piece.name[len('Furniture_'):], 'pose': piece.pose, 'keyFor': piece.row['keyFor'],
                        'pieces_height': piece.row['height'], 'model_top': round(hi.y, 3),
                        'height_finding': FINDINGS.get(piece.name)}
    if piece.lie:
        rec['furniture']['lie'] = {'person': PERSON, 'rise': list(piece.lie['rise']), 'drop': LIE_DROP,
                                   'waived': piece.lie['waived']}
    return rec


def shift(dx=0.0, dz=0.0):
    for n, (vs, _, _) in K.P.parts.items():
        if n in ('Root', 'LOD_Proxy'):
            continue
        for v in vs:
            v.x += dx
            v.z += dz


def stretch(sx, sz):
    for n, (vs, _, _) in K.P.parts.items():
        if n in ('Root', 'LOD_Proxy'):
            continue
        for v in vs:
            v.x *= sx
            v.z *= sz


ZF, ZB = -2.825, 2.825          # a bed's foot and head in a 3-square-deep footprint (the rooms' 5.65 bed, centred)


def hm_bed(hw=1.95, frame='wood_dark', blanket='violet', pillow='cream', head='gothic', head_col=None,
           foot=True, mattress='cream', pillows=(0.0,), legs=True):
    """The Manor's bed (build_hotel_haunted_manor.bed), centred, any width; the faces that shared a plane
    (footboard and frame, sheet and blanket, headboard and frame) moved 0.02-0.05 apart."""
    zf, zb = ZF, ZB
    head_col = head_col or frame
    if legs:
        for x in (-hw + 0.2, hw - 0.2):
            for z in (zf + 0.2, zb - 0.2):
                box('Body', (x, 0.5, z), (0.35, 0.8, 0.35), frame, bevel=0.06)
    span('Body', (-hw, 0.6, zf), (hw, 1.1, zb), frame, bevel=0.08)
    span('Body', (-hw + 0.1, 1.1, zf + 0.1), (hw - 0.1, 1.65, zb - 0.1), mattress, bevel=0.15)
    span('Body', (-hw + 0.02, 1.25, zf + 0.05), (hw - 0.02, 1.8, zf + 3.4), blanket, bevel=0.18)
    span('Body', (-hw + 0.05, 1.62, zf + 3.1), (hw - 0.05, 1.84, zf + 3.6), 'cream', bevel=0.08)  # turned sheet
    pw = 1.3 if len(pillows) == 1 else min(1.15, hw / 2 - 0.15)
    for px in pillows:
        span('Body', (px - pw, 1.6, zb - 1.5), (px + pw, 2.25, zb - 0.35), pillow, bevel=0.22)
    hb = hw + 0.05
    if head == 'gothic':
        pts = [(-hb, 0.0), (hb, 0.0), (hb, 3.2)] + [(x, y) for x, y in reversed(
            arch_points(-hb, hb, 3.2, 5.0, n=3))][1:-1] + [(-hb, 3.2)]
        prism('Body', pts, zb - 0.3, zb + 0.03, {'rest': head_col}, plane='xy')
        for x in (-hb + 0.15, hb - 0.15):
            sphere('Body', (x, 3.45, zb - 0.15), (0.24, 0.24, 0.24), 'gold', n=8, rings=4)
    if foot:
        span('Body', (-hb, 0.55, zf - 0.05), (hb, 2.3, zf + 0.25), frame, bevel=0.08)
    return zf, zb


def hm_furniture():
    return {
        'Bed': f_bed, 'DoubleBed': f_double_bed, 'PlanterBed': f_planter_bed, 'FourPosterBed': f_four_poster,
        'Sarcophagus': f_sarcophagus, 'WitchBed': f_witch_bed, 'DenNest': f_den_nest, 'Coffin': f_coffin,
        'OperaChaise': f_opera_chaise, 'SnackCounter': f_snack_counter, 'Jukebox': f_jukebox,
        'Gravestone': f_gravestone, 'ReadingDesk': f_reading_desk, 'PipeOrgan': f_pipe_organ,
        'Nightstand': f_nightstand, 'Wardrobe': f_wardrobe, 'WritingDesk': f_writing_desk,
        'DiningTable': f_dining_table, 'BreakfastBuffet': f_buffet, 'BarStool': f_bar_stool,
        'PoolTable': f_pool_table, 'CardTable': f_card_table, 'Bathtub': f_bathtub, 'FloorLamp': f_floor_lamp,
    }


def lie_on_blanket(y=1.8, z=-0.05, x=0.0):
    """The Lie point of a bed 5.65 long (ZF..ZB): the 5-stud person's middle, the head's top at the pillow's
    back (ZB - 0.4), the feet inside the footboard (ZF + 0.25)."""
    use((x, y, z), (0, 0, -1), 'Lie')


def f_bed():
    furn('Bed')
    hm_bed(frame='wood_dark', blanket='violet', head='gothic', head_col='plum_dark')
    lie_on_blanket()
    done("the Standard Room's bed: dark wood, a violet blanket, a gothic plum headboard with gold finials")


def f_double_bed():
    furn('DoubleBed')
    hm_bed(hw=2.9, frame='wood_dark', blanket='rose', head='gothic', head_col='plum_dark', pillows=(-1.35, 1.35))
    lie_on_blanket(x=-1.3)
    done('the bed twice as wide: two pillows, a rose blanket, the same gothic headboard widened')


def f_four_poster():
    furn('FourPosterBed')
    zf, zb = hm_bed(hw=2.9, frame='wood_dark', blanket='plum', head='gothic', head_col='plum_dark',
                    pillows=(-1.35, 1.35), legs=False, foot=False)
    for x in (-2.72, 2.72):
        for z in (zf + 0.22, zb - 0.22):
            cyl('Body', (x, 0, z), 0.17, 5.9, 'wood_dark', n=8)
            sphere('Body', (x, 6.14, z), 0.26, 'gold', n=8, rings=4)     # seated on the post (was 0.04 over it)
    # The canopy is an open frame (blind review 2026-10-21: a solid tester hid the bed and its guest from the
    # raised and top-down phone camera): plum rails on the posts, a plum valance hanging from each side rail,
    # the gold band on the foot rail. The side rails run between the end rails (their ends buried in them)
    # and sit 0.02 higher and lower, so no two faces share a plane.
    for sx in (-1, 1):
        x = 2.77 * sx
        span('Body', (x - 0.17, 5.55, zf + 0.1), (x + 0.17, 5.88, zb - 0.1), 'plum_dark', bevel=0.04)
        xa, xb = sorted((2.9 * sx, 2.98 * sx))      # the valance's top is held inside the rail
        span('Body', (xa, 5.02, zf + 0.34), (xb, 5.62, zb - 0.34), 'plum', bevel=0.02)
    for z in (zf + 0.22, zb - 0.22):
        span('Body', (-2.8, 5.57, z - 0.16), (2.8, 5.86, z + 0.16), 'plum_dark', bevel=0.04)
    span('Body', (-3.02, 5.38, zf - 0.04), (3.02, 5.62, zf + 0.3), 'gold', bevel=0.05)     # its valance's gold band
    for x in (-2.72, 2.72):
        lathe('Body', [(0.42, 2.6), (0.24, 4.2), (0.44, 5.5)], 'plum', n=6, base=(x, 0, zf + 0.62), scale=(0.4, 1))
    lie_on_blanket(x=-1.3)
    done('an antique four-poster: dark turned posts with gold finials, an open plum canopy frame with side '
         'valances and a gold band at the foot, drapes tied at the foot, the gothic headboard')


def f_planter_bed():
    furn('PlanterBed')
    span('Body', (-2.2, 0.0, -3.4), (2.2, 1.1, 3.4), 'wood', bevel=0.1)
    for (x0, z0, x1, z1) in ((-2.26, -3.46, 2.26, -3.12), (-2.26, 3.12, 2.26, 3.46),
                             (-2.26, -3.12, -1.92, 3.12), (1.92, -3.12, 2.26, 3.12)):
        span('Body', (x0, 1.0, z0), (x1, 1.3, z1), 'wood_dark', bevel=0.04)
    span('Body', (-1.9, 1.1, -3.1), (1.9, 1.42, 3.1), 'moss', bevel=0.12)
    span('Body', (-1.88, 1.3, -3.05), (1.88, 1.56, 0.6), 'leaf', bevel=0.12)
    span('Body', (-1.2, 1.36, 1.55), (1.2, 1.78, 2.85), 'cream', bevel=0.16)
    pumpkin_ = _HM['pumpkin']
    for x in (-1.6, 1.6):
        pumpkin_('Body', (x, 1.3 + 0.3 * 0.78, 3.0), 0.3)
    for k, (x, z) in enumerate(((-2.09, -2.4), (-2.09, -0.6), (2.09, -1.5), (2.09, 0.4), (-2.09, 1.4), (2.09, 2.2))):
        sphere('Body', (x, 1.42, z), (0.16, 0.12, 0.16), ('violet', 'pumpkin', 'lilac')[k % 3], n=6, rings=3)
    lie_on_blanket(y=1.56, z=0.25)     # the head on the pillow, the feet inside the foot rim
    done('a bed in a wooden planter: a moss mattress under a leaf blanket, pumpkins at the head, flowers on the rim')


def f_sarcophagus():
    furn('Sarcophagus')
    zf, zb = ZF, ZB
    span('Body', (-1.95, 0, zf), (1.95, 0.5, zb), 'stone', bevel=0.08)
    outline = [(-1.2, zf + 0.15), (1.2, zf + 0.15), (1.75, zf + 1.6), (1.55, zb - 0.15), (-1.55, zb - 0.15),
               (-1.75, zf + 1.6)]
    prism('Body', outline, 0.5, 1.6, 'gold', plane='xz')
    prism('Body', [(x * 0.95, z) for x, z in outline], 1.6, 1.78, 'teal', plane='xz')
    prism('Body', [(x * 0.9, z) for x, z in outline], 1.78, 2.2, 'gold', plane='xz')
    for k in range(4):
        z = zf + 0.9 + k * 0.9
        span('Body', (-1.5, 2.2, z - 0.12), (1.5, 2.26, z + 0.12), 'teal')
    sphere('Body', (0, 2.38, zb - 1.0), (0.75, 0.3, 0.62), 'gold', n=8, rings=4)
    for x in (-0.3, 0.3):
        box('Body', (x, 2.62, zb - 1.3), (0.24, 0.1, 0.12), 'ink')
    for x in (-0.95, 0.95):
        span('Body', (x - 0.22, 2.0, zb - 1.5), (x + 0.22, 2.45, zb - 0.5), 'teal', bevel=0.05)
    use((0, 2.2, 0.15), (0, 0, -1), 'Lie')     # on the lid, 5.35 long: the head on the face, the feet 0.3 in
    done("the Sarcophagus Suite's sarcophagus: gold on a stone plinth, teal bands, its face and striped headdress")


def f_witch_bed():
    furn('WitchBed')
    zf, zb = hm_bed(frame='plum_dark', blanket='teal', head='gothic', head_col='violet')
    # A sleeping black cat at the foot, a witch's hat on the left finial.
    sphere('Body', (0.9, 2.08, zf + 0.85), (0.55, 0.32, 0.42), 'black', n=8, rings=5)
    sphere('Body', (0.32, 2.12, zf + 0.6), 0.3, 'black', n=8, rings=5)
    for dx in (-0.14, 0.14):
        lathe('Body', [(0.11, 0), (0, 0.24)], 'black', n=4, base=(0.32 + dx, 2.32, zf + 0.6))
    lathe('Body', [(0.0, 3.62), (0.55, 3.62), (0.55, 3.68), (0.26, 3.7), (0.0, 4.5)], 'black', n=10,
          base=(-1.85, 0, zb - 0.15))
    lathe('Body', [(0.27, 3.72), (0.27, 3.86), (0.24, 3.88)], 'violet', n=10, base=(-1.85, 0, zb - 0.15))
    use((-0.7, 1.8, -0.05), (0, 0, -1), 'Lie')     # the legs beside the cat
    done("the Potion Loft's witch's bed: teal blanket, violet gothic headboard, a black cat asleep on it, a hat on a post")


def f_den_nest():
    furn('DenNest')
    lathe('Body', [(1.35, 0.0), (1.95, 0.0), (1.95, 0.9), (1.75, 1.35), (1.4, 1.2)], 'straw', n=12,
          scale=(1, 1.42), closed=True)
    lathe('Body', [(0, 0.0), (1.45, 0.0), (1.45, 0.6), (0, 0.75)], 'brown', n=12, scale=(1, 1.42))
    lathe('Body', [(0, 0.6), (1.0, 0.65), (0.6, 0.95), (0, 1.0)], 'rose', n=10, base=(0, 0, 1.6), scale=(1.2, 0.6))
    cyl('Body', (0, 0, 0), 0.14, 1.6, 'bone', n=6, m=K.Matrix.Translation((-0.8, 0.95, -1.2))
        @ K.Matrix.Rotation(math.radians(-90), 4, 'Z'))
    for x in (-0.8, 0.8):
        for dz in (-0.14, 0.14):
            sphere('Body', (x, 0.95, -1.2 + dz), 0.18, 'bone', n=6, rings=4)
    stretch(1.3, 1.3)
    use((0, surface_y(0, 0), 0), (0, 0, -1), 'Lie')     # centred: 4.98 inside the rim, the head on the pillow
    done("the Den Room's round straw nest, a third larger for its 3 x 3: a brown cushion, a rose pillow, a bone")


def f_coffin():
    furn('Coffin')
    # 6.0 long (blind review 2026-10-21: the Coffin Suite's 4.95 left a 5-stud guest's feet over the foot); its
    # outline's proportions kept along the length (the shoulders 0.737 of the way to the head), the width as it was.
    zf, zb = -3.0, 3.0
    zsh = zf + 0.737 * (zb - zf)
    outline = [(-0.95, zf), (0.95, zf), (1.9, zsh), (1.4, zb), (-1.4, zb), (-1.9, zsh)]
    prism('Body', outline, 0, 1.5, 'wood_dark', plane='xz')
    prism('Body', [(x * 0.84, z + (0.12 if z < 0 else -0.12)) for x, z in outline], 1.5, 1.62, 'crimson',
          plane='xz')
    span('Body', (-0.9, 1.62, zb - 1.1), (0.9, 2.0, zb - 0.3), 'cream', bevel=0.15)
    bat = [(0, 0.55), (0.35, 0.9), (0.9, 0.75), (1.25, 1.25), (0.7, 1.2), (0.3, 1.5), (0, 1.3),
           (-0.3, 1.5), (-0.7, 1.2), (-1.25, 1.25), (-0.9, 0.75), (-0.35, 0.9)]
    m = K.Matrix.Translation((0, 0, zf))       # the gold bat on the coffin's foot end
    prism('Body', [(x * 0.55, y) for x, y in bat], -0.04, 0.01, 'gold', plane='xy', m=m)
    use((0, 1.62, 0.3), (0, 0, -1), 'Lie')     # the head's top 0.1 behind the pillow, the feet 0.7 inside the foot
    done("the Coffin Suite's coffin, 6.0 long: dark wood, red velvet, a cream pillow, the gold bat on its foot")


def f_opera_chaise():
    furn('OperaChaise')
    for x in (-3.3, 3.3):
        for z in (-1.55, 1.55):
            lathe('Body', [(0.18, 0), (0.12, 0.3), (0.16, 0.7)], 'gold', n=6, base=(x, 0, z))
    span('Body', (-3.6, 0.65, -1.9), (3.6, 1.05, 1.9), 'gold', bevel=0.08)
    span('Body', (-3.5, 1.0, -1.8), (3.5, 1.6, 1.8), 'crimson', bevel=0.2)
    span('Body', (-3.6, 1.45, 1.32), (1.2, 2.45, 1.92), 'crimson', bevel=0.22)
    span('Body', (-3.62, 2.42, 1.48), (1.22, 2.6, 1.86), 'gold', bevel=0.05)
    for x in (-2.8, -1.6, -0.4):
        sphere('Body', (x, 2.0, 1.29), (0.1, 0.1, 0.06), 'gold', n=6, rings=3)
    cyl('Body', (0, 0, 0), 0.55, 3.9, 'crimson', n=10, m=at((-3.52, 2.0, -1.95), rx=90))
    for z in (-1.97, 1.97):
        cyl('Body', (0, 0, 0), 0.4, 0.06, 'gold', n=10, m=at((-3.52, 2.0, z - 0.03), rx=90))
    use((0.6, 1.6, -0.4), (1, 0, 0), 'Lie')
    done("the Opera Suite's fainting couch: crimson velvet on a gold frame, a rolled head end, a tufted back")


def f_snack_counter():
    furn('SnackCounter')
    span('Body', (-4.0, 0, -0.85), (4.0, 3.2, 1.0), 'plum', bevel=0.1)
    for i in range(13):
        x = -3.6 + i * 0.6
        span('Body', (x - 0.15, 0.2, -0.88), (x + 0.15, 3.0, -0.8), 'pumpkin' if i % 2 else 'cream')
    span('Body', (-4.1, 3.2, -1.05), (4.1, 3.45, 1.1), 'wood_light', bevel=0.06)
    for x, colr in ((-3.0, 'pumpkin'), (-1.8, 'rose'), (2.8, 'slime')):
        lathe('Body', [(0.3, 3.45), (0.38, 3.6), (0.38, 4.2), (0.25, 4.3)], 'lavender', n=8, base=(x, 0, 0.3))
        sphere('Body', (x, 4.4, 0.3), (0.2, 0.12, 0.2), colr, n=6, rings=3)
    lathe('Body', [(0.55, 3.45), (0.55, 3.85), (0.4, 3.95), (0, 4.0)], 'rose', n=10, base=(0.4, 0, 0.1))
    stand()
    done("the Snack Bar's candy-striped counter, its jars of sweets and a pie")


def f_jukebox():
    furn('Jukebox')
    span('Body', (-1.05, 0, -0.8), (1.05, 3.4, 0.8), 'wood_dark', bevel=0.1)
    prism('Body', round_arch_points(-1.05, 1.05, 3.4, 4.6, n=8), -0.8, 0.8, 'wood_dark', plane='xy')
    outer = round_arch_points(-0.9, 0.9, 3.0, 4.38, n=8)
    inner = round_arch_points(-0.62, 0.62, 3.0, 4.05, n=8)
    prism('Glow_Warm_1', outer + list(reversed(inner)), -0.86, -0.8, 'lamp', plane='xy')
    span('Body', (-0.62, 1.9, -0.84), (0.62, 2.95, -0.8), 'night')
    cyl('Body', (0, 0, 0), 0.4, 0.02, 'black', n=12, m=at((0, 2.42, -0.84), rx=-90))
    span('Body', (-0.62, 0.45, -0.84), (0.62, 1.6, -0.8), 'gold')
    for k in range(4):
        span('Body', (-0.5, 0.6 + k * 0.25, -0.86), (0.5, 0.68 + k * 0.25, -0.84), 'wood_dark')
    for x in (-0.82, 0.82):
        span('Body', (x - 0.1, 0.3, -0.85), (x + 0.1, 3.0, -0.8), 'violet' if x < 0 else 'pumpkin')
    stand()
    done('a jukebox: dark wood, a warm glowing arch, a record behind glass, a gold speaker grille')


def f_gravestone():
    furn('Gravestone')
    span('Body', (-1.0, 0, -0.6), (1.0, 0.4, 0.6), 'stone_dark', bevel=0.05)
    pts = [(-0.8, 0.4), (0.8, 0.4)] + round_arch_points(0.8, -0.8, 2.2, 3.0, n=8)[0:]
    prism('Body', pts, -0.25, 0.25, 'stone', plane='xy')
    span('Body', (-0.07, 1.5, -0.28), (0.07, 2.5, -0.25), 'stone_dark')
    span('Body', (-0.32, 2.08, -0.29), (0.32, 2.22, -0.25), 'stone_dark')
    for x, z, r in ((-0.7, -0.45, 0.22), (0.75, 0.35, 0.18), (0.5, -0.5, 0.14)):
        sphere('Body', (x, 0.42, z), (r, 0.1, r), 'moss', n=6, rings=3)
    stand()
    done("a friendly tombstone from the Graveyard Garden: rounded, a carved cross, moss on its plinth")


def f_reading_desk():
    furn('ReadingDesk')
    for x in (-2.2, 2.2):
        for z in (-0.8, 0.8):
            span('Body', (x - 0.13, 0, z - 0.13), (x + 0.13, 2.22, z + 0.13), 'wood_dark', bevel=0.03)
        span('Body', (x - 0.1, 0.5, -0.7), (x + 0.1, 0.7, 0.7), 'wood_dark')
    span('Body', (-2.1, 0.5, -0.08), (2.1, 0.7, 0.08), 'wood_dark')
    prism('Body', [(-1.0, 2.2), (1.0, 2.2), (1.0, 2.6), (-1.0, 2.3)], -2.4, 2.4, 'wood', plane='zy')
    span('Body', (-2.4, 2.6, 0.8), (2.4, 2.68, 1.0), 'wood_dark')
    slope = lambda z: 2.3 + (z + 1.0) * 0.15     # noqa: E731
    for x0, x1, col in ((-1.05, -0.02, 'cream'), (0.02, 1.05, 'cream')):
        prism('Body', [(-0.7, slope(-0.7) + 0.02), (0.55, slope(0.55) + 0.02), (0.55, slope(0.55) + 0.1),
                       (-0.7, slope(-0.7) + 0.1)], x0, x1, col, plane='zy')
    prism('Body', [(-0.72, slope(-0.72) + 0.005), (0.57, slope(0.57) + 0.005), (0.57, slope(0.57) + 0.04),
                   (-0.72, slope(-0.72) + 0.04)], -1.1, 1.1, 'book_a', plane='zy')
    cyl('Body', (1.7, 2.68, 0.9), 0.08, 0.03, 'black', n=6)
    stand()
    done("the Quiet Library's reading desk: a sloped lectern top with an open book, dark legs and stretchers")


def f_pipe_organ():
    furn('PipeOrgan')
    span('Body', (-1.8, 0, -0.6), (1.8, 2.6, 0.6), 'wood_dark', bevel=0.1)
    span('Body', (-1.6, 2.2, -0.75), (1.6, 2.45, -0.15), 'white', bevel=0.03)
    # The upper case runs back under the pipes (floor-level elevations 2026-10-21: they stood on nothing).
    span('Body', (-1.8, 2.6, -0.2), (1.8, 3.4, 1.3), 'wood_dark', bevel=0.08)
    for i, h in enumerate((4.0, 4.8, 5.6, 6.6, 5.6, 4.8, 4.0)):
        x = -1.5 + i * 0.5
        cyl('Body', (x, 3.4, 1.05), 0.22, h - 3.4, 'gold', n=8)
        lathe('Body', [(0.22, h), (0, h + 0.3)], 'gold', n=8, base=(x, 0, 1.05))
        box('Body', (x, 3.9, 0.82), (0.2, 0.3, 0.04), 'black')
    span('Body', (-1.2, 0, -1.6), (1.2, 1.3, -1.0), 'wood', bevel=0.06)
    K.refit_decor()
    stand()
    done("Decor_PipeOrgan's geometry as furniture (the Organ Hall's key piece): seven gold pipes, a dark console, "
         "its bench; a Wall piece, its back on the wall")


def f_nightstand():
    furn('Nightstand')
    for x in (-0.82, 0.82):
        for z in (-0.62, 0.62):
            span('Body', (x - 0.12, 0, z - 0.12), (x + 0.12, 0.35, z + 0.12), 'wood_dark')
    span('Body', (-1.0, 0.3, -0.8), (1.0, 2.0, 0.8), 'wood', bevel=0.08)
    span('Body', (-1.08, 2.0, -0.88), (1.08, 2.15, 0.88), 'wood_dark', bevel=0.04)
    span('Body', (-0.85, 1.3, -0.84), (0.85, 1.85, -0.78), 'wood_light', bevel=0.03)
    span('Body', (-0.85, 0.45, -0.84), (0.85, 1.15, -0.78), 'wood_light', bevel=0.03)
    for y in (1.57, 0.8):
        sphere('Body', (0, y, -0.88), 0.08, 'gold', n=6, rings=3)
    span('Body', (-0.6, 2.15, -0.3), (0.2, 2.3, 0.4), 'book_a', bevel=0.02)
    span('Body', (-0.5, 2.3, -0.2), (0.1, 2.42, 0.3), 'book_b', bevel=0.02)
    stand()
    done('a little bedside cabinet: a drawer and a door with gold knobs, two books on top')


def f_wardrobe():
    furn('Wardrobe')
    for x in (-1.9, 1.9):
        for z in (-0.65, 0.65):
            lathe('Body', [(0.16, 0), (0.22, 0.18), (0.17, 0.38)], 'wood_dark', n=6, base=(x, 0, z))
    span('Body', (-2.2, 0.35, -0.9), (2.2, 5.6, 0.9), 'plum_dark', bevel=0.1)
    for x0, x1 in ((-2.0, -0.04), (0.04, 2.0)):
        span('Body', (x0, 0.6, -0.95), (x1, 5.35, -0.88), 'plum', bevel=0.04)
        a, b = x0 + 0.3, x1 - 0.3
        pts = ([(a, 1.0), (b, 1.0), (b, 4.2)] + [(x, y) for x, y in reversed(arch_points(a, b, 4.2, 5.0, n=3))][1:-1]
               + [(a, 4.2)])
        prism('Body', pts, -0.98, -0.94, 'wood_dark', plane='xy')
    for x in (-0.22, 0.22):
        sphere('Body', (x, 3.0, -0.99), 0.1, 'gold', n=6, rings=3)
    span('Body', (-2.35, 5.6, -1.05), (2.35, 5.82, 1.05), 'gold', bevel=0.05)
    prism('Body', [(-1.0, 5.82), (1.0, 5.82), (0.0, 6.02)], -0.9, 0.9, 'gold', plane='xy')
    stand()
    done('a tall plum wardrobe: two doors with dark gothic-arched panels, gold knobs, a gold cornice')


def f_writing_desk():
    furn('WritingDesk')
    for x in (-2.15, 2.15):
        for z in (-0.75, 0.75):
            lathe('Body', [(0.14, 0), (0.1, 0.4), (0.15, 1.2), (0.11, 1.9)], 'wood_dark', n=6, base=(x, 0, z))
    span('Body', (-2.3, 1.88, -0.9), (2.3, 2.36, 0.9), 'wood_dark', bevel=0.04)
    span('Body', (-2.45, 2.35, -1.0), (2.45, 2.6, 1.0), 'wood', bevel=0.06)
    span('Body', (-0.8, 1.95, -0.95), (0.8, 2.3, -0.9), 'wood_light', bevel=0.02)
    sphere('Body', (0, 2.12, -0.98), 0.07, 'gold', n=6, rings=3)
    span('Body', (-0.9, 2.6, -0.55), (0.4, 2.63, 0.3), 'cream')
    cyl('Body', (1.4, 2.6, 0.4), 0.2, 0.22, 'black', n=8)
    cyl('Body', (0, 0, 0), 0.04, 1.1, 'white', n=4, m=at((-0.2, 2.67, -0.1), rz=-80, ry=20))
    stand()
    done('a writing desk on turned legs: a drawer, a sheet of paper, an inkpot and a quill')


def f_dining_table():
    furn('DiningTable')
    for x in (-2.15, 2.15):
        for z in (-2.15, 2.15):
            lathe('Body', [(0.16, 0), (0.12, 0.5), (0.18, 1.3), (0.13, 2.3)], 'wood_dark', n=6, base=(x, 0, z))
    span('Body', (-2.3, 2.0, -2.3), (2.3, 2.36, 2.3), 'wood_dark', bevel=0.04)
    span('Body', (-2.5, 2.35, -2.5), (2.5, 2.6, 2.5), 'wood', bevel=0.06)
    span('Body', (-0.8, 2.6, -2.4), (0.8, 2.63, 2.4), 'crimson')
    for x, z in ((-1.5, -1.5), (1.5, -1.5), (-1.5, 1.5), (1.5, 1.5)):
        cyl('Body', (x, 2.6, z), 0.45, 0.05, 'white', n=10)
    _HM['pumpkin']('Body', (0, 2.63 + 0.14 * 0.78, 0), 0.14)
    stand()
    done('a square dining table on turned legs: a crimson runner, four white plates, a small pumpkin')


def f_buffet():
    furn('BreakfastBuffet')
    for x in (-3.7, 3.7):
        for z in (-0.65, 0.65):
            lathe('Body', [(0.16, 0), (0.22, 0.16), (0.17, 0.32)], 'wood_dark', n=6, base=(x, 0, z))
    span('Body', (-4.0, 0.3, -0.92), (4.0, 2.5, 0.92), 'wood_dark', bevel=0.08)
    span('Body', (-4.1, 2.5, -1.05), (4.1, 2.65, 1.05), 'wood', bevel=0.05)
    for k in range(3):
        x0 = -3.8 + k * 2.55
        span('Body', (x0, 0.55, -0.97), (x0 + 2.45, 2.25, -0.9), 'wood', bevel=0.04)
        sphere('Body', (x0 + 1.225, 1.4, -1.0), 0.08, 'gold', n=6, rings=3)
    for x in (-2.6, 0.0, 2.6):
        cyl('Body', (x, 2.65, 0.0), 0.75, 0.04, 'white', n=10)
        lathe('Body', [(0.6, 2.69), (0.58, 2.8), (0.42, 2.98), (0.0, 3.04)], 'gold', n=10, base=(x, 0, 0))
        sphere('Body', (x, 3.06, 0), 0.07, 'gold', n=6, rings=3)
    stand()
    done('a sideboard with three cupboard doors, three gold cloches on white trays')


def f_bar_stool():
    furn('BarStool')
    # The seat at 2.6 (blind review 2026-10-21: at 2.0 it sat a guest chin-high at counters 3.4-3.8): the
    # approved stool raised 0.6 on a longer pedestal, the foot ring where a seated person's feet hang.
    cyl('Body', (0, 0, -0.2), 0.75, 0.1, 'iron', n=10)
    cyl('Body', (0, 0.1, -0.2), 0.13, 2.26, 'iron', n=6)
    lathe('Body', [(0.55, 0.55), (0.6, 0.55), (0.6, 0.62), (0.55, 0.62)], 'gold', n=10, base=(0, 0, -0.2),
          closed=True)
    for k in range(4):
        box('Body', (0, 0, 0), (0.44, 0.05, 0.06), 'gold',
            m=at((0, 0.585, -0.2), ry=45 + 90 * k) @ Matrix.Translation((0.34, 0, 0)))
    span('Body', (-1.0, 2.32, -0.9), (1.0, 2.44, 0.8), 'wood_dark', bevel=0.03)
    span('Body', (-1.04, 2.44, -0.88), (1.04, 2.6, 0.48), 'crimson', bevel=0.05)
    for x in (-0.9, 0.9):
        span('Body', (x - 0.09, 2.44, 0.56), (x + 0.09, 3.1, 0.74), 'wood_dark', bevel=0.02)
    span('Body', (-1.0, 2.98, 0.54), (1.0, 3.2, 0.76), 'wood_dark', bevel=0.04)
    bar_seat(-1.0, 1.0, -0.85, 0.45, 2.6)
    use((0, 2.6, -0.2), (0, 0, -1), 'Sit')
    done('a bar stool on an iron pedestal with a gold foot ring, a crimson cushion at 2.6, a low back')


def f_pool_table():
    furn('PoolTable')
    for x in (-3.4, 0.0, 3.4):
        for z in (-1.9, 1.9):
            lathe('Body', [(0.22, 0), (0.16, 0.4), (0.24, 0.9), (0.2, 1.25)], 'wood_dark', n=6, base=(x, 0, z))
    span('Body', (-3.9, 1.2, -2.4), (3.9, 2.3, 2.4), 'wood_dark', bevel=0.1)
    span('Body', (-3.5, 2.28, -2.0), (3.5, 2.42, 2.0), 'moss')
    for (x0, z0, x1, z1) in ((-3.9, -2.4, 3.9, -2.0), (-3.9, 2.0, 3.9, 2.4), (-3.9, -2.0, -3.5, 2.0),
                             (3.5, -2.0, 3.9, 2.0)):
        span('Body', (x0, 2.3, z0), (x1, 2.6, z1), 'wood', bevel=0.04)
    for x in (-3.42, 0.0, 3.42):
        for z in (-1.92, 1.92):
            cyl('Body', (x, 2.42, z), 0.22, 0.02, 'black', n=8)
    for x, z, colr in ((-1.6, 0.2, 'white'), (1.2, -0.5, 'crimson'), (1.5, 0.3, 'amber'), (1.8, -0.1, 'violet'),
                       (2.1, 0.5, 'black')):
        sphere('Body', (x, 2.6, z), 0.18, colr, n=8, rings=4)
    stand()
    done('a pool table: dark wood on six turned legs, green baize, black pockets, five balls')


def f_card_table():
    furn('CardTable')
    lathe('Body', [(1.2, 0), (1.2, 0.12), (0.3, 0.3), (0.22, 1.8), (0.45, 2.3)], 'wood_dark', n=10)
    cyl('Body', (0, 2.3, 0), 2.45, 0.24, 'wood', n=16)
    cyl('Body', (0, 2.44, 0), 2.2, 0.16, 'moss', n=16)
    for k, (x, z, ang, colr) in enumerate(((-1.0, -0.9, 20, 'cream'), (0.9, -1.1, -15, 'cream'),
                                          (1.1, 0.8, 35, 'crimson'), (-0.9, 1.0, -30, 'cream'))):
        box('Body', (0, 0, 0), (0.55, 0.02 + 0.005 * k, 0.8), colr, m=at((x, 2.611 + 0.006 * k, z), ry=ang))
    for x, z, colr in ((0.2, 0.0, 'crimson'), (0.55, 0.15, 'gold'), (-0.3, 0.3, 'ink')):
        cyl('Body', (x, 2.6, z), 0.18, 0.2, colr, n=8)
    stand()
    done('a round card table: green baize in a wood rim on a pedestal, cards dealt, stacks of chips')


def f_bathtub():
    furn('Bathtub')
    sc = (2.3, 0.95)
    lathe('Body', [(0.0, 0.5), (0.8, 0.5), (1.05, 1.9), (1.12, 2.0), (0.96, 2.0), (0.9, 0.75), (0.0, 0.75)],
          'white', n=16, scale=sc)
    cyl('Body', (0, 1.25, 0), 0.885, 0.05, 'sky', n=16, scale=sc)
    for x in (-1.2, 1.2):
        for z in (-0.45, 0.45):
            sphere('Body', (x, 0.33, z), (0.24, 0.32, 0.2), 'gold', n=6, rings=4)
    cyl('Body', (2.38, 1.95, 0), 0.1, 0.32, 'gold', n=6)
    cyl('Body', (0, 0, 0), 0.07, 0.5, 'gold', n=6, m=at((2.38, 2.2, 0), rz=90))
    for x, z, r in ((-0.6, 0.3, 0.16), (-0.3, -0.25, 0.12), (0.5, 0.2, 0.14)):
        sphere('Body', (x, 1.3, z), (r, r * 0.6, r), 'white', n=6, rings=3)
    use((-0.3, 1.3, 0.0), (1, 0, 0), 'Lie',
        waive='a tub is lain in reclining: its 2 x 1 squares (Pieces) hold 4.4 inside, a straight 5-stud person '
              "needs 3 x 1 (August's call)")
    done('a white clawfoot tub on gold feet, full to the middle, a gold tap at its foot end')


def f_floor_lamp():
    furn('FloorLamp')
    lathe('Body', [(0.0, 0.0), (0.7, 0.0), (0.7, 0.08), (0.3, 0.22), (0.0, 0.25)], 'gold', n=10)
    cyl('Body', (0, 0.2, 0), 0.08, 4.0, 'iron', n=6)
    sphere('Glow_Warm_1', (0, 4.12, 0), (0.22, 0.26, 0.22), 'lamp', n=8, rings=4)
    lathe('Body', [(0.95, 4.2), (0.55, 5.35), (0.0, 5.38)], 'violet', n=10)
    lathe('Body', [(0.94, 4.12), (1.0, 4.12), (1.0, 4.22), (0.94, 4.22)], 'gold', n=10, closed=True)
    sphere('Body', (0, 5.45, 0), 0.07, 'gold', n=6, rings=3)
    stand()
    done('a standing lamp: an iron stem on a gold foot, a violet shade with a gold hem, the bulb glowing')


# --- Frostfang Lodge -----------------------------------------------------------------------------------

def ff_bed(hw=1.95, frame='wood_light', quilt=('red', 'cream'), pillow='snow', head='log', head_col=None,
           mattress='cream', foot=True):
    """The Lodge's bed (build_hotel_frostfang_lodge.lodge_bed), centred, with the faces that shared a plane
    moved apart."""
    zf, zb = ZF, ZB
    for x in (-hw + 0.22, hw - 0.22):
        for z in (zf + 0.22, zb - 0.22):
            cyl('Body', (x, 0, z), 0.2, 1.6 if (foot and z < 0) else 0.7, frame, n=6)
    span('Body', (-hw, 0.6, zf), (hw, 1.1, zb), frame, bevel=0.08)
    span('Body', (-hw + 0.1, 1.1, zf + 0.1), (hw - 0.1, 1.65, zb - 0.1), mattress, bevel=0.15)
    a, b = quilt
    span('Body', (-hw + 0.02, 1.25, zf + 0.05), (hw - 0.02, 1.8, zf + 3.4), a, bevel=0.18)
    for x in (-1.1, 0.0, 1.1):
        span('Body', (x - 0.14, 1.79, zf + 0.15), (x + 0.14, 1.83, zf + 3.3), b)
    for z in (zf + 0.9, zf + 2.2):
        span('Body', (-hw + 0.1, 1.8, z - 0.14), (hw - 0.1, 1.845, z + 0.14), b)
    span('Body', (-hw + 0.05, 1.62, zf + 3.1), (hw - 0.05, 1.86, zf + 3.6), 'cream', bevel=0.08)
    span('Body', (-1.3, 1.6, zb - 1.5), (1.3, 2.25, zb - 0.35), pillow, bevel=0.22)
    head_col = head_col or frame
    if head == 'ice':
        dome = [(1.9 * math.cos(math.pi * i / 8), 1.1 + 2.5 * math.sin(math.pi * i / 8)) for i in range(9)]
        prism('Body', dome, zb - 0.3, zb + 0.02, head_col, plane='xy')
        span('Body', (-1.9, 0.58, zb - 0.32), (1.9, 1.12, zb + 0.03), head_col)
        for x in (-0.95, 0.95):
            span('Body', (x - 0.05, 2.5, zb - 0.34), (x + 0.05, 3.05, zb - 0.3), 'frost')
        for y in (2.45, 3.1):
            hwid = 1.9 * math.sqrt(max(0.0, 1 - ((y - 1.1) / 2.5) ** 2)) - 0.1
            span('Body', (-hwid, y - 0.05, zb - 0.35), (hwid, y + 0.05, zb - 0.31), 'frost')
    if foot:
        cyl('Body', (0, 0, 0), 0.24, 2 * hw - 0.16, frame, n=8, m=at((-hw + 0.08, 1.55, zf + 0.24), rz=-90))
    return zf, zb


def ff_furniture():
    return {'IceBed': f_ice_bed, 'IceSlab': f_ice_slab, 'SnowNest': f_snow_nest, 'KnittingChair': f_knitting_chair,
            'GlacierCoil': f_glacier_coil, 'StarHammock': f_star_hammock, 'CocoaBar': f_cocoa_bar,
            'SkyLounger': f_sky_lounger}


def f_ice_bed():
    furn('IceBed')
    ff_bed(frame='wood_light', quilt=('red', 'cream'), head='ice', head_col='ice')
    use((0, 1.83, -0.05), (0, 0, -1), 'Lie')
    done("the Igloo Room's bed: a red plaid quilt, an igloo-dome ice headboard with frost courses")


def f_ice_slab():
    furn('IceSlab')
    zf, zb = ZF, ZB
    span('Body', (-1.95, 0, zf), (1.95, 0.7, zb), 'stone_dark', bevel=0.15)
    span('Body', (-1.85, 0.7, zf + 0.1), (1.85, 1.2, zb - 0.1), 'stone', bevel=0.12)
    span('Body', (-1.9, 1.0, zf + 0.05), (1.9, 1.55, zf + 3.6), 'fur', bevel=0.22)
    for x in (-1.2, 0.0, 1.2):
        span('Body', (x - 0.2, 1.54, zf + 0.2), (x + 0.2, 1.58, zf + 3.4), 'fur_shade')
    span('Body', (-1.3, 1.2, zb - 1.5), (1.3, 1.85, zb - 0.35), 'snow', bevel=0.22)
    rock = [(-2.0, 0.0), (2.0, 0.0), (2.0, 2.6), (1.4, 3.4), (0.5, 3.1), (-0.3, 3.8), (-1.2, 3.2), (-2.0, 2.8)]
    prism('Body', rock, zb - 0.32, zb + 0.04, 'stone_dark', plane='xy')
    for x, y in ((-0.3, 3.8), (1.4, 3.4)):
        sphere('Body', (x, y - 0.05, zb - 0.14), (0.36, 0.12, 0.2), 'snow', n=6, rings=3)
    use((0, 1.58, -0.05), (0, 0, -1), 'Lie')
    done("the Ice Cave's stone slab bed under furs, a rock headboard with snow on it")


def f_snow_nest():
    furn('SnowNest')
    lathe('Body', [(1.35, 0.0), (1.95, 0.0), (1.95, 0.9), (1.75, 1.35), (1.4, 1.2)], 'fur', n=12,
          scale=(1, 1.42), closed=True)
    lathe('Body', [(0, 0.0), (1.45, 0.0), (1.45, 0.6), (0, 0.75)], 'fur_shade', n=12, scale=(1, 1.42))
    lathe('Body', [(0, 0.6), (1.0, 0.65), (0.6, 0.95), (0, 1.0)], 'ice_deep', n=10, base=(0, 0, -0.8),
          scale=(1.2, 0.8))
    sphere('Body', (0, 1.05, 1.4), (0.8, 0.3, 0.45), 'snow', n=8, rings=4)
    stretch(1.3, 1.3)
    use((0, surface_y(0, 0), 0), (0, 0, -1), 'Lie')     # centred: the head on the pillow, the feet in the rim
    done("the Yeti Den's round fur nest, a third larger for its 3 x 3: a blue blanket, a snow pillow")


def f_knitting_chair():
    furn('KnittingChair')
    lo = lambda z: 0.25 * (z / 1.7) ** 2           # noqa: E731  the rockers' underside
    zs_ = [-1.7 + 3.4 * i / 10 for i in range(11)]
    for x in (-1.05, 1.05):
        pts = [(z, lo(z)) for z in zs_] + [(z, lo(z) + 0.25) for z in reversed(zs_)]
        prism('Body', pts, x - 0.08, x + 0.08, 'wood', plane='zy')
        for z in (-0.8, 0.45):
            span('Body', (x - 0.07, lo(z) + 0.2, z - 0.07), (x + 0.07, 1.52, z + 0.07), 'wood_dark')
    span('Body', (-1.08, 1.5, -1.0), (1.08, 1.65, 0.6), 'wood', bevel=0.04)
    span('Body', (-1.02, 1.65, -0.96), (1.02, 1.75, 0.55), 'violet', bevel=0.04)
    for x in (-1.0, 1.0):
        span('Body', (x - 0.09, 0.3, 0.66), (x + 0.09, 3.45, 0.86), 'wood_dark', bevel=0.02)
        span('Body', (x * 1.12 - 0.1, 2.42, -0.9), (x * 1.12 + 0.1, 2.56, 0.8), 'wood', bevel=0.03)
        span('Body', (x * 1.12 - 0.06, 1.65, -0.8), (x * 1.12 + 0.06, 2.42, -0.68), 'wood_dark')
    span('Body', (-0.95, 1.6, 0.68), (0.95, 1.82, 0.84), 'wood_dark', bevel=0.02)
    for k in range(4):
        span('Body', (-0.7 + k * 0.47 - 0.08, 1.75, 0.7), (-0.7 + k * 0.47 + 0.08, 3.3, 0.8), 'wood')
    span('Body', (-1.1, 3.3, 0.62), (1.1, 3.6, 0.9), 'wood_dark', bevel=0.05)
    # The blanket hangs on the back slats and under the top rail (it stood 0.06 behind them).
    span('Body', (-0.85, 2.2, 0.79), (0.85, 3.32, 0.95), 'lilac', bevel=0.03)
    for y in (2.45, 2.95):
        span('Body', (-0.86, y, 0.77), (0.86, y + 0.12, 0.97), 'snow')
    lathe('Body', [(0.45, 0), (0.6, 0.55), (0.62, 0.62), (0.5, 0.62), (0.4, 0.08)], 'wood_light', n=10,
          base=(1.95, 0, -1.4), closed=True)
    cyl('Body', (1.95, 0.02, -1.4), 0.46, 0.1, 'wood', n=10)
    for k, (dx, dz, colr) in enumerate(((-0.15, 0.1, 'ice_deep'), (0.2, -0.1, 'pink_light'), (0.0, 0.25, 'mint'))):
        sphere('Body', (1.95 + dx, 0.62 + 0.05 * k, -1.4 + dz), 0.24, colr, n=8, rings=4)
    for k, ang in enumerate((-20, 20)):
        cyl('Body', (0, 0, 0), 0.04, 0.9, 'gold', n=4, m=at((1.95, 0.7, -1.35 + 0.12 * k), rx=ang, rz=-15))
    K.seat(-1.0, 1.0, -0.94, 0.53, 1.75)
    use((0, 1.75, -0.3), (0, 0, -1), 'Sit')
    done('a rocking chair: a violet cushion, a lilac knitted blanket with snow stripes over its back, a yarn basket')


def f_glacier_coil():
    furn('GlacierCoil')
    lathe('Body', [(1.45, 0.0), (1.95, 0.0), (1.95, 1.0), (1.7, 1.45), (1.45, 1.3)], 'ice_deep', n=14,
          scale=(1, 1.4), closed=True)
    lathe('Body', [(1.96, 0.45), (1.98, 0.45), (1.98, 0.62), (1.96, 0.62)], 'gold', n=14, scale=(1, 1.4),
          closed=True)
    lathe('Body', [(0, 0.0), (1.5, 0.0), (1.5, 0.75), (0, 0.9)], 'frost', n=14, scale=(1, 1.4))
    lathe('Body', [(0, 0.75), (1.1, 0.8), (0.7, 1.12), (0, 1.15)], 'navy', n=10, base=(0, 0, -0.7), scale=(1.2, 0.9))
    sphere('Body', (0, 1.15, 1.4), (0.85, 0.3, 0.42), 'snow', n=8, rings=4)
    for x in (-1.65, 1.65):
        lathe('Body', [(0.28, 0), (0.28, 3.6), (0, 4.4)], 'ice', n=6, base=(x, 0, 2.52))
        cyl('Body', (x, 3.4, 2.52), 0.33, 0.2, 'gold', n=6)
    stretch(1.3, 1.3)
    use((0, surface_y(0, 0), 0), (0, 0, -1), 'Lie')     # centred: 5.28 inside the rim, the head on the pillow
    done("the Glacier Suite's coiled round bed, a third larger: gold-banded ice, a navy blanket, two crystal pillars")


def f_star_hammock():
    furn('StarHammock')
    for x in (-3.5, 3.5):
        cyl('Body', (x, 0, 0), 0.55, 0.15, 'log_dark', n=8)
        cyl('Body', (x, 0.15, 0), 0.28, 2.6, 'log', n=8)
        sphere('Body', (x, 2.78, 0), (0.34, 0.2, 0.34), 'snow', n=8, rings=4)
    n, half = 9, 3.3
    sag = lambda x: 1.3 + 1.1 * (x / half) ** 2     # noqa: E731
    for i in range(n):
        xa, xb = -half + 2 * half * i / n, -half + 2 * half * (i + 1) / n
        ya, yb = sag(xa), sag(xb)
        ln = math.hypot(xb - xa, yb - ya) + 0.06
        ang = math.degrees(math.atan2(yb - ya, xb - xa))
        box('Body', (0, 0, 0), (ln, 0.15, 2.0 - 0.01 * (i % 2)), 'navy', m=at(((xa + xb) / 2, (ya + yb) / 2, 0), rz=ang))
    for x in (-half, half):
        for z in (-0.9, 0.9):
            a, b = Vector((x, sag(x), z)), Vector((x * 1.08, 2.55, z * 0.3))
            d = b - a
            cyl('Body', (0, 0, 0), 0.04, d.length, 'cream', n=4,
                m=Matrix.Translation(a) @ d.to_track_quat('Y', 'Z').to_matrix().to_4x4())
    sphere('Body', (-2.4, sag(-2.4) + 0.3, 0), (0.5, 0.25, 0.65), 'snow', n=8, rings=4)

    def top(x):         # the sling's top along its chords
        i = min(n - 1, max(0, int((x + half) / (2 * half) * n)))
        xa, xb = -half + 2 * half * i / n, -half + 2 * half * (i + 1) / n
        ang = math.atan2(sag(xb) - sag(xa), xb - xa)
        return sag(xa) + (x - xa) / (xb - xa) * (sag(xb) - sag(xa)) + 0.075 / math.cos(ang)
    for x, z in ((-0.9, -0.4), (0.4, 0.5), (1.2, -0.6), (-0.2, 0.7), (0.9, 0.1)):
        star = [(0.18 * math.cos(math.pi / 2 + k * math.pi / 5) * (1 if k % 2 == 0 else 0.45),
                 0.18 * math.sin(math.pi / 2 + k * math.pi / 5) * (1 if k % 2 == 0 else 0.45)) for k in range(10)]
        y = top(x)
        prism('Body', [(px + x, pz + z) for px, pz in star], y - 0.01, y + 0.02, 'yellow', plane='xz')
    use((0.2, top(0.2), 0.0), (1, 0, 0), 'Lie', rise=(0.8, 1.1))     # the sling rises to its ends
    done('a hammock of navy cloth with yellow stars, slung between two snow-capped log posts')


def _ff_mug(part, c, r=0.32, h=0.6, col='red', band='cream'):
    x, y, z = c
    cyl(part, (x, y, z), r, h, col, n=8)
    cyl(part, (x, y + h * 0.4, z), r + 0.02, h * 0.2, band, n=8)
    cyl(part, (x, y + h - 0.04, z), r - 0.05, 0.06, 'cocoa', n=8)
    box(part, (x + r + 0.03, y + h * 0.5, z), (0.14, h * 0.55, 0.12), col)     # its handle into the mug's side


def f_cocoa_bar():
    furn('CocoaBar')
    span('Body', (-4.0, 0, -0.85), (4.0, 3.2, 1.0), 'cocoa_dark', bevel=0.1)
    for i in range(13):
        x = -3.6 + i * 0.6
        span('Body', (x - 0.15, 0.2, -0.88), (x + 0.15, 3.0, -0.8), 'red' if i % 2 else 'cream')
    span('Body', (-4.1, 3.2, -1.05), (4.1, 3.45, 1.1), 'wood_light', bevel=0.06)
    lathe('Body', [(0.45, 3.45), (0.6, 3.7), (0.62, 4.4), (0.45, 4.6), (0.15, 4.75), (0, 4.8)], 'red', n=10,
          base=(-2.4, 0, 0.3))
    box('Body', (-1.7, 4.2, 0.3), (0.5, 0.14, 0.16), 'red')
    for x, colr in ((0.4, 'red'), (1.3, 'ice_deep'), (2.2, 'cream')):
        _ff_mug('Body', (x, 3.45, 0.2), r=0.26, h=0.5, col=colr)
        for k in range(2):
            box('Body', (x - 0.08 + 0.16 * k, 3.98 + 0.01 * k, 0.2), (0.14, 0.12, 0.14), 'white')
    lathe('Body', [(0.3, 3.45), (0.32, 4.1), (0.2, 4.2), (0.22, 4.35)], 'ice', n=8, base=(3.3, 0, 0.5))
    stand()
    done("the Cocoa Lounge's candy-cane counter: a big red cocoa pot, mugs with marshmallows, a jar")


def f_sky_lounger():
    furn('SkyLounger')
    for x in (-1.25, 1.25):
        for z in (-3.0, 0.9):
            span('Body', (x - 0.12, 0, z - 0.12), (x + 0.12, 0.65, z + 0.12), 'wood_dark')
    span('Body', (-1.4, 0.6, -3.3), (1.4, 0.85, 1.25), 'wood', bevel=0.05)
    span('Body', (-1.3, 0.85, -3.2), (1.3, 1.05, 1.15), 'teal', bevel=0.08)
    back = at((0, 0.85, 1.25), rx=-14)
    box('Body', (0, 0.12, 1.25), (2.8, 0.25, 2.5), 'wood', bevel=0.05, m=back)
    box('Body', (0, 0.34, 1.25), (2.6, 0.2, 2.4), 'teal', bevel=0.08, m=back)
    span('Body', (-1.35, 0.95, -3.1), (1.35, 1.15, -0.3), 'red', bevel=0.08)
    for z in (-2.5, -1.4):
        span('Body', (-1.36, 1.14, z - 0.12), (1.36, 1.17, z + 0.12), 'cream')
    span('Body', (-0.9, 1.15, 1.35), (0.9, 1.6, 1.95), 'snow', bevel=0.18)
    use((0, 1.15, -0.7), (0, 0, -1), 'Lie')     # the head on the pillow, the feet on the cushion's end
    done('a deck lounger: teal cushions, its back raised at the head, a red plaid blanket over the legs')


# --- Styles -------------------------------------------------------------------------------------------

def _courses(y0, y1, n, cols):
    k = (y1 - y0) / n
    return [(y0 + i * k, y0 + (i + 1) * k, cols[i % len(cols)]) for i in range(n)]


STYLES = {
    'haunted_manor': dict(
        title='Haunted Manor: inner walls, a door and furniture (built rooms)', location=1, palette=HM_PALETTE,
        body=[(0.0, 3.2, 'plum_dark'), (3.2, WALL, 'lilac')], reveal='gold', skirting='wood_dark', chair='gold',
        picture='gold', crown='gold', arch='pointed', trim='wood_dark', trim_base='plum_deep', keystone='gold',
        post=[(0.0, 0.6, 'wood_dark'), (0.6, WALL - 0.6, 'plum_deep'), (WALL - 0.6, POST_TOP, 'gold')],
        wall_note='plum wainscot under lilac paper, as the Standard Room; gold chair and picture rails and crown, '
                  'dark skirting, on both faces',
        door_note='a pointed arch, dark wood trim with a gold keystone, plinth blocks, both faces',
        post_note='plum with a dark wood foot and a gold cap',
        furniture=hm_furniture, locations=(1, 0)),
    'frostfang_lodge': dict(
        title='Frostfang Lodge: inner walls, a door and furniture (built rooms)', location=2, palette=FF_PALETTE,
        body=[(0.0, 3.2, 'wood_dark')] + _courses(3.2, WALL, 13, ('log', 'log_dark')), reveal='log_dark',
        skirting='log_dark', chair='wood_light', picture='wood_light', crown='snow', arch='round', trim='log_dark',
        trim_base='wood_dark', keystone='snow',
        post=[(0.0, 0.6, 'log_dark'), (0.6, WALL - 0.6, 'log'), (WALL - 0.6, POST_TOP, 'snow')],
        wall_note='log courses over a dark wainscot, as the lodge rooms; light wood rails, a snow cornice, both faces',
        door_note='a round arch, dark log trim with a snow keystone, plinth blocks, both faces',
        post_note='a log post with a dark foot and a snow cap',
        furniture=ff_furniture, locations=(2,)),
}

_HM = _lift(TOOLS / 'build_hotel_haunted_manor.py', ['pumpkin'], {'sphere': sphere, 'cyl': cyl})


# --- Review (Workbench on light grey: Studio is running, no EEVEE or Cycles) --------------------------

def _import(path):
    before = set(bpy.data.objects)
    bpy.context.scene.unit_settings.scale_length = .01
    bpy.ops.import_scene.fbx(filepath=str(path))
    new = [o for o in bpy.data.objects if o not in before]
    keep = []
    for ob in new:
        base = ob.name.split('.')[0]
        if ob.type != 'MESH' or base in ('Root', 'LOD_Proxy'):
            bpy.data.objects.remove(ob)
            continue
        keep.append(ob)
    return keep


def place(fbx, name, pos, ang=0.0):
    """A piece from its FBX at a Roblox position, turned `ang` degrees about Y."""
    objs = _import(fbx / f'{name}.fbx')
    M = Matrix.Translation(K.rb2bl(pos)) @ Matrix.Rotation(math.radians(ang), 4, 'Z')
    bpy.context.view_layer.update()
    for ob in objs:
        ob.matrix_world = M @ ob.matrix_world
        ob['piece'] = name
    return objs


ROOM = [    # a 2 x 2 cell room's corner with a T and a free end: (name, (x, z), turn)
    ('Wall_Half', (3, 0), 0), ('Wall_Door', (9, 0), 0),
    ('Wall_Half', (0, 3), 90), ('Wall_Half', (0, 9), 90),
    ('Wall_Half', (3, 12), 0), ('Wall_Half', (9, 12), 0),
    ('Wall_Half', (12, 3), 90), ('Wall_Door', (12, 9), 90),
    ('Wall_Half', (6, 15), 90), ('Wall_Half', (6, 21), 90),
    ('Wall_Half', (15, 0), 0), ('Wall_Half', (21, 0), 0),
]
POSTS = [(0, 0), (12, 0), (0, 12), (12, 12), (6, 12), (6, 24), (24, 0)]


def render(path, direction, res, lo, hi, scale=1.04):
    sc = bpy.context.scene
    sc.render.engine = 'BLENDER_WORKBENCH'
    sc.display.shading.light = 'STUDIO'
    sc.display.shading.color_type = 'TEXTURE'
    sc.display.shading.show_shadows = False
    sc.display.shading.show_cavity = True
    sc.render.resolution_x, sc.render.resolution_y = res
    sc.render.film_transparent = False
    sc.world = sc.world or bpy.data.worlds.new('World')
    sc.world.color = (0.80, 0.80, 0.82)        # light grey
    lo, hi = K.rb2bl(lo), K.rb2bl(hi)
    lo, hi = Vector(map(min, lo, hi)), Vector(map(max, lo, hi))
    centre = (lo + hi) / 2
    pts = [Vector((x, y, z)) for x in (lo.x, hi.x) for y in (lo.y, hi.y) for z in (lo.z, hi.z)]
    cam = sc.camera
    if cam is None:
        cam = bpy.data.objects.new('Review', bpy.data.cameras.new('Review'))
        sc.collection.objects.link(cam)
        sc.camera = cam
    cam.data.type = 'ORTHO'
    cam.data.clip_end = 3000
    d = K.rb2bl(direction).normalized()
    cam.location = centre + d * 600
    cam.rotation_euler = (-d).to_track_quat('-Z', 'Y').to_euler()
    rot = cam.rotation_euler.to_matrix()
    right, up = rot @ Vector((1, 0, 0)), rot @ Vector((0, 1, 0))
    xs = [(p - centre).dot(right) for p in pts]
    ys = [(p - centre).dot(up) for p in pts]
    cam.data.ortho_scale = max(max(xs) - min(xs), (max(ys) - min(ys)) * res[0] / res[1]) * scale
    cam.location += right * (max(xs) + min(xs)) / 2 + up * (max(ys) + min(ys)) / 2
    path.parent.mkdir(parents=True, exist_ok=True)
    sc.render.filepath = str(path)
    bpy.ops.render.render(write_still=True)
    print(f'REVIEW {path}', flush=True)
    return path


def clear():
    for ob in list(bpy.data.objects):
        bpy.data.objects.remove(ob)


_lift(TOOLS / 'build_facades.py', ['_poly_area', '_clip'], _REV)


def assembly_check(objs, posts, min_area=2e-4, tol=0.003):
    """Faces of two placed pieces lying on each other (coplanar, the same way, overlapping by more than
    min_area), unless the overlap lies inside a post (MODELS.md: the post covers every joint but a straight
    run). Triangles in Roblox coordinates; the overlap is clipped exactly (build_facades' Sutherland-Hodgman)."""
    tris, tags = [], []
    bpy.context.view_layer.update()
    for ob in objs:
        if ob.type != 'MESH' or 'inst' not in ob:
            continue
        me, mw = ob.data, ob.matrix_world
        me.calc_loop_triangles()
        for t in me.loop_triangles:
            tris.append(tuple(K.bl2rb(mw @ me.vertices[i].co) for i in t.vertices))
            tags.append(ob['inst'])
    groups = {}
    for i, (a, b, c) in enumerate(tris):
        n = (b - a).cross(c - a)
        if n.length < 1e-9:
            continue
        n.normalize()
        groups.setdefault((round(n.x, 2), round(n.y, 2), round(n.z, 2)), []).append((n.dot(a), i, n))

    def in_post(p):
        return any(abs(p.x - px) <= POST + 1e-3 and abs(p.z - pz) <= POST + 1e-3 and -1e-3 <= p.y <= POST_TOP + 1e-3
                   for px, pz in posts)
    found, hidden = [], 0
    for items in groups.values():
        items.sort(key=lambda e: e[0])
        for k, (d1, i, n) in enumerate(items):
            for d2, j, _ in items[k + 1:]:
                if d2 - d1 > tol:
                    break
                if tags[i] == tags[j]:
                    continue
                u = (Vector((1, 0, 0)) if abs(n.x) < 0.9 else Vector((0, 1, 0))).cross(n).normalized()
                v = n.cross(u)
                pa = [(p.dot(u), p.dot(v)) for p in tris[i]]
                pb = [(p.dot(u), p.dot(v)) for p in tris[j]]
                if _REV['_poly_area'](pa) < 0:
                    pa.reverse()
                if _REV['_poly_area'](pb) < 0:
                    pb.reverse()
                inter = _REV['_clip'](pa, pb)
                if len(inter) < 3 or abs(_REV['_poly_area'](inter)) <= min_area:
                    continue
                cu = sum(p[0] for p in inter) / len(inter)
                cv = sum(p[1] for p in inter) / len(inter)
                c3 = u * cu + v * cv + n * d1
                if in_post(c3):
                    hidden += 1
                    continue
                found.append(f'pieces {tags[i]} and {tags[j]} at {K.v3(c3, 2)} facing {K.v3(n, 2)}')
    return found, hidden


def review_walls(out, fbx):
    clear()
    objs = []
    for k, ((name, (x, z), ang)) in enumerate(ROOM + [('Wall_Post', p, 0) for p in POSTS]):
        new = place(fbx, name, (x, 0, z), ang)
        for ob in new:
            ob['inst'] = f'{name}@{x},{z}'
        objs += new
    faults, hidden = assembly_check(objs, POSTS)
    print(f'ASSEMBLY {len(faults)} visible overlaps, {hidden} inside posts', flush=True)
    _REV['_block']('floor', (-4, -0.3, -8), (28, 0, 26), (150, 150, 156))
    _REV['_person'](Vector((9, 0, 0)), -1.6)
    _REV['_person'](Vector((3, 0, 0)), 6.0)
    shots = []
    shots.append(render(out / 'walls_front.png', (-0.55, 0.75, -1.0), (900, 640), (-2, 0, -2), (25, 17.5, 25)))
    shots.append(render(out / 'walls_back.png', (0.6, 0.8, 1.0), (900, 640), (-2, 0, -2), (25, 17.5, 25)))
    shots.append(render(out / 'joint_corner.png', (-0.7, 0.45, -1.0), (900, 640), (10.5, 0, -1.2), (13.5, 17.5, 1.5)))
    shots.append(render(out / 'joint_tee.png', (0.8, 0.9, 1.0), (900, 640), (4.0, 11.0, 10.5), (8.0, 17.6, 14.0)))
    shots.append(render(out / 'door.png', (-0.25, 0.25, -1.0), (900, 640), (5.5, 0, -0.4), (12.6, 11.0, 0.4)))
    behind = [o for o in objs if float(o['inst'].split('@')[1].split(',')[1]) > 1.0 and not o.hide_render]
    for o in behind:     # a cutaway: only the front run, seen from inside the room
        o.hide_render = True
    shots.append(render(out / 'door_inside.png', (0.25, 0.25, 1.0), (900, 640), (5.5, 0, -0.4), (12.6, 11.0, 0.4)))
    for o in behind:
        o.hide_render = False
    # The door piece alone at the same angles: what is seen through the doorway in the room shots is the room
    # behind it (the far T joint's post, the side door), not the piece.
    clear()
    place(fbx, 'Wall_Door', (9, 0, 0), 0)
    _REV['_block']('floor', (4, -0.3, -3), (14, 0, 3), (150, 150, 156))
    shots.append(render(out / 'door_alone.png', (-0.25, 0.25, -1.0), (900, 640), (5.5, 0, -0.4), (12.6, 11.0, 0.4)))
    shots.append(render(out / 'door_alone_foot.png', (-0.6, 0.35, -1.0), (900, 640), (6.2, 0, -0.4), (8.4, 1.6, 0.4)))
    sheet = _REV['_compose']([[shots[0], shots[1]], [shots[2], shots[3]], [shots[4], shots[5]],
                              [shots[6], shots[7]]], out / 'walls_sheet.png')
    return faults, sheet


def _lying(use_pos, look):
    """The 5-stud person (_person's blocks) lying on its back on a Lie point: the head toward -look, the feet
    toward +look, the body's middle on the point."""
    skin, shirt, legs = (250, 200, 160), (70, 130, 200), (60, 60, 80)
    a = Vector((look[0], 0, look[2])).normalized()
    b = Vector((-a.z, 0, a.x))
    y0 = use_pos[1]
    p = Vector(use_pos)

    def blk(t0, t1, s0, s1, h, rgb):
        c = [p + a * t + b * s for t in (t0, t1) for s in (s0, s1)]
        lo = Vector((min(v.x for v in c), y0, min(v.z for v in c)))
        hi = Vector((max(v.x for v in c), y0 + h, max(v.z for v in c)))
        _REV['_block']('lying', lo, hi, rgb)
    blk(-2.5, -1.5, -0.6, 0.6, 1.2, skin)          # head
    blk(-1.5, 0.5, -1.0, 1.0, 1.0, shirt)          # torso
    blk(-1.5, 0.5, -1.9, -1.02, 0.9, skin)         # arms
    blk(-1.5, 0.5, 1.02, 1.9, 0.9, skin)
    blk(0.5, 2.5, -0.95, -0.05, 0.9, legs)         # legs
    blk(0.5, 2.5, 0.05, 0.95, 0.9, legs)


def _squares(cx, size, ang=0):
    w, d = (size[2], size[0]) if ang % 180 else (size[0], size[2])
    for i in range(int(round(w / 3))):
        for k in range(int(round(d / 3))):
            x0, z0 = cx - w / 2 + 3 * i, -d / 2 + 3 * k
            shade = (205, 205, 210) if (i + k) % 2 else (185, 185, 192)
            _REV['_block']('sq', (x0 + 0.03, -0.06, z0 + 0.03), (x0 + 2.97, -0.01, z0 + 2.97), shade)
    return w, d


def review_elevations(out, fbx, names, manifest, per_row=4):
    """Side elevations at floor level (a level camera, no floor under the pieces, only their 3-stud squares
    as a thin plate): anything floating shows the background under it, anything leaving its squares shows
    past the plate's ends. Each row twice: from the front (-Z) and from the side (the pieces turned 90)."""
    by = sorted(names, key=lambda n: (-manifest[n]['root']['size'][2], n))
    rows = [by[i:i + per_row] for i in range(0, len(by), per_row)]
    shots = []
    for ri, row in enumerate(rows):
        for ang, tag in ((0, 'front'), (90, 'side')):
            clear()
            x = 0.0
            for n in row:
                size = manifest[n]['root']['size']
                w = size[2] if ang else size[0]
                cx = x + w / 2
                place(fbx, n, (cx, 0, 0), ang)
                _squares(cx, size, ang)
                x += w + 2.0
            _REV['_person'](Vector((x + 1.0, 0, 0)), 0.0)
            shots.append(render(out / f'elevation_{ri + 1}_{tag}.png', (0.0, 0.0, -1.0), (1200, 300),
                                (-1, -0.3, -5), (x + 3, 7.4, 5), scale=1.02))
    return _REV['_compose']([[p] for p in shots], out / 'elevations_sheet.png')


def review_lying(out, fbx, names, manifest):
    """Every Lie piece with the 5-stud person lying on its Use point: from straight above and level from the
    side; the four-poster also from the raised phone camera."""
    shots = []
    for n in names:
        u = manifest[n]['attachments'].get('Use')
        if manifest[n].get('furniture', {}).get('pose') != 'Lie' or not u:
            continue
        size = manifest[n]['root']['size']
        lo, hi = (-size[0] / 2 - 0.5, -0.1, -size[2] / 2 - 0.5), (size[0] / 2 + 0.5, 7.0, size[2] / 2 + 0.5)
        for view, d in (('top', (0.0, 1.0, -0.05)), ('side', (-1.0, 0.0, 0.0) if abs(u['look'][2]) > 0.5
                                                              else (0.0, 0.0, -1.0))):
            clear()
            place(fbx, n, (0, 0, 0))
            _squares(0.0, size)
            _lying(u['pos'], u['look'])
            shots.append(render(out / f'lying_{n[len("Furniture_"):]}_{view}.png', d, (600, 600), lo, hi))
        if n == 'Furniture_FourPosterBed':
            shots.append(render(out / 'lying_FourPosterBed_phone.png', (-0.35, 1.1, -1.0), (600, 600), lo, hi))
    rows = [shots[i:i + 4] for i in range(0, len(shots), 4)]
    rows[-1] += [None] * (4 - len(rows[-1]))
    return _REV['_compose'](rows, out / 'lying_sheet.png')


def review_furniture(out, fbx, names, manifest, per_row=4):
    clear()
    by = sorted(names, key=lambda n: (-manifest[n]['root']['size'][2], n))
    rows, row, x, z, gap = [], [], 0.0, 0.0, 3.0
    widths = {n: manifest[n]['root']['size'][0] for n in by}
    for n in by:
        if len(row) == per_row:
            rows.append(row)
            row = []
        row.append(n)
    if row:
        rows.append(row)
    shots = []
    for ri, row in enumerate(rows):
        clear()
        x = 0.0
        depth = max(manifest[n]['root']['size'][2] for n in row)
        for n in row:
            w = widths[n]
            cx = x + w / 2
            place(fbx, n, (cx, 0, 0))
            size = manifest[n]['root']['size']
            for i in range(int(round(size[0] / 3))):
                for k in range(int(round(size[2] / 3))):
                    x0, z0 = cx - size[0] / 2 + 3 * i, -size[2] / 2 + 3 * k
                    shade = (205, 205, 210) if (i + k) % 2 else (185, 185, 192)
                    _REV['_block']('sq', (x0 + 0.03, -0.06, z0 + 0.03), (x0 + 2.97, -0.01, z0 + 2.97), shade)
            u = manifest[n]['attachments'].get('Use')
            if u:
                p = Vector(u['pos']) + Vector((cx, 0, 0))
                _REV['_block']('use', p - Vector((0.18, 0.0, 0.18)), p + Vector((0.18, 0.12, 0.18)), (230, 40, 40))
                lk = Vector(u['look'])
                q = p + lk * 0.6
                _REV['_block']('use', Vector(map(min, p, q)) - Vector((0.06, 0, 0.06)),
                               Vector(map(max, p, q)) + Vector((0.06, 0.08, 0.06)), (230, 40, 40))
            x += w + gap
        _REV['_person'](Vector((x + 1.5, 0, 0)), 0.0)
        _REV['_block']('floor', (-2, -0.3, -depth / 2 - 4), (x + 5, -0.07, depth / 2 + 2), (150, 150, 156))
        shots.append(render(out / f'furniture_{ri + 1}.png', (-0.45, 0.6, -1.0), (1200, 520),
                            (-1, 0, -depth / 2 - 3), (x + 4, 7.2, depth / 2 + 1), scale=1.02))
    rows_img = [[p] for p in shots]
    sheet = _REV['_compose'](rows_img, out / 'furniture_sheet.png')
    return sheet


# --- The set ------------------------------------------------------------------------------------------

def patch_fixup(path, manifest):
    """The kit's import_fixup.luau, plus each furniture piece's Use Pose (an attribute on the attachment)."""
    s = path.read_text(encoding='utf-8')
    poses = {n: r['furniture']['pose'] for n, r in manifest['pieces'].items() if 'furniture' in r}
    lines = []
    for line in s.split('\n'):
        lines.append(line)
        for n, pose in poses.items():
            if line == f'\t{n} = {{':
                lines.append(f'\t\tpose = "{pose}",')
    s = '\n'.join(lines)
    old = '\t\tatt.Parent = root\n'
    assert old in s, 'import_fixup.luau changed: the Pose patch has no anchor'
    s = s.replace(old, '\t\tif a[1] == "Use" and spec.pose then\n\t\t\tatt:SetAttribute("Pose", spec.pose)\n\t\tend\n'
                  + old, 1)
    s = s.replace('-- and hides LOD_Proxy.', '-- and hides LOD_Proxy; a furniture piece\'s Use gets its Pose attribute '
                  '(tools/build_built_rooms.py).', 1)
    path.write_text(s, encoding='utf-8')


def main():
    refused = []
    for style, st in STYLES.items():
        if SETS_ARG is not None and style not in SETS_ARG:
            continue
        set_dir = f'rooms/{style}'
        K.BUILT.clear()
        FINDINGS.clear()
        K.use_palette(st['palette'])
        K.start_set(set_dir)
        builds = [('Wall_Half', lambda: wall_half(st)), ('Wall_Door', lambda: wall_door(st)),
                  ('Wall_Post', lambda: wall_post(st))]
        table = st['furniture']()
        ids = [i for i, r in ROWS.items() if r['location'] in st['locations']]
        missing = [i for i in ids if i not in table]
        assert not missing, f'{style}: no build for {missing}'
        builds += [(f'Furniture_{i}', table[i]) for i in ids]
        bad = False
        for name, fn in builds:
            if not want(name):
                continue
            try:
                fn()
            except K.Refused as e:
                print(str(e), flush=True)
                refused.append(f'{style}/{name}')
                bad = True
        if bad:
            continue
        built = [p.name for p, _, _ in K.BUILT]
        furn_names = [n for n in built if n.startswith('Furniture_')]
        rows = [(['Wall_Half', 'Wall_Door', 'Wall_Post'], 2.0, 1.0)]
        for i in range(0, len(furn_names), 8):
            rows.append((furn_names[i:i + 8], 2.0, 1.0))
        K.end_set(st['title'], rows, sheet=False)
        out = K.ROOT / 'blender' / set_dir
        manifest = json.loads((out / 'manifest.json').read_text())
        patch_fixup(out / 'import_fixup.luau', manifest)
        val = json.loads((out / 'validation.json').read_text())
        val['height_findings'] = {
            n: {'pieces_height': r['furniture']['pieces_height'], 'model_top': r['furniture']['model_top']}
            for n, r in manifest['pieces'].items()
            if 'furniture' in r and abs(r['furniture']['pieces_height'] - r['furniture']['model_top']) > K.HEIGHT_TOL}
        val['height_note'] = ("Pieces.luau's `height` (the blockouts' placeholder) against the model's top, more than "
                              f"{K.HEIGHT_TOL} apart: a finding for the code session, not a fault (src/ untouched)")
        val['not_validated'] = val.get('not_validated', [])[:1] + [
            'the attachments and the Use Pose attribute exist only in manifest.json until import_fixup.luau makes them',
            'the code placing walls, doors and posts (none exists yet); walls meeting the facade (not assembled here)',
            'a guest walking to Use, sitting or lying: no walker or animation has run']
        if K.ONLY is None and not K.NOPREVIEW:
            rev = out / 'review'
            faults, sheet = review_walls(rev, out / 'fbx')
            val['assembly'] = {'checked': 'the FBXs assembled round a 2 x 2 cell room (an L corner, a T, a free end, '
                                          'two doors, a straight run): coplanar same-facing overlaps between pieces',
                               'faults': faults}
            fsheet = review_furniture(rev, out / 'fbx', furn_names, manifest['pieces'])
            esheet = review_elevations(rev, out / 'fbx', furn_names, manifest['pieces'])
            lsheet = review_lying(rev, out / 'fbx', furn_names, manifest['pieces'])
            print(f'SHEETS {sheet} {fsheet} {esheet} {lsheet}', flush=True)
            if faults:
                refused.append(f'{style}/assembly: {faults[:4]}')
        (out / 'validation.json').write_text(json.dumps(val, indent=1))
        print(f'SET {style}: {len(built)} pieces; height findings {sorted(val["height_findings"])}', flush=True)
    if refused:
        raise SystemExit(f'REFUSED: {refused}')


main()
