"""The hotel kit: everything a hotel-piece script needs that is not the piece's shape.

A build script on this kit is, per piece, begin() + its shapes + finish():
the primitives (box, lathe, cyl, sphere, prism), the palette atlas and its
UVs, the room shell every room and amenity shares (floor, walls in pieces
round the door, the lamp, the attachments), the LOD_Proxy, FBX export, the
manifest, the validator, the Workbench contact sheet and the import fix-up
Luau all live here. Lifted from Sector Omega's ship_kit.py (export settings,
the atlas, finish() refusing a bad model, validate() re-importing the FBX).

FRAME. Shapes are authored in ROBLOX coordinates: X right, Y up, the door
toward -Z (MODELS.md, "Hotel kit"), y = 0 where feet stand. rb2bl() turns a
Roblox point into Blender's (-x, z, y); the FBX export (axis_forward -Z, up Y,
as ship_kit) brings Blender -Y to Roblox -Z, so the street side arrives at -Z.
If Studio ever shows a set mirrored or turned, rb2bl() is the one line to fix,
and import_fixup.luau says so first: it compares every part's position with
the manifest before it touches anything.

THE CONTRACT. finish() refuses a piece that breaks MODELS.md, "Hotel kit":
names; Root's size and centre; every attachment the blockout in
src/server/HotelKit.luau carries, at the blockout's position within 0.1 stud
and with its LookVector; nothing outside the footprint; walls under 10 and
each wall piece's box exactly the blockout's; the door opening at least 4 x 7
and nothing colliding in it or on the walk from Door to Bed; decor slots
clear; triangle budgets; glow colours only in Glow_<Key>_<n> parts and
nothing else in them; the stair core's walked boxes identical to the
blockout's (walker-proven, 2026-10-19).

ATTACHMENTS do not travel through FBX. Every attachment is in manifest.json
(Roblox coordinates, piece frame), and import_fixup.luau, run once in Studio's
Edit datamodel after the import, makes them on Root, sets Root, PrimaryPart,
the pivot, CanCollide, CollisionFidelity, the glows and LOD_Proxy.

Run: blender -b --python-exit-code 1 -P tools/build_<set>.py [-- nopreview] [-- only Name,Name]
"""
import bpy
import bmesh
import json
import math
import re
import sys
from pathlib import Path
from mathutils import Vector, Matrix

ROOT = Path(__file__).resolve().parents[1]
ARGS = sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else []
NOPREVIEW = 'nopreview' in ARGS
ONLY = set(ARGS[ARGS.index('only') + 1].split(',')) if 'only' in ARGS else None

# Constants.Grid (src/shared/Constants.luau) and MODELS.md
CELL, WALL, FLOOR, T = 6.0, 10.0, 12.0, 0.4
DOOR_W, DOOR_H = 4.0, 7.0
LOBBY_W, LOBBY_D = 72.0, 12.0
TOL = 0.1
PERSON = 5.0                    # the standard avatar, his ruling 2026-10-19
PERSON_R = 0.8                  # half the width the walk check sweeps
BUDGET = {'Room': 6000, 'Amenity': 6000, 'Lobby': 8000, 'Stairs': 8000, 'Decor': 1500,
          'Sign': 3000,         # Sign: not in MODELS.md's table; a draft ceiling, see README
          'Cosmetic': 2000}     # Cosmetic: not in MODELS.md's table either; a draft ceiling (cosmetics set)
MESH_CAP = 20000
PROXY_BUDGET = 500
GLOW_KEYS = ('Warm', 'Cold', 'Eyes', 'Magic')
GLOW_COLOURS = {'Warm': (255, 200, 140), 'Cold': (170, 210, 255), 'Eyes': (255, 240, 120),
                'Magic': (120, 255, 170)}   # what import_fixup.luau makes them, Neon

# The palette: one 256 px atlas of 8 x 8 flat cells shared by the whole set
# (MODELS.md: textures shared, 1024 at most). Cozy creepy (GDD §12): purples,
# teals, pumpkin orange, moonlight blue. A third value names a glow key: that
# colour may only be in a Glow_<key>_<n> part.
PALETTE = [
    ('plum', (90, 70, 110)), ('plum_dark', (60, 45, 78)), ('plum_deep', (40, 30, 55)),
    ('violet', (130, 90, 180)), ('lilac', (170, 135, 210)), ('lavender', (210, 190, 235)),
    ('teal', (40, 150, 150)), ('teal_dark', (25, 95, 105)), ('teal_light', (110, 205, 190)),
    ('pumpkin', (240, 130, 40)), ('pumpkin_dark', (185, 85, 30)), ('amber', (240, 175, 70)),
    ('gold', (220, 180, 90)), ('moon', (175, 200, 240)), ('moon_dark', (90, 115, 170)),
    ('night', (35, 40, 70)), ('bone', (235, 225, 200)), ('cream', (245, 238, 250)),
    ('wood', (125, 82, 55)), ('wood_dark', (80, 52, 38)), ('wood_light', (170, 120, 80)),
    ('stone', (130, 125, 140)), ('stone_dark', (85, 82, 95)), ('moss', (85, 120, 70)),
    ('grass', (90, 150, 80)), ('leaf', (125, 185, 90)), ('crimson', (140, 30, 55)),
    ('crimson_dark', (90, 20, 40)), ('rose', (200, 90, 120)), ('black', (30, 28, 36)),
    ('iron', (60, 62, 70)), ('sand', (220, 200, 140)), ('meat', (170, 60, 50)),
    ('straw', (205, 170, 90)), ('white', (240, 240, 245)), ('slime', (140, 210, 90)),
    ('sky', (90, 140, 220)), ('dusty', (150, 130, 110)), ('jade', (120, 200, 170)),
    ('honey', (240, 190, 80)), ('brown', (140, 100, 70)), ('wine', (120, 30, 50)),
    ('ink', (50, 45, 70)), ('book_a', (150, 60, 70)), ('book_b', (60, 110, 130)),
    ('book_c', (190, 150, 70)), ('grey', (110, 110, 120)),
    ('flame', (255, 205, 120), 'Warm'), ('lamp', (255, 185, 110), 'Warm'),
    ('moonglow', (205, 225, 255), 'Cold'), ('brew', (120, 255, 160), 'Magic'),
]
COLOUR = {p[0]: i for i, p in enumerate(PALETTE)}
GLOW_OF = {p[0]: p[2] for p in PALETTE if len(p) > 2}
ATLAS_N, ATLAS_CELL = 8, 32
assert len(PALETTE) <= ATLAS_N * ATLAS_N


def use_palette(entries):
    """A set's own palette (one atlas per set): `entries` as PALETTE's, replacing it
    for every piece built after the call. The kit itself paints Root and LOD_Proxy
    'grey', so a set's palette has a 'grey'. Not calling it keeps the Haunted
    Manor palette above (added for Frostfang Lodge, 2026-10-19)."""
    global PALETTE, COLOUR, GLOW_OF, _ATLAS
    entries = list(entries)
    assert len(entries) <= ATLAS_N * ATLAS_N, f'{len(entries)} colours > the atlas {ATLAS_N * ATLAS_N}'
    assert any(e[0] == 'grey' for e in entries), "the palette needs 'grey' (Root, LOD_Proxy)"
    for e in entries:
        assert len(e) == 2 or e[2] in GLOW_KEYS, f'{e[0]}: glow key {e[2]!r} not in {GLOW_KEYS}'
    PALETTE = entries
    COLOUR = {e[0]: i for i, e in enumerate(PALETTE)}
    GLOW_OF = {e[0]: e[2] for e in PALETTE if len(e) > 2}
    _ATLAS = None


def rb2bl(v):
    """A Roblox point (x right, y up, -z the street) in Blender's frame."""
    return Vector((-v[0], v[2], v[1]))


def bl2rb(v):
    return Vector((-v[0], v[2], v[1]))


def v3(v, nd=4):
    return [round(float(c), nd) for c in v]


def unit(v):
    v = Vector(v)
    return v.normalized() if v.length else v


# --- The piece being built --------------------------------------------------------------

class Piece:
    def __init__(self, name, kind, size, root_centre, w=None, d=None):
        self.name, self.kind, self.w, self.d = name, kind, w, d
        self.size, self.root_centre = Vector(size), Vector(root_centre)
        self.parts = {}        # name -> [verts, faces, colour names]
        self.collide = {}      # name -> bool
        self.att = {}          # name -> (pos, look or None)
        self.notes = []
        # Cosmetic (and any later kind): extra contract checks, fn(piece, tris, stage) -> [faults],
        # tris {part: [(a, b, c), ...]} in Roblox coords, stage 'built' or 'fbx'; run by finish()
        # and validate(). `allowed`, when set, is the (lo, hi) box footprint() returns.
        self.checks = []
        self.allowed = None


P = None
BUILT = []                     # (Piece, records) in build order, for the sheet and the fix-up
SET_DIR = None


def begin(name, kind, size, root_centre=(0, 0.1, 0), w=None, d=None):
    """An empty piece: its Root (MODELS.md, invisible, footprint x 0.2) made already."""
    global P
    P = Piece(name, kind, size, root_centre, w, d)
    box('Root', root_centre, size, 'grey', collide=False)
    return P


def want(name):
    return ONLY is None or name in ONLY


def attach(name, pos, look=None):
    P.att[name] = (Vector(pos), unit(look) if look is not None else None)


def declare(part, collide):
    P.collide[part] = collide


def _part(name, collide):
    if name not in P.parts:
        P.parts[name] = [[], [], []]
        if name not in P.collide:
            P.collide[name] = (collide if collide is not None else
                               not (name.startswith(('Glow_', 'Dressing', 'LOD_Proxy')) or name == 'Root'))
    elif collide is not None:
        P.collide[name] = collide
    return P.parts[name]


def _side_of(n):
    if n.y > 0.7:
        return 'top'
    if n.y < -0.7:
        return 'bottom'
    if n.z < -0.7:
        return 'front'
    if n.z > 0.7:
        return 'back'
    if n.x < -0.7:
        return 'left'
    if n.x > 0.7:
        return 'right'
    return 'side'


def _colour(spec, n):
    if isinstance(spec, str):
        return spec
    side = _side_of(n)
    return spec.get(side, spec.get('side', spec.get('rest')))


def _add(part, verts, faces, col, m=None, collide=None):
    """Append closed geometry (Roblox coords) to `part`; each face coloured by
    `col`: a palette name, or {'top'|'bottom'|'front'|'back'|'left'|'right'|'side': name}."""
    store = _part(part, collide)
    if m is not None:
        verts = [m @ Vector(v) for v in verts]
    else:
        verts = [Vector(v) for v in verts]
    centroid = sum(verts, Vector()) / len(verts)
    base = len(store[0])
    store[0].extend(verts)
    for f in faces:
        pts = [verts[i] for i in f]
        n = Vector()
        for i in range(len(pts)):
            a, b = pts[i], pts[(i + 1) % len(pts)]
            n += Vector(((a.y - b.y) * (a.z + b.z), (a.z - b.z) * (a.x + b.x), (a.x - b.x) * (a.y + b.y)))
        fc = sum(pts, Vector()) / len(pts)
        if n.dot(fc - centroid) < 0:
            n = -n
        name = _colour(col, unit(n))
        assert name in COLOUR, f'{P.name}/{part}: colour {name!r} not in PALETTE'
        store[1].append([base + i for i in f])
        store[2].append(name)


def at(pos=(0, 0, 0), rx=0, ry=0, rz=0):
    """A transform in Roblox coords: rotate (degrees, X then Y then Z), then move to pos."""
    return (Matrix.Translation(Vector(pos)) @ Matrix.Rotation(math.radians(rz), 4, 'Z')
            @ Matrix.Rotation(math.radians(ry), 4, 'Y') @ Matrix.Rotation(math.radians(rx), 4, 'X'))


BOX_FACES = [(0, 1, 3, 2), (4, 6, 7, 5), (0, 4, 5, 1), (2, 3, 7, 6), (0, 2, 6, 4), (1, 5, 7, 3)]


def box(part, c, s, col, bevel=0.0, m=None, collide=None):
    """A box centred on `c` of size `s`; `bevel` chamfers every edge (the box keeps its size)."""
    c, s = Vector(c), Vector(s)
    if bevel <= 0:
        verts = [c + Vector(((i >> 2 & 1) - .5) * s.x * Vector((1, 0, 0))
                            + ((i >> 1 & 1) - .5) * s.y * Vector((0, 1, 0))
                            + ((i & 1) - .5) * s.z * Vector((0, 0, 1))) for i in range(8)]
        _add(part, verts, BOX_FACES, col, m, collide)
        return
    bevel = min(bevel, min(s) * 0.45)
    bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=1.0)
    for v in bm.verts:
        v.co = Vector((v.co.x * s.x, v.co.y * s.y, v.co.z * s.z)) + c
    bmesh.ops.bevel(bm, geom=list(bm.edges) + list(bm.verts), offset=bevel, segments=1,
                    affect='EDGES', profile=0.5)
    verts = [v.co.copy() for v in bm.verts]
    idx = {v: i for i, v in enumerate(bm.verts)}
    faces = [[idx[v] for v in f.verts] for f in bm.faces]
    bm.free()
    _add(part, verts, faces, col, m, collide)


def span(part, lo, hi, col, bevel=0.0, m=None, collide=None):
    """A box from corner `lo` to corner `hi`."""
    lo, hi = Vector(lo), Vector(hi)
    box(part, (lo + hi) / 2, hi - lo, col, bevel, m, collide)


def lathe(part, profile, col, n=8, base=(0, 0, 0), scale=(1, 1), m=None, phase=None, collide=None, closed=False):
    """Revolve (r, y) points, bottom to top, about the Y axis through `base`.
    A point with r = 0 is a pole; ends with r > 0 are capped. `closed`: the
    profile is a loop (a ring, a rim, a torus), joined last to first, no caps."""
    base = Vector(base)
    phase = math.pi / n if phase is None else phase
    verts, faces, rings = [], [], []
    for r, y in profile:
        if r <= 1e-6:
            rings.append([len(verts)])
            verts.append(base + Vector((0, y, 0)))
        else:
            ring = []
            for k in range(n):
                a = phase + 2 * math.pi * k / n
                ring.append(len(verts))
                verts.append(base + Vector((r * math.cos(a) * scale[0], y, r * math.sin(a) * scale[1])))
            rings.append(ring)
    pairs = list(zip(rings, rings[1:])) + ([(rings[-1], rings[0])] if closed else [])
    for r0, r1 in pairs:
        if len(r0) == 1 and len(r1) == 1:
            continue
        if len(r0) == 1:
            faces += [(r0[0], r1[(k + 1) % n], r1[k]) for k in range(n)]
        elif len(r1) == 1:
            faces += [(r0[k], r0[(k + 1) % n], r1[0]) for k in range(n)]
        else:
            faces += [(r0[k], r0[(k + 1) % n], r1[(k + 1) % n], r1[k]) for k in range(n)]
    if len(rings[0]) > 1 and not closed:
        faces.append(tuple(reversed(rings[0])))
    if len(rings[-1]) > 1 and not closed:
        faces.append(tuple(rings[-1]))
    _add(part, verts, faces, col, m, collide)


def cyl(part, base, r, h, col, n=8, r_top=None, scale=(1, 1), m=None, collide=None):
    lathe(part, [(r, 0), (r if r_top is None else r_top, h)], col, n, base, scale, m, collide=collide)


def sphere(part, c, radii, col, n=8, rings=5, m=None, collide=None):
    """An ellipsoid of half-sizes `radii` centred on `c`."""
    rx, ry, rz = radii if not isinstance(radii, (int, float)) else (radii, radii, radii)
    prof = [(math.sin(math.pi * i / rings), -math.cos(math.pi * i / rings)) for i in range(rings + 1)]
    prof[0], prof[-1] = (0, -1), (0, 1)
    c = Vector(c)
    lathe(part, [(r, y * ry) for r, y in prof], col, n, c, (rx, rz), m, collide=collide)


def prism(part, pts, a0, a1, col, plane='xy', m=None, collide=None):
    """A polygon (convex or not) of 2-D points in `plane`, extruded from a0 to a1
    along the remaining axis. 'xy': (x, y) along z; 'xz': (x, z) along y; 'zy': (z, y) along x."""
    def p3(u, v, w):
        return {'xy': (u, v, w), 'xz': (u, w, v), 'zy': (w, v, u)}[plane]
    k = len(pts)
    verts = [Vector(p3(u, v, a0)) for u, v in pts] + [Vector(p3(u, v, a1)) for u, v in pts]
    faces = [tuple(range(k)), tuple(range(2 * k - 1, k - 1, -1))]
    faces += [(i, (i + 1) % k, k + (i + 1) % k, k + i) for i in range(k)]
    _add(part, verts, faces, col, m, collide)


def arch_points(x0, x1, spring, apex, n=4, top=None):
    """The outline of a pointed (gothic) arch opening from x0 to x1, springing at
    `spring`, its point at `apex`: the points along the arch, left to right."""
    out = []
    mid = (x0 + x1) / 2
    for i in range(n + 1):
        t = i / n
        out.append((x0 + (mid - x0) * t, spring + (apex - spring) * math.sin(t * math.pi / 2)))
    for i in range(n - 1, -1, -1):
        t = i / n
        out.append((x1 - (x1 - mid) * t, spring + (apex - spring) * math.sin(t * math.pi / 2)))
    return out


def round_arch_points(x0, x1, spring, apex, n=6):
    """A round (elliptical) arch's outline from x0 to x1, springing at `spring`,
    its crown at `apex`: the points along it, left to right."""
    mid, hw = (x0 + x1) / 2, (x1 - x0) / 2
    return [(mid - hw * math.cos(math.pi * i / n), spring + (apex - spring) * math.sin(math.pi * i / n))
            for i in range(n + 1)]


# --- The blockout's numbers (src/server/HotelKit.luau), for the checks ----------------

def door_x(w):
    return (math.floor((w - 1) / 2) + 0.5) * CELL - w * CELL / 2


def blockout_attachments(kind, w=None, d=None):
    """Every attachment the Luau blockout makes for this kind, as {name: (pos, look)}."""
    if kind in ('Room', 'Amenity'):
        W, D = w * CELL, d * CELL
        dx = door_x(w)
        out = {
            'Door': ((dx, 0, -D / 2), (0, 0, -1)),
            'Sign': ((dx, DOOR_H + 1.2, -D / 2 - 0.3), (0, 0, -1)),
            'Decor_1': ((-W / 2 + 2, 0, D / 2 - 2), (1, 0, -1)),
            'Decor_2': ((W / 2 - 2, 0, D / 2 - 2), (-1, 0, -1)),
            'Decor_3': ((-W / 2 + 2, 0, 0), (1, 0, 0)),
        }
        out['Bed'] = ((0, 0, D / 2 - 7), (0, 0, -1)) if kind == 'Room' else ((0, 0, -D / 6), (0, 0, 1))
        return out
    if kind == 'Lobby':
        out = {'Entrance': ((0, 0, 0), (0, 0, -1)), 'Desk': ((-12, 3.8, 7.8), (0, 0, -1)),
               'Till': ((12, 3.8, 7.8), (0, 0, -1)), 'Spawn': ((4, 0, 8), (0, 0, -1)),
               'SignBoard': ((0, 0, -7), (0, 0, -1))}
        for i in range(1, 5):
            out[f'Queue_{i}'] = ((-12 - 4 * (i - 1), 0, 5.5), (0, 0, 1))
        for i in range(1, 4):
            out[f'Trap_{i}'] = ((-24 + 16 * i, 0, 3), (0, 0, -1))
        return out
    if kind == 'Stairs':
        return {'Bottom': ((-3, 0, -5.75), None), 'Path_1': ((-3, 6, 4), None),
                'Path_2': ((3, 6, 4), None), 'Top': ((3, FLOOR, -5.75), None)}
    return {}


def blockout_room_walls(w, d):
    """The blockout's wall boxes, {name: (centre, size)}: the collision a room keeps."""
    W, D = w * CELL, d * CELL
    dx = door_x(w)
    z = -D / 2 + T / 2
    out = {'Wall_Back': ((0, WALL / 2, D / 2 - T / 2), (W, WALL, T)),
           'Wall_Left': ((-W / 2 + T / 2, WALL / 2, 0), (T, WALL, D - 2 * T)),
           'Wall_Right': ((W / 2 - T / 2, WALL / 2, 0), (T, WALL, D - 2 * T)),
           'Wall_Lintel': ((dx, DOOR_H + (WALL - DOOR_H) / 2, z), (DOOR_W, WALL - DOOR_H, T))}
    left_end, right_start = dx - DOOR_W / 2, dx + DOOR_W / 2
    if left_end > -W / 2:
        ln = left_end + W / 2
        out['Wall_FrontLeft'] = ((-W / 2 + ln / 2, WALL / 2, z), (ln, WALL, T))
    if right_start < W / 2:
        ln = W / 2 - right_start
        out['Wall_FrontRight'] = ((W / 2 - ln / 2, WALL / 2, z), (ln, WALL, T))
    return out


def blockout_stairs(top):
    """The blockout's stair boxes, {name: (centre, size)}: the walker-proven geometry."""
    S, steps, tread = 12.0, 5, 1.5
    rise = FLOOR / 2 / steps
    z0 = -S / 2 + 0.5
    landing_start = z0 + tread * steps
    landing_depth = S / 2 - landing_start
    out = {}
    for i in range(1, steps + 1):
        out[f'Step_Up_{i}'] = ((-S / 4, rise * i - 0.5, z0 + tread * (i - 0.5)), (S / 2, 1, tread))
    landing_y = rise * steps
    out['Landing'] = ((0, landing_y - 0.5, landing_start + landing_depth / 2), (S, 1, landing_depth))
    for i in range(1, steps + 1):
        zc = landing_start - tread * (i - 0.5)
        h = landing_y + rise * i
        front = -S / 2 if i == steps else zc - tread / 2
        back = zc + tread / 2
        out[f'Step_Down_{i}'] = ((S / 4, h - 0.5, (front + back) / 2), (S / 2, 1, back - front))
    h = FLOOR + (3.5 if top else 0)
    out['Wall_Left'] = ((-S / 2 + T / 2, h / 2, 0), (T, h, S))
    out['Wall_Right'] = ((S / 2 - T / 2, h / 2, 0), (T, h, S))
    out['Wall_Back'] = ((0, h / 2, S / 2 - T / 2), (S, h, T))
    out['Divider'] = ((0, h / 2, (z0 + landing_start) / 2), (T, h, landing_start - z0))
    if top:
        out['Rail_Top'] = ((-S / 4, FLOOR + 1.75, -S / 2 + 1), (S / 2, 3.5, T))
    return out


# --- The room shell ------------------------------------------------------------------------

def room_shell(w, d, paper, wainscot='wood_dark', crown='gold', outside='plum', floor=('wood', 'wood_light'),
               rug=None, lamp=True, lintel='pointed', stripes=7):
    """Floor, walls in pieces round the door, the lamp and every attachment of a
    room or amenity: exactly the blockout's boxes, dressed by colour bands.
    `paper` is the wall colour, or a tuple of colours laid in `stripes`
    horizontal bands (logs, snow blocks); `floor` two plank colours, or one for
    a plain floor; `lintel` 'pointed' or 'round', the arch over the door."""
    W, D = w * CELL, d * CELL
    # Floor: planks along Z, a hair of groove between them by their chamfer.
    fw, fd = W - 0.2, D - 0.2
    if isinstance(floor, str):
        box('Floor', (0, 0.1, 0), (fw, 0.2, fd), floor, bevel=0.03)
    else:
        n = max(1, round(fw / 1.5))
        pw = fw / n
        for i in range(n):
            x = -fw / 2 + pw * (i + 0.5)
            box('Floor', (x, 0.1, 0), (pw, 0.2, fd), floor[i % len(floor)], bevel=0.03)
    if rug:
        rw, rd, rc, rb = rug[:4]
        box('Floor', (0, 0.215, rc), (rw, 0.03, rd), rb, bevel=0.01)
        box('Floor', (0, 0.235, rc), (rw - 0.6, 0.03, rd - 0.6), rug[4] if len(rug) > 4 else rb, bevel=0.01)
    # Walls: three bands in each, wainscot, paper, crown; the outside of the front
    # wall in the facade's colour.
    dx = door_x(w)
    zf, zb = -D / 2, -D / 2 + T
    jamb = 0.35
    for name, (c, s) in blockout_room_walls(w, d).items():
        c, s = Vector(c), Vector(s)
        lo, hi = c - s / 2, c + s / 2
        if name == 'Wall_Lintel':
            # A pointed arch from the 7-stud head: the opening only grows; the box stays the blockout's.
            pts = (round_arch_points(dx - DOOR_W / 2, dx + DOOR_W / 2, DOOR_H, DOOR_H + 1.6, n=6)
                   if lintel == 'round' else arch_points(dx - DOOR_W / 2, dx + DOOR_W / 2, DOOR_H, DOOR_H + 1.6, n=4))
            outline = [(dx - DOOR_W / 2, WALL)] + pts + [(dx + DOOR_W / 2, WALL)]
            prism(name, list(reversed(outline)), zf, zb, {'front': outside, 'rest': crown})
            continue
        front = name.startswith('Wall_Front')
        x0, x1 = lo.x, hi.x
        if name == 'Wall_FrontLeft':      # the door's jamb is the piece's own trim-coloured end
            x1 = hi.x - jamb
            span(name, (x1, 0, lo.z), (hi.x, WALL, hi.z), crown, bevel=0.06)
        if name == 'Wall_FrontRight':
            x0 = lo.x + jamb
            span(name, (lo.x, 0, lo.z), (x0, WALL, hi.z), crown, bevel=0.06)

        def col(base):
            return {'front': outside, 'rest': base} if front else base
        if isinstance(paper, (tuple, list)):
            k = 6.2 / stripes
            bands = ([(0.0, 3.2, wainscot)] + [(3.2 + i * k, 3.2 + (i + 1) * k, paper[i % len(paper)])
                                               for i in range(stripes)] + [(9.4, WALL, crown)])
        else:
            bands = [(0.0, 3.2, wainscot), (3.2, 9.4, paper), (9.4, WALL, crown)]
        for y0, y1, cname in bands:
            y0, y1 = max(y0, lo.y), min(y1, hi.y)
            if y1 - y0 > 1e-3 and x1 - x0 > 1e-3:
                span(name, (x0, y0, lo.z), (x1, y1, hi.z), col(cname), bevel=0.04)
    # The lamp: a sconce on the back wall, its flame the glow (MODELS.md rule 1).
    if lamp:
        zw = D / 2 - T
        box('Dressing', (0, 8.6, zw - 0.04), (0.7, 1.4, 0.12), 'gold', bevel=0.05)
        box('Dressing', (0, 8.2, zw - 0.35), (0.16, 0.16, 0.6), 'iron')
        cyl('Dressing', (0, 8.25, D / 2 - 1), 0.3, 0.35, 'gold', n=8, r_top=0.38)
        sphere('Glow_Warm_1', (0, 9.0, D / 2 - 1), (0.24, 0.42, 0.24), 'flame', n=8, rings=5)
    for name, (pos, look) in blockout_attachments(P.kind, w, d).items():
        attach(name, pos, look)


def picture(c, size, frame, inner, wall='back', depth=0.12):
    """A framed picture on a wall's inner face; `c` is its centre on the face."""
    c = Vector(c)
    sx, sy = size
    if wall == 'back':
        span('Dressing', (c.x - sx / 2, c.y - sy / 2, c.z - depth), (c.x + sx / 2, c.y + sy / 2, c.z + 0.02), frame, 0.04)
        span('Dressing', (c.x - sx / 2 + 0.25, c.y - sy / 2 + 0.25, c.z - depth - 0.02),
             (c.x + sx / 2 - 0.25, c.y + sy / 2 - 0.25, c.z - depth + 0.05), inner)
    else:   # 'left' (face toward +X) or 'right' (toward -X)
        sgn = 1 if wall == 'left' else -1
        x0, x1 = sorted((c.x - 0.02 * sgn, c.x + depth * sgn))
        span('Dressing', (x0, c.y - sy / 2, c.z - sx / 2), (x1, c.y + sy / 2, c.z + sx / 2), frame, 0.04)
        xi0, xi1 = sorted((c.x + (depth - 0.05) * sgn, c.x + (depth + 0.02) * sgn))
        span('Dressing', (xi0, c.y - sy / 2 + 0.25, c.z - sx / 2 + 0.25),
             (xi1, c.y + sy / 2 - 0.25, c.z + sx / 2 - 0.25), inner)


# --- Finishing ------------------------------------------------------------------------------

class Refused(Exception):
    pass


def _bounds(verts):
    xs, ys, zs = zip(*[(v.x, v.y, v.z) for v in verts])
    return Vector((min(xs), min(ys), min(zs))), Vector((max(xs), max(ys), max(zs)))


def _tris_rb(ob):
    """A mesh object's triangles in Roblox coordinates (world), for Piece.checks."""
    me = ob.data
    me.calc_loop_triangles()
    mw = ob.matrix_world
    return [tuple(bl2rb(mw @ me.vertices[i].co) for i in t.vertices) for t in me.loop_triangles]


def _overlap(alo, ahi, blo, bhi, eps=1e-3):
    return all(alo[i] < bhi[i] - eps and blo[i] < ahi[i] - eps for i in range(3))


def footprint(piece):
    """The (lo, hi) box nothing of the piece may leave."""
    if getattr(piece, 'allowed', None) is not None:     # a cosmetic's envelope, set by its script
        return Vector(piece.allowed[0]), Vector(piece.allowed[1])
    rc, s = piece.root_centre, piece.size
    lo = Vector((rc.x - s.x / 2, 0, rc.z - s.z / 2))
    hi = Vector((rc.x + s.x / 2, 0, rc.z + s.z / 2))
    top = {'Room': WALL, 'Amenity': WALL, 'Lobby': FLOOR, 'Stairs': FLOOR + 3.5, 'Decor': 7.0,
           'Sign': 14.0}[piece.kind]
    lo.y, hi.y = 0.0, top
    return lo, hi


def check_piece(piece, boxes, tris, faults):
    """The contract, on boxes {part: (lo, hi, collide)} in Roblox coords. Used by
    finish() on the built geometry and by validate() on the re-imported FBX."""
    def fault(ok, what):
        if not ok:
            faults.append(what)
    name, kind = piece.name, piece.kind
    ascii_name = re.compile(r'^[A-Za-z][A-Za-z0-9_]*$')
    for part in boxes:
        fault(ascii_name.match(part), f'{part}: not a plain ASCII instance name')
        if part.startswith('Glow'):
            fault(re.match(r'^Glow_(%s)_\d+$' % '|'.join(GLOW_KEYS), part), f'{part}: not Glow_<Key>_<n>')
    # Root
    fault('Root' in boxes, 'no Root')
    if 'Root' in boxes:
        lo, hi, col = boxes['Root']
        fault(((lo + hi) / 2 - piece.root_centre).length < 0.02 and (hi - lo - piece.size).length < 0.02,
              f'Root is {v3(hi - lo)} at {v3((lo + hi) / 2)}, not {v3(piece.size)} at {v3(piece.root_centre)}')
        fault(not col, 'Root collides')
    # Nothing outside the footprint (the sign and decor are not on the grid but keep theirs too).
    flo, fhi = footprint(piece)
    for part, (lo, hi, col) in boxes.items():
        if part == 'LOD_Proxy':
            continue
        out = [i for i in range(3) if lo[i] < flo[i] - 0.01 or hi[i] > fhi[i] + 0.01]
        fault(not out, f'{part} leaves the footprint {v3(flo)}..{v3(fhi)}: {v3(lo)}..{v3(hi)}')
    if kind == 'Decor':
        fault(piece.size.x <= 4.0 + 1e-6 and piece.size.z <= 4.0 + 1e-6, f'decor footprint {v3(piece.size)} > 4 x 4')
    # Required parts per kind
    required = {'Room': ['Floor', 'Bed'], 'Amenity': ['Floor', 'Centrepiece'], 'Lobby': ['Desk', 'Till'],
                'Stairs': [], 'Sign': ['Board', 'PostLeft', 'PostRight'], 'Decor': [], 'Cosmetic': []}[kind]
    if kind == 'Cosmetic':      # MODELS.md, "Cosmetics": visual only, nothing collides
        hits = [p for p, (lo, hi, col) in boxes.items() if col]
        fault(not hits, f'a cosmetic collides: {hits}')
    if kind in ('Room', 'Amenity'):
        walls = blockout_room_walls(piece.w, piece.d)
        required += list(walls)
        for wname, (c, s) in walls.items():
            if wname in boxes:
                lo, hi, col = boxes[wname]
                fault(((lo + hi) / 2 - Vector(c)).length < 0.02 and (hi - lo - Vector(s)).length < 0.02,
                      f'{wname}: box {v3(hi - lo)} at {v3((lo + hi) / 2)}, the blockout has {v3(s)} at {v3(c)}')
                fault(col, f'{wname} does not collide')
    if kind == 'Stairs':
        top = piece.name == 'StairCoreTop'
        for sname, (c, s) in blockout_stairs(top).items():
            required.append(sname)
            if sname in boxes:
                lo, hi, col = boxes[sname]
                fault(((lo + hi) / 2 - Vector(c)).length < 0.01 and (hi - lo - Vector(s)).length < 0.01,
                      f'{sname}: walked/wall box {v3(hi - lo)} at {v3((lo + hi) / 2)} is not the blockout\'s '
                      f'{v3(s)} at {v3(c)}')
                fault(col, f'{sname} does not collide')
        extra = [p for p, (lo, hi, col) in boxes.items() if col and p not in blockout_stairs(top)]
        fault(not extra, f'colliding parts the walker never walked: {extra}')
    if kind == 'Sign' and 'Board' in boxes:
        lo, hi, col = boxes['Board']
        fault(((lo + hi) / 2 - Vector((0, 8, 0))).length < 0.02 and (hi - lo - Vector((16, 6, 0.6))).length < 0.02,
              f'Board is {v3(hi - lo)} at {v3((lo + hi) / 2)}, the SurfaceGui wants 16 x 6 x 0.6 at (0, 8, 0)')
    missing = [r for r in required if r not in boxes]
    fault(not missing, f'missing parts {missing}')
    # The door: an opening at least 4 x 7, nothing colliding in it; the walk to the bed clear.
    if kind in ('Room', 'Amenity'):
        W, D = piece.w * CELL, piece.d * CELL
        dx = door_x(piece.w)
        olo, ohi = Vector((dx - DOOR_W / 2, 0.25, -D / 2 - 0.01)), Vector((dx + DOOR_W / 2, DOOR_H, -D / 2 + T + 0.5))
        hits = [p for p, (lo, hi, col) in boxes.items() if col and _overlap(lo, hi, olo, ohi)]
        fault(not hits, f'door opening {DOOR_W} x {DOOR_H} blocked by {hits}')
        a = Vector(blockout_attachments(kind, piece.w, piece.d)['Door'][0])
        b = Vector(blockout_attachments(kind, piece.w, piece.d)['Bed'][0])
        steps = max(2, int((b - a).length / 0.25))
        blocked = set()
        for i in range(steps + 1):
            p = a.lerp(b, i / steps)
            plo, phi = p + Vector((-PERSON_R, 0.3, -PERSON_R)), p + Vector((PERSON_R, PERSON, PERSON_R))
            for part, (lo, hi, col) in boxes.items():
                if col and part != 'Floor' and _overlap(lo, hi, plo, phi):
                    blocked.add(part)
        fault(not blocked, f'a {PERSON}-stud person walking Door -> Bed is blocked by {sorted(blocked)}')
        # Decor slots: a 4 x 4 square round each, clear of anything that collides but the walls.
        for k in (1, 2, 3):
            c = Vector(blockout_attachments(kind, piece.w, piece.d)[f'Decor_{k}'][0])
            slo, shi = c + Vector((-2, 0.3, -2)), c + Vector((2, 7, 2))
            hits = [p for p, (lo, hi, col) in boxes.items()
                    if col and not p.startswith('Wall_') and p != 'Floor' and _overlap(lo, hi, slo, shi, 0.06)]
            fault(not hits, f'Decor_{k} slot (4 x 4) taken by {hits}')
    if kind == 'Lobby':
        gate = (Vector((-PERSON_R * 2.5, 0.3, -1)), Vector((PERSON_R * 2.5, 7.0, 3)))
        hits = [p for p, (lo, hi, col) in boxes.items() if col and _overlap(lo, hi, *gate)]
        fault(not hits, f'the entrance (4 x 7) is blocked by {hits}')
        targets = blockout_attachments('Lobby')
        a = Vector((0, 0, 3))
        for tname in ['Queue_1', 'Queue_2', 'Queue_3', 'Queue_4', 'Spawn', 'Trap_1', 'Trap_2', 'Trap_3']:
            b = Vector(targets[tname][0])
            steps = max(2, int((b - a).length / 0.25))
            blocked = set()
            for i in range(steps + 1):
                p = a.lerp(b, i / steps)
                plo, phi = p + Vector((-PERSON_R, 0.3, -PERSON_R)), p + Vector((PERSON_R, PERSON, PERSON_R))
                blocked |= {q for q, (lo, hi, col) in boxes.items() if col and _overlap(lo, hi, plo, phi)}
            fault(not blocked, f'the walk entrance -> {tname} is blocked by {sorted(blocked)}')
    # Glow colours stay in glow parts (rule 1), checked in finish() where face colours are known.
    total = sum(t for p, t in tris.items() if p != 'LOD_Proxy')
    fault(total <= BUDGET[kind], f'{total} triangles > the {kind} budget {BUDGET[kind]}')
    for p, t in tris.items():
        fault(t <= MESH_CAP, f'{p}: {t} triangles > the per-mesh cap {MESH_CAP}')
    if 'LOD_Proxy' in tris:
        fault(tris['LOD_Proxy'] <= PROXY_BUDGET, f'LOD_Proxy {tris["LOD_Proxy"]} > {PROXY_BUDGET}')
    return total


_ATLAS = None


def _atlas():
    global _ATLAS
    if _ATLAS is not None:
        return _ATLAS
    n, c = ATLAS_N, ATLAS_CELL
    res = n * c
    img = bpy.data.images.new('HotelAtlas', width=res, height=res, alpha=False)
    px = [0.0] * (res * res * 4)
    for i, entry in enumerate(PALETTE):
        col, row = i % n, i // n
        r, g, b = [ch / 255 for ch in entry[1]]
        for y in range(row * c, (row + 1) * c):
            for x in range(col * c, (col + 1) * c):
                k = (y * res + x) * 4
                px[k:k + 4] = (r, g, b, 1.0)
    img.pixels.foreach_set(px)
    tex_dir = ROOT / 'blender' / SET_DIR / 'textures'
    tex_dir.mkdir(parents=True, exist_ok=True)
    img.filepath_raw = str(tex_dir / 'HotelAtlas.png')
    img.file_format = 'PNG'
    img.save()
    img.pack()
    mat = bpy.data.materials.new('HotelAtlas')
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes.get('Principled BSDF')
    tex = mat.node_tree.nodes.new('ShaderNodeTexImage')
    tex.image = img
    tex.interpolation = 'Closest'
    mat.node_tree.links.new(tex.outputs['Color'], bsdf.inputs['Base Color'])
    bsdf.inputs['Roughness'].default_value = 0.8
    flat = bpy.data.materials.new('LOD_Proxy_Flat')
    flat.use_nodes = True
    flat.node_tree.nodes.get('Principled BSDF').inputs['Base Color'].default_value = (0.1, 0.08, 0.13, 1)
    _ATLAS = (mat, flat)
    return _ATLAS


def _uv(name):
    i = COLOUR[name]
    col, row = i % ATLAS_N, i // ATLAS_N
    return ((col + 0.5) / ATLAS_N, (row + 0.5) / ATLAS_N)


def _proxy(piece):
    """LOD_Proxy (MODELS.md): the colliding parts' boxes joined, flat, no texture."""
    for part, (verts, faces, cols) in list(piece.parts.items()):
        if piece.collide.get(part) and part != 'Root':
            lo, hi = _bounds(verts)
            box('LOD_Proxy', (lo + hi) / 2, hi - lo, 'grey', collide=False)


def finish(proxy=None, note=''):
    """Check the piece against the contract, make its meshes, export
    fbx/<Name>.fbx, and record it for the manifest. Raises Refused on a fault."""
    piece = P
    if proxy is None:
        proxy = piece.kind in ('Room', 'Amenity', 'Lobby', 'Stairs')
    if proxy:
        _proxy(piece)
    faults = []
    # Glows: glow colours only in Glow_ parts, and Glow_ parts only glow colours of their key.
    for part, (verts, faces, cols) in piece.parts.items():
        glows = {GLOW_OF.get(c) for c in cols}
        if part.startswith('Glow_'):
            key = part.split('_')[1]
            if glows != {key}:
                faults.append(f'{part}: holds {sorted(set(cols))}, not only {key} glow colours')
        elif part != 'LOD_Proxy' and glows - {None}:
            faults.append(f'{part}: glow colour {sorted(c for c in set(cols) if c in GLOW_OF)} outside a Glow_ part')
    # Attachments: every one the blockout has, where it has it.
    expect = blockout_attachments(piece.kind, piece.w, piece.d)
    for aname, (pos, look) in expect.items():
        if aname not in piece.att:
            faults.append(f'attachment {aname} missing')
            continue
        got, glook = piece.att[aname]
        if (got - Vector(pos)).length > TOL:
            faults.append(f'attachment {aname} at {v3(got)}, the blockout has {pos}')
        if (look is None) != (glook is None) or (look is not None and glook.dot(unit(look)) < 0.999):
            faults.append(f'attachment {aname} looks {glook}, the blockout {look}')
    for aname in piece.att:
        if aname not in expect and not re.match(r'^[A-Za-z][A-Za-z0-9_]*$', aname):
            faults.append(f'attachment {aname}: bad name')

    atlas, flat = _atlas()
    objs, tris, boxes = [], {}, {}
    for part, (verts, faces, cols) in piece.parts.items():
        lo, hi = _bounds(verts)
        centre = (lo + hi) / 2
        boxes[part] = (lo, hi, piece.collide[part])
        me = bpy.data.meshes.new(part)
        bm = bmesh.new()
        bv = [bm.verts.new(rb2bl(v - centre)) for v in verts]
        uvl = bm.loops.layers.uv.new('UVMap')
        for f, cname in zip(faces, cols):
            face = bm.faces.new([bv[i] for i in f])
            u, v = _uv(cname)
            for k, loop in enumerate(face.loops):
                loop[uvl].uv = (u + 0.002 * (k % 2), v + 0.002 * (k // 2 % 2))
        bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
        bmesh.ops.triangulate(bm, faces=bm.faces, quad_method='BEAUTY', ngon_method='EAR_CLIP')
        if not all(e.is_manifold for e in bm.edges):
            faults.append(f'{part}: open edges')
        bm.to_mesh(me)
        bm.free()
        for poly in me.polygons:
            poly.use_smooth = True
        me.set_sharp_from_angle(angle=math.radians(50))
        me.materials.append(flat if part == 'LOD_Proxy' else atlas)
        me.calc_loop_triangles()
        tris[part] = len(me.loop_triangles)
        ob = bpy.data.objects.new(part, me)
        ob.location = rb2bl(centre)
        bpy.context.scene.collection.objects.link(ob)
        objs.append(ob)
    if getattr(piece, 'checks', None):
        bpy.context.view_layer.update()
        tris_rb = {ob.name: _tris_rb(ob) for ob in objs}
        for fn in piece.checks:
            faults += fn(piece, tris_rb, 'built')
    total = check_piece(piece, boxes, tris, faults)
    if faults:
        for ob in objs:
            bpy.data.objects.remove(ob)
        raise Refused(f'{piece.name} REFUSED:\n  ' + '\n  '.join(faults))

    out = ROOT / 'blender' / SET_DIR / 'fbx'
    out.mkdir(parents=True, exist_ok=True)
    bpy.context.scene.unit_settings.scale_length = .01
    bpy.ops.object.select_all(action='DESELECT')
    for ob in objs:
        ob.select_set(True)
    bpy.context.view_layer.objects.active = objs[0]
    bpy.ops.export_scene.fbx(filepath=str(out / f'{piece.name}.fbx'), use_selection=True,
                             object_types={'MESH'}, apply_unit_scale=True, apply_scale_options='FBX_SCALE_UNITS',
                             axis_forward='-Z', axis_up='Y', bake_anim=False, add_leaf_bones=False,
                             mesh_smooth_type='OFF', use_tspace=False, path_mode='COPY', embed_textures=True)
    records = {
        'name': piece.name, 'kind': piece.kind, 'footprint_cells': [piece.w, piece.d] if piece.w else None,
        'root': {'centre': v3(piece.root_centre), 'size': v3(piece.size)},
        'parts': {p: {'centre': v3((boxes[p][0] + boxes[p][1]) / 2), 'size': v3(boxes[p][1] - boxes[p][0]),
                      'triangles': tris[p], 'collide': boxes[p][2]} for p in boxes},
        'attachments': {a: {'pos': v3(pos), 'look': v3(look) if look is not None else None}
                        for a, (pos, look) in piece.att.items()},
        'triangles': total, 'budget': BUDGET[piece.kind],
        'collision_precise': [],
        'collision_note': ('every mesh Box: walls stand in pieces round the door and every walked step '
                           'is its own box, so nothing needs a decomposition'),
        'note': note,
    }
    for ob in objs:          # unique names in the .blend, so the next piece can use the same ones
        ob.name = f'{piece.name}__{ob.name}'
        ob.data.name = ob.name
    BUILT.append((piece, records, objs))
    print(f'BUILT {piece.name}: {total} triangles, {len(objs)} parts', flush=True)
    return records


# --- The set ---------------------------------------------------------------------------------

def start_set(set_dir):
    global SET_DIR
    SET_DIR = set_dir
    for ob in list(bpy.data.objects):
        bpy.data.objects.remove(ob)
    for me in list(bpy.data.meshes):
        bpy.data.meshes.remove(me)
    sc = bpy.context.scene
    sc.unit_settings.system = 'METRIC'
    sc.unit_settings.scale_length = .01
    (ROOT / 'blender' / set_dir).mkdir(parents=True, exist_ok=True)


def end_set(title, layout_rows, sheet=True):
    """Manifest, .blend, the one Workbench contact sheet, the validator, the fix-up Luau."""
    out = ROOT / 'blender' / SET_DIR
    manifest = {'set': SET_DIR, 'title': title, 'frame': 'Roblox studs, piece frame: X right, Y up, door/front toward -Z, '
                'origin per MODELS.md; Blender holds them as (-x, z, y)',
                'atlas': 'textures/HotelAtlas.png (embedded in every FBX)',
                'palette': {p[0]: list(p[1]) for p in PALETTE},
                'pieces': {piece.name: rec for piece, rec, _ in BUILT}}
    if ONLY is not None and (out / 'manifest.json').exists():     # a partial build keeps the rest
        old = json.loads((out / 'manifest.json').read_text())['pieces']
        manifest['pieces'] = {**old, **manifest['pieces']}
    (out / 'manifest.json').write_text(json.dumps(manifest, indent=1))
    # Lay the pieces out for the .blend and the sheet (the FBXs are already written, at their origins).
    by_name = {piece.name: objs for piece, rec, objs in BUILT}
    z = 0.0
    for row, gap, scale in layout_rows:
        names = [n for n in row if n in by_name]
        if not names:
            continue
        widths = [max(BUILT[[p.name for p, _, _ in BUILT].index(n)][0].size.x, 3.0) * scale for n in names]
        depth = max(BUILT[[p.name for p, _, _ in BUILT].index(n)][0].size.z for n in names) * scale
        x = -(sum(widths) + gap * (len(names) - 1)) / 2
        for n, wdt in zip(names, widths):
            piece = BUILT[[p.name for p, _, _ in BUILT].index(n)][0]
            off = Vector((x + wdt / 2, 0, z - piece.root_centre.z * scale))
            for ob in by_name[n]:
                ob.location = ob.location * scale + rb2bl(off)
                ob.scale = (scale, scale, scale)
                if ob.name.endswith('__LOD_Proxy') or ob.name.endswith('__Root'):
                    ob.hide_render = True
            x += wdt + gap
        z += depth + gap * 1.5
    bpy.ops.wm.save_as_mainfile(filepath=str(out / f'{SET_DIR.split("/")[-1]}.blend'))
    if sheet and not NOPREVIEW and ONLY is None:
        _sheet(out / 'review' / 'contact_sheet.png')
    results = validate()
    _fixup_luau(out / 'import_fixup.luau', manifest)
    return results


def _sheet(path):
    """One Workbench render of the whole set, at most 768 px, textured by the atlas."""
    sc = bpy.context.scene
    sc.render.engine = 'BLENDER_WORKBENCH'
    sc.display.shading.light = 'STUDIO'
    sc.display.shading.color_type = 'TEXTURE'
    sc.display.shading.show_shadows = False
    sc.display.shading.show_cavity = True
    sc.render.resolution_x, sc.render.resolution_y = 768, 576
    sc.render.film_transparent = False
    sc.world = sc.world or bpy.data.worlds.new('World')
    pts = [ob.matrix_world @ Vector(c) for ob in sc.objects if ob.type == 'MESH' and not ob.hide_render
           for c in ob.bound_box]
    lo, hi = _bounds(pts)
    centre = (lo + hi) / 2
    cam_data = bpy.data.cameras.new('Sheet')
    cam_data.type = 'ORTHO'
    cam = bpy.data.objects.new('Sheet', cam_data)
    sc.collection.objects.link(cam)
    # From the street side (Blender -Y), high and a little to the left, looking down into the rooms.
    direction = Vector((0.35, -1.0, 1.25)).normalized()
    cam.location = centre + direction * 400
    cam.rotation_euler = (-direction).to_track_quat('-Z', 'Y').to_euler()
    cam_data.clip_end = 2000
    # fit: project the box corners onto the camera plane
    rot = cam.rotation_euler.to_matrix()
    right, up = rot @ Vector((1, 0, 0)), rot @ Vector((0, 1, 0))
    xs = [(p - centre).dot(right) for p in pts]
    ys = [(p - centre).dot(up) for p in pts]
    aspect = sc.render.resolution_x / sc.render.resolution_y
    cam_data.ortho_scale = max(max(xs) - min(xs), (max(ys) - min(ys)) * aspect) * 1.04
    cam.location += right * (max(xs) + min(xs)) / 2 + up * (max(ys) + min(ys)) / 2
    sc.camera = cam
    path.parent.mkdir(parents=True, exist_ok=True)
    sc.render.filepath = str(path)
    bpy.ops.render.render(write_still=True)
    print(f'SHEET {path}', flush=True)


def validate():
    """Re-import every FBX of the set into an empty scene and check it against the
    manifest and the contract again (check_piece on the re-imported boxes): names,
    boxes within 0.02 stud, triangles, one material, UVs. Writes validation.json.
    It checks nothing in Studio."""
    out = ROOT / 'blender' / SET_DIR
    manifest = json.loads((out / 'manifest.json').read_text())
    report = {'set': SET_DIR, 'checked': 'each fbx/<Name>.fbx re-imported into Blender; nothing here ran in Studio',
              'pieces': {}}
    failed = []
    pieces = {piece.name: piece for piece, _, _ in BUILT}
    if ONLY is not None and (out / 'validation.json').exists():
        report['pieces'] = json.loads((out / 'validation.json').read_text())['pieces']
    for name, rec in manifest['pieces'].items():
        if name not in pieces:
            continue
        for ob in list(bpy.data.objects):
            bpy.data.objects.remove(ob)
        for coll in (bpy.data.meshes, bpy.data.materials, bpy.data.images, bpy.data.cameras):
            for x in list(coll):
                if x.users == 0:
                    coll.remove(x)
        bpy.context.scene.unit_settings.scale_length = .01
        bpy.ops.import_scene.fbx(filepath=str(out / 'fbx' / f'{name}.fbx'))
        meshes = {o.name: o for o in bpy.context.scene.objects if o.type == 'MESH'}
        faults, checks = [], []
        lost, extra = sorted(set(rec['parts']) - set(meshes)), sorted(set(meshes) - set(rec['parts']))
        if lost or extra:
            faults.append(f'part names differ: missing {lost}, unexpected {extra}')
        else:
            checks.append(f'{len(meshes)} part names round-trip')
        boxes, tris = {}, {}
        for pname, ob in meshes.items():
            corners = [bl2rb(ob.matrix_world @ Vector(c)) for c in ob.bound_box]
            lo, hi = _bounds(corners)
            want = rec['parts'].get(pname)
            ob.data.calc_loop_triangles()
            tris[pname] = len(ob.data.loop_triangles)
            if want:
                boxes[pname] = (lo, hi, want['collide'])
                if ((lo + hi) / 2 - Vector(want['centre'])).length > 0.02 or (hi - lo - Vector(want['size'])).length > 0.02:
                    faults.append(f'{pname}: box {v3(hi - lo, 3)} at {v3((lo + hi) / 2, 3)} after the round trip, '
                                  f'built {want["size"]} at {want["centre"]}')
                if tris[pname] != want['triangles']:
                    faults.append(f'{pname}: {tris[pname]} triangles, built {want["triangles"]}')
            if len(ob.data.uv_layers) != 1:
                faults.append(f'{pname}: {len(ob.data.uv_layers)} UV layers')
            if len(ob.data.materials) != 1:
                faults.append(f'{pname}: {len(ob.data.materials)} materials')
        checks.append('every box within 0.02 stud and every triangle count as built (orientation and scale)')
        has_image = any(img.size[0] > 0 for img in bpy.data.images)
        (checks if has_image else faults).append('the atlas travels embedded in the FBX' if has_image
                                                 else 'no image came back from the FBX')
        piece = pieces[name]
        if getattr(piece, 'checks', None):
            bpy.context.view_layer.update()
            tris_rb = {pname: _tris_rb(ob) for pname, ob in meshes.items()}
            for fn in piece.checks:
                faults += fn(piece, tris_rb, 'fbx')
            checks.append('the piece\'s own checks re-run on the re-imported triangles')
        check_piece(piece, boxes, tris, faults)
        checks.append('the contract re-checked on the re-imported boxes: Root, footprint, wall boxes = blockout, '
                      'door opening 4 x 7, Door -> Bed walk for a 5-stud person, decor slots, budgets'
                      if piece.kind in ('Room', 'Amenity') else
                      'the contract re-checked on the re-imported boxes (Root, footprint, kind rules, budgets)')
        report['pieces'][name] = {'ok': not faults, 'faults': faults, 'checks': checks,
                                  'triangles': rec['triangles'], 'budget': rec['budget'],
                                  'collision_precise': rec['collision_precise'],
                                  'attachments': sorted(rec['attachments'])}
        if faults:
            failed.append(name)
    report['collision_precise'] = {n: r['collision_precise'] for n, r in manifest['pieces'].items()}
    report['not_validated'] = [
        'anything in Studio: the import, the axis conversion on Roblox\'s side (import_fixup.luau checks it first), '
        'the atlas upload, how it looks lit',
        'walking: the stair walked boxes are identical to the walker-proven blockout\'s, but no walker has run on '
        'the imported meshes',
        'the attachments exist only in manifest.json until import_fixup.luau makes them',
    ]
    (out / 'validation.json').write_text(json.dumps(report, indent=1))
    print(f'VALIDATED {len(pieces) - len(failed)}/{len(pieces)} built now; failed {failed}', flush=True)
    assert not failed, f'validation failed: {failed}'
    return report


def _lua_v(v):
    return 'Vector3.new(%s)' % ', '.join(f'{c:g}' for c in v)


def _fixup_luau(path, manifest):
    """The Luau that turns an import into the contract: run in Studio's Edit
    datamodel after August imports the batch into Workspace (skill `import`, step 2)."""
    lines = [
        '-- Generated by tools/hotel_kit.py from manifest.json: do not edit by hand.',
        '-- Step 2 of skill `import`, in the Edit datamodel, after the batch is imported into Workspace.',
        '-- For each model: checks every part against the manifest (an axis or mirror fault stops it,',
        '-- touching nothing), flattens it, makes Root the invisible PrimaryPart with the pivot on the',
        '-- piece origin, makes every attachment on Root, sets Anchored, CanCollide, CanQuery, CanTouch,',
        '-- CollisionFidelity (Box, or Precise for collision_precise), the glows (Neon, colour, a light),',
        '-- and hides LOD_Proxy. Read back in a SEPARATE call (the second chunk at the end).',
        'local ONLY = {} -- model names to do this call, or empty for every one found in Workspace',
        'local GLOW = {',
    ]
    for k, (r, g, b) in GLOW_COLOURS.items():
        lines.append(f'\t{k} = Color3.fromRGB({r}, {g}, {b}),')
    lines += ['}', 'local SET = {']
    for name, rec in manifest['pieces'].items():
        lines.append(f'\t{name} = {{')
        lines.append(f'\t\troot = {_lua_v(rec["root"]["centre"])},')
        lines.append('\t\tparts = {')
        for p, pr in rec['parts'].items():
            lines.append(f'\t\t\t{p} = {{ c = {_lua_v(pr["centre"])}, s = {_lua_v(pr["size"])}, '
                         f'collide = {str(pr["collide"]).lower()} }},')
        lines.append('\t\t},')
        lines.append('\t\tatt = {')
        for a, ar in rec['attachments'].items():
            look = _lua_v(ar['look']) if ar['look'] else 'nil'
            lines.append(f'\t\t\t{{ "{a}", {_lua_v(ar["pos"])}, {look} }},')
        lines.append('\t\t},')
        lines.append('\t\tprecise = { %s },' % ', '.join(f'"{p}"' for p in rec['collision_precise']))
        lines.append('\t},')
    lines.append('}')
    lines.append(r'''
local out = {}
for name, spec in SET do
	if #ONLY > 0 and not table.find(ONLY, name) then
		continue
	end
	local m = workspace:FindFirstChild(name)
	if not (m and m:IsA("Model")) then
		continue
	end
	local parts = {}
	for _, d in m:GetDescendants() do
		if d:IsA("MeshPart") then
			parts[d.Name] = d
		end
	end
	local root = parts.Root
	if not root then
		table.insert(out, `{name}: NO Root, untouched`)
		continue
	end
	-- The piece origin in the world, from Root's centre; every part must sit where the manifest says.
	local origin = root.Position - spec.root
	local bad = {}
	for pname, ps in spec.parts do
		local p = parts[pname]
		if not p then
			table.insert(bad, `missing {pname}`)
		elseif (p.Position - (origin + ps.c)).Magnitude > 0.15 or (p.Size - ps.s).Magnitude > 0.15 then
			table.insert(bad, `{pname} at {p.Position - origin} size {p.Size}, manifest {ps.c} size {ps.s}`)
		end
	end
	for pname in parts do
		if not spec.parts[pname] then
			table.insert(bad, `unexpected {pname}`)
		end
	end
	if #bad > 0 then
		table.insert(out, `{name}: STOPPED, nothing changed (mirrored or turned? see hotel_kit.rb2bl): ` .. table.concat(bad, "; "))
		continue
	end
	local precise = {}
	for _, p in spec.precise do
		precise[p] = true
	end
	for pname, p in parts do
		local ps = spec.parts[pname]
		p.Parent = m
		p.Anchored = true
		p.CanCollide = ps.collide
		p.CanQuery = ps.collide
		p.CanTouch = false
		p.CollisionFidelity = if precise[pname] then Enum.CollisionFidelity.PreciseConvexDecomposition
			else Enum.CollisionFidelity.Box
		local key = string.match(pname, "^Glow_(%a+)_%d+$")
		if key then
			for _, c in p:GetChildren() do
				if c:IsA("SurfaceAppearance") then
					c:Destroy()
				end
			end
			p.TextureID = ""
			p.Material = Enum.Material.Neon
			p.Color = GLOW[key] or GLOW.Warm
			p.CastShadow = false
			if string.match(pname, "_1$") and not p:FindFirstChildOfClass("PointLight") then
				local light = Instance.new("PointLight")
				light.Range = 12
				light.Brightness = 0.6
				light.Color = p.Color
				light.Shadows = false
				light.Parent = p
			end
		end
	end
	for _, d in m:GetChildren() do -- empty groups the importer made
		if (d:IsA("Model") or d:IsA("Folder")) and #d:GetDescendants() == 0 then
			d:Destroy()
		end
	end
	root.Transparency = 1
	root.CastShadow = false
	for _, c in root:GetChildren() do
		if c:IsA("SurfaceAppearance") or c:IsA("Attachment") then
			c:Destroy()
		end
	end
	if parts.LOD_Proxy then
		parts.LOD_Proxy.Transparency = 1
		parts.LOD_Proxy.CastShadow = false
	end
	m.PrimaryPart = root
	root.PivotOffset = CFrame.new(-spec.root)
	for _, a in spec.att do
		local att = Instance.new("Attachment")
		att.Name = a[1]
		local rel = a[2] - spec.root
		att.CFrame = if a[3] then CFrame.lookAt(rel, rel + a[3]) else CFrame.new(rel)
		att.Parent = root
	end
	table.insert(out, `{name}: set, {#spec.att} attachments`)
end
return table.concat(out, "\n")

--[[ 2: READ BACK, in a separate call (CollisionFidelity shows a call late):
local out = {}
for _, m in workspace:GetChildren() do
	if m:IsA("Model") and m.PrimaryPart and m.PrimaryPart.Name == "Root" then
		local box, precise, default, atts = 0, 0, 0, 0
		for _, p in m:GetDescendants() do
			if p:IsA("MeshPart") then
				local f = p.CollisionFidelity
				if f == Enum.CollisionFidelity.Box then box += 1
				elseif f == Enum.CollisionFidelity.PreciseConvexDecomposition then precise += 1
				else default += 1 end
			elseif p:IsA("Attachment") then atts += 1 end
		end
		local proxy = m:FindFirstChild("LOD_Proxy")
		table.insert(out, `{m.Name}: Box {box}, Precise {precise}, Default {default}, attachments {atts}, `
			.. `Root hidden {m.PrimaryPart.Transparency == 1}, proxy hidden {proxy == nil or proxy.Transparency == 1}`)
	end
end
return table.concat(out, "\n")
]]
''')
    path.write_text('\n'.join(lines), encoding='utf-8')
    print(f'FIXUP {path}', flush=True)
