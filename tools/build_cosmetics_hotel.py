"""The hotel cosmetics (MODELS.md, "Cosmetics"): the Sign- and Lobby-slot models, a draft for August.

Seven models, one per Sign or Lobby row of src/shared/Cosmetics.luau, each on
tools/hotel_kit.py (begin + shapes + finish) as kind 'Cosmetic':

  Sign slot  (origin: the centre of the hotel sign's Board front face, front -Z)
    Cosmetic_PumpkinSign   the board set in a big lobed pumpkin, stem, leaves, a curl;
                           the carved edge glows round the board (Glow_Warm_1)
    Cosmetic_IcicleSign    snow piled on the board's top, front and back of the crest,
                           drifts over both ends, icicles off the ends and under the board
    Cosmetic_LanternSign   two iron lanterns on scroll brackets at the board's top
                           corners (Glow_Warm_1, Glow_Warm_2)
    Cosmetic_Family1       Haunted Manor crest: a violet heater shield with a ghost,
                           gold rim, bat wings, a crescent finial
    Cosmetic_Family2       Frostfang crest: a frost-blue shield with a snowflake,
                           snow on top, two curved fangs rising beside it
  Lobby slot (origin: the lobby's Entrance attachment, on the floor at the threshold, front -Z)
    Cosmetic_BatBunting    paper bats on a string in two swags across the arch
    Cosmetic_FairyLights   a wire in four swags with 12 warm bulbs (Glow_Warm_1..12)

THE FIT, measured from the two hotel kits' own FBX (blender/hotel/<kit>/fbx/
HotelSign.fbx and Lobby.fbx), loaded at the start: in a sign cosmetic's frame
the Board is x -8..8, y -3..3, z 0..0.6 (the same 16 x 6 x 0.6 in both kits,
hotel_kit.check_piece enforces it). No triangle of a sign cosmetic enters the
Board's face extruded forward (x -8..8, y -3..3, z < 0.6, plus 0.015), and none
touches either kit's sign (posts, Board, Crest, its glow). A lobby cosmetic
stays within the arch's span (|x| <= 5.5, the narrower kit's), in front of it
(z <= 0), its lowest point at least 8 studs up, and touches neither kit's
lobby. These are Piece.checks: finish() refuses on them and validate() re-runs
them on the re-imported FBX; the numbers go into manifest.json and
validation.json ("clearances").

Nothing collides (CanCollide, CanQuery, CanTouch off: the generated
import_fixup.luau sets them, as HotelKit.cosmetic does at runtime). Every model
has a Root (1 x 0.2 x 1, invisible) and a LOD_Proxy of a few boxes.

    blender -b --python-exit-code 1 -P tools/build_cosmetics_hotel.py [-- nopreview] [-- only A,B]

Writes blender/cosmetics/hotel/: fbx/<Name>.fbx, manifest.json,
validation.json, import_fixup.luau, the .blend, review/front.png,
review/angle.png and review/closeup.png (Workbench only, small).
"""
import json
import math
import sys
from pathlib import Path

import bpy
from mathutils import Vector, Matrix
from mathutils.bvhtree import BVHTree

sys.path.insert(0, str(Path(__file__).resolve().parent))
import hotel_kit as K  # noqa: E402
from hotel_kit import begin, finish, box, span, cyl, lathe, sphere, prism, declare, at  # noqa: E402

SET = 'cosmetics/hotel'
KITS = ['haunted_manor', 'frostfang_lodge']
SIGN_ORIGIN = Vector((0, 8, -0.3))      # the Board's front-face centre in the HotelSign frame
BOARD = (Vector((-8, -3, 0)), Vector((8, 3, 0.6)))      # the Board in a sign cosmetic's frame
FACE_MARGIN = 0.015
ARCH_X = 5.5            # the arch's outer half-width: pillars 5.5 in both kits, ArchTop 5.5 / 5.9
LOBBY_CLEAR = 8.0       # MODELS.md: the lowest part at least 8 studs above the threshold
SIGNS = ['Cosmetic_PumpkinSign', 'Cosmetic_IcicleSign', 'Cosmetic_LanternSign', 'Cosmetic_Family1',
         'Cosmetic_Family2']
LOBBIES = ['Cosmetic_BatBunting', 'Cosmetic_FairyLights']

# The set's palette: the Cosmetics.luau colours first (pumpkin, ice, lantern amber, violet,
# frost, bat plum, fairy bulb), then what dresses them. A third value is a glow key.
PALETTE = [
    ('pumpkin', (245, 140, 30)), ('pumpkin_dark', (205, 100, 25)), ('pumpkin_light', (255, 172, 70)),
    ('ice', (200, 235, 255)), ('ice_deep', (150, 205, 240)), ('ice_dark', (100, 160, 215)),
    ('amber', (255, 200, 110)), ('violet', (150, 90, 200)), ('violet_dark', (100, 60, 145)),
    ('frost', (170, 220, 255)), ('plum_deep', (40, 30, 50)), ('plum', (78, 56, 100)),
    ('snow', (245, 250, 255)), ('snow_shade', (214, 228, 242)),
    ('stem', (118, 92, 50)), ('stem_dark', (84, 64, 36)), ('leaf', (112, 172, 72)), ('leaf_dark', (72, 128, 56)),
    ('iron', (55, 56, 68)), ('iron_light', (92, 94, 108)), ('gold', (226, 186, 96)), ('gold_dark', (172, 132, 62)),
    ('lilac', (196, 168, 232)), ('navy', (48, 62, 110)), ('bone', (242, 234, 212)), ('cream', (250, 240, 225)),
    ('black', (30, 28, 36)), ('string', (226, 214, 186)), ('wire', (52, 74, 56)), ('grey', (120, 122, 132)),
    ('flame', (255, 205, 120), 'Warm'), ('bulb', (255, 230, 150), 'Warm'),
]


# --- The two kits' sign and lobby, in each slot's frame ------------------------------------------

KIT_TRIS = {}       # (slot, kit) -> {part: [(a, b, c), ...]} in the cosmetic's frame


def load_kits():
    """Each kit's HotelSign and Lobby FBX, as triangles in the cosmetic frames (Roblox studs)."""
    for kit in KITS:
        for slot, fname, offset in (('Sign', 'HotelSign', SIGN_ORIGIN), ('Lobby', 'Lobby', Vector())):
            for ob in list(bpy.data.objects):
                bpy.data.objects.remove(ob)
            bpy.context.scene.unit_settings.scale_length = .01
            bpy.ops.import_scene.fbx(filepath=str(K.ROOT / 'blender' / 'hotel' / kit / 'fbx' / f'{fname}.fbx'))
            bpy.context.view_layer.update()
            parts = {}
            for ob in bpy.context.scene.objects:
                if ob.type != 'MESH' or ob.name.split('.')[0] in ('Root', 'LOD_Proxy'):
                    continue
                parts[ob.name.split('.')[0]] = [tuple(p - offset for p in t) for t in K._tris_rb(ob)]
            KIT_TRIS[(slot, kit)] = parts
    for ob in list(bpy.data.objects):
        bpy.data.objects.remove(ob)
    for coll in (bpy.data.meshes, bpy.data.materials, bpy.data.images):
        for x in list(coll):
            if x.users == 0:
                coll.remove(x)
    # The sign's Board is the same box in both kits (the check the brief asks for).
    for kit in KITS:
        lo, hi = K._bounds([p for t in KIT_TRIS[('Sign', kit)]['Board'] for p in t])
        assert (lo - BOARD[0]).length < 0.02 and (hi - BOARD[1]).length < 0.02, f'{kit} Board {lo} {hi}'


def _bvh(tris):
    verts, polys = [], []
    for t in tris:
        polys.append((len(verts), len(verts) + 1, len(verts) + 2))
        verts.extend(Vector(p) for p in t)
    return BVHTree.FromPolygons(verts, polys, all_triangles=True)


_KIT_BVH = {}


def kit_bvh(slot, kit, part):
    key = (slot, kit, part)
    if key not in _KIT_BVH:
        _KIT_BVH[key] = _bvh(KIT_TRIS[(slot, kit)][part])
    return _KIT_BVH[key]


def tri_box(tri, lo, hi):
    """Whether a triangle and an axis-aligned box overlap (separating axes)."""
    c, h = (lo + hi) / 2, (hi - lo) / 2
    v = [Vector(p) - c for p in tri]
    for i in range(3):
        if min(p[i] for p in v) > h[i] or max(p[i] for p in v) < -h[i]:
            return False
    e = [v[1] - v[0], v[2] - v[1], v[0] - v[2]]
    n = e[0].cross(e[1])
    if abs(n.dot(v[0])) > h.x * abs(n.x) + h.y * abs(n.y) + h.z * abs(n.z):
        return False
    for ei in e:
        for ax in (Vector((1, 0, 0)), Vector((0, 1, 0)), Vector((0, 0, 1))):
            a = ax.cross(ei)
            if a.length < 1e-12:
                continue
            ps = [a.dot(p) for p in v]
            r = h.x * abs(a.x) + h.y * abs(a.y) + h.z * abs(a.z)
            if min(ps) > r or max(ps) < -r:
                return False
    return True


def box_dist(p, lo, hi):
    q = Vector((min(max(p.x, lo.x), hi.x), min(max(p.y, lo.y), hi.y), min(max(p.z, lo.z), hi.z)))
    return (p - q).length


def _kit_clearance(piece, tris, slot):
    """Faults and nearest distances against both kits' parts (not Root, not LOD_Proxy)."""
    faults, near = [], {}
    for kit in KITS:
        best = (1e9, None, None)
        for kpart in KIT_TRIS[(slot, kit)]:
            kb = kit_bvh(slot, kit, kpart)
            for part, ts in tris.items():
                if part in ('Root', 'LOD_Proxy') or not ts:
                    continue
                hits = _bvh(ts).overlap(kb)
                if hits:
                    faults.append(f'{part} intersects the {kit} {kpart} ({len(hits)} triangle pairs)')
                for t in ts:
                    for p in t:
                        loc, nrm, idx, d = kb.find_nearest(Vector(p))
                        if d is not None and d < best[0]:
                            best = (d, part, kpart)
        near[kit] = {'min_distance': round(best[0], 3), 'part': best[1], 'kit_part': best[2]}
    return faults, near


def sign_checks(piece, tris, stage):
    """The face stays clear; nothing touches either kit's sign."""
    faults = []
    lo = BOARD[0] - Vector((FACE_MARGIN, FACE_MARGIN, 0)) + Vector((0, 0, -1000))
    hi = BOARD[1] + Vector((FACE_MARGIN, FACE_MARGIN, FACE_MARGIN))
    face_lo, face_hi = BOARD[0] + Vector((0, 0, -1000)), BOARD[1]
    nearest, near_part = 1e9, None
    for part, ts in tris.items():
        if part == 'Root':          # invisible, CanQuery off: sits inside the Board
            continue
        bad = sum(1 for t in ts if tri_box(t, lo, hi))
        if bad:
            faults.append(f'{part}: {bad} triangles cover the Board front face (x -8..8, y -3..3, in front)')
        for t in ts:
            for p in t:
                d = box_dist(Vector(p), face_lo, face_hi)
                if d < nearest:
                    nearest, near_part = d, part
    kf, near = _kit_clearance(piece, tris, 'Sign')
    faults += kf
    allp = [Vector(p) for part, ts in tris.items() if part not in ('Root', 'LOD_Proxy') for t in ts for p in t]
    blo, bhi = K._bounds(allp)
    piece.measured[stage] = {
        'board_face': {'nearest_vertex_to_face_volume': round(nearest, 3), 'part': near_part,
                       'face_volume': 'x -8..8, y -3..3, z -inf..0.6 (the face extruded forward, and the board)'},
        'kits': near, 'bounds': {'lo': K.v3(blo, 3), 'hi': K.v3(bhi, 3), 'size': K.v3(bhi - blo, 3)}}
    return faults


def lobby_checks(piece, tris, stage):
    """Inside the arch's span, in front of it, at least 8 studs up; nothing touches either kit's lobby."""
    faults = []
    lowest, low_part = 1e9, None
    xs, zs = [], []
    for part, ts in tris.items():
        if part == 'Root':          # invisible, on the floor at the origin, CanQuery off
            continue
        for t in ts:
            for p in t:
                if p[1] < lowest:
                    lowest, low_part = p[1], part
                xs.append(p[0])
                zs.append(p[2])
    if lowest < LOBBY_CLEAR:
        faults.append(f'{low_part} reaches down to {lowest:.2f}, under the {LOBBY_CLEAR}-stud clearance')
    if max(abs(x) for x in xs) > ARCH_X + 1e-3:
        faults.append(f'reaches |x| {max(abs(x) for x in xs):.2f}, outside the arch span {ARCH_X}')
    if max(zs) > 1e-3:
        faults.append(f'reaches z {max(zs):.3f}: behind the arch front (z 0)')
    kf, near = _kit_clearance(piece, tris, 'Lobby')
    faults += kf
    allp = [Vector(p) for part, ts in tris.items() if part not in ('Root', 'LOD_Proxy') for t in ts for p in t]
    blo, bhi = K._bounds(allp)
    piece.measured[stage] = {
        'lowest_point': round(lowest, 3), 'lowest_part': low_part, 'person_headroom': round(lowest - K.PERSON, 3),
        'max_abs_x': round(max(abs(x) for x in xs), 3), 'max_z': round(max(zs), 3),
        'kits': near, 'bounds': {'lo': K.v3(blo, 3), 'hi': K.v3(bhi, 3), 'size': K.v3(bhi - blo, 3)}}
    return faults


def cosmetic(name, slot):
    """A cosmetic piece: Root 1 x 0.2 x 1 (inside the Board for a sign, on the floor for a lobby
    one), its envelope, its checks; every part declared non-colliding as it is made."""
    if slot == 'Sign':
        p = begin(name, 'Cosmetic', (1, 0.2, 1), root_centre=(0, 0, 0.3))
        p.allowed = ((-12, -6, -2), (12, 10, 4))
        p.checks.append(sign_checks)
    else:
        p = begin(name, 'Cosmetic', (1, 0.2, 1), root_centre=(0, 0.1, 0))
        p.allowed = ((-ARCH_X, 0, -2), (ARCH_X, 12, 0.5))   # z 0.5: Root; the rest is held to z <= 0
        p.checks.append(lobby_checks)
    p.slot = slot
    p.measured = {}
    return p


def done(note):
    for part in K.P.parts:
        declare(part, False)
    return finish(proxy=False, note=note)


# --- Shapes -------------------------------------------------------------------------------------

def rod(part, a, b, r, col, n=6, r_b=None):
    """A cylinder (or a cone, r_b) from point a to point b."""
    a, b = Vector(a), Vector(b)
    d = b - a
    q = Vector((0, 1, 0)).rotation_difference(d.normalized())
    cyl(part, (0, 0, 0), r, d.length, col, n=n, r_top=r_b, m=Matrix.Translation(a) @ q.to_matrix().to_4x4())


def chain(part, pts, r0, r1, col, n=6, tip=True):
    """A tapered tube through points (a stem, a fang); `tip` ends it in a point."""
    k = len(pts) - 1
    for i in range(k):
        ra, rb = r0 + (r1 - r0) * i / k, r0 + (r1 - r0) * (i + 1) / k
        a, b = Vector(pts[i]), Vector(pts[i + 1])
        if i == k - 1 and tip:
            rod(part, a, b, ra, col, n=n, r_b=0.0)
        else:
            d = (b - a).normalized()
            rod(part, a, b + d * rb * 0.6, ra, col, n=n, r_b=rb)


def ring(part, c, r, t, col, n=10, k=5, rx=90, ry=0, rz=0):
    """A torus of radius r and tube t, in the xy plane by default (facing -Z)."""
    prof = [(r + t * math.cos(2 * math.pi * i / k), t * math.sin(2 * math.pi * i / k)) for i in range(k)]
    lathe(part, prof, col, n=n, closed=True, m=at(c, rx=rx, ry=ry, rz=rz))


def swag(p0, p1, sag, t):
    """A point on a string hung from p0 to p1 sagging `sag` at its middle (a parabola)."""
    p0, p1 = Vector(p0), Vector(p1)
    return p0.lerp(p1, t) - Vector((0, 4 * sag * t * (1 - t), 0))


def string(part, p0, p1, sag, r, col, n=5, steps=8):
    pts = [swag(p0, p1, sag, i / steps) for i in range(steps + 1)]
    for a, b in zip(pts, pts[1:]):
        d = (b - a).normalized()
        rod(part, a - d * r * 0.5, b + d * r * 0.5, r, col, n=n)
    return pts


def shield_pts(w, top, mid, bottom, n=6):
    """A heater shield's outline: a straight top, straight sides down to `mid`, curving to a point."""
    hw = w / 2
    right = [(hw * math.cos(math.pi / 2 * i / n), mid - (mid - bottom) * math.sin(math.pi / 2 * i / n))
             for i in range(n + 1)]
    left = [(-x, y) for x, y in reversed(right[:-1])]
    return [(-hw + 0.25, top), (hw - 0.25, top), (hw, top - 0.25)] + right + left + [(-hw, top - 0.25)]


def bat_pts(c, s):
    """A bat silhouette (ears, round head, scalloped wings) centred on c, wingspan 2 s."""
    right = [(0.13, 0.44), (0.21, 0.24), (0.46, 0.31), (0.76, 0.42), (1.0, 0.34), (0.88, -0.02), (0.73, 0.1),
             (0.58, -0.12), (0.43, 0.01), (0.27, -0.17), (0.12, -0.3)]
    pts = [(0, 0.31)] + right + [(0, -0.38)] + [(-x, y) for x, y in reversed(right)]
    return [(c[0] + x * s, c[1] + y * s) for x, y in pts]


def flake(part, c, r, col, t=0.06):
    """A six-armed snowflake facing -Z: three crossed bars and a little tip on each arm."""
    for k in range(3):
        box(part, (0, 0, 0), (2 * r, r * 0.24, t), col, m=at(c, rz=k * 60))
    for k in range(6):
        a = math.radians(k * 60)
        p = (c[0] + 0.66 * r * math.cos(a), c[1] + 0.66 * r * math.sin(a), c[2])
        box(part, (0, 0, 0), (r * 0.46, r * 0.16, t), col, m=at(p, rz=k * 60 + 90))


def icicle(part, x, y, z, length, r=0.16, col='ice', n=5):
    lathe(part, [(0, y - length), (r, y)], col, n=n, base=(x, 0, z))


def proxy_box(lo, hi):
    span('LOD_Proxy', lo, hi, 'grey')


# --- Sign cosmetics (origin: the Board's front-face centre; the Board is x -8..8, y -3..3, z 0..0.6) ---

def pumpkin_sign():
    cosmetic('Cosmetic_PumpkinSign', 'Sign')
    # The pumpkin: seven upright lobes behind the board, front at z >= 1.05 (clear of the posts'
    # backs at 0.7 and the glow at 1.0), the board its carved face.
    lobes = [(0, 2.2, 5.2, 1.3, 'pumpkin'), (3.1, 2.2, 5.05, 1.25, 'pumpkin_light'),
             (6.0, 2.05, 4.75, 1.2, 'pumpkin'), (8.6, 1.75, 4.15, 1.05, 'pumpkin_light')]
    for x, rx, ry, rz, col in lobes:
        for sx in ((1, -1) if x else (1,)):
            sphere('Body', (sx * x, 0.35, 1.07 + rz), (rx, ry, rz), col, n=10, rings=8)
    # The core the lobes bulge from: it closes the gaps between them, so the grooves read as creases.
    sphere('Body', (0, 0.35, 2.55), (9.7, 4.75, 1.25), 'pumpkin_dark', n=16, rings=6)
    # The stem, curving back, a leaf each side and a curl of vine.
    chain('Body', [(0, 4.6, 2.4), (0.05, 5.6, 2.35), (0.35, 6.4, 2.25), (0.8, 6.9, 2.15)], 0.5, 0.36, 'stem',
          n=7, tip=False)
    lathe('Body', [(0, 6.65), (0.36, 6.75), (0.3, 7.08), (0, 7.12)], 'stem_dark', n=7, base=(0.8, 0, 2.15))
    leaf = [(0, 0), (0.7, 0.55), (1.3, 0.35), (1.6, 0.85), (2.3, 0.6), (2.75, 0.2), (2.2, -0.15), (2.5, -0.55),
            (1.6, -0.45), (0.9, -0.55)]
    prism('Body', leaf, -0.08, 0.08, 'leaf', m=at((0.3, 5.15, 1.6), rx=-12, rz=14))
    prism('Body', [(-x, y) for x, y in leaf], -0.08, 0.08, 'leaf_dark', m=at((-0.3, 5.25, 1.7), rx=-12, rz=-18))
    curl = [(-0.6 - 0.75 * math.cos(a) * (1 - a / 9), 5.6 + 0.7 * math.sin(a) * (1 - a / 9), 1.45)
            for a in [i * 0.55 for i in range(12)]]
    chain('Body', curl, 0.11, 0.06, 'leaf_dark', n=5)
    # The carved edge: warm light round the board, just outside its outline and behind its back face.
    z0, z1, g = 0.75, 1.0, 0.3
    span('Glow_Warm_1', (-8.04 - g, -3.04 - g, z0), (-8.04, 3.04 + g, z1), 'flame')
    span('Glow_Warm_1', (8.04, -3.04 - g, z0), (8.04 + g, 3.04 + g, z1), 'flame')
    span('Glow_Warm_1', (-8.04, 3.04, z0), (8.04, 3.04 + g, z1), 'flame')
    span('Glow_Warm_1', (-8.04, -3.04 - g, z0), (8.04, -3.04, z1), 'flame')
    proxy_box((-10.35, -4.8, 1.07), (10.35, 5.5, 3.65))
    proxy_box((-0.5, 5.5, 1.9), (1.2, 7.1, 2.8))
    return done('the board set in a seven-lobed pumpkin (the board its carved face), a curved stem, two '
                'leaves, a vine curl; warm light round the board\'s edge')


def icicle_sign():
    cosmetic('Cosmetic_IcicleSign', 'Sign')
    # Snow on the top, in front of and behind each kit's crest (which rises out of it): the
    # Frostfang crest's own snow strip is z -0.05..0.65, the Manor's gable 0.05..0.55.
    span('Body', (-8.9, 3.02, -0.82), (8.9, 3.5, -0.08), 'snow', bevel=0.12)
    span('Body', (-8.9, 3.02, 0.7), (8.9, 3.45, 1.32), 'snow', bevel=0.12)
    k = 0
    x = -8.3
    while x <= 8.31:
        r = (0.95, 0.75, 1.05, 0.8)[k % 4]
        col = 'snow' if k % 2 == 0 else 'snow_shade'
        sphere('Body', (x, 3.6, -0.45), (r, 0.42 + 0.06 * (k % 3), 0.36), col, n=8, rings=4)
        sphere('Body', (x + 0.6, 3.42, 1.01), (r * 0.9, 0.36, 0.3), col, n=8, rings=4)
        x += 1.38
        k += 1
    # Over each end: a cap joining front and back, a drift down the end face, icicles off both.
    for sx in (-1, 1):
        def X(a):
            return sx * a
        span('Body', (min(X(8.04), X(9.3)), 2.85, -0.85), (max(X(8.04), X(9.3)), 3.7, 1.35), 'snow', bevel=0.18)
        sphere('Body', (X(8.75), 3.75, 0.25), (0.75, 0.5, 1.05), 'snow_shade', n=8, rings=4)
        span('Body', (min(X(8.04), X(8.62)), 1.3, -0.22), (max(X(8.04), X(8.62)), 2.95, 0.85), 'snow', bevel=0.12)
        sphere('Body', (X(8.5), 1.45, 0.3), (0.4, 0.32, 0.6), 'snow', n=8, rings=4)
        for z, ln in ((-0.6, 1.5), (-0.1, 0.9), (0.45, 1.7), (1.05, 1.1)):
            icicle('Body', X(9.0), 2.88, z, ln, r=0.17, col='ice' if z < 0.4 else 'ice_deep')
        for z, ln in ((-0.05, 1.3), (0.45, 0.8)):
            icicle('Body', X(8.42), 1.32, z, ln, r=0.15, col='ice_deep')
    # Icicles under the board, clear of the posts (x 6.6..7.4) and in front of the Lodge's own.
    for x, ln in ((-7.85, 0.9), (-5.75, 1.45), (-4.1, 0.8), (-3.0, 1.2), (-1.45, 0.7), (0.45, 1.5), (2.55, 0.85),
                  (3.15, 1.25), (4.65, 0.75), (5.9, 1.3), (7.85, 1.0)):
        icicle('Body', x, -3.03, -0.02, ln, r=0.17, col='ice' if ln > 1 else 'ice_deep')
    proxy_box((-9.3, 3.02, -0.85), (9.3, 4.0, -0.08))
    proxy_box((-9.3, 3.02, 0.7), (9.3, 3.8, 1.35))
    proxy_box((-9.3, 1.3, -0.85), (-8.04, 3.02, 1.35))
    proxy_box((8.04, 1.3, -0.85), (9.3, 3.02, 1.35))
    return done('snow piled along the top (the crest rising out of it), drifts over both ends, icicles '
                'off the ends and under the board')


def lantern(sx, n):
    """A scroll bracket on the board's end face and an iron lantern hanging from it."""
    def X(a):
        return sx * a
    zc, cx = 0.3, 9.95
    span('Body', (min(X(8.02), X(8.18)), 1.35, 0.04), (max(X(8.02), X(8.18)), 2.95, 0.56), 'iron', bevel=0.04)
    for y in (1.65, 2.65):
        sphere('Body', (X(8.2), y, zc), 0.08, 'gold', n=6, rings=3)
    rod('Body', (X(8.12), 2.6, zc), (X(cx + 0.12), 2.6, zc), 0.1, 'iron', n=6)
    rod('Body', (X(8.12), 1.65, zc), (X(9.05), 2.6, zc), 0.08, 'iron', n=6)
    ring('Body', (X(8.95), 3.02, zc), 0.32, 0.07, 'iron', n=10, k=4)
    ring('Body', (X(9.55), 2.95, zc), 0.22, 0.06, 'iron', n=8, k=4)
    rod('Body', (X(cx), 2.62, zc), (X(cx), 2.3, zc), 0.05, 'iron', n=5)
    ring('Body', (X(cx), 2.38, zc), 0.12, 0.04, 'iron', n=8, k=4, ry=90)
    # The lantern: a hipped roof with a finial, a square frame, a candle and its flame.
    lathe('Body', [(0.95, 1.62), (0.2, 2.18), (0, 2.25)], 'iron', n=4, base=(X(cx), 0, zc), phase=math.pi / 4)
    sphere('Body', (X(cx), 2.27, zc), 0.1, 'gold', n=6, rings=3)
    span('Body', (X(cx) - 0.72, 1.48, zc - 0.72), (X(cx) + 0.72, 1.64, zc + 0.72), 'gold', bevel=0.04)
    span('Body', (X(cx) - 0.68, -0.12, zc - 0.68), (X(cx) + 0.68, 0.08, zc + 0.68), 'iron', bevel=0.05)
    lathe('Body', [(0.3, -0.12), (0.12, -0.42), (0, -0.48)], 'iron', n=4, base=(X(cx), 0, zc), phase=math.pi / 4)
    for ox in (-0.6, 0.6):
        for oz in (-0.6, 0.6):
            box('Body', (X(cx) + ox, 0.78, zc + oz), (0.13, 1.42, 0.13), 'iron')
    for y in (0.5, 1.05):
        for oz in (-0.6, 0.6):
            box('Body', (X(cx), y, zc + oz), (1.1, 0.07, 0.07), 'iron_light')
    cyl('Body', (X(cx), 0.08, zc), 0.22, 0.42, 'cream', n=7)
    sphere(f'Glow_Warm_{n}', (X(cx), 0.86, zc), (0.26, 0.4, 0.26), 'flame', n=8, rings=5)
    proxy_box((min(X(8.02), X(cx + 0.75)), -0.45, zc - 0.75), (max(X(8.02), X(cx + 0.75)), 2.95, zc + 0.75))


def lantern_sign():
    cosmetic('Cosmetic_LanternSign', 'Sign')
    lantern(-1, 1)
    lantern(1, 2)
    return done('two iron lanterns with candle flames hanging from scroll brackets on the board\'s ends, '
                'at its top corners')


def family_shield(rim, field):
    """The crest's shield, standing on the board's top edge in front of the kit's own crest
    (whose front is z -0.05): rim z -0.6..-0.15, the field 0.03 proud of it."""
    prism('Body', shield_pts(3.9, 7.4, 5.7, 3.12), -0.6, -0.15, rim)
    prism('Body', shield_pts(3.3, 7.1, 5.7, 3.6), -0.63, -0.45, field)


def family1():
    cosmetic('Cosmetic_Family1', 'Sign')
    family_shield('gold', 'violet')
    # A ghost on the field, with dark eyes and an O of a mouth.
    ghost = [(0.85 * math.cos(math.pi * i / 8), 5.95 + 0.85 * math.sin(math.pi * i / 8)) for i in range(9)]
    ghost += [(-0.85, 4.75), (-0.55, 5.0), (-0.28, 4.6), (0, 4.95), (0.28, 4.6), (0.55, 5.0), (0.85, 4.75)]
    prism('Body', ghost, -0.66, -0.58, 'cream')
    for x in (-0.3, 0.3):
        sphere('Body', (x, 6.05, -0.66), (0.13, 0.19, 0.04), 'plum_deep', n=6, rings=3)
    sphere('Body', (0, 5.55, -0.66), (0.11, 0.14, 0.04), 'plum_deep', n=6, rings=3)
    # Bat wings from behind the shield: a scalloped membrane, its bones, and a claw at the top.
    for sx in (-1, 1):
        wing = [(1.4, 6.75), (2.6, 7.35), (4.0, 7.75), (5.3, 7.95), (6.35, 8.15), (6.1, 6.95), (5.5, 6.2),
                (5.05, 6.6), (4.45, 5.5), (3.85, 5.95), (3.15, 4.85), (2.6, 5.35), (1.6, 4.7)]
        pts = [(sx * x, y) for x, y in wing]
        prism('Body', pts if sx > 0 else list(reversed(pts)), -0.42, -0.3, 'plum')
        for (x, y) in ((6.1, 6.95), (4.45, 5.5), (3.15, 4.85)):
            rod('Body', (sx * 1.6, 6.6, -0.44), (sx * x, y, -0.44), 0.08, 'plum_deep', n=5)
        rod('Body', (sx * 1.6, 6.6, -0.44), (sx * 6.35, 8.15, -0.44), 0.11, 'plum_deep', n=5)
        lathe('Body', [(0.12, 0), (0, 0.42)], 'plum_deep', n=5, m=at((sx * 6.35, 8.12, -0.44), rz=-sx * 35))
    # A crescent moon finial on the shield's top.
    moon = [(0.62 * math.cos(a), 8.1 + 0.62 * math.sin(a)) for a in [math.radians(t) for t in range(160, 381, 20)]]
    moon += [(0.5 * math.cos(a), 8.34 + 0.5 * math.sin(a)) for a in [math.radians(t) for t in range(370, 169, -25)]]
    prism('Body', moon, -0.5, -0.25, 'gold')
    span('Body', (-0.22, 7.38, -0.48), (0.22, 7.62, -0.27), 'gold_dark', bevel=0.04)
    proxy_box((-1.95, 3.12, -0.6), (1.95, 8.7, -0.15))
    proxy_box((-6.35, 4.7, -0.45), (6.35, 8.2, -0.3))
    return done('a violet heater shield with a gold rim and a little ghost, spread bat wings, a gold crescent '
                'finial; stands on the board\'s top edge in front of the kit\'s crest')


def family2():
    cosmetic('Cosmetic_Family2', 'Sign')
    family_shield('ice_dark', 'frost')
    flake('Body', (0, 5.85, -0.65), 1.05, 'snow', t=0.07)
    span('Body', (-0.16, 5.69, -0.7), (0.16, 6.01, -0.66), 'ice_dark')
    # Snow on the shield's top, a lump over each corner.
    span('Body', (-2.0, 7.38, -0.68), (2.0, 7.62, -0.1), 'snow', bevel=0.1)
    for x, r in ((-1.45, 0.62), (-0.35, 0.72), (0.75, 0.6), (1.6, 0.45)):
        sphere('Body', (x, 7.62, -0.4), (r, 0.3, 0.3), 'snow' if x < 0.5 else 'snow_shade', n=8, rings=4)
    # Two fangs rising beside the shield, curving out and in again (in front of the kit's crest).
    for sx in (-1, 1):
        pts = [(sx * 1.55, 3.55, -0.62), (sx * 2.45, 3.95, -0.62), (sx * 3.25, 4.75, -0.62),
               (sx * 3.65, 5.75, -0.62), (sx * 3.65, 6.75, -0.62), (sx * 3.35, 7.65, -0.62)]
        chain('Body', pts, 0.4, 0.14, 'bone', n=7)
        ring('Body', (sx * 2.0, 3.75, -0.62), 0.4, 0.1, 'ice_dark', n=8, k=4, rx=0, rz=-sx * math.degrees(math.atan2(0.9, 0.4)))
    proxy_box((-1.95, 3.12, -0.68), (1.95, 7.9, -0.1))
    proxy_box((-3.95, 3.4, -0.95), (-1.6, 7.7, -0.3))
    proxy_box((1.6, 3.4, -0.95), (3.95, 7.7, -0.3))
    return done('a frost-blue heater shield with an ice rim and a white snowflake, snow on its top, two '
                'curved fangs rising beside it; stands on the board\'s top edge in front of the kit\'s crest')


# --- Lobby cosmetics (origin: the Entrance, on the floor at the threshold; the arch front is z 0) ---

# Where a string is hung on the arch's front: each point is solid in both kits' arches
# (the Manor's pointed top and the Lodge's snowy gable), measured from their outlines.
HOOKS = [(-5.0, 9.45), (-2.5, 10.3), (0.0, 10.8), (2.5, 10.3), (5.0, 9.45)]
HOOK_Z, STRING_Z = -0.16, -0.2


def hook(x, y, col='gold'):
    sphere('Body', (x, y, HOOK_Z), (0.14, 0.14, 0.14), col, n=8, rings=4)


def bat_bunting():
    cosmetic('Cosmetic_BatBunting', 'Lobby')
    ends = [HOOKS[0], HOOKS[2], HOOKS[4]]
    for x, y in ends:
        hook(x, y)
    # A paper bow at the middle hook.
    for sx in (-1, 1):
        prism('Body', [(0, 10.8), (sx * 0.45, 11.05), (sx * 0.45, 10.55)], STRING_Z - 0.04, STRING_Z + 0.04, 'violet')
    k = 0
    for a, b in zip(ends, ends[1:]):
        p0, p1 = Vector((a[0], a[1], STRING_Z)), Vector((b[0], b[1], STRING_Z))
        string('Body', p0, p1, 0.55, 0.05, 'string')
        for t in (0.18, 0.5, 0.82):
            p = swag(p0, p1, 0.55, t)
            s = 0.85 if k % 2 == 0 else 0.72
            c = (p.x, p.y - 0.2 * s / 0.62)
            col = 'plum_deep' if k % 2 == 0 else 'violet_dark'
            prism('Body', bat_pts(c, s), STRING_Z - 0.04, STRING_Z + 0.04, col)
            for ex in (-0.07, 0.07):
                box('Body', (c[0] + ex * s / 0.62, c[1] + 0.1 * s / 0.62, STRING_Z - 0.055), (0.07, 0.07, 0.03),
                    'amber')
            k += 1
    # The big one hanging under the bow.
    c = (0.0, 10.2)
    prism('Body', bat_pts(c, 1.05), STRING_Z - 0.045, STRING_Z + 0.045, 'plum_deep')
    for ex in (-0.11, 0.11):
        box('Body', (ex, c[1] + 0.15, STRING_Z - 0.06), (0.11, 0.11, 0.03), 'amber')
    proxy_box((-5.0, 9.25, -0.3), (5.0, 10.95, -0.1))
    return done('paper bats (plum and violet, amber eyes) on a string in two swags from the arch\'s corners '
                'to a bow at its top, a big bat under the bow')


def fairy_lights():
    cosmetic('Cosmetic_FairyLights', 'Lobby')
    for x, y in HOOKS:
        hook(x, y, col='iron')
    n = 0
    for a, b in zip(HOOKS, HOOKS[1:]):
        p0, p1 = Vector((a[0], a[1], STRING_Z)), Vector((b[0], b[1], STRING_Z))
        string('Body', p0, p1, 0.35, 0.04, 'wire')
        for t in (0.22, 0.5, 0.78):
            p = swag(p0, p1, 0.35, t)
            cyl('Body', (p.x, p.y - 0.26, p.z), 0.095, 0.24, 'wire', n=6)
            n += 1
            sphere(f'Glow_Warm_{n}', (p.x, p.y - 0.44, p.z), (0.15, 0.22, 0.15), 'bulb', n=7, rings=4)
    proxy_box((-5.0, 9.0, -0.32), (5.0, 10.95, -0.06))
    return done(f'a dark green wire in four swags across the arch, {n} warm bulbs on little sockets')


BUILD = {'Cosmetic_PumpkinSign': pumpkin_sign, 'Cosmetic_IcicleSign': icicle_sign,
         'Cosmetic_LanternSign': lantern_sign, 'Cosmetic_Family1': family1, 'Cosmetic_Family2': family2,
         'Cosmetic_BatBunting': bat_bunting, 'Cosmetic_FairyLights': fairy_lights}


# --- The review: each cosmetic on both kits' sign or arch, Workbench, small ------------------------

def _flat(name, rgb):
    mat = bpy.data.materials.get(name)
    if mat:
        return mat
    img = bpy.data.images.new(name, 2, 2, alpha=False)
    img.pixels.foreach_set([c for _ in range(4) for c in (*[v / 255 for v in rgb], 1.0)])
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    tex = mat.node_tree.nodes.new('ShaderNodeTexImage')
    tex.image = img
    mat.node_tree.links.new(tex.outputs['Color'], mat.node_tree.nodes['Principled BSDF'].inputs['Base Color'])
    return mat


def _import(path, offset_rb, keep=None):
    before = set(bpy.data.objects)
    bpy.context.scene.unit_settings.scale_length = .01
    bpy.ops.import_scene.fbx(filepath=str(path))
    new = [o for o in bpy.data.objects if o not in before]
    for ob in new:
        base = ob.name.split('.')[0]
        if ob.type != 'MESH' or base in ('Root', 'LOD_Proxy') or (keep and base not in keep):
            bpy.data.objects.remove(ob)
            continue
        ob.location += K.rb2bl(offset_rb)
    return new


def _block(name, lo, hi, rgb):
    lo, hi = Vector(lo), Vector(hi)
    me = bpy.data.meshes.new(name)
    c, s = (lo + hi) / 2, hi - lo
    verts = [K.rb2bl(c + Vector(((i >> 2 & 1) - .5) * s.x * Vector((1, 0, 0)) + ((i >> 1 & 1) - .5) * s.y
                                 * Vector((0, 1, 0)) + ((i & 1) - .5) * s.z * Vector((0, 0, 1)))) for i in range(8)]
    me.from_pydata(verts, [], K.BOX_FACES)
    me.materials.append(_flat(f'flat_{rgb}', rgb))
    uv = me.uv_layers.new()
    for d in uv.data:
        d.uv = (0.5, 0.5)
    ob = bpy.data.objects.new(name, me)
    bpy.context.scene.collection.objects.link(ob)
    return ob


def _person(base, z):
    """A 5-stud person (the standard avatar's proportions: legs 2, torso 2, head 1)."""
    skin, shirt, legs = (250, 200, 160), (70, 130, 200), (60, 60, 80)
    x = base.x

    def blk(name, lo, hi, rgb):
        return _block(name, Vector(lo) + Vector((0, base.y, 0)), Vector(hi) + Vector((0, base.y, 0)), rgb)
    blk('person', (x - 0.95, 0, z - 0.45), (x - 0.05, 2.0, z + 0.45), legs)
    blk('person', (x + 0.05, 0, z - 0.45), (x + 0.95, 2.0, z + 0.45), legs)
    blk('person', (x - 1.0, 2.0, z - 0.5), (x + 1.0, 4.0, z + 0.5), shirt)
    blk('person', (x - 1.9, 2.0, z - 0.45), (x - 1.02, 4.0, z + 0.45), skin)
    blk('person', (x + 1.02, 2.0, z - 0.45), (x + 1.9, 4.0, z + 0.45), skin)
    blk('person', (x - 0.6, 4.0, z - 0.6), (x + 0.6, 5.0, z + 0.6), skin)


def _render(path, direction, res, target=None, scale=1.04):
    sc = bpy.context.scene
    sc.render.engine = 'BLENDER_WORKBENCH'
    sc.display.shading.light = 'STUDIO'
    sc.display.shading.color_type = 'TEXTURE'
    sc.display.shading.show_shadows = False
    sc.display.shading.show_cavity = True
    sc.render.resolution_x, sc.render.resolution_y = res
    sc.world = sc.world or bpy.data.worlds.new('World')
    sc.world.color = (0.16, 0.17, 0.22)
    pts = [ob.matrix_world @ Vector(c) for ob in sc.objects if ob.type == 'MESH' for c in ob.bound_box]
    lo, hi = K._bounds(pts) if target is None else (K.rb2bl(target[0]), K.rb2bl(target[1]))
    lo, hi = Vector(map(min, lo, hi)), Vector(map(max, lo, hi))
    centre = (lo + hi) / 2
    pts = [Vector((x, y, z)) for x in (lo.x, hi.x) for y in (lo.y, hi.y) for z in (lo.z, hi.z)]
    cam = sc.camera
    if cam is None:
        cam = bpy.data.objects.new('Review', bpy.data.cameras.new('Review'))
        sc.collection.objects.link(cam)
        sc.camera = cam
    cam.data.type = 'ORTHO'
    cam.data.clip_end = 3000
    d = Vector(direction).normalized()
    cam.location = centre + d * 600
    cam.rotation_euler = (-d).to_track_quat('-Z', 'Y').to_euler()
    rot = cam.rotation_euler.to_matrix()
    right, up = rot @ Vector((1, 0, 0)), rot @ Vector((0, 1, 0))
    xs = [(p - centre).dot(right) for p in pts]
    ys = [(p - centre).dot(up) for p in pts]
    aspect = res[0] / res[1]
    cam.data.ortho_scale = max(max(xs) - min(xs), (max(ys) - min(ys)) * aspect) * scale
    cam.location += right * (max(xs) + min(xs)) / 2 + up * (max(ys) + min(ys)) / 2
    path.parent.mkdir(parents=True, exist_ok=True)
    sc.render.filepath = str(path)
    bpy.ops.render.render(write_still=True)
    print(f'REVIEW {path}', flush=True)


def review(out):
    """Each sign cosmetic on the Manor's sign (top row) and the Lodge's (middle row); each lobby
    cosmetic on both arches with a 5-stud person under it and a red bar at 8 studs (bottom row)."""
    for ob in list(bpy.data.objects):
        bpy.data.objects.remove(ob)
    fbx = out / 'fbx'
    for row, kit in enumerate(KITS):
        for col, name in enumerate(SIGNS):
            base = Vector((col * 24, 0, row * 30 * 0)) + Vector((0, -row * 19, 0))
            _import(K.ROOT / 'blender' / 'hotel' / kit / 'fbx' / 'HotelSign.fbx', base)
            _import(fbx / f'{name}.fbx', base + SIGN_ORIGIN)
    for col, (kit, name) in enumerate([(k, n) for n in LOBBIES for k in KITS]):
        base = Vector((col * 24 + 12, -2 * 19 + 2, 0))
        _import(K.ROOT / 'blender' / 'hotel' / kit / 'fbx' / 'Lobby.fbx', base, keep={'ArchLeft', 'ArchRight', 'ArchTop'})
        _import(fbx / f'{name}.fbx', base)
        _block('floor', base + Vector((-7, -0.2, -3)), base + Vector((7, 0, 2)), (90, 92, 104))
        _block('bar8', base + Vector((-6.5, 7.95, -0.5)), base + Vector((-5.6, 8.05, -0.4)), (230, 50, 50))
        _block('bar8', base + Vector((5.6, 7.95, -0.5)), base + Vector((6.5, 8.05, -0.4)), (230, 50, 50))
        _person(base, -1.2)
    _render(out / 'review' / 'angle.png', (0.45, -1.0, 0.35), (1024, 720))
    _render(out / 'review' / 'front.png', (0, -1.0, 0), (1024, 720))
    # Close-up: the right end of the Lodge's board with the lantern, and the icicle sign's end.
    lo = Vector((2 * 24 + 5, -19 + 3, -3))
    _render(out / 'review' / 'closeup.png', (-0.6, -1.0, 0.3), (768, 480),
            target=(lo, lo + Vector((7, 10, 4))), scale=1.0)
    lo = Vector((1 * 24 + 5, -19 + 3, -3))
    _render(out / 'review' / 'closeup_icicle.png', (-0.6, -1.0, 0.3), (768, 480),
            target=(lo, lo + Vector((7, 10, 4))), scale=1.0)
    # The lobby cosmetics on both arches, closer: the Lodge's arch and the Manor's, each.
    for k, name in enumerate(LOBBIES):
        lo = Vector((k * 48 + 12 - 9, -36.5, -3))
        _render(out / 'review' / f'lobby_{name.split("_")[1]}.png', (0.3, -1.0, 0.2), (1024, 340),
                target=(lo, lo + Vector((42, 13, 2))), scale=1.0)


# --- The set ------------------------------------------------------------------------------------

def main():
    load_kits()
    K.use_palette(PALETTE)
    K.start_set(SET)
    refused = []
    for name, fn in BUILD.items():
        if not K.want(name):
            continue
        try:
            fn()
        except K.Refused as e:
            print(str(e), flush=True)
            refused.append(name)
    if refused:
        raise SystemExit(f'REFUSED: {refused}')
    rows = [(SIGNS, 22, 1.0), (LOBBIES, 12, 1.0)]
    report = K.end_set('Hotel cosmetics (Sign and Lobby slots), first draft', rows, sheet=False)
    # The slot, origin and measured clearances into the manifest and the validation.
    out = K.ROOT / 'blender' / SET
    pieces = {p.name: p for p, _, _ in K.BUILT}
    man = json.loads((out / 'manifest.json').read_text())
    val = json.loads((out / 'validation.json').read_text())
    for name, p in pieces.items():
        rec = man['pieces'][name]
        rec['slot'] = p.slot
        rec['origin'] = ('the centre of the hotel sign\'s Board front face, front -Z' if p.slot == 'Sign' else
                         'the lobby\'s Entrance attachment (the threshold, on the floor), front -Z')
        rec['collision_note'] = ('nothing collides: CanCollide, CanQuery and CanTouch off on every part '
                                 '(MODELS.md, "Cosmetics"); Box on every mesh')
        rec['clearances'] = p.measured.get('fbx', p.measured.get('built'))
        val['pieces'][name]['slot'] = p.slot
        val['pieces'][name]['clearances'] = p.measured.get('fbx')
        val['pieces'][name]['checks'].append(
            'Board face clear (no triangle in x -8..8, y -3..3, z < 0.6, +0.015) and no triangle touching either '
            'kit\'s HotelSign (posts, Board, Crest, glow)' if p.slot == 'Sign' else
            f'lowest point >= {LOBBY_CLEAR}, |x| <= {ARCH_X} (inside the arch), z <= 0 (in front of it), no '
            'triangle touching either kit\'s Lobby (arch, lantern, rug, desk...)')
    val['not_validated'] = [
        'anything in Studio: the import, Roblox\'s side of the axis conversion (import_fixup.luau checks every '
        'part against the manifest first), the atlas upload, how it looks lit',
        'the code placing it: HotelKit.cosmetic clones the template and PivotTo()s it onto the Board\'s front '
        'face (PlotService.drawCosmetics) or the Entrance; not run with these models',
        'the kit-clearance checks use the two kits\' FBX as built today; a change to a kit\'s sign or arch '
        'needs this set rebuilt (it re-checks on every build)',
        'clearances to the kits are nearest-vertex distances; intersections are exact (BVH triangle overlap)',
        'LOD_Proxy is not checked against the kits (hidden); it is held to the Board-face and arch rules',
        'the attachments: a cosmetic has none (its origin is its pivot, set by import_fixup.luau)',
    ]
    (out / 'manifest.json').write_text(json.dumps(man, indent=1))
    (out / 'validation.json').write_text(json.dumps(val, indent=1))
    if not K.NOPREVIEW and K.ONLY is None:
        review(out)
    print('DONE', flush=True)


main()
