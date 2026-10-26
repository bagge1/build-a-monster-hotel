"""More furniture and decor by purpose for Haunted Manor's built rooms (night draft 2026-10-21).

His ask (2026-10-21, night): "flesh out with more decorations and furniture for different purposes (i.e. snack
bars, breakfast buffet tables, pool tables etc.)". Pieces.luau's rows under "More furniture and decor by
purpose": dining, games, a lounge, a bathroom (an en-suite inside a bedroom's walls), a garden, the lobby, and
the Manor's spooky touches. Furniture (what a guest is walked to and uses: it has a `Use`) is Furniture_<Id>;
decor (what is looked at or sets the mood) is Decor_<Id>. Both keep MODELS.md's "Decor" rules; furniture adds
"Furniture"'s (footprint, `Use` and its `Pose`, a seat by rule 6, nothing floating).

Not a script of its own: tools/build_built_rooms.py runs this file in its own namespace (exec), so every helper
there (furn, use, stand, done, grounded_check, the kit's shapes) is used as it is; the set is built by

    blender -b --python-exit-code 1 -P tools/build_built_rooms.py -- sets haunted_manor [-- only <names>]

A `Wall` piece hangs on the wall: a shell that touches the wall's plane (z = 3fd/2 - 0.4) is held as one that
stands on the floor (hung_check; MODELS.md, "Furniture", "Nothing floats").
"""
# Names below (K, Vector, Matrix, math, box, span, cyl, lathe, sphere, prism, at, arch_points,
# round_arch_points, furn, use, stand, done, grounded_check, _body_bounds, PROXY_IF, FINDINGS, TOOLS, _HM) come
# from tools/build_built_rooms.py, which execs this file.

MORE_FURNITURE_IDS = ('DiningChair', 'SaladBar', 'CoffeeUrn', 'DessertTrolley', 'DartsBoard', 'ArcadeCabinet',
                      'PingPongTable', 'BoardGameShelf', 'ChessTable', 'CoffeeTable', 'Washstand', 'Toilet',
                      'GardenBench', 'CrystalBallTable', 'VendingMachine', 'BarTable', 'PopcornCart')
MORE_DECOR_IDS = ('PlantStand', 'HallStand', 'LuggageCart', 'Fireplace', 'TowelRack', 'Fountain', 'Candelabra')
MORE_NAMES = {f'Furniture_{i}' for i in MORE_FURNITURE_IDS} | {f'Decor_{i}' for i in MORE_DECOR_IDS}


def hung_check(piece, tris, stage):
    """Nothing floats, and a Wall piece may hang: the wall's plane behind it (z = 3fd/2 - 0.4, from the floor
    to the top) counts as a shell that stands on the floor."""
    if piece.layer != 'Wall':
        return grounded_check(piece, tris, stage)
    hx, back = 1.5 * piece.fw, 1.5 * piece.fd - 0.4
    a, b = Vector((-hx, 0.0, back)), Vector((hx, 0.0, back))
    c, d = Vector((hx, 7.0, back)), Vector((-hx, 7.0, back))
    return grounded_check(piece, {**tris, '_wall': [(a, b, c), (a, c, d)]}, stage)


def mfurn(id_):
    p = furn(id_)
    p.checks.remove(grounded_check)
    p.checks.append(hung_check)
    return p


def mdecor(id_):
    """Begin Decor_<id_> on its Pieces row's squares and layer (the kit refuses a height more than 0.3 off)."""
    e = K.pieces_decor()[id_]
    p = K.decor(id_, e['w'], e['d'], e['layer'])
    p.pose = p.lie = None
    p.checks.append(hung_check)
    return p


def ddone(note):
    """A decor piece: no LOD_Proxy (as the Manor's other decor), finish()."""
    return finish(proxy=False, note=note)


def gothic(x0, x1, y_spring, apex, n=3):
    """A rectangle x0..x1 from y 0 to y_spring with a pointed arch over it, as (x, y) points from (x0, 0)."""
    return ([(x0, 0.0), (x1, 0.0), (x1, y_spring)]
            + [(x, y) for x, y in reversed(arch_points(x0, x1, y_spring, apex, n=n))][1:-1] + [(x0, y_spring)])


def lifted(pts, dy):
    return [(x, y + dy) for x, y in pts]


def ellipse(cx, cy, rx, ry, n=16):
    return [(cx + rx * math.cos(2 * math.pi * k / n), cy + ry * math.sin(2 * math.pi * k / n)) for k in range(n)]


def candle(part, x, y, z, h=0.45, r=0.09, cup='gold'):
    """A candle in a cup on (x, y, z), its flame `part` (Glow_Warm_<n>)."""
    cyl('Body', (x, y, z), r + 0.07, 0.1, cup, n=8)
    cyl('Body', (x, y + 0.1, z), r, h, 'cream', n=8)
    sphere(part, (x, y + 0.1 + h + 0.12, z), (0.06, 0.14, 0.06), 'flame', n=6, rings=4)


# --- Dining -------------------------------------------------------------------------------------------

def f_dining_chair():
    mfurn('DiningChair')
    for x in (-0.82, 0.82):     # the front legs, and the back legs running up into the back's posts
        xa, xb = sorted((x, x + (0.2 if x > 0 else -0.2)))
        span('Body', (xa, 0, -1.02), (xb, 1.5, -0.82), 'wood_dark', bevel=0.03)
        span('Body', (xa, 0, 0.82), (xb, 4.3, 1.04), 'wood_dark', bevel=0.03)
        sphere('Body', (x + (0.1 if x > 0 else -0.1), 4.4, 0.93), 0.14, 'gold', n=6, rings=3)
    span('Body', (-1.06, 1.5, -1.06), (1.06, 1.7, 0.9), 'wood', bevel=0.04)
    span('Body', (-1.0, 1.7, -1.0), (1.0, 1.82, 0.7), 'crimson', bevel=0.04)
    prism('Body', lifted(gothic(-0.82, 0.82, 1.6, 2.4), 1.85), 0.86, 1.0, 'plum_dark', plane='xy')
    prism('Body', lifted(gothic(-0.5, 0.5, 1.2, 1.9), 2.2), 0.83, 0.86, 'crimson', plane='xy')
    K.seat(-1.0, 1.0, -1.0, 0.7, 1.82)
    use((0, 1.82, -0.15), (0, 0, -1), 'Sit')
    done('a dining chair: a crimson cushion at 1.82 on dark wood, a plum gothic-arched back with a crimson '
         'panel, gold finials')


def f_salad_bar():
    mfurn('SaladBar')
    for x in (-3.7, 3.7):
        for z in (-0.65, 0.65):
            lathe('Body', [(0.16, 0), (0.22, 0.16), (0.17, 0.32)], 'wood_dark', n=6, base=(x, 0, z))
    span('Body', (-4.0, 0.3, -0.92), (4.0, 2.6, 0.92), 'wood_dark', bevel=0.08)
    for k in range(3):          # three panels like the buffet's, the bar's rail in gold
        x0 = -3.8 + k * 2.55
        span('Body', (x0, 0.55, -0.97), (x0 + 2.45, 2.35, -0.9), 'moss', bevel=0.04)
    span('Body', (-4.1, 2.6, -1.05), (4.1, 2.78, 1.05), 'wood', bevel=0.05)
    span('Body', (-4.0, 2.78, 0.5), (4.0, 3.3, 1.0), 'wood_dark', bevel=0.04)     # the dressings' step
    for x, food in ((-3.0, 'leaf'), (-1.0, 'rose'), (1.0, 'pumpkin'), (3.0, 'slime')):
        lathe('Body', [(0.38, 2.78), (0.7, 3.1), (0.0, 3.1)], 'white', n=10, base=(x, 0, -0.3))
        sphere('Body', (x, 3.1, -0.3), (0.6, 0.16, 0.6), food, n=10, rings=4)
    for k, colr in enumerate(('amber', 'slime', 'crimson', 'amber', 'cream', 'slime', 'crimson')):
        x = -3.3 + k * 1.1
        lathe('Body', [(0.15, 3.3), (0.15, 3.68), (0.06, 3.8), (0.06, 3.92)], colr, n=6, base=(x, 0, 0.75))
    # The sneeze guard (blind review 2026-10-21: an opaque plum canopy at 3.9 hid the bowls from the raised
    # camera): one thin pane, `Glass` (the code may make it glass; MODELS.md, "Furniture"), level at 4.0 over
    # the bowls, on gold rails and six slim gold posts clear of the bowls.
    declare('Glass', False)
    for x in (-3.95, 0.0, 3.95):
        for z in (-0.88, 0.39):
            cyl('Body', (x, 2.78, z), 0.05, 1.16, 'gold', n=6)
    for z0, z1 in ((-0.92, -0.85), (0.36, 0.43)):
        span('Body', (-4.02, 3.94, z0), (4.02, 4.0, z1), 'gold')
    span('Glass', (-4.0, 4.0, -0.9), (4.0, 4.04, 0.4), 'moon')
    stand()
    done('a salad bar: four bowls of greens, beets, carrots and slime-green salad on a dark counter with moss '
         'panels, dressings on a step at the back, a thin glass sneeze guard on gold posts over the bowls')


def f_coffee_urn():
    mfurn('CoffeeUrn')
    span('Body', (-1.0, 0, -0.9), (1.0, 2.5, 0.9), 'wood_dark', bevel=0.06)
    span('Body', (-0.8, 0.3, -0.95), (0.8, 2.2, -0.88), 'wood', bevel=0.03)
    sphere('Body', (0.55, 1.25, -0.98), 0.07, 'gold', n=6, rings=3)
    span('Body', (-1.08, 2.5, -0.98), (1.08, 2.65, 1.0), 'wood', bevel=0.04)
    # A station, not a giant urn (blind review 2026-10-21: the 1.9-tall urn dwarfed its cabinet): the urn 1.3
    # tall on the left on little feet, its tap and black handle over a drip tray, cups and saucers on the right,
    # and a dark upstand at the back with a shelf of cups, so the piece keeps its height (Pieces' 4.6).
    ux, uz = -0.35, 0.05
    lathe('Body', [(0.3, 2.65), (0.33, 2.72), (0.22, 2.82), (0.4, 2.98), (0.44, 3.15), (0.44, 3.6),
                   (0.34, 3.78), (0.12, 3.85), (0.12, 3.92), (0.0, 3.97)], 'gold', n=10, base=(ux, 0, uz))
    lathe('Body', [(0.46, 3.3), (0.46, 3.44)], 'crimson', n=10, base=(ux, 0, uz))
    for s in (-1, 1):           # its handles, out of its sides and down
        xa, xb = sorted((ux + s * 0.38, ux + s * 0.62))
        span('Body', (xa, 3.42, uz - 0.04), (xb, 3.5, uz + 0.04), 'gold')
        span('Body', (ux + s * 0.56 - 0.04, 3.2, uz - 0.03), (ux + s * 0.56 + 0.04, 3.46, uz + 0.03), 'gold')
    span('Body', (ux - 0.06, 3.0, uz - 0.72), (ux + 0.06, 3.12, uz - 0.38), 'gold')   # the tap, from the front
    cyl('Body', (ux, 2.84, uz - 0.66), 0.05, 0.16, 'gold', n=6)
    span('Body', (ux - 0.05, 3.12, uz - 0.6), (ux + 0.05, 3.42, uz - 0.5), 'black')
    span('Body', (ux - 0.3, 2.65, uz - 0.88), (ux + 0.3, 2.7, uz - 0.44), 'iron')    # the drip tray
    cyl('Body', (ux, 2.7, uz - 0.66), 0.13, 0.14, 'white', n=8)                     # a cup under the tap
    for x, z, colr in ((0.55, -0.55, 'crimson'), (0.6, 0.0, 'white')):              # cups on saucers
        cyl('Body', (x, 2.65, z), 0.26, 0.03, 'white', n=10)
        cyl('Body', (x, 2.68, z), 0.17, 0.26, colr, n=8)
        span('Body', (x + 0.15, 2.76, z - 0.03), (x + 0.27, 2.88, z + 0.03), colr)
    span('Body', (-1.0, 2.65, 0.75), (1.0, 4.2, 1.0), 'wood_dark', bevel=0.04)     # the upstand
    span('Body', (-1.06, 4.2, 0.68), (1.06, 4.36, 1.06), 'plum_dark', bevel=0.03)
    span('Body', (-0.95, 3.75, 0.45), (0.95, 3.85, 0.76), 'wood')                    # its shelf of cups
    for k, x in enumerate((-0.6, -0.15, 0.3, 0.75)):
        cyl('Body', (x, 3.85, 0.6), 0.12, 0.2, ('crimson', 'white')[k % 2], n=8)
    stand()
    done('a coffee and cocoa station: a gold urn with a crimson band, handles and a tap over a drip tray on a '
         'dark cabinet, cups on saucers, a dark upstand with a shelf of cups')


def f_dessert_trolley():
    mfurn('DessertTrolley')
    for x in (-2.25, 2.25):
        for z in (-0.8, 0.64):
            cyl('Body', (0, 0, 0), 0.2, 0.16, 'black', n=10, m=at((x, 0.2, z), rx=90))
        for z in (-0.72, 0.72):
            cyl('Body', (x, 0.3, z), 0.07, 2.5 if x < 0 else 2.75, 'gold', n=6)
    for y in (0.9, 2.4):
        span('Body', (-2.45, y, -0.95), (2.45, y + 0.15, 0.95), 'wood', bevel=0.04)
        span('Body', (-2.4, y + 0.15, -0.9), (2.4, y + 0.17, 0.9), 'cream')
    span('Body', (-2.47, 0.36, -0.82), (2.47, 0.46, 0.82), 'gold')       # the axle frame under the wheels' tops
    cyl('Body', (0, 0, 0), 0.08, 1.6, 'gold', n=6, m=at((2.25, 3.05, -0.8), rx=90))  # the push bar
    # The top tier: a layered cake with a cherry, a green jelly, a stand of little cakes.
    lathe('Body', [(0.75, 2.57), (0.75, 2.95), (0.55, 2.95), (0.55, 3.28), (0.0, 3.28)], 'rose', n=12,
          base=(-1.2, 0, 0))
    lathe('Body', [(0.77, 2.85), (0.77, 2.93)], 'cream', n=12, base=(-1.2, 0, 0))
    sphere('Body', (-1.2, 3.38, 0), 0.12, 'crimson', n=6, rings=3)
    lathe('Body', [(0.5, 2.57), (0.35, 3.05), (0.0, 3.12)], 'slime', n=10, base=(0.55, 0, 0.3))
    lathe('Body', [(0.2, 2.57), (0.07, 2.65), (0.06, 2.95), (0.45, 2.98), (0.45, 3.02), (0.0, 3.02)], 'gold', n=10,
          base=(1.6, 0, -0.3))
    for k, colr in enumerate(('lilac', 'cream', 'rose')):
        a = 2 * math.pi * k / 3
        sphere('Body', (1.6 + 0.25 * math.cos(a), 3.1, -0.3 + 0.25 * math.sin(a)), (0.13, 0.09, 0.13), colr,
               n=6, rings=3)
    # The lower tier: a pie and a stack of plates.
    cyl('Body', (-1.0, 1.07, 0.1), 0.65, 0.2, 'pumpkin_dark', n=12)
    cyl('Body', (-1.0, 1.27, 0.1), 0.55, 0.06, 'amber', n=12)
    for k in range(4):
        cyl('Body', (1.2, 1.07 + 0.06 * k, 0.0), 0.5 - 0.01 * k, 0.05, 'white', n=10)
    stand()
    done('a two-tier dessert trolley on black wheels, gold posts and push bar: a pink layer cake with a cherry, '
         'a green jelly, a cake stand of little cakes; a pie and plates below')


# --- Games --------------------------------------------------------------------------------------------

def f_darts_board():
    mfurn('DartsBoard')
    back = 1.1
    prism('Body', lifted(gothic(-1.0, 1.0, 2.2, 2.7), 3.15), 0.85, back, 'wood_dark', plane='xy')
    for k, (r, colr) in enumerate(((0.85, 'black'), (0.7, 'cream'), (0.5, 'crimson'), (0.3, 'moss'),
                                   (0.1, 'crimson'))):
        z0 = 0.9 + 0.02 * k
        cyl('Body', (0, 0, 0), r, z0 - (0.7 - 0.02 * k), colr, n=20 if k < 2 else 12, m=at((0, 4.4, z0), rx=-90))
    for x, y in ((0.18, 4.55), (-0.25, 4.3), (0.05, 4.05)):
        cyl('Body', (0, 0, 0), 0.03, 0.45, 'gold', n=4, m=at((x, y, 0.64), rx=-90))
        box('Body', (x, y, 0.2), (0.22, 0.22, 0.12), 'crimson')
    span('Body', (-0.75, 2.2, 0.98), (0.75, 3.1, back), 'wood_dark', bevel=0.03)      # the chalk scoreboard
    span('Body', (-0.62, 2.32, 0.94), (0.62, 2.98, 1.0), 'night')
    for k in range(3):
        span('Body', (-0.5, 2.5 + 0.17 * k, 0.92), (-0.1 + 0.12 * k, 2.56 + 0.17 * k, 0.95), 'cream')
    stand()
    done('a darts board hung on the wall: rings of black, cream, crimson and green on a gothic-arched dark '
         'backboard, three darts in it, a chalk scoreboard under it')


def f_arcade_cabinet():
    mfurn('ArcadeCabinet')
    prof = [(-0.8, 0.0), (1.0, 0.0), (1.0, 5.5), (-0.7, 5.5), (-0.7, 4.6), (-0.35, 4.45), (-0.6, 3.2),
            (-1.05, 3.0), (-1.05, 2.75), (-0.8, 2.6)]
    prism('Body', prof, -1.05, 1.05, {'left': 'violet', 'right': 'violet', 'rest': 'plum_dark'}, plane='zy')
    # The screen on the slanted face (z -0.6, y 3.2 to z -0.35, y 4.45), a hair proud, glowing.
    d = Vector((0, 1.25, 0.25)).normalized()
    n = Vector((0, d.z, -d.y))
    c = Vector((0, 3.825, -0.475)) + n * 0.02
    ang = math.degrees(math.atan2(0.25, 1.25))
    box('Glow_Cold_1', (0, 0, 0), (1.5, 1.05, 0.03), 'moonglow', m=at(tuple(c), rx=ang))
    span('Glow_Warm_1', (-0.85, 4.75, -0.74), (0.85, 5.35, -0.71), 'lamp')         # the marquee
    span('Body', (-1.0, 5.5, -0.75), (1.0, 5.62, 1.0), 'gold', bevel=0.03)
    y = lambda z: 3.0 + (z + 1.05) * 0.2 / 0.45     # noqa: E731  the control panel's slope
    cyl('Body', (-0.5, y(-0.85) - 0.03, -0.85), 0.05, 0.32, 'black', n=6)
    sphere('Body', (-0.5, y(-0.85) + 0.33, -0.85), 0.11, 'crimson', n=6, rings=4)
    for x, colr in ((0.1, 'amber'), (0.38, 'sky'), (0.66, 'rose')):
        cyl('Body', (x, y(-0.8) - 0.03, -0.8), 0.09, 0.08, colr, n=8)
    span('Body', (-0.4, 1.2, -0.84), (0.4, 2.1, -0.78), 'iron', bevel=0.03)        # the coin door
    for x in (-0.15, 0.15):
        span('Body', (x - 0.05, 1.7, -0.86), (x + 0.05, 1.9, -0.83), 'amber')
    stand()
    play(((0.0, 0, -3.0), (0, 0, 1)))     # the one player at the controls (its Use too: the same point)
    done('an arcade cabinet: plum with violet sides, a glowing slanted screen and marquee, a joystick and three '
         'buttons, a coin door')


def f_ping_pong_table():
    mfurn('PingPongTable')
    for x in (-2.8, 2.8):
        for z in (-1.9, 1.9):
            span('Body', (x - 0.1, 0, z - 0.1), (x + 0.1, 2.2, z + 0.1), 'iron')
        span('Body', (x - 0.08, 0.5, -1.82), (x + 0.08, 0.66, 1.82), 'iron')
    span('Body', (-3.9, 2.2, -2.3), (3.9, 2.42, 2.3), 'iron')
    span('Body', (-4.0, 2.42, -2.4), (4.0, 2.6, 2.4), 'teal_dark', bevel=0.02)
    for (x0, z0, x1, z1) in ((-4.0, -2.4, 4.0, -2.3), (-4.0, 2.3, 4.0, 2.4), (-4.0, -2.3, -3.9, 2.3),
                             (3.9, -2.3, 4.0, 2.3), (-3.9, -0.04, 3.9, 0.04)):
        span('Body', (x0, 2.6, z0), (x1, 2.62, z1), 'white')
    span('Body', (-0.03, 2.59, -2.48), (0.03, 2.95, 2.48), 'grey')    # the net, its white top band, its posts
    span('Body', (-0.05, 2.95, -2.48), (0.05, 3.0, 2.48), 'white')
    for z in (-1, 1):
        za, zb = sorted((2.36 * z, 2.56 * z))
        span('Body', (-0.08, 2.3, za), (0.08, 3.05, zb), 'gold')
    for x, z, colr in ((-2.5, 1.0, 'crimson'), (2.6, -1.2, 'black')):
        cyl('Body', (x, 2.6, z), 0.38, 0.04, colr, n=10)
        span('Body', (x + 0.3, 2.6, z - 0.07), (x + 0.85, 2.68, z + 0.07), 'wood')
    sphere('Body', (1.0, 2.7, 0.5), 0.1, 'white', n=6, rings=4)
    stand()
    # One player an end, facing the net, on the middle of a square there (z 0 is a square's edge; ActivityKit.luau).
    play(((-6.0, 0, -1.5), (1, 0, 0)), ((6.0, 0, 1.5), (-1, 0, 0)))
    done('a ping-pong table: a dark teal top with white lines on iron legs, a grey net with a white band '
         'between gold posts, two bats and a ball')


def f_board_game_shelf():
    mfurn('BoardGameShelf')
    back = 1.1
    span('Body', (-2.3, 0, 0.95), (2.3, 5.3, back), 'wood_dark')
    for x in (-1, 1):
        xa, xb = sorted((2.3 * x, 2.5 * x))
        span('Body', (xa, 0, -0.9), (xb, 5.3, back), 'wood_dark', bevel=0.03)
    span('Body', (-2.58, 5.3, -1.0), (2.58, 5.55, back), 'plum_dark', bevel=0.05)
    span('Body', (-2.3, 0, -0.9), (2.3, 0.3, 0.95), 'wood_dark')
    shelves = (0.3, 1.6, 2.9, 4.2)
    for y in shelves[1:]:
        span('Body', (-2.3, y - 0.12, -0.85), (2.3, y, 0.95), 'wood')
    # Game boxes, not books (blind review 2026-10-21: thin flat stacks read as a bookcase): wide square boxes,
    # each with its lid a hair wider than the box and a band of another colour, so the lid's seam shows; in
    # each bay one of three ways (a flat stack, boxes stood on edge, one stood up showing its lid's picture),
    # with game pieces (pawns, dice) in front of a few.
    cols = ('crimson', 'teal', 'pumpkin', 'violet', 'moss', 'sky', 'rose', 'amber')
    lids = ('cream', 'gold', 'cream', 'lilac', 'bone', 'cream', 'white', 'night')
    k = [0]

    def game_box(lo, hi, axis):
        """A box from lo to hi; its lid the top 40 % along `axis` (1: lying flat, the lid up; 2: stood up, the
        lid's face toward -Z; 0: on edge, the lid toward -X), 0.02 wider all round, in another colour."""
        c, lid = cols[k[0] % len(cols)], lids[k[0] % len(lids)]
        k[0] += 1
        lo, hi = list(lo), list(hi)
        split = list(lo)
        cut = hi[axis] - 0.4 * (hi[axis] - lo[axis]) if axis == 1 else lo[axis] + 0.4 * (hi[axis] - lo[axis])
        if axis == 1:
            span('Body', lo, (hi[0], cut, hi[2]), c)
            span('Body', (lo[0] - 0.02, cut - 0.01, lo[2] - 0.02), (hi[0] + 0.02, hi[1], hi[2] + 0.02), lid)
        elif axis == 2:     # stood up, the lid toward -Z: the lid is the front 40 % (its foot 0.02 into the
            span('Body', (lo[0], lo[1], cut), hi, c)        # shelf, so its bottom never shares the box's plane)
            span('Body', (lo[0] - 0.02, lo[1] - 0.02, lo[2]), (hi[0] + 0.02, hi[1] + 0.02, cut + 0.01), lid)
        else:               # on edge, the lid toward -X
            span('Body', (cut, lo[1], lo[2]), hi, c)
            span('Body', (lo[0], lo[1] - 0.02, lo[2] - 0.02), (cut + 0.01, hi[1] + 0.02, hi[2] + 0.02), lid)
        return c

    def pawn(x, y, z, colr):
        lathe('Body', [(0.1, y), (0.1, y + 0.05), (0.035, y + 0.22), (0.0, y + 0.24)], colr, n=6, base=(x, 0, z))
        sphere('Body', (x, y + 0.3, z), 0.07, colr, n=6, rings=3)

    def die(x, y, z):
        span('Body', (x - 0.1, y, z - 0.1), (x + 0.1, y + 0.2, z + 0.1), 'white')
        for dx, dy in ((-0.05, 0.05), (0.05, 0.15)):
            span('Body', (x + dx - 0.02, y + dy - 0.02, z - 0.11), (x + dx + 0.02, y + dy + 0.02, z - 0.09),
                 'black')

    for si, y0 in enumerate(shelves):
        for bi, xc in enumerate((-1.5, 0.0, 1.5)):
            way = (si + bi) % 3
            if way == 0:        # a flat stack of two deep boxes, a title strip on each lid's front
                y = y0
                for j in range(2):
                    w, d, h = 1.3 - 0.12 * ((j + si) % 2), 1.3 - 0.12 * (j % 2), 0.4 - 0.04 * ((j + bi) % 2)
                    dx = 0.05 * (1 - 2 * (j % 2))
                    c = game_box((xc - w / 2 + dx, y, -d / 2 + 0.1), (xc + w / 2 + dx, y + h, d / 2 + 0.1), 1)
                    span('Body', (xc + dx - 0.3, y + h - 0.12, -d / 2 + 0.06), (xc + dx + 0.3, y + h - 0.05,
                                                                              -d / 2 + 0.1), c)
                    y += h
                if si % 2 == 0:     # pawns on the shelf in front of the stack
                    pawn(xc + 0.35, y0, -0.72, 'crimson')
                    pawn(xc - 0.2, y0, -0.7, 'sky')
            elif way == 1:      # two stood up, one behind the other, each lid's picture showing
                game_box((xc - 0.62, y0, 0.25), (xc + 0.38, y0 + 1.05, 0.5), 2)
                box('Body', (0, 0, 0), (0.22, 0.22, 0.05), 'gold', m=at((xc - 0.42, y0 + 0.85, 0.225), rz=45))
                face = game_box((xc - 0.3, y0, -0.45), (xc + 0.62, y0 + 0.85, -0.2), 2)
                cyl('Body', (0, 0, 0), 0.22, 0.04, 'night' if face != 'violet' else 'cream', n=6,
                    m=at((xc + 0.16, y0 + 0.38, -0.45), rx=-90))
                span('Body', (xc - 0.18, y0 + 0.66, -0.49), (xc + 0.5, y0 + 0.74, -0.45), 'gold')
            else:               # one stood up showing its lid, its picture a disc and a pawn, another behind it
                game_box((xc - 0.6, y0, 0.2), (xc + 0.55, y0 + 1.0, 0.45), 2)
                face = game_box((xc - 0.62, y0, -0.45), (xc + 0.62, y0 + 0.95, -0.2), 2)
                cyl('Body', (0, 0, 0), 0.26, 0.04, 'gold' if face != 'amber' else 'crimson', n=6,
                    m=at((xc - 0.18, y0 + 0.5, -0.45), rx=-90))
                box('Body', (0, 0, 0), (0.36, 0.36, 0.05), 'night', m=at((xc + 0.36, y0 + 0.5, -0.475), rz=45))
                if si % 2 == 0:
                    die(xc + 0.35, y0, -0.7)
    stand()
    done('a shelf of board games on the wall: dark wood, a plum cornice; on four shelves wide game boxes with '
         'lids of another colour, stacked flat with title strips and stood up showing the pictures on their lids, '
         'pawns and dice')


# --- Lounge -------------------------------------------------------------------------------------------

def f_chess_table():
    mfurn('ChessTable')
    lathe('Body', [(0.8, 0), (0.8, 0.1), (0.25, 0.3), (0.18, 2.2), (0.42, 2.45)], 'wood_dark', n=10)
    span('Body', (-1.05, 2.45, -1.05), (1.05, 2.62, 1.05), 'wood', bevel=0.04)
    span('Body', (-0.85, 2.62, -0.85), (0.85, 2.66, 0.85), 'bone')
    for i in range(8):
        for j in range(8):
            if (i + j) % 2:
                x0, z0 = -0.8 + 0.2 * i, -0.8 + 0.2 * j
                span('Body', (x0, 2.66, z0), (x0 + 0.2, 2.68, z0 + 0.2), 'wood_dark')
    for x, z, colr, tall in ((-0.5, -0.7, 'white', 0), (0.1, -0.5, 'white', 0), (0.3, -0.7, 'white', 1),
                             (-0.3, 0.5, 'black', 0), (0.5, 0.3, 'black', 0), (-0.1, 0.7, 'black', 1)):
        h = 0.45 if tall else 0.28
        lathe('Body', [(0.08, 2.67), (0.08, 2.71), (0.04, 2.71 + h * 0.5), (0.06, 2.71 + h * 0.75),
                       (0.0, 2.71 + h)], colr, n=8, base=(x, 0, z))
        sphere('Body', (x, 2.71 + h + 0.05, z), 0.07, colr, n=6, rings=3)
    stand()
    done('a chess table: a cream and dark-wood board on a turned pedestal, a game under way')


def f_coffee_table():
    mfurn('CoffeeTable')
    for x in (-2.15, 2.15):
        for z in (-0.72, 0.72):
            lathe('Body', [(0.14, 0), (0.1, 0.3), (0.15, 0.8), (0.11, 1.12)], 'wood_dark', n=6, base=(x, 0, z))
    span('Body', (-2.3, 1.1, -0.85), (2.3, 1.32, 0.85), 'wood_dark', bevel=0.03)
    span('Body', (-2.5, 1.3, -1.0), (2.5, 1.48, 1.0), 'wood', bevel=0.05)
    sphere('Body', (0.6, 1.76, 0.1), (0.36, 0.3, 0.36), 'white', n=10, rings=5)
    sphere('Body', (0.6, 2.04, 0.1), (0.14, 0.06, 0.14), 'gold', n=6, rings=3)
    cyl('Body', (0, 0, 0), 0.06, 0.45, 'white', n=6, m=at((0.25, 1.7, 0.1), rz=55))
    box('Body', (0.98, 1.78, 0.1), (0.1, 0.32, 0.08), 'white')
    for x, z in ((-0.4, -0.45), (1.5, -0.5)):
        cyl('Body', (x, 1.48, z), 0.25, 0.03, 'white', n=8)
        cyl('Body', (x, 1.51, z), 0.15, 0.18, 'violet', n=8)
    cyl('Body', (-1.4, 1.48, 0.3), 0.45, 0.03, 'white', n=10)
    for k, (x, z) in enumerate(((-1.55, 0.2), (-1.25, 0.4), (-1.45, 0.5), (-1.3, 0.12))):
        cyl('Body', (x, 1.51 + 0.04 * (k // 2), z), 0.13, 0.05, 'straw', n=8)
    span('Body', (-0.8, 1.48, 0.45), (0.1, 1.6, 0.9), 'book_b', bevel=0.02)
    stand()
    done('a low coffee table on turned legs: a white teapot with a gold knob, two violet cups, a plate of '
         'biscuits, a book')


# --- Bathroom -----------------------------------------------------------------------------------------

def f_washstand():
    mfurn('Washstand')
    span('Body', (-1.0, 0, -0.85), (1.0, 2.7, 0.9), 'wood_dark', bevel=0.06)
    for x0, x1 in ((-0.85, -0.03), (0.03, 0.85)):
        span('Body', (x0, 0.3, -0.9), (x1, 2.4, -0.83), 'wood', bevel=0.03)
    for x in (-0.15, 0.15):
        sphere('Body', (x, 1.4, -0.93), 0.06, 'gold', n=6, rings=3)
    span('Body', (-1.08, 2.7, -0.95), (1.08, 2.85, 1.0), 'bone', bevel=0.03)          # the marble top
    lathe('Body', [(0.5, 2.78), (0.72, 3.0), (0.78, 3.08), (0.68, 3.08), (0.0, 2.92)], 'white', n=12,
          base=(0, 0, -0.2))
    cyl('Body', (0, 2.85, 0.62), 0.06, 0.52, 'gold', n=6)
    span('Body', (-0.05, 3.3, 0.25), (0.05, 3.4, 0.68), 'gold')
    for x in (-0.25, 0.25):
        sphere('Body', (x, 2.92, 0.62), 0.08, 'gold', n=6, rings=3)
    prism('Body', lifted(gothic(-0.95, 0.95, 1.0, 2.45), 2.85), 0.75, 0.95, 'wood_dark', plane='xy')
    prism('Body', lifted(gothic(-0.78, 0.78, 0.95, 2.15), 3.0), 0.71, 0.77, 'moon', plane='xy')
    stand()
    done('a washstand: a white basin with a gold tap in a cream marble top on a dark cabinet, a gothic-arched '
         'mirror behind it')


def f_toilet():
    # One pedestal toilet (blind review 2026-10-21: a tapered bucket with a disc lid, and a cistern on a column
    # of its own behind it that never met the bowl): an oval bowl flaring from a pedestal on a foot, its back
    # running up into a deck the cistern stands on; a dark wood seat and a closed wood lid on the rim.
    mfurn('Toilet')
    zc, sz = -0.35, 0.75        # the bowl's centre and its oval (x 1, z 0.75)
    lathe('Body', [(0.62, 0.0), (0.62, 0.08), (0.5, 0.2), (0.44, 0.6), (0.7, 1.0), (0.93, 1.3), (0.97, 1.43),
                   (0.0, 1.46)], 'white', n=16, base=(0, 0, zc), scale=(1.0, sz))
    prism('Body', [(-0.25, 0.0), (0.3, 0.0), (0.95, 0.95), (0.95, 1.44), (-0.25, 1.44)], -0.42, 0.42, 'white',
          plane='zy')           # the bowl's back, rising to the deck under the cistern
    lathe('Body', [(0.62, 1.42), (1.0, 1.42), (1.0, 1.53), (0.62, 1.53)], 'wood_dark', n=16, base=(0, 0, zc),
          scale=(1.0, sz), closed=True)     # the seat
    lathe('Body', [(0.95, 1.53), (0.98, 1.58), (0.95, 1.67), (0.85, 1.71), (0.0, 1.72)], 'wood', n=16,
          base=(0, 0, zc), scale=(1.0, sz))  # the lid, closed
    span('Body', (-0.8, 1.42, 0.45), (0.8, 3.2, 1.05), 'wood_dark', bevel=0.05)     # the cistern on the deck
    span('Body', (-0.86, 3.2, 0.4), (0.86, 3.36, 1.1), 'white', bevel=0.03)
    span('Body', (-0.6, 1.8, 0.42), (0.6, 2.9, 0.47), 'wood', bevel=0.02)            # its panel
    span('Body', (0.45, 2.98, 0.37), (0.75, 3.06, 0.46), 'gold')                     # the lever
    sphere('Body', (0.75, 3.02, 0.36), 0.07, 'gold', n=6, rings=3)
    K.seat(-1.0, 1.0, -0.95, 0.25, 1.72)
    use((0, 1.72, -0.35), (0, 0, -1), 'Sit')
    done("a white pedestal toilet: an oval bowl with a dark wood seat and a closed wood lid at 1.72, a wood-clad "
         "cistern with a gold lever on the bowl's back, for an en-suite inside a room's walls")


# --- Garden -------------------------------------------------------------------------------------------

def f_garden_bench():
    mfurn('GardenBench')
    for sx in (-1, 1):
        xa, xb = sorted((2.35 * sx, 2.55 * sx))
        span('Body', (xa, 0, -0.98), (xb, 2.45, -0.78), 'iron', bevel=0.03)     # the front leg up to the arm
        span('Body', (xa, 0, 0.75), (xb, 3.4, 0.95), 'iron', bevel=0.03)        # the back leg up to the rail
        span('Body', (xa - 0.03, 2.4, -1.02), (xb + 0.03, 2.55, 0.85), 'iron', bevel=0.03)  # the arm
        sphere('Body', ((xa + xb) / 2, 3.48, 0.85), 0.13, 'iron', n=6, rings=3)
    span('Body', (-2.35, 1.4, -0.9), (2.35, 1.55, 0.7), 'iron')
    span('Body', (-2.5, 1.55, -1.0), (2.5, 1.75, 0.5), 'wood', bevel=0.03)
    # The back's slats and top rail on the posts' front (blind review 2026-10-21: they hung between the posts,
    # behind their front faces), 0.02 into them.
    for y in (2.0, 2.58):
        span('Body', (-2.5, y, 0.57), (2.5, y + 0.35, 0.77), 'wood', bevel=0.03)
    span('Body', (-2.5, 3.2, 0.55), (2.5, 3.36, 0.77), 'iron', bevel=0.03)
    K.seat(-2.4, 2.4, -0.95, 0.45, 1.75, people=2)
    # Use at the seat's middle (the sitting sheet, 2026-10-21: at x -1.1 the seated person's left arm, 1.9 out,
    # went through the arm and its post at x -2.35; at 0 both arms clear the arms' inner faces by 0.45).
    use((0, 1.75, -0.25), (0, 0, -1), 'Sit')
    done('a garden bench for two: a wooden seat and back on a black wrought-iron frame with arms and finials')


# --- The Manor's decor for those rooms ----------------------------------------------------------------

def d_plant_stand():
    mdecor('PlantStand')
    lathe('Body', [(0.6, 0), (0.6, 0.08), (0.2, 0.25), (0.1, 2.5), (0.45, 2.7), (0.45, 2.8)], 'iron', n=10)
    lathe('Body', [(0.38, 2.8), (0.55, 3.45), (0.6, 3.5), (0.0, 3.5)], 'pumpkin_dark', n=10)
    lathe('Body', [(0.62, 3.42), (0.62, 3.52)], 'gold', n=10)
    sphere('Body', (0, 3.95, 0), (0.35, 0.45, 0.35), 'leaf', n=8, rings=4)
    for k in range(7):
        phi = 2 * math.pi * k / 7
        dirn = Vector((math.sin(phi) * 0.866, 0.5, math.cos(phi) * 0.866))
        c = Vector((0, 3.72, 0)) + dirn * 0.55
        sphere('Body', (0, 0, 0), (0.24, 0.07, 0.6), 'moss' if k % 2 else 'leaf', n=8, rings=4,
               m=at(tuple(c), rx=-30, ry=math.degrees(phi)))
    ddone('a fern in a terracotta pot with a gold rim on a wrought-iron stand')


def d_hall_stand():
    mdecor('HallStand')
    span('Body', (-1.05, 0, -0.6), (1.05, 1.2, 0.9), 'wood_dark', bevel=0.05)        # the umbrella well
    span('Body', (-0.9, 0.2, -0.65), (0.9, 1.0, -0.58), 'wood', bevel=0.03)
    cyl('Body', (0, 0, 0), 0.07, 2.2, 'black', n=6, m=at((0.55, 1.0, -0.1), rx=-8, rz=-8))
    prism('Body', lifted(gothic(-0.95, 0.95, 4.5, 5.3), 1.2), 0.6, 0.95, 'wood_dark', plane='xy')
    prism('Body', ellipse(0, 3.7, 0.7, 1.0), 0.56, 0.62, 'gold', plane='xy')
    prism('Body', ellipse(0, 3.7, 0.6, 0.9), 0.52, 0.58, 'moon', plane='xy')
    for x in (-0.75, 0.75):
        cyl('Body', (0, 0, 0), 0.05, 0.36, 'gold', n=6, m=at((x, 5.0, 0.6), rx=-90))
        sphere('Body', (x, 5.0, 0.24), 0.08, 'gold', n=6, rings=3)
    # A crimson coat on the left hook, a top hat on the right.
    prism('Body', [(-1.05, 3.1), (-0.45, 3.1), (-0.6, 4.85), (-0.9, 4.85)], 0.15, 0.5, 'crimson', plane='xy')
    lathe('Body', [(0.0, 4.48), (0.34, 4.48), (0.34, 4.54), (0.24, 4.56), (0.24, 5.02), (0.0, 5.02)], 'black',
          n=10, base=(0.75, 0, 0.12))
    lathe('Body', [(0.26, 4.6), (0.26, 4.7)], 'crimson', n=10, base=(0.75, 0, 0.12))
    ddone('a Victorian hall stand: an umbrella well, a gothic-arched back with an oval mirror in gold, two gold '
          'hooks with a crimson coat and a top hat')


def d_luggage_cart():
    mdecor('LuggageCart')
    for x in (-2.2, 2.2):
        for z in (-0.9, 0.74):
            cyl('Body', (0, 0, 0), 0.22, 0.16, 'black', n=10, m=at((x, 0.22, z), rx=90))
    span('Body', (-2.55, 0.42, -1.05), (2.55, 0.62, 1.05), 'gold', bevel=0.03)
    span('Body', (-2.45, 0.62, -0.95), (2.45, 0.72, 0.95), 'crimson')
    for x in (-2.35, 2.35):
        for z in (-0.8, 0.8):
            cyl('Body', (x, 0.72, z), 0.08, 3.98, 'gold', n=6)
            sphere('Body', (x, 4.78, z), 0.14, 'gold', n=6, rings=3)
    for z in (-0.8, 0.8):
        cyl('Body', (0, 0, 0), 0.07, 4.7, 'gold', n=6, m=at((-2.35, 4.6, z), rz=-90))
    cyl('Body', (0, 0, 0), 0.06, 1.6, 'gold', n=6, m=at((0.0, 4.6, -0.8), rx=90))
    span('Body', (-2.2, 0.72, -0.8), (-0.2, 2.0, 0.8), 'wood', bevel=0.06)           # a trunk with gold bands
    for x in (-1.8, -0.6):
        span('Body', (x - 0.08, 0.7, -0.83), (x + 0.08, 2.03, 0.83), 'gold')
    cyl('Body', (-1.2, 2.0, 0.0), 0.55, 0.6, 'violet', n=12)                        # a hatbox on it
    cyl('Body', (-1.2, 2.6, 0.0), 0.58, 0.1, 'lilac', n=12)
    span('Body', (0.0, 0.72, -0.7), (2.1, 1.6, 0.6), 'teal', bevel=0.08)             # two suitcases
    span('Body', (0.3, 1.6, -0.5), (1.8, 2.3, 0.4), 'crimson', bevel=0.08)
    span('Body', (0.85, 2.3, -0.08), (1.25, 2.45, 0.02), 'gold')
    ddone("a bellhop's luggage cart in gold on a crimson deck: a banded trunk with a hatbox, two suitcases")


def d_fireplace():
    mdecor('Fireplace')
    back = 1.1
    # Blind review 2026-10-21: the mantel at 4.25 was a 5-stud person's head height, and the keystone hung
    # down into the arch's tip (a loose dark square in the opening). Now the arch 0.3 lower, the mantel's top
    # at 3.5 (the person's chest), the keystone standing on the arch's apex; above the mantel a gothic
    # overmantel mirror in a dark frame, so the piece keeps its height (Pieces' 5.6).
    span('Body', (-2.6, 0, -1.1), (2.6, 0.3, back), 'stone_dark', bevel=0.04)          # the hearth
    spring, apex = 1.8, 2.6
    opening = [(x, y + 0.3) for x, y in gothic(-1.3, 1.3, spring - 0.3, apex - 0.3)]
    surround = ([(-2.4, 0.3), (-1.3, 0.3)] + arch_points(-1.3, 1.3, spring, apex, n=3)
                + [(1.3, 0.3), (2.4, 0.3), (2.4, 3.25), (-2.4, 3.25)])
    prism('Body', surround, 0.4, back, 'stone', plane='xy')
    prism('Body', [(x * 0.985, y) for x, y in opening], 0.8, back - 0.02, 'black', plane='xy')
    prism('Body', [(-0.2, apex + 0.02), (0.2, apex + 0.02), (0.26, 3.12), (-0.26, 3.12)], 0.36, 0.44,
          'stone_dark', plane='xy')                                                    # the keystone
    span('Body', (-2.6, 3.25, 0.2), (2.6, 3.5, back), 'wood_dark', bevel=0.04)          # the mantel shelf
    span('Body', (-0.9, 0.3, 0.2), (0.9, 0.45, 0.75), 'iron')                           # the grate and logs
    cyl('Body', (0, 0, 0), 0.18, 1.5, 'wood', n=8, m=at((-0.75, 0.62, 0.45), rz=-90))
    cyl('Body', (0, 0, 0), 0.16, 1.3, 'wood_dark', n=8, m=at((-0.5, 0.62, 0.62), rz=-75))
    for k, (x, y, z, s) in enumerate(((-0.35, 1.05, 0.5, 1.0), (0.3, 1.0, 0.55, 0.85), (0.0, 1.2, 0.6, 1.2))):
        sphere('Glow_Warm_1', (x, y, z), (0.25 * s, 0.5 * s, 0.2 * s), 'flame', n=8, rings=5)
    m = 3.5                     # the mantel's top
    prism('Body', lifted(gothic(-1.15, 1.15, 1.25, 2.05), m), 0.88, back, 'wood_dark', plane='xy')
    prism('Body', lifted(gothic(-0.95, 0.95, 1.15, 1.85), m + 0.08), 0.84, 0.9, 'moon', plane='xy')
    for k, x in enumerate((-1.9, 1.9)):
        lathe('Body', [(0.22, m), (0.22, m + 0.06), (0.08, m + 0.2), (0.07, m + 0.7), (0.15, m + 0.75)], 'gold',
              n=8, base=(x, 0, 0.65))
        cyl('Body', (x, m + 0.75, 0.65), 0.08, 0.4, 'cream', n=8)
        sphere(f'Glow_Warm_{k + 2}', (x, m + 1.27, 0.65), (0.06, 0.14, 0.06), 'flame', n=6, rings=4)
    prism('Body', lifted(gothic(-0.45, 0.45, 0.6, 0.9), m), 0.45, 0.8, 'wood_dark', plane='xy')
    cyl('Body', (0, 0, 0), 0.28, 0.06, 'bone', n=12, m=at((0, m + 0.5, 0.47), rx=-90))
    ddone('a stone fireplace with a pointed-arch opening and a keystone on its apex, logs burning on an iron '
          'grate, a dark mantel at 3.5 with two gold candlesticks and a mantel clock, a gothic overmantel mirror')


def d_towel_rack():
    mdecor('TowelRack')
    back = 1.1
    for x in (-0.95, 0.95):
        span('Body', (x - 0.07, 1.5, 0.55), (x + 0.07, 4.2, back), 'gold', bevel=0.02)
        sphere('Body', (x, 4.28, 0.82), 0.09, 'gold', n=6, rings=3)
    for y in (2.6, 4.0):
        cyl('Body', (0, 0, 0), 0.06, 1.76, 'gold', n=6, m=at((-0.88, y, 0.7), rz=-90))
    # Each towel hangs over its rail in two layers 0.1 thick, the front longer, folded round the rail (blind
    # review 2026-10-21: a slab read from the side as a bar): its side, a U over the rail, shows its thickness.
    def drape(x0, x1, y, front, rear, colr, t=0.1, gap=0.08, n=5):
        z, r0, r1 = 0.7, gap, gap + t       # the rail's line; the fold's inner and outer radius
        outer = [(z - r1 * math.cos(math.pi * i / n), y + r1 * math.sin(math.pi * i / n)) for i in range(n + 1)]
        inner = [(z + r0 * math.cos(math.pi * i / n), y + r0 * math.sin(math.pi * i / n)) for i in range(n + 1)]
        prism('Body', [(z - r1, front)] + outer + [(z + r1, rear), (z + r0, rear)] + inner + [(z - r0, front)],
              x0, x1, colr, plane='zy')
    drape(-0.7, 0.7, 4.0, 2.85, 3.35, 'crimson')                                       # a bath towel, top rail
    span('Body', (-0.72, 3.25, 0.5), (0.72, 3.37, 0.54), 'gold')                       # its band, on the front
    drape(-0.45, 0.45, 2.6, 1.75, 2.1, 'cream', t=0.08, gap=0.08)                      # a hand towel below
    ddone('a gold towel rack hung on the wall: a crimson bath towel with a gold band and a cream hand towel, '
          'each folded over its rail')


def d_fountain():
    mdecor('Fountain')
    lathe('Body', [(1.9, 0.0), (2.2, 0.0), (2.2, 0.9), (1.9, 0.9)], 'stone', n=16, closed=True)
    cyl('Body', (0, 0, 0), 1.92, 0.2, 'stone_dark', n=16)
    cyl('Body', (0, 0.2, 0), 1.92, 0.5, 'sky', n=16)
    for x, z in ((1.2, 0.6), (-1.0, -1.0)):
        cyl('Body', (x, 0.7, z), 0.32, 0.03, 'leaf', n=8)
    lathe('Body', [(0.5, 0.7), (0.35, 1.1), (0.28, 1.85), (0.45, 2.05)], 'stone', n=10)
    lathe('Body', [(0.3, 2.0), (1.1, 2.4), (1.15, 2.6), (1.0, 2.6), (0.0, 2.45)], 'stone', n=12)
    cyl('Body', (0, 2.45, 0), 1.0, 0.07, 'sky', n=12)
    lathe('Body', [(0.2, 2.5), (0.15, 3.4), (0.5, 3.75), (0.52, 3.85), (0.0, 3.75)], 'stone', n=10)
    lathe('Body', [(0.15, 3.78), (0.25, 4.0), (0.2, 4.3), (0.0, 4.75)], 'stone_dark', n=8)
    for k in range(4):          # the four streams, each its own part Jet_<n> (the code may add a water effect;
        a = math.pi / 4 + k * math.pi / 2       # MODELS.md, "Decor"), not colliding
        cyl(f'Jet_{k + 1}', (1.12 * math.cos(a), 0.65, 1.12 * math.sin(a)), 0.06, 1.85, 'sky', n=5,
            collide=False)
    ddone('a two-tier stone fountain in a round basin: water in both bowls and four streams falling (Jet_1 to '
          'Jet_4), lily pads, a dark stone spire')


def d_candelabra():
    mdecor('Candelabra')
    lathe('Body', [(0.7, 0), (0.7, 0.1), (0.35, 0.3), (0.12, 0.6), (0.1, 4.0), (0.2, 4.1), (0.1, 4.2),
                   (0.08, 4.9)], 'iron', n=8)
    lathe('Body', [(0.16, 2.0), (0.16, 2.15)], 'gold', n=8)
    for ry, r, y in ((0, 0.06, 4.2), (90, 0.05, 4.23)):    # the two arms crossing, a hair apart in size
        cyl('Body', (0, 0, 0), r, 1.7, 'iron', n=6, m=at((0, y, 0), ry=ry) @ at((-0.85, 0, 0), rz=-90))
    k = 1
    for x, z in ((-0.85, 0), (0.85, 0), (0, -0.85), (0, 0.85)):
        cyl('Body', (x, 4.2, z), 0.06, 0.4, 'iron', n=6)
        candle(f'Glow_Warm_{k}', x, 4.6, z)
        k += 1
    candle(f'Glow_Warm_{k}', 0, 4.9, 0, h=0.5)
    ddone('a standing iron candelabra with a gold collar: five cream candles in gold cups, each flame its own glow')


# --- The Manor's own furniture ------------------------------------------------------------------------

def f_crystal_ball_table():
    mfurn('CrystalBallTable')
    lathe('Body', [(1.06, 0.0), (1.0, 0.05), (0.92, 2.35), (1.02, 2.45), (1.0, 2.6), (0.0, 2.6)], 'plum', n=12)
    lathe('Body', [(0.96, 2.28), (1.04, 2.28), (1.04, 2.4), (0.96, 2.4)], 'gold', n=12, closed=True)
    lathe('Body', [(0.35, 2.6), (0.35, 2.66), (0.2, 2.8), (0.28, 2.95)], 'gold', n=10)
    sphere('Glow_Cold_1', (0, 3.4, 0), 0.5, 'moonglow', n=12, rings=8)
    for k, x in enumerate((-0.65, 0.65)):
        cyl('Body', (x, 2.6, 0.45), 0.16, 0.06, 'gold', n=8)
        cyl('Body', (x, 2.66, 0.45), 0.08, 0.3 + 0.1 * k, 'cream', n=8)
        sphere(f'Glow_Warm_{k + 1}', (x, 2.66 + 0.3 + 0.1 * k + 0.12, 0.45), (0.05, 0.12, 0.05), 'flame', n=6,
               rings=4)
    for k, (x, z, ang) in enumerate(((-0.45, -0.55, 15), (0.0, -0.65, -5), (0.45, -0.5, -20))):
        box('Body', (0, 0, 0), (0.3, 0.02, 0.45), 'crimson' if k != 1 else 'bone',
            m=at((x, 2.61 + 0.02 * k, z), ry=ang))
    stand()
    done("a fortune-teller's table: a plum cloth with a gold band, a glowing crystal ball on a gold stand, two "
         "candles and three cards dealt")


def f_vending_machine():
    # His ask (2026-10-22: "buffet bord, vinylspelare, automat, barbord osv"): a snack machine a guest walks up to.
    mfurn('VendingMachine')
    span('Body', (-1.0, 0.12, -0.75), (1.0, 5.3, 1.0), 'plum_dark', bevel=0.06)
    for x in (-0.85, 0.85):
        for z in (-0.55, 0.85):
            cyl('Body', (x, 0, z), 0.12, 0.14, 'iron', n=6)
    span('Body', (-1.08, 5.3, -0.82), (1.08, 5.46, 1.08), 'gold', bevel=0.03)
    span('Body', (-0.95, 4.82, -0.9), (0.95, 5.26, -0.74), 'gold')                   # the name board, on the bay's plane
    span('Glow_Warm_1', (-0.88, 4.88, -0.94), (0.88, 5.2, -0.88), 'lamp')
    # The window bay standing a little out of the front: a lit back, four shelves of snacks, glass over them.
    span('Body', (-0.92, 1.75, -0.9), (0.3, 4.75, -0.74), 'gold')
    span('Glow_Cold_1', (-0.84, 1.85, -0.95), (0.22, 4.65, -0.88), 'moonglow')
    snacks = ('crimson', 'amber', 'slime', 'rose', 'sky', 'pumpkin')
    for k, y in enumerate((1.95, 2.65, 3.35, 4.05)):
        span('Body', (-0.84, y, -1.03), (0.22, y + 0.05, -0.94), 'iron')
        for j, x in enumerate((-0.7, -0.43, -0.16, 0.09)):
            colr = snacks[(k * 4 + j) % len(snacks)]
            span('Body', (x - 0.1, y + 0.05, -1.0), (x + 0.1, y + 0.48, -0.93), colr)
    declare('Glass', False)
    span('Glass', (-0.9, 1.77, -1.07), (0.28, 4.73, -1.04), 'moon')
    for x0, x1 in ((-0.95, -0.89), (0.27, 0.33)):                                      # the bay's gold sides
        span('Body', (x0, 1.72, -1.08), (x1, 4.78, -0.74), 'gold')
    # The column of buttons and the coin slot to the right of the window, the pick-up flap under it.
    span('Body', (0.42, 2.6, -0.81), (0.9, 4.5, -0.74), 'black')
    for r in range(3):
        for c in range(2):
            span('Body', (0.48 + c * 0.22, 3.1 + r * 0.42, -0.86), (0.66 + c * 0.22, 3.4 + r * 0.42, -0.8), 'amber')
    span('Body', (0.58, 2.72, -0.85), (0.76, 2.9, -0.8), 'gold')
    span('Body', (-0.8, 0.55, -0.83), (0.25, 1.35, -0.74), 'black')
    span('Body', (-0.7, 0.65, -0.87), (0.15, 0.8, -0.82), 'iron')
    stand()
    done('a snack vending machine: a plum cabinet with a gold top, a lit name board, a glass window bay with '
         'four shelves of colourful snacks on a pale lit back, a column of amber buttons and a coin slot, a '
         'pick-up flap at the bottom')


def f_bar_table():
    mfurn('BarTable')
    cyl('Body', (0, 0, 0), 0.9, 0.16, 'iron', n=12)
    # The top at a standing person's elbow (blind review 2026-10-22: at 3.3 it was chest-high).
    cyl('Body', (0, 0.16, 0), 0.16, 2.7, 'iron', n=8)
    cyl('Body', (0, 0.95, 0), 0.55, 0.08, 'gold', n=10)                               # a foot rest
    cyl('Body', (0, 2.78, 0), 1.1, 0.08, 'gold', n=14)
    cyl('Body', (0, 2.86, 0), 1.05, 0.14, 'wood_dark', n=14)
    candle('Glow_Warm_1', 0.0, 3.0, 0.0, cup='crimson')
    for x, z, colr in ((-0.6, -0.3, 'wine'), (0.55, 0.4, 'slime')):                   # two drinks, a straw each
        cyl('Body', (x, 3.0, z), 0.18, 0.4, colr, n=8)
        cyl('Body', (x + 0.06, 3.4, z), 0.03, 0.3, 'white', n=4)
    stand()
    done('a tall bar table to stand at: a round dark top with a gold edge on an iron column and base, a gold '
         'foot rest, a candle in a cup and two drinks')


def f_popcorn_cart():
    mfurn('PopcornCart')
    for x in (-0.88, 0.88):
        for z in (-0.6, 0.6):
            cyl('Body', (x, 0.18, z), 0.08, 0.5, 'gold', n=6)
            sphere('Body', (x, 0.14, z), 0.14, 'black', n=6, rings=4)
    span('Body', (-1.05, 0.66, -0.8), (1.05, 2.4, 0.8), 'crimson', bevel=0.06)
    for x0 in (-0.9, 0.1):
        span('Body', (x0, 0.9, -0.86), (x0 + 0.8, 2.15, -0.79), 'crimson_dark', bevel=0.03)
    span('Body', (-1.08, 2.4, -0.86), (1.08, 2.55, 0.86), 'gold', bevel=0.03)
    # The glass cabinet with a heap of popcorn and the kettle over it, under a crimson roof with a lamp.
    # Popcorn heaped high and yellow, spilling from a tipped kettle on the cabinet's back post (blind review
    # 2026-10-22: a grey heap under a hanging block read as a claw machine).
    sphere('Body', (0, 2.55, 0), (0.8, 0.7, 0.52), 'honey', n=10, rings=4)
    for x, y, z in ((-0.45, 3.05, -0.2), (0.3, 3.1, -0.25), (0.05, 3.2, 0.1), (0.5, 2.95, 0.2)):
        sphere('Body', (x, y, z), 0.16, 'cream', n=6, rings=3)
    lathe('Body', [(0.0, 0.0), (0.32, 0.04), (0.36, 0.32), (0.0, 0.36)], 'iron', n=8, m=at((0.45, 3.3, 0.35), rz=25))
    cyl('Body', (0.6, 2.55, 0.5), 0.05, 0.8, 'iron', n=6)
    declare('Glass', False)
    span('Glass', (-0.88, 2.56, -0.7), (0.88, 4.39, 0.7), 'moon')
    for x in (-0.93, 0.93):
        for z in (-0.75, 0.75):
            cyl('Body', (x, 2.55, z), 0.05, 1.85, 'gold', n=6)
    span('Body', (-0.9, 3.4, -0.75), (-0.84, 3.7, -0.71), 'gold')                     # the door's handle
    span('Body', (-1.02, 4.4, -0.85), (1.02, 4.5, 0.85), 'crimson', bevel=0.03)
    for k in range(5):                                                                  # a striped canopy
        x0 = -1.0 + k * 0.4
        span('Body', (x0, 4.5, -0.84), (x0 + 0.4, 4.78 - 0.1 * abs(k - 2), 0.84), ('crimson', 'cream')[k % 2])
    span('Glow_Warm_1', (-0.4, 4.25, -0.3), (0.4, 4.38, 0.3), 'lamp')                 # a lamp under the roof
    stand()
    done('a popcorn cart: a crimson cart on gold legs and little black casters, a glass cabinet on gold posts '
         'with a heap of popcorn and an iron kettle, a crimson roof with a small lamp on top')


def more_furniture():
    return {'DiningChair': f_dining_chair, 'SaladBar': f_salad_bar, 'CoffeeUrn': f_coffee_urn,
            'DessertTrolley': f_dessert_trolley, 'DartsBoard': f_darts_board, 'ArcadeCabinet': f_arcade_cabinet,
            'PingPongTable': f_ping_pong_table, 'BoardGameShelf': f_board_game_shelf, 'ChessTable': f_chess_table,
            'CoffeeTable': f_coffee_table, 'Washstand': f_washstand, 'Toilet': f_toilet,
            'GardenBench': f_garden_bench, 'CrystalBallTable': f_crystal_ball_table,
            'VendingMachine': f_vending_machine, 'BarTable': f_bar_table, 'PopcornCart': f_popcorn_cart}


def more_decor():
    return {'PlantStand': d_plant_stand, 'HallStand': d_hall_stand, 'LuggageCart': d_luggage_cart,
            'Fireplace': d_fireplace, 'TowelRack': d_towel_rack, 'Fountain': d_fountain,
            'Candelabra': d_candelabra}


assert set(more_furniture()) == set(MORE_FURNITURE_IDS) and set(more_decor()) == set(MORE_DECOR_IDS)


def review_more(out, fbx, names, manifest):
    """The new pieces' own sheets (review/more/): on their squares beside the 5-stud person with Use marked,
    and the floor-level elevations (a Wall piece hangs: it shows floating there, against no wall)."""
    sub = out / 'more'
    fsheet = review_furniture(sub, fbx, names, manifest)
    esheet = review_elevations(sub, fbx, names, manifest)
    ssheet = review_sitting(sub, fbx, 'haunted_manor', {n: manifest[n] for n in names})
    return fsheet, esheet, ssheet
