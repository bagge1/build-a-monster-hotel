"""Six smaller Poolside and Fitness pieces for Haunted Manor's kit (GDD A.13.2, the Indoor and Outdoor Pool and the
Gym rows; A.13.3, the Poolside and Fitness sets), matching the Pool and Gym sets built the same night.

    Furniture_Parasol       a parasol on a stone base: a bat-wing canopy of crimson and black panels on an iron
                            pole; no visitors' spots
    Furniture_PoolLadder    1 x 1: steps up to a pool's coping (its back, +Z, toward the pool); no visitors' spots
    Furniture_DivingBoard   1 x 2: a springboard, its tip at the front (-Z, toward the pool); no visitors' spots
    Furniture_DumbbellRack  2 x 1: dumbbells on a rack; Use_1 `Lift` placed as `Stand`, on the left front square
                            (src/server/ActivityKit.luau's blockout: front(-1.5))
    Furniture_ExerciseMat   1 x 2, `Rug`: a mat on the floor (0.15 at most); Use_1 `Lift` placed as `Lie`, on it
    Furniture_WallMirror    2 x 1, `Wall`: a tall mirror stood against the wall; no visitors' spots

The contract is MODELS.md, "Decor", "Furniture" and "Activity furniture: visitors' spots", as for the Pool and the
Gym: the 0.4 inset (a Rug's body to its footprint's edge instead), at most 7 tall (a Rug 0.15), `Body` not
colliding, no coplanar faces, nothing floats (a Wall piece may hang: hung_check), a Wall piece's back on the wall's
plane. The spots are the blockout's (ActivityKit.luau: the rack's and the mat's `Lift`, none on the others), held by
the one spot validator (tools/build_activity_bar.py's spots_check: a Lift by the Lie or Stand it names). Definitions
from tools/build_activity_billiards.py (wfurn's pattern, kdone, hung_check, and through it the karaoke, bar and
built-rooms kit), run without their mains.

The rows are on main's Pieces.luau; the kit's Pieces check runs against them, except where ROW_CHANGES below
proposes a change (README, "The Pieces rows"). Its own set, blender/rooms/haunted_manor_extras/; the models belong
in HotelKit.HauntedManor.

    blender -b -t 4 --python-exit-code 1 -P tools/build_activity_extras.py [-- grey] [-- nopreview]

`-- grey` writes the grey silhouettes (two options a piece, ids _A/_B, not for import) to
blender/rooms/haunted_manor_extras/silhouettes/. Otherwise the chosen six are built in the Manor's palette; review/
gets Workbench sheets only (Studio is running: no EEVEE or Cycles).
"""
import ast
import json
import math
from pathlib import Path

_BI = Path(__file__).resolve().parent / 'build_activity_billiards.py'
_tree = ast.parse(_BI.read_text(encoding='utf8'))
_tree.body = [n for n in _tree.body if not isinstance(n, ast.Try)]          # its main() call
NS = {'__file__': str(_BI), '__name__': 'build_activity_billiards'}
exec(compile(_tree, str(_BI), 'exec'), NS)
globals().update({k: v for k, v in NS.items() if not k.startswith('__')})

SET = 'rooms/haunted_manor_extras'
GREY = 'grey' in K.ARGS

# A row this set proposes to change (README): the parasol on 2 x 2, its canopy wide enough to shade a person.
ROW_CHANGES = {'Parasol': {'w': 2, 'd': 2}}
MAIN_ROWS = {k: dict(ROWS[k]) for k in ('Parasol', 'PoolLadder', 'DivingBoard', 'DumbbellRack', 'ExerciseMat',
                                        'WallMirror')}


def xfurn(id_, spots=False, row=None):
    """Begin Furniture_<id_> on its Pieces.luau row, or `row`'s changes to it (a silhouette _A/_B on its
    piece's); spots_check when it has spots; hung_check for every piece (it is grounded_check but on a Wall)."""
    base = id_.split('_')[0]
    r = dict(ROWS[base]) | (row or {})
    ROWS[id_] = r
    K.pieces_decor()
    K._PIECES[id_] = {k: r[k] for k in ('w', 'd', 'layer', 'height')} | {'always': False}
    p = furn(id_)
    p.checks.remove(use_check)
    p.checks.remove(grounded_check)
    p.checks.append(hung_check)
    if spots:
        p.checks.append(spots_check)
    p.spots = {}
    p.lift = {}
    return p


def lift_spot(n, pos, look, how):
    """A `Lift` spot placed as `how` (Lie or Stand; MODELS.md); spots_check holds it to that pose's checks."""
    spot(n, pos, look, 'Lift')
    K.P.lift[f'Use_{n}'] = how


def xdone(note):
    rec = kdone(note)
    if K.P.lift:
        rec['furniture']['lift_placed_as'] = dict(K.P.lift)
    return rec


def path_rod(part, pts, r, col, n=6, joints=True):
    """A rod along 3-D points, a ball at every bend so it reads as one bent tube. Its segments are turned half a
    facet by turns: two segments in one plane otherwise share a side facet's plane (coplanar, the kit refuses)."""
    for k, (a, b) in enumerate(zip(pts, pts[1:])):
        a, b = Vector(a), Vector(b)
        d = b - a
        lathe(part, [(r, 0.0), (r, d.length)], col, n=n, phase=(math.pi / n if k % 2 == 0 else 0.0),
              m=Matrix.Translation(a) @ d.to_track_quat('Y', 'Z').to_matrix().to_4x4())
    if joints:
        for q in pts[1:-1]:
            sphere(part, q, r, col, n=n, rings=3)


def vring(part, outer, inner, z0, z1, col):
    """A flat ring in the (x, y) plane between two outlines of as many points, z0..z1 thick (a frame round a
    pane): one closed solid."""
    k = len(outer)
    assert len(inner) == k
    verts = ([Vector((x, y, z0)) for x, y in outer] + [Vector((x, y, z1)) for x, y in outer]
             + [Vector((x, y, z0)) for x, y in inner] + [Vector((x, y, z1)) for x, y in inner])
    faces = []
    for i in range(k):
        j = (i + 1) % k
        faces += [(i, j, k + j, k + i), (2 * k + j, 2 * k + i, 3 * k + i, 3 * k + j),
                  (i, 2 * k + i, 2 * k + j, j), (k + i, k + j, 3 * k + j, 3 * k + i)]
    K._add(part, verts, faces, col)


# --- The parasol ------------------------------------------------------------------------------------------

def canopy(c, R, rim, apex, scallop=0.84, lift=0.22):
    """A bat-wing canopy: eight panels, each a closed wedge from the apex to two rib tips (R, at `rim`), its
    edge drawn up and in between them (scallop x R, `lift` higher); the panels crimson and black by turns.
    A shell about 0.06 thick at the rim, 0.2 at the apex, domed a little; returns the rib tips."""
    def ring(r, y, a):
        return Vector((r * math.cos(a), y, r * math.sin(a)))
    tips = []
    for k in range(8):
        dirs = [k * math.pi / 4, k * math.pi / 4 + math.pi / 8, (k + 1) * math.pi / 4]
        rim_r = [R, R * scallop, R]
        rim_y = [rim, rim + lift, rim]
        o_mid = [ring(0.5 * rr, apex - (apex - ry) * 0.38, a) for rr, ry, a in zip(rim_r, rim_y, dirs)]
        o_rim = [ring(rr, ry, a) for rr, ry, a in zip(rim_r, rim_y, dirs)]
        i_mid = [v - Vector((0, 0.11, 0)) for v in o_mid]
        i_rim = [v - Vector((0, 0.06, 0)) for v in o_rim]
        verts = [Vector((0, apex, 0)), Vector((0, apex - 0.2, 0))] + o_mid + o_rim + i_mid + i_rim
        faces = [(0, 2, 3), (0, 3, 4), (2, 5, 6, 3), (3, 6, 7, 4),
                 (1, 9, 8), (1, 10, 9), (8, 9, 12, 11), (9, 10, 13, 12),
                 (5, 11, 12, 6), (6, 12, 13, 7),
                 (0, 1, 8, 11, 5, 2), (0, 4, 7, 13, 10, 1)]
        K._add('Body', verts, faces, c['canopy'] if k % 2 == 0 else c['canopy2'])
        tips.append((o_rim[0], i_mid[0], i_rim[0]))
    return tips


def parasol(c, R, rim, base_r, top=6.95):
    """The parasol: a stone base, an iron pole into the canopy's apex, a gold finial, eight struts from a gold
    runner to the ribs, a gold bead under each rib tip."""
    lathe('Body', [(base_r, 0.0), (base_r, 0.16), (base_r * 0.78, 0.3), (0.24, 0.42), (0.0, 0.45)], c['base'], n=8)
    apex = top - 0.33
    cyl('Body', (0, 0.3, 0), 0.12, apex - 0.36, c['pole'], n=8)       # review 1: thicker
    tips = canopy(c, R, rim, apex)
    sphere('Body', (0, apex + 0.04, 0), 0.14, c['finial'], n=8, rings=4)
    cyl('Body', (0, apex + 0.1, 0), 0.06, top - apex - 0.1, c['finial'], n=6, r_top=0.0)
    ry = rim - 1.1 * R / 2.58 - 0.1
    cyl('Body', (0, ry - 0.1, 0), 0.13, 0.22, c['finial'], n=8)
    for o_rim, i_mid, i_rim in tips:
        q = i_mid.lerp(i_rim, 0.25)
        d = Vector((q.x, 0.0, q.z)).normalized()
        seg('Body', (d.x * 0.12, ry, d.z * 0.12), tuple(q), 0.045, c['strut'], n=4)   # review 1: thicker
        t = o_rim * ((R - 0.08) / R)
        sphere('Body', (t.x, rim - 0.1, t.z), 0.07, c['finial'], n=6, rings=3)


def parasol_a(c):
    """A: on the row's 1 x 1: the canopy 2.16 across (the 0.4 inset), its rim at 5.7."""
    parasol(c, 1.08, 5.7, 0.55)


def parasol_b(c):
    """B: on 2 x 2: the canopy 5.16 across, its rim at 5.95 (0.95 over a person's head; blind review 1: at 5.5
    it read as at head height)."""
    parasol(c, 2.58, 5.95, 0.75)


# --- The pool ladder: steps up to the coping (the pool behind, +Z) ---------------------------------------

COPE = 0.86                     # the Pool's coping (tools/build_activity_pool.py RIM_TOP): the top step's height


def ladder_a(c):
    """A: a pointed-arch iron step ladder: two side arches (front and back legs meeting in a point at 2.9),
    two wood treads up the front and two down the back, the top tread at the coping's height."""
    for sx in (-1, 1):
        x = sx * 0.85
        # arch_points gives (x, y) along the arch from one spring to the other: here its x is z
        pts = [(x, 0.03, -0.95)] + [(x, y, z) for z, y in arch_points(-0.95, 0.95, 1.2, 2.88, n=4)] + \
              [(x, 0.03, 0.95)]
        path_rod('Body', pts, 0.07, c['rail'])
        for z in (-0.95, 0.95):
            cyl('Body', (x, 0.0, z), 0.14, 0.06, c['foot'], n=8)
    for z0, z1 in ((-1.06, -0.7), (0.7, 1.06)):
        for y in (COPE / 2, COPE):
            span('Body', (-0.8, y - 0.1, z0), (0.8, y, z1), c['tread'], bevel=0.03)


def ladder_b(c):
    """B: two stone steps to the coping's height, two iron handrails: newel posts at the front with gold
    finials, the rail running back over the top step and turning down at its back edge (over the coping)."""
    prism('Body', [(-1.0, 0.0), (1.0, 0.0), (1.0, COPE), (0.0, COPE), (0.0, COPE / 2), (-1.0, COPE / 2)], -1.0, 1.0,
          {'top': c['stone2'], 'rest': c['stone']}, plane='zy')
    for sx in (-1, 1):
        x = sx * 0.88
        cyl('Body', (x, COPE / 2 - 0.02, -0.8), 0.11, 2.2 - COPE / 2, c['rail'], n=8)
        sphere('Body', (x, 2.3, -0.8), 0.15, c['foot'], n=8, rings=4)
        cyl('Body', (x, 2.4, -0.8), 0.08, 0.58, c['foot'], n=6, r_top=0.0)
        # Blind review 1: thicker (0.06 vanished on a phone); the rail's end iron, not a gold drop (a lantern).
        path_rod('Body', [(x, 2.05, -0.8), (x, 2.5, 0.2), (x, 2.58, 0.62), (x, 2.4, 0.88), (x, 1.85, 0.98)],
                 0.09, c['rail'])
        sphere('Body', (x, 1.85, 0.98), 0.09, c['rail'], n=6, rings=3)


# --- The diving board: its tip at the front (-Z), toward the pool ----------------------------------------

BOARD_Y = 2.0                   # the board's top: over the coping (0.86) and the pool's finials (1.45); blind review
                                # 1: at 1.3 it read as a bench at knee height


def board(c, z_back, y=BOARD_Y, w=0.55, t=0.14):
    """The board: a plank from z_back to the tip at -2.58, its tip rounded; its top a darker tread."""
    tip = -2.58
    pts = [(-w, z_back), (w, z_back), (w, tip + 0.35)] + \
          [(w * math.cos(a), tip + 0.35 - 0.35 * math.sin(a)) for a in (math.radians(d) for d in (30, 60, 90, 120, 150))] + \
          [(-w, tip + 0.35)]
    prism('Body', pts, y - t, y, {'top': c['board_top'], 'rest': c['board']}, plane='xz')


def board_a(c):
    """A: a springboard: a stone stair of two steps at the back to a platform at the board's height, the board
    on it and on an iron pointed-arch trestle (its fulcrum), two iron handrails beside the steps."""
    top = BOARD_Y - 0.14
    span('Body', (-1.0, 0.0, 1.0), (1.0, top, 1.98), c['stone'], bevel=0.04)                 # the platform
    span('Body', (-0.95, 0.0, 1.96), (0.95, top * 2 / 3, 2.3), c['stone2'], bevel=0.04)      # two steps
    span('Body', (-0.9, 0.0, 2.28), (0.9, top / 3, 2.6), c['stone'], bevel=0.04)
    board(c, 1.9)
    tre = [(-0.62, 0.0), (-0.3, 0.0)] + arch_points(-0.3, 0.3, 0.25, 0.75, n=3) + [(0.3, 0.0), (0.62, 0.0),
                                                                                   (0.45, BOARD_Y - 0.14), (-0.45, BOARD_Y - 0.14)]
    prism('Body', tre, -0.75, -0.55, c['frame'], plane='xy')
    for sx in (-1, 1):
        x = sx * 0.86
        path_rod('Body', [(x, 0.03, 2.48), (x, 2.85, 2.48), (x, 3.13, 2.2), (x, 3.15, 1.55), (x, 2.7, 1.15),
                          (x, BOARD_Y - 0.12, 1.05)], 0.09, c['rail'])


def board_b(c):
    """B: the plank: a dark board on a stone pier pierced by a pointed arch, its back end on the pier, iron
    straps across it; a three-rung iron ladder up the pier's back, its stiles hooped over at 2.9."""
    y = BOARD_Y + 0.25
    pts = [(0.9, 0.0), (1.3, 0.0)] + arch_points(1.3, 2.0, 0.35, 0.95, n=3) + \
          [(2.0, 0.0), (2.4, 0.0), (2.4, y - 0.14), (0.9, y - 0.14)]
    prism('Body', pts, -0.7, 0.7, c['stone'], plane='zy')
    board(c, 2.35, y=y)
    for z in (-1.6, 0.9):
        span('Body', (-0.58, y - 0.16, z - 0.06), (0.58, y + 0.02, z + 0.06), c['frame'])
    for sx in (-1, 1):
        x = sx * 0.45
        path_rod('Body', [(x, 0.03, 2.45), (x, 2.6, 2.45), (x, 2.86, 2.25), (x, 2.7, 1.95), (x, y, 1.9)], 0.06,
                 c['rail'])
    for k in range(3):
        rod_x('Body', -0.45, 0.45, 0.4 + k * 0.4, 2.45, 0.04, c['rail'], n=6)


# --- The dumbbell rack --------------------------------------------------------------------------------------

def dumbbell(c, x, y, z, r, half=0.42, col=None):
    """A hex dumbbell along Z (the rack's depth): two six-sided heads, a handle between them."""
    col = col or c['bell']
    for s in (-1, 1):
        z0 = z + s * half - (0.18 if s > 0 else 0.0)
        # phase 0: a flat face down, the head resting on the rails (its centre 0.866 r over them)
        lathe('Body', [(r, 0.0), (r, 0.18)], col, n=6, m=at((x, y, z0), rx=90), phase=0.0)
    cyl('Body', (0, 0, 0), 0.06, 2 * half - 0.3, c['handle'], n=6, m=at((x, y, z - half + 0.15), rx=90))


def rod_x(part, x0, x1, y, z, r, col, n=8):
    cyl(part, (0, 0, 0), r, x1 - x0, col, n=n, m=at((x0, y, z), rz=-90))


def rack_a(c):
    """A: a two-tier iron rack: end frames (a short front post, a tall back post with a gold finial, a foot),
    two rails a tier, five hex dumbbells a tier, larger on the low front tier."""
    for sx in (-1, 1):
        x = sx * 2.42
        # Blind review 1: every member thicker and the dumbbells larger (a smudge of dots on a phone).
        span('Body', (x - 0.12, 0.0, -1.0), (x + 0.12, 0.14, 1.0), c['rack'], bevel=0.03)
        span('Body', (x - 0.1, 0.14, -0.7), (x + 0.1, 1.48, -0.48), c['rack'])
        span('Body', (x - 0.1, 0.14, 0.4), (x + 0.1, 2.42, 0.62), c['rack'])
        seg('Body', (x, 1.3, -0.59), (x, 2.0, 0.42), 0.08, c['rack'])                      # a brace
        sphere('Body', (x, 2.52, 0.51), 0.14, c['finial'], n=8, rings=4)
        cyl('Body', (x, 2.6, 0.51), 0.08, 0.4, c['finial'], n=6, r_top=0.0)
        # each tier's bracket from the end frame's post, carrying its two rails
        span('Body', (x - 0.07, 1.34, -0.9), (x + 0.07, 1.46, 0.0), c['rack'])
        span('Body', (x - 0.07, 2.28, 0.06), (x + 0.07, 2.4, 0.86), c['rack'])
    for y, zs in ((1.42, (-0.78, -0.12)), (2.36, (0.18, 0.74))):
        for z in zs:
            rod_x('Body', -2.37, 2.37, y, z, 0.07, c['rack'], n=6)
    xs = (-1.8, -0.9, 0.0, 0.9, 1.8)
    for k, x in enumerate(xs):
        r = 0.3 + 0.02 * k
        dumbbell(c, x, 1.49 + r * 0.866, -0.45, r, col=c['bell'])
        r = 0.22 + 0.02 * k
        dumbbell(c, x, 2.43 + r * 0.866, 0.46, r, half=0.36, col=c['bell2'])
    lift_spot(1, (-1.5, 0.0, -3.0), (0, 0, 1), 'Stand')


def rack_b(c):
    """B: a dark-wood cabinet rack: a low cabinet with two pointed-arch panels, five dumbbells across its top
    in a row, a pointed-arch backboard behind them with two gold finials at its corners."""
    span('Body', (-2.5, 0.0, -0.9), (2.5, 1.2, 0.8), c['wood'], bevel=0.04)
    for cx in (-1.25, 1.25):
        prism('Body', lifted(gothic(cx - 0.9, cx + 0.9, 0.45, 0.85), 0.15), -0.93, -0.9, c['panel'], plane='xy')
    prism('Body', [(-2.45, 0.0), (2.45, 0.0), (2.45, 2.2)] + [(x, y) for x, y in reversed(
        arch_points(-2.45, 2.45, 2.2, 2.75, n=4))][1:-1] + [(-2.45, 2.2)], 0.8, 1.05, c['wood'], plane='xy')
    for sx in (-1, 1):
        sphere('Body', (sx * 2.35, 2.32, 0.92), 0.12, c['finial'], n=8, rings=4)
        cyl('Body', (sx * 2.35, 2.4, 0.92), 0.07, 0.58, c['finial'], n=6, r_top=0.0)
    for k, x in enumerate((-1.9, -0.95, 0.0, 0.95, 1.9)):
        r = 0.22 + 0.025 * k
        dumbbell(c, x, 1.2 + r * 0.86, -0.1, r)
    lift_spot(1, (-1.5, 0.0, -3.0), (0, 0, 1), 'Stand')


# --- The exercise mat (Rug: 0.15 at most, to its footprint's edge) -----------------------------------------

MAT_TOP = 0.1


def mat_outline(hx, hz, ch):
    return [(hx, hz - ch), (hx - ch, hz), (-hx + ch, hz), (-hx, hz - ch), (-hx, -hz + ch), (-hx + ch, -hz),
            (hx - ch, -hz), (hx, -hz + ch)]


def mat_a(c):
    """A: one mat with a border: a field 0.09 thick inside a border band 0.1, a gold crescent at the foot end."""
    ring_prism('Body', mat_outline(1.5, 3.0, 0.15), mat_outline(1.22, 2.72, 0.08), 0.0, MAT_TOP, c['border'],
               c['border'], c['border'])
    prism('Body', mat_outline(1.22, 2.72, 0.08), 0.0, MAT_TOP - 0.01, c['mat'], plane='xz')
    out = [(0.42 * math.cos(math.radians(a)), 0.42 * math.sin(math.radians(a))) for a in range(40, 330, 32)]
    inn = [(0.16 + 0.34 * math.cos(math.radians(a)), 0.34 * math.sin(math.radians(a))) for a in range(300, 50, -32)]
    prism('Body', [(x, z - 2.05) for x, z in out + inn], MAT_TOP - 0.02, MAT_TOP + 0.005, c['motif'], plane='xz')
    lift_spot(1, (0.0, MAT_TOP - 0.01, 0.0), (0, 0, -1), 'Lie')


def mat_b(c):
    """B: a folding mat: three bevelled panels with black seams between them."""
    for z0, z1 in ((-3.0, -1.04), (-0.96, 0.96), (1.04, 3.0)):
        span('Body', (-1.5, 0.0, z0), (1.5, MAT_TOP, z1), c['mat'], bevel=0.03)
    for z in (-1.0, 1.0):
        span('Body', (-1.47, 0.0, z - 0.05), (1.47, 0.06, z + 0.05), c['seam'])
    lift_spot(1, (0.0, MAT_TOP, 0.0), (0, 0, -1), 'Lie')


# --- The wall mirror (Wall: its back on z = 1.1) ----------------------------------------------------------

def framed(c, x0, x1, y0, spring, apex, border=0.3, lip=0.1, sheen=False, dz=0.0):
    """One pointed-arch mirror on the wall: a dark-wood backboard (z 0.9..1.1), a wood moulding proud of it
    (to z 0.75), a gold lip inside it (to 0.8), the pane (its face at 0.86); `dz` sets all but the backboard's
    back that much nearer the wall (two frames side by side never share a face's plane)."""
    n = 4
    o1 = gothic(x0, x1, spring, apex, n=n)
    o2 = gothic(x0 + border, x1 - border, spring - border * 0.5, apex - border * 1.2, n=n)
    o3 = gothic(x0 + border + lip, x1 - border - lip, spring - border * 0.5 - lip * 0.5,
                apex - border * 1.2 - lip * 1.3, n=n)
    o2 = [(x, y + border) if y == 0.0 else (x, y) for x, y in o2]
    o3 = [(x, y + border + lip) if y == 0.0 else (x, y) for x, y in o3]
    o1, o2, o3 = (lifted(o, y0) for o in (o1, o2, o3))
    prism('Body', o1, 0.9 + dz, 1.1, c['mframe'], plane='xy')
    vring('Body', o1, o2, 0.75 + dz, 0.9 + dz, c['mframe'])
    vring('Body', o2, o3, 0.8 + dz, 0.9 + dz, c['gilt'])
    prism('Body', o3, 0.86 + dz, 0.9 + dz, c['glass'], plane='xy')
    if sheen:       # diagonal light bands on the pane (off: from the game camera they read as scratches, taste.md)
        xa, xb = x0 + border + lip + 0.25, x1 - border - lip - 0.25
        bands = ((0.0, 0.32), (0.55, 0.14)) if xb - xa > 1.2 else ((0.0, 0.16),)
        ya = y0 + border + lip + 0.8
        for off, wd in bands:
            L = min((spring - border - lip) * 0.28, xb - xa - off - wd)
            p = [(xa + off, ya), (xa + off + wd, ya), (xa + off + wd + L, ya + L), (xa + off + L, ya + L)]
            prism('Body', p, 0.85 + dz, 0.86 + dz, c['sheen'], plane='xy')
    return o1


def mirror_a(c):
    """A: one tall pointed-arch mirror stood on a plinth against the wall, a gold finial on its point."""
    span('Body', (-2.2, 0.0, 0.62), (2.2, 0.32, 1.1), c['mframe'], bevel=0.04)
    framed(c, -2.0, 2.0, 0.3, 4.6, 6.15)
    cyl('Body', (0, 6.05, 1.0), 0.09, 0.45, c['gilt'], n=6, r_top=0.0)


def mirror_b(c):
    """B: a triptych: a tall pointed-arch mirror between two shorter ones, on one plinth against the wall."""
    span('Body', (-2.55, 0.0, 0.62), (2.55, 0.32, 1.1), c['mframe'], bevel=0.04)
    framed(c, -0.85, 0.85, 0.3, 4.75, 6.45, border=0.22, lip=0.08)
    for sx in (-1, 1):
        x0, x1 = sorted((sx * 0.87, sx * 2.5))
        framed(c, x0, x1, 0.3, 3.9, 5.2, border=0.22, lip=0.08, dz=0.03)


# --- The options ------------------------------------------------------------------------------------------

BUILD = {'Parasol': {'A': parasol_a, 'B': parasol_b}, 'PoolLadder': {'A': ladder_a, 'B': ladder_b},
         'DivingBoard': {'A': board_a, 'B': board_b}, 'DumbbellRack': {'A': rack_a, 'B': rack_b},
         'ExerciseMat': {'A': mat_a, 'B': mat_b}, 'WallMirror': {'A': mirror_a, 'B': mirror_b}}
SPOTS = {'DumbbellRack', 'ExerciseMat'}
SIL_ROWS = {('Parasol', 'B'): {'w': 2, 'd': 2}}

GC = {'canopy': 'grey', 'canopy2': 'stone_dark', 'pole': 'stone_dark', 'base': 'stone', 'finial': 'stone',
      'strut': 'stone_dark', 'rail': 'stone_dark', 'foot': 'stone', 'tread': 'grey', 'stone': 'stone',
      'stone2': 'grey', 'board': 'grey', 'board_top': 'stone_dark', 'frame': 'stone_dark', 'rack': 'stone_dark',
      'bell': 'grey', 'bell2': 'grey', 'handle': 'stone', 'wood': 'grey', 'panel': 'stone', 'border': 'stone_dark',
      'mat': 'grey', 'motif': 'stone', 'seam': 'black', 'mframe': 'stone_dark', 'gilt': 'stone', 'glass': 'white',
      'sheen': 'grey'}

NOTES = {'Parasol_A': 'A: 1 x 1 (the row): a bat-wing canopy 2.16 across on an iron pole, a stone base',
         'Parasol_B': 'B: 2 x 2: the same canopy 5.16 across, its rim 0.5 over a person\'s head',
         'PoolLadder_A': 'A: a pointed-arch iron step ladder, two treads up and two down, the top at the coping',
         'PoolLadder_B': 'B: two stone steps to the coping, iron handrails from newel posts turning down over it',
         'DivingBoard_A': 'A: a springboard on a stone stair and platform, an iron arch fulcrum, two handrails',
         'DivingBoard_B': 'B: a plank on two stone piers pierced by pointed arches, a hooped ladder at the back',
         'DumbbellRack_A': 'A: a two-tier iron rack, five hex dumbbells a tier, gold finials on the back posts',
         'DumbbellRack_B': 'B: a dark-wood cabinet, five dumbbells on top, a pointed-arch backboard',
         'ExerciseMat_A': 'A: one mat with a border band and a gold crescent at the foot end',
         'ExerciseMat_B': 'B: a folding mat, three bevelled panels with black seams',
         'WallMirror_A': 'A: one tall pointed-arch mirror on a plinth, a gold finial',
         'WallMirror_B': 'B: a triptych, a tall pointed-arch mirror between two shorter ones'}


def sil(kind, k):
    xfurn(f'{kind}_{k}', spots=kind in SPOTS, row=SIL_ROWS.get((kind, k)))
    BUILD[kind][k](GC)
    xdone(NOTES[f'{kind}_{k}'])


# --- The chosen six, in the Manor's dress -----------------------------------------------------------------

HM = {'canopy': 'crimson', 'canopy2': 'black', 'pole': 'iron', 'base': 'stone', 'finial': 'gold', 'strut': 'iron',
      'rail': 'iron', 'foot': 'gold', 'tread': 'wood', 'stone': 'stone', 'stone2': 'stone_dark', 'board': 'wood',
      'board_top': 'plum', 'frame': 'iron', 'rack': 'iron', 'bell': 'black', 'bell2': 'black', 'handle': 'gold',
      'wood': 'wood_dark', 'panel': 'crimson', 'border': 'crimson', 'mat': 'plum', 'motif': 'gold',
      'seam': 'black', 'mframe': 'wood_dark', 'gilt': 'gold', 'glass': 'moon', 'sheen': 'lavender'}

CHOSEN = {'Parasol': 'B', 'PoolLadder': 'B', 'DivingBoard': 'A', 'DumbbellRack': 'A', 'ExerciseMat': 'A',
          'WallMirror': 'A'}
FINAL_NOTES = {
    'Parasol': 'a Haunted Manor parasol: a bat-wing canopy of crimson and black panels on an iron pole, a gold '
               'finial, gold beads under the rib tips, iron struts from a gold runner, a stone base',
    'PoolLadder': 'Haunted Manor pool steps: two stone steps up to the coping\'s height, iron handrails from newel '
                  'posts with gold finials, running back over the top step and turning down over the pool',
    'DivingBoard': 'a Haunted Manor springboard: a wood board with a plum tread on a stone platform and step, an '
                   'iron pointed-arch fulcrum, iron handrails beside the step',
    'DumbbellRack': 'a Haunted Manor dumbbell rack: iron end frames with gold finials, two tiers of black hex '
                    'dumbbells with gold handles, larger on the low front tier',
    'ExerciseMat': 'a Haunted Manor exercise mat: a plum mat inside a crimson border band, a gold crescent at the '
                   'foot end',
    'WallMirror': 'a Haunted Manor wall mirror: a tall pointed-arch mirror in a dark-wood frame with a gold lip, on '
                  'a plinth against the wall, a gold finial on its point'}


def chosen(kind):
    k = CHOSEN[kind]
    xfurn(kind, spots=kind in SPOTS, row=ROW_CHANGES.get(kind))
    BUILD[kind][k](HM)
    rec = xdone(FINAL_NOTES[kind])
    rec['furniture']['option'] = k
    if kind in ROW_CHANGES:
        rec['furniture']['pieces_row'] = f'proposed: {ROW_CHANGES[kind]} (main\'s Pieces.luau differs; README)'
    return rec


# --- Review (Workbench on light grey: Studio is running, no EEVEE or Cycles) -------------------------------

POOL_RGB, WATER_RGB = (130, 125, 140), (40, 150, 150)


def pool_standin(x0, x1, z0, z1):
    """A stand-in for the Pool (not this set's): its rim walls to the coping's 0.86, its water at 0.72."""
    _REV['_block']('rim', (x0, 0, z0), (x1, COPE, z0 + 0.5), POOL_RGB)
    _REV['_block']('rim', (x0, 0, z1 - 0.5), (x1, COPE, z1), POOL_RGB)
    _REV['_block']('rim', (x0, 0, z0 + 0.5), (x0 + 0.5, COPE, z1 - 0.5), POOL_RGB)
    _REV['_block']('rim', (x1 - 0.5, 0, z0 + 0.5), (x1, COPE, z1 - 0.5), POOL_RGB)
    _REV['_block']('water', (x0 + 0.5, 0, z0 + 0.5), (x1 - 0.5, 0.72, z1 - 0.5), WATER_RGB)


def people(rec, cx, cz=0.0):
    lift = rec['furniture'].get('lift_placed_as', {})
    for a, pose in rec['furniture']['spots'].items():
        u = rec['attachments'][a]
        p = (cx + u['pos'][0], u['pos'][1], cz + u['pos'][2])
        if pose == 'Lie' or lift.get(a) == 'Lie':
            _lying(p, u['look'])
        else:
            _REV['_person'](Vector((p[0], p[1], 0)), p[2])


def squares(cx, cz, size):
    for a in range(int(round(size[0] / 3))):
        for b in range(int(round(size[2] / 3))):
            x0, z0 = cx - size[0] / 2 + 3 * a, cz - size[2] / 2 + 3 * b
            shade = (205, 205, 210) if (a + b) % 2 else (185, 185, 192)
            _REV['_block']('sq', (x0 + 0.03, -0.06, z0 + 0.03), (x0 + 2.97, -0.01, z0 + 2.97), shade)


def lay_row(fbx, recs, names, zback, labels, pool=False, wallrow=False, gap=4.6, tag=None):
    """Each piece with its back edge on z = zback, on its squares, a person on its spots and one beside it;
    the pool row with a pool stand-in behind (the ladders' backs and the boards' tips toward it), the gym row
    against a wall."""
    x = 0.0
    for n in names:
        size = recs[n]['root']['size']
        cx, cz = x + size[0] / 2, zback - size[2] / 2
        ang = 180 if 'DivingBoard' in n and pool else 0
        place(fbx, n, (cx, 0, cz), ang)
        squares(cx, cz, size)
        people(recs[n], cx, cz)
        if not recs[n]['furniture']['spots']:
            _REV['_person'](Vector((cx + size[0] / 2 + 2.3, 0, 0)), zback - 1.6)
        if labels:
            _label((tag or {}).get(n, n.split('_', 1)[1].replace('_', ' ')), cx, zback - 9.0, size=0.8)
        x += size[0] + gap
    if pool:
        pool_standin(-2, x, zback + 0.8, zback + 6.8)
    if wallrow:
        _REV['_block']('wall', (-2, 0, zback - 0.4), (x, 8.0, zback), WALL_RGB)
    return x


def silhouette_sheet(out, fbx, recs):
    pool_ids = [f'Furniture_{k}_{o}' for k in ('Parasol', 'PoolLadder', 'DivingBoard') for o in 'AB']
    gym_ids = [f'Furniture_{k}_{o}' for k in ('DumbbellRack', 'ExerciseMat', 'WallMirror') for o in 'AB']
    shots = []
    clear()
    x = max(lay_row(fbx, recs, pool_ids, 0.0, True, pool=True), lay_row(fbx, recs, gym_ids, 22.0, True,
                                                                         wallrow=True))
    _REV['_block']('floor', (-3, -0.3, -11), (x + 2, -0.07, 23), (150, 150, 156))
    shots.append(render(out / 'silhouettes_game.png', (-0.35, 1.25, -1.0), (1700, 1100), (-2, 0, -10), (x, 7.0, 22),
                        scale=1.0))
    for k, ids in enumerate((pool_ids, gym_ids), 1):
        clear()
        x = lay_row(fbx, recs, ids, 0.0, False, pool=k == 1, wallrow=k == 2)
        shots.append(render(out / f'silhouettes_front_{k}.png', (-0.2, 0.12, -1.0), (1700, 520), (-2, -0.3, -7),
                            (x, 7.2, 0.5), scale=1.02))
    return shots


NAMES = ['Furniture_Parasol', 'Furniture_PoolLadder', 'Furniture_DivingBoard', 'Furniture_DumbbellRack',
         'Furniture_ExerciseMat', 'Furniture_WallMirror']


def poolside(fbx):
    """A poolside: the pool stand-in (12 x 6, as the Pool's 4 x 2), the steps on the square in front of it, the
    springboard at its left end pointing in, the parasol at its front right with a person under it."""
    clear()
    pool_standin(-5.6, 5.6, -2.6, 2.6)
    place(fbx, NAMES[1], (-1.5, 0, -4.5))
    place(fbx, NAMES[2], (-9.0, 0, 0.0), -90)
    place(fbx, NAMES[0], (9.0, 0, -4.5))
    _REV['_person'](Vector((9.0, 0, 0)), -6.2)          # under the canopy, 1.7 in front of the pole
    _REV['_person'](Vector((-1.5, 0, 0)), -7.6)
    _REV['_block']('floor', (-13, -0.3, -10), (13, -0.07, 4), (150, 150, 156))


def gym(fbx, recs):
    """A gym's wall: the mirror on it, the rack beside it with its lifter on the spot, the mat in front of the
    mirror with a person lying on it."""
    clear()
    place(fbx, NAMES[5], (0, 0, 0))
    place(fbx, NAMES[3], (-6.0, 0, 0))
    people(recs[NAMES[3]], -6.0)
    place(fbx, NAMES[4], (0.0, 0, -4.5))
    people(recs[NAMES[4]], 0.0, -4.5)
    _REV['_person'](Vector((4.5, 0, 0)), -2.5)
    _REV['_block']('wall', (-10, 0, 1.1), (7, 8.0, 1.5), WALL_RGB)
    _REV['_block']('floor', (-10, -0.3, -10), (7, -0.07, 1.5), (150, 150, 156))


def review_final(out, fbx, recs):
    shots = []
    poolside(fbx)
    shots.append(render(out / '1_poolside_game_camera.png', (-0.45, 1.28, -1.0), (1400, 850), (-12.5, 0, -9),
                        (12.5, 7.0, 3), scale=1.0))
    gym(fbx, recs)
    shots.append(render(out / '2_gym_game_camera.png', (-0.45, 1.28, -1.0), (1400, 850), (-9.5, 0, -8),
                        (6.5, 7.0, 1.5), scale=1.0))
    # All six at floor level from the front, then from behind (anything floating shows the background).
    clear()
    x = 0.0
    for n in NAMES:
        size = recs[n]['root']['size']
        cx = x + size[0] / 2
        place(fbx, n, (cx, 0, 0))
        _squares(cx, size)
        x += size[0] + 2.0
    _REV['_block']('wall', (x - 2.0 - 6.0 - 0.2, 0, 1.1), (x - 1.8, 8.0, 1.5), WALL_RGB)
    _REV['_person'](Vector((x + 0.5, 0, 0)), 0.0)
    shots.append(render(out / '3_front_level.png', (0.0, 0.0, -1.0), (1600, 560), (-1.5, -0.3, -3.5),
                        (x + 2.5, 7.2, 3.5), scale=1.02))
    shots.append(render(out / '4_back_three_quarter.png', (0.7, 0.5, 1.0), (1600, 800), (-1.5, 0, -3.5),
                        (x + 2.5, 7.2, 3.5), scale=1.02))
    # Close up: the steps and the springboard at the pool, from a guest's height a little to one side.
    poolside(fbx)
    shots.append(render(out / '5_close_poolside.png', (-0.75, 0.45, -0.8), (1200, 800), (-12.2, 0, -6.2),
                        (0.5, 3.2, 2.0), scale=1.0))
    gym(fbx, recs)
    shots.append(render(out / '6_close_gym.png', (-0.55, 0.35, -1.0), (1200, 800), (-9.2, 0, -7.6), (2.8, 6.8, 1.2),
                        scale=1.0))
    return shots


# --- The set ------------------------------------------------------------------------------------------------

def main():
    K.use_palette(HM_PALETTE)
    if GREY:
        K.IMPORT_CHECKS = False         # drafts with _A/_B ids, not for import
        K.start_set(SET + '/silhouettes')
        for kind in BUILD:
            for k in 'AB':
                sil(kind, k)
        recs = {p.name: r for p, r, _ in K.BUILT}
        out = K.ROOT / 'blender' / SET / 'silhouettes'
        (out / 'manifest.json').write_text(json.dumps({'pieces': recs}, indent=1))
        bad = {p.name: r.get('faults') for p, r, _ in K.BUILT if r.get('faults')}
        print('SILHOUETTE FAULTS', bad, flush=True)
        print('SILHOUETTE TRIS', {p.name: r.get('triangles') for p, r, _ in K.BUILT}, flush=True)
        if not K.NOPREVIEW:
            print('SHEETS', silhouette_sheet(out / 'review', out / 'fbx', recs), flush=True)
        return
    K.start_set(SET)
    for kind in BUILD:
        chosen(kind)
    built = [p.name for p, _, _ in K.BUILT]
    K.end_set('Haunted Manor: Poolside and Fitness extras (parasol, pool steps, springboard, dumbbell rack, '
              'exercise mat, wall mirror; GDD A.13)', [(built, 3.0, 1.0)], sheet=False)
    out = K.ROOT / 'blender' / SET
    manifest = json.loads((out / 'manifest.json').read_text())
    patch_fixup(out / 'import_fixup.luau', manifest)
    val = json.loads((out / 'validation.json').read_text())
    val['spots'] = {n: {'spots': r['furniture']['spots'], 'lift_placed_as': r['furniture'].get('lift_placed_as', {}),
                        'checked': ('spots_check on the built and the re-imported triangles: Use_<n> from 1 '
                                    'without a gap, a Pose from MODELS.md\'s list, level, no two on a square; '
                                    'Lift held to the placement it names: the rack\'s Stand on the floor at the '
                                    'left front square\'s middle 1.5 in front, facing +Z, its square free; the '
                                    'mat\'s Lie on its surface with nothing over it and the lying 5-stud person '
                                    '(lie_faults) in the footprint, on the piece, nothing rising through it')
                        if r['furniture']['spots'] else
                        'no visitors\' spots (ActivityKit.luau: spots = none)'}
                    for n, r in manifest['pieces'].items()}
    val['hung'] = {n: ('hung_check on the built and the re-imported triangles: every shell stands on the floor or '
                       'touches one that does (a Wall piece: the wall\'s plane at z = 3fd/2 - 0.4 counts as one '
                       'that does)') for n in built}
    val['pieces_rows'] = {n: {k: ROWS[n[len('Furniture_'):]][k] for k in ('w', 'd', 'layer', 'height', 'keyFor')}
                          | {'model_top': manifest['pieces'][n]['furniture']['model_top'],
                             'main_row': {k: MAIN_ROWS[n[len('Furniture_'):]][k] for k in ('w', 'd')}
                             if n[len('Furniture_'):] in ROW_CHANGES else 'as main'}
                          for n in built}
    val['row_changes'] = {'note': 'the kit\'s Pieces check ran against these (main\'s Pieces.luau differs): the '
                                  'row must change before import, or the model',
                          **{f'Furniture_{k}': v for k, v in ROW_CHANGES.items()}}
    val['height_findings'] = {
        'note': 'Pieces.luau\'s height against the model\'s top, a finding (not refused): the row must say it',
        **{n: FINDINGS[n] for n in built if n in FINDINGS}}
    val['not_validated'] = val.get('not_validated', [])[:1] + [
        'the attachments and each Use_<n> Pose attribute exist only in manifest.json until import_fixup.luau makes '
        'them', 'a visitor walking to a spot, lifting at the rack or on the mat: no walker or clip has run',
        'the steps and the springboard beside the real Pool model (reviewed beside a stand-in of its rim and water)',
        'a Wall piece on a real wall in Studio, turned to each of the four walls by the build mode']
    (out / 'validation.json').write_text(json.dumps(val, indent=1))
    if not K.NOPREVIEW:
        print('SHEETS', review_final(out / 'review', out / 'fbx', manifest['pieces']), flush=True)
    bad = {n: r.get('faults') for n, r in val['pieces'].items() if not r['ok']}
    print(f'SET {SET}: {built}; validation faults in {bad}', flush=True)
    print('TRIS', {n: r.get('triangles') for n, r in val['pieces'].items()}, flush=True)
    print('HEIGHTS', {n: manifest['pieces'][n]['furniture']['model_top'] for n in built}, flush=True)
    if bad:
        raise SystemExit(f'VALIDATION FAULTS: {list(bad)}')


try:
    main()
except K.Refused as e:
    print(str(e), flush=True)
    raise SystemExit('REFUSED')
