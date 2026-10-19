"""Location 1's ten monsters, the Haunted Manor family (GDD §6.7), first drafts.

"Cozy creepy" (GDD §12): chunky rounded shapes, big glowing eyes with dark
pupils and a white glint, soft colours from Species.luau's `look`, never gore.
Each species is its shapes and a call to monster_kit.finish(), which refuses
anything breaking MODELS.md, "Monsters and street NPCs". Static meshes: no rig
and no Animations folder yet (the client bobs them).

Frame: Blender -Y is the front, +Z up, +X the monster's left (monster_kit).
Run headless only:
    blender -b --python-exit-code 1 -P tools/build_monsters_l1.py [-- norender] [-- only Slime,Ghost]  (one '--', then the words)
"""
import math
import sys

import numpy as np
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import monster_kit as k  # noqa: E402
from monster_kit import ball, limb, lathe, rings, prism, box, arc_shell, pair, eyes, marker, on_ball, front_y  # noqa: E402

SET = 'monsters/haunted_manor'
ORDER = ['Slime', 'Skeleton', 'PumpkinHead', 'Ghost', 'Mummy', 'Zombie', 'Witch', 'Werewolf',
         'VampireCount', 'GrandBanshee']
ONLY = next((a.split(',') for a in k.ARGS[k.ARGS.index('only') + 1:k.ARGS.index('only') + 2]), None) \
    if 'only' in k.ARGS else None

WHITE = (255, 255, 255)
BLUSH = (255, 150, 180)
INK = (45, 32, 60)          # the family's dark: a deep plum, never pure black


def cheeks(at_l, r=(0.18, 0.06, 0.11), part='Trim'):
    pair(ball, part, at=at_l, r=r, mirror=['at'])


def slime():
    k.begin('Slime', SET, {'Dark': INK, 'Light': WHITE, 'Trim': BLUSH})
    S = [(0, 0), (0.04, 1.25), (0.18, 1.5), (0.5, 1.58), (1.0, 1.52), (1.6, 1.32), (2.2, 0.98),
         (2.6, 0.62), (2.85, 0.28), (2.95, 0)]
    lathe('Body', S, n=24)
    for i in range(5):                                   # goo drips round the base
        t = math.radians(-60 + i * 72)
        ball('Body', (1.5 * math.cos(t), 1.5 * math.sin(t), 0.17), (0.34, 0.34, 0.16), n=10, k=5)
    lathe('Body', [(0, 0.26), (0.22, 0.18), (0.45, 0)], at=(0, 0, 2.72), n=10, rot=(0, 28, 0))   # the curl
    eyes((0.55, front_y(S, 1.78, 0.55, out=-0.14), 1.78), 0.42)
    ball('Dark', (0, front_y(S, 1.2, 0, out=0.0), 1.2), (0.2, 0.08, 0.12))
    cheeks((0.98, front_y(S, 1.3, 0.98, out=0.0), 1.3))
    ball('Light', (-0.62, front_y(S, 2.3, -0.62, out=0.01), 2.3), (0.26, 0.07, 0.15), rot=(0, 0, 25))
    marker('Hand', (-1.55, 0, 1.0))
    marker('Nameplate', (0, 0, 4.1))
    return k.finish('Blob; the client bobs and wobbles it. Hand is the right side of the body (no arms).')


def skeleton():
    k.begin('Skeleton', SET, {'Dark': INK, 'Light': WHITE, 'Trim': (40, 170, 170),
                              'Glow_Eyes_1': (150, 225, 255), 'Glow_Eyes_2': (150, 225, 255)})
    pair(ball, 'Body', at=(0.38, -0.12, 0.16), r=(0.26, 0.4, 0.16), mirror=['at'])            # feet
    for s in (1, -1):
        limb('Body', (s * 0.38, 0, 0.26), (s * 0.36, 0, 0.86), 0.13, n=8)
        ball('Body', (s * 0.36, 0, 0.92), 0.19, n=10, k=5)                                                 # knees
        limb('Body', (s * 0.36, 0, 0.98), (s * 0.3, 0, 1.45), 0.14, n=8)
    ball('Body', (0, 0, 1.55), (0.55, 0.38, 0.3))                                              # pelvis
    ball('Body', (0, 0, 1.87), (0.18, 0.18, 0.14), n=10, k=5)                                             # a vertebra
    RC, RR = (0, 0, 2.55), (0.75, 0.55, 0.6)
    ball('Body', RC, RR, n=16, k=8)                                                            # ribcage
    for s in (1, -1):
        for z in (2.35, 2.7):
            ball('Dark', on_ball(RC, RR, s * 0.36, z, out=-0.03), (0.2, 0.05, 0.055), n=10, k=5)           # rib gaps
    limb('Body', (0, 0, 3.05), (0, 0, 3.3), 0.14)                                              # neck
    SC, SR = (0, 0, 4.0), (0.95, 0.88, 0.9)
    ball('Body', SC, SR, n=20, k=10)                                                           # skull
    JC, JR = (0, -0.15, 3.35), (0.6, 0.55, 0.3)
    ball('Body', JC, JR, n=14, k=7)                                                            # jaw
    for s in (1, -1):
        ball('Dark', on_ball(SC, SR, s * 0.36, 4.05, out=-0.05), (0.3, 0.12, 0.33), n=10, k=5)             # sockets
    eyes((0.36, on_ball(SC, SR, 0.36, 4.0).y - 0.1, 4.0), 0.14, pupil=0)
    ny = on_ball(SC, SR, 0, 3.7).y
    prism('Dark', [(-0.1, 3.78), (0.1, 3.78), (0, 3.62)], ny - 0.03, 0.2)                     # nose
    ball('Dark', on_ball(JC, JR, 0, 3.3, out=-0.03), (0.3, 0.05, 0.04))                        # grin
    for s in (1, -1):
        ball('Body', (s * 0.78, 0, 3.0), 0.21, n=10, k=5)                                                 # shoulders
        limb('Body', (s * 0.8, 0, 2.9), (s * 0.95, -0.1, 2.3), 0.12, n=8)
        ball('Body', (s * 0.95, -0.1, 2.25), 0.15, n=10, k=5)                                             # elbows
        limb('Body', (s * 0.95, -0.12, 2.2), (s * 0.95, -0.36, 1.75), 0.11, n=8)
        ball('Body', (s * 0.95, -0.4, 1.6), (0.2, 0.2, 0.22))                                  # hands
    for s in (1, -1):                                                                          # bow tie
        ball('Trim', (s * 0.17, -0.44, 3.08), (0.18, 0.08, 0.12), n=10, k=5, rot=(0, s * -12, 0))
    ball('Trim', (0, -0.5, 3.08), (0.08, 0.06, 0.08), n=8, k=4)
    marker('Hand', (-0.95, -0.4, 1.6))
    marker('Nameplate', (0, 0, 5.9))
    return k.finish('Biped; a teal bow tie for the Front Desk.')


def pumpkin_head():
    warm = (255, 190, 60)
    k.begin('PumpkinHead', SET, {'Dark': (80, 50, 40), 'Trim': (70, 150, 85),
                                 'Glow_Eyes_1': warm, 'Glow_Eyes_2': warm, 'Glow_Warm_1': warm})
    pair(ball, 'Dark', at=(0.28, -0.08, 0.14), r=(0.2, 0.32, 0.14), mirror=['at'])            # boots
    for s in (1, -1):
        limb('Dark', (s * 0.25, 0, 0.22), (s * 0.25, 0, 1.0), 0.13)
    T = [(0.85, 0), (0.9, 0.6), (1.3, 0.62), (1.9, 0.52), (2.35, 0.4), (2.5, 0)]
    lathe('Trim', T, sy=0.8)                                                                   # tunic
    for i in range(4):                                                                         # leaf collar
        t = math.radians(-135 + i * 90)
        ball('Trim', (0.42 * math.cos(t), 0.42 * math.sin(t), 2.42), (0.3, 0.16, 0.07),
             rot=(0, 0, math.degrees(t) + 90))
    for s in (1, -1):
        limb('Trim', (s * 0.5, 0, 2.2), (s * 0.85, -0.2, 1.55), 0.12)
        ball('Dark', (s * 0.86, -0.22, 1.45), 0.15)                                            # gloves
    HC, HR = (0, 0, 3.15), (1.15, 1.0, 0.95)
    ball('Body', HC, HR, n=24, k=10, radial=lambda t: 1 + 0.06 * math.cos(8 * t))            # the pumpkin
    limb('Trim', (0, 0, 3.98), (0.12, 0, 4.42), 0.13, 0.09)                                   # stem
    ball('Trim', (0.32, 0, 4.12), (0.25, 0.12, 0.06), rot=(0, -20, 0))                         # its leaf
    prism('Glow_Eyes_1', [(0.2, 3.22), (0.62, 3.22), (0.41, 3.56)], -1.02, 0.34)
    prism('Glow_Eyes_2', [(-0.62, 3.22), (-0.2, 3.22), (-0.41, 3.56)], -1.02, 0.34)
    smile = [(-0.5, 2.95), (0.5, 2.95)] + [(0.5 * math.cos(math.radians(d)), 2.95 - 0.28 * math.sin(math.radians(d)))
                                           for d in (20, 50, 90, 130, 160)]
    prism('Glow_Warm_1', smile, -1.0, 0.36)                                                    # the grin
    marker('Hand', (-0.86, -0.22, 1.45))
    marker('Nameplate', (0, 0, 5.4))
    return k.finish('Biped; carved face lit warm: Glow_Eyes_1/2 and the mouth Glow_Warm_1 '
                    '(quirk: "head glows brighter when happy").')


def ghost():
    k.begin('Ghost', SET, {'Dark': INK, 'Light': WHITE, 'Trim': BLUSH,
                           'Glow_Eyes_1': (110, 90, 230), 'Glow_Eyes_2': (110, 90, 230)})
    G = [(0.78, 0), (0.5, 1.38), (1.0, 1.22), (1.8, 1.06), (2.6, 1.02), (3.3, 0.95), (3.8, 0.78),
         (4.15, 0.52), (4.4, 0.24), (4.5, 0)]
    lathe('Body', G, n=24, wave={1: lambda t: 0.16 * math.sin(6 * t)})
    pair(ball, 'Body', at=(1.12, -0.1, 2.3), r=(0.4, 0.3, 0.24), rot=(0, 28, 0), mirror=['at'])  # arm nubs
    eyes((0.38, front_y(G, 3.2, 0.38, out=-0.1), 3.2), 0.3, rr=(0.26, 0.2, 0.34))
    ball('Dark', (0, front_y(G, 2.68, 0, out=0.0), 2.68), (0.14, 0.06, 0.17))
    cheeks((0.66, front_y(G, 2.85, 0.66, out=0.0), 2.85), r=(0.16, 0.06, 0.1))
    marker('Hand', (-1.4, -0.1, 2.35))
    marker('Nameplate', (0, 0, 5.4))
    return k.finish('Float: the sheet hovers, its wavy hem 0.34 over the floor at its lowest. '
                    'Hand is the right arm nub.')


def mummy():
    k.begin('Mummy', SET, {'Dark': INK, 'Light': WHITE, 'Trim': (185, 168, 128),
                           'Glow_Eyes_1': (180, 255, 120), 'Glow_Eyes_2': (180, 255, 120)})
    pair(ball, 'Body', at=(0.32, -0.1, 0.15), r=(0.24, 0.36, 0.15), mirror=['at'])
    for s in (1, -1):
        limb('Body', (s * 0.3, 0, 0.26), (s * 0.3, 0, 1.5), 0.24)
    T = [(1.3, 0), (1.35, 0.6), (1.9, 0.8), (2.7, 0.85), (3.4, 0.8), (3.75, 0.6), (3.9, 0)]
    lathe('Body', T, sy=0.8)
    for z, tilt in ((1.85, 7), (2.55, -6), (3.25, 8)):                                         # bandage bands
        r = float(np.interp(z, [p[0] for p in T], [p[1] for p in T])) + 0.05
        lathe('Trim', [(-0.07, r), (0.07, r)], at=(0, 0, z), sy=0.8, rot=(tilt, 0, 0))
    HC, HR = (0, 0, 4.55), (0.85, 0.8, 0.9)
    ball('Body', HC, HR, n=18, k=9)
    lathe('Trim', [(-0.06, 0.86), (0.06, 0.86)], at=(0, 0, 4.98), n=18, sy=0.94, rot=(0, 14, 0))
    vis = on_ball(HC, HR, 0, 4.6, out=-0.1)
    ball('Dark', vis, (0.62, 0.15, 0.22))                                                      # the gap
    eyes((0.28, vis.y - 0.06, 4.6), 0.15)
    for s in (1, -1):
        limb('Body', (s * 0.8, 0, 3.4), (s * 0.75, -0.9, 3.0), 0.2)
        ball('Body', (s * 0.75, -1.05, 2.95), 0.2)
    box('Trim', (0.36, 0.66, 1.25), (0.22, 0.06, 0.9), bevel=0.02, rot=(12, 0, 0))             # the trailing end
    marker('Hand', (-0.75, -1.05, 2.95))
    marker('Nameplate', (0, 0, 6.4))
    return k.finish('Biped, arms forward; one bandage end hanging behind (quirk "trails bandages").')


def zombie():
    k.begin('Zombie', SET, {'Dark': (55, 60, 95), 'Light': (250, 250, 240), 'Trim': (130, 80, 170),
                            'Glow_Eyes_1': (255, 245, 170), 'Glow_Eyes_2': (255, 245, 170)})
    pair(ball, 'Dark', at=(0.33, -0.1, 0.15), r=(0.25, 0.38, 0.15), mirror=['at'])
    for s in (1, -1):
        limb('Dark', (s * 0.3, 0, 0.26), (s * 0.3, 0, 1.5), 0.24)
    ball('Dark', (0, 0, 1.55), (0.62, 0.45, 0.3))
    T = [(1.4, 0), (1.5, 0.66), (2.2, 0.72), (2.9, 0.75), (3.3, 0.68), (3.5, 0)]
    lathe('Trim', T, sy=0.75, wave={1: lambda t: 0.07 * math.sin(5 * t)})                      # the torn shirt
    limb('Body', (0, 0, 3.4), (0, 0, 3.6), 0.25)
    HC, HR = (0, 0, 4.4), (1.0, 0.9, 1.05)
    ball('Body', HC, HR, n=20, k=10)
    ball('Dark', (0, 0.18, 5.28), (0.5, 0.45, 0.22))                                           # hair
    limb('Dark', (0.1, 0.1, 5.35), (0.3, -0.1, 5.72), 0.1, 0.03)                               # the tuft
    eyes((0.36, on_ball(HC, HR, 0.36, 4.5, out=-0.12).y, 4.5), 0.3)
    mo = on_ball(HC, HR, 0, 3.9, out=-0.03)
    ball('Dark', mo, (0.3, 0.06, 0.1))
    box('Light', (0.09, mo.y - 0.05, 3.95), (0.1, 0.06, 0.09), bevel=0.015)                   # one tooth
    for s in (1, -1):
        limb('Trim', (s * 0.75, 0, 3.15), (s * 0.73, -0.35, 3.05), 0.24)                       # sleeves
        limb('Body', (s * 0.74, -0.3, 3.05), (s * 0.7, -0.9, 2.95), 0.17)
        ball('Body', (s * 0.7, -1.05, 2.93), 0.2)
    marker('Hand', (-0.7, -1.05, 2.93))
    marker('Nameplate', (0, 0, 6.5))
    return k.finish('Biped, arms forward; a torn purple shirt and one tooth.')


def witch():
    gl = (255, 210, 90)
    k.begin('Witch', SET, {'Dark': INK, 'Light': WHITE, 'Skin': (150, 210, 140), 'Trim': (240, 140, 40),
                           'Glow_Eyes_1': gl, 'Glow_Eyes_2': gl})
    pair(ball, 'Dark', at=(0.25, -0.15, 0.12), r=(0.18, 0.32, 0.12), mirror=['at'])
    D = [(0.15, 0), (0.15, 1.15), (0.6, 1.0), (1.4, 0.75), (2.2, 0.5), (2.8, 0.45), (3.05, 0.3), (3.15, 0)]
    lathe('Body', D, n=24, wave={1: lambda t: 0.06 * math.sin(8 * t)})                         # the dress
    lathe('Dark', [(-0.08, 0.54), (0.08, 0.54)], at=(0, 0, 2.2), n=16)                         # belt
    HC, HR = (0, 0, 3.7), (0.72, 0.68, 0.7)
    ball('Skin', HC, HR, n=18, k=9)
    pair(ball, 'Trim', at=(0.62, 0.15, 3.45), r=(0.3, 0.35, 0.45), mirror=['at'])              # orange hair
    ball('Trim', (0, 0.3, 3.75), (0.72, 0.5, 0.72))
    lathe('Body', [(0, 0), (0, 1.15), (0.12, 1.15), (0.12, 0)], at=(0, 0, 4.15), n=24)        # brim
    rings('Body', [(0, 0, 4.25, 0.68), (0.05, 0, 4.7, 0.55), (0.12, 0, 5.1, 0.38),
                   (0.3, 0, 5.35, 0.2), (0.55, 0, 5.5, 0)], n=16)                              # the bent cone
    lathe('Trim', [(-0.07, 0.69), (0.07, 0.69)], at=(0, 0, 4.36), n=16)                        # hat band
    eyes((0.26, on_ball(HC, HR, 0.26, 3.72, out=-0.1).y, 3.72), 0.2, rr=(0.2, 0.15, 0.24))
    ball('Skin', on_ball(HC, HR, 0, 3.52, out=-0.04), 0.1, n=8, k=4)                           # button nose
    ball('Dark', on_ball(HC, HR, 0, 3.33, out=-0.03), (0.18, 0.05, 0.06))
    for s in (1, -1):
        limb('Body', (s * 0.45, 0, 2.85), (s * 0.8, -0.2, 2.15), 0.15, 0.22)                   # bell sleeves
        ball('Skin', (s * 0.85, -0.25, 2.0), 0.15)
    marker('Hand', (-0.85, -0.25, 2.0))
    marker('Nameplate', (0, 0, 6.4))
    return k.finish('Biped; mint skin, orange hair, a bent hat. No cauldron or broom (props are the code\'s).')


def werewolf():
    k.begin('Werewolf', SET, {'Dark': (40, 30, 35), 'Light': (245, 240, 230), 'Trim': (205, 175, 135),
                              'Glow_Eyes_1': (255, 190, 50), 'Glow_Eyes_2': (255, 190, 50)})
    pair(ball, 'Body', at=(0.45, -0.25, 0.2), r=(0.35, 0.55, 0.2), mirror=['at'])
    for s in (1, -1):
        limb('Body', (s * 0.45, 0, 0.35), (s * 0.5, 0.1, 1.7), 0.32, 0.4)
    T = [(1.5, 0), (1.6, 0.85), (2.4, 1.05), (3.3, 1.2), (4.1, 1.2), (4.6, 0.95), (4.85, 0)]
    lathe('Body', T, sy=0.8)
    ball('Trim', (0, front_y(T, 2.9, 0, sy=0.8, out=-0.22), 2.9), (0.7, 0.25, 0.95))          # belly
    HC, HR = (0, -0.2, 5.45), (0.85, 0.8, 0.8)
    ball('Body', HC, HR, n=18, k=9)
    pair(lathe, 'Body', [(0, 0.26), (0.55, 0)], at=(0.5, -0.1, 5.98), n=10, rot=(0, 20, 0), mirror=['at'])
    pair(lathe, 'Trim', [(0, 0.15), (0.38, 0)], at=(0.5, -0.24, 6.0), n=8, rot=(0, 20, 0), mirror=['at'])
    ball('Trim', (0, -0.95, 5.22), (0.45, 0.45, 0.32))                                         # muzzle
    ball('Dark', (0, -1.38, 5.36), (0.16, 0.1, 0.11), n=10, k=5)                               # nose
    eyes((0.32, on_ball(HC, HR, 0.32, 5.68, out=-0.12).y, 5.68), 0.2)
    for s in (1, -1):
        limb('Body', (s * 1.05, 0, 4.3), (s * 1.25, -0.2, 3.1), 0.3)
        limb('Body', (s * 1.25, -0.2, 3.1), (s * 1.15, -0.4, 2.2), 0.28, 0.25)
        ball('Body', (s * 1.15, -0.45, 2.0), 0.33)
        for c in (-0.15, 0, 0.15):                                                             # blunt claws
            ball('Light', (s * 1.15 + c, -0.74, 1.86), 0.07, n=8, k=4)
    limb('Body', (0, 0.8, 1.9), (0, 1.6, 1.45), 0.3, 0.25)                                     # tail
    ball('Trim', (0, 1.75, 1.38), 0.3)
    marker('Hand', (-1.15, -0.45, 2.0))
    marker('Nameplate', (0, -0.1, 7.4))
    return k.finish('Biped, a big fluffy wolf; blunt round claws, nothing sharp.')


def vampire_count():
    k.begin('VampireCount', SET, {'Dark': (28, 22, 34), 'Light': (250, 250, 250), 'Skin': (232, 226, 242),
                                  'Trim': (190, 35, 60)})
    pair(ball, 'Dark', at=(0.33, -0.1, 0.16), r=(0.24, 0.42, 0.16), mirror=['at'])             # shoes
    for s in (1, -1):
        limb('Body', (s * 0.3, 0, 0.26), (s * 0.3, 0, 1.6), 0.2)
    T = [(1.45, 0), (1.5, 0.5), (1.9, 0.62), (2.6, 0.72), (3.3, 0.82), (3.75, 0.78), (3.95, 0.45), (4.05, 0)]
    lathe('Body', T, sy=0.7)
    ball('Light', (0, front_y(T, 3.35, 0, sy=0.7, out=-0.04), 3.35), (0.3, 0.08, 0.45))       # shirt
    ball('Trim', (0, front_y(T, 3.55, 0, sy=0.7, out=0.06), 3.55), 0.1, n=8, k=4)             # brooch
    limb('Skin', (0, 0, 3.9), (0, 0, 4.2), 0.22)
    HC, HR = (0, 0, 4.75), (0.78, 0.72, 0.8)
    ball('Skin', HC, HR, n=18, k=9)
    ball('Dark', (0, 0.18, 5.05), (0.84, 0.7, 0.6), n=16, k=8)                                 # slicked hair
    ball('Dark', (0, 0.1, 5.6), (0.4, 0.4, 0.32))                                              # the quiff
    fy = on_ball(HC, HR, 0, 5.15).y
    prism('Dark', [(-0.2, 5.38), (0.2, 5.38), (0, 5.08)], fy - 0.03, 0.3)                      # widow's peak
    eyes((0.27, on_ball(HC, HR, 0.27, 4.85, out=-0.1).y, 4.85), 0.17, rr=(0.17, 0.13, 0.2))
    pair(lathe, 'Skin', [(0, 0.12), (0.36, 0)], at=(0.74, 0.05, 4.85), n=8, rot=(0, 70, 0), mirror=['at'])
    mo = on_ball(HC, HR, 0, 4.48, out=-0.03)
    ball('Dark', mo, (0.2, 0.05, 0.04), n=10, k=4)
    for s in (1, -1):                                                                          # tiny fangs
        lathe('Light', [(-0.13, 0), (0, 0.05)], at=(s * 0.11, mo.y - 0.02, 4.47), n=6)
    CAPE = [(0.35, 1.35), (1.5, 1.15), (2.8, 0.98), (3.7, 0.9), (4.05, 0.7)]
    arc_shell('Body', CAPE, -15, 195, 0.08, sy=0.75)
    arc_shell('Trim', [(z + 0.05, r - 0.07) for z, r in CAPE[:-1]] + [(4.0, 0.63)], -13, 193, 0.09, sy=0.75)
    COL = [(3.85, 0.78), (4.4, 0.86), (5.2, 1.05), (5.7, 1.1)]
    arc_shell('Body', COL, 10, 170, 0.07, sy=0.85)
    arc_shell('Trim', [(3.9, 0.72), (4.4, 0.8), (5.2, 0.99), (5.65, 1.04)], 13, 167, 0.07, sy=0.85)
    for s in (1, -1):
        limb('Body', (s * 0.8, 0, 3.65), (s * 1.05, -0.15, 2.6), 0.2)
        limb('Body', (s * 1.05, -0.15, 2.6), (s * 0.95, -0.45, 1.9), 0.18)
        ball('Skin', (s * 0.95, -0.5, 1.78), 0.17)
    marker('Hand', (-0.95, -0.5, 1.78))
    marker('Nameplate', (0, 0, 6.9))
    return k.finish('Biped; cape with a red lining and a tall collar, two tiny fangs, red eyes '
                    '(Species.luau look.eyes).')


def grand_banshee():
    gl = (200, 255, 255)
    k.begin('GrandBanshee', SET, {'Dark': INK, 'Light': (236, 246, 255), 'Skin': (215, 240, 245),
                                  'Trim': (240, 200, 90), 'Glow_Eyes_1': gl, 'Glow_Eyes_2': gl})
    G = [(0.55, 0), (0.4, 1.6), (0.9, 1.45), (1.8, 1.2), (2.8, 0.95), (3.7, 0.7), (4.3, 0.55),
         (4.7, 0.62), (5.0, 0.55), (5.15, 0)]
    lathe('Body', G, n=24, wave={1: lambda t: 0.15 * math.sin(7 * t)})                         # the gown
    limb('Skin', (0, 0, 5.0), (0, 0, 5.4), 0.18)
    HC, HR = (0, 0, 5.95), (0.62, 0.58, 0.68)
    ball('Skin', HC, HR, n=18, k=9)
    ball('Light', (0, 0.35, 6.0), (0.8, 0.6, 0.9), n=16, k=8)                                  # hair
    limb('Light', (0, 0.62, 6.1), (0, 1.05, 3.6), 0.55, 0.2)                                   # flowing down
    ball('Light', (0, 0.25, 6.75), 0.3)                                                        # the bun
    ty = on_ball(HC, HR, 0, 6.5).y
    prism('Trim', [(-0.25, 6.5), (0.25, 6.5), (0, 6.82)], ty - 0.06, 0.25)                    # tiara
    eyes((0.22, on_ball(HC, HR, 0.22, 6.05, out=-0.09).y, 6.05), 0.15, rr=(0.15, 0.12, 0.19))
    ball('Dark', on_ball(HC, HR, 0, 5.62, out=-0.03), (0.12, 0.06, 0.16))                      # singing
    limb('Body', (0.5, 0, 4.9), (1.1, -0.1, 5.6), 0.14)                                        # left arm up
    limb('Body', (1.1, -0.1, 5.6), (1.25, -0.15, 6.2), 0.12)
    ball('Skin', (1.27, -0.15, 6.35), 0.14)
    limb('Body', (-0.5, 0, 4.9), (-0.95, -0.35, 4.4), 0.14)                                    # right arm out
    ball('Skin', (-1.0, -0.45, 4.3), 0.14)
    for x in (-0.22, 0, 0.22):                                                                 # pearls
        ball('Trim', (x, front_y(G, 4.85 - abs(x) * 0.5, x, out=0.02), 4.85 - abs(x) * 0.5), 0.08, n=8, k=4)
    marker('Hand', (-1.0, -0.45, 4.3))
    marker('Nameplate', (0, 0, 8.0))
    return k.finish('Float: an opera diva, one arm raised mid-song; gown hem 0.25 over the floor.')


BUILDERS = {'Slime': slime, 'Skeleton': skeleton, 'PumpkinHead': pumpkin_head, 'Ghost': ghost,
            'Mummy': mummy, 'Zombie': zombie, 'Witch': witch, 'Werewolf': werewolf,
            'VampireCount': vampire_count, 'GrandBanshee': grand_banshee}

if __name__ == '__main__':
    names = [n for n in ORDER if not ONLY or n in ONLY]
    k.start_set(SET)
    for n in names:
        BUILDERS[n]()
    k.finish_set(SET)
    k.validate(SET, names)
