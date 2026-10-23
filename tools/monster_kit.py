"""Everything a monster build script needs that is not the monster's own shape.

A build script on this kit is, per species, its shapes and a call to finish():
the mesh helpers (balls, lathes, limbs, prisms, arc shells), the part colours,
the Root, the LOD_Proxy, the contract checks, the FBX export, the manifest,
the validator and the one Workbench contact sheet all live here. If a monster
needs something new that is not its own shape, it goes here.

Frame (lifted from Sector Omega's ship_kit.py): Blender -Y is the monster's
front, +Z up, +X the monster's LEFT, 1 unit = 1 stud, exported with
axis_forward -Z / axis_up Y and unit scale 0.01, so the face arrives facing
Roblox -Z. A Blender point (x, y, z) is Roblox (-x, z, y) in the model's frame
(roblox()). Origin: on the floor (z = 0) between the feet, or under the body of
a floater.

MODELS.md, "Monsters and street NPCs", as finish() enforces it:
- `Body`: one part, the species' colour (Species.luau `look.colour`).
- `Glow_Eyes_1` (the monster's left, +X) and `Glow_Eyes_2`, their own parts.
- `Nameplate` and `Hand`: an FBX carries no attachments, so each arrives as a
  0.2-stud marker part centred on the place; the import step turns it into an
  Attachment of that name under `Root` and deletes the part (README).
- `Root`: made by finish(), 2 x height x 2, bottom at y = 0.
- `LOD_Proxy`: made by finish() from the finished model, <= 300 triangles.
- Any other part is one flat colour, merged by colour (rule 7), named from
  EXTRA_PARTS. No textures: an imported SurfaceAppearance would stop a
  mutation's Material and Color from landing (DEVNOTES.md).
- 4,000 triangles without the proxy, height within 10 % of `look.height`, no
  coplanar faces between pieces, every part closed.

Street NPCs (`NPCS`) and street scenery (trees, registered by a set's script
with `scenery()`) are begun and finished the same way, each kind with its own
checks in finish() and validate().

Run headless only, e.g.
    blender -b --python-exit-code 1 -P tools/build_monsters_l1.py
`-- norender` skips the contact sheet. The sheet is Workbench only, one image.
"""
import bpy
import bmesh
import itertools
import json
import math
import re
import sys
from pathlib import Path

import numpy as np
from mathutils import Matrix, Vector

ROOT = Path(__file__).resolve().parents[1]
ARGS = sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else []
NORENDER = 'norender' in ARGS

MONSTER_BUDGET = 4000      # MODELS.md, "What a model costs to draw": a monster
PROXY_BUDGET = 300         # ... plus LOD_Proxy 300
MESH_TRIANGLE_CAP = 20000  # Roblox's per-MeshPart import cap (long 20,000; MODELS.md says confirm)
HEIGHT_TOL = 0.10          # the brief: within 10 % of Species.luau's look.height
MARKER = 0.2               # a marker part's edge
PERSON = 5.0               # CLAUDE.md, "The scale of a person"
GLOW_WORDS = ('Warm', 'Cold', 'Eyes', 'Magic')   # MODELS.md rule 1, the code's palette keys
# Parts beyond the contract's, each one flat colour (merged by colour, rule 7).
# Not in MODELS.md yet: the report asks for them to be written there.
EXTRA_PARTS = ('Skin', 'Trim', 'Dark', 'Light')
MARKERS = ('Nameplate', 'Hand')
PART_RE = re.compile(r'^(Root|Body|LOD_Proxy|Nameplate|Hand|Skin|Trim|Dark|Light|Glow_(%s)_\d+)$'
                     % '|'.join(GLOW_WORDS))

# --- Street NPCs (MODELS.md, "Hunters (`Hunter`) and the bus (`NightBus`)") -------------
# The same frame and Root rule as a monster, their own contract. A street model is
# begun like a species (begin('Hunter', ...)) and finished by the same finish();
# its target comes from here instead of Species.luau, from the client blockouts it
# replaces (HunterRenderer.luau: Root 2 x 5 x 2; BusRenderer.luau: Root 24 x 9 x 8).
# `root` is the Root's size in Blender (x, y, z); `front` is the part that must be
# ahead of the Body along `facing` (Blender), so a model cannot face the wrong way.
BUS_BUDGET, BUS_PROXY_BUDGET = 8000, 500     # MODELS.md, "What a model costs to draw": the bus
VEHICLE_MARKERS = ('Door',)
ALL_MARKERS = MARKERS + VEHICLE_MARKERS
STREET_PART_RE = re.compile(r'^(Root|Body|LOD_Proxy|Nameplate|Hand|Door|Skin|Trim|Dark|Light|Wheel_\d+|Glow_(%s)_\d+)$'
                            % '|'.join(GLOW_WORDS))
NPCS = {
    # A hunter is a person: budgeted like a monster (MODELS.md names no hunter budget).
    'Hunter': {'kind': 'npc', 'height': PERSON, 'colour': None, 'eyes': None, 'shape': 'Biped', 'location': 0,
               'need': ('Body', 'Nameplate', 'Glow_Warm_1'), 'front': 'Glow_Warm_1', 'facing': (0, -1, 0),
               'root': (2, 2, PERSON), 'budget': MONSTER_BUDGET, 'proxy': PROXY_BUDGET},
    # The bus faces +X in Roblox, which is Blender -X; its Root is the bus's size.
    'NightBus': {'kind': 'vehicle', 'height': 9.0, 'colour': None, 'eyes': None, 'shape': 'Vehicle', 'location': 0,
                 'need': ('Body', 'Door', 'Glow_Warm_1'), 'front': 'Glow_Warm_2', 'facing': (-1, 0, 0),
                 'root': (24, 8, 9), 'budget': BUS_BUDGET, 'proxy': BUS_PROXY_BUDGET},
}

# --- Street scenery: trees (MODELS.md, "Street scenery: trees") ------------------------
# A tree is begun and finished like a street NPC, kind 'tree': no front, a column
# Root (the trunk's foot x the height, the code's only collider), at most six parts,
# 800 triangles and a 100-triangle proxy. Its target (height, Root) is the set's
# own: a build script registers each with scenery() before begin().
TREE_BUDGET, TREE_PROXY_BUDGET = 800, 100
TREE_MAX_PARTS = 6
TREE_HEIGHTS = (22.0, 40.0)    # MODELS.md: beside a 54-stud hotel of three floors
SCENERY = {}


def scenery(sid, height, foot, need=('Body',), proxy_colour=None):
    """Register a tree `sid` (`Tree_<Name>`): `height` in studs, `foot` the trunk's
    width at the ground (the Root column's side), `need` the parts it must have,
    `proxy_colour` (sRGB) the far proxy's colour when the Body's is not what the
    tree reads as from afar (a fir's needles, not its trunk)."""
    assert re.match(r'^Tree_[A-Z][A-Za-z]+$', sid), f'{sid}: a tree is named Tree_<Name>'
    assert TREE_HEIGHTS[0] <= height <= TREE_HEIGHTS[1], f'{sid}: {height} studs, MODELS.md says {TREE_HEIGHTS}'
    SCENERY[sid] = {'kind': 'tree', 'height': height, 'colour': None, 'eyes': None, 'shape': 'Tree',
                    'location': 0, 'need': tuple(need), 'front': None, 'facing': None,
                    'root': (foot, foot, height), 'budget': TREE_BUDGET, 'proxy': TREE_PROXY_BUDGET,
                    'proxy_colour': proxy_colour}


# --- Species.luau: the targets the code draws today ---------------------------------
def species_table():
    """{id: {height, colour (sRGB 0-255), eyes, shape}} read from src/shared/Species.luau,
    so a target never drifts from the code's."""
    text = (ROOT / 'src' / 'shared' / 'Species.luau').read_text(encoding='utf-8')
    out = {}
    starts = [m for m in re.finditer(r'id = "(\w+)"', text)]
    for i, m in enumerate(starts):
        block = text[m.end(): starts[i + 1].start() if i + 1 < len(starts) else len(text)]
        rgb = lambda key: (lambda g: tuple(int(c) for c in g.groups()) if g else None)(
            re.search(key + r' = Color3\.fromRGB\((\d+),\s*(\d+),\s*(\d+)\)', block))
        h = re.search(r'height = ([\d.]+)', block)
        shape = re.search(r'shape = "(\w+)"', block)
        loc = re.search(r'location = (\d+)', block)
        out[m.group(1)] = {'height': float(h.group(1)), 'colour': rgb('colour'), 'eyes': rgb('eyes'),
                           'shape': shape.group(1), 'location': int(loc.group(1))}
    return out


SPECIES = species_table()


def srgb_to_linear(c):
    c = c / 255.0
    return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4


def roblox(v):
    """A Blender point in the model's frame as Roblox (x, y, z) in the model's frame."""
    return [round(-v[0], 4), round(v[2], 4), round(v[1], 4)]


# --- The model being built ------------------------------------------------------------
class _Model:
    def __init__(self, sid, set_dir, colours):
        self.id, self.set_dir = sid, set_dir
        self.target = SPECIES[sid] if sid in SPECIES else NPCS[sid] if sid in NPCS else SCENERY[sid]
        self.kind = self.target.get('kind', 'monster')
        self.part_re = PART_RE if self.kind == 'monster' else STREET_PART_RE
        self.marker_names = MARKERS if self.kind == 'monster' else ALL_MARKERS
        self.budget = self.target.get('budget', MONSTER_BUDGET)
        self.proxy_budget = self.target.get('proxy', PROXY_BUDGET)
        self.out = ROOT / 'blender' / set_dir
        self.coll = bpy.data.collections.new(sid)
        bpy.context.scene.collection.children.link(self.coll)
        self.pieces = {}          # part -> [objects]
        self.colours = {'Body': self.target['colour'], 'Root': (128, 128, 128),
                        'Nameplate': (255, 0, 255), 'Hand': (255, 0, 255), 'Door': (255, 0, 255),
                        'Dark': (45, 32, 60), 'Light': (255, 255, 255)}   # eyes()' pupils and glints
        self.colours['Glow_Eyes_1'] = self.colours['Glow_Eyes_2'] = self.target['eyes'] or (255, 255, 255)
        self.colours.update(colours or {})
        self.markers = {}
        self.looks = {}           # marker -> the way its attachment faces (Blender), street models
        self.count = 0


m = None          # the model begin() made; every helper below adds to it
_done = []        # manifest records of the finished models, in build order


def start_set(set_dir):
    """An empty scene for a set of monsters writing to blender/<set_dir>/."""
    bpy.ops.wm.read_factory_settings(use_empty=True)
    scene = bpy.context.scene
    scene.unit_settings.system = 'METRIC'
    scene.unit_settings.scale_length = .01
    out = ROOT / 'blender' / set_dir
    for p in (out, out / 'fbx', out / 'review'):
        p.mkdir(parents=True, exist_ok=True)
    _done.clear()
    return out


def begin(sid, set_dir, colours=None):
    """Start the species `sid` (a Species.luau id). `colours` gives the extra parts'
    and glows' colours, sRGB 0-255, e.g. {'Dark': (40, 30, 50)}; Body and the eyes
    default to Species.luau's look."""
    global m
    assert sid in SPECIES or sid in NPCS or sid in SCENERY, \
        f'{sid} is not a species id in Species.luau, a street NPC nor a registered tree'
    m = _Model(sid, set_dir, colours)
    assert m.colours['Body'] is not None, f'{sid}: a street NPC\'s Body colour is given to begin()'
    return m.target['height']


def _material(part):
    key = f'{m.id}_{part}'
    mat = bpy.data.materials.get(key) or bpy.data.materials.new(key)
    lin = tuple(srgb_to_linear(c) for c in m.colours[part])
    mat.diffuse_color = (*lin, 1)
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes.get('Principled BSDF')
    bsdf.inputs['Base Color'].default_value = (*lin, 1)
    bsdf.inputs['Roughness'].default_value = 0.6
    return mat


def _object(part, bm, name=None):
    assert m.part_re.match(part), f'{part}: not a name the contract allows ({m.part_re.pattern})'
    assert part in m.colours, f'{part}: no colour given to begin()'
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    m.count += 1
    name = name or f'{m.id}.{part}.{m.count}'
    me = bpy.data.meshes.new(name)
    bm.to_mesh(me)
    bm.free()
    me.materials.append(_material(part))
    ob = bpy.data.objects.new(name, me)
    m.coll.objects.link(ob)
    m.pieces.setdefault(part, []).append(ob)
    return ob


def _matrix(at=(0, 0, 0), rot=(0, 0, 0), scale=(1, 1, 1)):
    r = Matrix.Identity(4)
    for axis, deg in zip('XYZ', rot):
        if deg:
            r = Matrix.Rotation(math.radians(deg), 4, axis) @ r
    s = Matrix.Diagonal((*scale, 1))
    return Matrix.Translation(at) @ r @ s


def rings(part, spec, n=16, wave=None, matrix=None, name=None, radial=None):
    """A closed solid through horizontal rings, bottom to top: `spec` is
    [(cx, cy, z, rx, ry)] (ry may be left out); a ring of radius 0 is a pole.
    `wave` {ring index: f(theta) -> dz} lifts one ring's points (a ghost's hem).
    Theta 0 is +X; the front (-Y) is theta -90. `radial` f(theta) scales every
    ring's radius (a pumpkin's ribs)."""
    bm = bmesh.new()
    loops = []
    for k, row in enumerate(spec):
        cx, cy, z, rx = row[:4]
        ry = row[4] if len(row) > 4 else rx
        if rx <= 1e-6:
            loops.append([bm.verts.new((cx, cy, z))])
            continue
        ring = []
        for i in range(n):
            t = 2 * math.pi * i / n
            dz = wave[k](t) if wave and k in wave else 0.0
            f = radial(t) if radial else 1.0
            ring.append(bm.verts.new((cx + f * rx * math.cos(t), cy + f * ry * math.sin(t), z + dz)))
        loops.append(ring)
    for a, b in zip(loops, loops[1:]):
        if len(a) == 1 and len(b) == 1:
            continue
        for i in range(n):
            j = (i + 1) % n
            if len(a) == 1:
                bm.faces.new((a[0], b[i], b[j]))
            elif len(b) == 1:
                bm.faces.new((a[i], a[j], b[0]))
            else:
                bm.faces.new((a[i], a[j], b[j], b[i]))
    if len(loops[0]) > 1:
        bm.faces.new(list(reversed(loops[0])))
    if len(loops[-1]) > 1:
        bm.faces.new(loops[-1])
    if matrix is not None:
        bm.transform(matrix)
    return _object(part, bm, name)


def lathe(part, profile, at=(0, 0, 0), n=16, sy=1.0, wave=None, rot=(0, 0, 0)):
    """Revolve [(z, r)] about the vertical through `at`, squashed front-to-back by `sy`."""
    spec = [(0, 0, z, r, r * sy) for z, r in profile]
    return rings(part, spec, n, wave, _matrix(at, rot))


def ball(part, at, r, n=12, k=6, rot=(0, 0, 0), name=None, radial=None):
    """An ellipsoid of radii `r` (a number or (rx, ry, rz)) centred on `at`."""
    rx, ry, rz = (r, r, r) if isinstance(r, (int, float)) else r
    spec = [(0, 0, -math.cos(math.pi * i / k), math.sin(math.pi * i / k)) for i in range(k + 1)]
    spec[0] = (0, 0, -1, 0)
    spec[-1] = (0, 0, 1, 0)
    return rings(part, spec, n, matrix=_matrix(at, rot, (rx, ry, rz)), name=name, radial=radial)


def on_ball(at, r, x, z, out=0.0):
    """The point on the front (-Y) of the ellipsoid ball(at, r) at (x, z), moved
    `out` along -Y: where a feature on a head sits."""
    rx, ry, rz = (r, r, r) if isinstance(r, (int, float)) else r
    q = 1 - ((x - at[0]) / rx) ** 2 - ((z - at[2]) / rz) ** 2
    assert q > 0, f'({x}, {z}) is off the ball'
    return Vector((x, at[1] - ry * math.sqrt(q) - out, z))


def limb(part, p0, p1, r0, r1=None, n=10):
    """A capsule from p0 to p1, radius r0 tapering to r1, rounded at both ends."""
    r1 = r0 if r1 is None else r1
    p0, p1 = Vector(p0), Vector(p1)
    d = p1 - p0
    L = d.length
    c = math.cos(math.radians(45))
    prof = [(-r0, 0), (-r0 * c, r0 * c), (0, r0), (L, r1), (L + r1 * c, r1 * c), (L + r1, 0)]
    rot = Vector((0, 0, 1)).rotation_difference(d.normalized()).to_matrix().to_4x4()
    return rings(part, [(0, 0, z, r) for z, r in prof], n, matrix=Matrix.Translation(p0) @ rot)


def box(part, at, size, bevel=0.0, rot=(0, 0, 0)):
    """A box, its edges rounded by `bevel` (two segments)."""
    bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=1.0)
    for v in bm.verts:
        v.co = Vector((v.co.x * size[0], v.co.y * size[1], v.co.z * size[2]))
    if bevel:
        bmesh.ops.bevel(bm, geom=list(bm.edges), offset=bevel, segments=2, profile=0.5, affect='EDGES')
    bm.transform(_matrix(at, rot))
    return _object(part, bm)


def prism(part, outline, y_front, depth, rot=(0, 0, 0), pivot=None):
    """A flat-faced solid from a convex outline of (x, z) points, its front face
    at y = `y_front` and `depth` deep toward +Y (a carved eye standing proud of
    a face)."""
    bm = bmesh.new()
    front = [bm.verts.new((x, y_front, z)) for x, z in outline]
    back = [bm.verts.new((x, y_front + depth, z)) for x, z in outline]
    bm.faces.new(front)
    bm.faces.new(list(reversed(back)))
    n = len(outline)
    for i in range(n):
        j = (i + 1) % n
        bm.faces.new((front[j], front[i], back[i], back[j]))
    if any(rot):
        c = Vector(pivot or (sum(x for x, _ in outline) / n, y_front, sum(z for _, z in outline) / n))
        bm.transform(Matrix.Translation(c) @ _matrix(rot=rot) @ Matrix.Translation(-c))
    return _object(part, bm)


def arc_shell(part, profile, t0, t1, thick, at=(0, 0, 0), n=14, sy=1.0):
    """A closed shell of `thick` between angles t0 and t1 (degrees, 0 = +X, the
    back is +90) through [(z, r_outer)] rows, bottom to top: a cape, a collar."""
    bm = bmesh.new()
    ax, ay, az = at
    grid = []
    for z, r in profile:
        row = []
        for i in range(n + 1):
            t = math.radians(t0 + (t1 - t0) * i / n)
            row.append((bm.verts.new((ax + r * math.cos(t), ay + r * sy * math.sin(t), az + z)),
                        bm.verts.new((ax + (r - thick) * math.cos(t), ay + (r - thick) * sy * math.sin(t), az + z))))
        grid.append(row)
    for a, b in zip(grid, grid[1:]):
        for i in range(n):
            bm.faces.new((a[i][0], a[i + 1][0], b[i + 1][0], b[i][0]))
            bm.faces.new((a[i][1], b[i][1], b[i + 1][1], a[i + 1][1]))
    for row, flip in ((grid[0], False), (grid[-1], True)):
        for i in range(n):
            q = (row[i][0], row[i][1], row[i + 1][1], row[i + 1][0])
            bm.faces.new(tuple(reversed(q)) if flip else q)
    for i, flip in ((0, False), (n, True)):
        for a, b in zip(grid, grid[1:]):
            q = (a[i][0], b[i][0], b[i][1], a[i][1])
            bm.faces.new(tuple(reversed(q)) if flip else q)
    return _object(part, bm)


def pair(fn, *args, **kw):
    """Call `fn` twice, mirrored across x: every argument named in `kw['mirror']`
    (a point or a list of points) has its x negated on the second call."""
    keys = kw.pop('mirror')
    out = [fn(*args, **kw)]
    kw2 = dict(kw)
    for key in keys:
        v = kw[key]
        if isinstance(v[0], (list, tuple)):
            kw2[key] = [(-p[0], *p[1:]) for p in v]
        else:
            kw2[key] = (-v[0], *v[1:])
    if 'rot' in kw:
        rx, ry, rz = kw['rot']
        kw2['rot'] = (rx, -ry, -rz)
    out.append(fn(*args, **kw2))
    return out


def front_y(profile, z, x=0.0, at=(0, 0, 0), sy=1.0, out=0.0):
    """Where the front (-Y) surface of a lathe(profile, at, sy) is at height z and
    offset x: the y a feature sits on."""
    zs = [p[0] for p in profile]
    rs = [p[1] for p in profile]
    r = float(np.interp(z - at[2], zs, rs))
    x -= at[0]
    if abs(x) >= r:
        return at[1] - out
    return at[1] - sy * math.sqrt(r * r - x * x) - out


def eyes(at, r, pupil=0.55, shine=True, rr=None):
    """Glow_Eyes_1 at `at` (the monster's left, +X) and Glow_Eyes_2 mirrored,
    each a ball of `r` (or radii `rr`), with a Dark pupil sunk into its front
    and a Light highlight on the pupil, so they read big and cute."""
    rx, ry, rz = rr or (r, r * 0.8, r)
    for i, side in ((1, 1), (2, -1)):
        c = Vector((side * abs(at[0]), at[1], at[2]))
        ball(f'Glow_Eyes_{i}', c, (rx, ry, rz), n=14, k=7)
        if pupil:
            pc = c + Vector((0, -ry * 0.62, -rz * 0.05))
            ball('Dark', pc, (rx * pupil, ry * 0.45, rz * pupil * 1.1), n=12, k=6)
            if shine:
                ball('Light', pc + Vector((side * rx * 0.18, -ry * 0.38, rz * pupil * 0.45)),
                     rx * 0.17, n=8, k=4)


def marker(name, at, look=None):
    """A contract place (MODELS.md: `Nameplate`, `Hand`; a street model's `Door`)
    as a 0.2 marker part centred on it; the import step makes it an Attachment
    under Root. `look` (Blender) is the way the attachment faces, written to the
    manifest and set by the import step (a marker part's rotation is lost)."""
    assert name in m.marker_names, name
    bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=MARKER)
    bm.transform(Matrix.Translation(at))
    m.markers[name] = Vector(at)
    if look is not None:
        m.looks[name] = Vector(look).normalized()
    return _object(name, bm, name=f'{m.id}.{name}')


def tube(part, pts, r, n=10, closed=False, up=None, name=None):
    """A tube through the polyline `pts`, radius `r` (a number, or one per point):
    a serpent's coil, a string, a hoop. Open ends are rounded shut; `closed`
    joins the last ring to the first (a ring). Ring frames follow the path
    (parallel transport, the first ring's vertex 0 pointing down, so a tube
    lying on the floor touches it); `up` (the plane's normal of a flat loop)
    fixes them instead, which a closed loop needs so it does not twist."""
    P = [Vector(p) for p in pts]
    N = len(P)
    R = list(r) if isinstance(r, (list, tuple)) else [r] * N
    assert len(R) == N and N >= 2
    T = []
    for i in range(N):
        d = (P[(i + 1) % N] - P[i - 1]) if closed else (P[min(i + 1, N - 1)] - P[max(i - 1, 0)])
        T.append(d.normalized())
    frames = []
    if up is not None:
        U = Vector(up)
        for t in T:
            nrm = U - U.dot(t) * t
            assert nrm.length > 1e-6, 'tube: the path runs along `up`'
            nrm.normalize()
            frames.append((nrm, t.cross(nrm)))
    else:
        U = Vector((0, 0, -1))
        nrm = U - U.dot(T[0]) * T[0]
        if nrm.length < 1e-6:
            nrm = Vector((1, 0, 0)) - T[0].x * T[0]
        nrm.normalize()
        for i, t in enumerate(T):
            if i:
                nrm = nrm - nrm.dot(t) * t
                nrm.normalize()
            frames.append((nrm, t.cross(nrm)))
    bm = bmesh.new()

    def ring(c, rad, f):
        a, b = f
        return [bm.verts.new(c + rad * (math.cos(2 * math.pi * j / n) * a + math.sin(2 * math.pi * j / n) * b))
                for j in range(n)]

    loops = [ring(P[i], R[i], frames[i]) for i in range(N)]
    if not closed:
        loops = ([[bm.verts.new(P[0] - T[0] * R[0])], ring(P[0] - T[0] * R[0] * 0.6, R[0] * 0.8, frames[0])]
                 + loops + [ring(P[-1] + T[-1] * R[-1] * 0.6, R[-1] * 0.8, frames[-1]),
                            [bm.verts.new(P[-1] + T[-1] * R[-1])]])
    seq = list(zip(loops, loops[1:]))
    if closed:
        seq.append((loops[-1], loops[0]))
    for A, B in seq:
        for j in range(n):
            k_ = (j + 1) % n
            if len(A) == 1:
                bm.faces.new((A[0], B[k_], B[j]))
            elif len(B) == 1:
                bm.faces.new((A[j], A[k_], B[0]))
            else:
                bm.faces.new((A[j], A[k_], B[k_], B[j]))
    return _object(part, bm, name)


# --- Checks -------------------------------------------------------------------------
def _tris(ob):
    deps = bpy.context.evaluated_depsgraph_get()
    bm = bmesh.new()
    bm.from_object(ob, deps)
    bm.transform(ob.matrix_world)
    bmesh.ops.triangulate(bm, faces=bm.faces)
    out = [np.array([tuple(v.co) for v in f.verts]) for f in bm.faces]
    bm.free()
    return out


def coplanar_overlaps(objs):
    """Faces of different pieces lying in one plane, facing the same way and
    overlapping: they z-fight in Roblox. Lifted from Sector Omega's
    ship_kit._coplanar_overlaps (broad phase on a 0.01 (normal, offset) grid,
    exact test by separating axes). Returns {"A / B": (faces, a point)}."""
    tris = []
    for o in objs:
        tris += [(o.name, P) for P in _tris(o)]
    cell = 0.01
    normals, buckets = [], {}
    for i, (_, P) in enumerate(tris):
        n = np.cross(P[1] - P[0], P[2] - P[0])
        a = np.linalg.norm(n)
        if a <= 1e-8:
            normals.append(None)
            continue
        n /= a
        normals.append(n)
        key = np.concatenate([n, [n @ P[0]]]) / cell
        lo, hi = np.floor(key - 0.5).astype(int), np.floor(key + 0.5).astype(int)
        for corner in itertools.product(*[(int(l),) if l == h else (int(l), int(h)) for l, h in zip(lo, hi)]):
            buckets.setdefault(corner, []).append(i)

    def overlap(A, B, na, nb):
        if na @ nb < 1 - 1e-6:
            return False
        if max(np.abs((B - A[0]) @ na).max(), np.abs((A - B[0]) @ nb).max()) > 1e-4:
            return False
        u = np.cross(na, (1, 0, 0) if abs(na[0]) < 0.9 else (0, 1, 0))
        u /= np.linalg.norm(u)
        w = np.cross(na, u)
        a, b = np.stack([A @ u, A @ w], 1), np.stack([B @ u, B @ w], 1)
        for poly in (a, b):
            for k in range(3):
                e = poly[(k + 1) % 3] - poly[k]
                axis = np.array([-e[1], e[0]])
                pa, pb = a @ axis, b @ axis
                if pa.max() <= pb.min() + 1e-3 or pb.max() <= pa.min() + 1e-3:
                    return False
        return True

    found, seen, done = {}, set(), set()
    for idx in buckets.values():
        members = frozenset(idx)
        if len(idx) < 2 or members in done:
            continue
        done.add(members)
        for x in range(len(idx)):
            for y in range(x + 1, len(idx)):
                i, j = idx[x], idx[y]
                if (i, j) in seen:
                    continue
                seen.add((i, j))
                (na, A), (nb, B) = tris[i], tris[j]
                if na != nb and normals[i] is not None and normals[j] is not None \
                        and overlap(A, B, normals[i], normals[j]):
                    pair_ = ' / '.join(sorted((na, nb)))
                    c, at = found.get(pair_, (0, [round(float(v), 2) for v in A.mean(0)]))
                    found[pair_] = (c + 1, at)
    return found


def _closed(ob, what):
    bm = bmesh.new()
    bm.from_mesh(ob.data)
    ok = all(e.is_manifold for e in bm.edges)
    degenerate = sum(1 for f in bm.faces if f.calc_area() <= 1e-9)
    bm.free()
    assert ok, f'{what}: open edges'
    assert not degenerate, f'{what}: {degenerate} degenerate faces'


def _bounds(objs):
    pts = [o.matrix_world @ v.co for o in objs for v in o.data.vertices]
    lo = Vector([min(p[i] for p in pts) for i in range(3)])
    hi = Vector([max(p[i] for p in pts) for i in range(3)])
    return lo, hi


def _join(part, objs):
    bpy.ops.object.select_all(action='DESELECT')
    for o in objs:
        o.select_set(True)
    bpy.context.view_layer.objects.active = objs[0]
    if len(objs) > 1:
        bpy.ops.object.join()
    ob = bpy.context.view_layer.objects.active
    ob.name = part if bpy.data.objects.get(part) is None else f'{m.id}_{part}'
    ob.data.name = ob.name
    ob['part'] = part
    bm = bmesh.new()
    bm.from_mesh(ob.data)
    bmesh.ops.triangulate(bm, faces=bm.faces)
    bm.to_mesh(ob.data)
    bm.free()
    _closed(ob, f'{m.id}/{part}')
    for poly in ob.data.polygons:
        poly.use_smooth = part not in ALL_MARKERS and part != 'Root'
    ob.data.set_sharp_from_angle(angle=math.radians(50))
    return ob


def _uv(ob, lo, hi):
    """One UV layer, a front projection of the model's box into 0-1: nothing is
    textured, but the importer and its tangents want a layer."""
    me = ob.data
    for existing in list(me.uv_layers):
        me.uv_layers.remove(existing)
    uv = me.uv_layers.new(name='UVMap')
    span = max(hi.x - lo.x, hi.z - lo.z, 1e-6)
    for loop in me.loops:
        co = ob.matrix_world @ me.vertices[loop.vertex_index].co
        uv.data[loop.index].uv = (min(max((co.x - lo.x) / span, 0), 1), min(max((co.z - lo.z) / span, 0), 1))


def _proxy(parts, lo, hi):
    """LOD_Proxy: the finished visible parts copied, joined and decimated to
    PROXY_BUDGET, one flat Body-coloured material (MODELS.md: made last, from
    the finished model, silhouette and base colour only)."""
    copies = []
    for ob in parts:
        c = ob.copy()
        c.data = ob.data.copy()
        m.coll.objects.link(c)
        copies.append(c)
    bpy.ops.object.select_all(action='DESELECT')
    for c in copies:
        c.select_set(True)
    bpy.context.view_layer.objects.active = copies[0]
    bpy.ops.object.join()
    px = bpy.context.view_layer.objects.active
    px.name = px.data.name = f'{m.id}_LOD_Proxy'
    px['part'] = 'LOD_Proxy'
    start = len(px.data.polygons)
    budget = m.proxy_budget
    ratio = (budget - 20) / start
    for _ in range(8):
        me = px.data.copy()
        mod = px.modifiers.new('Decimate', 'DECIMATE')
        mod.decimate_type = 'COLLAPSE'
        mod.ratio = ratio
        mod.use_collapse_triangulate = True
        deps = bpy.context.evaluated_depsgraph_get()
        ev = px.evaluated_get(deps)
        new = bpy.data.meshes.new_from_object(ev)
        px.modifiers.remove(mod)
        bm = bmesh.new()
        bm.from_mesh(new)
        bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=1e-4)
        bmesh.ops.dissolve_degenerate(bm, dist=1e-4, edges=bm.edges)
        bmesh.ops.triangulate(bm, faces=bm.faces)
        bm.faces.ensure_lookup_table()
        # The FBX round trip drops slivers and doubled faces: drop them first, so
        # the count in the manifest is the count that arrives.
        seen, bad = set(), []
        for f in bm.faces:
            key = frozenset(v.index for v in f.verts)
            if f.calc_area() <= 1e-6 or key in seen or len(key) < 3:
                bad.append(f)
            seen.add(key)
        if bad:
            bmesh.ops.delete(bm, geom=bad, context='FACES')
        bm.to_mesh(new)
        bm.free()
        if len(new.polygons) <= budget:
            old = px.data
            px.data = new
            bpy.data.meshes.remove(old)
            bpy.data.meshes.remove(me)
            break
        bpy.data.meshes.remove(new)
        bpy.data.meshes.remove(me)
        ratio *= 0.85
    else:
        raise AssertionError(f'{m.id}: LOD_Proxy did not decimate under {budget}')
    px.data.materials.clear()
    m.colours['LOD_Proxy'] = m.target.get('proxy_colour') or m.colours['Body']
    px.data.materials.append(_material('LOD_Proxy'))
    for poly in px.data.polygons:
        poly.use_smooth = True
    px.name = px.data.name = 'LOD_Proxy' if bpy.data.objects.get('LOD_Proxy') is None else f'{m.id}_LOD_Proxy'
    m.pieces['LOD_Proxy'] = [px]
    return px


# --- The rig (MODELS.md, "The rig") -----------------------------------------------------
# One armature per body shape. A template gives each bone its parent, head, tail and
# capsule radius from landmarks (studs, Blender frame); a landmark's default is a
# fraction of the height or read from the model (the Hand marker, the eyes, the
# bounds), and a species overrides any of them with finish(rig={...}). The weights
# are computed, never painted: see _skin().
RIG_ROOT = 'RigRoot'
RIG_OBJECT = 'Rig'              # the armature object's name, the FBX node the importer reads
MAX_INFLUENCES = 4              # Roblox: at most 4 bones a vertex
RIG_OWN = 0.15                  # a bone owns a piece when it is nearest to this share of its vertices
RIG_RIGID = 0.8                 # ... and a piece goes rigidly to one bone owning this share
RIG_BLEND = 0.05                # the soft blend's width across a piece's owners, x height
RIG_FLOOR = 0.04                # a weight under this is dropped (then the rest renormalised)
RIG_SHAPES = ('Biped', 'Quadruped', 'Blob', 'Float', 'Serpent')


def _landmarks(shape, h, lo, hi, given, parts):
    """The template's landmarks: `given` (finish(rig=...)) over the defaults."""
    hand = m.markers.get('Hand', Vector((-0.2 * h, -0.05 * h, 0.4 * h)))
    eye = _bounds([parts['Glow_Eyes_1']]) if 'Glow_Eyes_1' in parts else None
    eye_z = (eye[0].z + eye[1].z) / 2 if eye else 0.85 * h
    L = {}
    if shape == 'Biped':
        neck = min(0.72 * h, eye_z - 0.12 * h)
        L = {'hip_z': 0.32 * h, 'knee_z': 0.16 * h, 'hip_x': 0.075 * h, 'neck_z': neck,
             'shoulder': (0.16 * h, 0.0, neck - 0.05 * h), 'hand': tuple(hand)}
    elif shape == 'Quadruped':
        L = {'body_z': 0.5 * h, 'front_y': 0.55 * lo.y, 'back_y': 0.55 * hi.y, 'leg_x': 0.55 * hi.x,
             'nose': (0.0, 0.9 * lo.y, 0.8 * h), 'tail': (0.0, hi.y, 0.6 * h)}
    elif shape == 'Blob':
        L = {'middle_z': 0.35 * h, 'top_z': 0.7 * h, 'side': (0.42 * max(hi.x, -lo.x), 0.0, 0.4 * h)}
    elif shape == 'Float':
        L = {'body_z': 0.4 * h, 'neck_z': 0.7 * h, 'tail_z': lo.z + 0.02 * h,
             'shoulder': (0.15 * h, 0.0, 0.6 * h), 'hand': tuple(hand)}
    elif shape == 'Serpent':
        L = {'coil_top': (0.0, 0.0, 0.2 * h), 'neck_base': (0.0, 0.08 * h, 0.25 * h),
             'head_base': (0.0, -0.06 * h, 0.78 * h), 'tail_mid': (0.2 * h, -0.15 * h, 0.06 * h),
             'tail_tip': (0.3 * h, -0.3 * h, 0.06 * h)}
    unknown = set(given) - set(L) - {'radius'}
    assert not unknown, f'{m.id}: rig landmarks {sorted(unknown)} are not {shape}\'s ({sorted(L)})'
    L.update({k_: v for k_, v in given.items() if k_ != 'radius'})
    return L


def _rig_bones(shape, h, L):
    """[(name, parent, head, tail, radius)] in Blender studs, RigRoot first."""
    V = lambda *p: Vector(p[0] if len(p) == 1 else p)
    mir = lambda p: Vector((-p[0], p[1], p[2]))
    b = [(RIG_ROOT, None, V(0, 0, 0), V(0, 0, 0.1 * h), 0.0)]
    if shape == 'Biped':
        hz, kz, hx, nz = L['hip_z'], L['knee_z'], L['hip_x'], L['neck_z']
        waist = (hz + nz) / 2
        sh_l = V(L['shoulder']) if L['shoulder'][0] > 0 else mir(L['shoulder'])
        hand_r = V(L['hand'])
        b += [('Hips', RIG_ROOT, V(0, 0, hz), V(0, 0, waist), 0.12 * h),
              ('Spine', 'Hips', V(0, 0, waist), V(0, 0, nz), 0.15 * h),
              ('Head', 'Spine', V(0, 0, nz), V(0, 0, h), 0.18 * h),
              ('Arm_L', 'Spine', sh_l, mir(hand_r), 0.045 * h),
              ('Arm_R', 'Spine', mir(sh_l), hand_r, 0.045 * h)]
        for side, s in (('L', 1), ('R', -1)):
            b += [(f'Thigh_{side}', 'Hips', V(s * hx, 0, hz), V(s * hx, 0, kz), 0.05 * h),
                  (f'Shin_{side}', f'Thigh_{side}', V(s * hx, 0, kz), V(s * hx, 0, 0.02 * h), 0.05 * h)]
    elif shape == 'Quadruped':
        z, fy, by, lx = L['body_z'], L['front_y'], L['back_y'], L['leg_x']
        b += [('Hips', RIG_ROOT, V(0, by, z), V(0, 0, z), 0.2 * h),
              ('Spine', 'Hips', V(0, 0, z), V(0, fy, z), 0.2 * h),
              ('Head', 'Spine', V(0, fy, z), V(L['nose']), 0.2 * h),
              ('Tail', 'Hips', V(0, by, z), V(L['tail']), 0.06 * h)]
        for name, parent, y in (('Leg_F', 'Spine', fy), ('Leg_B', 'Hips', by)):
            for side, s in (('L', 1), ('R', -1)):
                b.append((f'{name}{side}', parent, V(s * lx, y, z), V(s * lx, y, 0.02 * h), 0.08 * h))
    elif shape == 'Blob':
        mz, tz, sd = L['middle_z'], L['top_z'], V(L['side'])
        b += [('Base', RIG_ROOT, V(0, 0, 0.02 * h), V(0, 0, mz), 0.45 * h),
              ('Middle', 'Base', V(0, 0, mz), V(0, 0, tz), 0.45 * h),
              ('Top', 'Middle', V(0, 0, tz), V(0, 0, h), 0.35 * h),
              ('Side_L', 'Middle', V(0.2 * sd.x, 0, sd.z), sd, 0.15 * h),
              ('Side_R', 'Middle', mir(V(0.2 * sd.x, 0, sd.z)), mir(sd), 0.15 * h)]
    elif shape == 'Float':
        bz, nz, tz = L['body_z'], L['neck_z'], L['tail_z']
        sh_l = V(L['shoulder']) if L['shoulder'][0] > 0 else mir(L['shoulder'])
        hand_r = V(L['hand'])
        mid = (bz + tz) / 2
        b += [('Body', RIG_ROOT, V(0, 0, bz), V(0, 0, nz), 0.25 * h),
              ('Head', 'Body', V(0, 0, nz), V(0, 0, h), 0.25 * h),
              ('Arm_L', 'Body', sh_l, mir(hand_r), 0.06 * h),
              ('Arm_R', 'Body', mir(sh_l), hand_r, 0.06 * h),
              ('Tail_1', 'Body', V(0, 0, bz), V(0, 0, mid), 0.25 * h),
              ('Tail_2', 'Tail_1', V(0, 0, mid), V(0, 0, tz), 0.25 * h)]
    elif shape == 'Serpent':
        ct, nb, hb = V(L['coil_top']), V(L['neck_base']), V(L['head_base'])
        b += [('Coil', RIG_ROOT, V(0, 0, 0.02 * h), ct, 0.3 * h),
              ('Neck', 'Coil', nb, hb, 0.1 * h),
              ('Head', 'Neck', hb, V(hb.x, hb.y, h), 0.15 * h),
              ('Tail_1', 'Coil', ct, V(L['tail_mid']), 0.06 * h),
              ('Tail_2', 'Tail_1', V(L['tail_mid']), V(L['tail_tip']), 0.06 * h)]
    else:
        raise AssertionError(f'{m.id}: no rig for the shape {shape} (MODELS.md, "The rig": {RIG_SHAPES})')
    return b


def _armature(bones):
    """The armature object at the origin, rotation 0, scale 1 (Roblox's rule)."""
    arm = bpy.data.armatures.new(f'{m.id}_Rig')
    ob = bpy.data.objects.new(f'{m.id}.{RIG_OBJECT}', arm)
    m.coll.objects.link(ob)
    bpy.ops.object.select_all(action='DESELECT')
    bpy.context.view_layer.objects.active = ob
    ob.select_set(True)
    bpy.ops.object.mode_set(mode='EDIT')
    made = {}
    for name, parent, head, tail, _r in bones:
        eb = arm.edit_bones.new(name)
        eb.head, eb.tail = head, tail
        if (tail - head).length < 1e-3:
            eb.tail = head + Vector((0, 0, 0.1))
        eb.roll = 0.0
        eb.use_deform = True
        if parent:
            eb.parent = made[parent]
            eb.use_connect = False
        made[name] = eb
    bpy.ops.object.mode_set(mode='OBJECT')
    return ob


def _seg_dist(P, a, b):
    a, b = np.array(a), np.array(b)
    ab = b - a
    t = np.clip(((P - a) @ ab) / max(ab @ ab, 1e-9), 0, 1)
    return np.linalg.norm(P - (a + t[:, None] * ab), axis=1)


def _islands(me):
    """Each vertex's connected piece (union-find over the edges)."""
    parent = list(range(len(me.vertices)))

    def find(i):
        while parent[i] != i:
            parent[i] = parent[parent[i]]
            i = parent[i]
        return i
    for e in me.edges:
        a, b = find(e.vertices[0]), find(e.vertices[1])
        if a != b:
            parent[a] = b
    return np.array([find(i) for i in range(len(me.vertices))])


def _skin(ob, bones, h):
    """Vertex groups for one part: each piece rigid to the bone owning almost all
    of it, else blended across its owners by distance to each bone's capsule.
    Returns {bone: vertices weighted} for the manifest."""
    deform = [b for b in bones if b[0] != RIG_ROOT]
    P = np.array([v.co[:] for v in ob.data.vertices])
    D = np.stack([_seg_dist(P, b[2], b[3]) - b[4] for b in deform], axis=1)    # n x B, to each capsule
    W = np.zeros_like(D)
    isl = _islands(ob.data)
    for key in np.unique(isl):
        idx = np.nonzero(isl == key)[0]
        d = D[idx]
        share = np.bincount(d.argmin(axis=1), minlength=len(deform)) / len(idx)
        top = int(share.argmax())
        if share[top] >= RIG_RIGID:
            W[idx, top] = 1.0
            continue
        owners = np.nonzero(share >= RIG_OWN)[0]
        do = d[:, owners]
        w = np.exp(-(do - do.min(axis=1, keepdims=True)) / (RIG_BLEND * h))
        w /= w.sum(axis=1, keepdims=True)
        w[w < RIG_FLOOR] = 0
        if len(owners) > MAX_INFLUENCES:
            cut = np.sort(w, axis=1)[:, -MAX_INFLUENCES][:, None]
            w[w < cut] = 0
        w /= w.sum(axis=1, keepdims=True)
        W[np.ix_(idx, owners)] = w
    assert np.allclose(W.sum(axis=1), 1, atol=1e-4), f'{m.id}/{ob.name}: a vertex unweighted'
    assert ((W > 0).sum(axis=1) <= MAX_INFLUENCES).all(), f'{m.id}/{ob.name}: over {MAX_INFLUENCES} influences'
    used = {}
    for j, b in enumerate(deform):
        nz = np.nonzero(W[:, j])[0]
        if len(nz):
            g = ob.vertex_groups.new(name=b[0])
            for i in nz:
                g.add([int(i)], float(W[i, j]), 'REPLACE')
            used[b[0]] = int(len(nz))
    return used


def _rig(parts, lo, hi, given):
    """The armature for this monster's shape, every visible part skinned and
    parented to it; returns (armature object, the manifest's rig record)."""
    shape = m.target['shape']
    h = m.target['height']
    L = _landmarks(shape, h, lo, hi, given or {}, parts)
    bones = _rig_bones(shape, h, L)
    radius = (given or {}).get('radius', {})
    assert set(radius) <= {b[0] for b in bones}, f'{m.id}: radius for bones not in {shape}: {sorted(radius)}'
    bones = [(n, p, hd, tl, radius.get(n, r)) for n, p, hd, tl, r in bones]
    rig = _armature(bones)
    weighted = {}
    for name, ob in parts.items():
        if name in ALL_MARKERS or name in ('Root', 'LOD_Proxy'):
            continue
        for bname, n in _skin(ob, bones, h).items():
            weighted[bname] = weighted.get(bname, 0) + n
        ob.parent = rig
        ob.matrix_parent_inverse = Matrix.Identity(4)
        mod = ob.modifiers.new('Armature', 'ARMATURE')
        mod.object = rig
    unused = [b[0] for b in bones if b[0] != RIG_ROOT and b[0] not in weighted]
    assert not unused, f'{m.id}: bones moving nothing: {unused} (a landmark is off the model)'
    rec = {'shape': shape, 'object': RIG_OBJECT, 'root_bone': RIG_ROOT,
           'bones': [{'name': n, 'parent': p, 'head_roblox': roblox(hd), 'tail_roblox': roblox(tl),
                      'radius': round(r, 3), 'vertices': weighted.get(n, 0)} for n, p, hd, tl, r in bones],
           'landmarks': {k_: (round(v, 3) if isinstance(v, (int, float)) else [round(c, 3) for c in v])
                         for k_, v in L.items()},
           'max_influences': MAX_INFLUENCES}
    return rig, rec


def finish(note='', rig=None):
    """Everything after the shapes; REFUSES (AssertionError) a model breaking the
    MODELS.md "Monsters" contract. In order: the names (Body, two Glow_Eyes, the
    Nameplate and Hand markers, nothing outside the allowed names), no coplanar
    faces between pieces, every part closed, the height within 10 % of
    Species.luau's look.height, nothing under the floor and a walker standing
    on it, the origin between the feet (or under a floater's body), facing -Z
    (the eyes ahead of the Body's centre, Glow_Eyes_1 on the left), the
    Nameplate above the head, the Hand on the model; then the Root (2 x h x 2,
    bottom at 0) and the LOD_Proxy, the budgets (4,000 + proxy 300, the
    per-mesh cap), the FBX, and the model's manifest record."""
    t = m.target
    h = t['height']
    tag = m.id
    monster = m.kind == 'monster'
    # Names.
    need_parts = ('Body', 'Glow_Eyes_1', 'Glow_Eyes_2', 'Nameplate', 'Hand') if monster else t['need']
    for need in need_parts:
        assert need in m.pieces, f'{tag}: no {need} (MODELS.md, {"Monsters" if monster else "Hunters and the bus"})'
    eye_parts = sorted(p for p in m.pieces if p.startswith('Glow_Eyes_'))
    if monster or eye_parts:
        assert eye_parts == ['Glow_Eyes_1', 'Glow_Eyes_2'], f'{tag}: eye parts {eye_parts}'
    assert 'Root' not in m.pieces and 'LOD_Proxy' not in m.pieces, f'{tag}: Root and LOD_Proxy are finish()\'s'
    # Coplanar faces between any two pieces, before they merge (markers left out).
    pieces = [o for p, objs in m.pieces.items() if p not in ALL_MARKERS for o in objs]
    for o in pieces:
        _closed(o, o.name)
    cop = coplanar_overlaps(pieces)
    assert not cop, f'{tag}: coplanar faces, will z-fight: {cop}'
    # Join every part.
    parts = {p: _join(p, objs) for p, objs in m.pieces.items()}
    visible = [ob for p, ob in parts.items() if p not in ALL_MARKERS]
    lo, hi = _bounds(visible)
    top = hi.z
    assert abs(top - h) <= HEIGHT_TOL * h, f'{tag}: {top:.2f} studs tall, target {h} +/- {HEIGHT_TOL:.0%}'
    assert lo.z >= -0.005, f'{tag}: {lo.z:.3f} under the floor'
    floats = t['shape'] == 'Float'
    root_size = t.get('root', (2, 2, h))
    if m.kind == 'vehicle':
        # Its Root is its size: everything inside it, and the bus filling it, wheels on the floor.
        half = Vector((root_size[0] / 2, root_size[1] / 2, 0))
        assert lo.z <= 0.02, f'{tag}: the wheels float {lo.z:.3f} over the floor'
        assert all(lo[i] >= -half[i] - 0.01 and hi[i] <= half[i] + 0.01 for i in range(2)) \
            and hi.z <= root_size[2] + 0.01, f'{tag}: outside its Root {root_size}: {tuple(lo)} {tuple(hi)}'
        assert all(hi[i] - lo[i] >= 0.9 * root_size[i] for i in range(3)), \
            f'{tag}: does not fill its Root {root_size} (bounds {tuple(hi - lo)})'
        c = (lo + hi) / 2
        assert abs(c.x) < 0.1 and abs(c.y) < 0.1, f'{tag}: origin not under the middle ({c.x:.2f}, {c.y:.2f})'
    elif floats:
        blo, bhi = _bounds([parts['Body']])
        c = (blo + bhi) / 2
        assert abs(c.x) < 0.1 and abs(c.y) < 0.3, f'{tag}: origin not under the body ({c.x:.2f}, {c.y:.2f})'
    else:
        assert lo.z <= 0.02, f'{tag}: a walker floats {lo.z:.3f} over the floor'
        feet = [p for ob in visible for p in (ob.matrix_world @ v.co for v in ob.data.vertices) if p.z < 0.08]
        if m.kind == 'tree':
            # A gnarled trunk's foot is not symmetric: its centre is the ring's centroid, not its extents' middle.
            fx = sum(p.x for p in feet) / len(feet)
            fy = sum(p.y for p in feet) / len(feet)
        else:
            fx = (min(p.x for p in feet) + max(p.x for p in feet)) / 2
            fy = (min(p.y for p in feet) + max(p.y for p in feet)) / 2
        assert abs(fx) < 0.05 and abs(fy) < 0.3, f'{tag}: origin not between the feet ({fx:.2f}, {fy:.2f})'
    blo, bhi = _bounds([parts['Body']])
    body_c = (blo + bhi) / 2
    if eye_parts:
        e1, e2 = (_bounds([parts[e]]) for e in ('Glow_Eyes_1', 'Glow_Eyes_2'))
        ec1, ec2 = (e1[0] + e1[1]) / 2, (e2[0] + e2[1]) / 2
        assert ec1.x > 0 > ec2.x, f'{tag}: Glow_Eyes_1 must be the monster\'s left (+X in Blender)'
        assert max(ec1.y, ec2.y) < body_c.y - 0.1, f'{tag}: the eyes are not on the front (-Y): it does not face -Z'
        assert abs(ec1.x + ec2.x) < 0.02 and abs(ec1.z - ec2.z) < 0.02, f'{tag}: the eyes are not a mirrored pair'
    if m.kind == 'tree':
        # MODELS.md, "Street scenery: trees": few parts, nothing but Root collides (the import's Box).
        assert len(parts) + 2 <= TREE_MAX_PARTS, f'{tag}: {len(parts) + 2} parts with Root and LOD_Proxy > {TREE_MAX_PARTS}'
    if not monster and t.get('front'):
        # The facing: the `front` part ahead of the Body along `facing`.
        f = Vector(t['facing'])
        flo, fhi = _bounds([parts[t['front']]])
        assert ((flo + fhi) / 2).dot(f) > body_c.dot(f) + 0.1, \
            f'{tag}: {t["front"]} is not ahead of the Body along {t["facing"]} (Blender): it faces the wrong way'
    if 'Nameplate' in m.markers or monster:
        nps = m.markers['Nameplate']
        assert nps.z >= top + 0.4 and math.hypot(nps.x, nps.y) < 0.6, f'{tag}: Nameplate not above the head'
    if 'Hand' in m.markers or monster:
        hd = m.markers['Hand']
        assert all(lo[i] - 0.3 <= hd[i] <= hi[i] + 0.3 for i in range(3)), f'{tag}: Hand off the model'
    if 'Door' in m.markers:
        # Where guests step out: on the floor just outside the bus's right (Roblox +Z, Blender +Y) side.
        d = m.markers['Door']
        assert hi.y - 0.05 <= d.y <= hi.y + 1.5 and abs(d.z) <= 0.3 and lo.x <= d.x <= hi.x, \
            f'{tag}: Door not on the floor beside the right (+Y) side: {tuple(d)}'
        assert 'Door' in m.looks and m.looks['Door'].y > 0.9, f'{tag}: Door must look out of the side (+Y)'
    # Root, exactly the contract's.
    bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=1.0)
    bm.transform(Matrix.Translation((0, 0, root_size[2] / 2)) @ Matrix.Diagonal((*root_size, 1)))
    root = _object('Root', bm, name=f'{tag}.Root')
    parts['Root'] = _join('Root', m.pieces['Root'])
    proxy = _proxy(visible, lo, hi)
    parts['LOD_Proxy'] = proxy
    # Budgets.
    records = []
    for p, ob in parts.items():
        ob.data.calc_loop_triangles()
        _uv(ob, lo, hi)
        records.append({'part': p, 'triangles': len(ob.data.loop_triangles),
                        'colour': list(m.colours[p]),
                        'material': 'Neon' if p.startswith('Glow_') else 'SmoothPlastic'})
    tris = sum(r['triangles'] for r in records if r['part'] != 'LOD_Proxy')
    ptris = next(r['triangles'] for r in records if r['part'] == 'LOD_Proxy')
    assert tris <= m.budget, f'{tag}: {tris} triangles > {m.budget}'
    assert ptris <= m.proxy_budget, f'{tag}: LOD_Proxy {ptris} > {m.proxy_budget}'
    assert max(r['triangles'] for r in records) <= MESH_TRIANGLE_CAP
    # The rig (MODELS.md, "The rig"): a monster's armature, every visible part skinned to it.
    armature, rig_rec = (_rig(parts, lo, hi, rig) if monster else (None, None))
    assert monster or rig is None, f'{tag}: only a monster is rigged'
    exported = dict(parts)
    if armature is not None:
        exported[RIG_OBJECT] = armature
    # Names in the FBX are the part names: Blender keeps one object per name, so
    # each model's parts are renamed to the bare names only while it exports.
    for p, ob in exported.items():
        other = bpy.data.objects.get(p)
        if other is not None and other is not ob:
            other.name = f'_held_{other.name}'
        ob.name = p
    bpy.ops.object.select_all(action='DESELECT')
    for ob in exported.values():
        ob.select_set(True)
    bpy.ops.export_scene.fbx(filepath=str(m.out / 'fbx' / f'{tag}.fbx'), use_selection=True,
                             object_types={'MESH', 'ARMATURE'} if armature else {'MESH'},
                             apply_unit_scale=True, apply_scale_options='FBX_SCALE_UNITS',
                             axis_forward='-Z', axis_up='Y', bake_anim=False, add_leaf_bones=False,
                             use_armature_deform_only=False, primary_bone_axis='Y', secondary_bone_axis='X',
                             mesh_smooth_type='OFF', use_tspace=False, path_mode='STRIP', embed_textures=False)
    for p, ob in exported.items():
        ob.name = f'{tag}.{p}'
    rec = {
        'species': tag, 'shape': t['shape'], 'fbx': f'fbx/{tag}.fbx',
        'height_target': h, 'height': round(top, 3),
        'bounds_blender': [[round(c, 3) for c in lo], [round(c, 3) for c in hi]],
        'triangles': tris, 'triangles_proxy': ptris,
        'budget': {'model': m.budget, 'proxy': m.proxy_budget, 'mesh_cap': MESH_TRIANGLE_CAP},
        'parts': records,
        'markers_blender': {k: [round(c, 4) for c in v] for k, v in m.markers.items()},
        'markers_roblox': {k: roblox(v) for k, v in m.markers.items()},
        'markers_roblox_from_root': {k: roblox(v - Vector((0, 0, root_size[2] / 2))) for k, v in m.markers.items()},
        'coplanar_overlaps': 'none',
        'rig': rig_rec or 'none: static meshes, no bones, no Animations folder (the client bobs them)',
        'note': note,
    }
    if not monster:
        # Street models only, so a monster's record stays as it was.
        rec['kind'] = m.kind
        rec['root_size_blender'] = list(root_size)
        rec['root_size_roblox'] = [root_size[0], root_size[2], root_size[1]]
        rec['front'] = t['front']
        rec['facing_blender'] = list(t['facing']) if t['facing'] else None
        rec['facing_roblox'] = roblox(Vector(t['facing'])) if t['facing'] else None
        rec['need'] = list(t['need'])
        rec['rig'] = 'none: static meshes, no bones (the client moves it whole)'
    if m.looks:
        rec['markers_look_roblox'] = {k_: roblox(v) for k_, v in m.looks.items()}
    _done.append(rec)
    print(f'{tag}: {tris} triangles + proxy {ptris}, {top:.2f} of {h} studs, parts {sorted(parts)}'
          + (f', rig {rig_rec["shape"]} {[b["name"] for b in rig_rec["bones"]]}' if rig_rec else ''), flush=True)
    return rec


def finish_set(set_dir, offsets=4.2, sheet=True, cols=5, place=None, frame=None):
    """Write manifest.json, spread the models along X for the review (each model's
    own frame is its FBX), save the .blend and render the one Workbench sheet.
    `cols` models per row, `offsets` apart. `place` {id: (x, turn_degrees[, z])}
    sets the layout by hand instead (the street set: a bus beside a person,
    turned so its door side faces the camera); a list of such views shows a
    model more than once (the bus's door side and its face, a row below). Only
    the review scene is moved, turned or copied: the FBX is already written.
    `frame` overrides the manifest's frame note."""
    out = ROOT / 'blender' / set_dir
    manifest = {'set': set_dir, 'frame': frame or ('Blender -Y front, +Z up, +X the monster\'s left; '
                'Roblox (x, y, z) = Blender (-x, z, y)'), 'models': _done}
    (out / 'manifest.json').write_text(json.dumps(manifest, indent=2))
    (out / 'import_settings.luau').write_text(import_luau(_done), encoding='utf-8')
    row_h = 9.0
    if place:
        cols = len(_done)
    view = lambda v: Matrix.Translation((v[0], 0, v[2] if len(v) > 2 else 0)) @ Matrix.Rotation(math.radians(v[1]), 4, 'Z')
    row_z = {0.0}
    for i, rec in enumerate(_done):
        coll = bpy.data.collections[rec['species']]
        views = place[rec['species']] if place else None
        views = [views] if views and not isinstance(views, list) else views
        for ob in list(coll.objects):
            if ob.get('part') in ('Root', 'LOD_Proxy') + ALL_MARKERS:
                ob.hide_render = True
            if ob.parent is not None:
                continue          # a skinned part moves with its armature
            if place:
                base = ob.matrix_world.copy()
                ob.matrix_world = view(views[0]) @ base
                for v in views[1:]:
                    if not ob.hide_render:
                        c = ob.copy()
                        c.name = f'{ob.name}.review'
                        coll.objects.link(c)
                        c.matrix_world = view(v) @ base
                row_z |= {float(v[2]) if len(v) > 2 else 0.0 for v in views}
            else:
                ob.location.x += (i % cols) * offsets
                ob.location.z -= (i // cols) * row_h
    rows = (len(_done) + cols - 1) // cols
    # A grey 5-stud person at the start of each row, for scale (not exported).
    person = bpy.data.collections.new('Person_5_studs')
    bpy.context.scene.collection.children.link(person)
    pm = bpy.data.materials.new('Person')
    pm.diffuse_color = (0.35, 0.35, 0.35, 1)
    px = -offsets
    if place:
        shown = [o for c in _done for o in bpy.data.collections[c['species']].objects if not o.hide_render]
        slo, shi = _bounds(shown)
        px = slo.x - 2.0
    for z0 in (sorted(row_z, reverse=True) if place else [-r * row_h for r in range(rows)]):
        for loc, size in (((px, 0, 0.0), (0.9, 0.5, 2.0)), ((px, 0, 2.0), (2.0, 1.0, 2.0)), ((px, 0, 4.0), (1.0, 1.0, 1.0))):
            bm = bmesh.new()
            bmesh.ops.create_cube(bm, size=1.0)
            bm.transform(Matrix.Translation((loc[0], loc[1], z0 + loc[2] + size[2] / 2)) @ Matrix.Diagonal((*size, 1)))
            me = bpy.data.meshes.new('person')
            bm.to_mesh(me)
            bm.free()
            me.materials.append(pm)
            ob = bpy.data.objects.new('Person', me)
            person.objects.link(ob)
    bpy.ops.wm.save_as_mainfile(filepath=str(out / f'{out.name}.blend'))
    if sheet and not NORENDER:
        if place:
            _sheet(out / 'review' / 'sheet.png', px - 1.5, shi.x + 1.0, slo.z - 0.6, shi.z + 0.8)
        else:
            _sheet(out / 'review' / 'sheet.png', px - 1.5, (min(cols, len(_done)) - 1) * offsets + 1.8,
                   -(rows - 1) * row_h - 0.6, max(7.6, max(r['height'] for r in _done) + 0.5))
        if 'pose' in ARGS and any(isinstance(r['rig'], dict) for r in _done):
            # The rig's proof: every armature in a test pose, the same sheet again.
            for rec in _done:
                if isinstance(rec['rig'], dict):
                    _test_pose(bpy.data.objects[f'{rec["species"]}.{RIG_OBJECT}'], rec['rig']['shape'],
                               rec['height_target'])
            _sheet(out / 'review' / 'pose.png', px - 1.5, (min(cols, len(_done)) - 1) * offsets + 1.8,
                   -(rows - 1) * row_h - 0.6, max(7.6, max(r['height'] for r in _done) + 0.5))
            for rec in _done:
                if isinstance(rec['rig'], dict):
                    for pb in bpy.data.objects[f'{rec["species"]}.{RIG_OBJECT}'].pose.bones:
                        pb.matrix_basis = Matrix.Identity(4)


# A pose far out on every bone, to see in one picture that each part follows its
# bone (the clips themselves are Luau: src/shared/MonsterMotion.luau). Degrees about
# the model's axes at rest, Blender frame (+X the monster's left, -Y front, +Z up);
# offsets x height.
TEST_POSES = {
    'Biped': {'Thigh_L': (-30, 0, 0), 'Shin_L': (35, 0, 0), 'Thigh_R': (30, 0, 0), 'Arm_L': (35, 0, 0),
              'Arm_R': (-40, 0, -35), 'Spine': (-8, 0, 10), 'Head': (10, 0, 25)},
    'Quadruped': {'Leg_FL': (-25, 0, 0), 'Leg_BR': (-25, 0, 0), 'Leg_FR': (25, 0, 0), 'Leg_BL': (25, 0, 0),
                  'Head': (15, 0, 25), 'Tail': (0, 0, 40)},
    'Blob': {'Top': ((0, 0, 0), (0, 0, -0.15)), 'Side_L': ((0, 0, 0), (0.1, 0, 0)),
             'Side_R': ((0, 0, 0), (-0.1, 0, 0)), 'Middle': (0, 12, 0)},
    'Float': {'Body': (-10, 0, 0), 'Tail_1': (25, 0, 0), 'Tail_2': (30, 0, 0), 'Arm_R': (0, -60, 0),
              'Arm_L': (0, 30, 0), 'Head': (0, 0, 25)},
    'Serpent': {'Neck': (15, 15, 0), 'Head': (10, 0, 30), 'Tail_1': (0, 0, 25), 'Tail_2': (0, 0, 30)},
}


def _test_pose(rig, shape, h):
    for name, pose in TEST_POSES[shape].items():
        rot, off = (pose, (0, 0, 0)) if isinstance(pose[0], (int, float)) else pose
        pb = rig.pose.bones[name]
        q = pb.bone.matrix_local.to_3x3()
        r = Matrix.Identity(3)
        for axis, deg in zip('XYZ', rot):
            if deg:
                r = Matrix.Rotation(math.radians(deg), 3, axis) @ r
        basis = (q.inverted() @ r @ q).to_4x4()
        basis.translation = q.inverted() @ (Vector(off) * h)
        pb.matrix_basis = basis


def import_luau(records):
    """The import step's Luau (skill `import`, step 2) for these monsters, run in
    the Edit datamodel once August has imported the FBXs into Workspace. What an
    FBX cannot carry, set here and saved into the .rbxm: Root as PrimaryPart,
    invisible, its pivot on the floor without the importer's -90 deg X; each
    marker part turned into an Attachment of its name under Root and deleted;
    every part's colour and material from the manifest with any imported
    SurfaceAppearance removed (a mutation must be able to tint it); Box
    collision and no collide/query/touch on every mesh; LOD_Proxy hidden.
    Read it back in a separate call (CollisionFidelity shows a call later)."""
    rows = []
    for r in records:
        cols = ', '.join(f'{p["part"]} = {{{", ".join(str(c) for c in p["colour"])}}}'
                         for p in r['parts'] if p['part'] not in ALL_MARKERS + ('Root',))
        rows.append(f'\t{r["species"]} = {{ {cols} }},')
    body = '\n'.join(rows)
    # The marker names these records carry (a monster set: Nameplate and Hand, as before),
    # and, for a street set, the way an attachment faces (the bus's Door looks out of its side).
    present = {k_ for r in records for k_ in r['markers_blender']}
    names = ', '.join(f'"{n}"' for n in ALL_MARKERS if n in present or n in MARKERS)
    looks = {r['species']: r['markers_look_roblox'] for r in records if r.get('markers_look_roblox')}
    looks_decl, looks_set = '', ''
    if looks:
        lrows = '\n'.join(f'\t{sid} = {{ ' + ', '.join(f'{n} = {{{", ".join(str(c) for c in v)}}}' for n, v in lk.items())
                          + ' },' for sid, lk in looks.items())
        looks_decl = f'local looks = {{\n{lrows}\n}}\n'
        looks_set = ('\t\t\tlocal look = looks[id] and looks[id][name]\n'
                     '\t\t\tif look then\n'
                     '\t\t\t\tlocal dir = root.CFrame:VectorToWorldSpace(Vector3.new(look[1], look[2], look[3]))\n'
                     '\t\t\t\ta.WorldCFrame = CFrame.lookAt(p.Position, p.Position + dir)\n'
                     '\t\t\tend\n')
    return f'''-- Generated by tools/monster_kit.py (import_luau); do not edit by hand.
-- Edit datamodel, after the FBXs are in Workspace. Then read back in a SEPARATE call.
local colours = {{
{body}
}}
{looks_decl}local out = {{}}
for id, parts in colours do
	local m = workspace:FindFirstChild(id)
	if not m then
		table.insert(out, id .. ": missing")
		continue
	end
	local root = m:FindFirstChild("Root") :: BasePart
	m.PrimaryPart = root
	root.PivotOffset = CFrame.new(0, -root.Size.Y / 2, 0)
	root.Transparency = 1
	for _, name in {{ {names} }} do
		local p = m:FindFirstChild(name)
		if p and p:IsA("BasePart") then
			local a = Instance.new("Attachment")
			a.Name = name
			a.Parent = root
			a.WorldPosition = p.Position
{looks_set}			p:Destroy()
		end
	end
	-- A rigged model (MODELS.md, "The rig"): the importer (Rig Type Custom) hangs every
	-- part on a `RootPart` holding the bones, by Motor6D. Those joints stay, unanchored,
	-- and Root anchors the whole; `RootPart` (not the manifest's) is hidden like Root;
	-- the animation editor's `InitialPoses` and the AnimationController go (the clips
	-- are code). The bones are reported.
	for _, junk in {{ "InitialPoses", "AnimationController" }} do
		local j = m:FindFirstChild(junk)
		if j then
			j:Destroy()
		end
	end
	local bones, homes, extra = 0, {{}}, {{}}
	for _, b in m:GetDescendants() do
		if b:IsA("Bone") then
			bones += 1
			homes[b.Parent.Name] = true
		elseif b:IsA("BasePart") and b ~= root and not parts[b.Name] and b.Name ~= "Root" then
			b.Transparency = 1
			table.insert(extra, b.Name)
		end
	end
	for _, p in m:GetDescendants() do
		if p:IsA("SurfaceAppearance") then
			p:Destroy()
		elseif p:IsA("BasePart") and table.find(extra, p.Name) then
			p.Anchored = false
			p.Massless = true
			p.CanCollide, p.CanQuery, p.CanTouch = false, false, false
		elseif p:IsA("MeshPart") then
			-- Jointed (rigged): only Root anchors, the rest ride on their Motor6Ds.
			p.Anchored = p == root or bones == 0
			p.Massless = p ~= root and bones > 0
			p.CanCollide, p.CanQuery, p.CanTouch = false, false, false
			p.CollisionFidelity = Enum.CollisionFidelity.Box
			local c = parts[p.Name]
			if c then
				p.Color = Color3.fromRGB(c[1], c[2], c[3])
				p.Material = if string.find(p.Name, "^Glow_") then Enum.Material.Neon else Enum.Material.SmoothPlastic
			end
			if p.Name == "LOD_Proxy" then
				p.Transparency = 1
			end
		end
	end
	local where = {{}}
	for n in homes do
		table.insert(where, n)
	end
	table.insert(out, id .. ": set" .. (if bones > 0
		then ` ({{bones}} bones under {{table.concat(where, "/")}}; extra parts {{table.concat(extra, "/")}})`
		else ""))
end
return table.concat(out, ", ")
'''


def _sheet(path, xmin, xmax, zmin, zmax):
    """ONE Workbench image of the whole set, at most 768 px wide: no EEVEE, no
    Cycles (a GPU hang loses the Studio playtest running beside it)."""
    scene = bpy.context.scene
    scene.render.engine = 'BLENDER_WORKBENCH'
    scene.display.shading.light = 'STUDIO'
    scene.display.shading.color_type = 'MATERIAL'
    scene.display.shading.show_cavity = True
    scene.display.shading.show_object_outline = True
    scene.render.resolution_x = 768
    scene.render.resolution_y = 600
    scene.render.resolution_percentage = 100
    world = bpy.data.worlds.new('W')
    scene.world = world
    world.color = (0.82, 0.8, 0.86)
    cam = bpy.data.cameras.new('Sheet')
    cam.type = 'ORTHO'
    width = xmax - xmin
    cam.ortho_scale = max(width, (zmax - zmin) * 768 / 600) * 1.04
    ob = bpy.data.objects.new('Sheet', cam)
    scene.collection.objects.link(ob)
    yaw, pitch = math.radians(-18), math.radians(8)
    d = Vector((math.sin(yaw) * math.cos(pitch), -math.cos(yaw) * math.cos(pitch), math.sin(pitch)))
    centre = Vector(((xmin + xmax) / 2, 0, (zmin + zmax) / 2))
    ob.location = centre + d * 60
    ob.rotation_euler = (-d).to_track_quat('-Z', 'Y').to_euler()
    scene.camera = ob
    scene.render.filepath = str(path)
    bpy.ops.render.render(write_still=True)
    print(f'sheet: {path}', flush=True)


# --- The validator ----------------------------------------------------------------------
def validate(set_dir, species):
    """Re-import each blender/<set_dir>/fbx/<id>.fbx into an empty scene and check
    it against the manifest the build wrote and MODELS.md: the part names
    round-trip and include every contract name, triangle counts as built, the
    budgets, one material and one UV layer per part, closed geometry, the height
    and the Root's size and place, the markers where the manifest says, the
    eyes in front. Writes validation.json. It cannot check anything in Studio."""
    root = ROOT / 'blender' / set_dir
    manifest = json.loads((root / 'manifest.json').read_text())
    recs = {r['species']: r for r in manifest['models']}
    report = {'set': set_dir, 'models': {}, 'collision_precise': {},
              'collision_note': 'Monsters collide with nothing (MonsterKit: CanCollide/CanQuery/CanTouch off): '
                                'Box on every mesh, PreciseConvexDecomposition on none.'}
    for sid in species:
        rec = recs[sid]
        bpy.ops.wm.read_factory_settings(use_empty=True)
        bpy.context.scene.unit_settings.system = 'METRIC'
        bpy.context.scene.unit_settings.scale_length = .01
        bpy.ops.import_scene.fbx(filepath=str(root / rec['fbx']))
        meshes = {o.name: o for o in bpy.context.scene.objects if o.type == 'MESH'}
        checks = []

        def check(ok, what):
            assert ok, f'{sid}: {what}'
            checks.append(what)

        kind = rec.get('kind', 'monster')
        expected = {p['part'] for p in rec['parts']}
        check(set(meshes) == expected, f'part names round-trip ({len(expected)} parts)')
        if kind == 'monster':
            need = {'Root', 'Body', 'Glow_Eyes_1', 'Glow_Eyes_2', 'Nameplate', 'Hand', 'LOD_Proxy'}
            check(need <= set(meshes), 'MODELS.md names present: Root, Body, Glow_Eyes_1/2, Nameplate, Hand, LOD_Proxy')
            check(all(PART_RE.match(n) for n in meshes), 'every other part an allowed name (Skin/Trim/Dark/Light/Glow_<Colour>_n)')
        else:
            need = {'Root', 'LOD_Proxy', *rec['need']}
            check(need <= set(meshes), 'MODELS.md names present: ' + ', '.join(sorted(need)))
            check(all(STREET_PART_RE.match(n) for n in meshes),
                  'every other part an allowed name (Skin/Trim/Dark/Light/Wheel_n/Glow_<Colour>_n)')
        total = 0
        for p in rec['parts']:
            ob = meshes[p['part']]
            me = ob.data
            me.calc_loop_triangles()
            n = len(me.loop_triangles)
            assert n == p['triangles'], (sid, p['part'], n, p['triangles'])
            assert len(me.uv_layers) == 1 and len(me.materials) == 1, (sid, p['part'])
            if p['part'] != 'LOD_Proxy':
                total += n
                bm = bmesh.new()
                bm.from_mesh(me)
                assert all(e.is_manifold for e in bm.edges), (sid, p['part'], 'open edges')
                bm.free()
        checks += ['triangle counts as built', 'one material and one UV layer per part',
                   'closed geometry (all but the proxy)']
        check(total <= rec['budget']['model'], f'{total} triangles within {rec["budget"]["model"]}')
        check(rec['triangles_proxy'] <= rec['budget']['proxy'],
              f'LOD_Proxy {rec["triangles_proxy"]} within {rec["budget"]["proxy"]}')
        world = lambda o: [o.matrix_world @ v.co for v in o.data.vertices]
        vis = [p for n_, o in meshes.items() if n_ not in ('Root', 'LOD_Proxy') + ALL_MARKERS for p in world(o)]
        top = max(p.z for p in vis)
        h = rec['height_target']
        check(abs(top - h) <= HEIGHT_TOL * h, f'height {top:.2f} studs against {h} (+/- 10 %)')
        check(min(p.z for p in vis) >= -0.005, 'nothing under the floor')
        rp = world(meshes['Root'])
        rlo = Vector([min(p[i] for p in rp) for i in range(3)])
        rhi = Vector([max(p[i] for p in rp) for i in range(3)])
        if kind == 'monster':
            check((rhi - rlo - Vector((2, 2, h))).length < 1e-3 and abs(rlo.z) < 1e-3
                  and abs(rlo.x + 1) < 1e-3 and abs(rlo.y + 1) < 1e-3, f'Root 2 x {h} x 2, bottom at 0, centred on the origin')
        else:
            rs = Vector(rec['root_size_blender'])
            check((rhi - rlo - rs).length < 1e-3 and abs(rlo.z) < 1e-3 and abs(rlo.x + rs.x / 2) < 1e-3
                  and abs(rlo.y + rs.y / 2) < 1e-3,
                  f'Root {rec["root_size_roblox"]} (Roblox x, y, z), bottom at 0, centred on the origin')
            if kind == 'vehicle':
                vlo = Vector([min(p[i] for p in vis) for i in range(3)])
                vhi = Vector([max(p[i] for p in vis) for i in range(3)])
                check(all(vlo[i] >= rlo[i] - 0.01 and vhi[i] <= rhi[i] + 0.01 for i in range(3)),
                      'the whole bus inside its Root')
        mks = list(rec['markers_blender'])
        for mk in mks:
            pts = world(meshes[mk])
            c = sum(pts, Vector()) / len(pts)
            assert (c - Vector(rec['markers_blender'][mk])).length < 1e-3, (sid, mk, tuple(c))
        check(True, ('Nameplate and Hand' if kind == 'monster' else ' and '.join(mks)) + ' markers where the manifest says')
        bp = world(meshes['Body'])
        if kind == 'monster':
            ey = [sum(world(meshes[e]), Vector()) / len(meshes[e].data.vertices) for e in ('Glow_Eyes_1', 'Glow_Eyes_2')]
            by = (min(p.y for p in bp) + max(p.y for p in bp)) / 2
            check(max(e.y for e in ey) < by and ey[0].x > 0 > ey[1].x, 'eyes on the front (-Y, Roblox -Z), Glow_Eyes_1 on the left')
        elif rec.get('front'):
            f = Vector(rec['facing_blender'])
            fp = world(meshes[rec['front']])
            fc = sum(fp, Vector()) / len(fp)
            bc = (Vector([min(p[i] for p in bp) for i in range(3)]) + Vector([max(p[i] for p in bp) for i in range(3)])) / 2
            check(fc.dot(f) > bc.dot(f), f'{rec["front"]} ahead of the Body: faces Roblox {rec["facing_roblox"]}')
        if isinstance(rec.get('rig'), dict):
            # The rig round-trips: its bones by name, RigRoot at the origin, every visible
            # part skinned (at most 4 influences, summing to 1, none on RigRoot), nothing else.
            arms = [o for o in bpy.context.scene.objects if o.type == 'ARMATURE']
            check(len(arms) == 1, f'one armature ({len(arms)})')
            arm = arms[0]
            names = [b['name'] for b in rec['rig']['bones']]
            check(sorted(b.name for b in arm.data.bones) == sorted(names), f'bones round-trip: {", ".join(names)}')
            check((arm.matrix_world @ arm.data.bones[RIG_ROOT].head_local).length < 1e-3, f'{RIG_ROOT} at the origin')
            for n_, o in meshes.items():
                groups = {g.index: g.name for g in o.vertex_groups}
                if n_ in ('Root', 'LOD_Proxy') + ALL_MARKERS:
                    assert not groups, (sid, n_, 'skinned')
                    continue
                assert RIG_ROOT not in groups.values(), (sid, n_, 'weights on RigRoot')
                for v in o.data.vertices:
                    ws = [g.weight for g in v.groups if g.weight > 1e-6]
                    assert 1 <= len(ws) <= MAX_INFLUENCES and abs(sum(ws) - 1) < 1e-3, (sid, n_, v.index, ws)
            check(True, f'every visible part skinned: 1-{MAX_INFLUENCES} influences a vertex, summing to 1, '
                        f'none on {RIG_ROOT}; Root, LOD_Proxy and the markers not skinned')
        report['models'][sid] = {'checks': checks, 'triangles': total, 'triangles_proxy': rec['triangles_proxy'],
                                 'height': round(top, 3), 'height_target': h}
        report['collision_precise'][sid] = []
    report['not_validated'] = [
        'nothing in Studio: the import, the axis conversion, the marker positions there, the colours arriving',
        'whether the importer carries a material\'s plain colour to MeshPart.Color (manifest has every colour)',
        'the look at the game\'s camera and at Tiny 0.5 / Giant 1.5 scale',
        'the rig in Studio: Rig Type Custom, every colour part deforming, Model:ScaleTo moving the bones'
        if any(isinstance(recs[s].get('rig'), dict) for s in species) else 'animations: none exist (no rig)']
    if any(recs[s].get('kind') == 'tree' for s in species):
        report['collision_note'] = ('A tree\'s Root is its only collider (MODELS.md, "Street scenery: trees"): '
                                    'ForestRenderer sets CanCollide on Root at runtime, so a person walks into '
                                    'the trunk; Box on every mesh, PreciseConvexDecomposition on none.')
        report['not_validated'][2] = 'the look in the game, at night, among hundreds of its kind and at 0.8-1.25 scale'
    elif any(recs[s].get('kind', 'monster') != 'monster' for s in species):
        report['collision_note'] = ('Street models collide with nothing (HunterRenderer and BusRenderer draw them '
                                    'CanCollide/CanQuery/CanTouch off): Box on every mesh, '
                                    'PreciseConvexDecomposition on none.')
        report['not_validated'][2] = 'the look at the game\'s camera, on the street at night'
        report['not_validated'].append('the Door attachment\'s orientation after import (set from the manifest by '
                                       'import_settings.luau; read it back in Studio)')
    (root / 'validation.json').write_text(json.dumps(report, indent=2))
    print(f'validation.json: {len(report["models"])} models passed', flush=True)
    return report
