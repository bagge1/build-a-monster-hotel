"""Location 2's seven monsters, the Frostfang Lodge family (GDD Appendix A.6), first drafts.

The same "cozy creepy" toys as the Haunted Manor set (GDD §12): chunky rounded
shapes, big glowing eyes with dark pupils and a white glint, rosy cheeks on the
soft ones, soft colours from Species.luau's `look`, nothing sharp. Icy here:
crystal horns are blunt and faceted, the troll's tusks are round, the glows are
cold blues and aurora greens. Each species is its shapes and a call to
monster_kit.finish(), which refuses anything breaking MODELS.md, "Monsters and
street NPCs". Static meshes: no rig, no Animations folder (the client bobs them).

Frame: Blender -Y is the front, +Z up, +X the monster's left (monster_kit).
Run headless only:
    blender -b --python-exit-code 1 -P tools/build_monsters_l2.py [-- norender] [-- only Yeti,IceImp]  (one '--', then the words)
"""
import math
import sys

from pathlib import Path
from mathutils import Matrix, Vector

sys.path.insert(0, str(Path(__file__).resolve().parent))
import monster_kit as k  # noqa: E402
from monster_kit import ball, limb, lathe, rings, box, arc_shell, pair, eyes, marker, on_ball, front_y, tube  # noqa: E402

SET = 'monsters/frostfang_lodge'
ORDER = ['SnowballSprite', 'IceImp', 'FrostTroll', 'Yeti', 'SnowWitch', 'IceWyrm', 'AuroraSpirit']
ONLY = next((a.split(',') for a in k.ARGS[k.ARGS.index('only') + 1:k.ARGS.index('only') + 2]), None) \
    if 'only' in k.ARGS else None

WHITE = (255, 255, 255)
BLUSH = (255, 150, 180)
INK = (45, 32, 60)          # the game's dark: a deep plum, never pure black (as Haunted Manor)
ICE = (215, 242, 255)       # pale ice: crystal horns, frosty mitts, bellies


def cheeks(at_l, r=(0.18, 0.06, 0.11), part='Trim'):
    pair(ball, part, at=at_l, r=r, mirror=['at'])


def snowball_sprite():
    gl = (120, 205, 255)
    k.begin('SnowballSprite', SET, {'Dark': INK, 'Light': WHITE, 'Trim': BLUSH, 'Skin': (60, 175, 185),
                                    'Glow_Eyes_1': gl, 'Glow_Eyes_2': gl})
    S = [(0, 0), (0.04, 0.8), (0.2, 1.08), (0.55, 1.3), (1.1, 1.38), (1.7, 1.28), (2.15, 1.0), (2.45, 0.62),
         (2.62, 0)]
    rings('Body', [(0, 0, z, r) for z, r in S], n=24, radial=lambda t: 1 + 0.035 * math.cos(7 * t))   # the snowball
    for t, z, r in ((150, 0.95, 0.32), (35, 1.55, 0.26), (100, 0.6, 0.3)):                     # packed-snow lumps
        a = math.radians(t)
        ball('Body', (1.2 * math.cos(a), 1.2 * math.sin(a), z), r, n=10, k=5)
    lathe('Skin', [(0, 0.9), (0.18, 0.84), (0.38, 0.66), (0.52, 0.4), (0.6, 0)], at=(0, 0, 2.18), n=20)  # beanie
    lathe('Skin', [(-0.1, 1.03), (0.1, 1.03)], at=(0, 0, 2.3), n=20)                          # its cuff
    ball('Trim', (0.05, 0, 2.86), 0.2, n=10, k=5)                                              # pompom
    eyes((0.42, front_y(S, 1.45, 0.42, out=-0.12), 1.45), 0.36)
    ball('Dark', (0, front_y(S, 0.98, 0, out=0.0), 0.98), (0.16, 0.07, 0.09))                 # little mouth
    cheeks((0.82, front_y(S, 1.12, 0.82, out=0.0), 1.12))
    pair(ball, 'Body', at=(1.35, -0.1, 1.05), r=(0.32, 0.26, 0.22), rot=(0, -25, 0), mirror=['at'])  # mitten nubs
    marker('Hand', (-1.55, -0.1, 1.05))
    marker('Nameplate', (0, 0, 3.6))
    return k.finish('Blob, a round snowball (quirk "rolls instead of walking"): a teal beanie and a pink pompom. '
                    'Hand is the right mitten nub.')


def ice_imp():
    gl = (255, 225, 110)
    k.begin('IceImp', SET, {'Dark': INK, 'Light': WHITE, 'Skin': ICE, 'Trim': (150, 90, 210),
                            'Glow_Eyes_1': gl, 'Glow_Eyes_2': gl})
    pair(ball, 'Body', at=(0.24, -0.1, 0.12), r=(0.2, 0.3, 0.12), mirror=['at'])               # feet
    for s in (1, -1):
        limb('Body', (s * 0.22, 0, 0.2), (s * 0.22, 0, 0.75), 0.13)
    T = [(0.6, 0), (0.65, 0.45), (1.0, 0.55), (1.4, 0.52), (1.75, 0.4), (1.9, 0)]
    lathe('Body', T, sy=0.85)
    ball('Skin', (0, front_y(T, 1.15, 0, sy=0.85, out=-0.08), 1.15), (0.32, 0.12, 0.36))      # frosty belly
    lathe('Trim', [(-0.1, 0.5), (0.1, 0.46)], at=(0, 0, 1.78), sy=0.9)                         # scarf
    box('Trim', (0.25, -0.5, 1.45), (0.2, 0.07, 0.55), bevel=0.02, rot=(8, 0, -8))            # its end
    HC, HR = (0, 0, 2.55), (0.85, 0.78, 0.78)
    ball('Body', HC, HR, n=18, k=9)
    pair(lathe, 'Body', [(0, 0.16), (0.42, 0)], at=(0.8, 0.05, 2.6), n=8, rot=(0, 70, 0), mirror=['at'])  # ears
    pair(lathe, 'Skin', [(0, 0.17), (0.25, 0.13), (0.5, 0)], at=(0.38, 0.05, 3.1), n=6, rot=(0, 22, 0),
         mirror=['at'])                                                                        # ice-crystal horns
    eyes((0.32, on_ball(HC, HR, 0.32, 2.62, out=-0.12).y, 2.62), 0.24)
    pair(ball, 'Dark', at=(0.33, on_ball(HC, HR, 0.33, 2.95, out=-0.02).y, 2.95), r=(0.17, 0.05, 0.045),
         rot=(0, -20, 0), mirror=['at'])                                                       # cheeky brows
    mo = on_ball(HC, HR, 0, 2.22, out=-0.03)
    ball('Dark', mo, (0.3, 0.06, 0.09), rot=(0, -8, 0))                                        # lopsided grin
    box('Light', (0.1, mo.y - 0.04, 2.27), (0.09, 0.05, 0.09), bevel=0.015)                    # one tooth
    limb('Body', (0.45, 0, 1.7), (0.85, -0.1, 2.1), 0.11)                                      # left arm waving
    ball('Skin', (0.92, -0.12, 2.2), 0.2)                                                      # frosty mitt
    limb('Body', (-0.45, 0, 1.7), (-0.7, -0.2, 1.25), 0.11)
    ball('Skin', (-0.74, -0.24, 1.15), 0.2)
    limb('Body', (0, 0.4, 0.9), (0, 0.95, 1.3), 0.08, 0.06)                                    # tail
    lathe('Skin', [(0, 0.13), (0.28, 0)], at=(0, 0.98, 1.32), n=6, rot=(-40, 0, 0))           # its crystal tip
    marker('Hand', (-0.74, -0.24, 1.15))
    marker('Nameplate', (0, 0, 4.1))
    return k.finish('Biped; blunt ice-crystal horns, big frosty mitts (quirk "leaves frost handprints"), '
                    'a purple scarf, a lopsided one-tooth grin.')


def frost_troll():
    gl = (160, 235, 255)
    k.begin('FrostTroll', SET, {'Dark': INK, 'Light': (240, 248, 255), 'Skin': (185, 205, 218),
                                'Trim': (240, 200, 90), 'Glow_Eyes_1': gl, 'Glow_Eyes_2': gl})
    pair(ball, 'Body', at=(0.75, -0.25, 0.3), r=(0.55, 0.75, 0.3), mirror=['at'])             # big feet
    for s in (1, -1):
        limb('Body', (s * 0.72, 0, 0.45), (s * 0.75, 0, 1.7), 0.45, 0.5)
    T = [(1.3, 0), (1.35, 1.2), (2.2, 1.65), (3.3, 1.8), (4.4, 1.7), (5.2, 1.35), (5.65, 0.8), (5.8, 0)]
    lathe('Body', T, n=20, sy=0.8)
    ball('Skin', (0, front_y(T, 3.0, 0, sy=0.8, out=-0.3), 3.0), (1.0, 0.36, 1.2))             # pale belly
    ball('Trim', (0.6, front_y(T, 4.15, 0.6, sy=0.8, out=0.0), 4.15), (0.2, 0.07, 0.2), n=12)  # Security badge
    HC, HR = (0, -0.55, 5.85), (0.95, 0.85, 0.8)
    ball('Body', HC, HR, n=18, k=9)
    ball('Light', (0, -0.5, 6.55), (0.8, 0.7, 0.28))                                           # snow cap
    pair(ball, 'Light', at=(1.15, 0.1, 5.25), r=(0.55, 0.5, 0.25), mirror=['at'])              # snowy shoulders
    ex, ez = 0.36, 5.95
    ey = on_ball(HC, HR, ex, ez, out=-0.1).y
    eyes((ex, ey, ez), 0.2)
    for s in (1, -1):                                                                          # heavy sleepy lids
        ball('Body', (s * ex, ey - 0.01, ez + 0.1), (0.23, 0.26, 0.14), n=12, k=6)
    ball('Skin', (0, on_ball(HC, HR, 0, 5.65).y - 0.15, 5.65), (0.32, 0.28, 0.26))             # big round nose
    mo = on_ball(HC, HR, 0, 5.35, out=-0.03)
    ball('Dark', mo, (0.42, 0.06, 0.08))
    for s in (1, -1):                                                                          # round tusks
        limb('Light', (s * 0.28, mo.y - 0.02, 5.3), (s * 0.3, mo.y - 0.04, 5.5), 0.07, 0.045, n=8)
    for s in (1, -1):
        limb('Body', (s * 1.5, 0, 4.8), (s * 1.85, -0.2, 3.2), 0.42, 0.38)
        limb('Body', (s * 1.85, -0.2, 3.2), (s * 1.8, -0.45, 2.0), 0.38, 0.42)
        ball('Body', (s * 1.8, -0.5, 1.6), (0.55, 0.55, 0.5))                                  # fists
    marker('Hand', (-1.8, -0.5, 1.6))
    marker('Nameplate', (0, -0.2, 7.4))
    return k.finish('Biped, a big slate-blue troll with snow on its head and shoulders, half-shut sleepy eyes '
                    '(quirk "sleeps standing up"), round tusks, a gold Security badge.')


def yeti():
    face, gl = (130, 185, 235), (110, 200, 255)
    k.begin('Yeti', SET, {'Dark': INK, 'Light': WHITE, 'Skin': face, 'Trim': BLUSH,
                          'Glow_Eyes_1': gl, 'Glow_Eyes_2': gl})
    pair(ball, 'Body', at=(0.75, -0.2, 0.35), r=(0.6, 0.85, 0.35), mirror=['at'])             # big feet
    for s in (1, -1):
        limb('Body', (s * 0.75, 0, 0.5), (s * 0.75, 0, 1.6), 0.5)
        for c in (-0.25, 0, 0.25):                                                             # blue toe pads
            ball('Skin', (s * 0.75 + c, -0.98, 0.2), (0.12, 0.08, 0.1), n=8, k=4)
    T = [(1.2, 0), (1.25, 1.25), (2.0, 1.7), (3.2, 1.85), (4.4, 1.75), (5.3, 1.45), (5.9, 0.9), (6.05, 0)]
    rings('Body', [(0, 0, z, r, r * 0.82) for z, r in T], n=24, radial=lambda t: 1 + 0.035 * math.cos(12 * t))
    HC, HR = (0, -0.25, 6.25), (1.05, 0.95, 0.95)
    ball('Body', HC, HR, n=20, k=10, radial=lambda t: 1 + 0.03 * math.cos(10 * t))
    lathe('Body', [(0, 0.3), (0.25, 0.2), (0.45, 0)], at=(0.05, -0.2, 7.05), n=10, rot=(0, -20, 0))  # the tuft
    FC, FR = (0, -0.9, 6.1), (0.78, 0.4, 0.68)
    ball('Skin', FC, FR, n=18, k=9)                                                            # blue face
    eyes((0.32, on_ball(FC, FR, 0.32, 6.3, out=-0.1).y, 6.3), 0.22)
    ball('Dark', (0, on_ball(FC, FR, 0, 6.05).y - 0.02, 6.05), (0.12, 0.07, 0.08), n=10, k=5)  # nose
    mo = on_ball(FC, FR, 0, 5.78, out=-0.03)
    ball('Dark', mo, (0.26, 0.06, 0.09))
    for s in (1, -1):                                                                          # two tiny fangs
        lathe('Light', [(-0.12, 0), (0, 0.05)], at=(s * 0.12, mo.y - 0.02, 5.82), n=6)
    cheeks((0.55, on_ball(FC, FR, 0.55, 5.95).y, 5.95), r=(0.15, 0.06, 0.1))
    for s in (1, -1):
        limb('Body', (s * 1.55, 0, 5.1), (s * 1.95, -0.15, 3.6), 0.45, 0.42)
        limb('Body', (s * 1.95, -0.15, 3.6), (s * 1.85, -0.4, 2.5), 0.42, 0.4)
        ball('Body', (s * 1.85, -0.45, 2.2), (0.48, 0.48, 0.5))
        ball('Skin', (s * 1.85, -0.86, 2.15), (0.3, 0.12, 0.3))                               # blue palms
    marker('Hand', (-1.85, -0.45, 2.2))
    marker('Nameplate', (0, 0, 8.1))
    return k.finish('Biped, a big fluffy white yeti (fur ripples), a blue face, palms and toe pads, '
                    'pink cheeks, two tiny fangs; gentle, for Housekeeping.')


def snow_witch():
    gl = (150, 235, 255)
    k.begin('SnowWitch', SET, {'Dark': INK, 'Light': WHITE, 'Skin': (232, 238, 255), 'Trim': (140, 105, 215),
                               'Glow_Eyes_1': gl, 'Glow_Eyes_2': gl, 'Glow_Cold_1': (170, 240, 255)})
    pair(ball, 'Dark', at=(0.25, -0.15, 0.12), r=(0.18, 0.3, 0.12), mirror=['at'])             # boots
    D = [(0.15, 0), (0.15, 1.25), (0.55, 1.12), (1.3, 0.88), (2.1, 0.62), (2.75, 0.5), (3.05, 0.36), (3.15, 0)]
    lathe('Body', D, n=24, wave={1: lambda t: 0.08 * math.sin(8 * t)})                         # the gown
    lathe('Light', [(-0.1, 1.2), (0, 1.3), (0.1, 1.2)], at=(0, 0, 0.32), n=24)                 # fur hem
    lathe('Light', [(-0.18, 0.55), (-0.05, 0.78), (0.12, 0.72), (0.22, 0.4)], at=(0, 0, 2.85), n=20)  # fur capelet
    HC, HR = (0, 0, 3.75), (0.7, 0.66, 0.7)
    ball('Skin', HC, HR, n=18, k=9)
    ball('Light', (0, 0.25, 3.75), (0.76, 0.55, 0.74))                                         # silver hair
    pair(ball, 'Light', at=(0.6, 0.05, 3.45), r=(0.24, 0.3, 0.45), mirror=['at'])
    limb('Light', (0, 0.45, 3.7), (0, 0.6, 2.6), 0.45, 0.25)
    rings('Trim', [(0, 0, 4.12, 0.72), (0.04, 0, 4.55, 0.6), (0.12, 0, 4.95, 0.45), (0.28, 0, 5.28, 0.3),
                   (0.52, 0, 5.45, 0.16), (0.8, 0, 5.38, 0)], n=16)                            # knitted stocking cap
    lathe('Light', [(-0.1, 0.76), (0.1, 0.76)], at=(0, 0, 4.2), n=20)                          # its fur brim
    ball('Light', (0.88, 0, 5.25), 0.2, n=10, k=5)                                             # pompom
    eyes((0.25, on_ball(HC, HR, 0.25, 3.78, out=-0.1).y, 3.78), 0.19, rr=(0.19, 0.14, 0.23))
    ball('Dark', on_ball(HC, HR, 0, 3.38, out=-0.03), (0.14, 0.05, 0.05))
    for s in (1, -1):
        limb('Body', (s * 0.42, 0, 2.85), (s * 0.5, -0.45, 2.3), 0.14, 0.2)                     # bell sleeves
        ball('Skin', (s * 0.4, -0.64, 2.27), 0.14)
    limb('Light', (0.38, -0.7, 2.25), (-0.05, -0.85, 2.75), 0.035, n=6)                        # knitting needles
    limb('Light', (-0.38, -0.7, 2.25), (0.05, -0.86, 2.75), 0.035, n=6)
    box('Trim', (0, -0.8, 2.0), (0.45, 0.08, 0.5), bevel=0.03)                                 # the knitting
    lathe('Glow_Cold_1', [(-0.45, 0), (0, 0.1)], at=(0, -0.8, 1.8), n=8)                       # a knitted icicle
    marker('Hand', (-0.4, -0.64, 2.27))
    marker('Nameplate', (0, 0, 6.0))
    return k.finish('Biped; pale-blue gown with a fur hem and capelet, silver hair, a violet knitted cap, '
                    'knitting a glowing icicle (quirk "knits icicles", Glow_Cold_1).')


def _bezier(p0, p1, p2, p3, n):
    out = []
    for i in range(1, n + 1):
        t = i / n
        a = (1 - t) ** 3, 3 * (1 - t) ** 2 * t, 3 * (1 - t) * t * t, t ** 3
        out.append(sum((Vector(p) * w for p, w in zip((p0, p1, p2, p3), a)), Vector()))
    return out


def ice_wyrm():
    gl = (170, 245, 255)
    k.begin('IceWyrm', SET, {'Dark': INK, 'Light': (240, 250, 255), 'Skin': (200, 238, 255), 'Trim': BLUSH,
                             'Glow_Eyes_1': gl, 'Glow_Eyes_2': gl})
    # The coil: from the tail tip (curled up, front right) round 1.55 turns, the
    # second turn resting on the first, then the neck rising up the back to the head.
    pts, rad = [], []
    N = 44
    for i in range(N + 1):
        s = i / N
        th = math.radians(-120) - s * 2 * math.pi * 1.55
        R = 1.65 - 0.65 * s
        r = 0.1 + 0.52 * min(1.0, s / 0.45)
        rise = 0.95 * (lambda u: u * u * (3 - 2 * u))(min(1.0, max(0.0, (s - 0.6) / 0.4)))
        curl = max(0.0, 0.1 - s) * 6.0                                                         # the tail tip lifts
        pts.append(Vector((R * math.cos(th), R * math.sin(th), r + rise + curl)))
        rad.append(r)
    end = pts[-1]
    th = math.radians(-120) - 2 * math.pi * 1.55
    tang = Vector((math.sin(th), -math.cos(th), 0))
    neck = _bezier(end, end + tang * 0.9 + Vector((0, 0, 0.7)), (0, 0.45, 3.3), (0, -0.2, 4.35), 9)
    pts += neck
    rad += [0.62 - 0.17 * (i + 1) / len(neck) for i in range(len(neck))]
    coil = tube('Body', pts, rad, n=12)
    # Centre the floor contacts on the origin (MODELS.md: origin between the "feet").
    low = [coil.matrix_world @ v.co for v in coil.data.vertices if v.co.z < 0.08]
    c = Vector(((min(p.x for p in low) + max(p.x for p in low)) / 2, (min(p.y for p in low) + max(p.y for p in low)) / 2, 0))
    coil.data.transform(Matrix.Translation(-c))
    pts = [p - c for p in pts]
    HC, HR = (0, -0.35, 4.7), (0.85, 0.78, 0.72)
    ball('Body', HC, HR, n=18, k=9)
    SC, SR = (0, -1.0, 4.45), (0.55, 0.5, 0.4)
    ball('Skin', SC, SR, n=14, k=7)                                                            # pale snout
    for s in (1, -1):
        ball('Dark', on_ball(SC, SR, s * 0.17, 4.6, out=-0.02), (0.06, 0.04, 0.05), n=8, k=4)   # nostrils
    ball('Dark', on_ball(SC, SR, 0, 4.3, out=-0.03), (0.25, 0.05, 0.05))                       # smile
    eyes((0.36, on_ball(HC, HR, 0.36, 4.85, out=-0.1).y, 4.85), 0.24)
    cheeks((0.58, on_ball(HC, HR, 0.58, 4.55).y, 4.55), r=(0.16, 0.06, 0.1))
    for s in (1, -1):                                                                          # round ice horns
        limb('Light', (s * 0.4, 0.0, 5.2), (s * 0.62, 0.45, 5.85), 0.13, 0.07, n=8)
    ball('Skin', (0, 0.42, 5.25), (0.07, 0.35, 0.3), rot=(30, 0, 0), n=10, k=5)               # head crest
    near = lambda z: min(range(len(pts)), key=lambda i: abs(pts[i].z - z) + (0 if i > N else 9))
    for z in (2.6, 3.2, 3.8):                                                                  # back fins
        i = near(z)
        ball('Skin', pts[i] + Vector((0, rad[i] * 0.9, 0)), (0.07, 0.3, 0.26), n=10, k=5)
    i = near(3.0)                                                                              # pale belly
    ball('Skin', pts[i] + Vector((0, -rad[i] * 0.65, 0)), (rad[i] * 0.75, rad[i] * 0.5, 0.7), n=12, k=6)
    i = near(3.3)
    for s in (1, -1):                                                                          # tiny wing nubs
        ball('Skin', pts[i] + Vector((s * (rad[i] + 0.12), 0.1, 0)), (0.32, 0.08, 0.2), rot=(0, s * -25, 0), n=10, k=5)
    marker('Hand', tuple(pts[0]))                                                              # the curled tail tip
    marker('Nameplate', (0, -0.2, 6.4))
    return k.finish('Serpent, a chubby ice wyrm coiled 1.5 turns on the floor (quirk "coils around the desk"), '
                    'round horns, pale snout and belly, back fins, tiny wing nubs. Hand is the curled tail tip.',
                    # The tail: the last third of a turn, from the tip at the front round the -X side.
                    rig=dict(neck_base=(0.4, 0.6, 1.6), head_base=(0, -0.2, 4.3), tail_base=(-1.58, 0.43, 0.26),
                             tail_mid=(-1.57, -0.6, 0.37), tail_tip=(-0.91, -1.43, 0.7), radius={'Coil': 1.2}))


def aurora_spirit():
    gl = (225, 255, 245)
    k.begin('AuroraSpirit', SET, {'Dark': INK, 'Light': WHITE, 'Skin': (225, 255, 240), 'Trim': (80, 200, 200),
                                  'Glow_Eyes_1': gl, 'Glow_Eyes_2': gl, 'Glow_Magic_1': (255, 240, 170),
                                  'Glow_Cold_1': (90, 230, 235), 'Glow_Magic_2': (175, 125, 255),
                                  'Glow_Magic_3': (170, 255, 120)})
    G = [(0.85, 0), (0.55, 1.15), (1.1, 1.02), (2.0, 0.86), (3.0, 0.7), (3.9, 0.6), (4.5, 0.62), (4.95, 0.55),
         (5.2, 0)]
    lathe('Body', G, n=24, wave={1: lambda t: 0.18 * math.sin(5 * t)})                         # the wisp
    limb('Skin', (0, 0, 5.0), (0, 0, 5.4), 0.18)
    HC, HR = (0, 0, 5.9), (0.62, 0.58, 0.66)
    ball('Skin', HC, HR, n=18, k=9)
    ball('Trim', (0, 0.3, 5.95), (0.72, 0.55, 0.75), n=16, k=8)                                # teal hair
    limb('Trim', (0, 0.55, 6.0), (0, 1.15, 3.9), 0.5, 0.18)
    pair(ball, 'Trim', at=(0.55, 0.05, 5.55), r=(0.2, 0.25, 0.4), mirror=['at'])
    halo = [(0.42 * math.cos(2 * math.pi * i / 20), 0.42 * math.sin(2 * math.pi * i / 20), 6.82) for i in range(20)]
    tube('Glow_Magic_1', halo, 0.055, n=8, closed=True, up=(0, 0, 1))                          # a floating halo
    eyes((0.22, on_ball(HC, HR, 0.22, 5.95, out=-0.09).y, 5.95), 0.16, rr=(0.16, 0.12, 0.2))
    ball('Dark', on_ball(HC, HR, 0, 5.58, out=-0.03), (0.12, 0.05, 0.04))
    limb('Body', (0.48, 0, 4.85), (0.85, -0.2, 5.15), 0.13)                                    # left arm, painting
    limb('Body', (0.85, -0.2, 5.15), (1.0, -0.3, 5.6), 0.11)
    ball('Skin', (1.05, -0.33, 5.7), 0.13)
    limb('Light', (1.0, -0.34, 5.55), (1.25, -0.45, 6.3), 0.045, n=6)                          # the paintbrush
    limb('Glow_Magic_3', (1.25, -0.45, 6.3), (1.31, -0.48, 6.52), 0.09, 0.03, n=8)            # its green tip
    limb('Body', (-0.48, 0, 4.85), (-0.95, -0.3, 4.35), 0.13)                                  # right arm, open
    ball('Skin', (-1.0, -0.4, 4.25), 0.13)
    arc_shell('Glow_Cold_1', [(1.4, 1.25), (2.4, 1.1), (3.4, 0.95), (4.4, 0.85), (4.9, 0.72)], 25, 155, 0.06)
    arc_shell('Glow_Magic_2', [(2.2, 1.3), (3.0, 1.18), (3.8, 1.06), (4.6, 0.95)], 45, 135, 0.06)  # aurora curtains
    marker('Hand', (-1.0, -0.4, 4.25))
    marker('Nameplate', (0, 0, 7.4))
    return k.finish('Float: a serene mint spirit with teal hair and a gold halo, aurora curtains (teal and violet) '
                    'hanging from its back, a paintbrush with a green glowing tip (quirk "paints the sky green").',
                    rig=dict(neck_z=5.0, shoulder=(0.48, 0, 4.85), hand_l=(1.0, -0.3, 5.6)))


BUILDERS = {'SnowballSprite': snowball_sprite, 'IceImp': ice_imp, 'FrostTroll': frost_troll, 'Yeti': yeti,
            'SnowWitch': snow_witch, 'IceWyrm': ice_wyrm, 'AuroraSpirit': aurora_spirit}

if __name__ == '__main__':
    names = [n for n in ORDER if not ONLY or n in ONLY]
    k.start_set(SET)
    for n in names:
        BUILDERS[n]()
    k.finish_set(SET, offsets=5.6, cols=4)
    k.validate(SET, names)
