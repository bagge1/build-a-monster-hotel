"""The Karaoke Lounge's two pieces for Haunted Manor's kit (GDD A.13.2, the Karaoke Lounge row; A.13.3, the Stage set).

    Furniture_KaraokeStage  2 x 2 squares, `Floor`: a low stage, its deck at 0.8 on a plum skirt, a lyrics
                            screen at its back (Glow_Cold_1, so the code can light it) in a pointed-arch frame,
                            two microphone stands; Use_1, Use_2 `Stand` on the deck for two singers, facing the
                            room (-Z)
    Furniture_Microphone    1 x 1 squares, `Floor`: a standalone microphone stand; no visitors' spots

The contract is MODELS.md, "Decor", "Furniture" and "Activity furniture: visitors' spots", as for the Bar, the Gym
and the Dance Floor (tools/build_activity_bar.py, whose definitions this runs: spot, spots_check, sdone,
patch_fixup, _label, and through it tools/build_built_rooms.py's kit). The singers' spots are `Stand` inside the
footprint, on the piece: spots_check sends them to stand_on_faults (added with tools/build_activity_gym.py: the deck
flat under both feet, the standing 5-stud person, arms included, clear of the body: the microphone in front, the
screen's frame behind). Nothing is added to the validator here.

Kept apart from the Bar's SmallStage (a round apron, curtains and a crescent, one performer `Dance`) but of its
family: the Manor's dark wood, gold and pointed arch; a square deck on a plum skirt, marquee bulbs; the screen where
the SmallStage has its curtains.

The rows are on main's Pieces.luau (w, d, layer, height; the kit's Pieces check runs against them). Its own set,
blender/rooms/haunted_manor_karaoke/; the models belong in HotelKit.HauntedManor.

    blender -b -t 4 --python-exit-code 1 -P tools/build_activity_karaoke.py [-- grey] [-- nopreview]

`-- grey` writes the grey silhouettes (three options a piece, ids _A/_B/_C, not for import) to
blender/rooms/haunted_manor_karaoke/silhouettes/. Otherwise the chosen two are built in the Manor's palette;
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

SET = 'rooms/haunted_manor_karaoke'
GREY = 'grey' in K.ARGS

DECK = 0.8                      # the deck's top, where the singers stand (the SmallStage's is 1.0)
SING_X, SING_Z = 1.3, -0.7      # the two singers, one a square, side by side; forward (blind review 1: at -0.3
                                # their heads hid the screen's lower lines from the game camera)
MIC_Z = -1.85                   # their microphones, in front: the capsule 0.3 ahead of the face, the foot 0.1 clear
                                # of the legs (blind review 2: at 0.03 the feet read as on the foot)
MIC_STANDALONE_Z = -0.5         # the standalone stand forward in its square, so the guest behind it stands in it too
SING_LOOK = (0, 0, -1)          # facing the room (the piece's front)


def kfurn(id_, spots=True):
    """Begin Furniture_<id_> on its Pieces.luau row (a silhouette _A/_B/_C on its piece's); its spots replace
    `Use` (use_check off; spots_check on when it has spots)."""
    base = id_.split('_')[0]
    row = dict(ROWS[base])
    ROWS[id_] = row
    K.pieces_decor()
    K._PIECES.setdefault(id_, {k: row[k] for k in ('w', 'd', 'layer', 'height')} | {'always': False})
    p = furn(id_)
    p.checks.remove(use_check)
    if spots:
        p.checks.append(spots_check)
    p.spots = {}
    return p


def kdone(note):
    rec = sdone(note)
    rec['furniture']['pieces_row'] = 'Pieces.luau'
    return rec


def singers():
    """Two singers on the deck, one a square, facing the room."""
    spot(1, (-SING_X, DECK, SING_Z), SING_LOOK, 'Stand')
    spot(2, (SING_X, DECK, SING_Z), SING_LOOK, 'Stand')


def glow(col):
    """The part a colour goes in: Glow_<Key>_1 for a glow colour (rule 1: the code lights it), else Body."""
    key = K.GLOW_OF.get(col)
    return f'Glow_{key}_1' if key else 'Body'


# --- Microphone stands (the standalone piece and the stage's two) -----------------------------------

def mic_a(c, x=0.0, z=0.0, y=0.0):
    """A: a vintage stand: a domed round foot, a straight pole, a gold collar and yoke, a pill-shaped capsule
    with a gold band, its top at 4.96 (the mouth of the 5-stud person at about 4.3). Blind review 1: heavier
    (the foot 0.55, the pole 0.09, the capsule 0.25 round; a hairline from the game camera)."""
    lathe('Body', [(0.6, 0.0), (0.6, 0.09), (0.36, 0.19), (0.13, 0.29)], c['foot'], n=10, base=(x, y, z))
    cyl('Body', (x, y + 0.27, z), 0.11, 3.83, c['pole'], n=6)          # blind review 2: 0.6 and 0.11
    cyl('Body', (x, y + 4.0, z), 0.13, 0.15, c['clip'], n=6)
    span('Body', (x - 0.31, y + 4.13, z - 0.04), (x + 0.31, y + 4.2, z + 0.04), c['clip'])     # inside the arms
    for sx in (-1, 1):
        span('Body', (x + sx * 0.3 - 0.03, y + 4.15, z - 0.05), (x + sx * 0.3 + 0.03, y + 4.64, z + 0.05),
             c['clip'])
    lathe('Body', [(0.0, 4.2), (0.19, 4.26), (0.25, 4.45), (0.24, 4.75), (0.14, 4.92), (0.0, 4.96)],
          c['head'], n=8, base=(x, y, z))
    cyl('Body', (x, y + 4.5, z), 0.255, 0.1, c['clip'], n=8)


def mic_b(c, x=0.0, z=0.0, y=0.0):
    """B: a tripod boom stand: three legs, the pole to 3.75, a boom rising back (+Z, toward the singer behind
    it) to a capsule angled down at the mouth, a counterweight at its front end."""
    hub = (x, y + 0.62, z)
    for k in range(3):
        a = math.radians(90 + 120 * k)
        foot = (x + 0.92 * math.cos(a), y + 0.05, z + 0.92 * math.sin(a))
        seg('Body', foot, hub, 0.05, c['pole'], n=5)
        sphere('Body', foot, (0.09, 0.05, 0.09), c['foot'], n=6, rings=3)
    cyl('Body', (x, y + 0.5, z), 0.1, 0.3, c['foot'], n=6)
    cyl('Body', (x, y + 0.6, z), 0.06, 3.2, c['pole'], n=6)
    sphere('Body', (x, y + 3.8, z), 0.12, c['clip'], n=6, rings=3)
    seg('Body', (x, y + 3.62, z - 0.55), (x, y + 4.72, z + 0.68), 0.04, c['pole'], n=5)
    sphere('Body', (x, y + 3.6, z - 0.6), (0.14, 0.14, 0.14), c['foot'], n=6, rings=3)
    seg('Body', (x, y + 4.74, z + 0.66), (x, y + 4.5, z + 0.94), 0.12, c['head'], n=8)
    sphere('Body', (x, y + 4.5, z + 0.94), 0.125, c['head'], n=8, rings=4)


def mic_c(c, x=0.0, z=0.0, y=0.0):
    """C: a gothic candlestick stand: a stepped six-sided foot, a turned baluster with a knop, the pole, a round
    ball microphone held in a gold crescent cradle, a gold finial on top."""
    cyl('Body', (x, y, z), 0.55, 0.12, c['foot'], n=6)
    cyl('Body', (x, y + 0.1, z), 0.4, 0.12, c['foot'], n=6)
    lathe('Body', [(0.16, 0.2), (0.1, 0.55), (0.2, 0.9), (0.2, 1.05), (0.09, 1.3), (0.07, 1.4)], c['pole'], n=8,
          base=(x, y, z))
    cyl('Body', (x, y + 1.35, z), 0.06, 2.85, c['pole'], n=6)
    cyl('Body', (x, y + 4.12, z), 0.1, 0.1, c['clip'], n=6)
    cr = [(0.34 * math.cos(math.radians(a)), 0.34 * math.sin(math.radians(a))) for a in range(200, 341, 20)]
    ci = [(0.26 * math.cos(math.radians(a)), 0.26 * math.sin(math.radians(a))) for a in range(340, 199, -20)]
    prism('Body', [(x + u, y + 4.52 + v) for u, v in cr + ci], z - 0.05, z + 0.05, c['clip'], plane='xy')
    sphere('Body', (x, y + 4.52, z), 0.24, c['head'], n=10, rings=6)
    cyl('Body', (x, y + 4.5, z), 0.245, 0.05, c['clip'], n=10)
    cyl('Body', (x, y + 4.74, z), 0.06, 0.24, c['clip'], n=4, r_top=0.0)


MICS = {'A': mic_a, 'B': mic_b, 'C': mic_c}


# --- Shared stage parts -----------------------------------------------------------------------------

def chamfered(h, z0, z1, ch):
    """A deck's outline (x, z): x -h..h, z z0..z1, its front corners cut by ch."""
    return [(-h + ch, z0), (h - ch, z0), (h, z0 + ch), (h, z1), (-h, z1), (-h, z0 + ch)]


def deck(c, top_pts, skirt_pts):
    """The deck: a skirt on the floor under a top 0.14 thick, its top at DECK."""
    prism('Body', skirt_pts, 0.0, DECK - 0.12, {'top': c['edge'], 'bottom': c['edge'], 'rest': c['skirt']},
          plane='xz')
    prism('Body', top_pts, DECK - 0.14, DECK, {'top': c['deck'], 'rest': c['edge']}, plane='xz')


def driver(x, y, z, r, c):
    """A loudspeaker on a front face at z (facing -Z): a gold rim plate, the cone and its dust cap proud of it."""
    cyl('Body', (0, 0, 0), r + 0.07, 0.04, c['rim'], n=10, m=at((x, y, z), rx=-90))
    lathe('Body', [(r, 0.0), (r * 0.9, 0.03), (r * 0.34, 0.08), (r * 0.3, 0.1), (r * 0.18, 0.14), (0.0, 0.16)],
          c['cone'], n=10, m=at((x, y, z - 0.04), rx=-90))


def lyrics_xy(lines, z, c):
    """Lyric lines on a screen facing -Z at z: [(cx, cy, width, sung fraction)], 0.24 tall, 0.02 proud; the sung
    part of a line in the highlight colour (the karaoke wipe)."""
    for cx, cy, w, sung in lines:
        x0, x1 = cx - w / 2, cx + w / 2
        xm = x1 - w * sung          # read from the room (looking +Z), +X is on the left: the wipe starts there
        if sung > 0:
            span('Body', (xm, cy - 0.12, z - 0.02), (x1, cy + 0.12, z + 0.005), c['sung'])
        if sung < 1:
            span('Body', (x0, cy - 0.12, z - 0.02), (xm, cy + 0.12, z + 0.005), c['text'])


# --- The stages ---------------------------------------------------------------------------------------

def stage_a(c, mic=mic_a, bulbs=True):
    """A: the lyrics window: a square deck (a step in front until blind review 2); at its back a pointed-arch frame, the
    lyrics screen in its arch over a speaker cabinet with two drivers, a gold sill between; a row of marquee
    bulbs round the arch and down the posts; two microphone stands in front of the singers."""
    # Blind review 1 (README): the singers forward 0.4 and the screen raised 0.6 (their heads hid its lower lines),
    # the deck forward to hold their microphones, the step as wide as the deck's front edge, the drivers bigger,
    # the back a crimson grille (two gold-rimmed ports read as eyes), the stands heavier.
    # Blind review 2: the front step went (the microphones' feet stood over it, the one way up); the deck runs to
    # the footprint's front as the SmallStage's does, its microphones 0.15 further forward.
    deck(c, chamfered(2.6, -2.6, 2.6, 0.4), chamfered(2.5, -2.5, 2.5, 0.38))
    for sx in (-1, 1):
        x0, x1 = sorted((sx * 2.22, sx * 2.58))         # 0.02 inside the deck's sides and back (coplanar there)
        span('Body', (x0, DECK - 0.02, 1.9), (x1, 5.5, 2.58), c['frame'])
    outer = K.arch_points(-2.58, 2.58, 5.3, 6.95, n=4)
    inner = K.arch_points(-2.22, 2.22, 5.3, 6.55, n=4)
    prism('Body', outer + list(reversed(inner)), 1.95, 2.55, c['frame'], plane='xy')
    prism('Body', lifted(gothic(-2.26, 2.26, 5.3 - DECK + 0.02, 6.62 - DECK + 0.02, n=4), DECK - 0.02), 2.3, 2.45,
          c['panel'], plane='xy')
    prism(glow(c['screen']), lifted(gothic(-1.95, 1.95, 1.8, 2.8), 3.6), 2.24, 2.32, c['screen'], plane='xy')
    lyrics_xy([(0.0, 5.6, 2.6, 0.0), (0.0, 4.95, 3.3, 0.55), (0.0, 4.3, 2.5, 0.0)], 2.24, c)
    span('Body', (-2.23, DECK - 0.02, 1.98), (2.23, 3.6, 2.31), c['cabinet'])
    span('Body', (-2.23, 3.54, 1.92), (2.23, 3.68, 2.32), c['sill'])
    for x in (-1.15, 1.15):
        driver(x, 2.15, 1.98, 0.6, c)
    if c.get('grille'):         # the back finished as a speaker's: a cloth grille on the cabinet, a gold rail over it
        # (blind review 2: an arched grille on the bare panel read as a tombstone)
        span('Body', (-1.95, DECK + 0.2, 2.44), (1.95, 3.3, 2.47), c['grille'])
        span('Body', (-2.24, 3.42, 2.44), (2.24, 3.6, 2.5), c['sill'])
    if bulbs:
        part = glow(c['bulb'])
        for bx, by in K.arch_points(-2.41, 2.41, 5.3, 6.75, n=4):
            sphere(part, (bx, by, 1.95), 0.13, c['bulb'], n=6, rings=3)
        for sx in (-1, 1):
            for by in (1.6, 2.9, 4.2):     # even down the posts (blind review 3; not re-reviewed)
                sphere(part, (sx * 2.41, by, 1.9), 0.13, c['bulb'], n=6, rings=3)
    for sx in (-1, 1):
        mic(c, sx * SING_X, MIC_Z, DECK)


def stage_b(c, mic=mic_a):
    """B: the prompter: a square deck; at its front a wedge monitor sloped up at the singers, its lyrics screen
    facing them; at its back two speaker towers with pointed caps either side of a drape under a gold rod."""
    deck(c, chamfered(2.6, -2.6, 2.6, 0.2), chamfered(2.5, -2.5, 2.5, 0.18))
    p1, p2 = Vector((-1.6, DECK + 0.55)), Vector((-2.5, DECK + 1.45))          # (z, y) along the slope
    prism('Body', [(-2.5, DECK - 0.02), (-1.6, DECK - 0.02), tuple(p1), tuple(p2)], -0.7, 0.7, c['cabinet'],
          plane='zy')
    u = (p2 - p1).normalized()
    nrm = Vector((-u.y, u.x)) if (-u.y) > 0 else Vector((u.y, -u.x))           # up and back, toward the singers
    q1, q2 = p1 + u * 0.1, p2 - u * 0.1
    prism(glow(c['screen']), [tuple(q1 - nrm * 0.01), tuple(q2 - nrm * 0.01), tuple(q2 + nrm * 0.04),
                              tuple(q1 + nrm * 0.04)], -0.6, 0.6, c['screen'], plane='zy')
    for k, (t, w, sung) in enumerate(((0.3, 1.0, 0.0), (0.55, 1.0, 0.5), (0.8, 0.8, 0.0))):
        a = q1 + (q2 - q1) * t
        a0, a1 = a - u * 0.07, a + u * 0.07
        pts = [tuple(a0 + nrm * 0.03), tuple(a1 + nrm * 0.03), tuple(a1 + nrm * 0.06), tuple(a0 + nrm * 0.06)]
        if sung:
            prism('Body', pts, -w / 2, -w / 2 + w * sung, c['sung'], plane='zy')
            prism('Body', pts, -w / 2 + w * sung, w / 2, c['text'], plane='zy')
        else:
            prism('Body', pts, -w / 2, w / 2, c['text'], plane='zy')
    for sx in (-1, 1):
        x0, x1 = sorted((sx * 1.65, sx * 2.55))
        span('Body', (x0, DECK - 0.02, 1.55), (x1, 5.6, 2.55), c['cabinet'])
        xa, xb = sorted((sx * 1.6, sx * 2.6))
        prism('Body', [(xa, 5.55), (xb, 5.55), (sx * 2.1, 6.9)][::sx], 1.5, 2.6, c['frame'], plane='xy')
        for y, r in ((2.0, 0.37), (3.3, 0.3), (4.5, 0.2)):
            driver(sx * 2.1, y, 1.55, r, c)
    span('Body', (-1.7, DECK - 0.02, 2.3), (1.7, 5.2, 2.45), c['panel'])
    cyl('Body', (0, 0, 0), 0.07, 3.4, c['sill'], n=6, m=at((-1.7, 5.25, 2.25), rz=-90))
    for sx in (-1, 1):
        mic(c, sx * SING_X, MIC_Z, DECK)


def ellipse_pts(cx, cy, rx, ry, n=20):
    return [(cx + rx * math.cos(2 * math.pi * k / n), cy + ry * math.sin(2 * math.pi * k / n)) for k in range(n)]


def stage_c(c, mic=mic_a):
    """C: the magic mirror: a half-octagon fronted deck; at its back centre a tall oval mirror in a gold frame
    on a turned pedestal, the lyrics glowing in the glass; the two singers either side of it, forward."""
    deck(c, chamfered(2.6, -2.6, 2.6, 1.5), chamfered(2.5, -2.5, 2.5, 1.45))
    lathe('Body', [(0.5, DECK - 0.02), (0.5, DECK + 0.15), (0.3, DECK + 0.3), (0.18, DECK + 0.9), (0.28, DECK + 1.3),
                   (0.16, DECK + 1.6), (0.16, 2.7)], c['frame'], n=8, base=(0, 0, 2.0))
    cy = 4.4
    # the frame's ring as two halves (a prism's polygon is one loop): left and right of x = 0
    for half in (-1, 1):
        o = [(x, y) for x, y in ellipse_pts(0, cy, 1.22, 1.8, n=40) if half * x >= -1e-6]
        i = [(x, y) for x, y in ellipse_pts(0, cy, 0.98, 1.56, n=40) if half * x >= -1e-6]
        o.sort(key=lambda p: p[1])
        i.sort(key=lambda p: -p[1])
        prism('Body', o + i, 1.85, 2.15, c['sill'], plane='xy')
    prism(glow(c['screen']), ellipse_pts(0, cy, 1.0, 1.58), 1.95, 2.05, c['screen'], plane='xy')
    prism('Body', ellipse_pts(0, cy, 1.0, 1.58), 2.04, 2.12, c['panel'], plane='xy')
    lyrics_xy([(0.0, 4.95, 1.4, 0.0), (0.0, 4.4, 1.7, 0.5), (0.0, 3.85, 1.3, 0.0)], 1.95, c)
    prism('Body', [(-0.3, 6.12), (0.3, 6.12), (0.0, 6.92)], 1.92, 2.08, c['sill'], plane='xy')
    for sx in (-1, 1):
        mic(c, sx * SING_X, MIC_Z, DECK)


STAGES = {'A': stage_a, 'B': stage_b, 'C': stage_c}

GC = {'deck': 'stone', 'edge': 'stone_dark', 'skirt': 'grey', 'frame': 'stone_dark', 'panel': 'stone_dark',
      'screen': 'white', 'text': 'black', 'sung': 'stone_dark', 'cabinet': 'grey', 'sill': 'stone', 'rim': 'stone',
      'cone': 'black', 'bulb': 'white', 'foot': 'stone_dark', 'pole': 'stone_dark', 'clip': 'stone', 'head': 'grey'}

NOTES = {'KaraokeStage_A': 'A: the lyrics window: a square deck behind a step, the screen in a pointed-arch frame '
                           'over a speaker cabinet, marquee bulbs, two mics',
         'KaraokeStage_B': 'B: the prompter: a wedge monitor at the front sloped up at the singers, two speaker '
                           'towers and a drape behind, two mics',
         'KaraokeStage_C': 'C: the magic mirror: a tall oval mirror on a pedestal at the back, the lyrics in its '
                           'glass, two mics',
         'Microphone_A': 'A: a vintage stand: a domed foot, a straight pole, a pill capsule in a gold yoke',
         'Microphone_B': 'B: a tripod boom stand, the capsule angled down at the mouth',
         'Microphone_C': 'C: a gothic candlestick stand, a ball microphone in a gold crescent'}


def sil(kind, k):
    kfurn(f'{kind}_{k}', spots=(kind == 'KaraokeStage'))
    if kind == 'KaraokeStage':
        STAGES[k](GC)
        singers()
    else:
        MICS[k](GC)
    kdone(NOTES[f'{kind}_{k}'])


# --- The chosen two, in the Manor's dress -------------------------------------------------------------

HM = {'deck': 'wood', 'edge': 'wood_dark', 'skirt': 'plum', 'frame': 'wood_dark', 'panel': 'night',
      'screen': 'moonglow', 'text': 'ink', 'sung': 'crimson', 'cabinet': 'plum_dark', 'sill': 'gold', 'rim': 'gold',
      'cone': 'black', 'bulb': 'lamp', 'foot': 'iron', 'pole': 'iron', 'clip': 'gold', 'head': 'stone',
      'grille': 'crimson'}

CHOSEN = {'KaraokeStage': 'A', 'Microphone': 'A'}


def karaoke_stage():
    kfurn('KaraokeStage')
    STAGES[CHOSEN['KaraokeStage']](HM, mic=MICS[CHOSEN['Microphone']])
    singers()
    kdone('a Haunted Manor karaoke stage: a wood deck at 0.8 on a plum skirt; at its back '
          'a dark-wood pointed-arch frame lined with warm marquee bulbs, a pale lyrics screen in its arch (three '
          'lines, the sung half of one in crimson) on a night-blue panel, a gold sill over a plum speaker cabinet '
          'with two gold-rimmed drivers; two vintage microphone stands in front of the singers')


def microphone():
    kfurn('Microphone', spots=False)
    MICS[CHOSEN['Microphone']](HM, z=MIC_STANDALONE_Z)
    kdone('a Haunted Manor microphone stand: a domed iron foot, an iron pole, a gold collar and yoke holding a '
          'silver pill-shaped capsule with a gold band, its top at 4.96')


# --- Review (Workbench on light grey: Studio is running, no EEVEE or Cycles) --------------------------

def people(rec, cx, cz=0.0):
    for a in rec['furniture']['spots']:
        u = rec['attachments'][a]
        _REV['_person'](Vector((cx + u['pos'][0], u['pos'][1], 0)), cz + u['pos'][2])


def at_mic(cx, cz):
    """A person at a standalone microphone, behind it (+Z), facing the room past it as the stage's singers do."""
    _REV['_person'](Vector((cx, 0, 0)), cz + MIC_STANDALONE_Z + 1.2)    # in the square, 0.15 clear of the foot


ROWS_SIL = (('KaraokeStage_A', 'KaraokeStage_B', 'KaraokeStage_C'), ('Microphone_A', 'Microphone_B', 'Microphone_C'))


def lay(fbx, recs, row, z0, labels, gap=6.0, users=True):
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
        if users:
            if recs[n]['furniture']['spots']:
                people(recs[n], cx, z0)
            else:
                at_mic(cx, z0 + (0.7 if i.endswith('_B') else 0.0))     # B's boom reaches back 0.94
        if labels:
            _label(i.split('_')[1], cx, z0 - size[2] / 2 - 3.2)
        x += max(size[0], 3.8) + gap
    _REV['_person'](Vector((x - gap + 2.2, 0, 0)), z0)
    return x


def silhouette_sheet(out, fbx, recs):
    shots = []
    clear()
    x = max(lay(fbx, recs, ROWS_SIL[0], 0.0, True), lay(fbx, recs, ROWS_SIL[1], 12.0, True))
    _REV['_block']('floor', (-3, -0.3, -8), (x + 2, -0.07, 15), (150, 150, 156))
    shots.append(render(out / 'silhouettes_game.png', (-0.35, 1.25, -1.0), (1600, 1000), (-2, 0, -7), (x, 7.2, 14),
                        scale=1.0))
    for k, row in enumerate(ROWS_SIL, 1):
        clear()
        x = lay(fbx, recs, row, 0.0, False, users=(k == 2))
        shots.append(render(out / f'silhouettes_front_{k}.png', (-0.25, 0.2, -1.0), (1600, 650), (-2, -0.3, -3.2),
                            (x, 7.4, 3.2), scale=1.02))
    return shots


NAMES = ['Furniture_KaraokeStage', 'Furniture_Microphone']


def lounge(fbx, recs, singing=True):
    """The two as a karaoke lounge would have them: the stage with its singers, a standalone microphone off its
    front corner with a guest at it, a person beside for scale."""
    clear()
    place(fbx, NAMES[0], (0, 0, 0))
    _squares(0, recs[NAMES[0]]['root']['size'])
    if singing:
        people(recs[NAMES[0]], 0.0)
    place(fbx, NAMES[1], (-6.0, 0, -3.0))
    if singing:
        at_mic(-6.0, -3.0)
    _REV['_person'](Vector((5.5, 0, 0)), -4.0)
    _REV['_block']('floor', (-9, -0.3, -8), (8, -0.07, 5), (150, 150, 156))


def review_final(out, fbx, recs):
    shots = []

    def scene(users=True):
        clear()
        x = 0.0
        for n in NAMES:
            size = recs[n]['root']['size']
            cx = x + max(size[0], 3.8) / 2
            place(fbx, n, (cx, 0, 0))
            _squares(cx, size)
            if users and recs[n]['furniture']['spots']:
                people(recs[n], cx)
            x += max(size[0], 3.8) + 3.0
        _REV['_person'](Vector((x + 0.5, 0, 0)), 0.0)
        _REV['_block']('floor', (-3, -0.3, -6), (x + 4, -0.07, 5), (150, 150, 156))
        return x
    lounge(fbx, recs)
    shots.append(render(out / '1_game_camera.png', (-0.45, 1.28, -1.0), (1400, 800), (-8.5, 0, -6.5), (7.5, 7.2, 4),
                        scale=1.02))
    x = scene()
    lo, hi = (-1.5, 0, -4.5), (x + 2.5, 7.2, 3.5)
    shots.append(render(out / '2_front_three_quarter.png', (-0.7, 0.45, -1.0), (1400, 800), lo, hi, scale=1.02))
    shots.append(render(out / '3_back_three_quarter.png', (0.7, 0.55, 1.0), (1400, 800), lo, hi, scale=1.02))
    x = scene(users=False)
    shots.append(render(out / '4_front_level.png', (0.0, 0.0, -1.0), (1400, 700), (-1.5, -0.3, -4.5),
                        (x + 2.5, 7.4, 3.5), scale=1.02))
    shots.append(render(out / '5_top.png', (0.0, 1.0, -0.02), (1400, 800), (-1.5, 0, -4.5), (x + 2.5, 7.4, 3.5),
                        scale=1.02))
    clear()
    x = 0.0
    for n in NAMES:
        size = recs[n]['root']['size']
        cx = x + max(size[2], 3.8) / 2
        place(fbx, n, (cx, 0, 0), 90)
        _squares(cx, size, 90)
        x += max(size[2], 3.8) + 3.0
    _REV['_person'](Vector((x + 1.0, 0, 0)), 0.0)
    shots.append(render(out / '6_side_level.png', (0.0, 0.0, -1.0), (1400, 600), (-1.5, -0.3, -5), (x + 3, 7.4, 5),
                        scale=1.02))
    # Close-ups: the singers at their microphones from the game's angle, the screen and its frame from in front
    # without them, the standalone microphone beside a person at it.
    clear()
    place(fbx, NAMES[0], (0, 0, 0))
    people(recs[NAMES[0]], 0.0)
    _REV['_block']('floor', (-5, -0.3, -5), (5, -0.07, 5), (150, 150, 156))
    shots.append(render(out / '7_close_singers.png', (-0.5, 0.7, -1.0), (1000, 800), (-3.5, 0, -3.2), (3.5, 7.0, 3),
                        scale=1.0))
    clear()
    place(fbx, NAMES[0], (0, 0, 0))
    _REV['_block']('floor', (-5, -0.3, -5), (5, -0.07, 5), (150, 150, 156))
    shots.append(render(out / '8_close_screen.png', (-0.2, 0.25, -1.0), (1000, 900), (-3.1, 0, -3), (3.1, 7.1, 3),
                        scale=1.0))
    clear()
    place(fbx, NAMES[1], (0, 0, 0))
    at_mic(0.0, 0.0)
    _REV['_person'](Vector((3.0, 0, 0)), 0.0)
    _REV['_block']('floor', (-3, -0.3, -4), (5, -0.07, 3), (150, 150, 156))
    shots.append(render(out / '9_close_mic.png', (-0.6, 0.35, -1.0), (1000, 900), (-2.2, 0, -2.0), (5.0, 5.2, 1.5),
                        scale=1.0))
    return shots


# --- The set ------------------------------------------------------------------------------------------

def main():
    K.use_palette(HM_PALETTE)
    if GREY:
        K.IMPORT_CHECKS = False         # drafts with _A/_B/_C ids, not for import
        K.start_set(SET + '/silhouettes')
        for kind in ('KaraokeStage', 'Microphone'):
            for k in 'ABC':
                sil(kind, k)
        recs = {p.name: r for p, r, _ in K.BUILT}
        out = K.ROOT / 'blender' / SET / 'silhouettes'
        (out / 'manifest.json').write_text(json.dumps({'pieces': recs}, indent=1))
        bad = {p.name: r.get('faults') for p, r, _ in K.BUILT if r.get('faults')}
        print('SILHOUETTE FAULTS', bad, flush=True)
        if not K.NOPREVIEW:
            print('SHEETS', silhouette_sheet(out / 'review', out / 'fbx', recs), flush=True)
        return
    K.start_set(SET)
    karaoke_stage()
    microphone()
    built = [p.name for p, _, _ in K.BUILT]
    K.end_set('Haunted Manor: the Karaoke Lounge\'s stage and microphone (GDD A.13)', [(built, 3.0, 1.0)],
              sheet=False)
    out = K.ROOT / 'blender' / SET
    manifest = json.loads((out / 'manifest.json').read_text())
    patch_fixup(out / 'import_fixup.luau', manifest)
    val = json.loads((out / 'validation.json').read_text())
    val['spots'] = {n: {'spots': r['furniture']['spots'],
                        'checked': ('spots_check on the built and the re-imported triangles: Use_<n> from 1 without '
                                    'a gap, a Pose from MODELS.md\'s list, a level LookVector, no two spots on one '
                                    'square; a Stand inside the footprint (on the deck) by stand_on_faults: the '
                                    f'deck flat to {USE_SURFACE_TOL} under both feet, the standing 5-stud person '
                                    '(legs, torso, arms out to 3.8 across, head; each block shrunk by '
                                    f'{SIT_GAP}) clear of the body')
                        if r['furniture']['spots'] else 'no visitors\' spots (A.13.2: not a key piece)'}
                    for n, r in manifest['pieces'].items()}
    val['pieces_rows'] = {n: {k: ROWS[n[len('Furniture_'):]][k] for k in ('w', 'd', 'layer', 'height', 'keyFor')}
                          | {'model_top': manifest['pieces'][n]['furniture']['model_top']} for n in built}
    val['height_findings'] = {
        'note': 'Pieces.luau\'s height against the model\'s top, a finding (not refused): the row must say it',
        **{n: FINDINGS[n] for n in built if n in FINDINGS}}
    val['not_validated'] = val.get('not_validated', [])[:1] + [
        'the attachments and each Use_<n> Pose attribute exist only in manifest.json until import_fixup.luau makes '
        'them', 'a visitor walking onto the deck (0.8 up, no step) and singing: no walker or clip has '
        'run', 'the screen lit: import_fixup makes Glow_Cold_1 Neon; no code changes what it shows',
        'the two singers\' figures side by side: each is checked against the piece, not against each other']
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
