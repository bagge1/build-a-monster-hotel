"""The Cinema's two pieces for Haunted Manor's kit (GDD A.13.2, the Cinema row).

    Furniture_FilmScreen    3 x 1 squares, `Wall`: a film screen in a dark-wood pointed-arch frame on a low
                            stage, crimson curtains drawn aside; the Cinema's key piece; no visitors' spots
    Furniture_CinemaSeat    3 x 1 squares, `Floor`: a row of three seats, their tops at 1.7, armrests between;
                            Use_1..Use_3 `Watch`

The contract is MODELS.md, "Furniture" and "Activity furniture: visitors' spots", as for the Bar
(tools/build_activity_bar.py, whose definitions this runs: bfurn, spot, spots_check, sdone, loft, patch_fixup,
the review helpers, and through it tools/build_built_rooms.py's kit). The convention for `Watch`: a seat faces
the piece's front, -Z (every Sit in the kits looks -Z), so each spot's LookVector is -Z and the player turns the
row's front toward the screen; spots_check holds a Watch spot to -Z, to a declared seat (rule 6) and to the seated
5-stud person (sit_blocks) clear of the body.

A sibling of build_activity_bar.py, not an extension of it: the Bar's pieces stay as they were reviewed, and its
spot validator (spots_check, which this script's Watch spots added Sit and Watch to) stays one function both
use. Its own set, blender/rooms/haunted_manor_cinema/; the models belong in HotelKit.HauntedManor.

    blender -b -t 4 --python-exit-code 1 -P tools/build_activity_cinema.py [-- grey] [-- nopreview]

`-- grey` writes the grey silhouettes (three options a piece, ids _A/_B/_C, not for import) to
blender/rooms/haunted_manor_cinema/silhouettes/. Otherwise the chosen two are built in the Manor's palette;
review/ gets Workbench sheets only (Studio is running).
"""
import ast
import json
import math
from pathlib import Path

_AB = Path(__file__).resolve().parent / 'build_activity_bar.py'
_tree = ast.parse(_AB.read_text(encoding='utf8'))
_tree.body = [n for n in _tree.body if not isinstance(n, ast.Try)]          # its main() call
NS = {'__file__': str(_AB), '__name__': 'build_activity_bar'}
exec(compile(_tree, str(_AB), 'exec'), NS)
globals().update({k: v for k, v in NS.items() if not k.startswith('__')})
# From here, besides build_built_rooms.py's names (K, bpy, Vector, span, prism, cyl, sphere, lathe, at, ...):
# PENDING, bfurn, spot, spots_check, sdone, loft, arc, _label, patch_fixup, sit_blocks, _sitting.

SET = 'rooms/haunted_manor_cinema'
GREY = 'grey' in K.ARGS

# The Pieces rows these need (the code branch adds them). bfurn reads the same dict object.
PENDING.update({
    'FilmScreen': {'w': 3, 'd': 1, 'layer': 'Wall', 'height': 6.95, 'location': 0, 'keyFor': ['Cinema']},
    'CinemaSeat': {'w': 3, 'd': 1, 'layer': 'Floor', 'height': 4.05, 'location': 0, 'keyFor': []},
})

SEAT_TOP = 1.7                  # rule 6: 1.5 to 2.0
SEAT_X = (-2.75, 0.0, 2.75)     # the three sitters: 2.75 apart, so each seat is 2 wide between armrests
SEAT_Z = -0.25                  # the Watch point: the torso's back (z +0.25) clear of the back's face at 0.42
ARMS = ((-4.1, -3.75), (-1.75, -1.0), (1.0, 1.75), (3.75, 4.1))     # the armrests' x spans
ARM_TOP = 2.4                   # under the seated figure's arms (SEAT_TOP + 0.75)


def no_spots(id_):
    """A piece guests do not visit (the screen): neither Use nor Use_<n>."""
    p = bfurn(id_)
    p.checks.remove(spots_check)
    p.spots = {}
    return p


def sdone2(note):
    rec = sdone(note)
    if not K.P.spots:
        rec['furniture']['spots'] = {}
    return rec


def watch_spots():
    """A seat (rule 6) and a Watch spot for each sitter, facing the row's front (-Z)."""
    for k, x in enumerate(SEAT_X):
        K.seat(x - 1.0, x + 1.0, -0.88, 0.34, SEAT_TOP)
        spot(k + 1, (x, SEAT_TOP, SEAT_Z), (0, 0, -1), 'Watch')


def arches(x0, x1, n, y0, spring, apex, k=4):
    """One outline (x, y), counter-clockwise: a rectangle x0..x1 from y0 with n pointed arches along its top."""
    pts = [(x0, y0), (x1, y0)]
    w = (x1 - x0) / n
    for i in range(n - 1, -1, -1):
        a = K.arch_points(x0 + w * i, x0 + w * (i + 1), spring, apex, n=k)
        for p in reversed(a):
            if (abs(p[0] - pts[-1][0]) > 1e-6 or abs(p[1] - pts[-1][1]) > 1e-6):
                pts.append(p)
    return pts


# --- The seat rows ------------------------------------------------------------------------------------

def row_a(c):
    """A: three theatre seats, each its own upholstered back under a pointed arch; armrests between, all on a
    plinth. `c`: base, seat, frame, arm, cap."""
    span('Body', (-4.08, 0, -0.7), (4.08, 0.25, 1.0), c['frame'])
    for x in SEAT_X:
        span('Body', (x - 0.9, 0.24, -0.66), (x + 0.9, 1.37, 0.55), c['base'])
        span('Body', (x - 0.99, 1.33, -0.88), (x + 0.99, SEAT_TOP, 0.44), c['seat'], bevel=0.1)
        prism('Body', lifted(gothic(x - 0.92, x + 0.92, 1.75, 2.3), 1.6), 0.42, 0.76, c['seat'], plane='xy')
    # The shell runs down to the plinth (blind review 2026-10-26: open below it, the back read unfinished).
    prism('Body', arches(-4.1, 4.1, 3, 0.24, 3.2, 4.05), 0.74, 0.98, c['frame'], plane='xy')
    if c.get('panel'):      # the back, which the camera behind the player sees most: a pointed panel a seat
        for x in SEAT_X:    # (the second review: a flat slab read as a wall), the Bar counter's language
            prism('Body', lifted(gothic(x - 0.95, x + 0.95, 1.9, 2.65), 0.6), 0.97, 1.0, c['panel'], plane='xy')
    for xa, xb in ARMS:
        span('Body', (xa + 0.03, 0.24, -0.8), (xb - 0.03, ARM_TOP - 0.18, 0.76), c['arm'])
        span('Body', (xa, ARM_TOP - 0.2, -0.98), (xb, ARM_TOP, 0.6), c['cap'], bevel=0.05)
    watch_spots()


def row_b(c):
    """B: a pew: one bench cushion, one tall back panel with three pointed panels, end standards rising behind."""
    span('Body', (-4.1, 0, -0.7), (4.1, 0.25, 1.0), c['frame'])
    span('Body', (-3.72, 0.24, -0.66), (3.72, 1.37, 0.55), c['base'])
    span('Body', (-3.74, 1.33, -0.88), (3.74, SEAT_TOP, 0.44), c['seat'], bevel=0.08)
    span('Body', (-3.75, 1.3, 0.6), (3.75, 3.7, 1.0), c['frame'])
    span('Body', (-3.85, 3.7, 0.55), (3.85, 3.95, 1.05), c['cap'])
    for x in SEAT_X:
        prism('Body', lifted(gothic(x - 0.8, x + 0.8, 1.4, 2.0), 1.6), 0.42, 0.62, c['seat'], plane='xy')
    for xa, xb in ARMS:
        if xa in (-4.1, 3.75):         # the end standards: an armrest in front, a pointed post behind
            span('Body', (xa, 0.24, -0.98), (xb, ARM_TOP, 0.5), c['arm'])
            prism('Body', [(xa, 0.24), (xb, 0.24), (xb, 4.0), ((xa + xb) / 2, 4.35), (xa, 4.0)], 0.5, 1.02,
                  c['arm'], plane='xy')
        else:                           # the dividers, on the bench
            span('Body', (xa, SEAT_TOP - 0.02, -0.75), (xb, ARM_TOP - 0.1, 0.5), c['arm'], bevel=0.05)
    watch_spots()


def row_c(c):
    """C: a low velvet sofa row: a continuous rolled back, rolled end arms, a cushion per seat, low dividers."""
    span('Body', (-4.1, 0, -0.7), (4.1, 0.25, 1.0), c['frame'])
    span('Body', (-4.05, 0.24, -0.66), (4.05, 1.35, 1.0), c['base'], bevel=0.12)
    for x in SEAT_X:
        span('Body', (x - 0.99, 1.3, -0.88), (x + 0.99, SEAT_TOP, 0.44), c['seat'], bevel=0.15)
        span('Body', (x - 1.05, 1.3, 0.45), (x + 1.05, 3.0, 0.9), c['seat'], bevel=0.2)
    cyl('Body', (0, 0, 0), 0.28, 8.2, c['frame'], n=10, m=at((-4.1, 3.0, 0.72), rz=-90))
    for xa, xb in ARMS:
        top = ARM_TOP if xa in (-4.1, 3.75) else ARM_TOP - 0.15
        span('Body', (xa, 0.24, -0.9), (xb, top, 0.9), c['arm'], bevel=0.12)
    watch_spots()


# --- The screens --------------------------------------------------------------------------------------

def screen_a(c, sconces=None):
    """A: a pointed-arch proscenium on a low stage: two posts, the arch's head, a back panel to the wall, the
    screen in a black masking border, curtains drawn aside to the posts. `c`: stage, skirt, frame, panel,
    border, screen, curtain."""
    deck = 0.6
    span('Body', (-4.07, 0, -1.07), (4.07, deck - 0.1, 1.04), c['skirt'])
    span('Body', (-4.1, deck - 0.12, -1.1), (4.1, deck, 1.06), c['stage'], bevel=0.04)
    for sx in (-1, 1):
        x0, x1 = sorted((sx * 3.52, sx * 4.06))
        span('Body', (x0, deck - 0.02, 0.24), (x1, 5.9, 1.06), c['frame'])
    # The head: a pointed-arch band over the opening (its outer edge a pointed arch too: a straight gable read
    # as a house's roof, 2026-10-26), a pyramid pinnacle on each post.
    inner = K.arch_points(-3.5, 3.5, 5.75, 6.35, n=5)
    outer = list(reversed(K.arch_points(-3.5, 3.5, 6.2, 6.95, n=5)))
    head = [(-4.1, 5.75)] + inner + [(4.1, 5.75), (4.1, 6.2)] + outer + [(-4.1, 6.2)]
    prism('Body', head, 0.2, 1.08, c['frame'], plane='xy')
    for sx in (-1, 1):
        cyl('Body', (sx * 3.79, 6.18, 0.65), 0.3, 0.77, c['frame'], n=4, r_top=0.0)
    prism('Body', [(-3.52, deck - 0.03), (3.52, deck - 0.03), (3.52, 6.15), (0.0, 6.6), (-3.52, 6.15)], 1.0, 1.1,
          c['panel'], plane='xy')
    # The screen raised to 2.1..5.6 (blind review 2026-10-26: a second row saw the first row's heads over it), a
    # dark-wood dado under its border.
    span('Body', (-3.45, 1.9, 0.86), (3.45, 5.8, 1.01), c['border'])
    span('Body', (-3.2, 2.1, 0.84), (3.2, 5.6, 0.87), c['screen'])
    span('Body', (-3.5, deck - 0.03, 0.9), (3.5, 1.9, 1.02), c['dado'])
    # A swagged pelmet under the arch, over the screen's top (the third review: the backing showed there as a
    # dark crescent, a hole), its top hidden in the head.
    swags = [(-3.5 + 7.0 * (k + i / 6) / 3, 5.78 - 0.16 * math.sin(math.pi * i / 6)) for k in range(3)
             for i in range(6)] + [(3.5, 5.78)]
    prism('Body', swags + [(3.5, 6.15), (0.0, 6.6), (-3.5, 6.15)], 0.8, 0.85, c['curtain'], plane='xy')
    for sx in (-1, 1):
        def half(w):
            xs = [-3.52 + w * i / 6 for i in range(7)]
            front = [(x, 0.45 - 0.07 * (1 - math.cos(math.pi * 2 * i / 3))) for i, x in enumerate(xs)]
            pts = front + [(xs[-1], 0.8), (-3.52, 0.8)]
            return [(-x if sx > 0 else x, z) for x, z in pts]
        # Narrower than first built (the fourth review: they covered the screen's corners).
        loft('Body', [(deck - 0.02, half(0.55)), (2.6, half(0.3)), (4.0, half(0.5)), (6.12, half(0.9))],
             c['curtain'])
    if sconces:
        for sx in (-1, 1):          # a candle sconce on each post's front, between the curtain and the head
            x = sx * 3.8
            span('Body', (x - 0.08, 4.35, -0.05), (x + 0.08, 4.47, 0.26), sconces['metal'])
            candle(sconces['glow'], x, 4.47, 0.08, h=0.4, r=0.08, cup=sconces['metal'])


def screen_b(c):
    """B: the screen hung on the wall in a heavy frame, a pelmet over it, floor-length curtains either side."""
    span('Body', (-3.9, 1.6, 0.75), (3.9, 6.2, 1.1), c['frame'])
    span('Body', (-3.5, 2.0, 0.71), (3.5, 5.8, 0.76), c['screen'])
    span('Body', (-4.1, 6.2, 0.2), (4.1, 6.95, 1.1), c['curtain'])
    for sx in (-1, 1):
        x0, x1 = sorted((sx * 3.3, sx * 4.1))
        span('Body', (x0, 0, 0.3), (x1, 6.22, 0.78), c['curtain'])


def screen_c(c):
    """C: a roll-down screen on a stand: two posts on feet, a roller case with finials, a weighted hem."""
    for sx in (-1, 1):
        x = sx * 3.85
        span('Body', (x - 0.25, 0, -1.0), (x + 0.25, 0.18, 1.1), c['frame'])
        cyl('Body', (x, 0.18, 0.85), 0.13, 6.1, c['frame'], n=8)
        sphere('Body', (x, 6.55, 0.85), (0.2, 0.35, 0.2), c['frame'], n=8, rings=4)
    cyl('Body', (0, 0, 0), 0.24, 7.5, c['border'], n=10, m=at((-3.75, 6.1, 0.85), rz=-90))
    span('Body', (-3.6, 1.5, 0.78), (3.6, 6.05, 0.84), c['screen'])
    cyl('Body', (0, 0, 0), 0.08, 7.3, c['border'], n=6, m=at((-3.65, 1.45, 0.81), rz=-90))
    span('Body', (-3.75, 0.8, 0.8), (3.75, 0.95, 0.9), c['frame'])


GC = {'base': 'stone_dark', 'seat': 'grey', 'frame': 'stone_dark', 'arm': 'stone', 'cap': 'stone',
      'stage': 'stone', 'skirt': 'stone_dark', 'panel': 'stone_dark', 'border': 'black', 'screen': 'white',
      'curtain': 'grey', 'dado': 'stone_dark'}


def sil(fn, id_, note, spots=True):
    (bfurn if spots else no_spots)(id_)
    fn(GC)
    sdone2(note)


SILHOUETTES = [
    lambda: sil(screen_a, 'FilmScreen_A', 'A: a pointed-arch proscenium on a low stage, curtains drawn aside', False),
    lambda: sil(screen_b, 'FilmScreen_B', 'B: a framed screen hung on the wall, a pelmet, floor-length curtains',
                False),
    lambda: sil(screen_c, 'FilmScreen_C', 'C: a roll-down screen on a two-post stand with a roller case', False),
    lambda: sil(row_a, 'CinemaSeat_A', 'A: three theatre seats, each back a pointed arch, armrests between'),
    lambda: sil(row_b, 'CinemaSeat_B', 'B: a pew: one bench, one tall back with three pointed panels'),
    lambda: sil(row_c, 'CinemaSeat_C', 'C: a low velvet sofa row with a rolled back and rolled arms'),
]


# --- The chosen two, in the Manor's dress -------------------------------------------------------------

def film_screen():
    no_spots('FilmScreen')
    screen_a({'stage': 'wood', 'skirt': 'crimson_dark', 'frame': 'wood_dark', 'panel': 'night', 'border': 'black',
              'screen': 'cream', 'curtain': 'crimson', 'dado': 'wood_dark'}, sconces={'metal': 'gold', 'glow': 'Glow_Warm_1'})
    sdone2('a Haunted Manor film screen: a pale screen in a black border inside a dark-wood pointed-arch '
           'proscenium with two pinnacles on a low stage with a crimson skirt, a dark dado under the screen, '
           'crimson curtains drawn aside, a night-blue '
           'panel behind, a candle sconce on each post')


def cinema_seat():
    bfurn('CinemaSeat')
    row_a({'base': 'crimson_dark', 'seat': 'crimson', 'frame': 'wood_dark', 'arm': 'wood_dark', 'cap': 'wood',
           'panel': 'crimson'})
    sdone2('a Haunted Manor cinema row: three crimson velvet seats at 1.7, each back under a pointed arch on a '
           'dark-wood shell with a crimson pointed panel behind each seat, four dark-wood armrests with lighter '
           'caps, on a plinth')


# --- Review (Workbench on light grey: Studio is running, no EEVEE or Cycles) --------------------------

def turn(v, ang):
    """A piece-frame vector turned `ang` degrees as place() turns the piece (0 or 180 here)."""
    return (v[0], v[1], v[2]) if ang % 360 == 0 else (-v[0], v[1], -v[2])


def people(rec, cx, cz=0.0, ang=0):
    for a, pose in rec['furniture']['spots'].items():
        u = rec['attachments'][a]
        p, look = turn(u['pos'], ang), turn(u['look'], ang)
        if pose in ('Sit', 'Watch'):
            _sitting((cx + p[0], p[1], cz + p[2]), look)
        else:
            _REV['_person'](Vector((cx + p[0], 0, 0)), cz + p[2])


def silhouette_sheet(out, fbx, recs):
    rows = (('FilmScreen_A', 'FilmScreen_B', 'FilmScreen_C'), ('CinemaSeat_A', 'CinemaSeat_B', 'CinemaSeat_C'))

    def lay(row, z0, labels):
        x = 0.0
        for i in row:
            n = f'Furniture_{i}'
            size = recs[n]['root']['size']
            cx = x + size[0] / 2
            place(fbx, n, (cx, 0, z0))
            for a in range(int(round(size[0] / 3))):
                for b in range(int(round(size[2] / 3))):
                    x0, zz = cx - size[0] / 2 + 3 * a, z0 - size[2] / 2 + 3 * b
                    shade = (205, 205, 210) if (a + b) % 2 else (185, 185, 192)
                    _REV['_block']('sq', (x0 + 0.03, -0.06, zz + 0.03), (x0 + 2.97, -0.01, zz + 2.97), shade)
            people(recs[n], cx, z0)
            _REV['_person'](Vector((cx + size[0] / 2 + 2.2, 0, 0)), z0)
            if labels:
                _label(i.split('_')[1], cx, z0 - size[2] / 2 - 3.5)
            x += size[0] + 6.0
        return x
    shots = []
    clear()
    x = max(lay(rows[0], 9.0, True), lay(rows[1], 0.0, True))
    _REV['_block']('floor', (-3, -0.3, -7), (x + 2, -0.07, 12), (150, 150, 156))
    shots.append(render(out / 'silhouettes_game.png', (-0.35, 1.25, -1.0), (1600, 900), (-2, 0, -6), (x, 7.2, 11),
                        scale=1.0))
    for k, row in enumerate(rows):
        clear()
        x = lay(row, 0.0, False)
        shots.append(render(out / f'silhouettes_front_{k + 1}.png', (0.0, 0.05, -1.0), (1600, 420), (-2, -0.3, -5),
                            (x, 7.4, 3), scale=1.02))
    # The rows from the side, a section through the middle seat's near arm (the seated figure against its seat).
    clear()
    for k, i in enumerate(rows[1]):
        n = f'Furniture_{i}'
        place(fbx, n, (0, 0, 9.0 * k))
        people(recs[n], 0.0, 9.0 * k)
    shots.append(render(out / 'silhouettes_seat_side.png', (-1.0, 0.0, 0.0), (1600, 420), (-1, -0.3, -2),
                        (1, 5.2, 9.0 * 2 + 2), scale=1.02, cut=(-1.01, 0, 0)))
    return shots


def cinema_scene(fbx, recs, wall=True):
    """The screen against a wall, two rows turned to face it (their fronts, -Z, toward +Z) with a sitter on every
    spot, a person standing in the aisle."""
    place(fbx, 'Furniture_FilmScreen', (0, 0, 0))
    _squares(0.0, recs['Furniture_FilmScreen']['root']['size'])
    if wall:
        _REV['_block']('wall', (-7, 0, 1.12), (7, 9, 1.5), (196, 186, 200))
    for k, z in enumerate((-6.0, -12.0)):
        place(fbx, 'Furniture_CinemaSeat', (0, 0, z), 180)
        people(recs['Furniture_CinemaSeat'], 0.0, z, 180)
    _REV['_person'](Vector((6.0, 0, 0)), -8.0)
    _REV['_block']('floor', (-8, -0.3, -15), (8, -0.07, 1.5), (150, 150, 156))


def review_final(out, fbx, recs):
    names = ['Furniture_FilmScreen', 'Furniture_CinemaSeat']
    shots = []

    def scene(spots=True):
        clear()
        x = 0.0
        for n in names:
            size = recs[n]['root']['size']
            cx = x + size[0] / 2
            place(fbx, n, (cx, 0, 0))
            _squares(cx, size)
            if spots:
                people(recs[n], cx)
            x += size[0] + 4.0
        _REV['_person'](Vector((x + 0.5, 0, 0)), 0.0)
        _REV['_block']('floor', (-3, -0.3, -6), (x + 4, -0.07, 4), (150, 150, 156))
        return x
    x = scene()
    lo, hi = (-1.5, 0, -3.5), (x + 3, 7.2, 2.5)
    shots.append(render(out / '1_game_camera.png', (-0.45, 1.28, -1.0), (1400, 800), lo, hi, scale=1.02))
    shots.append(render(out / '2_front_three_quarter.png', (-0.7, 0.45, -1.0), (1400, 800), lo, hi, scale=1.02))
    shots.append(render(out / '3_back_three_quarter.png', (0.7, 0.55, 1.0), (1400, 800), lo, hi, scale=1.02))
    x = scene(spots=False)
    shots.append(render(out / '4_front_level.png', (0.0, 0.0, -1.0), (1400, 800), (-1.5, -0.3, -3.5),
                        (x + 3, 7.4, 2.5), scale=1.02))
    shots.append(render(out / '5_top.png', (0.0, 1.0, -0.02), (1400, 800), (-1.5, 0, -3.5), (x + 3, 7.4, 2.5),
                        scale=1.02))
    clear()
    x = 0.0
    for n in names:
        size = recs[n]['root']['size']
        cx = x + size[2] / 2
        place(fbx, n, (cx, 0, 0), 90)
        _squares(cx, size, 90)
        x += size[2] + 3.0
    _REV['_person'](Vector((x + 1.0, 0, 0)), 0.0)
    shots.append(render(out / '6_side_level.png', (0.0, 0.0, -1.0), (1400, 800), (-1.5, -0.3, -5), (x + 3, 7.4, 5),
                        scale=1.02))
    # The row up close with its three sitters; and from the side, cut through the middle seat's near arm.
    clear()
    place(fbx, names[1], (0, 0, 0))
    people(recs[names[1]], 0.0)
    shots.append(render(out / '7_close_seats.png', (-0.55, 0.5, -1.0), (1000, 800), (-4.5, 0, -2.5), (4.5, 5.0, 1.5),
                        scale=1.0))
    _REV['_block']('floor', (-5, -0.3, -3), (5, -0.07, 2), (150, 150, 156))
    shots.append(render(out / '8_seat_section.png', (-1.0, 0.0, 0.0), (800, 700), (-1, -0.3, -2.2), (1, 5.2, 1.5),
                        scale=1.0, cut=(-0.999, 0, 0)))
    clear()
    place(fbx, names[0], (0, 0, 0))
    _REV['_person'](Vector((-2.0, 0.6, 0)), -0.4)           # a person on the stage, before the screen
    shots.append(render(out / '9_close_screen.png', (-0.5, 0.35, -1.0), (1000, 800), (-4.5, 0, -1.5), (4.5, 7.0, 1.5),
                        scale=1.0))
    # In use: the screen on a wall, two rows facing it, from the game's camera and from behind the rows.
    clear()
    cinema_scene(fbx, recs)
    shots.append(render(out / '10_cinema_game_camera.png', (-0.45, 1.28, -1.0), (1400, 900), (-7, 0, -14),
                        (7, 8, 1.5), scale=1.02))
    shots.append(render(out / '11_cinema_from_behind.png', (-0.25, 0.3, -1.0), (1400, 900), (-7, 0, -14), (7, 8, 1.5),
                        scale=1.02))
    return shots


# --- The set ------------------------------------------------------------------------------------------

def main():
    K.use_palette(HM_PALETTE)
    if GREY:
        K.IMPORT_CHECKS = False         # drafts with _A/_B/_C ids, not for import
        K.start_set(SET + '/silhouettes')
        for fn in SILHOUETTES:
            fn()
        recs = {p.name: r for p, r, _ in K.BUILT}
        out = K.ROOT / 'blender' / SET / 'silhouettes'
        (out / 'manifest.json').write_text(json.dumps({'pieces': recs}, indent=1))
        if not K.NOPREVIEW:
            print('SHEETS', silhouette_sheet(out / 'review', out / 'fbx', recs), flush=True)
        return
    K.start_set(SET)
    film_screen()
    cinema_seat()
    built = [p.name for p, _, _ in K.BUILT]
    K.end_set('Haunted Manor: the Cinema\'s film screen and seat row (GDD A.13)', [(built, 3.0, 1.0)], sheet=False)
    out = K.ROOT / 'blender' / SET
    manifest = json.loads((out / 'manifest.json').read_text())
    patch_fixup(out / 'import_fixup.luau', manifest)
    val = json.loads((out / 'validation.json').read_text())
    val['spots'] = {n: {'spots': r['furniture']['spots'],
                        'checked': ('spots_check on the built and the re-imported triangles: Use_<n> from 1 without '
                                    'a gap, a Pose from MODELS.md\'s list, a level LookVector, no two spots on one '
                                    'square; Watch facing the row\'s front (-Z), on a declared seat (rule 6), on its '
                                    'surface with nothing over it for 1.5, the seated 5-stud person (sit_blocks: '
                                    'torso, head, arms, thighs, shins, feet) clear of the body')
                        if r['furniture']['spots'] else 'no visitors\' spots (none wanted: guests watch from the '
                                                        'seats); neither Use nor Use_<n>'}
                    for n, r in manifest['pieces'].items()}
    val['pending_pieces_rows'] = {
        'note': 'Pieces.luau has no rows for these yet (the code branch adds them). The kit\'s Pieces check ran '
                'against these values; the rows must say the same w, d, layer and height (to 0.3).',
        **{f'Furniture_{i}': {k: r[k] for k in ('w', 'd', 'layer', 'height', 'keyFor')} | {'furniture': True}
           for i, r in PENDING.items() if i in ('FilmScreen', 'CinemaSeat')}}
    val['not_validated'] = val.get('not_validated', [])[:1] + [
        'the attachments and each Use_<n> Pose attribute exist only in manifest.json until import_fixup.luau makes '
        'them', 'a visitor walking to a seat and sitting: no walker or animation has run',
        'Pieces.luau rows (pending, above)']
    (out / 'validation.json').write_text(json.dumps(val, indent=1))
    if not K.NOPREVIEW:
        print('SHEETS', review_final(out / 'review', out / 'fbx', manifest['pieces']), flush=True)
    bad = [n for n, r in val['pieces'].items() if not r['ok']]
    print(f'SET {SET}: {built}; validation faults in {bad}', flush=True)
    if bad:
        raise SystemExit(f'VALIDATION FAULTS: {bad}')


try:
    main()
except K.Refused as e:
    print(str(e), flush=True)
    raise SystemExit('REFUSED')
