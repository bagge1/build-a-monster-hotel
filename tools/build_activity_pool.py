"""The Indoor Pool's two first pieces for Haunted Manor's kit (GDD A.13.2, the Indoor Pool row; A.13.3, Poolside).

    Furniture_Pool          a pool on the floor: a basin walled by a step-over rim (its coping at 0.86; the floor
                            cannot be dug), one `Water` part, a gargoyle spout on the back rim (its stream `Jet_1`),
                            gothic tiles; Use_1..Use_n `Swim`, one a square, each inside the inner edge by 1.5
    Furniture_Lounger       1 x 2 squares: a poolside lounger laid flat (a Lie pose is flat, 2026-10-21); Use_1 `Lie`

The contract is MODELS.md, "Furniture" and "Activity furniture: visitors' spots", as for the Bar and the Cinema
(tools/build_activity_bar.py, whose definitions this runs: bfurn's pattern, spot, spots_check with its Lie and Swim
branches, sdone, loft, patch_fixup, _label, and through it tools/build_built_rooms.py's kit). A pool's water is one
part, `Water` (not colliding; the code makes it water), and a spout's falling stream is `Jet_1` (MODELS.md, "Decor":
a fountain's falling streams are Jet_<n>). spots_check holds each Swim spot to the water's top and to 1.5 clear of
the rim, the spout and the stream round it; where the swimmer's body then reaches against the floor (its middle
1.5 under the surface) is a finding in validation.json `swim_findings`, not a refusal.

Its own set, blender/rooms/haunted_manor_pool/; the models belong in HotelKit.HauntedManor.

    blender -b -t 4 --python-exit-code 1 -P tools/build_activity_pool.py [-- grey] [-- nopreview]

`-- grey` writes the grey silhouettes (three options a piece, ids _A/_B/_C, not for import) to
blender/rooms/haunted_manor_pool/silhouettes/. Otherwise the chosen two are built in the Manor's palette; review/
gets Workbench sheets only (Studio is running).
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

SET = 'rooms/haunted_manor_pool'
GREY = 'grey' in K.ARGS

# The Pieces rows these need (the code branch's rows say Pool 3 x 2 height 1.5, Lounger 1 x 2 height 2.0: README).
PENDING.update({
    'Pool': {'w': 4, 'd': 2, 'layer': 'Floor', 'height': 3.15, 'location': 0, 'keyFor': ['IndoorPool']},
    'Lounger': {'w': 1, 'd': 2, 'layer': 'Floor', 'height': 2.12, 'location': 0, 'keyFor': []},
})

RIM_TOP = 0.86                  # the coping's top: low enough to step over (0.6 to 1.0)
COPE_Y0 = 0.70                  # its underside; the wall under it reaches 0.74 (buried in it)
WATER_TOP = 0.72                # the water 0.14 under the coping, as a pool's is
RIM_T = 0.5                     # the wall, outer face to inner
COPE_IN, COPE_OUT = 0.06, 0.05  # the coping's overhang into the pool and over the wall's outer face
FLOOR_T = 0.06                  # the basin's floor slab
SQ2 = 2 - math.sqrt(2)          # an octagon's chamfer shrinks by this times an inward offset


def pfurn(id_, w=None, d=None):
    """Begin Furniture_<id_> on its pending row (a silhouette's own w x d); its spots replace `Use`."""
    row = dict(PENDING[id_.split('_')[0]])
    if w:
        row['w'], row['d'] = w, d
    ROWS[id_] = row
    K.pieces_decor()
    K._PIECES.setdefault(id_, {k: row[k] for k in ('w', 'd', 'layer', 'height')} | {'always': False})
    p = furn(id_)
    p.checks.remove(use_check)
    p.checks.append(spots_check)
    p.spots = {}
    return p


def outline(hx, hz, c=0.0):
    """A rectangle +-hx, +-hz in (x, z), its corners cut by c (an octagon), counter-clockwise from +X."""
    if c <= 0:
        return [(hx, hz), (-hx, hz), (-hx, -hz), (hx, -hz)]
    return [(hx, hz - c), (hx - c, hz), (-hx + c, hz), (-hx, hz - c), (-hx, -hz + c), (-hx + c, -hz),
            (hx - c, -hz), (hx, -hz + c)]


def inset(c, t):
    return 0.0 if c <= 0 else max(c - SQ2 * t, 0.02)


def cone(part, a, b, r, col, n=4):
    a, b = Vector(a), Vector(b)
    d = b - a
    cyl(part, (0, 0, 0), r, d.length, col, n=n, r_top=0.0,
        m=Matrix.Translation(a) @ d.to_track_quat('Y', 'Z').to_matrix().to_4x4())


def basin(c, w, d, chamfer=0.0):
    """The pool's basin: the floor slab, the wall ring (0..0.74), the coping (0.70..0.86) and the `Water`; returns
    (OX, OZ, EX, EZ): the body's outer half sizes and the coping's inner edge (the pool's inner edge)."""
    OX, OZ = 1.5 * w - 0.4, 1.5 * d - 0.4
    IX, IZ = OX - RIM_T, OZ - RIM_T
    EX, EZ = IX - COPE_IN, IZ - COPE_IN
    prism('Body', outline(IX + 0.02, IZ + 0.02, inset(chamfer, RIM_T - 0.02)), 0.0, FLOOR_T, c['floor'], plane='xz')
    ring_prism('Body', outline(OX - COPE_OUT, OZ - COPE_OUT, inset(chamfer, COPE_OUT)),
               outline(IX, IZ, inset(chamfer, RIM_T)), 0.0, COPE_Y0 + 0.04, c['wall'], c['lining'], c['wall'])
    ring_prism('Body', outline(OX, OZ, chamfer), outline(EX, EZ, inset(chamfer, RIM_T + COPE_IN)), COPE_Y0, RIM_TOP,
               c['cope'], c['cope'], c['cope'])
    declare('Water', False)
    prism('Water', outline(IX + 0.02, IZ + 0.02, inset(chamfer, RIM_T - 0.02)), 0.04, WATER_TOP, c['water'],
          plane='xz')
    return OX, OZ, EX, EZ


def gargoyle(c, OZ, wings=True):
    """A stone gargoyle crouched on a pier across the back rim's middle, leaning out over the water, its stream
    (`Jet_1`) falling from its open mouth to the water 1.5 inside the body's back edge."""
    span('Body', (-0.42, 0.0, OZ - 0.47), (0.42, 1.55, OZ - 0.02), c['pier'])      # inside the wall (reviews 1, 2)
    span('Body', (-0.5, 1.53, OZ - 0.72), (0.5, 1.7, OZ - 0.01), c['cope'], bevel=0.04)
    g = c['gargoyle']
    sphere('Body', (0, 2.04, OZ - 0.36), (0.42, 0.38, 0.36), g, n=8, rings=5)          # the haunches
    sphere('Body', (0, 2.16, OZ - 0.68), (0.32, 0.34, 0.28), g, n=8, rings=5)          # the chest, leaning out
    sphere('Body', (0, 2.38, OZ - 0.98), (0.27, 0.25, 0.27), g, n=8, rings=5)          # the head
    span('Body', (-0.17, 2.3, OZ - 1.36), (0.17, 2.46, OZ - 1.08), g, bevel=0.03)      # the upper jaw, the snout
    span('Body', (-0.14, 2.07, OZ - 1.27), (0.14, 2.16, OZ - 1.06), g)      # the lower jaw, open
    for sx in (-1, 1):
        cone('Body', (sx * 0.15, 2.52, OZ - 0.96), (sx * 0.3, 2.95, OZ - 0.82), 0.07, g)   # horns
        seg('Body', (sx * 0.2, 1.7, OZ - 0.64), (sx * 0.2, 2.1, OZ - 0.7), 0.09, g)        # forelegs
        sphere('Body', (sx * 0.2, 1.74, OZ - 0.62), (0.11, 0.06, 0.1), g, n=6, rings=3)   # paws on the cap (review 2)
        if wings:       # folded bat wings, their points behind the shoulders
            x0, x1 = sorted((sx * 0.28, sx * 0.4))
            prism('Body', [(OZ - 0.78, 2.22), (OZ - 0.46, 2.6), (OZ - 0.3, 3.15), (OZ - 0.12, 2.8),
                           (OZ - 0.06, 2.05), (OZ - 0.22, 2.2), (OZ - 0.38, 1.98), (OZ - 0.55, 2.14)],
                  x0, x1, g, plane='zy')
    declare('Jet_1', False)
    # One lofted tube through horizontal sections, the mouth to under the water's top (segments of rods met
    # with their side facets in one plane: coplanar, 2026-10-26).
    # Tapered, widening as it falls, and ending on a splash ring on the water (the first blind review: a uniform
    # rod with a capped end under the surface read as a pipe).
    path = [(WATER_TOP + 0.01, OZ - 1.32, 0.15), (1.15, OZ - 1.32, 0.13), (1.62, OZ - 1.31, 0.11),
            (2.02, OZ - 1.27, 0.1), (2.22, OZ - 1.17, 0.09)]   # its top between the jaws (review 3)
    loft('Jet_1', [(y, [(r * math.cos(math.pi * k / 4), z + r * math.sin(math.pi * k / 4)) for k in range(8)])
                   for y, z, r in path], c['jet'])
    lathe('Jet_1', [(0.1, WATER_TOP + 0.005), (0.27, WATER_TOP + 0.005), (0.2, WATER_TOP + 0.06),
                    (0.1, WATER_TOP + 0.045)], c['jet'], n=10, base=(0, 0, OZ - 1.32), closed=True)


def finials(c, OX, OZ):
    """A short stone post with a pyramid cap on each corner of the coping."""
    for sx in (-1, 1):
        for sz in (-1, 1):
            x, z = sx * (OX - 0.24), sz * (OZ - 0.24)
            span('Body', (x - 0.21, RIM_TOP - 0.02, z - 0.21), (x + 0.21, 1.45, z + 0.21), c['cope'])
            cyl('Body', (x, 1.43, z), 0.33, 0.5, c['cope'], n=4, r_top=0.0)


def tiles(c, OX, OZ, skip_back=0.7):
    """Gothic encaustic tiles: a row of lozenges 0.02 proud of the wall's outer faces, under the coping."""
    y, hy, hw, step = 0.36, 0.22, 0.2, 0.9
    wx, wz = OX - COPE_OUT, OZ - COPE_OUT
    for half, along, face in ((wx, 'x', wz), (wz, 'z', wx)):
        n = int((2 * half - 0.5) // step) + 1
        for i in range(n):
            u = (i - (n - 1) / 2) * step
            for s in (-1, 1):
                if along == 'x' and s > 0 and abs(u) < skip_back:
                    continue            # the pier stands there
                col = c['tile'] if i % 2 == 0 else c.get('tile2', c['tile'])
                pts = [(u - hw, y), (u, y - hy), (u + hw, y), (u, y + hy)]
                a0, a1 = sorted((s * (face - 0.01), s * (face + 0.02)))
                prism('Body', pts, a0, a1, col, plane='xy' if along == 'x' else 'zy')


def floor_motif(c, IX, IZ):
    """On the basin's floor: a border of darker tiles round the lining."""
    ring_prism('Body', outline(IX + 0.01, IZ + 0.01), outline(IX - 0.35, IZ - 0.35), FLOOR_T - 0.01, FLOOR_T + 0.015,
               c['border'], c['border'], c['border'])
    # The eight-pointed star in the middle went: two blind reviews read it, through the water, as a stray polygon.


def swim_spots(pts):
    for k, (x, z) in enumerate(pts):
        spot(k + 1, (x, WATER_TOP, z), (0, 0, -1), 'Swim')


# --- The pools: three options (their footprints differ: README, "Why 4 x 2") -------------------------

def pool_a(c, dress=False):
    """A: 3 x 2 (GDD A.13.2's size): a plain rectangle, the gargoyle on the back rim's middle. The inner edge's 1.5
    leaves the swimmers a strip 4.1 x 1.1 down the middle: two swimmers 4 apart."""
    OX, OZ, EX, EZ = basin(c, 3, 2)
    gargoyle(c, OZ)
    swim_spots([(-2.0, -0.5), (2.0, -0.5)])


def pool_b(c, dress=False):
    """B: 4 x 2, a lap pool: the rectangle, a finial post on each corner, the gargoyle on the back rim's middle;
    three swimmers 3.5 apart down its length."""
    OX, OZ, EX, EZ = basin(c, 4, 2)
    gargoyle(c, OZ)
    finials(c, OX, OZ)
    if dress:
        tiles(c, OX, OZ)
        floor_motif(c, OX - RIM_T, OZ - RIM_T)
    swim_spots([(-3.5, -0.52), (0.0, -0.52), (3.5, -0.52)])


def pool_c(c, dress=False):
    """C: 3 x 3, an octagonal basin (a cloister's fountain basin), the gargoyle on the back facet; four swimmers
    4 apart, one in each corner square."""
    OX, OZ, EX, EZ = basin(c, 3, 3, chamfer=1.2)
    gargoyle(c, OZ)
    swim_spots([(-2.0, -2.0), (2.0, -2.0), (-2.0, 2.0), (2.0, 2.0)])


# --- The loungers -------------------------------------------------------------------------------------

LIE_Y = 1.1                     # the cushion's top, where the guest lies (a lounger's, under a bed's 2)


def lounger_a(c, dress=False):
    """A: a wooden deck lounger on four legs: a slatted frame, a long cushion raised into a head rest at the head
    (+Z) end, a pointed-arch board behind it."""
    for x in (-0.88, 0.88):
        for z in (-2.3, 2.3):
            span('Body', (x - 0.12, 0, z - 0.12), (x + 0.12, 0.68, z + 0.12), c['frame'])
    for x0, x1 in ((-1.1, -0.92), (0.92, 1.1)):
        span('Body', (x0, 0.6, -2.6), (x1, 0.88, 2.6), c['frame'])
    span('Body', (-0.94, 0.66, -2.55), (0.94, 0.8, 2.48), c['slat'])
    span('Body', (-0.95, 0.78, -2.5), (0.95, LIE_Y, 1.3), c['cushion'], bevel=0.08)
    # The head rest: the cushion raised in a wedge over the head's last 1.25 (MODELS.md's Lie: at most 0.8 under
    # the head; the first blind review read a flat cushion and a pillow as a bed), its back a pointed-arch board.
    prism('Body', [(1.15, 0.79), (2.46, 0.79), (2.46, 1.8), (1.22, LIE_Y)], -0.93, 0.93, c['cushion'], plane='zy')
    prism('Body', lifted(gothic(-1.07, 1.07, 1.23, 1.5), 0.62), 2.47, 2.58, c['frame'], plane='xy')
    if dress:
        span('Body', (-0.9, LIE_Y - 0.02, -2.3), (0.9, LIE_Y + 0.1, -1.55), c['towel'], bevel=0.04)
        span('Body', (-0.91, LIE_Y + 0.02, -2.0), (0.91, LIE_Y + 0.11, -1.85), c['stripe'])
    spot(1, (0.0, LIE_Y, -0.05), (0, 0, -1), 'Lie')


def lounger_b(c, dress=False):
    """B: a wrought-iron daybed lounger: two side frames on splayed legs, the cushion, a rolled head end."""
    for sx in (-1, 1):
        x0, x1 = sorted((sx * 0.95, sx * 1.08))
        prism('Body', [(-2.6, 0.0), (-2.38, 0.0), (-2.1, 0.62), (2.1, 0.62), (2.38, 0.0), (2.6, 0.0), (2.5, 0.86),
                       (-2.5, 0.86)], x0, x1, c['frame'], plane='zy')
    span('Body', (-0.97, 0.62, -2.58), (0.97, 0.8, 2.5), c['slat'])
    span('Body', (-0.95, 0.78, -2.55), (0.95, LIE_Y, 2.0), c['cushion'], bevel=0.08)
    cyl('Body', (0, 0, 0), 0.4, 2.1, c['cushion'], n=10, m=at((-1.05, 1.18, 2.15), rz=-90))
    for sx in (-1, 1):
        cyl('Body', (0, 0, 0), 0.42, 0.06, c['frame'], n=10, m=at((sx * 1.05 - (0.06 if sx > 0 else 0), 1.18, 2.15),
                                                                 rz=-90))
    spot(1, (0.0, LIE_Y, -0.08), (0, 0, -1), 'Lie')


def lounger_c(c, dress=False):
    """C: a stone slab on two gothic trestles (a pointed arch through each), a cushion and a bolster."""
    for z in (-1.9, 1.9):
        pts = [(-1.0, 0.0), (-0.5, 0.0)] + [(x, y) for x, y in K.arch_points(-0.5, 0.5, 0.2, 0.55, n=3)] + \
              [(0.5, 0.0), (1.0, 0.0), (1.0, 0.72), (-1.0, 0.72)]
        prism('Body', pts, z - 0.25, z + 0.25, c['frame'], plane='xy')
    span('Body', (-1.08, 0.7, -2.6), (1.08, 0.88, 2.6), c['slat'], bevel=0.04)
    span('Body', (-0.95, 0.86, -2.5), (0.95, LIE_Y, 2.5), c['cushion'], bevel=0.08)
    cyl('Body', (0, 0, 0), 0.28, 1.8, c['pillow'], n=10, m=at((-0.9, LIE_Y + 0.22, 2.0), rz=-90))
    spot(1, (0.0, LIE_Y, 0.0), (0, 0, -1), 'Lie')


GC = {'floor': 'stone_dark', 'wall': 'grey', 'lining': 'stone_dark', 'cope': 'stone', 'water': 'moon_dark',
      'pier': 'grey', 'gargoyle': 'stone_dark', 'jet': 'moon', 'tile': 'stone_dark', 'border': 'stone',
      'star': 'stone', 'frame': 'stone_dark', 'slat': 'grey', 'cushion': 'stone', 'pillow': 'white',
      'towel': 'white', 'stripe': 'grey'}

POOLS = {'A': (pool_a, 3, 2), 'B': (pool_b, 4, 2), 'C': (pool_c, 3, 3)}
LOUNGERS = {'A': lounger_a, 'B': lounger_b, 'C': lounger_c}
NOTES = {'Pool_A': 'A: 3 x 2, a plain rectangle, the gargoyle on the back rim; two swimmers',
         'Pool_B': 'B: 4 x 2, a lap pool, finial posts on the corners, the gargoyle on the back rim; three swimmers',
         'Pool_C': 'C: 3 x 3, an octagonal basin, the gargoyle on the back facet; four swimmers',
         'Lounger_A': 'A: a wooden deck lounger on four legs, a raised head rest, a pointed-arch board behind it',
         'Lounger_B': 'B: a wrought-iron daybed lounger on splayed side frames, a rolled head end',
         'Lounger_C': 'C: a stone slab on two gothic trestles, a cushion and a bolster'}


def sil_pool(k):
    fn, w, d = POOLS[k]
    pfurn(f'Pool_{k}', w, d)
    fn(GC)
    sdone(NOTES[f'Pool_{k}'])


def sil_lounger(k):
    pfurn(f'Lounger_{k}')
    LOUNGERS[k](GC)
    sdone(NOTES[f'Lounger_{k}'])


# --- The chosen two, in the Manor's dress -------------------------------------------------------------

HM = {'floor': 'teal_dark', 'wall': 'plum_dark', 'lining': 'moon_dark', 'cope': 'stone', 'water': 'teal',
      'pier': 'stone', 'gargoyle': 'stone_dark', 'jet': 'moon', 'tile': 'crimson',
      'border': 'night', 'star': 'moon_dark', 'frame': 'wood_dark', 'slat': 'wood', 'cushion': 'crimson',
      'pillow': 'cream', 'towel': 'cream', 'stripe': 'teal'}


def pool():
    pfurn('Pool')
    pool_b(HM, dress=True)
    sdone('a Haunted Manor indoor pool: a basin on the floor walled by a plum rim with crimson lozenge tiles '
          'under a stone coping at 0.86 (stepped over), a finial post on each corner, a night border '
          'on its teal floor, a stone gargoyle crouched on a pier on the back rim spouting a stream into the water')


def lounger():
    pfurn('Lounger')
    lounger_a(HM, dress=True)
    sdone('a Haunted Manor lounger: a crimson cushion on a slatted dark-wood frame on four legs, raised into a '
          'head rest at the head end with a pointed-arch board behind it, a folded cream towel with a teal stripe '
          'at the foot')


# --- Review (Workbench on light grey: Studio is running, no EEVEE or Cycles) --------------------------

def _swimmer(pos):
    """The 5-stud person as the contract poses a swimmer (its middle SWIM_DEPTH under the water's top at `pos`),
    drawn only above the basin's floor: what shows; the rest is under the floor (README, the depth finding)."""
    skin, shirt, sleeve = (250, 200, 160), (70, 130, 200), (45, 95, 155)    # sleeves: skin under water read
    y0 = pos[1] - SWIM_DEPTH - 2.5
    x, z = pos[0], pos[2]
    for lo, hi, rgb in (((x - 1.0, 2.0, z - 0.5), (x + 1.0, 4.0, z + 0.5), shirt),
                        ((x - 1.9, 2.0, z - 0.45), (x - 1.02, 4.0, z + 0.45), sleeve),
                        ((x + 1.02, 2.0, z - 0.45), (x + 1.9, 4.0, z + 0.45), sleeve),
                        ((x - 0.6, 4.0, z - 0.6), (x + 0.6, 5.0, z + 0.6), skin)):
        a, b = y0 + lo[1], y0 + hi[1]
        if b <= FLOOR_T + 0.03:
            continue
        _REV['_block']('swimmer', (lo[0], max(a, FLOOR_T + 0.03), lo[2]), (hi[0], b, hi[2]), rgb)


def squares_at(cx, cz, size):
    for a in range(int(round(size[0] / 3))):
        for b in range(int(round(size[2] / 3))):
            x0, z0 = cx - size[0] / 2 + 3 * a, cz - size[2] / 2 + 3 * b
            shade = (205, 205, 210) if (a + b) % 2 else (185, 185, 192)
            _REV['_block']('sq', (x0 + 0.03, -0.06, z0 + 0.03), (x0 + 2.97, -0.01, z0 + 2.97), shade)


def people(rec, cx, cz=0.0):
    for a, pose in rec['furniture']['spots'].items():
        u = rec['attachments'][a]
        p = (cx + u['pos'][0], u['pos'][1], cz + u['pos'][2])
        if pose == 'Swim':
            _swimmer(p)
        elif pose == 'Lie':
            _lying(p, u['look'])
        else:
            _REV['_person'](Vector((p[0], 0, 0)), p[2])


def pplace(fbx, name, pos, ang=0.0):
    objs = place(fbx, name, pos, ang)
    for ob in objs:
        if ob.name.split('.')[0] == 'Water':
            _see_through(ob, 0.45)          # the code makes it water: drawn see-through, as Glass is
    return objs


def silhouette_sheet(out, fbx, recs):
    rows = (('Pool_A', 'Pool_B', 'Pool_C'), ('Lounger_A', 'Lounger_B', 'Lounger_C'))

    def lay(row, z0, labels):
        x = 0.0
        for i in row:
            n = f'Furniture_{i}'
            size = recs[n]['root']['size']
            cx = x + size[0] / 2
            pplace(fbx, n, (cx, 0, z0))
            squares_at(cx, z0, size)
            people(recs[n], cx, z0)
            _REV['_person'](Vector((cx + size[0] / 2 + 2.2, 0, 0)), z0)
            if labels:
                _label(i.split('_')[1], cx, z0 - size[2] / 2 - 3.0)
            x += size[0] + 6.0
        return x
    shots = []
    clear()
    x = max(lay(rows[0], 11.0, True), lay(rows[1], 0.0, True))
    _REV['_block']('floor', (-3, -0.3, -6), (x + 2, -0.07, 17), (150, 150, 156))
    shots.append(render(out / 'silhouettes_game.png', (-0.35, 1.25, -1.0), (1600, 900), (-2, 0, -5), (x, 4.0, 16),
                        scale=1.0))
    for k, row in enumerate(rows):
        clear()
        x = lay(row, 0.0, False)
        shots.append(render(out / f'silhouettes_front_{k + 1}.png', (0.0, 0.05, -1.0), (1600, 420), (-2, -0.3, -5),
                            (x, 5.4, 3), scale=1.02))
    return shots


def review_final(out, fbx, recs):
    names = ['Furniture_Pool', 'Furniture_Lounger']
    shots = []

    def scene(spots=True):
        clear()
        x = 0.0
        for n in names:
            size = recs[n]['root']['size']
            cx = x + size[0] / 2
            pplace(fbx, n, (cx, 0, 0))
            _squares(cx, size)
            if spots:
                people(recs[n], cx)
            x += size[0] + 4.0
        _REV['_person'](Vector((x + 0.5, 0, 0)), 0.0)
        _REV['_block']('floor', (-3, -0.3, -6), (x + 4, -0.07, 5), (150, 150, 156))
        return x
    x = scene()
    lo, hi = (-1.5, 0, -3.5), (x + 3, 5.2, 3.5)
    shots.append(render(out / '1_game_camera.png', (-0.45, 1.28, -1.0), (1400, 800), lo, hi, scale=1.02))
    shots.append(render(out / '2_front_three_quarter.png', (-0.7, 0.45, -1.0), (1400, 800), lo, hi, scale=1.02))
    shots.append(render(out / '3_back_three_quarter.png', (0.7, 0.55, 1.0), (1400, 800), lo, hi, scale=1.02))
    x = scene(spots=False)
    shots.append(render(out / '4_front_level.png', (0.0, 0.0, -1.0), (1400, 600), (-1.5, -0.3, -3.5),
                        (x + 3, 5.4, 3.5), scale=1.02))
    shots.append(render(out / '5_top.png', (0.0, 1.0, -0.02), (1400, 800), (-1.5, 0, -3.5), (x + 3, 5.4, 3.5),
                        scale=1.02))
    clear()
    x = 0.0
    for n in names:
        size = recs[n]['root']['size']
        cx = x + size[2] / 2
        pplace(fbx, n, (cx, 0, 0), 90)
        _squares(cx, size, 90)
        x += size[2] + 3.0
    _REV['_person'](Vector((x + 1.0, 0, 0)), 0.0)
    shots.append(render(out / '6_side_level.png', (0.0, 0.0, -1.0), (1400, 600), (-1.5, -0.3, -7), (x + 3, 5.4, 7),
                        scale=1.02))
    # The gargoyle and its stream up close (the joints: pier, cap, paws, jaw, stream into the water).
    clear()
    pplace(fbx, names[0], (0, 0, 0))
    OZ = recs[names[0]]['root']['size'][2] / 2 - 0.4
    shots.append(render(out / '7_close_gargoyle.png', (-0.6, 0.35, -1.0), (1000, 800), (-1.6, 0, OZ - 2.0),
                        (1.6, 3.3, OZ + 0.1), scale=1.0))
    # The pool in use from the game's camera, the lounger with its guest.
    people(recs[names[0]], 0.0)
    _REV['_person'](Vector((-7.6, 0, 0)), -1.0)
    _REV['_block']('floor', (-9, -0.3, -5), (8, -0.07, 4), (150, 150, 156))
    shots.append(render(out / '8_pool_in_use.png', (-0.45, 1.28, -1.0), (1400, 800), (-8.5, 0, -3.5), (6.5, 3.5, 3.5),
                        scale=1.0))
    clear()
    pplace(fbx, names[1], (0, 0, 0))
    people(recs[names[1]], 0.0)
    _REV['_block']('floor', (-3, -0.3, -4), (3, -0.07, 4), (150, 150, 156))
    shots.append(render(out / '9_close_lounger.png', (-0.7, 0.5, -0.7), (1000, 800), (-2.2, 0, -3.2), (2.2, 2.2, 3.2),
                        scale=1.0))
    # A poolside: the pool with two loungers along its front a square away, from the game's camera.
    clear()
    pplace(fbx, names[0], (0, 0, 0))
    people(recs[names[0]], 0.0)
    for k, lx in enumerate((-3.0, 3.0)):
        pplace(fbx, names[1], (lx, 0, -7.5), 0 if k else 0)
    people(recs[names[1]], -3.0, -7.5)
    _REV['_person'](Vector((7.5, 0, 0)), -4.5)
    _REV['_block']('floor', (-9, -0.3, -12), (9, -0.07, 4), (150, 150, 156))
    shots.append(render(out / '10_poolside_game_camera.png', (-0.45, 1.28, -1.0), (1400, 900), (-8, 0, -11),
                        (8, 3.5, 3.5), scale=1.0))
    return shots


# --- The set ------------------------------------------------------------------------------------------

def main():
    K.use_palette(HM_PALETTE)
    if GREY:
        K.IMPORT_CHECKS = False         # drafts with _A/_B/_C ids, not for import
        K.start_set(SET + '/silhouettes')
        for k in POOLS:
            sil_pool(k)
        for k in LOUNGERS:
            sil_lounger(k)
        recs = {p.name: r for p, r, _ in K.BUILT}
        out = K.ROOT / 'blender' / SET / 'silhouettes'
        (out / 'manifest.json').write_text(json.dumps({'pieces': recs, 'swim_findings': SWIM_FINDINGS}, indent=1))
        if not K.NOPREVIEW:
            print('SHEETS', silhouette_sheet(out / 'review', out / 'fbx', recs), flush=True)
        return
    K.start_set(SET)
    pool()
    lounger()
    built = [p.name for p, _, _ in K.BUILT]
    K.end_set('Haunted Manor: the Indoor Pool\'s pool and lounger (GDD A.13)', [(built, 3.0, 1.0)], sheet=False)
    out = K.ROOT / 'blender' / SET
    manifest = json.loads((out / 'manifest.json').read_text())
    patch_fixup(out / 'import_fixup.luau', manifest)
    val = json.loads((out / 'validation.json').read_text())
    val['spots'] = {n: {'spots': r['furniture']['spots'],
                        'checked': ('spots_check on the built and the re-imported triangles: Use_<n> from 1 without '
                                    'a gap, a Pose from MODELS.md\'s list, a level LookVector, no two spots on one '
                                    'square; Swim: the one Water part present and not colliding, the spot on its top '
                                    f'(to 0.02), nothing else of the piece within {SWIM_IN} round it from the basin '
                                    f'floor to {SWIM_CLEAR} over the water (inside the inner edge by {SWIM_IN}, no '
                                    'spout or stream on a swimmer); Lie: inside the footprint, on its surface with '
                                    'nothing over it, and the lying 5-stud person (lie_faults: in the footprint, '
                                    'on the piece, nothing rising through it, arms included)')}
                    for n, r in manifest['pieces'].items()}
    val['swim_findings'] = {
        'note': ('MODELS.md\'s Swim puts the body\'s middle 1.5 under the water\'s surface (shoulders at it, the head '
                 'over it, the feet 4 under it). The floor cannot be dug, so the water is 0.72 over the floor: the '
                 'body\'s middle and legs are under the floor the pool stands on (inside the 1-stud slab, and past '
                 'it into the room below). A finding for the code (README, his call), not a refusal.'),
        **SWIM_FINDINGS}
    val['pending_pieces_rows'] = {
        'note': 'Pieces.luau has no rows for these on main (the code branch claude/room-types has Pool 3 x 2 height '
                '1.5 and Lounger 1 x 2 height 2.0). The kit\'s Pieces check ran against these values; the rows must '
                'say the same w, d, layer and height (to 0.3).',
        **{f'Furniture_{i}': {k: r[k] for k in ('w', 'd', 'layer', 'height', 'keyFor')} | {'furniture': True}
           for i, r in PENDING.items() if i in ('Pool', 'Lounger')}}
    val['not_validated'] = val.get('not_validated', [])[:1] + [
        'the attachments and each Use_<n> Pose attribute exist only in manifest.json until import_fixup.luau makes '
        'them', 'a visitor walking to a spot, stepping over the rim, swimming or lying: no walker or animation has run',
        'the Water made water and the Jet_1 stream dressed: the code does it (nothing does yet)',
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
