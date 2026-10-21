"""The location-0 ("every location") furniture in Frostfang Lodge's and Bayou Spa's own styles (2026-10-21).

MODELS.md, "Inner walls, doors and furniture (built rooms)": the location-0 furniture is modelled in every kit in
its style; until a kit has one, the code may take HotelKit.HauntedManor's. These are the Lodge's and the Spa's,
the 23 ids Pieces.luau has with `location = 0` and `furniture = true`:

    Nightstand Wardrobe WritingDesk DiningTable BreakfastBuffet BarStool PoolTable CardTable Bathtub FloorLamp
    DiningChair SaladBar CoffeeUrn DessertTrolley DartsBoard ArcadeCabinet PingPongTable BoardGameShelf
    ChessTable CoffeeTable Washstand Toilet GardenBench

The same footprints (their Pieces rows), the same `Use` points and Poses as the Manor's (so the code treats every
kit's alike): Stand 1.5 in front; Sit on the BarStool (0, 2.6, -0.2), DiningChair (0, 1.82, -0.15), Toilet
(0, 1.72, -0.35) and GardenBench (0, 1.75, -0.25), all looking -Z; the Bathtub Lie (-0.3, 0.75, 0) looking +X in
its water, waived as the Manor's (2 x 1 squares hold a reclined guest only). Every Sit piece here is held to the
seated 5-stud person (sit_faults, `sit_figure` per piece): its seat ends where the shins hang (0.4 ahead of Use)
and its back stands behind the torso, so the seats are a little shallower in front than the Manor's.

Frostfang Lodge (an icy lodge): pale birch with log legs and edges, carved snowflakes on the panels, red and
cream plaid, iron hardware, snow caps on the tall tops, aurora stripes (teal, mint, violet) as accents, an
aurora-glowing arcade marquee. Bayou Spa (a swamp spa): weathered cypress on flared root feet, drift-grey tops,
woven rattan panels, moss hanging off the edges, copper and brass, lily pads, lotus flowers, frogs, firefly jars.

Not a script of its own: tools/build_built_rooms.py runs this file in its own namespace (exec), after
tools/build_built_rooms_more.py, so furn, use, stand, done, mfurn, the kit's shapes and the Bayou helpers (seg,
lotus, frog, lily_pad, cattails, firefly_lantern, boulder, oval, ring_prism) are used as they are there:

    blender -b --python-exit-code 1 -P tools/build_built_rooms.py -- sets frostfang_lodge,bayou_spa
"""
# Names below (K, Vector, Matrix, math, box, span, cyl, lathe, sphere, prism, at, round_arch_points, declare,
# mfurn, use, stand, done, bar_seat, review_*, place, clear, render, _squares, _sitting, _REV, FF_PALETTE,
# BS_PALETTE, TOOLS, the Bayou helpers, _ff_mug, ellipse) come from tools/build_built_rooms.py, which execs this.

EVERY_IDS = ('Nightstand', 'Wardrobe', 'WritingDesk', 'DiningTable', 'BreakfastBuffet', 'BarStool', 'PoolTable',
             'CardTable', 'Bathtub', 'FloorLamp', 'DiningChair', 'SaladBar', 'CoffeeUrn', 'DessertTrolley',
             'DartsBoard', 'ArcadeCabinet', 'PingPongTable', 'BoardGameShelf', 'ChessTable', 'CoffeeTable',
             'Washstand', 'Toilet', 'GardenBench')

# The kits' palettes gain a few colours, appended (the atlas cells of the colours already there keep their place).
FF_PALETTE.extend([('birch', (228, 210, 178)), ('birch_shade', (200, 178, 142)), ('felt', (44, 104, 96))])
BS_PALETTE.extend([('berry', (170, 52, 84)), ('felt', (60, 112, 84))])

_lift(TOOLS / 'build_hotel_frostfang_lodge.py', ['flake'], globals())

ROLE = {    # each kit's colour for a role the shared shapes below ask for
    'ff': dict(wood='birch', wood2='birch_shade', dark='log_dark', mid='log', top='log', metal='iron',
               knob='iron', glass='ice', bowl='log', plate='white', cloth='cream', line='white'),
    'bs': dict(wood='cypress', wood2='cypress_light', dark='cypress_dark', mid='cypress_light', top='drift',
               metal='brass', knob='copper', glass='water_light', bowl='stone_light', plate='white',
               cloth='linen', line='linen'),
}
WAIVE_TUB = ('a tub is lain in reclining: its 2 x 1 squares (Pieces) hold 4.4 x 1.8 inside; a straight 5-stud '
             "person, arms at the sides, needs 5.2 x 3.9: 3 x 2 squares (August's call)")


def kfurn(id_):
    """Begin Furniture_<id_> (a Wall piece may hang: mfurn), held to the seated figure if it is a Sit piece."""
    p = mfurn(id_)
    p.sit_figure = True
    return p


# --- The kits' dress ----------------------------------------------------------------------------------

def leg(kit, x, z, h, r=0.14, col=None):
    """A leg standing on the floor to h: the Lodge's a round log, the Spa's a cypress knee flaring at its foot."""
    if kit == 'ff':
        cyl('Body', (x, 0, z), r, h, col or 'log', n=8)
    else:
        lathe('Body', [(r * 1.9, 0.0), (r * 1.35, 0.12), (r * 1.05, 0.38), (r, h)], col or 'cypress_dark', n=8,
              base=(x, 0, z))


def panel(kit, x0, x1, y0, y1, z, carve=True):
    """A door or drawer front on a face at z (facing -Z), 0.05 proud, its back 0.02 in. The Lodge's a lighter
    birch panel with a snowflake carved on it (`carve`); the Spa's woven rattan, two-tone bands alternately
    0.015 prouder (a weave, no raised seams)."""
    if kit == 'ff':
        span('Body', (x0, y0, z - 0.05), (x1, y1, z + 0.02), 'birch_shade', bevel=0.03)
        if carve:
            r = 0.3 * min(x1 - x0, y1 - y0)
            flake('Body', ((x0 + x1) / 2, (y0 + y1) / 2, z - 0.05), r, 'snow', stagger=True)
        return
    n = max(2, round((y1 - y0) / 0.22))
    for i in range(n):
        ya, yb = y0 + (y1 - y0) * i / n, y0 + (y1 - y0) * (i + 1) / n
        span('Body', (x0, ya, z - 0.05 - 0.015 * (i % 2)), (x1, yb, z + 0.02), 'rattan' if i % 2 else 'rattan_dark')


def knob(kit, x, y, z, r=0.07):
    sphere('Body', (x, y, z), r, ROLE[kit]['knob'], n=6, rings=3)


def moss_fringe(x0, x1, ytop, z, depth=0.3, col='moss', t=0.04):
    """Moss hanging off an edge on a face at z (facing -Z): scallops from ytop down about `depth`, t thick in
    front of the face (the Spa's walls' fringe, smaller)."""
    n = max(1, round((x1 - x0) / 0.5))
    w = (x1 - x0) / n
    pts = [(x0, ytop)]
    for k in range(n):
        xc = x0 + w * (k + 0.5)
        dip = depth * (1.0 if k % 2 == 0 else 0.7)
        pts += [(xc - 0.5 * w * math.cos(math.pi * i / 6), ytop - 0.06 - dip * math.sin(math.pi * i / 6))
                for i in range(1, 6)]
        pts.append((x0 + w * (k + 1), ytop - 0.06))
    pts[-1] = (x1, ytop)
    prism('Body', pts, z - t, z, col, plane='xy')


def aurora(x0, x1, y0, z, h=0.3, waves=1.0):
    """Three wavy stripes, teal under mint under violet, h tall in all, on a face at z (facing -Z): the Lodge's
    aurora accent. Each 0.01 prouder than the one under it; their backs 0.01 in."""
    n = 8
    amp = 0.12 * h

    def edge(k, x):
        return y0 + k * h / 3 + amp * math.sin(2 * math.pi * waves * (x - x0) / (x1 - x0) + 0.5 * k)
    xs = [x0 + (x1 - x0) * i / n for i in range(n + 1)]
    for k, col in enumerate(('teal', 'mint', 'violet')):
        pts = [(x, edge(k, x)) for x in xs] + [(x, edge(k + 1, x)) for x in reversed(xs)]
        prism('Body', pts, z - 0.02 - 0.01 * k, z + 0.01, col, plane='xy')


def aurora_side(sx, z0, z1, y0, h=0.4):
    """The aurora's stripes on a side face at x = sx * 1.05 (the arcade cabinet's), along Z."""
    n = 6
    amp = 0.12 * h
    zs_ = [z0 + (z1 - z0) * i / n for i in range(n + 1)]

    def edge(k, z):
        return y0 + k * h / 3 + amp * math.sin(2 * math.pi * (z - z0) / (z1 - z0) + 0.5 * k)
    for k, col in enumerate(('teal', 'mint', 'violet')):
        pts = [(z, edge(k, z)) for z in zs_] + [(z, edge(k + 1, z)) for z in reversed(zs_)]
        a, b = sorted((sx * 1.04, sx * (1.07 + 0.01 * k)))
        prism('Body', pts, a, b, col, plane='zy')


def snow_cap(x0, x1, z0, z1, y):
    """Soft snow lying on a top at y: a bevelled layer 0.1 thick and one long low drift along it (separate round
    lumps read as plates lying on the top, the sheets 2026-10-21)."""
    span('Body', (x0, y - 0.01, z0), (x1, y + 0.1, z1), 'snow', bevel=0.04)
    sphere('Body', ((x0 + x1) / 2, y + 0.1, (z0 + z1) / 2), ((x1 - x0) * 0.42, 0.07, (z1 - z0) * 0.32), 'snow',
           n=10, rings=3)


def jar_lantern(glow, x, y, z, r=0.14, h=0.22, metal='brass'):
    """A firefly jar standing on (x, y, z): a brass foot, the glowing jar (`glow`, its own part), a brass cap."""
    cyl('Body', (x, y, z), r + 0.04, 0.05, metal, n=8)
    cyl(glow, (x, y + 0.05, z), r, h, 'firefly', n=8)
    cyl('Body', (x, y + 0.05 + h, z), r + 0.03, 0.07, metal, n=8, r_top=0.06)


def plaid(x0, x1, z0, z1, y, along=(), across=(), w=0.05):
    """Cream stripes on a red cushion's top at y: `along` at those z, `across` at those x (crossing ones 0.004
    prouder, so their tops never share a plane)."""
    for z in along:
        span('Body', (x0, y - 0.01, z - w), (x1, y + 0.012, z + w), 'cream')
    for x in across:
        span('Body', (x - w, y - 0.01, z0), (x + w, y + 0.016, z1), 'cream')


def star(x, y, z, r, col, t=0.04):
    pts = [(x + r * math.cos(math.pi / 2 + k * math.pi / 5) * (1 if k % 2 == 0 else 0.45),
            z + r * math.sin(math.pi / 2 + k * math.pi / 5) * (1 if k % 2 == 0 else 0.45)) for k in range(10)]
    prism('Body', pts, y, y + t, col, plane='xz')


def cup_on_saucer(x, y, z, cup, saucer='white', h=0.24, r=0.16):
    cyl('Body', (x, y, z), r + 0.09, 0.03, saucer, n=10)
    cyl('Body', (x, y + 0.03, z), r, h, cup, n=8)
    span('Body', (x + r - 0.03, y + 0.1, z - 0.03), (x + r + 0.11, y + 0.22, z + 0.03), cup)


# --- Bedroom ------------------------------------------------------------------------------------------

def ff_nightstand():
    kfurn('Nightstand')
    for x in (-0.8, 0.8):
        for z in (-0.6, 0.6):
            leg('ff', x, z, 0.36, r=0.13, col='log_dark')
    span('Body', (-1.0, 0.3, -0.8), (1.0, 1.95, 0.8), 'birch', bevel=0.08)
    span('Body', (-1.08, 1.95, -0.88), (1.08, 2.1, 0.88), 'log', bevel=0.04)
    panel('ff', -0.85, 0.85, 1.3, 1.8, -0.8, carve=False)                  # the drawer, an aurora band on it
    aurora(-0.7, 0.7, 1.43, -0.85, h=0.24)
    panel('ff', -0.85, 0.85, 0.45, 1.15, -0.8)                              # the door, a snowflake carved on it
    knob('ff', 0.0, 1.36, -0.86, r=0.06)
    knob('ff', 0.66, 0.8, -0.86)
    _ff_mug('Body', (0.45, 2.1, 0.25), r=0.2, h=0.34, col='red')
    span('Body', (-0.75, 2.1, -0.45), (0.1, 2.24, 0.35), 'navy', bevel=0.02)
    span('Body', (-0.66, 2.24, -0.36), (0.0, 2.33, 0.25), 'red_dark', bevel=0.02)
    stand()
    done('a log-legged birch bedside cabinet: an aurora band across the drawer, a snowflake carved on the door, '
         'iron knobs, a mug of cocoa and two books on the log top')


def bs_nightstand():
    kfurn('Nightstand')
    for x in (-0.78, 0.78):
        for z in (-0.6, 0.6):
            leg('bs', x, z, 0.4, r=0.11)
    span('Body', (-1.0, 0.32, -0.8), (1.0, 1.95, 0.8), 'cypress', bevel=0.08)
    span('Body', (-1.08, 1.95, -0.88), (1.08, 2.1, 0.88), 'drift', bevel=0.04)
    panel('bs', -0.85, 0.85, 1.3, 1.8, -0.8)
    panel('bs', -0.85, 0.85, 0.45, 1.15, -0.8)
    knob('bs', 0.0, 1.55, -0.88)
    knob('bs', 0.66, 0.8, -0.88)
    moss_fringe(-1.08, -0.3, 2.06, -0.88, depth=0.32)
    jar_lantern('Glow_Warm_1', 0.5, 2.1, 0.3, r=0.15, h=0.22)
    span('Body', (-0.8, 2.1, -0.5), (0.0, 2.19, 0.3), 'towel', bevel=0.03)
    lotus((-0.4, 2.19, -0.1), s=0.55)
    stand()
    done('a cypress bedside cabinet on root feet: woven rattan drawer and door, copper knobs, moss hanging off the '
         'weathered top, a firefly jar, a folded towel with a lotus on it')


def ff_wardrobe():
    kfurn('Wardrobe')
    for x in (-2.22, 2.22):
        for z in (-0.72, 0.72):
            cyl('Body', (x, 0, z), 0.18, 5.62, 'log', n=8)                 # log corner posts
    span('Body', (-2.2, 0.35, -0.9), (2.2, 5.6, 0.9), 'birch', bevel=0.1)
    for sx in (-1, 1):
        x0, x1 = sorted((0.04 * sx, 2.0 * sx))
        span('Body', (x0, 0.6, -0.95), (x1, 5.25, -0.88), 'birch_shade', bevel=0.04)
        flake('Body', (1.02 * sx, 3.55, -0.95), 0.5, 'snow', stagger=True)
        flake('Body', (1.02 * sx, 1.6, -0.95), 0.28, 'snow', stagger=True)
        xa, xb = sorted((2.0 * sx, 1.45 * sx))
        for y in (1.0, 4.75):                                               # iron strap hinges
            span('Body', (xa, y, -0.99), (xb, y + 0.14, -0.94), 'iron')
        sphere('Body', (0.25 * sx, 3.0, -0.98), 0.09, 'iron', n=6, rings=3)
    aurora(-2.0, 2.0, 5.28, -0.9, h=0.28, waves=1.5)
    span('Body', (-2.45, 5.6, -1.05), (2.45, 5.82, 1.05), 'log_dark', bevel=0.05)
    # A little cabin roof running left to right on the cornice, snow lying on both slopes (a ridge running front to
    # back read as an open book from the game's camera, the sheets 2026-10-21).
    prism('Body', [(-0.98, 5.82), (0.98, 5.82), (0.0, 6.1)], -2.36, 2.36, 'log', plane='zy')
    prism('Body', [(-1.08, 5.82), (-0.98, 5.82), (0.0, 6.1), (0.98, 5.82), (1.08, 5.82), (0.0, 6.2)], -2.42, 2.42,
          'snow', plane='zy')
    stand()
    done('a tall birch armoire between four log posts: two doors with carved snowflakes and iron strap hinges, '
         'an aurora band under a dark log cornice, a little log cabin roof on top with snow on both slopes')


def bs_wardrobe():
    kfurn('Wardrobe')
    for x in (-1.9, 1.9):
        for z in (-0.6, 0.6):
            leg('bs', x, z, 0.4, r=0.15)
    span('Body', (-2.2, 0.35, -0.9), (2.2, 5.5, 0.9), 'cypress', bevel=0.1)
    for sx in (-1, 1):
        x0, x1 = sorted((0.04 * sx, 2.0 * sx))
        span('Body', (x0, 0.6, -0.95), (x1, 5.25, -0.88), 'cypress_dark', bevel=0.03)
        panel('bs', x0 + 0.22, x1 - 0.22, 1.0, 4.85, -0.95)                 # louvred rattan in a dark frame
        knob('bs', 0.13 * sx, 3.0, -0.97, r=0.08)
    span('Body', (-2.3, 5.5, -1.0), (2.3, 5.68, 1.0), 'cypress_dark', bevel=0.05)
    prism('Body', round_arch_points(-2.0, 2.0, 5.68, 6.2, n=10), -0.9, 0.9, 'cypress', plane='xy')
    cyl('Body', (0, 0, 0), 0.22, 0.04, 'lily', n=10, m=at((0, 5.95, -0.9), rx=-90))      # a lily pad medallion
    cyl('Body', (0, 0, 0), 0.09, 0.06, 'lotus', n=8, m=at((0, 5.95, -0.9), rx=-90))
    moss_fringe(-2.3, -1.1, 5.64, -1.0, depth=0.45, col='moss_light')
    moss_fringe(1.5, 2.3, 5.64, -1.0, depth=0.35)
    stand()
    done('a cypress armoire on root feet: louvred rattan doors in dark frames, copper knobs, a round-arched top '
         'with a lily pad medallion, Spanish moss hanging off the cornice')


def ff_writing_desk():
    kfurn('WritingDesk')
    for x in (-2.15, 2.15):
        for z in (-0.72, 0.72):
            cyl('Body', (x, 0, z), 0.15, 1.95, 'log', n=8)
        cyl('Body', (0, 0, 0), 0.07, 1.44, 'log_dark', n=6, m=at((x, 0.5, -0.72), rx=90))
    cyl('Body', (0, 0, 0), 0.07, 4.3, 'log_dark', n=6, m=at((-2.15, 0.5, 0.72), rz=-90))
    span('Body', (-2.3, 1.9, -0.85), (2.3, 2.36, 0.85), 'birch')
    span('Body', (-2.45, 2.35, -1.0), (2.45, 2.6, 1.0), 'log', bevel=0.06)
    span('Body', (-0.8, 1.95, -0.9), (0.8, 2.3, -0.83), 'birch_shade', bevel=0.02)
    knob('ff', 0.0, 2.12, -0.92, r=0.06)
    for x0, x1 in ((-2.2, -0.9), (0.9, 2.2)):
        aurora(x0, x1, 1.98, -0.85, h=0.3)
    span('Body', (-0.9, 2.6, -0.55), (0.4, 2.63, 0.3), 'cream')
    cyl('Body', (1.4, 2.6, 0.4), 0.18, 0.2, 'ink', n=8)
    cyl('Body', (0, 0, 0), 0.04, 1.1, 'white', n=4, m=at((-0.2, 2.67, -0.1), rz=-80, ry=20))
    _ff_mug('Body', (-1.7, 2.6, 0.35), r=0.2, h=0.26, col='red')
    stand()
    done('a writing desk on log legs and stretchers: a log top, a birch drawer between two aurora bands, a letter, '
         'an inkpot, a quill and a mug of cocoa')


def bs_writing_desk():
    kfurn('WritingDesk')
    for x in (-2.15, 2.15):
        for z in (-0.72, 0.72):
            leg('bs', x, z, 1.95, r=0.12)
    span('Body', (-2.3, 1.9, -0.85), (2.3, 2.36, 0.85), 'cypress')
    span('Body', (-2.45, 2.35, -1.0), (2.45, 2.6, 1.0), 'drift', bevel=0.06)
    panel('bs', -0.8, 0.8, 1.95, 2.3, -0.85)
    knob('bs', 0.0, 2.12, -0.93, r=0.06)
    moss_fringe(-2.45, -1.6, 2.56, -1.0, depth=0.3)
    span('Body', (-0.9, 2.6, -0.55), (0.4, 2.63, 0.3), 'linen')
    lily_pad((-0.2, 2.63, -0.1), 0.24, 0.04, 'lily', notch=30)               # a lily-pad paperweight
    cyl('Body', (1.4, 2.6, 0.4), 0.17, 0.2, 'copper', n=8)
    seg('Body', (1.4, 2.72, 0.4), (1.02, 2.84, 0.22), 0.03, 'reed', n=4)     # a reed pen in the inkpot
    cyl('Body', (-1.7, 2.6, 0.4), 0.22, 0.14, 'stone', n=8)
    sphere('Body', (-1.7, 2.74, 0.4), (0.2, 0.1, 0.2), 'moss', n=8, rings=3)
    stand()
    done('a writing desk on cypress root legs: a weathered top with moss hanging off its corner, a rattan drawer, '
         'a letter under a lily-pad paperweight, a copper inkpot with a reed pen, a pot of moss')


# --- Dining -------------------------------------------------------------------------------------------

def ff_dining_table():
    kfurn('DiningTable')
    for x in (-2.15, 2.15):
        for z in (-2.15, 2.15):
            cyl('Body', (x, 0, z), 0.2, 2.05, 'log', n=8)
    span('Body', (-2.3, 2.0, -2.3), (2.3, 2.36, 2.3), 'birch')
    span('Body', (-2.5, 2.35, -2.5), (2.5, 2.6, 2.5), 'log', bevel=0.06)
    span('Body', (-0.8, 2.6, -2.4), (0.8, 2.63, 2.4), 'red')                 # a plaid runner
    plaid(-0.78, 0.78, -2.38, 2.38, 2.63, across=(-0.5, 0.5))
    for z in (-1.6, 1.6):
        span('Body', (-0.78, 2.62, z - 0.05), (0.78, 2.65, z + 0.05), 'cream')
    for k, (x, z) in enumerate(((-1.5, -1.5), (1.5, -1.5), (-1.5, 1.5), (1.5, 1.5))):
        cyl('Body', (x, 2.6, z), 0.45, 0.05, 'white', n=10)
        span('Body', (x - 0.16, 2.65, z - 0.24), (x + 0.16, 2.69, z + 0.24), ('teal', 'violet', 'mint', 'teal')[k])
    lathe('Body', [(0.22, 2.63), (0.5, 2.72), (0.0, 2.72)], 'log_dark', n=10)
    for dx, dz in ((-0.2, -0.1), (0.18, -0.13), (0.0, 0.2)):
        sphere('Body', (dx, 2.77, dz), 0.11, 'red', n=6, rings=4)
    stand()
    done('a square log-legged table: a red plaid runner, four white plates with napkins in aurora colours, a '
         'bowl of red apples')


def bs_dining_table():
    kfurn('DiningTable')
    for x in (-2.15, 2.15):
        for z in (-2.15, 2.15):
            leg('bs', x, z, 2.05, r=0.16)
    span('Body', (-2.3, 2.0, -2.3), (2.3, 2.36, 2.3), 'cypress')
    span('Body', (-2.5, 2.35, -2.5), (2.5, 2.6, 2.5), 'drift', bevel=0.06)
    for i in range(12):                                                      # a woven rattan runner
        za, zb = -2.4 + 0.4 * i, -2.4 + 0.4 * (i + 1)
        span('Body', (-0.8, 2.59, za), (0.8, 2.63 + 0.012 * (i % 2), zb), 'rattan' if i % 2 else 'rattan_dark')
    for k, (x, z) in enumerate(((-1.5, -1.5), (1.5, -1.5), (-1.5, 1.5), (1.5, 1.5))):
        lily_pad((x, 2.6, z), 0.62, 0.025, 'lily', notch=45 + 90 * k)        # lily-pad place mats
        cyl('Body', (x, 2.625, z), 0.4, 0.04, 'white', n=10)
    lathe('Body', [(0.3, 2.63), (0.56, 2.7), (0.0, 2.7)], 'stone', n=10)    # a shallow water bowl, a lotus in it
    cyl('Body', (0, 2.7, 0), 0.5, 0.01, 'water', n=10)
    lotus((0, 2.71, 0), s=0.36)
    stand()
    done('a square table on cypress root legs: a weathered top, a woven rattan runner, white plates on lily-pad '
         'mats, a lotus floating in a stone bowl')


def ff_buffet():
    kfurn('BreakfastBuffet')
    for x in (-3.7, 3.7):
        for z in (-0.65, 0.65):
            cyl('Body', (x, 0, z), 0.18, 0.34, 'log_dark', n=8)
    span('Body', (-4.0, 0.3, -0.92), (4.0, 2.5, 0.92), 'birch', bevel=0.08)
    span('Body', (-4.1, 2.5, -1.05), (4.1, 2.65, 1.05), 'log', bevel=0.05)
    for k in range(3):
        x0 = -3.8 + k * 2.55
        panel('ff', x0, x0 + 2.45, 0.55, 2.25, -0.92)
        knob('ff', x0 + 2.2, 1.4, -0.98)
    cyl('Body', (-2.6, 2.65, 0), 0.55, 0.04, 'white', n=12)                 # pancakes, syrup and butter
    for k in range(4):
        cyl('Body', (-2.6, 2.69 + 0.07 * k, 0), 0.38 - 0.02 * (k % 2), 0.07, 'cocoa_light', n=10)
    cyl('Body', (-2.6, 2.97, 0), 0.3, 0.015, 'cocoa', n=10)
    span('Body', (-2.68, 2.98, -0.08), (-2.52, 3.04, 0.08), 'yellow')
    lathe('Body', [(0.45, 2.65), (0.62, 2.9), (0.0, 2.9)], 'wood_light', n=10, base=(0.0, 0, 0.05))   # bread
    for x, z, a in ((-0.18, -0.08, 20), (0.2, 0.2, -30)):
        sphere('Body', (0, 0, 0), (0.3, 0.13, 0.15), 'cocoa_light', n=8, rings=4, m=at((x, 2.95, z), ry=a))
    lathe('Body', [(0.22, 2.65), (0.26, 2.85), (0.17, 3.0), (0.2, 3.06), (0.0, 3.06)], 'white', n=10,
          base=(2.4, 0, -0.1))                                               # a milk jug and jam jars
    span('Body', (2.62, 2.75, -0.14), (2.74, 2.98, -0.06), 'white')
    for x, z, colr in ((3.15, 0.4, 'red'), (3.35, -0.3, 'pink')):
        cyl('Body', (x, 2.65, z), 0.14, 0.22, colr, n=8)
        cyl('Body', (x, 2.87, z), 0.15, 0.05, 'cream', n=8)
    stand()
    done('a birch sideboard on log feet, three doors with carved snowflakes: a stack of pancakes with syrup and '
         'butter, a basket of bread, a milk jug, jars of jam')


def bs_buffet():
    kfurn('BreakfastBuffet')
    for x in (-3.7, 3.7):
        for z in (-0.65, 0.65):
            leg('bs', x, z, 0.34, r=0.12)
    span('Body', (-4.0, 0.3, -0.92), (4.0, 2.5, 0.92), 'cypress', bevel=0.08)
    span('Body', (-4.1, 2.5, -1.05), (4.1, 2.65, 1.05), 'drift', bevel=0.05)
    for k in range(3):
        x0 = -3.8 + k * 2.55
        panel('bs', x0, x0 + 2.45, 0.55, 2.25, -0.92)
        knob('bs', x0 + 2.2, 1.4, -1.0)
    moss_fringe(2.9, 4.1, 2.62, -1.05, depth=0.4)
    cyl('Body', (-2.6, 2.65, 0), 0.6, 0.04, 'white', n=12)                  # beignets
    for x, z in ((-2.85, -0.2), (-2.35, -0.2), (-2.6, 0.22), (-2.95, 0.2), (-2.25, 0.22)):
        sphere('Body', (x, 2.78, z), (0.17, 0.11, 0.17), 'linen', n=8, rings=4)
    lathe('Body', [(0.32, 2.65), (0.36, 2.9), (0.3, 3.1), (0.16, 3.2), (0.18, 3.25), (0.0, 3.28)], 'copper', n=10,
          base=(0.0, 0, 0.1))                                                # a copper coffee pot
    seg('Body', (0.28, 2.95, 0.1), (0.56, 3.15, 0.1), 0.05, 'copper', n=5)
    span('Body', (-0.45, 2.85, 0.06), (-0.33, 3.12, 0.14), 'cypress_dark')
    lathe('Body', [(0.22, 2.65), (0.25, 2.95), (0.18, 3.05), (0.0, 3.05)], 'lotus_heart', n=10, base=(2.2, 0, -0.1))
    span('Body', (2.4, 2.75, -0.14), (2.52, 2.96, -0.06), 'lotus_heart')
    lathe('Body', [(0.18, 2.65), (0.35, 2.8), (0.0, 2.8)], 'stone_light', n=10, base=(3.2, 0, 0.3))
    for dx, dz in ((-0.1, -0.08), (0.12, 0.0), (0.0, 0.13), (-0.05, 0.02)):
        sphere('Body', (3.2 + dx, 2.86, 0.3 + dz), 0.09, 'berry', n=6, rings=3)
    stand()
    done('a cypress sideboard on root feet with three rattan doors and moss hanging off its end: a plate of '
         'beignets, a copper coffee pot, a jug of juice, a bowl of berries')


def ff_bar_stool():
    kfurn('BarStool')
    # The seat ends at z -0.6 (the seated figure's shins hang from 0.4 ahead of Use) and the back stands behind
    # the torso (z 0.62..0.86); the foot ring at 1.42, under the feet (MODELS.md "Furniture": the seat 2.6).
    for x in (-0.53, 0.53):
        for z in (-0.5, 0.5):
            cyl('Body', (x, 0, z), 0.1, 2.44, 'birch', n=6)
    lathe('Body', [(0.69, 1.42), (0.77, 1.42), (0.77, 1.5), (0.69, 1.5)], 'iron', n=12, closed=True)
    span('Body', (-1.05, 2.42, -0.6), (1.05, 2.52, 0.86), 'log', bevel=0.03)
    span('Body', (-1.02, 2.52, -0.58), (1.02, 2.6, 0.6), 'red', bevel=0.03)
    plaid(-1.0, 1.0, -0.56, 0.58, 2.6, along=(-0.25, 0.25), across=(-0.45, 0.45))
    for x in (-0.8, 0.8):
        cyl('Body', (x, 2.52, 0.74), 0.08, 0.6, 'log_dark', n=6)
    cyl('Body', (0, 0, 0), 0.12, 2.0, 'log', n=8, m=at((-1.0, 3.12, 0.74), rz=-90))
    bar_seat(-1.0, 1.0, -0.6, 0.6, 2.6)
    use((0, 2.6, -0.2), (0, 0, -1), 'Sit')
    done('a bar stool on four birch legs with an iron foot ring, a red plaid cushion at 2.6 on a log seat, a low '
         'log back rail')


def bs_bar_stool():
    kfurn('BarStool')
    lathe('Body', [(0.75, 0.0), (0.55, 0.12), (0.3, 0.35), (0.17, 0.9), (0.15, 2.44)], 'cypress_dark', n=10)
    lathe('Body', [(0.56, 1.42), (0.64, 1.42), (0.64, 1.5), (0.56, 1.5)], 'copper', n=12, closed=True)
    for k in range(4):
        box('Body', (0, 0, 0), (0.46, 0.05, 0.06), 'copper',
            m=at((0, 1.46, 0), ry=45 + 90 * k) @ Matrix.Translation((0.36, 0, 0)))
    span('Body', (-1.05, 2.42, -0.6), (1.05, 2.52, 0.86), 'drift', bevel=0.03)
    span('Body', (-1.02, 2.52, -0.58), (1.02, 2.6, 0.6), 'lotus', bevel=0.03)
    for x in (-0.86, 0.86):
        cyl('Body', (x, 2.52, 0.74), 0.07, 0.72, 'cypress_dark', n=6)
    for i in range(4):
        ya, yb = 2.62 + 0.155 * i, 2.62 + 0.155 * (i + 1)
        span('Body', (-0.8, ya, 0.68 - 0.015 * (i % 2)), (0.8, yb, 0.8), 'rattan' if i % 2 else 'rattan_dark')
    span('Body', (-0.95, 3.24, 0.64), (0.95, 3.34, 0.84), 'cypress_light', bevel=0.03)
    bar_seat(-1.0, 1.0, -0.6, 0.6, 2.6)
    use((0, 2.6, -0.2), (0, 0, -1), 'Sit')
    done('a bar stool on a cypress root pedestal with a copper foot ring, a lotus-pink cushion at 2.6 on a '
         'weathered seat, a low woven rattan back')


def dining_chair(kit):
    kfurn('DiningChair')
    # The seat's front at z -0.55 (the seated figure's shins hang from 0.4 ahead of Use) and the back from z 0.64,
    # 0.3 behind the torso; the cushion at 1.82 as the Manor's.
    if kit == 'ff':
        for sx in (-1, 1):
            x0, x1 = sorted((0.82 * sx, 1.02 * sx))
            span('Body', (x0, 0, -0.5), (x1, 1.62, -0.32), 'birch', bevel=0.03)
            span('Body', (x0, 0, 0.66), (x1, 4.1, 0.86), 'birch', bevel=0.03)
            lathe('Body', [(0.0, 4.08), (0.11, 4.16), (0.09, 4.28), (0.0, 4.36)], 'cocoa_dark', n=6,
                  base=((x0 + x1) / 2, 0, 0.76))
            span('Body', (x0 + 0.03, 0.5, -0.33), (x1 - 0.03, 0.6, 0.67), 'log')       # side stretchers
        span('Body', (-1.06, 1.6, -0.55), (1.06, 1.72, 0.84), 'birch', bevel=0.03)
        span('Body', (-1.0, 1.72, -0.53), (1.0, 1.82, 0.6), 'red', bevel=0.03)
        plaid(-0.98, 0.98, -0.51, 0.58, 1.82, along=(-0.2, 0.25), across=(-0.45, 0.45))
        cyl('Body', (0, 0, 0), 0.08, 1.64, 'log', n=6, m=at((-0.82, 2.2, 0.76), rz=-90))
        back = [(-0.82, 2.3), (0.82, 2.3)] + list(reversed(round_arch_points(-0.82, 0.82, 3.5, 3.95, n=8)))
        prism('Body', back, 0.7, 0.82, 'birch_shade', plane='xy')
        flake('Body', (0, 3.15, 0.7), 0.36, 'snow', stagger=True)
        aurora(-0.7, 0.7, 2.4, 0.7, h=0.24)
        note = ('a birch dining chair: a red plaid cushion at 1.82, a round-topped back with a carved snowflake '
                'over an aurora band, pine-cone finials')
    else:
        for sx in (-1, 1):
            leg('bs', 0.9 * sx, -0.42, 1.62, r=0.08)
            leg('bs', 0.9 * sx, 0.76, 3.0, r=0.09)
            sphere('Body', (0.9 * sx, 3.02, 0.76), 0.11, 'copper', n=6, rings=3)
        span('Body', (-1.06, 1.6, -0.55), (1.06, 1.72, 0.86), 'rattan', bevel=0.03)
        span('Body', (-1.0, 1.72, -0.53), (1.0, 1.82, 0.6), 'lotus', bevel=0.03)
        # A peacock fan of woven rattan behind the seat: wedges from a hub, alternately prouder, in a light rim.
        hub, rx, ry = (0.0, 1.95), 1.06, 2.45
        arc = lambda th, sx_=rx, sy=ry: (sx_ * math.cos(math.radians(th)), hub[1] + sy * math.sin(math.radians(th)))   # noqa: E731
        n = 8
        for k in range(n):
            t0, t1 = 12 + 156 * k / n, 12 + 156 * (k + 1) / n
            pts = [hub, arc(t0), arc((t0 + t1) / 2), arc(t1)]
            prism('Body', pts, 0.68 - 0.02 * (k % 2), 0.8, 'rattan' if k % 2 else 'rattan_dark', plane='xy')
        ths = [12 + 156 * i / 16 for i in range(17)]
        rim = [arc(t, 1.08, 2.53) for t in ths] + [arc(t, 1.0, 2.37) for t in reversed(ths)]
        prism('Body', rim, 0.64, 0.82, 'cypress_light', plane='xy')
        note = ('a cypress dining chair on root legs: a lotus-pink cushion at 1.82 on a rattan seat, a peacock fan '
                'back of woven rattan in a light cypress rim, copper caps')
    K.seat(-1.0, 1.0, -0.55, 0.65, 1.82)
    use((0, 1.82, -0.15), (0, 0, -1), 'Sit')
    done(note)


def salad_bar(kit):
    kfurn('SaladBar')
    R = ROLE[kit]
    for x in (-3.7, 3.7):
        for z in (-0.65, 0.65):
            leg(kit, x, z, 0.34, r=0.16 if kit == 'ff' else 0.12, col=R['dark'])
    span('Body', (-4.0, 0.3, -0.92), (4.0, 2.6, 0.92), R['wood'], bevel=0.08)
    for k in range(3):
        x0 = -3.8 + k * 2.55
        panel(kit, x0, x0 + 2.45, 0.55, 2.35, -0.92)
    span('Body', (-4.1, 2.6, -1.05), (4.1, 2.78, 1.05), R['top'], bevel=0.05)
    span('Body', (-4.0, 2.78, 0.5), (4.0, 3.3, 1.0), R['dark'], bevel=0.04)
    foods = ('mint', 'red_dark', 'orange', 'yellow') if kit == 'ff' else ('herb', 'lotus', 'lotus_heart', 'berry')
    for x, food in zip((-3.0, -1.0, 1.0, 3.0), foods):
        lathe('Body', [(0.38, 2.78), (0.7, 3.1), (0.0, 3.1)], R['bowl'], n=8, base=(x, 0, -0.3))
        sphere('Body', (x, 3.1, -0.3), (0.6, 0.16, 0.6), food, n=8, rings=3)
    bottles = (('cream', 'red', 'pine', 'yellow') if kit == 'ff' else ('copper', 'lily_dark', 'berry', 'chamomile'))
    for k in range(5):
        lathe('Body', [(0.15, 3.3), (0.15, 3.68), (0.06, 3.8), (0.06, 3.92)], bottles[k % 4], n=6,
              base=(-3.0 + k * 1.5, 0, 0.75))
    declare('Glass', False)
    for x in (-3.95, 0.0, 3.95):
        for z in (-0.88, 0.39):
            cyl('Body', (x, 2.78, z), 0.05, 1.16, R['metal'], n=6)
    for z0, z1 in ((-0.92, -0.85), (0.36, 0.43)):
        span('Body', (-4.02, 3.94, z0), (4.02, 4.0, z1), R['metal'])
    span('Glass', (-4.0, 4.0, -0.9), (4.0, 4.04, 0.4), R['glass'])
    if kit == 'bs':
        moss_fringe(-4.1, -2.6, 2.74, -1.05, depth=0.35)
        moss_fringe(1.4, 2.6, 2.74, -1.05, depth=0.3, col='moss_light')
    stand()
    done({'ff': 'a salad bar of birch with carved snowflake panels: greens, beets, carrots and corn in log bowls, '
                'dressings on a step, a thin glass sneeze guard on iron posts',
          'bs': 'a cypress salad bar with rattan panels and moss off its edge: herbs, radishes, corn and berries in '
                'stone bowls, dressings on a step, a thin glass sneeze guard on brass posts'}[kit])


def coffee_urn(kit):
    kfurn('CoffeeUrn')
    R = ROLE[kit]
    span('Body', (-1.0, 0, -0.9), (1.0, 2.5, 0.9), R['wood'], bevel=0.06)
    panel(kit, -0.8, 0.8, 0.3, 2.2, -0.9)
    knob(kit, 0.64, 1.25, -0.97)
    span('Body', (-1.08, 2.5, -0.98), (1.08, 2.65, 1.0), R['top'], bevel=0.04)
    ux, uz = -0.35, 0.05
    body, band, metal = ('red', 'cream', 'iron') if kit == 'ff' else ('copper', 'brass', 'brass')
    lathe('Body', [(0.3, 2.65), (0.33, 2.72), (0.22, 2.82), (0.4, 2.98), (0.44, 3.15), (0.44, 3.6),
                   (0.34, 3.78), (0.12, 3.85), (0.12, 3.92), (0.0, 3.97)], body, n=10, base=(ux, 0, uz))
    lathe('Body', [(0.46, 3.3), (0.46, 3.44)], band, n=10, base=(ux, 0, uz))
    for s in (-1, 1):
        xa, xb = sorted((ux + s * 0.38, ux + s * 0.62))
        span('Body', (xa, 3.42, uz - 0.04), (xb, 3.5, uz + 0.04), metal)
        span('Body', (ux + s * 0.56 - 0.04, 3.2, uz - 0.03), (ux + s * 0.56 + 0.04, 3.46, uz + 0.03), metal)
    span('Body', (ux - 0.06, 3.0, uz - 0.72), (ux + 0.06, 3.12, uz - 0.38), metal)
    cyl('Body', (ux, 2.84, uz - 0.66), 0.05, 0.16, metal, n=6)
    span('Body', (ux - 0.05, 3.12, uz - 0.6), (ux + 0.05, 3.42, uz - 0.5), 'black' if kit == 'ff' else 'cypress_dark')
    span('Body', (ux - 0.3, 2.65, uz - 0.88), (ux + 0.3, 2.7, uz - 0.44), 'iron')
    cyl('Body', (ux, 2.7, uz - 0.66), 0.13, 0.14, R['cloth'], n=8)
    span('Body', (-1.0, 2.65, 0.75), (1.0, 4.2, 1.0), R['dark'], bevel=0.04)
    span('Body', (-1.06, 4.2, 0.68), (1.06, 4.36, 1.06), R['mid'], bevel=0.03)
    span('Body', (-0.95, 3.75, 0.45), (0.95, 3.85, 0.76), R['wood'])
    if kit == 'ff':
        _ff_mug('Body', (0.55, 2.65, -0.5), r=0.17, h=0.26, col='red')
        _ff_mug('Body', (0.55, 2.65, 0.1), r=0.17, h=0.26, col='cream', band='red')
        for k, x in enumerate((-0.6, -0.15, 0.3, 0.75)):
            cyl('Body', (x, 3.85, 0.6), 0.12, 0.2, ('red', 'cream')[k % 2], n=8)
        snow_cap(-1.04, 1.04, 0.7, 1.04, 4.36)
        note = ('a cocoa station: a red enamel urn with a cream band, iron handles and tap over a drip tray on a '
                'birch cabinet with a carved snowflake, two mugs, a dark log upstand with a shelf of mugs, snow on top')
    else:
        cup_on_saucer(0.55, 2.65, -0.5, 'linen')
        cup_on_saucer(0.6, 2.65, 0.05, 'lotus')
        for k, x in enumerate((-0.6, -0.15, 0.3, 0.75)):
            colr = ('chamomile', 'lavender', 'herb', 'chamomile')[k]
            cyl('Body', (x, 3.85, 0.6), 0.12, 0.2, colr, n=8)
            cyl('Body', (x, 4.05, 0.6), 0.13, 0.05, 'cypress_light', n=8)
        moss_fringe(-1.06, 0.2, 4.32, 0.68, depth=0.35)
        note = ('a tea station: a copper urn with a brass band, handles and tap over a drip tray on a cypress '
                'cabinet with a rattan door, cups on saucers, an upstand with jars of chamomile, lavender and herbs, '
                'moss off its top')
    stand()
    done(note)


def dessert_trolley(kit):
    kfurn('DessertTrolley')
    R = ROLE[kit]
    post = 'log' if kit == 'ff' else 'brass'
    wheel = 'iron' if kit == 'ff' else 'cypress_dark'
    for x in (-2.25, 2.25):
        for z in (-0.8, 0.64):
            cyl('Body', (0, 0, 0), 0.2, 0.16, wheel, n=10, m=at((x, 0.2, z), rx=90))
        for z in (-0.72, 0.72):
            cyl('Body', (x, 0.3, z), 0.075, 2.5 if x < 0 else 2.75, post, n=6)
    for y in (0.9, 2.4):
        span('Body', (-2.45, y, -0.95), (2.45, y + 0.15, 0.95), R['wood'], bevel=0.04)
        span('Body', (-2.4, y + 0.15, -0.9), (2.4, y + 0.17, 0.9), R['cloth'])
    span('Body', (-2.47, 0.36, -0.82), (2.47, 0.46, 0.82), R['dark'] if kit == 'ff' else 'brass')
    cyl('Body', (0, 0, 0), 0.08, 1.6, 'log_dark' if kit == 'ff' else 'brass', n=6, m=at((2.25, 3.05, -0.8), rx=90))
    if kit == 'ff':
        cyl('Body', (0, 0, 0), 0.28, 1.3, 'cocoa', n=10, m=at((-1.85, 2.85, 0.05), rz=-90))     # a Yule log cake
        for x in (-1.84, -0.56):        # its ends' rings, each 0.01 into the log
            cyl('Body', (0, 0, 0), 0.24, 0.02, 'cocoa_light', n=10, m=at((x, 2.85, 0.05), rz=-90 if x > -1 else 90))
        sphere('Body', (-1.2, 3.11, 0.05), (0.6, 0.06, 0.2), 'snow', n=8, rings=3)
        sphere('Body', (-1.0, 3.2, 0.05), 0.07, 'red', n=6, rings=3)
        for i, a in enumerate((-35, 145)):
            box('Body', (0, 0, 0), (0.18, 0.03, 0.08), 'pine',
                m=at((-1.0, 3.18 + 0.01 * i, 0.05), ry=a) @ Matrix.Translation((0.14, 0, 0)))
        span('Body', (1.0, 2.57, -0.35), (1.8, 3.0, 0.35), 'cocoa_light')                      # a gingerbread house
        prism('Body', [(0.92, 3.0), (1.88, 3.0), (1.4, 3.38)], -0.42, 0.42, 'snow', plane='xy')
        span('Body', (1.3, 2.57, -0.37), (1.5, 2.82, -0.34), 'cocoa_dark')
        for k, x in enumerate((1.12, 1.68)):
            sphere('Body', (x, 2.88, -0.36), 0.04, ('red', 'mint')[k], n=6, rings=3)
        lathe('Body', [(0.36, 2.57), (0.28, 2.92), (0.0, 2.96)], 'pink', n=10, base=(0.25, 0, 0.3))
        sphere('Body', (0.25, 2.97, 0.3), (0.12, 0.06, 0.12), 'cream', n=6, rings=3)
        cyl('Body', (-1.0, 1.07, 0.1), 0.62, 0.18, 'cocoa_light', n=12)                        # a berry pie
        cyl('Body', (-1.0, 1.25, 0.1), 0.52, 0.04, 'red', n=12)
        for dx in (-0.2, 0.2):
            span('Body', (-1.0 + dx - 0.05, 1.26, -0.4), (-1.0 + dx + 0.05, 1.31, 0.6), 'cocoa_light')
        note = ('a two-tier dessert trolley of birch on log posts and iron wheels: a Yule log cake with snow icing '
                'and holly, a gingerbread house with a snowy roof, a pink jelly; a berry pie and plates below')
    else:
        lathe('Body', [(0.75, 2.57), (0.75, 2.95), (0.55, 2.95), (0.55, 3.28), (0.0, 3.28)], 'lotus', n=12,
              base=(-1.2, 0, 0))
        lathe('Body', [(0.77, 2.85), (0.77, 2.93)], 'linen', n=12, base=(-1.2, 0, 0))
        lotus((-1.2, 3.28, 0), s=0.4)
        lathe('Body', [(0.5, 2.57), (0.35, 3.05), (0.0, 3.12)], 'frog', n=10, base=(0.55, 0, 0.3))
        cyl('Body', (1.6, 2.57, -0.3), 0.45, 0.03, 'white', n=10)
        for k in range(4):
            a = 2 * math.pi * k / 4
            sphere('Body', (1.6 + 0.22 * math.cos(a), 2.69, -0.3 + 0.22 * math.sin(a)), (0.14, 0.09, 0.14), 'linen',
                   n=6, rings=3)
        cyl('Body', (-1.0, 1.07, 0.1), 0.62, 0.18, 'cypress_light', n=12)                      # a pecan pie
        cyl('Body', (-1.0, 1.25, 0.1), 0.52, 0.04, 'mud', n=12)
        for k in range(5):
            a = 2 * math.pi * k / 5
            sphere('Body', (-1.0 + 0.3 * math.cos(a), 1.3, 0.1 + 0.3 * math.sin(a)), (0.08, 0.03, 0.05),
                   'cypress_dark', n=6, rings=3)
        note = ('a two-tier dessert trolley of cypress on brass posts and wooden wheels: a lotus-pink layer cake '
                'with a lotus on top, a frog-green jelly, beignets; a pecan pie and plates below')
    for k in range(4):
        cyl('Body', (1.2, 1.07 + 0.06 * k, 0.0), 0.5 - 0.01 * k, 0.05, 'white', n=10)
    stand()
    done(note)


# --- Games --------------------------------------------------------------------------------------------

def ff_pool_table():
    kfurn('PoolTable')
    for x in (-3.4, 0.0, 3.4):
        for z in (-1.9, 1.9):
            cyl('Body', (x, 0, z), 0.24, 1.25, 'log', n=8)
    span('Body', (-3.9, 1.2, -2.4), (3.9, 2.3, 2.4), 'log_dark', bevel=0.1)
    span('Body', (-3.5, 2.28, -2.0), (3.5, 2.42, 2.0), 'felt')
    for (x0, z0, x1, z1) in ((-3.9, -2.4, 3.9, -2.0), (-3.9, 2.0, 3.9, 2.4), (-3.9, -2.0, -3.5, 2.0),
                             (3.5, -2.0, 3.9, 2.0)):
        span('Body', (x0, 2.3, z0), (x1, 2.6, z1), 'birch', bevel=0.04)
    for x in (-3.42, 0.0, 3.42):
        for z in (-1.92, 1.92):
            cyl('Body', (x, 2.42, z), 0.22, 0.02, 'black', n=8)
    for x in (-2.6, -1.3, 1.3, 2.6):        # the rails' sights in aurora colours
        for z in (-2.2, 2.2):
            box('Body', (0, 0, 0), (0.12, 0.03, 0.12), 'teal' if abs(x) > 2 else 'violet', m=at((x, 2.6, z), ry=45))
    for x, z, colr in ((-1.6, 0.2, 'white'), (1.2, -0.5, 'red'), (1.5, 0.3, 'yellow'), (1.8, -0.1, 'navy'),
                       (2.1, 0.5, 'orange')):
        sphere('Body', (x, 2.6, z), 0.18, colr, n=8, rings=4)
    stand()
    done('a pool table: dark log body on six log legs, deep green felt, birch rails with aurora-coloured sights, '
         'black pockets, five balls')


def bs_pool_table():
    kfurn('PoolTable')
    for x in (-3.4, 0.0, 3.4):
        for z in (-1.9, 1.9):
            leg('bs', x, z, 1.25, r=0.2)
    span('Body', (-3.9, 1.2, -2.4), (3.9, 2.3, 2.4), 'cypress', bevel=0.1)
    span('Body', (-3.5, 2.28, -2.0), (3.5, 2.42, 2.0), 'felt')
    for (x0, z0, x1, z1) in ((-3.9, -2.4, 3.9, -2.0), (-3.9, 2.0, 3.9, 2.4), (-3.9, -2.0, -3.5, 2.0),
                             (3.5, -2.0, 3.9, 2.0)):
        span('Body', (x0, 2.3, z0), (x1, 2.6, z1), 'drift', bevel=0.04)
    for x in (-3.42, 0.0, 3.42):
        for z in (-1.92, 1.92):
            cyl('Body', (x, 2.42, z), 0.22, 0.02, 'black', n=8)
    for x in (-2.6, -1.3, 1.3, 2.6):
        for z in (-2.2, 2.2):
            cyl('Body', (x, 2.595, z), 0.07, 0.02, 'lotus', n=6)
    moss_fringe(-3.9, -1.6, 2.42, -2.4, depth=0.35)
    moss_fringe(1.9, 3.5, 2.42, -2.4, depth=0.3, col='moss_light')
    for x, z, colr in ((-1.6, 0.2, 'white'), (1.2, -0.5, 'lotus'), (1.5, 0.3, 'lotus_heart'), (1.8, -0.1, 'frog'),
                       (2.1, 0.5, 'velvet')):
        sphere('Body', (x, 2.6, z), 0.18, colr, n=8, rings=4)
    stand()
    done('a pool table: a cypress body on six root legs, moss hanging off its apron, green felt, weathered rails '
         'with lotus-pink sights, black pockets, five balls')


def card_table(kit):
    kfurn('CardTable')
    if kit == 'ff':
        lathe('Body', [(1.0, 0), (1.0, 0.12), (0.4, 0.3), (0.3, 0.6), (0.26, 2.1), (0.45, 2.3)], 'log', n=10)
        cyl('Body', (0, 2.3, 0), 2.45, 0.24, 'birch', n=16)
        lathe('Body', [(2.45, 2.36), (2.49, 2.36), (2.49, 2.47), (2.45, 2.47)], 'teal', n=16, closed=True)
        cards, chips = ('cream', 'cream', 'red', 'cream'), ('red', 'yellow', 'navy')
        note = ('a round card table: deep green felt in a birch rim with an aurora-teal band, on a log pedestal; '
                'cards dealt, stacks of chips')
    else:
        lathe('Body', [(1.05, 0), (0.8, 0.12), (0.45, 0.35), (0.28, 0.8), (0.25, 2.1), (0.45, 2.3)], 'cypress_dark',
              n=10)
        cyl('Body', (0, 2.3, 0), 2.45, 0.24, 'cypress', n=16)
        cards, chips = ('linen', 'linen', 'velvet', 'linen'), ('lotus', 'brass', 'frog')
        jar_lantern('Glow_Warm_1', -1.5, 2.6, 1.25, r=0.13, h=0.16)
        note = ('a round card table: green felt in a cypress rim on a root pedestal; cards dealt, stacks of chips, '
                'a firefly jar')
    cyl('Body', (0, 2.44, 0), 2.2, 0.16, 'felt', n=16)
    for k, (x, z, ang) in enumerate(((-1.0, -0.9, 20), (0.9, -1.1, -15), (1.1, 0.8, 35), (-0.9, 1.0, -30))):
        box('Body', (0, 0, 0), (0.55, 0.02 + 0.005 * k, 0.8), cards[k], m=at((x, 2.611 + 0.006 * k, z), ry=ang))
    for (x, z), colr in zip(((0.2, 0.0), (0.55, 0.15), (-0.3, 0.3)), chips):
        cyl('Body', (x, 2.6, z), 0.18, 0.2, colr, n=8)
    stand()
    done(note)


def darts_board(kit):
    kfurn('DartsBoard')
    if kit == 'ff':
        cyl('Body', (0, 0, 0), 1.1, 0.24, 'log_dark', n=20, m=at((0, 4.4, 1.1), rx=-90))       # a log slice
        cyl('Body', (0, 0, 0), 1.0, 0.24, 'birch', n=20, m=at((0, 4.4, 1.08), rx=-90))
        rings = ('black', 'cream', 'red', 'pine', 'red')
        flights = ('teal', 'violet', 'mint')
        sphere('Body', (0, 5.48, 0.97), (0.5, 0.12, 0.15), 'snow', n=8, rings=3)
        frame, slate, chalk = 'log_dark', 'night', 'snow'
        note = ('a darts board on a log slice with snow on it, hung on the wall: black, cream, red and green rings, '
                'three darts with aurora-coloured flights, a chalk scoreboard under it')
    else:
        cyl('Body', (0, 0, 0), 1.1, 0.24, 'rattan_dark', n=20, m=at((0, 4.4, 1.1), rx=-90))   # a woven backer
        cyl('Body', (0, 0, 0), 1.0, 0.24, 'rattan', n=20, m=at((0, 4.4, 1.08), rx=-90))
        rings = ('black', 'linen', 'velvet', 'lily', 'velvet')
        flights = ('lotus', 'lotus', 'lotus_heart')
        for a, ln in ((115, 0.42), (135, 0.5), (155, 0.36)):            # Spanish moss off its rim
            c = (1.0 * math.cos(math.radians(a)), 4.4 + 1.0 * math.sin(math.radians(a)) - 0.2, 0.84)
            sphere('Body', c, (0.13, ln, 0.05), 'moss_light', n=6, rings=4)
        frame, slate, chalk = 'cypress_dark', 'stone_dark', 'linen'
        note = ('a darts board on a round woven rattan backer hung on the wall, Spanish moss off its rim: black, '
                'linen, red and green rings, three darts with lotus flights, a slate scoreboard under it')
    for k, (r, colr) in enumerate(zip((0.8, 0.66, 0.47, 0.28, 0.1), rings)):
        back, front = 0.86 + 0.01 * k, 0.8 - 0.02 * k
        cyl('Body', (0, 0, 0), r, back - front, colr, n=20 if k < 2 else 12, m=at((0, 4.4, back), rx=-90))
    for (x, y), fl in zip(((0.18, 4.55), (-0.25, 4.3), (0.05, 4.05)), flights):
        cyl('Body', (0, 0, 0), 0.03, 0.45, 'iron' if kit == 'ff' else 'brass', n=4, m=at((x, y, 0.74), rx=-90))
        box('Body', (x, y, 0.3), (0.22, 0.22, 0.12), fl)
    span('Body', (-0.75, 2.2, 0.98), (0.75, 3.1, 1.1), frame, bevel=0.03)
    span('Body', (-0.62, 2.32, 0.94), (0.62, 2.98, 1.0), slate)
    for k in range(3):
        span('Body', (-0.5, 2.5 + 0.17 * k, 0.92), (-0.1 + 0.12 * k, 2.56 + 0.17 * k, 0.95), chalk)
    stand()
    done(note)


def arcade_cabinet(kit):
    kfurn('ArcadeCabinet')
    prof = [(-0.8, 0.0), (1.0, 0.0), (1.0, 5.5), (-0.7, 5.5), (-0.7, 4.6), (-0.35, 4.45), (-0.6, 3.2),
            (-1.05, 3.0), (-1.05, 2.75), (-0.8, 2.6)]
    side, body = ('navy', 'log_dark') if kit == 'ff' else ('lily_dark', 'cypress')
    prism('Body', prof, -1.05, 1.05, {'left': side, 'right': side, 'rest': body}, plane='zy')
    d = Vector((0, 1.25, 0.25)).normalized()
    nrm = Vector((0, d.z, -d.y))
    c = Vector((0, 3.825, -0.475)) + nrm * 0.02
    ang = math.degrees(math.atan2(0.25, 1.25))
    box('Glow_Cold_1', (0, 0, 0), (1.5, 1.05, 0.03), 'frostglow' if kit == 'ff' else 'moonglow', m=at(tuple(c), rx=ang))
    y = lambda z: 3.0 + (z + 1.05) * 0.2 / 0.45     # noqa: E731  the control panel's slope
    if kit == 'ff':
        span('Glow_Magic_1', (-0.85, 4.75, -0.74), (0.85, 5.35, -0.71), 'aurora')            # the marquee
        span('Body', (-1.0, 5.5, -0.75), (1.0, 5.62, 1.0), 'iron', bevel=0.03)
        snow_cap(-0.98, 0.98, -0.72, 0.98, 5.62)
        for sx in (-1, 1):
            aurora_side(sx, -0.3, 0.9, 3.7, h=0.45)
        stick, buttons, door = 'red', ('yellow', 'teal', 'pink'), 'iron'
        note = ('an arcade cabinet: navy sides painted with aurora waves, a dark log front, a frost-blue glowing '
                'screen, an aurora-glowing marquee, snow on top, a joystick and three buttons, a coin door')
    else:
        span('Glow_Warm_1', (-0.85, 4.75, -0.74), (0.85, 5.35, -0.71), 'firefly')
        span('Body', (-1.0, 5.5, -0.75), (1.0, 5.62, 1.0), 'copper', bevel=0.03)
        moss_fringe(-1.0, -0.1, 5.58, -0.75, depth=0.3)
        for sx in (-1, 1):
            cyl('Body', (0, 0, 0), 0.45, 0.03, 'lily', n=10, m=at((1.04 * sx, 1.6, 0.2), rz=-90 * sx))
            cyl('Body', (0, 0, 0), 0.14, 0.05, 'lotus', n=8, m=at((1.04 * sx, 1.6, 0.2), rz=-90 * sx))
        stick, buttons, door = 'lotus', ('lotus_heart', 'frog', 'lavender'), 'copper'
        note = ('an arcade cabinet: cypress with lily-green sides and a lily pad on each, a moon-glow screen, a '
                'firefly-glowing marquee with moss hanging over it, a joystick and three buttons, a copper coin door')
    cyl('Body', (-0.5, y(-0.85) - 0.03, -0.85), 0.05, 0.32, 'black', n=6)
    sphere('Body', (-0.5, y(-0.85) + 0.33, -0.85), 0.11, stick, n=6, rings=4)
    for x, colr in zip((0.1, 0.38, 0.66), buttons):
        cyl('Body', (x, y(-0.8) - 0.03, -0.8), 0.09, 0.08, colr, n=8)
    span('Body', (-0.4, 1.2, -0.84), (0.4, 2.1, -0.78), door, bevel=0.03)
    for x in (-0.15, 0.15):
        span('Body', (x - 0.05, 1.7, -0.86), (x + 0.05, 1.9, -0.83), 'yellow' if kit == 'ff' else 'lotus_heart')
    stand()
    done(note)


def ping_pong_table(kit):
    kfurn('PingPongTable')
    R = ROLE[kit]
    for x in (-2.8, 2.8):
        for z in (-1.9, 1.9):
            leg(kit, x, z, 2.24, r=0.11)
        span('Body', (x - 0.08, 0.5, -1.82), (x + 0.08, 0.66, 1.82), R['dark'])
    span('Body', (-3.9, 2.2, -2.3), (3.9, 2.42, 2.3), R['dark'])
    top, net, bats, handle = (('navy', 'frost', ('red', 'teal'), 'birch') if kit == 'ff'
                              else ('water_deep', 'reed', ('lotus', 'lily'), 'cypress_light'))
    span('Body', (-4.0, 2.42, -2.4), (4.0, 2.6, 2.4), top, bevel=0.02)
    for (x0, z0, x1, z1) in ((-4.0, -2.4, 4.0, -2.3), (-4.0, 2.3, 4.0, 2.4), (-4.0, -2.3, -3.9, 2.3),
                             (3.9, -2.3, 4.0, 2.3), (-3.9, -0.04, 3.9, 0.04)):
        span('Body', (x0, 2.6, z0), (x1, 2.62, z1), R['line'])
    span('Body', (-0.03, 2.59, -2.48), (0.03, 2.95, 2.48), net)
    span('Body', (-0.05, 2.95, -2.48), (0.05, 3.0, 2.48), R['line'])
    for z in (-1, 1):
        za, zb = sorted((2.36 * z, 2.56 * z))
        span('Body', (-0.08, 2.3, za), (0.08, 3.05, zb), R['metal'])
    for (x, z), colr in zip(((-2.5, 1.0), (2.6, -1.2)), bats):
        cyl('Body', (x, 2.6, z), 0.38, 0.04, colr, n=10)
        span('Body', (x + 0.3, 2.6, z - 0.07), (x + 0.85, 2.68, z + 0.07), handle)
    sphere('Body', (1.0, 2.7, 0.5), 0.1, 'white', n=6, rings=4)
    stand()
    done({'ff': 'a ping-pong table: a navy top with white lines on log legs, a frosted net with a white band between '
                'iron posts, a red and a teal bat, a ball',
          'bs': 'a ping-pong table: a deep water-green top with linen lines on cypress root legs, a reed-green net '
                'between brass posts, a lotus and a lily bat, a ball'}[kit])


def board_game_shelf(kit):
    kfurn('BoardGameShelf')
    R = ROLE[kit]
    back = 1.1
    span('Body', (-2.3, 0, 0.95), (2.3, 5.3, back), R['dark'] if kit == 'ff' else 'rattan_dark')
    for x in (-1, 1):
        xa, xb = sorted((2.3 * x, 2.5 * x))
        span('Body', (xa, 0, -0.9), (xb, 5.3, back), R['wood'], bevel=0.03)
    span('Body', (-2.58, 5.3, -1.0), (2.58, 5.55, back), R['mid'], bevel=0.05)
    span('Body', (-2.3, 0, -0.9), (2.3, 0.3, 0.95), R['wood'])
    shelves = (0.3, 1.6, 2.9, 4.2)
    for yy in shelves[1:]:
        span('Body', (-2.3, yy - 0.12, -0.85), (2.3, yy, 0.95), R['wood2'])
    if kit == 'ff':
        cols = ('red', 'navy', 'teal', 'yellow', 'violet', 'pine', 'orange', 'pink')
        lids = ('cream', 'snow', 'white', 'cream', 'snow', 'gold', 'cream', 'ink')
    else:
        cols = ('lotus', 'lily_dark', 'sage', 'copper', 'velvet', 'lavender', 'frog', 'moonstone_dark')
        lids = ('linen', 'white', 'chamomile', 'linen', 'lotus_light', 'white', 'linen', 'plum')
    k = [0]

    def game_box(lo, hi, axis):
        """A game box; its lid the top 40 % (axis 1, lying flat) or the front 40 % (axis 2, stood up showing it),
        0.02 wider all round, in another colour (the Manor's shelf)."""
        c, lid = cols[k[0] % len(cols)], lids[k[0] % len(lids)]
        k[0] += 1
        if axis == 1:
            cut = hi[1] - 0.4 * (hi[1] - lo[1])
            span('Body', lo, (hi[0], cut, hi[2]), c)
            span('Body', (lo[0] - 0.02, cut - 0.01, lo[2] - 0.02), (hi[0] + 0.02, hi[1], hi[2] + 0.02), lid)
        else:
            cut = lo[2] + 0.4 * (hi[2] - lo[2])
            span('Body', (lo[0], lo[1], cut), hi, c)
            span('Body', (lo[0] - 0.02, lo[1] - 0.02, lo[2]), (hi[0] + 0.02, hi[1] + 0.02, cut + 0.01), lid)
        return c

    for si, y0 in enumerate(shelves):
        for bi, xc in enumerate((-1.5, 0.0, 1.5)):
            if (si + bi) % 2 == 0:      # a flat stack of two, a title strip on each lid's front
                yy = y0
                for j in range(2):
                    w, dd, h = 1.3 - 0.12 * ((j + si) % 2), 1.3 - 0.12 * (j % 2), 0.4 - 0.04 * ((j + bi) % 2)
                    dx = 0.05 * (1 - 2 * (j % 2))
                    c = game_box((xc - w / 2 + dx, yy, -dd / 2 + 0.1), (xc + w / 2 + dx, yy + h, dd / 2 + 0.1), 1)
                    span('Body', (xc + dx - 0.3, yy + h - 0.12, -dd / 2 + 0.06),
                         (xc + dx + 0.3, yy + h - 0.05, -dd / 2 + 0.1), c)
                    yy += h
            else:                       # one stood up showing its lid's picture, another behind it
                game_box((xc - 0.6, y0, 0.2), (xc + 0.55, y0 + 1.0, 0.45), 2)
                face = game_box((xc - 0.62, y0, -0.45), (xc + 0.62, y0 + 0.95, -0.2), 2)
                cyl('Body', (0, 0, 0), 0.26, 0.04, R['plate'] if face not in ('white', 'linen') else 'black', n=6,
                    m=at((xc - 0.18, y0 + 0.5, -0.45), rx=-90))
                box('Body', (0, 0, 0), (0.36, 0.36, 0.05), 'ink' if kit == 'ff' else 'plum',
                    m=at((xc + 0.36, y0 + 0.5, -0.475), rz=45))
    if kit == 'ff':
        aurora(-2.4, 2.4, 5.33, -1.0, h=0.19, waves=2.0)
        snow_cap(-2.56, 2.56, -0.98, 1.08, 5.55)
        note = ('a shelf of board games on the wall: birch sides, a log cornice with an aurora band and snow on it; '
                'wide game boxes with lids of another colour, stacked flat and stood up showing their pictures')
    else:
        moss_fringe(-2.58, -0.9, 5.5, -1.0, depth=0.45)
        moss_fringe(1.2, 2.58, 5.5, -1.0, depth=0.35, col='moss_light')
        note = ('a shelf of board games on the wall: cypress sides, a woven rattan back, moss hanging off the '
                'cornice; wide game boxes with lids of another colour, stacked flat and stood up showing their '
                'pictures')
    stand()
    done(note)


# --- Lounge -------------------------------------------------------------------------------------------

def chess_table(kit):
    kfurn('ChessTable')
    if kit == 'ff':
        lathe('Body', [(0.8, 0), (0.8, 0.1), (0.32, 0.3), (0.24, 2.2), (0.42, 2.45)], 'log', n=10)
        top, base, dark, men = 'birch', 'birch_shade', 'log_dark', ('snow', 'navy')
        note = 'a chess table: a birch and dark-log board on a log pedestal, snow-white and navy men, a game under way'
    else:
        lathe('Body', [(0.85, 0), (0.6, 0.12), (0.35, 0.35), (0.22, 0.9), (0.2, 2.2), (0.42, 2.45)], 'cypress_dark',
              n=10)
        top, base, dark, men = 'drift', 'linen', 'cypress_dark', ('linen', 'moss_dark')
        note = ('a chess table: a linen and dark-cypress board on a weathered top and root pedestal, linen and moss '
                'men, a game under way')
    span('Body', (-1.05, 2.45, -1.05), (1.05, 2.62, 1.05), top, bevel=0.04)
    span('Body', (-0.85, 2.62, -0.85), (0.85, 2.66, 0.85), base)
    for i in range(8):
        for j in range(8):
            if (i + j) % 2:
                x0, z0 = -0.8 + 0.2 * i, -0.8 + 0.2 * j
                span('Body', (x0, 2.66, z0), (x0 + 0.2, 2.68, z0 + 0.2), dark)
    for x, z, side, tall in ((-0.5, -0.7, 0, 0), (0.1, -0.5, 0, 0), (0.3, -0.7, 0, 1),
                             (-0.3, 0.5, 1, 0), (0.5, 0.3, 1, 0), (-0.1, 0.7, 1, 1)):
        h = 0.45 if tall else 0.28
        lathe('Body', [(0.08, 2.67), (0.08, 2.71), (0.04, 2.71 + h * 0.5), (0.06, 2.71 + h * 0.75),
                       (0.0, 2.71 + h)], men[side], n=8, base=(x, 0, z))
        sphere('Body', (x, 2.71 + h + 0.05, z), 0.07, men[side], n=6, rings=3)
    stand()
    done(note)


def ff_coffee_table():
    kfurn('CoffeeTable')
    for x in (-1.7, 1.7):
        cyl('Body', (x, 0, 0), 0.62, 1.2, 'log', n=12)                        # two log rounds
    span('Body', (-2.5, 1.18, -1.0), (2.5, 1.48, 1.0), 'birch', bevel=0.06)
    for z0, z1 in ((-1.04, -0.97), (0.97, 1.04)):                            # its bark edges
        span('Body', (-2.46, 1.21, z0), (2.46, 1.45, z1), 'log_dark', bevel=0.02)
    lathe('Body', [(0.3, 1.48), (0.36, 1.62), (0.34, 1.82), (0.2, 1.92), (0.22, 1.97), (0.0, 2.0)], 'red', n=10,
          base=(0.4, 0, 0.1))                                                # a cocoa pot
    seg('Body', (0.7, 1.68, 0.1), (0.98, 1.88, 0.1), 0.05, 'red', n=5)
    span('Body', (-0.08, 1.62, 0.06), (0.06, 1.86, 0.14), 'red')
    _ff_mug('Body', (-0.5, 1.48, -0.45), r=0.17, h=0.26, col='cream', band='red')
    _ff_mug('Body', (1.4, 1.48, -0.5), r=0.17, h=0.26, col='red')
    cyl('Body', (-1.4, 1.48, 0.3), 0.42, 0.03, 'white', n=10)               # gingerbread stars
    for x, z in ((-1.55, 0.2), (-1.25, 0.42), (-1.35, 0.12)):
        star(x, 1.51 + (0.04 if (x, z) == (-1.35, 0.12) else 0.0), z, 0.17, 'cocoa_light')
    span('Body', (-0.75, 1.48, 0.45), (0.0, 1.6, 0.88), 'navy', bevel=0.02)
    stand()
    done('a low coffee table: a thick birch slab with bark edges on two log rounds, a red cocoa pot, two mugs, a '
         'plate of gingerbread stars, a book')


def bs_coffee_table():
    kfurn('CoffeeTable')
    for x in (-1.75, 1.75):
        leg('bs', x, 0, 1.22, r=0.38)
    n = 16                                  # a live-edge cypress slab
    xs = [-2.5 + 5.0 * i / n for i in range(n + 1)]
    front = [(x, -0.95 + 0.05 * math.sin(3.1 * x) + 0.02 * math.cos(7.3 * x)) for x in xs]
    back_ = [(x, 0.95 - 0.05 * math.sin(2.7 * x + 1.0) - 0.02 * math.cos(6.1 * x)) for x in reversed(xs)]
    prism('Body', front + back_, 1.2, 1.48, {'top': 'drift', 'rest': 'cypress'}, plane='xz')
    lathe('Body', [(0.22, 1.48), (0.34, 1.6), (0.32, 1.78), (0.14, 1.86), (0.16, 1.9), (0.0, 1.96)], 'copper', n=10,
          base=(0.4, 0, 0.1))                                                # a copper teapot
    seg('Body', (0.68, 1.62, 0.1), (0.95, 1.82, 0.1), 0.05, 'copper', n=5)
    span('Body', (-0.02, 1.58, 0.06), (0.1, 1.82, 0.14), 'cypress_dark')
    cup_on_saucer(-0.5, 1.48, -0.45, 'linen', h=0.2, r=0.14)
    cup_on_saucer(1.4, 1.48, -0.5, 'lotus', h=0.2, r=0.14)
    lathe('Body', [(0.16, 1.48), (0.32, 1.6), (0.0, 1.6)], 'stone_light', n=10, base=(-1.4, 0, 0.3))
    lotus((-1.4, 1.6, 0.3), s=0.6)
    frog((1.9, 1.48, 0.5), ang=200, s=0.6)
    stand()
    done('a low coffee table: a live-edge cypress slab, weathered on top, on two root stumps: a copper teapot, two '
         'cups on saucers, a lotus in a stone bowl, a frog on the corner')


# --- Bathroom -----------------------------------------------------------------------------------------

def ff_bathtub():
    kfurn('Bathtub')
    # A wooden tub of birch staves (alternate faces a shade darker) in two iron hoops, its floor at 0.75, water to
    # 1.3; a rolled plaid towel across the head end (-X), an iron pump at the foot.
    n = 20
    out, inn = oval(2.5, 1.0, n), oval(2.25, 0.8, n)
    ring_prism('Body', out, inn, 0.0, 2.0, ['birch', 'birch_shade'], 'birch_shade', 'birch')
    for y0 in (0.3, 1.5):
        ring_prism('Body', oval(2.535, 1.035, n), out, y0, y0 + 0.16, 'iron', 'iron', 'iron')
    prism('Body', oval(2.23, 0.78, n), 0.0, 0.75, 'log', plane='xz')
    prism('Body', oval(2.22, 0.77, n), 1.25, 1.3, 'ice_deep', plane='xz')
    for x, z, r in ((0.6, 0.3, 0.14), (1.1, -0.35, 0.11), (-1.3, 0.35, 0.12)):
        sphere('Body', (x, 1.288, z), (r, 0.012, r), 'snow', n=6, rings=3)
    cyl('Body', (0, 0, 0), 0.15, 1.4, 'red', n=8, m=at((-2.375, 2.15, -0.7), rx=90))
    for z in (-0.35, 0.35):
        cyl('Body', (0, 0, 0), 0.16, 0.1, 'cream', n=8, m=at((-2.375, 2.15, z - 0.05), rx=90))
    cyl('Body', (2.38, 1.9, 0), 0.09, 0.4, 'iron', n=6)
    cyl('Body', (0, 0, 0), 0.06, 0.45, 'iron', n=6, m=at((2.38, 2.22, 0), rz=90))
    use((-0.3, 0.75, 0.0), (1, 0, 0), 'Lie', liquid=(1.25, 1.3), waive=WAIVE_TUB)
    done('a wooden tub of birch staves in two iron hoops, water to the middle with a little foam, a rolled red '
         'plaid towel across its head end, an iron pump at its foot')


def bs_bathtub():
    kfurn('Bathtub')
    sc = (2.3, 0.95)
    lathe('Body', [(0.0, 0.5), (0.8, 0.5), (1.05, 1.9), (1.12, 2.0), (0.96, 2.0), (0.9, 0.75), (0.0, 0.75)],
          'copper', n=16, scale=sc)
    cyl('Body', (0, 1.25, 0), 0.885, 0.05, 'water', n=16, scale=sc)
    lily_pad((0.7, 1.3, 0.25), 0.24, 0.02, 'lily', notch=30)
    lily_pad((1.35, 1.3, -0.25), 0.18, 0.02, 'lily_dark', notch=200)
    for x, z, ang in ((-1.25, -0.42, 0), (1.25, -0.42, 0), (-1.25, 0.42, 180), (1.25, 0.42, 180)):
        frog((x, 0, z), ang=ang, s=1.08)                                     # four frogs for feet
    cyl('Body', (2.38, 1.95, 0), 0.1, 0.32, 'brass', n=6)
    cyl('Body', (0, 0, 0), 0.07, 0.5, 'brass', n=6, m=at((2.38, 2.2, 0), rz=90))
    frog((-2.39, 2.0, 0.0), ang=90, s=0.45)                                  # and one on the rim
    use((-0.3, 0.75, 0.0), (1, 0, 0), 'Lie', liquid=(1.25, 1.32), waive=WAIVE_TUB)
    done('a copper soaking tub standing on four frogs, still water with two lily pads, a brass tap at its foot, a '
         'little frog on the rim')


def washstand(kit):
    kfurn('Washstand')
    R = ROLE[kit]
    span('Body', (-1.0, 0, -0.85), (1.0, 2.7, 0.9), R['wood'], bevel=0.06)
    for x0, x1 in ((-0.85, -0.03), (0.03, 0.85)):
        panel(kit, x0, x1, 0.3, 2.4, -0.85)
    for x in (-0.15, 0.15):
        knob(kit, x, 1.4, -0.92, r=0.06)
    span('Body', (-1.08, 2.7, -0.95), (1.08, 2.85, 1.0), 'stone_light' if kit == 'ff' else 'drift', bevel=0.03)
    lathe('Body', [(0.5, 2.78), (0.72, 3.0), (0.78, 3.08), (0.68, 3.08), (0.0, 2.92)],
          'white' if kit == 'ff' else 'stone_light', n=12, base=(0, 0, -0.2))
    metal = 'iron' if kit == 'ff' else 'copper'
    cyl('Body', (0, 2.85, 0.62), 0.07, 0.52, metal, n=6)
    span('Body', (-0.05, 3.3, 0.25), (0.05, 3.4, 0.68), metal)
    if kit == 'ff':
        span('Body', (0.06, 3.32, 0.58), (0.42, 3.38, 0.66), 'iron')           # the pump's handle
        frame = [(-0.95, 2.85), (0.95, 2.85)] + list(reversed(round_arch_points(-0.95, 0.95, 4.3, 5.25, n=8)))
        glass = [(-0.78, 3.0), (0.78, 3.0)] + list(reversed(round_arch_points(-0.78, 0.78, 4.25, 5.05, n=8)))
        prism('Body', frame, 0.75, 0.95, 'log_dark', plane='xy')
        prism('Body', glass, 0.71, 0.77, 'frost', plane='xy')
        sphere('Body', (0, 5.25, 0.85), (0.42, 0.1, 0.13), 'snow', n=8, rings=3)
        note = ('a washstand: a white basin in a stone top on a birch cabinet with carved snowflake doors, an iron '
                'pump tap, a round-topped frosted mirror in a dark log frame with snow on it')
    else:
        for x in (-0.25, 0.25):
            sphere('Body', (x, 2.92, 0.62), 0.08, 'copper', n=6, rings=3)
        prism('Body', ellipse(0, 4.0, 0.9, 1.15), 0.75, 0.95, 'cypress_dark', plane='xy')
        prism('Body', ellipse(0, 4.0, 0.76, 1.0), 0.71, 0.77, 'moonstone', plane='xy')
        for k, (x, ln) in enumerate(((-0.55, 0.42), (-0.2, 0.3), (0.35, 0.5))):     # moss over the frame's top
            yy = 4.0 + 1.15 * math.sqrt(max(0.0, 1 - (x / 0.9) ** 2))
            sphere('Body', (x, yy - ln * 0.6, 0.71), (0.13, ln, 0.05), 'moss_light' if k % 2 else 'moss', n=6,
                   rings=4)
        lotus((0.72, 2.85, -0.62), s=0.45)
        note = ('a washstand: a stone basin in a weathered top on a cypress cabinet with rattan doors, a copper tap, '
                'an oval moonstone mirror in a dark cypress frame with moss over it, a lotus')
    stand()
    done(note)


def toilet(kit):
    kfurn('Toilet')
    # The Manor's pedestal toilet on an oval 2.0 x 1.2 (was 1.5) centred 0.21 further back, so the bowl, seat and
    # lid end at z -0.74, where the seated figure's shins hang (0.4 ahead of Use); the lid at 1.72 is the seat.
    zc, sz = -0.14, 0.6
    lathe('Body', [(0.62, 0.0), (0.62, 0.08), (0.5, 0.2), (0.44, 0.6), (0.7, 1.0), (0.93, 1.3), (0.97, 1.43),
                   (0.0, 1.46)], 'white', n=16, base=(0, 0, zc), scale=(1.0, sz))
    prism('Body', [(-0.05, 0.0), (0.5, 0.0), (1.0, 0.95), (1.0, 1.44), (-0.05, 1.44)], -0.42, 0.42, 'white',
          plane='zy')
    seat_c, lid_c = ('birch', 'birch_shade') if kit == 'ff' else ('cypress', 'cypress_light')
    lathe('Body', [(0.62, 1.42), (1.0, 1.42), (1.0, 1.53), (0.62, 1.53)], seat_c, n=16, base=(0, 0, zc),
          scale=(1.0, sz), closed=True)
    lathe('Body', [(0.95, 1.53), (0.98, 1.58), (0.95, 1.67), (0.85, 1.71), (0.0, 1.72)], lid_c, n=16,
          base=(0, 0, zc), scale=(1.0, sz))
    if kit == 'ff':
        span('Body', (-0.8, 1.42, 0.5), (0.8, 3.2, 1.05), 'log', bevel=0.05)
        span('Body', (-0.86, 3.2, 0.45), (0.86, 3.36, 1.1), 'birch', bevel=0.03)
        panel('ff', -0.6, 0.6, 1.85, 2.95, 0.5)
        span('Body', (0.45, 2.98, 0.37), (0.75, 3.06, 0.46), 'iron')
        sphere('Body', (0.75, 3.02, 0.36), 0.07, 'iron', n=6, rings=3)
        note = ("a white pedestal toilet with a birch seat and closed lid at 1.72, a log-clad cistern on the bowl's "
                "back with a carved snowflake panel and an iron lever")
    else:
        span('Body', (-0.8, 1.42, 0.5), (0.8, 3.2, 1.05), 'cypress', bevel=0.05)
        span('Body', (-0.86, 3.2, 0.45), (0.86, 3.36, 1.1), 'drift', bevel=0.03)
        panel('bs', -0.65, 0.65, 1.7, 3.05, 0.5)
        span('Body', (0.45, 2.98, 0.37), (0.75, 3.06, 0.43), 'brass')
        sphere('Body', (0.75, 3.02, 0.36), 0.07, 'brass', n=6, rings=3)
        cyl('Body', (-0.4, 3.36, 0.72), 0.2, 0.22, 'stone', n=8)            # a fern on the cistern
        for k in range(5):
            a = 2 * math.pi * k / 5
            sphere('Body', (0, 0, 0), (0.07, 0.045, 0.2), 'herb', n=6, rings=3,
                   m=at((-0.4, 3.6, 0.72), ry=math.degrees(a)) @ Matrix.Translation((0, 0, 0.1))
                   @ Matrix.Rotation(math.radians(-25), 4, 'X'))
        note = ("a white pedestal toilet with a cypress seat and closed lid at 1.72, a cypress cistern on the bowl's "
                "back with a woven rattan front, a brass lever, a fern in a stone pot on top")
    K.seat(-1.0, 1.0, -0.74, 0.46, 1.72)
    use((0, 1.72, -0.35), (0, 0, -1), 'Sit')
    done(note)


# --- Garden -------------------------------------------------------------------------------------------

def garden_bench(kit):
    kfurn('GardenBench')
    # The seat's front at z -0.62 (the shins hang from 0.4 ahead of Use, z -0.65), three planks a hair apart, the
    # back from z 0.58 (0.3 behind the torso); Use at the middle (the Manor's: the arms clear the bench's arms).
    if kit == 'ff':
        for sx in (-1, 1):
            cyl('Body', (2.45 * sx, 0, -0.45), 0.11, 2.4, 'log', n=8)
            cyl('Body', (2.45 * sx, 0, 0.78), 0.13, 3.3, 'log', n=8)
            cyl('Body', (0, 0, 0), 0.1, 1.45, 'log_dark', n=8, m=at((2.45 * sx, 2.42, -0.62), rx=90))
            sphere('Body', (2.45 * sx, 3.34, 0.78), (0.15, 0.08, 0.15), 'snow', n=6, rings=3)
        planks = 'birch'
        for yy in (2.25, 2.95):
            cyl('Body', (0, 0, 0), 0.2, 4.9, 'log', n=8, m=at((-2.45, yy, 0.78), rz=-90))
        sphere('Body', (0, 3.13, 0.78), (2.1, 0.07, 0.15), 'snow', n=10, rings=3)     # snow along the top rail
        note = ('a garden bench of logs for two: a birch plank seat, log arms, two half-log back rails with snow '
                'lying on the top one and on the posts')
    else:
        for sx in (-1, 1):
            leg('bs', 2.42 * sx, -0.45, 2.4, r=0.08)
            leg('bs', 2.4 * sx, 0.78, 3.3, r=0.1)
            xa, xb = sorted((2.34 * sx, 2.56 * sx))
            span('Body', (xa, 2.36, -0.65), (xb, 2.5, 0.9), 'cypress_light', bevel=0.03)
        planks = 'drift'
        for i in range(5):
            ya, yb = 2.0 + 0.2 * i, 2.0 + 0.2 * (i + 1)
            span('Body', (-2.3, ya, 0.7 - 0.02 * (i % 2)), (2.3, yb, 0.86), 'rattan' if i % 2 else 'rattan_dark')
        span('Body', (-2.5, 3.0, 0.62), (2.5, 3.16, 0.92), 'cypress_light', bevel=0.03)
        moss_fringe(-2.4, -0.8, 3.12, 0.62, depth=0.3)
        sphere('Body', (-1.4, 3.16, 0.77), (0.6, 0.1, 0.15), 'moss', n=8, rings=3)
        frog((1.6, 3.16, 0.77), ang=0, s=0.5)
        note = ('a garden bench for two: weathered planks on cypress root legs, a woven rattan back with moss over '
                'its top rail and a frog sitting on it')
    for z0, z1 in ((-0.62, -0.13), (-0.11, 0.39), (0.41, 0.92)):
        span('Body', (-2.55, 1.5, z0), (2.55, 1.75, z1), planks, bevel=0.03)
    K.seat(-2.4, 2.4, -0.62, 0.58, 1.75, people=2)
    use((0, 1.75, -0.25), (0, 0, -1), 'Sit')
    done(note)


# --- The tables the main script reads -----------------------------------------------------------------

def floor_lamp(kit):
    kfurn('FloorLamp')
    if kit == 'ff':
        lathe('Body', [(0.0, 0.0), (0.75, 0.0), (0.75, 0.14), (0.4, 0.26), (0.0, 0.3)], 'log_dark', n=10)
        cyl('Body', (0, 0.25, 0), 0.1, 3.8, 'birch', n=8)
        for k, (yy, a) in enumerate(((0.9, 20), (1.7, 140), (2.5, 260), (3.3, 60))):     # the birch's dark marks
            box('Body', (0, 0, 0), (0.12, 0.04, 0.04), 'log_dark', m=at((0, yy, 0), ry=a) @ Matrix.Translation((0, 0, -0.085)))
        sphere('Glow_Warm_1', (0, 4.05, 0), (0.22, 0.26, 0.22), 'lamp', n=8, rings=4)
        lathe('Body', [(0.98, 4.15), (0.62, 5.25), (0.0, 5.28)], 'cream', n=12)
        lathe('Body', [(0.97, 4.08), (1.04, 4.08), (1.04, 4.2), (0.97, 4.2)], 'red', n=12, closed=True)
        lathe('Body', [(0.89, 4.36), (0.93, 4.36), (0.91, 4.44), (0.87, 4.44)], 'teal', n=12, closed=True)
        lathe('Body', [(0.0, 5.26), (0.12, 5.32), (0.1, 5.45), (0.0, 5.52)], 'cocoa_dark', n=6)
        note = ('a standing lamp: a birch post with its dark marks on a log-slice foot, a cream shade with a red hem '
                'and an aurora-teal band, a pine-cone finial, the bulb glowing')
    else:
        boulder((0, 0, 0), 0.7, 0.45, 'stone', n=8)
        pts = [(0, 0.3, 0), (0.12, 1.4, 0.06), (0.04, 2.6, -0.05), (-0.1, 3.7, 0.02), (0, 4.82, 0)]
        for a, b in zip(pts, pts[1:]):
            seg('Body', a, b, 0.09, 'cypress_dark', n=6)
        for p in pts[1:-1]:
            sphere('Body', p, 0.095, 'cypress_dark', n=6, rings=3)
        lathe('Body', [(1.0, 4.78), (0.96, 4.9), (0.45, 5.25), (0.0, 5.34)], {'bottom': 'lily_dark', 'rest': 'lily'},
              n=14)
        firefly_lantern('Glow_Warm_1', (0.55, 4.8, 0.0), h=0.36, r=0.14)
        cattails(0.62, -0.45, y=0.0, k=2, tall=1.5)
        note = ('a standing lamp: a crooked cypress branch on a smooth stone, a lily-pad shade, a firefly jar hanging '
                'under it, cattails at its foot')
    stand()
    done(note)


def every_furniture(kit):
    """{id: build} for the 23 location-0 pieces in the kit's style ('ff' Frostfang Lodge, 'bs' Bayou Spa)."""
    own = {'ff': {'Nightstand': ff_nightstand, 'Wardrobe': ff_wardrobe, 'WritingDesk': ff_writing_desk,
                  'DiningTable': ff_dining_table, 'BreakfastBuffet': ff_buffet, 'BarStool': ff_bar_stool,
                  'PoolTable': ff_pool_table, 'Bathtub': ff_bathtub, 'CoffeeTable': ff_coffee_table},
           'bs': {'Nightstand': bs_nightstand, 'Wardrobe': bs_wardrobe, 'WritingDesk': bs_writing_desk,
                  'DiningTable': bs_dining_table, 'BreakfastBuffet': bs_buffet, 'BarStool': bs_bar_stool,
                  'PoolTable': bs_pool_table, 'Bathtub': bs_bathtub, 'CoffeeTable': bs_coffee_table}}[kit]
    shared = {'CardTable': card_table, 'FloorLamp': floor_lamp, 'DiningChair': dining_chair, 'SaladBar': salad_bar,
              'CoffeeUrn': coffee_urn, 'DessertTrolley': dessert_trolley, 'DartsBoard': darts_board,
              'ArcadeCabinet': arcade_cabinet, 'PingPongTable': ping_pong_table, 'BoardGameShelf': board_game_shelf,
              'ChessTable': chess_table, 'Washstand': washstand, 'Toilet': toilet, 'GardenBench': garden_bench}
    out = dict(own)
    out.update({i: (lambda fn=fn: fn(kit)) for i, fn in shared.items()})
    assert set(out) == set(EVERY_IDS), sorted(set(EVERY_IDS) ^ set(out))
    return out


# --- Review (Workbench on light grey: Studio is running, no EEVEE or Cycles) --------------------------

def review_top(out, fbx, names, manifest, per_row=4):
    """Every piece straight from above on its 3-stud squares, Use marked red with its facing (the phone's
    top-down camera)."""
    by = sorted(names, key=lambda n: (-manifest[n]['root']['size'][2], n))
    rows = [by[i:i + per_row] for i in range(0, len(by), per_row)]
    shots = []
    for ri, row in enumerate(rows):
        clear()
        x = 0.0
        depth = max(manifest[n]['root']['size'][2] for n in row)
        for n in row:
            size = manifest[n]['root']['size']
            cx = x + size[0] / 2
            place(fbx, n, (cx, 0, 0))
            _squares(cx, size)
            u = manifest[n]['attachments'].get('Use')
            if u:
                p = Vector(u['pos']) + Vector((cx, 0, 0))
                p.y = 7.2       # above everything, so it shows from the top
                _REV['_block']('use', p - Vector((0.18, 0.0, 0.18)), p + Vector((0.18, 0.05, 0.18)), (230, 40, 40))
                q = p + Vector(u['look']) * 0.6
                _REV['_block']('use', Vector(map(min, p, q)) - Vector((0.06, 0, 0.06)),
                               Vector(map(max, p, q)) + Vector((0.06, 0.04, 0.06)), (230, 40, 40))
            x += size[0] + 2.0
        _REV['_person'](Vector((x + 1.0, 0, 0)), 0.0)
        shots.append(render(out / f'top_{ri + 1}.png', (0.0, 1.0, -0.02), (1200, 520),
                            (-1, 0, -depth / 2 - 2.0), (x + 3, 7.4, depth / 2 + 1.0), scale=1.02))
    return _REV['_compose']([[p] for p in shots], out / 'top_sheet.png')


def review_every_sitting(out, fbx, names, manifest, style):
    """Every Sit piece with the 5-stud person sitting on its Use (sit_blocks, the figure sit_faults checks):
    from the side as a section just outside the torso, from the front and from three-quarters; the kit's bar
    stool at a counter (the Lodge's at its Cocoa Bar; the Spa has none, so the Manor's Snack Counter)."""
    stool = manifest['Furniture_BarStool']['attachments']['Use']
    if style == 'frostfang_lodge':
        cfbx, counter = fbx, 'Furniture_CocoaBar'
    else:
        cfbx, counter = K.ROOT / 'blender' / 'rooms' / 'haunted_manor' / 'fbx', 'Furniture_SnackCounter'
    scenes = []

    def at_counter():
        place(cfbx, counter, (0, 0, 0))
        place(fbx, 'Furniture_BarStool', (0, 0, -3.0), 180)
        sp = Vector(stool['pos'])
        _sitting((-sp.x, sp.y, -sp.z - 3.0), (0, 0, 1))
        return (-4.6, 0, -4.6), (4.6, 6.2, 1.6), None
    scenes.append(('BarStool_at_' + counter[len('Furniture_'):], at_counter))
    for n in names:
        r = manifest[n]
        if r.get('furniture', {}).get('pose') != 'Sit':
            continue

        def one(n=n, r=r):
            place(fbx, n, (0, 0, 0))
            u = r['attachments']['Use']
            _sitting(u['pos'], u['look'])
            sz = r['root']['size']
            return ((-sz[0] / 2 - 0.3, 0, -sz[2] / 2 - 2.0), (sz[0] / 2 + 0.3, 5.8, sz[2] / 2 + 0.3),
                    (u['pos'][0] - 1.01, 0, 0))
        scenes.append((n[len('Furniture_'):], one))
    rows = []
    for name, build in scenes:
        row = []
        for view, d in (('side', (-1.0, 0.0, 0.0)), ('front', (0.0, 0.25, -1.0)), ('three_quarter', (-0.7, 0.45, -1.0))):
            clear()
            lo, hi, cut = build()
            _REV['_block']('floor', (lo[0] - 1, -0.3, lo[2] - 1), (hi[0] + 1, -0.02, hi[2] + 1), (150, 150, 156))
            row.append(render(out / f'sitting_{name}_{view}.png', d, (600, 600), lo, hi,
                              cut=cut if view == 'side' else None))
        rows.append(row)
    return _REV['_compose'](rows, out / 'sitting_sheet.png')


def review_every(out, fbx, names, manifest, style):
    """The location-0 pieces' own sheets (review/every/): on their squares beside the 5-stud person, from above,
    the floor-level elevations, the Bathtub with the person lying in it, every Sit piece with the person seated."""
    sub = out / 'every'
    return (review_furniture(sub, fbx, names, manifest), review_top(sub, fbx, names, manifest),
            review_elevations(sub, fbx, names, manifest), review_lying(sub, fbx, names, manifest),
            review_every_sitting(sub, fbx, names, manifest, style))
