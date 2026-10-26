"""The Sauna's three pieces for Frostfang Lodge's kit (GDD A.13.2, the Sauna row: Frostfang, location 2).

    Furniture_SaunaBench    2 x 1 squares, `Floor`: a two-tier slatted bench, the upper tier the seat at 1.8 for two,
                            the lower tier at 0.7 under their feet; a slatted backrest to 3.0; Use_1, Use_2 `Sit` on
                            the upper tier, one a square, the feet on the lower tier
    Furniture_SteamStone    1 x 1 squares, `Floor`: a sauna stove, an iron box on short legs, a cage of stones on
                            top, a fire door glowing with embers (Glow_Warm_1); no visitors' spots
    Furniture_WaterBucket   1 x 1 squares, `Floor`: a wooden bucket of staves in iron hoops, icy water, a ladle;
                            no visitors' spots

The contract is MODELS.md, "Furniture" and "Activity furniture: visitors' spots", as for the Manor's activity sets
(tools/build_activity_bar.py, whose definitions this runs: spot, spots_check, sdone, patch_fixup, _label, and
through it tools/build_built_rooms.py's kit and the Lodge's palette and dress). Nothing is added to the shared
validator. Here, for these pieces only:

    tier_seat   a seat with its own height range: a lower tier is rule 6's seat (1.5..2.0); an upper tier whose
                sitters' feet rest on the tier under it is held as a bar stool's seat (2.4..2.8), its feet on the
                tier as a stool's on its ring (option B only; the chosen bench's seat is rule 6's)
    feet_check  a sitter whose feet rest on a lower tier: under both soles (1.1 under the seat, sit_blocks) the
                body is at most FEET_DROP under them (they stand on it, sit_faults keeps it out of them)
    figures_check  sitters on different tiers (one behind and above another): their seated figures apart (the
                upper one's feet behind the lower one's back). Side-by-side sitters one square apart are not held
                to it: their arms (3.8 across) overlap 0.8, as on the Cinema's row of three.

    blender -b -t 4 --python-exit-code 1 -P tools/build_activity_sauna.py [-- grey] [-- nopreview]

`-- grey` writes the grey silhouettes (three options a piece, ids _A/_B/_C, not for import) to
blender/rooms/frostfang_lodge_sauna/silhouettes/. Otherwise the chosen three are built in the Lodge's palette;
review/ gets Workbench sheets only (no EEVEE or Cycles). Its own set, blender/rooms/frostfang_lodge_sauna/; the
models belong in HotelKit.FrostfangLodge.
"""
import ast
import json
import math
from pathlib import Path
from types import SimpleNamespace

_AB = Path(__file__).resolve().parent / 'build_activity_bar.py'
_tree = ast.parse(_AB.read_text(encoding='utf8'))
_tree.body = [n for n in _tree.body if not isinstance(n, ast.Try)]          # its main() call
NS = {'__file__': str(_AB), '__name__': 'build_activity_bar'}
exec(compile(_tree, str(_AB), 'exec'), NS)
globals().update({k: v for k, v in NS.items() if not k.startswith('__')})

SET = 'rooms/frostfang_lodge_sauna'
GREY = 'grey' in K.ARGS

# Option B (grey only) needs a larger row: 2 x 2, two seated tiers and a foot step, four sitters.
PROPOSED_SIL = {'SaunaBench_B': {'w': 2, 'd': 2}}

SEAT_TOP = 1.8                  # the bench's seat (the upper tier): rule 6's 1.5..2.0; ActivityKit's blockout's 1.8
STEP_TOP = SEAT_TOP - 1.1       # the lower tier under the sitters' soles (sit_blocks: 1.1 under the seat)
USE_Z = 0.4                     # the sitters' spots: the seat 0.6 either side, the backrest behind the torso, the
                                # lower tier under the feet, all inside the 1-square depth (z -1.1..1.1)
SPOT_X = 1.5                    # one a square
BACK_TOP = 3.0                  # the backrest's cap (Pieces' 3.0)
FEET_DROP = 0.12                # the soles stand on a lower tier: the body at most this under them
TIER_Y = (2.4, 2.8)             # an upper tier whose sitters' feet rest on the tier under it (B)


# --- The pieces' frames, seats and these checks --------------------------------------------------------

def sfurn(id_, spots=True):
    """Begin Furniture_<id_> on its Pieces.luau row (a silhouette's own w x d from PROPOSED_SIL); its spots replace
    `Use` (use_check off; spots_check on when it has spots)."""
    base = id_.split('_')[0]
    row = dict(ROWS[base]) | PROPOSED_SIL.get(id_, {})
    ROWS[id_] = row
    K.pieces_decor()
    K._PIECES[id_] = {k: row[k] for k in ('w', 'd', 'layer', 'height')} | {'always': False}
    p = furn(id_)
    p.checks.remove(use_check)
    if spots:
        p.checks.append(spots_check)
    p.spots = {}
    p.feet_on = []
    return p


def sdone2(note):
    rec = sdone(note)
    rec['furniture']['pieces_row'] = 'Pieces.luau'
    return rec


def tier_seat(x0, x1, z0, z1, y, people=1, rng=None):
    """A seat (rule 6's checks, K._seat_check's) with its own height range: K.SEAT_Y, or `rng`."""
    K.P.seats.append({'x': [round(x0, 4), round(x1, 4)], 'z': [round(z0, 4), round(z1, 4)], 'y': round(y, 4),
                      'people': people, 'narrow': None, 'range': list(rng or K.SEAT_Y)})
    if _tier_seat_check not in K.P.checks:
        K.P.checks.append(_tier_seat_check)


def _tier_seat_check(piece, tris, stage):
    f = []
    saved = K.SEAT_Y
    try:
        for i, s in enumerate(piece.seats):
            K.SEAT_Y = tuple(s['range'])
            f += [x.replace('seat 1 (', f'seat {i + 1} (') for x in K._seat_check(SimpleNamespace(seats=[s]), tris,
                                                                                 stage)]
    finally:
        K.SEAT_Y = saved
    return f


def sit(n, x, y, z, rng=None, feet=True, people_seat=True):
    """A Sit spot facing -Z at (x, y, z) and its seat (1.2 deep from 0.6 ahead of it, 2.0 across)."""
    spot(n, (x, y, z), (0, 0, -1), 'Sit')
    if people_seat:
        tier_seat(x - 1.0, x + 1.0, z - 0.6, z + 0.6, y, rng=rng)
    if feet:
        K.P.feet_on.append(f'Use_{n}')
        if feet_check not in K.P.checks:
            K.P.checks.append(feet_check)


def feet_check(piece, tris, stage):
    """The feet of a sitter on an upper tier rest on the tier under it: under each sole's middle and its ends
    (sit_blocks' feet: 0.5..1.5 ahead of the spot, 0.05..0.95 either side, their soles 1.1 under the seat) the body
    is at most FEET_DROP under the sole."""
    f = []
    allt = [t for p, ts in tris.items() if p not in ('Root', 'LOD_Proxy') for t in ts]
    for a in piece.feet_on:
        pos, look = piece.att[a]
        sole = pos.y - 1.1
        fa = Vector((look.x, 0, look.z)).normalized()
        fb = Vector((-fa.z, 0, fa.x))
        for t in (0.65, 1.0, 1.35):
            for s in (-0.8, -0.5, -0.2, 0.2, 0.5, 0.8):
                q = pos + fa * t + fb * s
                top = max(K._ray_down(allt, q.x, q.z, sole + 0.05), default=None)
                if top is None or sole - top > FEET_DROP:
                    f.append(f'{a} ({stage}): under the sole at ({q.x:.2f}, {q.z:.2f}) the body is at '
                             f'{"nothing" if top is None else f"{top:.2f}"}, the sole at {sole:.2f}: the feet hang')
                    break
            else:
                continue
            break
    return f


def _boxes_meet(a_lo, a_hi, b_lo, b_hi, gap):
    return all(a_lo[i] + gap < b_hi[i] - gap and b_lo[i] + gap < a_hi[i] - gap for i in range(3))


def figures_check(piece, tris, stage):
    """Sitters on different tiers (their spots apart in z) do not meet: the seated figures (sit_blocks)."""
    sits = [a for a, p in piece.spots.items() if p == 'Sit']
    blocks = {a: sit_blocks(*piece.att[a]) for a in sits}
    f = []
    for i, a in enumerate(sits):
        for b in sits[i + 1:]:
            if abs(piece.att[a][0].z - piece.att[b][0].z) < 0.5:
                continue
            for lo, hi, _, na in blocks[a]:
                hit = next((nb for lo2, hi2, _, nb in blocks[b] if _boxes_meet(lo, hi, lo2, hi2, SIT_GAP)), None)
                if hit:
                    f.append(f'{a} and {b} ({stage}): the seated figures meet ({na} and {hit})')
                    break
    return f


def ccw_zy(pts):
    a = sum(x0 * z1 - x1 * z0 for (x0, z0), (x1, z1) in zip(pts, pts[1:] + pts[:1]))
    return pts if a > 0 else list(reversed(pts))


# --- The benches: three options ----------------------------------------------------------------------

def slats(c, x0, x1, z0, z1, top, n, t=0.12, gap=0.1):
    """n slats along X over z0..z1, their tops at `top`, gaps `gap` between them, a dark board 0.05 under their
    tops filling the gaps (so the seat's rays and the gaps' shadow both hold: within the seat check's 0.08)."""
    w = (z1 - z0 - gap * (n - 1)) / n
    for k in range(n):
        za = z0 + k * (w + gap)
        span('Body', (x0, top - t, za), (x1, top, za + w), c['slat'])     # flat, square-edged (blind reviews 1, 2)
    span('Body', (x0 + 0.16, top - 0.14, z0 + 0.03), (x1 - 0.16, top - 0.05, z1 - 0.03), c['gap'])


def end_panels(c, outline, x_in=2.40, x_out=2.54, flake_at=None):
    """The two end boards, an outline in (z, y), from x_in to x_out either side."""
    pts = ccw_zy(outline)
    for sx in (-1, 1):
        a, b = sorted((sx * x_in, sx * x_out))
        prism('Body', pts, a, b, c['end'], plane='zy')
        if flake_at and c.get('flake'):
            z, y, r = flake_at
            flake('Body', (sx * (x_out - 0.01), y, z), r, c['flake'], wall='side', stagger=True)


def backrest(c, z0, z1, y_slats, cap, x=2.42):
    for y0, y1 in y_slats:
        span('Body', (-x, y0, z0), (x, y1, z1), c['slat'])      # boards, not rails (blind review 2)
    span('Body', (-x - 0.14, cap[0], z0 - 0.02), (x + 0.14, cap[1], z1 + 0.04), c['cap'], bevel=0.03)   # (not the posts' 0.92)


def bench_a(c, dress=False):
    """A: 2 x 1 (the row's size), boxed: the upper tier the seat at 1.8 for two, the lower tier at 0.7 under their
    feet, boarded risers, stepped end boards that rise at the back into the backrest's posts, three backrest slats
    under a cap at 3.0."""
    zf, zs, zb = -1.08, USE_Z - 0.6, 1.08          # the step's front, the seat's front, the back
    slats(c, -2.56, 2.56, zs, USE_Z + 0.6, SEAT_TOP, 4)
    slats(c, -2.56, 2.56, zf, zs + 0.06, STEP_TOP, 3)
    span('Body', (-2.42, STEP_TOP - 0.08, zs + 0.16), (2.42, SEAT_TOP - 0.1, zs + 0.26), c['riser'])     # upper riser,
    # behind the soles (the feet reach 0.1 back under the seat's front)
    span('Body', (-2.42, 0.0, zf + 0.04), (2.42, STEP_TOP - 0.1, zf + 0.14), c['riser'])                # step riser
    span('Body', (-2.42, 0.0, 0.94), (2.42, SEAT_TOP - 0.1, 1.04), c['riser'])                          # back board
    end_panels(c, [(zf + 0.02, 0.0), (zb, 0.0), (zb, BACK_TOP - 0.02), (0.92, BACK_TOP - 0.02),
                   (0.92, SEAT_TOP - 0.06), (zs + 0.1, SEAT_TOP - 0.06), (zs + 0.1, STEP_TOP - 0.06),
                   (zf + 0.02, STEP_TOP - 0.06)], flake_at=(0.35, 0.95, 0.42))
    backrest(c, 0.95, 1.06, ((2.08, 2.3), (2.46, 2.68)), (2.82, BACK_TOP))
    # (A rolled towel on the cap went: blind review 1, on the thinnest edge it read as a floating cylinder.)
    for k, sx in enumerate((-1, 1), 1):
        sit(k, sx * SPOT_X, SEAT_TOP, USE_Z, people_seat=False)
    tier_seat(-2.4, 2.4, zs - 0.05, USE_Z + 0.55, SEAT_TOP, people=2)     # its back 0.05 clear of the backrest's


def bench_b(c, dress=False):
    """B: 2 x 2, three tiers: a foot step at 0.4, the lower seat at 1.5 for two, the upper seat at 2.6 for two
    behind it (their feet on the lower tier, as a bar stool's on its ring), a backrest to 3.8: four sitters."""
    zl, zu = -0.3, 1.8
    slats(c, -2.56, 2.56, -2.2, zl - 0.6 + 0.06, 0.4, 3)                    # the foot step
    slats(c, -2.56, 2.56, zl - 0.6, zu - 0.6 + 0.06, 1.5, 6)                # the lower tier
    slats(c, -2.56, 2.56, zu - 0.6, zu + 0.6, 2.6, 4)                       # the upper tier
    span('Body', (-2.42, 0.0, -2.16), (2.42, 0.3, -2.06), c['riser'])
    span('Body', (-2.42, 0.3, zl - 0.44), (2.42, 1.4, zl - 0.34), c['riser'])
    span('Body', (-2.42, 1.4, zu - 0.44), (2.42, 2.5, zu - 0.34), c['riser'])
    end_panels(c, [(-2.18, 0.0), (2.58, 0.0), (2.58, 3.78), (2.42, 3.78), (2.42, 2.54), (zu - 0.48, 2.54),
                   (zu - 0.48, 1.44), (zl - 0.48, 1.44), (zl - 0.48, 0.34), (-2.18, 0.34)])
    backrest(c, 2.44, 2.55, ((2.9, 3.12), (3.26, 3.48)), (3.6, 3.8))
    sit(1, -SPOT_X, 2.6, zu, rng=TIER_Y)
    sit(2, SPOT_X, 2.6, zu, rng=TIER_Y)
    sit(3, -SPOT_X, 1.5, zl)
    sit(4, SPOT_X, 1.5, zl)
    K.P.checks.append(figures_check)


def bench_c(c, dress=False):
    """C: 2 x 1, open: the tiers' slats on a frame of round log legs and rails (no boarded risers), a tall backrest
    of vertical slats between two log posts."""
    zf, zs = -1.08, USE_Z - 0.6
    slats(c, -2.56, 2.56, zs, USE_Z + 0.6, SEAT_TOP, 4)
    slats(c, -2.56, 2.56, zf, zs + 0.06, STEP_TOP, 3)
    for sx in (-1, 1):
        x = sx * 2.34
        cyl('Body', (x, 0, zf + 0.14), 0.1, STEP_TOP - 0.12, c['end'], n=8)       # the step's front legs
        cyl('Body', (x, 0, zs + 0.26), 0.1, SEAT_TOP - 0.12, c['end'], n=8)       # the seat's legs, behind the soles
        cyl('Body', (x, 0, 0.98), 0.1, 3.4, c['end'], n=8)                      # the back posts
        seg('Body', (x, STEP_TOP - 0.2, zf + 0.04), (x, STEP_TOP - 0.2, 1.0), 0.08, c['end'])
        seg('Body', (x, SEAT_TOP - 0.2, zs + 0.02), (x, SEAT_TOP - 0.2, 1.0), 0.08, c['end'])
    for z, y in ((zf + 0.14, STEP_TOP - 0.2), (zs + 0.26, SEAT_TOP - 0.2), (0.98, 0.9)):
        seg('Body', (-2.34, y, z), (2.34, y, z), 0.08, c['end'])
    for k in range(9):
        x = -2.0 + 0.5 * k
        span('Body', (x - 0.17, 2.0, 0.94), (x + 0.17, 3.3, 1.05), c['slat'], bevel=0.02)
    span('Body', (-2.3, 1.9, 0.9), (2.3, 2.02, 1.06), c['end'])
    span('Body', (-2.3, 3.24, 0.9), (2.3, 3.36, 1.06), c['end'])
    for k, sx in enumerate((-1, 1), 1):
        sit(k, sx * SPOT_X, SEAT_TOP, USE_Z, people_seat=False)
    tier_seat(-2.4, 2.4, zs - 0.05, USE_Z + 0.55, SEAT_TOP, people=2)


# --- The stoves: three options ------------------------------------------------------------------------

STONES = ((0.0, 0.0, 0.3), (0.42, 0.25, 0.24), (-0.4, 0.22, 0.25), (0.38, -0.3, 0.23), (-0.42, -0.28, 0.24),
          (0.05, 0.42, 0.22), (0.02, -0.42, 0.22), (-0.15, 0.1, 0.2), (0.2, -0.05, 0.2))


def stone_heap(c, cx, y, cz, scale=1.0, stones=STONES):
    for k, (dx, dz, r) in enumerate(stones):
        r *= scale
        lift = 0.18 if k >= 7 else 0.0
        col = (c['stone'], c['stone2'], c['stone3'])[k % 3]
        sphere('Body', (cx + dx * scale, y + r * 0.7 + lift * scale, cz + dz * scale), (r, r * 0.75, r * 0.95), col,
               n=6, rings=3)


def fire_door(c, x0, x1, y0, y1, z, glow=True):
    """A fire door on a face at z (facing -Z): an iron plate, a window of embers (Glow_Warm_1), two bars, a knob."""
    span('Body', (x0, y0, z - 0.06), (x1, y1, z + 0.02), c['door'], bevel=0.02)
    gx0, gx1, gy0, gy1 = x0 + 0.12, x1 - 0.12, y0 + 0.12, y1 - 0.2
    if glow:
        declare('Glow_Warm_1', False)
        span('Glow_Warm_1', (gx0, gy0, z - 0.075), (gx1, gy1, z - 0.03), c['ember'])
    for k in (1, 2):
        x = gx0 + (gx1 - gx0) * k / 3
        span('Body', (x - 0.025, gy0 - 0.02, z - 0.1), (x + 0.025, gy1 + 0.02, z - 0.05), c['bar'])
    sphere('Body', (x1 - 0.08, (y0 + y1) / 2 + 0.05, z - 0.1), 0.06, c['knob'], n=6, rings=3)


HEAP = ([(0.0, 0.0, 0.34, 0.0)]
        + [(0.56 * math.cos(math.radians(a)), 0.5 * math.sin(math.radians(a)), 0.3, 0.0) for a in range(0, 360, 45)]
        + [(0.3 * math.cos(math.radians(a)), 0.28 * math.sin(math.radians(a)), 0.28, 0.28) for a in (30, 120, 210, 300)]
        + [(0.0, 0.02, 0.24, 0.42)])


def heap(c, y):
    """The stones heaped as a dome over the cage's rail (blind review 1: one flat layer under the rail read as
    charcoal in a grill): a ring of eight round a middle one, four on them, one on top; each a little different in
    size, squash, turn and tilt (blind review 2: alike six-sided ones read as hex nuts or a honeycomb)."""
    for k, (dx, dz, r, lift) in enumerate(HEAP):
        col = (c['stone'], c['stone2'], c['stone3'])[k % 3]
        j = [((k * 7919 + i * 104729) % 1000) / 1000.0 for i in range(5)]     # fixed jitter, the same every build
        rx, ry, rz = r * (0.9 + 0.25 * j[0]), r * (0.6 + 0.2 * j[1]), r * (0.85 + 0.2 * j[2])
        sphere('Body', (0, 0, 0), (rx, ry, rz), col, n=7, rings=4,
               m=at((dx, y + ry * 0.9 + lift, dz), rx=-12 + 24 * j[3], ry=360 * j[4]))


def fire_window(c, x0, x1, y0, y1, z):
    """A fire door on a face at z (facing -Z): an iron plate with a brass-rimmed round-topped window, the fire
    behind it (Glow_Warm_1) with two dark logs lying across its foot, a brass knob (blind review 1: three barred
    slots read as a vent)."""
    span('Body', (x0, y0, z - 0.06), (x1, y1, z + 0.02), c['door'], bevel=0.02)
    cx, hw, ys, yt = (x0 + x1) / 2, (x1 - x0) / 2 - 0.12, y0 + 0.12, y1 - 0.12
    spring = yt - hw

    def arch_win(h):
        return [(cx - h, ys - (h - hw)), (cx + h, ys - (h - hw))] + [
            (cx + h * math.cos(math.pi * i / 8), spring + h * math.sin(math.pi * i / 8)) for i in range(9)]
    rim = arch_win(hw + 0.06)
    win = arch_win(hw)
    # The rim in the door's iron, not brass (blind review 2: a brass rim round the fire's own warm colour read as
    # one ring round a dark hole); the logs a low stack at the window's foot, level (crossed, they read as a slash).
    prism('Body', rim, z - 0.08, z - 0.05, c['rim'], plane='xy')
    declare('Glow_Warm_1', False)
    prism('Glow_Warm_1', win, z - 0.095, z - 0.07, c['ember'], plane='xy')
    for dx, dy, dz, ln in ((-0.03, 0.06, 0.0, 2 * hw - 0.12), (0.03, 0.06, -0.06, 2 * hw - 0.2),
                           (0.0, 0.14, -0.03, 2 * hw - 0.28)):
        cyl('Body', (0, 0, 0), 0.05, ln, c['char'], n=6,
            m=at((cx - ln / 2 + dx, ys + dy, z - 0.14 + dz), rz=-90))
    sphere('Body', (x1 - 0.07, (y0 + y1) / 2, z - 0.1), 0.06, c['knob'], n=6, rings=3)


def stove_a(c, dress=False):
    """A: an iron box on four short legs, a fire door whose round-topped window shows the fire, a low cage of iron
    rods on its top with the stones heaped over it (blind review 1: wider for its square, the stones a dome over the
    rail, one window for the barred slots, no snowflake on the one hot thing in the room)."""
    for x in (-0.74, 0.74):
        for z in (-0.56, 0.56):
            cyl('Body', (x, 0, z), 0.09, 0.27, c['iron'], n=6)
    span('Body', (-0.92, 0.25, -0.72), (0.92, 1.3, 0.72), c['iron'], bevel=0.05)
    span('Body', (-0.98, 1.28, -0.8), (0.98, 1.37, 0.8), c['iron2'], bevel=0.03)
    for x in (-0.93, 0.93):
        for z in (-0.75, 0.75):
            cyl('Body', (x, 1.37, z), 0.06, 0.24, c['iron'], n=6)
    # The rods thicker (blind review 2: hair-thin at a phone's size).
    for z in (-0.75, 0.75):
        seg('Body', (-0.93, 1.57, z), (0.93, 1.57, z), 0.055, c['iron'], n=4)
    for x in (-0.93, 0.93):
        seg('Body', (x, 1.61, -0.75), (x, 1.61, 0.75), 0.055, c['iron'], n=4)     # over the others (coplanar tops)
    heap(c, 1.37)
    fire_window(c, -0.5, 0.5, 0.4, 1.16, -0.72)


def stove_b(c, dress=False):
    """B: a hearth of stones, no iron: a ring of large stones on the floor, a heap of smaller ones on it, the embers
    glowing low in the ring's mouth at the front."""
    n = 9
    for k in range(n):
        a = 2 * math.pi * (k + 0.5) / n
        if abs(math.degrees(a) - 270) < 25:        # the mouth at the front (-Z)
            continue
        r = 0.32 if k % 2 else 0.28
        sphere('Body', (0.75 * math.cos(a), r * 0.8, 0.75 * math.sin(a)), (r, r * 0.8, r), c['stone2'], n=6, rings=3)
    cyl('Body', (0, 0, 0), 0.62, 0.45, c['stone3'], n=9)
    declare('Glow_Warm_1', False)
    span('Glow_Warm_1', (-0.24, 0.02, -0.78), (0.24, 0.3, -0.5), c['ember'])
    stone_heap(c, 0.0, 0.45, 0.0, scale=1.25)


def stove_c(c, dress=False):
    """C: a round iron drum stove, a stone basket on its top, a fire door with embers, a birch guard rail round it
    on four log posts."""
    lathe('Body', [(0.5, 0.15), (0.55, 0.22), (0.55, 1.25), (0.6, 1.3), (0.6, 1.38), (0.0, 1.38)], c['iron'], n=12)
    for a in (45, 135, 225, 315):
        cyl('Body', (0.42 * math.cos(math.radians(a)), 0, 0.42 * math.sin(math.radians(a))), 0.06, 0.2, c['iron'], n=6)
    ring_prism('Body', ngon(0.62, 12), ngon(0.54, 12), 1.38, 1.62, c['iron2'], c['iron2'], c['iron2'])
    stone_heap(c, 0.0, 1.38, 0.0, scale=0.95)
    fire_door(c, -0.3, 0.3, 0.4, 1.0, -0.5)
    for x in (-1.0, 1.0):
        for z in (-1.0, 1.0):
            cyl('Body', (x, 0, z), 0.08, 1.25, c['guard_post'], n=8)
    for y in (0.7, 1.15):
        for z in (-1.0, 1.0):
            span('Body', (-1.02, y - 0.08, z - 0.05), (1.02, y + 0.08, z + 0.05), c['guard'], bevel=0.02)
        for x in (-1.0, 1.0):
            span('Body', (x - 0.05, y - 0.08, -0.92), (x + 0.05, y + 0.08, 0.92), c['guard'], bevel=0.02)


def ngon(r, n, phase=None):
    ph = math.pi / n if phase is None else phase
    return [(r * math.cos(ph + 2 * math.pi * k / n), r * math.sin(ph + 2 * math.pi * k / n)) for k in range(n)]


# --- The buckets: three options -----------------------------------------------------------------------

def bucket(c, y0, h, r_out=0.58, r_in=0.5, water=0.75, n=12, ice=False):
    """A bucket of staves standing on y0 (alternate staves a shade apart), two iron hoops, its floor, the water at
    `water` of its height (ice floating on it when dressed). Returns the water's top."""
    staves = [c['stave'], c['stave2']] * (n // 2)
    ring_prism('Body', ngon(r_out, n), ngon(r_in, n), y0, y0 + h, staves, c['stave2'], c['stave'])
    for f in (0.16, 0.74):
        ya = y0 + h * f
        ring_prism('Body', ngon(r_out + 0.03, n), ngon(r_out - 0.02, n), ya, ya + 0.1, c['hoop'], c['hoop'], c['hoop'])
    prism('Body', ngon(r_in + 0.02, n), y0, y0 + 0.1, c['stave2'], plane='xz')
    wt = y0 + h * water
    prism('Body', ngon(r_in + 0.01, n), y0 + 0.1, wt, c['water'], plane='xz')
    if ice:
        for dx, dz, r in ((0.18, 0.12, 0.13), (-0.2, -0.05, 0.11), (0.05, -0.25, 0.09)):
            span('Body', (dx - r, wt - 0.04, dz - r * 0.8), (dx + r, wt + 0.06, dz + r * 0.8), c['ice'], bevel=0.03)
    return wt


def ladle(c, bowl, tip, r=0.17):
    """A ladle: its bowl (a half sphere, open up) at `bowl`, its handle up to `tip`."""
    x, y, z = bowl
    lathe('Body', [(0.0, -r), (r * 0.7, -r * 0.75), (r, 0.0), (r * 0.85, 0.0), (0.0, -r * 0.6)], c['ladle'], n=8,
          base=(x, y, z), closed=True)
    seg('Body', (x + (tip[0] - x) * 0.08, y + 0.02, z + (tip[2] - z) * 0.08), tip, 0.065, c['handle'])  # (review 2)


def bucket_a(c, dress=False):
    """A: a bucket of staves in two iron hoops with an iron bail handle, a ladle standing in it, its handle out over
    the rim."""
    wt = bucket(c, 0.0, 1.0, ice=dress)
    for sz in (-1, 1):
        span('Body', (-0.06, 0.8, sz * 0.58 - 0.04), (0.06, 0.98, sz * 0.58 + 0.04), c['hoop'])
    pts = [(0.0, 0.92 + 0.48 * math.sin(math.pi * i / 8), -0.6 * math.cos(math.pi * i / 8)) for i in range(9)]
    for a, b in zip(pts, pts[1:]):
        seg('Body', a, b, 0.05, c['hoop'], n=6)          # (blind review 2: hair-thin at 0.03)
    ladle(c, (0.2, wt + 0.12, 0.05), (0.98, 1.42, -0.55))


def bucket_b(c, dress=False):
    """B: a Nordic sauna bucket (kiulu): one stave runs up at its back into a handle with a hand hole, the ladle
    lying across the rim."""
    wt = bucket(c, 0.0, 0.95, r_out=0.6, r_in=0.52, ice=dress)
    prism('Body', [(-0.16, 0.6), (0.16, 0.6), (0.16, 1.48), (-0.16, 1.48)], 0.5, 0.64, c['stave'], plane='xy')
    span('Body', (-0.08, 1.2, 0.48), (0.08, 1.36, 0.66), c['gap'])
    cyl('Body', (0, 0, 0), 0.05, 1.5, c['handle'], n=6, m=at((-0.75, 0.99, -0.15), rz=-90))
    lathe('Body', [(0.0, -0.15), (0.13, -0.11), (0.17, 0.0), (0.14, 0.0), (0.0, -0.09)], c['ladle'], n=8,
          base=(0.85, 1.0, -0.15), closed=True)


def bucket_c(c, dress=False):
    """C: a smaller bucket standing on a log-slice stool, its ladle hung on its rim by the handle's hook."""
    cyl('Body', (0, 0, 0), 0.8, 0.42, c['stool'], n=12)
    cyl('Body', (0, 0.42, 0), 0.82, 0.06, c['stool_top'], n=12)
    wt = bucket(c, 0.48, 0.78, r_out=0.5, r_in=0.43, ice=dress)
    seg('Body', (0.46, 1.24, 0.0), (0.7, 1.32, 0.0), 0.04, c['handle'])
    seg('Body', (0.7, 1.32, 0.0), (0.7, 0.66, 0.0), 0.045, c['handle'])
    lathe('Body', [(0.0, -0.15), (0.13, -0.11), (0.17, 0.0), (0.14, 0.0), (0.0, -0.09)], c['ladle'], n=8,
          base=(0.7, 0.66, 0.0), closed=True)


# --- Grey silhouettes ----------------------------------------------------------------------------------

GC = {'slat': 'stone_light', 'gap': 'stone_dark', 'riser': 'grey', 'end': 'stone_dark', 'cap': 'stone',
      'towel': 'stone_light', 'towel_band': 'grey', 'flake': None, 'iron': 'stone_dark', 'iron2': 'grey',
      'stone': 'stone', 'stone2': 'grey', 'stone3': 'stone_dark', 'door': 'grey', 'bar': 'stone_dark',
      'knob': 'stone_light', 'ember': 'flame', 'char': 'black', 'rim': 'stone', 'guard': 'stone_light', 'guard_post': 'stone_dark',
      'stave': 'stone_light', 'stave2': 'stone', 'hoop': 'stone_dark', 'water': 'grey', 'ice': 'stone_light',
      'ladle': 'stone', 'handle': 'stone_light', 'stool': 'stone_dark', 'stool_top': 'stone'}

BENCHES = {'A': bench_a, 'B': bench_b, 'C': bench_c}
STOVES = {'A': stove_a, 'B': stove_b, 'C': stove_c}
BUCKETS = {'A': bucket_a, 'B': bucket_b, 'C': bucket_c}
KINDS = {'SaunaBench': BENCHES, 'SteamStone': STOVES, 'WaterBucket': BUCKETS}
NOTES = {'SaunaBench_A': 'A: 2 x 1, boxed: the seat tier at 1.8 for two, the foot tier at 0.7, a slatted backrest',
         'SaunaBench_B': 'B: 2 x 2: a foot step at 0.4, the lower seat at 1.5, the upper at 2.6 behind: four sitters',
         'SaunaBench_C': 'C: 2 x 1, open: the same tiers on a log frame, a tall backrest of vertical slats',
         'SteamStone_A': 'A: an iron box stove on legs, a fire door with embers, a cage of stones on top',
         'SteamStone_B': 'B: a hearth: a ring of large stones, a heap on it, the embers in its mouth',
         'SteamStone_C': 'C: a round iron drum stove, a stone basket, a fire door, a wooden guard rail round it',
         'WaterBucket_A': 'A: a bucket of staves in two hoops, an iron bail, a ladle standing in it',
         'WaterBucket_B': 'B: a Nordic sauna bucket, one stave up into a handle, the ladle across the rim',
         'WaterBucket_C': 'C: a smaller bucket on a log-slice stool, the ladle hung on its rim'}


def sil(kind, k):
    sfurn(f'{kind}_{k}', spots=(kind == 'SaunaBench'))
    KINDS[kind][k](GC)
    sdone2(NOTES[f'{kind}_{k}'])


# --- The chosen three, in the Lodge's dress -------------------------------------------------------------

FF = {'slat': 'birch', 'gap': 'log_dark', 'riser': 'birch_shade', 'end': 'wood_light', 'cap': 'wood_light',
      'towel': 'ice', 'towel_band': 'snow', 'flake': 'ice', 'char': 'black', 'rim': 'stone_dark', 'iron': 'iron', 'iron2': 'stone_dark', 'stone': 'stone',
      'stone2': 'stone_light', 'stone3': 'stone_dark', 'door': 'black', 'bar': 'iron', 'knob': 'gold',
      'ember': 'lamp', 'guard': 'birch', 'guard_post': 'log', 'stave': 'birch', 'stave2': 'birch_shade',
      'hoop': 'iron', 'water': 'ice_deep', 'ice': 'ice', 'ladle': 'log', 'handle': 'birch', 'stool': 'log',
      'stool_top': 'birch'}
FF_STOVE = dict(FF, flake=None)     # no snowflake on the one hot thing in the room (blind review 1)

CHOSEN = {'SaunaBench': 'A', 'SteamStone': 'A', 'WaterBucket': 'A'}
NAMES = ['Furniture_SaunaBench', 'Furniture_SteamStone', 'Furniture_WaterBucket']


def sauna_bench():
    sfurn('SaunaBench')
    BENCHES[CHOSEN['SaunaBench']](FF, dress=True)
    sdone2('a Frostfang Lodge sauna bench for two: flat pale birch slats with air gaps on two tiers (the seat at 1.8, '
           'the foot tier at 0.7), birch-board risers, light pine end boards that step down with the tiers and rise '
           'at the back into the backrest\'s posts, an ice-blue snowflake carved on each; two birch backrest slats '
           'under a pine cap at 3.0')


def steam_stone():
    sfurn('SteamStone', spots=False)
    STOVES[CHOSEN['SteamStone']](FF_STOVE, dress=True)
    sdone2('a Frostfang Lodge sauna stove: an iron box on four short legs, a black fire door with an iron-rimmed '
           'round-topped window onto the fire (a low stack of dark logs at its foot) and a gold knob; on its top a low '
           'cage of iron rods with grey stones heaped in a dome over it')


def water_bucket():
    sfurn('WaterBucket', spots=False)
    BUCKETS[CHOSEN['WaterBucket']](FF, dress=True)
    sdone2('a Frostfang Lodge sauna bucket: birch staves in two iron hoops, an iron bail handle, ice-blue water with '
           'three chunks of ice floating, a log ladle standing in it, its birch handle out over the rim')


# --- Review (Workbench on light grey: no EEVEE or Cycles) ------------------------------------------------

def people(rec, cx, cz=0.0):
    for a, pose in rec['furniture']['spots'].items():
        u = rec['attachments'][a]
        _sitting((cx + u['pos'][0], u['pos'][1], cz + u['pos'][2]), u['look'])


def squares_at(cx, cz, size):
    for a in range(int(round(size[0] / 3))):
        for b in range(int(round(size[2] / 3))):
            x0, z0 = cx - size[0] / 2 + 3 * a, cz - size[2] / 2 + 3 * b
            shade = (205, 205, 210) if (a + b) % 2 else (185, 185, 192)
            _REV['_block']('sq', (x0 + 0.03, -0.06, z0 + 0.03), (x0 + 2.97, -0.01, z0 + 2.97), shade)


ROWS_SIL = tuple(tuple(f'{kind}_{k}' for k in 'ABC') for kind in KINDS)


def lay(fbx, recs, row, z0, labels, gap=4.5, users=True):
    x = 0.0
    for i in row:
        n = f'Furniture_{i}'
        size = recs[n]['root']['size']
        cx = x + max(size[0], 3.8) / 2
        place(fbx, n, (cx, 0, z0))
        squares_at(cx, z0, size)
        if users and recs[n]['furniture']['spots']:
            people(recs[n], cx, z0)
        if labels:
            _label(i.split('_')[1], cx, z0 - size[2] / 2 - 1.6)
        x += max(size[0], 3.8) + gap
    _REV['_person'](Vector((x - gap + 2.2, 0, 0)), z0)
    return x


def silhouette_sheet(out, fbx, recs):
    shots = []
    clear()
    x = max(lay(fbx, recs, ROWS_SIL[0], 13.0, True), lay(fbx, recs, ROWS_SIL[1], 5.5, True),
            lay(fbx, recs, ROWS_SIL[2], 0.0, True))
    _REV['_block']('floor', (-3, -0.3, -4), (x + 2, -0.07, 17), (150, 150, 156))
    shots.append(render(out / 'silhouettes_game.png', (-0.35, 1.25, -1.0), (1600, 1000), (-2, 0, -3), (x, 5.0, 16),
                        scale=1.0))
    clear()
    x = lay(fbx, recs, ROWS_SIL[0], 0.0, False)
    shots.append(render(out / 'silhouettes_side_benches.png', (-1.0, 0.15, -0.35), (1600, 600), (-2, -0.3, -3),
                        (x, 5.8, 3), scale=1.02))
    clear()
    x = max(lay(fbx, recs, ROWS_SIL[1], 4.0, False, gap=3.0), lay(fbx, recs, ROWS_SIL[2], 0.0, False, gap=3.0))
    shots.append(render(out / 'silhouettes_front_stoves_buckets.png', (-0.4, 0.35, -1.0), (1600, 700),
                        (-2, -0.3, -2), (x, 5.2, 6), scale=1.02))
    return shots


def sauna(fbx, recs, users=True):
    """The three as a sauna would have them: the bench against the back, the stove in front of it to one side, the
    bucket beside the stove, a person standing by for scale."""
    clear()
    place(fbx, NAMES[0], (0, 0, 0))
    squares_at(0, 0, recs[NAMES[0]]['root']['size'])
    if users:
        people(recs[NAMES[0]], 0.0)
    place(fbx, NAMES[1], (4.5, 0, -4.5))
    squares_at(4.5, -4.5, recs[NAMES[1]]['root']['size'])
    place(fbx, NAMES[2], (1.5, 0, -4.5))
    squares_at(1.5, -4.5, recs[NAMES[2]]['root']['size'])
    _REV['_person'](Vector((-2.5, 0, 0)), -5.0)
    _REV['_block']('floor', (-6, -0.3, -8), (8, -0.07, 3), (150, 150, 156))


def review_final(out, fbx, recs):
    shots = []

    def scene(users=True):
        clear()
        x = 0.0
        for n in NAMES:
            size = recs[n]['root']['size']
            cx = x + max(size[0], 3.8) / 2
            place(fbx, n, (cx, 0, 0))
            _squares(cx, size)
            if users and recs[n]['furniture']['spots']:
                people(recs[n], cx)
            x += max(size[0], 3.8) + 3.0
        _REV['_person'](Vector((x + 0.5, 0, 0)), 0.0)
        _REV['_block']('floor', (-3, -0.3, -5), (x + 4, -0.07, 4), (150, 150, 156))
        return x
    sauna(fbx, recs)
    shots.append(render(out / '1_game_camera.png', (-0.45, 1.28, -1.0), (1400, 900), (-5.5, 0, -6.2), (6.5, 5.0, 2),
                        scale=1.02))
    x = scene()
    lo, hi = (-1.5, 0, -3.5), (x + 2.5, 5.2, 3)
    shots.append(render(out / '2_front_three_quarter.png', (-0.7, 0.45, -1.0), (1400, 800), lo, hi, scale=1.02))
    shots.append(render(out / '3_back_three_quarter.png', (0.7, 0.55, 1.0), (1400, 800), lo, hi, scale=1.02))
    x = scene(users=False)
    shots.append(render(out / '4_front_level.png', (0.0, 0.0, -1.0), (1400, 600), (-1.5, -0.3, -3.5),
                        (x + 2.5, 5.4, 3), scale=1.02))
    shots.append(render(out / '5_top.png', (0.0, 1.0, -0.02), (1400, 700), (-1.5, 0, -3.5), (x + 2.5, 5.4, 3),
                        scale=1.02))
    clear()
    x = 0.0
    for n in NAMES:
        size = recs[n]['root']['size']
        cx = x + max(size[2], 3.8) / 2
        place(fbx, n, (cx, 0, 0), 90)
        _squares(cx, size, 90)
        x += max(size[2], 3.8) + 3.0
    _REV['_person'](Vector((x + 1.0, 0, 0)), 0.0)
    shots.append(render(out / '6_side_level.png', (0.0, 0.0, -1.0), (1400, 600), (-1.5, -0.3, -3.5), (x + 3, 5.4, 3.5),
                        scale=1.02))
    # The bench in use, from the side at the sitters' height (the feet on the lower tier) and from the game's angle.
    clear()
    place(fbx, NAMES[0], (0, 0, 0))
    people(recs[NAMES[0]], 0.0)
    _REV['_block']('floor', (-4, -0.3, -3), (4, -0.07, 3), (150, 150, 156))
    shots.append(render(out / '7_bench_side_in_use.png', (-1.0, 0.05, 0.0), (1000, 700), (-3.2, -0.2, -2.2),
                        (3.2, 5.0, 1.6), scale=1.0))
    shots.append(render(out / '8_bench_in_use.png', (-0.5, 0.6, -1.0), (1000, 800), (-3.4, 0, -2.4), (3.4, 5.0, 1.6),
                        scale=1.0))
    clear()
    place(fbx, NAMES[0], (0, 0, 0))
    _REV['_block']('floor', (-4, -0.3, -3), (4, -0.07, 3), (150, 150, 156))
    shots.append(render(out / '9_bench_empty.png', (-0.6, 0.55, -1.0), (1000, 700), (-3.1, 0, -1.6), (3.1, 3.4, 1.6),
                        scale=1.0))
    clear()
    place(fbx, NAMES[1], (0, 0, 0))
    place(fbx, NAMES[2], (-3.0, 0, 0))
    _REV['_person'](Vector((3.2, 0, 0)), 0.0)
    _REV['_block']('floor', (-5, -0.3, -3), (5, -0.07, 3), (150, 150, 156))
    shots.append(render(out / '10_close_stove_bucket.png', (-0.5, 0.5, -1.0), (1100, 700), (-4.3, 0, -1.4),
                        (4.4, 5.0, 1.4), scale=1.0))
    return shots


# --- The set ------------------------------------------------------------------------------------------

def main():
    K.use_palette(FF_PALETTE)
    if GREY:
        K.IMPORT_CHECKS = False         # drafts with _A/_B/_C ids, not for import
        K.start_set(SET + '/silhouettes')
        for kind in KINDS:
            for k in 'ABC':
                sil(kind, k)
        recs = {p.name: r for p, r, _ in K.BUILT}
        out = K.ROOT / 'blender' / SET / 'silhouettes'
        (out / 'manifest.json').write_text(json.dumps({'pieces': recs}, indent=1))
        bad = {p.name: r.get('faults') for p, r, _ in K.BUILT if r.get('faults')}
        print('SILHOUETTE FAULTS', bad, flush=True)
        if not K.NOPREVIEW:
            print('SHEETS', silhouette_sheet(out / 'review', out / 'fbx', recs), flush=True)
        return
    K.start_set(SET)
    sauna_bench()
    steam_stone()
    water_bucket()
    built = [p.name for p, _, _ in K.BUILT]
    K.end_set('Frostfang Lodge: the Sauna\'s bench, stove and bucket (GDD A.13)', [(built, 3.0, 1.0)], sheet=False)
    out = K.ROOT / 'blender' / SET
    manifest = json.loads((out / 'manifest.json').read_text())
    patch_fixup(out / 'import_fixup.luau', manifest)
    val = json.loads((out / 'validation.json').read_text())
    val['spots'] = {n: {'spots': r['furniture']['spots'],
                        'checked': ('spots_check on the built and the re-imported triangles: Use_<n> from 1 without '
                                    'a gap, a Pose from MODELS.md\'s list, a level LookVector, no two spots on one '
                                    'square; Sit: inside the footprint, on a declared seat (tier_seat: rule 6\'s '
                                    f'{K.SEAT_Y[0]}..{K.SEAT_Y[1]}, 1.2 deep, 2.0 a person, nothing over it for 3), '
                                    f'the surface under it within {USE_SURFACE_TOL}, nothing over it, the seated '
                                    '5-stud person (sit_blocks, arms included) clear of the body; feet_check: both '
                                    f'soles on the lower tier (the body at most {FEET_DROP} under them)')
                        if r['furniture']['spots'] else 'no visitors\' spots (A.13.2: not a key piece)'}
                    for n, r in manifest['pieces'].items()}
    val['pieces_rows'] = {n: {k: ROWS[n[len('Furniture_'):]][k] for k in ('w', 'd', 'layer', 'height', 'location',
                                                                         'keyFor')}
                          | {'model_top': manifest['pieces'][n]['furniture']['model_top']} for n in built}
    val['height_findings'] = {
        'note': 'Pieces.luau\'s height against the model\'s top, a finding (not refused): the row must say it',
        **{n: FINDINGS[n] for n in built if n in FINDINGS}}
    val['not_validated'] = val.get('not_validated', [])[:1] + [
        'the attachments and each Use_<n> Pose attribute exist only in manifest.json until import_fixup.luau makes '
        'them', 'a visitor walking to the bench and sitting: no walker or clip has run', 'the embers lit: '
        'import_fixup makes Glow_Warm_1 Neon', 'steam: no part or attachment for it (the code\'s, if any)',
        'the two sitters\' figures side by side: each is checked against the piece; their arms (3.8 across, one '
        'square apart) overlap 0.8, as on the Cinema\'s row']
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
