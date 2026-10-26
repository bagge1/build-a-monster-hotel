"""The Gym's three key pieces for Haunted Manor's kit (GDD A.13.2, the Gym row; A.13.3, the Fitness set).

    Furniture_WeightBench   1 x 2 squares: a plum leather bench on an iron frame, a barbell racked over its head end
                            between two gothic iron uprights; Use_1 `Lift`, placed as `Lie` (on the bench)
    Furniture_Treadmill     1 x 2 squares: an iron deck and belt, hip rails, a console with a lit clock face at the
                            back end; Use_1 `Stand` on the belt, facing the console (+Z)
    Furniture_PunchingBag   1 x 1 squares: a plum leather bag on a chain from an iron stand standing on the floor;
                            Use_1 `Stand` on the square in front, facing it

The contract is MODELS.md, "Furniture" and "Activity furniture: visitors' spots", as for the Bar, the Cinema and the
Pool (tools/build_activity_bar.py, whose definitions this runs: spot, spots_check, sdone, loft, patch_fixup, _label,
and through it tools/build_built_rooms.py's kit). Two branches of the one spot validator were added for these
(purely additive; no other set reaches them): a `Lift` spot is held to the checks of the placement it names
(MODELS.md: "as Lie or Stand would place it"; the bench's is `Lie`: the lying 5-stud person, lie_faults), and a
`Stand` inside the footprint (the treadmill's belt) to stand_on_faults: flat under both feet, the standing person,
arms included, clear of the body.

The rows are on main's Pieces.luau (w, d, layer; the kit's Pieces check runs against them). Its own set,
blender/rooms/haunted_manor_gym/; the models belong in HotelKit.HauntedManor.

    blender -b -t 4 --python-exit-code 1 -P tools/build_activity_gym.py [-- grey] [-- nopreview]

`-- grey` writes the grey silhouettes (three options a piece, ids _A/_B/_C, not for import) to
blender/rooms/haunted_manor_gym/silhouettes/. Otherwise the chosen three are built in the Manor's palette; review/
gets Workbench sheets only (Studio is running).
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

SET = 'rooms/haunted_manor_gym'
GREY = 'grey' in K.ARGS

BENCH_TOP = 1.5                 # the pad's top, where the lifter lies: a seat's 1.5 (rule 6; blind review 1: at 1.3
                                # it read as lying on the floor)
BAR_Y, BAR_Z = 3.58, 1.45       # the racked bar over the head end: over the lying person's reach, its plates
PLATE_R = 0.48                  # clear of the lie check's 1.5 over the pad (their bottom 3.1)
PAD_W, HEAD_W, HEAD_Z = 0.85, 0.6, 1.45     # the pad's half widths: wide under the body, narrow between the
                                # uprights from HEAD_Z (blind review 1: a 1.2 pad vanished under the 2-wide torso)
BELT_TOP = 0.5                  # the treadmill's belt
WALK_Z = -0.5                   # the walker's spot on the belt
STRAP_TOP = 5.12                # the straps' ring over the bag, where the chain hangs from
BAG_Z = -0.3                    # the bag's axis: its front 1.0 forward, 1.5 from the boxer's chest


def gfurn(id_):
    """Begin Furniture_<id_> on its Pieces.luau row (a silhouette _A/_B/_C on its piece's); its spots replace
    `Use` (use_check off, spots_check on)."""
    base = id_.split('_')[0]
    row = dict(ROWS[base])
    ROWS[id_] = row
    K.pieces_decor()
    K._PIECES.setdefault(id_, {k: row[k] for k in ('w', 'd', 'layer', 'height')} | {'always': False})
    p = furn(id_)
    p.checks.remove(use_check)
    p.checks.append(spots_check)
    p.spots = {}
    p.lift = {}
    return p


def lift_spot(n, pos, look, how):
    """A `Lift` spot, placed as `how` (Lie or Stand) would place it (MODELS.md); spots_check holds it to that."""
    spot(n, pos, look, 'Lift')
    K.P.lift[f'Use_{n}'] = how


def gdone(note):
    rec = sdone(note)
    rec['furniture']['pieces_row'] = 'Pieces.luau'
    if K.P.lift:
        rec['furniture']['lift_placed_as'] = dict(K.P.lift)
    return rec


def cone(part, a, b, r, col, n=4):
    a, b = Vector(a), Vector(b)
    d = b - a
    cyl(part, (0, 0, 0), r, d.length, col, n=n, r_top=0.0,
        m=Matrix.Translation(a) @ d.to_track_quat('Y', 'Z').to_matrix().to_4x4())


def rod_x(part, x0, x1, y, z, r, col, n=8):
    cyl(part, (0, 0, 0), r, x1 - x0, col, n=n, m=at((x0, y, z), rz=-90))


def arch_band(x_out, x_in, spring, apex_out, apex_in, z0, z1, col, n=4, part='Body'):
    """A pointed-arch band (x, y) between two arches, extruded z0..z1: its feet at `spring` buried in posts."""
    outer = arch_points(-x_out, x_out, spring, apex_out, n=n)
    inner = arch_points(-x_in, x_in, spring, apex_in, n=n)
    prism(part, outer + list(reversed(inner)), z0, z1, col, plane='xy')


# --- The weight bench ---------------------------------------------------------------------------------

def bench_base(c):
    """The pad on an iron spine, two trestle feet; the head end (+Z) foot doubles as the rack's floor bar."""
    ch = 0.12
    outline = [(PAD_W - ch, -2.55), (PAD_W, -2.55 + ch), (PAD_W, HEAD_Z), (HEAD_W, HEAD_Z), (HEAD_W, 2.55 - ch),
               (HEAD_W - ch, 2.55), (-HEAD_W + ch, 2.55), (-HEAD_W, 2.55 - ch), (-HEAD_W, HEAD_Z), (-PAD_W, HEAD_Z),
               (-PAD_W, -2.55 + ch), (-PAD_W + ch, -2.55)]
    prism('Body', outline, BENCH_TOP - 0.26, BENCH_TOP, c['pad'], plane='xz')
    span('Body', (-0.3, 0.8, -2.25), (0.3, BENCH_TOP - 0.24, 2.25), c['frame'])
    for z in (-1.95, 1.75):
        span('Body', (-0.18, 0.12, z - 0.14), (0.18, 0.82, z + 0.14), c['frame'])
    span('Body', (-0.95, 0.0, -2.15), (0.95, 0.14, -1.75), c['frame'], bevel=0.03)
    span('Body', (-1.06, 0.0, 1.55), (1.06, 0.14, 1.95), c['frame'], bevel=0.03)


def barbell(c, y=BAR_Y, z=BAR_Z):
    """The bar along X over the head end, two plates outside the uprights, collars."""
    rod_x('Body', -1.1, 1.1, y, z, 0.07, c['bar'])
    for sx in (-1, 1):
        x0, x1 = sorted((sx * 0.9, sx * 1.06))
        rod_x('Body', x0, x1, y, z, PLATE_R, c['plate'], n=16)     # round (review 2: 12 sides read as gears)
        x0, x1 = sorted((sx * 0.865, sx * 0.9))
        rod_x('Body', x0, x1, y, z, 0.13, c['collar'], n=8)


def uprights(c, top):
    """Two square iron uprights beside the head, J-hooks on their front faces holding the bar."""
    for sx in (-1, 1):
        x0, x1 = sorted((sx * 0.66, sx * 0.86))
        span('Body', (x0, 0.14, 1.62), (x1, top, 1.86), c['frame'])
        span('Body', (x0 + 0.02, BAR_Y - 0.18, 1.32), (x1 - 0.02, BAR_Y - 0.07, 1.63), c['frame'])     # the hook
        span('Body', (x0 + 0.02, BAR_Y - 0.07, 1.32), (x1 - 0.02, BAR_Y + 0.06, 1.38), c['frame'])     # its lip


def bench_a(c, dress=False):
    """A: a flat bench, the rack at its head end: two uprights joined by a pointed arch over the head, gothic
    finials, the barbell racked on hooks over the lifter's face."""
    bench_base(c)
    # No arch over the bar: two blind reviews read it, behind the bar's line, as the bar bent into a hoop (raised
    # clear of it after the first, still read so in the second). The uprights end in tall gold spires.
    uprights(c, 3.95)
    for sx in (-1, 1):
        span('Body', (sx * 0.76 - 0.13, 3.95, 1.61), (sx * 0.76 + 0.13, 4.03, 1.87), c['finial'])
        cyl('Body', (sx * 0.76, 4.03, 1.74), 0.12, 0.47, c['finial'], n=4, r_top=0.0)
    barbell(c)
    # (Gold studs down the pad's sides went: the second blind review read them as a coffin's dressing.)
    lift_spot(1, (0.0, BENCH_TOP, 0.0), (0, 0, -1), 'Lie')


def bench_b(c, dress=False):
    """B: the bench under a tall gothic arch: the uprights rise into a pointed arch at 5.6 over the head end,
    the bar on hooks at the same height as A's."""
    bench_base(c)
    uprights(c, 4.9)
    arch_band(0.86, 0.66, 4.8, 5.6, 5.3, 1.68, 1.8, c['frame'])
    cone('Body', (0, 5.5, 1.74), (0, 6.1, 1.74), 0.14, c['finial'])
    barbell(c)
    lift_spot(1, (0.0, BENCH_TOP, 0.0), (0, 0, -1), 'Lie')


def bench_c(c, dress=False):
    """C: a flat bench with no rack: a pair of dumbbells on a low iron shelf under the pad."""
    bench_base(c)
    span('Body', (-0.95, 0.45, -0.9), (0.95, 0.55, 0.9), c['frame'])
    for sx in (-1, 1):
        span('Body', (sx * 0.85 - 0.06, 0.14, -0.85), (sx * 0.85 + 0.06, 0.46, 0.85), c['frame'])
        for z in (-0.45, 0.45):
            rod_x('Body', sx * 0.55 - 0.3, sx * 0.55 + 0.3, 0.75, z, 0.06, c['bar'])
            for dx in (-0.3, 0.22):
                rod_x('Body', sx * 0.55 + dx, sx * 0.55 + dx + 0.08, 0.75, z, 0.2, c['plate'], n=10)
    lift_spot(1, (0.0, BENCH_TOP, 0.0), (0, 0, -1), 'Lie')


# --- The treadmill --------------------------------------------------------------------------------------

def deck(c):
    """The deck: side skirts, the belt between them (its top BELT_TOP), a rounded front, a motor hood at the back,
    four claw feet."""
    for sx in (-1, 1):
        x0, x1 = sorted((sx * 0.98, sx * 1.08))
        span('Body', (x0, 0.02, -2.5), (x1, 0.62, 1.6), c['frame'], bevel=0.03)     # to the floor (review 1)
    span('Body', (-0.97, 0.3, -2.4), (0.97, BELT_TOP, 1.58), c['belt'])
    rod_x('Body', -0.96, 0.96, 0.4, -2.4, 0.1, c['belt'])
    span('Body', (-1.1, 0.05, 1.55), (1.1, 0.74, 2.55), c['hood'], bevel=0.08)
    for x in (-0.96, 0.96):      # round and tucked under (blind review 3: they read as loose cubes)
        for z in (-2.35, 2.35):
            sphere('Body', (x, 0.1, z), (0.13, 0.1, 0.13), c['foot'], n=10, rings=4)


def rails(c, front=-0.9, y=2.12):
    """Hip rails from the uprights forward, turned down to the skirts at the front: under the walker's arms
    (2.0 over the belt), beside the legs."""
    for sx in (-1, 1):
        x0, x1 = sorted((sx * 0.97, sx * 1.08))      # clear of the walker's legs (review 1: the grip in them)
        span('Body', (x0, y, front), (x1, y + 0.13, 1.85), c['rail'])
        span('Body', (x0 + 0.01, 0.6, front + 0.01), (x1 - 0.01, y + 0.01, front + 0.13), c['rail'])
        span('Body', (x0 - 0.01, y - 0.02, front - 0.02), (x1 + 0.01, y + 0.15, front + 1.3), c['grip'])   # review 2


def console(c, dress=False):
    """Two uprights from the hood to a console with a pointed-arch top, a clock face toward the walker."""
    for sx in (-1, 1):
        x0, x1 = sorted((sx * 0.84, sx * 1.04))
        span('Body', (x0, 0.78, 1.8), (x1, 3.62, 2.05), c['frame'])
    prism('Body', lifted(gothic(-1.05, 1.05, 0.48, 0.82), 3.58), 1.3, 2.1, c['console'], plane='xy')
    cyl('Body', (0, 0, 0), 0.34, 0.04, c['bezel'], n=12, m=at((0, 3.98, 1.31), rx=-90))
    if dress:
        declare('Glow_Cold_1', False)
        cyl('Glow_Cold_1', (0, 0, 0), 0.28, 0.03, c['dial'], n=12, m=at((0, 3.98, 1.28), rx=-90))
        span('Body', (-0.02, 3.96, 1.235), (0.02, 4.2, 1.255), c['hand'])
        span('Body', (-0.02, 3.96, 1.239), (0.16, 4.0, 1.259), c['hand'])
        sphere('Body', (0, 4.44, 1.7), 0.07, c['bezel'], n=6, rings=3)
    else:
        cyl('Body', (0, 0, 0), 0.28, 0.03, c['dial'], n=12, m=at((0, 3.98, 1.28), rx=-90))


def treadmill_a(c, dress=False):
    """A: the deck, hip rails, two uprights to a console with a pointed-arch top and a clock face."""
    deck(c)
    rails(c)
    console(c, dress)
    # (The crimson arch panels on the skirts went: blind review 1 read them as tail lights.)
    spot(1, (0.0, BELT_TOP, WALK_Z), (0, 0, 1), 'Stand')


def treadmill_b(c, dress=False):
    """B: no rails: the deck and one gothic column on the hood carrying a lectern console."""
    deck(c)
    lathe('Body', [(0.3, 0.8), (0.3, 0.95), (0.16, 1.05), (0.13, 3.3), (0.22, 3.45)], c['frame'], n=8,
          base=(0, 0, 2.0))
    prism('Body', [(1.35, 3.42), (2.3, 3.42), (2.3, 3.7), (1.5, 4.3), (1.25, 4.2)], -0.9, 0.9, c['console'],
          plane='zy')
    spot(1, (0.0, BELT_TOP, WALK_Z), (0, 0, 1), 'Stand')


def treadmill_c(c, dress=False):
    """C: rails, and the uprights rise past the console into a tall pointed arch over the back end."""
    deck(c)
    rails(c)
    for sx in (-1, 1):
        x0, x1 = sorted((sx * 0.84, sx * 1.04))
        span('Body', (x0, 0.78, 1.8), (x1, 5.5, 2.05), c['frame'])
    arch_band(1.04, 0.84, 5.4, 6.7, 6.35, 1.86, 1.99, c['frame'])
    span('Body', (-0.86, 3.5, 1.4), (0.86, 4.2, 2.0), c['console'])
    spot(1, (0.0, BELT_TOP, WALK_Z), (0, 0, 1), 'Stand')


# --- The punching bag -----------------------------------------------------------------------------------

def bag(c, z=BAG_Z, top=4.62, dress=False):
    """The bag: a leather cylinder, rounded ends, two straps, an iron cap and a chain up to `hang`."""
    # 1.4 across (blind review 1: 1.24 with gold bands read as a lantern on a lamp post)
    lathe('Body', [(0.0, 1.6), (0.48, 1.62), (0.66, 1.78), (0.7, 2.1), (0.7, 4.2), (0.66, 4.48), (0.45, top - 0.02),
                   (0.0, top)], c['bag'], n=12, base=(0, 0, z))
    if dress:
        for y in (2.0, 4.12):
            lathe('Body', [(0.68, y), (0.72, y + 0.01), (0.72, y + 0.12), (0.68, y + 0.13)], c['band'], n=12,
                  base=(0, 0, z), closed=True)
    cyl('Body', (0, top - 0.04, z), 0.2, 0.1, c['frame'], n=8)
    # Four straps from the bag's shoulder up to a ring, where the chain hangs (the second blind review: without
    # them the bag read as a canister).
    for k in range(4):
        a = math.pi / 4 + k * math.pi / 2
        seg('Body', (0.5 * math.cos(a), top - 0.2, z + 0.5 * math.sin(a)), (0.05 * math.cos(a), STRAP_TOP, z + 0.05 * math.sin(a)),
            0.035, c['band'], n=4)
    lathe('Body', [(0.06, STRAP_TOP - 0.06), (0.11, STRAP_TOP), (0.06, STRAP_TOP + 0.06), (0.03, STRAP_TOP)], c['chain'],
          n=6, base=(0, 0, z), closed=True)


def chain(c, z, y0, y1, links=3):
    """A chain from the cap (y0) to the hanger (y1): a rod and a few links round it."""
    seg('Body', (0, y0, z), (0, y1, z), 0.035, c['chain'], n=4)
    for k in range(links):
        y = y0 + (y1 - y0) * (k + 0.5) / links
        lathe('Body', [(0.06, y - 0.12), (0.1, y), (0.06, y + 0.12), (0.03, y)], c['chain'], n=6,
              base=(0, 0, z), closed=True)


def bag_a(c, dress=False):
    """A: a gallows stand: a square iron post at the back on a T foot, an arm over the bag with a brace,
    a gothic finial on the post."""
    span('Body', (-1.0, 0.0, 0.72), (1.0, 0.14, 1.08), c['frame'], bevel=0.03)
    span('Body', (-0.12, 0.0, -0.95), (0.12, 0.12, 0.8), c['frame'], bevel=0.03)
    span('Body', (-0.13, 0.12, 0.8), (0.13, 6.12, 1.06), c['frame'])
    span('Body', (-0.1, 5.92, -0.48), (0.1, 6.1, 0.81), c['frame'])
    seg('Body', (0, 4.9, 0.85), (0, 5.95, 0.05), 0.06, c['frame'], n=6)
    cyl('Body', (0, 6.11, 0.93), 0.2, 0.36, c['finial'], n=4, r_top=0.0)
    sphere('Body', (0, 5.97, -0.48), (0.1, 0.1, 0.06), c['finial'], n=6, rings=3)
    bag(c, dress=dress)
    chain(c, BAG_Z, STRAP_TOP + 0.04, 5.93, links=2)
    spot(1, (0.0, 0.0, -4.5 + 1.5), (0, 0, 1), 'Stand')


def bag_b(c, dress=False):
    """B: a pointed-arch frame: two iron posts beside the bag on long feet, the arch over it, the bag on a chain
    from the arch's point."""
    zc = -0.4
    for sx in (-1, 1):
        x0, x1 = sorted((sx * 0.86, sx * 1.06))
        span('Body', (x0 - 0.02, 0.0, -1.05), (x1 + 0.02, 0.14, 1.05), c['frame'], bevel=0.03)
        span('Body', (x0, 0.14, zc - 0.11), (x1, 5.2, zc + 0.11), c['frame'])
    arch_band(1.06, 0.86, 5.1, 6.45, 6.15, zc - 0.08, zc + 0.08, c['frame'])
    bag(c, z=zc, dress=dress)
    chain(c, zc, STRAP_TOP + 0.04, 6.16, links=2)
    spot(1, (0.0, 0.0, -3.0), (0, 0, 1), 'Stand')


def bag_c(c, dress=False):
    """C: a round iron column on a stepped plinth, a shepherd's-crook arm curling over to the bag."""
    zc = 0.62
    cyl('Body', (0, 0, zc), 0.46, 0.18, c['frame'], n=10)
    cyl('Body', (0, 0.18, zc), 0.32, 0.16, c['frame'], n=10)
    cyl('Body', (0, 0.34, zc), 0.12, 5.3, c['frame'], n=8)
    pts = [(0.0, 5.6, zc), (0.0, 6.05, zc - 0.05), (0.0, 6.28, zc - 0.3), (0.0, 6.3, zc - 0.62),
           (0.0, 6.15, zc - 0.88), (0.0, 5.95, BAG_Z)]
    for a, b in zip(pts, pts[1:]):
        seg('Body', a, b, 0.08, c['frame'], n=6)
        sphere('Body', b, 0.08, c['frame'], n=6, rings=3)
    bag(c, dress=dress)
    chain(c, BAG_Z, STRAP_TOP + 0.04, 5.92, links=2)
    spot(1, (0.0, 0.0, -3.0), (0, 0, 1), 'Stand')


GC = {'pad': 'stone', 'frame': 'stone_dark', 'finial': 'stone_dark', 'bar': 'stone_dark', 'plate': 'grey',
      'collar': 'stone', 'belt': 'black', 'hood': 'stone_dark', 'foot': 'stone_dark', 'rail': 'stone_dark',
      'grip': 'stone', 'console': 'grey', 'bezel': 'stone', 'dial': 'white', 'hand': 'black', 'panel': 'grey',
      'bag': 'grey', 'band': 'stone', 'chain': 'stone_dark'}

BENCHES = {'A': bench_a, 'B': bench_b, 'C': bench_c}
TREADMILLS = {'A': treadmill_a, 'B': treadmill_b, 'C': treadmill_c}
BAGS = {'A': bag_a, 'B': bag_b, 'C': bag_c}
NOTES = {'WeightBench_A': 'A: a flat bench, the barbell racked between two uprights joined by a low pointed arch',
         'WeightBench_B': 'B: the bench under a tall pointed arch over its head end, the barbell racked on it',
         'WeightBench_C': 'C: a flat bench with no rack, two dumbbells on a shelf under it',
         'Treadmill_A': 'A: the deck, hip rails, two uprights to a pointed-arch console with a clock face',
         'Treadmill_B': 'B: no rails, one gothic column on the hood carrying a lectern console',
         'Treadmill_C': 'C: hip rails, the uprights rising into a tall pointed arch over the console',
         'PunchingBag_A': 'A: a gallows stand: a post at the back, an arm and a brace, the bag on a chain',
         'PunchingBag_B': 'B: a pointed-arch frame over the bag, the bag on a chain from its point',
         'PunchingBag_C': 'C: a round column on a plinth, a shepherd\'s-crook arm curling over to the bag'}


def sil(kind, k, table):
    gfurn(f'{kind}_{k}')
    table[k](GC)
    gdone(NOTES[f'{kind}_{k}'])


# --- The chosen three, in the Manor's dress -------------------------------------------------------------

HM = {'pad': 'plum', 'frame': 'iron', 'finial': 'gold', 'bar': 'black', 'plate': 'black', 'collar': 'gold',
      'belt': 'black', 'hood': 'iron', 'foot': 'gold', 'rail': 'iron', 'grip': 'plum', 'console': 'wood_dark',
      'bezel': 'gold', 'dial': 'moonglow', 'hand': 'black', 'panel': 'crimson', 'bag': 'plum', 'band': 'black',
      'chain': 'iron'}


def weight_bench():
    gfurn('WeightBench')
    bench_a(HM, dress=True)
    gdone('a Haunted Manor weight bench: a plum leather pad (narrow between the uprights) on an iron spine and '
          'trestle feet; at its head end two iron uprights ending in gold spires, a black barbell with round plates '
          'and gold collars racked on their hooks over the lifter\'s face')


def treadmill():
    gfurn('Treadmill')
    treadmill_a(HM, dress=True)
    gdone('a Haunted Manor treadmill: a black belt between iron skirts on gold claw feet, '
          'iron hip rails with plum grips, an iron motor hood; two iron uprights to a dark-wood '
          'pointed-arch console with a gold-rimmed clock face lit moon-blue')


def punching_bag():
    gfurn('PunchingBag')
    bag_a(HM, dress=True)
    gdone('a Haunted Manor punching bag: a plum leather bag with two black bands, four straps to a ring and an iron chain from a '
          'gallows stand: an iron post on a T foot, its arm and brace, a gold finial')


# --- Review (Workbench on light grey: Studio is running, no EEVEE or Cycles) --------------------------

def people(rec, cx, cz=0.0):
    """A person on every spot: lying on a Lift placed as Lie, standing on the belt, standing in front."""
    lift = rec['furniture'].get('lift_placed_as', {})
    for a, pose in rec['furniture']['spots'].items():
        u = rec['attachments'][a]
        p = (cx + u['pos'][0], u['pos'][1], cz + u['pos'][2])
        if pose == 'Lie' or lift.get(a) == 'Lie':
            _lying(p, u['look'])
        else:
            _REV['_person'](Vector((p[0], p[1], 0)), p[2])


ROWS_SIL = (('WeightBench_A', 'WeightBench_B', 'WeightBench_C'), ('Treadmill_A', 'Treadmill_B', 'Treadmill_C'),
            ('PunchingBag_A', 'PunchingBag_B', 'PunchingBag_C'))


def lay(fbx, recs, row, z0, labels, gap=6.0):
    x = 0.0
    for i in row:
        n = f'Furniture_{i}'
        size = recs[n]['root']['size']
        cx = x + max(size[0], 3.8) / 2
        place(fbx, n, (cx, 0, z0))
        for a in range(int(round(size[0] / 3))):
            for b in range(int(round(size[2] / 3))):
                x0, zz = cx - size[0] / 2 + 3 * a, z0 - size[2] / 2 + 3 * b
                shade = (205, 205, 210) if (a + b) % 2 else (185, 185, 192)
                _REV['_block']('sq', (x0 + 0.03, -0.06, zz + 0.03), (x0 + 2.97, -0.01, zz + 2.97), shade)
        people(recs[n], cx, z0)
        if labels:
            _label(i.split('_')[1], cx, z0 - size[2] / 2 - (5.2 if i.startswith('Punching') else 1.6))
        x += max(size[0], 3.8) + gap
    _REV['_person'](Vector((x - gap + 2.2, 0, 0)), z0)
    return x


def silhouette_sheet(out, fbx, recs):
    shots = []
    clear()
    x = max(lay(fbx, recs, ROWS_SIL[0], 0.0, True), lay(fbx, recs, ROWS_SIL[1], 10.0, True),
            lay(fbx, recs, ROWS_SIL[2], 20.0, True))
    _REV['_block']('floor', (-3, -0.3, -6), (x + 2, -0.07, 23), (150, 150, 156))
    shots.append(render(out / 'silhouettes_game.png', (-0.35, 1.25, -1.0), (1600, 1000), (-2, 0, -6), (x, 6.5, 22),
                        scale=1.0))
    for k, row in enumerate(ROWS_SIL):
        clear()
        x = lay(fbx, recs, row, 0.0, False)
        # the side, so the bench's lifter, the walker and the boxer show against their pieces
        shots.append(render(out / f'silhouettes_side_{k + 1}.png', (-0.75, 0.25, -0.65), (1600, 600), (-2, -0.3, -4.5),
                            (x, 6.8, 3), scale=1.02))
    return shots


NAMES = ['Furniture_WeightBench', 'Furniture_Treadmill', 'Furniture_PunchingBag']


def review_final(out, fbx, recs):
    shots = []

    def scene(spots=True):
        clear()
        x = 0.0
        for n in NAMES:
            size = recs[n]['root']['size']
            cx = x + max(size[0], 3.8) / 2
            place(fbx, n, (cx, 0, 0))
            _squares(cx, size)
            if spots:
                people(recs[n], cx)
            x += max(size[0], 3.8) + 3.0
        _REV['_person'](Vector((x + 0.5, 0, 0)), 0.0)
        _REV['_block']('floor', (-3, -0.3, -6), (x + 4, -0.07, 5), (150, 150, 156))
        return x
    x = scene()
    lo, hi = (-1.5, 0, -4.5), (x + 2.5, 6.6, 3.2)
    shots.append(render(out / '1_game_camera.png', (-0.45, 1.28, -1.0), (1400, 800), lo, hi, scale=1.02))
    shots.append(render(out / '2_front_three_quarter.png', (-0.7, 0.45, -1.0), (1400, 800), lo, hi, scale=1.02))
    shots.append(render(out / '3_back_three_quarter.png', (0.7, 0.55, 1.0), (1400, 800), lo, hi, scale=1.02))
    x = scene(spots=False)
    shots.append(render(out / '4_front_level.png', (0.0, 0.0, -1.0), (1400, 700), (-1.5, -0.3, -4.5),
                        (x + 2.5, 6.8, 3.2), scale=1.02))
    shots.append(render(out / '5_top.png', (0.0, 1.0, -0.02), (1400, 800), (-1.5, 0, -4.5), (x + 2.5, 6.8, 3.2),
                        scale=1.02))
    # The side elevations at floor level, each piece turned 90 degrees (anything floating shows the background).
    clear()
    x = 0.0
    for n in NAMES:
        size = recs[n]['root']['size']
        cx = x + size[2] / 2
        place(fbx, n, (cx, 0, 0), 90)
        _squares(cx, size, 90)
        x += size[2] + 3.0
    _REV['_person'](Vector((x + 1.0, 0, 0)), 0.0)
    shots.append(render(out / '6_side_level.png', (0.0, 0.0, -1.0), (1400, 600), (-1.5, -0.3, -5), (x + 3, 6.8, 5),
                        scale=1.02))
    # Close-ups where a person uses them: the lifter under the bar (from the side, level), the walker at the
    # console, the boxer at the bag.
    clear()
    place(fbx, NAMES[0], (0, 0, 0))
    people(recs[NAMES[0]], 0.0)
    _REV['_block']('floor', (-3, -0.3, -4), (3, -0.07, 4), (150, 150, 156))
    shots.append(render(out / '7_close_bench_side.png', (-1.0, 0.12, 0.0), (1000, 700), (-1.5, 0, -3.2),
                        (1.5, 4.2, 3.2), scale=1.0))
    shots.append(render(out / '8_close_bench.png', (-0.6, 0.6, -0.8), (1000, 800), (-2.0, 0, -3.2), (2.0, 4.2, 3.2),
                        scale=1.0))
    clear()
    place(fbx, NAMES[1], (0, 0, 0))
    people(recs[NAMES[1]], 0.0)
    _REV['_block']('floor', (-3, -0.3, -4), (3, -0.07, 4), (150, 150, 156))
    shots.append(render(out / '9_close_treadmill.png', (-0.75, 0.45, -0.75), (1000, 800), (-2.0, 0, -3.2),
                        (2.0, 6.0, 3.2), scale=1.0))
    clear()
    place(fbx, NAMES[2], (0, 0, 0))
    people(recs[NAMES[2]], 0.0)
    _REV['_block']('floor', (-3, -0.3, -5), (3, -0.07, 2), (150, 150, 156))
    shots.append(render(out / '10_close_bag.png', (-0.9, 0.35, -0.6), (1000, 800), (-2.0, 0, -3.6), (2.0, 6.6, 1.6),
                        scale=1.0))
    return shots


# --- The set ------------------------------------------------------------------------------------------

def main():
    K.use_palette(HM_PALETTE)
    if GREY:
        K.IMPORT_CHECKS = False         # drafts with _A/_B/_C ids, not for import
        K.start_set(SET + '/silhouettes')
        for k in BENCHES:
            sil('WeightBench', k, BENCHES)
        for k in TREADMILLS:
            sil('Treadmill', k, TREADMILLS)
        for k in BAGS:
            sil('PunchingBag', k, BAGS)
        recs = {p.name: r for p, r, _ in K.BUILT}
        out = K.ROOT / 'blender' / SET / 'silhouettes'
        (out / 'manifest.json').write_text(json.dumps({'pieces': recs}, indent=1))
        bad = [p.name for p, r, _ in K.BUILT if r.get('faults')]
        print('SILHOUETTE FAULTS', bad, flush=True)
        if not K.NOPREVIEW:
            print('SHEETS', silhouette_sheet(out / 'review', out / 'fbx', recs), flush=True)
        return
    K.start_set(SET)
    weight_bench()
    treadmill()
    punching_bag()
    built = [p.name for p, _, _ in K.BUILT]
    K.end_set('Haunted Manor: the Gym\'s weight bench, treadmill and punching bag (GDD A.13)', [(built, 3.0, 1.0)],
              sheet=False)
    out = K.ROOT / 'blender' / SET
    manifest = json.loads((out / 'manifest.json').read_text())
    patch_fixup(out / 'import_fixup.luau', manifest)
    val = json.loads((out / 'validation.json').read_text())
    val['spots'] = {n: {'spots': r['furniture']['spots'], 'lift_placed_as': r['furniture'].get('lift_placed_as', {}),
                        'checked': ('spots_check on the built and the re-imported triangles: Use_<n> from 1 without '
                                    'a gap, a Pose from MODELS.md\'s list, a level LookVector, no two spots on one '
                                    'square; Lift: held to the placement it names (the bench\'s Lie: inside the '
                                    'footprint, on its surface with nothing over it, and the lying 5-stud person, '
                                    'lie_faults: in the footprint, on the piece, nothing rising through it, arms '
                                    'included); Stand on the piece (the belt): flat under both feet to '
                                    f'{USE_SURFACE_TOL}, the standing person (stand_blocks, arms included, 3.8 '
                                    'across, 5 tall) clear of the body; Stand in front: on the floor at the front '
                                    'square\'s middle 1.5 in front, facing +Z, its square free of the body')}
                    for n, r in manifest['pieces'].items()}
    val['pieces_rows'] = {n: {k: ROWS[n[len('Furniture_'):]][k] for k in ('w', 'd', 'layer', 'height', 'keyFor')}
                          | {'model_top': manifest['pieces'][n]['furniture']['model_top']} for n in built}
    val['height_findings'] = {
        'note': 'Pieces.luau\'s height against the model\'s top, a finding (not refused): the row must say it',
        **{n: FINDINGS[n] for n in built if n in FINDINGS}}
    val['not_validated'] = val.get('not_validated', [])[:1] + [
        'the attachments and each Use_<n> Pose attribute exist only in manifest.json until import_fixup.luau makes '
        'them', 'a visitor walking to a spot, lying on the bench, walking the belt or punching: no walker or clip '
        'has run', 'the bar, the belt and the bag are Body: nothing moves (MODELS.md names no part for them)']
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
