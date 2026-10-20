"""Haunted Manor's first free-building decor set, as GREY SILHOUETTES for August to pick the look from
(skill `modelling`: he picks the shape before any detail). Each piece is built to the decor contract
(MODELS.md, "Decor": fw x fd squares of 3 studs, the body 0.4 inside, at most 7 tall, a Wall piece's
back on z = 3fd/2 - 0.4) on tools/hotel_kit.py, so the one he picks keeps its frame and its footprint.

The ids are the code's (Pieces.luau); where a piece invites a choice, two variants _A and _B:

    GrandfatherClock 1x1 Floor (A a longcase with a round hood, B a coffin case with bat wings),
    WallClock 1x1 Wall, BlackRoses 1x1 Floor (a vase of roses on a little stand), CarnivorousPlant 1x1
    Floor, GhostFern 1x1 Floor, Armchair 1x1 Floor (a wingback), VelvetSofa 2x1 Floor, Bookshelf 2x1
    Wall, SideTable 1x1 Floor (with a candle lamp), GrandPiano 2x2 Floor (A a grand, B an upright).

Not for import: nothing here is staged until he has picked.

    blender -b --python-exit-code 1 -P tools/build_decor_silhouettes_haunted_manor.py [-- nopreview]

Writes blender/hotel/haunted_manor/silhouettes/: fbx/, manifest.json, validation.json,
review/silhouettes.png (each piece on its footprint beside the 5-stud person, labelled).
"""
import math
import sys
from pathlib import Path

import bpy
from mathutils import Vector, Matrix

sys.path.insert(0, str(Path(__file__).resolve().parent))
import hotel_kit as K  # noqa: E402
from hotel_kit import finish, box, span, cyl, lathe, sphere, prism, at  # noqa: E402

SET = 'hotel/haunted_manor/silhouettes'
K.IMPORT_CHECKS = False        # drafts with _A/_B ids, not for import: Pieces.luau and z-fighting are not theirs
G, D, L = 'grey', 'stone_dark', 'stone'       # the silhouette's greys: body, shadowed detail, light detail


def decor(id_, fw, fd, layer):
    return K.decor(id_, fw, fd, layer)


# --- Clocks ------------------------------------------------------------------------------------------

def dial(c, r, depth=0.1):
    """A round clock face on a front (-Z) face at `c`, its hands."""
    x, y, z = c
    cyl('Body', (0, 0, 0), r + 0.08, depth, D, n=16, m=at((x, y, z), rx=-90))
    cyl('Body', (0, 0, 0), r, depth + 0.03, L, n=16, m=at((x, y, z), rx=-90))
    box('Body', (x, y + r * 0.3, z - depth - 0.05), (0.07, r * 0.6, 0.03), D)
    box('Body', (x + r * 0.22, y, z - depth - 0.05), (r * 0.45, 0.07, 0.03), D)


def grandfather_clock_a():
    decor('GrandfatherClock_A', 1, 1, 'Floor')
    span('Body', (-1.0, 0, -0.8), (1.0, 0.9, 0.8), D, bevel=0.08)                 # plinth
    span('Body', (-0.75, 0.9, -0.6), (0.75, 4.3, 0.6), G, bevel=0.05)             # trunk
    span('Body', (-0.4, 1.5, -0.64), (0.4, 3.9, -0.6), D)                          # pendulum window
    cyl('Body', (0, 0, 0), 0.28, 0.04, L, n=12, m=at((0, 2.0, -0.64), rx=-90))      # the bob behind it
    span('Body', (-0.9, 4.3, -0.72), (0.9, 4.5, 0.72), D, bevel=0.04)              # waist moulding
    span('Body', (-0.95, 4.5, -0.75), (0.95, 6.0, 0.75), G, bevel=0.06)           # hood
    dial((0, 5.25, -0.75), 0.6)
    top = K.round_arch_points(-1.0, 1.0, 6.0, 6.6, n=8)
    prism('Body', top, -0.75, 0.75, D, plane='xy')                                  # the round pediment
    for x, y in ((-0.85, 6.05), (0.85, 6.05)):
        sphere('Body', (x, y + 0.14, -0.55), 0.13, L, n=8, rings=4)
    sphere('Body', (0, 6.78, 0), 0.14, L, n=8, rings=4)
    finish(proxy=False, note='silhouette A: a longcase clock, a round hood with a domed pediment and finials')


def grandfather_clock_b():
    decor('GrandfatherClock_B', 1, 1, 'Floor')
    coffin = [(-0.55, 0), (0.55, 0), (0.95, 4.1), (0.72, 6.0), (-0.72, 6.0), (-0.95, 4.1)]
    prism('Body', coffin, -0.6, 0.6, G, plane='xy')
    inner = [(x * 0.55, 0.9 + y * 0.5) for x, y in coffin]                           # the pendulum window
    prism('Body', inner, -0.64, -0.6, D, plane='xy')
    cyl('Body', (0, 0, 0), 0.26, 0.04, L, n=12, m=at((0, 1.6, -0.66), rx=-90))
    dial((0, 4.95, -0.6), 0.55)
    wing = [(0.1, 6.0), (1.05, 6.05), (0.95, 6.5), (0.75, 6.35), (0.55, 6.65), (0.35, 6.45), (0.1, 6.7)]
    prism('Body', wing, -0.15, 0.15, D, plane='xy')
    prism('Body', [(-x, y) for x, y in reversed(wing)], -0.15, 0.15, D, plane='xy')
    sphere('Body', (0, 6.62, 0), (0.22, 0.2, 0.2), D, n=8, rings=4)
    finish(proxy=False, note='silhouette B: a coffin-shaped case clock with bat wings on its crown')


def wall_clock():
    decor('WallClock', 1, 1, 'Wall')
    zb = 1.1                                                                         # the wall's face
    span('Body', (-0.55, 3.3, zb - 0.4), (0.55, 5.0, zb), G, bevel=0.05)            # the pendulum box
    span('Body', (-0.32, 3.55, zb - 0.43), (0.32, 4.8, zb - 0.4), D)
    cyl('Body', (0, 0, 0), 0.18, 0.03, L, n=10, m=at((0, 3.9, zb - 0.43), rx=-90))
    cyl('Body', (0, 0, 0), 0.95, 0.35, G, n=16, m=at((0, 5.85, zb), rx=-90))       # the round case
    dial((0, 5.85, zb - 0.35), 0.75)
    lathe('Body', [(0.0, 6.75), (0.18, 6.8), (0.0, 6.98)], D, n=8, base=(0, 0, zb - 0.2))
    finish(proxy=False, note='silhouette: a round wall clock over a pendulum box')


# --- Flowers and plants --------------------------------------------------------------------------

def stand(top_y, r_top=0.8):
    """A little round pedestal stand."""
    lathe('Body', [(0.7, 0), (0.7, 0.12), (0.25, 0.3), (0.16, top_y - 0.25), (r_top, top_y - 0.12),
                   (r_top, top_y)], G, n=12)


def black_roses():
    decor('BlackRoses', 1, 1, 'Floor')
    stand(2.4)
    lathe('Body', [(0.22, 2.4), (0.45, 2.75), (0.38, 3.25), (0.2, 3.5), (0.28, 3.65)], D, n=10)   # the vase
    for k in range(7):
        a = k * math.tau / 7
        r = 0.0 if k == 0 else 0.42
        x, z = r * math.cos(a), r * math.sin(a)
        y = 4.55 if k == 0 else 4.15 + 0.12 * (k % 2)
        cyl('Body', (x * 0.3, 3.5, z * 0.3), 0.04, y - 3.5, L, n=4)
        sphere('Body', (x, y, z), (0.24, 0.2, 0.24), D, n=8, rings=4)
    for a in (0.6, 2.7, 4.6):
        sphere('Body', (0.45 * math.cos(a), 3.75, 0.45 * math.sin(a)), (0.28, 0.06, 0.14), L, n=6, rings=3,
               m=None)
    finish(proxy=False, note='silhouette: a vase of seven roses on a little pedestal stand')


def carnivorous_plant():
    decor('CarnivorousPlant', 1, 1, 'Floor')
    lathe('Body', [(0.55, 0), (0.75, 0.9), (0.85, 1.0), (0.85, 1.15), (0.72, 1.15), (0, 1.05)], D, n=12)   # the pot
    # A thick stalk curving up and forward, the trap's two jaws open toward -Z, teeth round their rims.
    pts = [(0, 1.05, 0.1), (0.05, 1.9, 0.15), (0.05, 2.6, -0.05), (0.0, 3.0, -0.35)]
    for a, b in zip(pts, pts[1:]):
        a, b = Vector(a), Vector(b)
        d = b - a
        ang = math.degrees(math.atan2(-d.z, d.y))
        cyl('Body', (0, 0, 0), 0.17, d.length + 0.05, G, n=8, m=at(a, rx=-ang))
    # The two lobes hinged at the stalk's top, gaping toward -Z (upper tilted up, lower down), each a
    # flattened half-disc with a row of long teeth along its front rim pointing at the other lobe.
    hinge = (0, 3.05, -0.1)
    for tilt, sign in ((38, -1), (-22, 1)):
        m = at(hinge, rx=tilt)
        sphere('Body', (0, 0, -0.42), (0.66, 0.11, 0.46), G, n=12, rings=4, m=m)
        for k in range(9):
            t = math.pi * (0.08 + 0.84 * k / 8)
            rim = (0.62 * math.cos(t), 0, -0.42 - 0.43 * math.sin(t))
            lathe('Body', [(0.06, 0), (0.0, sign * 0.32)], L, n=4, base=rim, m=m)
    for a in (0.4, 2.3, 4.2):            # leaves drooping over the pot's rim
        sphere('Body', (0, 0, 0.55), (0.18, 0.06, 0.55), L, n=6, rings=3, m=at((0, 1.15, 0), ry=math.degrees(a), rx=18))
    finish(proxy=False, note='silhouette: a flytrap in a pot, its open jaws toothed, toward the front')


def ghost_fern():
    decor('GhostFern', 1, 1, 'Floor')
    for k in range(3):                    # a three-legged plant stand
        a = k * math.tau / 3 + 0.5
        cyl('Body', (0.6 * math.cos(a), 0, 0.6 * math.sin(a)), 0.07, 1.7, D, n=6, r_top=0.06)
    cyl('Body', (0, 1.6, 0), 0.75, 0.12, D, n=12)
    lathe('Body', [(0.4, 1.72), (0.6, 2.5), (0.66, 2.6), (0.55, 2.6), (0, 2.5)], G, n=12)   # the pot
    for k in range(9):                    # long fronds arching out and down
        a = k * 360 / 9 + 20
        tilt = -25 if k % 2 else -10
        sphere('Body', (0, 0, 0.48), (0.16, 0.05, 0.5), L, n=6, rings=3, m=at((0, 2.75, 0), ry=a, rx=-tilt))
    for k in range(4):
        a = k * 90 + 45
        sphere('Body', (0, 0.3, 0.2), (0.1, 0.4, 0.06), L, n=6, rings=3, m=at((0, 2.7, 0), ry=a, rx=-15))
    finish(proxy=False, note='silhouette: a pale fern in a pot on a three-legged stand, fronds arching down')


# --- Furniture -------------------------------------------------------------------------------------

def armchair():
    decor('Armchair', 1, 1, 'Floor')
    for x in (-0.85, 0.85):
        for z in (-0.8, 0.8):
            span('Body', (x - 0.12, 0, z - 0.12), (x + 0.12, 0.5, z + 0.12), D)
    span('Body', (-1.05, 0.5, -1.0), (1.05, 1.4, 0.95), G, bevel=0.12)              # the seat base
    span('Body', (-0.72, 1.4, -0.98), (0.72, 1.7, 0.55), L, bevel=0.12)              # the cushion
    back = [(-1.05, 1.4), (1.05, 1.4), (1.05, 4.2)] + K.round_arch_points(-1.05, 1.05, 4.2, 5.0, n=8)[::-1][1:-1] \
        + [(-1.05, 4.2)]
    prism('Body', back, 0.55, 1.05, G, plane='xy')                                    # the tall back
    for sx in (-1, 1):
        wing = [(0.55, 1.9), (0.95, 2.2), (0.95, 4.3), (0.55, 4.6), (0.0, 4.4), (-0.3, 3.4), (-0.35, 2.3)]
        prism('Body', wing, sx * 1.05, sx * 0.8, G, plane='zy')                       # the wings
        span('Body', (sx * 1.05 if sx < 0 else 0.72, 1.4, -1.0), (-0.72 if sx < 0 else 1.05, 2.0, 0.55), G,
             bevel=0.08)                                                              # the arms
        cyl('Body', (0, 0, 0), 0.2, 1.6, D, n=10, m=at((sx * 0.88, 2.0, -1.0), rx=90))   # rolled arm ends
    finish(proxy=False, note='silhouette: a wingback armchair, its tall rounded back to +Z')


def velvet_sofa():
    decor('VelvetSofa', 2, 1, 'Floor')
    for x in (-2.3, 2.3):
        for z in (-0.8, 0.8):
            lathe('Body', [(0.14, 0), (0.1, 0.45)], D, n=6, base=(x, 0, z))
    span('Body', (-2.55, 0.45, -1.0), (2.55, 1.35, 0.95), G, bevel=0.12)
    for k in range(3):
        x0 = -2.05 + k * 1.37
        span('Body', (x0, 1.35, -0.98), (x0 + 1.33, 1.65, 0.5), L, bevel=0.12)
    camel = [(-2.55, 1.35), (2.55, 1.35), (2.55, 3.0), (1.6, 3.3), (0.0, 3.9), (-1.6, 3.3), (-2.55, 3.0)]
    prism('Body', camel, 0.5, 1.05, G, plane='xy')                                    # a camelback
    for sx in (-1, 1):
        span('Body', (min(sx * 2.6, sx * 2.08), 0.45, -1.05), (max(sx * 2.6, sx * 2.08), 2.0, 1.0), G, bevel=0.1)
        cyl('Body', (0, 0, 0), 0.3, 2.05, D, n=10, m=at((sx * 2.3, 2.0, -1.05), rx=90))
    for x in (-1.37, 0.0, 1.37):          # buttons in the back
        sphere('Body', (x, 2.7, 0.47), (0.08, 0.08, 0.04), D, n=6, rings=3)
    finish(proxy=False, note='silhouette: a camelback sofa with rolled arms and three seat cushions')


def bookshelf():
    decor('Bookshelf', 2, 1, 'Wall')
    zb, zf = 1.1, -0.25
    span('Body', (-2.5, 0, zf), (2.5, 0.35, zb), D)                                 # plinth
    span('Body', (-2.5, 0.35, zb - 0.1), (2.5, 6.6, zb), D)                          # back
    for x in (-2.5, 2.25):
        span('Body', (x, 0.35, zf), (x + 0.25, 6.6, zb - 0.1), G)                   # sides
    shelves = (0.35, 1.9, 3.4, 4.9)
    for y in shelves + (6.4,):
        span('Body', (-2.25, y, zf), (2.25, y + 0.15, zb - 0.1), G)
    for i, y in enumerate(shelves):
        x, k = -2.2, 0
        while x < 2.0:
            bw = 0.22 + 0.08 * ((k * 5 + i * 3) % 3)
            bh = 0.95 + 0.15 * ((k * 7 + i) % 3)
            if (k + i) % 9 == 4:          # a leaning book, a gap
                x += 0.3
            span('Body', (x, y + 0.15, zf + 0.15), (min(x + bw - 0.03, 2.2), y + 0.15 + bh, zb - 0.15),
                 L if (k + i) % 2 else D)
            x += bw
            k += 1
    span('Body', (-2.6, 6.55, zf - 0.15), (2.6, 6.9, zb), G, bevel=0.05)            # the cornice
    finish(proxy=False, note='silhouette: a tall bookcase of four full shelves under a cornice, against the wall')


def side_table():
    decor('SideTable', 1, 1, 'Floor')
    for k in range(3):                    # tripod feet
        a = k * math.tau / 3 + 0.3
        box('Body', (0.42, 0.09, 0), (0.85, 0.18, 0.16), D, m=at((0, 0, 0), ry=math.degrees(a)))
    lathe('Body', [(0.18, 0.2), (0.12, 0.8), (0.2, 1.4), (0.12, 2.2), (0.2, 2.45)], G, n=10)   # the pedestal
    cyl('Body', (0, 2.45, 0), 0.95, 0.15, G, n=16)                                  # the round top
    # A candle lamp: a dish, a tall candle, a glass chimney.
    cyl('Body', (0.2, 2.6, -0.1), 0.35, 0.08, D, n=12)
    cyl('Body', (0.2, 2.68, -0.1), 0.11, 0.75, L, n=8)
    lathe('Body', [(0.2, 2.75), (0.3, 3.05), (0.28, 3.5), (0.18, 3.75), (0.2, 3.85)], G, n=10)
    sphere('Body', (0.2, 3.55, -0.1), (0.06, 0.12, 0.06), L, n=6, rings=3)
    span('Body', (-0.55, 2.6, -0.35), (-0.05, 2.75, 0.35), D)                         # a book beside it
    finish(proxy=False, note='silhouette: a round pedestal side table with a candle lamp and a book')


def grand_piano_a():
    decor('GrandPiano_A', 2, 2, 'Floor')
    # A grand, its keyboard toward -Z, the straight spine on the player's left (+X), the curved bentside
    # on the right, the tail toward +Z; its lid propped open; the bench in front.
    case = [(1.5, -1.0), (1.5, 2.45), (1.2, 2.6), (0.4, 2.5), (-0.3, 1.9), (-0.8, 1.0), (-1.2, 0.2),
            (-1.5, -0.4), (-1.5, -1.0)]
    prism('Body', case, 1.5, 2.6, G, plane='xz')
    for x, z in ((-1.2, -0.6), (1.2, -0.6), (0.9, 2.1)):
        lathe('Body', [(0.2, 0), (0.14, 0.2), (0.18, 1.5)], D, n=8, base=(x, 0, z))
    span('Body', (-1.55, 1.9, -1.7), (1.55, 2.25, -1.0), D)                          # key bed
    span('Body', (-1.4, 2.25, -1.68), (1.4, 2.33, -1.12), L)                          # the keys
    for x in (-1.55, 1.4):
        span('Body', (x, 2.25, -1.7), (x + 0.15, 2.6, -1.0), D)                       # cheek blocks
    span('Body', (-0.35, 0.0, -0.75), (0.35, 1.5, -0.55), D)                          # the pedal lyre
    prism('Body', [(-1.0, 2.6), (1.0, 2.6), (1.0, 3.4), (-1.0, 3.4)], -0.85, -0.75, D, plane='xy')   # music desk
    lid = [(x - 1.5, z) for x, z in case]
    prism('Body', lid, 0.0, 0.08, D, plane='xz', m=at((1.5, 2.62, 0), rz=-38))      # the lid, propped open
    cyl('Body', (0, 0, 0), 0.04, 1.3, D, n=4, m=at((-0.2, 2.6, 0.9), rz=-12))        # its stick
    span('Body', (-0.9, 0, -2.6), (0.9, 1.6, -1.95), G, bevel=0.06)                    # the bench
    finish(proxy=False, note='silhouette A: a grand piano with its lid propped open, a bench at the keyboard')


def grand_piano_b():
    decor('GrandPiano_B', 2, 2, 'Floor')
    # An upright, its back toward +Z, the keyboard toward -Z, the bench in front.
    span('Body', (-2.2, 0, 1.05), (2.2, 4.6, 2.6), G, bevel=0.06)                      # the case
    span('Body', (-2.25, 4.6, 0.95), (2.25, 4.85, 2.6), D, bevel=0.04)                 # the top
    span('Body', (-2.2, 2.0, 0.4), (2.2, 2.35, 1.05), D)                               # key bed
    span('Body', (-2.0, 2.35, 0.42), (2.0, 2.43, 0.98), L)                             # the keys
    for x in (-2.2, 2.0):
        span('Body', (x, 0, 0.4), (x + 0.2, 2.6, 1.05), D)                            # the cheeks and toes
    span('Body', (-1.6, 2.9, 0.98), (1.6, 4.3, 1.05), D)                               # the fallboard panel
    for x in (-1.75, 1.75):              # candle arms on its front
        box('Body', (x, 3.6, 0.8), (0.12, 0.12, 0.5), D)
        cyl('Body', (x, 3.66, 0.55), 0.09, 0.45, L, n=6)
    span('Body', (-1.0, 0, -1.4), (1.0, 1.6, -0.75), G, bevel=0.06)                   # the bench
    finish(proxy=False, note='silhouette B: an upright piano against the wall side, candle arms, a bench')


BUILD = [('GrandfatherClock_A', grandfather_clock_a), ('GrandfatherClock_B', grandfather_clock_b),
         ('WallClock', wall_clock), ('BlackRoses', black_roses), ('CarnivorousPlant', carnivorous_plant),
         ('GhostFern', ghost_fern), ('Armchair', armchair), ('VelvetSofa', velvet_sofa), ('Bookshelf', bookshelf),
         ('SideTable', side_table), ('GrandPiano_A', grand_piano_a), ('GrandPiano_B', grand_piano_b)]


# --- The review sheet: each piece on its footprint beside the 5-stud person, labelled --------------

def _mat(name, rgb):
    m = bpy.data.materials.get(name) or bpy.data.materials.new(name)
    m.diffuse_color = (*[c / 255 for c in rgb], 1)
    return m


def _block(lo, hi, rgb):
    lo, hi = Vector(lo), Vector(hi)
    me = bpy.data.meshes.new('blk')
    ob = bpy.data.objects.new('blk', me)
    bpy.context.scene.collection.objects.link(ob)
    import bmesh
    bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=1)
    bm.to_mesh(me)
    bm.free()
    c, s = (lo + hi) / 2, hi - lo
    ob.location = K.rb2bl(c)
    ob.scale = (s.x, s.z, s.y)
    me.materials.append(_mat(f'm{rgb}', rgb))
    return ob


def _person(x, z):
    legs, shirt, skin = (40, 60, 140), (60, 150, 90), (240, 200, 150)
    for lo, hi, rgb in (((-0.95, 0, -0.45), (-0.05, 2.0, 0.45), legs), ((0.05, 0, -0.45), (0.95, 2.0, 0.45), legs),
                        ((-1.0, 2.0, -0.5), (1.0, 4.0, 0.5), shirt), ((-1.9, 2.0, -0.45), (-1.02, 4.0, 0.45), skin),
                        ((1.02, 2.0, -0.45), (1.9, 4.0, 0.45), skin), ((-0.6, 4.0, -0.6), (0.6, 5.0, 0.6), skin)):
        _block((lo[0] + x, lo[1], lo[2] + z), (hi[0] + x, hi[1], hi[2] + z), rgb)


def _label(text, x, z, size=0.75):
    cu = bpy.data.curves.new('lbl', 'FONT')
    cu.body = text
    cu.size = size
    cu.align_x = 'CENTER'
    ob = bpy.data.objects.new('lbl', cu)
    bpy.context.scene.collection.objects.link(ob)
    ob.location = K.rb2bl((x, 0.02, z))
    # Flat on the floor, reading along Blender +X: left to right from the camera at -Z.
    ob.data.materials.append(_mat('ink', (20, 20, 25)))
    return ob


def sheet(path):
    for ob in list(bpy.data.objects):
        bpy.data.objects.remove(ob)
    bpy.context.scene.unit_settings.scale_length = 0.01
    rows = [BUILD[:6], BUILD[6:]]
    for r, row in enumerate(rows):
        x = 0.0                       # laid toward Roblox -X: left to right as the camera at -Z sees it
        z0 = r * 22.0
        for name, _ in row:
            rec = next(rr for p, rr, _ in K.BUILT if rr['name'] == f'Decor_{name}')
            fw, fd, layer = rec['decor']['fw'], rec['decor']['fd'], rec['decor']['layer']
            W, Dd = 3 * fw, 3 * fd
            cx = -(x + W / 2)
            before = set(bpy.data.objects)
            bpy.ops.import_scene.fbx(filepath=str(K.ROOT / 'blender' / SET / 'fbx' / f'Decor_{name}.fbx'))
            for o in set(bpy.data.objects) - before:
                if o.parent is None:
                    o.matrix_world = Matrix.Translation(K.rb2bl((cx, 0, z0))) @ o.matrix_world
                if o.name.startswith('Root'):
                    o.hide_render = True
            # The footprint's 3-stud squares, a hair under the floor line, and a wall behind a Wall piece.
            for i in range(fw):
                for j in range(fd):
                    ax, az = cx - W / 2 + 3 * i, z0 - Dd / 2 + 3 * j
                    _block((ax + 0.05, -0.06, az + 0.05), (ax + 2.95, -0.01, az + 2.95), (205, 200, 185))
            if layer == 'Wall':
                _block((cx - W / 2, 0, z0 + Dd / 2 - 0.4), (cx + W / 2, 7.5, z0 + Dd / 2), (175, 170, 160))
            _person(cx - W / 2 - 2.1, z0 + 0.5)
            _label(name.replace('_', ' ') + '\n' + f'{fw}x{fd} {layer}', cx - 1.0, z0 - Dd / 2 - 1.4, 0.72)
            x += W + 5.4
    _block((-80, -0.4, -8), (4, -0.06, 36), (150, 147, 140))
    sc = bpy.context.scene
    sc.render.engine = 'BLENDER_WORKBENCH'
    sc.display.shading.light = 'STUDIO'
    sc.display.shading.color_type = 'MATERIAL'
    sc.display.shading.show_shadows = False
    sc.display.shading.show_cavity = True
    sc.render.resolution_x, sc.render.resolution_y = 1500, 820
    bpy.context.view_layer.update()          # the blocks' matrices, before they are measured
    pts = [ob.matrix_world @ Vector(c) for ob in sc.objects if ob.type in ('MESH', 'FONT') and not ob.hide_render
           and not (ob.dimensions.x > 60) for c in ob.bound_box]
    lo = Vector([min(p[i] for p in pts) for i in range(3)])
    hi = Vector([max(p[i] for p in pts) for i in range(3)])
    centre = (lo + hi) / 2
    cam = bpy.data.objects.new('Sheet', bpy.data.cameras.new('Sheet'))
    sc.collection.objects.link(cam)
    cam.data.type = 'ORTHO'
    direction = Vector((0.35, -1.0, 0.75)).normalized()       # from the front (-Z), raised, a little to one side
    cam.location = centre + direction * 300
    cam.rotation_euler = (-direction).to_track_quat('-Z', 'Y').to_euler()
    cam.data.clip_end = 1000
    rot = cam.rotation_euler.to_matrix()
    right, up = rot @ Vector((1, 0, 0)), rot @ Vector((0, 1, 0))
    xs = [(p - centre).dot(right) for p in pts]
    ys = [(p - centre).dot(up) for p in pts]
    aspect = sc.render.resolution_x / sc.render.resolution_y
    cam.data.ortho_scale = max(max(xs) - min(xs), (max(ys) - min(ys)) * aspect) * 1.03
    cam.location += right * (max(xs) + min(xs)) / 2 + up * (max(ys) + min(ys)) / 2
    sc.camera = cam
    path.parent.mkdir(parents=True, exist_ok=True)
    sc.render.filepath = str(path)
    bpy.ops.render.render(write_still=True)
    print(f'SHEET {path}', flush=True)


def main():
    K.start_set(SET)
    refused = []
    for name, fn in BUILD:
        if not K.want(f'Decor_{name}'):
            continue
        try:
            fn()
        except K.Refused as e:
            print(str(e), flush=True)
            refused.append(name)
    if refused:
        raise SystemExit(f'REFUSED: {refused}')
    K.end_set('Haunted Manor decor, grey silhouettes for his pick (not for import)',
              [([f'Decor_{n}' for n, _ in BUILD[:6]], 3, 1.0), ([f'Decor_{n}' for n, _ in BUILD[6:]], 3, 1.0)],
              sheet=False)
    if not K.NOPREVIEW:
        sheet(K.ROOT / 'blender' / SET / 'review' / 'silhouettes.png')


main()
