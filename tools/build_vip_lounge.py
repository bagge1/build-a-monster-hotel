"""The VIP lounge set (GDD A.2, §10.2: the VIP Lobby pass's "VIP lounge decor set"), a draft for August's review.

Five decor pieces of every location (Pieces.luau, location = 0, pass = "VIPLobby"), one model for all three
hotels (MODELS.md, "Decor": decor of every location is one model, saved into Haunted Manor's folder), so
its colours are none of a location's: black lacquer, gold and red velvet, a showbiz lounge.

    Decor_VipRope      3 x 1 Floor  two gold stanchions and a red velvet rope swagged between them
    Decor_VipSofa      2 x 1 Floor  a red velvet sofa for two on a black and gold frame, a gold star on its crest
    Decor_VipCupcakes  1 x 1 Floor  a gold three-tier stand of cupcakes
    Decor_VipCarpet    4 x 2 Rug    a red carpet runner with gold borders and diamonds; its ends open
    Decor_VipSign      2 x 1 Wall   a black marquee in a gold frame, "VIP" in lit bulbs (Glow_Warm_1)

    blender -b --python-exit-code 1 -P tools/build_vip_lounge.py [-- nopreview] [-- only A,B]

Writes blender/decor/vip_lounge/: fbx/<Name>.fbx, manifest.json, validation.json, import_fixup.luau,
review/contact_sheet.png, the .blend.
"""
import math
import sys
from pathlib import Path

from mathutils import Matrix, Vector

sys.path.insert(0, str(Path(__file__).resolve().parent))
import hotel_kit as K  # noqa: E402
from hotel_kit import finish, box, span, cyl, lathe, sphere, prism  # noqa: E402

SET = 'decor/vip_lounge'
PALETTE = [
    ('grey', (110, 110, 120)), ('gold', (226, 182, 78)), ('gold_dark', (170, 128, 46)), ('gold_light', (246, 214, 128)),
    ('velvet', (168, 28, 48)), ('velvet_dark', (116, 16, 34)), ('velvet_light', (200, 56, 72)),
    ('lacquer', (30, 28, 34)), ('lacquer_light', (58, 54, 64)), ('cream', (248, 240, 222)), ('white', (246, 246, 250)),
    ('icing_pink', (246, 160, 196)), ('icing_mint', (164, 232, 204)), ('icing_cream', (252, 236, 206)),
    ('choc', (110, 66, 44)), ('cherry', (210, 30, 50)), ('wrapper', (236, 200, 112)),
    ('flame', (255, 205, 120), 'Warm'), ('bulb', (255, 226, 160), 'Warm'),
]
IDS = ['VipRope', 'VipSofa', 'VipCupcakes', 'VipCarpet', 'VipSign']

decor = K.decor


def rod(part, a, b, r, col, n=6):
    """A round rod from a to b."""
    a, b = Vector(a), Vector(b)
    d = b - a
    cyl(part, (0, 0, 0), r, d.length, col, n=n, m=Matrix.Translation(a) @ d.to_track_quat('Y', 'Z').to_matrix().to_4x4())


def stanchion(x, z):
    """A gold post on a domed foot with a ball finial and the rope's hook; returns the hook's point."""
    lathe('Body', [(0.62, 0.0), (0.64, 0.06), (0.5, 0.18), (0.22, 0.32), (0.12, 0.42), (0.0, 0.44)], 'gold', n=10,
          base=(x, 0, z))
    cyl('Body', (x, 0.42, z), 0.1, 2.0, 'gold', n=10)
    lathe('Body', [(0.17, 2.4), (0.22, 2.48), (0.15, 2.54)], 'gold_dark', n=10, base=(x, 0, z))
    sphere('Body', (x, 2.7, z), (0.2, 0.2, 0.2), 'gold_light', n=10, rings=6)
    return (x, 2.22, z)


def d_rope():
    decor('VipRope', 3, 1, 'Floor')
    ha = stanchion(-3.4, 0)
    hb = stanchion(3.4, 0)
    for (x, y, z), s in ((ha, 1), (hb, -1)):                 # the clips on the posts
        span('Body', (x + s * 0.06, y - 0.08, -0.08), (x + s * 0.2, y + 0.08, 0.08), 'gold_dark')
    # The rope: a catenary of short rods, thick velvet, sagging 0.55, at a person's waist.
    n = 12
    pts = []
    for i in range(n + 1):
        t = i / n
        x = ha[0] + 0.2 + (hb[0] - ha[0] - 0.4) * t
        pts.append((x, ha[1] - 0.55 * (1 - (2 * t - 1) ** 2), 0))
    for a, b in zip(pts, pts[1:]):
        rod('Body', a, b, 0.21, 'velvet', n=7)
    for p in pts[1:-1]:
        sphere('Body', p, (0.21, 0.21, 0.21), 'velvet', n=7, rings=3)
    for p in (pts[0], pts[-1]):                               # gold end caps on the clips
        sphere('Body', p, (0.25, 0.25, 0.25), 'gold', n=8, rings=4)
    finish(note='two gold stanchions on domed feet, a red velvet rope swagged between them on gold clips')


def d_sofa():
    decor('VipSofa', 2, 1, 'Floor')
    # Black lacquer plinth on four gold ball feet under a gold trim; two velvet seat cushions; rolled arms;
    # a velvet back under a gold crest with a black inset and a gold star.
    for x in (-2.3, 2.3):
        for z in (-0.82, 0.8):
            sphere('Body', (x, 0.2, z), (0.2, 0.2, 0.2), 'gold', n=8, rings=4)
    span('Body', (-2.56, 0.38, -1.08), (2.56, 1.16, 1.08), 'lacquer', bevel=0.06)
    span('Body', (-2.6, 1.12, -1.1), (2.6, 1.2, 1.1), 'gold', bevel=0.02)
    for x0, x1 in ((-2.05, 0.0), (0.0, 2.05)):
        span('Body', (x0, 1.2, -1.1), (x1, 1.8, 0.4), 'velvet', bevel=0.06)
    K.seat(-2.05, 2.05, -1.1, 0.4, 1.8, people=2)
    for sx in (-1, 1):                                        # the arms, rolled over at the top
        span('Body', (min(sx * 2.1, sx * 2.6), 1.2, -1.02), (max(sx * 2.1, sx * 2.6), 2.35, 1.1), 'velvet', bevel=0.1)
        cyl('Body', (0, 0, 0), 0.25, 2.11, 'velvet_light', n=10, m=K.at((sx * 2.35, 2.35, -1.05), rx=90))
        cyl('Body', (0, 0, 0), 0.2, 0.03, 'gold', n=10, m=K.at((sx * 2.35, 2.35, -1.05), rx=-90))
    # The back: velvet from z 0.42 to 1.1, up to 3.4.
    span('Body', (-2.1, 1.2, 0.42), (2.1, 3.4, 1.1), 'velvet', bevel=0.14)
    # The crest: gold over the back's whole depth, a black inset on its front, a gold star on that.
    prism('Body', K.round_arch_points(-2.2, 2.2, 3.3, 3.85, n=8), 0.4, 1.1, 'gold', plane='xy')
    prism('Body', K.round_arch_points(-1.95, 1.95, 3.42, 3.7, n=8), 0.37, 0.41, 'lacquer', plane='xy')
    star(0, 3.6, 0.37, 0.2, 'gold_light', t=0.05)
    finish(note='a red velvet sofa for two on a black lacquer plinth with gold ball feet, rolled arms, a gold '
                'crest with a black inset and a gold star')


def star(x, y, z, r, col, t=0.08, part='Body'):
    """A five-pointed star standing on a face toward -Z at z (its back at z)."""
    pts = []
    for i in range(10):
        a = math.pi / 2 + math.pi * i / 5
        rr = r if i % 2 == 0 else r * 0.45
        pts.append((x + rr * math.cos(a), y + rr * math.sin(a)))
    prism(part, pts, z - t, z, col, plane='xy')


def cupcake(x, y, z, icing, cherry=False):
    lathe('Body', [(0.14, y), (0.2, y + 0.24), (0.0, y + 0.24)], 'wrapper', n=7, base=(x, 0, z))
    sphere('Body', (x, y + 0.3, z), (0.21, 0.13, 0.21), icing, n=7, rings=3)
    sphere('Body', (x, y + 0.42, z), (0.12, 0.09, 0.12), icing, n=6, rings=3)
    if cherry:
        sphere('Body', (x, y + 0.53, z), (0.06, 0.06, 0.06), 'cherry', n=5, rings=3)


def d_cupcakes():
    decor('VipCupcakes', 1, 1, 'Floor')
    lathe('Body', [(0.62, 0.0), (0.64, 0.06), (0.4, 0.2), (0.12, 0.34), (0.0, 0.36)], 'gold', n=14)
    cyl('Body', (0, 0.34, 0), 0.07, 3.4, 'gold', n=8)
    icings = ('choc', 'icing_cream', 'velvet_light')        # chocolate, cream and red velvet: the set's colours
    k = 0
    for y, r, count, ring in ((0.95, 1.05, 6, 0.72), (2.0, 0.78, 4, 0.48), (2.95, 0.52, 2, 0.24)):
        lathe('Body', [(0.0, y - 0.06), (r, y - 0.06), (r + 0.02, y + 0.02), (r - 0.04, y + 0.03), (0.0, y)],
              'gold', n=16)
        for i in range(count):
            a = 2 * math.pi * i / count + (0.4 if count == 4 else 0)
            cupcake(ring * math.cos(a), y, ring * math.sin(a), icings[k % 3], cherry=y > 2.5)
            k += 1
    sphere('Body', (0, 3.82, 0), (0.12, 0.12, 0.12), 'gold_light', n=8, rings=4)   # a ball, no star: it read as a tree
    finish(note='a gold three-tier stand of cupcakes in chocolate, cream and red velvet icing, cherries on the top tier, a '
                'gold ball on its pole')


def d_carpet():
    decor('VipCarpet', 4, 2, 'Rug')
    K.rug('runner', border='gold', field='velvet', pin='gold_light', motif='gold', motif_inner='velvet_dark')
    finish(note='a red carpet runner with gold borders, a pin line and gold diamonds; its ends open, so two join')


# The letters V, I, P as bulb positions (x, y) on the marquee's face, as written; drawn at -x, since a guest
# facing the sign (it faces -Z) has +X on their left.
LETTERS = {
    'V': [(-1.95 + 0.11 * i, 6.0 - 0.36 * i) for i in range(6)] + [(-0.85 - 0.11 * i, 6.0 - 0.36 * i) for i in range(5)],
    'I': [(0.0, 6.0 - 0.36 * i) for i in range(6)],  # 4.2..6.0, drawn 0.1 higher (d_sign)
    'P': [(0.85, 6.0 - 0.36 * i) for i in range(6)] + [(1.3, 6.0), (1.72, 5.86), (1.85, 5.5), (1.72, 5.14), (1.3, 5.0)],
}


def arched(x, lo, hi, rise):
    """A panel's outline from (-x, lo) to (x, lo), up its sides to hi, under a shallow round arch."""
    head = list(reversed(K.round_arch_points(-x, x, hi, hi + rise, n=8)))
    return [(-x, lo), (x, lo)] + head


def d_sign():
    decor('VipSign', 2, 1, 'Wall')
    zb = 1.5 - 0.4                                   # the wall's inner face (MODELS.md, "Decor": Wall)
    lo, hi = 3.6, 6.4
    # The gold frame (its back on the wall) and the black marquee panel 0.03 proud of it.
    prism('Body', arched(2.58, lo - 0.12, hi, 0.47), zb - 0.34, zb, 'gold', plane='xy')
    prism('Body', arched(2.34, lo + 0.12, hi, 0.25), zb - 0.37, zb - 0.33, 'lacquer', plane='xy')
    zf = zb - 0.37
    for pts in LETTERS.values():                     # glowing bulbs, set into the panel (one part, rule 1)
        for x, y in pts:
            sphere('Glow_Warm_1', (-x, y + 0.1, zf - 0.05), (0.1, 0.1, 0.1), 'bulb', n=6, rings=3)
    border = arched(2.46, lo, hi, 0.36) + [(-2.46, lo)]      # small bulbs all round the gold frame
    for (xa, ya), (xb, yb) in zip(border, border[1:]):
        n = max(1, round(math.hypot(xb - xa, yb - ya) / 0.5))
        for i in range(n):
            t = i / n
            sphere('Glow_Warm_1', (xa + (xb - xa) * t, ya + (yb - ya) * t, zb - 0.38), (0.06, 0.06, 0.06), 'bulb',
                   n=5, rings=3)
    star(0, 6.5, zf, 0.2, 'gold_light')
    finish(note='a black marquee in a gold frame with a shallow arched top, "VIP" in lit bulbs, a '
                'border of small bulbs all round the frame, a gold star on its crown')


BUILD = {'VipRope': d_rope, 'VipSofa': d_sofa, 'VipCupcakes': d_cupcakes, 'VipCarpet': d_carpet, 'VipSign': d_sign}


def main():
    K.use_palette(PALETTE)
    K.start_set(SET)
    refused = []
    for i in IDS:
        if not K.want(f'Decor_{i}'):
            continue
        try:
            BUILD[i]()
        except K.Refused as e:
            print(str(e), flush=True)
            refused.append(i)
    K.end_set('The VIP lounge set (every location; the VIP Lobby pass), a draft', [([f'Decor_{i}' for i in IDS], 2.5, 2.0)])
    if refused:
        raise SystemExit(f'REFUSED: {refused}')


main()
