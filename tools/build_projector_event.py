"""The Cinema's projector for Haunted Manor's kit, and the two event decor pieces (one model for every kit).

    Furniture_Projector     1 x 1 `Floor` (GDD A.13.2, the Cinema row's "other furniture"): a film projector on a
                            tripod stand, two reels on top, its lens (Glow_Warm_1) to the front, -Z; no visitors'
                            spots (guests watch from the seats). Manor dress, beside the Film Screen and the Cinema
                            Seats (tools/build_activity_cinema.py). Set blender/rooms/haunted_manor_projector/.
    Decor_JackOLantern      1 x 1 `Floor`, event decor (Pieces.luau location 0: the Halloween Candy shop, GDD
                            §8.2): a carved pumpkin, its face (Glow_Warm_1) to the front.
    Decor_Snowman           1 x 1 `Floor`, event decor (the Winter shop, "the Frostfang crossover"): a snowman.
                            Set blender/decor/event_decor/.

Two sets because the contract puts them apart (MODELS.md, "Decor": decor of every location, location 0 and not
`always`, which is event decor, is one model for every kit, built in its own set under blender/decor/, its colours
its own, none a location's), while the projector is location-0 furniture, modelled in each kit in its style.

The contract is MODELS.md "Decor" and "Furniture": footprint and layer the Pieces.luau row's (main has all three
rows: Projector 1 x 1 Floor 4.5, JackOLantern 1 x 1 Floor 2.0, Snowman 1 x 1 Floor 4.5; the kit refuses a height
off by more than 0.3), the body 0.4 inside the footprint, `Body` not colliding, glows their own parts, no coplanar
faces, nothing floats (grounded_check, on the event decor too), budgets 1,500. Definitions from
tools/build_activity_cinema.py (and through it the bar's and the built rooms' kit), run without its main.

    blender -b -t 4 --python-exit-code 1 -P tools/build_projector_event.py -- grey|projector|event [nopreview]

`grey`: the silhouettes, two options a piece (ids _A/_B, not for import) and one sheet, into
blender/rooms/haunted_manor_projector/silhouettes/. `projector`: the Projector's set; it first builds the Cinema's
screen and seat row (build_activity_cinema.py's own functions, unchanged) into the set's context/ folder, only to
stand them beside it in the review pictures (never for import; the Cinema set is not touched). `event`: the event
decor set. review/ gets Workbench pictures only (no EEVEE or Cycles).
"""
import ast
import json
import math
from pathlib import Path

_CI = Path(__file__).resolve().parent / 'build_activity_cinema.py'
_tree = ast.parse(_CI.read_text(encoding='utf8'))
_tree.body = [n for n in _tree.body if not isinstance(n, ast.Try)]          # its main() call
NS = {'__file__': str(_CI), '__name__': 'build_activity_cinema'}
exec(compile(_tree, str(_CI), 'exec'), NS)
globals().update({k: v for k, v in NS.items() if not k.startswith('__') and k not in ('SET', 'GREY', 'main')})
# From here, besides the cinema's names (film_screen, cinema_seat, no_spots, sdone2, people, ...): K, bpy, Vector,
# Matrix, span, box, cyl, lathe, sphere, prism, at, finish, grounded_check, PENDING, ROWS, render, clear, place,
# _squares, _REV, _label, HM_PALETTE.

SET_P = 'rooms/haunted_manor_projector'
SET_E = 'decor/event_decor'
MODE = next((m for m in ('grey', 'projector', 'event') if m in K.ARGS), 'projector')

PENDING['Projector'] = dict(ROWS['Projector'])        # main's row, as bfurn reads rows (no change proposed)

EV_PALETTE = [
    ('grey', (110, 110, 120)), ('white', (240, 240, 245)), ('black', (30, 28, 36)),
    ('stone', (130, 125, 140)), ('stone_dark', (85, 82, 95)),
    ('pumpkin', (236, 120, 28)), ('pumpkin_dark', (150, 62, 18)), ('pumpkin_light', (250, 156, 52)),
    ('stem', (104, 112, 52)), ('stem_dark', (72, 76, 38)),
    ('snow', (244, 248, 255)), ('snow_shade', (212, 224, 240)), ('coal', (38, 38, 46)), ('carrot', (242, 118, 36)),
    ('twig', (112, 78, 50)), ('scarf', (186, 36, 48)), ('scarf_light', (244, 238, 228)), ('hat', (34, 32, 40)),
    ('flame', (255, 196, 92), 'Warm'),
]


def rod(part, a, b, r, col, n=6, r1=None):
    """A round rod from a to b (r1: its radius at b)."""
    a, b = Vector(a), Vector(b)
    d = b - a
    cyl(part, (0, 0, 0), r, d.length, col, n=n, r_top=r1,
        m=Matrix.Translation(a) @ d.to_track_quat('Y', 'Z').to_matrix().to_4x4())


def ring_x(part, c, r0, r1, half, col, n=16):
    """A flat ring (a reel's flange) about the X axis through c: radii r0..r1, x c.x +- half."""
    lathe(part, [(r0, -half), (r1, -half), (r1, half), (r0, half)], col, n=n, closed=True,
          m=at(c, rz=90))


def disc_x(part, c, r, half, col, n=16):
    cyl(part, (0, -half, 0), r, 2 * half, col, n=n, m=at(c, rz=90))


# --- The projector ----------------------------------------------------------------------------------

REEL_Y, REEL_R = 4.0, 0.5           # the reels' hubs and radius: tops at 4.5 (the row's height)
REEL_Z = (-0.53, 0.56)              # the front and the rear reel


def reel(c, z, metal, film, hub):
    ctr = (0.0, REEL_Y, z)
    ring_x('Body', ctr, REEL_R - 0.08, REEL_R, 0.06, metal)
    disc_x('Body', ctr, 0.3, 0.035, film)                     # the coiled film
    for k in range(4):                                          # spokes, flange to hub
        a = math.pi / 4 + k * math.pi / 2
        p0 = (0.0, REEL_Y + 0.08 * math.sin(a), z + 0.08 * math.cos(a))
        p1 = (0.0, REEL_Y + (REEL_R - 0.06) * math.sin(a), z + (REEL_R - 0.06) * math.cos(a))
        rod('Body', p0, p1, 0.035, metal, n=4)
    disc_x('Body', ctr, 0.1, 0.09, hub, n=8)


def projector_head(c, y0, lens_glow):
    """The projector itself from y0: the lamp housing, a metallic band, the lens barrel to the front (-Z) and
    its glass, a crank on the right (+X), two reels on arms."""
    span('Body', (-0.42, y0, -0.6), (0.42, y0 + 0.85, 0.58), c['body'], bevel=0.08)
    span('Body', (-0.44, y0 + 0.38, -0.62), (0.44, y0 + 0.5, 0.6), c['trim'])
    span('Body', (-0.3, y0 + 0.84, -0.4), (0.3, y0 + 0.98, 0.42), c['body'], bevel=0.04)     # the lamp's lid
    zf, yl = -0.6, y0 + 0.44
    lathe('Body', [(0.0, 0.0), (0.27, 0.0), (0.27, 0.1), (0.2, 0.12), (0.2, 0.36), (0.24, 0.38), (0.24, 0.44),
                   (0.0, 0.44)], c['trim'], n=12, m=at((0, yl, zf + 0.02), rx=-90))
    cyl(lens_glow, (0, 0, 0), 0.16, 0.04, c['glow'], n=12, m=at((0, yl, zf - 0.39), rx=-90))
    cyl('Body', (0, 0, 0), 0.16, 0.12, c['trim'], n=10, m=at((0.4, y0 + 0.44, 0.1), rz=-90))  # the crank's boss
    rod('Body', (0.5, y0 + 0.44, 0.1), (0.53, y0 + 0.44, 0.1 + 0.001), 0.04, c['trim'])
    span('Body', (0.5, y0 + 0.4, 0.06), (0.56, y0 + 0.75, 0.14), c['trim'])
    rod('Body', (0.53, y0 + 0.72, 0.1), (0.7, y0 + 0.72, 0.1), 0.05, c['body'], n=6)
    for z, zb in zip(REEL_Z, (-0.25, 0.28)):
        rod('Body', (0.13, y0 + 0.96, zb), (0.13, REEL_Y, z), 0.05, c['metal'])
        rod('Body', (0.13, REEL_Y, z), (0.0, REEL_Y, z), 0.05, c['metal'])
        reel(c, z, c['metal'], c['film'], c['trim'])


def projector_a(c, lens='Glow_Warm_1'):
    """A: on a tripod stand: three splayed legs (one back, two front), a turned column, the projector on a yoke."""
    y0 = 2.62
    for a in (90, 210, 330):
        ex, ez = 0.95 * math.cos(math.radians(a)), 0.95 * math.sin(math.radians(a))
        rod('Body', (0.0, 1.05, 0.0), (ex, 0.1, ez), 0.07, c['leg'], n=6, r1=0.05)
        sphere('Body', (ex, 0.07, ez), (0.13, 0.07, 0.13), c['metal'], n=8, rings=4)
    lathe('Body', [(0.0, 0.85), (0.2, 0.85), (0.24, 0.95), (0.2, 1.15), (0.13, 1.2), (0.0, 1.2)], c['metal'], n=10)
    lathe('Body', [(0.0, 1.18), (0.1, 1.18), (0.09, 2.3), (0.15, 2.36), (0.15, 2.44), (0.0, 2.44)], c['leg'], n=10)
    span('Body', (-0.3, 2.42, -0.35), (0.3, y0 + 0.02, 0.35), c['metal'])                       # the yoke
    projector_head(c, y0, lens)


def projector_b(c, lens='Glow_Warm_1'):
    """B: on a little wooden cart: a top on four turned legs, a shelf with two film cans, the projector on it."""
    y0 = 2.62
    span('Body', (-0.95, 2.45, -0.95), (0.95, y0, 0.95), c['top'], bevel=0.04)
    for sx in (-1, 1):
        for sz in (-1, 1):
            lathe('Body', [(0.0, 0.0), (0.1, 0.0), (0.12, 0.25), (0.07, 0.5), (0.07, 2.0), (0.11, 2.2),
                           (0.09, 2.46), (0.0, 2.46)], c['leg'], n=6, base=(sx * 0.8, 0, sz * 0.8))
    span('Body', (-0.85, 0.7, -0.85), (0.85, 0.82, 0.85), c['top'])
    for x in (-0.38, 0.38):
        cyl('Body', (x, 0.82, 0.1), 0.32, 0.12, c['metal'], n=10)
    projector_head(c, y0, lens)


# --- The jack-o'-lantern ----------------------------------------------------------------------------

def pumpkin(c, y0, R, H, lobes=8, phase=22.5, n=10, rings=6):
    """A pumpkin of `lobes` ellipsoids round a darker core (the grooves), base at y0, R across its middle, H tall.
    Returns the shapes for front_z."""
    shapes = []
    rr = R * 0.57                       # a lobe's radial half-size; its centre R - rr out
    for k in range(lobes):
        ang = phase + 360.0 * k / lobes
        cl, rad = (R - rr, y0 + H / 2, 0.0), (rr, H / 2, R * 0.42 * 8 / lobes)
        sphere('Body', cl, rad, c['skin'], n=n, rings=rings, m=at((0, 0, 0), ry=ang))
        shapes.append((cl, rad, ang))
    core = ((0.0, y0 + H / 2 + 0.01, 0.0), (R * 0.89, H * 0.47, R * 0.89), 0.0)     # shows in the grooves
    sphere('Body', *core[:2], c['groove'], n=n + 2, rings=rings)
    shapes.append(core)
    return shapes


def front_z(x, y, shapes):
    """The front (-Z) surface's z at (x, y) over the ellipsoids, or None."""
    best = None
    for cl, rad, ang in shapes:
        mi = at((0, 0, 0), ry=ang).inverted()
        o = mi @ Vector((x, y, -9.0)) - Vector(cl)
        d = mi.to_3x3() @ Vector((0, 0, 1))
        oq = Vector((o.x / rad[0], o.y / rad[1], o.z / rad[2]))
        dq = Vector((d.x / rad[0], d.y / rad[1], d.z / rad[2]))
        a, b, cc = dq.dot(dq), 2 * oq.dot(dq), oq.dot(oq) - 1
        disc = b * b - 4 * a * cc
        if disc >= 0:
            z = -9.0 + (-b - math.sqrt(disc)) / (2 * a)
            best = z if best is None else min(best, z)
    return best


def carve(part, shapes, outline, col, proud=0.03, deep=0.14):
    """A face feature: `outline` (x, y) as a flat-fronted prism through the skin, its front `proud` before the
    most forward point under it (Glow_Warm_1: the candlelight through the cut)."""
    zs = [front_z(x, y, shapes) for x, y in outline]
    cx = sum(p[0] for p in outline) / len(outline)
    cy = sum(p[1] for p in outline) / len(outline)
    zs.append(front_z(cx, cy, shapes))
    prism(part, outline, min(zs) - proud, max(zs) + deep, col, plane='xy')


def face(shapes, s, y, col, part='Glow_Warm_1'):
    """Triangle eyes, a nose and a grin with two teeth, scaled by s about (0, y)."""
    def sc(pts):
        return [(px * s, y + py * s) for px, py in pts]
    for sx in (-1, 1):                  # the eyes, their points up and in
        carve(part, shapes, sc([(sx * 0.2, 0.18), (sx * 0.58, 0.14), (sx * 0.34, 0.5)][::sx]), col)
    carve(part, shapes, sc([(-0.1, -0.06), (0.1, -0.06), (0.0, 0.1)]), col)
    grin = [(-0.62, -0.18), (-0.36, -0.36), (-0.2, -0.38), (-0.2, -0.3), (-0.06, -0.3), (-0.06, -0.4),
            (0.2, -0.4), (0.38, -0.34), (0.62, -0.18), (0.36, -0.24), (0.2, -0.24), (0.2, -0.32),
            (0.06, -0.32), (0.06, -0.24), (-0.36, -0.22)]
    carve(part, shapes, sc(grin), col)


def stem(c, x, y, z, h=0.45, r=0.12):
    rod('Body', (x, y - 0.12, z), (x + 0.04, y + h * 0.6, z + 0.02), r, c['stem'], n=6, r1=r * 0.8)
    rod('Body', (x + 0.04, y + h * 0.6, z + 0.02), (x + 0.16, y + h - r * 0.7, z + 0.08), r * 0.8, c['stem'], n=6,
        r1=r * 0.6)
    cyl('Body', (x, y - 0.05, z), r * 1.6, 0.08, c['stem_dark'], n=6)


def lantern_a(c):
    """A: one big carved pumpkin, triangle eyes and a toothy grin, a bent stem."""
    sh = pumpkin(c, 0.0, 1.06, 1.56)
    face(sh, 1.0, 0.86, c['glow'], part=c.get('face', 'Glow_Warm_1'))
    stem(c, 0.0, 1.52, 0.0)


def lantern_b(c):
    """B: two stacked: a squat plain pumpkin under a smaller carved one, its stem on top."""
    pumpkin(c, 0.0, 1.06, 0.98, n=8, rings=5)
    sh = pumpkin(c, 0.9, 0.74, 0.86, n=8, rings=5)
    face(sh, 0.66, 1.3, c['glow'], part=c.get('face', 'Glow_Warm_1'))
    stem(c, 0.0, 1.74, 0.0, h=0.32, r=0.09)


# --- The snowman ------------------------------------------------------------------------------------

def snowball(c, r, cy, n=12, rings=7, floor=False):
    """A ball of snow centred at cy; `floor`: cut flat where it meets the floor (y 0), a little drift round it."""
    if not floor:
        sphere('Body', (0, cy, 0), r, c['snow'], n=n, rings=rings)
        return
    prof = []
    for i in range(rings + 1):
        a = -math.pi / 2 + math.pi * i / rings
        prof.append((r * math.cos(a), cy + r * math.sin(a)))
    prof = [(math.sqrt(max(r * r - cy * cy, 0)), 0.0)] + [p for p in prof if p[1] > 0.02]
    prof = [(0.0, 0.0)] + prof[:-1] + [(0.0, cy + r)]
    lathe('Body', prof, c['snow'], n=n)
    lathe('Body', [(0.0, 0.0), (r * 1.04, 0.0), (r * 0.98, 0.1), (r * 0.8, 0.2), (0.0, 0.2)], c['shade'], n=n)


def coal(x, y, z, r, c):
    sphere('Body', (x, y, z), (r, r, r * 0.8), c['coal'], n=6, rings=4)


def on_ball(r, cy, ax, ay, sink=0.04):
    """The point on a ball's front (-Z) at angles ax (right), ay (up), degrees, sunk `sink` into it."""
    ax, ay = math.radians(ax), math.radians(ay)
    rr = r - sink
    return (rr * math.cos(ay) * math.sin(ax), cy + rr * math.sin(ay), -rr * math.cos(ay) * math.cos(ax))


def snow_face(c, r, cy):
    for sx in (-1, 1):
        coal(*on_ball(r, cy, sx * 22, 18), 0.075 * r / 0.5, c)
    for k in range(5):
        coal(*on_ball(r, cy, -32 + 16 * k, -24 - 7 * math.cos(math.radians(-32 + 16 * k) * 2.8)), 0.05 * r / 0.5, c)
    p = on_ball(r, cy, 0, 0, sink=0.08)
    rod('Body', p, (p[0], p[1] - 0.03, p[2] - 0.4), 0.09, c['carrot'], n=6, r1=0.01)


def twig_arm(c, sx, a, b):
    rod('Body', a, b, 0.05, c['twig'], n=5, r1=0.03)
    m = [(a[i] * 0.3 + b[i] * 0.7) for i in range(3)]
    rod('Body', m, (m[0] + sx * 0.02, m[1] + 0.28, m[2]), 0.035, c['twig'], n=4, r1=0.02)
    rod('Body', b, (b[0] - sx * 0.12, b[1] + 0.2, b[2]), 0.03, c['twig'], n=4, r1=0.015)


def scarf(c, y, r, tail_x, ball, drop):
    """A scarf round the neck at y (ring radius r), a cream stripe, and its tail laid down the front of `ball`
    (radius, centre y) at x tail_x for `drop`, a cream band at its end."""
    lathe('Body', [(r - 0.1, y - 0.1), (r + 0.06, y - 0.12), (r + 0.08, y + 0.1), (r - 0.08, y + 0.12)],
          c['scarf'], n=12, closed=True)
    lathe('Body', [(r - 0.06, y - 0.03), (r + 0.1, y - 0.04), (r + 0.1, y + 0.04), (r - 0.06, y + 0.04)],
          c['scarf2'], n=12, closed=True)
    br, bcy = ball

    def surf(yy, out):
        s = math.sqrt(max(br * br - (yy - bcy) ** 2 - tail_x ** 2, 0.0))
        return -(s - 0.04) - out
    ys = [y - 0.04 - drop * i / 6 for i in range(7)]
    inner = [(surf(yy, 0.0), yy) for yy in ys]
    outer = [(surf(yy, 0.11), yy) for yy in reversed(ys)]
    prism('Body', inner + outer, tail_x - 0.14, tail_x + 0.14, c['scarf'], plane='zy')
    ye = ys[-1]
    band = [(surf(ye + 0.02, -0.01), ye + 0.02), (surf(ye + 0.12, -0.01), ye + 0.12),
            (surf(ye + 0.12, 0.125), ye + 0.12), (surf(ye + 0.02, 0.125), ye + 0.02)]
    prism('Body', band, tail_x - 0.15, tail_x + 0.15, c['scarf2'], plane='zy')


def snowman_a(c):
    """A: three balls, a top hat with a band, coal eyes and smile, a carrot, a scarf, twig arms raised."""
    snowball(c, 0.98, 0.84, n=14, rings=9, floor=True)          # 0 .. 1.82; finer (blind review: coarse facets)
    snowball(c, 0.7, 2.26)                                      # 1.56 .. 2.96
    snowball(c, 0.5, 3.28)                                      # 2.78 .. 3.78
    for k in range(3):
        coal(*on_ball(0.7, 2.26, 0, 28 - 26 * k), 0.07, c)
    snow_face(c, 0.5, 3.28)
    scarf(c, 2.86, 0.4, -0.2, (0.7, 2.26), 0.75)
    cyl('Body', (0, 3.66, 0), 0.56, 0.07, c['hat'], n=14)       # the brim
    cyl('Body', (0, 3.71, 0), 0.37, 0.79, c['hat'], n=14)
    cyl('Body', (0, 3.75, 0), 0.385, 0.14, c['band'], n=14)
    for sx in (-1, 1):
        twig_arm(c, sx, (sx * 0.6, 2.4, 0.0), (sx * 1.04, 3.2, -0.05))


def snowman_b(c):
    """B: two big balls, a knitted bobble hat, a long scarf, coal eyes and smile, a carrot, twig arms out."""
    snowball(c, 1.04, 0.92, floor=True)                         # 0 .. 1.96
    snowball(c, 0.72, 2.5)                                      # 1.78 .. 3.22
    for k in range(3):
        coal(*on_ball(1.04, 0.92, 0, 36 - 24 * k), 0.08, c)
    snow_face(c, 0.72, 2.46)
    scarf(c, 1.9, 0.46, -0.3, (1.04, 0.92), 0.85)
    lathe('Body', [(0.0, 2.84), (0.62, 2.84), (0.68, 2.92), (0.66, 3.1), (0.58, 3.14), (0.0, 3.14)], c['band'], n=14)
    lathe('Body', [(0.0, 3.1), (0.56, 3.1), (0.5, 3.4), (0.36, 3.75), (0.18, 4.05), (0.0, 4.16)], c['hat'], n=14)
    sphere('Body', (0, 4.28, 0), (0.2, 0.2, 0.2), c['band'], n=8, rings=5)
    for sx in (-1, 1):
        twig_arm(c, sx, (sx * 0.75, 1.5, 0.0), (sx * 1.05, 2.5, -0.1))


# --- Beginning and finishing a piece ----------------------------------------------------------------

def ev_decor(id_):
    """Begin Decor_<id_> on 1 x 1 Floor (its Pieces row; a silhouette _A/_B on its piece's), nothing floating."""
    base = id_.split('_')[0]
    K.pieces_decor()
    if id_ != base:
        K._PIECES[id_] = dict(K._PIECES[base])
    p = K.decor(id_, 1, 1, 'Floor')
    p.checks.append(grounded_check)
    return p


def edone(note):
    rec = finish(note=note)
    return rec


GC = {'leg': 'stone_dark', 'metal': 'stone', 'body': 'stone_dark', 'trim': 'stone', 'film': 'black',
      'top': 'stone', 'glow': 'white', 'skin': 'grey', 'groove': 'stone_dark', 'stem': 'stone_dark',
      'stem_dark': 'black', 'snow': 'white', 'shade': 'stone', 'coal': 'black', 'carrot': 'stone_dark',
      'twig': 'stone_dark', 'scarf': 'grey', 'scarf2': 'stone', 'hat': 'black', 'band': 'grey', 'face': 'Body'}

PJ = {'leg': 'wood_dark', 'metal': 'iron', 'body': 'black', 'trim': 'gold', 'film': 'wood_dark', 'top': 'wood',
      'glow': 'lamp'}
EV = {'skin': 'pumpkin', 'groove': 'pumpkin_dark', 'stem': 'stem', 'stem_dark': 'stem_dark', 'glow': 'flame',
      'snow': 'snow', 'shade': 'snow_shade', 'coal': 'coal', 'carrot': 'carrot', 'twig': 'twig', 'scarf': 'scarf',
      'scarf2': 'scarf_light', 'hat': 'hat', 'band': 'scarf'}

BUILD = {'Projector': {'A': projector_a, 'B': projector_b}, 'JackOLantern': {'A': lantern_a, 'B': lantern_b},
         'Snowman': {'A': snowman_a, 'B': snowman_b}}
CHOSEN = {'Projector': 'A', 'JackOLantern': 'A', 'Snowman': 'A'}
NOTES = {
    'Projector_A': 'A: a projector on a tripod stand, two reels on top, the lens to the front',
    'Projector_B': 'B: the same projector on a little wooden cart with a shelf of film cans',
    'JackOLantern_A': 'A: one big carved pumpkin, triangle eyes and a toothy grin',
    'JackOLantern_B': 'B: a carved pumpkin stacked on a squat plain one',
    'Snowman_A': 'A: three balls, a top hat, a scarf, twig arms raised',
    'Snowman_B': 'B: two big balls, a knitted bobble hat, a long scarf',
}
FINAL_NOTES = {
    'Projector': 'a Haunted Manor film projector: a black housing with a gold band on a dark-wood tripod stand with '
                 'iron feet and yoke, a gold lens barrel to the front (its glass Glow_Warm_1), a crank on the right, '
                 'two iron reels of film on arms above, their tops at 4.5',
    'JackOLantern': 'a jack-o\'-lantern: an orange pumpkin of eight lobes over dark grooves, a carved face of '
                    'triangle eyes, a nose and a grin with two teeth lit from inside (Glow_Warm_1), a bent green stem',
    'Snowman': 'a snowman of three snowballs on a little drift, a black top hat with a red band, coal eyes, smile '
               'and buttons, a carrot nose, a red and cream scarf, twig arms raised',
}


def sil(kind, k):
    i = f'{kind}_{k}'
    if kind == 'Projector':
        no_spots(i)
        BUILD[kind][k](GC, lens='Body')
        sdone2(NOTES[i])
    else:
        ev_decor(i)
        BUILD[kind][k](GC)                          # grey: the face in the body (no glow colour)
        edone(NOTES[i])


def chosen(kind):
    k = CHOSEN[kind]
    if kind == 'Projector':
        no_spots(kind)
        BUILD[kind][k](PJ)
        return sdone2(FINAL_NOTES[kind])
    ev_decor(kind)
    BUILD[kind][k](EV)
    return edone(FINAL_NOTES[kind])


# --- Review (Workbench on light grey; no EEVEE or Cycles) -------------------------------------------

def name_of(i):
    return ('Furniture_' if i.startswith('Projector') else 'Decor_') + i


def lay(fbx, recs, ids, labels=False, gap=4.4, ang=0):
    x = 0.0
    for i in ids:
        n = name_of(i)
        size = recs[n]['root']['size']
        cx = x + size[0] / 2
        place(fbx(n), n, (cx, 0, 0), ang)
        _squares(cx, size, ang)
        _REV['_person'](Vector((cx + size[0] / 2 + 2.1, 0, 0)), 0.0)
        if labels:
            _label(i.replace('_', ' '), cx + 1.0, -4.5, size=0.7)
        x += size[0] + gap
    return x


def silhouette_sheet(out, fbxdir, recs):
    ids = [f'{k}_{o}' for k in BUILD for o in 'AB']
    shots = []
    clear()
    x = lay(lambda n: fbxdir, recs, ids, labels=True)
    _REV['_block']('floor', (-3, -0.3, -6), (x + 2, -0.07, 3), (150, 150, 156))
    shots.append(render(out / 'silhouettes_game.png', (-0.35, 1.0, -1.0), (1800, 560), (-2, 0, -5.5), (x, 5.2, 2),
                        scale=1.0))
    clear()
    lay(lambda n: fbxdir, recs, ids)
    shots.append(render(out / 'silhouettes_front.png', (0.0, 0.0, -1.0), (1800, 300), (-2, -0.3, -2), (x, 5.3, 2),
                        scale=1.0))
    return shots


def cinema_with_projector(ctx, fbx, recs_ctx):
    """The screen on a wall, two rows facing it with a sitter on every spot, the projector behind them facing the
    screen (its front, -Z, toward +Z: turned 180 as the rows are), a person beside it."""
    place(ctx, 'Furniture_FilmScreen', (0, 0, 0))
    _REV['_block']('wall', (-7, 0, 1.12), (7, 9, 1.5), (196, 186, 200))
    for z in (-6.0, -12.0):
        place(ctx, 'Furniture_CinemaSeat', (0, 0, z), 180)
        people(recs_ctx['Furniture_CinemaSeat'], 0.0, z, 180)
    place(fbx, 'Furniture_Projector', (0, 0, -16.5), 180)
    _REV['_person'](Vector((2.6, 0, 0)), -16.5)
    _REV['_block']('floor', (-8, -0.3, -19.5), (8, -0.07, 1.5), (150, 150, 156))


def review_projector(out, fbx, ctx, recs_ctx):
    n = 'Furniture_Projector'
    shots = []
    lo, hi = (-2.0, 0, -2.0), (4.5, 5.2, 2.0)

    def alone():
        clear()
        place(fbx, n, (0, 0, 0))
        _squares(0.0, (3, 0.2, 3))
        _REV['_person'](Vector((2.6, 0, 0)), 0.0)
        _REV['_block']('floor', (-3, -0.3, -3), (5, -0.07, 3), (150, 150, 156))
    alone()
    shots.append(render(out / '1_game_camera.png', (-0.45, 1.28, -1.0), (1000, 800), lo, hi, scale=1.05))
    shots.append(render(out / '2_front_three_quarter.png', (-0.7, 0.35, -1.0), (1000, 800), lo, hi, scale=1.05))
    shots.append(render(out / '3_back_three_quarter.png', (0.7, 0.45, 1.0), (1000, 800), lo, hi, scale=1.05))
    clear()
    place(fbx, n, (0, 0, 0))
    _squares(0.0, (3, 0.2, 3))
    place(fbx, n, (6.0, 0, 0), 90)
    _squares(6.0, (3, 0.2, 3))
    _REV['_person'](Vector((9.6, 0, 0)), 0.0)
    shots.append(render(out / '4_front_and_side_level.png', (0.0, 0.0, -1.0), (1200, 600), (-2, -0.3, -2),
                        (11.6, 5.3, 2), scale=1.03))
    clear()
    place(fbx, n, (0, 0, 0))
    shots.append(render(out / '5_close_top.png', (-0.5, 0.75, -0.8), (900, 800), (-1.2, 2.3, -1.2), (1.2, 4.6, 1.2),
                        scale=1.05))
    clear()
    cinema_with_projector(ctx, fbx, recs_ctx)
    shots.append(render(out / '6_cinema_game_camera.png', (-0.45, 1.28, -1.0), (1400, 1000), (-7, 0, -19),
                        (7, 8, 1.5), scale=1.02))
    shots.append(render(out / '7_cinema_from_the_projector.png', (-0.2, 0.32, -1.0), (1400, 900), (-7, 0, -19),
                        (7, 8, 1.5), scale=1.02))
    return shots


def review_event(out, fbx, recs):
    ids = ['JackOLantern', 'Snowman']
    shots = []

    def scene(ang=0):
        clear()
        x = lay(lambda n: fbx, recs, ids, ang=ang)
        _REV['_block']('floor', (-3, -0.3, -3.5), (x + 2, -0.07, 3), (150, 150, 156))
        return x
    x = scene()
    lo, hi = (-2, 0, -2), (x, 5.2, 2)
    shots.append(render(out / '1_game_camera.png', (-0.45, 1.28, -1.0), (1300, 800), lo, hi, scale=1.04))
    shots.append(render(out / '2_front_three_quarter.png', (-0.7, 0.35, -1.0), (1300, 800), lo, hi, scale=1.04))
    shots.append(render(out / '3_back_three_quarter.png', (0.7, 0.45, 1.0), (1300, 800), lo, hi, scale=1.04))
    shots.append(render(out / '4_front_level.png', (0.0, 0.0, -1.0), (1300, 600), (-2, -0.3, -2), (x, 5.3, 2),
                        scale=1.03))
    x = scene(90)
    shots.append(render(out / '5_side_level.png', (0.0, 0.0, -1.0), (1300, 600), (-2, -0.3, -2), (x, 5.3, 2),
                        scale=1.03))
    clear()
    place(fbx, 'Decor_JackOLantern', (0, 0, 0))
    place(fbx, 'Decor_Snowman', (3.4, 0, 0))
    shots.append(render(out / '6_close_faces.png', (-0.25, 0.25, -1.0), (1200, 800), (-1.3, 0, -1.3), (4.7, 4.6, 1.3),
                        scale=1.04))
    return shots


# --- The sets ---------------------------------------------------------------------------------------

def report(out, built, title):
    val = json.loads((out / 'validation.json').read_text())
    bad = {n: r.get('faults') for n, r in val['pieces'].items() if not r['ok']}
    print(f'SET {title}: {built}; validation faults in {bad}', flush=True)
    print('TRIS', {n: r.get('triangles') for n, r in val['pieces'].items()}, flush=True)
    return val, bad


def main():
    if MODE == 'grey':
        K.use_palette(HM_PALETTE)
        K.IMPORT_CHECKS = False         # drafts with _A/_B ids, not for import
        K.start_set(SET_P + '/silhouettes')
        for kind in BUILD:
            for k in 'AB':
                sil(kind, k)
        recs = {p.name: r for p, r, _ in K.BUILT}
        out = K.ROOT / 'blender' / SET_P / 'silhouettes'
        (out / 'manifest.json').write_text(json.dumps({'pieces': recs}, indent=1))
        print('SILHOUETTE TRIS', {p.name: r.get('triangles') for p, r, _ in K.BUILT}, flush=True)
        if not K.NOPREVIEW:
            print('SHEETS', silhouette_sheet(out / 'review', out / 'fbx', recs), flush=True)
        return
    if MODE == 'projector':
        K.use_palette(HM_PALETTE)
        # The Cinema's screen and row, only to stand beside the projector in the pictures (context/, not for import).
        K.start_set(SET_P + '/context')
        film_screen()
        cinema_seat()
        recs_ctx = {p.name: r for p, r, _ in K.BUILT}
        K.BUILT.clear()
        K.start_set(SET_P)
        chosen('Projector')
        built = [p.name for p, _, _ in K.BUILT]
        K.end_set('Haunted Manor: the Cinema\'s projector (GDD A.13)', [(built, 3.0, 1.0)], sheet=False)
        out = K.ROOT / 'blender' / SET_P
        manifest = json.loads((out / 'manifest.json').read_text())
        val, bad = report(out, built, SET_P)
        val['spots'] = {n: 'no visitors\' spots (none wanted: guests watch from the seats); neither Use nor Use_<n>'
                        for n in built}
        val['grounded'] = {n: 'grounded_check on the built and the re-imported triangles: every shell stands on the '
                              'floor or touches one that does' for n in built}
        val['pieces_rows'] = {n: {k: ROWS['Projector'][k] for k in ('w', 'd', 'layer', 'height')}
                              | {'model_top': manifest['pieces'][n]['furniture']['model_top'], 'row': 'as main'}
                              for n in built}
        val['not_validated'] = val.get('not_validated', [])[:1] + [
            'the lens lit (Workbench draws Glow_Warm_1 unlit)', 'the projector beside the Cinema\'s real screen and '
            'seats in Studio (reviewed beside them rebuilt by their script into context/)']
        (out / 'validation.json').write_text(json.dumps(val, indent=1))
        if not K.NOPREVIEW:
            print('SHEETS', review_projector(out / 'review', out / 'fbx', out / 'context' / 'fbx', recs_ctx),
                  flush=True)
    else:
        K.use_palette(EV_PALETTE)
        K.start_set(SET_E)
        for kind in ('JackOLantern', 'Snowman'):
            chosen(kind)
        built = [p.name for p, _, _ in K.BUILT]
        K.end_set('Event decor: the Jack-o\'-Lantern and the Snowman (every location; GDD §8.2)', [(built, 3.0, 1.0)],
                  sheet=False)
        out = K.ROOT / 'blender' / SET_E
        manifest = json.loads((out / 'manifest.json').read_text())
        val, bad = report(out, built, SET_E)
        val['grounded'] = {n: 'grounded_check on the built and the re-imported triangles: every shell stands on the '
                              'floor or touches one that does' for n in built}
        pieces = K.pieces_decor()
        val['pieces_rows'] = {n: {k: pieces[n[len('Decor_'):]][k] for k in ('w', 'd', 'layer', 'height')}
                              | {'row': 'as main'} for n in built}
        val['not_validated'] = val.get('not_validated', [])[:1] + [
            'the face lit (Workbench draws Glow_Warm_1 unlit)', 'placement by the build mode in Studio']
        (out / 'validation.json').write_text(json.dumps(val, indent=1))
        if not K.NOPREVIEW:
            print('SHEETS', review_event(out / 'review', out / 'fbx', manifest['pieces']), flush=True)
    if bad:
        raise SystemExit(f'VALIDATION FAULTS: {list(bad)}')


try:
    main()
except K.Refused as e:
    print(str(e), flush=True)
    raise SystemExit('REFUSED')
