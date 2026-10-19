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
        self.target = SPECIES[sid]
        self.out = ROOT / 'blender' / set_dir
        self.coll = bpy.data.collections.new(sid)
        bpy.context.scene.collection.children.link(self.coll)
        self.pieces = {}          # part -> [objects]
        self.colours = {'Body': self.target['colour'], 'Root': (128, 128, 128),
                        'Nameplate': (255, 0, 255), 'Hand': (255, 0, 255),
                        'Dark': (45, 32, 60), 'Light': (255, 255, 255)}   # eyes()' pupils and glints
        self.colours['Glow_Eyes_1'] = self.colours['Glow_Eyes_2'] = self.target['eyes'] or (255, 255, 255)
        self.colours.update(colours or {})
        self.markers = {}
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
    assert sid in SPECIES, f'{sid} is not a species id in Species.luau'
    m = _Model(sid, set_dir, colours)
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
    assert PART_RE.match(part), f'{part}: not a name the contract allows ({PART_RE.pattern})'
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


def marker(name, at):
    """A contract place (MODELS.md: `Nameplate`, `Hand`) as a 0.2 marker part
    centred on it; the import step makes it an Attachment under Root."""
    assert name in MARKERS, name
    bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=MARKER)
    bm.transform(Matrix.Translation(at))
    m.markers[name] = Vector(at)
    return _object(name, bm, name=f'{m.id}.{name}')


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
        poly.use_smooth = part not in MARKERS and part != 'Root'
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
    ratio = (PROXY_BUDGET - 20) / start
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
        if len(new.polygons) <= PROXY_BUDGET:
            old = px.data
            px.data = new
            bpy.data.meshes.remove(old)
            bpy.data.meshes.remove(me)
            break
        bpy.data.meshes.remove(new)
        bpy.data.meshes.remove(me)
        ratio *= 0.85
    else:
        raise AssertionError(f'{m.id}: LOD_Proxy did not decimate under {PROXY_BUDGET}')
    px.data.materials.clear()
    m.colours['LOD_Proxy'] = m.colours['Body']
    px.data.materials.append(_material('LOD_Proxy'))
    for poly in px.data.polygons:
        poly.use_smooth = True
    px.name = px.data.name = 'LOD_Proxy' if bpy.data.objects.get('LOD_Proxy') is None else f'{m.id}_LOD_Proxy'
    m.pieces['LOD_Proxy'] = [px]
    return px


def finish(note=''):
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
    # Names.
    for need in ('Body', 'Glow_Eyes_1', 'Glow_Eyes_2', 'Nameplate', 'Hand'):
        assert need in m.pieces, f'{tag}: no {need} (MODELS.md, Monsters)'
    eye_parts = sorted(p for p in m.pieces if p.startswith('Glow_Eyes_'))
    assert eye_parts == ['Glow_Eyes_1', 'Glow_Eyes_2'], f'{tag}: eye parts {eye_parts}'
    assert 'Root' not in m.pieces and 'LOD_Proxy' not in m.pieces, f'{tag}: Root and LOD_Proxy are finish()\'s'
    # Coplanar faces between any two pieces, before they merge (markers left out).
    pieces = [o for p, objs in m.pieces.items() if p not in MARKERS for o in objs]
    for o in pieces:
        _closed(o, o.name)
    cop = coplanar_overlaps(pieces)
    assert not cop, f'{tag}: coplanar faces, will z-fight: {cop}'
    # Join every part.
    parts = {p: _join(p, objs) for p, objs in m.pieces.items()}
    visible = [ob for p, ob in parts.items() if p not in MARKERS]
    lo, hi = _bounds(visible)
    top = hi.z
    assert abs(top - h) <= HEIGHT_TOL * h, f'{tag}: {top:.2f} studs tall, target {h} +/- {HEIGHT_TOL:.0%}'
    assert lo.z >= -0.005, f'{tag}: {lo.z:.3f} under the floor'
    floats = t['shape'] == 'Float'
    if floats:
        blo, bhi = _bounds([parts['Body']])
        c = (blo + bhi) / 2
        assert abs(c.x) < 0.1 and abs(c.y) < 0.3, f'{tag}: origin not under the body ({c.x:.2f}, {c.y:.2f})'
    else:
        assert lo.z <= 0.02, f'{tag}: a walker floats {lo.z:.3f} over the floor'
        feet = [p for ob in visible for p in (ob.matrix_world @ v.co for v in ob.data.vertices) if p.z < 0.08]
        fx = (min(p.x for p in feet) + max(p.x for p in feet)) / 2
        fy = (min(p.y for p in feet) + max(p.y for p in feet)) / 2
        assert abs(fx) < 0.05 and abs(fy) < 0.3, f'{tag}: origin not between the feet ({fx:.2f}, {fy:.2f})'
    blo, bhi = _bounds([parts['Body']])
    body_c = (blo + bhi) / 2
    e1, e2 = (_bounds([parts[e]]) for e in ('Glow_Eyes_1', 'Glow_Eyes_2'))
    ec1, ec2 = (e1[0] + e1[1]) / 2, (e2[0] + e2[1]) / 2
    assert ec1.x > 0 > ec2.x, f'{tag}: Glow_Eyes_1 must be the monster\'s left (+X in Blender)'
    assert max(ec1.y, ec2.y) < body_c.y - 0.1, f'{tag}: the eyes are not on the front (-Y): it does not face -Z'
    assert abs(ec1.x + ec2.x) < 0.02 and abs(ec1.z - ec2.z) < 0.02, f'{tag}: the eyes are not a mirrored pair'
    nps = m.markers['Nameplate']
    assert nps.z >= top + 0.4 and math.hypot(nps.x, nps.y) < 0.6, f'{tag}: Nameplate not above the head'
    hd = m.markers['Hand']
    assert all(lo[i] - 0.3 <= hd[i] <= hi[i] + 0.3 for i in range(3)), f'{tag}: Hand off the model'
    # Root, exactly the contract's.
    bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=1.0)
    bm.transform(Matrix.Translation((0, 0, h / 2)) @ Matrix.Diagonal((2, 2, h, 1)))
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
    assert tris <= MONSTER_BUDGET, f'{tag}: {tris} triangles > {MONSTER_BUDGET}'
    assert ptris <= PROXY_BUDGET, f'{tag}: LOD_Proxy {ptris} > {PROXY_BUDGET}'
    assert max(r['triangles'] for r in records) <= MESH_TRIANGLE_CAP
    # Names in the FBX are the part names: Blender keeps one object per name, so
    # each model's parts are renamed to the bare names only while it exports.
    for p, ob in parts.items():
        other = bpy.data.objects.get(p)
        if other is not None and other is not ob:
            other.name = f'_held_{other.name}'
        ob.name = p
    bpy.ops.object.select_all(action='DESELECT')
    for ob in parts.values():
        ob.select_set(True)
    bpy.ops.export_scene.fbx(filepath=str(m.out / 'fbx' / f'{tag}.fbx'), use_selection=True,
                             object_types={'MESH'}, apply_unit_scale=True, apply_scale_options='FBX_SCALE_UNITS',
                             axis_forward='-Z', axis_up='Y', bake_anim=False, add_leaf_bones=False,
                             mesh_smooth_type='OFF', use_tspace=False, path_mode='STRIP', embed_textures=False)
    for p, ob in parts.items():
        ob.name = f'{tag}.{p}'
    rec = {
        'species': tag, 'shape': t['shape'], 'fbx': f'fbx/{tag}.fbx',
        'height_target': h, 'height': round(top, 3),
        'bounds_blender': [[round(c, 3) for c in lo], [round(c, 3) for c in hi]],
        'triangles': tris, 'triangles_proxy': ptris,
        'budget': {'model': MONSTER_BUDGET, 'proxy': PROXY_BUDGET, 'mesh_cap': MESH_TRIANGLE_CAP},
        'parts': records,
        'markers_blender': {k: [round(c, 4) for c in v] for k, v in m.markers.items()},
        'markers_roblox': {k: roblox(v) for k, v in m.markers.items()},
        'markers_roblox_from_root': {k: roblox(v - Vector((0, 0, h / 2))) for k, v in m.markers.items()},
        'coplanar_overlaps': 'none',
        'rig': 'none: static meshes, no bones, no Animations folder (the client bobs them)',
        'note': note,
    }
    _done.append(rec)
    print(f'{tag}: {tris} triangles + proxy {ptris}, {top:.2f} of {h} studs, parts {sorted(parts)}', flush=True)
    return rec


def finish_set(set_dir, offsets=4.2, sheet=True):
    """Write manifest.json, spread the models along X for the review (each model's
    own frame is its FBX), save the .blend and render the one Workbench sheet."""
    out = ROOT / 'blender' / set_dir
    manifest = {'set': set_dir, 'frame': 'Blender -Y front, +Z up, +X the monster\'s left; '
                'Roblox (x, y, z) = Blender (-x, z, y)', 'models': _done}
    (out / 'manifest.json').write_text(json.dumps(manifest, indent=2))
    (out / 'import_settings.luau').write_text(import_luau(_done), encoding='utf-8')
    cols, row_h = 5, 9.0
    for i, rec in enumerate(_done):
        coll = bpy.data.collections[rec['species']]
        for ob in coll.objects:
            ob.location.x += (i % cols) * offsets
            ob.location.z -= (i // cols) * row_h
            if ob.get('part') in ('Root', 'LOD_Proxy', 'Nameplate', 'Hand'):
                ob.hide_render = True
    rows = (len(_done) + cols - 1) // cols
    # A grey 5-stud person at the start of each row, for scale (not exported).
    person = bpy.data.collections.new('Person_5_studs')
    bpy.context.scene.collection.children.link(person)
    pm = bpy.data.materials.new('Person')
    pm.diffuse_color = (0.35, 0.35, 0.35, 1)
    px = -offsets
    for r in range(rows):
        z0 = -r * row_h
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
        _sheet(out / 'review' / 'sheet.png', px - 1.5, (min(cols, len(_done)) - 1) * offsets + 1.8,
               -(rows - 1) * row_h - 0.6, 7.6)


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
                         for p in r['parts'] if p['part'] not in MARKERS + ('Root',))
        rows.append(f'\t{r["species"]} = {{ {cols} }},')
    body = '\n'.join(rows)
    return f'''-- Generated by tools/monster_kit.py (import_luau); do not edit by hand.
-- Edit datamodel, after the FBXs are in Workspace. Then read back in a SEPARATE call.
local colours = {{
{body}
}}
local out = {{}}
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
	for _, name in {{ "Nameplate", "Hand" }} do
		local p = m:FindFirstChild(name)
		if p and p:IsA("BasePart") then
			local a = Instance.new("Attachment")
			a.Name = name
			a.Parent = root
			a.WorldPosition = p.Position
			p:Destroy()
		end
	end
	for _, p in m:GetDescendants() do
		if p:IsA("SurfaceAppearance") then
			p:Destroy()
		elseif p:IsA("MeshPart") then
			p.Anchored = true
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
	table.insert(out, id .. ": set")
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

        expected = {p['part'] for p in rec['parts']}
        check(set(meshes) == expected, f'part names round-trip ({len(expected)} parts)')
        need = {'Root', 'Body', 'Glow_Eyes_1', 'Glow_Eyes_2', 'Nameplate', 'Hand', 'LOD_Proxy'}
        check(need <= set(meshes), 'MODELS.md names present: Root, Body, Glow_Eyes_1/2, Nameplate, Hand, LOD_Proxy')
        check(all(PART_RE.match(n) for n in meshes), 'every other part an allowed name (Skin/Trim/Dark/Light/Glow_<Colour>_n)')
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
        vis = [p for n_, o in meshes.items() if n_ not in ('Root', 'LOD_Proxy', 'Nameplate', 'Hand') for p in world(o)]
        top = max(p.z for p in vis)
        h = rec['height_target']
        check(abs(top - h) <= HEIGHT_TOL * h, f'height {top:.2f} studs against {h} (+/- 10 %)')
        check(min(p.z for p in vis) >= -0.005, 'nothing under the floor')
        rp = world(meshes['Root'])
        rlo = Vector([min(p[i] for p in rp) for i in range(3)])
        rhi = Vector([max(p[i] for p in rp) for i in range(3)])
        check((rhi - rlo - Vector((2, 2, h))).length < 1e-3 and abs(rlo.z) < 1e-3
              and abs(rlo.x + 1) < 1e-3 and abs(rlo.y + 1) < 1e-3, f'Root 2 x {h} x 2, bottom at 0, centred on the origin')
        for mk in ('Nameplate', 'Hand'):
            pts = world(meshes[mk])
            c = sum(pts, Vector()) / len(pts)
            assert (c - Vector(rec['markers_blender'][mk])).length < 1e-3, (sid, mk, tuple(c))
        check(True, 'Nameplate and Hand markers where the manifest says')
        ey = [sum(world(meshes[e]), Vector()) / len(meshes[e].data.vertices) for e in ('Glow_Eyes_1', 'Glow_Eyes_2')]
        bp = world(meshes['Body'])
        by = (min(p.y for p in bp) + max(p.y for p in bp)) / 2
        check(max(e.y for e in ey) < by and ey[0].x > 0 > ey[1].x, 'eyes on the front (-Y, Roblox -Z), Glow_Eyes_1 on the left')
        report['models'][sid] = {'checks': checks, 'triangles': total, 'triangles_proxy': rec['triangles_proxy'],
                                 'height': round(top, 3), 'height_target': h}
        report['collision_precise'][sid] = []
    report['not_validated'] = [
        'nothing in Studio: the import, the axis conversion, the marker positions there, the colours arriving',
        'whether the importer carries a material\'s plain colour to MeshPart.Color (manifest has every colour)',
        'the look at the game\'s camera and at Tiny 0.5 / Giant 1.5 scale',
        'animations: none exist (no rig)']
    (root / 'validation.json').write_text(json.dumps(report, indent=2))
    print(f'validation.json: {len(report["models"])} models passed', flush=True)
    return report
