"""Frostfang Lodge (Location 2): the hotel kit's second set, a draft for August's review.

The 6 rooms and 2 amenities of Pieces.luau (location = 2), the Lobby, the
stair core (StairCore, StairCoreTop), the HotelSign and the 6 Location 2
decor pieces, each authored on tools/hotel_kit.py in the frames and with the
attachments of the Luau blockout (src/server/HotelKit.luau), so a delivered
model replaces geometry and nothing else (CLAUDE.md). The shared structure
(Lobby, stairs, sign) keeps the Haunted Manor's colliding boxes exactly:
only colour and dressing differ.

Cosy-frosty (GDD §6.6, §12, Appendix A.6): a timber lodge with log walls,
snow on every wall's top edge and icicles under it, icy blues, warm cocoa
browns and red plaid; chunky chamfered shapes; one 256 px palette atlas of
the lodge's own colours (hotel_kit.use_palette).

    blender -b --python-exit-code 1 -P tools/build_hotel_frostfang_lodge.py [-- nopreview] [-- only A,B]

Writes blender/hotel/frostfang_lodge/: fbx/<Name>.fbx, manifest.json,
validation.json, import_fixup.luau, review/contact_sheet.png, the .blend.
"""
import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import hotel_kit as K  # noqa: E402
from hotel_kit import (begin, finish, box, span, cyl, lathe, sphere, prism, attach, declare,  # noqa: E402
                       room_shell, picture, at, CELL, T)

SET = 'hotel/frostfang_lodge'
ROOMS = [('IglooRoom', 2, 2), ('IceCave', 2, 3), ('YetiDen', 3, 3), ('FrostLoft', 2, 3),
         ('GlacierSuite', 3, 3), ('AuroraDome', 3, 3)]
AMENITIES = ['CocoaLounge', 'AuroraDeck']
DECOR = ['IceBlock', 'CocoaMug', 'PrankBox', 'RockPile', 'SnowGlobe', 'AuroraLamp']

# The lodge's palette (Locations.luau id 2: ground 200,215,230 = 'ground', facade
# 120,160,200 = 'facade', trim 240,250,255 = 'trim'). A third value is a glow key.
PALETTE = [
    ('snow', (245, 250, 255)), ('snow_shade', (214, 228, 242)), ('frost', (196, 222, 244)),
    ('ice', (165, 212, 240)), ('ice_deep', (115, 175, 220)), ('ice_dark', (70, 120, 170)),
    ('glacier', (100, 170, 220)), ('facade', (120, 160, 200)), ('facade_dark', (85, 120, 160)),
    ('ground', (200, 215, 230)), ('trim', (240, 250, 255)),
    ('night', (30, 40, 78)), ('navy', (48, 62, 110)), ('sky', (90, 140, 220)),
    ('log', (158, 104, 64)), ('log_dark', (118, 76, 48)), ('wood', (140, 92, 58)),
    ('wood_dark', (90, 58, 40)), ('wood_light', (192, 140, 92)),
    ('pine', (58, 112, 92)), ('pine_dark', (38, 80, 70)),
    ('cocoa', (122, 78, 52)), ('cocoa_dark', (82, 52, 36)), ('cocoa_light', (178, 128, 92)),
    ('cream', (250, 240, 225)), ('red', (205, 62, 62)), ('red_dark', (140, 40, 48)),
    ('orange', (240, 140, 50)), ('yellow', (250, 212, 92)), ('gold', (226, 186, 96)),
    ('iron', (64, 70, 86)), ('grey', (120, 122, 132)),
    ('stone', (138, 140, 152)), ('stone_dark', (94, 96, 110)), ('stone_light', (178, 180, 192)),
    ('fur', (228, 228, 234)), ('fur_shade', (190, 196, 208)),
    ('mint', (150, 226, 200)), ('teal', (60, 190, 185)), ('violet', (150, 112, 220)),
    ('lilac', (186, 166, 232)), ('pink', (230, 90, 160)), ('pink_light', (246, 164, 204)),
    ('black', (32, 34, 44)), ('white', (246, 246, 250)), ('ink', (40, 46, 72)),
    ('flame', (255, 205, 120), 'Warm'), ('lamp', (255, 185, 110), 'Warm'),
    ('frostglow', (205, 230, 255), 'Cold'), ('aurora', (130, 255, 190), 'Magic'),
]


# --- Shared dressing ------------------------------------------------------------------------------

def flake(part, c, r, col, wall='back', t=0.06):
    """A six-armed snowflake of three crossed bars on a wall face (or the sign)."""
    for k in range(3):
        a = k * 60
        if wall == 'back':
            box(part, (0, 0, 0), (2 * r, r * 0.22, t), col, m=at(c, rz=a))
        else:
            box(part, (0, 0, 0), (t, r * 0.22, 2 * r), col, m=at(c, rx=a))
    for k in range(6):   # little tips, so it reads as a flake and not a star
        a = math.radians(k * 60)
        if wall == 'back':
            p = (c[0] + 0.7 * r * math.cos(a), c[1] + 0.7 * r * math.sin(a), c[2])
            box(part, (0, 0, 0), (r * 0.4, r * 0.14, t), col, m=at(p, rz=k * 60 + 90))
        else:
            p = (c[0], c[1] + 0.7 * r * math.sin(a), c[2] + 0.7 * r * math.cos(a))
            box(part, (0, 0, 0), (t, r * 0.14, r * 0.4), col, m=at(p, rx=-(k * 60 + 90)))


def icicle(part, x, y, z, length, r=0.13, col='ice'):
    lathe(part, [(0, y - length), (r, y)], col, n=5, base=(x, 0, z))


def snow_edges(W, D, icicles=True, col='snow'):
    """A snow cornice along the top of every wall's inner face, and icicles under it."""
    hw, hd, lip = W / 2 - T, D / 2 - T, 0.24
    span('Dressing', (-hw, 9.55, hd - lip), (hw, 10.0, hd), col, bevel=0.1)
    span('Dressing', (-hw, 9.55, -hd), (hw, 10.0, -hd + lip), col, bevel=0.1)
    span('Dressing', (-hw, 9.55, -hd + lip), (-hw + lip, 10.0, hd - lip), col, bevel=0.1)
    span('Dressing', (hw - lip, 9.55, -hd + lip), (hw, 10.0, hd - lip), col, bevel=0.1)
    if not icicles:
        return
    lengths = (0.9, 0.5, 0.7, 0.4, 1.1, 0.6)
    k = 0
    x = -hw + 0.8
    while x < hw - 0.6:
        icicle('Dressing', x, 9.6, hd - 0.12, lengths[k % 6]); k += 1; x += 1.3
    for sx in (-1, 1):
        z = -hd + 1.2
        while z < hd - 0.6:
            icicle('Dressing', sx * (hw - 0.12), 9.6, z, lengths[k % 6]); k += 1; z += 1.4


def lantern(x, y, z, wall, n, col='iron'):
    """A wall lantern: a bracket and a little iron-capped box, the flame Glow_Warm_<n>."""
    d = {'back': (0, -1), 'left': (1, 0), 'right': (-1, 0)}[wall]
    cx, cz = x + d[0] * 0.7, z + d[1] * 0.7
    box('Dressing', (x + d[0] * 0.05, y, z + d[1] * 0.05), (0.5 if wall == 'back' else 0.1, 0.8, 0.1 if wall == 'back' else 0.5), col, 0.03)
    box('Dressing', ((x + cx) / 2, y + 0.3, (z + cz) / 2), (abs(cx - x) + 0.12, 0.12, abs(cz - z) + 0.12), col)
    box('Dressing', (cx, y + 0.12, cz), (0.75, 0.14, 0.75), col, 0.03)
    box('Dressing', (cx, y - 1.0, cz), (0.75, 0.14, 0.75), col, 0.03)
    lathe('Dressing', [(0.45, y + 0.19), (0.1, y + 0.5), (0, y + 0.55)], 'red', n=4, base=(cx, 0, cz), phase=math.pi / 4)
    for ox in (-0.32, 0.32):
        for oz in (-0.32, 0.32):
            box('Dressing', (cx + ox, y - 0.45, cz + oz), (0.08, 1.0, 0.08), col)
    sphere(f'Glow_Warm_{n}', (cx, y - 0.45, cz), (0.22, 0.36, 0.22), 'flame', n=8, rings=4)


def window(c, size, wall='back', inner='night', frame='wood', flakes=True):
    """A window on a wall's inner face: a night pane, a snowy sill, a flake or two."""
    picture(c, size, frame, inner, wall)
    x, y, z = c
    sx, sy = size
    if wall == 'back':
        span('Dressing', (x - sx / 2 - 0.1, y - sy / 2 - 0.12, z - 0.34), (x + sx / 2 + 0.1, y - sy / 2 + 0.12, z), 'snow', 0.08)
        box('Dressing', (x, y, z - 0.15), (0.12, sy - 0.4, 0.06), frame)
        box('Dressing', (x, y, z - 0.15), (sx - 0.4, 0.12, 0.06), frame)
        if flakes:
            flake('Dressing', (x - sx / 4, y + sy / 4, z - 0.17), 0.22, 'white')
            flake('Dressing', (x + sx / 4, y - sy / 5, z - 0.17), 0.16, 'white')
    else:
        sgn = 1 if wall == 'left' else -1
        x0, x1 = sorted((x, x + 0.34 * sgn))
        span('Dressing', (x0, y - sy / 2 - 0.12, z - sx / 2 - 0.1), (x1, y - sy / 2 + 0.12, z + sx / 2 + 0.1), 'snow', 0.08)
        box('Dressing', (x + 0.15 * sgn, y, z), (0.06, sy - 0.4, 0.12), frame)
        box('Dressing', (x + 0.15 * sgn, y, z), (0.06, 0.12, sx - 0.4), frame)
        if flakes:
            flake('Dressing', (x + 0.17 * sgn, y + sy / 4, z - sx / 4), 0.22, 'white', wall)
            flake('Dressing', (x + 0.17 * sgn, y - sy / 5, z + sx / 4), 0.16, 'white', wall)


def aurora_ribbon(part, x0, x1, y, z, amp, col, wall='back', seg=6, h=0.35):
    """A wavy ribbon of tilted bars along a wall face (the northern lights)."""
    pts = [(x0 + (x1 - x0) * i / seg, y + amp * math.sin(i * 1.3)) for i in range(seg + 1)]
    for (ax, ay), (bx, by) in zip(pts, pts[1:]):
        ln = math.hypot(bx - ax, by - ay) + 0.08
        ang = math.degrees(math.atan2(by - ay, bx - ax))
        if wall == 'back':
            box(part, (0, 0, 0), (ln, h, 0.06), col, m=at(((ax + bx) / 2, (ay + by) / 2, z), rz=ang))
        else:
            box(part, (0, 0, 0), (0.06, h, ln), col, m=at((z, (ay + by) / 2, (ax + bx) / 2), rx=-ang))


def lodge_shell(w, d, paper=('log', 'log_dark'), wainscot='wood_dark', crown='snow', floor=('wood', 'wood_light'),
                rug=None, lamp=True, icicles=True):
    """room_shell in the lodge's dress: log or snow-block walls, a round doorway,
    the facade blue outside, a snow cornice and icicles, a lantern as the lamp."""
    W, D = w * CELL, d * CELL
    room_shell(w, d, paper=paper, wainscot=wainscot, crown=crown, outside='facade', floor=floor, rug=rug,
               lamp=False, lintel='round')
    snow_edges(W, D, icicles)
    if lamp:
        lantern(0, 8.6, D / 2 - T, 'back', 1)
    return W, D


def lodge_bed(D, frame='wood_light', quilt=('red', 'cream'), pillow='snow', head='log', head_col=None,
              mattress='cream', foot=True, part='Bed'):
    """A bed against the back wall, inside the blockout's bed box (x +-2, z D/2-6.15..D/2-0.4)."""
    zb, zf = D / 2 - T - 0.05, D / 2 - 6.1
    hw = 1.95
    for x in (-hw + 0.22, hw - 0.22):
        for z in (zf + 0.22, zb - 0.22):
            cyl(part, (x, 0, z), 0.2, 0.7, frame, n=6)
    span(part, (-hw, 0.6, zf), (hw, 1.1, zb), frame, bevel=0.08)
    span(part, (-hw + 0.1, 1.1, zf + 0.1), (hw - 0.1, 1.65, zb - 0.1), mattress, bevel=0.15)
    a, b = quilt
    span(part, (-hw + 0.02, 1.25, zf + 0.05), (hw - 0.02, 1.8, zf + 3.4), a, bevel=0.18)
    for x in (-1.1, 0.0, 1.1):          # plaid: stripes both ways, a hair proud of the quilt
        span(part, (x - 0.14, 1.79, zf + 0.15), (x + 0.14, 1.83, zf + 3.3), b)
    for z in (zf + 0.9, zf + 2.2):
        span(part, (-hw + 0.1, 1.8, z - 0.14), (hw - 0.1, 1.84, z + 0.14), b)
    span(part, (-hw + 0.02, 1.62, zf + 3.1), (hw - 0.02, 1.86, zf + 3.6), 'cream', bevel=0.08)
    span(part, (-1.3, 1.6, zb - 1.5), (1.3, 2.25, zb - 0.35), pillow, bevel=0.22)
    head_col = head_col or frame
    if head == 'log':
        for x in (-hw + 0.24, hw - 0.24):
            cyl(part, (x, 0.7, zb - 0.22), 0.22, 3.0, head_col, n=8)
            sphere(part, (x, 3.75, zb - 0.22), (0.26, 0.16, 0.26), 'snow', n=8, rings=3)
        for y in (2.0, 2.6, 3.2):
            cyl(part, (0, 0, 0), 0.26, 2 * hw - 0.9, head_col if y != 2.6 else 'log_dark', n=8,
                m=at((-hw + 0.45, y, zb - 0.22), rz=-90))
    elif head == 'ice':
        dome = [(1.9 * math.cos(math.pi * i / 8), 1.1 + 2.5 * math.sin(math.pi * i / 8)) for i in range(9)]
        prism(part, dome, zb - 0.3, zb, head_col or 'ice', plane='xy')
        span(part, (-1.9, 0.6, zb - 0.3), (1.9, 1.1, zb), head_col or 'ice')
        for x in (-0.95, 0.95):
            span(part, (x - 0.05, 2.5, zb - 0.34), (x + 0.05, 3.05, zb - 0.28), 'frost')
        for y in (2.45, 3.1):
            hwid = 1.9 * math.sqrt(max(0.0, 1 - ((y - 1.1) / 2.5) ** 2)) - 0.1
            span(part, (-hwid, y - 0.05, zb - 0.34), (hwid, y + 0.05, zb - 0.28), 'frost')
    if foot:
        cyl(part, (0, 0, 0), 0.24, 2 * hw - 0.2, frame, n=8, m=at((-hw + 0.1, 1.55, zf + 0.24), rz=-90))
    return zf, zb


def mug(part, c, r=0.32, h=0.6, col='red', band='cream'):
    x, y, z = c
    cyl(part, (x, y, z), r, h, col, n=8)
    cyl(part, (x, y + h * 0.4, z), r + 0.02, h * 0.2, band, n=8)
    cyl(part, (x, y + h - 0.04, z), r - 0.05, 0.06, 'cocoa', n=8)
    box(part, (x + r + 0.1, y + h * 0.5, z), (0.14, h * 0.55, 0.12), col)


def pine_tree(part, c, h=3.0, r=1.1, pot='wood'):
    x, y, z = c
    lathe(part, [(r * 0.45, y), (r * 0.55, y + 0.6), (r * 0.6, y + 0.7), (0, y + 0.7)], pot, n=8, base=(x, 0, z))
    cyl(part, (x, y + 0.7, z), 0.14, 0.4, 'wood_dark', n=6)
    for k, (y0, rr) in enumerate(((0.9, 1.0), (0.45, 0.78), (0.0, 0.55))):
        yy = y + 1.0 + k * h * 0.27
        lathe(part, [(rr * r, yy), (0, yy + h * 0.42)], 'pine' if k % 2 == 0 else 'pine_dark', n=8, base=(x, 0, z))
        lathe(part, [(rr * r * 0.6, yy + h * 0.17), (0, yy + h * 0.42 + 0.02)], 'snow', n=8, base=(x, 0, z))


# --- Rooms -----------------------------------------------------------------------------------------

def igloo_room():
    w, d = 2, 2
    begin('IglooRoom', 'Room', (w * CELL, 0.2, d * CELL), w=w, d=d)
    W, D = lodge_shell(w, d, paper=('snow', 'snow_shade'), wainscot='frost', crown='snow',
                       floor=('wood_light', 'wood'), rug=(5.0, 3.6, -2.4, 'red', 'cream'))
    lodge_bed(D, frame='wood_light', quilt=('red', 'cream'), head='ice', head_col='ice')
    # An ice-block dresser on the right wall, a mug of cocoa and a candle lantern on it.
    xr = W / 2 - T
    span('Furniture', (xr - 1.3, 0, -3.4), (xr - 0.02, 2.6, 0.2), 'ice', bevel=0.12)
    for y in (0.55, 1.35, 2.1):
        span('Furniture', (xr - 1.36, y - 0.3, -3.2), (xr - 1.2, y + 0.26, 0.0), 'frost', bevel=0.05)
        box('Furniture', (xr - 1.42, y - 0.02, -1.6), (0.12, 0.14, 0.5), 'wood_dark')
    span('Furniture', (xr - 1.36, 2.6, -3.46), (xr, 2.82, 0.26), 'snow', bevel=0.1)
    mug('Furniture', (xr - 0.7, 2.82, -2.6))
    cyl('Furniture', (xr - 0.65, 2.82, -0.8), 0.3, 0.12, 'iron', n=6)
    for oz in (-0.2, 0.2):
        for ox in (-0.2, 0.2):
            box('Furniture', (xr - 0.65 + ox, 3.3, -0.8 + oz), (0.06, 0.85, 0.06), 'iron')
    box('Furniture', (xr - 0.65, 3.76, -0.8), (0.5, 0.1, 0.5), 'iron')
    sphere('Glow_Warm_2', (xr - 0.65, 3.3, -0.8), (0.13, 0.24, 0.13), 'flame', n=6, rings=4)
    window((xr, 6.2, -1.6), (3.0, 2.2), 'right')
    picture((-3.0, 7.0, D / 2 - T), (1.6, 1.3), 'wood', 'sky')
    sphere('Dressing', (-3.0, 6.75, D / 2 - T - 0.13), (0.3, 0.3, 0.05), 'snow', n=8, rings=4)   # a snowman
    sphere('Dressing', (-3.0, 7.2, D / 2 - T - 0.14), (0.2, 0.2, 0.05), 'snow', n=8, rings=4)
    box('Dressing', (-2.9, 7.2, D / 2 - T - 0.2), (0.14, 0.05, 0.05), 'orange')
    picture((3.0, 7.0, D / 2 - T), (1.6, 1.3), 'wood', 'pine')
    flake('Dressing', (3.0, 7.0, D / 2 - T - 0.15), 0.32, 'white')
    finish(note='the starter room: snow-block walls, an igloo-dome headboard, an ice dresser with cocoa and a lantern')


def ice_cave():
    w, d = 2, 3
    begin('IceCave', 'Room', (w * CELL, 0.2, d * CELL), w=w, d=d)
    W, D = lodge_shell(w, d, paper=('ice', 'ice_deep'), wainscot='stone_dark', crown='snow',
                       floor=('stone', 'stone_light'), rug=(4.8, 4.0, -3.0, 'fur_shade', 'fur'))
    zb, zf = D / 2 - T - 0.05, D / 2 - 6.1
    # A stone slab bed under furs, a rock headboard.
    span('Bed', (-1.95, 0, zf), (1.95, 0.7, zb), 'stone_dark', bevel=0.15)
    span('Bed', (-1.85, 0.7, zf + 0.1), (1.85, 1.2, zb - 0.1), 'stone', bevel=0.12)
    span('Bed', (-1.9, 1.0, zf + 0.05), (1.9, 1.55, zf + 3.6), 'fur', bevel=0.22)
    for x in (-1.2, 0.0, 1.2):
        span('Bed', (x - 0.2, 1.54, zf + 0.2), (x + 0.2, 1.58, zf + 3.4), 'fur_shade')
    span('Bed', (-1.3, 1.2, zb - 1.5), (1.3, 1.85, zb - 0.35), 'snow', bevel=0.22)
    rock = [(-1.95, 0.0), (1.95, 0.0), (1.95, 2.6), (1.4, 3.4), (0.5, 3.1), (-0.3, 3.8), (-1.2, 3.2), (-1.95, 2.8)]
    prism('Bed', rock, zb - 0.32, zb, 'stone_dark', plane='xy')
    for x, y in ((-0.3, 3.8), (1.4, 3.4)):
        sphere('Bed', (x, y - 0.05, zb - 0.16), (0.36, 0.12, 0.16), 'snow', n=6, rings=3)
    # An ice-crystal cluster on a rock by the right wall; the middle crystal glows.
    xr = W / 2 - T
    span('Furniture', (xr - 1.5, 0, -6.2), (xr - 0.02, 0.9, -1.8), 'stone_dark', bevel=0.25)
    for z, h, r, colr in ((-5.4, 2.2, 0.36, 'ice'), (-4.5, 3.4, 0.45, None), (-3.5, 2.6, 0.38, 'ice_deep'),
                          (-2.6, 1.6, 0.3, 'ice')):
        lathe('Glow_Cold_1' if colr is None else 'Furniture',
              [(r, 0.9), (r, 0.9 + h * 0.75), (0, 0.9 + h)], 'frostglow' if colr is None else colr, n=6,
              base=(xr - 0.75, 0, z))
    lathe('Furniture', [(0.25, 0.9), (0.25, 1.9), (0, 2.4)], 'ice_deep', n=6, base=(xr - 1.15, 0, -4.9),
          m=None)
    # Longer stalactites over the back of the cave.
    for x, ln in ((-4.2, 1.8), (-2.6, 1.2), (2.4, 1.5), (4.0, 2.0)):
        icicle('Dressing', x, 9.6, D / 2 - T - 0.6, ln, r=0.22, col='ice_deep')
    window((-W / 2 + T, 6.4, -4.5), (3.0, 2.0), 'left')
    finish(note='an ice-brick cave: a stone slab bed under furs, a glowing crystal cluster, stalactites')


def yeti_den():
    w, d = 3, 3
    begin('YetiDen', 'Room', (w * CELL, 0.2, d * CELL), w=w, d=d)
    W, D = lodge_shell(w, d, floor=('wood', 'wood_light'), rug=(6.0, 5.0, -3.5, 'cream', 'ice_deep'))
    # Big yeti footprints on the rug.
    for x, z, sgn in ((-1.1, -4.9, 1), (1.0, -2.6, -1)):
        sphere('Dressing', (x, 0.26, z), (0.5, 0.03, 0.75), 'cream', n=8, rings=2)
        for k in range(3):
            sphere('Dressing', (x - 0.35 + 0.35 * k, 0.26, z + 0.95), (0.16, 0.03, 0.2), 'cream', n=6, rings=2)
    zb, zf = D / 2 - T - 0.05, D / 2 - 6.1
    zc = (zb + zf) / 2
    # A round fur nest with a blue blanket.
    lathe('Bed', [(1.35, 0.0), (1.95, 0.0), (1.95, 0.9), (1.75, 1.35), (1.4, 1.2)], 'fur', n=12,
          base=(0, 0, zc), scale=(1, 1.42), closed=True)
    lathe('Bed', [(0, 0.0), (1.45, 0.0), (1.45, 0.6), (0, 0.75)], 'fur_shade', n=12, base=(0, 0, zc), scale=(1, 1.42))
    lathe('Bed', [(0, 0.6), (1.0, 0.65), (0.6, 0.95), (0, 1.0)], 'ice_deep', n=10, base=(0, 0, zc - 0.8), scale=(1.2, 0.8))
    sphere('Bed', (0, 1.05, zc + 1.4), (0.8, 0.3, 0.45), 'snow', n=8, rings=4)
    # A stone stove with a glowing hearth and a log stack, on the right wall.
    xr = W / 2 - T
    span('Furniture', (xr - 1.8, 0, -4.6), (xr - 0.02, 2.6, -1.4), 'stone', bevel=0.2)
    span('Furniture', (xr - 1.86, 0.4, -3.6), (xr - 1.6, 1.8, -2.4), 'black', bevel=0.05)
    span('Furniture', (xr - 1.9, 2.6, -4.7), (xr, 2.85, -1.3), 'stone_dark', bevel=0.08)
    cyl('Furniture', (xr - 0.8, 2.85, -3.0), 0.35, 6.4, 'iron', n=8)
    sphere('Glow_Warm_2', (xr - 1.6, 0.85, -3.0), (0.2, 0.35, 0.45), 'flame', n=6, rings=4)
    for k, (y, z) in enumerate(((0.45, -7.4), (0.45, -6.4), (0.45, -5.4), (1.3, -6.9), (1.3, -5.9), (2.15, -6.4))):
        cyl('Furniture', (0, 0, 0), 0.45, 1.6, 'log' if k % 2 else 'wood_light', n=8,
            m=at((xr - 1.7, y, z), rz=-90))
    # A big window over the nest, crossed snowshoes on the left wall.
    window((0, 7.2, D / 2 - T), (3.6, 2.6), 'back')
    xl = -W / 2 + T
    for ang in (-25, 25):
        lathe('Dressing', [(0.5, -0.04), (0.62, -0.04), (0.62, 0.04), (0.5, 0.04)], 'wood_light', n=10, closed=True,
              scale=(1, 2.0), m=at((xl + 0.08, 6.4, -1.0), ry=90 + ang, rz=90))
    finish(note='a log den: a round fur nest, yeti footprints on the rug, a stone stove, a log stack')


def frost_loft():
    w, d = 2, 3
    begin('FrostLoft', 'Room', (w * CELL, 0.2, d * CELL), w=w, d=d)
    W, D = lodge_shell(w, d, paper=('wood_light', 'log'), wainscot='violet', crown='snow',
                       floor=('wood', 'wood_dark'), rug=(4.4, 4.4, -3.0, 'violet', 'lilac'))
    lodge_bed(D, frame='wood', quilt=('violet', 'lilac'), pillow='snow', head='log', head_col='log')
    # A knitting shelf on the right wall: balls of yarn and knitted icicles.
    xr = W / 2 - T
    z0, z1 = -6.6, -2.2
    span('Furniture', (xr - 1.2, 0, z0), (xr - 0.02, 5.0, z0 + 0.25), 'wood_dark', bevel=0.05)
    span('Furniture', (xr - 1.2, 0, z1 - 0.25), (xr - 0.02, 5.0, z1), 'wood_dark', bevel=0.05)
    span('Furniture', (xr - 0.2, 0, z0), (xr - 0.02, 5.0, z1), 'wood')
    cols = ['ice_deep', 'lilac', 'snow', 'violet', 'mint', 'pink_light']
    for i, y in enumerate((0.0, 1.7, 3.4, 4.8)):
        span('Furniture', (xr - 1.2, y, z0), (xr - 0.02, y + 0.2, z1), 'wood_dark', bevel=0.04)
        if y < 4.5:
            for j in range(3):
                z = z0 + 0.95 + j * 1.25
                sphere('Furniture', (xr - 0.65, y + 0.62, z), (0.42, 0.42, 0.42), cols[(i * 3 + j) % 6], n=8, rings=4)
            if i == 1:          # knitted icicles hanging under the second shelf
                for j in range(4):
                    icicle('Furniture', xr - 1.05, y, z0 + 0.7 + j * 1.0, 0.45, r=0.1)
    for z in (z0 + 1.2, z1 - 1.2):          # knitting needles stuck in the top ball
        cyl('Furniture', (0, 0, 0), 0.04, 1.0, 'gold', n=4, m=at((xr - 0.65, 4.0, z), rx=20 if z < -4 else -20))
    # Rafters under the roof, stars hanging from them.
    for z in (-5.0, 0.0, 5.0):
        span('Dressing', (-W / 2 + T, 8.95, z - 0.25), (W / 2 - T, 9.45, z + 0.25), 'wood_dark', bevel=0.05)
    for x, z in ((-4.0, -2.5), (-1.5, 2.5), (1.5, -2.5), (4.0, 2.5)):
        cyl('Dressing', (x, 8.3, z), 0.03, 0.7, 'iron', n=4)
        flake('Dressing', (x, 7.9, z), 0.35, 'ice', 'back')
    # An aurora window on the left wall.
    xl = -W / 2 + T
    picture((xl, 6.3, -4.5), (3.4, 2.4), 'wood', 'night', 'left')
    for k, colr in enumerate(('mint', 'teal', 'violet')):
        aurora_ribbon('Dressing', -5.8, -3.2, 6.7 - k * 0.4, xl + 0.16, 0.25, colr, wall='left', h=0.22)
    finish(note='a snow witch\'s loft: a violet-plaid log bed, a shelf of yarn and knitted icicles, an aurora window')


def glacier_suite():
    w, d = 3, 3
    begin('GlacierSuite', 'Room', (w * CELL, 0.2, d * CELL), w=w, d=d)
    W, D = lodge_shell(w, d, paper=('glacier', 'ice'), wainscot='ice_dark', crown='snow',
                       floor=('ice', 'frost'), rug=(6.4, 5.2, -3.5, 'gold', 'ice_deep'))
    zb, zf = D / 2 - T - 0.05, D / 2 - 6.1
    zc = (zb + zf) / 2
    # A round bed in a coil (the wyrm curls up), gold-banded, two crystal pillars at its head.
    lathe('Bed', [(1.45, 0.0), (1.95, 0.0), (1.95, 1.0), (1.7, 1.45), (1.45, 1.3)], 'ice_deep', n=14,
          base=(0, 0, zc), scale=(1, 1.4), closed=True)
    lathe('Bed', [(1.96, 0.45), (1.98, 0.45), (1.98, 0.62), (1.96, 0.62)], 'gold', n=14, base=(0, 0, zc),
          scale=(1, 1.4), closed=True)
    lathe('Bed', [(0, 0.0), (1.5, 0.0), (1.5, 0.75), (0, 0.9)], 'frost', n=14, base=(0, 0, zc), scale=(1, 1.4))
    lathe('Bed', [(0, 0.75), (1.1, 0.8), (0.7, 1.12), (0, 1.15)], 'navy', n=10, base=(0, 0, zc - 0.7), scale=(1.2, 0.9))
    sphere('Bed', (0, 1.15, zc + 1.4), (0.85, 0.3, 0.42), 'snow', n=8, rings=4)
    for x in (-1.65, 1.65):
        lathe('Bed', [(0.28, 0), (0.28, 3.6), (0, 4.4)], 'ice', n=6, base=(x, 0, zb - 0.3))
        cyl('Bed', (x, 3.4, zb - 0.3), 0.33, 0.2, 'gold', n=6)
    # An ice vanity with a round frost mirror and a crystal lamp, on the right wall.
    xr = W / 2 - T
    span('Furniture', (xr - 1.4, 0, -4.8), (xr - 0.02, 2.4, -1.2), 'ice', bevel=0.12)
    span('Furniture', (xr - 1.46, 2.4, -4.86), (xr, 2.6, -1.14), 'gold', bevel=0.06)
    lathe('Furniture', [(1.1, 0), (1.1, 0.16)], 'gold', n=12,
          m=at((xr - 0.18, 4.3, -3.0), rz=90))
    lathe('Furniture', [(0.9, 0), (0.9, 0.2)], 'frost', n=12,
          m=at((xr - 0.2, 4.3, -3.0), rz=90))
    lathe('Furniture', [(0.3, 2.6), (0.12, 2.8), (0.12, 3.3)], 'gold', n=6, base=(xr - 0.8, 0, -1.7))
    lathe('Glow_Cold_1', [(0.22, 3.3), (0.22, 3.75), (0, 4.15)], 'frostglow', n=6, base=(xr - 0.8, 0, -1.7))
    lantern(xr, 8.0, 2.8, 'right', 2)
    picture((-W / 2 + T, 6.4, -4.5), (3.2, 2.2), 'gold', 'ice_dark', 'left')
    flake('Dressing', (-W / 2 + T + 0.16, 6.4, -4.5), 0.6, 'snow', 'left')
    finish(note='a glacier suite: a gold-banded coiled round bed between crystal pillars, an ice vanity with a frost mirror')


def aurora_dome():
    w, d = 3, 3
    begin('AuroraDome', 'Room', (w * CELL, 0.2, d * CELL), w=w, d=d)
    W, D = lodge_shell(w, d, paper=('navy', 'night'), wainscot='ice_dark', crown='snow',
                       floor=('navy', 'ink'), rug=(6.4, 5.2, -3.5, 'lilac', 'violet'))
    # The northern lights across the back and both side walls (three Magic glows).
    hd, hw = D / 2 - T, W / 2 - T
    aurora_ribbon('Glow_Magic_1', -7.6, 7.6, 6.4, hd - 0.05, 0.6, 'aurora', seg=10, h=0.45)
    for n, sx in ((2, -1), (3, 1)):
        aurora_ribbon(f'Glow_Magic_{n}', -7.4, 2.4, 7.2, sx * (hw - 0.05), 0.5, 'aurora', wall='left', seg=7, h=0.4)
    # Stars.
    for k in range(18):
        x = -7.6 + (k * 3.7) % 15.2
        y = 4.2 + (k * 1.7) % 4.6
        if abs(y - 6.4) < 0.9:
            y -= 1.6
        sphere('Dressing', (x, y, hd - 0.04), (0.11, 0.11, 0.04), 'yellow' if k % 3 else 'white', n=6, rings=3)
    # A cloud bed: puffs of snow on a low base, a violet blanket.
    zb, zf = D / 2 - T - 0.05, D / 2 - 6.1
    span('Bed', (-1.95, 0, zf), (1.95, 0.6, zb), 'lilac', bevel=0.2)
    for x, z, r in ((-1.3, zf + 0.9, 0.65), (0.0, zf + 0.8, 0.7), (1.3, zf + 0.9, 0.65), (-1.35, zb - 1.0, 0.6),
                    (1.35, zb - 1.0, 0.6), (-1.35, zf + 2.6, 0.6), (1.35, zf + 2.6, 0.6)):
        sphere('Bed', (x, 0.95, z), (r, r * 0.6, r), 'snow', n=8, rings=4)
    span('Bed', (-1.6, 0.6, zf + 0.4), (1.6, 1.4, zb - 0.4), 'snow_shade', bevel=0.3)
    span('Bed', (-1.7, 1.2, zf + 0.25), (1.7, 1.6, zf + 3.2), 'violet', bevel=0.18)
    span('Bed', (-1.1, 1.4, zb - 1.4), (1.1, 1.95, zb - 0.45), 'lilac', bevel=0.2)
    # A telescope on a tripod by the right wall, pointing up at the lights.
    xr = W / 2 - T
    for k in range(3):
        a = k * math.tau / 3
        box('Furniture', (0, 0, 0), (0.12, 3.0, 0.12), 'wood_dark',
            m=at((xr - 1.1 + 0.45 * math.cos(a), 1.55, -3.0 + 0.45 * math.sin(a)), rx=10 * math.sin(a), rz=-10 * math.cos(a)))
    cyl('Furniture', (0, 0, 0), 0.25, 2.4, 'gold', n=8, r_top=0.34, m=at((xr - 1.1, 2.9, -3.6), rx=55))
    cyl('Furniture', (0, 0, 0), 0.36, 0.2, 'iron', n=8, m=at((xr - 1.1, 2.9, -3.6), rx=55) @ K.Matrix.Translation((0, 2.4, 0)))
    span('Furniture', (xr - 1.5, 0, -1.4), (xr - 0.05, 1.0, 0.2), 'wood', bevel=0.08)
    sphere('Furniture', (xr - 0.78, 1.5, -0.6), 0.5, 'sky', n=10, rings=6)
    cyl('Furniture', (xr - 0.78, 1.0, -0.6), 0.25, 0.12, 'gold', n=6)
    finish(note='a night-sky dome: the northern lights glowing across three walls, stars, a cloud bed, a telescope')


# --- Amenities -------------------------------------------------------------------------------------

def amenity(id_, **kw):
    w, d = 2, 2
    begin(id_, 'Amenity', (w * CELL, 0.2, d * CELL), w=w, d=d)
    return lodge_shell(w, d, **kw)


def cocoa_lounge():
    W, D = amenity('CocoaLounge', paper=('cocoa_light', 'cocoa'), wainscot='cocoa_dark', crown='snow',
                   floor=('wood', 'wood_light'), rug=(4.6, 3.0, -3.4, 'red', 'cream'))
    # A candy-cane-striped counter, a big cocoa pot, mugs, a jar of marshmallows.
    span('Centrepiece', (-1.95, 0, 0.0), (1.95, 3.2, 1.6), 'cocoa_dark', bevel=0.1)
    for i in range(7):
        x = -1.95 + 0.28 + i * 0.56
        span('Centrepiece', (x - 0.14, 0.2, -0.03), (x + 0.14, 3.0, 0.05), 'red' if i % 2 else 'cream')
    span('Centrepiece', (-1.95, 3.2, -0.1), (1.95, 3.45, 1.7), 'wood_light', bevel=0.06)
    lathe('Centrepiece', [(0.45, 3.45), (0.6, 3.7), (0.62, 4.4), (0.45, 4.6), (0.15, 4.75), (0, 4.8)], 'red', n=10,
          base=(-1.0, 0, 0.9))
    box('Centrepiece', (-0.3, 4.2, 0.9), (0.5, 0.14, 0.16), 'red')
    for x in (0.4, 1.2):
        mug('Centrepiece', (x, 3.45, 0.6), r=0.26, h=0.5, col='red' if x < 1 else 'ice_deep')
        for k in range(2):
            box('Centrepiece', (x - 0.08 + 0.16 * k, 3.98, 0.6), (0.14, 0.12, 0.14), 'white')
    lathe('Centrepiece', [(0.3, 3.45), (0.32, 4.1), (0.2, 4.2), (0.22, 4.35)], 'ice', n=8, base=(1.0, 0, 1.3))
    # The back shelf of mugs.
    zw = D / 2 - T
    span('Centrepiece', (-1.95, 0, zw - 1.0), (1.95, 5.2, zw), 'wood_dark', bevel=0.06)
    for y in (2.4, 3.8):
        span('Centrepiece', (-1.95, y - 0.1, zw - 1.6), (1.95, y, zw - 1.0), 'wood_light')
        for k, x in enumerate((-1.4, -0.45, 0.45, 1.4)):
            mug('Centrepiece', (x, y, zw - 1.3), r=0.24, h=0.45, col=('red', 'cream', 'ice_deep', 'pine')[k])
    # A striped awning with snow on it (dressing).
    for i in range(8):
        x = -2.4 + i * 0.6
        span('Dressing', (x, 7.0, zw - 1.5), (x + 0.6, 7.45, zw - 0.02), 'red' if i % 2 else 'cream', bevel=0.05)
    span('Dressing', (-2.45, 7.45, zw - 1.45), (2.45, 7.65, zw - 0.02), 'snow', bevel=0.08)
    window((-W / 2 + T, 6.2, -2.4), (2.6, 2.0), 'left')
    finish(note='a cocoa bar: a candy-cane counter, a big red cocoa pot, mugs with marshmallows, a snowy awning')


def aurora_deck():
    W, D = amenity('AuroraDeck', paper=('log', 'log_dark'), wainscot='wood_dark', crown='snow',
                   floor=('wood_light', 'wood'), rug=None, lamp=False)
    zw = D / 2 - T
    lantern(W / 2 - T, 8.2, -2.0, 'right', 1)
    # A wide window on the back wall with the northern lights in it.
    picture((0, 6.2, zw), (8.4, 4.2), 'wood', 'night')
    for x in (-1.4, 1.4):
        box('Dressing', (x, 6.2, zw - 0.15), (0.14, 3.8, 0.06), 'wood')
    span('Dressing', (-4.35, 3.85, zw - 0.4), (4.35, 4.15, zw), 'snow', bevel=0.1)
    aurora_ribbon('Glow_Magic_1', -3.8, 3.8, 6.8, zw - 0.16, 0.5, 'aurora', seg=8, h=0.4)
    aurora_ribbon('Glow_Magic_2', -3.6, 3.6, 5.6, zw - 0.16, 0.4, 'aurora', seg=8, h=0.25)
    for x, y in ((-3.2, 7.7), (-1.0, 7.9), (2.3, 7.6), (3.4, 5.0), (-2.6, 4.9)):
        sphere('Dressing', (x, y, zw - 0.16), (0.1, 0.1, 0.04), 'white', n=6, rings=3)
    # Two deck chairs facing the window, plaid blankets, a little table with mugs between.
    for sx in (-1, 1):
        x = sx * 1.25
        span('Centrepiece', (x - 0.7, 0.0, 0.0), (x + 0.7, 0.9, 2.0), 'wood', bevel=0.08)
        prism('Centrepiece', [(0.0, 0.9), (0.4, 0.9), (-0.45, 2.6), (-0.8, 2.5)], x - 0.7, x + 0.7, 'wood', plane='zy')
        span('Centrepiece', (x - 0.6, 0.9, 0.3), (x + 0.6, 1.05, 1.9), 'red' if sx < 0 else 'ice_deep', bevel=0.05)
        for z in (0.7, 1.4):
            span('Centrepiece', (x - 0.6, 1.05, z - 0.1), (x + 0.6, 1.07, z + 0.1), 'cream')
    span('Centrepiece', (-0.4, 0, 2.3), (0.4, 1.2, 3.0), 'wood_dark', bevel=0.06)
    mug('Centrepiece', (-0.15, 1.2, 2.65), r=0.16, h=0.32)
    finish(note='a viewing deck: a wide window with the northern lights glowing in it, two deck chairs with plaid blankets')


# --- The lobby, the stair core and the sign (the Haunted Manor's colliding boxes, re-dressed) -----

def lobby():
    begin('Lobby', 'Lobby', (72, 0.2, 12), root_centre=(0, 0.1, 6))
    declare('Rug', False)       # the blockout's Rug does not collide either
    nx, nz = 12, 2
    tw, td = 71.0 / nx, 11.0 / nz
    for i in range(nx):
        for j in range(nz):
            x0, z0 = -35.5 + i * tw, 0.5 + j * td
            span('Rug', (x0, 0, z0), (x0 + tw, 0.1, z0 + td), 'wood' if (i + j) % 2 else 'wood_light', bevel=0.02)
    span('Rug', (-2.2, 0.1, 0.5), (2.2, 0.13, 6.0), 'cream')
    span('Rug', (-1.9, 0.13, 0.5), (1.9, 0.15, 6.0), 'red')
    for z in (1.5, 3.2, 4.9):
        span('Rug', (-1.9, 0.15, z - 0.12), (1.9, 0.16, z + 0.12), 'cream')
    # The front desk: the blockout's box (x -17..-7, z 8..10, top at 3.8), a log front.
    span('Desk', (-17, 0, 8), (-7, 3.5, 10), 'log_dark', bevel=0.1)
    for y in (0.55, 1.45, 2.35):
        cyl('Desk', (0, 0, 0), 0.42, 9.8, 'log', n=8, m=at((-16.9, y, 8.35), rz=-90))
    for x in (-15.2, -12, -8.8):
        flake('Desk', (x, 1.75, 7.9), 0.45, 'white')
    span('Desk', (-17.2, 3.5, 7.8), (-6.8, 3.8, 10.2), 'wood_light', bevel=0.05)
    span('Desk', (-17.2, 3.75, 9.6), (-6.8, 3.82, 10.2), 'snow')
    lathe('Desk', [(0.3, 3.8), (0.3, 3.85), (0.22, 4.0), (0.05, 4.2), (0, 4.25)], 'gold', n=8, base=(-14.5, 0, 8.6))
    span('Desk', (-10.4, 3.8, 8.3), (-9.0, 3.95, 9.3), 'red', bevel=0.03)
    # The till: the blockout's boxes (x 10.5..13.5, z 8..10, up to 4.7).
    span('Till', (10.5, 0, 8), (13.5, 3.5, 10), 'log_dark', bevel=0.1)
    span('Till', (11, 3.5, 8.3), (13, 4.1, 9.7), 'red', bevel=0.08)
    prism('Till', [(8.3, 4.1), (9.7, 4.1), (9.7, 4.7), (8.9, 4.7)], 11.1, 12.9, 'red', plane='zy')
    for k in range(3):
        box('Till', (11.5 + k * 0.5, 4.15, 8.45), (0.3, 0.12, 0.3), 'gold')
    span('Till', (11.2, 1.8, 7.96), (12.8, 2.8, 8.1), 'gold', bevel=0.04)
    # The front arch: log pillars and a snowy timber gable (opening 9 wide, 9 tall at its sides).
    for name, x in (('ArchLeft', -5), ('ArchRight', 5)):
        span(name, (x - 0.5, 0, 0), (x + 0.5, 0.6, 1), 'stone_dark', bevel=0.08)
        cyl(name, (x, 0.6, 0.5), 0.42, 7.8, 'log', n=8)
        span(name, (x - 0.5, 8.4, 0), (x + 0.5, 9.0, 1), 'wood_dark', bevel=0.08)
    outline = [(-5.5, 9.0), (5.5, 9.0), (5.5, 9.5), (0, 11.2), (-5.5, 9.5)]
    prism('ArchTop', outline, 0.05, 0.95, {'front': 'facade', 'back': 'facade', 'rest': 'wood_dark'}, plane='xy')
    snow = [(-5.9, 9.4), (-5.5, 9.45), (0, 11.15), (5.5, 9.45), (5.9, 9.4), (5.9, 9.75), (0, 11.75), (-5.9, 9.75)]
    prism('ArchTop', snow, 0.0, 1.0, 'snow', plane='xy')
    flake('ArchTop', (0, 10.1, 0.03), 0.5, 'trim')
    for x in (-4.2, -2.6, 2.4, 4.0):
        icicle('Dressing', x, 9.0, 0.5, 0.5 + 0.2 * (abs(x) % 2), r=0.12)
    # The lantern hanging under the arch, and the desk lamp.
    cyl('Dressing', (0, 9.2, 1.5), 0.05, 1.5, 'iron', n=4)
    box('Dressing', (0, 9.2, 1.5), (0.8, 0.12, 0.8), 'iron')
    box('Dressing', (0, 7.8, 1.5), (0.8, 0.12, 0.8), 'iron')
    for dx in (-0.36, 0.36):
        for dz in (-0.36, 0.36):
            box('Dressing', (dx, 8.5, 1.5 + dz), (0.08, 1.3, 0.08), 'iron')
    sphere('Glow_Warm_1', (0, 8.5, 1.5), (0.3, 0.45, 0.3), 'lamp', n=8, rings=5)
    cyl('Dressing', (-12, 3.8, 10.0), 0.3, 0.1, 'iron', n=8)
    cyl('Dressing', (-12, 3.9, 10.0), 0.06, 1.75, 'iron', n=6)
    lathe('Dressing', [(0.75, 5.75), (0.35, 6.55), (0.3, 6.6)], 'red', n=8, base=(-12, 0, 10.0))
    sphere('Glow_Warm_2', (-12, 6.0, 10.0), (0.22, 0.22, 0.22), 'lamp', n=8, rings=4)
    # Snowy pine trees in tubs in the far corners.
    for k, x in enumerate((-33.5, 33.5)):
        pine_tree(f'Planter_{k + 1}', (x, 0, 9.5), h=5.0, r=1.1)
    for aname, (pos, look) in K.blockout_attachments('Lobby').items():
        attach(aname, pos, look)
    finish(note='a plank floor with a red runner, a log desk with snowflakes, a snowy timber gable over the entrance')


def stairs(top):
    name = 'StairCoreTop' if top else 'StairCore'
    begin(name, 'Stairs', (12, 0.2, 12))
    # Every walked box is the blockout's, exactly (K.blockout_stairs); only colour and chamfers are added.
    for sname, (c, s) in K.blockout_stairs(top).items():
        c, s = K.Vector(c), K.Vector(s)
        lo, hi = c - s / 2, c + s / 2
        if sname.startswith(('Step_', 'Landing')):
            # Their ends lie in the core walls' outer faces: the wall's own colour there.
            ends = {'top': 'red', 'left': 'log_dark', 'right': 'log_dark', 'rest': 'wood_dark'}
            if sname == 'Landing':
                ends['back'] = 'log_dark'
            box(sname, c, s, ends, bevel=0.06)
        elif sname.startswith('Wall_') or sname == 'Divider':
            h = hi.y
            bands = [(0, 1.0, 'wood_dark')]
            if sname == 'Divider':
                bands.append((1.0, h - 0.4, 'wood'))
            else:
                n = int((h - 1.4) / 0.9)
                k = (h - 1.4) / n
                bands += [(1.0 + i * k, 1.0 + (i + 1) * k, 'log' if i % 2 else 'log_dark') for i in range(n)]
            bands.append((h - 0.4, h, 'snow'))
            outer = {'Wall_Left': 'left', 'Wall_Right': 'right', 'Wall_Back': 'back'}.get(sname)
            for y0, y1, colr in bands:   # the outer face one colour: the step ends lie in it
                span(sname, (lo.x, y0, lo.z), (hi.x, y1, hi.z), {outer: 'log_dark', 'rest': colr} if outer else colr,
                     bevel=0.04)
        elif sname == 'Rail_Top':
            span(sname, (lo.x, hi.y - 0.35, lo.z), (hi.x, hi.y, hi.z), 'wood', bevel=0.06)
            span(sname, (lo.x, lo.y, lo.z + 0.05), (hi.x, lo.y + 0.3, hi.z - 0.05), 'wood_dark', bevel=0.04)
            span(sname, (lo.x, lo.y, lo.z), (lo.x + 0.4, hi.y, hi.z), 'wood_dark', bevel=0.05)
            span(sname, (hi.x - 0.4, lo.y, lo.z), (hi.x, hi.y, hi.z), 'wood_dark', bevel=0.05)
            x = lo.x + 0.9
            while x < hi.x - 0.6:
                cyl(sname, (x, lo.y + 0.3, c.z), 0.1, s.y - 0.65, 'wood_light', n=6)
                x += 0.6
    for aname, (pos, look) in K.blockout_attachments('Stairs').items():
        attach(aname, pos, look)
    # A lantern over the flight up, high on the left wall, and a snowy-mountain picture over the landing.
    lantern(-6 + T, 11.6, -1.0, 'left', 1)
    yp = 9.6 if not top else 10.6
    picture((0, yp, 6 - T), (2.6, 2.4), 'wood', 'sky')
    prism('Dressing', [(-1.0, yp - 0.95), (1.0, yp - 0.95), (0.25, yp + 0.6), (-0.05, yp + 0.3), (-0.4, yp + 0.75)],
          6 - T - 0.16, 6 - T - 0.1, 'ice_deep', plane='xy')
    prism('Dressing', [(-0.62, yp + 0.3), (-0.4, yp + 0.75), (-0.2, yp + 0.47)], 6 - T - 0.2, 6 - T - 0.14, 'snow', plane='xy')
    finish(note='the walker-proven switchback in logs, red-carpeted, snow on the walls\' tops' + (', railed round the stairwell' if top else ''))


def hotel_sign():
    begin('HotelSign', 'Sign', (16, 0.2, 1))
    for name, x in (('PostLeft', -7), ('PostRight', 7)):
        span(name, (x - 0.4, 0, -0.4), (x + 0.4, 0.5, 0.4), 'stone_dark', bevel=0.06)
        # The post ends under the Board (bottom y 5): its ring never reaches the board's text face.
        lathe(name, [(0.32, 0.5), (0.32, 4.6), (0.4, 4.8), (0.4, 5.0)], 'log', n=8, base=(x, 0, 0))
    # The Board: a plain box, its front (-Z) the SurfaceGui's face.
    box('Board', (0, 8, 0), (16, 6, 0.6), {'front': 'navy', 'back': 'facade_dark', 'rest': 'wood'}, bevel=0.08)
    # A crest over it: a snowy timber gable with a lit snowflake; icicles under the board.
    prism('Crest', [(-6, 11), (6, 11), (0, 13.2)], -0.25, 0.25, {'front': 'facade', 'back': 'facade', 'rest': 'wood_dark'},
          plane='xy')
    prism('Crest', [(-6.6, 10.95), (-6.0, 10.95), (0, 13.15), (6.0, 10.95), (6.6, 10.95), (6.6, 11.3), (0, 13.75),
                    (-6.6, 11.3)], -0.35, 0.35, 'snow', plane='xy')
    span('Crest', (-8, 10.95, -0.35), (8, 11.35, 0.35), 'snow', bevel=0.12)
    declare('Crest', False)
    flake('Glow_Cold_1', (0, 12.0, -0.3), 0.55, 'frostglow')
    for k, x in enumerate((-6.5, -4.8, -2.4, -0.6, 1.5, 3.6, 5.6, 7.0)):
        icicle('Crest', x, 5.0, 0.0, (0.6, 0.9, 0.45, 1.0)[k % 4], r=0.13)
    finish(note='log posts and a 16 x 6 board for the SurfaceGui, a snowy gable crest with a lit snowflake, icicles')


# --- Decor (origin at the base centre, front -Z, at most 4 x 4 x 7) -------------------------------

def decor(id_, fw, fd):
    begin(f'Decor_{id_}', 'Decor', (fw, 0.2, fd))
    declare('Body', False)          # the blockout's Body does not collide


def d_ice_block():
    decor('IceBlock', 3.0, 3.0)
    span('Body', (-1.3, 0, -1.3), (1.3, 2.4, 1.3), 'ice', bevel=0.25)
    span('Body', (-1.0, 2.38, -1.0), (1.0, 2.5, 1.0), 'snow', bevel=0.06)
    for x, y in ((-0.85, 1.9), (0.9, 0.6)):           # frost glints on the front
        span('Body', (x - 0.25, y - 0.05, -1.34), (x + 0.25, y + 0.05, -1.28), 'white')
    # A little orange fish frozen in it, showing at the front.
    fish = [(-0.5, 1.2), (0.0, 1.5), (0.4, 1.3), (0.7, 1.55), (0.7, 0.85), (0.4, 1.1), (0.0, 0.9)]
    prism('Body', fish, -1.36, -1.3, 'orange', plane='xy')
    box('Body', (-0.25, 1.25, -1.37), (0.1, 0.1, 0.04), 'black')
    finish(note='a chamfered ice block with a snow cap and a little orange fish frozen inside')


def d_cocoa_mug():
    decor('CocoaMug', 3.0, 3.0)
    lathe('Body', [(0.9, 0), (0.95, 0.1), (1.0, 1.7), (1.02, 1.8), (0.9, 1.8), (0.9, 1.65), (0, 1.65)], 'red', n=12)
    lathe('Body', [(1.01, 0.7), (1.04, 0.7), (1.04, 1.0), (1.01, 1.0)], 'cream', n=12, closed=True)
    lathe('Body', [(0, 1.6), (0.9, 1.6), (0.9, 1.68), (0, 1.68)], 'cocoa', n=12)
    lathe('Body', [(0.28, -0.08), (0.36, -0.08), (0.36, 0.08), (0.28, 0.08)], 'red', n=10, closed=True,
          m=at((1.12, 0.95, 0), rx=90), scale=(1, 1.4))
    for x, z in ((-0.3, -0.2), (0.25, 0.1), (-0.05, 0.4), (0.35, -0.35)):
        box('Body', (x, 1.78, z), (0.32, 0.28, 0.32), 'white', bevel=0.06)
    for k, (x, z) in enumerate(((-0.2, 0.0), (0.25, -0.1))):   # curls of steam
        lathe('Body', [(0.12, -0.05), (0.18, -0.05), (0.18, 0.05), (0.12, 0.05)], 'white', n=8, closed=True,
              m=at((x, 2.4 + k * 0.5, z), rx=90))
    flake('Body', (0, 1.32, -1.0), 0.25, 'white')
    finish(note='a giant red mug of cocoa with marshmallows, steam curls and a snowflake')


def d_prank_box():
    decor('PrankBox', 2.4, 2.4)
    span('Body', (-0.9, 0, -0.9), (0.9, 1.8, 0.9), 'pink', bevel=0.1)
    for x, y in ((-0.45, 0.5), (0.4, 1.25), (0.5, 0.45), (-0.4, 1.35)):
        cyl('Body', (0, 0, 0), 0.16, 0.04, 'yellow', n=8, m=at((x, y, -0.88), rx=-90))
    span('Body', (-0.95, 1.8, -0.95), (0.95, 1.95, 0.95), 'pink_light', bevel=0.04)
    span('Body', (-0.95, 1.95, 0.85), (0.95, 3.6, 0.95), 'pink_light', bevel=0.04)   # the lid, open
    cyl('Body', (0, 0, 0), 0.08, 0.18, 'gold', n=6, m=at((0.9, 1.0, 0), rz=-90))
    box('Body', (1.1, 1.2, 0), (0.1, 0.5, 0.1), 'gold')
    for k in range(5):                                       # the spring
        cyl('Body', (0, 1.95 + k * 0.28, 0), 0.32 - 0.02 * k, 0.12, 'stone_light', n=8)
    sphere('Body', (0, 3.75, 0), (0.62, 0.6, 0.62), 'snow', n=10, rings=6)     # a snowman's head pops out
    lathe('Body', [(0.06, 0), (0, 0.45)], 'orange', n=6, m=at((0, 3.75, -0.58), rx=-90))
    for x in (-0.22, 0.22):
        sphere('Body', (x, 3.95, -0.55), 0.07, 'black', n=6, rings=3)
    cyl('Body', (0, 4.25, 0), 0.5, 0.12, 'red', n=10)
    cyl('Body', (0, 4.37, 0), 0.32, 0.45, 'red', n=10)
    finish(note='a pink polka-dot jack-in-the-box with a snowman\'s head on the spring')


def d_rock_pile():
    decor('RockPile', 3.6, 3.6)
    for (x, y, z), r in (((-0.8, 0.6, 0.3), (0.95, 0.6, 0.85)), ((0.75, 0.5, 0.5), (0.85, 0.5, 0.8)),
                         ((0.1, 0.45, -0.8), (0.8, 0.45, 0.7)), ((-0.1, 1.3, 0.2), (0.7, 0.55, 0.65)),
                         ((0.15, 1.95, 0.1), (0.45, 0.35, 0.42))):
        sphere('Body', (x, y, z), r, 'stone' if x < 0 else 'stone_dark', n=7, rings=4)
    for (x, y, z), r in (((0.15, 2.22, 0.1), (0.36, 0.1, 0.34)), ((-0.35, 1.72, 0.35), (0.4, 0.1, 0.35)),
                         ((-1.05, 1.1, 0.3), (0.5, 0.1, 0.45)), ((0.95, 0.92, 0.6), (0.45, 0.08, 0.4)),
                         ((0.15, 0.85, -0.95), (0.4, 0.08, 0.35))):
        sphere('Body', (x, y, z), r, 'snow', n=7, rings=3)
    finish(note='a pile of round grey stones with snow caps')


def d_snow_globe():
    decor('SnowGlobe', 2.6, 2.6)
    lathe('Body', [(1.1, 0), (1.15, 0.1), (1.0, 0.7), (0.85, 0.75), (0, 0.75)], 'wood', n=12)
    lathe('Body', [(1.11, 0.25), (1.14, 0.25), (1.14, 0.45), (1.11, 0.45)], 'gold', n=12, closed=True)
    lathe('Body', [(0, 0.75), (0.7, 0.75), (0.86, 1.1), (0.9, 1.55), (0.82, 1.95), (0.58, 2.25), (0.28, 2.42),
                   (0, 2.46)], 'ice', n=12)
    # The scene inside, shown on the dome's front (opaque: MODELS.md has no glass part for decor).
    prism('Body', [(-0.62, 0.95), (0.62, 0.95), (0.55, 1.15), (-0.55, 1.15)], -0.93, -0.8, 'snow', plane='xy')
    prism('Body', [(-0.45, 1.15), (0.05, 1.15), (-0.2, 2.0)], -0.95, -0.85, 'pine', plane='xy')
    prism('Body', [(0.12, 1.15), (0.55, 1.15), (0.55, 1.45), (0.335, 1.68), (0.12, 1.45)], -0.95, -0.8, 'red', plane='xy')
    for x, y in ((-0.5, 1.75), (0.4, 1.95), (0.1, 2.2), (-0.15, 1.45), (0.6, 1.6)):
        sphere('Body', (x, y, -0.86), (0.05, 0.05, 0.03), 'white', n=6, rings=3)
    finish(note='an ice-blue snow globe on a wooden base with a gold band, a pine and a red cabin on its front')


def d_aurora_lamp():
    decor('AuroraLamp', 2.4, 2.4)
    lathe('Body', [(0.8, 0), (0.85, 0.1), (0.6, 0.35), (0.15, 0.45), (0.12, 3.6), (0.2, 3.7)], 'wood', n=10)
    lathe('Body', [(0.82, 0.12), (0.86, 0.12), (0.86, 0.22), (0.82, 0.22)], 'gold', n=10, closed=True)
    lathe('Glow_Magic_1', [(0.0, 3.7), (0.9, 3.75), (1.0, 4.4), (0.75, 5.0), (0.3, 5.3), (0, 5.35)], 'aurora', n=10)
    lathe('Body', [(1.0, 4.3), (1.04, 4.3), (1.04, 4.5), (1.0, 4.5)], 'violet', n=10, closed=True)
    sphere('Body', (0, 5.45, 0), (0.18, 0.14, 0.18), 'gold', n=6, rings=3)
    finish(note='a standing lamp whose rounded shade glows aurora green, banded violet')


DECOR_BUILD = {'IceBlock': d_ice_block, 'CocoaMug': d_cocoa_mug, 'PrankBox': d_prank_box,
               'RockPile': d_rock_pile, 'SnowGlobe': d_snow_globe, 'AuroraLamp': d_aurora_lamp}
ROOM_BUILD = {'IglooRoom': igloo_room, 'IceCave': ice_cave, 'YetiDen': yeti_den, 'FrostLoft': frost_loft,
              'GlacierSuite': glacier_suite, 'AuroraDome': aurora_dome}
AMENITY_BUILD = {'CocoaLounge': cocoa_lounge, 'AuroraDeck': aurora_deck}


def main():
    K.use_palette(PALETTE)
    K.start_set(SET)
    order = ([('IglooRoom', igloo_room), ('Lobby', lobby), ('StairCore', lambda: stairs(False)),
              ('StairCoreTop', lambda: stairs(True)), ('HotelSign', hotel_sign)]
             + [(n, f) for n, f in ROOM_BUILD.items() if n != 'IglooRoom']
             + list(AMENITY_BUILD.items())
             + [(f'Decor_{n}', f) for n, f in DECOR_BUILD.items()])
    refused = []
    for name, fn in order:
        if not K.want(name):
            continue
        try:
            fn()
        except K.Refused as e:
            print(str(e), flush=True)
            refused.append(name)
    rows = [(['Lobby', 'HotelSign'], 8, 1.0),
            ([n for n, _, _ in ROOMS], 5, 1.0),
            (list(AMENITY_BUILD) + ['StairCore', 'StairCoreTop'], 5, 1.0),
            ([f'Decor_{n}' for n in DECOR], 2.5, 2.0)]
    K.end_set('Frostfang Lodge hotel kit (Location 2), first draft', rows)
    if refused:
        raise SystemExit(f'REFUSED: {refused}')


main()
