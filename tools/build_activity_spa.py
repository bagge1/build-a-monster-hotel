"""The Spa's two key pieces for Haunted Manor's kit (GDD A.13.2, the Spa row; A.13.3, the Poolside set serves it).

    Furniture_HotTub        3 x 3 squares: a round tub standing on the floor (the floor cannot be dug): violet and
                            plum staves under two gold hoops, a pale stone coping at 2.45, two treads (0.6, 1.2) in
                            each corner, one `Water` part, an underwater bench round the inside; Use_1..Use_4 `Sit`
                            on the bench, the head over the water, one a square; on the back corners a gold brazier
                            of steam stones over glowing embers (Glow_Warm_2) and a candelabra (Glow_Warm_1)
    Furniture_MassageTable  1 x 2 squares: a plum leather pad on four turned legs under a cream sheet, a horseshoe
                            face cradle at the head end, a shelf of towels and oils; Use_1 `Lie` (face down)

The contract is MODELS.md, "Furniture" and "Activity furniture: visitors' spots", as for the Bar, the Cinema, the
Pool and the Gym (tools/build_activity_bar.py, whose definitions this runs: spot, spots_check, sdone, loft,
patch_fixup, _label, and through it tools/build_built_rooms.py's kit). One branch of the one spot validator was
added for these (purely additive; no other set's spots reach it): a `Sit` spot under a piece's `Water` top (a hot
tub's bench) is held by soak_faults: the Water not colliding, the spot on a declared seat with the solid body
(the water left out) under it and nothing over it, the water over the seated torso at least SOAK_MIN and at
most SOAK_MAX over the seat (the head above it), and the seated 5-stud person (sit_blocks) clear of the body.

Here, for these pieces only: a tub's bench is a seat under water (tub_seat: rule 6's depth, width and clear top,
on the solid body, its top at TUB_SEAT_Y, which the seated figure's 1.1 of shins needs over the tub's floor, not
1.5..2.0), and no two visitors' figures overlap (figures_check: every pair of Sit spots' seated figures apart).

    blender -b -t 4 --python-exit-code 1 -P tools/build_activity_spa.py [-- grey] [-- nopreview]

`-- grey` writes the grey silhouettes (three options a piece, ids _A/_B/_C, not for import) to
blender/rooms/haunted_manor_spa/silhouettes/. Otherwise the chosen two are built in the Manor's palette; review/
gets Workbench sheets only (Studio is running; no EEVEE or Cycles).
"""
import ast
import json
import math
from pathlib import Path

_AB = Path(__file__).resolve().parent / 'build_activity_bar.py'
_tree = ast.parse(_AB.read_text(encoding='utf8'))
_tree.body = [n for n in _tree.body if not isinstance(n, ast.Try)]          # its main() call
NS = {'__file__': str(_AB), '__name__': 'build_activity_bar'}
exec(compile(_tree, str(_AB), 'exec'), NS)
globals().update({k: v for k, v in NS.items() if not k.startswith('__')})

SET = 'rooms/haunted_manor_spa'
GREY = 'grey' in K.ARGS

# The rows these need. main's Pieces.luau has HotTub 2 x 2 height 2.5 and MassageTable 1 x 2 height 2.8; the
# hot tub must be 3 x 3 to seat four (README, "Why 3 x 3"): its row is overridden here, and validation.json
# `pieces_rows` says what main has and what the row must say.
PROPOSED = {
    'HotTub': {'w': 3, 'd': 3, 'layer': 'Floor', 'height': 3.7, 'location': 0, 'keyFor': ['Spa']},
}

FLOOR_T = 0.06                  # the tub's floor slab
SEAT_TOP = 1.2                  # the underwater bench: the seated figure's feet hang 1.1 under it, over the slab
WATER_TOP = 2.3                 # the water 1.1 over the bench (the torso half under), 0.9 under the shoulders
RIM_TOP = 2.45                  # the coping's top (Pieces' 2.5)
COPE_Y0 = 2.29                  # its underside; the wall under it reaches COPE_Y0 + 0.04 (buried in it)
WALL_T = 0.35                   # the tub's wall, outer face to inner
COPE_IN, COPE_OUT = 0.06, 0.05  # the coping's overhang into the tub and over the wall's outer face
STEP_TOP = 1.2                  # a corner's upper tread: half the rim
TREAD_TOP = 0.6                 # and its lower
TUB_SEAT_Y = (1.1, 1.4)         # a bench under water: over the shins' 1.1 and the slab, the water still over the waist
PAD_TOP = 2.3                   # the massage table's pad, where the guest lies (a table's 2.6..3 less a little: the
                                # masseur's hip; a bed's 2)
SEG = 16                        # the tub's round: segments (staves; the budget)


def sfurn(id_, w=None, d=None):
    """Begin Furniture_<id_> on its row (main's Pieces.luau, or PROPOSED; a silhouette's own w x d); its spots
    replace `Use` (use_check off, spots_check on)."""
    base = id_.split('_')[0]
    row = dict(PROPOSED.get(base) or ROWS[base])
    if w:
        row['w'], row['d'] = w, d
    ROWS[id_] = row
    K.pieces_decor()
    K._PIECES[id_] = {k: row[k] for k in ('w', 'd', 'layer', 'height')} | {'always': False}
    p = furn(id_)
    p.checks.remove(use_check)
    p.checks.append(spots_check)
    p.spots = {}
    return p


def ngon(r, n=SEG, phase=None):
    """A regular n-gon of radius r in (x, z), counter-clockwise from +X (phase: the first vertex's angle)."""
    ph = math.pi / n if phase is None else phase
    return [(r * math.cos(ph + 2 * math.pi * k / n), r * math.sin(ph + 2 * math.pi * k / n)) for k in range(n)]


def rect(hx, z0, z1, x0=None):
    x0 = -hx if x0 is None else x0
    return [(hx, z0), (hx, z1), (x0, z1), (x0, z0)]


# --- Seats in water and the visitors' figures (these pieces' checks) ----------------------------------

def tub_seat(x0, x1, z0, z1, y, look):
    """A seat on a tub's bench, under the water: rule 6's checks (K._seat_check's: 1.2 deep along `look`, 2.0
    wide across it, its top at y over its middle, nothing over it for 3) on the solid body, the water left out,
    its top at TUB_SEAT_Y."""
    K.P.seats.append({'x': [round(x0, 4), round(x1, 4)], 'z': [round(z0, 4), round(z1, 4)], 'y': round(y, 4),
                      'people': 1, 'narrow': None, 'tub': True, 'look': list(look)})
    if _tub_seat_check not in K.P.checks:
        K.P.checks.append(_tub_seat_check)


def _tub_seat_check(piece, tris, stage):
    faults = []
    solid = [t for p, ts in tris.items() if p not in ('Root', 'LOD_Proxy', 'Water') for t in ts]
    for i, s in enumerate(piece.seats):
        (x0, x1), (z0, z1), y = s['x'], s['z'], s['y']
        tag = f'tub seat {i + 1} ({stage})'
        along_x = abs(s['look'][0]) > 0.5
        deep, wide = (x1 - x0, z1 - z0) if along_x else (z1 - z0, x1 - x0)
        if not TUB_SEAT_Y[0] <= y <= TUB_SEAT_Y[1]:
            faults.append(f'{tag}: its top at {y:.2f}, not {TUB_SEAT_Y[0]}..{TUB_SEAT_Y[1]}')
        if deep < K.SEAT_DEPTH - 1e-6:
            faults.append(f'{tag}: {deep:.2f} deep, under {K.SEAT_DEPTH}')
        if wide < K.SEAT_W - 1e-6:
            faults.append(f'{tag}: {wide:.2f} wide, under {K.SEAT_W}')
        w, d = x1 - x0, z1 - z0
        for fx in (0.25, 0.5, 0.75):
            for fz in (0.25, 0.5, 0.75):
                x, z = x0 + w * fx, z0 + d * fz
                top = max(K._ray_down(solid, x, z, y + K.SEAT_CLEAR), default=None)
                if top is None or abs(top - y) > 0.08:
                    faults.append(f'{tag}: at ({x:.2f}, {z:.2f}) the top is '
                                  f'{"nothing" if top is None else f"{top:.2f}"}, not the seat at {y:.2f}')
        n = 6
        for ix in range(n + 1):
            for iz in range(n + 1):
                x, z = x0 + 0.1 + (w - 0.2) * ix / n, z0 + 0.1 + (d - 0.2) * iz / n
                over = [h for h in K._ray_down(solid, x, z, y + K.SEAT_CLEAR) if h > y + 0.08]
                if over:
                    faults.append(f'{tag}: something over the seat at ({x:.2f}, {max(over):.2f}, {z:.2f})')
                    break
            else:
                continue
            break
    return faults


def _boxes_meet(a_lo, a_hi, b_lo, b_hi, gap):
    return all(a_lo[i] + gap < b_hi[i] - gap and b_lo[i] + gap < a_hi[i] - gap for i in range(3))


def figures_check(piece, tris, stage):
    """No two visitors' seated figures (sit_blocks) overlap: a tub's sitters' feet, thighs and arms apart."""
    sits = [a for a, p in piece.spots.items() if p == 'Sit']
    blocks = {a: sit_blocks(*piece.att[a]) for a in sits}
    f = []
    for i, a in enumerate(sits):
        for b in sits[i + 1:]:
            for lo, hi, _, na in blocks[a]:
                hit = next((nb for lo2, hi2, _, nb in blocks[b] if _boxes_meet(lo, hi, lo2, hi2, SIT_GAP)), None)
                if hit:
                    f.append(f'{a} and {b} ({stage}): the seated figures meet ({na} and {hit})')
                    break
    return f


def sit_spot(n, pos, look):
    """A Sit spot on a tub's bench, facing `look`, and its seat: from the bench's front edge under the feet
    (0.47 ahead of the spot, where the shins hang clear) back 1.2, 2.0 across."""
    spot(n, pos, look, 'Sit')
    a = Vector(look)
    p = Vector(pos)
    front = p + a * 0.47
    back = front - a * K.SEAT_DEPTH
    b = Vector((-a.z, 0, a.x))
    c = [front + b * 1.0, front - b * 1.0, back + b * 1.0, back - b * 1.0]
    tub_seat(min(v.x for v in c), max(v.x for v in c), min(v.z for v in c), max(v.z for v in c), pos[1], look)
    if figures_check not in K.P.checks:
        K.P.checks.append(figures_check)


# --- The tubs: three options ----------------------------------------------------------------------

def round_tub(c, R, staves=None, hoops=(), floor=None):
    """A round tub of outer radius R (to the coping's edge): its floor slab (`floor`: its outline, where a bench
    does not cover it), wall ring, coping, `Water`. Returns (RI, EI): the wall's inner radius and the coping's
    inner edge."""
    RO = R - COPE_OUT
    RI = RO - WALL_T
    EI = RI - COPE_IN
    prism('Body', floor or ngon(RI + 0.02), 0.0, FLOOR_T, c['floor'], plane='xz')
    ring_prism('Body', ngon(RO), ngon(RI), 0.0, COPE_Y0 + 0.04, staves or c['wall'], c['lining'], c['wall'])
    for y0, y1 in hoops:            # gold hoops 0.03 proud of the staves
        ring_prism('Body', ngon(RO + 0.03), ngon(RO - 0.02), y0, y1, c['hoop'], c['hoop'], c['hoop'])
    ring_prism('Body', ngon(R), ngon(EI), COPE_Y0, RIM_TOP, c['cope'], c['cope'], c['cope'])
    declare('Water', False)
    prism('Water', ngon(RI + 0.02), 0.04, WATER_TOP, c['water'], plane='xz')
    return RI, EI


def square_tub(c, HX, HZ, chamfer=0.4):
    """A square tub, the body's outer half sizes HX x HZ, its corners cut: floor, wall ring, coping, `Water`.
    Returns (IX, IZ): the wall's inner half sizes."""
    OX, OZ = HX - COPE_OUT, HZ - COPE_OUT
    IX, IZ = OX - WALL_T, OZ - WALL_T
    EX, EZ = IX - COPE_IN, IZ - COPE_IN
    o = lambda hx, hz, ch: outline(hx, hz, ch)      # noqa: E731
    prism('Body', o(IX + 0.02, IZ + 0.02, inset(chamfer, WALL_T - 0.02)), 0.0, FLOOR_T, c['floor'], plane='xz')
    ring_prism('Body', o(OX, OZ, inset(chamfer, COPE_OUT)), o(IX, IZ, inset(chamfer, COPE_OUT + WALL_T)), 0.0,
               COPE_Y0 + 0.04, c['wall'], c['lining'], c['wall'])
    ring_prism('Body', o(HX, HZ, chamfer), o(EX, EZ, inset(chamfer, COPE_OUT + WALL_T + COPE_IN)), COPE_Y0, RIM_TOP,
               c['cope'], c['cope'], c['cope'])
    declare('Water', False)
    prism('Water', o(IX + 0.02, IZ + 0.02, inset(chamfer, WALL_T - 0.02)), 0.04, WATER_TOP, c['water'],
          plane='xz')
    return IX, IZ


SQ2 = 2 - math.sqrt(2)


def outline(hx, hz, c=0.0):
    """A rectangle +-hx, +-hz in (x, z), its corners cut by c (an octagon), counter-clockwise from +X."""
    if c <= 0:
        return [(hx, hz), (-hx, hz), (-hx, -hz), (hx, -hz)]
    return [(hx, hz - c), (hx - c, hz), (-hx + c, hz), (-hx, hz - c), (-hx, -hz + c), (-hx + c, -hz),
            (hx - c, -hz), (hx, -hz + c)]


def inset(c, t):
    return 0.0 if c <= 0 else max(c - SQ2 * t, 0.02)


def octagon_bench(c, b, diag, r_out):
    """The bench round a round tub's inside: from the wall (r_out, buried in it) in to a footwell that is an
    octagon (its sides b from the middle on the axes, |x| + |z| < diag across the corners), where the seated
    figures' shins and feet hang; the ring's outer points at the same angles as the octagon's (two a side)."""
    verts = []
    for sx, sz in ((1, 1), (-1, 1), (-1, -1), (1, -1)):
        # one quadrant, counter-clockwise: the axis side's half, the corner's cut, the next axis side's half
        q = [(b, 0.0), (b, diag - b), (diag - b, b), (0.0, b)]
        if sx * sz < 0:
            q = [(z, x) for x, z in q]
        pts = [(sx * x, sz * z) for x, z in q]
        for i in range(3):          # each edge in two
            (x0, z0), (x1, z1) = pts[i], pts[i + 1]
            verts += [(x0, z0), ((x0 + x1) / 2, (z0 + z1) / 2)]
    inner = verts
    outer = [(r_out * math.cos(math.atan2(z, x)), r_out * math.sin(math.atan2(z, x))) for x, z in inner]
    ring_prism('Body', outer, inner, 0.0, SEAT_TOP, c['bench_side'], c['bench_side'], c['bench'])


def corner_fill(c, sx, sz, R, top, col_top, col_side, a0=18.0, a1=72.0):
    """A block filling the footprint's corner (sx, sz) round the tub (its arc at R, against the wall), top at `top`."""
    H = 4.1
    arc_pts = [(R * math.cos(math.radians(a)), R * math.sin(math.radians(a)))
               for a in (a1 - (a1 - a0) * i / 4 for i in range(5))]
    pts = [(H, arc_pts[-1][1]), (H, H), (arc_pts[0][0], H)] + arc_pts
    pts = [(sx * x, sz * z) for x, z in pts]
    if sx * sz < 0:
        pts.reverse()
    prism('Body', pts, 0.0, top, {'top': col_top, 'rest': col_side}, plane='xz')


def tub_a(c, dress=False):
    """A: 2 x 2 (Pieces' size): a square tub with cut corners, the bench along its back wall: one visitor (a
    second's arms, 3.8 across, meet the walls or the first's)."""
    IX, IZ = square_tub(c, 2.6, 2.6)
    zf = 1.47 - 0.5 + 0.03
    span('Body', (-IX - 0.02, FLOOR_T - 0.02, zf), (IX + 0.02, SEAT_TOP, IZ + 0.02), c['bench'])
    sit_spot(1, (0.0, SEAT_TOP, 1.47), (0, 0, -1))


def tub_b(c, dress=False):
    """B: 3 x 2, a long square tub, a U of bench along the back and the ends: three visitors (one at the back,
    one at each end), the front wall free."""
    IX, IZ = square_tub(c, 4.1, 2.6)
    xs, zb = 2.97, 1.47
    prism('Body', [(IX + 0.02, -IZ - 0.02), (IX + 0.02, IZ + 0.02), (-IX - 0.02, IZ + 0.02), (-IX - 0.02, -IZ - 0.02),
                   (-xs + 0.47, -IZ - 0.02), (-xs + 0.47, zb - 0.47), (xs - 0.47, zb - 0.47), (xs - 0.47, -IZ - 0.02)],
          FLOOR_T - 0.02, SEAT_TOP, {'top': c['bench'], 'rest': c['bench_side']}, plane='xz')
    sit_spot(1, (0.0, SEAT_TOP, zb), (0, 0, -1))
    sit_spot(2, (xs, SEAT_TOP, 0.0), (-1, 0, 0))
    sit_spot(3, (-xs, SEAT_TOP, 0.0), (1, 0, 0))


TUB_R = 4.1                     # the round tub's coping, to the footprint's inset
SIT_R = 2.55                    # its visitors' spots from the middle: the arms 3.8 across inside the coping's edge
BENCH_B = 2.06                  # the footwell's sides: the feet (0.5 ahead of a spot) clear of the bench's front
BENCH_DIAG = 3.0                # and its cut corners: a feet's outer corner (0.95, 2.05) inside the footwell


def tub_c(c, dress=False):
    """C: 3 x 3, a round tub (a barrel of staves under hoops when dressed), the bench all round an octagonal
    footwell: four visitors facing its middle, one on each side; a step in each corner at half the rim, the back
    two carrying a brazier of steam stones and a candelabra (blind review 1: rim-height back decks and half-height
    front steps read as four unrelated blocks, and the props were specks from the game's camera)."""
    hoops = ((1.26, 1.5), (2.03, 2.29)) if dress else ()       # the lower on the steps' line (blind review 1)
    staves = [c['wall'], c.get('wall2', c['wall'])] * (SEG // 2)
    well = outline(BENCH_B + 0.1, BENCH_B + 0.1, 2 * BENCH_B - BENCH_DIAG + 0.1)     # the footwell's floor, under the bench's edge
    RI, EI = round_tub(c, TUB_R, staves=staves, hoops=hoops, floor=well)
    octagon_bench(c, BENCH_B, BENCH_DIAG, RI + 0.04)
    for sx in (-1, 1):
        for sz in (-1, 1):
            # Two treads (blind review 2: one half-rim block in each corner read as a crate): the lower filling
            # the corner, the upper a block on the diagonal against the staves.
            corner_fill(c, sx, sz, RI + WALL_T - 0.07, TREAD_TOP, c['step'], c['step_side'])
            d, q = Vector((sx, 0, sz)) * (0.5 ** 0.5), Vector((-sz, 0, sx)) * (0.5 ** 0.5)
            pts = [(v.x, v.z) for v in (d * 3.9 + q * 0.55, d * 5.1 + q * 0.55, d * 5.1 - q * 0.55, d * 3.9 - q * 0.55)]
            prism('Body', ccw(pts), 0.0, STEP_TOP, {'top': c['step'], 'rest': c['step_side']}, plane='xz')
    k = 4.7 * (0.5 ** 0.5)          # the props on the back upper treads, clear of the coping (r 4.1)
    if dress:
        steam_stones(c, -k, k)
        candelabra(c, k, k)
    else:
        cyl('Body', (-k, STEP_TOP, k), 0.42, 1.4, c['hoop'], n=10)
        cyl('Body', (k, STEP_TOP, k), 0.12, 2.0, c['hoop'], n=6)
    for k, (x, z, look) in enumerate(((0.0, SIT_R, (0, 0, -1)), (SIT_R, 0.0, (-1, 0, 0)),
                                       (0.0, -SIT_R, (0, 0, 1)), (-SIT_R, 0.0, (1, 0, 0)))):
        sit_spot(k + 1, (x, SEAT_TOP, z), look)


def steam_stones(c, x, z):
    """A brazier on an iron stand on the corner's upper tread, its gold bowl over the rim, glowing embers
    (Glow_Warm_2) under a heap of dark steam stones. Steam itself is left to the code (blind reviews 1 and 2:
    puffs of spheres read as pebbles, lofted wisps as crystal or crumpled paper)."""
    y = STEP_TOP
    cyl('Body', (x, y, z), 0.36, 0.1, c['brazier'], n=8)
    cyl('Body', (x, y + 0.1, z), 0.08, 1.02, c['brazier'], n=6)
    y = STEP_TOP + 1.1
    lathe('Body', [(0.0, 0.0), (0.3, 0.0), (0.48, 0.2), (0.55, 0.36), (0.0, 0.36)], c['hoop'], n=8,
          base=(x, y, z))
    declare('Glow_Warm_2', False)
    cyl('Glow_Warm_2', (x, y + 0.34, z), 0.46, 0.04, 'flame', n=8)
    for dx, dz, r, col in ((0.0, 0.0, 0.22, 'stones'), (0.24, 0.12, 0.17, 'stones2'), (-0.2, 0.16, 0.16, 'stones'),
                           (0.06, -0.24, 0.17, 'stones2')):
        sphere('Body', (x + dx, y + 0.38, z + dz), (r, r * 0.7, r), c[col], n=6, rings=3)


def candelabra(c, x, z):
    """A gold three-branch candelabra on the corner step, its candles over the rim (Glow_Warm_1)."""
    y = STEP_TOP
    cyl('Body', (x, y, z), 0.36, 0.12, c['hoop'], n=8)
    cyl('Body', (x, y + 0.12, z), 0.11, 1.58, c['hoop'], n=6, r_top=0.08)       # (blind review 2: a wisp)
    top = y + 1.7
    candle6('Glow_Warm_1', x, top, z, 0.45, c['hoop'])
    for s in (-1, 1):
        ex, ez = x - s * 0.4, z + s * 0.4
        seg('Body', (x, top - 0.3, z), (ex, top - 0.05, ez), 0.07, c['hoop'], n=4)
        candle6('Glow_Warm_1', ex, top - 0.1, ez, 0.35, c['hoop'])


def candle6(part, x, y, z, h, cup):
    """A candle in a cup on (x, y, z), its flame `part` (Glow_Warm_<n>): six-sided (the tub's budget)."""
    cyl('Body', (x, y, z), 0.17, 0.1, cup, n=6)
    cyl('Body', (x, y + 0.1, z), 0.1, h, 'cream', n=6)
    sphere(part, (x, y + 0.1 + h + 0.12, z), (0.06, 0.14, 0.06), 'flame', n=5, rings=3)


# --- The massage tables: three options ----------------------------------------------------------------

PAD_Z0, PAD_Z1 = -2.55, 1.55    # the pad, foot (-Z) to head (+Z); the face cradle beyond it
SHEET = 0.03                    # the cream sheet over the pad's middle (blind review 3: the guest's dark legs vanished
                                # into the plum pad); the Lie point on it
CRADLE_Z, CRADLE_R = 2.05, 0.45     # the cradle's ring: middle and radius (its tube 0.1)
LIE_Z = 0.0                     # the Lie point: the feet at -2.5, the head's top at 2.5 on the cradle


def ccw(pts):
    a = sum(x0 * z1 - x1 * z0 for (x0, z0), (x1, z1) in zip(pts, pts[1:] + pts[:1]))
    return pts if a > 0 else list(reversed(pts))


def pad(c, hw=1.05):
    """The pad and the face cradle at the head end (the bolster under the ankles went: blind review 2, the
    guest lies flat through it)."""
    span('Body', (-hw, PAD_TOP - 0.34, PAD_Z0), (hw, PAD_TOP, PAD_Z1), c['pad'], bevel=0.08)
    # The face cradle: a padded horseshoe open at the head end, 0.1 under the pad's top, on a dark-wood stem
    # from under the pad (blind review 1: a flat oval ring with a dark hole, level with the pad, on a gold stalk
    # read as a toilet seat).
    ro, ri, zc, zend = 0.55, 0.24, CRADLE_Z, 2.58
    arc_o = [(ro * math.cos(math.radians(a)), zc + ro * math.sin(math.radians(a))) for a in range(0, -181, -30)]
    arc_i = [(ri * math.cos(math.radians(a)), zc + ri * math.sin(math.radians(a))) for a in range(-180, 1, 30)]
    u = [(ro, zend)] + arc_o + [(-ro, zend), (-ri, zend)] + arc_i + [(ri, zend)]
    prism('Body', ccw(u), PAD_TOP - 0.36, PAD_TOP - 0.1, c['pad'], plane='xz')
    span('Body', (-0.4, PAD_TOP - 0.48, PAD_Z1 - 0.6), (0.4, PAD_TOP - 0.36, zend - 0.1), c['bracket'])
    spot(1, (0.0, PAD_TOP + SHEET, LIE_Z), (0, 0, -1), 'Lie')


def table_a(c, dress=False):
    """A: four turned legs, an apron under the pad, a shelf between the legs with towels and oils."""
    for x in (-0.82, 0.82):
        for z in (-2.2, 1.2):
            lathe('Body', [(0.13, 0.0), (0.16, 0.12), (0.1, 0.3), (0.12, 0.9), (0.09, 1.5), (0.13, PAD_TOP - 0.6),
                           (0.13, PAD_TOP - 0.34)], c['leg'], n=8, base=(x, 0, z))
    span('Body', (-0.95, PAD_TOP - 0.6, -2.35), (0.95, PAD_TOP - 0.33, 1.35), c['apron'])
    if dress:
        span('Body', (-0.97, PAD_TOP - 0.42, -2.37), (0.97, PAD_TOP - 0.36, 1.37), c['trim'])
    span('Body', (-0.82, 0.48, -2.2), (0.82, 0.58, 1.2), c['shelf'])
    if dress:
        for z in (-1.7, -1.15):
            cyl('Body', (0, 0, 0), 0.24, 1.3, c['towel'], n=8, m=at((-0.65, 0.82, z), rz=-90))
        # (Two candles here went: blind review 1, a flame under the table by the linen, unseen from the camera.)
        bottle(0.35, 0.58, 0.3, 0.6, 0.13, c['oil'])
        bottle(-0.1, 0.58, 0.6, 0.5, 0.12, c['oil2'])
        span('Body', (-1.08, PAD_TOP - 0.24, -2.1), (1.08, PAD_TOP + SHEET, 1.2), c['towel'], bevel=0.02)
    pad(c)


def table_b(c, dress=False):
    """B: two gothic trestle ends, a pointed arch through each, a stretcher between them."""
    for z in (-1.9, 0.9):
        pts = [(-0.95, 0.0), (-0.55, 0.0)] + [(x, y) for x, y in K.arch_points(-0.55, 0.55, 0.9, 1.45, n=3)] + \
              [(0.55, 0.0), (0.95, 0.0), (0.95, PAD_TOP - 0.33), (-0.95, PAD_TOP - 0.33)]
        prism('Body', pts, z - 0.22, z + 0.22, c['leg'], plane='xy')
    span('Body', (-0.15, 1.5, -1.7), (0.15, 1.75, 0.7), c['leg'])
    pad(c)


def table_c(c, dress=False):
    """C: a cabinet base under the pad: a plinth, panels with pointed arches on its long sides."""
    span('Body', (-0.95, 0.0, -2.35), (0.95, 0.2, 1.35), c['leg'])
    span('Body', (-0.88, 0.2, -2.28), (0.88, PAD_TOP - 0.33, 1.28), c['apron'])
    for sx in (-1, 1):
        x0, x1 = sorted((sx * 0.88, sx * 0.91))
        for zc in (-1.4, 0.4):
            prism('Body', lifted(gothic(zc - 0.6, zc + 0.6, 0.6, 1.1), 0.35), x0, x1, c['shelf'], plane='zy')
    pad(c)


GC = {'floor': 'stone_dark', 'wall': 'grey', 'wall2': 'grey', 'lining': 'stone_dark', 'cope': 'stone',
      'water': 'moon_dark', 'hoop': 'stone_dark', 'bench': 'stone', 'bench_side': 'stone_dark', 'step': 'stone',
      'step_side': 'grey', 'brazier': 'stone_dark', 'stones': 'stone_dark', 'stones2': 'grey', 'steam': 'white',
      'pad': 'stone', 'cradle': 'stone_dark', 'bracket': 'stone_dark', 'bolster': 'grey', 'leg': 'stone_dark',
      'apron': 'grey', 'trim': 'stone', 'shelf': 'grey', 'towel': 'white', 'oil': 'stone', 'oil2': 'grey'}

TUBS = {'A': (tub_a, 2, 2), 'B': (tub_b, 3, 2), 'C': (tub_c, 3, 3)}
TABLES = {'A': table_a, 'B': table_b, 'C': table_c}
NOTES = {'HotTub_A': 'A: 2 x 2, a square tub with cut corners, a bench along the back: one visitor',
         'HotTub_B': 'B: 3 x 2, a long square tub, a U of bench: three visitors',
         'HotTub_C': 'C: 3 x 3, a round tub, a bench all round: four visitors; corner steps, a deck at the back',
         'MassageTable_A': 'A: four turned legs, an apron, a shelf below; a face cradle, a bolster',
         'MassageTable_B': 'B: two gothic trestle ends with pointed arches, a stretcher; a face cradle, a bolster',
         'MassageTable_C': 'C: a cabinet base with pointed-arch panels; a face cradle, a bolster'}


def sil_tub(k):
    fn, w, d = TUBS[k]
    sfurn(f'HotTub_{k}', w, d)
    fn(GC)
    sdone(NOTES[f'HotTub_{k}'])


def sil_table(k):
    sfurn(f'MassageTable_{k}')
    TABLES[k](GC)
    sdone(NOTES[f'MassageTable_{k}'])


# --- The chosen two, in the Manor's dress -------------------------------------------------------------

HM = {'floor': 'teal_dark', 'wall': 'violet', 'wall2': 'plum', 'lining': 'teal_dark', 'cope': 'bone',
      'water': 'teal', 'hoop': 'gold', 'bench': 'stone', 'bench_side': 'stone_dark', 'step': 'bone',
      'step_side': 'plum', 'brazier': 'iron', 'stones': 'stone_dark', 'stones2': 'black', 'steam': 'white',
      'pad': 'plum', 'cradle': 'plum_dark', 'bracket': 'wood_dark', 'bolster': 'cream', 'leg': 'wood_dark',
      'apron': 'wood_dark', 'trim': 'gold', 'shelf': 'wood', 'towel': 'cream', 'oil': 'amber', 'oil2': 'wine'}


def hot_tub():
    sfurn('HotTub')
    tub_c(HM, dress=True)
    sdone('a Haunted Manor hot tub: a round barrel of violet and plum staves under two gold hoops, a pale stone '
          'coping at 2.45, teal water over a stone bench round the inside; two pale stone treads in each corner; on '
          'the back corners a gold brazier of dark steam stones over glowing embers on an iron stand, and a gold '
          'three-branch candelabra')


def massage_table():
    sfurn('MassageTable')
    table_a(HM, dress=True)
    sdone('a Haunted Manor massage table: a plum leather pad at 2.3 under a cream sheet, on four turned dark-wood '
          'legs and an apron with a gold band, a plum horseshoe face cradle on a dark-wood stem at the head end; on '
          'a shelf below, rolled cream towels and two oil bottles')


# --- Review (Workbench on light grey: Studio is running, no EEVEE or Cycles) --------------------------

def people(rec, cx, cz=0.0):
    for a, pose in rec['furniture']['spots'].items():
        u = rec['attachments'][a]
        p = (cx + u['pos'][0], u['pos'][1], cz + u['pos'][2])
        if pose == 'Lie':
            _lying(p, u['look'])
        elif pose == 'Sit':
            _sitting(p, u['look'])
        else:
            _REV['_person'](Vector((p[0], p[1], 0)), p[2])


def splace(fbx, name, pos, ang=0.0):
    objs = place(fbx, name, pos, ang)
    for ob in objs:
        if ob.name.split('.')[0] == 'Water':
            _see_through(ob, 0.45)          # the code makes it water: drawn see-through, as Glass is
    return objs


def squares_at(cx, cz, size):
    for a in range(int(round(size[0] / 3))):
        for b in range(int(round(size[2] / 3))):
            x0, z0 = cx - size[0] / 2 + 3 * a, cz - size[2] / 2 + 3 * b
            shade = (205, 205, 210) if (a + b) % 2 else (185, 185, 192)
            _REV['_block']('sq', (x0 + 0.03, -0.06, z0 + 0.03), (x0 + 2.97, -0.01, z0 + 2.97), shade)


ROWS_SIL = (('HotTub_A', 'HotTub_B', 'HotTub_C'), ('MassageTable_A', 'MassageTable_B', 'MassageTable_C'))


def lay(fbx, recs, row, z0, labels, gap=5.0, spots=True):
    x = 0.0
    for i in row:
        n = f'Furniture_{i}'
        size = recs[n]['root']['size']
        cx = x + max(size[0], 3.8) / 2
        splace(fbx, n, (cx, 0, z0))
        squares_at(cx, z0, size)
        if spots:
            people(recs[n], cx, z0)
        if labels:
            _label(i.split('_')[1], cx, z0 - size[2] / 2 - 1.6)
        x += max(size[0], 3.8) + gap
    _REV['_person'](Vector((x - gap + 2.2, 0, 0)), z0)
    return x


def silhouette_sheet(out, fbx, recs):
    shots = []
    clear()
    x = max(lay(fbx, recs, ROWS_SIL[0], 9.0, True), lay(fbx, recs, ROWS_SIL[1], 0.0, True))
    _REV['_block']('floor', (-3, -0.3, -6), (x + 2, -0.07, 15), (150, 150, 156))
    shots.append(render(out / 'silhouettes_game.png', (-0.35, 1.25, -1.0), (1600, 1000), (-2, 0, -5), (x, 5.0, 14),
                        scale=1.0))
    for k, row in enumerate(ROWS_SIL):
        clear()
        x = lay(fbx, recs, row, 0.0, False)
        shots.append(render(out / f'silhouettes_side_{k + 1}.png', (-0.7, 0.3, -0.7), (1600, 600), (-2, -0.3, -5),
                            (x, 5.4, 5), scale=1.02))
    clear()
    x = lay(fbx, recs, ROWS_SIL[0], 0.0, False)
    shots.append(render(out / 'silhouettes_top_tubs.png', (0.0, 1.0, -0.02), (1600, 600), (-2, 0, -5), (x, 5.4, 5),
                        scale=1.02))
    return shots


NAMES = ['Furniture_HotTub', 'Furniture_MassageTable']


def review_final(out, fbx, recs):
    shots = []

    def scene(spots=True):
        clear()
        x = 0.0
        for n in NAMES:
            size = recs[n]['root']['size']
            cx = x + max(size[0], 3.8) / 2
            splace(fbx, n, (cx, 0, 0))
            _squares(cx, size)
            if spots:
                people(recs[n], cx)
            x += max(size[0], 3.8) + 3.0
        _REV['_person'](Vector((x + 0.5, 0, 0)), 0.0)
        _REV['_block']('floor', (-3, -0.3, -6), (x + 4, -0.07, 6), (150, 150, 156))
        return x
    x = scene()
    lo, hi = (-1.5, 0, -4.8), (x + 2.5, 5.2, 4.8)
    shots.append(render(out / '1_game_camera.png', (-0.45, 1.28, -1.0), (1400, 800), lo, hi, scale=1.02))
    shots.append(render(out / '2_front_three_quarter.png', (-0.7, 0.45, -1.0), (1400, 800), lo, hi, scale=1.02))
    shots.append(render(out / '3_back_three_quarter.png', (0.7, 0.55, 1.0), (1400, 800), lo, hi, scale=1.02))
    x = scene(spots=False)
    shots.append(render(out / '4_front_level.png', (0.0, 0.0, -1.0), (1400, 600), (-1.5, -0.3, -4.8),
                        (x + 2.5, 5.4, 4.8), scale=1.02))
    shots.append(render(out / '5_top.png', (0.0, 1.0, -0.02), (1400, 800), (-1.5, 0, -4.8), (x + 2.5, 5.4, 4.8),
                        scale=1.02))
    clear()
    x = 0.0
    for n in NAMES:
        size = recs[n]['root']['size']
        cx = x + size[2] / 2
        splace(fbx, n, (cx, 0, 0), 90)
        _squares(cx, size, 90)
        x += size[2] + 3.0
    _REV['_person'](Vector((x + 1.0, 0, 0)), 0.0)
    shots.append(render(out / '6_side_level.png', (0.0, 0.0, -1.0), (1400, 600), (-1.5, -0.3, -5), (x + 3, 5.4, 5),
                        scale=1.02))
    # The tub in use, from the game's camera and cut through its middle (the bench and the sitters under water).
    clear()
    splace(fbx, NAMES[0], (0, 0, 0))
    _REV['_block']('floor', (-6, -0.3, -6), (6, -0.07, 6), (150, 150, 156))
    shots.append(render(out / '9_close_steam_candles.png', (-0.55, 0.5, -1.0), (1200, 700), (-4.3, 0.0, 2.4),
                        (4.3, 4.0, 4.3), scale=1.0))
    people(recs[NAMES[0]], 0.0)
    shots.append(render(out / '7_tub_in_use.png', (-0.45, 1.28, -1.0), (1200, 900), (-4.6, 0, -4.6), (4.6, 4.4, 4.6),
                        scale=1.0))
    shots.append(render(out / '8_tub_section.png', (0.0, 0.08, -1.0), (1200, 700), (-4.6, -0.2, -4.6),
                        (4.6, 4.6, 4.6), scale=1.0, cut=(0, 0, -0.2)))
    clear()
    splace(fbx, NAMES[1], (0, 0, 0))
    people(recs[NAMES[1]], 0.0)
    _REV['_block']('floor', (-3, -0.3, -4), (3, -0.07, 4), (150, 150, 156))
    shots.append(render(out / '10_close_table.png', (-0.75, 0.45, -0.75), (1000, 800), (-2.0, 0, -3.2),
                        (2.0, 3.6, 3.2), scale=1.0))
    shots.append(render(out / '11_table_side.png', (-1.0, 0.1, 0.0), (1000, 600), (-1.5, -0.2, -3.2), (1.5, 3.6, 3.2),
                        scale=1.0))
    clear()
    splace(fbx, NAMES[1], (0, 0, 0))
    _REV['_block']('floor', (-3, -0.3, -4), (3, -0.07, 4), (150, 150, 156))
    shots.append(render(out / '12_table_empty.png', (-0.6, 0.6, 0.8), (1000, 800), (-2.0, 0, -3.2), (2.0, 3.0, 3.2),
                        scale=1.0))
    return shots


# --- The set ------------------------------------------------------------------------------------------

def main():
    K.use_palette(HM_PALETTE)
    if GREY:
        K.IMPORT_CHECKS = False         # drafts with _A/_B/_C ids, not for import
        K.start_set(SET + '/silhouettes')
        for k in TUBS:
            sil_tub(k)
        for k in TABLES:
            sil_table(k)
        recs = {p.name: r for p, r, _ in K.BUILT}
        out = K.ROOT / 'blender' / SET / 'silhouettes'
        (out / 'manifest.json').write_text(json.dumps({'pieces': recs, 'soak_findings': SOAK_FINDINGS}, indent=1))
        bad = [p.name for p, r, _ in K.BUILT if r.get('faults')]
        print('SILHOUETTE FAULTS', bad, flush=True)
        if not K.NOPREVIEW:
            print('SHEETS', silhouette_sheet(out / 'review', out / 'fbx', recs), flush=True)
        return
    K.start_set(SET)
    hot_tub()
    massage_table()
    built = [p.name for p, _, _ in K.BUILT]
    K.end_set('Haunted Manor: the Spa\'s hot tub and massage table (GDD A.13)', [(built, 3.0, 1.0)], sheet=False)
    out = K.ROOT / 'blender' / SET
    manifest = json.loads((out / 'manifest.json').read_text())
    patch_fixup(out / 'import_fixup.luau', manifest)
    val = json.loads((out / 'validation.json').read_text())
    val['spots'] = {n: {'spots': r['furniture']['spots'],
                        'checked': ('spots_check on the built and the re-imported triangles: Use_<n> from 1 without '
                                    'a gap, a Pose from MODELS.md\'s list, a level LookVector, no two spots on one '
                                    'square; Sit under Water (soak_faults): the Water not colliding, the spot on a '
                                    'declared tub seat with the solid body under it to 0.15 and nothing over it, '
                                    f'the water over the seated torso {SOAK_MIN}..{SOAK_MAX} over the seat (the '
                                    'head above it), the seated 5-stud person (sit_blocks, arms included) clear of '
                                    'the body; tub_seat: 1.2 deep, 2.0 wide, its top '
                                    f'{TUB_SEAT_Y[0]}..{TUB_SEAT_Y[1]}, nothing over it for 3 (the water left out); '
                                    'figures_check: no two seated figures overlap; Lie: inside the footprint, on '
                                    'its surface with nothing over it, and the lying 5-stud person (lie_faults: in '
                                    'the footprint, on the piece, nothing rising through it, arms included)')}
                    for n, r in manifest['pieces'].items()}
    val['soak_findings'] = {'note': 'each tub spot: the seat, the water\'s top, the seated person\'s shoulders '
                                    '(seat + 2) and head top (seat + 3)', **SOAK_FINDINGS}
    main_rows = {'HotTub': {'w': 2, 'd': 2, 'layer': 'Floor', 'height': 2.5},
                 'MassageTable': {'w': 1, 'd': 2, 'layer': 'Floor', 'height': 2.8}}
    val['pieces_rows'] = {n: {'main': main_rows[n[len('Furniture_'):]],
                              'needs': {k: ROWS[n[len('Furniture_'):]][k] for k in ('w', 'd', 'layer', 'height',
                                                                                     'keyFor')},
                              'model_top': manifest['pieces'][n]['furniture']['model_top']} for n in built}
    val['height_findings'] = {
        'note': 'Pieces.luau\'s height against the model\'s top, a finding (not refused): the row must say it',
        **{n: FINDINGS[n] for n in built if n in FINDINGS}}
    val['not_validated'] = val.get('not_validated', [])[:1] + [
        'the attachments and each Use_<n> Pose attribute exist only in manifest.json until import_fixup.luau makes '
        'them', 'a visitor walking to a spot, getting into the tub, sitting in the water or lying face down: no '
        'walker or clip has run', 'the Water made water and the candles lit: the code does it',
        'HotTub 3 x 3: main\'s Pieces.luau row says 2 x 2 (pieces_rows); the kit\'s Pieces check ran against the '
        'proposed row']
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
