"""Bayou Spa (Location 3): the hotel kit's third set, a draft for August's review (LAUNCH.md workstream 5).

What the code reads from `ServerStorage.HotelKit.BayouSpa` and the built-rooms set (blender/rooms/bayou_spa/)
does not make: the FrontDesk, the stair core (StairCore, StairCoreTop), the HotelSign, the RoomPlaque, and
the location's decor of Pieces.luau (location = 3: MossMound, FireflyJar, MudPot, HerbRack, SteamVent) with
the five every kit has (`always`: Bench, UrnPlanter, RugRunner, RugCorner, RugSquare). Rooms are built from
walls now (A.12) and the Lobby shell retired into Facade_Entrance (tools/build_facades.py, style bayou_spa),
so neither is here. Each piece keeps the frames, colliding boxes and attachments of the Luau blockout
(src/server/HotelKit.luau, K.blockout_*), as the Manor's and the Lodge's do: only colour and dressing differ.

The look is the built-rooms set's (its README): a swamp spa, cosy not grim; weathered cypress, soft sage,
woven rattan, lily greens and lotus pinks, mud and still water, brass and copper, firefly light. Moss is
used lightly (a tuft at a corner, never a garland along a whole edge: the kits' fourth blind review, finding
9, recommends it and it is the reversible choice).

    blender -b --python-exit-code 1 -P tools/build_hotel_bayou_spa.py [-- nopreview] [-- only A,B]

Writes blender/hotel/bayou_spa/: fbx/<Name>.fbx, manifest.json, validation.json, import_fixup.luau,
review/contact_sheet.png, the .blend.
"""
import ast
import math
import sys
from pathlib import Path

from mathutils import Matrix, Vector

sys.path.insert(0, str(Path(__file__).resolve().parent))
import hotel_kit as K  # noqa: E402
from hotel_kit import (begin, finish, box, span, cyl, lathe, sphere, prism, declare, attach,  # noqa: E402
                       picture, at, T, STAIR_S)

TOOLS = Path(__file__).resolve().parent
SET = 'hotel/bayou_spa'


def _lift(path, names, ns):
    """Top-level functions and literal assignments called `names` from another build script, without
    running it (as tools/build_facades.py does): the built-rooms set's palette and its Bayou shapes."""
    for node in ast.parse(path.read_text(encoding='utf8')).body:
        if isinstance(node, ast.FunctionDef) and node.name in names:
            exec(compile(ast.Module([node], []), str(path), 'exec'), ns)
        elif isinstance(node, ast.Assign) and getattr(node.targets[0], 'id', None) in names:
            ns[node.targets[0].id] = ast.literal_eval(node.value)
    missing = [n for n in names if n not in ns]
    assert not missing, f'{path.name}: {missing} not found'
    return ns


_NS = {'box': box, 'span': span, 'cyl': cyl, 'lathe': lathe, 'sphere': sphere, 'prism': prism, 'at': at,
       'math': math, 'Matrix': Matrix, 'Vector': Vector}
_lift(TOOLS / 'build_built_rooms.py', ['BS_PALETTE', 'seg', 'firefly_lantern', 'lotus', 'frog', 'lily_pad',
                                       'cattails', 'boulder'], _NS)
seg, firefly_lantern, lotus, lily_pad = _NS['seg'], _NS['firefly_lantern'], _NS['lotus'], _NS['lily_pad']
cattails, boulder = _NS['cattails'], _NS['boulder']

# The built rooms' palette and the Locations.luau colours of id 3 (ground 60,80,50; facade 80,110,70;
# trim 200,230,120).
PALETTE = list(_NS['BS_PALETTE']) + [('ground', (60, 80, 50)), ('facade', (80, 110, 70)), ('trim', (200, 230, 120))]

DECOR = ['MossMound', 'FireflyJar', 'MudPot', 'HerbRack', 'SteamVent',
         'Bench', 'UrnPlanter', 'RugRunner', 'RugCorner', 'RugSquare']   # the last five: every kit's


def into(part, fn, *a, **kw):
    """Run a lifted shape (they all draw into 'Body') and move what it drew into `part`."""
    had = K.P.parts.pop('Body', None)
    fn(*a, **kw)
    drawn = K.P.parts.pop('Body', None)
    if had is not None:
        K.P.parts['Body'] = had
    if drawn is None:
        return
    dst = K._part(part, None)
    base = len(dst[0])
    dst[0].extend(drawn[0])
    dst[1].extend([[base + i for i in f] for f in drawn[1]])
    dst[2].extend(drawn[2])


def tuft(part, x, y, z, r=0.32, droop=0.0):
    """One short, light tuft of moss sitting on an edge at (x, y, z), a lobe drooping `droop` over it."""
    sphere(part, (x, y + 0.06, z), (r, 0.12, r * 0.85), 'moss_light', n=7, rings=3)
    sphere(part, (x + 0.12, y + 0.1, z + 0.08), (r * 0.6, 0.12, r * 0.55), 'moss', n=6, rings=3)
    if droop:
        sphere(part, (x - 0.05, y - droop / 2, z - r), (r * 0.45, droop / 2 + 0.06, 0.1), 'moss_light',
               n=6, rings=3)


# --- The front desk (MODELS.md, "Front desk") ------------------------------------------------------------

def front_desk():
    """A cypress counter with three woven rattan panels in light cypress frames, a drift-grey top, a brass bell at the check-in prompt, a lily-green ledger, a copper
    till, a rattan-shaded lamp, and behind the clerk the key rack: a cypress cabinet, a sage board of brass,
    lotus and lily tags, and a round clock."""
    begin('FrontDesk', 'Desk', (K.DESK_W, 0.2, K.DESK_D))
    (lo, hi), (tlo, thi) = K.DESK_COUNTER, K.DESK_TOP
    span('Counter', lo, hi, 'cypress_dark', bevel=0.1)
    zf = lo[2]
    span('Dressing', (lo[0] - 0.04, 0, zf - 0.06), (hi[0] + 0.04, 0.35, hi[2] + 0.04), 'stone_dark', bevel=0.04)
    for xc in (-3.0, 0.0, 3.0):
        span('Dressing', (xc - 1.3, 0.55, zf - 0.04), (xc + 1.3, 3.15, zf + 0.02), 'cypress_light', bevel=0.03)
        span('Dressing', (xc - 1.08, 0.75, zf - 0.07), (xc + 1.08, 2.95, zf - 0.02), 'rattan')
        y = 0.93
        while y < 2.85:                                   # the weave: a darker reed every 0.36
            span('Dressing', (xc - 1.08, y, zf - 0.09), (xc + 1.08, y + 0.1, zf - 0.06), 'rattan_dark')
            y += 0.36
    span('Counter', tlo, thi, 'drift_light', bevel=0.05)
    span('Dressing', (tlo[0] + 0.02, 3.42, tlo[2] - 0.02), (thi[0] - 0.02, 3.5, thi[2] - 0.02), 'cypress')
    K.desk_bell('Dressing', 0.0, thi[1], lo[2] + 0.4, 'brass')          # at the check-in prompt
    span('Dressing', (0.8, thi[1], lo[2] + 0.4), (1.8, thi[1] + 0.15, lo[2] + 1.3), 'lily_dark', bevel=0.03)
    span('Dressing', (0.85, thi[1] + 0.15, lo[2] + 0.45), (1.75, thi[1] + 0.17, lo[2] + 1.25), 'linen')
    K.desk_till(body='copper', keys='linen', drawer='brass', screen='linen')
    K.desk_lamp('brass', 'rattan')
    K.desk_keyrack(cabinet='cypress_dark', drawer='cypress_light', knob='brass', board='sage',
                   tags=('brass', 'lotus', 'lily'), cornice='cypress_light', face='linen', hands='black')
    for aname, (pos, look) in K.blockout_attachments('Desk').items():
        attach(aname, pos, look)
    finish(note='a cypress counter with three woven rattan panels in light cypress frames, a drift-grey top '
                'and a brass bell, a lily-green ledger, a copper till, a rattan-shaded lamp, the '
                'key rack (cypress, a sage board of brass, lotus and lily tags) and its clock')


# --- The stair core (MODELS.md, "Stairs") -------------------------------------------------------------------

STAIR_BANDS = [(0, 1.0, 'cypress_dark'), (1.0, 3.4, 'cypress'), (3.4, 3.62, 'cypress_light')]


def stairs(top):
    name = 'StairCoreTop' if top else 'StairCore'
    begin(name, 'Stairs', (STAIR_S, 0.2, STAIR_S))
    # Every walked box is the blockout's, exactly (K.blockout_stairs); only colour and chamfers are added.
    for sname, (c, s) in K.blockout_stairs(top).items():
        c, s = Vector(c), Vector(s)
        lo, hi = c - s / 2, c + s / 2
        if sname.startswith(('Step_', 'Landing')):
            # A woven rattan runner on cypress treads; their ends lie in the walls' outer faces.
            ends = {'top': 'rattan', 'left': 'cypress_dark', 'right': 'cypress_dark', 'rest': 'cypress'}
            if sname == 'Landing':
                ends['back'] = 'cypress_dark'
            box(sname, c, s, ends, bevel=0.06)
        elif sname.startswith('Wall_') or sname == 'Divider':
            h = hi.y
            bands = list(STAIR_BANDS) + [(3.62, h - 0.4, 'sage'), (h - 0.4, h, 'cypress_light')]
            outer = {'Wall_Left': 'left', 'Wall_Right': 'right', 'Wall_Back': 'back'}.get(sname)
            for y0, y1, colr in bands:   # the outer face one colour: the step ends lie in it
                span(sname, (lo.x, y0, lo.z), (hi.x, y1, hi.z), {outer: 'cypress_dark', 'rest': colr} if outer else colr,
                     bevel=0.04)
        elif sname == 'Rail_Top':
            span(sname, (lo.x, hi.y - 0.35, lo.z), (hi.x, hi.y, hi.z), 'cypress_light', bevel=0.06)
            span(sname, (lo.x, lo.y, lo.z + 0.05), (hi.x, lo.y + 0.3, hi.z - 0.05), 'cypress_dark', bevel=0.04)
            span(sname, (lo.x, lo.y, lo.z), (lo.x + 0.4, hi.y, hi.z), 'cypress_dark', bevel=0.05)
            span(sname, (hi.x - 0.4, lo.y, lo.z), (hi.x, hi.y, hi.z), 'cypress_dark', bevel=0.05)
            x = lo.x + 0.9
            while x < hi.x - 0.6:
                cyl(sname, (x, lo.y + 0.3, c.z), 0.1, s.y - 0.65, 'rattan_dark', n=6)
                x += 0.6
    for aname, (pos, look) in K.blockout_attachments('Stairs').items():
        attach(aname, pos, look)
    hs = STAIR_S / 2
    # A firefly jar hung from a crooked cypress bracket high on the left wall, over the flight up.
    xw, yb, zb = -hs + T, 14.6, -4.0
    span('Dressing', (xw, yb - 0.5, zb - 0.25), (xw + 0.12, yb + 0.5, zb + 0.25), 'cypress_dark', bevel=0.03)
    seg('Dressing', (xw + 0.1, yb, zb), (xw + 0.85, yb + 0.25, zb), 0.07, 'cypress')
    seg('Dressing', (xw + 0.85, yb + 0.25, zb), (xw + 0.95, yb + 0.05, zb), 0.05, 'cypress')
    into('Dressing', firefly_lantern, 'Glow_Warm_1', (xw + 0.95, yb + 0.05, zb), h=0.6, r=0.24)
    K.stair_handrails('cypress_dark', 'brass')
    K.stair_soffits('cypress_dark')
    # A picture over the landing: the moon over still water, a cypress on the left bank, two lily pads.
    yp = K.STAIR_LANDING_Y + (3.6 if not top else 4.6)
    zf = hs - T
    picture((0, yp, zf), (2.6, 2.4), 'cypress_light', 'plum')
    span('Dressing', (-1.05, yp - 0.95, zf - 0.16), (1.05, yp - 0.2, zf - 0.1), 'water_deep')
    cyl('Dressing', (0, 0, 0), 0.32, 0.05, 'moonstone', n=12, m=at((0.45, yp + 0.4, zf - 0.12), rx=-90))
    prism('Dressing', [(-1.0, yp - 0.2), (-0.55, yp - 0.2), (-0.7, yp + 0.2), (-0.62, yp + 0.62), (-0.9, yp + 0.75),
                       (-1.05, yp + 0.5)], zf - 0.2, zf - 0.15, 'moss_dark', plane='xy')
    for x, y in ((-0.2, yp - 0.55), (0.55, yp - 0.75)):
        cyl('Dressing', (0, 0, 0), 0.16, 0.04, 'lily', n=8, m=at((x, y, zf - 0.15), rx=-90))
    finish(note='the walker-proven switchback in cypress under a woven rattan runner, cypress wainscot and sage '
                'walls, a firefly jar on a crooked bracket, a moonlit bayou picture'
                + (', railed round the stairwell' if top else ''))


# --- The hotel sign (MODELS.md, "Facade and sign": a 16 x 6 Board at (0, 8, 0)) -----------------------------

def hotel_sign():
    begin('HotelSign', 'Sign', (16, 0.2, 1))
    for name, x in (('PostLeft', -7), ('PostRight', 7)):
        span(name, (x - 0.45, 0, -0.45), (x + 0.45, 0.4, 0.45), 'stone_dark', bevel=0.08)
        # A cypress post flaring at its root; it ends under the Board (bottom y 5), clear of its text face.
        lathe(name, [(0.5, 0.4), (0.36, 1.1), (0.32, 4.6), (0.4, 4.8), (0.4, 5.0)], 'cypress', n=8, base=(x, 0, 0))
    # The Board: a plain box, its front (-Z) the SurfaceGui's face (the text is light: a dark water teal).
    box('Board', (0, 8, 0), (16, 6, 0.6), {'front': 'water_deep', 'back': 'cypress_dark', 'rest': 'cypress'}, bevel=0.08)
    # The crest: a low round-topped cypress board over it, a lotus in the middle on a lily pad, a crescent
    # moon lit behind it, a light moss tuft on each upper corner of the board.
    crest = K.round_arch_points(-5.5, 5.5, 11.0, 12.6, n=8)
    prism('Crest', crest, -0.25, 0.25,
          {'front': 'cypress_light', 'back': 'cypress', 'rest': 'cypress_dark'}, plane='xy')
    span('Crest', (-8, 10.95, -0.35), (8, 11.3, 0.35), 'cypress_dark', bevel=0.1)
    declare('Crest', False)
    moon = [(1.05 * math.cos(math.radians(a)), 12.75 + 1.05 * math.sin(math.radians(a))) for a in range(-70, 251, 20)]
    moon += [(0.32 + 0.82 * math.cos(math.radians(a)), 12.9 + 0.82 * math.sin(math.radians(a)))
             for a in range(240, -71, -20)]
    prism('Glow_Cold_1', moon, 0.0, 0.12, 'moonglow', plane='xy')
    cyl('Crest', (0, 0, 0), 1.3, 0.08, 'lily', n=12, m=at((0, 12.15, -0.22), rx=-90), scale=(1, 0.45))
    for k in range(5):                      # the lotus's petals, flat on the crest's face, fanned
        a = math.radians(-64 + 32 * k)
        sphere('Crest', (0.85 * math.sin(a), 12.5 + 0.62 * math.cos(a), -0.33 - 0.015 * k), (0.32, 0.66, 0.07),
               'lotus' if k % 2 == 0 else 'lotus_light', n=6, rings=3)
    sphere('Crest', (0, 12.5, -0.42), (0.3, 0.24, 0.07), 'lotus_heart', n=6, rings=3)
    for x in (-7.3, 7.3):
        tuft('Crest', x, 10.97, 0.08, r=0.38, droop=0.55)
    finish(note='cypress posts flaring at their roots, a 16 x 6 board (dark water teal) for the SurfaceGui, a '
                'round cypress crest with a lotus on a lily pad and a lit crescent moon, a light moss tuft on '
                'each corner')


# --- Decor (MODELS.md, "Decor": origin at the base centre, front -Z, fw x fd squares of 3 studs) -----------

decor = K.decor


def d_moss_mound():
    decor('MossMound', 1, 1, 'Floor')
    prof = [(1.02, 0), (1.06, 0.18), (0.9, 0.62), (0.55, 0.95), (0.0, 1.06)]
    lathe('Body', prof, 'moss', n=18)

    def surface(x, z):
        d = (x * x + z * z) ** 0.5
        for (r0, y0), (r1, y1) in zip(prof[2:], prof[3:]):
            if r1 <= d <= r0:
                return y1 + (y0 - y1) * (d - r1) / (r0 - r1)
        return prof[2][1]
    for (x, z), r in (((-0.45, -0.45), 0.32), ((0.5, -0.2), 0.28), ((0.05, 0.45), 0.34)):   # lighter cushions
        sphere('Body', (x, surface(x, z) - 0.02, z), (r, 0.14, r), 'moss_light', n=7, rings=3)
    for x, z, s in ((0.3, -0.25, 1.0), (0.55, 0.05, 0.7)):          # two toadstools, lotus-pink caps
        cyl('Body', (x, 0.72, z), 0.07 * s, 0.4 * s, 'linen', n=6)
        lathe('Body', [(0.0, 0.72 + 0.36 * s), (0.25 * s, 0.74 + 0.36 * s), (0.18 * s, 0.84 + 0.36 * s),
                       (0.0, 0.9 + 0.36 * s)], 'lotus', n=8)
    for x, z in ((-0.95, 0.4), (0.85, 0.7), (-0.2, -0.95)):        # pebbles at its foot
        sphere('Body', (x, 0.09, z), (0.14, 0.09, 0.12), 'stone', n=6, rings=3)
    finish(note='a soft moss mound with lighter cushions, two lotus-pink toadstools, pebbles at its foot')


def d_firefly_jar():
    decor('FireflyJar', 1, 1, 'Floor')
    lathe('Body', [(0.62, 0), (0.64, 0.17), (0.58, 0.2), (0.0, 0.2)], 'cypress', n=12)       # a small stump slice
    # The jar: its glowing heart of fireflies (Glow_Warm_1, the code's Neon and light) seen between the ribs of
    # a moonstone glass cage, a base ring and a shoulder (nothing is see-through, so the glass is a cage).
    lathe('Glow_Warm_1', [(0.0, 0.26), (0.44, 0.3), (0.48, 0.5), (0.48, 1.12), (0.36, 1.26), (0.0, 1.3)], 'firefly', n=12)
    lathe('Body', [(0.5, 0.2), (0.56, 0.24), (0.56, 0.38), (0.5, 0.4)], 'moonstone', n=12, closed=True)
    for k in range(8):
        a = math.radians(45 * k + 22.5)
        seg('Body', (0.53 * math.cos(a), 0.38, 0.53 * math.sin(a)), (0.53 * math.cos(a), 1.14, 0.53 * math.sin(a)),
            0.05, 'moonstone', n=4)
    lathe('Body', [(0.54, 1.12), (0.56, 1.18), (0.42, 1.32), (0.35, 1.36)], 'moonstone', n=12)
    cyl('Body', (0, 1.34, 0), 0.37, 0.14, 'brass', n=12)
    lathe('Body', [(0.28, 1.48), (0.2, 1.53), (0.0, 1.55)], 'linen', n=10)
    # The wire bail over the lid.
    pts = [(0.37 * math.cos(math.radians(a)), 1.41 + 0.22 * math.sin(math.radians(a)), 0) for a in range(0, 181, 30)]
    for a, b in zip(pts, pts[1:]):
        seg('Body', a, b, 0.025, 'iron', n=4)
    for x, y, z in ((0.5, 1.62, -0.3), (-0.42, 1.72, 0.12)):    # two flown out over it
        sphere('Glow_Warm_1', (x, y, z), (0.08, 0.08, 0.08), 'firefly', n=6, rings=3)
    finish(note='a jar glowing with fireflies (Glow_Warm_1) inside a moonstone glass cage of ribs, a brass lid, a '
                'linen cap and a wire bail, on a small cypress stump slice; two fireflies flown out over it')


def d_mud_pot():
    decor('MudPot', 1, 1, 'Floor')
    for k in range(3):                                   # three flat stones under it
        a = math.radians(90 + 120 * k)
        boulder((0.62 * math.cos(a), 0, 0.62 * math.sin(a)), 0.32, 0.22, 'stone_dark')
    lathe('Body', [(0.4, 0.16), (0.78, 0.32), (0.95, 0.62), (0.9, 0.95), (0.78, 1.08), (0.84, 1.14), (0.8, 1.2),
                   (0.68, 1.2)], 'mud_light', n=14)
    lathe('Body', [(0.69, 1.02), (0.0, 1.04)], 'mud_dark', n=14)       # the mud, under the rim
    for (x, z), r in (((0.2, -0.15), 0.12), ((-0.25, 0.2), 0.09), ((0.05, 0.3), 0.06), ((-0.3, -0.25), 0.07)):
        sphere('Body', (x, 1.04, z), (r, r * 0.8, r), 'mud', n=6, rings=3)
    lathe('Body', [(0.955, 0.6), (0.98, 0.6), (0.98, 0.72), (0.955, 0.72)], 'copper', n=14, closed=True)
    seg('Body', (0.15, 0.95, 0.15), (0.75, 1.6, 0.55), 0.06, 'cypress', n=6)          # a paddle leant in it
    finish(note='a squat clay pot of bubbling mud with a copper band on three flat stones, a cypress paddle '
                'leant in it')


def d_herb_rack():
    decor('HerbRack', 1, 1, 'Floor')
    # An A-frame drying ladder of cypress, its feet 1.9 apart front to back, three rungs a side.
    for x in (-0.85, 0.85):
        for zf in (-1.0, 1.0):
            seg('Body', (x, 0.03, zf), (x, 3.75, zf * 0.12), 0.08, 'cypress', n=6)
    span('Body', (-0.95, 3.66, -0.2), (0.95, 3.86, 0.2), 'cypress_dark', bevel=0.05)       # the ridge
    herbs = (('sage', 'sage_light'), ('lavender', 'plum'), ('herb', 'chamomile'), ('sage_light', 'herb'))
    k = 0
    for y in (1.35, 2.25, 3.1):
        for zf in (-1.0, 1.0):
            z = zf * (1.0 - 0.88 * y / 3.75)
            seg('Body', (-0.85, y, z), (0.85, y, z), 0.05, 'cypress_light', n=6)
            if zf < 0:                                   # bundles hung head down from the front rungs only
                for x in ((-0.45, 0.0, 0.45) if y < 3 else (-0.3, 0.3)):
                    stem, tip = herbs[k % len(herbs)]
                    k += 1
                    cyl('Body', (x, y - 0.16, z), 0.06, 0.16, 'rattan_dark', n=5)           # the twine
                    for i in range(3):                   # a spray of stems fanning down, leaves at their tips
                        dx = (i - 1) * 0.1
                        dz = 0.05 * ((i % 2) * 2 - 1)
                        end = (x + dx * 1.8, y - 0.72 + 0.06 * abs(i - 1), z + dz)
                        seg('Body', (x + dx * 0.3, y - 0.15, z), end, 0.022, stem, n=4)
                        sphere('Body', end, (0.07, 0.13, 0.05), tip if i % 2 else stem, n=5, rings=3)
    # A rattan basket of cut herbs at its foot.
    lathe('Body', [(0.36, 0.0), (0.46, 0.34), (0.42, 0.36), (0.0, 0.36)], 'rattan', n=10, base=(0.05, 0, -0.05))
    for (x, z), c in (((-0.05, -0.1), 'herb'), ((0.15, 0.05), 'lavender'), ((0.05, -0.2), 'sage_light')):
        sphere('Body', (x, 0.42, z), (0.18, 0.12, 0.16), c, n=6, rings=3)
    finish(note='an A-frame cypress drying ladder hung with bundles of sage, lavender, chamomile and herbs, a '
                'rattan basket of cut herbs at its foot')


def d_steam_vent():
    decor('SteamVent', 1, 1, 'Floor')
    for k in range(7):                                   # a ring of stones round the vent
        a = math.radians(360 * k / 7 + 10)
        r = 0.72 + 0.06 * (k % 2)
        boulder((r * math.cos(a), 0, r * math.sin(a)), 0.28 - 0.04 * (k % 3), 0.42 - 0.06 * (k % 2),
                'stone' if k % 2 else 'stone_dark')
    lathe('Body', [(0.62, 0.0), (0.62, 0.12), (0.0, 0.12)], 'water_deep', n=12)
    lathe('Body', [(0.3, 0.12), (0.34, 0.16), (0.0, 0.17)], 'mud_dark', n=10)
    # An iron grate over the vent's mouth.
    lathe('Body', [(0.34, 0.14), (0.42, 0.14), (0.42, 0.22), (0.34, 0.22)], 'iron', n=10, closed=True)
    for k in range(3):
        box('Body', (0, 0.19 + 0.01 * k, 0), (0.7, 0.05, 0.06), 'iron', m=at((0, 0, 0), ry=60 * k))   # off each other's faces
    # The steam: a thin wisp curling up off the grate, each puff smaller and leaner than the one under it.
    for k in range(7):
        t = k / 6
        a = math.radians(140 * k)
        sphere('Body', (0.16 * t * math.cos(a) + 0.04, 0.45 + 1.4 * t, 0.16 * t * math.sin(a)),
               (0.26 - 0.13 * t, 0.3 - 0.08 * t, 0.26 - 0.13 * t), 'steam' if k % 2 == 0 else 'white', n=8, rings=4)
    finish(note='an iron grate in a ring of stones over a dark pool, a thin wisp of steam curling up off it')


def d_bench():
    decor('Bench', 3, 1, 'Floor')
    K.decor_bench(7.0, frame='cypress_dark', cushion='sage', back='rattan')
    finish(note='the old lobby bench in dark cypress, a sage cushion, woven rattan back rails')


def d_urn_planter():
    decor('UrnPlanter', 1, 1, 'Floor')
    lathe('Body', [(0.55, 0), (0.6, 0.12), (0.42, 0.3), (0.55, 0.7), (0.82, 1.15), (0.92, 1.38), (0.86, 1.45),
                   (0.0, 1.45)], 'stone_light', n=12)
    lathe('Body', [(0.85, 1.3), (0.0, 1.42)], 'mud_dark', n=12)
    into('Body', cattails, 0.25, 0.15, y=1.4, k=3, tall=1.5)
    for k in range(6):                                   # fern fronds arching out of it
        a = 60 * k + 15
        prism('Body', [(-0.09, 0.0), (0.09, 0.0), (0.05, 0.9), (0.0, 1.05), (-0.05, 0.9)], -0.02, 0.02, 'lily',
              plane='xy', m=at((0.25 * math.cos(math.radians(a)), 1.4, 0.25 * math.sin(math.radians(a))),
                               ry=-a) @ Matrix.Rotation(math.radians(-45), 4, 'Z'))
    lotus((-0.35, 1.42, -0.3), s=0.9)
    finish(note='a pale stone urn of cattails, arching fern fronds and a lotus')


def d_rug(kind, fw, fd, note):
    decor({'runner': 'RugRunner', 'corner': 'RugCorner', 'square': 'RugSquare'}[kind], fw, fd, 'Rug')
    K.rug(kind, border='cypress_dark', field='rattan', pin='rattan_dark', motif='lily', motif_inner='lotus')
    finish(note=note)


def room_plaque():
    """The plaque over a room's door (MODELS.md, "Room plaque"): the code writes light text on its Face."""
    p = begin('RoomPlaque', 'Cosmetic', (1, 0.2, 0.2), root_centre=(0, 0, 0.15))
    p.allowed = ((-2.1, -0.8, -0.1), (2.1, 0.8, 0.31))
    span('Board', (-2.0, -0.65, 0.0), (2.0, 0.65, 0.3), 'cypress', bevel=0.06)
    span('Board', (-1.85, -0.5, -0.03), (1.85, 0.5, 0.0), 'sage_light', bevel=0.02)
    span('Face', (-1.75, -0.42, -0.06), (1.75, 0.42, -0.03), 'cypress_dark')
    for x in (-1.92, 1.92):
        sphere('Board', (x, 0, -0.02), (0.05, 0.05, 0.03), 'brass', n=6, rings=3)
    for part in list(K.P.parts):
        declare(part, False)
    finish(proxy=False, note='a cypress plaque with a sage rim and brass pins; the code writes on its dark Face')


DECOR_BUILD = {'MossMound': d_moss_mound, 'FireflyJar': d_firefly_jar, 'MudPot': d_mud_pot,
               'HerbRack': d_herb_rack, 'SteamVent': d_steam_vent, 'Bench': d_bench, 'UrnPlanter': d_urn_planter,
               'RugRunner': lambda: d_rug('runner', 4, 2, 'a woven rattan runner, dark cypress borders on its long '
                                                         'sides, lily and lotus diamonds; its ends open'),
               'RugCorner': lambda: d_rug('corner', 2, 2, "the runner's corner: bordered on +X and +Z"),
               'RugSquare': lambda: d_rug('square', 4, 4, 'a 12 x 12 woven rattan rug with a lily and lotus medallion')}


def main():
    K.use_palette(PALETTE)
    K.start_set(SET)
    order = ([('FrontDesk', front_desk), ('StairCore', lambda: stairs(False)), ('StairCoreTop', lambda: stairs(True)),
              ('HotelSign', hotel_sign), ('RoomPlaque', room_plaque)]
             + [(f'Decor_{n}', DECOR_BUILD[n]) for n in DECOR])
    refused = []
    for name, fn in order:
        if not K.want(name):
            continue
        try:
            fn()
        except K.Refused as e:
            print(str(e), flush=True)
            refused.append(name)
    rows = [(['FrontDesk', 'HotelSign', 'StairCore', 'StairCoreTop'], 6, 1.0),
            ([f'Decor_{n}' for n in DECOR] + ['RoomPlaque'], 2.5, 2.0)]
    K.end_set('Bayou Spa hotel kit (Location 3), a draft', rows)
    if refused:
        raise SystemExit(f'REFUSED: {refused}')


main()
