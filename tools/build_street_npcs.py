"""The street's two NPC models, first drafts: `Hunter` and `NightBus`
(MODELS.md, "Hunters (`Hunter`) and the bus (`NightBus`)"; GDD §8.1, §4.3).

Built on monster_kit like a monster (begin, shapes, finish), with the street
targets of monster_kit.NPCS: a Hunter is a 5-stud person (HunterRenderer's
blockout, Root 2 x 5 x 2) carrying `Nameplate`; the NightBus is 24 long, 8 wide
and 9 tall (BusRenderer's blockout), authored facing Roblox +X (Blender -X), its
Root the size of the bus, a `Door` marker on the floor outside its door (the
right side, Roblox +Z, toward the stop) and `Glow_Warm_<n>` windows and lamps.
Same look as the monsters (GDD §12, "cozy creepy"): rounded, toy-like, soft
colours; the hunter is goofy, never threatening.

Run headless only:
    blender -b --python-exit-code 1 -P tools/build_street_npcs.py [-- norender] [-- only Hunter]
"""
import math
import sys

from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import monster_kit as k  # noqa: E402
from monster_kit import ball, limb, lathe, box, pair, marker, on_ball, tube  # noqa: E402

SET = 'street/npcs'
ORDER = ['Hunter', 'NightBus']
ONLY = next((a.split(',') for a in k.ARGS[k.ARGS.index('only') + 1:k.ARGS.index('only') + 2]), None) \
    if 'only' in k.ARGS else None


def hunter():
    k.begin('Hunter', SET, {'Body': (105, 135, 75), 'Skin': (245, 205, 170), 'Trim': (240, 190, 60),
                            'Dark': (85, 58, 42), 'Light': (250, 245, 225), 'Glow_Warm_1': (255, 240, 170)})
    pair(ball, 'Dark', at=(0.32, -0.12, 0.17), r=(0.26, 0.4, 0.17), n=10, k=5, mirror=['at'])            # boots
    for s in (1, -1):
        limb('Dark', (s * 0.32, -0.02, 0.2), (s * 0.32, 0, 0.42), 0.2, n=8)
        limb('Trim', (s * 0.32, 0, 0.45), (s * 0.32, 0, 0.85), 0.15, n=8)                           # knee socks
        ball('Skin', (s * 0.32, 0, 1.0), 0.16, n=8, k=4)                                      # knobbly knees
        limb('Skin', (s * 0.32, 0, 1.0), (s * 0.3, 0, 1.3), 0.13, n=8)
    lathe('Body', [(1.15, 0), (1.2, 0.55), (1.45, 0.66), (1.62, 0.66), (1.7, 0)], sy=0.8)    # shorts
    T = [(1.55, 0), (1.6, 0.66), (2.2, 0.74), (2.8, 0.68), (3.05, 0.45), (3.15, 0)]
    lathe('Body', T, n=14, sy=0.8)                                                              # safari jacket
    lathe('Dark', [(-0.07, 0.68), (0.07, 0.68)], at=(0, 0, 1.62), sy=0.8)                      # belt
    box('Trim', (0, -0.565, 1.62), (0.22, 0.06, 0.16), bevel=0.02)                             # buckle
    HC, HR = (0, 0, 3.75), (0.78, 0.74, 0.78)
    ball('Skin', HC, HR, n=16, k=8)
    pair(ball, 'Skin', at=(0.78, 0.05, 3.72), r=(0.12, 0.1, 0.2), n=8, k=4, mirror=['at'])               # ears
    ball('Skin', (0, on_ball(HC, HR, 0, 3.62).y - 0.1, 3.62), (0.2, 0.18, 0.18), n=10, k=5)    # big round nose
    for s in (1, -1):
        mc = on_ball(HC, HR, s * 0.18, 3.43, out=0.0)
        ball('Dark', mc, (0.22, 0.08, 0.09), rot=(0, s * -15, 0), n=8, k=4)                   # bushy moustache
        ec = on_ball(HC, HR, s * 0.27, 3.97, out=-0.08)
        ball('Light', ec, (0.18, 0.11, 0.2), n=10, k=5)                                        # goggly eyes
        ball('Dark', (ec.x - s * 0.04, ec.y - 0.09, ec.z - 0.02), (0.08, 0.05, 0.09), n=8, k=4)  # a bit cross-eyed
        ball('Dark', on_ball(HC, HR, s * 0.28, 4.22, out=-0.02), (0.18, 0.06, 0.06), rot=(0, s * 12, 0),
             n=8, k=4)                                                                        # worried brows
    tilt = (0, -8, 0)                                                                          # an oversized pith helmet
    lathe('Light', [(0, 1.05), (0.07, 1.05)], at=(0, 0, 4.32), n=20, rot=tilt)
    lathe('Light', [(0, 0.8), (0.28, 0.78), (0.5, 0.62), (0.68, 0.36), (0.76, 0)], at=(0, 0, 4.36), n=16, rot=tilt)
    lathe('Dark', [(0.05, 0.81), (0.17, 0.81)], at=(0, 0, 4.36), n=16, rot=tilt)
    ball('Light', (0.76 * math.sin(math.radians(-8)), 0, 4.36 + 0.76 * math.cos(math.radians(8)) + 0.03), 0.09,
         n=8, k=4)
    # The garlic necklace: a string round the neck and five bulbs hanging at the front.
    zf = lambda t: 3.08 - 0.13 * max(0.0, -math.sin(t))
    loop = [(0.55 * math.cos(t), 0.5 * math.sin(t), zf(t)) for t in (2 * math.pi * i / 18 for i in range(18))]
    tube('Dark', loop, 0.03, n=5, closed=True, up=(0, 0, 1))
    for a in (-50, -25, 0, 25, 50):
        t = math.radians(-90 + a)
        c = (0.55 * math.cos(t), 0.5 * math.sin(t) - 0.08, zf(t) - 0.13)
        ball('Light', c, (0.14, 0.13, 0.13), n=8, k=4, radial=lambda u: 1 + 0.08 * math.cos(6 * u))
        lathe('Light', [(0, 0.05), (0.12, 0)], at=(c[0], c[1], c[2] + 0.11), n=5)
    # Left arm forward with an oversized flashlight; its lens is the one glow.
    limb('Body', (0.62, 0, 2.85), (0.88, -0.25, 2.35), 0.15, n=8)
    limb('Body', (0.88, -0.25, 2.35), (0.8, -0.6, 2.25), 0.14, n=8)
    ball('Skin', (0.78, -0.72, 2.25), 0.17, n=10, k=5)
    limb('Trim', (0.78, -0.5, 2.25), (0.78, -1.1, 2.25), 0.13, n=8)
    lathe('Trim', [(0, 0.15), (0.12, 0.27), (0.36, 0.29)], at=(0.78, -1.1, 2.25), n=12, rot=(90, 0, 0))
    ball('Glow_Warm_1', (0.78, -1.47, 2.25), (0.24, 0.05, 0.24), n=12, k=5)
    # Right arm holding a butterfly net upright.
    limb('Body', (-0.62, 0, 2.85), (-0.95, -0.1, 2.4), 0.15, n=8)
    limb('Body', (-0.95, -0.1, 2.4), (-1.0, -0.25, 2.1), 0.14, n=8)
    ball('Skin', (-1.0, -0.28, 2.05), 0.17, n=10, k=5)
    limb('Dark', (-1.0, -0.28, 0.45), (-1.0, -0.28, 4.15), 0.06, n=6)                          # the pole
    hoop = [(-1.0 + 0.48 * math.cos(t), -0.28, 4.62 + 0.48 * math.sin(t)) for t in (2 * math.pi * i / 16 for i in range(16))]
    tube('Trim', hoop, 0.05, n=6, closed=True, up=(0, 1, 0))
    lathe('Light', [(0, 0.44), (0.35, 0.4), (0.7, 0.26), (0.9, 0)], at=(-1.0, -0.26, 4.62), n=12, rot=(-75, 0, 0))
    marker('Nameplate', (0, 0, 6.0))
    return k.finish('A goofy monster hunter (GDD 8.1): pith helmet too big, worried brows, goggly cross-eyes, '
                    'bushy moustache, shorts and mustard knee socks, a garlic necklace, a butterfly net and an '
                    'oversized flashlight (its lens Glow_Warm_1, the part that proves he faces Roblox -Z).')


def night_bus():
    warm = (255, 205, 120)
    lamp = (255, 240, 180)
    wheel = (50, 42, 62)
    k.begin('NightBus', SET, {'Body': (105, 70, 155), 'Trim': (240, 145, 45), 'Dark': (45, 32, 60),
                              'Light': (245, 240, 230), 'Wheel_1': wheel, 'Wheel_2': wheel, 'Wheel_3': wheel,
                              'Wheel_4': wheel, 'Glow_Warm_1': warm, 'Glow_Warm_2': lamp, 'Glow_Warm_3': lamp,
                              'Glow_Warm_4': (255, 190, 90), 'Glow_Warm_5': (255, 120, 70)})
    # Blender -X is the front (Roblox +X), +Y the right side with the door (Roblox +Z, the stop's side).
    box('Body', (0, 0, 4.9), (23.4, 7.6, 5.8), bevel=0.8)                                       # the body
    box('Trim', (0.1, 0, 8.1), (22.6, 7.2, 0.7), bevel=0.3)                                     # orange roof
    box('Glow_Warm_4', (-9.0, 0, 8.66), (1.2, 2.6, 0.6), bevel=0.2)                             # roof lantern
    box('Trim', (0.2, -3.82, 4.0), (21.4, 0.1, 0.45), bevel=0.04)                               # side stripes
    box('Trim', (-8.5, 3.82, 4.0), (4.0, 0.1, 0.45), bevel=0.04)
    box('Trim', (3.7, 3.82, 4.0), (14.4, 0.1, 0.45), bevel=0.04)
    for x in (-8.8, -5.8, -2.8, 0.2, 3.2, 6.2, 9.2):                                           # windows, left
        box('Glow_Warm_1', (x, -3.83, 5.85), (2.3, 0.1, 1.6), bevel=0.04)
    for x, w in ((-8.8, 2.3), (-2.2, 2.3), (0.8, 2.3), (3.8, 2.3), (6.8, 2.3), (9.6, 1.9)):    # windows, right
        box('Glow_Warm_1', (x, 3.83, 5.85), (w, 0.1, 1.6), bevel=0.04)
    box('Glow_Warm_1', (-11.73, 0, 5.6), (0.1, 5.6, 1.9), bevel=0.04)                           # windscreen
    box('Glow_Warm_1', (11.73, 0, 5.8), (0.1, 5.0, 1.4), bevel=0.04)                            # rear window
    box('Dark', (-5.0, 3.87, 4.55), (2.7, 0.12, 4.7), bevel=0.05)                               # the door
    for x in (-5.62, -4.38):
        box('Glow_Warm_1', (x, 3.95, 5.0), (1.0, 0.08, 3.4), bevel=0.03)                        # its lit panes
    box('Dark', (-5.0, 3.3, 1.75), (2.6, 1.2, 0.3), bevel=0.06)                                 # the step
    # The face: headlamps for eyes (each its own part: the code may hang a light on one), rims, a grille smile.
    ball('Glow_Warm_2', (-11.78, -2.25, 3.55), (0.16, 0.62, 0.62), n=16, k=8)
    ball('Glow_Warm_3', (-11.78, 2.25, 3.55), (0.16, 0.62, 0.62), n=16, k=8)
    for y in (-2.25, 2.25):
        rim = [(-11.74, y + 0.68 * math.cos(t), 3.55 + 0.68 * math.sin(t)) for t in (2 * math.pi * i / 20 for i in range(20))]
        tube('Light', rim, 0.07, n=6, closed=True, up=(1, 0, 0))
    tube('Dark', [(-11.74, 1.0 * u, 3.25 - 0.25 * (1 - u * u)) for u in (i / 6 - 1 for i in range(13))], 0.09, n=8)
    box('Dark', (-11.65, 0, 2.25), (0.6, 7.0, 0.6), bevel=0.2)                                  # bumpers
    box('Dark', (11.65, 0, 2.25), (0.6, 7.0, 0.6), bevel=0.2)
    for y in (-2.6, 2.6):
        ball('Glow_Warm_5', (11.78, y, 3.4), (0.14, 0.4, 0.4), n=12, k=6)                       # tail lamps
    # Wheels, each its own part (MODELS.md rule 2: a wheel moves), Light hubcaps, Dark arches.
    tyre = [(-0.5, 1.15), (-0.42, 1.42), (-0.25, 1.5), (0.25, 1.5), (0.42, 1.42), (0.5, 1.15)]
    for i, (x, s) in enumerate(((-8, -1), (-8, 1), (8, -1), (8, 1)), 1):
        lathe(f'Wheel_{i}', tyre, at=(x, s * 3.35, 1.5), n=16, rot=(90, 0, 0))
        ball('Light', (x, s * 3.86, 1.5), (0.6, 0.08, 0.6), n=12, k=6)
        arch = [(x + 1.75 * math.cos(t), s * 3.84, 1.5 + 1.75 * math.sin(t))
                for t in (math.radians(15 + 150 * j / 12) for j in range(13))]
        tube('Dark', arch, 0.12, n=8, up=(0, 1, 0))
    marker('Door', (-5.0, 4.6, 0.0), look=(0, 1, 0))
    return k.finish('A cute purple night bus with an orange roof and a lit lantern on top, warm-lit windows '
                    '(Glow_Warm_1: windows, windscreen, door panes), headlamp eyes Glow_Warm_2 (its left) and '
                    'Glow_Warm_3 (its right), a grille smile, tail lamps Glow_Warm_5. Faces Roblox +X. Door: on '
                    'the floor 0.6 outside the right side (Roblox +Z), looking out. Wheel_1..4: front-left, '
                    'front-right, rear-left, rear-right; nothing turns them yet.')


BUILDERS = {'Hunter': hunter, 'NightBus': night_bus}

if __name__ == '__main__':
    names = [n for n in ORDER if not ONLY or n in ONLY]
    k.start_set(SET)
    for n in names:
        BUILDERS[n]()
    k.finish_set(SET, place={'Hunter': (-15.5, 0), 'NightBus': [(0, 180), (0, 40, -12)]},
                 frame='Blender +Z up; the Hunter faces Blender -Y (Roblox -Z), the NightBus Blender -X '
                       '(Roblox +X); Roblox (x, y, z) = Blender (-x, z, y)')
    k.validate(SET, names)
