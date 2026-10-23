"""Location 3's ten monsters, the Bayou Spa family (GDD Appendix A, WAITING §2.36), first drafts.

The same "cozy creepy" toys as the Haunted Manor and Frostfang sets (GDD §12):
chunky rounded shapes, big glowing eyes with dark pupils and a white glint,
rosy cheeks on the soft ones, soft colours from Species.luau's `look`, nothing
sharp. Swampy here: moss, lily pads, mud, steam, fireflies and jazz; the glows
are warm firefly ambers and cool moonlight. Each species is its shapes and a
call to monster_kit.finish(), which refuses anything breaking MODELS.md,
"Monsters and street NPCs". Static meshes (the kit's export); each model's
manifest record carries `rig_shape`, the armature it takes when the rigs come
(LAUNCH.md #6: Blob, Biped, Float or Serpent).

This script, not the kit, also renders the review pictures: the grey
silhouettes (Workbench) and, with `final`, the finished sheets (Cycles on the
CPU, 4 threads, never the GPU) beside the 5-stud person.

Frame: Blender -Y is the front, +Z up, +X the monster's left (monster_kit).
Run headless only:
    blender -b --python-exit-code 1 -t 4 -P tools/build_monsters_l3.py [-- norender] [final] [only BogFrog,MudPuppy]
"""
import math
import sys

from pathlib import Path
from mathutils import Matrix, Vector

sys.path.insert(0, str(Path(__file__).resolve().parent))
import monster_kit as k  # noqa: E402
from monster_kit import ball, limb, lathe, rings, box, arc_shell, pair, eyes, marker, on_ball, front_y, tube  # noqa: E402

import bpy  # noqa: E402

SET = 'monsters/bayou_spa'
ORDER = ['BogFrog', 'Mossling', 'FireflySprite', 'MudPuppy', 'GatorGhoul',
         'WillOWisp', 'SwampHag', 'BayouHydra', 'CypressKing', 'MoonHeron']
ONLY = next((a.split(',') for a in k.ARGS[k.ARGS.index('only') + 1:k.ARGS.index('only') + 2]), None) \
    if 'only' in k.ARGS else None
FINAL = 'final' in k.ARGS

# The armature each species takes: Species.luau's shape (MODELS.md, "The rig";
# the Quadruped rig was added for the Mud Puppy, 2026-10-23).
RIG = {'BogFrog': 'Blob', 'Mossling': 'Blob', 'FireflySprite': 'Float', 'MudPuppy': 'Quadruped',
       'GatorGhoul': 'Biped', 'WillOWisp': 'Float', 'SwampHag': 'Biped', 'BayouHydra': 'Serpent',
       'CypressKing': 'Biped', 'MoonHeron': 'Biped'}

WHITE = (255, 255, 255)
BLUSH = (255, 150, 180)
INK = (45, 32, 60)          # the game's dark: a deep plum, never pure black (as Haunted Manor)
FIREFLY = (255, 215, 100)   # the bayou's warm glow


def cheeks(at_l, r=(0.16, 0.06, 0.1), part='Trim'):
    pair(ball, part, at=at_l, r=r, mirror=['at'])


def smile(part, z0, half, lift, y_at, r=0.045, n=11, cx=0.0):
    """A curved mouth across the front: z0 at the middle (x = cx), rising `lift` at
    cx +/- half; y_at(x, z) is the surface's y there."""
    pts = []
    for i in range(n):
        u = -1 + 2 * i / (n - 1)
        x = cx + half * u
        z = z0 + lift * u * u
        pts.append((x, y_at(x, z), z))
    return tube(part, pts, r, n=8)


def eye(part, c, r, side):
    """One eye as monster_kit.eyes() makes it, at any centre (a head off the middle), lighter."""
    c = Vector(c)
    rx, ry, rz = r, r * 0.8, r
    ball(part, c, (rx, ry, rz), n=10, k=5)
    pc = c + Vector((0, -ry * 0.62, -rz * 0.05))
    ball('Dark', pc, (rx * 0.55, ry * 0.45, rz * 0.6), n=8, k=4)
    ball('Light', pc + Vector((side * rx * 0.18, -ry * 0.38, rz * 0.25)), rx * 0.17, n=6, k=3)


def recentre_y():
    """Move the whole model along Y so its floor contacts are centred on the origin
    (MODELS.md: origin between the "feet"); X is left alone, it is symmetric."""
    m = k.m
    low = [o.matrix_world @ v.co for p, objs in m.pieces.items() if p not in k.ALL_MARKERS
           for o in objs for v in o.data.vertices if (o.matrix_world @ v.co).z < 0.08]
    cy = (min(p.y for p in low) + max(p.y for p in low)) / 2
    for objs in m.pieces.values():
        for o in objs:
            o.data.transform(Matrix.Translation((0, -cy, 0)))
    for name in m.markers:
        m.markers[name] = m.markers[name] - Vector((0, cy, 0))
    return cy


def finished(note, rig=None):
    sid = k.m.id
    rec = k.finish(note, rig=rig)
    rec['rig_shape'] = RIG[sid]
    return rec


def bog_frog():
    k.begin('BogFrog', SET, {'Dark': INK, 'Light': WHITE, 'Skin': (210, 225, 140), 'Trim': BLUSH,
                             'Glow_Eyes_1': (255, 210, 90), 'Glow_Eyes_2': (255, 210, 90)})
    S = [(0, 0), (0.03, 0.85), (0.2, 1.15), (0.6, 1.35), (1.1, 1.33), (1.6, 1.15), (2.0, 0.85), (2.25, 0.42),
         (2.33, 0)]
    lathe('Body', S, n=24, sy=0.9)                                                           # the squat body
    DC, DR = (0.55, -0.3, 2.38), (0.5, 0.46, 0.52)
    pair(ball, 'Body', at=DC, r=DR, n=14, k=7, mirror=['at'])                                # bulging eye domes
    eyes((0.55, on_ball(DC, DR, 0.55, 2.44, out=-0.12).y, 2.44), 0.3)
    fy = lambda x, z: front_y(S, z, x, sy=0.9) + 0.01
    smile('Dark', 1.76, 0.75, 0.12, fy)                                                      # the wide frog grin
    cheeks((0.72, front_y(S, 1.95, 0.72, sy=0.9), 1.95))
    ball('Skin', (0, front_y(S, 1.4, 0, sy=0.9) + 0.18, 1.4), (0.5, 0.32, 0.32))             # croaking throat sac
    ball('Skin', (0, front_y(S, 0.65, 0, sy=0.9) + 0.22, 0.65), (0.8, 0.3, 0.5))             # pale belly
    pair(ball, 'Dark', at=(0.17, -1.25, 1.03), r=(0.17, 0.07, 0.12), rot=(0, 15, 0), mirror=['at'])  # bow tie
    ball('Dark', (0, -1.29, 1.03), (0.07, 0.06, 0.08), n=8, k=4)                             # its knot
    lathe('Skin', [(-0.04, 0.34), (0.04, 0.34)], at=(0, 0.2, 2.4), n=16, rot=(-10, 0, 0))    # lily pad cap
    ball('Trim', (0, 0.2, 2.53), (0.1, 0.1, 0.09), n=8, k=4)                                 # its flower
    for a in (0, 120, 240):
        t = math.radians(a + 90)
        ball('Trim', (0.12 * math.cos(t), 0.2 + 0.12 * math.sin(t), 2.5), (0.09, 0.09, 0.06), n=8, k=4,
             rot=(0, 0, a))
    for s in (1, -1):
        limb('Body', (s * 0.85, -0.75, 1.05), (s * 0.75, -0.92, 0.25), 0.15)                 # front legs
        ball('Body', (s * 0.75, -0.95, 0.09), (0.26, 0.25, 0.09))                            # webbed hands
        ball('Body', (s * 1.0, 0.15, 0.48), (0.42, 0.65, 0.48))                              # big haunches
        ball('Body', (s * 1.15, -0.45, 0.08), (0.28, 0.4, 0.08))                             # hind feet
    marker('Hand', (-0.75, -0.95, 0.12))
    marker('Nameplate', (0, 0, 3.6))
    return finished('Blob, a squat bog frog on its haunches: eye domes, a wide grin, a puffed throat sac '
                    '(quirk "croaks a chord at check-in"), a jazz bow tie, a lily pad cap with a pink flower. '
                    'Hand is the right front hand.')


def mossling():
    k.begin('Mossling', SET, {'Dark': INK, 'Light': WHITE, 'Skin': (175, 215, 120), 'Trim': BLUSH,
                              'Glow_Eyes_1': (240, 235, 140), 'Glow_Eyes_2': (240, 235, 140)})
    S = [(0, 0), (0.05, 0.8), (0.3, 1.1), (0.8, 1.25), (1.3, 1.2), (1.8, 1.0), (2.15, 0.65), (2.38, 0)]
    rings('Body', [(0, 0, z, r, r * 0.92) for z, r in S], n=27,
          radial=lambda t: 1 + 0.04 * math.cos(9 * t))                                       # the soft moss ball
    pair(ball, 'Body', at=(0.45, -0.45, 0.12), r=(0.28, 0.34, 0.12), mirror=['at'])          # stubby feet
    pair(ball, 'Body', at=(1.18, -0.25, 1.0), r=(0.24, 0.22, 0.3), mirror=['at'])            # arm nubs
    for t, z in ((20, 1.6), (160, 1.6), (90, 1.95), (50, 2.1), (130, 2.1), (90, 1.2), (0, 1.15), (180, 1.15)):
        a = math.radians(t)
        r = float(k.np.interp(z, [p[0] for p in S], [p[1] for p in S])) * 0.95
        ball('Skin', (r * math.cos(a), 0.92 * r * math.sin(a), z), 0.3, n=10, k=5)          # fresh moss tufts
    eyes((0.4, front_y(S, 1.45, 0.4, sy=0.92, out=-0.12), 1.45), 0.3)
    smile('Dark', 1.08, 0.18, 0.05, lambda x, z: front_y(S, z, x, sy=0.92) + 0.01, r=0.04, n=7)
    cheeks((0.75, front_y(S, 1.15, 0.75, sy=0.92), 1.15))
    limb('Skin', (0, 0.05, 2.25), (0.03, 0.05, 2.8), 0.07)                                   # the sprout
    pair(ball, 'Skin', at=(0.3, 0.05, 2.88), r=(0.32, 0.1, 0.13), rot=(0, -25, 0), mirror=['at'])
    limb('Skin', (0.45, 0.25, 2.0), (0.6, 0.3, 2.4), 0.04)                                   # a second, budding
    ball('Trim', (0.62, 0.3, 2.47), 0.1, n=8, k=4)
    marker('Hand', (-1.2, -0.25, 1.0))
    marker('Nameplate', (0, 0, 3.6))
    return finished('Blob, a soft round moss ball with light-green tufts, a two-leaf sprout and a pink bud on top '
                    '(quirk "little sprouts grow where it sits"). Hand is the right arm nub.')


def firefly_sprite():
    k.begin('FireflySprite', SET, {'Dark': INK, 'Light': WHITE, 'Skin': (220, 240, 255), 'Trim': BLUSH,
                                   'Glow_Eyes_1': (140, 220, 255), 'Glow_Eyes_2': (140, 220, 255),
                                   'Glow_Warm_1': (255, 190, 30), 'Glow_Warm_2': (255, 235, 150)})
    lathe('Glow_Warm_1', [(0.08, 0), (0.12, 0.2), (0.28, 0.45), (0.6, 0.62), (0.95, 0.66), (1.25, 0.6),
                          (1.55, 0)], n=24)                                                  # the lantern tail
    ball('Body', (0, 0, 1.62), (0.5, 0.45, 0.38))                                            # thorax
    HC, HR = (0, 0, 2.1), (0.58, 0.52, 0.52)
    ball('Body', HC, HR, n=16, k=8)
    ball('Dark', (0, 0.16, 2.3), (0.6, 0.45, 0.42), n=14, k=7)                              # a firefly's hood
    for s in (1, -1):
        limb('Dark', (s * 0.2, 0.05, 2.5), (s * 0.42, -0.05, 2.85), 0.04, n=6)               # antennae
        ball('Glow_Warm_2', (s * 0.45, -0.07, 2.9), 0.1, n=8, k=4)                           # their lights
    eyes((0.24, on_ball(HC, HR, 0.24, 2.15, out=-0.1).y, 2.15), 0.2)
    ball('Dark', on_ball(HC, HR, 0, 1.86, out=-0.02), (0.1, 0.04, 0.04), n=8, k=4)
    cheeks((0.4, on_ball(HC, HR, 0.4, 1.92).y, 1.92), r=(0.1, 0.04, 0.07))
    pair(ball, 'Dark', at=(0.27, 0.32, 1.6), r=(0.3, 0.24, 0.65), rot=(-15, 0, -10), mirror=['at'])  # wing cases
    pair(ball, 'Skin', at=(0.45, 0.5, 1.95), r=(0.45, 0.04, 0.25), rot=(0, -30, 20), mirror=['at'])  # wings
    for s in (1, -1):
        limb('Body', (s * 0.4, -0.1, 1.7), (s * 0.6, -0.4, 1.55), 0.08, n=8)
        ball('Body', (s * 0.63, -0.43, 1.52), 0.1, n=8, k=4)
    marker('Hand', (-0.63, -0.43, 1.52))
    marker('Nameplate', (0, 0, 3.5))
    return finished('Float, a little firefly with a long glowing amber lantern tail (Glow_Warm_1, quirk "lights up '
                    'the hallway"), glowing antenna tips (Glow_Warm_2), a dark hood, dark beetle wing cases and two pale wings. Hand is the right hand.')


def ell(c, r, d, sink=0.95):
    """A point on the ellipsoid ball(c, r) in the direction d (before scaling)."""
    d = Vector(d).normalized()
    return Vector(c) + Vector((r[0] * d.x, r[1] * d.y, r[2] * d.z)) * sink


def mud_puppy():
    mud = (58, 36, 20)
    k.begin('MudPuppy', SET, {'Dark': INK, 'Light': (245, 235, 215), 'Skin': mud, 'Trim': (205, 65, 75),
                              'Glow_Eyes_1': (255, 220, 120), 'Glow_Eyes_2': (255, 220, 120)})
    BC, BR = (0, 0.2, 1.05), (0.72, 1.0, 0.65)
    ball('Body', BC, BR, n=16, k=8)
    for s in (1, -1):
        limb('Body', (s * 0.42, -0.45, 0.95), (s * 0.42, -0.55, 0.22), 0.2)                  # front legs
        ball('Skin', (s * 0.42, -0.62, 0.13), (0.24, 0.3, 0.13))                             # muddy paws
        limb('Skin', (s * 0.42, -0.53, 0.5), (s * 0.42, -0.56, 0.25), 0.215, n=10)           # muddy socks
        limb('Skin', (s * 0.45, 0.76, 0.5), (s * 0.45, 0.74, 0.25), 0.235, n=10)
        limb('Body', (s * 0.45, 0.8, 0.95), (s * 0.45, 0.75, 0.22), 0.22)                    # hind legs
        ball('Skin', (s * 0.45, 0.72, 0.13), (0.25, 0.3, 0.13))
    dip = [(0, BC[1], BC[2] - BR[2] * 1.03, 0)]
    for i in range(1, 7):
        phi = math.radians(-90 + 80 * i / 6)
        dip.append((0, BC[1], BC[2] + BR[2] * 1.03 * math.sin(phi), BR[0] * 1.03 * math.cos(phi),
                    BR[1] * 1.03 * math.cos(phi)))
    rings('Skin', dip, n=20, wave={6: lambda t: 0.1 * math.sin(5 * t) + 0.05 * math.sin(11 * t)})  # dipped in mud
    for d in ((0.6, 0.3, 0.75), (-0.5, -0.2, 0.85), (0.3, 0.8, 0.5)):
        ball('Skin', ell(BC, BR, d, 0.9), 0.28, n=10, k=5)                                   # mud splats on top
    limb('Body', (0, 1.0, 1.3), (0, 1.45, 1.72), 0.18, 0.12, n=8)                            # happy tail
    limb('Body', (0, 1.45, 1.72), (0, 1.48, 2.05), 0.12, 0.07, n=8)
    HC, HR = (0, -0.85, 1.95), (0.72, 0.66, 0.62)
    ball('Body', HC, HR, n=16, k=8)
    ball('Light', (0, -1.42, 1.78), (0.38, 0.32, 0.28))                                      # cream muzzle
    ball('Dark', (0, -1.74, 1.9), (0.13, 0.09, 0.1), n=8, k=4)                               # nose
    ball('Dark', (0, -1.62, 1.62), (0.22, 0.05, 0.05), n=8, k=4)                             # mouth
    ball('Trim', (0, -1.6, 1.5), (0.12, 0.07, 0.15), n=8, k=4)                               # tongue
    eyes((0.3, on_ball(HC, HR, 0.3, 2.12, out=-0.1).y, 2.12), 0.21)
    for d, r in (((0.35, 0.2, 0.9), 0.24), ((-0.75, -0.45, 0.2), 0.16), ((0.8, -0.2, -0.3), 0.15)):
        ball('Skin', ell(HC, HR, d, 0.92), r, n=10, k=5)                                     # mud on its head and face
    pair(ball, 'Skin', at=(0.7, -0.75, 1.75), r=(0.16, 0.32, 0.5), rot=(0, -18, 0), mirror=['at'])  # floppy ears
    lathe('Trim', [(0, 0.33), (0.3, 0.33), (0.34, 0.26), (0.36, 0)], at=(0.12, -0.8, 2.45), n=16,
          rot=(0, -12, 0))                                                                   # bellhop cap
    lathe('Light', [(0.02, 0.345), (0.1, 0.345)], at=(0.12, -0.8, 2.45), n=16, rot=(0, -12, 0))  # its band
    marker('Hand', (0, -1.66, 1.5))
    marker('Nameplate', (0, -0.3, 3.5))
    return finished('Quadruped, a chubby brown pup dipped in mud to its middle '
                    'with a drippy edge, muddy socks and splats (quirk "shakes mud on the doorman"), a cream muzzle, floppy ears, a red bellhop '
                    'pillbox cap with a cream band. Hand is the mouth: a pup carries in its mouth.',
                    rig=dict(body_z=1.05, front_y=-0.5, back_y=0.78, leg_x=0.43, nose=(0, -1.6, 1.9),
                             tail=(0, 1.48, 2.05)))


def gator_ghoul():
    gl = (190, 255, 130)
    k.begin('GatorGhoul', SET, {'Dark': INK, 'Light': (250, 248, 232), 'Skin': (200, 205, 150),
                                'Trim': (240, 200, 90), 'Glow_Eyes_1': gl, 'Glow_Eyes_2': gl})
    for s in (1, -1):
        limb('Body', (s * 0.55, 0.05, 0.45), (s * 0.55, 0.05, 1.3), 0.38)
        ball('Body', (s * 0.6, -0.2, 0.22), (0.4, 0.6, 0.22))                                # big feet
    T = [(1.0, 0), (1.05, 0.95), (1.6, 1.18), (2.4, 1.22), (3.1, 1.08), (3.5, 0.85), (3.75, 0)]
    lathe('Body', T, n=20, sy=0.85)
    ball('Skin', (0, front_y(T, 2.2, 0, sy=0.85) + 0.25, 2.2), (0.6, 0.3, 0.95))            # pale belly
    rt = lambda z: float(k.np.interp(z, [p[0] for p in T], [p[1] for p in T]))
    arc_shell('Dark', [(z, rt(z) + 0.05) for z in (1.75, 2.2, 2.7, 3.15)], -55, 235, 0.08, sy=0.85, n=14)  # vest
    a = math.radians(-40)
    rb = rt(2.8) + 0.07
    ball('Trim', (rb * math.cos(a), rb * 0.85 * math.sin(a), 2.8), (0.14, 0.06, 0.14), rot=(0, 0, 50))  # badge
    for s in (1, -1):
        limb('Body', (s * 1.0, 0, 3.05), (s * 1.4, -0.25, 2.3), 0.3, 0.27)
        limb('Body', (s * 1.4, -0.25, 2.3), (s * 1.35, -0.55, 1.65), 0.27, 0.26)
        ball('Body', (s * 1.35, -0.62, 1.5), (0.32, 0.3, 0.32), n=10, k=5)                   # big hands
    CC, CR = (0, -0.15, 4.05), (0.78, 0.72, 0.62)
    ball('Body', CC, CR, n=14, k=7)                                                          # cranium
    SC, SR = (0, -1.15, 3.82), (0.56, 0.92, 0.33)
    ball('Body', SC, SR, n=14, k=7)                                                          # the long snout
    for s in (1, -1):
        ball('Dark', (s * 0.15, -1.95, 3.98), 0.05, n=6, k=3)                                # nostrils
    BC = (0.36, -0.55, 4.42)
    pair(ball, 'Body', at=BC, r=0.3, mirror=['at'])                                          # eye bumps
    eyes((0.36, on_ball(BC, 0.3, 0.36, 4.46, out=-0.1).y, 4.46), 0.22)
    g = lambda a, out=1.01, dz=0.0: (SR[0] * 0.983 * math.cos(a) * out, SC[1] + SR[1] * 0.983 * math.sin(a) * out,
                                     3.76 + 0.1 * (1 + math.sin(a)) + dz)
    tube('Dark', [g(math.radians(d)) for d in range(150, 391, 15)], 0.07, n=8)               # the far-too-wide grin
    for d in range(165, 376, 21):
        ball('Light', g(math.radians(d), 1.04, -0.06), 0.1, n=6, k=3)                       # far too many teeth
    lathe('Dark', [(0, 0.5), (0.28, 0.47), (0.33, 0.35), (0.36, 0)], at=(0, -0.05, 4.62), n=16, rot=(-8, 0, 0))
    ball('Dark', (0, -0.62, 4.72), (0.45, 0.3, 0.05), rot=(-8, 0, 0))                        # security cap, visor
    ball('Trim', (0, -0.5, 4.86), (0.09, 0.04, 0.09), n=8, k=4)                              # cap badge
    tube('Body', [(0, 0.6, 1.7), (0, 1.2, 1.2), (0.25, 1.7, 0.72), (0.7, 2.0, 0.45), (1.2, 2.05, 0.4),
                  (1.6, 1.8, 0.5)], [0.45, 0.38, 0.3, 0.22, 0.16, 0.11], n=10)               # tail swept aside, off the floor
    marker('Hand', (-1.35, -0.62, 1.5))
    marker('Nameplate', (0, 0, 5.6))
    return finished('Biped, an upright gator: a long snout with a far-too-wide grin and a row of round teeth '
                    '(quirk), ghoul-green eyes on eye bumps, a pale belly, a Security vest, cap and gold badge, '
                    'the tail held off the floor.')


def will_o_wisp():
    gl = (255, 240, 170)
    k.begin('WillOWisp', SET, {'Dark': INK, 'Light': WHITE, 'Trim': BLUSH, 'Glow_Eyes_1': gl, 'Glow_Eyes_2': gl,
                               'Glow_Cold_1': (110, 255, 215)})
    P = [(0.45, 0), (0.55, 0.45), (0.8, 0.78), (1.2, 0.95), (1.7, 0.97), (2.2, 0.85), (2.55, 0.6), (2.75, 0.3),
         (2.82, 0)]
    rings('Body', [(0, 0, z, r, r * 0.9) for z, r in P], n=20)
    rings('Glow_Cold_1', [(0, 0, 2.45, 0.55, 0.5), (0.04, 0, 2.75, 0.5, 0.45), (0.12, 0, 3.0, 0.4, 0.36),
                          (0.06, 0, 3.25, 0.3, 0.27), (0.16, 0, 3.5, 0.2, 0.18), (0.32, 0, 3.72, 0.1, 0.09),
                          (0.45, 0, 3.95, 0)], n=16, radial=lambda t: 1 + 0.1 * math.cos(3 * t),
          wave={2: lambda t: 0.06 * math.sin(4 * t), 4: lambda t: 0.05 * math.sin(5 * t + 1)})  # its flame
    for s in (1, -1):
        rings('Glow_Cold_1', [(0, 0, 0, 0.28), (s * 0.06, 0, 0.28, 0.24), (s * 0.02, 0, 0.5, 0.15),
                              (s * 0.15, 0, 0.7, 0.07), (s * 0.28, 0, 0.85, 0)], n=12,
              matrix=Matrix.Translation((s * 0.4, 0, 2.3)) @ Matrix.Rotation(math.radians(s * 25), 4, 'Y'))
    fy = lambda x, z: front_y(P, z, x, sy=0.9)
    eyes((0.33, fy(0.33, 1.75) + 0.12, 1.75), 0.27)
    ball('Dark', (0, fy(0, 1.3) - 0.01, 1.3), (0.08, 0.05, 0.09), n=8, k=4)                 # a shy little "o"
    cheeks((0.6, fy(0.6, 1.45), 1.45), r=(0.14, 0.05, 0.09))
    for s in (1, -1):                                                                        # little arms
        limb('Body', (s * 0.75, -0.3, 1.2), (s * 0.98, -0.45, 0.95), 0.11, n=8)
        ball('Body', (s * 1.0, -0.48, 0.9), 0.12, n=8, k=4)
    tube('Body', [(0, 0.15, 0.8), (0, 0.45, 0.55), (0.15, 0.75, 0.45), (0.38, 0.9, 0.45), (0.55, 0.85, 0.58)],
         [0.42, 0.3, 0.18, 0.1, 0.06], n=10)                                                 # wispy tail
    for c, r in (((1.05, 0.25, 2.5), 0.12), ((-0.95, 0.35, 3.05), 0.1), ((0.8, 0.15, 3.4), 0.08)):
        ball('Glow_Cold_1', c, r, n=8, k=4)                                                  # floating motes
    marker('Hand', (-1.0, -0.48, 0.9))
    marker('Nameplate', (0, 0, 4.6))
    return finished('Float, a pale-blue spirit under a glowing three-tongued flame (Glow_Cold_1), a wispy tail, little arms, a shy "o" '
                    'mouth and blush (quirk "goes out when it gets shy"), three glowing motes (Glow_Cold_1). '
                    'Hand is the right hand.')


def swamp_hag():
    k.begin('SwampHag', SET, {'Dark': INK, 'Light': (232, 230, 216), 'Skin': (180, 210, 150),
                              'Trim': (125, 85, 150), 'Glow_Eyes_1': (255, 205, 90),
                              'Glow_Eyes_2': (255, 205, 90), 'Glow_Magic_1': (160, 255, 205)})
    pair(ball, 'Dark', at=(0.25, -0.15, 0.12), r=(0.18, 0.3, 0.12), mirror=['at'])          # boots
    D = [(0.15, 0), (0.15, 1.1), (0.6, 1.0), (1.3, 0.86), (2.0, 0.72), (2.6, 0.66), (2.95, 0.55), (3.15, 0.32),
         (3.25, 0)]
    lean = lambda z: -0.3 * (z / 3.25) ** 2                                                  # a hunch forward
    rings('Body', [(0, lean(z), z, r) for z, r in D], n=24, wave={1: lambda t: 0.06 * math.sin(7 * t)})  # robe
    arc_shell('Trim', [(2.3, 0.82), (2.65, 0.8), (2.95, 0.7), (3.15, 0.52)], -60, 240, 0.07, at=(0, -0.21, 0),
              n=20)                                                                          # the shawl
    HC, HR = (0, -0.4, 3.62), (0.58, 0.55, 0.6)
    ball('Skin', HC, HR, n=16, k=8)
    ball('Light', (0, -0.15, 3.72), (0.66, 0.55, 0.62), n=16, k=8)                           # wild grey hair
    for s in (1, -1):
        limb('Light', (s * 0.45, -0.15, 3.5), (s * 0.55, 0.0, 2.75), 0.2, 0.12)              # side locks
    limb('Light', (0, 0.15, 3.6), (0, 0.35, 2.6), 0.35, 0.18)
    hat = Matrix.Translation((0, -0.3, 4.07)) @ Matrix.Rotation(math.radians(-16), 4, 'X')
    lathe('Dark', [(-0.07, 0.9), (-0.045, 0.97), (0.045, 0.97), (0.07, 0.9)], at=(0, -0.3, 4.05), n=24,
          rot=(-16, 0, 0))                                                                   # hat brim, tilted back
    rings('Dark', [(0, 0, 0, 0.55), (0.02, 0, 0.3, 0.45), (0.08, 0.05, 0.55, 0.32), (0.2, 0.12, 0.75, 0.2),
                   (0.4, 0.2, 0.84, 0.12), (0.55, 0.25, 0.8, 0)], n=16, matrix=hat)          # its droopy cone
    ball('Trim', hat @ Vector((0.6, 0.25, 0.78)), 0.1, n=8, k=4)                             # tip bobble
    lathe('Trim', [(-0.06, 0.56), (0.06, 0.53)], at=(0, -0.3, 4.15), n=20, rot=(-16, 0, 0))  # hat band
    ball('Skin', on_ball(HC, HR, 0, 3.55, out=0.12), (0.17, 0.2, 0.17), n=10, k=5)           # big round nose
    eyes((0.23, on_ball(HC, HR, 0.23, 3.78, out=-0.1).y, 3.78), 0.17)
    smile('Dark', 3.3, 0.22, 0.06, lambda x, z: on_ball(HC, HR, x, z, out=0.0).y + 0.01, r=0.04, n=7)
    mo = on_ball(HC, HR, 0.06, 3.27)
    box('Light', (0.06, mo.y - 0.02, 3.25), (0.07, 0.05, 0.08), bevel=0.015)                 # one tooth
    for s in (1, -1):
        limb('Body', (s * 0.55, -0.25, 2.75), (s * 0.7, -0.65, 2.2), 0.16, 0.22)            # sleeves
        ball('Skin', (s * 0.7, -0.78, 2.1), 0.15, n=10, k=5)
    ball('Trim', (0.8, -1.0, 1.88), (0.32, 0.28, 0.26))                                      # her teapot
    ball('Trim', (0.8, -1.0, 2.16), 0.08, n=8, k=4)
    limb('Trim', (1.08, -1.03, 1.9), (1.32, -1.06, 2.1), 0.07, 0.05, n=8)
    for c, r in (((1.36, -1.06, 2.2), 0.14), ((1.45, -1.02, 2.55), 0.19), ((1.3, -0.98, 2.8), 0.23),
                 ((1.08, -0.95, 3.0), 0.25), ((1.32, -0.95, 3.15), 0.2)):
        ball('Glow_Magic_1', c, r, n=8, k=4)                                                 # mint fog curling up
    marker('Hand', (-0.7, -0.78, 2.1))
    marker('Nameplate', (0, 0, 5.6))
    return finished('Biped, a hunched kindly swamp hag: a sage robe with a ragged hem, a purple shawl, wild grey '
                    'hair, a droopy witch hat, a big round nose and one tooth, a teapot puffing mint fog '
                    '(Glow_Magic_1, quirk). Hand is the right hand.')


def bayou_hydra():
    k.begin('BayouHydra', SET, {'Dark': INK, 'Light': WHITE, 'Skin': (175, 215, 160), 'Trim': (255, 140, 170),
                                'Glow_Eyes_1': (255, 215, 110), 'Glow_Eyes_2': (255, 215, 110)})
    rings('Body', [(0, 0, z, r, r * 0.88) for z, r in ((0, 0), (0.03, 1.25), (0.3, 1.55), (0.85, 1.62),
                                                         (1.45, 1.45), (1.95, 1.1), (2.25, 0.6), (2.35, 0))],
          n=20)                                                                              # the tubby body
    for s in (1, -1):                                                                        # stubby front legs
        limb('Body', (s * 0.85, -0.85, 0.6), (s * 0.95, -1.2, 0.22), 0.26, 0.22, n=8)
        ball('Body', (s * 0.95, -1.3, 0.12), (0.28, 0.32, 0.12), n=10, k=5)
    ball('Skin', (0, -1.15, 0.95), (0.95, 0.4, 0.75))                                        # pale belly
    for y, z, r in ((0.95, 1.75, 0.25), (1.3, 1.25, 0.28), (1.45, 0.7, 0.24)):
        ball('Skin', (0, y, z), (0.07, r, r * 0.85), n=8, k=4)                               # back fins
    tube('Body', [(0, 1.0, 0.55), (0, 1.7, 0.39), (0, 2.3, 0.29), (0, 2.75, 0.45), (0, 2.95, 0.85),
                  (0, 2.8, 1.15), (0, 2.55, 1.15)], [0.5, 0.38, 0.28, 0.22, 0.17, 0.13, 0.1], n=10)  # curled tail
    HR, SR = (0.62, 0.64, 0.52), (0.45, 0.46, 0.3)
    necks = {0: ([(0, -0.1, 1.7), (0, -0.25, 2.6), (0, -0.35, 3.5), (0, -0.45, 4.4), (0, -0.55, 5.05)],
                 (0, -0.6, 5.4)),
             1: ([(0.6, -0.05, 1.6), (1.3, -0.1, 2.25), (1.75, -0.2, 2.95), (1.78, -0.35, 3.6), (1.62, -0.45, 4.05)],
                 (1.62, -0.5, 4.35))}
    heads = []
    for side in (0, 1, -1):
        pts, hc = necks[abs(side)]
        sx = 1 if side >= 0 else -1
        tube('Body', [(sx * x, y, z) for x, y, z in pts], [0.48, 0.4, 0.33, 0.28, 0.26], n=8)
        hc = Vector((sx * hc[0], hc[1], hc[2]))
        ball('Body', hc, HR, n=12, k=6)
        sc = hc + Vector((0, -0.6, -0.12))
        ball('Body', sc, SR, n=10, k=5)                                                      # snout
        for i, d in ((1, 0.27), (2, -0.27)):
            eye(f'Glow_Eyes_{i}', on_ball(hc, HR, hc.x + d, hc.z + 0.14, out=-0.1), 0.22, 1 if d > 0 else -1)
        for d in (0.12, -0.12):
            ball('Dark', on_ball(sc, SR, sc.x + d, sc.z + 0.12, out=-0.01), 0.04, n=6, k=3)  # nostrils
        heads.append((hc, sc))
    (mc, ms), (lc, ls), (rc, rs) = heads
    smile('Dark', ms.z - 0.1, 0.22, 0.06, lambda x, z: on_ball(ms, SR, x, z).y + 0.01, r=0.035, n=7)
    cheeks((0.4, on_ball(mc, HR, 0.4, mc.z - 0.12).y, mc.z - 0.12), r=(0.12, 0.05, 0.08))
    ball('Skin', mc + Vector((0, 0.1, 0.47)), (0.06, 0.32, 0.22), rot=(25, 0, 0), n=10, k=5)  # middle: a crest
    ball('Dark', on_ball(ls, SR, ls.x, ls.z - 0.08, out=-0.02), (0.1, 0.05, 0.1), n=8, k=4)  # left: "ooh, one of..."
    for a in (0, 72, 144, 216, 288):
        t = math.radians(a)
        ball('Trim', lc + Vector((0.57 + 0.1 * math.cos(t), 0.1, 0.27 + 0.1 * math.sin(t))), (0.03, 0.09, 0.09),
             n=6, k=3)                                                                       # ... a lily behind its ear
    ball('Light', lc + Vector((0.57, 0.08, 0.27)), 0.05, n=6, k=3)
    smile('Dark', rs.z - 0.08, 0.2, 0.05, lambda x, z: on_ball(rs, SR, x, z).y + 0.01, r=0.035, n=7, cx=rs.x)
    limb('Trim', on_ball(rs, SR, rs.x, rs.z - 0.12, out=-0.05), on_ball(rs, SR, rs.x, rs.z - 0.12) +
         Vector((0, -0.12, -0.18)), 0.06, 0.07, n=8)                                         # right: tongue out
    cy = recentre_y()
    marker('Hand', (0, 2.55 - cy, 1.15))
    marker('Nameplate', (0, -0.55, 6.7))
    return finished('Serpent, a tubby teal body sitting on the floor on two stubby front legs, with three S-curved necks; the heads differ (quirk '
                    '"every head orders something different"): the middle one smiles under a crest, the left one '
                    'says "ooh" with a lily behind its ear, the right one sticks its tongue out. A curled tail; '
                    'Hand is its tip.',
                    # One Neck and Head for the middle neck; the side necks take the two tail
                    # bones, each on Coil (its curled tail rides on Coil).
                    rig=dict(coil_top=(0, 0, 1.9), neck_base=(0, -0.1, 1.7), head_base=(0, -0.55, 5.0),
                             tail_base=(0.6, -0.05, 1.6), tail_mid=(1.62, -0.5, 4.35),
                             tail_2_base=(-0.6, -0.05, 1.6), tail_tip=(-1.62, -0.5, 4.35), tail_2_parent='Coil',
                             tail_radius=0.35, radius={'Coil': 1.4, 'Neck': 0.35}))


def cypress_king():
    k.begin('CypressKing', SET, {'Dark': INK, 'Light': WHITE, 'Skin': (170, 185, 140), 'Trim': (95, 140, 70),
                                 'Glow_Eyes_1': (255, 205, 90), 'Glow_Eyes_2': (255, 205, 90),
                                 'Glow_Warm_1': (255, 225, 110)})
    for s in (1, -1):
        limb('Body', (s * 0.5, 0, 0.45), (s * 0.5, 0, 1.6), 0.42, 0.48)                      # root legs
        for dx, dy in ((0.2, -0.75), (0.65, 0.05), (0, 0.55)):
            limb('Body', (s * 0.5, 0, 0.2), (s * (0.5 + dx), dy, 0.13), 0.2, 0.13, n=6)      # root toes
    T = [(1.2, 0), (1.3, 0.7), (1.7, 0.9), (2.4, 0.92), (3.3, 0.9), (4.2, 0.85), (4.8, 0.72), (5.1, 0.45),
         (5.2, 0)]
    rings('Body', [(0, 0, z, r, r * 0.9) for z, r in T], n=24, radial=lambda t: 1 + 0.1 * math.cos(8 * t))
    T6 = [(z, r * 1.1) for z, r in T]                                                       # the flutes' crests
    fy = lambda x, z: front_y(T6, z, x, sy=0.9)
    for i, s in ((1, 1), (2, -1)):
        eye(f'Glow_Eyes_{i}', (s * 0.36, fy(0.36, 4.25) + 0.1, 4.25), 0.25, s)
    pair(ball, 'Body', at=(0.38, fy(0.38, 4.6) + 0.05, 4.6), r=(0.25, 0.12, 0.08), rot=(0, 0, 0),
         mirror=['at'])                                                                      # kindly brows
    ball('Body', (0, fy(0, 3.98) - 0.06, 3.98), (0.13, 0.15, 0.17), n=10, k=5)              # knob nose
    smile('Dark', 3.7, 0.3, 0.08, lambda x, z: fy(x, z) + 0.01)
    y0 = fy(0, 3.2) + 0.1
    rings('Skin', [(0, y0, 3.56, 0), (0, y0, 3.5, 0.4, 0.18), (0, y0 - 0.03, 3.3, 0.5, 0.22),
                   (0, y0 - 0.04, 3.05, 0.42, 0.2), (0, y0 - 0.03, 2.8, 0.25, 0.14), (0, y0, 2.6, 0.08, 0.06),
                   (0, y0 + 0.02, 2.52, 0)], n=14, radial=lambda t: 1 + 0.05 * math.cos(6 * t))  # a moss beard
    pair(ball, 'Trim', at=(0.85, 0.05, 4.35), r=(0.5, 0.45, 0.32), mirror=['at'])            # cypress shoulders
    for s in (1, -1):
        limb('Body', (s * 0.75, 0, 4.0), (s * 1.4, -0.1, 4.35), 0.24, 0.2, n=8)              # branch arms, raised
        limb('Body', (s * 1.4, -0.1, 4.35), (s * 1.7, -0.4, 3.55), 0.2, 0.17, n=8)
        ball('Body', (s * 1.72, -0.45, 3.45), 0.18, n=10, k=5)
        for dx, dz in ((0.12, -0.3), (0, -0.35), (-0.12, -0.3)):
            limb('Body', (s * 1.72, -0.47, 3.4), (s * (1.72 + dx), -0.57, 3.4 + dz), 0.07, 0.05, n=5)  # twig fingers
        for t, ln in ((0.3, 0.75), (0.6, 0.95), (0.9, 0.7)):                                 # moss hanging off
            a = Vector((s * 0.75, 0, 4.0)).lerp(Vector((s * 1.4, -0.1, 4.35)), t)
            limb('Skin', a, a + Vector((s * 0.03, 0.02, -ln)), 0.1, 0.04, n=5)
    tube('Body', [(0.52 * math.cos(t), 0.47 * math.sin(t), 5.05) for t in
                  (2 * math.pi * i / 12 for i in range(12))], 0.08, n=6, closed=True, up=(0, 0, 1))  # crown band
    for i in range(8):
        t = math.radians(22.5 + 45 * i)
        h = 5.5 if i % 2 else 5.3
        limb('Body', (0.52 * math.cos(t), 0.47 * math.sin(t), 5.05),
             (0.8 * math.cos(t), 0.72 * math.sin(t), h), 0.07, 0.04, n=5)                    # splayed crown twigs
        ball('Glow_Warm_1', (0.86 * math.cos(t), 0.78 * math.sin(t), h + 0.08), 0.1, n=6, k=3)  # a firefly on each
    for c in ((0.35, -0.3, 5.95), (-0.45, 0.1, 6.05), (0.05, 0.4, 6.1)):
        ball('Glow_Warm_1', c, 0.07, n=6, k=3)                                               # and a few loose higher
    marker('Hand', (-1.72, -0.47, 3.4))
    marker('Nameplate', (0, 0, 6.8))
    return finished('Biped, a bald-cypress king: a fluted bark trunk on root legs, a kind carved face, a moss '
                    'beard, moss hanging off its raised branch arms, cypress-green shoulders, twig hands, a splayed '
                    'twig crown with a firefly on each point and a few loose (Glow_Warm_1, quirk "wears a crown of fireflies").')


def moon_heron():
    k.begin('MoonHeron', SET, {'Dark': INK, 'Light': WHITE, 'Skin': (150, 170, 220), 'Trim': (245, 200, 110),
                               'Glow_Eyes_1': (170, 220, 255), 'Glow_Eyes_2': (170, 220, 255),
                               'Glow_Cold_1': (215, 235, 255)})
    for s in (1, -1):
        limb('Skin', (s * 0.35, 0.1, 0.15), (s * 0.35, 0.15, 2.45), 0.13, 0.15, n=8)         # long legs
        for dx, dy in ((0.18, -0.5), (0, -0.55), (0, 0.45)):
            limb('Skin', (s * 0.35, 0.1, 0.07), (s * (0.35 + dx), dy, 0.07), 0.07, n=6)       # toes
    BR = (0.8, 1.2, 0.9)
    ball('Body', (0, 0.2, 3.15), BR, n=16, k=8, rot=(-12, 0, 0))                             # body
    ball('Skin', (0, 1.45, 2.75), (0.35, 0.55, 0.12), rot=(-25, 0, 0), n=10, k=5)            # tail plumes
    pair(ball, 'Body', at=(0.72, 0.3, 3.25), r=(0.22, 1.05, 0.65), rot=(-12, 0, 0), mirror=['at'])  # folded wings
    pair(ball, 'Skin', at=(0.72, 1.25, 2.95), r=(0.18, 0.4, 0.3), rot=(-20, 0, 0), mirror=['at'])  # wing tips
    tube('Body', [(0, -0.55, 3.6), (0, -0.8, 4.3), (0, -0.6, 4.95), (0, -0.35, 5.45), (0, -0.45, 5.95)],
         [0.42, 0.32, 0.27, 0.25, 0.25], n=12)                                               # the S of the neck
    HC, HR = (0, -0.6, 6.2), (0.4, 0.45, 0.4)
    ball('Body', HC, HR, n=14, k=7)
    limb('Trim', (0, -0.95, 6.12), (0, -2.15, 5.95), 0.12, 0.05, n=10)                      # a blunt gold beak
    eyes((0.2, on_ball(HC, HR, 0.2, 6.36, out=-0.08).y, 6.36), 0.15)
    tube('Skin', [(0, -0.45, 6.5), (0, -0.05, 6.75), (0, 0.45, 6.75), (0, 0.85, 6.55)], [0.08, 0.07, 0.06, 0.05],
         n=8)                                                                                # crest plumes
    tube('Skin', [(0, -0.4, 6.4), (0, 0.0, 6.55), (0, 0.45, 6.45), (0, 0.75, 6.25)], 0.06, n=8)
    for c in ((0, 0.9, 6.52), (0, 0.8, 6.22)):
        ball('Skin', c, 0.08, n=8, k=4)
    N = 24
    cres = [(0.8 * math.cos(math.radians(35 + 290 * i / N)), 0.3, 6.35 + 0.8 * math.sin(math.radians(35 + 290 * i / N)))
            for i in range(N + 1)]
    tube('Glow_Cold_1', cres, [0.03 + 0.2 * math.sin(math.pi * i / N) for i in range(N + 1)], n=8,
         up=(0, 1, 0))                                                                       # the crescent moon
    marker('Hand', (-0.8, -0.5, 3.4))
    marker('Nameplate', (0, 0, 7.8))
    return finished('Biped, a tall moon-white heron: long periwinkle legs, an S-curved neck, a blunt gold beak, '
                    'crest plumes, periwinkle wing tips and tail, a glowing crescent moon behind its head '
                    '(Glow_Cold_1; quirk "its call calms the whole street"). Hand is the right wing\'s front.')


BUILDERS = {'BogFrog': bog_frog, 'Mossling': mossling, 'FireflySprite': firefly_sprite, 'MudPuppy': mud_puppy,
            'GatorGhoul': gator_ghoul, 'WillOWisp': will_o_wisp, 'SwampHag': swamp_hag,
            'BayouHydra': bayou_hydra, 'CypressKing': cypress_king, 'MoonHeron': moon_heron}


# --- The review pictures (this set's; the kit's own sheet is the Workbench colour one) ----------
OFFSETS, COLS, ROW_H = 5.0, 5, 9.0     # finish_set's layout: a person at x = -OFFSETS on each row


def _camera(name, x0, x1, z0, z1, yaw, pitch, res):
    scene = bpy.context.scene
    cam = bpy.data.cameras.new(name)
    cam.type = 'ORTHO'
    cam.ortho_scale = max(x1 - x0, (z1 - z0) * res[0] / res[1]) * 1.04
    ob = bpy.data.objects.new(name, cam)
    scene.collection.objects.link(ob)
    yaw, pitch = math.radians(yaw), math.radians(pitch)
    d = Vector((math.sin(yaw) * math.cos(pitch), -math.cos(yaw) * math.cos(pitch), math.sin(pitch)))
    ob.location = Vector(((x0 + x1) / 2, 0, (z0 + z1) / 2)) + d * 80
    ob.rotation_euler = (-d).to_track_quat('-Z', 'Y').to_euler()
    scene.camera = ob
    scene.render.resolution_x, scene.render.resolution_y = res
    scene.render.resolution_percentage = 100


def _shoot(path):
    bpy.context.scene.render.filepath = str(path)
    bpy.ops.render.render(write_still=True)
    print(f'render: {path}', flush=True)


def silhouettes(out, rows):
    """Grey, shaded, no colour: the shapes alone beside the person."""
    scene = bpy.context.scene
    scene.render.engine = 'BLENDER_WORKBENCH'
    sh = scene.display.shading
    sh.light, sh.color_type, sh.single_color = 'STUDIO', 'SINGLE', (0.55, 0.55, 0.57)
    sh.show_cavity, sh.show_object_outline = False, False
    scene.world = scene.world or bpy.data.worlds.new('W')
    scene.world.color = (0.9, 0.9, 0.92)
    _camera('Grey', -OFFSETS - 1.5, (COLS - 1) * OFFSETS + 2.0, -(rows - 1) * ROW_H - 0.6, 7.9, 0, 4, (1200, 900))
    _shoot(out / 'review' / 'silhouettes.png')


def cycles_sheets(out, rows):
    """The finished pictures: Cycles on the CPU (4 threads; a GPU hang once lost a Studio playtest),
    the glows lit, a floor under each row, the 5-stud person at each row's start."""
    scene = bpy.context.scene
    scene.render.engine = 'CYCLES'
    scene.cycles.device = 'CPU'
    scene.cycles.samples = 40
    scene.cycles.use_denoising = True
    scene.render.threads_mode = 'FIXED'
    scene.render.threads = 4
    scene.render.film_transparent = False
    scene.view_settings.view_transform = 'AgX'
    world = bpy.data.worlds.new('Dusk')
    world.use_nodes = True
    world.node_tree.nodes['Background'].inputs['Color'].default_value = (0.2, 0.22, 0.3, 1)
    world.node_tree.nodes['Background'].inputs['Strength'].default_value = 1.0
    scene.world = world
    for mat in bpy.data.materials:
        if '_Glow_' in mat.name and mat.use_nodes:
            bsdf = mat.node_tree.nodes.get('Principled BSDF')
            bsdf.inputs['Emission Color'].default_value = bsdf.inputs['Base Color'].default_value
            bsdf.inputs['Emission Strength'].default_value = 3.5
    sun = bpy.data.objects.new('Sun', bpy.data.lights.new('Sun', 'SUN'))
    sun.data.energy = 3.5
    sun.data.angle = math.radians(8)
    sun.rotation_euler = (math.radians(50), math.radians(-20), math.radians(-30))
    scene.collection.objects.link(sun)
    fm = bpy.data.materials.new('Floor')
    fm.use_nodes = True
    fm.node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value = (0.16, 0.2, 0.15, 1)
    for r in range(rows):
        bpy.ops.mesh.primitive_plane_add(size=1, location=((COLS - 1) * OFFSETS / 2 - 1, 0, -r * ROW_H))
        fl = bpy.context.active_object
        fl.scale = ((COLS + 1) * OFFSETS + 4, 4.4, 1)
        fl.data.materials.append(fm)
    x0, x1 = -OFFSETS - 1.5, (COLS - 1) * OFFSETS + 2.2
    for r in range(rows):
        _camera(f'Row{r + 1}', x0, x1, -r * ROW_H - 0.5, -r * ROW_H + 7.8, -18, 8, (1600, 560))
        _shoot(out / 'review' / f'final_front_row{r + 1}.png')
    _camera('Back', x0, x1, -(rows - 1) * ROW_H - 0.6, 7.9, 162, 8, (1400, 900))
    _shoot(out / 'review' / 'final_back.png')
    _camera('Game', x0, x1, -(rows - 1) * ROW_H - 2.5, 8.2, -25, 38, (1400, 900))
    _shoot(out / 'review' / 'final_game_camera.png')


if __name__ == '__main__':
    names = [n for n in ORDER if not ONLY or n in ONLY]
    out = k.start_set(SET)
    for n in names:
        BUILDERS[n]()
    k.finish_set(SET, offsets=OFFSETS, cols=COLS)
    rows = (len(names) + COLS - 1) // COLS
    if not k.NORENDER:
        silhouettes(out, rows)
        if FINAL:
            cycles_sheets(out, rows)
    k.validate(SET, names)
