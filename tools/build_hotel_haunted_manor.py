"""Haunted Manor (Location 1): the hotel kit's first set, a draft for August's review.

The 8 rooms and 5 amenities of GDD §5.2 and Pieces.luau, the Lobby, the stair
core (StairCore, and StairCoreTop with its rail), the HotelSign and the 15
Location 1 decor pieces, each authored on tools/hotel_kit.py in the frames
and with the attachments of the Luau blockout (src/server/HotelKit.luau), so
a delivered model replaces geometry and nothing else (CLAUDE.md).

Cozy creepy (GDD §12): saturated purples, teals, pumpkin orange, moonlight
blue; chunky shapes with chamfered edges; one 256 px palette atlas.

    blender -b --python-exit-code 1 -P tools/build_hotel_haunted_manor.py [-- nopreview]

Writes blender/hotel/haunted_manor/: fbx/<Name>.fbx, manifest.json,
validation.json, import_fixup.luau, review/contact_sheet.png, the .blend.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import hotel_kit as K  # noqa: E402
from hotel_kit import (begin, finish, box, span, cyl, lathe, sphere, prism, attach, declare,  # noqa: E402
                       room_shell, picture, arch_points, CELL, WALL, T, want)

SET = 'hotel/haunted_manor'
ROOMS = [  # id, w, d (Pieces.luau)
    ('StandardRoom', 2, 2), ('GardenRoom', 2, 2), ('AtticRoom', 2, 2), ('SarcophagusSuite', 2, 3),
    ('PotionLoft', 2, 3), ('DenRoom', 3, 3), ('CoffinSuite', 3, 3), ('OperaSuite', 3, 3)]
AMENITIES = ['SnackBar', 'MusicRoom', 'GraveyardGarden', 'QuietLibrary', 'OrganHall']
DECOR = ['PuddleRug', 'SnackBasket', 'RecordPlayer', 'Candles', 'Planter', 'AntiqueWardrobe',
         'BlackoutCurtains', 'SandTray', 'CatBasket', 'Cauldron', 'SteakPlatter', 'MoonWindow',
         'PipeOrgan', 'SoundproofWalls', 'Chandelier']


# --- Shared furniture ------------------------------------------------------------------------

def bed(D, frame='wood_dark', blanket='violet', pillow='cream', head='gothic', head_col=None,
        foot=True, part='Bed', mattress='cream'):
    """A bed against the back wall, inside the blockout's bed box (x +-2, z D/2-6.15..D/2-0.4)."""
    zb, zf = D / 2 - T - 0.05, D / 2 - 6.1
    hw = 1.95
    head_col = head_col or frame
    for x in (-hw + 0.2, hw - 0.2):
        for z in (zf + 0.2, zb - 0.2):
            box(part, (x, 0.5, z), (0.35, 0.8, 0.35), frame, bevel=0.06)
    span(part, (-hw, 0.6, zf), (hw, 1.1, zb), frame, bevel=0.08)
    span(part, (-hw + 0.1, 1.1, zf + 0.1), (hw - 0.1, 1.65, zb - 0.1), mattress, bevel=0.15)
    span(part, (-hw + 0.02, 1.25, zf + 0.05), (hw - 0.02, 1.8, zf + 3.4), blanket, bevel=0.18)
    span(part, (-hw + 0.02, 1.62, zf + 3.1), (hw - 0.02, 1.84, zf + 3.6), 'cream', bevel=0.08)  # turned sheet
    span(part, (-1.3, 1.6, zb - 1.5), (1.3, 2.25, zb - 0.35), pillow, bevel=0.22)
    if head == 'gothic':
        pts = [(-hw, 0.0), (hw, 0.0), (hw, 3.2)] + [(x, y) for x, y in reversed(
            arch_points(-hw, hw, 3.2, 5.0, n=3))][1:-1] + [(-hw, 3.2)]
        prism(part, pts, zb - 0.3, zb, {'rest': head_col}, plane='xy')
        for x in (-hw + 0.15, hw - 0.15):
            sphere(part, (x, 3.45, zb - 0.15), (0.24, 0.24, 0.24), 'gold', n=8, rings=4)
    if foot:
        span(part, (-hw, 0.6, zf), (hw, 2.3, zf + 0.25), frame, bevel=0.08)
    return zf, zb


def sconce(x, y, z, wall, n):
    """An extra wall light: bracket in Dressing, flame Glow_Warm_<n>."""
    dz = {'back': (0, 0, -1), 'left': (1, 0, 0), 'right': (-1, 0, 0)}[wall]
    box('Dressing', (x + dz[0] * 0.05, y - 0.3, z + dz[2] * 0.05), (0.6 if wall == 'back' else 0.12, 1.2, 0.12 if wall == 'back' else 0.6), 'gold', 0.04)
    cx, cz = x + dz[0] * 0.45, z + dz[2] * 0.45
    box('Dressing', ((x + cx) / 2, y - 0.6, (z + cz) / 2), (abs(cx - x) + 0.14, 0.14, abs(cz - z) + 0.14), 'iron')
    cyl('Dressing', (cx, y - 0.7, cz), 0.25, 0.3, 'gold', n=8, r_top=0.32)
    sphere(f'Glow_Warm_{n}', (cx, y - 0.1, cz), (0.2, 0.34, 0.2), 'flame')


def pumpkin(part, c, r, col='pumpkin', stem='moss'):
    sphere(part, c, (r, r * 0.78, r), col, n=8, rings=4)
    cyl(part, (c[0], c[1] + r * 0.65, c[2]), r * 0.16, r * 0.4, stem, n=6, r_top=r * 0.1)


def ivy(c, wall, size=1.0):
    """A small flat cluster of leaves on a wall's inner face."""
    import math
    for k in range(5):
        a = k * 2.4
        dx, dy = math.cos(a) * 0.45 * size, math.sin(a) * 0.45 * size - k * 0.25 * size
        if wall == 'back':
            sphere('Dressing', (c[0] + dx, c[1] + dy, c[2] - 0.04), (0.35 * size, 0.28 * size, 0.08), 'leaf' if k % 2 else 'moss', n=6, rings=3)
        else:
            sx = 0.04 if wall == 'left' else -0.04
            sphere('Dressing', (c[0] + sx, c[1] + dy, c[2] + dx), (0.08, 0.28 * size, 0.35 * size), 'leaf' if k % 2 else 'moss', n=6, rings=3)


def moon_picture(c, size, wall='back'):
    picture(c, size, 'gold', 'night', wall)
    x, y, z = c
    r = min(size) * 0.22
    if wall == 'back':
        sphere('Dressing', (x + size[0] * 0.15, y + size[1] * 0.12, z - 0.12), (r, r, 0.05), 'moon', n=10, rings=4)
    else:
        sgn = 1 if wall == 'left' else -1
        sphere('Dressing', (x + 0.12 * sgn, y + size[1] * 0.12, z + size[0] * 0.15), (0.05, r, r), 'moon', n=10, rings=4)


# --- Rooms ---------------------------------------------------------------------------------------

def standard_room():
    w, d = 2, 2
    W, D = w * CELL, d * CELL
    begin('StandardRoom', 'Room', (W, 0.2, D), w=w, d=d)
    room_shell(w, d, paper='lilac', wainscot='plum_dark', crown='gold', rug=(5.0, 3.6, -2.4, 'plum', 'violet'))
    bed(D, frame='wood_dark', blanket='violet', head='gothic', head_col='plum_dark')
    # A dresser on the right wall, a candle on it.
    xr = W / 2 - T
    span('Furniture', (xr - 1.3, 0, -3.4), (xr - 0.02, 3.0, 0.2), 'wood', bevel=0.1)
    for y in (0.6, 1.5, 2.4):
        span('Furniture', (xr - 1.36, y - 0.32, -3.2), (xr - 1.2, y + 0.32, 0.0), 'wood_dark', bevel=0.05)
        box('Furniture', (xr - 1.42, y, -1.6), (0.12, 0.16, 0.5), 'gold')
    cyl('Furniture', (xr - 0.6, 3.0, -0.6), 0.32, 0.12, 'gold', n=8)
    cyl('Furniture', (xr - 0.6, 3.12, -0.6), 0.14, 0.9, 'cream', n=6)
    sphere('Glow_Warm_2', (xr - 0.6, 4.25, -0.6), (0.13, 0.24, 0.13), 'flame', n=6, rings=4)
    moon_picture((xr, 6.2, -1.6), (3.0, 2.2), 'right')
    picture((-3.0, 7.6, D / 2 - T), (1.6, 1.2), 'gold', 'teal')
    picture((3.0, 7.6, D / 2 - T), (1.6, 1.2), 'gold', 'pumpkin')
    finish(note='the starter room: a gothic bed, a dresser with a candle, a moon painting')


def garden_room():
    w, d = 2, 2
    W, D = w * CELL, d * CELL
    begin('GardenRoom', 'Room', (W, 0.2, D), w=w, d=d)
    room_shell(w, d, paper='grass', wainscot='wood', crown='pumpkin', floor=('wood_light', 'wood'),
               rug=(4.6, 3.4, -2.4, 'moss', 'leaf'))
    zf, zb = bed(D, frame='wood', blanket='leaf', head='gothic', head_col='wood_light')
    for x, y in ((-1.2, 3.0), (0.4, 4.2), (1.3, 2.6), (-0.3, 3.6)):
        sphere('Bed', (x, y, zb - 0.32), (0.4, 0.3, 0.1), 'moss', n=6, rings=3)
    # A planter box of pumpkins along the right wall.
    xr = W / 2 - T
    span('Furniture', (xr - 1.4, 0, -4.4), (xr - 0.02, 1.2, 0.4), 'wood', bevel=0.1)
    span('Furniture', (xr - 1.25, 1.2, -4.25), (xr - 0.17, 1.28, 0.25), 'wood_dark')
    for z, r in ((-3.4, 0.55), (-1.9, 0.7), (-0.5, 0.5)):
        pumpkin('Furniture', (xr - 0.7, 1.28 + r * 0.7, z), r)
    for c in ((-4.8, 8.6, D / 2 - T), (2.6, 8.8, D / 2 - T)):
        ivy(c, 'back')
    ivy((-W / 2 + T, 8.6, -3.0), 'left')
    ivy((xr, 8.4, 2.0), 'right', 1.2)
    picture((xr, 6.0, -2.0), (2.6, 2.0), 'pumpkin', 'moon_dark', 'right')
    finish(note='a bed under ivy, a planter of pumpkins')


def attic_room():
    import math
    w, d = 2, 2
    W, D = w * CELL, d * CELL
    begin('AtticRoom', 'Room', (W, 0.2, D), w=w, d=d)
    room_shell(w, d, paper='dusty', wainscot='wood_dark', crown='wood', floor=('wood_light', 'dusty'))
    # A mattress on crates and a patchwork quilt.
    zb, zf = D / 2 - T - 0.05, D / 2 - 6.1
    for z0, z1 in ((zf, zf + 2.7), (zf + 2.85, zb)):
        span('Bed', (-1.95, 0, z0), (1.95, 0.9, z1), 'wood_light', bevel=0.08)
        span('Bed', (-1.98, 0.35, z0 + 0.1), (1.98, 0.55, z1 - 0.1), 'wood')
    span('Bed', (-1.85, 0.9, zf + 0.05), (1.85, 1.5, zb - 0.05), 'cream', bevel=0.2)
    for i, colr in enumerate(('rose', 'teal_light', 'amber', 'violet')):
        span('Bed', (-1.9 + i * 0.95, 1.2, zf), (-0.95 + i * 0.95, 1.62, zf + 3.4), colr, bevel=0.12)
    span('Bed', (-1.2, 1.45, zb - 1.4), (1.2, 2.0, zb - 0.3), 'cream', bevel=0.2)
    # Rafters in the top of the room, clear of a person's head.
    for z in (-3.2, 0.4, 3.6):
        for sgn in (-1, 1):
            ang = math.degrees(math.atan2(1.6, W / 2 - T))
            box('Dressing', (0, 0, 0), (W / 2 - T + 0.3, 0.45, 0.45), 'wood_dark', bevel=0.05,
                m=K.Matrix.Translation((sgn * (W / 4 - T / 2), 8.9, z)) @ K.Matrix.Rotation(K.math.radians(-sgn * ang), 4, 'Z'))
        box('Dressing', (0, 9.75, z), (0.6, 0.5, 0.5), 'wood', bevel=0.05)
    span('Dressing', (-0.3, 9.5, -D / 2 + T - 0.02), (0.3, 9.95, D / 2 - T + 0.02), 'wood_dark')
    # A round window on the back wall (a moonlit pane, not a light).
    zw = D / 2 - T
    lathe('Dressing', [(1.0, 0), (1.0, 0.14)], 'wood', n=10, base=(0, 0, 0),
          m=K.Matrix.Translation((-3.6, 7.0, zw + 0.02)) @ K.Matrix.Rotation(K.math.radians(-90), 4, 'X'))
    lathe('Dressing', [(0.78, 0), (0.78, 0.18)], 'moon', n=10,
          m=K.Matrix.Translation((-3.6, 7.0, zw + 0.02)) @ K.Matrix.Rotation(K.math.radians(-90), 4, 'X'))
    box('Dressing', (-3.6, 7.0, zw - 0.17), (1.6, 0.12, 0.08), 'wood')
    box('Dressing', (-3.6, 7.0, zw - 0.17), (0.12, 1.6, 0.08), 'wood')
    # An old trunk and a stack of boxes on the right wall.
    xr = W / 2 - T
    span('Furniture', (xr - 1.5, 0, -4.2), (xr - 0.05, 1.3, -1.6), 'wood', bevel=0.1)
    lathe('Furniture', [(0.72, 0), (0.72, 2.5)], 'wood_light', n=8, phase=0,
          m=K.Matrix.Translation((xr - 0.78, 1.3, -1.65)) @ K.Matrix.Rotation(K.math.radians(-90), 4, 'X'), scale=(1, 0.6))
    for z in (-3.6, -2.2):
        span('Furniture', (xr - 1.55, 0, z - 0.1), (xr - 0.02, 1.75, z + 0.1), 'gold')
    span('Furniture', (xr - 1.4, 0, -0.9), (xr - 0.1, 1.2, 0.4), 'straw', bevel=0.06)
    span('Furniture', (xr - 1.2, 1.2, -0.7), (xr - 0.2, 2.1, 0.2), 'dusty', bevel=0.06)
    picture((-W / 2 + T, 6.0, -3.6), (1.4, 1.8), 'wood', 'lilac', 'left')
    finish(note='a mattress on crates under the rafters, a round moon window, a trunk')


def sarcophagus_suite():
    w, d = 2, 3
    W, D = w * CELL, d * CELL
    begin('SarcophagusSuite', 'Room', (W, 0.2, D), w=w, d=d)
    room_shell(w, d, paper='sand', wainscot='teal_dark', crown='gold', floor=('honey', 'sand'),
               rug=(4.8, 4.0, -3.0, 'teal_dark', 'teal'))
    zb, zf = D / 2 - T - 0.05, D / 2 - 6.1
    span('Bed', (-1.95, 0, zf), (1.95, 0.5, zb), 'stone', bevel=0.08)
    outline = [(-1.2, zf + 0.15), (1.2, zf + 0.15), (1.75, zf + 1.6), (1.55, zb - 0.15), (-1.55, zb - 0.15), (-1.75, zf + 1.6)]
    prism('Bed', outline, 0.5, 1.6, 'gold', plane='xz')
    small = [(x * 0.95, z) for x, z in outline]
    prism('Bed', small, 1.6, 1.78, 'teal', plane='xz')
    prism('Bed', [(x * 0.9, z) for x, z in outline], 1.78, 2.2, 'gold', plane='xz')
    for k in range(4):
        z = zf + 0.9 + k * 0.9
        span('Bed', (-1.5, 2.2, z - 0.12), (1.5, 2.26, z + 0.12), 'teal')
    # The face at the head end, and its striped headdress.
    sphere('Bed', (0, 2.45, zb - 1.0), (0.75, 0.4, 0.62), 'gold', n=8, rings=4)
    for x in (-0.3, 0.3):
        box('Bed', (x, 2.72, zb - 1.3), (0.24, 0.1, 0.12), 'ink')
    for x in (-0.95, 0.95):
        span('Bed', (x - 0.22, 2.0, zb - 1.5), (x + 0.22, 2.45, zb - 0.5), 'teal', bevel=0.05)
    # Canopic jars on a plinth by the right wall.
    xr = W / 2 - T
    span('Furniture', (xr - 1.3, 0, -6.4), (xr - 0.02, 1.0, -1.6), 'stone', bevel=0.08)
    for z, head in ((-5.6, 'teal'), (-4.0, 'gold'), (-2.4, 'teal')):
        lathe('Furniture', [(0.3, 0), (0.45, 0.4), (0.42, 1.0), (0.3, 1.2)], 'bone', n=8, base=(xr - 0.65, 1.0, z))
        sphere('Furniture', (xr - 0.65, 2.35, z), (0.32, 0.3, 0.32), head, n=8, rings=4)
    sconce(xr, 7.8, 2.5, 'right', 2)
    picture((-W / 2 + T, 6.4, -4.5), (3.2, 2.0), 'gold', 'teal_dark', 'left')
    sphere('Dressing', (-W / 2 + T + 0.12, 6.4, -4.5), (0.06, 0.45, 0.75), 'gold', n=8, rings=4)
    finish(note='a gold sarcophagus with a teal-striped headdress, canopic jars, a torch')


def potion_loft():
    w, d = 2, 3
    W, D = w * CELL, d * CELL
    begin('PotionLoft', 'Room', (W, 0.2, D), w=w, d=d)
    room_shell(w, d, paper='jade', wainscot='teal_dark', crown='violet', floor=('wood_dark', 'wood'),
               rug=(4.4, 4.4, -3.0, 'violet', 'plum'))
    bed(D, frame='plum_dark', blanket='teal', head='gothic', head_col='violet')
    # A potion shelf along the right wall; one flask glows.
    xr = W / 2 - T
    z0, z1 = -6.6, -2.2
    span('Furniture', (xr - 1.2, 0, z0), (xr - 0.02, 5.4, z0 + 0.25), 'wood_dark', bevel=0.05)
    span('Furniture', (xr - 1.2, 0, z1 - 0.25), (xr - 0.02, 5.4, z1), 'wood_dark', bevel=0.05)
    span('Furniture', (xr - 0.2, 0, z0), (xr - 0.02, 5.4, z1), 'wood')
    cols = ['rose', 'teal_light', 'amber', 'violet', 'slime', 'lilac']
    for i, y in enumerate((0.0, 1.8, 3.6, 5.2)):
        span('Furniture', (xr - 1.2, y, z0), (xr - 0.02, y + 0.2, z1), 'wood_dark', bevel=0.04)
        if y < 5:
            for j in range(4):
                z = z0 + 0.7 + j * 1.0
                c = cols[(i * 4 + j) % len(cols)]
                if i == 1 and j == 2:
                    lathe('Furniture', [(0.18, y + 0.2), (0.28, y + 0.35)], 'white', n=8, base=(xr - 0.6, 0, z))
                    sphere('Glow_Magic_1', (xr - 0.6, y + 0.72, z), (0.36, 0.36, 0.36), 'brew', n=8, rings=5)
                    cyl('Furniture', (xr - 0.6, y + 1.05, z), 0.1, 0.35, 'wood_light', n=6)
                else:
                    lathe('Furniture', [(0.25, y + 0.2), (0.3, y + 0.55), (0.1, y + 0.85), (0.1, y + 1.15)], c, n=6,
                          base=(xr - 0.6, 0, z))
    # Herb bundles hanging from the crown.
    for x, z in ((-4.5, 4.5), (-1.5, 6.5), (1.5, 6.5), (4.5, 4.5)):
        cyl('Dressing', (x, 9.0, z), 0.04, 0.6, 'iron', n=4)
        lathe('Dressing', [(0.0, 7.8), (0.35, 8.5), (0.15, 9.0)], 'leaf' if x < 0 else 'straw', n=6, base=(x, 0, z))
    moon_picture((-W / 2 + T, 6.3, -4.5), (2.6, 2.0), 'left')
    finish(note='a witch\'s bed, a potion shelf with one glowing flask, herbs hanging')


def den_room():
    w, d = 3, 3
    W, D = w * CELL, d * CELL
    begin('DenRoom', 'Room', (W, 0.2, D), w=w, d=d)
    room_shell(w, d, paper='brown', wainscot='wood_dark', crown='moss', floor=('wood', 'brown'),
               rug=(6.0, 5.0, -3.5, 'bone', 'cream'))
    zb, zf = D / 2 - T - 0.05, D / 2 - 6.1
    zc = (zb + zf) / 2
    # A round nest: a straw rim and a cushion.
    lathe('Bed', [(1.35, 0.0), (1.95, 0.0), (1.95, 0.9), (1.75, 1.35), (1.4, 1.2)], 'straw', n=12,
          base=(0, 0, zc), scale=(1, 1.42), closed=True)
    lathe('Bed', [(0, 0.0), (1.45, 0.0), (1.45, 0.6), (0, 0.75)], 'brown', n=12, base=(0, 0, zc), scale=(1, 1.42))
    lathe('Bed', [(0, 0.6), (1.0, 0.65), (0.6, 0.95), (0, 1.0)], 'rose', n=10, base=(0, 0, zc + 1.6), scale=(1.2, 0.6))
    # A gnawed bone in the nest.
    cyl('Bed', (0, 0, 0), 0.14, 1.6, 'bone', n=6, m=K.Matrix.Translation((-0.8, 0.95, zc - 1.2)) @ K.Matrix.Rotation(K.math.radians(-90), 4, 'Z'))
    for x in (-0.8, 0.8):
        for dz in (-0.14, 0.14):
            sphere('Bed', (x, 0.95, zc - 1.2 + dz), 0.18, 'bone', n=6, rings=4)
    # A log pile on the right wall.
    xr = W / 2 - T
    for k, (y, z) in enumerate(((0.5, -6.0), (0.5, -4.9), (0.5, -3.8), (1.45, -5.45), (1.45, -4.35), (2.4, -4.9))):
        cyl('Furniture', (0, 0, 0), 0.5, 1.6, 'wood' if k % 2 else 'wood_light', n=8,
            m=K.Matrix.Translation((xr - 1.7, y, z)) @ K.Matrix.Rotation(K.math.radians(-90), 4, 'Z'))
    # A full-moon window over the nest.
    picture((0, 7.8, D / 2 - T), (3.6, 2.6), 'wood_dark', 'night')
    sphere('Dressing', (0.6, 8.1, D / 2 - T - 0.12), (0.75, 0.75, 0.05), 'moon', n=10, rings=4)
    picture((xr, 6.2, -1.0), (2.2, 2.8), 'wood_dark', 'moss', 'right')
    finish(note='a round straw nest with a bone, a log pile, a full moon over it')


def coffin_suite():
    w, d = 3, 3
    W, D = w * CELL, d * CELL
    begin('CoffinSuite', 'Room', (W, 0.2, D), w=w, d=d)
    room_shell(w, d, paper='wine', wainscot='black', crown='gold', floor=('plum_deep', 'crimson_dark'),
               rug=(6.4, 5.2, -3.5, 'gold', 'crimson'))
    zb, zf = D / 2 - T - 0.05, D / 2 - 6.1
    outline = [(-0.95, zf + 0.1), (0.95, zf + 0.1), (1.9, zb - 1.9), (1.4, zb - 0.6), (-1.4, zb - 0.6), (-1.9, zb - 1.9)]
    prism('Bed', [(x, z) for x, z in outline], 0, 1.5, 'wood_dark', plane='xz')
    prism('Bed', [(x * 0.84, z + (0.12 if z < 0 else -0.12)) for x, z in outline], 1.5, 1.62, 'crimson', plane='xz')
    span('Bed', (-0.9, 1.62, zb - 1.7), (0.9, 2.0, zb - 0.9), 'cream', bevel=0.15)
    # Its lid, standing against the back wall behind the head.
    lid = [(-0.95, 1.6), (0.95, 1.6), (1.9, 4.6), (1.4, 6.4), (-1.4, 6.4), (-1.9, 4.6)]
    prism('Bed', lid, zb - 0.3, zb, 'wood_dark', plane='xy')
    bat = [(0, 4.2), (0.35, 4.55), (0.9, 4.4), (1.25, 4.9), (0.7, 4.85), (0.3, 5.15), (0, 4.95),
           (-0.3, 5.15), (-0.7, 4.85), (-1.25, 4.9), (-0.9, 4.4), (-0.35, 4.55)]
    prism('Bed', bat, zb - 0.38, zb - 0.28, 'gold', plane='xy')
    # A candelabra on the right wall, three flames.
    xr = W / 2 - T
    lathe('Furniture', [(0.7, 0), (0.7, 0.2), (0.2, 0.4), (0.12, 4.0), (0.25, 4.2)], 'iron', n=8, base=(xr - 1.2, 0, -3.0))
    box('Furniture', (xr - 1.2, 4.3, -3.0), (0.2, 0.2, 2.0), 'iron')
    for k, z in enumerate((-4.0, -3.0, -2.0)):
        cyl('Furniture', (xr - 1.2, 4.3, z), 0.2, 0.2, 'gold', n=8)
        cyl('Furniture', (xr - 1.2, 4.5, z), 0.12, 0.7 if k != 1 else 0.95, 'cream', n=6)
        sphere(f'Glow_Warm_{k + 2}', (xr - 1.2, (5.38 if k != 1 else 5.63), z), (0.12, 0.22, 0.12), 'flame', n=6, rings=4)
    # A gothic window on the right wall with crimson drapes.
    picture((xr, 6.4, 1.0), (2.6, 3.2), 'gold', 'night', 'right')
    sphere('Dressing', (xr - 0.12, 7.2, 1.4), (0.05, 0.55, 0.55), 'moon', n=10, rings=4)
    for z in (-0.8, 2.8):
        lathe('Dressing', [(0.5, 3.6), (0.35, 6.0), (0.5, 9.3)], 'crimson', n=6, base=(xr - 0.3, 0, z), scale=(0.5, 1))
    finish(note='a coffin with red velvet, its lid against the wall with a gold bat, a candelabra')


def opera_suite():
    w, d = 3, 3
    W, D = w * CELL, d * CELL
    begin('OperaSuite', 'Room', (W, 0.2, D), w=w, d=d)
    room_shell(w, d, paper='lavender', wainscot='plum', crown='gold', floor=('wood_light', 'wood'),
               rug=(6.4, 5.2, -3.5, 'gold', 'crimson'))
    zf, zb = bed(D, frame='gold', blanket='rose', head='gothic', head_col='crimson', foot=False)
    # A canopy on four gold posts.
    for x in (-1.75, 1.75):
        for z in (zf + 0.2, zb - 0.2):
            cyl('Bed', (x, 0, z), 0.16, 7.6, 'gold', n=8)
            sphere('Bed', (x, 7.85, z), 0.26, 'gold', n=8, rings=4)
    span('Bed', (-1.95, 7.2, zf), (1.95, 7.7, zb), 'crimson', bevel=0.12)   # under the sconce at 8.2
    for x in (-1.85, 1.85):
        lathe('Bed', [(0.4, 3.5), (0.22, 5.4), (0.42, 7.2)], 'crimson', n=6, base=(x, 0, zf + 0.5), scale=(0.4, 1))
    # A gramophone on a stand by the right wall.
    xr = W / 2 - T
    lathe('Furniture', [(0.8, 0), (0.8, 0.2), (0.25, 0.4), (0.25, 2.6), (0.9, 2.8), (0.9, 3.0)], 'wood_dark', n=8,
          base=(xr - 1.2, 0, -3.0))
    span('Furniture', (xr - 1.9, 3.0, -3.7), (xr - 0.5, 3.6, -2.3), 'wood', bevel=0.08)
    cyl('Furniture', (xr - 1.2, 3.6, -3.0), 0.55, 0.08, 'black', n=10)
    lathe('Furniture', [(0.1, 0), (0.18, 0.9), (0.45, 1.6), (1.0, 2.0)], 'gold', n=10,
          m=K.Matrix.Translation((xr - 1.0, 3.7, -2.6)) @ K.Matrix.Rotation(K.math.radians(-35), 4, 'X'))
    # Masks on the left wall over the decor slot, a swag of curtain over the bed.
    picture((-W / 2 + T, 7.6, -4.5), (3.0, 1.8), 'gold', 'crimson', 'left')
    for z, colr in ((-5.2, 'bone'), (-3.8, 'gold')):
        sphere('Dressing', (-W / 2 + T + 0.14, 7.6, z), (0.06, 0.55, 0.45), colr, n=8, rings=4)
    finish(note='a canopy bed in crimson and gold, a gramophone, theatre masks')


# --- Amenities: the centrepiece stays in x +-1.95, z -1..D/2-0.4 (the guest stands at z -2) --------

def amenity(id_, paper, wainscot, crown, floor, rug=None):
    w, d = 2, 2
    begin(id_, 'Amenity', (w * CELL, 0.2, d * CELL), w=w, d=d)
    room_shell(w, d, paper=paper, wainscot=wainscot, crown=crown, floor=floor, rug=rug)
    return w * CELL, d * CELL


def snack_bar():
    W, D = amenity('SnackBar', 'honey', 'plum_dark', 'pumpkin', ('wood', 'wood_light'))
    span('Centrepiece', (-1.95, 0, 0.0), (1.95, 3.2, 1.6), 'plum', bevel=0.1)
    for i in range(7):
        x = -1.95 + 0.28 + i * 0.56
        span('Centrepiece', (x - 0.14, 0.2, -0.03), (x + 0.14, 3.0, 0.05), 'pumpkin' if i % 2 else 'cream')
    span('Centrepiece', (-1.95, 3.2, -0.1), (1.95, 3.45, 1.7), 'wood_light', bevel=0.06)
    for x, colr in ((-1.3, 'pumpkin'), (0.0, 'rose'), (1.3, 'slime')):
        lathe('Centrepiece', [(0.3, 3.45), (0.38, 3.6), (0.38, 4.2), (0.25, 4.3)], 'lavender', n=8, base=(x, 0, 0.8))
        sphere('Centrepiece', (x, 4.4, 0.8), (0.2, 0.12, 0.2), colr, n=6, rings=3)
    lathe('Centrepiece', [(0.55, 3.45), (0.55, 3.85), (0.4, 3.95), (0, 4.0)], 'rose', n=10, base=(0.65, 0, 0.3))
    # The back shelf of jars.
    zw = D / 2 - T
    span('Centrepiece', (-1.95, 0, zw - 1.0), (1.95, 5.2, zw), 'wood_dark', bevel=0.06)
    for y in (2.4, 3.8):
        for k, x in enumerate((-1.4, -0.45, 0.45, 1.4)):
            lathe('Centrepiece', [(0.28, y), (0.3, y + 0.75), (0.18, y + 0.85)], ('amber', 'rose', 'teal_light', 'pumpkin')[k],
                  n=6, base=(x, 0, zw - 1.25))
    # A striped awning over it all (dressing, nothing walks into it).
    for i in range(8):
        x = -2.4 + i * 0.6
        span('Dressing', (x, 7.0, zw - 1.5), (x + 0.6, 7.45, zw - 0.02), 'pumpkin' if i % 2 else 'cream', bevel=0.05)
    finish(note='a candy-striped counter with jars and a pie, a striped awning')


def music_room():
    W, D = amenity('MusicRoom', 'sky', 'night', 'gold', ('wood_dark', 'wood'), rug=(4.4, 3.0, -1.6, 'night', 'moon_dark'))
    zw = D / 2 - T
    span('Centrepiece', (-1.95, 0, zw - 1.6), (1.95, 4.4, zw - 0.02), 'night', bevel=0.12)
    span('Centrepiece', (-1.95, 4.4, zw - 1.7), (1.95, 4.6, zw - 0.02), 'black', bevel=0.06)
    span('Centrepiece', (-1.9, 2.0, zw - 2.3), (1.9, 2.45, zw - 1.6), 'night', bevel=0.05)
    span('Centrepiece', (-1.75, 2.45, zw - 2.25), (1.75, 2.6, zw - 1.65), 'white')
    for k in range(10):
        if k % 7 in (2, 6):
            continue
        x = -1.6 + k * 0.36
        span('Centrepiece', (x - 0.08, 2.6, zw - 1.95), (x + 0.08, 2.72, zw - 1.65), 'black')
    for x in (-1.7, 1.7):
        span('Centrepiece', (x - 0.15, 0, zw - 2.3), (x + 0.15, 2.0, zw - 2.0), 'night', bevel=0.04)
    span('Centrepiece', (-0.6, 3.0, zw - 1.75), (0.6, 3.9, zw - 1.6), 'cream')    # the music
    lathe('Centrepiece', [(0.35, 0), (0.15, 0.2), (0.15, 1.4), (0.55, 1.55), (0.55, 1.75)], 'crimson', n=8,
          base=(0, 0, zw - 3.4))
    # Music notes on the side walls.
    for wall, x in (('left', -W / 2 + T), ('right', W / 2 - T)):
        sgn = 1 if wall == 'left' else -1
        for z, y in ((-2.5, 6.6), (-0.8, 7.4)):
            sphere('Dressing', (x + 0.06 * sgn, y, z), (0.07, 0.3, 0.38), 'gold', n=8, rings=4)
            span('Dressing', (min(x, x + 0.1 * sgn), y, z + 0.28), (max(x, x + 0.1 * sgn), y + 1.3, z + 0.4), 'gold')
    finish(note='a midnight-blue upright piano and its stool, gold notes on the walls')


def graveyard_garden():
    W, D = amenity('GraveyardGarden', 'stone', 'stone_dark', 'moss', ('grass', 'moss'))
    lathe('Centrepiece', [(0, 0.2), (1.95, 0.2), (1.6, 0.6), (0.6, 0.85), (0, 0.9)], 'moss', n=10, base=(0, 0, 3.4),
          scale=(1, 1.1))
    for x, z, h, colr in ((-1.1, 4.0, 2.4, 'stone'), (0.2, 4.6, 2.9, 'grey'), (1.25, 3.7, 2.1, 'stone')):
        pts = [(x - 0.5, 0.4), (x + 0.5, 0.4), (x + 0.5, h - 0.5)] + \
              [(x + 0.5 * __import__('math').cos(a / 6 * 3.14159), h - 0.5 + 0.5 * __import__('math').sin(a / 6 * 3.14159))
               for a in range(1, 6)] + [(x - 0.5, h - 0.5)]
        prism('Centrepiece', pts, z - 0.15, z + 0.15, colr, plane='xy')
        span('Centrepiece', (x - 0.6, 0.2, z - 0.3), (x + 0.6, 0.6, z + 0.3), 'stone_dark', bevel=0.05)
        span('Centrepiece', (x - 0.25, h - 0.9, z - 0.17), (x + 0.25, h - 0.8, z - 0.15), 'stone_dark')
        span('Centrepiece', (x - 0.05, h - 1.2, z - 0.17), (x + 0.05, h - 0.5, z - 0.15), 'stone_dark')
    # A lantern post at the front of the mound.
    lathe('Centrepiece', [(0.3, 0), (0.12, 0.2), (0.1, 3.3), (0.25, 3.4)], 'iron', n=6, base=(-1.5, 0, 1.6))
    box('Centrepiece', (-1.5, 3.95, 1.6), (0.7, 0.1, 0.7), 'iron')
    box('Centrepiece', (-1.5, 4.85, 1.6), (0.75, 0.15, 0.75), 'iron')
    for dx in (-0.3, 0.3):
        for dz in (-0.3, 0.3):
            box('Centrepiece', (-1.5 + dx, 4.4, 1.6 + dz), (0.08, 0.8, 0.08), 'iron')
    sphere('Glow_Warm_2', (-1.5, 4.4, 1.6), (0.26, 0.34, 0.26), 'lamp', n=8, rings=4)
    pumpkin('Centrepiece', (1.3, 0.55, 1.8), 0.45)
    for c, wall in (((-4.5, 8.4, D / 2 - T), 'back'), ((3.5, 8.8, D / 2 - T), 'back'),
                    ((-W / 2 + T, 8.2, -2.5), 'left'), ((W / 2 - T, 8.4, -1.0), 'right')):
        ivy(c, wall, 1.2)
    finish(note='a mossy mound of three friendly tombstones, a lantern, a pumpkin; grass underfoot')


def quiet_library():
    W, D = amenity('QuietLibrary', 'teal_dark', 'wood_dark', 'gold', ('wood', 'wood_dark'), rug=(4.0, 3.0, -1.4, 'crimson', 'wine'))
    zw = D / 2 - T
    span('Centrepiece', (-1.95, 0, zw - 1.2), (1.95, 7.0, zw - 0.02), 'wood_dark', bevel=0.08)
    books = ('book_a', 'book_b', 'book_c', 'teal', 'plum', 'amber')
    for i, y in enumerate((0.5, 2.1, 3.7, 5.3)):
        span('Centrepiece', (-1.8, y, zw - 1.25), (1.8, y + 1.3, zw - 0.6), 'ink')
        x = -1.75
        k = 0
        while x < 1.55:
            bw = 0.28 + 0.1 * ((k * 7 + i * 3) % 3)
            bh = 0.95 + 0.12 * ((k * 5 + i) % 3)
            span('Centrepiece', (x, y, zw - 1.3), (x + bw - 0.03, y + bh, zw - 0.65), books[(k + i * 2) % len(books)], bevel=0.02)
            x += bw
            k += 1
    # A reading chair facing the guest, and a candle on the shelf top.
    span('Centrepiece', (-1.2, 0, 0.6), (1.2, 1.4, 2.2), 'crimson', bevel=0.25)
    span('Centrepiece', (-1.2, 1.4, 1.8), (1.2, 3.4, 2.4), 'crimson', bevel=0.25)
    for x in (-1.25, 1.25):
        span('Centrepiece', (x - 0.3, 1.0, 0.6), (x + 0.3, 2.1, 2.4), 'wine', bevel=0.2)
    cyl('Centrepiece', (1.3, 7.0, zw - 0.6), 0.25, 0.1, 'gold', n=8)
    cyl('Centrepiece', (1.3, 7.1, zw - 0.6), 0.12, 0.6, 'cream', n=6)
    sphere('Glow_Warm_2', (1.3, 7.95, zw - 0.6), (0.12, 0.22, 0.12), 'flame', n=6, rings=4)
    # High shelves on the side walls, over the decor slots.
    for wall, x in (('left', -W / 2 + T), ('right', W / 2 - T)):
        sgn = 1 if wall == 'left' else -1
        xa, xb = sorted((x - 0.02 * sgn, x + 0.9 * sgn))
        span('Dressing', (xa, 7.3, -4.5), (xb, 7.5, 2.5), 'wood_dark', bevel=0.04)
        z = -4.4
        k = 0
        while z < 2.2:
            bw = 0.3 + 0.1 * (k % 3)
            xa2, xb2 = sorted((x + 0.05 * sgn, x + 0.75 * sgn))
            span('Dressing', (xa2, 7.5, z), (xb2, 7.5 + 0.9 + 0.15 * (k % 2), z + bw - 0.03), books[k % len(books)])
            z += bw
            k += 1
    finish(note='a tall bookcase, a crimson reading chair, a candle, shelves high on the walls')


def organ_hall():
    W, D = amenity('OrganHall', 'plum', 'plum_deep', 'gold', ('plum_dark', 'stone_dark'), rug=(4.0, 3.2, -1.6, 'crimson', 'wine'))
    zw = D / 2 - T
    span('Centrepiece', (-1.95, 0, 2.0), (1.95, 3.0, 3.8), 'wood_dark', bevel=0.1)
    span('Centrepiece', (-1.8, 3.0, 2.0), (1.8, 3.3, 2.9), 'white', bevel=0.03)
    span('Centrepiece', (-1.8, 3.3, 2.5), (1.8, 3.55, 3.0), 'black', bevel=0.03)
    span('Centrepiece', (-1.95, 3.0, 3.0), (1.95, 4.4, 3.8), 'wood_dark', bevel=0.08)
    for i, h in enumerate((5.2, 6.2, 7.0, 7.6, 7.0, 6.2, 5.2)):     # under the sconce at 8.2
        x = -1.62 + i * 0.54
        cyl('Centrepiece', (x, 4.4, zw - 0.6), 0.25, h - 4.4, 'gold', n=8)
        lathe('Centrepiece', [(0.25, h), (0.0, h + 0.35)], 'gold', n=8, base=(x, 0, zw - 0.6))
        span('Centrepiece', (x - 0.12, 5.0, zw - 0.87), (x + 0.12, 5.4, zw - 0.83), 'black')
    span('Centrepiece', (-1.3, 0, 0.6), (1.3, 1.6, 1.4), 'wood', bevel=0.08)
    for k, x in enumerate((-1.6, 1.6)):
        cyl('Centrepiece', (x, 4.4, 2.6), 0.2, 0.12, 'gold', n=8)
        cyl('Centrepiece', (x, 4.52, 2.6), 0.11, 0.6, 'cream', n=6)
        sphere(f'Glow_Warm_{k + 2}', (x, 5.32, 2.6), (0.12, 0.22, 0.12), 'flame', n=6, rings=4)
    for wall, x in (('left', -W / 2 + T), ('right', W / 2 - T)):
        picture((x, 7.0, -2.0), (2.0, 2.6), 'gold', 'wine', wall)
    finish(note='a pipe organ in gold pipes and dark wood, its bench, two candles')


# --- Lobby, stairs, sign -------------------------------------------------------------------------

def lobby():
    import math
    begin('Lobby', 'Lobby', (72, 0.2, 12), root_centre=(0, 0.1, 6))
    declare('Rug', False)       # the blockout's Rug does not collide either
    # The floor: the whole lobby to its edges (the plot's ground showed at the threshold and the ends).
    for i in range(12):
        for j in range(2):
            x0, z0 = -36 + i * 6, j * 6
            span('Rug', (x0, 0, z0), (x0 + 6, 0.1, z0 + 6), 'plum' if (i + j) % 2 else 'plum_dark', bevel=0.02)
    # A carpet from the door into the lobby, and on along the queue to the desk.
    span('Rug', (-2.2, 0.1, 0.8), (2.2, 0.13, 6.0), 'gold')
    span('Rug', (-1.9, 0.13, 0.8), (1.9, 0.15, 6.0), 'crimson')
    span('Rug', (-24.6, 0.1, 1.4), (-2.2, 0.13, 4.4), 'gold')
    span('Rug', (-24.3, 0.13, 1.7), (-1.9, 0.15, 4.1), 'crimson')
    # The front wall round the arch (MODELS.md, "Lobby"), the hotel's outside colour to the street.
    K.lobby_front_wall(outside='plum', paper='lilac', wainscot='plum_dark', crown='gold',
                       plinth='stone_dark', frame='wood_dark', sill='gold')
    # The front desk across the -X end, served toward +X (the entrance).
    (lo, hi), (tlo, thi) = K.LOBBY_COUNTER, K.LOBBY_COUNTER_TOP
    span('Desk', lo, hi, 'wood_dark', bevel=0.1)
    zc = (lo[2] + hi[2]) / 2
    for z in (zc - 1.9, zc, zc + 1.9):
        span('Desk', (hi[0] - 0.1, 0.5, z - 0.75), (hi[0] + 0.13, 3.0, z + 0.75), 'violet', bevel=0.06)
        sphere('Desk', (hi[0] + 0.14, 1.75, z), (0.06, 0.35, 0.35), 'gold', n=8, rings=4)
    span('Desk', tlo, thi, 'gold', bevel=0.05)
    K.lobby_bell('Desk', -25.6, thi[1], 2.9, 'gold')   # at the check-in prompt
    span('Desk', (-26.5, 3.8, 3.7), (-25.6, 3.95, 4.7), 'crimson', bevel=0.03)
    K.lobby_till(body='wood_dark', keys='pumpkin', drawer='gold', screen='bone')
    # The desk lamp on the counter's near end.
    K.lobby_lamp('gold', 'teal')
    # The key rack against the end, behind the clerk.
    K.lobby_keyrack(cabinet='wood_dark', drawer='wood', knob='gold', board='plum_dark',
                    tags=('gold', 'gold', 'pumpkin'), cornice='gold', face='bone', hands='black')
    # The waiting area: benches with their backs to the front wall, pumpkin planters.
    for k, (x0, x1) in enumerate(K.LOBBY_BENCHES):
        K.lobby_bench(f'Bench_{k + 1}', x0, x1, frame='wood_dark', cushion='crimson', back='violet')
    for k, (x, z) in enumerate(K.LOBBY_PLANTERS):
        name = f'Planter_{k + 1}'
        lathe(name, [(0.7, 0), (0.9, 0.2), (1.0, 1.4), (1.1, 1.6), (1.1, 1.8), (0.9, 1.8)], 'stone', n=8, base=(x, 0, z))
        pumpkin(name, (x - 0.2, 2.25, z - 0.1), 0.6)
        for a in range(4):
            sphere(name, (x + 0.6 * math.cos(a * 1.6), 2.0, z + 0.6 * math.sin(a * 1.6)), (0.4, 0.15, 0.3), 'leaf', n=6, rings=3)
    # The front arch: pillars and a pointed top (opening 9 wide, 9 tall at its sides).
    for name, x in (('ArchLeft', -5), ('ArchRight', 5)):
        span(name, (x - 0.5, 0, 0), (x + 0.5, 0.6, 1), 'stone_dark', bevel=0.08)
        span(name, (x - 0.42, 0.6, 0.08), (x + 0.42, 8.4, 0.92), 'stone', bevel=0.1)
        span(name, (x - 0.5, 8.4, 0), (x + 0.5, 9.0, 1), 'gold', bevel=0.08)
    inner = arch_points(-4.5, 4.5, 9.0, 10.6, n=5)
    outline = [(-5.5, 9.0)] + [(-5.5, 10.4), (0, 11.8), (5.5, 10.4)] + [(5.5, 9.0)] + list(reversed(inner))
    prism('ArchTop', outline, 0.05, 0.95, {'front': 'plum', 'back': 'plum', 'rest': 'gold'}, plane='xy')
    pumpkin('ArchTop', (0, 11.15, 0.5), 0.4)
    # The lantern hanging inside the arch.
    cyl('Dressing', (0, 9.2, 1.5), 0.05, 1.5, 'iron', n=4)
    box('Dressing', (0, 9.2, 1.5), (0.8, 0.12, 0.8), 'iron')
    box('Dressing', (0, 7.8, 1.5), (0.8, 0.12, 0.8), 'iron')
    for dx in (-0.36, 0.36):
        for dz in (-0.36, 0.36):
            box('Dressing', (dx, 8.5, 1.5 + dz), (0.08, 1.3, 0.08), 'iron')
    sphere('Glow_Warm_1', (0, 8.5, 1.5), (0.3, 0.45, 0.3), 'lamp', n=8, rings=5)
    for n, x in enumerate(K.LOBBY_SCONCES):
        K.lobby_sconce(x, 7.2, n + 3, 'gold', candle='bone')
    for aname, (pos, look) in K.blockout_attachments('Lobby').items():
        attach(aname, pos, look)
    finish(note='an indoor reception: the front wall with windows round the arch, the desk across the end '
                'with its key rack and clock, benches and pumpkin planters, the back row clear for the floor-1 doors')


def stairs(top):
    name = 'StairCoreTop' if top else 'StairCore'
    begin(name, 'Stairs', (12, 0.2, 12))
    # Every walked box is the blockout's, exactly (K.blockout_stairs); only colour and chamfers are added.
    for sname, (c, s) in K.blockout_stairs(top).items():
        c, s = K.Vector(c), K.Vector(s)
        lo, hi = c - s / 2, c + s / 2
        if sname.startswith(('Step_', 'Landing')):
            # Their ends lie in the core walls' outer faces (the blockout's boxes): the wall's own
            # colour there, so the coplanar faces cannot show a fight.
            ends = {'top': 'crimson', 'left': 'plum_dark', 'right': 'plum_dark', 'rest': 'wood_dark'}
            if sname == 'Landing':
                ends['back'] = 'plum_dark'
            box(sname, c, s, ends, bevel=0.06)
        elif sname.startswith('Wall_') or sname == 'Divider':
            h = hi.y
            bands = [(0, 1.0, 'wood_dark'), (1.0, h - 0.4, 'plum_dark' if sname != 'Divider' else 'wood'), (h - 0.4, h, 'gold')]
            for y0, y1, colr in bands:
                span(sname, (lo.x, y0, lo.z), (hi.x, y1, hi.z), colr, bevel=0.04)
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
    # A light over the flight up, high on the left wall, and a portrait over the landing.
    sconce(-6 + T, 11.4, -1.0, 'left', 1)
    picture((0, 9.6 if not top else 10.6, 6 - T), (2.4, 2.6), 'gold', 'plum')
    sphere('Dressing', (0, 9.9 if not top else 10.9, 6 - T - 0.13), (0.55, 0.6, 0.05), 'lilac', n=8, rings=4)
    finish(note='the walker-proven switchback, crimson-carpeted' + (', railed round the stairwell' if top else ''))


def hotel_sign():
    import math
    begin('HotelSign', 'Sign', (16, 0.2, 1))
    for name, x in (('PostLeft', -7), ('PostRight', 7)):
        span(name, (x - 0.4, 0, -0.4), (x + 0.4, 0.5, 0.4), 'stone_dark', bevel=0.06)
        # The post ends under the Board (bottom y 5): its ring never reaches the board's text face.
        lathe(name, [(0.3, 0.5), (0.3, 4.6), (0.4, 4.8), (0.4, 5.0)], 'wood_dark', n=8, base=(x, 0, 0))
    # The Board: a plain box, its front (-Z) the SurfaceGui's face.
    box('Board', (0, 8, 0), (16, 6, 0.6), {'front': 'night', 'back': 'plum_dark', 'rest': 'gold'}, bevel=0.08)
    # A crest over it: a gable with a crescent moon (lit) and two bats.
    prism('Crest', [(-6, 11), (6, 11), (4.5, 12.4), (0, 13.6), (-4.5, 12.4)], -0.25, 0.25,
          {'front': 'plum', 'back': 'plum', 'rest': 'gold'}, plane='xy')
    declare('Crest', False)
    moon = [(0.9 * math.cos(a), 12.2 + 0.9 * math.sin(a)) for a in [math.radians(t) for t in range(60, 301, 30)]]
    moon += [(0.45 + 0.75 * math.cos(a), 12.2 + 0.75 * math.sin(a)) for a in [math.radians(t) for t in range(280, 79, -40)]]
    prism('Glow_Cold_1', moon, -0.32, -0.24, 'moonglow', plane='xy')
    for sx in (-1, 1):
        bat = [(sx * x, y) for x, y in ((2.2, 11.9), (2.6, 12.25), (3.1, 12.05), (3.5, 12.45), (2.95, 12.4),
                                        (2.6, 12.7), (2.25, 12.4), (1.75, 12.45), (2.05, 12.05))]
        prism('Crest', bat if sx > 0 else list(reversed(bat)), -0.3, -0.24, 'black', plane='xy')
    finish(note='posts and a 16 x 6 board for the SurfaceGui, a gable crest with a lit crescent moon and bats')


# --- Decor (origin at the base centre, front -Z, at most 4 x 4 x 7) -------------------------------

def decor(id_, fw, fd):
    begin(f'Decor_{id_}', 'Decor', (fw, 0.2, fd))
    declare('Body', False)          # the blockout's Body does not collide


def d_puddle_rug():
    import math
    decor('PuddleRug', 3.6, 3.6)
    rr = (1.7, 1.45, 1.75, 1.5, 1.65, 1.35, 1.7, 1.55, 1.6, 1.4)
    pts = [(rr[k] * math.cos(k * math.tau / 10), rr[k] * math.sin(k * math.tau / 10)) for k in range(10)]
    prism('Body', pts, 0, 0.06, 'sky', plane='xz')
    prism('Body', [(x * 0.62 + 0.15, z * 0.62 - 0.1) for x, z in pts], 0.06, 0.08, 'moon', plane='xz')
    prism('Body', [(x * 0.35 + 0.25, z * 0.35 - 0.15) for x, z in pts], 0.08, 0.1, 'sky', plane='xz')
    sphere('Body', (-0.7, 0.35, 0.5), (0.3, 0.25, 0.35), 'amber', n=8, rings=4)
    sphere('Body', (-0.7, 0.72, 0.3), 0.19, 'amber', n=8, rings=4)
    box('Body', (-0.7, 0.68, 0.08), (0.14, 0.06, 0.16), 'pumpkin')
    finish(note='a puddle-blue rug with ripples and a rubber duck')


def d_snack_basket():
    decor('SnackBasket', 2.2, 2.2)
    lathe('Body', [(0.75, 0), (1.0, 0.8), (1.05, 0.9), (0.9, 0.9), (0.68, 0.15)], 'straw', n=10, closed=True)
    lathe('Body', [(0, 0.1), (0.75, 0.1), (0.85, 0.7), (0, 0.7)], 'wood_light', n=10)
    for k in range(5):
        a = k * 3.14159 / 4
        box('Body', (0, 0, 0), (0.42, 0.12, 0.14), 'wood',
            m=K.Matrix.Translation((-0.95 * K.math.cos(a), 0.9 + 0.95 * K.math.sin(a), 0)) @ K.Matrix.Rotation(-a + K.math.pi / 2, 4, 'Z'))
    for x, z, colr in ((-0.4, -0.2, 'pumpkin'), (0.35, 0.25, 'rose'), (0.1, -0.45, 'slime'), (-0.2, 0.45, 'amber')):
        sphere('Body', (x, 0.85, z), 0.26, colr, n=6, rings=4)
    cyl('Body', (0.45, 0.75, -0.35), 0.3, 0.12, 'honey', n=8)
    finish(note='a wicker basket of candies and a cookie')


def d_record_player():
    decor('RecordPlayer', 2.4, 2.4)
    span('Body', (-0.9, 0, -0.8), (0.9, 2.0, 0.8), 'wood', bevel=0.1)
    span('Body', (-0.75, 0.25, -0.84), (0.75, 1.75, -0.78), 'wood_dark', bevel=0.04)
    box('Body', (0, 1.0, -0.86), (0.4, 0.1, 0.06), 'gold')
    span('Body', (-0.95, 2.0, -0.85), (0.95, 2.15, 0.85), 'gold', bevel=0.04)
    cyl('Body', (-0.15, 2.15, -0.1), 0.62, 0.06, 'black', n=12)
    cyl('Body', (-0.15, 2.21, -0.1), 0.18, 0.02, 'crimson', n=8)
    box('Body', (0.6, 2.3, 0.0), (0.08, 0.08, 0.8), 'gold')
    lathe('Body', [(0.1, 0), (0.12, 0.5), (0.3, 1.2), (0.85, 1.75), (0.95, 1.8)], 'gold', n=10,
          m=K.Matrix.Translation((0.2, 2.15, 0.55)) @ K.Matrix.Rotation(K.math.radians(-30), 4, 'X'))
    finish(note='a wooden cabinet gramophone with a gold flower horn')


def d_candles():
    decor('Candles', 2.0, 2.0)
    cyl('Body', (0, 0, 0), 0.9, 0.15, 'gold', n=10)
    for k, (x, z, h) in enumerate(((-0.35, 0.2, 1.4), (0.35, 0.25, 1.0), (0.0, -0.4, 0.7))):
        cyl('Body', (x, 0.15, z), 0.2, h, 'cream', n=8)
        sphere('Body', (x + 0.15, 0.15 + h - 0.15, z - 0.12), (0.06, 0.14, 0.06), 'cream', n=6, rings=3)
        sphere(f'Glow_Warm_{k + 1}', (x, 0.15 + h + 0.22, z), (0.11, 0.2, 0.11), 'flame', n=6, rings=4)
    finish(note='three cream candles on a gold dish, each flame its own glow')


def d_planter():
    import math
    decor('Planter', 2.4, 2.4)
    lathe('Body', [(0.6, 0), (0.8, 0.15), (0.95, 1.2), (1.05, 1.3), (1.05, 1.5), (0.85, 1.5)], 'stone', n=10)
    lathe('Body', [(0, 1.3), (0.88, 1.3), (0.88, 1.4), (0, 1.4)], 'wood_dark', n=10)
    lathe('Body', [(0.96, 0.6), (0.99, 0.6), (0.99, 0.85), (0.96, 0.85)], 'teal', n=10)
    cyl('Body', (0, 1.4, 0), 0.08, 1.8, 'moss', n=6, r_top=0.05)
    for k in range(5):
        a = k * math.tau / 5
        r = 0.55
        sphere('Body', (r * math.cos(a), 1.9 + 0.25 * (k % 2), r * math.sin(a)), (0.5, 0.12, 0.28), 'leaf', n=6, rings=3,
               m=None)
    sphere('Body', (0, 3.35, 0), (0.38, 0.45, 0.38), 'violet', n=8, rings=4)
    sphere('Body', (0, 3.85, 0), (0.12, 0.12, 0.12), 'lilac', n=6, rings=3)
    finish(note='a stone pot with a teal band and a violet-budded spooky plant')


def d_antique_wardrobe():
    decor('AntiqueWardrobe', 3.4, 2.0)
    for x in (-1.45, 1.45):
        for z in (-0.65, 0.65):
            lathe('Body', [(0.15, 0), (0.22, 0.2), (0.18, 0.4)], 'wood_dark', n=6, base=(x, 0, z))
    span('Body', (-1.6, 0.4, -0.8), (1.6, 5.9, 0.8), 'wood', bevel=0.12)
    for x0, x1 in ((-1.45, -0.04), (0.04, 1.45)):
        span('Body', (x0, 0.6, -0.86), (x1, 5.6, -0.78), 'wood_dark', bevel=0.06)
        span('Body', (x0 + 0.2, 3.3, -0.9), (x1 - 0.2, 5.3, -0.84), 'wood_light', bevel=0.04)
        span('Body', (x0 + 0.2, 0.9, -0.9), (x1 - 0.2, 2.9, -0.84), 'wood_light', bevel=0.04)
    for x in (-0.22, 0.22):
        sphere('Body', (x, 3.1, -0.9), 0.1, 'gold', n=6, rings=3)
    prism('Body', [(-1.7, 5.9), (1.7, 5.9), (1.7, 6.1), (0.6, 6.45), (0, 6.6), (-0.6, 6.45), (-1.7, 6.1)], -0.9, 0.9,
          'wood_dark', plane='xy')
    sphere('Body', (0, 6.75, -0.4), 0.15, 'gold', n=6, rings=3)
    finish(note='a tall carved wardrobe with a crown top and gold knobs')


def d_blackout_curtains():
    import math
    decor('BlackoutCurtains', 4.0, 1.0)
    for x in (-1.85, 1.85):
        span('Body', (x - 0.12, 0, -0.45), (x + 0.12, 0.12, 0.45), 'iron')
        cyl('Body', (x, 0.12, 0), 0.07, 6.3, 'iron', n=6)
        sphere('Body', (x, 6.5, 0), 0.15, 'gold', n=6, rings=3)
    cyl('Body', (0, 0, 0), 0.07, 3.7, 'iron', n=6, m=K.Matrix.Translation((-1.85, 6.35, 0)) @ K.Matrix.Rotation(K.math.radians(-90), 4, 'Z'))
    for sx in (-1, 1):
        pts = []
        for k in range(9):
            x = sx * (0.02 + k * 0.205)
            pts.append((x, -0.2 + 0.18 * (k % 2)))
        pts += [(x, 0.22) for x, _ in reversed(pts)]
        prism('Body', pts if sx > 0 else list(reversed(pts)), 0.25, 6.25, 'plum_deep', plane='xz')
        span('Body', (min(0, sx * 1.75), 3.1, -0.28), (max(0, sx * 1.75), 3.3, -0.14), 'gold')
    finish(note='heavy plum curtains on an iron rod, closed, a gold tie across each')


def d_sand_tray():
    decor('SandTray', 3.0, 2.4)
    for x in (-1.3, 1.3):
        for z in (-0.95, 0.95):
            cyl('Body', (x, 0, z), 0.12, 0.6, 'wood_dark', n=6)
    span('Body', (-1.45, 0.6, -1.1), (1.45, 0.75, 1.1), 'wood_light', bevel=0.04)
    for (x0, z0, x1, z1) in ((-1.45, -1.1, 1.45, -0.95), (-1.45, 0.95, 1.45, 1.1), (-1.45, -0.95, -1.3, 0.95), (1.3, -0.95, 1.45, 0.95)):
        span('Body', (x0, 0.75, z0), (x1, 1.05, z1), 'wood', bevel=0.03)
    span('Body', (-1.3, 0.75, -0.95), (1.3, 0.95, 0.95), 'sand')
    lathe('Body', [(0.45, 0.95), (0.0, 1.45)], 'honey', n=4, base=(0.5, 0, 0.2), phase=0.785)
    box('Body', (-0.6, 1.0, -0.2), (0.08, 0.06, 1.0), 'wood_dark')
    box('Body', (-0.6, 1.0, -0.72), (0.5, 0.06, 0.08), 'wood_dark')
    finish(note='a wooden tray of raked sand with a little pyramid')


def d_cat_basket():
    import math
    decor('CatBasket', 2.6, 2.6)
    lathe('Body', [(0.95, 0), (1.25, 0.05), (1.25, 0.7), (1.1, 0.8), (1.0, 0.25)], 'pumpkin_dark', n=12, closed=True)
    lathe('Body', [(0, 0.05), (1.0, 0.05), (1.0, 0.45), (0, 0.5)], 'rose', n=12)
    sphere('Body', (0.1, 0.8, 0.15), (0.65, 0.38, 0.5), 'black', n=8, rings=5)
    sphere('Body', (-0.55, 0.85, -0.3), 0.36, 'black', n=8, rings=5)
    for dx in (-0.2, 0.18):
        lathe('Body', [(0.13, 0), (0, 0.28)], 'black', n=4, base=(-0.55 + dx, 1.12, -0.3))
        box('Body', (-0.62 + dx * 1.2, 0.88, -0.63), (0.14, 0.04, 0.04), 'amber')
    for k in range(4):
        a = -0.6 + k * 0.6
        sphere('Body', (0.4 + 0.55 * math.cos(a), 0.62, -0.25 + 0.55 * math.sin(a)), 0.12, 'black', n=6, rings=3)
    finish(note='a woven basket, a pink cushion and a sleeping black cat')


def d_cauldron():
    import math
    decor('Cauldron', 2.6, 2.6)
    for k in range(3):
        a = k * math.tau / 3 + 0.5
        cyl('Body', (0.85 * math.cos(a), 0, 0.85 * math.sin(a)), 0.13, 0.7, 'iron', n=6, r_top=0.16)
    for k in range(3):
        a = k * math.tau / 3
        cyl('Body', (0, 0, 0), 0.14, 1.1, 'wood', n=6,
            m=K.Matrix.Translation((0.5 * math.cos(a), 0.15, 0.5 * math.sin(a))) @ K.Matrix.Rotation(-a, 4, 'Y') @ K.Matrix.Rotation(K.math.radians(-90), 4, 'Z')
            @ K.Matrix.Translation((0, -0.55, 0)))
    lathe('Body', [(0, 0.45), (0.8, 0.55), (1.15, 1.0), (1.15, 1.45), (0.95, 1.85), (1.08, 2.0), (1.1, 2.1), (0.88, 2.05), (0.86, 1.85)],
          'iron', n=12)
    lathe('Glow_Magic_1', [(0, 1.84), (0.86, 1.84), (0.86, 1.92), (0, 1.96)], 'brew', n=12)
    for x, z, r in ((0.3, 0.2, 0.18), (-0.35, -0.1, 0.13), (0.0, -0.4, 0.1)):
        sphere('Glow_Magic_1', (x, 2.0 + r * 0.6, z), r, 'brew', n=6, rings=4)
    finish(note='an iron cauldron on three legs over logs, a glowing green brew with bubbles')


def d_steak_platter():
    import math
    decor('SteakPlatter', 2.6, 2.6)
    lathe('Body', [(1.0, 0), (1.0, 0.15), (0.3, 0.3), (0.22, 2.2), (1.2, 2.35), (1.2, 2.5), (0, 2.5)], 'wood_dark', n=10)
    lathe('Body', [(0, 2.5), (0.95, 2.5), (1.0, 2.62), (0, 2.58)], 'white', n=12, scale=(1, 0.8))
    pts = [(0.7 * math.cos(a) * (1 + 0.12 * math.sin(3 * a)), 0.5 * math.sin(a)) for a in [k * math.tau / 10 for k in range(10)]]
    prism('Body', pts, 2.6, 2.88, {'top': 'meat', 'bottom': 'meat', 'rest': 'crimson'}, plane='xz')
    cyl('Body', (0, 0, 0), 0.08, 0.9, 'bone', n=6, m=K.Matrix.Translation((0.2, 2.85, -0.2)) @ K.Matrix.Rotation(K.math.radians(-80), 4, 'Z'))
    sphere('Body', (1.08, 3.0, -0.2), 0.13, 'bone', n=6, rings=3)
    sphere('Body', (-0.5, 2.9, 0.35), (0.22, 0.06, 0.12), 'leaf', n=6, rings=3)
    finish(note='a steak with its bone on a white platter, on a pedestal table')


def d_moon_window():
    decor('MoonWindow', 3.4, 1.0)
    for x in (-1.3, 1.3):
        span('Body', (x - 0.3, 0, -0.45), (x + 0.3, 0.2, 0.45), 'wood_dark', bevel=0.04)
    span('Body', (-1.6, 0.2, -0.25), (1.6, 0.6, 0.25), 'wood_dark', bevel=0.05)
    for x in (-1.4, 1.4):
        span('Body', (x - 0.2, 0.6, -0.2), (x + 0.2, 4.6, 0.2), 'wood_dark', bevel=0.05)
    outer = arch_points(-1.6, 1.6, 4.6, 6.6, n=5)
    inner = arch_points(-1.2, 1.2, 4.6, 6.0, n=5)
    prism('Body', outer + list(reversed(inner)), -0.2, 0.2, 'wood_dark', plane='xy')
    prism('Body', [(-1.2, 0.6), (1.2, 0.6)] + list(reversed(inner)), -0.04, 0.04, 'night', plane='xy')
    import math
    moon = [(0.25 + 0.85 * math.cos(a), 4.3 + 0.85 * math.sin(a)) for a in [k * math.tau / 12 for k in range(12)]]
    prism('Glow_Cold_1', moon, -0.1, -0.05, 'moonglow', plane='xy')
    span('Body', (-0.06, 0.6, -0.14), (0.06, 6.0, 0.06), 'wood_dark')
    span('Body', (-1.2, 3.0, -0.14), (1.2, 3.12, 0.06), 'wood_dark')
    finish(note='a freestanding gothic window, a full moon glowing in the night pane')


def d_pipe_organ():
    decor('PipeOrgan', 3.8, 3.4)
    span('Body', (-1.8, 0, -0.6), (1.8, 2.6, 0.6), 'wood_dark', bevel=0.1)
    span('Body', (-1.6, 2.2, -0.75), (1.6, 2.45, -0.15), 'white', bevel=0.03)
    span('Body', (-1.8, 2.6, -0.2), (1.8, 3.4, 0.6), 'wood_dark', bevel=0.08)
    for i, h in enumerate((4.0, 4.8, 5.6, 6.6, 5.6, 4.8, 4.0)):
        x = -1.5 + i * 0.5
        cyl('Body', (x, 3.4, 1.05), 0.22, h - 3.4, 'gold', n=8)
        lathe('Body', [(0.22, h), (0, h + 0.3)], 'gold', n=8, base=(x, 0, 1.05))
        box('Body', (x, 3.9, 0.82), (0.2, 0.3, 0.04), 'black')
    span('Body', (-1.2, 0, -1.6), (1.2, 1.3, -1.0), 'wood', bevel=0.06)
    finish(note='a small pipe organ: seven gold pipes over a dark console and its bench')


def d_soundproof_walls():
    import math
    decor('SoundproofWalls', 4.0, 1.6)
    for k, (x, ang) in enumerate(((-1.3, 20), (0, -20), (1.3, 20))):
        m = K.Matrix.Translation((x, 0, 0)) @ K.Matrix.Rotation(K.math.radians(ang), 4, 'Y')
        box('Body', (0, 3.2, 0), (1.3, 6.0, 0.25), 'plum_dark', bevel=0.06, m=m)
        box('Body', (0, 0.1, 0), (0.6, 0.2, 0.5), 'iron', m=m)
        for i in range(2):
            for j in range(3):
                box('Body', (-0.3 + i * 0.6, 1.4 + j * 1.8, -0.16), (0.52, 1.7, 0.12), 'violet', bevel=0.05, m=m)
    finish(note='a three-panel folding screen of quilted violet pads')


def d_chandelier():
    import math
    decor('Chandelier', 3.0, 3.0)
    for k in range(3):
        a = k * math.tau / 3
        box('Body', (0, 0, 0), (1.2, 0.2, 0.2), 'iron',
            m=K.Matrix.Rotation(-a, 4, 'Y') @ K.Matrix.Translation((0.6, 0.12, 0)))
    lathe('Body', [(0.25, 0), (0.12, 0.3), (0.09, 5.6), (0.2, 5.8)], 'iron', n=6)
    lathe('Body', [(1.05, 5.6), (1.25, 5.6), (1.25, 5.78), (1.05, 5.78)], 'gold', n=12, closed=True)
    for k in range(5):
        a = k * math.tau / 5
        x, z = 1.15 * math.cos(a), 1.15 * math.sin(a)
        box('Body', (x / 2, 5.7, z / 2), (0.08, 0.08, 0.08), 'gold')
        cyl('Body', (x, 5.78, z), 0.17, 0.14, 'gold', n=6)
        cyl('Body', (x, 5.92, z), 0.09, 0.45, 'cream', n=6)
        sphere(f'Glow_Warm_{k + 1}', (x, 6.55, z), (0.09, 0.16, 0.09), 'flame', n=6, rings=3)
        sphere('Body', (1.15 * math.cos(a + 0.63), 5.35, 1.15 * math.sin(a + 0.63)), (0.08, 0.16, 0.08), 'lavender', n=6, rings=3)
    for k in range(5):
        a = k * math.tau / 5
        box('Body', (0.57 * math.cos(a), 5.69, 0.57 * math.sin(a)), (0.1, 0.06, 0.1), 'gold')
    sphere('Body', (0, 6.0, 0), (0.2, 0.25, 0.2), 'gold', n=6, rings=4)
    finish(note='a standing iron chandelier: a gold ring of five candles and crystal drops')


DECOR_BUILD = {
    'PuddleRug': d_puddle_rug, 'SnackBasket': d_snack_basket, 'RecordPlayer': d_record_player, 'Candles': d_candles,
    'Planter': d_planter, 'AntiqueWardrobe': d_antique_wardrobe, 'BlackoutCurtains': d_blackout_curtains,
    'SandTray': d_sand_tray, 'CatBasket': d_cat_basket, 'Cauldron': d_cauldron, 'SteakPlatter': d_steak_platter,
    'MoonWindow': d_moon_window, 'PipeOrgan': d_pipe_organ, 'SoundproofWalls': d_soundproof_walls,
    'Chandelier': d_chandelier,
}
ROOM_BUILD = {'StandardRoom': standard_room, 'GardenRoom': garden_room, 'AtticRoom': attic_room,
              'SarcophagusSuite': sarcophagus_suite, 'PotionLoft': potion_loft, 'DenRoom': den_room,
              'CoffinSuite': coffin_suite, 'OperaSuite': opera_suite}
AMENITY_BUILD = {'SnackBar': snack_bar, 'MusicRoom': music_room, 'GraveyardGarden': graveyard_garden,
                 'QuietLibrary': quiet_library, 'OrganHall': organ_hall}


def main():
    K.start_set(SET)
    order = ([('StandardRoom', standard_room), ('Lobby', lobby), ('StairCore', lambda: stairs(False)),
              ('StairCoreTop', lambda: stairs(True)), ('HotelSign', hotel_sign)]
             + [(n, f) for n, f in ROOM_BUILD.items() if n != 'StandardRoom']
             + list(AMENITY_BUILD.items())
             + [(f'Decor_{n}', f) for n, f in DECOR_BUILD.items()])
    refused = []
    for name, fn in order:
        if not want(name):
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
    K.end_set('Haunted Manor hotel kit (Location 1), first draft', rows)
    if refused:
        raise SystemExit(f'REFUSED: {refused}')


main()
