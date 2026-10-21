"""Rare decor sets and souvenirs (GDD A.11.3; MODELS.md, "Rare decor sets and souvenirs").

Two sets, built in one run:

    blender/decor/count_study/   Haunted Manor's rare set (location 1), five Decor_CountStudy_<Piece>:
                                 Portrait (Wall 2 x 1), Globe, Clock, Bust (Floor 1 x 1), Rug (Rug 3 x 2).
                                 One look: crimson, black and gold, the set's crest (a gold bat) on every
                                 piece, a glow on three of them; each piece read from above.
    blender/decor/souvenir/      Souvenir_Base: one 1 x 1 keepsake, a prize rosette under a bell jar on a
                                 plinth, for every species: Ribbon and Trim tinted by the code, the emblem on
                                 Medal's top, the name on Badge's front, Glass the jar.

Every piece keeps MODELS.md's "Decor" rules through the kit (tools/hotel_kit.py): footprint and 0.4 inset,
layer, nothing colliding, glows their own parts, no coplanar faces; plus nothing floating (a Wall piece may
hang: tools/build_built_rooms.py's grounded_check, build_built_rooms_more.py's hung_check, lifted here
unchanged). No Pieces.luau rows exist for these yet (this session may not touch src/): SET_ROWS below is
what the rows must say, and the kit's Pieces agreement is checked against it (the height is recorded in the
manifest, `model_top`, for the code session's rows).

    blender -b --python-exit-code 1 -t 4 -P tools/build_rare_decor.py [-- only <names>] [-- nopreview]

Review: Workbench on light grey only (Studio runs: no EEVEE or Cycles): review/set_sheet.png (each piece on
its squares beside the 5-stud person), review/elevations_sheet.png (front and side at floor level),
review/topdown.png (the set laid out in a 2 x 2 cell study, straight down) with topdown_phone.png (the same
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


NS = {'bpy': bpy, 'K': K, 'Vector': Vector, 'Matrix': Matrix, 'math': math, 'np': np}
_lift(TOOLS / 'build_built_rooms.py', ['GROUND_TOL', 'grounded_check', '_import', 'place', 'render', 'clear'], NS)
_lift(TOOLS / 'build_built_rooms_more.py', ['hung_check'], NS)
_lift(TOOLS / 'build_cosmetics_hotel.py', ['_flat', '_block', '_person'], NS)
_lift(TOOLS / 'build_facades.py', ['_compose'], NS)
hung_check, place, render, clear = NS['hung_check'], NS['place'], NS['render'], NS['clear']
_block, _person, _compose, _flat = NS['_block'], NS['_person'], NS['_compose'], NS['_flat']

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

K.pieces_decor()
for _id, (_w, _d, _layer) in list(SET_ROWS.items()) + [SOUVENIR_ROW]:
    assert _id not in K._PIECES, f'{_id} is in Pieces.luau already: read its row instead'
    # `always` turns the kit's height agreement off: no row has a height yet; the model's top is recorded.
    K._PIECES[_id] = {'w': _w, 'd': _d, 'layer': _layer, 'height': 0.0, 'always': True}

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
    w, d, layer = SET_ROWS[f'{SET_ID}_{piece_id}']
    p = K.decor(f'{SET_ID}_{piece_id}', w, d, layer)
    p.checks.append(hung_check)
    p.checks.append(no_use_check)
    return p


def sdone(note):
    """No LOD_Proxy (as the Manor's other decor); the model's top for the Pieces row."""
    piece = K.P
    pts = [v for n, (vs, _, _) in piece.parts.items() if n not in ('Root', 'LOD_Proxy') for v in vs]
    top = max(v.y for v in pts)
    rec = finish(proxy=False, note=note)
    rec['pieces_row'] = {'id': piece.name[len('Decor_'):] if piece.name.startswith('Decor_') else piece.name,
                         'w': piece.fw, 'd': piece.fd, 'layer': piece.layer, 'height': round(top, 2),
                         'model_top': round(top, 3)}
    if piece.name.startswith('Decor_'):
        rec['pieces_row'].update({'set': SET_ID, 'found': True, 'location': 1})
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


def review_set(rev, fbx, names, manifest):
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
            _block('wall', (cx - 1.5 * w, 0, 1.5 * d - 0.4), (cx + 1.5 * w, 7.6, 1.5 * d - 0.1), WALL_RGB)
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


def review_topdown(rev, fbx, souvenir_fbx):
    """The set laid out in a study, straight down and from the raised build camera; four souvenirs."""
    clear()
    for n, (x, z), ang in STUDY:
        place(fbx, n, (x, 0, z), ang)
    for k, (sp, rgb) in enumerate(SPECIES):
        objs = place(souvenir_fbx, 'Souvenir_Base', (10.5, 0, 4.5 - 3 * k))
        if rgb:
            tint(objs, rgb, darker(rgb))
        hide(objs, 'Glass')         # the code makes it glass; opaque in Workbench it would hide the emblem
    _block('floor', (-12, -0.3, -12), (12, -0.01, 12), (120, 82, 55))
    for lo, hi in (((-12, 0, 11.6), (12, 2.5, 12)), ((-12, 0, -12), (-11.6, 2.5, 12)),
                   ((11.6, 0, -12), (12, 2.5, 12)), ((-12, 0, -12), (-2, 2.5, -11.6)),
                   ((2, 0, -12), (12, 2.5, -11.6))):
        _block('wall', lo, hi, WALL_RGB)
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

def build_set(set_dir, title, builds):
    K.BUILT.clear()
    K.use_palette(PALETTE)
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


def main():
    refused = []
    study = [(f'Decor_{SET_ID}_{p}', fn) for p, fn in (('Portrait', d_portrait), ('Globe', d_globe),
                                                       ('Clock', d_clock), ('Bust', d_bust), ('Rug', d_rug))]
    bad, man_study = build_set('decor/count_study', "The Count's Study (Haunted Manor's rare decor set)", study)
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
    if K.NOPREVIEW or K.ONLY is not None:
        return
    root = K.ROOT / 'blender' / 'decor'
    fbx, sfbx = root / 'count_study' / 'fbx', root / 'souvenir' / 'fbx'
    rev = root / 'count_study' / 'review'
    both = {**man_study['pieces'], **man_souv['pieces']}
    names = study_names + ['Souvenir_Base']
    # place() reads one fbx folder: copy the souvenir's FBX beside the study's for the shared sheets
    shutil.copy2(sfbx / 'Souvenir_Base.fbx', fbx / 'Souvenir_Base.fbx')
    try:
        print('SHEETS', review_set(rev, fbx, names, both), review_elevations(rev, fbx, names, both),
              *review_topdown(rev, fbx, fbx), review_souvenir(root / 'souvenir' / 'review', sfbx), flush=True)
    finally:
        (fbx / 'Souvenir_Base.fbx').unlink()


main()
