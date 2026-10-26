"""The Bar's two key pieces for Haunted Manor's kit (GDD A.13.2, the Bar row; A.13.3, the Stage set).

    Furniture_BarCounter    3 x 1 squares: a counter, its top at 3.7, with a back bar behind it; Use_1..Use_3
                            `Stand`, one on each square in front
    Furniture_SmallStage    2 x 2 squares: a low stage, its deck at 1.0; Use_1 `Dance` on the deck for a performer

The contract is MODELS.md, "Furniture" and "Activity furniture: visitors' spots": furniture keeps every decor rule
(footprint, the 0.4 inset, at most 7 tall, `Body` not colliding, no coplanar faces), nothing floats, and each
visitor's spot is a `Use_<n>` attachment with a `Pose`. Checked here (spots_check), on the built and on the
re-imported triangles: numbered from 1 without a gap, a Pose from MODELS.md's list, a level LookVector, no two
spots on one square; a `Stand` spot on the floor at the middle of a square in front of the front edge, 1.5 in front
of it, facing +Z, its square free of the body; a `Dance` spot on a flat surface inside the footprint with the
5-stud person's whole figure (3.8 across, arms out; 5.2 tall) clear of the body; a `Sit` or `Watch` spot (a Sit
facing the row's front, -Z) on a declared seat with the seated person (sit_blocks) clear of the body; a `Lie` spot
as a bed's Use (lie_faults); a `Swim` spot on the pool's `Water` top, inside its inner edge by 1.5 (swim_faults,
added with tools/build_activity_pool.py, which the Bar's pieces never reach). A pose this
script has no check for is refused, not passed. tools/build_activity_cinema.py (and the next activity sets) load
these definitions; spots_check is the one validator of visitors' spots.

Not a kit of its own: it runs tools/build_built_rooms.py's definitions (every helper there and the kit's shapes,
without its main()) and adds the spots. Its own set, blender/rooms/haunted_manor_bar/, so the Manor's built-rooms
set (and whoever is building other activity pieces into theirs) is not rewritten; the models belong in
HotelKit.HauntedManor like the rest of that set. Pieces.luau has no rows for them yet (the code branch adds
them): PENDING below holds the w, d, layer and height the rows must have, the kit's Pieces check runs against
it, and validation.json `pending_pieces_rows` says so.

    blender -b -t 4 --python-exit-code 1 -P tools/build_activity_bar.py [-- grey] [-- nopreview]

`-- grey` writes the grey silhouettes (three options a piece, ids _A/_B/_C, not for import) to
blender/rooms/haunted_manor_bar/silhouettes/ and review/silhouettes.png. Otherwise the chosen two are built in the
Manor's palette; review/ gets Workbench sheets only (Studio is running): each piece beside the 5-stud person
with a person on every spot, from the game's raised build camera, the front and side elevations at floor level,
from above, and close-ups.
"""
import ast
import json
import math
import re
import sys
from pathlib import Path

_BR = Path(__file__).resolve().parent / 'build_built_rooms.py'
_tree = ast.parse(_BR.read_text(encoding='utf8'))
_tree.body = [n for n in _tree.body if not (isinstance(n, ast.Expr) and isinstance(n.value, ast.Call)
                                             and getattr(n.value.func, 'id', None) == 'main')]
NS = {'__file__': str(_BR), '__name__': 'build_built_rooms'}
exec(compile(_tree, str(_BR), 'exec'), NS)
globals().update({k: v for k, v in NS.items() if not k.startswith('__')})
# From here: K, bpy, Vector, Matrix, furn, attach, declare, box, span, cyl, lathe, sphere, prism, at, finish,
# grounded_check, use_check, _tri_box, _body_bounds, PROXY_IF, USE_SURFACE_TOL, gothic, lifted, candle, render,
# clear, place, _squares, _REV, HM_PALETTE, ROWS (the same objects build_built_rooms.py's functions use).

SET = 'rooms/haunted_manor_bar'
GREY = 'grey' in K.ARGS

# The Pieces rows these need (the code branch adds them; MODELS.md, "Furniture": w, d, layer and height its row's).
PENDING = {
    'BarCounter': {'w': 3, 'd': 1, 'layer': 'Floor', 'height': 6.79, 'location': 0, 'keyFor': ['Bar']},
    'SmallStage': {'w': 2, 'd': 2, 'layer': 'Floor', 'height': 6.95, 'location': 0, 'keyFor': []},
}

# --- Visitors' spots (MODELS.md, "Activity furniture: visitors' spots") -------------------------------

SPOT_POSES = ('Lie', 'Sit', 'Stand', 'Dance', 'Swim', 'Lift', 'Watch', 'Play')
SPOT_RE = re.compile(r'^Use_(\d+)$')
FIGURE_R = 1.9                  # the 5-stud person's half width, arms out (3.8 across; skill `modelling`)
FIGURE_H = 5.2                  # and tall, with a little to spare
TORSO_R = 1.0                   # the feet and torso's half width: the surface under it is flat


def bfurn(id_):
    """Begin Furniture_<id_> on its pending row; its spots replace `Use` (use_check off, spots_check on)."""
    base = id_.split('_')[0]
    row = dict(PENDING[base])
    ROWS[id_] = row
    K.pieces_decor()
    K._PIECES.setdefault(id_, {k: row[k] for k in ('w', 'd', 'layer', 'height')} | {'always': False})
    p = furn(id_)
    p.checks.remove(use_check)
    p.checks.append(spots_check)
    p.spots = {}
    return p


def spot(n, pos, look, pose):
    assert pose in SPOT_POSES, pose
    attach(f'Use_{n}', pos, look)
    K.P.spots[f'Use_{n}'] = pose


def stand_spots():
    """A Stand spot on every square along the front: 1.5 in front of the front edge, facing +Z."""
    p = K.P
    for k in range(p.fw):
        spot(k + 1, (-1.5 * p.fw + 1.5 + 3 * k, 0, -1.5 * p.fd - 1.5), (0, 0, 1), 'Stand')


def _square(piece, pos):
    return (math.floor((pos.x + 1.5 * piece.fw) / 3 + 1e-6), math.floor((pos.z + 1.5 * piece.fd) / 3 + 1e-6))


def _samples(t, k=3):
    a, b, c = t
    for i in range(k + 1):
        for j in range(k + 1 - i):
            u, v = i / k, j / k
            yield a + (b - a) * u + (c - a) * v


def spots_check(piece, tris, stage):
    f = []
    names = sorted((a for a in piece.att if SPOT_RE.match(a)), key=lambda a: int(SPOT_RE.match(a).group(1)))
    if not names:
        return ['no Use_<n> attachment (MODELS.md, "Activity furniture")']
    nums = [int(SPOT_RE.match(a).group(1)) for a in names]
    if nums != list(range(1, len(nums) + 1)):
        f.append(f'spots numbered {nums}, not from 1 without a gap')
    allt = [t for p, ts in tris.items() if p not in ('Root', 'LOD_Proxy') for t in ts]
    hx, hz = 1.5 * piece.fw, 1.5 * piece.fd
    seen = {}
    for a in names:
        pos, look = piece.att[a]
        pose = piece.spots.get(a)
        tag = f'{a} ({stage})'
        if pose not in SPOT_POSES:
            f.append(f'{tag}: Pose {pose!r} not one of {SPOT_POSES}')
            continue
        if look is None or abs(look.y) > 1e-3:
            f.append(f'{tag}: its LookVector {look} is not level')
            continue
        sq = _square(piece, pos)
        if sq in seen:
            f.append(f'{tag}: on the square {sq} with {seen[sq]} (two spots never share a square)')
        seen[sq] = a
        if pose == 'Stand':
            centres = [-hx + 1.5 + 3 * k for k in range(piece.fw)]
            if (abs(pos.y) > 0.01 or abs(pos.z - (-hz - 1.5)) > 0.01 or min(abs(pos.x - c) for c in centres) > 0.01
                    or (look - Vector((0, 0, 1))).length > 1e-3):
                f.append(f'{tag}: a Stand spot is on the floor at x in {centres}, z {-hz - 1.5:g}, looking +Z; '
                         f'it is {K.v3(pos)} looking {K.v3(look)}')
            x0 = -hx + 3 * sq[0]
            lo, hi = Vector((x0 + 0.01, 0.0, -hz - 3 + 0.01)), Vector((x0 + 3 - 0.01, 7.5, -hz - 0.01))
            if any(_tri_box(t, lo, hi) for t in allt):
                f.append(f'{tag}: its square in front is not free of the body')
        elif pose == 'Dance':
            if abs(pos.x) > hx - TORSO_R or abs(pos.z) > hz - TORSO_R:
                f.append(f'{tag}: {K.v3(pos)} is not inside the footprint by the torso ({TORSO_R})')
            for r in (0.0, 0.5, TORSO_R):
                for k in range(1 if r == 0 else 8):
                    ang = 2 * math.pi * k / 8
                    x, z = pos.x + r * math.cos(ang), pos.z + r * math.sin(ang)
                    top = max(K._ray_down(allt, x, z, pos.y + 0.5), default=None)
                    if top is None or abs(top - pos.y) > USE_SURFACE_TOL:
                        f.append(f'{tag}: under the feet at ({x:.2f}, {z:.2f}) the surface is {top}, not '
                                 f'{pos.y:.2f} (flat to {USE_SURFACE_TOL})')
                        break
            for t in allt:
                hit = next((q for q in _samples(t) if pos.y + 0.15 < q.y < pos.y + FIGURE_H
                            and math.hypot(q.x - pos.x, q.z - pos.z) < FIGURE_R), None)
                if hit is not None:
                    f.append(f'{tag}: the body at {K.v3(hit, 2)} is inside the dancer\'s figure '
                             f'({FIGURE_R} round, {FIGURE_H} tall over {pos.y:.2f})')
                    break
        elif pose in ('Sit', 'Watch'):
            # A seat's Sit (Watch: a Sit facing the screen; the piece's front, -Z, is the way a seat faces, as
            # every Sit in the kits looks -Z): inside the footprint, on a declared seat (rule 6, K.seat), on
            # its surface with nothing over it, and the seated 5-stud person (sit_blocks) clear of the body.
            if abs(pos.x) > hx or abs(pos.z) > hz:
                f.append(f'{tag}: {K.v3(pos)} leaves the footprint')
            if pose == 'Watch' and (look - Vector((0, 0, -1))).length > 1e-3:
                f.append(f'{tag}: a Watch spot faces the row\'s front (-Z, turned toward the screen), not {K.v3(look)}')
            if not any(s['x'][0] <= pos.x <= s['x'][1] and s['z'][0] <= pos.z <= s['z'][1] for s in piece.seats):
                f.append(f'{tag}: not on a declared seat (rule 6)')
            top = max(K._ray_down(allt, pos.x, pos.z, pos.y + 0.5), default=None)
            if top is None or abs(top - pos.y) > USE_SURFACE_TOL:
                f.append(f'{tag}: the surface under {K.v3(pos)} is at {top}, not within {USE_SURFACE_TOL} of it')
            over = [h for h in K._ray_down(allt, pos.x, pos.z, pos.y + USE_CLEAR) if h > pos.y + 0.2]
            if over:
                f.append(f'{tag}: something over the seat at {max(over):.2f}')
            f += sit_faults(allt, pos, look, tag)
        elif pose == 'Lie':
            # As a bed's `Use` (use_check): inside the footprint, on its surface with nothing over it, and the
            # lying 5-stud person (lie_faults: in the footprint, on the piece, nothing through it).
            if abs(pos.x) > hx or abs(pos.z) > hz:
                f.append(f'{tag}: {K.v3(pos)} leaves the footprint')
            top = max(K._ray_down(allt, pos.x, pos.z, pos.y + 0.5), default=None)
            if top is None or abs(top - pos.y) > USE_SURFACE_TOL:
                f.append(f'{tag}: the surface under {K.v3(pos)} is at {top}, not within {USE_SURFACE_TOL} of it')
            over = [h for h in K._ray_down(allt, pos.x, pos.z, pos.y + USE_CLEAR) if h > pos.y + 0.2]
            if over:
                f.append(f'{tag}: something over the Lie point at {max(over):.2f}')
            if not getattr(piece, 'lie', None):
                piece.lie = {'rise': tuple(LIE_RISE), 'waived': None}
            f += lie_faults(piece, allt, pos, look, tag)
        elif pose == 'Swim':
            f += swim_faults(piece, tris, pos, tag)
        else:
            f.append(f'{tag}: this script has no check for Pose {pose} (refused, not passed)')
    return f


SWIM_DEPTH = 1.5                # MODELS.md, `Swim`: the body's middle 1.5 under the water's surface
SWIM_IN = 1.5                   # and the spot inside the pool's inner edge by 1.5
SWIM_CLEAR = 2.5                # nothing of the body over the water within SWIM_IN for this far (the head is 1.0 up)
SWIM_FINDINGS = {}              # Furniture_<Id> -> where the swimmer's body reaches against the floor (a finding)


def swim_faults(piece, tris, pos, tag):
    """A `Swim` spot (MODELS.md, "Activity furniture"): the pool's one `Water` part, not colliding; the spot on
    the water's top; inside the inner edge by SWIM_IN: within SWIM_IN round it nothing of the rest of the piece
    from the basin's floor to SWIM_CLEAR over the water (no rim, no spout, no stream on a swimmer). Where the
    body then reaches (its middle SWIM_DEPTH under the surface, the feet 4 under it) against the floor the pool
    stands on is recorded in SWIM_FINDINGS, not refused: the floor cannot be dug (a finding for the code)."""
    f = []
    water = tris.get('Water')
    if not water:
        return [f'{tag}: a Swim spot and no Water part (MODELS.md: a pool\'s water is one part, `Water`)']
    if piece.collide.get('Water', True):
        f.append(f'{tag}: Water collides (MODELS.md: not colliding, CanQuery false)')
    wtop = max(K._ray_down(water, pos.x, pos.z, pos.y + 1.0), default=None)
    if wtop is None or abs(wtop - pos.y) > 0.02:
        f.append(f'{tag}: not on the water\'s surface ({wtop} under {K.v3(pos)})')
        return f
    solid = [t for p, ts in tris.items() if p not in ('Root', 'LOD_Proxy', 'Water') for t in ts]
    floor = max(K._ray_down(solid, pos.x, pos.z, pos.y), default=None)
    if floor is None:
        return f + [f'{tag}: no basin floor under the spot']
    for r in (0.0, 0.5, 1.0, SWIM_IN):
        for k in range(1 if r == 0 else 16):
            a = 2 * math.pi * k / 16
            x, z = pos.x + r * math.cos(a), pos.z + r * math.sin(a)
            hits = K._ray_down(solid, x, z, pos.y + SWIM_CLEAR)
            top = max(hits, default=None)
            if top is None or top > floor + 0.05:
                f.append(f'{tag}: {r} from the spot at ({x:.2f}, {z:.2f}) the piece is at {top} (the basin floor '
                         f'{floor:.2f}): not inside the inner edge by {SWIM_IN}, or something over the water')
                return f
    SWIM_FINDINGS.setdefault(piece.name, {})[tag.split(' ')[0]] = {
        'surface': round(pos.y, 3), 'basin_floor': round(floor, 3), 'body_middle': round(pos.y - SWIM_DEPTH, 3),
        'feet': round(pos.y - SWIM_DEPTH - 2.5, 3), 'head_top': round(pos.y - SWIM_DEPTH + 2.5, 3)}
    return f


def sdone(note):
    """LOD_Proxy where the contract asks, finish(), the furniture record with its spots."""
    piece = K.P
    lo, hi = _body_bounds(piece)
    if max(piece.fw, piece.fd) > PROXY_IF[0] or hi.y > PROXY_IF[1]:
        box('LOD_Proxy', (lo + hi) / 2, hi - lo, 'grey', collide=False)
    rec = finish(proxy=False, note=note)
    rec['furniture'] = {'id': piece.name[len('Furniture_'):], 'pose': None,
                        'spots': {a: piece.spots[a] for a in sorted(piece.spots, key=lambda a: int(a[4:]))},
                        'keyFor': piece.row['keyFor'], 'pieces_height': piece.row['height'],
                        'model_top': round(hi.y, 3), 'pieces_row': 'pending (PENDING in the build script)'}
    return rec


def loft(part, sections, col):
    """A closed solid through horizontal sections [(y, [(x, z), ...]), ...], bottom to top, each as many points."""
    k = len(sections[0][1])
    verts = [Vector((x, y, z)) for y, pts in sections for x, z in pts]
    faces = [tuple(range(k - 1, -1, -1)), tuple(range(k * (len(sections) - 1), k * len(sections)))]
    for s in range(len(sections) - 1):
        a, b = s * k, (s + 1) * k
        faces += [(a + i, a + (i + 1) % k, b + (i + 1) % k, b + i) for i in range(k)]
    K._add(part, verts, faces, col)


def bottle(x, y, z, h, r, col, part='Body'):
    """A bottle: its body, the shoulder narrowing to the neck's top (32 triangles)."""
    lathe(part, [(r, 0), (r, h * 0.62), (r * 0.4, h)], col, n=6, base=(x, y, z))


def arc(r, a0, a1, n, cz=0.0):
    return [(r * math.cos(math.radians(a0 + (a1 - a0) * i / n)), cz + r * math.sin(math.radians(a0 + (a1 - a0) * i / n)))
            for i in range(n + 1)]


def apron(r, back):
    """The stage's outline from above: a half disc toward -Z, square behind (x, z)."""
    return arc(r, 180, 360, 10) + [(r, back), (-r, back)]


# --- Grey silhouettes: three options a piece ---------------------------------------------------------

G, D, L = 'grey', 'stone_dark', 'stone'


def counter_front(z1, top=3.7, z0=-1.1):
    """The counter itself (every option): a plinth, the cabinet, the top overhanging the front 0.4, a foot rail."""
    span('Body', (-3.95, 0, z0 + 0.5), (3.95, 0.3, z1 - 0.04), D)
    span('Body', (-4.0, 0.3, z0 + 0.4), (4.0, top - 0.25, z1 - 0.04), G)
    span('Body', (-4.1, top - 0.25, z0), (4.1, top, z1), L)
    cyl('Body', (0, 0, 0), 0.07, 7.8, D, n=6, m=at((-3.9, 0.75, z0 + 0.12), rz=-90))
    for x in (-3.4, 0.0, 3.4):
        span('Body', (x - 0.05, 0.7, z0 + 0.1), (x + 0.05, 0.8, z0 + 0.42), D)


def sil_counter_a():
    bfurn('BarCounter_A')
    # A: the counter and, behind it, a back bar: a cabinet, two shelves of bottles in side bays, an arched mirror.
    counter_front(0.46)
    span('Body', (-4.0, 0, 0.5), (4.0, 3.95, 1.1), D)
    span('Body', (-3.9, 3.95, 0.85), (3.9, 6.3, 1.08), G)
    for x in (-3.85, -1.4, 1.4, 3.85):
        span('Body', (x - 0.13, 3.95, 0.52), (x + 0.13, 6.45, 1.09), D)
    for x0, x1 in ((-3.75, -1.5), (1.5, 3.75)):
        for y in (4.75, 5.55):
            span('Body', (x0, y, 0.55), (x1, y + 0.1, 0.86), D)
        for k in range(3):
            x = x0 + 0.4 + k * 0.72
            bottle(x, 3.95, 0.7, 0.7, 0.14, L)
            bottle(x + 0.2, 4.85, 0.7, 0.6, 0.12, L)
    prism('Body', lifted(gothic(-1.0, 1.0, 1.3, 2.0), 4.1), 0.82, 0.85, L, plane='xy')
    span('Body', (-4.08, 6.3, 0.5), (4.08, 6.55, 1.1), D)
    stand_spots()
    sdone('A: a counter with a back bar behind it (bottles on two shelves, an arched mirror), 6.55 tall')


def sil_counter_b():
    bfurn('BarCounter_B')
    # B: an island counter, the full depth, a low stepped rack of bottles on its back half and a tap tower.
    span('Body', (-3.95, 0, -0.6), (3.95, 0.3, 0.6), D)
    span('Body', (-4.0, 0.3, -0.7), (4.0, 3.45, 0.7), G)
    span('Body', (-4.1, 3.45, -1.1), (4.1, 3.7, 1.1), L)
    cyl('Body', (0, 0, 0), 0.07, 7.8, D, n=6, m=at((-3.9, 0.75, -0.98), rz=-90))
    for x in (-3.4, 0.0, 3.4):
        span('Body', (x - 0.05, 0.7, -1.0), (x + 0.05, 0.8, -0.68), D)
    span('Body', (-3.8, 3.7, 0.25), (3.8, 4.25, 1.05), D)
    span('Body', (-3.8, 4.25, 0.6), (3.8, 4.8, 1.05), D)
    for k in range(7):
        x = -3.4 + k * 1.13
        bottle(x, 4.25, 0.4, 0.7, 0.13, L)
        bottle(x + 0.5, 4.8, 0.8, 0.7, 0.13, L)
    cyl('Body', (0, 3.7, -0.35), 0.12, 1.0, D, n=6)
    span('Body', (-0.6, 4.6, -0.45), (0.6, 4.75, -0.25), D)
    stand_spots()
    sdone('B: an island counter the full depth, a low stepped bottle rack on its back half, a tap tower; 5.5 tall')


def sil_counter_c():
    bfurn('BarCounter_C')
    # C: the counter with a canopy on two end posts, glasses hanging from it, and a low back ledge of bottles.
    counter_front(1.1)
    span('Body', (-3.8, 3.7, 0.55), (3.8, 4.1, 1.05), D)
    for k in range(6):
        bottle(-3.3 + k * 1.3, 4.1, 0.8, 0.7, 0.13, L)
    for x in (-3.85, 3.85):
        span('Body', (x - 0.14, 3.7, 0.6), (x + 0.14, 6.35, 0.9), D)
    span('Body', (-4.1, 6.35, -0.7), (4.1, 6.7, 1.05), G)
    for k in range(7):
        x = -3.0 + k * 1.0
        lathe('Body', [(0.0, 5.5), (0.18, 5.6), (0.2, 5.85), (0.03, 5.95), (0.03, 6.35)], L, n=6, base=(x, 0, -0.2))
    stand_spots()
    sdone('C: the counter under a canopy on two posts, glasses hanging from it, a low back ledge of bottles; 6.7 tall')


def sil_stage_a():
    bfurn('SmallStage_A')
    # A: a square deck, a side step, footlights along the front, a microphone stand.
    span('Body', (-2.6, 0, -2.6), (1.9, 0.86, 2.6), G)
    span('Body', (-2.6, 0.86, -2.6), (2.0, 1.0, 2.6), L)
    span('Body', (2.0, 0, -1.0), (2.6, 0.5, 1.0), D)
    for x in (-1.9, -0.6, 0.6):
        span('Body', (x - 0.25, 1.0, -2.5), (x + 0.25, 1.25, -2.3), D)
    mic(-0.3, -1.75)
    spot(1, (-0.3, 1.0, 0.35), (0, 0, -1), 'Dance')
    sdone('A: a plain square deck with a side step, three footlights and a microphone stand; 4.5 tall')


def sil_stage_b():
    bfurn('SmallStage_B')
    # B: a round-fronted apron deck, a pointed-arch backdrop with curtains drawn aside, footlights, a microphone.
    prism('Body', apron(2.5, 2.5), 0.0, 0.88, G, plane='xz')
    prism('Body', apron(2.6, 2.6), 0.86, 1.0, L, plane='xz')
    backdrop(G, D, L, D)
    mic(0.0, -1.75)
    spot(1, (0.0, 1.0, 0.3), (0, 0, -1), 'Dance')
    sdone('B: a round-fronted apron deck under a pointed-arch backdrop with curtains drawn aside; 6.95 tall')


def sil_stage_c():
    bfurn('SmallStage_C')
    # C: a square deck under a proscenium: two posts at the front corners, a valance, drapes down the posts.
    span('Body', (-2.6, 0, -2.6), (2.6, 0.86, 2.6), G)
    span('Body', (-2.6, 0.86, -2.6), (2.6, 1.0, 2.6), L)
    for x in (-2.35, 2.35):
        span('Body', (x - 0.2, 1.0, -2.55), (x + 0.2, 6.4, -2.15), D)
    span('Body', (-2.6, 6.4, -2.6), (2.6, 6.9, -2.1), D)
    for sx in (-1, 1):
        loft('Body', [(1.0, [(sx * 2.15, -2.5), (sx * 1.7, -2.5), (sx * 1.7, -2.2), (sx * 2.15, -2.2)]),
                      (6.4, [(sx * 2.15, -2.5), (sx * 1.2, -2.5), (sx * 1.2, -2.2), (sx * 2.15, -2.2)])], L)
    mic(0.0, -1.2)
    spot(1, (0.0, 1.0, 1.0), (0, 0, -1), 'Dance')
    sdone('C: a square deck framed by a proscenium at the front (posts, valance, drapes); 6.9 tall')


def mic(x, z, deck=1.0, metal='iron', head='iron', clip='gold', r=0.045, hr=0.13):
    """A microphone stand on the deck: a round base, the pole, a clip, the microphone at a performer's mouth."""
    cyl('Body', (x, deck, z), 0.3, 0.06, metal, n=10)
    cyl('Body', (x, deck + 0.06, z), r, 4.04, metal, n=6)
    cyl('Body', (x, deck + 4.1, z), r + 0.04, 0.12, clip, n=6)
    sphere('Body', (x, deck + 4.22 + hr * 1.4, z), (hr, hr * 1.5, hr), head, n=8, rings=4)


def backdrop(frame, curtain, panel, moon, deck=1.0):
    """The stage's backdrop at its back edge: two posts and a pointed-arch head (z 2.08..2.55), a flat panel
    behind (z 2.42..2.545) under the head's gable, two curtains drawn aside to the posts (gathered at 3.4, flared to the deck, their tops at 5.95 hidden in the
    head, which is 6.0 or more everywhere), a crescent."""
    for sx in (-1, 1):
        span('Body', (2.2 if sx > 0 else -2.5, deck - 0.02, 2.08), (2.5 if sx > 0 else -2.2, 5.32, 2.55), frame)
    inner = [(x, y) for x, y in K.arch_points(-2.2, 2.2, 5.3, 6.55, n=4)]
    head = [(-2.52, 5.3)] + inner + [(2.52, 5.3), (2.52, 6.0), (0.0, 6.95), (-2.52, 6.0)]
    prism('Body', head, 2.1, 2.53, frame, plane='xy')        # as deep as the posts, near enough (review 2)
    prism('Body', [(-2.2, deck - 0.04), (2.2, deck - 0.04), (2.2, 6.05), (0.0, 6.85), (-2.2, 6.05)], 2.42, 2.545, panel,
          plane='xy')
    for sx in (-1, 1):
        def half(w):
            x0 = -2.2
            xs = [x0 + w * i / 6 for i in range(7)]
            front = [(x, 2.3 - 0.07 * (1 - math.cos(math.pi * 2 * i / 3))) for i, x in enumerate(xs)]
            pts = front + [(xs[-1], 2.44), (x0, 2.44)]
            return [(-x if sx > 0 else x, z) for x, z in pts]
        loft('Body', [(deck - 0.02, half(0.9)), (3.4, half(0.45)), (4.6, half(0.9)), (5.95, half(1.5))], curtain)
    out = [(0.5 * math.cos(math.radians(a)), 0.5 * math.sin(math.radians(a))) for a in (60 + 30 * i for i in range(9))]
    inn = [(0.22 + 0.434 * math.cos(math.radians(a)), 0.434 * math.sin(math.radians(a)))
           for a in (274 - 188 * i / 6 for i in range(1, 6))]
    prism('Body', [(x, y + 5.55) for x, y in out + inn], 2.38, 2.42, moon, plane='xy')


SILHOUETTES = [sil_counter_a, sil_counter_b, sil_counter_c, sil_stage_a, sil_stage_b, sil_stage_c]


def _label(text, x, z, size=0.9):
    cu = bpy.data.curves.new('lbl', 'FONT')
    cu.body = text
    cu.size = size
    cu.align_x = 'CENTER'
    ob = bpy.data.objects.new('lbl', cu)
    bpy.context.scene.collection.objects.link(ob)
    ob.location = K.rb2bl((x, 0.02, z))
    ob.data.materials.append(_REV['_flat']('flat_ink', (20, 20, 25)))
    return ob


def people_on_spots(manifest_rec, cx, cz=0.0):
    for a, pose in manifest_rec['furniture']['spots'].items():
        u = manifest_rec['attachments'][a]
        _REV['_person'](Vector((cx + u['pos'][0], u['pos'][1], 0)), cz + u['pos'][2])


def silhouette_sheet(out, fbx, recs):
    """The six options in two rows, each on its squares, a person on every spot and one beside it, labelled, from
    the game's build camera (51 degrees up, from the front a little to one side); then each row level from the
    front at floor level."""
    rows = (('BarCounter_A', 'BarCounter_B', 'BarCounter_C'), ('SmallStage_A', 'SmallStage_B', 'SmallStage_C'))

    def lay(row, z0, labels):
        x = 0.0
        for i in row:
            n = f'Furniture_{i}'
            size = recs[n]['root']['size']
            cx = x + size[0] / 2
            place(fbx, n, (cx, 0, z0))
            for a in range(int(round(size[0] / 3))):
                for b in range(int(round(size[2] / 3))):
                    x0, zz = cx - size[0] / 2 + 3 * a, z0 - size[2] / 2 + 3 * b
                    shade = (205, 205, 210) if (a + b) % 2 else (185, 185, 192)
                    _REV['_block']('sq', (x0 + 0.03, -0.06, zz + 0.03), (x0 + 2.97, -0.01, zz + 2.97), shade)
            people_on_spots(recs[n], cx, z0)
            _REV['_person'](Vector((cx + size[0] / 2 + 2.2, 0, 0)), z0)
            if labels:
                _label(i.split('_')[1], cx, z0 - size[2] / 2 - 5.0)
            x += size[0] + 6.0
        return x
    shots = []
    clear()
    x = max(lay(rows[0], 0.0, True), lay(rows[1], 13.0, True))
    _REV['_block']('floor', (-3, -0.3, -10), (x + 2, -0.07, 18), (150, 150, 156))
    shots.append(render(out / 'silhouettes_game.png', (-0.35, 1.25, -1.0), (1600, 900), (-2, 0, -9), (x, 7.2, 17),
                        scale=1.0))
    for k, row in enumerate(rows):
        clear()
        x = lay(row, 0.0, False)
        shots.append(render(out / f'silhouettes_front_{k + 1}.png', (0.0, 0.05, -1.0), (1600, 420), (-2, -0.3, -5),
                            (x, 7.4, 3), scale=1.02))
    return shots


# --- The chosen two, in the Manor's dress -------------------------------------------------------------

def bar_counter():
    bfurn('BarCounter')
    # The counter (option A, his to judge): its top at 3.7 (a counter 3.4-3.8; a bar stool's seat 2.6 sits
    # under its 3.45 underside), overhanging the cabinet's front by 0.4 for a stool's knees; a gold foot rail.
    z0, z1, top = -1.1, 0.46, 3.7
    span('Body', (-3.95, 0, -0.6), (3.95, 0.3, 0.4), 'wood_dark')
    span('Body', (-4.0, 0.3, -0.7), (4.0, 3.45, 0.42), 'plum_dark')
    for c, hw in ((-2.68, 0.95), (0.0, 1.15), (2.68, 0.95)):          # a pointed-arch panel on each square
        prism('Body', lifted(gothic(c - hw, c + hw, 1.75, 2.5), 0.55), -0.76, -0.7, 'crimson', plane='xy')
    for x in (-3.86, -1.5, 1.5, 3.86):
        span('Body', (x - 0.13, 0.0, -0.84), (x + 0.13, 3.46, -0.66), 'wood_dark')
    span('Body', (-4.1, 3.45, z0), (4.1, top, z1), 'wood_dark', bevel=0.06)
    cyl('Body', (0, 0, 0), 0.07, 7.8, 'gold', n=6, m=at((-3.9, 0.75, -0.98), rz=-90))
    for x in (-3.86, -1.5, 1.5, 3.86):          # the rail's brackets, into the posts
        span('Body', (x - 0.05, 0.7, -1.0), (x + 0.05, 0.8, -0.83), 'gold')
    # On the top: a gold tap tower over an iron drip tray, two pints, a goblet of wine and a candle.
    # The taps between the first and the middle guest (the second blind review: in the middle they hid the mirror).
    tx = -1.5
    span('Body', (tx - 0.75, top, -0.55), (tx + 0.75, top + 0.06, -0.05), 'iron')
    cyl('Body', (tx, top + 0.06, -0.3), 0.11, 0.85, 'gold', n=6)
    span('Body', (tx - 0.62, top + 0.88, -0.38), (tx + 0.62, top + 1.0, -0.22), 'gold')
    for x, colr in ((tx - 0.45, 'crimson'), (tx, 'black'), (tx + 0.45, 'crimson')):
        span('Body', (x - 0.04, top + 0.62, -0.34), (x + 0.04, top + 0.89, -0.26), 'gold')
        cyl('Body', (x, top + 0.99, -0.3), 0.05, 0.42, colr, n=5)
    for x, z in ((0.6, -0.45), (2.0, -0.55)):
        cyl('Body', (x, top, z), 0.16, 0.42, 'amber', n=6)
        cyl('Body', (x, top + 0.42, z), 0.17, 0.08, 'cream', n=6)
    lathe('Body', [(0.16, 0), (0.04, 0.05), (0.04, 0.28), (0.2, 0.42), (0.17, 0.62)], 'wine', n=6,
          base=(3.2, top, -0.4))
    candle('Glow_Warm_1', -3.4, top, -0.3, cup='crimson')
    # The back bar: a cabinet whose top is a ledge at 3.95, two shelves of bottles in the side bays between dark
    # posts, a pointed-arch mirror in a gold frame in the middle, a cornice with gold finials (the gold crest over
    # the mirror went: the blind review 2026-10-26 read it as a blank name plate); its back panel plum, lighter
    # than the posts (the review: dark on dark).
    span('Body', (-4.0, 0, 0.5), (4.0, 3.95, 1.1), 'wood_dark')
    span('Body', (-3.9, 3.92, 0.85), (3.9, 6.3, 1.08), 'plum')
    for x in (-3.85, -1.4, 1.4, 3.85):
        span('Body', (x - 0.13, 3.9, 0.52), (x + 0.13, 6.45, 1.09), 'wood_dark')
        sphere('Body', (x, 6.67, 0.8), 0.12, 'gold', n=6, rings=3)
    cols = (('wine', 'slime', 'amber'), ('teal', 'amber', 'wine'), ('moon', 'wine', 'slime'))
    for side, (x0, x1) in enumerate(((-3.72, -1.53), (1.53, 3.72))):
        for y in (4.75, 5.55):
            span('Body', (x0 - 0.03, y, 0.55), (x1 + 0.03, y + 0.1, 0.86), 'wood')
        for k in range(3):
            x = x0 + 0.38 + k * 0.72
            bottle(x, 3.95, 0.7, 0.7, 0.14, cols[k][side])
            if k != 1:          # two a shelf over three on the ledge (the budget: 1,500)
                bottle(x + 0.12, 4.85, 0.7, 0.62, 0.12, cols[(k + 1) % 3][side])
                bottle(x - 0.06, 5.65, 0.7, 0.56, 0.12, cols[(k + 2) % 3][side])
    prism('Body', lifted(gothic(-1.12, 1.12, 1.35, 2.1), 4.02), 0.83, 0.85, 'gold', plane='xy')
    prism('Body', lifted(gothic(-0.98, 0.98, 1.3, 1.92), 4.1), 0.8, 0.83, 'moon', plane='xy')
    for x in (-0.55, 0.55):                                             # two glowing potions on the ledge
        bottle(x, 3.95, 0.66, 0.6, 0.13, 'brew', part='Glow_Magic_1')
    span('Body', (-4.08, 6.3, 0.5), (4.08, 6.55, 1.1), 'wood_dark')
    stand_spots()
    sdone('a Haunted Manor bar: a plum counter with three pointed-arch crimson panels between dark posts, a dark '
          'wood top at 3.7 with a gold tap tower, two pints, a goblet and a candle, a gold foot rail; behind it a '
          'back bar of bottles on two shelves either side of a gold-framed pointed-arch mirror, two glowing potions '
          'on its ledge, a cornice with gold finials')


def small_stage():
    bfurn('SmallStage')
    # Option B, his to judge: a round-fronted apron deck at 1.0 on a crimson skirt, a pointed-arch backdrop in
    # dark wood with crimson curtains drawn aside before a night-blue panel and a gold crescent, a row of footlights.
    # Blind review 2026-10-26 (README): the step and the gold keystone went (a crate, a blank plate), the curtains
    # crimson (plum on night blue did not separate), the four footlight hoods one gold trough along the front (they
    # read as litter), the microphone stand thicker (a hairline from the game's camera).
    deck = 1.0
    prism('Body', apron(2.5, 2.5), 0.0, 0.88, {'top': 'wood_dark', 'bottom': 'wood_dark', 'rest': 'crimson'},
          plane='xz')
    prism('Body', apron(2.6, 2.6), 0.86, deck, {'top': 'wood', 'rest': 'wood_dark'}, plane='xz')
    backdrop('wood_dark', 'crimson', 'night', 'gold', deck)
    # The footlights: a low gold trough along the curved front edge (radius 2.22..2.5), five warm bulbs set in it.
    a0, a1 = 196, 344
    trough = arc(2.5, a0, a1, 12) + arc(2.22, a1, a0, 12)
    prism('Body', trough, deck - 0.02, deck + 0.2, 'gold', plane='xz')
    for k in range(5):
        a = math.radians(a0 + 10 + (a1 - a0 - 20) * k / 4)
        sphere('Glow_Warm_1', (2.36 * math.cos(a), deck + 0.2, 2.36 * math.sin(a)), (0.12, 0.1, 0.12), 'lamp', n=6,
               rings=4)
    mic(0.0, -1.85, r=0.07, hr=0.17)
    spot(1, (0.0, deck, 0.3), (0, 0, -1), 'Dance')
    sdone('a Haunted Manor small stage: a round-fronted deck at 1.0 on a crimson skirt, a gold footlight trough '
          'with five warm bulbs along its front, a microphone stand; behind it a dark-wood pointed arch, crimson curtains '
          'drawn aside before a night-blue panel with a gold crescent moon')


# --- Review (Workbench on light grey: Studio is running, no EEVEE or Cycles) --------------------------

def review_final(out, fbx, recs):
    names = ['Furniture_BarCounter', 'Furniture_SmallStage']
    shots = []

    def scene(spots=True):
        clear()
        x = 0.0
        for n in names:
            size = recs[n]['root']['size']
            cx = x + size[0] / 2
            place(fbx, n, (cx, 0, 0))
            _squares(cx, size)
            if spots:
                people_on_spots(recs[n], cx)
            x += size[0] + 4.0
        _REV['_person'](Vector((x + 0.5, 0, 0)), 0.0)
        _REV['_block']('floor', (-3, -0.3, -8), (x + 4, -0.07, 6), (150, 150, 156))
        return x
    x = scene()
    lo, hi = (-1.5, 0, -5), (x + 3, 7.2, 3.5)
    shots.append(render(out / '1_game_camera.png', (-0.45, 1.28, -1.0), (1400, 800), lo, hi, scale=1.02))
    shots.append(render(out / '2_front_three_quarter.png', (-0.7, 0.45, -1.0), (1400, 800), lo, hi, scale=1.02))
    shots.append(render(out / '3_back_three_quarter.png', (0.7, 0.55, 1.0), (1400, 800), lo, hi, scale=1.02))
    x = scene(spots=False)
    shots.append(render(out / '4_front_level.png', (0.0, 0.0, -1.0), (1400, 800), (-1.5, -0.3, -5), (x + 3, 7.4, 3.5),
                        scale=1.02))
    shots.append(render(out / '5_top.png', (0.0, 1.0, -0.02), (1400, 800), (-1.5, 0, -5), (x + 3, 7.4, 3.5), scale=1.02))
    # The side elevations at floor level: each piece turned 90 degrees on its squares (anything floating shows
    # the background under it).
    clear()
    x = 0.0
    for n in names:
        size = recs[n]['root']['size']
        cx = x + size[2] / 2
        place(fbx, n, (cx, 0, 0), 90)
        _squares(cx, size, 90)
        x += size[2] + 3.0
    _REV['_person'](Vector((x + 1.0, 0, 0)), 0.0)
    shots.append(render(out / '6_side_level.png', (0.0, 0.0, -1.0), (1400, 800), (-1.5, -0.3, -5), (x + 3, 7.4, 5),
                        scale=1.02))
    # Close-ups where a person uses them: a guest at the counter's middle spot, the performer at the microphone.
    clear()
    place(fbx, names[0], (0, 0, 0))
    people_on_spots(recs[names[0]], 0.0)
    shots.append(render(out / '7_close_counter.png', (-0.55, 0.5, -1.0), (1000, 800), (-2.5, 0, -4.2), (2.5, 7.0, 1.2),
                        scale=1.0))
    clear()
    place(fbx, names[1], (0, 0, 0))
    people_on_spots(recs[names[1]], 0.0)
    shots.append(render(out / '8_close_stage.png', (-0.6, 0.55, -1.0), (1000, 800), (-3, 0, -3), (3, 7.0, 3),
                        scale=1.0))
    return shots


# --- The set ------------------------------------------------------------------------------------------

def patch_fixup(path, manifest):
    """The kit's import_fixup.luau, plus each spot's Pose (an attribute on its Use_<n> attachment)."""
    s = path.read_text(encoding='utf-8')
    spots = {n: r['furniture']['spots'] for n, r in manifest['pieces'].items() if 'furniture' in r}
    lines = []
    for line in s.split('\n'):
        lines.append(line)
        for n, sp in spots.items():
            if line == f'\t{n} = {{':
                lines.append('\t\tposes = { ' + ', '.join(f'{a} = "{p}"' for a, p in sp.items()) + ' },')
    s = '\n'.join(lines)
    old = '\t\tatt.Parent = root\n'
    assert old in s, 'import_fixup.luau changed: the Pose patch has no anchor'
    s = s.replace(old, '\t\tif spec.poses and spec.poses[a[1]] then\n\t\t\tatt:SetAttribute("Pose", spec.poses[a[1]])'
                  '\n\t\tend\n' + old, 1)
    s = s.replace('-- and hides LOD_Proxy.', '-- and hides LOD_Proxy; each visitor spot Use_<n> gets its Pose attribute '
                  '(tools/build_activity_bar.py).', 1)
    path.write_text(s, encoding='utf-8')


def main():
    K.use_palette(HM_PALETTE)
    if GREY:
        K.IMPORT_CHECKS = False         # drafts with _A/_B/_C ids, not for import
        K.start_set(SET + '/silhouettes')
        for fn in SILHOUETTES:
            fn()
        recs = {p.name: r for p, r, _ in K.BUILT}
        out = K.ROOT / 'blender' / SET / 'silhouettes'
        (out / 'manifest.json').write_text(json.dumps({'pieces': recs}, indent=1))
        if not K.NOPREVIEW:
            print('SHEETS', silhouette_sheet(out / 'review', out / 'fbx', recs), flush=True)
        return
    K.start_set(SET)
    bar_counter()
    small_stage()
    built = [p.name for p, _, _ in K.BUILT]
    K.end_set('Haunted Manor: the Bar\'s counter and small stage (GDD A.13)', [(built, 3.0, 1.0)], sheet=False)
    out = K.ROOT / 'blender' / SET
    manifest = json.loads((out / 'manifest.json').read_text())
    patch_fixup(out / 'import_fixup.luau', manifest)
    val = json.loads((out / 'validation.json').read_text())
    val['spots'] = {n: {'spots': r['furniture']['spots'],
                        'checked': 'spots_check on the built and the re-imported triangles: Use_<n> from 1 without '
                                   'a gap, a Pose from MODELS.md\'s list, a level LookVector, no two spots on one '
                                   'square; Stand on the floor at a front square\'s middle 1.5 in front, facing +Z, '
                                   'its square free of the body; Dance on a flat surface (to 0.15 over the torso\'s '
                                   f'{TORSO_R} round) inside the footprint, nothing of the body within the '
                                   f'figure ({FIGURE_R} round, {FIGURE_H} tall)'}
                    for n, r in manifest['pieces'].items()}
    val['pending_pieces_rows'] = {
        'note': 'Pieces.luau has no rows for these yet (the code branch adds them). The kit\'s Pieces check ran '
                'against these values; the rows must say the same w, d, layer and height (to 0.3).',
        **{f'Furniture_{i}': {k: r[k] for k in ('w', 'd', 'layer', 'height', 'keyFor')} | {'furniture': True}
           for i, r in PENDING.items()}}
    val['not_validated'] = val.get('not_validated', [])[:1] + [
        'the attachments and each Use_<n> Pose attribute exist only in manifest.json until import_fixup.luau makes '
        'them', 'a visitor walking to a spot, standing or dancing: no walker or animation has run',
        'Pieces.luau rows (pending, above)']
    (out / 'validation.json').write_text(json.dumps(val, indent=1))
    if not K.NOPREVIEW:
        print('SHEETS', review_final(out / 'review', out / 'fbx', manifest['pieces']), flush=True)
    bad = [n for n, r in val['pieces'].items() if not r['ok']]
    print(f'SET {SET}: {built}; validation faults in {bad}', flush=True)
    if bad:
        raise SystemExit(f'VALIDATION FAULTS: {bad}')


try:
    main()
except K.Refused as e:
    print(str(e), flush=True)
    raise SystemExit('REFUSED')
