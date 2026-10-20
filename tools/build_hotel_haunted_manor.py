"""Haunted Manor (Location 1): the hotel kit's first set, a draft for August's review.

The 8 rooms and 5 amenities of GDD §5.2 and Pieces.luau, the Lobby (a shell),
the FrontDesk, the stair core (StairCore, and StairCoreTop with its rail), the
HotelSign, the RoomPlaque and the 30 Location 1 decor pieces (five the old
lobby's bench, planter and carpet; the last ten what he named for the manor), each authored on tools/hotel_kit.py in the frames
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
from hotel_kit import LOBBY_W, LOBBY_D, STAIR_S  # noqa: E402

SET = 'hotel/haunted_manor'
ROOMS = [  # id, w, d (Pieces.luau)
    ('StandardRoom', 2, 2), ('GardenRoom', 2, 2), ('AtticRoom', 2, 2), ('SarcophagusSuite', 2, 3),
    ('PotionLoft', 2, 3), ('DenRoom', 3, 3), ('CoffinSuite', 3, 3), ('OperaSuite', 3, 3)]
AMENITIES = ['SnackBar', 'MusicRoom', 'GraveyardGarden', 'QuietLibrary', 'OrganHall']
DECOR = ['PuddleRug', 'SnackBasket', 'RecordPlayer', 'Candles', 'Planter', 'AntiqueWardrobe',
         'BlackoutCurtains', 'SandTray', 'CatBasket', 'Cauldron', 'SteakPlatter', 'MoonWindow',
         'PipeOrgan', 'SoundproofWalls', 'Chandelier',
         'Bench', 'UrnPlanter', 'RugRunner', 'RugCorner', 'RugSquare',    # these five: the old lobby's
         'GrandfatherClock', 'WallClock', 'BlackRoses', 'CarnivorousPlant', 'GhostFern', 'Armchair',
         'VelvetSofa', 'Bookshelf', 'SideTable', 'GrandPiano']            # what he named (§5.4, 2026-10-20)


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
    # Rafters in the top of the room, under the slab, clear of a person's head.
    ry = WALL - 2.1
    for z in (-8.4, -2.8, 2.8, 8.4):
        for sgn in (-1, 1):
            ang = math.degrees(math.atan2(1.6, W / 2 - T))
            box('Dressing', (0, 0, 0), (W / 2 - T + 0.3, 0.45, 0.45), 'wood_dark', bevel=0.05,
                m=K.Matrix.Translation((sgn * (W / 4 - T / 2), ry, z)) @ K.Matrix.Rotation(K.math.radians(-sgn * ang), 4, 'Z'))
        box('Dressing', (0, ry + 0.85, z), (0.6, 0.5, 0.5), 'wood', bevel=0.05)
    span('Dressing', (-0.3, ry + 0.6, -D / 2 + T - 0.02), (0.3, ry + 1.05, D / 2 - T + 0.02), 'wood_dark')
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
    # Herb bundles hanging on long strings from under the slab.
    for x, z in ((-4.5, 4.5), (-1.5, 6.5), (1.5, 6.5), (4.5, 4.5)):
        cyl('Dressing', (x, 9.0, z), 0.04, WALL - 9.05, 'iron', n=4)
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
    zc = zw - 1.8                     # the console's back, against the pipes (it stood 1.8 off the wall)
    span('Centrepiece', (-1.95, 0, zc - 1.8), (1.95, 3.0, zc), 'wood_dark', bevel=0.1)
    span('Centrepiece', (-1.8, 3.0, zc - 1.8), (1.8, 3.3, zc - 0.9), 'white', bevel=0.03)
    span('Centrepiece', (-1.8, 3.3, zc - 1.3), (1.8, 3.55, zc - 0.8), 'black', bevel=0.03)
    span('Centrepiece', (-1.95, 3.0, zc - 0.8), (1.95, 4.4, zc), 'wood_dark', bevel=0.08)
    for i, h in enumerate((5.2, 6.2, 7.0, 7.6, 7.0, 6.2, 5.2)):     # under the sconce at 8.2
        x = -1.62 + i * 0.54
        cyl('Centrepiece', (x, 4.4, zw - 0.6), 0.25, h - 4.4, 'gold', n=8)
        lathe('Centrepiece', [(0.25, h), (0.0, h + 0.35)], 'gold', n=8, base=(x, 0, zw - 0.6))
        span('Centrepiece', (x - 0.12, 5.0, zw - 0.87), (x + 0.12, 5.4, zw - 0.83), 'black')
    span('Centrepiece', (-1.3, 0, zc - 3.2), (1.3, 1.6, zc - 2.4), 'wood', bevel=0.08)
    for k, x in enumerate((-1.6, 1.6)):
        cyl('Centrepiece', (x, 4.4, zc - 1.2), 0.2, 0.12, 'gold', n=8)
        cyl('Centrepiece', (x, 4.52, zc - 1.2), 0.11, 0.6, 'cream', n=6)
        sphere(f'Glow_Warm_{k + 2}', (x, 5.32, zc - 1.2), (0.12, 0.22, 0.12), 'flame', n=6, rings=4)
    for wall, x in (('left', -W / 2 + T), ('right', W / 2 - T)):
        picture((x, 7.0, -2.0), (2.0, 2.6), 'gold', 'wine', wall)
    finish(note='a pipe organ in gold pipes and dark wood, its bench, two candles')


# --- Lobby, stairs, sign -------------------------------------------------------------------------

def lobby():
    """The shell (MODELS.md, "Lobby", his ruling 2026-10-19, GDD 5.4): the front wall round the arch, its
    lantern and sconces, and the tiled Floor; the desk, the benches, the planters and the carpet are
    pieces the player places now (FrontDesk, Decor_Bench, Decor_UrnPlanter, the rugs)."""
    begin('Lobby', 'Lobby', (LOBBY_W, 0.2, LOBBY_D), root_centre=(0, 0.1, LOBBY_D / 2))
    declare('Floor', False)     # as the blockout's: people walk on the plot's slab under it
    # The floor: the whole lobby to its edges (the plot's ground showed at the threshold and the ends),
    # in 6-stud tiles (a cell's 12 read as patchy light, not a checkerboard: blind review 2026-10-19).
    tile = CELL / 2
    for i in range(int(LOBBY_W // tile)):
        for j in range(int(LOBBY_D // tile)):
            x0, z0 = -LOBBY_W / 2 + i * tile, j * tile
            span('Floor', (x0, 0, z0), (x0 + tile, K.LOBBY_FLOOR_TOP, z0 + tile), 'plum' if (i + j) % 2 else 'plum_dark')
    # The front wall round the arch (MODELS.md, "Lobby"), the hotel's outside colour to the street.
    K.lobby_front_wall(outside='plum', paper='lilac', wainscot='plum_dark', crown='gold',
                       plinth='stone_dark', frame='wood_dark', sill='gold')
    # The front arch: pillars and a pointed top (opening 9 wide, 9 tall at its sides).
    for name, x in (('ArchLeft', -5), ('ArchRight', 5)):
        span(name, (x - 0.5, 0, 0), (x + 0.5, 0.6, 1), 'stone_dark', bevel=0.08)
        span(name, (x - 0.42, 0.6, 0.08), (x + 0.42, 8.4, 0.92), 'stone', bevel=0.1)
        span(name, (x - 0.5, 8.4, 0), (x + 0.5, 9.0, 1), 'gold', bevel=0.08)
    inner = arch_points(-4.5, 4.5, 9.0, 10.6, n=5)
    outline = [(-5.5, 9.0)] + [(-5.5, 10.4), (0, 11.8), (5.5, 10.4)] + [(5.5, 9.0)] + list(reversed(inner))
    prism('ArchTop', outline, 0.05, 0.95, {'front': 'plum', 'back': 'plum', 'rest': 'gold'}, plane='xy')
    pumpkin('ArchTop', (0, 11.15, 0.5), 0.4)
    # The wall over the gable, up to the slab: the arch is a door's height, the wall the storey's.
    over = [(-5.5, 10.41), (0, 11.81), (5.5, 10.41), (5.5, K.LOBBY_WIN_HI), (-5.5, K.LOBBY_WIN_HI)]
    prism('ArchTop', over, 0.0, K.LOBBY_WALL_T, {'front': 'plum', 'back': 'lilac', 'rest': 'lilac'}, plane='xy')
    course = K.LOBBY_WIN_HI + 0.5
    span('ArchTop', (-5.5, K.LOBBY_WIN_HI, 0.0), (5.5, course, K.LOBBY_WALL_T), 'gold')
    span('ArchTop', (-5.5, course, 0.0), (5.5, WALL - 0.4, K.LOBBY_WALL_T), {'front': 'plum', 'back': 'lilac', 'rest': 'lilac'})
    span('ArchTop', (-5.5, WALL - 0.4, 0.0), (5.5, WALL, K.LOBBY_WALL_T), 'gold')
    # The lantern hanging inside the arch, its chain from the ceiling.
    cyl('Dressing', (0, 10.7, 1.5), 0.05, WALL - 10.7, 'iron', n=4)
    box('Dressing', (0, 10.7, 1.5), (0.8, 0.12, 0.8), 'iron')
    box('Dressing', (0, 9.3, 1.5), (0.8, 0.12, 0.8), 'iron')
    for dx in (-0.36, 0.36):
        for dz in (-0.36, 0.36):
            box('Dressing', (dx, 10.0, 1.5 + dz), (0.08, 1.3, 0.08), 'iron')
    sphere('Glow_Warm_1', (0, 10.0, 1.5), (0.3, 0.45, 0.3), 'lamp', n=8, rings=5)
    for n, x in enumerate(K.LOBBY_SCONCES):
        K.lobby_sconce(x, 7.2, n + 2, 'gold', candle='bone')
    for aname, (pos, look) in K.blockout_attachments('Lobby').items():
        attach(aname, pos, look)
    finish(note='the lobby shell: the front wall with windows round the pointed arch, its lantern and sconces, '
                'the plum tiled floor; everything else is placed by the player')


def front_desk():
    """The reception desk as a piece (MODELS.md, "Front desk"): the old lobby desk re-laid, served
    toward -Z: the counter with violet panels and a gold top, the bell at the check-in prompt, the
    ledger, the till on its +X end, the lamp on its -X end, the key rack and clock behind the clerk."""
    begin('FrontDesk', 'Desk', (K.DESK_W, 0.2, K.DESK_D))
    (lo, hi), (tlo, thi) = K.DESK_COUNTER, K.DESK_TOP
    span('Counter', lo, hi, 'wood_dark', bevel=0.1)
    for x in (-3.6, -1.8, 0.0, 1.8, 3.6):
        span('Counter', (x - 0.75, 0.5, lo[2] - 0.13), (x + 0.75, 3.0, lo[2] + 0.1), 'violet', bevel=0.06)
        sphere('Counter', (x, 1.75, lo[2] - 0.14), (0.35, 0.35, 0.06), 'gold', n=8, rings=4)
    span('Counter', tlo, thi, 'gold', bevel=0.05)
    K.desk_bell('Dressing', 0.0, thi[1], lo[2] + 0.4, 'gold')          # at the check-in prompt
    span('Dressing', (0.8, thi[1], lo[2] + 0.4), (1.8, thi[1] + 0.15, lo[2] + 1.3), 'crimson', bevel=0.03)
    K.desk_till(body='wood_dark', keys='pumpkin', drawer='gold', screen='bone')
    K.desk_lamp('gold', 'teal')
    K.desk_keyrack(cabinet='wood_dark', drawer='wood', knob='gold', board='plum_dark',
                   tags=('gold', 'gold', 'pumpkin'), cornice='gold', face='bone', hands='black')
    for aname, (pos, look) in K.blockout_attachments('Desk').items():
        attach(aname, pos, look)
    finish(note='the old lobby desk as a 2 x 1 piece: a dark counter with violet panels and a gold top, a bell, '
                'a ledger, an antique till, a teal-shaded lamp, the key rack and clock behind the clerk')


def stairs(top):
    name = 'StairCoreTop' if top else 'StairCore'
    begin(name, 'Stairs', (STAIR_S, 0.2, STAIR_S))
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
    hs = STAIR_S / 2
    sconce(-hs + T, 14.5, -4.0, 'left', 1)
    K.stair_handrails('gold', 'iron')
    K.stair_soffits('plum_dark')
    yp = K.STAIR_LANDING_Y + (3.6 if not top else 4.6)
    picture((0, yp, hs - T), (2.4, 2.6), 'gold', 'plum')
    sphere('Dressing', (0, yp + 0.3, hs - T - 0.13), (0.55, 0.6, 0.05), 'lilac', n=8, rings=4)
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


# --- Decor (MODELS.md, "Decor": origin at the base centre, front -Z, fw x fd squares of 3 studs) ----
# The pieces built before the 3-stud grid are refitted (K.refit_decor: scaled down at most 0.4, shifted,
# a Wall piece's back onto the wall), with no other change of look.

decor = K.decor


def d_bench():
    decor('Bench', 3, 1, 'Floor')
    K.decor_bench(7.0, frame='wood_dark', cushion='crimson', back='violet')
    finish(note='the old lobby bench: dark wood, a crimson cushion, violet back rails, arms')


def d_urn_planter():
    import math
    decor('UrnPlanter', 1, 1, 'Floor')
    lathe('Body', [(0.7, 0), (0.9, 0.2), (1.0, 1.4), (1.1, 1.6), (1.1, 1.8), (0.9, 1.8)], 'stone', n=8)
    pumpkin('Body', (-0.2, 2.25, -0.1), 0.6)
    for a in range(4):
        sphere('Body', (0.6 * math.cos(a * 1.6), 2.0, 0.6 * math.sin(a * 1.6)), (0.4, 0.15, 0.3), 'leaf', n=6, rings=3)
    finish(note='the old lobby planter: a stone urn with a pumpkin among leaves')


def d_rug_runner():
    decor('RugRunner', 4, 2, 'Rug')
    K.rug('runner', border='gold', field='crimson', pin='gold', motif='gold', motif_inner='crimson_dark')
    finish(note='the old gold-and-crimson carpet as a 12 x 6 runner: gold borders on its long sides, its ends open')


def d_rug_corner():
    decor('RugCorner', 2, 2, 'Rug')
    K.rug('corner', border='gold', field='crimson', pin='gold', motif='gold', motif_inner='crimson_dark')
    finish(note='the runner\'s corner: bordered on +X and +Z, joining a runner from -X and one toward -Z')


def d_rug_square():
    decor('RugSquare', 4, 4, 'Rug')
    K.rug('square', border='gold', field='crimson', pin='gold', motif='gold', motif_inner='crimson_dark')
    finish(note='a 12 x 12 gold-bordered crimson rug with a medallion')


def d_puddle_rug():
    import math
    decor('PuddleRug', 2, 2, 'Floor')
    rr = (1.7, 1.45, 1.75, 1.5, 1.65, 1.35, 1.7, 1.55, 1.6, 1.4)
    pts = [(rr[k] * math.cos(k * math.tau / 10), rr[k] * math.sin(k * math.tau / 10)) for k in range(10)]
    prism('Body', pts, 0, 0.06, 'sky', plane='xz')
    prism('Body', [(x * 0.62 + 0.15, z * 0.62 - 0.1) for x, z in pts], 0.06, 0.08, 'moon', plane='xz')
    prism('Body', [(x * 0.35 + 0.25, z * 0.35 - 0.15) for x, z in pts], 0.08, 0.1, 'sky', plane='xz')
    sphere('Body', (-0.7, 0.35, 0.5), (0.3, 0.25, 0.35), 'amber', n=8, rings=4)
    sphere('Body', (-0.7, 0.72, 0.3), 0.19, 'amber', n=8, rings=4)
    box('Body', (-0.7, 0.68, 0.08), (0.14, 0.06, 0.16), 'pumpkin')
    K.refit_decor()
    finish(note='a puddle-blue rug with ripples and a rubber duck')


def d_snack_basket():
    decor('SnackBasket', 1, 1, 'Floor')
    lathe('Body', [(0.75, 0), (1.0, 0.8), (1.05, 0.9), (0.9, 0.9), (0.68, 0.15)], 'straw', n=10, closed=True)
    lathe('Body', [(0, 0.1), (0.75, 0.1), (0.85, 0.7), (0, 0.7)], 'wood_light', n=10)
    for k in range(5):
        a = k * 3.14159 / 4
        box('Body', (0, 0, 0), (0.42, 0.12, 0.14), 'wood',
            m=K.Matrix.Translation((-0.95 * K.math.cos(a), 0.9 + 0.95 * K.math.sin(a), 0)) @ K.Matrix.Rotation(-a + K.math.pi / 2, 4, 'Z'))
    for x, z, colr in ((-0.4, -0.2, 'pumpkin'), (0.35, 0.25, 'rose'), (0.1, -0.45, 'slime'), (-0.2, 0.45, 'amber')):
        sphere('Body', (x, 0.85, z), 0.26, colr, n=6, rings=4)
    cyl('Body', (0.45, 0.75, -0.35), 0.3, 0.12, 'honey', n=8)
    K.refit_decor()
    finish(note='a wicker basket of candies and a cookie')


def d_record_player():
    decor('RecordPlayer', 1, 1, 'Floor')
    span('Body', (-0.9, 0, -0.8), (0.9, 2.0, 0.8), 'wood', bevel=0.1)
    span('Body', (-0.75, 0.25, -0.84), (0.75, 1.75, -0.78), 'wood_dark', bevel=0.04)
    box('Body', (0, 1.0, -0.86), (0.4, 0.1, 0.06), 'gold')
    span('Body', (-0.95, 2.0, -0.85), (0.95, 2.15, 0.85), 'gold', bevel=0.04)
    cyl('Body', (-0.15, 2.15, -0.1), 0.62, 0.06, 'black', n=12)
    cyl('Body', (-0.15, 2.21, -0.1), 0.18, 0.02, 'crimson', n=8)
    box('Body', (0.6, 2.3, 0.0), (0.08, 0.08, 0.8), 'gold')
    lathe('Body', [(0.1, 0), (0.12, 0.5), (0.3, 1.2), (0.85, 1.75), (0.95, 1.8)], 'gold', n=10,
          m=K.Matrix.Translation((0.2, 2.15, 0.55)) @ K.Matrix.Rotation(K.math.radians(-30), 4, 'X'))
    K.refit_decor()
    finish(note='a wooden cabinet gramophone with a gold flower horn')


def d_candles():
    decor('Candles', 1, 1, 'Floor')
    cyl('Body', (0, 0, 0), 0.9, 0.15, 'gold', n=10)
    for k, (x, z, h) in enumerate(((-0.35, 0.2, 1.4), (0.35, 0.25, 1.0), (0.0, -0.4, 0.7))):
        cyl('Body', (x, 0.15, z), 0.2, h, 'cream', n=8)
        sphere('Body', (x + 0.15, 0.15 + h - 0.15, z - 0.12), (0.06, 0.14, 0.06), 'cream', n=6, rings=3)
        sphere(f'Glow_Warm_{k + 1}', (x, 0.15 + h + 0.22, z), (0.11, 0.2, 0.11), 'flame', n=6, rings=4)
    K.refit_decor()
    finish(note='three cream candles on a gold dish, each flame its own glow')


def d_planter():
    import math
    decor('Planter', 1, 1, 'Floor')
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
    K.refit_decor()
    finish(note='a stone pot with a teal band and a violet-budded spooky plant')


def d_antique_wardrobe():
    decor('AntiqueWardrobe', 2, 1, 'Floor')
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
    K.refit_decor()
    finish(note='a tall carved wardrobe with a crown top and gold knobs')


def d_blackout_curtains():
    import math
    decor('BlackoutCurtains', 2, 1, 'Wall')
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
    K.refit_decor()
    finish(note='heavy plum curtains on an iron rod, closed, a gold tie across each')


def d_sand_tray():
    decor('SandTray', 2, 1, 'Floor')
    for x in (-1.3, 1.3):
        for z in (-0.95, 0.95):
            cyl('Body', (x, 0, z), 0.12, 0.6, 'wood_dark', n=6)
    span('Body', (-1.45, 0.6, -1.1), (1.45, 0.75, 1.1), 'wood_light', bevel=0.04)
    for (x0, z0, x1, z1) in ((-1.45, -1.1, 1.45, -0.95), (-1.45, 0.95, 1.45, 1.1), (-1.45, -0.95, -1.3, 0.95), (1.3, -0.95, 1.45, 0.95)):
        span('Body', (x0, 0.75, z0), (x1, 1.05, z1), 'wood', bevel=0.03)
    span('Body', (-1.3, 0.75, -0.95), (1.3, 0.95, 0.95), 'sand')
    lathe('Body', [(0.45, 0.95), (0.0, 1.45)], 'honey', n=4, base=(0.5, 0, 0.2), phase=0.785)
    box('Body', (-0.6, 1.0, -0.2), (0.08, 0.06, 1.0), 'wood_dark')
    box('Body', (-0.6, 1.005, -0.72), (0.5, 0.06, 0.08), 'wood_dark')
    K.refit_decor()
    finish(note='a wooden tray of raked sand with a little pyramid')


def d_cat_basket():
    import math
    decor('CatBasket', 1, 1, 'Floor')
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
    K.refit_decor()
    finish(note='a woven basket, a pink cushion and a sleeping black cat')


def d_cauldron():
    import math
    decor('Cauldron', 1, 1, 'Floor')
    for k in range(3):
        a = k * math.tau / 3 + 0.5
        cyl('Body', (0.85 * math.cos(a), 0, 0.85 * math.sin(a)), 0.13, 0.7, 'iron', n=6, r_top=0.16)
    for k in range(3):
        a = k * math.tau / 3
        cyl('Body', (0, 0, 0), 0.14 - 0.006 * k, 1.1, 'wood', n=6,
            m=K.Matrix.Translation((0.5 * math.cos(a), 0.15, 0.5 * math.sin(a))) @ K.Matrix.Rotation(-a, 4, 'Y') @ K.Matrix.Rotation(K.math.radians(-90), 4, 'Z')
            @ K.Matrix.Translation((0, -0.55, 0)))
    lathe('Body', [(0, 0.45), (0.8, 0.55), (1.15, 1.0), (1.15, 1.45), (0.95, 1.85), (1.08, 2.0), (1.1, 2.1), (0.88, 2.05), (0.86, 1.85)],
          'iron', n=12)
    lathe('Glow_Magic_1', [(0, 1.84), (0.86, 1.84), (0.86, 1.92), (0, 1.96)], 'brew', n=12)
    for x, z, r in ((0.3, 0.2, 0.18), (-0.35, -0.1, 0.13), (0.0, -0.4, 0.1)):
        sphere('Glow_Magic_1', (x, 2.0 + r * 0.6, z), r, 'brew', n=6, rings=4)
    K.refit_decor()
    finish(note='an iron cauldron on three legs over logs, a glowing green brew with bubbles')


def d_steak_platter():
    import math
    decor('SteakPlatter', 1, 1, 'Floor')
    lathe('Body', [(1.0, 0), (1.0, 0.15), (0.3, 0.3), (0.22, 2.2), (1.2, 2.35), (1.2, 2.5), (0, 2.5)], 'wood_dark', n=10)
    lathe('Body', [(0, 2.5), (0.95, 2.5), (1.0, 2.62), (0, 2.58)], 'white', n=12, scale=(1, 0.8))
    pts = [(0.7 * math.cos(a) * (1 + 0.12 * math.sin(3 * a)), 0.5 * math.sin(a)) for a in [k * math.tau / 10 for k in range(10)]]
    prism('Body', pts, 2.6, 2.88, {'top': 'meat', 'bottom': 'meat', 'rest': 'crimson'}, plane='xz')
    cyl('Body', (0, 0, 0), 0.08, 0.9, 'bone', n=6, m=K.Matrix.Translation((0.2, 2.85, -0.2)) @ K.Matrix.Rotation(K.math.radians(-80), 4, 'Z'))
    sphere('Body', (1.08, 3.0, -0.2), 0.13, 'bone', n=6, rings=3)
    sphere('Body', (-0.5, 2.9, 0.35), (0.22, 0.06, 0.12), 'leaf', n=6, rings=3)
    K.refit_decor()
    finish(note='a steak with its bone on a white platter, on a pedestal table')


def d_moon_window():
    decor('MoonWindow', 2, 1, 'Wall')
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
    span('Body', (-1.2, 3.0, -0.13), (1.2, 3.12, 0.05), 'wood_dark')
    K.refit_decor()
    finish(note='a freestanding gothic window, a full moon glowing in the night pane')


def d_pipe_organ():
    decor('PipeOrgan', 2, 2, 'Wall')
    span('Body', (-1.8, 0, -0.6), (1.8, 2.6, 0.6), 'wood_dark', bevel=0.1)
    span('Body', (-1.6, 2.2, -0.75), (1.6, 2.45, -0.15), 'white', bevel=0.03)
    span('Body', (-1.8, 2.6, -0.2), (1.8, 3.4, 0.6), 'wood_dark', bevel=0.08)
    for i, h in enumerate((4.0, 4.8, 5.6, 6.6, 5.6, 4.8, 4.0)):
        x = -1.5 + i * 0.5
        cyl('Body', (x, 3.4, 1.05), 0.22, h - 3.4, 'gold', n=8)
        lathe('Body', [(0.22, h), (0, h + 0.3)], 'gold', n=8, base=(x, 0, 1.05))
        box('Body', (x, 3.9, 0.82), (0.2, 0.3, 0.04), 'black')
    span('Body', (-1.2, 0, -1.6), (1.2, 1.3, -1.0), 'wood', bevel=0.06)
    K.refit_decor()
    finish(note='a small pipe organ: seven gold pipes over a dark console and its bench')


def d_soundproof_walls():
    import math
    decor('SoundproofWalls', 2, 1, 'Wall')
    for k, (x, ang) in enumerate(((-1.3, 20), (0, -20), (1.3, 20))):
        m = K.Matrix.Translation((x, 0, 0)) @ K.Matrix.Rotation(K.math.radians(ang), 4, 'Y')
        box('Body', (0, 3.2, 0), (1.3, 6.0, 0.25), 'plum_dark', bevel=0.06, m=m)
        box('Body', (0, 0.1, 0), (0.6, 0.2, 0.5), 'iron', m=m)
        for i in range(2):
            for j in range(3):
                box('Body', (-0.3 + i * 0.6, 1.4 + j * 1.8, -0.16), (0.52, 1.7, 0.12), 'violet', bevel=0.05, m=m)
    K.refit_decor()
    finish(note='a three-panel folding screen of quilted violet pads')


def d_chandelier():
    import math
    decor('Chandelier', 1, 1, 'Floor')
    for k in range(3):
        a = k * math.tau / 3
        box('Body', (0, 0, 0), (1.2, 0.2 + 0.01 * k, 0.2), 'iron',
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
        box('Body', (0.57 * math.cos(a), 5.695, 0.57 * math.sin(a)), (0.1, 0.06, 0.1), 'gold')
    sphere('Body', (0, 6.0, 0), (0.2, 0.25, 0.2), 'gold', n=6, rings=4)
    K.refit_decor()
    finish(note='a standing iron chandelier: a gold ring of five candles and crystal drops')


# --- The decor he named for Haunted Manor (GDD §5.4, A.2; WAITING §2.24). His picks from the grey
# silhouettes (2026-10-20): the longcase clock (A), the grand piano (A), the Armchair kept at 1 x 1.
# Each keeps its silhouette's frame and outline; detail, palette and glows added here.

import math  # noqa: E402
from mathutils import Vector, Matrix  # noqa: E402
from hotel_kit import at  # noqa: E402


def limb(part, a, b, r0, r1, col, n=6):
    """A tapered rod from point a to point b."""
    a, b = Vector(a), Vector(b)
    d = b - a
    rot = Vector((0, 1, 0)).rotation_difference(d.normalized()).to_matrix().to_4x4()
    cyl(part, (0, 0, 0), r0, d.length, col, n=n, r_top=r1, m=Matrix.Translation(a) @ rot)


def tilt_to(pos, direction):
    """A transform putting local +Y along `direction` at `pos`."""
    rot = Vector((0, 1, 0)).rotation_difference(Vector(direction).normalized()).to_matrix().to_4x4()
    return Matrix.Translation(Vector(pos)) @ rot


def clock_face(c, r):
    """A dial on a front (-Z) face whose surface is at c.z: a gold bezel, a bone face, twelve hour
    marks and the hands at ten past ten, each a hair proud of the last."""
    x, y, z = c
    cyl('Body', (0, 0, 0), r + 0.09, 0.06, 'gold', n=20, m=at((x, y, z), rx=-90))
    cyl('Body', (0, 0, 0), r, 0.08, 'bone', n=20, m=at((x, y, z), rx=-90))
    zf = z - 0.08
    for k in range(12):
        a = k * math.tau / 12
        big = k % 3 == 0
        ln = r * (0.22 if big else 0.13)
        rr = r * 0.8
        box('Body', (0, 0, 0), (0.07 if big else 0.045, ln, 0.03), 'ink',
            m=at((x + rr * math.sin(a), y + rr * math.cos(a), zf - 0.012), rz=-math.degrees(a)))
    for k, (deg, ln, w) in enumerate(((300, 0.5, 0.075), (60, 0.78, 0.05))):   # hour at ten, minute at two
        box('Body', (0, ln * r / 2, 0), (w, ln * r, 0.03), 'black', m=at((x, y, zf - 0.04 - 0.012 * k), rz=-deg))
    cyl('Body', (0, 0, 0), 0.06, 0.085, 'gold', n=8, m=at((x, y, zf), rx=-90))


def d_grandfather_clock():
    """His pick A: a longcase clock. Bracket feet, a panelled plinth, a trunk whose door has a pointed
    glass window and the brass pendulum behind it, a hood with gilt columns, the dial with a moon arch
    above it, a cornice and a round pediment with three gilt finials."""
    decor('GrandfatherClock', 1, 1, 'Floor')
    for x in (-0.8, 0.8):
        for z in (-0.6, 0.6):
            span('Body', (x - 0.16, 0, z - 0.14), (x + 0.16, 0.3, z + 0.14), 'wood_dark', bevel=0.05)
    span('Body', (-0.98, 0.28, -0.76), (0.98, 1.1, 0.76), 'wood_dark', bevel=0.06)           # plinth
    span('Body', (-0.62, 0.42, -0.8), (0.62, 0.96, -0.74), 'wood', bevel=0.03)               # its panel
    span('Body', (-1.03, 1.1, -0.8), (1.03, 1.26, 0.8), 'wood', bevel=0.05)                  # base moulding
    span('Body', (-0.72, 1.26, -0.6), (0.72, 4.35, 0.6), 'wood_dark', bevel=0.05)            # trunk
    span('Body', (-0.56, 1.45, -0.64), (0.56, 4.15, -0.58), 'wood', bevel=0.03)              # trunk door
    win = [(-0.34, 2.25)] + arch_points(-0.34, 0.34, 3.5, 3.95, n=4) + [(0.34, 2.25)]
    prism('Body', win, -0.68, -0.62, 'night', plane='xy')                                       # its glass
    span('Body', (-0.025, 3.0, -0.72), (0.025, 3.85, -0.68), 'gold')                           # pendulum rod
    cyl('Body', (0, 0, 0), 0.22, 0.05, 'gold', n=14, m=at((0, 2.88, -0.68), rx=-90))           # its bob
    span('Body', (-0.86, 4.35, -0.72), (0.86, 4.55, 0.72), 'wood', bevel=0.04)               # waist moulding
    span('Body', (-0.95, 4.55, -0.78), (0.95, 6.05, 0.76), 'wood_dark', bevel=0.05)          # hood
    for x in (-0.84, 0.84):
        cyl('Body', (x, 4.55, -0.84), 0.07, 1.5, 'gold', n=8)                                  # hood columns
    arc = [(0.38 * math.cos(math.pi * i / 8), 5.62 + 0.38 * math.sin(math.pi * i / 8)) for i in range(9)]
    prism('Body', arc, -0.81, -0.77, 'night', plane='xy')                                       # moon arch
    outer = [(0.15 + 0.15 * math.cos(a), 5.86 + 0.13 * math.sin(a)) for a in
             [math.radians(70 + 220 * i / 10) for i in range(11)]]
    inner = [(0.21 + 0.12 * math.cos(a), 5.88 + 0.1 * math.sin(a)) for a in
             [math.radians(255 - 160 * i / 8) for i in range(9)]]
    prism('Body', outer + inner, -0.83, -0.79, 'moon', plane='xy')                            # a crescent
    clock_face((0, 5.1, -0.78), 0.5)
    span('Body', (-1.04, 6.05, -0.86), (1.04, 6.22, 0.8), 'wood', bevel=0.04)                # cornice
    prism('Body', K.round_arch_points(-0.98, 0.98, 6.22, 6.62, n=8), -0.74, 0.7, 'wood_dark', plane='xy')
    sphere('Body', (0, 6.36, -0.75), (0.15, 0.1, 0.03), 'gold', n=8, rings=4)                 # cartouche
    for x in (-0.86, 0.86):
        lathe('Body', [(0.1, 6.22), (0.12, 6.28), (0.06, 6.36), (0.1, 6.46), (0, 6.58)], 'gold', n=8,
              base=(x, 0, -0.8))
    lathe('Body', [(0.13, 6.56), (0.16, 6.64), (0.08, 6.74), (0.12, 6.82), (0, 6.95)], 'gold', n=8)
    finish(note='his pick A: a longcase clock, a pointed glass trunk window with the brass pendulum, '
                'a moon arch over the dial, gilt columns, a round pediment and three finials')


def d_wall_clock():
    """A round wall clock over a pendulum box with a pointed glass window, a drop finial below and a
    gilt finial on top, hung from 3 to 7 on the wall."""
    decor('WallClock', 1, 1, 'Wall')
    zb = 1.1                                                                          # the wall's face
    span('Body', (-0.55, 3.35, zb - 0.38), (0.55, 5.05, zb), 'wood_dark', bevel=0.05)
    win = [(-0.32, 3.55)] + arch_points(-0.32, 0.32, 4.45, 4.82, n=3) + [(0.32, 3.55)]
    prism('Body', win, zb - 0.42, zb - 0.36, 'night', plane='xy')
    span('Body', (-0.022, 3.85, zb - 0.46), (0.022, 4.75, zb - 0.42), 'gold')
    cyl('Body', (0, 0, 0), 0.17, 0.05, 'gold', n=12, m=at((0, 3.78, zb - 0.42), rx=-90))
    lathe('Body', [(0.2, 3.37), (0.15, 3.22), (0.07, 3.08), (0.09, 3.0), (0, 2.92)], 'wood_dark', n=8,
          base=(0, 0, zb - 0.19))
    cyl('Body', (0, 0, 0), 0.95, 0.43, 'wood_dark', n=24, m=at((0, 5.85, zb), rx=-90))      # the round case
    clock_face((0, 5.85, zb - 0.43), 0.72)
    lathe('Body', [(0.0, 6.76), (0.13, 6.82), (0.07, 6.88), (0.09, 6.92), (0, 6.98)], 'gold', n=8,
          base=(0, 0, zb - 0.19))
    finish(note='a round wall clock over a pendulum box with a pointed glass window and a brass bob')


def d_black_roses():
    """Seven black roses with red hearts in a teal vase with a gold band, on a slim turned plum pedestal."""
    decor('BlackRoses', 1, 1, 'Floor')
    lathe('Body', [(0.62, 0), (0.64, 0.1), (0.5, 0.18), (0.2, 0.32), (0.13, 0.9), (0.2, 1.25), (0.13, 1.6),
                   (0.13, 2.0), (0.3, 2.18), (0.56, 2.26), (0.56, 2.38), (0, 2.38)], 'plum', n=10)
    lathe('Body', [(0.22, 2.38), (0.34, 2.48), (0.46, 2.78), (0.44, 3.1), (0.24, 3.42), (0.2, 3.52),
                   (0.3, 3.66), (0.26, 3.72), (0, 3.6)], 'teal_dark', n=10)
    lathe('Body', [(0.44, 2.88), (0.475, 2.93), (0.44, 2.98)], 'gold', n=10, closed=True)
    roses = [((0, 4.62, 0), (0, 1, 0))]
    for k in range(6):
        a = k * math.tau / 6 + 0.3
        out = Vector((math.cos(a), 0, math.sin(a)))
        roses.append((tuple(Vector((0, 4.18 + 0.16 * (k % 2), 0)) + out * 0.5), tuple(out * 0.7 + Vector((0, 1, 0)))))
    for pos, up in roses:
        m = tilt_to(pos, up)
        lathe('Body', [(0, -0.14), (0.17, -0.1), (0.27, 0.02), (0.25, 0.1), (0.15, 0.06), (0, 0.05)],
              'black', n=7, m=m)
        sphere('Body', (0, 0.06, 0), (0.13, 0.1, 0.13), 'crimson', n=6, rings=3, m=m)
        foot = Vector(pos) - Vector(up).normalized() * 0.12
        limb('Body', (foot.x * 0.25, 3.55, foot.z * 0.25), foot, 0.035, 0.03, 'moss', n=4)
    for k in range(3):
        a = k * math.tau / 3 + 1.0
        sphere('Body', (0, 0, 0.3), (0.12, 0.03, 0.3), 'moss', n=6, rings=3,
               m=at((0.2 * math.cos(a), 3.75, 0.2 * math.sin(a)), ry=-math.degrees(a) + 90, rx=25))
    finish(note='seven black roses with red hearts in a teal vase with a gold band, on a slim plum pedestal')


def d_carnivorous_plant():
    """A flytrap in a stone pot with a teal band: a thick curved stalk, the trap's two dark green lobes
    gaping toward the front, wine-red inside, straw-coloured cilia for teeth, a small closed trap on a side stalk, leaves over the rim."""
    decor('CarnivorousPlant', 1, 1, 'Floor')
    lathe('Body', [(0.5, 0), (0.55, 0.05), (0.72, 0.85), (0.86, 0.9), (0.88, 1.15), (0.74, 1.15), (0.7, 0.9),
                   (0, 0.9)], 'stone_dark', n=12)
    lathe('Body', [(0.63, 0.42), (0.68, 0.5), (0.665, 0.58)], 'teal_dark', n=12, closed=True)
    cyl('Body', (0, 0.92, 0), 0.7, 0.1, 'wood_dark', n=12)                                    # soil
    pts = [(0, 0.95, 0.1), (0.05, 1.9, 0.15), (0.05, 2.6, -0.05), (0.0, 3.05, -0.1)]
    for a, b, r0, r1 in zip(pts, pts[1:], (0.19, 0.16, 0.14), (0.16, 0.14, 0.12)):
        limb('Body', a, b, r0, r1, 'moss', n=8)
    hinge = (0, 3.05, -0.1)
    for tilt, inner, sign in ((38, 'bottom', -1), (-22, 'top', 1)):
        m = at(hinge, rx=tilt)
        sphere('Body', (0, 0, -0.42), (0.62, 0.11, 0.44), {inner: 'wine', 'rest': 'moss'}, n=12, rings=4, m=m)
        for k in range(9):
            t = math.pi * (0.08 + 0.84 * k / 8)
            rim = (0.58 * math.cos(t), 0, -0.42 - 0.4 * math.sin(t))
            lathe('Body', [(0.055, 0), (0.0, sign * 0.3)], 'straw', n=4, base=rim, m=m)
    limb('Body', (0.1, 0.95, 0.15), (0.45, 1.75, 0.35), 0.08, 0.06, 'moss', n=6)               # the bud's stalk
    sphere('Body', (0.5, 1.98, 0.38), (0.17, 0.26, 0.12), {'front': 'wine', 'rest': 'moss'}, n=8, rings=4)
    for dx in (-0.08, 0.0, 0.08):
        lathe('Body', [(0.03, 0), (0.0, 0.14)], 'straw', n=4, base=(0.5 + dx, 2.2, 0.38))
    for a in (0.4, 2.3, 4.2):
        sphere('Body', (0, 0, 0.55), (0.18, 0.05, 0.55), 'leaf', n=6, rings=3,
               m=at((0, 1.21, 0), ry=math.degrees(a), rx=-6))
    finish(note='a flytrap in a stone pot, dark green jaws wine-red inside with straw cilia, a closed bud')


def d_ghost_fern():
    """A pale fern in a plum pot on a three-legged stand: eight lobed fronds arching up,
    out and down."""
    decor('GhostFern', 1, 1, 'Floor')
    for k in range(3):
        a = k * math.tau / 3 + 0.5
        d = Vector((math.cos(a), 0, math.sin(a)))
        limb('Body', tuple(d * 0.42 + Vector((0, 1.62, 0))), tuple(d * 0.78 + Vector((0, 0.09, 0))), 0.11, 0.08,
             'wood_dark', n=6)
        sphere('Body', tuple(d * 0.79 + Vector((0, 0.11, 0))), 0.1, 'wood_dark', n=6, rings=3)
    cyl('Body', (0, 1.58, 0), 0.72, 0.14, 'wood_dark', n=10)
    lathe('Body', [(0.36, 1.72), (0.44, 1.78), (0.6, 2.45), (0.68, 2.52), (0.68, 2.64), (0.58, 2.64),
                   (0.56, 2.5), (0, 2.5)], 'plum', n=10)
    cyl('Body', (0, 2.48, 0), 0.55, 0.07, 'wood_dark', n=10)                                   # soil
    base = Vector((0, 2.55, 0))
    fronds = [(45, 1.3, 0.55, 0.75), (100, 0.9, 0.5, 0.6), (150, 1.05, 0.55, 0.7), (205, 0.95, 0.5, 0.65),
              (232, 1.2, 0.55, 0.75), (300, 0.9, 0.5, 0.6), (345, 1.05, 0.55, 0.7), (20, 0.8, 0.85, 0.45)]
    for yaw, reach, rise, droop in fronds:
        a = math.radians(yaw)
        h = Vector((math.cos(a), 0, math.sin(a)))
        s = Vector((-h.z, 0, h.x))

        def p(t):
            return base + h * (reach * t) + Vector((0, 4 * rise * t * (1 - t) - droop * t * t, 0))
        # One blade per frond: its two edges folded down at each station, its width tapering from the bare
        # stem to the tip and every other station pinched to a third (the pinnae), a jade rib along it.
        n = 15
        top, bot = [], []
        for i in range(n):
            t = 0.04 + 0.96 * i / (n - 1)
            c = p(t)
            tan = (p(min(1.0, t + 0.02)) - p(max(0.0, t - 0.02))).normalized()
            up = s.cross(tan).normalized()
            w = (0.62 * min(1.0, t / 0.25) * ((1 - t) / 0.75 if t > 0.25 else 1.0) + 0.04) * (1.0 if i % 2 else 0.35)
            for q in (c - s * w - up * 0.3 * w, c + s * w - up * 0.3 * w):
                top.append(q + up * 0.015)
                bot.append(q - up * 0.015)
        faces = []
        o = 2 * n
        for i in range(n - 1):
            a, b = 2 * i, 2 * (i + 1)
            faces += [(a, a + 1, b + 1, b), (o + a, o + b, o + b + 1, o + a + 1),
                      (a, b, o + b, o + a), (a + 1, o + a + 1, o + b + 1, b + 1)]
        e = 2 * (n - 1)
        faces += [(0, 1, o + 1, o), (e, o + e, o + e + 1, e + 1)]
        K._add('Body', top + bot, faces, {'bottom': 'jade', 'rest': 'teal_light'})
        ts = [0.0, 0.35, 0.7, 1.0]                                                            # its rib
        for t0, t1 in zip(ts, ts[1:]):
            limb('Body', p(t0) + Vector((0, 0.02, 0)), p(t1) + Vector((0, 0.02, 0)), 0.045 * (1 - 0.6 * t0),
                 0.045 * (1 - 0.6 * t1), 'jade', n=3)
    finish(note='a pale fern in a plum pot on a three-legged stand, eight lobed fronds arching out and down')


def d_armchair():
    """His ruling: a 1 x 1 wingback (2026-10-20). A crimson-dark frame and a crimson cushion and inner
    back, rolled arms, wings, a tall round-topped back tufted with five buttons, turned legs. The arms
    are as slim as real thickness allows, so the seat is 1.6 wide."""
    decor('Armchair', 1, 1, 'Floor')
    for x in (-0.86, 0.86):
        lathe('Body', [(0.1, 0), (0.13, 0.12), (0.08, 0.3), (0.12, 0.52)], 'wood_dark', n=8, base=(x, 0, -0.8))
        span('Body', (x - 0.1, 0, 0.72), (x + 0.1, 0.52, 0.92), 'wood_dark', bevel=0.03)
    span('Body', (-1.08, 0.5, -1.0), (1.08, 1.32, 1.0), 'crimson_dark', bevel=0.1)              # seat base
    span('Body', (-0.8, 1.3, -0.98), (0.8, 1.72, 0.55), 'crimson', bevel=0.12)                 # cushion
    back = ([(-1.05, 1.3), (1.05, 1.3)] + K.round_arch_points(-1.05, 1.05, 4.2, 5.0, n=8)[::-1])
    prism('Body', back, 0.55, 1.05, 'crimson_dark', plane='xy')                                  # the tall back
    inner = [(-0.78, 1.72), (0.78, 1.72)] + K.round_arch_points(-0.78, 0.78, 4.15, 4.75, n=8)[::-1]
    prism('Body', inner, 0.5, 0.56, 'crimson', plane='xy')                                       # its inner face
    for x, y in ((-0.38, 3.95), (0.38, 3.95), (0, 3.4), (-0.38, 2.85), (0.38, 2.85)):
        sphere('Body', (x, y, 0.49), (0.06, 0.06, 0.03), 'crimson_dark', n=6, rings=3)
    for sx in (-1, 1):
        wing = [(0.55, 1.9), (1.0, 2.2), (1.0, 4.3), (0.55, 4.6), (0.0, 4.4), (-0.3, 3.4), (-0.35, 2.4)]
        prism('Body', wing, sx * 1.06, sx * 0.82, 'crimson_dark', plane='zy')                   # wings
        span('Body', (min(sx * 1.08, sx * 0.8), 1.3, -0.96), (max(sx * 1.08, sx * 0.8), 2.25, 0.6),
             'crimson_dark', bevel=0.08)                                                          # arms
        cyl('Body', (0, 0, 0), 0.17, 1.62, 'crimson_dark', n=10, m=at((sx * 0.92, 2.25, -1.02), rx=90))
        cyl('Body', (0, 0, 0), 0.12, 0.04, 'crimson', n=10, m=at((sx * 0.92, 2.25, -1.02), rx=-90))
    K.seat(-0.8, 0.8, -0.98, 0.5, 1.72, narrow='his ruling 2026-10-20: the Armchair stays 1 x 1')
    finish(note='his ruling: a 1 x 1 crimson wingback, rolled arms, a tufted round-topped back; seat 1.6 wide')


def d_velvet_sofa():
    """A camelback sofa for two: a plum frame, two violet velvet cushions and inner back, rolled arms,
    a row of tufting buttons, turned legs."""
    decor('VelvetSofa', 2, 1, 'Floor')
    for x in (-2.3, 0.0, 2.3):
        for z in (-0.78, 0.78):
            if x == 0.0 and z < 0:
                continue
            lathe('Body', [(0.11, 0), (0.15, 0.1), (0.09, 0.28), (0.13, 0.47)], 'wood_dark', n=8, base=(x, 0, z))
    span('Body', (-2.55, 0.45, -1.0), (2.55, 1.3, 0.95), 'plum', bevel=0.12)
    for k in range(2):
        x0 = -2.08 + k * 2.08
        span('Body', (x0, 1.3, -0.98), (x0 + 2.08, 1.68, 0.48), 'violet', bevel=0.12)
    camel = [(-2.55, 1.3), (2.55, 1.3), (2.55, 3.0), (1.6, 3.3), (0.7, 3.8), (0.0, 3.9), (-0.7, 3.8),
             (-1.6, 3.3), (-2.55, 3.0)]
    prism('Body', camel, 0.5, 1.05, 'plum', plane='xy')
    face = [(-2.08, 1.68), (2.08, 1.68), (2.08, 2.95), (1.55, 3.18), (0.68, 3.62), (0.0, 3.72), (-0.68, 3.62),
            (-1.55, 3.18), (-2.08, 2.95)]
    prism('Body', face, 0.46, 0.52, 'violet', plane='xy')
    for x, y in ((-1.4, 2.75), (-0.7, 3.05), (0.0, 3.15), (0.7, 3.05), (1.4, 2.75), (-1.05, 2.3), (0.0, 2.4),
                 (1.05, 2.3)):
        sphere('Body', (x, y, 0.44), (0.06, 0.06, 0.03), 'plum_dark', n=6, rings=3)
    for sx in (-1, 1):
        span('Body', (min(sx * 2.6, sx * 2.08), 1.3, -1.0), (max(sx * 2.6, sx * 2.08), 1.98, 0.95), 'plum',
             bevel=0.1)
        cyl('Body', (0, 0, 0), 0.26, 2.0, 'plum', n=10, m=at((sx * 2.33, 1.98, -1.04), rx=90))
        cyl('Body', (0, 0, 0), 0.19, 0.04, 'violet', n=10, m=at((sx * 2.33, 1.98, -1.04), rx=-90))
    for x0 in (-2.08, 0.0):                                                                       # a seat a cushion
        K.seat(x0, x0 + 2.08, -0.98, 0.46, 1.68)
    finish(note='a camelback velvet sofa for two: plum frame, violet cushions, tufted back')


def d_bookshelf():
    """A tall gothic bookcase against the wall: two bays under pointed arches, a plum back, four shelves
    of books in the set's colours, a skull bookend and a potion bottle, a cornice."""
    decor('Bookshelf', 2, 1, 'Wall')
    zb, zf = 1.1, -0.3
    span('Body', (-2.55, 0, zf - 0.08), (2.55, 0.4, zb), 'wood_dark', bevel=0.04)             # plinth
    span('Body', (-2.3, 0.4, zb - 0.12), (2.3, 6.45, zb), 'plum_deep')                         # back
    for x in (-2.5, 2.25):
        span('Body', (x, 0.4, zf), (x + 0.25, 6.45, zb), 'wood_dark', bevel=0.03)              # sides
    span('Body', (-0.1, 0.54, zf + 0.02), (0.1, 6.3, zb - 0.12), 'wood_dark')                 # centre post
    shelves = (0.4, 1.95, 3.5, 5.0)
    for y in shelves + (6.3,):
        span('Body', (-2.25, y, zf), (2.25, y + 0.14, zb - 0.12), 'wood_dark')
    for x0, x1 in ((-2.25, -0.1), (0.1, 2.25)):                                                  # pointed arches
        arch = arch_points(x0, x1, 5.82, 6.3, n=4)
        prism('Body', [(x0, 6.3)] + arch[:5], zf - 0.04, zf + 0.1, 'wood_dark', plane='xy')
        prism('Body', arch[4:] + [(x1, 6.3)], zf - 0.04, zf + 0.1, 'wood_dark', plane='xy')
    span('Body', (-2.6, 6.44, zf - 0.15), (2.6, 6.78, zb), 'wood', bevel=0.05)                # cornice
    lathe('Body', [(0.12, 6.78), (0.15, 6.84), (0.07, 6.9), (0, 6.98)], 'gold', n=8, base=(0, 0, zf + 0.1))
    cols = ('book_a', 'book_b', 'book_c', 'wine', 'teal_dark', 'plum', 'book_b', 'moss', 'book_a', 'ink')
    zb0, zb1 = zf + 0.16, zb - 0.2

    def row(x0, x1, y, k0, lean_at=None, hmax=1.28):
        x, k = x0 + 0.04, k0
        while x < x1 - 0.2:
            bw = 0.2 + 0.07 * ((k * 5) % 3)
            bh = min(hmax, 0.92 + 0.12 * ((k * 7) % 4))
            col = cols[k % len(cols)]
            if lean_at is not None and k == lean_at:
                box('Body', (0, bh / 2, 0), (bw - 0.03, bh, zb1 - zb0), col,
                    m=at((x + bw / 2 + 0.4, y, (zb0 + zb1) / 2), rz=18))
                x += bw + 0.6
            else:
                span('Body', (x, y, zb0), (min(x + bw - 0.03, x1 - 0.04), y + bh, zb1), col)
                x += bw
            k += 1
    y0, y1, y2, y3 = (s + 0.14 for s in shelves)
    row(-2.25, -0.1, y0, 0)
    row(0.1, 2.25, y0, 3)
    row(-2.25, -0.1, y1, 6, lean_at=10)
    row(0.95, 2.25, y1, 2)
    sphere('Body', (0.5, y1 + 0.26, 0.35), (0.24, 0.24, 0.28), 'bone', n=8, rings=5)          # the skull
    span('Body', (0.36, y1, 0.1), (0.64, y1 + 0.12, 0.42), 'bone', bevel=0.03)
    for x in (0.41, 0.59):
        sphere('Body', (x, y1 + 0.3, 0.07), (0.07, 0.07, 0.04), 'black', n=6, rings=3)
    row(-2.25, -1.05, y2, 4)
    for i, (h, col) in enumerate(((0.16, 'wine'), (0.13, 'book_b'), (0.15, 'book_c'))):         # a stack
        yb = y2 + sum((0.16, 0.13, 0.15)[:i])
        span('Body', (-0.95 + 0.04 * i, yb, zb0 + 0.05), (-0.25 - 0.03 * i, yb + h, zb1 - 0.05), col)
    lathe('Body', [(0.16, y2 + 0.44), (0.2, y2 + 0.55), (0.18, y2 + 0.72), (0.07, y2 + 0.82), (0.06, y2 + 0.98),
                   (0.08, y2 + 1.02), (0, y2 + 1.04)], 'teal', n=8, base=(-0.6, -0.0, 0.35))
    row(0.1, 2.25, y2, 8)
    row(-2.25, -0.1, y3, 1, hmax=1.04)
    row(0.1, 2.25, y3, 5, lean_at=9, hmax=1.04)
    finish(note='a gothic bookcase: two bays under pointed arches, a plum back, books, a skull and a potion')


def d_side_table():
    """A round pedestal table on three curved feet, a brass lantern with a lit candle (Glow_Warm_1), a book."""
    decor('SideTable', 1, 1, 'Floor')
    for k in range(3):
        a = k * math.tau / 3 + 0.3
        d = Vector((math.cos(a), 0, math.sin(a)))
        pts = [d * 0.12 + Vector((0, 0.55, 0)), d * 0.45 + Vector((0, 0.3, 0)), d * 0.78 + Vector((0, 0.07, 0))]
        limb('Body', pts[0], pts[1], 0.11, 0.09, 'wood_dark', n=6)
        limb('Body', pts[1], pts[2], 0.09, 0.07, 'wood_dark', n=6)
        sphere('Body', tuple(d * 0.82 + Vector((0, 0.07, 0))), (0.09, 0.07, 0.09), 'wood_dark', n=6, rings=3)
    lathe('Body', [(0.22, 0.35), (0.24, 0.5), (0.13, 0.75), (0.2, 1.25), (0.11, 1.75), (0.14, 2.2), (0.26, 2.36),
                   (0, 2.36)], 'wood_dark', n=10)
    lathe('Body', [(0.9, 2.35), (0.98, 2.41), (0.98, 2.5), (0.93, 2.55), (0, 2.55)], 'wood', n=18)
    lx, lz = 0.25, -0.12
    cyl('Body', (lx, 2.55, lz), 0.34, 0.06, 'gold', n=12)                                     # the dish
    lathe('Body', [(0.12, 2.61), (0.06, 2.7), (0.05, 2.85), (0.09, 2.9), (0.08, 2.94)], 'gold', n=8,
          base=(lx, 0, lz))
    cyl('Body', (lx, 2.94, lz), 0.075, 0.42, 'cream', n=8)                                   # the candle
    sphere('Body', (lx + 0.07, 3.28, lz - 0.03), (0.035, 0.08, 0.035), 'cream', n=6, rings=3)
    sphere('Glow_Warm_1', (lx, 3.48, lz), (0.065, 0.13, 0.065), 'flame', n=6, rings=4)
    lathe('Body', [(0.27, 2.6), (0.31, 2.63), (0.27, 2.66)], 'gold', n=10, closed=True, base=(lx, 0, lz))
    lathe('Body', [(0.19, 3.72), (0.23, 3.75), (0.19, 3.78)], 'gold', n=10, closed=True, base=(lx, 0, lz))
    for k in range(4):
        a = k * math.tau / 4 + math.pi / 4
        d = Vector((math.cos(a), 0, math.sin(a)))
        c = Vector((lx, 0, lz))
        limb('Body', c + d * 0.29 + Vector((0, 2.63, 0)), c + d * 0.33 + Vector((0, 3.2, 0)), 0.025, 0.025, 'gold', n=4)
        limb('Body', c + d * 0.33 + Vector((0, 3.2, 0)), c + d * 0.21 + Vector((0, 3.75, 0)), 0.025, 0.025, 'gold', n=4)
    lathe('Body', [(0.21, 3.76), (0.1, 3.88), (0.05, 3.92), (0.07, 3.96), (0, 4.0)], 'gold', n=8, base=(lx, 0, lz))
    span('Body', (-0.66, 2.55, -0.3), (-0.1, 2.58, 0.36), 'wine')                              # a book
    span('Body', (-0.66, 2.67, -0.3), (-0.1, 2.7, 0.36), 'wine')
    span('Body', (-0.66, 2.58, -0.3), (-0.62, 2.67, 0.36), 'wine')
    span('Body', (-0.62, 2.58, -0.28), (-0.12, 2.67, 0.34), 'bone')
    finish(note='a round pedestal table on curved feet, a brass lantern with a lit candle, a book')


GRAND = [(1.85, -0.7), (1.85, 2.25), (1.7, 2.5), (1.35, 2.58), (0.85, 2.5), (0.35, 2.1), (-0.15, 1.5),
         (-0.75, 0.9), (-1.4, 0.4), (-1.75, 0.0), (-1.85, -0.35), (-1.85, -0.7)]     # the case, from above


def _inset(pts, t):
    """A closed polygon moved `t` inward (counter-clockwise or not)."""
    n = len(pts)
    area = sum(pts[i][0] * pts[(i + 1) % n][1] - pts[(i + 1) % n][0] * pts[i][1] for i in range(n))
    sgn = 1 if area > 0 else -1
    out = []
    for i in range(n):
        (ax, az), (bx, bz), (cx, cz) = pts[i - 1], pts[i], pts[(i + 1) % n]
        n1 = Vector((-(bz - az), bx - ax)).normalized() * sgn
        n2 = Vector((-(cz - bz), cx - bx)).normalized() * sgn
        nm = (n1 + n2).normalized()
        k = t / max(0.3, nm.dot(n1))
        out.append((bx + nm.x * k, bz + nm.y * k))
    return out


def d_grand_piano():
    """His pick A: a baby grand, the keyboard toward -Z, the straight spine on the player's left (+X),
    the curved bentside on the right, its lid propped open on a stick over a gold plate, three turned legs
    with brass castors, the pedal lyre, a music desk with a sheet, and its bench (a seat for one)."""
    decor('GrandPiano', 2, 2, 'Floor')
    inner = _inset(GRAND, 0.13)
    prism('Body', GRAND, 1.8, 2.5, 'black', plane='xz')                                           # lower case
    prism('Body', inner, 2.5, 2.55, 'wood_light', plane='xz')                                     # soundboard
    plate = [((x - 0.2) * 0.84 + 0.2, (z - 0.9) * 0.84 + 0.75) for x, z in inner]
    prism('Body', plate, 2.55, 2.62, 'gold', plane='xz')                                          # the plate
    k = len(GRAND) // 2                                                                           # the rim, in two
    prism('Body', GRAND[:k + 1] + inner[:k + 1][::-1], 2.5, 2.9, 'black', plane='xz')
    prism('Body', GRAND[k:] + GRAND[:1] + inner[:1] + inner[k:][::-1], 2.5, 2.9, 'black', plane='xz')
    lid = [(x - 1.85, z) for x, z in GRAND]
    prism('Body', lid, 0.0, 0.08, 'black', plane='xz', m=at((1.85, 2.9, 0), rz=-36))            # the lid
    tip = at((1.85, 2.9, 0), rz=-36) @ Vector((-2.75, 0.0, 0.3))
    limb('Body', (-1.4, 2.9, 0.3), (tip.x + 0.04, tip.y - 0.1, 0.3), 0.04, 0.035, 'black', n=4)       # its stick
    span('Body', (-1.85, 1.8, -1.4), (1.85, 2.4, -0.7), 'black')                                  # key bed
    for x0 in (-1.85, 1.66):
        span('Body', (x0 - 0.03 if x0 < 0 else x0, 1.75, -1.42), (x0 + 0.19 if x0 < 0 else 1.88, 2.64, -0.69), 'black')              # cheeks
    span('Body', (-1.64, 2.4, -1.38), (1.64, 2.48, -0.78), 'white')                               # the keys
    oct_w = 3.28 / 5
    for o in range(5):
        for f in (0.12, 0.27, 0.53, 0.67, 0.81):
            x = -1.64 + oct_w * (o + f)
            span('Body', (x - 0.035, 2.48, -1.05), (x + 0.035, 2.56, -0.78), 'black')
    span('Body', (-1.66, 2.48, -0.78), (1.66, 2.82, -0.7), 'black')                               # nameboard
    span('Body', (-1.72, 2.5, -0.7), (1.72, 2.88, -0.45), 'black')                                # over the action
    box('Body', (0, 0.25, 0), (2.0, 0.5, 0.06), 'black', m=at((0, 2.9, -0.55), rx=14))          # music desk,
    box('Body', (0.1, 0.27, -0.04), (0.8, 0.38, 0.02), 'bone', m=at((0, 2.9, -0.55), rx=14))    # under the lid
    for x, z in ((-1.6, -1.05), (1.6, -1.05), (1.25, 2.05)):
        lathe('Body', [(0.15, 0.1), (0.2, 0.25), (0.13, 0.45), (0.11, 1.2), (0.18, 1.6), (0.24, 1.82)],
              'black', n=8, base=(x, 0, z))
        cyl('Body', (x, 0, z), 0.12, 0.12, 'gold', n=8)
    span('Body', (-0.32, 0.34, -0.02), (-0.24, 1.82, 0.06), 'black')                              # pedal lyre
    span('Body', (0.24, 0.34, -0.02), (0.32, 1.82, 0.06), 'black')
    span('Body', (-0.38, 0.22, -0.08), (0.38, 0.36, 0.1), 'black')
    for x in (-0.18, 0.0, 0.18):
        span('Body', (x - 0.04, 0.26, -0.32), (x + 0.04, 0.3, -0.07), 'gold')
    for x in (-0.85, 0.85):                                                                       # the bench
        for z in (-2.4, -1.55):
            lathe('Body', [(0.08, 0), (0.1, 0.1), (0.06, 0.6), (0.1, 1.42)], 'black', n=6, base=(x, 0, z))
    span('Body', (-1.06, 1.4, -2.6), (1.06, 1.55, -1.36), 'black', bevel=0.04)
    span('Body', (-1.0, 1.55, -2.58), (1.0, 1.75, -1.38), 'crimson', bevel=0.08)
    K.seat(-1.0, 1.0, -2.58, -1.38, 1.75)
    finish(note='his pick A: a black baby grand, its lid propped over a gold plate, three legs, a bench')


def room_plaque():
    """The wooden plaque over a room's door (MODELS.md, "Room plaque"): the room's name and tier
    on its Face, written by the code, instead of floating text (his ask, 2026-10-19). Origin at the
    room's Sign attachment, 0.3 in front of the wall; the back lies on the wall, front toward -Z."""
    p = begin('RoomPlaque', 'Cosmetic', (1, 0.2, 0.2), root_centre=(0, 0, 0.15))
    p.allowed = ((-2.1, -0.8, -0.1), (2.1, 0.8, 0.31))
    span('Board', (-2.0, -0.65, 0.0), (2.0, 0.65, 0.3), 'wood_dark', bevel=0.06)
    span('Board', (-1.85, -0.5, -0.03), (1.85, 0.5, 0.0), 'gold', bevel=0.02)
    span('Face', (-1.75, -0.42, -0.06), (1.75, 0.42, -0.03), 'wood')
    for x in (-1.92, 1.92):
        sphere('Board', (x, 0, -0.02), (0.05, 0.05, 0.03), 'gold', n=6, rings=3)
    for part in list(K.P.parts):
        declare(part, False)
    finish(proxy=False, note='a dark wooden plaque with a gold rim; the code writes on its Face')

DECOR_BUILD = {
    'PuddleRug': d_puddle_rug, 'SnackBasket': d_snack_basket, 'RecordPlayer': d_record_player, 'Candles': d_candles,
    'Planter': d_planter, 'AntiqueWardrobe': d_antique_wardrobe, 'BlackoutCurtains': d_blackout_curtains,
    'SandTray': d_sand_tray, 'CatBasket': d_cat_basket, 'Cauldron': d_cauldron, 'SteakPlatter': d_steak_platter,
    'MoonWindow': d_moon_window, 'PipeOrgan': d_pipe_organ, 'SoundproofWalls': d_soundproof_walls,
    'Chandelier': d_chandelier, 'Bench': d_bench, 'UrnPlanter': d_urn_planter, 'RugRunner': d_rug_runner,
    'RugCorner': d_rug_corner, 'RugSquare': d_rug_square,
    'GrandfatherClock': d_grandfather_clock, 'WallClock': d_wall_clock, 'BlackRoses': d_black_roses,
    'CarnivorousPlant': d_carnivorous_plant, 'GhostFern': d_ghost_fern, 'Armchair': d_armchair,
    'VelvetSofa': d_velvet_sofa, 'Bookshelf': d_bookshelf, 'SideTable': d_side_table, 'GrandPiano': d_grand_piano,
}
ROOM_BUILD = {'StandardRoom': standard_room, 'GardenRoom': garden_room, 'AtticRoom': attic_room,
              'SarcophagusSuite': sarcophagus_suite, 'PotionLoft': potion_loft, 'DenRoom': den_room,
              'CoffinSuite': coffin_suite, 'OperaSuite': opera_suite}
AMENITY_BUILD = {'SnackBar': snack_bar, 'MusicRoom': music_room, 'GraveyardGarden': graveyard_garden,
                 'QuietLibrary': quiet_library, 'OrganHall': organ_hall}


def main():
    K.start_set(SET)
    order = ([('StandardRoom', standard_room), ('Lobby', lobby), ('FrontDesk', front_desk),
              ('StairCore', lambda: stairs(False)),
              ('StairCoreTop', lambda: stairs(True)), ('HotelSign', hotel_sign), ('RoomPlaque', room_plaque)]
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
    rows = [(['Lobby', 'FrontDesk', 'HotelSign'], 8, 1.0),
            ([n for n, _, _ in ROOMS], 5, 1.0),
            (list(AMENITY_BUILD) + ['StairCore', 'StairCoreTop'], 5, 1.0),
            ([f'Decor_{n}' for n in DECOR] + ['RoomPlaque'], 2.5, 2.0)]
    K.end_set('Haunted Manor hotel kit (Location 1), first draft', rows)
    if refused:
        raise SystemExit(f'REFUSED: {refused}')


main()
