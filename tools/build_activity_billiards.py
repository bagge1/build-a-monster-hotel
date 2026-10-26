"""The Billiard Hall's wall pieces for Haunted Manor's kit (GDD A.13.2, the Billiard Hall row; its key piece, the
Pool Table, is Haunted Manor's built-rooms set, tools/build_built_rooms.py, with its Play spots).

    Furniture_CueRack       1 x 1 squares, `Wall`: an upright rack of five cues on a pointed-arch backboard; no
                            visitors' spots
    Furniture_Scoreboard    2 x 1 squares, `Wall`: a bead scoreboard (two wires of beads) under a pointed-arch
                            crest with an eight-ball medallion, a chalk ledge under it; no visitors' spots
    Furniture_WallLamp      1 x 1 squares, `Wall`: a gooseneck sconce, a green pool-hall shade on an iron arm, its
                            bulb Glow_Warm_1; no visitors' spots

The contract is MODELS.md, "Decor", "Furniture" and "Activity furniture: visitors' spots": a `Wall` piece's back
on the wall's plane (z = 3fd/2 - 0.4 = 1.1), the body 0.4 inside the footprint, at most 7 tall, `Body` not
colliding, no coplanar faces (but on the wall's face), and nothing floats: a Wall piece may hang, a shell touching
the wall's plane held as one on the floor (hung_check, tools/build_built_rooms_more.py, the DartsBoard's). These
three have no `Use_<n>` (ActivityKit.luau: `spots = none, body = onWall`), so spots_check is not run and nothing
is added to the validator. Definitions from tools/build_activity_karaoke.py (kfurn, kdone, and through it
tools/build_activity_bar.py's and tools/build_built_rooms.py's kit), run without their mains.

The rows are on main's Pieces.luau (w, d, layer, height; the kit's Pieces check runs against them). Its own set,
blender/rooms/haunted_manor_billiards/; the models belong in HotelKit.HauntedManor.

    blender -b -t 4 --python-exit-code 1 -P tools/build_activity_billiards.py [-- grey] [-- nopreview]

`-- grey` writes the grey silhouettes (three options a piece, ids _A/_B/_C, not for import) to
blender/rooms/haunted_manor_billiards/silhouettes/. Otherwise the chosen three are built in the Manor's palette;
review/ gets Workbench sheets only (Studio is running).
"""
import ast
import json
import math
from pathlib import Path

_KA = Path(__file__).resolve().parent / 'build_activity_karaoke.py'
_tree = ast.parse(_KA.read_text(encoding='utf8'))
_tree.body = [n for n in _tree.body if not isinstance(n, ast.Try)]          # its main() call
NS = {'__file__': str(_KA), '__name__': 'build_activity_karaoke'}
exec(compile(_tree, str(_KA), 'exec'), NS)
globals().update({k: v for k, v in NS.items() if not k.startswith('__')})

SET = 'rooms/haunted_manor_billiards'
GREY = 'grey' in K.ARGS
BACK = 1.1                      # the wall's plane for a 1-deep Wall piece: z = 3fd/2 - 0.4


def wfurn(id_):
    """Begin a Wall piece: kfurn without spots, and hung_check (a Wall piece may hang) for grounded_check."""
    p = kfurn(id_, spots=False)
    p.checks.remove(grounded_check)
    p.checks.append(hung_check)
    return p


def rod(part, a, b, r0, r1, col, n=6):
    """A round rod from a to b, r0 at a tapering to r1 at b."""
    a, b = Vector(a), Vector(b)
    d = b - a
    cyl(part, (0, 0, 0), r0, d.length, col, n=n, r_top=r1,
        m=Matrix.Translation(a) @ d.to_track_quat('Y', 'Z').to_matrix().to_4x4())


CUE_BANDS = ((0.0, 0.02, 1.0, 1.0, 'bumper'), (0.02, 0.3, 1.0, 0.92, 'butt'), (0.3, 0.33, 0.95, 0.95, 'ring'),
             (0.33, 0.55, 0.9, 0.82, 'wrap'), (0.55, 0.57, 0.84, 0.84, 'ring'), (0.57, 0.972, 0.72, 0.5, 'shaft'),
             (0.972, 0.992, 0.5, 0.5, 'ferrule'), (0.992, 1.0, 0.48, 0.46, 'tip'))


def cue(c, a, b, r=0.11, wrap='wrap'):
    """A cue from its butt at a to its tip at b: a black bumper, the butt, a gold ring, the wrap, the joint ring,
    the pale shaft tapering, a white ferrule, the blue chalked tip. Thicker than true (0.22 at the butt) so it
    is no hairline from the game camera."""
    a, b = Vector(a), Vector(b)
    for f0, f1, k0, k1, role in CUE_BANDS:
        rod('Body', a + (b - a) * f0, a + (b - a) * f1, r * k0, r * k1, c[wrap if role == 'wrap' else role])


# --- Cue racks --------------------------------------------------------------------------------------

CUE_XS = (-0.72, -0.36, 0.0, 0.36, 0.72)


def rack_a(c, dy=0.3):
    """A: the upright rack: a pointed-arch backboard with a plum inset, a ledge on two corbels with a gold cup for
    each butt, a slotted rail the cues stand through, five cues upright. Blind review 1: lifted 0.3 (the corbels'
    feet 0.3 over the floor read as a cabinet lifted off it; now 0.6, plainly hung), the finial gone (its top 6.08)."""
    prism('Body', lifted(gothic(-1.05, 1.05, 4.5, 5.23), 0.55 + dy), 0.96, BACK, c['board'], plane='xy')
    prism('Body', lifted(gothic(-0.85, 0.85, 4.0, 4.6), 0.95 + dy), 0.94, 0.97, c['panel'], plane='xy')
    span('Body', (-1.08, 0.75 + dy, 0.42), (1.08, 1.0 + dy, 1.08), c['wood'], bevel=0.03)     # 0.03 past the board
    for x in (-0.85, 0.85):
        prism('Body', [(1.0, 0.76 + dy), (0.5, 0.76 + dy), (1.0, 0.3 + dy)], x - 0.08, x + 0.08, c['board'],
              plane='zy')
    span('Body', (-1.08, 4.3 + dy, 0.42), (1.08, 4.52 + dy, 0.98), c['wood'], bevel=0.03)
    for k, x in enumerate(CUE_XS):
        cyl('Body', (x, 0.99 + dy, 0.66), 0.15, 0.12, c['ring'], n=8)
        cue(c, (x, 1.0 + dy, 0.66), (x, 5.3 + dy, 0.66), wrap='wrap' if k % 2 == 0 else 'wrap2')


def rack_b(c):
    """B: the fan: a low half-octagon stand on the floor against the wall, the butts close in its cups, the cues
    fanned out to a rail on a slim back post under a small pointed crest."""
    prism('Body', [(-1.0, 1.08), (-1.0, 0.7), (-0.55, 0.3), (0.55, 0.3), (1.0, 0.7), (1.0, 1.08)], 0.0, 0.7,
          c['board'], plane='xz')
    span('Body', (-0.14, 0.6, 0.9), (0.14, 5.5, BACK), c['board'])
    prism('Body', lifted(gothic(-0.32, 0.32, 0.15, 0.5), 5.45), 0.92, BACK, c['board'], plane='xy')
    span('Body', (-1.0, 4.6, 0.72), (1.0, 4.78, 1.08), c['wood'], bevel=0.03)
    for k, (xb, xt) in enumerate(zip((-0.4, -0.2, 0.0, 0.2, 0.4), (-0.92, -0.46, 0.0, 0.46, 0.92))):
        cyl('Body', (xb, 0.69, 0.48), 0.13, 0.03, c['bumper'], n=8)
        cue(c, (xb, 0.7, 0.48), (xt, 5.25, 0.84), wrap='wrap' if k % 2 == 0 else 'wrap2')


def shield_pts(s=1.0, y0=1.9):
    """A heraldic shield (x, y): pointed below, a pointed arch above, 1.8 wide at s = 1."""
    arch = K.arch_points(-0.9 * s, 0.9 * s, y0 + 2.7 * s, y0 + 3.6 * s, n=4)
    return [(0.0, y0), (0.9 * s, y0 + 1.0 * s)] + list(reversed(arch)) + [(-0.9 * s, y0 + 1.0 * s)]


def rack_c(c):
    """C: crossed cues: a shield on the wall with a plum inset, two cues crossed over it, an eight-ball medallion
    between their tips, a racking triangle between their butts."""
    prism('Body', shield_pts(), 0.96, BACK, c['board'], plane='xy')
    prism('Body', [(x, y * 0.82 + 0.55) for x, y in shield_pts(0.82, 1.9)], 0.94, 0.97, c['panel'], plane='xy')
    cue(c, (-1.0, 1.6, 0.86), (1.0, 5.95, 0.86))
    cue(c, (1.0, 1.6, 0.7), (-1.0, 5.95, 0.7), wrap='wrap2')
    cyl('Body', (0, 0, 0), 0.25, 0.06, c['ball'], n=12, m=at((0, 4.95, 0.98), rx=-90))
    cyl('Body', (0, 0, 0), 0.11, 0.03, c['ballring'], n=10, m=at((0, 4.95, 0.93), rx=-90))
    tri_o = [(0.0, 3.0), (0.36, 2.38), (-0.36, 2.38)]
    tri_i = [(0.0, 2.84), (-0.22, 2.46), (0.22, 2.46)]
    for (a0, a1), (b0, b1) in zip(zip(tri_o, tri_o[1:] + tri_o[:1]), zip(tri_i, tri_i[1:] + tri_i[:1])):
        prism('Body', [a0, a1, (b1[0], b1[1]), (b0[0], b0[1])][::-1], 0.91, 0.965, c['wood'], plane='xy')


RACKS = {'A': rack_a, 'B': rack_b, 'C': rack_c}


# --- Scoreboards ------------------------------------------------------------------------------------

BEAD = [(0.0, -0.12), (0.17, -0.04), (0.17, 0.04), (0.0, 0.12)]       # 24 triangles (the budget: 1,500)


def bead_wire(c, y, z, left, right, x0=-2.08, x1=2.08, step=0.2):
    """A gold wire across x0..x1 at (y, z), `left` beads pushed to the left end and `right` (the score) to the
    right, in groups of five of alternating colour."""
    cyl('Body', (0, 0, 0), 0.03, (x1 - x0) + 0.5, c['wire'], n=4, m=at((x0 - 0.25, y, z), rz=-90))
    xs = [x0 + step * k for k in range(left)] + [x1 - step * k for k in range(right)][::-1]
    for k, x in enumerate(xs):
        col = c['bead1'] if (k // 5) % 2 == 0 else c['bead2']
        lathe('Body', BEAD, col, n=6, m=at((x, y, z), rz=90))


def board_a(c):
    """A: the bead board: a long dark board, two gold wires of beads across a plum panel between end posts, a
    pointed-arch crest over its middle with an eight-ball medallion, gold finials. Blind review 1: raised over the
    heads (at 3.7..5.2 a guest at the wall hid it from the game camera; now 5.05..6.35, the crest to 6.95), the beads
    fewer and bigger, the eight ball given its 8, the chalk ledge gone (its cubes read as notes)."""
    y0, y1 = 5.05, 6.35
    span('Body', (-2.5, y0, 0.95), (2.5, y1, BACK), c['board'], bevel=0.03)
    span('Body', (-2.3, y0 + 0.15, 0.93), (2.3, y1 - 0.15, 0.97), c['panel'])
    for sx in (-1, 1):
        x0, x1 = sorted((sx * 2.2, sx * 2.42))
        span('Body', (x0, y0 + 0.17, 0.66), (x1, y1 - 0.17, 0.98), c['post'], bevel=0.02)
        sphere('Body', (sx * 2.42, y1 + 0.08, 1.0), 0.1, c['gold'], n=6, rings=3)
    bead_wire(c, y0 + 0.38, 0.78, 6, 4, step=0.26)
    bead_wire(c, y0 + 0.92, 0.78, 8, 2, step=0.26)
    prism('Body', lifted(gothic(-1.0, 1.0, 0.2, 0.65), y1 - 0.05), 0.97, BACK, c['board'], plane='xy')
    cy = y1 + 0.27
    cyl('Body', (0, 0, 0), 0.3, 0.065, c['ball'], n=12, m=at((0, cy, 0.985), rx=-90))
    cyl('Body', (0, 0, 0), 0.15, 0.03, c['ballring'], n=10, m=at((0, cy, 0.93), rx=-90))
    for dy, r in ((0.052, 0.05), (-0.05, 0.06)):          # the 8: two ink rings on the white
        lathe('Body', [(r - 0.022, 0.0), (r, 0.0), (r, 0.02), (r - 0.022, 0.02)], c['digit'], n=8, closed=True,
              m=at((0, cy + dy, 0.9), rx=-90))


def board_b(c):
    """B: the hymn board: a tall pointed-arch board, two columns of number cards on three slats (the two
    players' scores), two gold name plates over them."""
    prism('Body', lifted(gothic(-1.7, 1.7, 2.85, 3.6), 2.4), 0.96, BACK, c['board'], plane='xy')
    prism('Body', lifted(gothic(-1.5, 1.5, 2.65, 3.3), 2.55), 0.94, 0.97, c['panel'], plane='xy')
    for sx in (-1, 1):
        x0, x1 = sorted((sx * 0.15, sx * 1.3))
        span('Body', (x0, 5.0, 0.91), (x1, 5.28, 0.95), c['gold'])
    for yr in (2.7, 3.45, 4.2):
        span('Body', (-1.45, yr - 0.1, 0.78), (1.45, yr + 0.02, 0.96), c['wood'])
        for sx in (-1, 1):
            x0, x1 = sorted((sx * 0.15, sx * 1.3))
            span('Body', (x0, yr, 0.86), (x1, yr + 0.62, 0.92), c['card'])
            for dx in (0.3, 0.75):
                xm = min(x0, x1) + dx
                span('Body', (xm - 0.14, yr + 0.1, 0.845), (xm + 0.14, yr + 0.52, 0.865), c['digit'])


def tally(c, x, y, n, z=0.925):
    """n chalk tally sticks from x (groups of five: four upright, the fifth across)."""
    for k in range(n):
        g, i = divmod(k, 5)
        gx = x + g * 0.85
        if i < 4:
            span('Body', (gx + 0.14 * i - 0.025, y, z), (gx + 0.14 * i + 0.025, y + 0.48, z + 0.02), c['line'])
        else:
            box('Body', (0, 0, 0), (0.05, 0.66, 0.02), c['line'], m=at((gx + 0.21, y + 0.24, z + 0.005), rz=-55))


def board_c(c):
    """C: the chalk slate: a wide Tudor-arched frame round a slate, two columns of chalk tallies under a header
    line and scribbled names, a chalk tray with chalk and a felt eraser."""
    prism('Body', lifted(gothic(-2.45, 2.45, 2.95, 3.45), 2.55), 0.97, BACK, c['board'], plane='xy')
    prism('Body', lifted(gothic(-2.2, 2.2, 2.75, 3.15), 2.75), 0.94, 0.98, c['slate'], plane='xy')
    span('Body', (-0.03, 3.0, 0.925), (0.03, 5.2, 0.945), c['line'])
    span('Body', (-2.0, 4.95, 0.925), (2.0, 5.01, 0.945), c['line'])
    for sx in (-1, 1):
        for k, w in enumerate((0.6, 0.35)):
            x0 = sx * 0.4 if sx > 0 else -0.4 - 1.1
            span('Body', (x0 + 0.7 * k, 5.15, 0.925), (x0 + 0.7 * k + w, 5.25, 0.945), c['line'])
    tally(c, -1.85, 4.05, 13)
    tally(c, 0.3, 4.05, 8)
    span('Body', (-2.3, 2.45, 0.72), (2.3, 2.62, 1.08), c['wood'], bevel=0.02)
    for x in (-1.6, -1.1):
        cyl('Body', (0, 0, 0), 0.05, 0.35, c['chalk'], n=6, m=at((x, 2.67, 0.85), rz=-90))
    span('Body', (1.2, 2.62, 0.78), (1.75, 2.8, 0.98), c['wood'])
    span('Body', (1.22, 2.8, 0.8), (1.73, 2.86, 0.96), c['felt'])


BOARDS = {'A': board_a, 'B': board_b, 'C': board_c}


# --- Wall lamps -------------------------------------------------------------------------------------

def shade(c, x, y_rim, z, r, h, glow_part):
    """A pool-hall shade opening down: a green cone, its underside hollowed up to the bulb, a gold collar on
    top; the bulb (`glow_part`) peeping under the rim."""
    lathe('Body', [(0.0, y_rim + 0.16), (r * 0.9, y_rim + 0.02), (r, y_rim), (r * 0.97, y_rim + 0.08),
                   (r * 0.62, y_rim + 0.45 * h), (r * 0.3, y_rim + 0.85 * h), (r * 0.22, y_rim + h),
                   (0.0, y_rim + h + 0.02)], c['shade'], n=10, base=(x, 0, z))
    cyl('Body', (x, y_rim + h - 0.04, z), 0.12, 0.12, c['gold'], n=6)
    sphere(glow_part, (x, y_rim + 0.05, z), (0.17, 0.15, 0.17), c['bulb'], n=8, rings=4)


def backplate(c, y0=4.75):
    """The sconce's plate on the wall: a small pointed arch (dark wood in the Manor's dress: blind review 1 read an
    iron one as a luggage tag)."""
    prism('Body', lifted(gothic(-0.32, 0.32, 0.95, 1.35), y0), 0.98, BACK, c['plate'], plane='xy')


def path_rod(c, pts, r):
    """An iron rod through `pts`, a ball on every bend so the joints close."""
    for k, (a, b) in enumerate(zip(pts, pts[1:])):       # 6 and 8 sides in turn: two runs nearly in line
        rod('Body', a, b, r, r, c['iron'], n=6 if k % 2 == 0 else 8)     # never share a side's plane
    for p in pts[1:-1]:
        sphere('Body', p, r * 1.08, c['iron'], n=6, rings=3)


def lamp_a(c):
    """A: the gooseneck: an iron arm leaving the plate at 45 degrees and curving over into the top of a green shade
    that hangs 1.6 out from the wall, the bulb under it. Blind review 1: all 0.4 higher (the bulb 0.6 over a 5-stud
    head, the shade's rim at 5.7) and the arm thicker (0.16; 0.12 vanished from the game camera)."""
    backplate(c, 5.15)
    cyl('Body', (0, 0, 0), 0.15, 0.06, c['gold'], n=8, m=at((0, 5.75, 1.0), rx=-90))
    # The neck a cubic Bezier in 8 straight runs (5 showed their kinks in the side view).
    p0, p1, p2, p3 = (Vector(v) for v in ((0, 5.75, 1.0), (0, 6.45, 0.55), (0, 6.85, -0.2), (0, 6.46, -0.5)))
    neck = [tuple(p0 * (1 - t) ** 3 + p1 * 3 * t * (1 - t) ** 2 + p2 * 3 * t * t * (1 - t) + p3 * t ** 3)
            for t in (k / 8 for k in range(9))]
    path_rod(c, neck, 0.08)
    shade(c, 0.0, 5.7, -0.5, 0.58, 0.7, glow(c['bulb']))


def lamp_b(c):
    """B: the lantern: a straight iron bracket with a brace, a hexagonal lantern hanging from its end, its panes
    the glow."""
    backplate(c, 4.95)
    path_rod(c, [(0, 6.3, 1.0), (0, 6.3, -0.45)], 0.06)
    rod('Body', (0, 5.4, 1.0), (0, 6.28, 0.35), 0.05, 0.05, c['iron'])
    sphere('Body', (0, 6.3, -0.5), 0.09, c['gold'], n=6, rings=3)
    cyl('Body', (0, 6.0, -0.4), 0.03, 0.28, c['iron'], n=4)
    cyl('Body', (0, 5.82, -0.4), 0.34, 0.2, c['iron'], n=6, r_top=0.06)
    cyl(glow(c['bulb']), (0, 5.3, -0.4), 0.27, 0.53, c['bulb'], n=6)
    cyl('Body', (0, 5.22, -0.4), 0.32, 0.09, c['iron'], n=6)
    lathe('Body', [(0.0, 5.02), (0.1, 5.22)], c['iron'], n=6, base=(0, 0, -0.4))


def lamp_c(c):
    """C: the twin pendant: a pool table's lamp in little, a T-arm out from the plate, two green shades hanging
    from its crossbar."""
    backplate(c, 5.0)
    path_rod(c, [(0, 6.3, 1.0), (0, 6.3, -0.3)], 0.06)
    rod('Body', (0, 5.5, 1.0), (0, 6.28, 0.45), 0.05, 0.05, c['iron'])
    path_rod(c, [(-0.66, 6.3, -0.3), (0.66, 6.3, -0.3)], 0.055)
    part = glow(c['bulb'])
    for sx in (-1, 1):
        sphere('Body', (sx * 0.7, 6.3, -0.3), 0.08, c['gold'], n=6, rings=3)
        rod('Body', (sx * 0.5, 6.3, -0.3), (sx * 0.5, 5.9, -0.3), 0.03, 0.03, c['iron'], n=4)
        shade(c, sx * 0.5, 5.4, -0.3, 0.4, 0.55, part)


LAMPS = {'A': lamp_a, 'B': lamp_b, 'C': lamp_c}

BUILD = {'CueRack': RACKS, 'Scoreboard': BOARDS, 'WallLamp': LAMPS}

GC = {'board': 'stone_dark', 'panel': 'grey', 'wood': 'stone', 'ring': 'stone', 'bumper': 'black',
      'butt': 'stone_dark', 'wrap': 'grey', 'wrap2': 'black', 'shaft': 'white', 'ferrule': 'white', 'tip': 'grey',
      'ball': 'black', 'ballring': 'white', 'post': 'stone', 'wire': 'stone', 'bead1': 'white', 'bead2': 'grey',
      'gold': 'stone', 'chalk': 'white', 'card': 'white', 'digit': 'black', 'slate': 'black', 'line': 'white',
      'felt': 'grey', 'iron': 'stone_dark', 'plate': 'stone_dark', 'shade': 'grey', 'bulb': 'white'}

NOTES = {'CueRack_A': 'A: an upright rack, five cues on a pointed-arch backboard, a ledge of cups and a rail',
         'CueRack_B': 'B: a fan, the cues spread from a low stand on the floor to a rail on a back post',
         'CueRack_C': 'C: two cues crossed over a shield, an eight-ball medallion and a racking triangle',
         'Scoreboard_A': 'A: a bead board, two wires of beads under a pointed crest with an eight ball',
         'Scoreboard_B': 'B: a hymn board, two columns of number cards in a tall pointed arch',
         'Scoreboard_C': 'C: a chalk slate in a Tudor-arched frame, tallies in two columns, a chalk tray',
         'WallLamp_A': 'A: a gooseneck sconce, one green shade on an iron arm',
         'WallLamp_B': 'B: a hexagonal lantern on a straight bracket',
         'WallLamp_C': 'C: a twin pendant, two green shades on a T-arm'}


def sil(kind, k):
    wfurn(f'{kind}_{k}')
    BUILD[kind][k](GC)
    kdone(NOTES[f'{kind}_{k}'])


# --- The chosen three, in the Manor's dress ---------------------------------------------------------

HM = {'board': 'wood_dark', 'panel': 'plum', 'wood': 'wood', 'ring': 'gold', 'bumper': 'black', 'butt': 'wood',
      'wrap': 'crimson', 'wrap2': 'black', 'shaft': 'wood_light', 'ferrule': 'cream', 'tip': 'sky',
      'ball': 'black', 'ballring': 'cream', 'post': 'wood', 'wire': 'gold', 'bead1': 'bone', 'bead2': 'crimson',
      'gold': 'gold', 'chalk': 'sky', 'card': 'cream', 'digit': 'ink', 'slate': 'black', 'line': 'bone',
      'felt': 'crimson', 'iron': 'iron', 'plate': 'wood_dark', 'shade': 'moss', 'bulb': 'lamp'}

CHOSEN = {'CueRack': 'A', 'Scoreboard': 'A', 'WallLamp': 'A'}
FINAL_NOTES = {
    'CueRack': 'a Haunted Manor cue rack: a dark-wood pointed-arch backboard with a plum inset, a wood ledge on two '
               'corbels with a gold cup for each butt, a slotted rail, five cues upright (wood butts, crimson and '
               'black wraps between gold rings, pale shafts, white ferrules, blue chalked tips), hung 0.6 '
               'clear of the floor',
    'Scoreboard': 'a Haunted Manor bead scoreboard: a dark-wood board, two gold wires of bone and crimson beads in '
                  'fives across a plum panel between wood end posts, a pointed-arch crest with an eight-ball '
                  'medallion (its 8 in ink), gold finials, hung over the heads (5.05 to 6.95)',
    'WallLamp': 'a Haunted Manor pool-hall sconce: a dark-wood pointed-arch plate with a gold boss, an iron gooseneck '
                'arm curving over into the gold collar of a green shade, a warm bulb under its rim'}


def chosen(kind):
    wfurn(kind)
    BUILD[kind][CHOSEN[kind]](HM)
    kdone(FINAL_NOTES[kind])


# --- Review (Workbench on light grey: Studio is running, no EEVEE or Cycles) --------------------------

WALL_RGB = (214, 208, 196)


def wall(x0, x1, z0=0.0, h=8.0):
    """The room's wall behind the pieces: its face on their wall plane."""
    _REV['_block']('wall', (x0, 0.0, z0 + BACK), (x1, h, z0 + BACK + 0.4), WALL_RGB)


ROWS_SIL = tuple(tuple(f'{kind}_{k}' for k in 'ABC') for kind in ('CueRack', 'Scoreboard', 'WallLamp'))


def lay(fbx, recs, row, z0, labels, gap=3.6):
    x = 0.0
    for i in row:
        n = f'Furniture_{i}'
        size = recs[n]['root']['size']
        cx = x + size[0] / 2
        place(fbx, n, (cx, 0, z0))
        for a in range(int(round(size[0] / 3))):
            x0 = cx - size[0] / 2 + 3 * a
            shade_ = (205, 205, 210) if a % 2 else (185, 185, 192)
            _REV['_block']('sq', (x0 + 0.03, -0.06, z0 - 1.47), (x0 + 2.97, -0.01, z0 + 1.47), shade_)
        _REV['_person'](Vector((cx + size[0] / 2 + 1.3, 0, 0)), z0 + 0.5)
        if labels:
            _label(i.split('_')[1], cx, z0 - 3.2)
        x += size[0] + gap
    wall(-1.5, x, z0)
    return x


def silhouette_sheet(out, fbx, recs):
    shots = []
    clear()
    x = max(lay(fbx, recs, row, 12.0 * k, True) for k, row in enumerate(ROWS_SIL))
    _REV['_block']('floor', (-3, -0.3, -6), (x + 2, -0.07, 27), (150, 150, 156))
    shots.append(render(out / 'silhouettes_game.png', (-0.35, 1.25, -1.0), (1600, 1100), (-2, 0, -5), (x, 8.0, 26),
                        scale=1.0))
    for k, row in enumerate(ROWS_SIL, 1):
        clear()
        x = lay(fbx, recs, row, 0.0, False)
        shots.append(render(out / f'silhouettes_front_{k}.png', (-0.25, 0.15, -1.0), (1600, 650), (-1.5, -0.3, -2),
                            (x, 7.6, 1.5), scale=1.02))
    clear()
    x = 0.0
    for row in ROWS_SIL:
        for i in row:
            n = f'Furniture_{i}'
            place(fbx, n, (x, 0, 0), 90)
            _REV['_block']('wall', (x + BACK, 0, -2.0), (x + BACK + 0.4, 8.0, 2.0), WALL_RGB)
            x += 4.0
    _REV['_person'](Vector((x, 0, 0)), 0.0)
    shots.append(render(out / 'silhouettes_side.png', (0.0, 0.05, -1.0), (1800, 500), (-2, -0.3, -2), (x + 2, 7.6, 2),
                        scale=1.02))
    return shots


NAMES = ['Furniture_CueRack', 'Furniture_Scoreboard', 'Furniture_WallLamp']
POOL_FBX = [K.ROOT / 'blender' / 'rooms' / 'haunted_manor' / 'fbx',
            K.ROOT.parents[2] / 'blender' / 'rooms' / 'haunted_manor' / 'fbx']     # a worktree: the main checkout's


def hall(fbx, pool=True):
    """A billiard hall's wall as a room would have it: the cue rack, a lamp either side of the scoreboard, the
    Manor's pool table in front (context only, from the Manor's set), a person before the rack, one beside."""
    clear()
    place(fbx, NAMES[0], (-7.5, 0, 0))
    place(fbx, NAMES[1], (0, 0, 0))
    for x in (-4.5, 4.5):
        place(fbx, NAMES[2], (x, 0, 0))
    wall(-10, 10)
    src = next((p for p in POOL_FBX if (p / 'Furniture_PoolTable.fbx').exists()), None)
    if pool and src is not None:
        place(src, 'Furniture_PoolTable', (0, 0, -6.0))
    _REV['_person'](Vector((-7.5, 0, 0)), -3.5)       # in front of the rack, back far enough not to hide it
    _REV['_person'](Vector((7.5, 0, 0)), 0.5)
    _REV['_block']('floor', (-10, -0.3, -11), (10, -0.07, 1.5), (150, 150, 156))
    return src is not None


def review_final(out, fbx, recs):
    shots = []
    had_pool = hall(fbx)
    shots.append(render(out / '1_game_camera.png', (-0.4, 1.25, -1.0), (1400, 900), (-10, 0, -10), (10, 8.0, 1.5),
                        scale=1.02))
    hall(fbx, pool=False)
    shots.append(render(out / '2_front_level.png', (0.0, 0.0, -1.0), (1400, 650), (-10, -0.3, -2), (10, 8.0, 1.5),
                        scale=1.02))
    clear()
    x = 0.0
    for n in NAMES:
        place(fbx, n, (x, 0, 0), 90)
        _REV['_block']('wall', (x + BACK, 0, -1.5 * recs[n]['root']['size'][0] / 3 - 0.5),
                       (x + BACK + 0.4, 8.0, 1.5 * recs[n]['root']['size'][0] / 3 + 0.5), WALL_RGB)
        x += 6.0
    _REV['_person'](Vector((x - 6.0 - 2.3, 0, 0)), 0.0)  # in the room under the lamp's shade (its front is -x here)
    shots.append(render(out / '3_side_level.png', (0.0, 0.0, -1.0), (1400, 600), (-2, -0.3, -3), (x - 4, 7.6, 3),
                        scale=1.02))
    # Close up from a guest's height a little to one side: each piece on its wall, a person beside it.
    clear()
    x = 0.0
    for n in NAMES:
        size = recs[n]['root']['size']
        cx = x + size[0] / 2
        place(fbx, n, (cx, 0, 0))
        x += size[0] + 1.2
    _REV['_person'](Vector((x - 1.2 - 1.5, 0, 0)), -0.9)    # under the lamp's shade
    wall(-0.5, x)
    _REV['_block']('floor', (-1, -0.3, -4), (x + 1, -0.07, 1.5), (150, 150, 156))
    shots.append(render(out / '4_close_three_quarter.png', (-0.55, 0.3, -1.0), (1400, 800), (-0.5, 0, -2.5),
                        (x, 7.0, 1.2), scale=1.0))
    clear()
    x = 0.0
    for n in NAMES:
        size = recs[n]['root']['size']
        place(fbx, n, (x + size[0] / 2, 0, 0))
        x += size[0] + 1.2
    _REV['_block']('floor', (-1, -0.3, -4), (x + 1, -0.07, 1.5), (150, 150, 156))
    shots.append(render(out / '5_top.png', (0.0, 1.0, -0.02), (1400, 500), (-0.5, 0, -1.5), (x, 7.0, 1.5),
                        scale=1.02))
    return shots, had_pool


# --- The set ------------------------------------------------------------------------------------------

def main():
    K.use_palette(HM_PALETTE)
    if GREY:
        K.IMPORT_CHECKS = False         # drafts with _A/_B/_C ids, not for import
        K.start_set(SET + '/silhouettes')
        for kind in BUILD:
            for k in 'ABC':
                sil(kind, k)
        recs = {p.name: r for p, r, _ in K.BUILT}
        out = K.ROOT / 'blender' / SET / 'silhouettes'
        (out / 'manifest.json').write_text(json.dumps({'pieces': recs}, indent=1))
        bad = {p.name: r.get('faults') for p, r, _ in K.BUILT if r.get('faults')}
        print('SILHOUETTE FAULTS', bad, flush=True)
        print('SILHOUETTE TRIS', {p.name: r.get('triangles') for p, r, _ in K.BUILT}, flush=True)
        if not K.NOPREVIEW:
            print('SHEETS', silhouette_sheet(out / 'review', out / 'fbx', recs), flush=True)
        return
    K.start_set(SET)
    for kind in BUILD:
        chosen(kind)
    built = [p.name for p, _, _ in K.BUILT]
    K.end_set('Haunted Manor: the Billiard Hall\'s cue rack, scoreboard and wall lamp (GDD A.13)',
              [(built, 3.0, 1.0)], sheet=False)
    out = K.ROOT / 'blender' / SET
    manifest = json.loads((out / 'manifest.json').read_text())
    patch_fixup(out / 'import_fixup.luau', manifest)
    val = json.loads((out / 'validation.json').read_text())
    val['spots'] = {n: {'spots': r['furniture']['spots'],
                        'checked': 'no visitors\' spots (A.13.2: not a key piece; ActivityKit.luau spots = none)'}
                    for n, r in manifest['pieces'].items()}
    val['hung'] = {n: ('hung_check on the built and the re-imported triangles: every shell stands on the floor or '
                       f'touches one that does, the wall\'s plane at z = {BACK} counting as one that does '
                       '(MODELS.md, "Furniture", "Nothing floats"); the back on that plane (the kit\'s Wall rule)')
                   for n in built}
    val['pieces_rows'] = {n: {k: ROWS[n[len('Furniture_'):]][k] for k in ('w', 'd', 'layer', 'height', 'keyFor')}
                          | {'model_top': manifest['pieces'][n]['furniture']['model_top']} for n in built}
    val['height_findings'] = {
        'note': 'Pieces.luau\'s height against the model\'s top, a finding (not refused): the row must say it',
        **{n: FINDINGS[n] for n in built if n in FINDINGS}}
    val['not_validated'] = val.get('not_validated', [])[:1] + [
        'the lamp lit: import_fixup makes Glow_Warm_1 Neon; no light source is added by the model',
        'a piece on a real wall in Studio, turned to each of the four walls by the build mode']
    (out / 'validation.json').write_text(json.dumps(val, indent=1))
    if not K.NOPREVIEW:
        shots, had_pool = review_final(out / 'review', out / 'fbx', manifest['pieces'])
        print('SHEETS', shots, 'pool table in 1:', had_pool, flush=True)
    bad = [n for n, r in val['pieces'].items() if not r['ok']]
    print(f'SET {SET}: {built}; validation faults in {bad}', flush=True)
    print('TRIS', {n: r.get('triangles') for n, r in val['pieces'].items()}, flush=True)
    if bad:
        raise SystemExit(f'VALIDATION FAULTS: {bad}')


try:
    main()
except K.Refused as e:
    print(str(e), flush=True)
    raise SystemExit('REFUSED')
