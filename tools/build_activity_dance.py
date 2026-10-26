"""The Dance Floor's three pieces for Haunted Manor's kit (GDD A.13.2, the Dance Floor row; A.13.3, the Stage set).

    Furniture_LightFloor    2 x 2 squares, `Rug`: a light-up dance floor flat on the floor, 0.15 tall, to its
                            footprint's edges; every tile its own Glow_<Key>_<n> part so the code can light it;
                            Use_1..Use_4 `Dance`, one a square (the order of src/server/ActivityKit.luau's blockout)
    Furniture_Speaker       1 x 1 squares, `Floor`: a gothic speaker cabinet; no visitors' spots
    Furniture_DiscoBall     1 x 1 squares, `Floor`: a mirror ball hung from a stand on the floor; no spots

The contract is MODELS.md, "Decor" (the Rug layer: at most 0.15 tall, nothing above it, to the footprint's edge so
rugs meet edge to edge), "Furniture" and "Activity furniture: visitors' spots", as for the Bar and the Gym
(tools/build_activity_bar.py, whose definitions this runs: spot, spots_check, sdone, patch_fixup, _label, and
through it tools/build_built_rooms.py's kit). Added here, for the floor only: rug_check (the body to the
footprint's four edges, 0..0.15, no hole in the walked top, every tile a Glow_ part with its top at the dancers'
height). The `Dance` branch of spots_check is the Bar's, unchanged.

The tiles glow `Magenta` and `Cold`: MODELS.md rule 1 names `Magenta` as a palette key (the Neon facade's,
tools/build_facades.py), so the key is added to the kit's GLOW_KEYS here exactly as that script adds it.

The rows are on main's Pieces.luau (w, d, layer; the kit's Pieces check runs against them). Its own set,
blender/rooms/haunted_manor_dance/; the models belong in HotelKit.HauntedManor.

    blender -b -t 4 --python-exit-code 1 -P tools/build_activity_dance.py [-- grey] [-- nopreview]

`-- grey` writes the grey silhouettes (three options a piece, ids _A/_B/_C, not for import) to
blender/rooms/haunted_manor_dance/silhouettes/. Otherwise the chosen three are built in the Manor's palette;
review/ gets Workbench sheets only (Studio is running).
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

SET = 'rooms/haunted_manor_dance'
GREY = 'grey' in K.ARGS

if 'Magenta' not in K.GLOW_KEYS:        # MODELS.md rule 1's key, as tools/build_facades.py adds it
    K.GLOW_KEYS = K.GLOW_KEYS + ('Magenta',)
    K.GLOW_COLOURS = {**K.GLOW_COLOURS, 'Magenta': (255, 60, 200)}
DANCE_PALETTE = list(HM_PALETTE) + [('magenta', (255, 60, 200), 'Magenta'), ('silver', (185, 188, 198))]

TILE_BASE = 0.08                # the floor's base slab (the grout between the tiles): 0..0.08
TILE_TOP = K.RUG_TOP            # the tiles' tops, where the dancers stand: 0.15, the Rug layer's most
DOT_TOP = 0.13                  # the gold dots between the octagons, a hair under the tiles
DANCE_LOOK = (0, 0, -1)         # the floor's front, as the blockout's BACK: the player turns it toward the stage
BALL_R = 0.72                   # the mirror ball: 1.44 across (blind review 1: at 1.2 it read as a knob)
BALL_Y = 5.4                    # its centre: its bottom 4.68, a visible chain over it (review 1: jammed in the apex)


def dfurn(id_, spots=True):
    """Begin Furniture_<id_> on its Pieces.luau row (a silhouette _A/_B/_C on its piece's); its spots replace
    `Use` (use_check off; spots_check on when it has spots); a Rug piece gets rug_check."""
    base = id_.split('_')[0]
    row = dict(ROWS[base])
    ROWS[id_] = row
    K.pieces_decor()
    K._PIECES.setdefault(id_, {k: row[k] for k in ('w', 'd', 'layer', 'height')} | {'always': False})
    p = furn(id_)
    p.checks.remove(use_check)
    if spots:
        p.checks.append(spots_check)
    if row['layer'] == 'Rug':
        p.checks.append(rug_check)
    p.spots = {}
    p.glow_n = {}
    return p


def ddone(note):
    rec = sdone(note)
    rec['furniture']['pieces_row'] = 'Pieces.luau'
    if K.P.layer == 'Rug':
        rec['furniture']['rug'] = RUG_FINDINGS.get(K.P.name)
    return rec


def dance_spots():
    """One dancer a square, at its middle on the tiles' top, facing the floor's front; numbered as the
    blockout's (src/server/ActivityKit.luau, LightFloor): along x, then along z."""
    p = K.P
    n = 1
    for j in range(p.fd):
        for i in range(p.fw):
            spot(n, ((i - (p.fw - 1) / 2) * 3.0, TILE_TOP, (j - (p.fd - 1) / 2) * 3.0), DANCE_LOOK, 'Dance')
            n += 1


# --- The Rug layer's own check (MODELS.md, "Decor": Rug) --------------------------------------------------

RUG_FINDINGS = {}


def rug_check(piece, tris, stage):
    """A Rug piece: its body reaches all four edges of its footprint (rugs meet edge to edge), lies within
    0..RUG_TOP; the walked top has no hole (a ray every 0.25 finds the piece) and steps at most
    USE_SURFACE_TOL; it has Glow_ tiles, each one part, its top at TILE_TOP (where the dancers stand)."""
    f = []
    hx, hz = 1.5 * piece.fw, 1.5 * piece.fd
    allt = [t for p, ts in tris.items() if p not in ('Root', 'LOD_Proxy') for t in ts]
    vs = [v for t in allt for v in t]
    lo = Vector((min(v.x for v in vs), min(v.y for v in vs), min(v.z for v in vs)))
    hi = Vector((max(v.x for v in vs), max(v.y for v in vs), max(v.z for v in vs)))
    for a, b, what in ((lo.x, -hx, '-X'), (hi.x, hx, '+X'), (lo.z, -hz, '-Z'), (hi.z, hz, '+Z')):
        if abs(a - b) > 0.01:
            f.append(f'rug ({stage}): its {what} edge at {a:.3f}, not the footprint\'s {b:g} (rugs meet edge to edge)')
    if lo.y < -0.005 or hi.y > K.RUG_TOP + 0.005:
        f.append(f'rug ({stage}): y {lo.y:.3f}..{hi.y:.3f}, not 0..{K.RUG_TOP}')
    tops = []
    n = int(round(2 * hx / 0.25))
    m = int(round(2 * hz / 0.25))
    for i in range(n):
        for k in range(m):
            x, z = -hx + 0.125 + 0.25 * i, -hz + 0.125 + 0.25 * k
            top = max(K._ray_down(allt, x, z, 1.0), default=None)
            if top is None:
                f.append(f'rug ({stage}): a hole at ({x:.2f}, {z:.2f})')
                break
            tops.append(top)
    if tops and max(tops) - min(tops) > USE_SURFACE_TOL:
        f.append(f'rug ({stage}): its top steps {min(tops):.3f}..{max(tops):.3f}, over {USE_SURFACE_TOL}')
    glows = sorted(p for p in tris if p.startswith('Glow_'))
    if not glows and not GREY:
        f.append(f'rug ({stage}): no Glow_<Key>_<n> tile')
    for p in glows:
        top = max(v.y for t in tris[p] for v in t)
        if abs(top - TILE_TOP) > 0.005:
            f.append(f'rug ({stage}): {p}\'s top at {top:.3f}, not {TILE_TOP}')
    RUG_FINDINGS[piece.name] = {'edges': [K.v3(lo, 3), K.v3(hi, 3)], 'top_min': round(min(tops), 3) if tops else None,
                                'top_max': round(max(tops), 3) if tops else None, 'tiles': len(glows),
                                'tile_parts': glows}
    return f


# --- Shapes ---------------------------------------------------------------------------------------------

def rect(x0, z0, x1, z1):
    return [(x0, z0), (x1, z0), (x1, z1), (x0, z1)]


def clip_box(pts, h):
    """A convex polygon (x, z) clipped to the square |x|, |z| <= h (Sutherland-Hodgman)."""
    def clip(poly, inside, cut):
        out = []
        for i, p in enumerate(poly):
            q = poly[(i + 1) % len(poly)]
            if inside(p):
                out.append(p)
                if not inside(q):
                    out.append(cut(p, q))
            elif inside(q):
                out.append(cut(p, q))
        return out
    for axis, s in ((0, 1), (0, -1), (1, 1), (1, -1)):
        def inside(p, axis=axis, s=s):
            return s * p[axis] <= h + 1e-9

        def cut(p, q, axis=axis, s=s):
            t = (s * h - p[axis]) / (q[axis] - p[axis])
            return (p[0] + (q[0] - p[0]) * t, p[1] + (q[1] - p[1]) * t)
        pts = clip(pts, inside, cut)
        if not pts:
            return []
    out = []            # a vertex on the cut line comes out twice: drop the repeat (a degenerate face otherwise)
    for q in pts:
        if not out or abs(q[0] - out[-1][0]) + abs(q[1] - out[-1][1]) > 1e-6:
            out.append(q)
    if len(out) > 1 and abs(out[0][0] - out[-1][0]) + abs(out[0][1] - out[-1][1]) <= 1e-6:
        out.pop()
    return out


def tile(pts, col, y0=TILE_BASE, y1=TILE_TOP):
    """A tile: its own Glow_<Key>_<n> part when `col` is a glow colour (rule 1: the code lights each), else Body."""
    key = K.GLOW_OF.get(col)
    if key:
        n = K.P.glow_n[key] = K.P.glow_n.get(key, 0) + 1
        part = f'Glow_{key}_{n}'
    else:
        part = 'Body'
    prism(part, pts, y0, y1, col, plane='xz')


def sector(r0, r1, a0, a1, gap, k=4):
    """An annulus sector r0..r1 from angle a0 to a1 (degrees), shrunk by `gap` / 2 on every side."""
    def arc_pts(r, rev):
        da = math.degrees(gap / 2 / r)
        angs = [a0 + da + (a1 - a0 - 2 * da) * i / k for i in range(k + 1)]
        pts = [(r * math.cos(math.radians(a)), r * math.sin(math.radians(a))) for a in angs]
        return list(reversed(pts)) if rev else pts
    return arc_pts(r1 - gap / 2, False) + arc_pts(r0 + gap / 2, True)


def floor_base(c):
    span('Body', (-3.0, 0.0, -3.0), (3.0, TILE_BASE, 3.0), c['grout'])


def floor_a(c):
    """A: octagon and dot, the Victorian hall floor: 4 x 4 octagons (1.4 across, corners cut 0.3) in a chequer,
    a gold dot at every crossing; to the footprint's edge (the edge dots halved), so floors laid side by side
    join into one pattern."""
    floor_base(c)
    p, g, ch = 1.5, 0.1, 0.3
    for i in range(4):
        for k in range(4):
            x0, z0 = -3 + p * i + g / 2, -3 + p * k + g / 2
            x1, z1 = x0 + p - g, z0 + p - g
            octo = [(x0 + ch, z0), (x1 - ch, z0), (x1, z0 + ch), (x1, z1 - ch), (x1 - ch, z1), (x0 + ch, z1),
                    (x0, z1 - ch), (x0, z0 + ch)]
            tile(octo, c['a'] if (i + k) % 2 == 0 else c['b'])
    r = ch + g / 2 - 0.1            # the dot inside the cut corners' diamond, 0.1 of grout round it
    for i in range(5):
        for k in range(5):
            x, z = -3 + p * i, -3 + p * k
            d = clip_box([(x - r, z), (x, z - r), (x + r, z), (x, z + r)], 3.0)
            if len(d) >= 3:
                prism('Body', d, TILE_BASE, DOT_TOP, c['dot'], plane='xz')


def floor_b(c):
    """B: a framed floor: a dark border 0.45 wide with gold corner blocks, 4 x 4 square tiles in a chequer."""
    floor_base(c)
    b = 0.45
    for lo, hi in (((-3, -3), (3, -3 + b)), ((-3, 3 - b), (3, 3)), ((-3, -3 + b), (-3 + b, 3 - b)),
                   ((3 - b, -3 + b), (3, 3 - b))):
        span('Body', (lo[0], TILE_BASE, lo[1]), (hi[0], DOT_TOP, hi[1]), c['frame'])
    for sx in (-1, 1):
        for sz in (-1, 1):
            x0, x1 = sorted((sx * 3, sx * (3 - b)))
            z0, z1 = sorted((sz * 3, sz * (3 - b)))
            span('Body', (x0 + 0.06, DOT_TOP, z0 + 0.06), (x1 - 0.06, TILE_TOP, z1 - 0.06), c['dot'])
    h, g = 3 - b - 0.05, 0.1
    p = 2 * h / 4
    for i in range(4):
        for k in range(4):
            x0, z0 = -h + p * i + g / 2, -h + p * k + g / 2
            tile(rect(x0, z0, x0 + p - g, z0 + p - g), c['a'] if (i + k) % 2 == 0 else c['b'])


def floor_c(c):
    """C: a rose window laid in the floor: a round centre, a ring of eight petals, an outer ring of eight
    offset, four corner spandrels, in iron tracery."""
    floor_base(c)
    g = 0.12
    cen = [(0.55 * math.cos(math.radians(22.5 + 45 * i)), 0.55 * math.sin(math.radians(22.5 + 45 * i)))
           for i in range(8)]
    tile(cen, c['a'])
    for i in range(8):
        tile(sector(0.62, 1.7, 45 * i, 45 * (i + 1), g), c['b'] if i % 2 == 0 else c['a'])
    for i in range(8):
        tile(sector(1.7, 2.9, 22.5 + 45 * i, 22.5 + 45 * (i + 1), g), c['a'] if i % 2 == 0 else c['b'])
    e, cut = 2.95, 1.0
    for sx in (-1, 1):
        for sz in (-1, 1):
            rr = 2.9 + g / 2 + g / 2
            arcp = [(rr * math.cos(a), rr * math.sin(a))
                    for a in (math.atan2(math.sqrt(rr * rr - cut * cut), cut) * (1 - t / 4)
                              + math.atan2(cut, math.sqrt(rr * rr - cut * cut)) * (t / 4) for t in range(5))]
            pts = [(cut, e), (e, e), (e, cut)] + list(reversed(arcp))
            # arcp runs from (cut, 2.85) to (2.85, cut); reversed, it closes the corner from (e, cut)
            tile([(sx * x, sz * z) for x, z in pts], c['b'])


def driver(x, y, z, r, c):
    """A loudspeaker on a front face at z (facing -Z): a gold rim plate, the cone and its dust cap proud of it."""
    cyl('Body', (0, 0, 0), r + 0.07, 0.04, c['rim'], n=16, m=at((x, y, z), rx=-90))
    lathe('Body', [(r, 0.0), (r * 0.9, 0.03), (r * 0.34, 0.08), (r * 0.3, 0.1), (r * 0.18, 0.14), (0.0, 0.16)],
          c['cone'], n=16, m=at((x, y, z - 0.04), rx=-90))


def speaker_a(c):
    """A: a gothic cabinet: a plinth, the case with dark corner posts, a pointed-arch roof the full depth, a gold
    spire; a cloth grille under a pointed arch on the front with three drivers, largest at the bottom."""
    span('Body', (-1.08, 0.0, -0.88), (1.08, 0.22, 0.98), c['plinth'], bevel=0.03)
    span('Body', (-0.96, 0.22, -0.76), (0.96, 4.1, 0.86), c['case'])
    for sx in (-1, 1):
        for z0, z1 in ((-0.84, -0.6), (0.7, 0.94)):
            x0, x1 = sorted((sx * 0.82, sx * 1.04))
            span('Body', (x0, 0.22, z0), (x1, 4.12, z1), c['post'])
    prism('Body', lifted(gothic(-1.06, 1.06, 0.12, 0.85), 4.08), -0.86, 0.96, c['roof'], plane='xy')
    cyl('Body', (0, 4.86, -0.62), 0.1, 0.32, c['spire'], n=4, r_top=0.0)
    # Blind review 1 (README): bigger drivers on a wider grille (small dark discs from the game camera), and the
    # back finished: a pointed-arch panel with a gold-rimmed port and a gold plate (a blank panel read unfinished).
    prism('Body', lifted(gothic(-0.79, 0.79, 2.95, 3.5), 0.45), -0.79, -0.75, c['grille'], plane='xy')
    driver(0.0, 1.38, -0.79, 0.66, c)
    driver(0.0, 2.66, -0.79, 0.44, c)
    driver(0.0, 3.5, -0.79, 0.22, c)
    if c.get('back'):       # two bass ports low on the back (review 2: an arched panel with a plate read as a door)
        for x in (-0.4, 0.4):
            cyl('Body', (0, 0, 0), 0.3, 0.03, c['back'], n=14, m=at((x, 1.0, 0.86), rx=90))
            cyl('Body', (0, 0, 0), 0.22, 0.02, c['cone'], n=14, m=at((x, 1.0, 0.89), rx=90))


def speaker_b(c):
    """B: a stack: a wide bass box with one big driver, a narrower box with a mid driver, and a gramophone horn
    on top facing forward."""
    span('Body', (-1.06, 0.0, -0.86), (1.06, 2.6, 0.92), c['case'], bevel=0.05)
    span('Body', (-0.92, 0.3, -0.9), (0.92, 2.4, -0.86), c['grille'])
    driver(0.0, 1.35, -0.9, 0.72, c)
    span('Body', (-0.76, 2.6, -0.6), (0.76, 3.85, 0.8), c['post'], bevel=0.04)
    driver(0.0, 3.22, -0.6, 0.34, c)
    cyl('Body', (0, 3.85, 0.35), 0.14, 0.45, c['rim'], n=8)
    lathe('Body', [(0.12, 0.0), (0.13, 0.4), (0.2, 0.75), (0.36, 0.95), (0.6, 1.05), (0.62, 1.1), (0.08, 1.1)],
          c['roof'], n=14, m=at((0, 4.38, 0.42), rx=-100))


def speaker_c(c):
    """C: a coffin standing upright, its lid a cloth grille with three drivers."""
    out = [(-0.6, 0.0), (0.6, 0.0), (1.05, 3.4), (0.72, 5.0), (-0.72, 5.0), (-1.05, 3.4)]
    prism('Body', out, -0.7, 0.85, c['case'], plane='xy')
    inn = [(-0.5, 0.3), (0.5, 0.3), (0.88, 3.4), (0.6, 4.75), (-0.6, 4.75), (-0.88, 3.4)]
    prism('Body', inn, -0.74, -0.7, c['grille'], plane='xy')
    driver(0.0, 3.3, -0.74, 0.55, c)
    driver(0.0, 2.0, -0.74, 0.38, c)
    driver(0.0, 4.22, -0.74, 0.2, c)


def mirror_ball(c, centre, r=BALL_R, n=30, rings=16):     # fine facets (reviews 1, 2: coarse read as a beach ball)
    """The ball: a sphere of n x rings facets in a chequer of two mirror colours, a gold cap on top."""
    cx, cy, cz = centre
    verts = [Vector((cx, cy - r, cz))]
    for j in range(1, rings):
        ph = -math.pi / 2 + math.pi * j / rings
        for i in range(n):
            th = 2 * math.pi * (i + 0.5 * (j % 2 == 0) * 0) / n
            verts.append(Vector((cx + r * math.cos(ph) * math.cos(th), cy + r * math.sin(ph),
                                 cz + r * math.cos(ph) * math.sin(th))))
    verts.append(Vector((cx, cy + r, cz)))
    top = len(verts) - 1
    faces = ([], [])

    def ring(j, i):
        return 1 + (j - 1) * n + i % n
    for i in range(n):
        faces[i % 2].append((0, ring(1, i + 1), ring(1, i)))
        faces[(i + rings) % 2].append((ring(rings - 1, i), ring(rings - 1, i + 1), top))
    for j in range(1, rings - 1):
        for i in range(n):
            faces[(i + j) % 2].append((ring(j, i), ring(j, i + 1), ring(j + 1, i + 1), ring(j + 1, i)))
    # One closed shell, each facet its chequer colour (the kit's _add colours a call alike).
    store = K._part('Body', None)
    base = len(store[0])
    store[0].extend(verts)
    for col, fs in ((c['ball_a'], faces[0]), (c['ball_b'], faces[1])):
        assert col in K.COLOUR, col
        for fc in fs:
            store[1].append([base + i for i in fc])
            store[2].append(col)
    cyl('Body', (cx, cy + r - 0.04, cz), 0.13, 0.12, c['cap'], n=8)


def hang(c, x, z, y0, y1):
    """The ball's chain from its cap (y0) up to the hanger (y1): a rod and two links."""
    seg('Body', (x, y0 - 0.02, z), (x, y1 + 0.02, z), 0.03, c['chain'], n=4)
    for k in range(2):
        y = y0 + (y1 - y0) * (k + 0.5) / 2
        lathe('Body', [(0.05, y - 0.08), (0.08, y), (0.05, y + 0.08), (0.03, y)], c['chain'], n=6,
              base=(x, 0, z), closed=True)


BALL_TOP = BALL_Y + BALL_R + 0.08       # the cap's top


def ball_a(c):
    """A: a gallows stand: a square post at the back on a round foot with a bar forward under the ball, an arm
    over the ball with a short brace, a gold spire on the post; the ball on a chain from the arm."""
    zb, zp = -0.3, 0.74
    cyl('Body', (0, 0, zp - 0.12), 0.45, 0.14, c['frame'], n=12)
    span('Body', (-0.12, 0.0, -0.95), (0.12, 0.1, zp - 0.3), c['frame'], bevel=0.02)
    span('Body', (-0.12, 0.13, zp - 0.12), (0.12, 6.74, zp + 0.12), c['frame'])
    span('Body', (-0.09, 6.58, zb - 0.16), (0.09, 6.74, zp - 0.1), c['frame'])
    seg('Body', (0, 6.02, zp - 0.11), (0, 6.6, zp - 0.5), 0.05, c['frame'], n=6)
    sphere('Body', (0, 6.66, zb - 0.22), 0.1, c['spire'], n=6, rings=3)
    cyl('Body', (0, 6.73, zp), 0.17, 0.27, c['spire'], n=4, r_top=0.0)
    mirror_ball(c, (0, BALL_Y, zb))
    hang(c, 0, zb, BALL_TOP, 6.59)


def ball_b(c):
    """B: a pointed-arch frame: two posts on long feet, the arch over them, a gold spire; the ball on a chain
    from the arch's point."""
    for sx in (-1, 1):
        x0, x1 = sorted((sx * 0.86, sx * 1.1))      # 0.24 thick (blind review 1: hairlines from the game camera)
        span('Body', (x0, 0.0, -1.0), (x1, 0.12, 1.0), c['frame'], bevel=0.02)
        span('Body', (x0, 0.12, -0.13), (x1, 5.9, 0.13), c['frame'])
    outer = K.arch_points(-1.1, 1.1, 5.8, 6.72, n=4)
    inner = K.arch_points(-0.86, 0.86, 5.8, 6.45, n=4)
    prism('Body', outer + list(reversed(inner)), -0.1, 0.1, c['frame'], plane='xy')
    cyl('Body', (0, 6.62, 0), 0.13, 0.38, c['spire'], n=4, r_top=0.0)
    mirror_ball(c, (0, BALL_Y, 0))
    hang(c, 0, 0, BALL_TOP, 6.47)


def ball_c(c):
    """C: a tripod cage: three iron legs rising nearly upright and curving in to a point, a gold spire on it;
    the ball on a chain from the point, inside the legs."""
    for k in range(3):
        a = math.radians(90 + 120 * k)
        pts = [(r * math.cos(a), y, r * math.sin(a)) for r, y in ((0.9, 0.08), (0.88, 0.5), (0.86, 5.4), (0.68, 6.25),
                                                                  (0.3, 6.62), (0.0, 6.72))]
        for p0, p1 in zip(pts, pts[1:]):
            seg('Body', p0, p1, 0.07, c['frame'], n=6)
            sphere('Body', p1, 0.07, c['frame'], n=6, rings=3)
        sphere('Body', (pts[0][0], 0.09, pts[0][2]), (0.13, 0.09, 0.13), c['spire'], n=8, rings=4)
    cyl('Body', (0, 6.7, 0), 0.13, 0.3, c['spire'], n=4, r_top=0.0)
    mirror_ball(c, (0, BALL_Y, 0))
    hang(c, 0, 0, BALL_TOP, 6.7)


GC = {'grout': 'stone_dark', 'a': 'white', 'b': 'stone', 'dot': 'grey', 'frame': 'stone_dark',
      'plinth': 'stone_dark', 'case': 'grey', 'post': 'stone_dark', 'roof': 'stone_dark', 'spire': 'stone',
      'grille': 'stone', 'rim': 'stone_dark', 'cone': 'black', 'ball_a': 'white', 'ball_b': 'stone', 'cap': 'stone',
      'chain': 'stone_dark'}

FLOORS = {'A': floor_a, 'B': floor_b, 'C': floor_c}
SPEAKERS = {'A': speaker_a, 'B': speaker_b, 'C': speaker_c}
BALLS = {'A': ball_a, 'B': ball_b, 'C': ball_c}
NOTES = {'LightFloor_A': 'A: octagon and dot, the Victorian hall floor: 16 octagon tiles, gold dots between, to the edges',
         'LightFloor_B': 'B: a framed floor: a dark border with gold corners round 16 square tiles',
         'LightFloor_C': 'C: a rose window in the floor: a centre, two rings of eight, four corner spandrels',
         'Speaker_A': 'A: a gothic cabinet under a pointed-arch roof, three drivers in an arched grille',
         'Speaker_B': 'B: a stack: a bass box, a mid box and a gramophone horn on top',
         'Speaker_C': 'C: an upright coffin, its lid a grille with three drivers',
         'DiscoBall_A': 'A: a gallows stand: a post at the back, an arm over the ball on a chain',
         'DiscoBall_B': 'B: a pointed-arch frame, the ball hung from its point',
         'DiscoBall_C': 'C: a tripod cage of three bowed iron legs, the ball hung inside'}


def sil(kind, k, table):
    dfurn(f'{kind}_{k}', spots=(kind == 'LightFloor'))
    table[k](GC)
    if kind == 'LightFloor':
        dance_spots()
    ddone(NOTES[f'{kind}_{k}'])


# --- The chosen three, in the Manor's dress -------------------------------------------------------------

HM = {'grout': 'iron', 'a': 'magenta', 'b': 'moonglow', 'dot': 'gold', 'frame': 'iron', 'plinth': 'wood_dark',
      'case': 'plum', 'back': 'plum_dark', 'post': 'wood_dark', 'roof': 'wood_dark', 'spire': 'gold', 'grille': 'crimson',
      'rim': 'gold', 'cone': 'black', 'ball_a': 'white', 'ball_b': 'silver', 'cap': 'gold', 'chain': 'iron'}

CHOSEN = {'LightFloor': 'A', 'Speaker': 'A', 'DiscoBall': 'B'}


def light_floor():
    dfurn('LightFloor')
    FLOORS[CHOSEN['LightFloor']](HM)
    dance_spots()
    ddone('a Haunted Manor light-up floor: the Victorian octagon-and-dot hall floor, 16 octagon tiles lit magenta '
          'and moon-blue in a chequer (each its own Glow part), gold dots between on iron grout, to the edges')


def speaker():
    dfurn('Speaker', spots=False)
    SPEAKERS[CHOSEN['Speaker']](HM)
    ddone('a Haunted Manor speaker: a plum cabinet between dark-wood corner posts on a plinth, a dark-wood '
          'pointed-arch roof with a gold spire, a crimson cloth grille under a pointed arch with three black '
          'drivers in gold rims')


def disco_ball():
    dfurn('DiscoBall', spots=False)
    BALLS[CHOSEN['DiscoBall']](HM)
    ddone('a Haunted Manor disco ball: a mirror ball of white and silver facets on an iron chain from the '
          'point of an iron pointed-arch frame on two long feet, a gold spire on the point')


# --- Review (Workbench on light grey: Studio is running, no EEVEE or Cycles) --------------------------

def people(rec, cx, cz=0.0):
    for a, pose in rec['furniture']['spots'].items():
        u = rec['attachments'][a]
        _REV['_person'](Vector((cx + u['pos'][0], u['pos'][1], 0)), cz + u['pos'][2])


ROWS_SIL = (('LightFloor_A', 'LightFloor_B', 'LightFloor_C'), ('Speaker_A', 'Speaker_B', 'Speaker_C'),
            ('DiscoBall_A', 'DiscoBall_B', 'DiscoBall_C'))


def lay(fbx, recs, row, z0, labels, gap=6.0, spots=True):
    x = 0.0
    for i in row:
        n = f'Furniture_{i}'
        size = recs[n]['root']['size']
        cx = x + max(size[0], 3.8) / 2
        place(fbx, n, (cx, 0, z0))
        for a in range(int(round(size[0] / 3))):
            for b in range(int(round(size[2] / 3))):
                x0, zz = cx - size[0] / 2 + 3 * a, z0 - size[2] / 2 + 3 * b
                shade = (205, 205, 210) if (a + b) % 2 else (185, 185, 192)
                _REV['_block']('sq', (x0 + 0.03, -0.06, zz + 0.03), (x0 + 2.97, -0.01, zz + 2.97), shade)
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
    x = max(lay(fbx, recs, ROWS_SIL[0], 0.0, True), lay(fbx, recs, ROWS_SIL[1], 11.0, True),
            lay(fbx, recs, ROWS_SIL[2], 19.0, True))
    _REV['_block']('floor', (-3, -0.3, -6), (x + 2, -0.07, 22), (150, 150, 156))
    shots.append(render(out / 'silhouettes_game.png', (-0.35, 1.25, -1.0), (1600, 1000), (-2, 0, -6), (x, 7.2, 21),
                        scale=1.0))
    clear()
    x = lay(fbx, recs, ROWS_SIL[0], 0.0, False, spots=False)
    shots.append(render(out / 'silhouettes_top_floors.png', (0.0, 1.0, -0.02), (1600, 600), (-2, 0, -3.5),
                        (x, 0.2, 3.5), scale=1.02))
    for k, row in enumerate(ROWS_SIL[1:], 2):
        clear()
        x = lay(fbx, recs, row, 0.0, False)
        shots.append(render(out / f'silhouettes_side_{k}.png', (-0.75, 0.25, -0.65), (1600, 650), (-2, -0.3, -2.5),
                            (x, 7.4, 2.5), scale=1.02))
    return shots


NAMES = ['Furniture_LightFloor', 'Furniture_Speaker', 'Furniture_DiscoBall']


def room(fbx, recs, dancers=True):
    """The three as a dance floor would have them: the floor in the middle with its dancers, a speaker either
    side at its back corners, the disco ball beside its front corner; a person beside for scale."""
    clear()
    place(fbx, NAMES[0], (0, 0, 0))
    _squares(0, recs[NAMES[0]]['root']['size'])
    if dancers:
        people(recs[NAMES[0]], 0.0)
    for x in (-4.5, 4.5):
        place(fbx, NAMES[1], (x, 0, 1.5))
    place(fbx, NAMES[2], (-4.5, 0, -4.5))     # off the floor's front corner, in front of nothing (review 3)
    _REV['_person'](Vector((6.5, 0, 0)), -4.5)
    _REV['_block']('floor', (-8, -0.3, -8), (8, -0.07, 5), (150, 150, 156))


def review_final(out, fbx, recs):
    shots = []

    def scene(spots=True):
        clear()
        x = 0.0
        for n in NAMES:
            size = recs[n]['root']['size']
            cx = x + max(size[0], 3.8) / 2
            place(fbx, n, (cx, 0, 0))
            _squares(cx, size)
            if spots:
                people(recs[n], cx)
            x += max(size[0], 3.8) + 3.0
        _REV['_person'](Vector((x + 0.5, 0, 0)), 0.0)
        _REV['_block']('floor', (-3, -0.3, -6), (x + 4, -0.07, 5), (150, 150, 156))
        return x
    room(fbx, recs)
    shots.append(render(out / '1_game_camera.png', (-0.45, 1.28, -1.0), (1400, 800), (-7, 0, -5.5), (7, 7.2, 4),
                        scale=1.02))
    x = scene()
    lo, hi = (-1.5, 0, -4.5), (x + 2.5, 7.2, 3.5)
    shots.append(render(out / '2_front_three_quarter.png', (-0.7, 0.45, -1.0), (1400, 800), lo, hi, scale=1.02))
    shots.append(render(out / '3_back_three_quarter.png', (0.7, 0.55, 1.0), (1400, 800), lo, hi, scale=1.02))
    x = scene(spots=False)
    shots.append(render(out / '4_front_level.png', (0.0, 0.0, -1.0), (1400, 700), (-1.5, -0.3, -4.5),
                        (x + 2.5, 7.4, 3.5), scale=1.02))
    shots.append(render(out / '5_top.png', (0.0, 1.0, -0.02), (1400, 800), (-1.5, 0, -4.5), (x + 2.5, 7.4, 3.5),
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
    shots.append(render(out / '6_side_level.png', (0.0, 0.0, -1.0), (1400, 600), (-1.5, -0.3, -5), (x + 3, 7.4, 5),
                        scale=1.02))
    # Close-ups: the floor's tiles from the game's angle (no dancers), two floors laid side by side (they join),
    # the speaker's front, the ball and its stand beside a person.
    clear()
    place(fbx, NAMES[0], (0, 0, 0))
    _REV['_block']('floor', (-5, -0.3, -5), (5, -0.07, 5), (150, 150, 156))
    shots.append(render(out / '7_close_floor.png', (-0.45, 1.28, -1.0), (1000, 800), (-3.2, 0, -3.2), (3.2, 0.2, 3.2),
                        scale=1.0))
    clear()
    place(fbx, NAMES[0], (-3, 0, 0))
    place(fbx, NAMES[0], (3, 0, 0))
    place(fbx, NAMES[0], (-3, 0, 6))
    place(fbx, NAMES[0], (3, 0, 6))
    _REV['_block']('floor', (-8, -0.3, -5), (8, -0.07, 11), (150, 150, 156))
    shots.append(render(out / '8_four_floors.png', (0.0, 1.0, -0.02), (1000, 1000), (-6.2, 0, -3.2), (6.2, 0.2, 9.2),
                        scale=1.0))
    clear()
    place(fbx, NAMES[1], (0, 0, 0))
    _REV['_person'](Vector((2.6, 0, 0)), -0.5)
    _REV['_block']('floor', (-3, -0.3, -4), (4, -0.07, 3), (150, 150, 156))
    shots.append(render(out / '9_close_speaker.png', (-0.55, 0.3, -1.0), (1000, 800), (-1.5, 0, -1.5), (3.6, 5.4, 1.5),
                        scale=1.0))
    clear()
    place(fbx, NAMES[2], (0, 0, 0))
    _REV['_person'](Vector((0.0, 0, 0)), -3.0)
    _REV['_block']('floor', (-3, -0.3, -5), (3, -0.07, 3), (150, 150, 156))
    shots.append(render(out / '10_close_ball.png', (-0.8, 0.35, -0.7), (1000, 900), (-1.9, 0, -3.6), (1.9, 7.1, 1.3),
                        scale=1.0))
    return shots


# --- The set ------------------------------------------------------------------------------------------

def main():
    K.use_palette(DANCE_PALETTE)
    if GREY:
        K.IMPORT_CHECKS = False         # drafts with _A/_B/_C ids, not for import
        K.start_set(SET + '/silhouettes')
        for kind, table in (('LightFloor', FLOORS), ('Speaker', SPEAKERS), ('DiscoBall', BALLS)):
            for k in table:
                sil(kind, k, table)
        recs = {p.name: r for p, r, _ in K.BUILT}
        out = K.ROOT / 'blender' / SET / 'silhouettes'
        (out / 'manifest.json').write_text(json.dumps({'pieces': recs}, indent=1))
        bad = [p.name for p, r, _ in K.BUILT if r.get('faults')]
        print('SILHOUETTE FAULTS', bad, flush=True)
        if not K.NOPREVIEW:
            print('SHEETS', silhouette_sheet(out / 'review', out / 'fbx', recs), flush=True)
        return
    K.start_set(SET)
    light_floor()
    speaker()
    disco_ball()
    built = [p.name for p, _, _ in K.BUILT]
    K.end_set('Haunted Manor: the Dance Floor\'s light-up floor, speaker and disco ball (GDD A.13)',
              [(built, 3.0, 1.0)], sheet=False)
    out = K.ROOT / 'blender' / SET
    manifest = json.loads((out / 'manifest.json').read_text())
    patch_fixup(out / 'import_fixup.luau', manifest)
    val = json.loads((out / 'validation.json').read_text())
    val['spots'] = {n: {'spots': r['furniture']['spots'],
                        'checked': ('spots_check on the built and the re-imported triangles: Use_<n> from 1 without '
                                    'a gap, a Pose from MODELS.md\'s list, a level LookVector, no two spots on one '
                                    'square; Dance inside the footprint by the torso '
                                    f'({TORSO_R}), the surface flat to {USE_SURFACE_TOL} under it, nothing of the '
                                    f'body within the dancer\'s figure ({FIGURE_R} round, {FIGURE_H} tall)')
                        if r['furniture']['spots'] else 'no visitors\' spots (A.13.2: not a key piece)'}
                    for n, r in manifest['pieces'].items()}
    val['rug'] = {'Furniture_LightFloor': {
        'checked': 'rug_check on the built and the re-imported triangles: the body to all four footprint edges '
                   f'(+-3), y 0..{K.RUG_TOP}, a ray every 0.25 finds it (no hole), its top steps at most '
                   f'{USE_SURFACE_TOL}, every tile a Glow_ part with its top at {TILE_TOP}',
        **(RUG_FINDINGS.get('Furniture_LightFloor') or {})}}
    val['pieces_rows'] = {n: {k: ROWS[n[len('Furniture_'):]][k] for k in ('w', 'd', 'layer', 'height', 'keyFor')}
                          | {'model_top': manifest['pieces'][n]['furniture']['model_top']} for n in built}
    val['height_findings'] = {
        'note': 'Pieces.luau\'s height against the model\'s top, a finding (not refused): the row must say it',
        **{n: FINDINGS[n] for n in built if n in FINDINGS}}
    val['not_validated'] = val.get('not_validated', [])[:1] + [
        'the attachments and each Use_<n> Pose attribute exist only in manifest.json until import_fixup.luau makes '
        'them', 'a visitor walking to a spot and dancing: no walker or clip has run',
        'the tiles lit: import_fixup makes them Neon in their key\'s colour; no code lights them in turn yet',
        'the ball is Body: nothing spins (MODELS.md names no part for it)']
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
