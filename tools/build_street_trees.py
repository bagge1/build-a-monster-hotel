"""The forest round Creepy Lane, first drafts: five trees (MODELS.md, "Street
scenery: trees"; GDD §5.4, his idea 2026-10-19: "so it does not look like a
big lawn").

Built on monster_kit like the street NPCs (begin, shapes, finish), kind 'tree':
standing on z = 0, the trunk's foot centred on the origin, no front but the
hollow's eyes (Blender -Y), a column Root the code uses as the tree's only
collider. Low-poly for phones: hundreds stand round the street, so each is at
most 800 triangles beside a 100-triangle proxy, one flat colour a part.

- Haunted Manor: `Tree_Crooked` (a leaning zigzag trunk, claw branches),
  `Tree_Bare` (a tall dead tree forking into bare limbs), `Tree_Hollow` (short,
  fat and gnarled, a dark hollow with a pair of glowing eyes; rare).
- Both: `Tree_Fir` (dark, five drooping tiers).
- Frostfang Lodge: `Tree_SnowFir` (frostier tiers under caps of snow).
- Bayou Spa: `Tree_Cypress` (a fluted trunk flaring into a low foot with knees round it, level limbs under broad
  clumps, a flat-topped crown, Spanish moss in tasselled curtains). `-- grey variants` builds the three cypress
  silhouettes (`Tree_Cypress`, `_CypressLean`, `_CypressTwin`) into review/silhouettes.png; only `Tree_Cypress`
  is built otherwise.

Run headless only:
    blender -b --python-exit-code 1 -P tools/build_street_trees.py [-- norender] [-- grey [variants]] [-- only Tree_Fir]
`-- grey` builds the silhouettes (every part one grey) and writes the sheet as
review/silhouettes.png; the FBX it writes are overwritten by the next full build.
"""
import math
import shutil
import sys

import bmesh
import bpy
from mathutils import Matrix

from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import monster_kit as k  # noqa: E402
from monster_kit import ball, lathe, prism, rings, tube  # noqa: E402

SET = 'street/trees'
ORDER = ['Tree_Crooked', 'Tree_Bare', 'Tree_Hollow', 'Tree_Fir', 'Tree_SnowFir']
ONLY = next((a.split(',') for a in k.ARGS[k.ARGS.index('only') + 1:k.ARGS.index('only') + 2]), None) \
    if 'only' in k.ARGS else None
GREY = 'grey' in k.ARGS

BARK = (96, 76, 88)
DEAD = (156, 150, 146)
FIRBARK = BARK
NEEDLES = (50, 92, 84)
FROST = (62, 104, 98)
SNOW = (226, 236, 246)

k.scenery('Tree_Crooked', 29.0, 3.0)
k.scenery('Tree_Bare', 35.0, 3.0)
k.scenery('Tree_Hollow', 22.0, 5.0, need=('Body', 'Dark', 'Glow_Eyes_1', 'Glow_Eyes_2'))
k.scenery('Tree_Fir', 36.0, 10.0, need=('Body', 'Trim'), proxy_colour=NEEDLES)
k.scenery('Tree_SnowFir', 33.0, 9.5, need=('Body', 'Trim', 'Light'), proxy_colour=(150, 172, 176))


def begin(sid, colours):
    if GREY:
        colours = {p: (150, 150, 150) for p in colours}
    k.begin(sid, SET, colours)


def flare(rt):
    """The trunk's foot: a little wider than the trunk `rt` at the ground, rising steeply into it."""
    lathe('Body', [(0, 1.18 * rt), (0.6, 1.04 * rt), (1.6, 0.95 * rt), (2.2, 0)], n=8)


def carve(ob, at, r, n=12, k=6):
    """Cut an ellipsoid of radii `r` at `at` out of the closed mesh `ob`: a hollow
    that is a hole, not a disc on the bark. Blender's boolean on two closed
    meshes; the cutter shares no face with the trunk (modelling skill)."""
    bm = bmesh.new()
    bmesh.ops.create_uvsphere(bm, u_segments=n, v_segments=k, radius=1.0)
    bm.transform(Matrix.Translation(at) @ Matrix.Diagonal((*r, 1)))
    me = bpy.data.meshes.new('Cutter')
    bm.to_mesh(me)
    bm.free()
    cutter = bpy.data.objects.new('Cutter', me)
    bpy.context.scene.collection.objects.link(cutter)
    mod = ob.modifiers.new('Hollow', 'BOOLEAN')
    mod.operation = 'DIFFERENCE'
    mod.object = cutter
    solvers = [e.identifier for e in mod.bl_rna.properties['solver'].enum_items]
    mod.solver = 'MANIFOLD' if 'MANIFOLD' in solvers else 'EXACT'
    before = len(ob.data.polygons)
    deps = bpy.context.evaluated_depsgraph_get()
    new = bpy.data.meshes.new_from_object(ob.evaluated_get(deps))
    ob.modifiers.remove(mod)
    old = ob.data
    ob.data = new
    bpy.data.meshes.remove(old)
    bpy.data.objects.remove(cutter)
    while len(new.materials) > 1:
        new.materials.pop()
    for poly in new.polygons:
        poly.material_index = 0
    assert len(new.polygons) > before, 'carve: the boolean cut nothing (it fails silently)'


def twigs(base, spread, r=0.24):
    """A fork of two or three twigs at a branch's tip, so a bare crown reads busy, not single-line."""
    bx, by, bz = base
    for dx, dy, dz in spread:
        tube('Body', [(bx, by, bz), (bx + dx * 0.55, by + dy * 0.55, bz + dz * 0.6), (bx + dx, by + dy, bz + dz)],
             [r, r * 0.72, r * 0.5], n=5)


def tree_crooked():
    begin('Tree_Crooked', {'Body': BARK})
    flare(1.6)
    T = [(0, 0, 1.7), (1.4, 0, 5), (-1.8, 0.6, 10), (1.4, -0.4, 15), (4.0, 0, 19.5), (2.4, 0.8, 24),
         (5.0, 0.3, 28.2)]
    tube('Body', T, [1.6, 1.4, 1.25, 1.1, 0.9, 0.65, 0.3], n=8)
    # Branches leaving the trunk's bends, reaching out and curling up like claws, each forking into twigs.
    tube('Body', [T[2], (-5.2, 0.8, 11.5), (-8.2, -0.5, 14.5), (-9.2, -1.2, 18)], [0.85, 0.6, 0.4, 0.2], n=6)
    twigs((-9.2, -1.2, 18), [(-1.6, -0.4, 2.4), (0.8, -1.0, 2.8)])
    tube('Body', [T[3], (5.2, -1.2, 16), (8.2, -0.6, 18.2), (9.2, 0.6, 21.2)], [0.75, 0.55, 0.35, 0.17], n=6)
    twigs((9.2, 0.6, 21.2), [(1.4, 0.6, 2.2), (-0.6, 1.2, 2.6)])
    tube('Body', [T[4], (0.4, 1.2, 22), (-2.4, 0.6, 25), (-3.0, -0.6, 27.2)], [0.6, 0.42, 0.28, 0.14], n=5)
    twigs((-3.0, -0.6, 27.2), [(-1.2, -0.6, 1.6), (0.6, -0.4, 1.8)], r=0.2)
    tube('Body', [T[5], (5.6, 1.6, 25.6), (7.0, 1.2, 27.8)], [0.45, 0.3, 0.15], n=5)
    return k.finish('A crooked bare tree: a thick trunk zigzagging up and leaning a little, four branches '
                    'reaching out and curling up like claws, each forking into twigs. Haunted Manor.')


def tree_bare():
    begin('Tree_Bare', {'Body': DEAD})
    flare(1.65)
    tube('Body', [(0, 0, 1.8), (0.3, 0.1, 7), (-0.3, 0, 13), (0, 0, 16)], [1.65, 1.45, 1.3, 1.15], n=8)
    # Two main limbs from the fork, a third lower down, each forking again.
    tube('Body', [(0, 0, 16), (-2.8, 0.5, 22), (-4.4, 0, 28), (-5, -0.5, 32.5)], [1.0, 0.72, 0.45, 0.2], n=6)
    tube('Body', [(0, 0, 16), (2.8, -0.3, 21), (5, 0.5, 26), (6.6, 0.8, 30)], [0.95, 0.68, 0.42, 0.2], n=6)
    tube('Body', [(-0.3, 0, 13), (1.2, 2.2, 18), (1.8, 3.8, 24), (1.5, 4.2, 27)], [0.7, 0.52, 0.4, 0.34], n=6)
    tube('Body', [(0, 0, 15.5), (0.2, 0.1, 18.5), (0.4, 0.1, 20.2)], [1.0, 0.92, 0.86], n=6)   # the snapped top
    tube('Body', [(-2.8, 0.5, 22), (-6.4, 1, 25), (-8, 1.5, 27.4)], [0.45, 0.28, 0.12], n=5)
    tube('Body', [(5, 0.5, 26), (3.8, 2.5, 31), (3.2, 3, 34.6)], [0.4, 0.24, 0.1], n=5)
    twigs((-5, -0.5, 32.5), [(-1.2, 0.4, 2.0), (0.9, -0.6, 2.2)], r=0.22)
    twigs((6.6, 0.8, 30), [(1.6, 0.2, 1.8), (0.4, 1.2, 2.6)], r=0.22)
    # A limb snapped off short: a dead tree's tell.
    tube('Body', [(0.2, 0.05, 9), (-2.2, -0.6, 10.2), (-3.2, -0.9, 10.4)], [0.55, 0.42, 0.36], n=5)
    return k.finish('A tall dead tree, silvery grey: a thick straight trunk forking at 16 studs into bare limbs '
                    'that reach up and out and fork again into twigs, one limb snapped short and another broken off. '
                    'Haunted Manor.')


def tree_hollow():
    begin('Tree_Hollow', {'Body': (104, 82, 88), 'Dark': (22, 14, 26), 'Glow_Eyes_1': (255, 214, 92),
                          'Glow_Eyes_2': (255, 214, 92)})
    # Gnarled, but plain on the front (theta -90) where the hollow is.
    gnarl = lambda t: 1 + 0.18 * math.sin(3 * t + math.pi / 2) + 0.08 * math.sin(7 * t + 3.5 * math.pi)  # noqa: E731
    trunk = rings('Body', [(0, 0, 0, 3.3), (0, 0, 0.7, 3.0), (0, 0, 2.2, 2.7), (0.2, 0, 8, 2.4), (0.3, 0, 11, 2.1),
                   (0.2, 0, 13.5, 1.5), (0.1, 0.4, 15.6, 0.95), (0, 0.8, 17, 0)], n=10, radial=gnarl)
    # A hollow carved into the front, dark inside, and in it a pair of eyes peeping out; a burl on one side.
    # At a person's eye height once planted, so the eyes meet a passer-by's.
    zc, rf = 4.9, 2.45                     # the hollow's centre height; the trunk's front face there
    carve(trunk, (0, -rf, zc), (1.4, 1.0, 1.8))
    ball('Dark', (0, -rf + 1.15, zc), (1.25, 0.55, 1.65), n=8, k=4)
    for i, s in ((1, 1), (2, -1)):
        ball(f'Glow_Eyes_{i}', (s * 0.48, -rf + 0.62, zc + 0.25), (0.28, 0.12, 0.38), n=8, k=4)
    ball('Body', (2.2, -0.9, 9.0), (1.1, 1.0, 1.4), n=8, k=4)   # a burl, seen from the street
    tube('Body', [(0.2, 0, 11.5), (-3.4, 0.5, 14.5), (-5.6, 0, 18.2), (-6.2, -0.8, 21.4)], [1.25, 0.85, 0.45, 0.14],
         n=5)
    tube('Body', [(0.3, 0, 10.5), (3.8, -0.5, 13), (6, 0, 16.6), (7, 0.5, 19)], [1.15, 0.8, 0.42, 0.14], n=5)
    tube('Body', [(0.1, 0.6, 15.2), (0.6, 1.6, 18), (-0.5, 2.2, 20.6), (0.2, 1.8, 21.8)], [0.9, 0.6, 0.34, 0.12],
         n=5)
    for base, spread in (((-5.6, 0, 18.2), (-2.2, 0.6, 1.4)), ((6, 0, 16.6), (2.0, -0.6, 1.8)),
                         ((-0.5, 2.2, 20.6), (-1.6, 0.8, 1.2))):
        tube('Body', [base, tuple(b + s * 0.55 for b, s in zip(base, spread)), tuple(b + s for b, s in zip(base, spread))],
             [0.32, 0.2, 0.09], n=5)
    return k.finish('A short, fat, gnarled tree with a dark hollow in its front and a pair of warm glowing eyes '
                    'peeping out of it (cozy creepy, never scary); three stubby branches. Haunted Manor, rare.')


def fir_tiers(part, tiers, wave=0.5):
    """Drooping tiers of needles: each a skirt from an inner underside out to a
    scalloped rim and up to its tip. `tiers` [(z_rim, radius, height)]."""
    for i, (z0, R, H) in enumerate(tiers):
        lobes = 5 + i % 2
        rim = lambda t, lobes=lobes, R=R: wave * math.sin(lobes * t + R)  # noqa: E731
        rings(part, [(0, 0, z0 + 0.9, R * 0.45), (0, 0, z0, R), (0, 0, z0 + H, 0)], n=10, wave={1: rim})


def fir_trunk(top):
    lathe('Body', [(0, 1.7), (0.6, 1.4), (2.5, 1.2), (9, 0.95), (top, 0.3), (top + 0.6, 0)], n=6)


FIR = [(2.5, 8.2, 11), (9.5, 7.0, 9.5), (15.5, 5.7, 8.5), (21.5, 4.3, 8), (27, 2.9, 9)]
SNOWFIR = [(2.5, 7.6, 10), (9, 6.3, 9), (15, 5.0, 8), (20.5, 3.8, 7.5), (25.5, 2.5, 7.5)]


def tree_fir():
    begin('Tree_Fir', {'Body': FIRBARK, 'Trim': NEEDLES})
    fir_trunk(30)
    fir_tiers('Trim', FIR)
    return k.finish('A dark fir: a trunk under five drooping tiers of needles with scalloped rims, narrowing to '
                    'a point. Haunted Manor and Frostfang Lodge.')


def tree_snowfir():
    begin('Tree_SnowFir', {'Body': FIRBARK, 'Trim': FROST, 'Light': SNOW})
    fir_trunk(27)
    fir_tiers('Trim', SNOWFIR, wave=0.4)
    # Snow on each tier's upper half: a cone a little proud of the needles, its edge dripping.
    for i, (z0, R, H) in enumerate(SNOWFIR):
        zs = z0 + 0.2 * H
        rr = R * (1 - 0.2) * 1.02
        drip = lambda t, i=i: 0.3 * math.sin(6 * t + i)  # noqa: E731
        rings('Light', [(0, 0, zs, rr), (0, 0, z0 + H + 0.2, 0)], n=10, wave={0: drip})
    return k.finish('A snowy fir: frosty tiers of needles, each under a cap of snow with a dripping edge. '
                    'Frostfang Lodge.')


CYBARK = (104, 90, 78)
CROWN = (74, 108, 66)
MOSS = (154, 166, 132)


def buttress(rt, flutes=5):
    """A swamp tree's bell-bottomed foot (the silhouette variants'): fluted ridges spreading out at the waterline."""
    ridge = lambda t: 1 + 0.24 * math.cos(flutes * t)  # noqa: E731
    rings('Body', [(0, 0, 0, 2.5 * rt), (0, 0, 0.7, 2.0 * rt), (0, 0, 2.0, 1.45 * rt), (0, 0, 3.8, 1.1 * rt),
                   (0, 0, 5.2, 0)], n=10, radial=ridge)


def cypress_trunk(profile, flutes=5):
    """The whole trunk as one fluted shape, from a wide flare at the waterline up to its tip, so the foot is the
    trunk spreading into roots, never a trunk standing in a cup; the flutes uneven, not a star. `profile`
    [(cx, cy, z, r)]. (A 3-lobe term keeps the foot's centroid on the axis with 2 x `flutes` sides.)"""
    ridge = lambda t: 1 + 0.16 * math.cos(flutes * t) + 0.07 * math.sin(3 * t + 1)  # noqa: E731
    rings('Body', profile, n=2 * flutes, radial=ridge)


def knees(turn, heights, r=5.0):
    """Cypress knees: rounded knobs poking out of the ground round the foot, evenly round it from angle `turn`
    (so the foot's centroid stays on the origin), one per height."""
    for i, h in enumerate(heights):
        a = math.radians(turn) + 2 * math.pi * i / len(heights)
        x, y = r * math.cos(a), r * math.sin(a)
        rings('Body', [(x, y, 0, 0.55), (x, y, 0.65 * h, 0.42), (x, y, h, 0.16)], n=5)


def pad(at, r, phase=0.0):
    """A clump of needles: the cypress's crown, broad and level with a lumpy outline, never a coin."""
    lumpy = lambda t: 1 + 0.14 * math.sin(3 * t + phase) + 0.06 * math.sin(5 * t + 2 * phase)  # noqa: E731
    ball('Dark', at, (r, 0.85 * r, 0.4 * r), n=8, k=3, radial=lumpy)


def moss(at, length, w=1.1, phase=0.0, turn=0.0):
    """Spanish moss hanging from a limb or out of a clump's underside: a thin flat curtain, narrow where it hangs
    from, widening, and ending in three ragged tassels of unequal length (never one point: a point is an icicle).
    `turn` degrees about the vertical, so the curtains of one tree do not all face one way."""
    x, y, z = at
    L = length
    j = 0.08 * L * math.sin(phase)      # each curtain's tassels a little different
    outline = [(-0.3 * w, 0), (0.3 * w, 0), (0.85 * w, -0.45 * L), (0.6 * w, -0.78 * L - j),
               (0.35 * w, -0.7 * L), (0.05 * w, -L + j), (-0.25 * w, -0.8 * L), (-0.55 * w, -0.93 * L - j),
               (-0.8 * w, -0.5 * L)]
    prism('Trim', [(x + ox, z + oz) for ox, oz in outline], y - 0.12, 0.24, rot=(0, 0, turn), pivot=(x, y, z))


def limb(base, mid, tip, r, n=4):
    """A near-level limb reaching out to carry a clump, thinning to the tip."""
    tube('Body', [base, mid, tip], [r, 0.7 * r, 0.45 * r], n=n)


def tree_cypress():
    """Bayou Spa's swamp cypress: one fluted trunk flaring into a tall uneven foot, rounded knees close round it, a
    dense flat-topped crown of overlapping clumps over a lower tier of two on short limbs, Spanish moss in long
    ragged curtains hanging from the limbs and out of the clumps' undersides."""
    begin('Tree_Cypress', {'Body': CYBARK, 'Dark': CROWN, 'Trim': MOSS})
    cypress_trunk([(0, 0, 0, 3.4), (0, 0, 0.8, 2.8), (0, 0, 2.2, 2.1), (0, 0, 4.2, 1.6), (0.05, 0.05, 6.5, 1.35),
                   (0.2, 0.1, 15, 1.1), (0.25, 0.15, 27.5, 0.45), (0.3, 0.2, 29, 0)])
    knees(30, (1.6, 2.2, 1.3, 1.9), r=4.5)
    # The lower tier: two short limbs, each under a broad clump reaching in to the trunk, so no stick shows bare.
    limb((0.2, 0, 16), (2.4, 0.5, 17), (4.4, 1.0, 18), 0.9, n=5)
    limb((0, 0, 18.5), (-2.2, -0.8, 19.4), (-4.2, -1.5, 20), 0.85, n=5)
    # The crown: three clumps overlapping round the trunk's top into one flat-topped mass.
    limb((0.15, 0.1, 23.5), (-1.2, 0.6, 25.4), (-2.4, 1.2, 26.6), 0.7)
    limb((0.2, 0.1, 24.5), (1.4, -0.5, 26.2), (2.6, -1.0, 27.0), 0.65)
    for i, (at, r) in enumerate((((4.6, 1.0, 18.6), 4.6), ((-4.4, -1.6, 20.4), 4.4), ((-2.4, 1.2, 27.1), 5.2),
                                 ((2.6, -1.0, 27.5), 5.2), ((0.2, 2.6, 28.1), 4.4))):
        pad(at, r, phase=1.3 * i)
    for i, (x, y, z, length) in enumerate(((2.4, 0.5, 16.8, 7.0), (5.8, 2.6, 17.6, 6.0), (-2.2, -0.8, 19.2, 7.5),
                                           (-5.6, -0.2, 19.6, 6.0), (3.6, -2.6, 26.2, 8.0))):
        moss((x, y, z), length, w=0.75, phase=i, turn=(37 * i) % 120 - 60)
    return k.finish('A swamp cypress: one fluted trunk flaring into a tall uneven foot with rounded knees close round '
                    'it, a dense flat-topped crown of overlapping clumps of needles over a lower tier of two, and pale '
                    'Spanish moss hanging in long ragged curtains from the limbs and the clumps. Bayou Spa.')


def tree_cypress_lean():
    """Silhouette variant B: the trunk leaning out over the water, one broad umbrella crown, heavy moss."""
    begin('Tree_CypressLean', {'Body': CYBARK, 'Dark': CROWN, 'Trim': MOSS})
    buttress(1.3)
    tube('Body', [(0, 0, 3.6), (1.6, 0, 12), (4.2, 0.2, 20), (5.6, 0.2, 26)], [1.4, 1.05, 0.75, 0.4], n=7)
    knees(150, (1.6, 2.0, 1.3))
    for at, r in (((5.6, 0.2, 27.2), 6.2), ((0.6, 1.6, 25.0), 4.0), ((9.4, -1.2, 25.2), 3.8)):
        pad(at, r)
    limb((4.2, 0.2, 20), (2.0, 1.2, 22.6), (0.8, 1.6, 24.4), 0.5)
    limb((4.6, 0.2, 21.5), (7.6, -0.8, 23.2), (9.2, -1.2, 24.6), 0.45)
    for x, y, z, length in ((1.0, 2.6, 24.4, 7.0), (3.2, -2.6, 25.8, 8.0), (8.0, 2.6, 25.6, 7.5),
                            (10.6, -2.2, 24.6, 6.0), (6.0, 4.6, 26.0, 6.5), (-0.8, -0.6, 24.2, 6.0)):
        moss((x, y, z), length)
    return k.finish('Silhouette B: a cypress leaning out, one broad umbrella crown, heavy moss.')


def tree_cypress_twin():
    """Silhouette variant C: two trunks rising from one fluted foot, each with its own stack of pads."""
    begin('Tree_CypressTwin', {'Body': CYBARK, 'Dark': CROWN, 'Trim': MOSS})
    buttress(1.5, flutes=6)
    for s, top in ((1, 31.0), (-1, 26.0)):
        tube('Body', [(0, 0, 3.6), (s * 1.6, 0.2, 11), (s * 2.6, 0.3, 20), (s * 3.0, 0.3, top)],
             [1.2, 0.9, 0.65, 0.3], n=6)
        for z, dx, r in ((top - 9, 4.2, 3.4), (top - 4, -3.0, 3.0), (top + 0.6, 0.4, 2.4)):
            pad((s * (3.0 + dx), 0.6 * dx, z), r)
            moss((s * (3.0 + dx * 0.9), 0.5 * dx, z - 0.4), 4.5)
    knees(80, (1.8, 1.5, 1.3), r=5.6)
    return k.finish('Silhouette C: twin cypress trunks from one foot, pads in tiers, moss.')


k.scenery('Tree_Cypress', 32.0, 5.0, need=('Body', 'Dark', 'Trim'), proxy_colour=CROWN)
VARIANTS = 'variants' in k.ARGS
if VARIANTS:
    k.scenery('Tree_CypressLean', 30.0, 5.0, need=('Body', 'Dark', 'Trim'), proxy_colour=CROWN)
    k.scenery('Tree_CypressTwin', 32.0, 5.5, need=('Body', 'Dark', 'Trim'), proxy_colour=CROWN)
    ORDER = ['Tree_Cypress', 'Tree_CypressLean', 'Tree_CypressTwin']
else:
    ORDER.append('Tree_Cypress')

BUILDERS = {'Tree_Crooked': tree_crooked, 'Tree_Bare': tree_bare, 'Tree_Hollow': tree_hollow,
            'Tree_Fir': tree_fir, 'Tree_SnowFir': tree_snowfir, 'Tree_Cypress': tree_cypress,
            'Tree_CypressLean': tree_cypress_lean, 'Tree_CypressTwin': tree_cypress_twin}

if __name__ == '__main__':
    names = [n for n in ORDER if not ONLY or n in ONLY]
    out = k.start_set(SET)
    for n in names:
        BUILDERS[n]()
    k.finish_set(SET, place={n: (i * 18.0, 0) for i, n in enumerate(names)},
                 frame='Blender +Z up, the trunk\'s foot on the origin; no front but Tree_Hollow\'s eyes '
                       '(Blender -Y, Roblox -Z); Roblox (x, y, z) = Blender (-x, z, y)')
    if GREY and not k.NORENDER:
        shutil.move(str(out / 'review' / 'sheet.png'), str(out / 'review' / 'silhouettes.png'))
    else:
        k.validate(SET, names)
