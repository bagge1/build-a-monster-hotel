"""Built rooms' art (MODELS.md, "Inner walls, doors and furniture (built rooms)"), one set per location kit.

His ruling, 2026-10-21 (GDD 5.4, A.12): rooms are no longer whole models. The player draws inner walls on
half-cell edges, puts a door in one and furnishes the room on the 3-stud grid. So each location kit gets:

    Wall_Half           one 6-stud half edge, 0.4 thick centred on the edge, 17 tall, both faces alike
    Wall_Door           the same half edge with an open arched doorway (clear x -2..2, y 0..7.2), `Door`, `Sign`
    Wall_Post           the 0.6 square post the code puts on every joint that is not a straight run
    Furniture_<Id>      every Pieces row with `furniture = true` of the location and the location-0 rows ("for
                        any room"), on its w x d 3-stud squares, with `Use` and its `Pose`; the Lodge's and the
                        Spa's location-0 pieces are tools/build_built_rooms_kits.py (review/every/)

Sets: blender/rooms/haunted_manor/ (location 1 and 0, the Manor's palette and dress),
blender/rooms/frostfang_lodge/ (location 2, the Lodge's) and blender/rooms/bayou_spa/ (location 3, a draft: new
shapes, no approved room models to reuse). The look reuses the approved room models' shapes
(tools/build_hotel_haunted_manor.py, build_hotel_frostfang_lodge.py): their beds, coffin, sarcophagus,
nests, counters and the pipe organ, re-authored in the furniture frame (origin the footprint's centre on the
floor, front -Z) with the faces that met in one plane moved a hair apart (decor's coplanar check).

The contract is enforced here (MODELS.md, "Checks"): the walls' exact boxes, the opening clear, nothing outside
the frame, the piece the same turned 180 degrees about Y, no coplanar faces; furniture through the kit's decor
checks (footprint, 0.4 inset, layer, seats, coplanar faces, w/d/layer from Pieces.luau) plus `Use`: its Pose,
a Lie or Sit point on the surface it names with nothing over it, a Stand point 1.5 in front of the front edge, the
5-stud person lying on a Lie point across the body's whole width, arms included (lie_faults), a bar stool's seat at
2.4-2.8, and no shell floating.
Pieces.luau's `height` against the model's top is recorded as a finding (validation.json `height_findings`),
not refused: those heights are the blockouts' placeholders, and this session may not touch src/.

    blender -b --python-exit-code 1 -P tools/build_built_rooms.py [-- sets haunted_manor] [-- only Bed,Wall_Half]
                                                                  [-- nopreview]

Writes blender/rooms/<set>/: fbx/*.fbx, manifest.json, validation.json, import_fixup.luau (with each Use's
Pose attribute), the .blend, and review/ (Workbench sheets on light grey: the walls assembled round a room
corner with a T and a free end, the joints close up, the door piece alone, the furniture on its squares beside
a 5-stud person, floor-level elevations of every piece from the front and the side, every Lie piece from above
and from the side with the 5-stud person lying on its Use, and every Sit piece with the person sitting on it, the
bar stool at a counter).
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
SKIRT_Y, CHAIR_Y = (0.0, 0.5), (3.05, 3.38)     # the skirting and the chair rail on a wall's face (rails())
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
# Bayou Spa (location 3, a draft: WAITING 2.36): a swamp spa, cosy not grim. Mossy weathered cypress, sage, lily
# greens and lotus pinks, mud, still water and steam, warm lantern and firefly light; Locations.luau's facade
# (80, 110, 70), trim (200, 230, 120) and lamp (200, 235, 130) are the moss and lily tones here.
BS_PALETTE = [
    ('moss', (92, 132, 70)), ('moss_dark', (62, 94, 52)), ('moss_light', (140, 176, 96)),
    ('lily', (108, 168, 88)), ('lily_dark', (70, 124, 68)), ('lily_light', (160, 204, 118)),
    ('lotus', (238, 148, 178)), ('lotus_light', (250, 206, 222)), ('lotus_heart', (250, 214, 110)),
    ('cypress', (128, 96, 66)), ('cypress_dark', (86, 63, 45)), ('cypress_light', (172, 136, 96)),
    ('drift', (152, 140, 120)), ('drift_dark', (112, 102, 88)), ('drift_light', (188, 176, 152)),
    ('mud', (122, 86, 56)), ('mud_dark', (86, 60, 40)), ('mud_light', (162, 122, 82)),
    ('water', (72, 142, 132)), ('water_deep', (42, 96, 96)), ('water_light', (132, 192, 178)),
    ('steam', (228, 234, 232)), ('stone', (130, 136, 120)), ('stone_dark', (90, 96, 84)),
    ('stone_light', (178, 182, 166)), ('reed', (120, 140, 70)), ('cattail', (110, 72, 44)),
    ('rattan', (206, 170, 106)), ('rattan_dark', (162, 122, 72)), ('linen', (238, 230, 210)),
    ('towel', (246, 243, 234)), ('sage', (152, 176, 132)), ('sage_light', (196, 212, 176)),
    ('lavender', (176, 150, 206)), ('herb', (96, 150, 80)), ('chamomile', (246, 236, 172)),
    ('copper', (192, 116, 72)), ('copper_dark', (142, 82, 52)), ('brass', (216, 176, 92)),
    ('plum', (92, 72, 112)), ('velvet', (132, 42, 62)), ('iron', (60, 62, 68)), ('black', (32, 34, 36)),
    ('white', (244, 244, 240)), ('grey', (120, 122, 118)), ('moonstone', (200, 218, 240)),
    ('moonstone_dark', (150, 170, 200)), ('frog', (118, 188, 80)), ('frog_belly', (222, 230, 164)),
    ('flame', (255, 205, 120), 'Warm'), ('lamp', (255, 185, 110), 'Warm'), ('firefly', (246, 240, 140), 'Warm'),
    ('moonglow', (205, 225, 255), 'Cold'),
]
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


def wall_body(part, x0, x1, bands, ends=None, top=None):
    """The wall slab x0..x1 in colour bands [(y0, y1, colour)], flat (a straight run of half walls meets
    with no seam: no chamfer at the ends). `ends`: {'left'|'right': colour} for an end face (the reveal);
    `top`: the colour of the wall's top face (the crown's, so the crowns either side read as one cap)."""
    for y0, y1, c in bands:
        col = {'rest': c}
        if ends:
            col.update(ends)
        if top and y1 >= WALL - 1e-9:
            col['top'] = top
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
            strip('Dressing', x0, x1, *SKIRT_Y, 0.05, st['skirting'], s)
            strip('Dressing', x0, x1, *CHAIR_Y, 0.07, st['chair'], s)
        for x0, x1 in upper:
            strip('Dressing', x0, x1, RAIL_Y, RAIL_Y + 0.3, 0.05, st['picture'], s)
            strip('Dressing', x0, x1, WALL - 0.55, WALL, PROUD, st['crown'], s)
    both_faces(face)


def fringe(st):
    """Bayou Spa: a scalloped moss fringe hanging under the crown on both faces (its top buried in the crown,
    0.06 proud: behind the crown's front), four scallops a half edge, meeting at a point on the ends so two
    walls in a line read as one fringe; nothing when the style has none."""
    if not st.get('fringe'):
        return

    def face(s):
        z0, z1 = zs(s, 0.06)
        top = WALL - 0.5
        for xc in (-2.25, -0.75, 0.75, 2.25):
            pts = ([(xc - 0.75, top)]
                   + [(xc - 0.75 * math.cos(math.pi * i / 6), top - 0.06 - 0.3 * math.sin(math.pi * i / 6))
                      for i in range(1, 6)] + [(xc + 0.75, top)])
            prism('Dressing', pts, z0, z1, st['fringe'])
    both_faces(face)


def wall_half(st):
    wpiece('Wall_Half')
    wall_body('Wall', -HALF, HALF, st['body'], top=st['crown'])
    rails(st, [(-HALF, HALF)], [(-HALF, HALF)])
    fringe(st)
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
        top = {'top': st['crown']} if y1 >= WALL - 1e-9 else {}
        if ya >= apex - 1e-9:
            span('Wall_Lintel', (-OPEN_X, ya, -TH), (OPEN_X, y1, TH), {'rest': c, **top})
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
                prism('Wall_Lintel', clean, -TH, TH, {'front': c, 'back': c, 'rest': st['reveal'], **top})


def wall_door(st):
    wpiece('Wall_Door')
    wall_body('Wall_Left', -HALF, -OPEN_X, st['body'], ends={'right': st['reveal']}, top=st['crown'])
    wall_body('Wall_Right', OPEN_X, HALF, st['body'], ends={'left': st['reveal']}, top=st['crown'])
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
        top = _arch_y(outer, 0.0)
        if st.get('keystone_moss'):
            # Bayou Spa (2026-10-21, blind review: a bright green block on the crown): a light cypress keystone
            # with moss over its head, hanging in three scallops down its face, the moss the proudest.
            ka, kb = zs(s, PROUD - 0.015, base=TH + 0.005)
            prism('Dressing', [(-0.34, top - 0.85), (0.34, top - 0.85), (0.44, top), (-0.44, top)],
                  ka, kb, st['keystone'])
            ma, mb = zs(s, PROUD - 0.01, base=TH + 0.01)
            moss = [(-0.5, top + 0.06), (0.5, top + 0.06), (0.5, top - 0.12)]
            for i, xc in enumerate((0.3, 0.0, -0.3)):
                dip = 0.36 if i == 1 else 0.28
                moss += [(xc + 0.15 * math.cos(math.pi * k / 4), top - 0.12 - dip * math.sin(math.pi * k / 4))
                         for k in range(1, 4)] + [(xc - 0.15, top - 0.12)]
            moss[-1] = (-0.5, top - 0.12)
            prism('Dressing', moss, ma, mb, st['keystone_moss'])
        else:
            ka, kb = zs(s, PROUD - 0.005, base=TH + 0.005)    # the keystone, prouder than the trim, its back in it
            prism('Dressing', [(-0.3, top - 0.75), (0.3, top - 0.75), (0.38, top), (-0.38, top)],
                  ka, kb, st['keystone'])
    both_faces(face)
    rails(st, [(-HALF, -trim), (trim, HALF)], [(-HALF, HALF)])
    fringe(st)
    attach('Door', (0, 0, 0), (0, 0, -1))
    attach('Sign', SIGN, (0, 0, -1))
    wfinish(f"a half wall with an open {st['arch']}-arched doorway (clear 4 x 7.2): {st['door_note']}")


def post_bands(st):
    """The post's colour up its height: what a wall's face shows at each height, the dressing over the body
    (skirting, chair rail, picture rail, crown), so every band of the walls meeting it turns the corner on
    the post (2026-10-21, second review: the post's own foot ring and two tones ended the walls' bands
    abruptly at a corner and a free end, and its cap sat on the crowns like a small separate block)."""
    dress = [(SKIRT_Y, st['skirting']), (CHAIR_Y, st['chair']), ((RAIL_Y, RAIL_Y + 0.3), st['picture']),
             ((WALL - 0.55, POST_TOP), st['crown'])]
    cuts = sorted({0.0, POST_TOP} | {y for (a, b), _ in dress for y in (a, b)}
                  | {y for y0, y1, _ in st['body'] for y in (y0, y1) if y < POST_TOP})
    bands = []
    for a, b in zip(cuts, cuts[1:]):
        m = (a + b) / 2
        c = next((c for (y0, y1), c in dress if y0 <= m <= y1), None) \
            or next(c for y0, y1, c in st['body'] if y0 <= m <= y1)
        if bands and bands[-1][2] == c:
            bands[-1] = (bands[-1][0], b, c)
        else:
            bands.append((a, b, c))
    return bands


def column(part, h, bands, chamfer=0.0):
    """A square column x, z -h..h in colour bands [(y0, y1, colour)], one closed solid: rings of corners at
    each band's foot, a side face per band and side, a cap at each end (no faces between bands). `chamfer`:
    its four upright edges cut at 45 degrees that far each way (an octagon; its box still -h..h)."""
    ys = [bands[0][0]] + [b[1] for b in bands]
    c = chamfer
    corners = (((-h, -h), (h, -h), (h, h), (-h, h)) if c <= 0 else
               ((-h + c, -h), (h - c, -h), (h, -h + c), (h, h - c), (h - c, h), (-h + c, h), (-h, h - c),
                (-h, -h + c)))
    m = len(corners)
    verts = [Vector((x, y, z)) for y in ys for x, z in corners]
    faces, cols = [tuple(range(m - 1, -1, -1))], [bands[0][2]]
    for k, (_, _, col) in enumerate(bands):
        for i in range(m):
            j = (i + 1) % m
            faces.append((m * k + i, m * k + j, m * (k + 1) + j, m * (k + 1) + i))
            cols.append(col)
    top = m * len(bands)
    faces.append(tuple(range(top, top + m)))
    cols.append(bands[-1][2])
    store = K._part(part, None)
    first = len(store[1])
    K._add(part, verts, faces, bands[0][2])
    for n, c in enumerate(cols):
        store[2][first + n] = c


def wall_post(st):
    wpiece('Wall_Post')
    column('Post', POST, post_bands(st), chamfer=st.get('post_chamfer', 0.0))
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
SIT_FIGURE = [False]            # sit_faults on (per style, main()): Bayou Spa's seats are held to the seated
                                # figure; the Manor's and the Lodge's get it when next rebuilt and reviewed


def use(pos, look, pose, rise=None, waive=None, liquid=None):
    """`rise`: (legs and torso, head) when a piece's lying surface is not flat (a hammock's sling rises to its
    ends); `waive`: the reason a Lie piece cannot hold the 5-stud person straight (a finding, recorded);
    `liquid`: (y0, y1), a water layer the guest lies in (a tub): its faces, all inside that band, are not a
    surface to the checks."""
    assert pose in POSES, pose
    attach('Use', pos, look)
    K.P.pose = pose
    K.P.lie = {'rise': tuple(rise or LIE_RISE), 'waived': waive} if pose == 'Lie' else None
    K.P.liquid = liquid


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


def _cross_section(t):
    """The lying person's width at t along the body (the review's figure, _lying): the head 1.2 wide, the
    torso 2 and the arms beside it to 1.9 either side, the legs 1.9. Lines across it, sampled by lie_faults."""
    if t < -1.5:
        return (0.0, -0.55, 0.55)
    if t < 0.5:
        return (0.0, -0.45, 0.45, -0.95, 0.95, -1.45, 1.45, -1.85, 1.85)
    return (0.0, -0.45, 0.45, -0.9, 0.9)


def lie_faults(piece, allt, pos, look, tag):
    """MODELS.md, "Furniture" (`Lie`, at the middle of where the body lies): the 5-stud person centred on Use,
    the head toward -LookVector, lies on the piece: the body's middle lines (centre and the legs' lines) are
    in the footprint and on something no more than LIE_DROP below the Lie point, and nothing across the whole
    body, arms included, rises more than the piece's rise (legs and torso; the head's last HEAD on its
    pillow) within USE_CLEAR (2026-10-21, second review: a coffin's and a nest's walls went through the arms;
    the arms may lie past a bed's edge, over nothing)."""
    f = []
    a = Vector((look.x, 0, look.z)).normalized()
    b = Vector((-a.z, 0, a.x))
    body, head = piece.lie['rise']
    hx, hz = 1.5 * piece.fw, 1.5 * piece.fd
    n = 40
    for i in range(n + 1):
        t = -PERSON / 2 + 0.05 + (PERSON - 0.1) * i / n
        for s in _cross_section(t):
            q = pos + a * t + b * s
            where = f'{"head" if t < 0 else "feet"} {abs(t):.2f} from Use' + (f', across {s:+.2f}' if s else '')
            middle = abs(s) <= 0.45 + 1e-9
            hits = K._ray_down(allt, q.x, q.z, pos.y + USE_CLEAR)
            top = max(hits, default=None)
            rise = head if t < -PERSON / 2 + HEAD else body
            if not middle:
                if top is not None and top > pos.y + rise + 1e-6:
                    f.append(f'{tag}: something at {top:.2f} goes through the lying person ({where}; the Lie '
                             f'point at {pos.y:.2f}, at most {rise} higher)')
                    return f
                continue
            if abs(q.x) > hx + 1e-6 or abs(q.z) > hz + 1e-6:
                f.append(f'{tag}: the lying person leaves the footprint ({where})')
                return f
            if top is None or top < pos.y - LIE_DROP:
                f.append(f'{tag}: the lying person hangs off the piece ({where}: '
                         f'{"nothing" if top is None else f"{top:.2f}"} under it, the Lie point at {pos.y:.2f})')
                return f
            if top > pos.y + rise + 1e-6:
                f.append(f'{tag}: something at {top:.2f} goes through the lying person ({where}; the Lie point at '
                         f'{pos.y:.2f}, at most {rise} higher)')
                return f
    return f


SKIN, SHIRT, LEGS, THIGHS, SHOES = (250, 200, 160), (70, 130, 200), (60, 60, 80), (84, 84, 112), (34, 34, 40)
SIT_GAP = 0.03                  # the seated figure's blocks shrunk by this before the piece may not touch them


def sit_blocks(use_pos, look):
    """The 5-stud person seated on a Sit point, facing `look`, as boxes (lo, hi, rgb) in the piece's frame:
    the torso and head over the point, the thighs (a lighter blue, 0.6 thick) lying level on the seat from
    the seat of the trousers under the torso's back to the knees 1.2 ahead, the shins (0.55 deep) hanging
    straight down from the knees, not from the thighs' middle, to 1.1 under the seat, the feet under them
    pointing ahead 0.3 past the knees (dark shoes: the pose reads seated from the front too), the arms
    beside the torso from an armrest's height (_person's widths). The review's figure and sit_faults' are
    this one; each box is (lo, hi, rgb, name).

    2026-10-21, the kits' blind review (the side view's rig): the thighs were 0.9 thick and began at the
    torso's middle, and the shins 0.9 deep hung from 0.4 ahead, under the thighs' middle, so a seat had to
    end under the torso's front and the side view showed the lap and legs hanging in front of the seat as
    one stepped block. A seat may now run 0.6 ahead of Use, under the thighs, the shins hanging past its
    front edge; the soles stay 1.1 under the seat (the bar stool's ring)."""
    a = Vector((look[0], 0, look[2])).normalized()
    b = Vector((-a.z, 0, a.x))
    p = Vector(use_pos)
    ys = p.y
    out = []

    def blk(t0, t1, s0, s1, y0, y1, rgb, name):
        c = [p + a * t + b * s for t in (t0, t1) for s in (s0, s1)]
        out.append((Vector((min(v.x for v in c), y0, min(v.z for v in c))),
                    Vector((max(v.x for v in c), y1, max(v.z for v in c))), rgb, name))
    blk(-0.5, 0.5, -1.0, 1.0, ys, ys + 2.0, SHIRT, 'torso')
    blk(-0.6, 0.6, -0.6, 0.6, ys + 2.0, ys + 3.0, SKIN, 'head')
    for s0, s1, side in ((-1.9, -1.02, 'one'), (1.02, 1.9, 'other')):
        blk(-0.45, 0.45, s0, s1, ys + 0.75, ys + 2.0, SKIN, f'{side} arm')
    for s0, s1, side in ((-0.95, -0.05, 'one'), (0.05, 0.95, 'other')):
        blk(-0.5, 1.2, s0, s1, ys, ys + 0.6, THIGHS, f'{side} thigh')
        blk(0.65, 1.2, s0, s1, ys - 0.8, ys, LEGS, f'{side} shin')
        blk(0.5, 1.5, s0, s1, ys - 1.1, ys - 0.8, SHOES, f'{side} foot')
    return out


def _tri_box(tri, lo, hi):
    """Whether a triangle and an axis-aligned box overlap (separating axes, Akenine-Moller)."""
    c, h = (lo + hi) / 2, (hi - lo) / 2
    v = [t - c for t in tri]
    for i in range(3):
        if min(p[i] for p in v) > h[i] or max(p[i] for p in v) < -h[i]:
            return False
    e = [v[1] - v[0], v[2] - v[1], v[0] - v[2]]
    n = e[0].cross(e[1])
    if abs(n.dot(v[0])) > abs(n.x) * h.x + abs(n.y) * h.y + abs(n.z) * h.z:
        return False
    for ed in e:
        for ax in (Vector((1, 0, 0)), Vector((0, 1, 0)), Vector((0, 0, 1))):
            axis = ax.cross(ed)
            if axis.length < 1e-12:
                continue
            ps = [axis.dot(p) for p in v]
            r = abs(axis.x) * h.x + abs(axis.y) * h.y + abs(axis.z) * h.z
            if min(ps) > r or max(ps) < -r:
                return False
    return True


def sit_faults(allt, pos, look, tag):
    """The seated 5-stud person (sit_blocks) is clear of the piece: no face of it inside any block shrunk by
    SIT_GAP (blind review 2026-10-21, Bayou Spa: the throne's seat front through the shins, its armrests
    through the arms, the perch's boulder through the legs, and the sheet read as a person standing)."""
    for lo, hi, _, nm in sit_blocks(pos, look):
        g = Vector((SIT_GAP,) * 3)
        lo2, hi2 = lo + g, hi - g
        for t in allt:
            if _tri_box(t, lo2, hi2):
                cen = (t[0] + t[1] + t[2]) / 3
                return [f'{tag}: the piece goes through the seated person\'s {nm} (a face at {K.v3(cen, 2)})']
    return []


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
    liquid = getattr(piece, 'liquid', None)
    if liquid:
        allt = [t for t in allt if not all(liquid[0] - 0.005 <= v.y <= liquid[1] + 0.005 for v in t)]
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
        if SIT_FIGURE[0] or getattr(piece, 'sit_figure', False):      # per style, or per piece (_kits.py)
            f += sit_faults(allt, pos, look, tag)
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


def ring_prism(part, outer, inner, y0, y1, outside, inside, top):
    """A walled ring standing y0..y1 between two (x, z) outlines of as many points (a vessel's walls, one
    closed solid): `outside` on the outer faces, `inside` on the inner (its lining), `top` on the rim."""
    k = len(outer)
    assert len(inner) == k
    verts = ([Vector((x, y0, z)) for x, z in outer] + [Vector((x, y1, z)) for x, z in outer]
             + [Vector((x, y0, z)) for x, z in inner] + [Vector((x, y1, z)) for x, z in inner])
    ob, ot, ib, it = 0, k, 2 * k, 3 * k
    faces, cols = [], []
    for i in range(k):
        j = (i + 1) % k
        faces += [(ob + i, ob + j, ot + j, ot + i), (ib + j, ib + i, it + i, it + j),
                  (ot + i, ot + j, it + j, it + i), (ib + i, ib + j, ob + j, ob + i)]
        oc = outside[i % len(outside)] if isinstance(outside, (list, tuple)) else outside    # a list: per segment
        cols += [oc, inside, top, oc]
    store = K._part(part, None)
    first = len(store[1])
    K._add(part, verts, faces, cols[0])
    for n, c in enumerate(cols):
        store[2][first + n] = c


def nest_rim(r, wide=0.6, tall=(0.9, 1.35, 1.2)):
    """A nest's rim profile (the rooms' nests: 0.6 thick, its top rolled inward), its inside radius `r`."""
    return [(r, 0.0), (r + wide, 0.0), (r + wide, tall[0]), (r + wide - 0.2, tall[1]), (r + 0.05, tall[2])]


NEST_IN = 1.85                  # a nest's inside radius before its stretch: the lying person's arms inside the rim
NEST_Z = 1.2                    # its oval (the rooms' 1.42 held the person's arms in the rim; 2026-10-21 review)


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
        **more_furniture(),     # tools/build_built_rooms_more.py
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
    # (0.3 further right than the Potion Loft's: the lying person's legs, 1.9 wide, lay through its head.)
    sphere('Body', (1.2, 2.08, zf + 0.85), (0.55, 0.32, 0.42), 'black', n=8, rings=5)
    sphere('Body', (0.62, 2.12, zf + 0.6), 0.3, 'black', n=8, rings=5)
    for dx in (-0.14, 0.14):
        lathe('Body', [(0.11, 0), (0, 0.24)], 'black', n=4, base=(0.62 + dx, 2.32, zf + 0.6))
    lathe('Body', [(0.0, 3.62), (0.55, 3.62), (0.55, 3.68), (0.26, 3.7), (0.0, 4.5)], 'black', n=10,
          base=(-1.85, 0, zb - 0.15))
    lathe('Body', [(0.27, 3.72), (0.27, 3.86), (0.24, 3.88)], 'violet', n=10, base=(-1.85, 0, zb - 0.15))
    use((-0.7, 1.8, -0.05), (0, 0, -1), 'Lie')     # the legs beside the cat
    done("the Potion Loft's witch's bed: teal blanket, violet gothic headboard, a black cat asleep on it, a hat on a post")


def f_den_nest():
    furn('DenNest')
    # The rim's inside widened (2026-10-21, second review: the lying person's arms went through it): inside
    # 4.8 x 5.8 after the stretch, the rim 0.6 thick as the Den Room's, the oval 1.2 (was 1.42).
    lathe('Body', nest_rim(NEST_IN), 'straw', n=12, scale=(1, NEST_Z), closed=True)
    lathe('Body', [(0, 0.0), (NEST_IN + 0.1, 0.0), (NEST_IN + 0.1, 0.6), (0, 0.75)], 'brown', n=12,
          scale=(1, NEST_Z))
    lathe('Body', [(0, 0.6), (1.0, 0.65), (0.6, 0.95), (0, 1.0)], 'rose', n=10, base=(0, 0, 1.6), scale=(1.2, 0.6))
    cyl('Body', (0, 0, 0), 0.14, 1.6, 'bone', n=6, m=K.Matrix.Translation((-0.8, 0.95, -1.2))
        @ K.Matrix.Rotation(math.radians(-90), 4, 'Z'))
    for x in (-0.8, 0.8):
        for dz in (-0.14, 0.14):
            sphere('Body', (x, 0.95, -1.2 + dz), 0.18, 'bone', n=6, rings=4)
    stretch(1.3, 1.3)
    use((0, surface_y(0, 0), 0), (0, 0, -1), 'Lie')     # centred on the cushion inside the rim, the head on the pillow
    done("the Den Room's round straw nest, larger for its 3 x 3 (inside 4.8 x 5.8, the lying person's arms "
         "inside its rim): a brown cushion, a rose pillow, a bone")


def f_coffin():
    furn('Coffin')
    # 6.0 long (blind review 2026-10-21: the Coffin Suite's 4.95 left a 5-stud guest's feet over the foot); its
    # outline's proportions kept along the length (the shoulders 0.737 of the way to the head), the width as it was.
    # Open and hollow (2026-10-21, second review: a solid box with velvet on top laid the guest on it, not in
    # it): dark wood walls 0.15 thick round a velvet floor at 0.6, the rim at 1.5. 1.36 times the Suite's
    # width (2.58 at the shoulders, within the 2 squares' 2.6) so the lying person's arms, 3.8 across, lie
    # inside the walls; the outline's proportions kept.
    zf, zb = -3.0, 3.0
    zsh = zf + 0.737 * (zb - zf)
    wall = 0.15
    hw = [1.29, 2.58, 1.9]          # the foot, the shoulders, the head
    outline = [(-hw[0], zf), (hw[0], zf), (hw[1], zsh), (hw[2], zb), (-hw[2], zb), (-hw[1], zsh)]
    inner = [(-hw[0] + wall, zf + wall), (hw[0] - wall, zf + wall), (hw[1] - wall, zsh), (hw[2] - wall, zb - wall),
             (-hw[2] + wall, zb - wall), (-hw[1] + wall, zsh)]
    ring_prism('Body', outline, inner, 0.0, 1.5, 'wood_dark', 'crimson', 'wood_dark')
    floor = [(x + (0.02 if x < 0 else -0.02), z + (0.02 if z < 0 else -0.02)) for x, z in inner]
    prism('Body', floor, 0.0, 0.6, {'top': 'crimson', 'rest': 'wood_dark'}, plane='xz')
    span('Body', (-0.9, 0.58, zb - 1.1), (0.9, 0.98, zb - 0.3), 'cream', bevel=0.15)
    bat = [(0, 0.55), (0.35, 0.9), (0.9, 0.75), (1.25, 1.25), (0.7, 1.2), (0.3, 1.5), (0, 1.3),
           (-0.3, 1.5), (-0.7, 1.2), (-1.25, 1.25), (-0.9, 0.75), (-0.35, 0.9)]
    m = K.Matrix.Translation((0, 0, zf))       # the gold bat on the coffin's foot end
    prism('Body', [(x * 0.55, y) for x, y in bat], -0.04, 0.01, 'gold', plane='xy', m=m)
    use((0, 0.6, 0.3), (0, 0, -1), 'Lie')     # in it, on the velvet: the head on the pillow, the feet 0.65 in
    done("the Coffin Suite's coffin, open, 6.0 long and 5.16 wide: dark wood walls, a red velvet lining, a cream "
         "pillow, the gold bat on its foot")


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
    use((0.6, 1.6, -0.65), (1, 0, 0), 'Lie')     # the arms clear of the back (2026-10-21: at -0.4 through it)
    done("the Opera Suite's fainting couch: crimson velvet on a gold frame, a rolled head end, a tufted back")


def f_snack_counter():
    furn('SnackCounter')
    # Its top at 3.75 (2026-10-21, second review: at 3.45 a guest on the bar stool, seat 2.6, had the thighs
    # above it): the counter 0.3 taller, its jars and pie with it.
    # The front 0.6 further back under the top, which overhangs it by 0.8 (blind review of the sitting sheet,
    # 2026-10-21: the seated guest's legs read as in the counter's front): knee room for the bar stool.
    up = 0.3
    span('Body', (-4.0, 0, -0.25), (4.0, 3.2 + up, 1.0), 'plum', bevel=0.1)
    for i in range(13):
        x = -3.6 + i * 0.6
        span('Body', (x - 0.15, 0.2, -0.28), (x + 0.15, 3.0 + up, -0.2), 'pumpkin' if i % 2 else 'cream')
    span('Body', (-4.1, 3.2 + up, -1.05), (4.1, 3.45 + up, 1.1), 'wood_light', bevel=0.06)
    for x, colr in ((-3.0, 'pumpkin'), (-1.8, 'rose'), (2.8, 'slime')):
        lathe('Body', [(0.3, 3.45), (0.38, 3.6), (0.38, 4.2), (0.25, 4.3)], 'lavender', n=8, base=(x, up, 0.3))
        sphere('Body', (x, 4.4 + up, 0.3), (0.2, 0.12, 0.2), colr, n=6, rings=3)
    lathe('Body', [(0.55, 3.45), (0.55, 3.85), (0.4, 3.95), (0, 4.0)], 'rose', n=10, base=(0.4, up, 0.1))
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
    # The book stop along the low front edge, a level pen tray along the high back edge (2026-10-21, second
    # review: a rail standing up at the back read from the side as a chair's back).
    span('Body', (-2.36, 2.22, -1.06), (2.36, 2.42, -0.9), 'wood_dark', bevel=0.02)
    span('Body', (-2.36, 2.45, 0.72), (2.36, 2.61, 1.02), 'wood_dark', bevel=0.02)
    slope = lambda z: 2.3 + (z + 1.0) * 0.15     # noqa: E731
    for x0, x1, col in ((-1.05, -0.02, 'cream'), (0.02, 1.05, 'cream')):
        prism('Body', [(-0.7, slope(-0.7) + 0.02), (0.55, slope(0.55) + 0.02), (0.55, slope(0.55) + 0.1),
                       (-0.7, slope(-0.7) + 0.1)], x0, x1, col, plane='zy')
    prism('Body', [(-0.72, slope(-0.72) + 0.005), (0.57, slope(0.57) + 0.005), (0.57, slope(0.57) + 0.04),
                   (-0.72, slope(-0.72) + 0.04)], -1.1, 1.1, 'book_a', plane='zy')
    cyl('Body', (1.7, 2.61, 0.87), 0.1, 0.12, 'black', n=6)     # the inkpot on the pen tray
    stand()
    done("the Quiet Library's reading desk: a sloped lectern top with an open book against its front stop, an "
         "inkpot on the pen tray, dark legs and stretchers")


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
    # The bench 0.75 out from the console (the sitting sheet, 2026-10-21: 0.4 from it, a seated player's
    # thighs went into the console; now the knees end under the keys' front).
    span('Body', (-1.2, 0, -2.35), (1.2, 1.3, -1.75), 'wood', bevel=0.06)
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
    # The foot ring at 1.42 (the sitting sheet, 2026-10-21: at 0.55 it was a stud under the seated person's
    # feet, which hang at about 1.5).
    lathe('Body', [(0.55, 1.42), (0.6, 1.42), (0.6, 1.49), (0.55, 1.49)], 'gold', n=10, base=(0, 0, -0.2),
          closed=True)
    for k in range(4):
        box('Body', (0, 0, 0), (0.44, 0.05, 0.06), 'gold',
            m=at((0, 1.455, -0.2), ry=45 + 90 * k) @ Matrix.Translation((0.34, 0, 0)))
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
    # In it, on the tub's floor under the water (2026-10-21, second review: on the water's top the guest lay
    # on the tub); the water is no surface to the checks.
    use((-0.3, 0.75, 0.0), (1, 0, 0), 'Lie', liquid=(1.25, 1.3),
        waive='a tub is lain in reclining: its 2 x 1 squares (Pieces) hold 4.4 x 1.8 inside; a straight 5-stud '
              "person, arms at the sides, needs 5.2 x 3.9: 3 x 2 squares (August's call)")
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
            'SkyLounger': f_sky_lounger, **every_furniture('ff')}     # the location-0 pieces: _kits.py


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
    # The inside widened as the Den Nest's (2026-10-21, second review: the arms through the rim).
    lathe('Body', nest_rim(NEST_IN), 'fur', n=12, scale=(1, NEST_Z), closed=True)
    lathe('Body', [(0, 0.0), (NEST_IN + 0.1, 0.0), (NEST_IN + 0.1, 0.6), (0, 0.75)], 'fur_shade', n=12,
          scale=(1, NEST_Z))
    lathe('Body', [(0, 0.6), (1.0, 0.65), (0.6, 0.95), (0, 1.0)], 'ice_deep', n=10, base=(0, 0, -0.8),
          scale=(1.2, 0.8))
    sphere('Body', (0, 1.05, 1.4), (0.8, 0.3, 0.45), 'snow', n=8, rings=4)
    stretch(1.3, 1.3)
    use((0, surface_y(0, 0), 0), (0, 0, -1), 'Lie')     # centred: the head on the pillow, the feet in the rim
    done("the Yeti Den's round fur nest, larger for its 3 x 3 (the lying person's arms inside its rim): a blue "
         "blanket, a snow pillow")


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
    # The inside widened as the nests' (2026-10-21, second review: the arms through the coil), the coil 0.5
    # thick as the Glacier Suite's; its spires stay where they stood, clear of it.
    r = NEST_IN
    lathe('Body', [(r, 0.0), (r + 0.5, 0.0), (r + 0.5, 1.0), (r + 0.25, 1.45), (r, 1.3)], 'ice_deep', n=14,
          scale=(1, NEST_Z), closed=True)
    lathe('Body', [(r + 0.51, 0.45), (r + 0.53, 0.45), (r + 0.53, 0.62), (r + 0.51, 0.62)], 'gold', n=14,
          scale=(1, NEST_Z), closed=True)
    lathe('Body', [(0, 0.0), (r + 0.05, 0.0), (r + 0.05, 0.75), (0, 0.9)], 'frost', n=14, scale=(1, NEST_Z))
    lathe('Body', [(0, 0.75), (1.1, 0.8), (0.7, 1.12), (0, 1.15)], 'navy', n=10, base=(0, 0, -0.7), scale=(1.2, 0.9))
    sphere('Body', (0, 1.15, 1.4), (0.85, 0.3, 0.42), 'snow', n=8, rings=4)
    for x in (-1.65, 1.65):
        lathe('Body', [(0.28, 0), (0.28, 3.6), (0, 4.4)], 'ice', n=6, base=(x, 0, 2.52))
        cyl('Body', (x, 3.4, 2.52), 0.33, 0.2, 'gold', n=6)
    stretch(1.3, 1.3)
    use((0, surface_y(0, 0), 0), (0, 0, -1), 'Lie')     # centred inside the coil, the head on the pillow
    done("the Glacier Suite's coiled round bed, larger (the lying person's arms inside the coil): gold-banded ice, "
         "a navy blanket, two crystal pillars")


def f_star_hammock():
    furn('StarHammock')
    for x in (-3.5, 3.5):
        cyl('Body', (x, 0, 0), 0.55, 0.15, 'log_dark', n=8)
        cyl('Body', (x, 0.15, 0), 0.28, 2.6, 'log', n=8)
        sphere('Body', (x, 2.78, 0), (0.34, 0.2, 0.34), 'snow', n=8, rings=4)
    # The sling's bottom flat under the body, rising steeply at the ends to the ropes (2026-10-21, second
    # review: a parabola sagged 0.9 under the middle of a straight 5-stud person, who hung over it): it rises
    # 0.4 under the head and feet, the guest lying in the cloth.
    n, half = 9, 3.3
    sag = lambda x: 1.3 + 1.1 * (x / half) ** 4     # noqa: E731
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
    sphere('Body', (-2.0, sag(-2.0) + 0.3, 0), (0.5, 0.25, 0.65), 'snow', n=8, rings=4)     # under the head

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
    use((0.0, top(0.0), 0.0), (1, 0, 0), 'Lie')     # centred in the sling, the head on the pillow
    done('a hammock of navy cloth with yellow stars, slung between two snow-capped log posts, the guest lying in it')


def _ff_mug(part, c, r=0.32, h=0.6, col='red', band='cream'):
    x, y, z = c
    cyl(part, (x, y, z), r, h, col, n=8)
    cyl(part, (x, y + h * 0.4, z), r + 0.02, h * 0.2, band, n=8)
    cyl(part, (x, y + h - 0.04, z), r - 0.05, 0.06, 'cocoa', n=8)
    box(part, (x + r + 0.03, y + h * 0.5, z), (0.14, h * 0.55, 0.12), col)     # its handle into the mug's side


def f_cocoa_bar():
    furn('CocoaBar')
    # Its top at 3.75, as the Snack Counter's (a guest on the bar stool sits at it), its pot, mugs and jar with it.
    # The front 0.6 further back, under a top overhanging it by 0.8, as the Snack Counter's (knee room).
    up = 0.3
    span('Body', (-4.0, 0, -0.25), (4.0, 3.2 + up, 1.0), 'cocoa_dark', bevel=0.1)
    for i in range(13):
        x = -3.6 + i * 0.6
        span('Body', (x - 0.15, 0.2, -0.28), (x + 0.15, 3.0 + up, -0.2), 'red' if i % 2 else 'cream')
    span('Body', (-4.1, 3.2 + up, -1.05), (4.1, 3.45 + up, 1.1), 'wood_light', bevel=0.06)
    lathe('Body', [(0.45, 3.45), (0.6, 3.7), (0.62, 4.4), (0.45, 4.6), (0.15, 4.75), (0, 4.8)], 'red', n=10,
          base=(-2.4, up, 0.3))
    box('Body', (-1.7, 4.2 + up, 0.3), (0.5, 0.14, 0.16), 'red')
    for x, colr in ((0.4, 'red'), (1.3, 'ice_deep'), (2.2, 'cream')):
        _ff_mug('Body', (x, 3.45 + up, 0.2), r=0.26, h=0.5, col=colr)
        for k in range(2):
            box('Body', (x - 0.08 + 0.16 * k, 3.98 + up + 0.01 * k, 0.2), (0.14, 0.12, 0.14), 'white')
    lathe('Body', [(0.3, 3.45), (0.32, 4.1), (0.2, 4.2), (0.22, 4.35)], 'ice', n=8, base=(3.3, up, 0.5))
    stand()
    done("the Cocoa Lounge's candy-cane counter: a big red cocoa pot, mugs with marshmallows, a jar")


def f_sky_lounger():
    furn('SkyLounger')
    # Laid flat (2026-10-21, second review: the guest lay flat with the raised back tilted behind the head
    # and the pillow at the hinge; a Lie pose is flat): its back section down level with the seat, two teal
    # cushions meeting at the hinge, the pillow at the head end, the plaid blanket at the foot.
    for x in (-1.25, 1.25):
        for z in (-3.0, 0.0, 3.0):
            span('Body', (x - 0.12, 0, z - 0.12), (x + 0.12, 0.65, z + 0.12), 'wood_dark')
    span('Body', (-1.4, 0.6, -3.3), (1.4, 0.85, 3.3), 'wood', bevel=0.05)
    span('Body', (-1.3, 0.85, -3.2), (1.3, 1.05, 1.17), 'teal', bevel=0.08)
    span('Body', (-1.3, 0.85, 1.23), (1.3, 1.05, 3.2), 'teal', bevel=0.08)
    span('Body', (-1.35, 0.95, -3.1), (1.35, 1.15, -0.3), 'red', bevel=0.08)
    for z in (-2.5, -1.4):
        span('Body', (-1.36, 1.14, z - 0.12), (1.36, 1.17, z + 0.12), 'cream')
    span('Body', (-0.9, 0.98, 2.45), (0.9, 1.43, 3.1), 'snow', bevel=0.18)
    use((0, 1.05, 0.55), (0, 0, -1), 'Lie')     # the head on the pillow, the feet on the blanket
    done('a deck lounger laid flat: teal cushions on a wood frame, a snow pillow at the head, a red plaid blanket '
         'over the foot')


# --- Bayou Spa (location 3, a draft: WAITING 2.36) -----------------------------------------------------
# A swamp spa, cosy not grim: weathered cypress, moss, lily pads and lotus, mud and still water, steam, warm
# lantern and firefly light. No approved room models to reuse (the location is a draft): new shapes, kept to the
# same checks as the Manor's and the Lodge's.

def seg(part, a, b, r, col, n=6):
    """A round rod from a to b (a stalk, a cord, a branch)."""
    a, b = Vector(a), Vector(b)
    d = b - a
    cyl(part, (0, 0, 0), r, d.length, col, n=n, m=Matrix.Translation(a) @ d.to_track_quat('Y', 'Z').to_matrix().to_4x4())


def firefly_lantern(glow, top, h=0.42, r=0.16):
    """A firefly jar hanging from `top` (a hook's underside): a cord, a brass cap, the glowing jar (`glow`, its
    own part: MODELS.md rule 1), a brass foot."""
    x, y, z = top
    cyl('Body', (x, y - 0.18, z), 0.025, 0.22, 'iron', n=4)
    cyl('Body', (x, y - 0.3, z), r + 0.03, 0.12, 'brass', n=8, r_top=0.06)
    cyl(glow, (x, y - 0.3 - h, z), r, h, 'firefly', n=8)
    cyl('Body', (x, y - 0.38 - h, z), r + 0.03, 0.08, 'brass', n=8)


def lotus(c, s=1.0, ang=0.0):
    """A lotus flower standing on (x, y, z): six pink petals leaning out, three pale ones inside, a gold heart."""
    x, y, z = c
    cyl('Body', (x, y, z), 0.14 * s, 0.1 * s, 'lily_dark', n=6)
    for k in range(6):
        sphere('Body', (0, 0, 0), (0.11 * s, 0.27 * s, 0.17 * s), 'lotus', n=5, rings=3,
               m=at((x, y, z), ry=ang + 60 * k) @ Matrix.Translation((0, 0.22 * s, 0.17 * s))
               @ Matrix.Rotation(math.radians(38), 4, 'X'))
    for k in range(3):
        sphere('Body', (0, 0, 0), (0.1 * s, 0.25 * s, 0.13 * s), 'lotus_light', n=5, rings=3,
               m=at((x, y, z), ry=ang + 30 + 120 * k) @ Matrix.Translation((0, 0.26 * s, 0.07 * s))
               @ Matrix.Rotation(math.radians(14), 4, 'X'))
    sphere('Body', (x, y + 0.3 * s, z), (0.12 * s, 0.07 * s, 0.12 * s), 'lotus_heart', n=6, rings=3)


def frog(c, ang=0.0, s=1.0):
    """A small green frog sitting on (x, y, z), facing -Z turned `ang` about Y."""
    M = at(c, ry=ang)

    def put(p, radii, col):
        sphere('Body', (0, 0, 0), tuple(r * s for r in radii), col, n=6, rings=3,
               m=M @ Matrix.Translation(Vector(p) * s))
    put((0, 0.24, 0.05), (0.32, 0.24, 0.36), 'frog')
    put((0, 0.2, -0.16), (0.24, 0.14, 0.2), 'frog_belly')
    for sx in (-1, 1):
        put((0.15 * sx, 0.46, -0.16), (0.1, 0.1, 0.1), 'frog')
        put((0.17 * sx, 0.5, -0.24), (0.045, 0.045, 0.03), 'black')
        put((0.3 * sx, 0.1, 0.18), (0.13, 0.1, 0.24), 'frog')


def lily_pad(c, r, h, col, notch=0.0, n=10):
    """A flat lily pad on (x, y, z), its V notch toward `notch` degrees (0 = +X)."""
    x, y, z = c
    a0 = math.radians(notch)
    pts = [(x, z)] + [(x + r * math.cos(a0 + math.radians(16 + (360 - 32) * i / n)),
                       z + r * math.sin(a0 + math.radians(16 + (360 - 32) * i / n))) for i in range(n + 1)]
    prism('Body', pts, y, y + h, col, plane='xz')


def cattails(x, z, y=0.0, k=3, tall=2.0, firefly=None):
    """A clump of cattails on (x, y, z): k stalks of reed with brown heads, two leaf blades; `firefly`: a glow
    part name, a firefly resting on the tallest head's tip."""
    for i in range(k):
        a = math.radians(40 + 360 * i / k)
        px, pz = x + 0.12 * math.cos(a), z + 0.12 * math.sin(a)
        h = tall * (1.0 - 0.12 * i)
        cyl('Body', (px, y, pz), 0.045, h, 'reed', n=4)
        cyl('Body', (px, y + h - 0.65, pz), 0.1, 0.45, 'cattail', n=6)
        if i == 0 and firefly:
            sphere(firefly, (px, y + h + 0.06, pz), (0.08, 0.08, 0.08), 'firefly', n=6, rings=3)
    for i, a in enumerate((-15, 20)):
        prism('Body', [(-0.07, 0.0), (0.07, 0.0), (0.0, tall * 0.8)], -0.02, 0.02, 'reed', plane='xy',
              m=at((x, y + 0.03, z), ry=70 * i + 30, rz=a))     # its corners clear of the floor when leant


def f_lily_pad_bed():
    furn('LilyPadBed')
    # A giant lily pad (the Victoria kind, its rim turned up) on a moss mound; a linen petal sheet, a pale lotus-petal
    # blanket, a lotus bud pillow at the head (+Z), two lotus flowers on the pad beside the guest.
    lathe('Body', [(3.5, 0.0), (3.3, 0.3), (2.8, 0.45), (0.0, 0.48)], 'moss_dark', n=16)
    cyl('Body', (0, 0.42, 0), 3.9, 0.26, 'lily', n=20)
    for k in range(8):          # the veins, from the middle out (apart at the middle: no shared plane)
        a = math.radians(22.5 + 45 * k)
        c, s = math.cos(a), math.sin(a)
        pts = [(0.5 * c - 0.05 * s, 0.5 * s + 0.05 * c), (3.5 * c - 0.03 * s, 3.5 * s + 0.03 * c),
               (3.5 * c + 0.03 * s, 3.5 * s - 0.03 * c), (0.5 * c + 0.05 * s, 0.5 * s - 0.05 * c)]
        prism('Body', pts, 0.67, 0.70, 'lily_light', plane='xz')
    lathe('Body', [(3.62, 0.6), (3.9, 0.6), (3.98, 1.05), (3.82, 1.08), (3.62, 0.76)], 'lily_dark', n=20,
          closed=True)
    # The guest lies on petals the whole length, arms included (2026-10-21, blind review: the blanket stopped
    # at the waist and the body bridged the pad over a gap): a pink petal sheet under the head and torso, the
    # pale petal blanket over the legs 0.02 higher, both 4 wide.
    span('Body', (-2.0, 0.68, 0.26), (2.0, 0.8, 2.6), 'linen', bevel=0.04)
    span('Body', (-2.02, 0.68, -2.6), (2.02, 0.82, 0.3), 'lotus_light', bevel=0.05)
    sphere('Body', (0, 0.98, 1.95), (0.95, 0.3, 0.5), 'lotus', n=10, rings=4)
    lotus((2.6, 0.68, 1.5), 1.2)
    lotus((-2.55, 0.68, -1.6), 1.1, ang=20)
    use((0, 0.82, 0), (0, 0, -1), 'Lie')     # the head on the bud pillow, the feet under the blanket
    done("the Lily Pad Room's bed: a giant lily pad with its rim turned up on a moss mound, a pale petal blanket, a "
         "lotus bud pillow, two lotus flowers")


def f_willow_hammock():
    furn('WillowHammock')
    # The Star Hammock's sling (flat under the body, rising steeply to the ropes) in woven rattan, between two
    # gnarled cypress posts crowned with weeping willow; a firefly jar hangs from each post (tags: fireflies).
    for sx in (-1, 1):
        x = 3.45 * sx
        lathe('Body', [(0.55, 0.0), (0.38, 0.25), (0.28, 0.6), (0.25, 2.4), (0.3, 2.9), (0.0, 3.05)], 'cypress_dark',
              n=8, base=(x, 0, 0))
        lathe('Body', [(0.0, 2.72), (0.64, 2.78), (0.62, 3.3), (0.42, 3.75), (0.0, 3.9)], 'lily_dark', n=10,
              base=(x, 0, 0))
        for k in range(5):      # willow strands hanging down the outer side, their tops in the crown
            a = math.radians(-60 + 30 * k)
            px, pz = x + sx * 0.58 * math.cos(a), 0.58 * math.sin(a)
            box('Body', (0, 0, 0), (0.12, 0.95 - 0.12 * (k % 2), 0.04), 'lily',      # thin across the radius
                m=at((px, 2.4 + 0.06 * (k % 2), pz), ry=math.degrees(math.atan2(sx * math.cos(a), math.sin(a)))))
        # The lantern hangs off the post's front-outer side, clear of the widened sling and its ropes.
        hx, hz = x + sx * 0.32, -0.88
        seg('Body', (x + sx * 0.12, 2.5, -0.2), (hx, 2.47, hz), 0.05, 'cypress_dark', n=5)      # its hook branch
        firefly_lantern(f'Glow_Warm_{1 if sx < 0 else 2}', (hx, 2.42, hz))
    # The sling 3.9 wide (the 5-stud person's arms on it, 3.8) and flat under the whole body, rising only past
    # its ends (2026-10-21, Bayou blind review: 2.4 wide, the arms over its edges, and the Lodge's x^4 curve
    # still rose 0.36 under the head and feet, the straight body sunk into it): level to |x| 2.5, then up to
    # the ropes in three short chords a side.
    half, flat = 3.3, 2.5
    sag = lambda x: 1.3 + 1.1 * max(0.0, (abs(x) - flat) / (half - flat)) ** 1.6     # noqa: E731
    xs = [-3.3, -3.05, -2.8, -2.55, -1.7, -0.85, 0.0, 0.85, 1.7, 2.55, 2.8, 3.05, 3.3]
    for i, (xa, xb) in enumerate(zip(xs, xs[1:])):
        ya, yb = sag(xa), sag(xb)
        ln = math.hypot(xb - xa, yb - ya) + 0.06
        ang = math.degrees(math.atan2(yb - ya, xb - xa))
        box('Body', (0, 0, 0), (ln, 0.15 + 0.02 * (i % 2), 3.9 - 0.01 * (i % 2)), 'rattan' if i % 2 else
            'rattan_dark', m=at(((xa + xb) / 2, (ya + yb) / 2, 0), rz=ang))     # the flat chords 0.01 apart
    for x in (-half, half):
        for z in (-1.9, 1.9):
            a, b = Vector((x, sag(x), z)), Vector((x * 1.06, 2.55, z * 0.25))
            seg('Body', a, b, 0.04, 'linen', n=4)
    sphere('Body', (-2.0, sag(-2.0) + 0.3, 0), (0.5, 0.25, 0.7), 'linen', n=8, rings=4)     # under the head

    def top(x):         # the sling's top along its chords
        i = max(k for k in range(len(xs) - 1) if xs[k] <= x or k == 0)
        xa, xb = xs[i], xs[i + 1]
        ang = math.atan2(sag(xb) - sag(xa), xb - xa)
        return sag(xa) + (x - xa) / (xb - xa) * (sag(xb) - sag(xa)) + 0.075 / math.cos(ang)
    use((0.0, top(0.0), 0.0), (1, 0, 0), 'Lie')     # centred in the sling, the head on the pillow
    done("the Willow Nook's hammock: woven rattan between two gnarled cypress posts crowned with weeping willow, "
         "a firefly jar hanging from each")


def oval(rx, rz, n=20, cz=0.0):
    return [(rx * math.cos(2 * math.pi * (i + 0.5) / n), cz + rz * math.sin(2 * math.pi * (i + 0.5) / n))
            for i in range(n)]


def f_mud_tub():
    furn('MudTub')
    # An oval cypress tub of staves (alternate faces a lighter wood: no raised seams), two copper hoops, warm mud
    # to the brim with a few bubbles; a rolled towel under the head (+Z), folded towels on the rim.
    n = 20
    out, inn = oval(2.55, 4.05, n), oval(2.25, 3.75, n)
    ring_prism('Body', out, inn, 0.0, 2.0, ['cypress', 'cypress_light'], 'mud_dark', 'cypress_light')
    for y0 in (0.35, 1.45):
        ring_prism('Body', oval(2.585, 4.085, n), out, y0, y0 + 0.2, 'copper', 'copper', 'copper')
    prism('Body', oval(2.23, 3.73, n), 0.0, 0.6, 'cypress_dark', plane='xz')
    prism('Body', oval(2.22, 3.72, n), 1.35, 1.45, 'mud', plane='xz')
    for x, z, r in ((-0.9, 1.0, 0.16), (1.1, -0.6, 0.12), (0.4, -2.2, 0.14), (-1.2, -1.6, 0.1)):
        sphere('Body', (x, 1.43, z), (r, 0.015, r), 'mud_light', n=6, rings=3)
    cyl('Body', (0, 0, 0), 0.3, 2.4, 'towel', n=8, m=at((-1.2, 0.9, 2.2), rz=-90))
    span('Body', (1.98, 2.0, -0.6), (2.58, 2.14, 0.4), 'towel', bevel=0.03)
    span('Body', (2.03, 2.14, -0.5), (2.53, 2.26, 0.3), 'sage', bevel=0.03)
    # In it, on the tub's floor under the mud (as the Bathtub: the mud is no surface to the checks).
    use((0, 0.6, 0.0), (0, 0, -1), 'Lie', liquid=(1.35, 1.45))
    done("the Mud Bath's tub: an oval of cypress staves with two copper hoops, warm mud to the brim, a rolled towel "
         "under the head, towels folded on the rim")


def f_herb_bed():
    furn('HerbBed')
    # A weathered bed with a moss mattress under a lavender quilt; its headboard a row of rattan reed bundles
    # bound in copper, three herb bundles hung drying from the binding (above the lying guest's head); a planter
    # of herbs as its footboard.
    zf, zb, hw = -2.7, 3.2, 2.3
    for x in (-hw + 0.22, hw - 0.22):
        for z in (zf + 0.22, zb - 0.45):
            cyl('Body', (x, 0, z), 0.18, 0.7, 'drift_dark', n=6)
    span('Body', (-hw, 0.6, zf), (hw, 1.1, zb - 0.25), 'drift', bevel=0.08)
    span('Body', (-hw + 0.1, 1.1, zf + 0.1), (hw - 0.1, 1.65, zb - 0.35), 'moss', bevel=0.15)
    span('Body', (-hw + 0.02, 1.25, zf + 0.05), (hw - 0.02, 1.8, zf + 3.6), 'lavender', bevel=0.18)
    for z in (zf + 1.0, zf + 2.3):
        span('Body', (-hw + 0.1, 1.8, z - 0.14), (hw - 0.1, 1.84, z + 0.14), 'sage_light')
    span('Body', (-hw + 0.05, 1.62, zf + 3.3), (hw - 0.05, 1.86, zf + 3.8), 'linen', bevel=0.08)
    span('Body', (-1.3, 1.6, zb - 1.5), (1.3, 2.25, zb - 0.4), 'linen', bevel=0.22)
    for i in range(9):          # the headboard: reed bundles, tallest in the middle
        x = -2.0 + 0.5 * i
        h = 3.2 + 1.1 * math.cos(x / 2.2 * math.pi / 2)
        cyl('Body', (x, 0, zb - 0.1), 0.21, h, 'rattan' if i % 2 else 'rattan_dark', n=6)
        sphere('Body', (x, h, zb - 0.1), (0.21, 0.1, 0.21), 'rattan' if i % 2 else 'rattan_dark', n=6, rings=3)
    span('Body', (-2.27, 2.9, zb - 0.34), (2.27, 3.05, zb + 0.14), 'copper_dark')
    span('Body', (-1.3, 3.85, zb - 0.34), (1.3, 4.0, zb + 0.14), 'copper_dark')
    for x, colr in ((-0.85, 'lavender'), (0.0, 'herb'), (0.85, 'chamomile')):
        z = zb - 0.42      # against the reeds, behind the lying guest's head (2026-10-21, blind review: it clipped them)
        cyl('Body', (x, 3.72, z), 0.07, 0.24, 'herb', n=5)
        cyl('Body', (x, 3.7, z), 0.1, 0.09, 'linen', n=6)
        lathe('Body', [(0.0, 3.4), (0.2, 3.5), (0.15, 3.72)], colr, n=6, base=(x, 0, z))
        box('Body', (x, 3.92, z + 0.12), (0.05, 0.05, 0.3), 'linen')     # its string to the binding
    span('Body', (-2.25, 0.0, -3.75), (2.25, 1.2, zf + 0.02), 'drift', bevel=0.06)      # the planter footboard
    span('Body', (-2.1, 1.1, -3.6), (2.1, 1.24, zf - 0.13), 'mud_dark')
    for k, x in enumerate((-1.6, -0.8, 0.0, 0.8, 1.6)):
        sphere('Body', (x, 1.42, -3.2), (0.38, 0.3, 0.32), ('herb', 'sage', 'lavender')[k % 3], n=8, rings=4)
    use((0, 1.8, 0.0), (0, 0, -1), 'Lie')     # the head's top 0.08 short of the herb bundles, on the pillow
    done("the Herb Loft's bed: weathered wood, a moss mattress under a lavender quilt, a headboard of rattan reed "
         "bundles bound in copper with herbs hung drying, a planter of herbs at its foot")


def boulder(c, r, h, col, sz=0.95, n=8):
    """A rounded stone standing flat on (x, y, z): its widest a third up, r across, h tall, `sz` its depth
    (2026-10-21, Bayou blind review: spheres stood on their points, balanced on bevelled undersides)."""
    lathe('Body', [(0.82 * r, 0.0), (r, 0.35 * h), (0.72 * r, 0.82 * h), (0.0, h)], col, n=n, base=c,
          scale=(1, sz))


def f_steam_pool():
    furn('SteamPool')
    # A round hot pool walled in mossy boulders, steam curling up from two of them, a lantern on the back stone,
    # a smooth stone headrest at the head (+Z), lily pads and a lotus on the water. The guest lies in it on its
    # floor (0.1) under the water (1.1-1.15), only the head's top above it (2026-10-21, blind review: on a 0.3
    # floor under water at 1.0, the body showed at the rim's height); the boulders stand flat on the floor.
    lathe('Body', [(2.9, 0.0), (3.3, 0.0), (3.3, 1.2), (2.9, 1.2)], 'stone_dark', n=14, closed=True)
    cyl('Body', (0, 0, 0), 2.92, 0.1, 'stone_dark', n=14)
    cyl('Body', (0, 1.1, 0), 2.95, 0.05, 'water', n=14)
    k_n = 14
    tops = {}
    for k in range(k_n):
        a = 2 * math.pi * (k + 0.5) / k_n
        r = 0.6 if k % 2 else 0.66
        h = 2 * (0.62 + 0.04 * (k % 3))
        tops[k] = h
        boulder((3.42 * math.cos(a), 0.0, 3.42 * math.sin(a)), r, h, ('stone', 'stone_light', 'stone')[k % 3], n=6)
    for k in (2, 5, 9, 12):      # moss on some of them
        a = 2 * math.pi * (k + 0.5) / k_n
        sphere('Body', (3.42 * math.cos(a), tops[k] - 0.08, 3.42 * math.sin(a)), (0.42, 0.14, 0.4), 'moss',
               n=6, rings=3)
    sphere('Body', (0, 0.36, 2.0), (0.8, 0.26, 0.5), 'stone_light', n=10, rings=4)       # the headrest, on the floor
    for sx in (-1, 1):          # steam rising off the back stones
        k = 1 if sx > 0 else 5
        a = 2 * math.pi * ((k + 0.5) / k_n)    # the back (+Z) stones
        x, z = 3.42 * math.cos(a), 3.42 * math.sin(a)
        for i, (dy, r) in enumerate(((0.12, 0.36), (0.57, 0.3), (0.97, 0.24), (1.29, 0.17))):
            sphere('Body', (x + 0.08 * sx * i, tops[k] + dy, z - 0.05 * i), (r, r * 0.8, r), 'steam', n=6, rings=3)
    a = 2 * math.pi * (3.5 / k_n)     # the back stone, behind the head
    lx, lz = 3.42 * math.cos(a), 3.42 * math.sin(a)
    ly = tops[3] - 0.04
    cyl('Body', (lx, ly, lz), 0.22, 0.12, 'brass', n=8)
    cyl('Glow_Warm_1', (lx, ly + 0.12, lz), 0.17, 0.4, 'lamp', n=8)
    cyl('Body', (lx, ly + 0.52, lz), 0.22, 0.14, 'brass', n=8, r_top=0.05)
    lily_pad((-2.2, 1.15, -1.2), 0.42, 0.02, 'lily', notch=40)
    lily_pad((2.1, 1.15, -1.6), 0.36, 0.02, 'lily_dark', notch=200)
    lily_pad((-2.3, 1.15, 0.9), 0.32, 0.02, 'lily', notch=120)
    lotus((-2.2, 1.17, -1.2), 0.8)
    # In it, on the pool's floor under the water (the water and the pads on it are no surface to the checks).
    use((0, 0.1, 0.0), (0, 0, -1), 'Lie', liquid=(1.1, 1.17))
    done("the Steam Grotto's hot pool: still water in a ring of mossy boulders, steam curling off two of them, a "
         "lantern on the back stone, a smooth headrest, lily pads and a lotus")


def f_cypress_throne():
    furn('CypressThrone')
    # A throne carved from a cypress stump: a root flare, a moss cushion between two knobbly root-knee arms, a
    # high back with a carved crown and a lighter inset panel, Spanish moss draped over its shoulders, a firefly
    # jar hanging from a crooked branch. Fitted to the seated 5-stud person (2026-10-21, blind review: the arms
    # went through the person's arms and the seat's front through the shins): the arms stand 3.92 apart (the
    # person 3.8 across), the seat 1.2 deep from the back, its front where the shins hang, the guest's back 0.3
    # off the backrest.
    lathe('Body', [(2.55, 0.0), (2.35, 0.2), (1.9, 0.42), (0.0, 0.45)], 'cypress_dark', n=12, base=(0, 0, -0.4),
          scale=(1, 0.85))
    half = [(2.45, 0.4), (2.45, 3.4), (2.1, 4.1), (1.45, 4.4), (0.75, 4.8)]
    outline = half + [(0.0, 5.0)] + [(-x, y) for x, y in reversed(half)]
    prism('Body', outline, 0.0, 0.85, 'cypress', plane='xy')
    inset = [(0.72 * x, 2.0 + 0.62 * (y - 0.4)) for x, y in outline]
    prism('Body', inset, -0.03, 0.0, 'cypress_light', plane='xy')
    span('Body', (-1.6, 0.4, -1.1), (1.6, 1.2, 0.02), 'cypress_dark')
    span('Body', (-1.98, 1.2, -1.2), (1.98, 1.55, 0.02), 'cypress', bevel=0.05)
    span('Body', (-1.92, 1.55, -1.18), (1.92, 1.8, -0.03), 'moss', bevel=0.08)
    for sx in (-1, 1):
        xa, xb = sorted((1.96 * sx, 2.56 * sx))
        span('Body', (xa, 0.0, -1.55), (xb, 2.5, 0.05), 'cypress_dark', bevel=0.18)
        sphere('Body', (2.26 * sx, 2.5, -1.25), (0.3, 0.24, 0.32), 'cypress_light', n=8, rings=4)
        drape = [(1.75, 4.22), (2.4, 3.75), (2.5, 3.4), (2.5, 2.9), (2.38, 2.62), (2.28, 3.0), (2.16, 2.66),
                 (2.05, 3.1), (1.92, 3.45)]
        prism('Body', [(x * sx, y) for x, y in drape][::sx], -0.07, -0.02, 'moss_light', plane='xy')
    for p, q in (((1.6, 4.2, 0.45), (2.15, 4.75, 0.2)), ((2.15, 4.75, 0.2), (2.35, 4.5, -0.35))):
        seg('Body', p, q, 0.07, 'cypress_dark', n=5)
    firefly_lantern('Glow_Warm_1', (2.35, 4.47, -0.35), h=0.36, r=0.14)
    K.seat(-1.05, 1.05, -1.2, 0.0, 1.8)
    use((0, 1.8, -0.8), (0, 0, -1), 'Sit')
    done("the Cypress Suite's throne carved from a cypress stump: a moss cushion, root-knee arms, a high carved back "
         "draped with Spanish moss, a firefly jar on a crooked branch")


def f_lagoon_perch():
    furn('LagoonPerch')
    # A smooth moonstone boulder with a lily-pad cushion to sit on, facing a little lagoon pool in front (-Z):
    # lily pads, a lotus, a frog; a reed stalk curving over from behind with a glowing crescent moon on a cord;
    # cattails at the back. The boulder is long across and shallow front to back, the cushion at its front, so
    # the seated person's shins hang clear in front of it (2026-10-21, blind review: on a round boulder's top
    # the legs went down through the stone, the figure read as standing on it).
    lathe('Body', [(1.95, 0.0), (2.05, 0.45), (1.95, 1.1), (1.55, 1.58), (0.0, 1.68)], 'moonstone', n=12,
          base=(0, 0, 2.6), scale=(1, 0.5))
    cyl('Body', (0, 1.5, 2.45), 1.15, 0.23, 'lily', n=12, scale=(1, 0.52))
    boulder((-2.4, 0.0, 2.9), 0.85, 1.15, 'moonstone_dark', sz=0.88)
    sphere('Body', (-2.4, 1.08, 2.9), (0.48, 0.16, 0.42), 'moss', n=8, rings=3)
    lathe('Body', [(2.0, 0.0), (2.35, 0.0), (2.35, 0.35), (2.2, 0.5), (2.0, 0.45)], 'stone', n=16,
          base=(0, 0, -1.7), closed=True)
    cyl('Body', (0, 0, -1.7), 2.03, 0.4, 'water_deep', n=16)
    lily_pad((-0.9, 0.4, -2.5), 0.5, 0.03, 'lily', notch=70)
    lily_pad((0.9, 0.4, -1.1), 0.42, 0.03, 'lily_dark', notch=250)
    lily_pad((0.6, 0.4, -3.0), 0.34, 0.03, 'lily', notch=160)
    frog((-0.9, 0.43, -2.5), ang=20, s=0.9)
    lotus((0.9, 0.43, -1.1), 0.75)
    boulder((2.9, 0.0, 3.3), 0.4, 0.55, 'stone_dark')
    stalk = [(2.9, 0.1, 3.3), (3.0, 1.5, 3.1), (2.95, 3.0, 2.6), (2.75, 3.85, 1.9), (2.55, 4.0, 1.45)]
    for a, b in zip(stalk, stalk[1:]):
        seg('Body', a, b, 0.07, 'reed', n=5)
    sphere('Body', stalk[-1], 0.07, 'reed', n=5, rings=3)
    cyl('Body', (2.55, 3.84, 1.45), 0.02, 0.16, 'linen', n=4)
    outer = [(0.45 * math.cos(math.radians(a)), 0.45 * math.sin(math.radians(a))) for a in range(40, 321, 20)]
    inner = [(0.2 + 0.36 * math.cos(math.radians(a)), 0.36 * math.sin(math.radians(a))) for a in range(300, 59, -20)]
    prism('Glow_Cold_1', outer + inner, -0.06, 0.06, 'moonglow', plane='xy',
          m=at((2.55, 3.84 - 0.45, 1.45)))      # its top on the cord, the horns toward +X
    cattails(-3.2, 0.8, k=3, tall=2.2)
    cattails(3.3, -3.3, k=2, tall=1.8)
    K.seat(-1.05, 1.05, 1.85, 3.05, 1.73)
    use((0, 1.73, 1.95), (0, 0, -1), 'Sit')
    done("the Moonlit Lagoon's perch: a smooth moonstone boulder with a lily-pad cushion facing a little lagoon "
         "(lily pads, a lotus, a frog), a glowing crescent moon hung from a reed stalk, cattails")


def f_jazz_stage():
    furn('JazzStage')
    # A low porch stage of weathered boards (planks in two tones, a hair apart in height) with a velvet skirt,
    # three footlights, a vintage microphone, an upright bass leaning back, a stool with a straw boater, and a
    # string of warm bulbs between two posts at the back.
    span('Body', (-4.0, 0.0, -2.45), (4.0, 0.8, 2.45), 'cypress_dark')
    zs_ = [-2.55 + 5.1 * i / 6 for i in range(7)]
    for i in range(6):
        span('Body', (-4.1, 0.78, zs_[i]), (4.1, 0.9 + 0.01 * (i % 2), zs_[i + 1]), 'drift' if i % 2 else 'drift_light')
    span('Body', (-4.0, 0.05, -2.5), (4.0, 0.78, -2.45), 'velvet')
    for k, x in enumerate((-3.0, -1.5, 1.5)):
        sphere(f'Glow_Warm_{k + 1}', (x, 0.9, -2.25), (0.2, 0.13, 0.13), 'lamp', n=8, rings=4)
        span('Body', (x - 0.3, 0.9, -2.15), (x + 0.3, 1.16, -2.0), 'brass', bevel=0.03)
    cyl('Body', (0, 0.9, -1.1), 0.32, 0.06, 'iron', n=10)
    cyl('Body', (0, 0.96, -1.1), 0.04, 3.1, 'iron', n=6)
    cyl('Body', (0, 4.04, -1.1), 0.15, 0.08, 'brass', n=8)
    sphere('Body', (0, 4.28, -1.1), (0.14, 0.22, 0.14), 'iron', n=8, rings=4)
    # The upright bass, leaning 6 degrees on its endpin.
    M = at((2.5, 0.9, 0.7), rz=6)
    half = [(0.06, 0.32), (0.62, 0.45), (0.78, 0.9), (0.72, 1.35), (0.48, 1.65), (0.5, 1.95), (0.6, 2.25),
            (0.45, 2.55), (0.12, 2.66)]
    prism('Body', [(x, y) for x, y in half] + [(-x, y) for x, y in reversed(half)], -0.25, 0.25,
          {'front': 'cypress_light', 'back': 'cypress_light', 'rest': 'cypress'}, plane='xy', m=M)
    cyl('Body', (0, 0.0, 0), 0.03, 0.34, 'iron', n=4, m=M)
    box('Body', (0, 3.3, -0.1), (0.18, 1.4, 0.28), 'cypress_dark', m=M)
    box('Body', (0, 2.8, -0.27), (0.14, 2.3, 0.06), 'black', m=M)
    sphere('Body', (0, 4.08, -0.1), (0.13, 0.16, 0.13), 'cypress_dark', n=6, rings=4, m=M)
    for sx in (-1, 1):
        box('Body', (0.3 * sx, 1.4, -0.26), (0.05, 0.42, 0.03), 'black', m=M)
    # The stool and the boater.
    for k in range(3):
        a = math.radians(90 + 120 * k)
        cyl('Body', (-2.4 + 0.3 * math.cos(a), 0.9, 0.8 + 0.3 * math.sin(a)), 0.05, 1.5, 'cypress', n=4)
    cyl('Body', (-2.4, 2.4, 0.8), 0.42, 0.1, 'cypress', n=10)
    cyl('Body', (-2.4, 2.5, 0.8), 0.4, 0.03, 'rattan', n=12)
    cyl('Body', (-2.4, 2.53, 0.8), 0.24, 0.2, 'rattan', n=10)
    cyl('Body', (-2.4, 2.56, 0.8), 0.25, 0.07, 'velvet', n=10)
    # The posts and the string of lights, as high as a Floor piece may reach (MODELS.md: at most 7 tall): the
    # string pulled nearly taut, its lowest bulb 5.4 over the deck, clear of a 5-stud person walking the stage
    # by 0.4 (2026-10-21, blind review: it sagged to 2.6 over the deck, through their head; the review asked
    # for 7 over the deck, which the 7-stud layer cannot hold over a 0.9 deck).
    for sx in (-1, 1):
        cyl('Body', (3.75 * sx, 0.9, 2.2), 0.13, 5.88, 'cypress', n=6)
        sphere('Body', (3.75 * sx, 6.82, 2.2), 0.17, 'brass', n=6, rings=3)     # its band clear of the post's faces
    pts = [(-3.75 + 7.5 * i / 8, 6.7 - 0.15 * math.sin(math.pi * i / 8), 2.2) for i in range(9)]
    for a, b in zip(pts, pts[1:]):
        seg('Body', a, b, 0.025, 'black', n=4)
    for x, y, z in pts[1:-1]:
        sphere('Glow_Warm_4', (x, y - 0.13, z), (0.09, 0.12, 0.09), 'lamp', n=6, rings=3)
    stand()
    done("the Jazz Porch's stage: weathered boards on a velvet skirt, three footlights, a vintage microphone, an "
         "upright bass, a stool with a straw boater, a string of warm bulbs")


def f_lily_basin():
    furn('LilyBasin')
    # A low round stone pond: a pale coping, still water, notched lily pads, two lotus flowers, a mossy rock, a
    # frog on the rim, cattails at the back with a firefly resting on one.
    lathe('Body', [(3.4, 0.0), (4.0, 0.0), (4.0, 0.9), (3.4, 0.9)], 'stone', n=16, closed=True)
    lathe('Body', [(3.32, 0.9), (4.06, 0.9), (4.06, 1.0), (3.32, 1.0)], 'stone_light', n=16, closed=True)
    cyl('Body', (0, 0, 0), 3.42, 0.75, 'water', n=16)
    for x, z, r, colr, nt in ((-1.4, -1.2, 0.7, 'lily', 30), (0.6, -2.0, 0.55, 'lily_dark', 160),
                              (1.8, 0.2, 0.6, 'lily', 250), (-0.6, 0.9, 0.5, 'lily_dark', 300),
                              (-2.3, 0.6, 0.45, 'lily', 90)):
        lily_pad((x, 0.75, z), r, 0.03, colr, notch=nt)
    lotus((-1.4, 0.78, -1.2), 1.0)
    lotus((1.8, 0.78, 0.2), 0.85, ang=25)
    sphere('Body', (0.9, 0.6, 1.9), (0.9, 0.5, 0.7), 'stone_dark', n=8, rings=4)
    sphere('Body', (0.9, 1.0, 1.9), (0.6, 0.16, 0.48), 'moss', n=8, rings=3)
    a = math.radians(225)
    frog((3.7 * math.cos(a), 1.0, -3.7 * math.sin(a)), ang=-45)
    cattails(-1.8, 2.3, y=0.75, k=3, tall=2.0, firefly='Glow_Warm_1')
    cattails(2.6, 1.9, y=0.75, k=2, tall=1.6)
    stand()
    done("the Lily Pond's basin: a round stone pond with a pale coping, still water, notched lily pads, two lotus "
         "flowers, a mossy rock, a frog on the rim, cattails with a firefly")


def bs_furniture():
    return {'LilyPadBed': f_lily_pad_bed, 'WillowHammock': f_willow_hammock, 'MudTub': f_mud_tub,
            'HerbBed': f_herb_bed, 'SteamPool': f_steam_pool, 'CypressThrone': f_cypress_throne,
            'LagoonPerch': f_lagoon_perch, 'JazzStage': f_jazz_stage, 'LilyBasin': f_lily_basin,
            **every_furniture('bs')}        # the location-0 pieces: tools/build_built_rooms_kits.py


# --- Styles -------------------------------------------------------------------------------------------

def _courses(y0, y1, n, cols):
    k = (y1 - y0) / n
    return [(y0 + i * k, y0 + (i + 1) * k, cols[i % len(cols)]) for i in range(n)]


STYLES = {
    'haunted_manor': dict(
        title='Haunted Manor: inner walls, a door and furniture (built rooms)', location=1, palette=HM_PALETTE,
        body=[(0.0, 3.2, 'plum_dark'), (3.2, WALL, 'lilac')], reveal='gold', skirting='wood_dark', chair='gold',
        picture='gold', crown='gold', arch='pointed', trim='wood_dark', trim_base='plum_deep', keystone='gold',
        wall_note='plum wainscot under lilac paper, as the Standard Room; gold chair and picture rails and crown, '
                  'dark skirting, on both faces',
        door_note='a pointed arch, dark wood trim with a gold keystone, plinth blocks, both faces',
        post_note='banded as the walls meeting it (dark skirting, plum wainscot, gold chair rail, lilac paper, gold '
                  'picture rail and crown), so their bands turn the corner on it',
        furniture=hm_furniture, locations=(1, 0), decor=lambda: more_decor()),
    'frostfang_lodge': dict(
        title='Frostfang Lodge: inner walls, a door and furniture (built rooms)', location=2, palette=FF_PALETTE,
        body=[(0.0, 3.2, 'wood_dark')] + _courses(3.2, WALL, 13, ('log', 'log_dark')), reveal='log_dark',
        skirting='log_dark', chair='wood_light', picture='wood_light', crown='snow', arch='round', trim='log_dark',
        trim_base='wood_dark', keystone='snow',
        wall_note='log courses over a dark wainscot, as the lodge rooms; light wood rails, a snow cornice, both faces',
        door_note='a round arch, dark log trim with a snow keystone, plinth blocks, both faces',
        post_note='banded as the walls meeting it (dark skirting and wainscot, light rails, the log courses, the '
                  'snow cornice), so their bands turn the corner on it',
        furniture=ff_furniture, locations=(2, 0)),
    'bayou_spa': dict(
        title='Bayou Spa: inner walls, a door and furniture (built rooms)', location=3, palette=BS_PALETTE,
        body=[(0.0, 3.2, 'cypress'), (3.2, WALL, 'sage')], reveal='cypress_dark', skirting='cypress_dark',
        chair='cypress_light', picture='cypress_light', crown='moss', fringe='moss', arch='round', trim='cypress_dark',
        trim_base='cypress', keystone='cypress_light', keystone_moss='moss', post_chamfer=0.08, sit_figure=True,
        wall_note='a cypress wainscot under soft sage, light cypress rails, a moss crown with a scalloped moss '
                  'fringe hanging under it, both faces',
        door_note='a round arch, dark cypress trim with a light cypress keystone under a moss cap, plinth blocks, '
                  'both faces',
        post_note='banded as the walls meeting it (dark skirting, the cypress wainscot, light rails, sage, the moss '
                  'crown), so their bands turn the corner on it; its upright edges chamfered 0.08 (blind review '
                  '2026-10-21: its square edge 0.1 proud of the wainscot read as a dark slit at the joint)',
        furniture=bs_furniture, locations=(3, 0)),
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
    ('Wall_Half', (6, 9), 90),      # through the T at (6, 12): a + joint, and a free end at (6, 6)
]
POSTS = [(0, 0), (12, 0), (0, 12), (12, 12), (6, 12), (6, 24), (24, 0), (6, 6)]


def render(path, direction, res, lo, hi, scale=1.04, cut=None):
    """`cut`: a Roblox point; everything nearer the camera than it is cut away (a section, by clip_start)."""
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
    cam.data.clip_start = 0.1 if cut is None else (cam.location - K.rb2bl(cut)).dot(d)
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
    extra = [render(out / 'joint_free_end.png', (-0.8, 0.5, -0.6), (900, 640), (4.0, 0, 4.5), (8.0, 6.0, 8.0)),
             render(out / 'joint_corner_foot.png', (-0.7, 0.45, -1.0), (900, 640), (10.6, 0, -1.0), (13.4, 4.5, 1.2))]
    shots.append(render(out / 'joint_cross.png', (0.8, 0.9, 1.0), (900, 640), (4.0, 11.0, 10.5), (8.0, 17.6, 14.0)))
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
    sheet = _REV['_compose']([[shots[0], shots[1]], [shots[2], shots[3]], extra, [shots[4], shots[5]],
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


def _sitting(use_pos, look):
    """The 5-stud person sitting on a Sit point, facing `look` (sit_blocks: the same blocks sit_faults
    checks the piece against)."""
    for lo, hi, rgb, _ in sit_blocks(use_pos, look):
        _REV['_block']('sitting', lo, hi, rgb)


def review_sitting(out, fbx, style, manifest):
    """Every Sit piece with the 5-stud person sitting on its Use, and the bar stool at a counter (the stool
    turned to face it on the square in front); in the Manor also the organ's bench (its Pose is Stand)."""
    hm = K.ROOT / 'blender' / 'rooms' / 'haunted_manor'
    hm_man = json.loads((hm / 'manifest.json').read_text())['pieces']
    stool = hm_man['Furniture_BarStool']['attachments']['Use']
    shots, scenes = [], []
    counter = {'haunted_manor': 'Furniture_SnackCounter', 'frostfang_lodge': 'Furniture_CocoaBar'}.get(style)

    def at_counter():
        place(fbx, counter, (0, 0, 0))
        place(hm / 'fbx', 'Furniture_BarStool', (0, 0, -3.0), 180)
        sp = Vector(stool['pos'])
        _sitting((-sp.x, sp.y, -sp.z - 3.0), (0, 0, 1))
        return (-4.6, 0, -4.6), (4.6, 6.2, 1.6)
    if counter:         # Bayou Spa has no counter
        scenes.append(('BarStool_at_' + counter[len('Furniture_'):], at_counter))
    for n, r in manifest.items():
        if r.get('furniture', {}).get('pose') != 'Sit' or n == 'Furniture_BarStool':
            continue

        def one(n=n, r=r):
            place(fbx, n, (0, 0, 0))
            u = r['attachments']['Use']
            _sitting(u['pos'], u['look'])
            sz = r['root']['size']
            # The side view a section just outside the torso (2026-10-21, Bayou blind review: the near armrest
            # hid the thighs, and the shins alone read as a person standing): the near arm and armrest cut away.
            cut = (u['pos'][0] - 1.01, 0, 0) if abs(u['look'][2]) > 0.5 else None
            return (-sz[0] / 2 - 0.3, 0, -sz[2] / 2 - 0.3), (sz[0] / 2 + 0.3, 5.2, sz[2] / 2 + 0.3), cut
        scenes.append((n[len('Furniture_'):], one))
    if 'Furniture_PipeOrgan' in manifest:
        def organ():
            place(fbx, 'Furniture_PipeOrgan', (0, 0, 0))
            dz = manifest['Furniture_PipeOrgan']['decor']['refit']['shift'][2]
            _sitting((0, 1.3, -2.05 + dz), (0, 0, 1))      # f_pipe_organ's bench, refitted
            return (-3.0, 0, -3.0), (3.0, 7.0, 3.0)
        scenes.append(('PipeOrgan_bench', organ))
    for name, build in scenes:
        for view, d in (('side', (-1.0, 0.0, 0.0)), ('three_quarter', (-0.7, 0.45, -1.0))):
            clear()
            lo, hi, *cut = build()
            _REV['_block']('floor', (lo[0] - 1, -0.3, lo[2] - 1), (hi[0] + 1, -0.02, hi[2] + 1), (150, 150, 156))
            shots.append(render(out / f'sitting_{name}_{view}.png', d, (600, 600), lo, hi,
                                cut=cut[0] if cut and view == 'side' else None))
    rows = [shots[i:i + 4] for i in range(0, len(shots), 4)]
    rows[-1] += [None] * (4 - len(rows[-1]))
    return _REV['_compose'](rows, out / 'sitting_sheet.png')


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
        SIT_FIGURE[0] = st.get('sit_figure', False)
        K.start_set(set_dir)
        builds = [('Wall_Half', lambda: wall_half(st)), ('Wall_Door', lambda: wall_door(st)),
                  ('Wall_Post', lambda: wall_post(st))]
        table = st['furniture']()
        ids = [i for i, r in ROWS.items() if r['location'] in st['locations']]
        missing = [i for i in ids if i not in table]
        assert not missing, f'{style}: no build for {missing}'
        builds += [(f'Furniture_{i}', table[i]) for i in ids]
        builds += [(f'Decor_{i}', fn) for i, fn in st.get('decor', dict)().items()]    # the set's own decor
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
        laid = furn_names + [n for n in built if n.startswith('Decor_')]
        rows = [(['Wall_Half', 'Wall_Door', 'Wall_Post'], 2.0, 1.0)]
        for i in range(0, len(laid), 8):
            rows.append((laid[i:i + 8], 2.0, 1.0))
        more = [n for n in built if n in MORE_NAMES and style == 'haunted_manor']   # own sheets (review/more/)
        # Another kit's own location-0 pieces (tools/build_built_rooms_kits.py): their sheets in review/every/.
        every = [n for n in furn_names if style != 'haunted_manor' and ROWS[n[len('Furniture_'):]]['location'] == 0]
        furn_names = [n for n in furn_names if n not in MORE_NAMES and n not in every]
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
        if more and not K.NOPREVIEW:
            print(f"SHEETS {review_more(out / 'review', out / 'fbx', more, manifest['pieces'])}", flush=True)
        if every and not K.NOPREVIEW and (K.ONLY is None or 'every_sheets' in ARGS):
            print(f"SHEETS {review_every(out / 'review', out / 'fbx', every, manifest['pieces'], style)}", flush=True)
        if K.ONLY is None and not K.NOPREVIEW:
            rev = out / 'review'
            faults, sheet = review_walls(rev, out / 'fbx')
            val['assembly'] = {'checked': 'the FBXs assembled round a 2 x 2 cell room (L corners, a T, a + joint, '
                                          'free ends, two doors, straight runs): coplanar same-facing overlaps '
                                          'between pieces',
                               'faults': faults}
            fsheet = review_furniture(rev, out / 'fbx', furn_names, manifest['pieces'])
            esheet = review_elevations(rev, out / 'fbx', furn_names, manifest['pieces'])
            lsheet = review_lying(rev, out / 'fbx', furn_names, manifest['pieces'])
            ssheet = review_sitting(rev, out / 'fbx', style,
                                    {n: r for n, r in manifest['pieces'].items() if n not in MORE_NAMES and n not in every})
            print(f'SHEETS {sheet} {fsheet} {esheet} {lsheet} {ssheet}', flush=True)
            if faults:
                refused.append(f'{style}/assembly: {faults[:4]}')
        (out / 'validation.json').write_text(json.dumps(val, indent=1))
        print(f'SET {style}: {len(built)} pieces; height findings {sorted(val["height_findings"])}', flush=True)
    if refused:
        raise SystemExit(f'REFUSED: {refused}')


# More furniture and decor by purpose (night draft 2026-10-21): their shapes are tools/build_built_rooms_more.py,
# run in this namespace (it uses furn, use, stand, done and the kit's shapes as they are here).
_MORE = TOOLS / 'build_built_rooms_more.py'
exec(compile(_MORE.read_text(encoding='utf8'), str(_MORE), 'exec'))
# The location-0 furniture in the Lodge's and the Spa's own styles (2026-10-21): tools/build_built_rooms_kits.py,
# run here the same way.
_KITS = TOOLS / 'build_built_rooms_kits.py'
exec(compile(_KITS.read_text(encoding='utf8'), str(_KITS), 'exec'))

main()
