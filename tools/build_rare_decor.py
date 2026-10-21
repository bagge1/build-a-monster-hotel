"""Rare decor sets and souvenirs (GDD A.11.3; MODELS.md, "Rare decor sets and souvenirs").

Four folders, one set of five per launch location plus the souvenir:

    blender/decor/count_study/   Haunted Manor's rare set (location 1), five Decor_CountStudy_<Piece>:
                                 Portrait (Wall 2 x 1), Globe, Clock, Bust (Floor 1 x 1), Rug (Rug 3 x 2).
                                 One look: crimson, black and gold, the set's crest (a gold bat) on every
                                 piece, a glow on three of them; each piece read from above.
    blender/decor/aurora_lodge/  Frostfang Lodge's (location 2), five Decor_AuroraLodge_<Piece>: Painting
                                 (Wall 2 x 1), WolfStatue, Telescope (Floor 1 x 1), Sleigh (Floor 2 x 1), Rug
                                 (Rug 3 x 2). Navy, snow, ice and gold, the aurora glowing; the crest a gold
                                 wolf's head (the Frostfang) with a snow mask on every piece.
    blender/decor/lantern_grove/ Bayou Spa's (location 3), five Decor_LanternGrove_<Piece>: StainedGlass
                                 (Wall 2 x 1), Lamp, Gramophone (Floor 1 x 1), Pirogue (Floor 2 x 1), Rug
                                 (Rug 3 x 2). Cypress, brass, plum dusk and teal water, lantern and firefly
                                 light; the crest a dragonfly (pale wings, brass body) on every piece.
    blender/decor/souvenir/      Souvenir_Base: one 1 x 1 keepsake, a prize rosette under a bell jar on a
                                 plinth, for every species: Ribbon and Trim tinted by the code, the emblem on
                                 Medal's top, the name on Badge's front, Glass the jar.

Every piece keeps MODELS.md's "Decor" rules through the kit (tools/hotel_kit.py): footprint and 0.4 inset,
layer, nothing colliding, glows their own parts, no coplanar faces; plus nothing floating (a Wall piece may
hang: tools/build_built_rooms.py's grounded_check, build_built_rooms_more.py's hung_check, lifted here
unchanged). A set's rows (SET_ROWS, LODGE_ROWS, GROVE_ROWS) are what Pieces.luau must say: where the code
session has written a row the kit holds the model to it, its height included; where not, w, d and layer are
checked against this script and the height is recorded in the manifest (`pieces_row`) for the row.

    blender -b --python-exit-code 1 -t 4 -P tools/build_rare_decor.py [-- sets <dirs>] [-- only <names>]
        [-- nopreview]          <dirs>: count_study, aurora_lodge, lantern_grove, souvenir (default: all)

Review: Workbench on light grey only (Studio runs: no EEVEE or Cycles): review/set_sheet.png (each piece on
its squares beside the 5-stud person), review/elevations_sheet.png (front and side at floor level),
review/topdown.png (the set laid out in a 2 x 2 cell room, straight down) with topdown_phone.png (the same
at a phone's size) and review/raised.png (the build camera's raised angle); the souvenir's
review/souvenir_sheet.png (four species' tints, the cloche hidden and as built, from above).
"""
import ast
import json
import math
import shutil
import sys
from pathlib import Path

import bpy
import numpy as np
from mathutils import Matrix, Vector

sys.path.insert(0, str(Path(__file__).resolve().parent))
import hotel_kit as K  # noqa: E402
from hotel_kit import box, span, cyl, lathe, sphere, prism, at, finish  # noqa: E402

TOOLS = Path(__file__).resolve().parent


def _lift(path, names, ns):
    """Top-level functions and literal assignments called `names` from another script, without running it."""
    src = path.read_text(encoding='utf8')
    for node in ast.parse(src).body:
        if isinstance(node, ast.FunctionDef) and node.name in names:
            exec(compile(ast.Module([node], []), str(path), 'exec'), ns)
        elif isinstance(node, ast.Assign) and getattr(node.targets[0], 'id', None) in names:
            ns[node.targets[0].id] = ast.literal_eval(node.value)
    missing = [n for n in names if n not in ns]
    assert not missing, f'{path.name}: {missing} not found'
    return ns


NS = {'bpy': bpy, 'K': K, 'Vector': Vector, 'Matrix': Matrix, 'math': math, 'np': np, 'box': box,
      'span': span, 'cyl': cyl, 'lathe': lathe, 'sphere': sphere, 'prism': prism, 'at': at}
_lift(TOOLS / 'build_built_rooms.py', ['GROUND_TOL', 'grounded_check', '_import', 'place', 'render', 'clear',
                                       'BS_PALETTE', 'seg', 'firefly_lantern', 'lotus', 'lily_pad', 'cattails'], NS)
_lift(TOOLS / 'build_built_rooms_more.py', ['hung_check'], NS)
_lift(TOOLS / 'build_cosmetics_hotel.py', ['_flat', '_block', '_person'], NS)
_lift(TOOLS / 'build_facades.py', ['_compose'], NS)
hung_check, place, render, clear = NS['hung_check'], NS['place'], NS['render'], NS['clear']
_block, _person, _compose, _flat = NS['_block'], NS['_person'], NS['_compose'], NS['_flat']
seg, firefly_lantern, lotus, lily_pad, cattails = (NS[n] for n in ('seg', 'firefly_lantern', 'lotus', 'lily_pad',
                                                                   'cattails'))
FF_PALETTE = _lift(TOOLS / 'build_hotel_frostfang_lodge.py', ['PALETTE'], {})['PALETTE']   # the Lodge's own
BS_PALETTE = NS['BS_PALETTE']                                                              # Bayou Spa's

# --- What the Pieces rows must say (MODELS.md: the model agrees with Pieces) -------------------------

SET_ID = 'CountStudy'
SET_ROWS = {    # id: (w, d, layer); every row also set = "CountStudy", found = true, location = 1
    'CountStudy_Portrait': (2, 1, 'Wall'),
    'CountStudy_Globe': (1, 1, 'Floor'),
    'CountStudy_Clock': (1, 1, 'Floor'),
    'CountStudy_Bust': (1, 1, 'Floor'),
    'CountStudy_Rug': (3, 2, 'Rug'),
}
SOUVENIR_ROW = ('Souvenir_Base', (1, 1, 'Floor'))
SOUVENIR_BUDGET = 800
TINTED = ('Ribbon', 'Trim')            # the parts the code colours per species
# The palette: the Manor's, and the Eyes glow (the portrait's and the bust's eyes; import_fixup makes it Neon
# in GLOW_COLOURS['Eyes']).
PALETTE = list(K.PALETTE) + [('eyes', K.GLOW_COLOURS['Eyes'], 'Eyes')]

LODGE_ROWS = {  # Frostfang Lodge's set: set = "AuroraLodge", found = true, location = 2
    'AuroraLodge_Painting': (2, 1, 'Wall'),
    'AuroraLodge_WolfStatue': (1, 1, 'Floor'),
    'AuroraLodge_Telescope': (1, 1, 'Floor'),
    'AuroraLodge_Sleigh': (2, 1, 'Floor'),
    'AuroraLodge_Rug': (3, 2, 'Rug'),
}
GROVE_ROWS = {  # Bayou Spa's set: set = "LanternGrove", found = true, location = 3
    'LanternGrove_StainedGlass': (2, 1, 'Wall'),
    'LanternGrove_Lamp': (1, 1, 'Floor'),
    'LanternGrove_Gramophone': (1, 1, 'Floor'),
    'LanternGrove_Pirogue': (2, 1, 'Floor'),
    'LanternGrove_Rug': (3, 2, 'Rug'),
}

K.pieces_decor()
for _id, (_w, _d, _layer) in list({**SET_ROWS, **LODGE_ROWS, **GROVE_ROWS}.items()) + [SOUVENIR_ROW]:
    _e = K._PIECES.get(_id)
    if _e is not None:      # the code session wrote the row: the kit holds the model to it, height included
        assert (_e['w'], _e['d'], _e['layer']) == (_w, _d, _layer), \
            f'{_id}: Pieces.luau has {_e["w"]} x {_e["d"]} {_e["layer"]}, this script {_w} x {_d} {_layer}'
        continue
    # `always` turns the kit's height agreement off: no row has a height yet; the model's top is recorded.
    K._PIECES[_id] = {'w': _w, 'd': _d, 'layer': _layer, 'height': 0.0, 'always': True}

CUR = {'id': SET_ID, 'location': 1, 'rows': SET_ROWS}     # the set being built (build_set() sets it)

_check_piece = K.check_piece


def check_piece(piece, boxes, tris, faults):
    """Souvenir_Base through the kit's decor checks (its lookups use Decor_<Id>), its own budget."""
    if piece.name != 'Souvenir_Base':
        return _check_piece(piece, boxes, tris, faults)
    saved = K.BUDGET['Decor']
    piece.name, K.BUDGET['Decor'] = 'Decor_Souvenir_Base', SOUVENIR_BUDGET
    sub = []
    try:
        total = _check_piece(piece, boxes, tris, sub)
    finally:
        piece.name, K.BUDGET['Decor'] = 'Souvenir_Base', saved
    faults += [f.replace('the Decor budget', 'the souvenir budget') for f in sub]
    return total


K.check_piece = check_piece


def souvenir_check(piece, tris, stage):
    """MODELS.md, "The souvenir": every contract part there; Ribbon and Trim one flat colour each; Medal's
    top and Badge's front each one flat plane with nothing of another part over it."""
    f = []
    need = ('Body', 'Ribbon', 'Trim', 'Medal', 'Badge', 'Glass')
    missing = [n for n in need if n not in tris]
    if missing:
        return [f'souvenir ({stage}): missing {missing}']
    if stage == 'built':
        for n in TINTED:
            cols = set(piece.parts[n][2])
            if len(cols) != 1:
                f.append(f'{n} holds {sorted(cols)}: one flat colour, the code tints it')

    def plane(part, axis, sign):
        vs = [v for t in tris[part] for v in t]
        ext = max(v[axis] for v in vs) if sign > 0 else min(v[axis] for v in vs)
        face = [t for t in tris[part] if all(abs(v[axis] - ext) < 1e-3 for v in t)]
        area = sum(((t[1] - t[0]).cross(t[2] - t[0])).length / 2 for t in face)
        return ext, face, area
    top, face, area = plane('Medal', 1, 1)
    if area < 0.3:
        f.append(f'souvenir ({stage}): Medal has no flat top for the emblem ({area:.2f} sq studs at {top:.3f})')
    lo = Vector([min(v[i] for t in face for v in t) for i in range(3)])
    hi = Vector([max(v[i] for t in face for v in t) for i in range(3)])
    for n, ts in tris.items():      # nothing of another part (the Glass excepted) over the medal's top
        if n in ('Medal', 'Glass', 'Root', 'LOD_Proxy', '_wall'):
            continue
        if any(lo.x < v.x < hi.x and lo.z < v.z < hi.z and v.y > top + 1e-3 for t in ts for v in t):
            f.append(f'souvenir ({stage}): {n} rises over the Medal\'s top')
    front, face, area = plane('Badge', 2, -1)
    if area < 0.3:
        f.append(f'souvenir ({stage}): Badge has no flat front for the name ({area:.2f} sq studs at z {front:.3f})')
    lo = Vector([min(v[i] for t in face for v in t) for i in range(3)])
    hi = Vector([max(v[i] for t in face for v in t) for i in range(3)])
    for n, ts in tris.items():
        if n in ('Badge', 'Root', 'LOD_Proxy'):
            continue
        if any(lo.x + 1e-3 < v.x < hi.x - 1e-3 and lo.y + 1e-3 < v.y < hi.y - 1e-3 and v.z < front - 1e-3
               for t in ts for v in t):
            f.append(f'souvenir ({stage}): {n} stands in front of the Badge\'s face')
    return f


def no_use_check(piece, tris, stage):
    """A set piece is decor: no Use, no seat (MODELS.md, "A set piece")."""
    f = []
    if 'Use' in piece.att:
        f.append('a set piece has a Use: decor has none (a used piece is Furniture_)')
    if piece.seats:
        f.append('a set piece declares a seat')
    return f


def sdecor(piece_id):
    w, d, layer = CUR['rows'][f'{CUR["id"]}_{piece_id}']
    p = K.decor(f'{CUR["id"]}_{piece_id}', w, d, layer)
    p.checks.append(hung_check)
    p.checks.append(no_use_check)
    return p


def sdone(note, colour=None):
    """No LOD_Proxy (as the Manor's other decor); the model's top for the Pieces row; `colour`: the palette
    name of the piece's main colour (the row's `colour`, the build list's swatch)."""
    piece = K.P
    pts = [v for n, (vs, _, _) in piece.parts.items() if n not in ('Root', 'LOD_Proxy') for v in vs]
    top = max(v.y for v in pts)
    rec = finish(proxy=False, note=note)
    rec['pieces_row'] = {'id': piece.name[len('Decor_'):] if piece.name.startswith('Decor_') else piece.name,
                         'w': piece.fw, 'd': piece.fd, 'layer': piece.layer, 'height': round(top, 2),
                         'model_top': round(top, 3)}
    if piece.name.startswith('Decor_'):
        rec['pieces_row'].update({'set': CUR['id'], 'found': True, 'location': CUR['location']})
    if colour:
        rec['pieces_row']['colour'] = list(K.PALETTE[K.COLOUR[colour]][1])
    return rec


# --- Shapes -------------------------------------------------------------------------------------------

def _scallop(a, b, h, n=4):
    """The points between finger tips a and b of a wing's membrane, bowed up by h (a quadratic curve)."""
    mx, my = (a[0] + b[0]) / 2, (a[1] + b[1]) / 2 + 2 * h
    return [((1 - t) ** 2 * a[0] + 2 * t * (1 - t) * mx + t * t * b[0],
             (1 - t) ** 2 * a[1] + 2 * t * (1 - t) * my + t * t * b[1]) for t in [k / n for k in range(1, n)]]


_F1, _F2, _F3, _HIP = (0.86, -0.06), (0.62, -0.2), (0.39, -0.25), (0.17, -0.1)
# The crest's right half (blind review 2026-10-21: the first outline read as a toothy jaw, a gem with wings
# and small wings; one bat everywhere now): the head between two tall ears, the wing's leading edge sweeping
# up to a pointed tip, three rounded membrane scallops between the finger tips, the body's round foot.
BAT_R = ([(0.0, 0.15), (0.05, 0.17), (0.10, 0.40), (0.15, 0.19), (0.17, 0.12), (0.24, 0.15), (0.40, 0.27),
          (0.56, 0.38), (0.72, 0.47), (0.86, 0.54), (1.0, 0.62), _F1] + _scallop(_F1, _F2, 0.13) + [_F2]
         + _scallop(_F2, _F3, 0.11) + [_F3] + _scallop(_F3, _HIP, 0.08, 3)
         + [_HIP, (0.15, -0.2), (0.11, -0.3), (0.05, -0.37), (0.0, -0.38)])


def bat(cx, cy, s):
    """The set's crest, a bat with spread wings, 2s wide and s tall (v from -0.38s to 0.62s), as (u, v)
    points about (cx, cy); v up."""
    pts = BAT_R + [(-x, y) for x, y in reversed(BAT_R[1:-1])]
    return [(cx + x * s, cy + y * s) for x, y in pts]


def crest(part, s, pos, tilt=0.0, depth=0.1, m=None):
    """The crest standing up and facing -Z (toward the room), its middle at `pos`, leaned back `tilt`
    degrees so a floor piece shows it to the raised build camera as well as from the front."""
    M = at(pos, rx=tilt) if m is None else m
    prism(part, bat(0.0, 0.0, s), -depth / 2, depth / 2, 'gold', plane='xy', m=M)


def parc(x1, spring, apex, n=6):
    """A pointed arch's right side, from (x1, spring) up to (0, apex): an arc centred on the springing line."""
    h = apex - spring
    cx = (x1 * x1 - h * h) / (2 * x1)
    r = x1 - cx
    a1 = math.atan2(h, -cx)
    return [(cx + r * math.cos(a1 * i / n), spring + r * math.sin(a1 * i / n)) for i in range(n + 1)]


def gothic(hw, y0, spring, apex, n=6):
    right = parc(hw, spring, apex, n)
    return [(-hw, y0), (hw, y0)] + right + [(-x, y) for x, y in reversed(right)][1:]


def frame_halves(hw, y0, spring, apex, t, n=6):
    """A pointed-arch frame t wide as two C-shaped halves (a prism has no holes), right then left."""
    inner = parc(hw - t, spring, apex - 1.4 * t, n)
    right = [(0.0, y0), (hw, y0)] + parc(hw, spring, apex, n) + list(reversed(inner)) + [(hw - t, y0 + t), (0.0, y0 + t)]
    return right, [(-x, y) for x, y in reversed(right)]


def ellipse(cx, cy, rx, ry, n=16):
    return [(cx + rx * math.cos(2 * math.pi * k / n), cy + ry * math.sin(2 * math.pi * k / n)) for k in range(n)]


def rod(part, p0, p1, r, col, n=6):
    p0, p1 = Vector(p0), Vector(p1)
    d = p1 - p0
    m = Matrix.Translation(p0) @ Vector((0, 1, 0)).rotation_difference(d.normalized()).to_matrix().to_4x4()
    cyl(part, (0, 0, 0), r, d.length, col, n=n, m=m)


def facing(pos, rx=-90):
    """A transform turning a cylinder's +Y axis to -Z (toward the viewer), its base at pos."""
    return at(pos, rx=rx)


def faces_coloured(part, verts, faces, cols, collide=False):
    """Closed geometry with a colour per face (one shell: shared vertices), Roblox coords."""
    store = K._part(part, collide)
    base = len(store[0])
    store[0].extend(Vector(v) for v in verts)
    for f, c in zip(faces, cols):
        assert c in K.COLOUR, c
        store[1].append([base + i for i in f])
        store[2].append(c)


# --- The Count's Study (Haunted Manor) ---------------------------------------------------------------

PORTRAIT_SCALE, PORTRAIT_Y0 = 0.8, 2.5     # blind review 2026-10-21: it hung at 1.4 (read as leaning on the
# floor); now its frame runs 2.5 to 6.58, centre 4.54, eye level for the 5-stud person, and 0.8 the size, so the
# crest still keeps under the 7-stud top.


def d_portrait():
    sdecor('Portrait')
    back = 1.1
    # Drawn in the first draft's frame (bottom at 1.4) and moved by PM: scaled 0.8 in x and y (not in depth),
    # its bottom to PORTRAIT_Y0.
    PM = (Matrix.Translation((0, PORTRAIT_Y0, 0))
          @ Matrix.Diagonal((PORTRAIT_SCALE, PORTRAIT_SCALE, 1, 1)) @ Matrix.Translation((0, -1.4, 0)))

    def pz(part, pts, a0, a1, col):
        prism(part, pts, a0, a1, col, plane='xy', m=PM)
    y0, hw, spring, apex = 1.4, 2.1, 4.2, 6.5       # the rise above the springing > the half width: pointed
    # The canvas behind (night).
    pz('Body', gothic(hw - 0.06, y0 + 0.04, spring, apex - 0.06), 0.97, back, 'night')
    # The gilt frame, moulded (blind review: it read as a flat band): an outer fillet, a raised ridge, an inner
    # step, three golds stepping in depth (fronts at 0.82, 0.70, 0.77); each ring overlaps the one outside it
    # by 0.01 and buries its back at its own depth, so no two faces share a plane.
    rings = [(0.12, 0.82, 0.985, 'amber'), (0.14, 0.70, 0.99, 'honey'), (0.12, 0.77, 0.995, 'gold')]
    h, b, a = hw, y0, apex
    for t, front, rear, col in rings:
        for half in frame_halves(h, b, spring, a, t):
            pz('Body', half, front, rear, col)
        h, b, a = h - t + 0.01, b + t - 0.01, a - 1.4 * t + 0.014
    # A crimson velvet slip inside the frame, a step back from its face.
    for half in frame_halves(h, b, spring, a, 0.13):
        pz('Body', half, 0.86, 0.975, 'crimson_dark')
    # The Count: each layer a step proud of the one it overlaps, the backs buried in the canvas.
    pz('Body', ellipse(0.9, 5.05, 0.28, 0.28, 14), 0.955, 0.98, 'moon')                         # the moon
    pz('Body', [(-1.5, 1.7), (1.5, 1.7), (1.45, 2.9), (1.0, 3.45), (0.3, 3.7), (-0.3, 3.7), (-1.0, 3.45),
                (-1.45, 2.9)], 0.955, 0.98, 'black')                                            # the cape
    for s in (-1, 1):                                                                             # the collar
        pz('Body', [(s * 0.3, 3.62), (s * 1.05, 3.4), (s * 1.0, 4.75), (s * 0.42, 4.1)][::s], 0.96, 0.98,
           'crimson')
    pz('Body', [(-0.18, 3.55), (0.18, 3.55), (0.18, 3.9), (-0.18, 3.9)], 0.952, 0.98, 'bone')
    pz('Body', [(-0.32, 3.7), (0.32, 3.7), (0.0, 2.6)], 0.948, 0.98, 'bone')                     # the shirt
    cyl('Body', (0, 0, 0), 0.15, 0.04, 'gold', n=10, m=PM @ facing((0, 3.05, 0.975)))             # a gold pin
    for s in (-1, 1):                                                                             # pointed ears
        pz('Body', [(s * 0.36, 4.45), (s * 0.64, 4.8), (s * 0.4, 4.18)][::s], 0.95, 0.98, 'bone')
    pz('Body', ellipse(0.0, 4.3, 0.4, 0.52, 16), 0.945, 0.98, 'bone')                             # the face
    pz('Body', [(-0.44, 4.35), (-0.42, 4.7), (-0.25, 4.9), (0.0, 4.96), (0.25, 4.9), (0.42, 4.7), (0.44, 4.35),
                (0.3, 4.62), (0.15, 4.66), (0.0, 4.5), (-0.15, 4.66), (-0.3, 4.62)], 0.94, 0.98, 'black')
    for k, s in enumerate((-1, 1)):                                                               # widow's peak ^
        pz(f'Glow_Eyes_{k + 1}', [(s * 0.08, 4.35), (s * 0.23, 4.35), (s * 0.22, 4.41), (s * 0.08, 4.43)][::s],
           0.932, 0.96, 'eyes')
        pz('Body', [(s * 0.06, 4.45), (s * 0.28, 4.5), (s * 0.28, 4.56), (s * 0.06, 4.5)][::s], 0.936, 0.96,
           'black')                                                                               # the brows
    pz('Body', [(-0.14, 3.97), (0.14, 3.97), (0.1, 4.0), (-0.1, 4.0)], 0.938, 0.96, 'crimson')
    # The crest standing on the apex (6.58), gold on the wall paper, its foot over the frame's point.
    crest('Body', 0.55, (0, 6.6, 0.77), depth=0.18)
    # Two candle sconces either side, on gold backplates on the wall, at the frame's middle.
    for k, x in enumerate((-2.2, 2.2)):
        span('Body', (x - 0.12, 3.8, 1.0), (x + 0.12, 4.5, back), 'gold', bevel=0.02)
        span('Body', (x - 0.05, 4.05, 0.55), (x + 0.05, 4.15, 1.0), 'gold')
        cyl('Body', (x, 4.15, 0.66), 0.16, 0.1, 'gold', n=8)
        cyl('Body', (x, 4.25, 0.66), 0.09, 0.45, 'cream', n=8)
        sphere(f'Glow_Warm_{k + 1}', (x, 4.82, 0.66), (0.06, 0.14, 0.06), 'flame', n=6, rings=4)
    sdone('the Count\'s portrait at eye level (frame 2.5 to 6.58): a moulded gilt pointed-arch frame (three '
          'stepped rings) with a crimson slip, the Count in a black cape and a high crimson collar, widow\'s '
          'peak, glowing eyes (Glow_Eyes_1, _2), a moon behind; the crest (the gold bat) standing on the apex; '
          'two candle sconces (Glow_Warm_1, _2)')


LANDS = [   # (direction, angular radius): blobs that join into two continents and an island (a sea of single
            # blobs read as a chequer at this resolution)
    ((0.55, 0.45, -0.7), 0.6), ((0.75, 0.1, -0.65), 0.5), ((0.6, -0.3, -0.75), 0.45), ((0.35, 0.7, -0.6), 0.4),
    ((-0.55, 0.3, 0.75), 0.6), ((-0.3, -0.25, 0.9), 0.5), ((-0.75, -0.1, 0.6), 0.45),
    ((-0.8, 0.35, -0.45), 0.3)]


def globe_sphere(part, c, r, m, n=20, rings=12):
    """A sphere whose faces are sea (night) or land (gold) by LANDS, one shell; m turns its axis."""
    verts, faces, cols = [], [], []
    loc = [Vector((0, -r, 0))]
    for i in range(1, rings):
        a = math.pi * i / rings
        for k in range(n):
            b = 2 * math.pi * k / n
            loc.append(Vector((r * math.sin(a) * math.cos(b), -r * math.cos(a), r * math.sin(a) * math.sin(b))))
    loc.append(Vector((0, r, 0)))
    top = len(loc) - 1

    def ring(i, k):
        return 1 + (i - 1) * n + k % n
    for k in range(n):
        faces.append((0, ring(1, k + 1), ring(1, k)))
        faces.append((top, ring(rings - 1, k), ring(rings - 1, k + 1)))
    for i in range(1, rings - 1):
        for k in range(n):
            faces.append((ring(i, k), ring(i, k + 1), ring(i + 1, k + 1), ring(i + 1, k)))
    lands = [(Vector(d).normalized(), math.cos(a)) for d, a in LANDS]
    for f in faces:
        nrm = (sum((loc[i] for i in f), Vector()) / len(f)).normalized()
        cols.append('gold' if any(nrm.dot(d) > ca for d, ca in lands) else 'night')
    M = Matrix.Translation(Vector(c)) @ m
    faces_coloured(part, [M @ v for v in loc], faces, cols)


def d_globe():
    sdecor('Globe')
    lathe('Body', [(0.95, 0.0), (0.95, 0.1), (0.75, 0.18), (0.3, 0.35), (0.16, 0.6), (0.13, 1.6), (0.2, 1.75),
                   (0.12, 1.9)], 'wood_dark', n=12)
    lathe('Body', [(0.98, 0.02), (0.98, 0.09)], 'gold', n=12)                       # the foot's gold band
    lathe('Body', [(0.18, 0.95), (0.18, 1.1)], 'gold', n=12)                        # a collar on the stem
    cy, r = 3.0, 0.8
    for k in range(4):                                                              # four struts to the horizon
        a = math.pi / 4 + k * math.pi / 2
        c, s = math.cos(a), math.sin(a)
        p0, p1, p2 = (0.12 * c, 1.8, 0.12 * s), (0.75 * c, 2.2, 0.75 * s), (0.96 * c, 2.98, 0.96 * s)
        rod('Body', p0, p1, 0.05, 'wood_dark')
        rod('Body', p1, p2, 0.05, 'wood_dark')
    lathe('Body', [(0.9, cy - 0.04), (1.05, cy - 0.04), (1.05, cy + 0.03), (0.9, cy + 0.03)], 'wood_dark', n=20,
          closed=True)                                                              # the horizon ring
    tilt = Matrix.Rotation(math.radians(-23), 4, 'Z')
    globe_sphere('Body', (0, cy, 0), r, tilt)
    lathe('Body', [(0.86, -0.03), (0.92, -0.03), (0.92, 0.03), (0.86, 0.03)], 'gold', n=20, closed=True,
          m=at((0, cy, 0), rx=90))                                                  # the gold meridian
    axis = tilt @ Vector((0, 1, 0))
    for s in (-1, 1):                                                               # the axis's pins
        rod('Body', Vector((0, cy, 0)) + s * 0.74 * axis, Vector((0, cy, 0)) + s * 0.9 * axis, 0.05, 'gold')
    cyl('Body', (0, 1.86, 0), 0.07, 0.3, 'gold', n=8)                               # the meridian's post
    # The crest standing on the meridian's top (cy + 0.92), leaned back 30 degrees to the raised camera.
    crest('Body', 0.45, (0, cy + 1.05, 0.07), tilt=30)     # its foot (y 3.90, z -0.02) in the meridian
    sdone('the Count\'s night globe: a gilded globe (gold lands on a night sea) on a tilted axis in a gold '
          'meridian, a dark wood horizon ring on four struts, a turned stand with gold bands; the crest (the gold '
          'bat) standing on the meridian\'s top, leaned back to the raised camera')


def d_clock():
    sdecor('Clock')
    for x in (-0.68, 0.68):                                                         # gold ball feet
        for z in (-0.53, 0.53):
            sphere('Body', (x, 0.16, z), 0.16, 'gold', n=8, rings=5)
    span('Body', (-0.85, 0.2, -0.7), (0.85, 0.45, 0.7), 'black', bevel=0.04)
    case = [(-0.6, 0.45), (0.6, 0.45), (0.95, 4.1), (0.75, 5.7), (-0.75, 5.7), (-0.95, 4.1)]
    prism('Body', case, -0.55, 0.55, 'wood_dark', plane='xy')                       # a coffin standing up
    prism('Body', [(-0.45, 0.75), (0.45, 0.75), (0.75, 4.0), (0.58, 5.45), (-0.58, 5.45), (-0.75, 4.0)], -0.58,
          -0.5, 'crimson', plane='xy')                                              # the velvet inlay
    # The crown (blind review 2026-10-21: from above it was a dark box): a black cornice with a gold band, and
    # on it a coffin lid's crimson gable, its ridge across in gold, so the top reads crimson and gold from
    # above; the crest stands on the ridge, leaned back to the raised camera.
    prism('Body', [(-0.88, 5.68), (0.88, 5.68), (0.86, 5.84), (-0.86, 5.84)], -0.68, 0.68, 'black', plane='xy')
    span('Body', (-0.9, 5.74, -0.7), (0.9, 5.8, 0.7), 'gold')
    prism('Body', [(-0.64, 5.83), (0.64, 5.83), (0.0, 6.28)], -0.82, 0.82, 'crimson', plane='zy')
    rod('Body', (-0.86, 6.28, 0), (0.86, 6.28, 0), 0.06, 'gold', n=6)
    crest('Body', 0.62, (0, 6.42, 0.0), tilt=30)           # its foot buried in the front slope
    # The pendulum behind a dark pointed window.
    prism('Body', gothic(0.42, 1.25, 3.2, 3.8), -0.61, -0.56, 'black', plane='xy')
    span('Body', (-0.03, 1.95, -0.63), (0.03, 3.5, -0.6), 'gold')
    cyl('Body', (0, 0, 0), 0.2, 0.045, 'gold', n=12, m=facing((0, 1.85, -0.6)))
    # The face: a gold bezel, the moonlit dial (Glow_Cold_1), the hands at five to midnight.
    dy = 4.65
    cyl('Body', (0, 0, 0), 0.52, 0.04, 'gold', n=16, m=facing((0, dy, -0.58)))
    cyl('Glow_Cold_1', (0, 0, 0), 0.44, 0.04, 'moonglow', n=16, m=facing((0, dy, -0.6)))
    box('Body', (0, 0, 0), (0.07, 0.26, 0.018), 'black', m=at((0, dy + 0.12, -0.646)))
    box('Body', (0, 0, 0), (0.045, 0.36, 0.023), 'black', m=at((-0.09, dy + 0.156, -0.6485), rz=30))
    for a in range(4):
        x, y = 0.34 * math.sin(a * math.pi / 2), dy + 0.34 * math.cos(a * math.pi / 2)
        cyl('Body', (0, 0, 0), 0.045, 0.016, 'black', n=6, m=facing((x, y, -0.636)))
    sdone('the Count\'s clock: a longcase clock shaped as a coffin standing up, dark wood on gold ball feet, a '
          'crimson inlay, the pendulum behind a pointed window, a moonlit dial (Glow_Cold_1) at five to midnight '
          'in a gold bezel; a crimson gable crown with a gold ridge, the crest (the gold bat) standing on it')


def d_bust():
    sdecor('Bust')
    # Blind review 2026-10-21: the first read as a bird on a post (a 1-stud head on a 3.5 pedestal, the
    # collar bigger than the head, a raven beside it). Now a bust: a lower column (capital top 2.16), marble
    # shoulders 1.8 wide and a head 0.72 wide and 0.9 tall on them (about the ratio of a real bust), the
    # high collar two crimson-lined wings behind the head, reaching 0.25 past it each side and to its
    # middle's height: it frames the head. No raven.
    span('Body', (-0.75, 0.0, -0.75), (0.75, 0.3, 0.75), 'black', bevel=0.04)
    span('Body', (-0.42, 0.28, -0.42), (0.42, 2.0, 0.42), 'crimson_dark')   # its ends buried in base and capital
    span('Body', (-0.46, 0.3, -0.46), (0.46, 0.42, 0.46), 'gold')
    span('Body', (-0.46, 1.86, -0.46), (0.46, 1.98, 0.46), 'gold')
    span('Body', (-0.64, 1.98, -0.64), (0.64, 2.16, 0.64), 'black', bevel=0.04)
    span('Body', (-0.36, 0.72, -0.465), (0.36, 1.6, -0.4), 'black', bevel=0.02)    # the plaque
    crest('Body', 0.32, (0, 1.17, -0.48), depth=0.06)                               # the crest on it
    lathe('Body', [(0.4, 2.15), (0.4, 2.21), (0.24, 2.3), (0.28, 2.42)], 'gold', n=12)        # the socle
    lathe('Body', [(0.26, 2.4), (0.6, 2.45), (0.84, 2.6), (0.9, 2.82), (0.84, 3.02), (0.6, 3.14), (0.3, 3.2),
                   (0.0, 3.22)], 'bone', n=14, scale=(1, 0.42))                    # chest and shoulders, marble
    for s in (-1, 1):                                                               # the high collar's wings
        wing = [(0.0, 0.0), (0.5, -0.03), (0.54, 0.8), (0.06, 0.46)]
        pts = [(s * x, y) for x, y in wing][::s]
        M = at((s * 0.16, 3.05, 0.14), ry=-35 * s)
        prism('Body', pts, 0.0, 0.035, 'crimson', plane='xy', m=M)                 # its lining, to the front
        prism('Body', pts, 0.035, 0.09, 'black', plane='xy', m=M)       # face to face: no shared side planes
    cyl('Body', (0, 3.05, 0), 0.19, 0.4, 'bone', n=10)                              # the neck
    sphere('Body', (0, 3.68, -0.02), (0.36, 0.45, 0.4), 'bone', n=14, rings=8)      # the head, in marble
    sphere('Body', (0, 3.84, 0.09), (0.37, 0.33, 0.36), 'black', n=14, rings=7)     # the hair, swept back
    prism('Body', [(-0.17, 3.98), (0.17, 3.98), (0.0, 3.8)], -0.39, -0.2, 'black', plane='xy')   # widow's peak
    for s in (-1, 1):                                                               # pointed ears
        prism('Body', [(s * 0.32, 3.62), (s * 0.5, 3.92), (s * 0.34, 3.5)][::s], -0.06, 0.06, 'bone', plane='xy')
    for k, s in enumerate((-1, 1)):
        sphere(f'Glow_Eyes_{k + 1}', (s * 0.13, 3.72, -0.385), (0.065, 0.04, 0.03), 'eyes', n=6, rings=4)
    sdone('the Count\'s bust: head and shoulders in white marble, black hair with a widow\'s peak, pointed '
          'ears and glowing eyes (Glow_Eyes_1, _2), a high crimson-lined collar framing the head, on a gold '
          'socle and a crimson column with gold bands and a black capital; the crest (the gold bat) on a black '
          'plaque on the column')


def d_rug():
    sdecor('Rug')
    hx, hz = 4.5, 3.0
    span('Body', (-hx, 0.0, -hz), (hx, 0.05, hz), 'gold')
    span('Body', (-hx + 0.3, 0.05, -hz + 0.3), (hx - 0.3, 0.08, hz - 0.3), 'black')
    span('Body', (-hx + 0.6, 0.08, -hz + 0.6), (hx - 0.6, 0.1, hz - 0.6), 'crimson')
    prism('Body', ellipse(0, 0, 2.0, 1.5, 24), 0.1, 0.115, 'gold', plane='xz')       # the medallion
    prism('Body', ellipse(0, 0, 1.75, 1.28, 24), 0.115, 0.13, 'crimson_dark', plane='xz')
    prism('Body', bat(0.0, -0.15, 1.35), 0.13, 0.145, 'gold', plane='xz')     # the crest, head away from the door
    fx, fz = hx - 0.75, hz - 0.75
    for sx in (-1, 1):                                                              # the corners' gold
        for sz in (-1, 1):
            pts = [(sx * fx, sz * fz), (sx * (fx - 0.9), sz * fz), (sx * fx, sz * (fz - 0.7))]
            prism('Body', pts if sx * sz > 0 else pts[::-1], 0.1, 0.12, 'gold', plane='xz')
        prism('Body', [(sx * 3.0 - 0.35, 0), (sx * 3.0, -0.35), (sx * 3.0 + 0.35, 0), (sx * 3.0, 0.35)], 0.1, 0.12,
              'gold', plane='xz')
    sdone('the Count\'s rug: crimson in a black and gold border, a gold medallion with the crest (a gold bat, '
          'its head away from the door) in the middle, gold corners and two gold diamonds')


# --- Shared by the Lodge's and the Bayou's sets -----------------------------------------------------------

def sym(right):
    """A symmetric outline from its right half, listed from the top centre (u = 0) round to the bottom centre."""
    return right + [(-x, y) for x, y in reversed(right[1:-1])]


def mirror(pts):
    """A polygon's left twin (u -> -u), its order reversed so it stays one way round."""
    return [(-x, y) for x, y in reversed(pts)]


EMBLEM_STEP = 0.02          # a crest's upper layer stands this far proud of the one under it (a 0.01 coplanar grid)


def emblem(part, layers, s, M, depth=0.08, step=EMBLEM_STEP):
    """A set's crest: `layers` [(points, colour, k)] in unit coordinates (u right, v up, about 2 across), scaled
    by s, standing in M's local xy plane and facing -Z. Layer k reaches step * k further forward than layer 0
    and 0.004 k further back, so every layer's faces lie in planes of their own and its back is buried."""
    for pts, col, k in layers:
        prism(part, [(u * s, v * s) for u, v in pts], -depth / 2 - step * k, depth / 2 + 0.004 * k, col,
              plane='xy', m=M)


def flat(pos, ry=0.0):
    """M for a crest lying face up at pos (its middle depth), its head (+v) toward +Z turned ry about Y."""
    return at(pos, rx=90, ry=ry)


def ellarc(hw, spring, apex, n=6):
    """A round (elliptical) arch's right quarter, from (hw, spring) up to (0, apex)."""
    return [(hw * math.cos(math.pi / 2 * i / n), spring + (apex - spring) * math.sin(math.pi / 2 * i / n))
            for i in range(n + 1)]


def round_top(hw, y0, spring, apex, n=6):
    r = ellarc(hw, spring, apex, n)
    return [(-hw, y0), (hw, y0)] + r + [(-x, y) for x, y in reversed(r)][1:]


def round_frame_halves(hw, y0, spring, apex, t, n=6):
    """A round-topped frame t wide as two C-shaped halves (a prism has no holes), right then left."""
    inner = ellarc(hw - t, spring, apex - t, n)
    right = ([(0.0, y0), (hw, y0)] + ellarc(hw, spring, apex, n) + list(reversed(inner))
             + [(hw - t, y0 + t), (0.0, y0 + t)])
    return right, mirror(right)


def ring_halves(cy, ro, ri, n=9):
    """A round frame (centre (0, cy), radii ro > ri) as two C-shaped halves, right then left."""
    outer = [(ro * math.cos(math.pi * (-0.5 + i / n)), cy + ro * math.sin(math.pi * (-0.5 + i / n)))
             for i in range(n + 1)]
    inner = [(ri * math.cos(math.pi * (0.5 - i / n)), cy + ri * math.sin(math.pi * (0.5 - i / n)))
             for i in range(n + 1)]
    right = outer + inner
    return right, mirror(right)


def _area(pts):
    return sum(pts[i][0] * pts[(i + 1) % len(pts)][1] - pts[(i + 1) % len(pts)][0] * pts[i][1]
               for i in range(len(pts))) / 2


def offset_poly(pts, d, cap=2.5):
    """The outline grown by d (mitred corners, a mitre at most cap * d)."""
    sgn = 1.0 if _area(pts) > 0 else -1.0
    k = len(pts)
    out = []
    for i in range(k):
        p0, p1, p2 = Vector(pts[i - 1]), Vector(pts[i]), Vector(pts[(i + 1) % k])
        n1 = Vector(((p1 - p0).y, -(p1 - p0).x)).normalized() * sgn
        n2 = Vector(((p2 - p1).y, -(p2 - p1).x)).normalized() * sgn
        m = n1 + n2
        m = m * (d / max(0.2, 1 + n1.dot(n2))) if m.length > 1e-9 else n1 * d
        if m.length > cap * d:
            m = m.normalized() * cap * d
        out.append((p1.x + m.x, p1.y + m.y))
    return out


def stroke(line, w):
    """A polyline drawn w wide, as one outline."""
    left, right = [], []
    for i, p in enumerate(line):
        a, b = Vector(line[max(i - 1, 0)]), Vector(line[min(i + 1, len(line) - 1)])
        t = (b - a).normalized()
        n = Vector((-t.y, t.x)) * (w / 2)
        left.append((p[0] + n.x, p[1] + n.y))
        right.append((p[0] - n.x, p[1] - n.y))
    return left + list(reversed(right))


def wave_band(x0, x1, yc, amp, th, k, ph, n=9):
    """A ribbon from x0 to x1 waving about yc, th thick in the middle and pointed at its ends."""
    top, bot = [], []
    for i in range(n + 1):
        f = i / n
        x = x0 + (x1 - x0) * f
        y = yc + amp * math.sin(2 * math.pi * k * f + ph)
        h = max(0.02, th * math.sin(math.pi * f) ** 0.6) / 2
        top.append((x, y + h))
        bot.append((x, y - h))
    return bot + list(reversed(top))


def cone(part, p0, p1, r0, r1, col, n=8):
    """A tapered rod from p0 (radius r0) to p1 (radius r1)."""
    p0, p1 = Vector(p0), Vector(p1)
    d = p1 - p0
    m = Matrix.Translation(p0) @ Vector((0, 1, 0)).rotation_difference(d.normalized()).to_matrix().to_4x4()
    cyl(part, (0, 0, 0), r0, d.length, col, n=n, r_top=r1, m=m)


def lathe_coloured(part, loop, cols, n, m):
    """A closed (r, y) loop revolved about local Y (a horn with its inside), band j (loop[j] to loop[j + 1])
    in cols[j]; one shell, placed by m."""
    verts, faces, fc = [], [], []
    for r, y in loop:
        for k in range(n):
            a = math.pi / n + 2 * math.pi * k / n
            verts.append(m @ Vector((r * math.cos(a), y, r * math.sin(a))))
    L = len(loop)
    for j in range(L):
        j2 = (j + 1) % L
        for k in range(n):
            faces.append((j * n + k, j * n + (k + 1) % n, j2 * n + (k + 1) % n, j2 * n + k))
            fc.append(cols[j])
    faces_coloured(part, verts, faces, fc)


def loft(part, sections, cols):
    """A solid through quads [bottom-left, bottom-right, top-right, top-left] (left = -Z), first to last;
    cols {'bottom', 'side', 'top', 'cap'}."""
    verts, faces, fc = [], [], []
    for q in sections:
        verts += [Vector(v) for v in q]
    for i in range(len(sections) - 1):
        a, b = 4 * i, 4 * i + 4
        for (p, q), what in (((0, 1), 'bottom'), ((1, 2), 'side'), ((2, 3), 'top'), ((3, 0), 'side')):
            faces.append((a + p, a + q, b + q, b + p))
            fc.append(cols[what])
    last = 4 * (len(sections) - 1)
    faces += [(0, 3, 2, 1), (last, last + 1, last + 2, last + 3)]
    fc += [cols['cap'], cols['cap']]
    faces_coloured(part, verts, faces, fc)


# --- The Aurora Lodge (Frostfang Lodge) -------------------------------------------------------------------
# One crest on every piece: the Frostfang, a wolf's head seen from the front (tall pointed ears, a ruff of
# three spikes a cheek, a long muzzle), gold with a snow mask, inner ears and dark eyes and nose.

WOLF_R = [(0.0, 0.50), (0.16, 0.56), (0.42, 1.05), (0.62, 0.50), (0.80, 0.42), (1.00, 0.12), (0.78, 0.04),
          (0.94, -0.24), (0.66, -0.28), (0.72, -0.52), (0.44, -0.52), (0.26, -0.86), (0.13, -1.0), (0.0, -1.02)]
WOLF_MASK_R = [(0.0, 0.2), (0.16, 0.08), (0.5, -0.2), (0.4, -0.46), (0.22, -0.78), (0.0, -0.78)]
WOLF_EAR = [(0.22, 0.58), (0.40, 0.90), (0.52, 0.54)]
WOLF_EYE = [(0.14, 0.24), (0.40, 0.32), (0.44, 0.22), (0.22, 0.14)]
WOLF_NOSE_R = [(0.0, -0.83), (0.11, -0.86), (0.09, -0.95), (0.0, -0.98)]
WOLF = [(sym(WOLF_R), 'gold', 0), (sym(WOLF_MASK_R), 'snow', 1), (WOLF_EAR, 'snow', 1),
        (mirror(WOLF_EAR), 'snow', 1), (WOLF_EYE, 'night', 1), (mirror(WOLF_EYE), 'night', 1),
        (sym(WOLF_NOSE_R), 'night', 1)]


def d_lodge_painting():
    sdecor('Painting')
    # The aurora over the Frostfang peaks, the Lodge's own lit window under the pines, in a moulded round-
    # topped frame (log, log, gold: three stepped rings as the Count's portrait) at eye level (2.4 to 6.1),
    # the crest standing on the frame's crown; an iron lantern on a bracket either side.
    back, hw, y0, spring, apex = 1.1, 1.95, 2.4, 5.3, 6.1
    prism('Body', round_top(hw - 0.06, y0 + 0.04, spring, apex - 0.06), 0.97, back, 'night')       # the canvas
    rings = [(0.14, 0.80, 0.985, 'log_dark'), (0.16, 0.68, 0.99, 'log'), (0.10, 0.76, 0.995, 'gold')]
    h, b, a = hw, y0, apex
    for t, front, rear, col in rings:
        for half in round_frame_halves(h, b, spring, a, t):
            prism('Body', half, front, rear, col, plane='xy')
        h, b, a = h - t + 0.01, b + t - 0.01, a - t + 0.01
    # The picture inside the opening (x +-1.57, y 2.76 up): each layer a step proud, its back in the canvas.
    prism('Glow_Magic_1', wave_band(-1.45, 1.45, 4.45, 0.18, 0.26, 1.2, 0.3), 0.955, 0.98, 'aurora')
    prism('Glow_Magic_2', wave_band(-1.3, 1.35, 4.92, 0.14, 0.18, 1.0, 2.0), 0.943, 0.98, 'aurora')
    prism('Body', wave_band(-1.0, 1.0, 5.25, 0.07, 0.12, 0.8, 1.0), 0.955, 0.98, 'violet')
    prism('Body', [(-1.57, 2.76), (1.57, 2.76), (1.57, 3.5), (1.15, 3.95), (0.75, 3.55), (0.15, 4.35),
                   (-0.4, 3.7), (-0.85, 4.05), (-1.57, 3.35)], 0.931, 0.98, 'snow')                # the peaks
    for pts in ([(0.15, 4.35), (0.45, 3.95), (0.75, 3.55), (0.3, 3.3)],
                [(-0.85, 4.05), (-0.62, 3.88), (-0.4, 3.7), (-0.72, 3.45)],
                [(1.15, 3.95), (1.36, 3.72), (1.57, 3.5), (1.57, 3.3), (1.2, 3.42)]):
        prism('Body', offset_poly(pts, -0.015), 0.918, 0.97, 'snow_shade')   # their shade, inside their edges
    for x, hgt, front in ((-1.25, 1.0, 0.905), (-0.92, 0.75, 0.892), (0.95, 0.85, 0.905), (1.28, 1.05, 0.892)):
        prism('Body', [(x - 0.24, 2.76), (x + 0.24, 2.76), (x + 0.112, 2.76 + 0.4 * hgt), (x + 0.18, 2.76 + 0.4 * hgt),
                       (x, 2.76 + hgt), (x - 0.18, 2.76 + 0.4 * hgt), (x - 0.112, 2.76 + 0.4 * hgt)], front,
              front + 0.05, 'pine_dark')                                  # the pines, neighbours a step apart
    prism('Body', [(0.02, 2.76), (0.6, 2.76), (0.6, 3.12), (0.31, 3.38), (0.02, 3.12)], 0.905, 0.96, 'log_dark')
    prism('Body', [(-0.07, 3.09), (0.67, 3.09), (0.3, 3.45)], 0.89, 0.95, 'snow')                  # its roof
    prism('Glow_Warm_1', [(0.2, 2.86), (0.4, 2.86), (0.4, 3.02), (0.2, 3.02)], 0.89, 0.95, 'flame')  # its window
    prism('Body', [(-1.57, 2.76), (1.57, 2.76), (1.57, 2.84), (-1.57, 2.84)], 0.875, 0.95, 'snow')  # the snow
    # The crest on the crown, its chin 0.06 into the frame's apex, its ears' tips at 6.97.
    emblem('Body', WOLF, 0.45, at((0, 6.5, 0.75)), depth=0.16)
    for k, x in enumerate((-2.3, 2.3)):     # the lanterns: an iron backplate and arm, gold foot and finial
        span('Body', (x - 0.13, 3.55, 1.0), (x + 0.13, 4.35, back), 'iron', bevel=0.02)
        span('Body', (x - 0.05, 3.78, 0.6), (x + 0.05, 3.88, 1.0), 'iron')
        cyl('Body', (x, 3.83, 0.6), 0.17, 0.08, 'gold', n=6)
        cyl(f'Glow_Warm_{k + 2}', (x, 3.91, 0.6), 0.12, 0.4, 'flame', n=6)
        cyl('Body', (x, 4.31, 0.6), 0.18, 0.16, 'iron', n=6, r_top=0.05)
        sphere('Body', (x, 4.5, 0.6), 0.06, 'gold', n=6, rings=4)
    sdone('the aurora over the Frostfang peaks (Glow_Magic_1, _2 and a violet band), the Lodge\'s lit window '
          '(Glow_Warm_1) under the pines, in a moulded round-topped frame (log, log, gold) at eye level (2.4 to '
          '6.1); the crest (the gold wolf\'s head) on its crown; an iron lantern either side (Glow_Warm_2, _3)',
          colour='navy')


def d_lodge_rug():
    sdecor('Rug')
    # Snow, a red stripe, snow, a navy field; an ice medallion with the crest large (2.7 across, its head away
    # from the door), the aurora waving across both ends (mint and violet), gold stars in the corners.
    hx, hz = 4.5, 3.0
    span('Body', (-hx, 0.0, -hz), (hx, 0.03, hz), 'snow')
    span('Body', (-hx + 0.3, 0.03, -hz + 0.3), (hx - 0.3, 0.05, hz - 0.3), 'red')
    span('Body', (-hx + 0.48, 0.05, -hz + 0.48), (hx - 0.48, 0.065, hz - 0.48), 'snow')
    span('Body', (-hx + 0.62, 0.065, -hz + 0.62), (hx - 0.62, 0.08, hz - 0.62), 'navy')
    prism('Body', ellipse(0, 0, 2.1, 1.75, 24), 0.08, 0.095, 'ice', plane='xz')                    # the medallion
    prism('Body', ellipse(0, 0, 1.9, 1.55, 24), 0.095, 0.11, 'night', plane='xz')
    emblem('Body', WOLF, 1.35, flat((0, 0.1175, -0.03)), depth=0.015, step=0.015)                 # 0.11 to 0.14
    for s in (-1, 1):                                                                              # the aurora
        for x, col, ph in ((2.75, 'mint', 0.0), (3.25, 'violet', 1.4)):
            band = wave_band(-1.7, 1.7, 0.0, 0.18, 0.24, 1.0, ph)
            prism('Body', [(s * (x + v), z) for z, v in band], 0.08, 0.095, col, plane='xz')
    for sx in (-1, 1):                                                                             # the stars
        for sz in (-1, 1):
            cx, cz = sx * 3.6, sz * 2.1
            prism('Body', [(cx + 0.26 * math.cos(a) * (1 if i % 2 == 0 else 0.35),
                            cz + 0.26 * math.sin(a) * (1 if i % 2 == 0 else 0.35))
                           for i, a in enumerate(math.pi / 4 * j for j in range(8))], 0.08, 0.095, 'gold', plane='xz')
    sdone('the Lodge\'s rug: snow with a red stripe round a navy field, an ice medallion with the crest (the '
          'gold wolf\'s head, its snow mask, 2.7 across, its head away from the door), the aurora waving across '
          'both ends in mint and violet, gold stars in the corners', colour='navy')


def d_lodge_wolf():
    sdecor('WolfStatue')
    # A wolf carved in ice, sitting and howling, a gold collar, on an octagonal stone plinth with two gold
    # bands, a light cap and the crest on its front; from above a pale wolf (haunches, raised head and muzzle,
    # a tail round its feet) on a light octagon ringed in gold.
    lathe('Body', [(1.05, 0.0), (1.05, 0.22)], 'stone_dark', n=8)
    lathe('Body', [(0.86, 0.2), (0.86, 1.42)], 'stone', n=8)
    for y in (0.22, 1.3):
        lathe('Body', [(0.93, y), (0.93, y + 0.08)], 'gold', n=8)
    lathe('Body', [(1.0, 1.38), (1.04, 1.5), (0.97, 1.6)], 'stone_light', n=8)
    emblem('Body', WOLF, 0.3, at((0, 0.82, -0.795 - 0.03)), depth=0.08)          # on the plinth's front face
    y0 = 1.6
    sphere('Body', (0, y0 + 0.55, 0.3), (0.62, 0.55, 0.62), 'ice', n=10, rings=6)                # haunches
    for s in (-1, 1):
        sphere('Body', (s * 0.36, y0 + 0.1, -0.08), (0.18, 0.1, 0.3), 'frost', n=6, rings=4)     # hind feet
        rod('Body', (s * 0.22, y0 + 0.85, -0.3), (s * 0.22, y0 + 0.06, -0.4), 0.11, 'ice')      # forelegs
        sphere('Body', (s * 0.22, y0 + 0.08, -0.47), (0.13, 0.08, 0.18), 'frost', n=6, rings=4)  # forepaws
    sphere('Body', (0, 0, 0), (0.48, 0.75, 0.45), 'ice', n=10, rings=6, m=at((0, y0 + 1.15, 0.05), rx=15))
    sphere('Body', (0, y0 + 1.35, -0.25), (0.36, 0.5, 0.25), 'snow', n=8, rings=5)               # the chest ruff
    rod('Body', (0, y0 + 1.6, 0.05), (0, y0 + 2.15, -0.05), 0.28, 'ice', n=8)                    # the neck
    lathe('Body', [(0.26, -0.05), (0.33, -0.05), (0.33, 0.05), (0.26, 0.05)], 'gold', n=10, closed=True,
          m=at((0, y0 + 1.75, 0.03), rx=-10))                                                      # the collar
    hc = Vector((0, y0 + 2.25, -0.08))
    sphere('Body', hc, (0.3, 0.3, 0.32), 'ice', n=10, rings=6)                                    # the head
    d = Vector((0, math.sin(math.radians(55)), -math.cos(math.radians(55))))
    cone('Body', hc + 0.12 * d, hc + 0.72 * d, 0.18, 0.08, 'frost', n=8)                          # the muzzle, up
    sphere('Body', hc + 0.74 * d, 0.075, 'ice_dark', n=6, rings=4)
    for s in (-1, 1):
        cone('Body', hc + Vector((s * 0.15, 0.15, 0.1)), hc + Vector((s * 0.23, 0.38, 0.26)), 0.11, 0.015, 'ice',
             n=6)                                                                                  # ears, laid back
    for p0, p1 in (((0.45, y0 + 0.16, 0.62), (0.72, y0 + 0.12, 0.2)), ((0.72, y0 + 0.12, 0.2), (0.6, y0 + 0.1, -0.25)),
                   ((0.6, y0 + 0.1, -0.25), (0.4, y0 + 0.1, -0.5))):
        rod('Body', p0, p1, 0.13, 'frost', n=6)                                                   # the tail
    sphere('Body', (0.4, y0 + 0.1, -0.5), 0.14, 'snow', n=6, rings=4)
    sdone('the Frostfang in ice: a wolf sitting and howling (haunches, a snow chest ruff, a gold collar, its muzzle '
          'raised, ears laid back, a tail round its feet) on an octagonal stone plinth with two gold bands and a '
          'light cap; the crest (the gold wolf\'s head) on the plinth\'s front', colour='ice')


def d_lodge_telescope():
    sdecor('Telescope')
    # A brass telescope on a light wood tripod, aimed up at the aurora, on a round base: a gold rim, a navy
    # star chart with the crest lying on it (in front of the tripod, clear of the tube from above).
    lathe('Body', [(1.05, 0.0), (1.05, 0.14)], 'wood_dark', n=16)
    lathe('Body', [(1.07, 0.03), (1.07, 0.11)], 'gold', n=16)
    lathe('Body', [(0.95, 0.13), (0.95, 0.16)], 'navy', n=16)
    emblem('Body', WOLF, 0.32, flat((0, 0.1675, -0.58)), depth=0.015, step=0.015)
    hub = Vector((-0.04, 3.5, 0.15))
    feet = [Vector((-0.04, 0.14, 1.0)), Vector((-0.8, 0.16, -0.28)), Vector((0.72, 0.16, -0.28))]
    for f in feet:
        rod('Body', hub, f, 0.06, 'wood_light', n=6)
        sphere('Body', f + Vector((0, 0.04, 0)), 0.08, 'gold', n=6, rings=4)
    mids = [hub + (f - hub) * 0.62 for f in feet]
    for i in range(3):
        rod('Body', mids[i], mids[(i + 1) % 3], 0.03, 'gold', n=4)                                # the spreaders
    cyl('Body', hub + Vector((0, -0.05, 0)), 0.16, 0.27, 'gold', n=8)
    cyl('Body', hub + Vector((0, 0.2, 0)), 0.07, 0.3, 'gold', n=6)                                # the post
    T = Matrix.Translation(hub + Vector((0, 0.6, 0))) @ Matrix.Rotation(math.radians(-60), 4, 'Z')  # 30 deg up, +X
    lathe('Body', [(0.15, -0.85), (0.19, 0.68)], 'navy', n=10, m=T)                               # the tube
    for y in (-0.75, 0.45):
        rb = 0.15 + 0.04 * (y + 0.85) / 1.53 + 0.025
        lathe('Body', [(rb, y - 0.05), (rb, y + 0.05)], 'gold', n=10, m=T)                       # its bands
    lathe('Body', [(0.165, -0.07), (0.25, -0.07), (0.25, 0.07), (0.165, 0.07)], 'gold', n=10, closed=True,
          m=T)                                                                                     # the cradle
    lathe('Body', [(0.185, 0.64), (0.25, 0.64), (0.25, 1.08), (0.185, 1.08)], 'gold', n=10, closed=True, m=T)
    cyl('Body', (0, 0.9, 0), 0.205, 0.05, 'ice', n=10, m=T)                                       # the lens
    cyl('Body', (0, -1.08, 0), 0.07, 0.25, 'black', n=8, m=T)                                     # the eyepiece
    lathe('Body', [(0.1, -1.1), (0.1, -1.02)], 'gold', n=8, m=T)
    cyl('Body', (-0.21, -0.35, 0), 0.045, 0.5, 'gold', n=6, m=T)                                  # the finder
    sdone('a brass telescope aimed up at the aurora (a navy tube with gold bands, a gold cradle and dew cap, an '
          'ice lens, a finder) on a light wood tripod with gold spreaders and feet, on a round base: a gold rim, '
          'a navy star chart with the crest (the gold wolf\'s head) lying in front of the tripod', colour='gold')


SLEIGH = [(-1.55, 0.85), (1.75, 0.85), (2.0, 1.4), (2.1, 2.3), (2.0, 2.9), (1.75, 3.1), (1.5, 3.0), (1.5, 2.6),
          (1.6, 2.2), (1.35, 1.85), (-0.9, 1.85), (-1.3, 2.0), (-1.7, 2.45), (-2.05, 2.7), (-2.3, 2.65), (-2.35, 2.4),
          (-2.15, 2.2), (-1.95, 1.55)]
RUNNER = [(2.25, 0.45), (2.15, 0.2), (1.9, 0.07), (-1.8, 0.07), (-2.2, 0.15), (-2.42, 0.4), (-2.48, 0.7),
          (-2.38, 0.95), (-2.2, 1.05), (-2.05, 0.95), (-2.05, 0.8)]


def d_lodge_sleigh():
    sdecor('Sleigh')
    # A red sleigh, a gold edge round both side panels (it shows from above as two gold lines), a swan-curl dash
    # and a high curled back, on gold runners curling up in front; a navy blanket with the crest lying on it
    # (from above) and the crest on both sides; a white fur cushion at the back; a lantern hung over the dash.
    prism('Body', SLEIGH, -0.8, 0.8, 'red', plane='xy')
    for s in (-1, 1):
        for line, z0, z1 in ((SLEIGH[1:] + SLEIGH[:1], 0.79, 0.84), (SLEIGH[:2], 0.795, 0.825)):  # its own planes
            prism('Body', stroke(line, 0.12), s * z0, s * z1, 'gold', plane='xy')
    for z in (-0.62, 0.62):
        prism('Body', stroke(RUNNER, 0.14), z - 0.05, z + 0.05, 'gold', plane='xy')
        for x in (-1.3, 0.1, 1.5):
            rod('Body', (x, 0.1, z), (x, 0.9, z), 0.04, 'gold', n=4)
    span('Body', (-0.85, 1.85, -0.9), (1.4, 2.0, 0.9), 'navy')                                    # the blanket
    for s in (-1, 1):
        span('Body', (-0.6, 1.62, min(s * 0.9, s * 0.85)), (1.15, 1.85, max(s * 0.9, s * 0.85)), 'navy')
        emblem('Body', WOLF, 0.26, at((0.25, 1.3, s * (0.8 + 0.03)), ry=0 if s < 0 else 180), depth=0.08)
    emblem('Body', WOLF, 0.42, flat((0.15, 2.01, 0)), depth=0.02, step=0.015)
    span('Body', (1.2, 1.87, -0.62), (1.5, 2.75, 0.62), 'fur', bevel=0.06)                        # the cushion
    rod('Body', (-1.85, 2.4, 0), (-1.85, 3.45, 0), 0.05, 'iron', n=6)                             # the lantern
    rod('Body', (-1.85, 3.45, 0), (-2.2, 3.62, 0), 0.04, 'iron', n=6)
    rod('Body', (-2.2, 3.64, 0), (-2.2, 3.44, 0), 0.02, 'iron', n=4)
    cyl('Body', (-2.2, 3.3, 0), 0.17, 0.15, 'gold', n=6, r_top=0.05)
    cyl('Glow_Warm_1', (-2.2, 2.95, 0), 0.12, 0.35, 'flame', n=6)
    cyl('Body', (-2.2, 2.88, 0), 0.15, 0.07, 'gold', n=6)
    sdone('a red sleigh edged in gold, a swan-curl dash and a high curled back, on gold runners curling up in '
          'front; a navy blanket with the crest (the gold wolf\'s head) lying on it, the crest on both sides, a '
          'white fur cushion; a lantern (Glow_Warm_1) hung over the dash on an iron crook', colour='red')


# --- The Lantern Grove (Bayou Spa) ------------------------------------------------------------------------
# One crest on every piece: a dragonfly seen from above (four pale wings, a brass body: head, thorax, a long
# tail), the bayou's own creature, which reads as itself from the top-down camera.

DF_FORE = [(0.08, 0.56), (0.32, 0.69), (0.66, 0.74), (0.96, 0.69), (0.98, 0.58), (0.66, 0.50), (0.12, 0.44)]
DF_HIND = [(0.08, 0.38), (0.40, 0.40), (0.78, 0.30), (0.96, 0.16), (0.86, 0.07), (0.50, 0.14), (0.10, 0.28)]
DF_BODY_R = [(0.0, 0.94), (0.09, 0.91), (0.14, 0.82), (0.12, 0.72), (0.08, 0.67), (0.13, 0.60), (0.14, 0.42),
             (0.08, 0.27), (0.075, -0.2), (0.065, -0.8), (0.04, -0.97), (0.0, -1.0)]
DRAGONFLY = [(DF_FORE, 'moonstone', 0), (mirror(DF_FORE), 'moonstone', 0), (DF_HIND, 'moonstone', 0),
             (mirror(DF_HIND), 'moonstone', 0), (sym(DF_BODY_R), 'brass', 1)]


def pad_xy(cx, cy, r, notch, n=12):
    """A lily pad seen from the front of a picture: a disc with its V notch toward `notch` degrees."""
    a0 = math.radians(notch)
    return [(cx, cy)] + [(cx + r * math.cos(a0 + math.radians(16 + 328 * i / n)),
                          cy + r * math.sin(a0 + math.radians(16 + 328 * i / n))) for i in range(n + 1)]


def d_grove_glass():
    sdecor('StainedGlass')
    # A round stained-glass window at eye level (2.6 to 6.5): the dragonfly large over a dusk bayou (a plum sky,
    # the moon glowing, teal water, two lily pads and a lotus, two fireflies), in a moulded round frame
    # (dark cypress, cypress, brass), Spanish moss draped over its top; a firefly jar hung either side.
    back, cy = 1.1, 4.55
    prism('Body', ellipse(0, cy, 1.89, 1.89, 18), 0.97, back, 'plum')                               # the glass
    rings = [(0.16, 0.80, 0.985, 'cypress_dark'), (0.18, 0.68, 0.99, 'cypress'), (0.10, 0.76, 0.995, 'brass')]
    r = 1.95
    for t, front, rear, col in rings:
        for half in ring_halves(cy, r, r - t):
            prism('Body', half, front, rear, col, plane='xy')
        r = r - t + 0.01
    wl = cy - 0.8                                                                                   # the water
    a1 = math.degrees(math.asin(-0.8 / 1.55))
    arc = [(1.55 * math.cos(math.radians(a)), cy + 1.55 * math.sin(math.radians(a)))
           for a in np.linspace(a1, -180 - a1, 9)]
    prism('Body', arc, 0.957, 0.98, 'water')
    prism('Glow_Cold_1', ellipse(-0.75, 5.55, 0.28, 0.28, 12), 0.957, 0.98, 'moonglow')            # the moon
    prism('Body', pad_xy(-0.55, 3.5, 0.32, 60), 0.944, 0.97, 'lily')
    prism('Body', pad_xy(0.75, 3.62, 0.28, 120), 0.944, 0.97, 'lily')
    cx, cyl_ = 0.75, 3.72                                                                           # the lotus
    prism('Body', [(cx - 0.3, cyl_), (cx - 0.15, cyl_ - 0.1), (cx + 0.15, cyl_ - 0.1), (cx + 0.3, cyl_),
                   (cx + 0.22, cyl_ + 0.18), (cx + 0.12, cyl_ + 0.12), (cx, cyl_ + 0.32), (cx - 0.12, cyl_ + 0.12),
                   (cx - 0.22, cyl_ + 0.18)], 0.931, 0.96, 'lotus')
    for k, (x, y) in enumerate(((0.95, 5.65), (-1.15, 4.1))):                                       # fireflies
        prism(f'Glow_Warm_{k + 1}', [(x, y - 0.08), (x + 0.07, y), (x, y + 0.08), (x - 0.07, y)], 0.944, 0.97,
              'firefly')
    emblem('Body', DRAGONFLY, 0.85, at((0.2, 4.55, 0.9465)), depth=0.057)                          # the crest
    upper = [(2.02 * math.cos(math.radians(a)), cy + 2.02 * math.sin(math.radians(a))) for a in np.linspace(145, 35, 8)]
    lower = [((1.7 if i % 2 == 0 else 1.86) * math.cos(math.radians(a)),
              cy + (1.7 if i % 2 == 0 else 1.86) * math.sin(math.radians(a))) for i, a in enumerate(np.linspace(35, 145, 11))]
    prism('Body', upper + lower, 0.66, 0.95, 'moss')                                                 # the moss
    for k, x in enumerate((-2.3, 2.3)):
        span('Body', (x - 0.1, 4.95, 1.0), (x + 0.1, 5.5, back), 'brass', bevel=0.02)
        seg('Body', (x, 5.35, 1.0), (x, 5.35, 0.55), 0.04, 'brass')
        sphere('Body', (x, 5.35, 0.55), 0.06, 'brass', n=6, rings=4)
        firefly_lantern(f'Glow_Warm_{k + 3}', (x, 5.3, 0.55))
    sdone('a round stained-glass window at eye level (2.6 to 6.5): the crest (the dragonfly, pale wings and a '
          'brass body) large over a dusk bayou (a plum sky, the moon Glow_Cold_1, teal water, lily pads, a lotus, '
          'fireflies Glow_Warm_1, _2) in a moulded round frame (dark cypress, cypress, brass) under draped moss; '
          'a firefly jar hung either side (Glow_Warm_3, _4)', colour='plum')


def d_grove_rug():
    sdecor('Rug')
    # A woven rug: a dark cypress edge, a rattan band, teal water; a great lily pad (its notch to the front
    # right) with the crest large on it (2.0 long, its head away from the door), a pale ripple round it, a
    # lotus in each corner.
    hx, hz = 4.5, 3.0
    span('Body', (-hx, 0.0, -hz), (hx, 0.03, hz), 'cypress_dark')
    span('Body', (-hx + 0.25, 0.03, -hz + 0.25), (hx - 0.25, 0.05, hz - 0.25), 'rattan')
    span('Body', (-hx + 0.5, 0.05, -hz + 0.5), (hx - 0.5, 0.07, hz - 0.5), 'water')
    ro, ri = 2.45, 2.3                                                                              # the ripple
    for half in ring_halves(0.0, ro, ri, n=12):
        prism('Body', half, 0.07, 0.085, 'water_light', plane='xz')
    lily_pad((0, 0.07, 0), 2.15, 0.015, 'lily', notch=-45, n=28)
    emblem('Body', DRAGONFLY, 1.3, flat((0, 0.0925, -0.02)), depth=0.015, step=0.015)            # 0.085 to 0.115
    for sx in (-1, 1):
        for sz in (-1, 1):
            cx, cz = sx * 3.55, sz * 2.0
            pts = [(cx + 0.42 * math.cos(a) * (1 if i % 2 == 0 else 0.45), cz + 0.42 * math.sin(a) * (1 if i % 2 == 0 else 0.45))
                   for i, a in enumerate(math.pi / 6 * j + math.pi / 12 for j in range(12))]
            prism('Body', pts, 0.07, 0.085, 'lotus', plane='xz')
            prism('Body', ellipse(cx, cz, 0.13, 0.13, 8), 0.085, 0.1, 'lotus_heart', plane='xz')
    sdone('the Grove\'s rug: teal water in a rattan band and a dark cypress edge, a great lily pad with the crest '
          '(the dragonfly, 2.0 long, its head away from the door) inside a pale ripple, a lotus in each corner',
          colour='water')


def d_grove_lamp():
    sdecor('Lamp')
    # A dragonfly floor lamp: a lily-pad foot, a brass reed stem with two leaves, an eight-sided shade of warm
    # glass (Glow_Warm_1, all of it) with a brass dragonfly on four of its panels (heads up the slope: from above
    # four crests round a lotus bud), a brass rim and cap.
    lily_pad((0, 0, 0), 0.98, 0.1, 'lily_dark', notch=-60, n=14)
    lathe('Body', [(0.42, 0.08), (0.36, 0.2), (0.16, 0.4), (0.09, 0.62)], 'brass', n=10)
    cyl('Body', (0, 0.55, 0), 0.075, 4.1, 'brass', n=8)
    for i, ang in enumerate((25, 145)):
        prism('Body', [(-0.09, 0.0), (0.09, 0.0), (0.02, 1.7 - 0.3 * i)], -0.02, 0.02, 'lily', plane='xy',
              m=at((0, 0.42, 0), ry=ang, rz=8))
    lathe('Glow_Warm_1', [(1.0, 4.55), (1.0, 4.85), (0.36, 5.35)], 'lamp', n=8)                    # the shade
    lathe('Body', [(0.98, 4.5), (1.04, 4.5), (1.04, 4.6), (0.98, 4.6)], 'brass', n=8, closed=True)
    lathe('Body', [(0.4, 5.32), (0.3, 5.45), (0.08, 5.52)], 'brass', n=8)
    sphere('Body', (0, 5.64, 0), (0.12, 0.18, 0.12), 'lotus', n=8, rings=5)                         # a lotus bud
    tilt, depth = math.degrees(math.atan2(0.763, 0.646)), 0.05
    nrm = Vector((0, 0.763, -0.646))
    pos = Vector((0, 5.1, -0.628)) + nrm * (depth / 2 - 0.01)
    for ry in (0, 90, 180, 270):
        emblem('Body', DRAGONFLY, 0.28, Matrix.Rotation(math.radians(ry), 4, 'Y') @ at(pos, rx=tilt), depth=depth)
    sdone('a dragonfly floor lamp: a lily-pad foot, a brass reed stem with two leaves, an eight-sided shade of '
          'warm glass (Glow_Warm_1) with the crest (a brass and pale dragonfly) on four panels, a brass rim, a '
          'brass cap and a lotus bud', colour='lamp')


HORN = [(0.1, 0.0), (0.14, 0.35), (0.24, 0.7), (0.42, 0.98), (0.68, 1.15), (0.86, 1.22),
        (0.8, 1.2), (0.6, 1.1), (0.36, 0.92), (0.2, 0.68), (0.08, 0.4), (0.05, 0.05)]


def d_grove_gramophone():
    sdecor('Gramophone')
    # A cypress gramophone cabinet on brass ball feet, a plum-velvet speaker front in a dark frame with the crest
    # on it, a brass band under the lid; a brass turntable with a record (a lotus label) and tonearm; a horn
    # shaped as a flower (brass outside, lotus pink inside) rising from the back, a brass dragonfly perched on
    # its rim (from above: the horn's pink mouth and the crest).
    for x in (-0.7, 0.7):
        for z in (-0.7, 0.7):
            sphere('Body', (x, 0.12, z), (0.14, 0.12, 0.14), 'brass', n=6, rings=4)
    span('Body', (-0.92, 0.18, -0.92), (0.92, 0.42, 0.92), 'cypress_dark', bevel=0.04)
    span('Body', (-0.8, 0.4, -0.8), (0.8, 2.3, 0.8), {'front': 'velvet', 'rest': 'cypress'})
    for lo, hi in (((-0.82, 0.4), (0.82, 0.62)), ((-0.82, 2.08), (0.82, 2.3)), ((-0.82, 0.62), (-0.6, 2.08)),
                   ((0.6, 0.62), (0.82, 2.08))):           # 0.02 proud of the sides: no shared side planes
        span('Body', (lo[0], lo[1], -0.86), (hi[0], hi[1], -0.79), 'cypress_dark')               # the frame
    emblem('Body', DRAGONFLY, 0.42, at((0, 1.35, -0.83)), depth=0.07)
    span('Body', (-0.83, 2.22, -0.83), (0.83, 2.3, 0.83), 'brass')
    span('Body', (-0.9, 2.3, -0.9), (0.9, 2.45, 0.9), 'cypress_dark', bevel=0.04)                 # the lid
    cyl('Body', (0, 2.45, -0.12), 0.66, 0.07, 'brass', n=16)                                       # turntable
    cyl('Body', (0, 2.52, -0.12), 0.6, 0.03, 'black', n=16)
    cyl('Body', (0, 2.55, -0.12), 0.2, 0.015, 'lotus', n=10)
    cyl('Body', (0.0, 2.45, 0.68), 0.12, 0.37, 'brass', n=8)                                       # horn column
    seg('Body', (0.0, 2.72, 0.62), (0.28, 2.64, -0.05), 0.035, 'brass')                           # tonearm
    cyl('Body', (0.28, 2.56, -0.05), 0.1, 0.1, 'brass', n=8)
    d = Vector((0, 0.82, -0.57)).normalized()
    base = Vector((0, 3.3, 0.5))
    seg('Body', (0, 2.78, 0.68), base + 0.05 * d, 0.1, 'brass', n=8)                              # the neck
    hm = Matrix.Translation(base) @ Vector((0, 1, 0)).rotation_difference(d).to_matrix().to_4x4()
    lathe_coloured('Body', HORN, ['brass'] * 6 + ['lotus_light'] * 5 + ['brass'], 14, hm)
    lip = base + 1.22 * d + 0.86 * Vector((0, 0.57, 0.82)).normalized()
    emblem('Body', DRAGONFLY, 0.3, flat(lip + Vector((0, 0.025, 0.15)), ry=180), depth=0.03, step=0.015)  # thorax on the lip
    seg('Body', (0.8, 1.5, 0.0), (0.98, 1.5, 0.0), 0.035, 'brass')                                # the crank
    seg('Body', (0.98, 1.5, 0.0), (0.98, 1.2, 0.0), 0.03, 'brass')
    sphere('Body', (0.98, 1.16, 0.0), 0.06, 'cypress_dark', n=6, rings=4)
    sdone('a cypress gramophone on brass ball feet: a plum-velvet front in a dark frame with the crest (the '
          'dragonfly), a brass band under the lid, a brass turntable with a record and tonearm, a flower horn '
          '(brass outside, lotus pink inside) with a brass dragonfly perched on its rim', colour='cypress')


def _boat(x):
    f = min(1.0, abs(x) / 2.45)
    w = 0.8 * max(0.005, 1 - f * f) ** 0.55
    return w, 0.28 * f ** 3, 0.8 + 0.22 * f ** 3        # half-width at the top, the bottom's rise, the fill's top


def d_grove_pirogue():
    sdecor('Pirogue')
    # A cypress pirogue (the bayou's flat-bottomed canoe) as a planter: moss to its gunwales, a lotus, two lily
    # pads and a clump of cattails with a firefly; a lantern (a firefly jar) hung from a crooked pole over the
    # bow (-X); the crest on both sides and on the bow's deck.
    secs = []
    for x in np.linspace(-2.45, 2.45, 11):
        w, b, t = _boat(x)
        secs.append([(x, b, -0.65 * w), (x, b, 0.65 * w), (x, t, w), (x, t, -w)])
    loft('Body', secs, {'bottom': 'cypress_dark', 'side': 'cypress', 'top': 'moss_dark', 'cap': 'cypress'})
    for s, xe, lift in ((-1, 2.5, 0.0), (1, 2.47, 0.015)):          # the gunwales, one a hair over the other
        strip = []
        for x in np.linspace(-xe, xe, 11):
            w, b, t = _boat(x)
            zi, zo = s * (w - 0.07), s * (w + 0.04)
            lo, hi = t - 0.12 - lift, t + 0.1 + lift
            strip.append([(x, lo, min(zi, zo)), (x, lo, max(zi, zo)), (x, hi, max(zi, zo)), (x, hi, min(zi, zo))])
        loft('Body', strip, {'bottom': 'cypress_light', 'side': 'cypress_light', 'top': 'cypress_light',
                             'cap': 'cypress_light'})
    deck = []                                                       # the bow's deck, rising with the sheer
    for x in np.linspace(-1.8, -2.42, 4):
        w, b, t = _boat(x)
        hw = max(0.02, w - 0.06)
        deck.append([(x, t - 0.02, -hw), (x, t - 0.02, hw), (x, t + 0.05, hw), (x, t + 0.05, -hw)])
    loft('Body', deck, {'bottom': 'cypress_light', 'side': 'cypress_light', 'top': 'cypress_light',
                        'cap': 'cypress_light'})
    x0, x1 = -1.9, -2.2
    slope = math.atan2(_boat(x1)[2] - _boat(x0)[2], x0 - x1)       # the deck's rise toward the bow (-X)
    yc = _boat(-2.05)[2] + 0.05 + 0.0075
    emblem('Body', DRAGONFLY, 0.22, Matrix.Translation((-2.05, yc, 0)) @ Matrix.Rotation(-slope, 4, 'Z')
           @ flat((0, 0, 0), ry=-90), depth=0.015, step=0.015)                                  # its head to the bow
    w0, b0, t0 = _boat(0.25)
    for s in (-1, 1):              # on each side, leaning with the flare (the side faces out and a little down)
        flare = math.degrees(math.atan2(0.35 * w0, t0 - b0))
        mid = Vector((0.25, (b0 + t0) / 2 - 0.03, s * (0.825 * w0 - 0.0105)))
        nrm = Vector((0, -math.sin(math.radians(flare)), s * math.cos(math.radians(flare))))
        emblem('Body', DRAGONFLY, 0.34, Matrix.Translation(mid + nrm * 0.02)
               @ at((0, 0, 0), rx=-flare, ry=0 if s < 0 else 180), depth=0.06)
    lotus((-0.85, _boat(-0.85)[2] - 0.02, -0.15), s=1.0)
    lily_pad((-0.15, _boat(-0.15)[2] - 0.01, 0.25), 0.36, 0.04, 'lily', notch=200)
    lily_pad((1.0, _boat(1.0)[2] - 0.01, -0.22), 0.32, 0.04, 'lily_light', notch=30)
    cattails(1.7, 0.1, y=_boat(1.7)[2] - 0.02, k=3, tall=2.0, firefly='Glow_Warm_2')
    yb = _boat(-1.55)[2] - 0.05
    seg('Body', (-1.55, yb, 0.05), (-1.62, 3.0, 0.05), 0.07, 'cypress_dark')                     # the pole
    seg('Body', (-1.62, 3.0, 0.05), (-1.95, 3.55, 0.05), 0.06, 'cypress_dark')
    seg('Body', (-1.95, 3.55, 0.05), (-2.12, 3.48, 0.05), 0.05, 'cypress_dark')
    firefly_lantern('Glow_Warm_1', (-2.12, 3.47, 0.05))
    sdone('a cypress pirogue as a planter: moss to its light gunwales, a lotus, two lily pads, cattails with a '
          'firefly (Glow_Warm_2); a firefly jar (Glow_Warm_1) hung from a crooked pole over the bow; the crest (the '
          'dragonfly) on both sides and on the bow\'s deck', colour='cypress')


# --- The souvenir ---------------------------------------------------------------------------------------

def souvenir():
    # Blind review 2026-10-21: the first (a cushion and a 0.8 medal in a ring of four tassels on a square
    # top) read from above as a loudspeaker. Now a prize rosette under a tall bell jar on a low plinth: from
    # above a scalloped ribbon disc with its two tails running to the front edge and folding over it (an
    # award's sign, and no concentric rings of equal weight), the medal 1.2 across (the emblem's face, three
    # times the first's area), and from the front and the raised camera the jar's dome and the name plaque.
    p = K.decor('Souvenir_Base', 1, 1, 'Floor')
    p.name = 'Souvenir_Base'
    p.checks.append(NS['grounded_check'])
    p.checks.append(no_use_check)
    p.checks.append(souvenir_check)
    for n in ('Ribbon', 'Trim', 'Medal', 'Badge', 'Glass'):
        K.declare(n, False)
    span('Body', (-1.0, 0.0, -1.0), (1.0, 0.22, 1.0), 'wood_dark', bevel=0.05)       # the plinth's foot
    span('Body', (-0.8, 0.2, -0.8), (0.8, 1.47, 0.8), 'wood_dark')                   # its shaft, ends buried
    span('Body', (-1.04, 1.45, -1.04), (1.04, 1.65, 1.04), 'wood_dark', bevel=0.04)  # its top
    span('Trim', (-0.85, 0.22, -0.85), (0.85, 0.32, 0.85), 'gold')                   # its bands, tinted
    span('Trim', (-0.85, 1.35, -0.85), (0.85, 1.45, 0.85), 'gold')
    span('Body', (-0.62, 0.58, -0.84), (0.62, 1.16, -0.79), 'gold')                  # the plaque's gold mount
    span('Badge', (-0.54, 0.64, -0.86), (0.54, 1.1, -0.8), 'bone')                   # the name plaque
    lathe('Trim', [(0.92, 1.64), (1.0, 1.64), (1.0, 1.7), (0.92, 1.7)], 'gold', n=16, closed=True)  # jar's foot
    # The rosette, its middle 0.08 behind the plinth's so the tails have room in front.
    zc = 0.08
    for s, top in ((-1, 1.685), (1, 1.69)):     # the tails: splayed 20 degrees, to the top's front edge
        k = s * math.tan(math.radians(20))
        x0, x1, z0, z1 = k * (zc + 0.1), k * (zc + 1.06), -0.1, -1.06
        prism('Ribbon', [(x0 - 0.13, z0), (x0 + 0.13, z0), (x1 + 0.13, z1), (x1 - 0.13, z1)], 1.645, top,
              'crimson', plane='xz')
        prism('Ribbon', [(x1 - 0.13, top + 0.005), (x1 + 0.13, top + 0.005), (x1 + 0.13, 1.32), (x1, 1.42),
                         (x1 - 0.13, 1.32)], -1.085, -1.035, 'crimson', plane='xy')   # folded over, notched
    pleats = [(0.8 - 0.1 * (1 - abs(math.sin(8 * a))), a) for a in [2 * math.pi * i / 48 for i in range(48)]]
    prism('Ribbon', [(r * math.cos(a), zc + r * math.sin(a)) for r, a in pleats], 1.645, 1.75, 'crimson',
          plane='xz')                                                                 # 16 rounded pleats
    cyl('Trim', (0, 1.72, zc), 0.66, 0.08, 'gold', n=16)                              # the medal's rim
    cyl('Medal', (0, 1.76, zc), 0.6, 0.12, 'gold', n=16)                              # its top flat at 1.88
    lathe('Glass', [(0.96, 1.66), (0.96, 2.8), (0.84, 3.28), (0.56, 3.58), (0.0, 3.7)], 'moon', n=16)
    sdone('a keepsake on display: a prize rosette (Ribbon: 16 pleats and two tails folded over the front '
          'edge) with a gold rim (Trim) round a medal 1.2 across (Medal, its top for the emblem), under a tall '
          'bell jar (Glass, no knob: it would hide the emblem from above) on a foot ring (Trim), on a low dark '
          'wood plinth with two bands (Trim) and a gold-mounted name plaque (Badge, its front for the name)')


# --- Review (Workbench on light grey only: Studio runs) ----------------------------------------------

PERSON_RGB = None
WALL_RGB = (170, 135, 210)              # the Manor's lilac paper, behind a Wall piece
FLOOR_RGB = (150, 150, 156)


def squares(cx, cz, w, d, y=-0.06):
    for i in range(w):
        for k in range(d):
            x0, z0 = cx - 1.5 * w + 3 * i, cz - 1.5 * d + 3 * k
            shade = (205, 205, 210) if (i + k) % 2 else (185, 185, 192)
            _block('sq', (x0 + 0.03, y, z0 + 0.03), (x0 + 2.97, y + 0.05, z0 + 2.97), shade)


def tint(objs, ribbon, trim):
    for ob in objs:
        base = ob.name.split('.')[0]
        if base == 'Ribbon':
            ob.data.materials.clear()
            ob.data.materials.append(_flat(f'flat_{ribbon}', ribbon))
        elif base == 'Trim':
            ob.data.materials.clear()
            ob.data.materials.append(_flat(f'flat_{trim}', trim))


def hide(objs, part):
    for ob in objs:
        if ob.name.split('.')[0] == part:
            ob.hide_render = True


def darker(rgb, f=0.6):
    return tuple(int(c * f) for c in rgb)


SPECIES = [     # (name, look.colour from src/shared/Species.luau): the souvenir's tints in the sheet
    ('VampireCount', None), ('Slime', (110, 220, 120)), ('Ghost', (220, 235, 255)), ('Werewolf', (120, 95, 75))]


def review_set(rev, fbx, names, manifest, wall_rgb=WALL_RGB):
    """Each piece on its squares beside the 5-stud person, from the front three-quarters."""
    clear()
    x, shots = 0.0, []
    for n in names:
        w, d = manifest[n]['decor']['fw'], manifest[n]['decor']['fd']
        cx = x + 1.5 * w
        objs = place(fbx, n, (cx, 0, 0))
        if n == 'Souvenir_Base':
            hide(objs, 'Glass')
        squares(cx, 0, w, d)
        if manifest[n]['decor']['layer'] == 'Wall':
            _block('wall', (cx - 1.5 * w, 0, 1.5 * d - 0.4), (cx + 1.5 * w, 7.6, 1.5 * d - 0.1), wall_rgb)
        x += 3 * w + 1.0
    _person(Vector((x + 1.5, 0, 0)), 0.0)
    _block('floor', (-2, -0.3, -5), (x + 5, -0.07, 4), FLOOR_RGB)
    shots.append(render(rev / 'set_front.png', (-0.4, 0.45, -1.0), (1500, 560), (-1, 0, -3.5), (x + 4, 7.2, 3.2),
                        scale=1.02))
    shots.append(render(rev / 'set_raised.png', (-0.3, 1.0, -0.8), (1500, 560), (-1, 0, -3.5), (x + 4, 7.2, 3.2),
                        scale=1.02))
    return _compose([[p] for p in shots], rev / 'set_sheet.png')


def review_elevations(rev, fbx, names, manifest):
    rows = []
    for n in names:
        clear()
        w, d = manifest[n]['decor']['fw'], manifest[n]['decor']['fd']
        objs = place(fbx, n, (0, 0, 0))
        if n == 'Souvenir_Base':
            hide(objs, 'Glass')
        _block('floor', (-1.5 * w - 1, -0.3, -1.5 * d - 1), (1.5 * w + 1, -0.01, 1.5 * d + 1), FLOOR_RGB)
        _person(Vector((1.5 * w + 2.4, 0, 0)), 0.0)
        lo, hi = (-1.5 * w - 0.3, 0, -1.5 * d), (1.5 * w + 3.5, 7.2, 1.5 * d)
        f = render(rev / f'elev_{n}_front.png', (0, 0.0001, -1), (700, 520), lo, hi, scale=1.05)
        for ob in bpy.data.objects:     # the person stands at +X: out of the side view's way
            if ob.name.startswith('person'):
                ob.hide_render = True
        s = render(rev / f'elev_{n}_side.png', (1, 0.0001, 0), (700, 520), (-1.5 * w, 0, -1.5 * d - 0.3),
                   (1.5 * w, 7.2, 1.5 * d + 3.5), scale=1.05)
        rows.append([f, s])
    return _compose(rows, rev / 'elevations_sheet.png')


STUDY = [   # the set in a 2 x 2 cell study (24 x 24, the door side -Z): (name, (x, z), turn)
    ('Decor_CountStudy_Rug', (0, 0), 0), ('Decor_CountStudy_Portrait', (0, 10.5), 0),
    ('Decor_CountStudy_Clock', (-10.5, 10.5), 0), ('Decor_CountStudy_Bust', (10.5, 10.5), 0),
    ('Decor_CountStudy_Globe', (-7.5, -1.5), 0),
]


def review_topdown(rev, fbx, souvenir_fbx, study=None, floor_rgb=(120, 82, 55), wall_rgb=WALL_RGB):
    """The set laid out in a room, straight down and from the raised build camera; four souvenirs when
    souvenir_fbx is given."""
    clear()
    for n, (x, z), ang in (study or STUDY):
        place(fbx, n, (x, 0, z), ang)
    for k, (sp, rgb) in enumerate(SPECIES if souvenir_fbx else []):
        objs = place(souvenir_fbx, 'Souvenir_Base', (10.5, 0, 4.5 - 3 * k))
        if rgb:
            tint(objs, rgb, darker(rgb))
        hide(objs, 'Glass')         # the code makes it glass; opaque in Workbench it would hide the emblem
    _block('floor', (-12, -0.3, -12), (12, -0.01, 12), floor_rgb)
    for lo, hi in (((-12, 0, 11.6), (12, 2.5, 12)), ((-12, 0, -12), (-11.6, 2.5, 12)),
                   ((11.6, 0, -12), (12, 2.5, 12)), ((-12, 0, -12), (-2, 2.5, -11.6)),
                   ((2, 0, -12), (12, 2.5, -11.6))):
        _block('wall', lo, hi, wall_rgb)
    _person(Vector((0, 0, 0)), -8.0)
    top = render(rev / 'topdown.png', (0.0001, 1, -0.0001), (1000, 1000), (-12.5, 0, -12.5), (12.5, 7, 12.5),
                 scale=1.02)
    raised = render(rev / 'raised.png', (0, 1.0, -0.75), (1200, 900), (-12.5, 0, -12.5), (12.5, 7, 12.5),
                    scale=1.02)
    img = bpy.data.images.load(str(top))
    img.scale(360, 360)
    img.filepath_raw = str(rev / 'topdown_phone.png')
    img.file_format = 'PNG'
    img.save()
    bpy.data.images.remove(img)
    return top, raised, rev / 'topdown_phone.png'


def review_souvenir(rev, fbx):
    shots = []
    for glass in (False, True):
        clear()
        for k, (sp, rgb) in enumerate(SPECIES):
            objs = place(fbx, 'Souvenir_Base', (4 * k, 0, 0))
            if rgb:
                tint(objs, rgb, darker(rgb))
            if not glass:
                hide(objs, 'Glass')
        _person(Vector((4 * len(SPECIES) + 0.5, 0, 0)), 0.0)
        _block('floor', (-2.5, -0.3, -3), (4 * len(SPECIES) + 3, -0.01, 3), FLOOR_RGB)
        tag = 'glass' if glass else 'open'
        shots.append(render(rev / f'souvenir_{tag}.png', (-0.35, 0.5, -1.0), (1400, 560), (-1.5, 0, -1.5),
                            (4 * len(SPECIES) + 2, 5.2, 1.5), scale=1.03))
    clear()
    for k, (sp, rgb) in enumerate(SPECIES):
        objs = place(fbx, 'Souvenir_Base', (4 * k, 0, 0))
        if rgb:
            tint(objs, rgb, darker(rgb))
        hide(objs, 'Glass')
    _block('floor', (-2.5, -0.3, -3), (4 * len(SPECIES) + 1, -0.01, 3), FLOOR_RGB)
    shots.append(render(rev / 'souvenir_top.png', (0.0001, 1, -0.0001), (1400, 560), (-1.6, 0, -1.6),
                        (4 * len(SPECIES) - 2.4, 4, 1.6), scale=1.03))
    return _compose([[p] for p in shots], rev / 'souvenir_sheet.png')


# --- The sets ---------------------------------------------------------------------------------------

def build_set(set_dir, title, builds, cur=None, palette=None):
    global CUR
    if cur is not None:
        CUR = cur
    K.BUILT.clear()
    K.use_palette(palette or PALETTE)
    K.start_set(set_dir)
    refused = []
    for name, fn in builds:
        if K.ONLY is not None and name not in K.ONLY:
            continue
        try:
            fn()
        except K.Refused as e:
            print(str(e), flush=True)
            refused.append(name)
    if refused:
        return refused, None
    built = [p.name for p, _, _ in K.BUILT]
    K.end_set(title, [(built, 2.0, 1.0)], sheet=False)
    out = K.ROOT / 'blender' / set_dir
    return [], json.loads((out / 'manifest.json').read_text())


def stage(set_dir, names):
    dst = K.ROOT / 'blender' / '_import'
    dst.mkdir(exist_ok=True)
    for n in names:
        shutil.copy2(K.ROOT / 'blender' / set_dir / 'fbx' / f'{n}.fbx', dst / f'{n}.fbx')
        print(f'STAGED {n}.fbx', flush=True)


# The Lodge's and the Grove's: (dir, title, the set, its palette, its pieces, a 2 x 2 cell room's layout
# (the door side -Z), the room's floor and wall colours for the sheets).
LOCATION_SETS = [
    ('decor/aurora_lodge', "The Aurora Lodge (Frostfang Lodge's rare decor set)",
     {'id': 'AuroraLodge', 'location': 2, 'rows': LODGE_ROWS}, FF_PALETTE,
     [('Painting', d_lodge_painting), ('WolfStatue', d_lodge_wolf), ('Telescope', d_lodge_telescope),
      ('Sleigh', d_lodge_sleigh), ('Rug', d_lodge_rug)],
     [('Rug', (0, 0), 0), ('Painting', (0, 10.5), 0), ('WolfStatue', (-10.5, 10.5), 0),
      ('Telescope', (10.5, 10.5), 0), ('Sleigh', (7.5, -6.0), 0)],
     (192, 140, 92), (158, 104, 64)),
    ('decor/lantern_grove', "The Lantern Grove (Bayou Spa's rare decor set)",
     {'id': 'LanternGrove', 'location': 3, 'rows': GROVE_ROWS}, BS_PALETTE,
     [('StainedGlass', d_grove_glass), ('Lamp', d_grove_lamp), ('Gramophone', d_grove_gramophone),
      ('Pirogue', d_grove_pirogue), ('Rug', d_grove_rug)],
     [('Rug', (0, 0), 0), ('StainedGlass', (0, 10.5), 0), ('Lamp', (-10.5, 10.5), 0),
      ('Gramophone', (10.5, 10.5), 0), ('Pirogue', (7.5, -6.0), 0)],
     (152, 140, 120), (152, 176, 132)),
]
SETS_ARG = set(K.ARGS[K.ARGS.index('sets') + 1].split(',')) if 'sets' in K.ARGS else None


def wanted(set_dir):
    return SETS_ARG is None or set_dir.split('/')[-1] in SETS_ARG


def main():
    refused = []
    root = K.ROOT / 'blender' / 'decor'
    if wanted('decor/count_study') or wanted('decor/souvenir'):
        study = [(f'Decor_{SET_ID}_{p}', fn) for p, fn in (('Portrait', d_portrait), ('Globe', d_globe),
                                                           ('Clock', d_clock), ('Bust', d_bust), ('Rug', d_rug))]
        bad, man_study = build_set('decor/count_study', "The Count's Study (Haunted Manor's rare decor set)", study,
                                   {'id': SET_ID, 'location': 1, 'rows': SET_ROWS})
        refused += bad
        bad, man_souv = build_set('decor/souvenir', 'Souvenir_Base (every species\' souvenir)',
                                  [('Souvenir_Base', souvenir)])
        refused += bad
        if refused:
            raise SystemExit(f'REFUSED: {refused}')
        study_names = [n for n, _ in study if n in man_study['pieces']]
        if K.ONLY is None:
            stage('decor/count_study', study_names)
            stage('decor/souvenir', ['Souvenir_Base'])
        if not (K.NOPREVIEW or K.ONLY is not None):
            fbx, sfbx = root / 'count_study' / 'fbx', root / 'souvenir' / 'fbx'
            rev = root / 'count_study' / 'review'
            both = {**man_study['pieces'], **man_souv['pieces']}
            names = study_names + ['Souvenir_Base']
            # place() reads one fbx folder: copy the souvenir's FBX beside the study's for the shared sheets
            shutil.copy2(sfbx / 'Souvenir_Base.fbx', fbx / 'Souvenir_Base.fbx')
            try:
                print('SHEETS', review_set(rev, fbx, names, both), review_elevations(rev, fbx, names, both),
                      *review_topdown(rev, fbx, fbx), review_souvenir(root / 'souvenir' / 'review', sfbx),
                      flush=True)
            finally:
                (fbx / 'Souvenir_Base.fbx').unlink()
    for set_dir, title, cur, palette, pieces, room, floor_rgb, wall_rgb in LOCATION_SETS:
        if not wanted(set_dir):
            continue
        builds = [(f'Decor_{cur["id"]}_{p}', fn) for p, fn in pieces]
        bad, man = build_set(set_dir, title, builds, cur, palette)
        if bad:
            raise SystemExit(f'REFUSED: {bad}')
        names = [n for n, _ in builds if n in man['pieces']]
        if K.ONLY is None:
            stage(set_dir, names)
        if K.NOPREVIEW or K.ONLY is not None:
            continue
        out = K.ROOT / 'blender' / set_dir
        fbx, rev = out / 'fbx', out / 'review'
        study = [(f'Decor_{cur["id"]}_{p}', xz, ang) for p, xz, ang in room]
        print('SHEETS', review_set(rev, fbx, names, man['pieces'], wall_rgb),
              review_elevations(rev, fbx, names, man['pieces']),
              *review_topdown(rev, fbx, None, study, floor_rgb, wall_rgb), flush=True)


main()
