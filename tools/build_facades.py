"""The hotel's facade pieces (MODELS.md, "Facade (`Facade_*`) and sign"), one set per style.

Walls stand only round the tiles a player owns (his ruling, 2026-10-20; GDD 5.4, A.1): the code
walks the outline and puts a piece on every outline edge and at every corner, and windows are
bought and placed, one per wall section, from four types (his rulings, GDD A.1). So every style is
seven pieces, each to the contract's frame (origin at the middle of the cell edge on the walking
surface, the owned cell toward +Z, the wall outside the edge from z -0.62 to -0.02, 17 tall):

    Facade_Wall             12 x 17, plain
    Facade_Window_<Type>    the same section with one window, its opening within x -4..4, y 3..13:
                            TwinSash (two tall narrow panes), Arched (one tall pointed arch), Round
                            (a round moon window), Wide (three panes over a flower box)
    Facade_Entrance         24 x 17, the arch (9 x 9 clear) between solid walls, its lantern, `Entrance`
    Facade_Corner           the 0.64 post at a corner, in the -X -Z quadrant of its origin

Seven styles, each its own set in blender/facade/<style>/ (the names are the same in every set):
the two hotel kits' own (haunted_manor, frostfang_lodge: the approved Lobby front wall's bands,
windows and arch carried over into the new frame) and the five facade cosmetics of
Cosmetics.luau (gothic, neon, candy, pirate, slime: drafts from the one-line looks he said yes
to, GDD decision log 2026-10-20).

The contract is enforced here, not only in MODELS.md: finish() refuses a piece whose colliding
boxes, envelope, ends, windows, opening or corner quadrant break it (facade_boxes, facade_tris),
on the built and the re-imported triangles, and every set is laid out round a convex and a
concave corner, re-imported from its FBXs, and checked for details running into each other and
for coplanar faces between pieces (assembly(), written into validation.json).

    blender -b --python-exit-code 1 -P tools/build_facades.py [-- styles gothic,neon] [-- nopreview]

Writes blender/facade/<style>/: fbx/Facade_*.fbx, manifest.json, validation.json,
import_fixup.luau, review/ (the sheet: the layout, the entrance with a 5-stud person, both
corners), and blender/facade/review/overview.png (every style's layout).
"""
import ast
import json
import math
import re
import sys
from pathlib import Path

import bpy
import numpy as np
from mathutils import Matrix, Vector
from mathutils.bvhtree import BVHTree

sys.path.insert(0, str(Path(__file__).resolve().parent))
import hotel_kit as K  # noqa: E402
from hotel_kit import (begin, finish, box, span, cyl, lathe, sphere, prism, attach, declare, at,  # noqa: E402
                       arch_points, round_arch_points, WALL)

TOOLS = Path(__file__).resolve().parent
ARGS = K.ARGS
STYLES_ARG = set(ARGS[ARGS.index('styles') + 1].split(',')) if 'styles' in ARGS else None

# --- The contract (MODELS.md, "Facade") ----------------------------------------------------------

OUT_Z, IN_Z = -0.62, -0.02      # the wall's outer and inner faces
POST = 0.64                     # the corner post's side
WINDOW_TYPES = ('TwinSash', 'Arched', 'Round', 'Wide')     # his four, GDD A.1 (2026-10-20)
WINDOWS = tuple(f'Facade_Window_{t}' for t in WINDOW_TYPES)
HALF = {'Facade_Wall': 6.0, 'Facade_Entrance': 12.0, **{w: 6.0 for w in WINDOWS}}
WIN_BOUNDS = (-4.0, 4.0, 3.0, 13.0)    # a window's opening stays within x -4..4, y 3..13 (MODELS.md)
ARCH_X, ARCH_Y = 4.5, 9.0       # the entrance's clear opening: x -4.5..4.5, y 0..9
PIER = 5.5                      # the arch's pillars x 4.5..5.5; Wall_Left/Right from here to the end
INNER_MAX = 0.2                 # a non-colliding detail reaches this far inside the edge (a sill)
WEDGE = 0.02                    # a detail proud by p stays 0.62 + p + WEDGE from the piece's ends
INNER_END = 0.65                # an inside detail stays this far from the ends
END_ZONE, END_DIP = 0.64, 0.02  # the wall's top and bottom slope this much over its last END_ZONE
WIN_ZONE = (2.5, 12.5)          # the corner's details beyond its post stay out of this height,
BEAD_REACH = 0.9                # but for a bead on its outer edge (within x, z >= -0.9), at any height
BODY = {'Facade_Wall': ('Wall',), 'Facade_Entrance': ('Wall_Left', 'Wall_Right', 'ArchLeft', 'ArchRight', 'ArchTop'),
        'Facade_Corner': ('Post',), **{w: ('Wall',) for w in WINDOWS}}
BUDGETS = {'Facade_Wall': 1500, 'Facade_Entrance': 3000, 'Facade_Corner': 800,     # MODELS.md, a draft
           **{w: 2500 for w in WINDOWS}}
PIECES = ('Facade_Wall',) + WINDOWS + ('Facade_Entrance', 'Facade_Corner')

# Rule 1's palette keys for the Neon facade's tubes (MODELS.md): what import_fixup.luau makes them.
K.GLOW_KEYS = K.GLOW_KEYS + ('Cyan', 'Magenta')
K.GLOW_COLOURS = {**K.GLOW_COLOURS, 'Cyan': (70, 245, 255), 'Magenta': (255, 60, 200)}


def _lift(path, names, ns):
    """Top-level functions and literal assignments called `names` from another build script,
    without running it (the Frostfang script builds its whole set on import): carried, not copied."""
    src = path.read_text(encoding='utf8')
    for node in ast.parse(src).body:
        if isinstance(node, ast.FunctionDef) and node.name in names:
            exec(compile(ast.Module([node], []), str(path), 'exec'), ns)
        elif isinstance(node, ast.Assign) and getattr(node.targets[0], 'id', None) in names:
            ns[node.targets[0].id] = ast.literal_eval(node.value)
    missing = [n for n in names if n not in ns]
    assert not missing, f'{path.name}: {missing} not found'
    return ns


HM_PALETTE = list(K.PALETTE)    # the kit's default is the Haunted Manor's
_KIT = {'box': box, 'span': span, 'cyl': cyl, 'lathe': lathe, 'sphere': sphere, 'prism': prism, 'at': at, 'math': math}
_lift(TOOLS / 'build_hotel_haunted_manor.py', ['pumpkin'], _KIT)
_lift(TOOLS / 'build_hotel_frostfang_lodge.py', ['PALETTE', 'icicle'], _KIT)
FF_PALETTE = _KIT['PALETTE']
_REV = {'bpy': bpy, 'K': K, 'Vector': Vector}
_lift(TOOLS / 'build_cosmetics_hotel.py', ['_flat', '_block', '_person', '_render'], _REV)


# --- The kit, extended from here (another session is editing hotel_kit.py) ---------------------

_check_piece = K.check_piece


def check_piece(piece, boxes, tris, faults):
    """The kit's generic rules for a facade piece (names, glow parts, Root, the envelope, budgets),
    through kind Cosmetic, which requires no part, then the facade's own (facade_boxes)."""
    if piece.kind != 'Facade':
        return _check_piece(piece, boxes, tris, faults)
    saved = K.BUDGET['Cosmetic']
    piece.kind, K.BUDGET['Cosmetic'] = 'Cosmetic', BUDGETS[piece.name]
    sub = []
    try:
        total = _check_piece(piece, boxes, tris, sub)
    finally:
        piece.kind, K.BUDGET['Cosmetic'] = 'Facade', saved
    faults += [f.replace('the Cosmetic budget', 'the facade piece budget') for f in sub
               if not f.startswith('a cosmetic collides')]
    faults += facade_boxes(piece, boxes)
    return total


K.check_piece = check_piece


def piece(name):
    """Begin a facade piece in its frame: Root, the envelope, its checks."""
    if name == 'Facade_Corner':
        p = begin(name, 'Facade', (POST, 0.2, POST), root_centre=(-POST / 2, 0.1, -POST / 2))
        p.allowed = ((-2.5, 0.0, -2.5), (0.0, WALL, 0.0))
    else:
        h = HALF[name]
        p = begin(name, 'Facade', (2 * h, 0.2, 0.6), root_centre=(0, 0.1, (OUT_Z + IN_Z) / 2))
        p.allowed = ((-h, 0.0, -2.5), (h, WALL, INNER_MAX))
    K.BUDGET['Facade'] = BUDGETS[name]
    p.checks.append(facade_tris)
    p.openings = []             # a window's openings, their boxes (x0, x1, y0, y1), for facade_tris
    declare('Glass', False)
    for b in BODY[name]:
        declare(b, True)
    if name == 'Facade_Entrance':
        attach('Entrance', (0, 0, 0), (0, 0, -1))
    return p


def _same_box(lo, hi, want_lo, want_hi, tol=0.01):
    return all(abs(lo[i] - want_lo[i]) <= tol and abs(hi[i] - want_hi[i]) <= tol for i in range(3))


def facade_boxes(piece, boxes):
    """The contract on the parts' boxes (MODELS.md, "Facade"): the colliding parts exactly, nothing
    else colliding, nothing colliding inside the edge, the entrance's opening clear, `Entrance`."""
    f, name = [], piece.name
    body = BODY[name]
    for p, (lo, hi, col) in boxes.items():
        if p in ('Root', 'LOD_Proxy'):
            continue
        if p in body:
            if not col:
                f.append(f'{p} does not collide')
            if name != 'Facade_Corner' and hi.z > IN_Z + 0.005:    # the post is 0.02 proud both ways
                f.append(f'{p} reaches z {hi.z:.3f}, inside the edge (a person collides with it there)')
        elif col:
            f.append(f'{p} collides: only {list(body)} do')
    missing = [b for b in body if b not in boxes]
    if missing:
        f.append(f'missing parts {missing}')
    exact = {**{w: {'Wall': ((-6, 0, OUT_Z), (6, WALL, IN_Z))} for w in ('Facade_Wall',) + WINDOWS},
             'Facade_Entrance': {'Wall_Left': ((-12, 0, OUT_Z), (-PIER, WALL, IN_Z)),
                                 'Wall_Right': ((PIER, 0, OUT_Z), (12, WALL, IN_Z))},
             'Facade_Corner': {'Post': ((-POST, 0, -POST), (0, WALL, 0))}}[name]
    for p, (wlo, whi) in exact.items():
        if p in boxes and not _same_box(boxes[p][0], boxes[p][1], wlo, whi):
            f.append(f'{p} is {K.v3(boxes[p][0], 3)}..{K.v3(boxes[p][1], 3)}, the contract {wlo}..{whi}')
    if name == 'Facade_Entrance':
        olo, ohi = Vector((-ARCH_X + 0.01, 0.01, -3)), Vector((ARCH_X - 0.01, ARCH_Y - 0.01, 3))
        hits = [p for p, (lo, hi, col) in boxes.items() if col and K._overlap(lo, hi, olo, ohi)]
        if hits:
            f.append(f'the opening (9 x 9) is blocked by the boxes of {hits}')
        for p in ('ArchLeft', 'ArchRight'):
            if p in boxes:
                lo, hi, _ = boxes[p]
                if not (abs(lo.x) >= ARCH_X - 0.01 and abs(hi.x) >= ARCH_X - 0.01 and max(abs(lo.x), abs(hi.x)) <= PIER + 0.4):
                    f.append(f'{p} x {lo.x:.2f}..{hi.x:.2f}: a pillar stands at |x| 4.5..5.5')
        if 'ArchTop' in boxes and boxes['ArchTop'][0].y < ARCH_Y - 0.01:
            f.append(f"ArchTop's box reaches down to {boxes['ArchTop'][0].y:.2f}, into the 9-tall opening")
        a = piece.att.get('Entrance')
        if not a or a[0].length > 1e-6 or a[1] is None or a[1].dot(Vector((0, 0, -1))) < 0.999:
            f.append(f'Entrance attachment {a}: (0, 0, 0), LookVector -Z')
    elif 'Entrance' in piece.att:
        f.append('only Facade_Entrance carries Entrance')
    return f


def coverage(tris, xs, ys):
    """Which (x, y) grid points the triangles cover, seen along Z: bool [len(ys), len(xs)]."""
    X, Y = np.meshgrid(xs, ys)
    cov = np.zeros(X.shape, bool)
    for a, b, c in tris:
        ax, ay, bx, by, cx, cy = a.x, a.y, b.x, b.y, c.x, c.y
        d = (by - cy) * (ax - cx) + (cx - bx) * (ay - cy)
        if abs(d) < 1e-9:
            continue
        i0, i1 = np.searchsorted(xs, min(ax, bx, cx)), np.searchsorted(xs, max(ax, bx, cx), 'right')
        j0, j1 = np.searchsorted(ys, min(ay, by, cy)), np.searchsorted(ys, max(ay, by, cy), 'right')
        if i0 >= i1 or j0 >= j1:
            continue
        sx, sy = X[j0:j1, i0:i1], Y[j0:j1, i0:i1]
        l1 = ((by - cy) * (sx - cx) + (cx - bx) * (sy - cy)) / d
        l2 = ((cy - ay) * (sx - cx) + (ax - cx) * (sy - cy)) / d
        cov[j0:j1, i0:i1] |= (l1 >= -1e-6) & (l2 >= -1e-6) & (1 - l1 - l2 >= -1e-6)
    return X, Y, cov


def _poly_area(pts):
    return 0.5 * sum(pts[i - 1][0] * pts[i][1] - pts[i][0] * pts[i - 1][1] for i in range(len(pts)))


def _clip(subject, clipper):
    """Sutherland-Hodgman: a convex polygon clipped by a counter-clockwise convex one."""
    out = list(subject)
    for i in range(len(clipper)):
        a, b = clipper[i - 1], clipper[i]
        inp, out = out, []
        if not inp:
            break

        def inside(p):
            return (b[0] - a[0]) * (p[1] - a[1]) - (b[1] - a[1]) * (p[0] - a[0]) >= -1e-9

        def cross(p, q):
            dx, dy = q[0] - p[0], q[1] - p[1]
            ex, ey = b[0] - a[0], b[1] - a[1]
            den = dx * ey - dy * ex
            t = ((a[0] - p[0]) * ey - (a[1] - p[1]) * ex) / den if abs(den) > 1e-12 else 0
            return (p[0] + t * dx, p[1] + t * dy)
        for j in range(len(inp)):
            p, q = inp[j - 1], inp[j]
            if inside(q):
                if not inside(p):
                    out.append(cross(p, q))
                out.append(q)
            elif inside(p):
                out.append(cross(p, q))
    return out


def zfights(tris, tags=None, min_area=2e-4, tol=0.003):
    """Pairs of same-facing coplanar triangles that overlap: they flicker in Studio (MODELS.md, rule:
    coplanar faces). `tags`: only pairs whose tags differ (pieces in an assembly)."""
    groups = {}
    for i, (a, b, c) in enumerate(tris):
        n = (b - a).cross(c - a)
        if n.length < 1e-9:
            continue
        n.normalize()
        groups.setdefault((round(n.x, 2), round(n.y, 2), round(n.z, 2)), []).append((n.dot(a), i, n))
    found = []
    for items in groups.values():
        items.sort()
        for k, (d1, i, n) in enumerate(items):
            for d2, j, _ in items[k + 1:]:
                if d2 - d1 > tol:
                    break
                if tags is not None and tags[i] == tags[j]:
                    continue
                u = (Vector((1, 0, 0)) if abs(n.x) < 0.9 else Vector((0, 1, 0))).cross(n).normalized()
                v = n.cross(u)
                pa = [(p.dot(u), p.dot(v)) for p in tris[i]]
                pb = [(p.dot(u), p.dot(v)) for p in tris[j]]
                if _poly_area(pa) < 0:
                    pa.reverse()
                if _poly_area(pb) < 0:
                    pb.reverse()
                inter = _clip(pa, pb)
                if len(inter) >= 3 and abs(_poly_area(inter)) > min_area:
                    found.append((i, j, abs(_poly_area(inter))))
    return found


def facade_tris(piece, tris, stage):
    """The contract on the triangles (Roblox coords, the piece's frame), built and re-imported: the
    height, the ends and the wedge, the inside, the windows seen through the wall, the opening,
    the corner's quadrant, and no coplanar faces flickering."""
    f, name = [], piece.name
    tag = f'({stage})'
    vis = {p: ts for p, ts in tris.items() if p not in ('Root', 'LOD_Proxy')}
    pts = [(p, v) for p, ts in vis.items() for t in ts for v in t]
    bad_y = [(p, round(v.y, 3)) for p, v in pts if v.y < -0.005 or v.y > WALL + 0.005]
    if bad_y:
        f.append(f'{tag} {len(bad_y)} points outside y 0..17, e.g. {bad_y[:3]}')
    if name in HALF:
        h = HALF[name]
        out_x = [(p, round(v.x, 3)) for p, v in pts if abs(v.x) > h + 0.005]
        if out_x:
            f.append(f'{tag} {len(out_x)} points past x +-{h:g}, e.g. {out_x[:3]}')
        wedge, inner = [], []
        for p, v in pts:
            e = h - abs(v.x)
            prd = OUT_Z - v.z
            if prd > 0.005 and e < -OUT_Z + prd + WEDGE - 0.002:
                wedge.append((p, K.v3(v, 2)))
            if v.z > IN_Z + 0.005 and (e < INNER_END - 0.002 or v.z > INNER_MAX + 0.005):
                inner.append((p, K.v3(v, 2)))
        if wedge:
            f.append(f'{tag} {len(wedge)} proud points too near an end (0.62 + proud + {WEDGE}), e.g. {wedge[:3]}')
        if inner:
            f.append(f'{tag} {len(inner)} inside points too near an end or past {INNER_MAX} inside, e.g. {inner[:3]}')
        xs = np.arange(-h + 0.0503, h, 0.1)      # off every round edge (a sample on one is a coin toss)
        ys = np.arange(0.0497, WALL, 0.1)
        X, Y, cov = coverage([t for p, ts in vis.items() if p != 'Glass' for t in ts], xs, ys)
        if name != 'Facade_Entrance':
            # A window's openings (piece.openings, their boxes) are holes seen through the wall, open
            # across their whole width and height, within x -4..4 and y 3..13; the rest of the face is
            # covered. A plain wall has none.
            hole = np.zeros(cov.shape, bool)
            bx0, bx1, by0, by1 = WIN_BOUNDS
            if name in WINDOWS and not piece.openings:
                f.append(f'{tag} a window piece with no opening')
            for x0, x1, y0, y1 in piece.openings:
                if x0 < bx0 - 1e-6 or x1 > bx1 + 1e-6 or y0 < by0 - 1e-6 or y1 > by1 + 1e-6:
                    f.append(f'{tag} the opening x {x0:g}..{x1:g}, y {y0:g}..{y1:g} leaves x -4..4, y 3..13')
                inslot = (X > x0) & (X < x1) & (Y > y0) & (Y < y1)
                hole |= (X > x0 - 0.06) & (X < x1 + 0.06) & (Y > y0 - 0.06) & (Y < y1 + 0.06)
                op = inslot & ~cov
                if not op.any():
                    f.append(f'{tag} the opening at x {x0:g}..{x1:g} is not open at all')
                    continue
                w = X[op].max() - X[op].min() + 0.1
                hh = Y[op].max() - Y[op].min() + 0.1
                if w < (x1 - x0) - 0.4 or hh < (y1 - y0) - 0.4:
                    f.append(f'{tag} the opening at x {x0:g}..{x1:g} is open {w:.2f} x {hh:.2f}, '
                             f'not {x1 - x0:g} x {y1 - y0:g}')
            gaps = (~hole) & ~cov
            if gaps.any():
                f.append(f'{tag} {int(gaps.sum())} points of the face outside the windows are open, in '
                         f'x {X[gaps].min():.2f}..{X[gaps].max():.2f}, y {Y[gaps].min():.2f}..{Y[gaps].max():.2f}')
        else:
            opening = (np.abs(X) < ARCH_X - 0.1) & (Y < 7.5)
            if (opening & cov).any():
                f.append(f'{tag} something hangs in the entrance below 7.5, e.g. '
                         f'({X[opening & cov][0]:.2f}, {Y[opening & cov][0]:.2f})')
            solid = (np.abs(X) > PIER + 0.1) | (Y > 14.0)
            if (solid & ~cov).any():
                f.append(f'{tag} the wall beside or over the arch is open at '
                         f'({X[solid & ~cov][0]:.2f}, {Y[solid & ~cov][0]:.2f})')
    else:
        out = [(p, K.v3(v, 2)) for p, v in pts if v.x > 0.005 or v.z > 0.005 or v.x < -2.5 or v.z < -2.5]
        if out:
            f.append(f'{tag} {len(out)} points leave the corner\'s quadrant, e.g. {out[:3]}')
        beyond = [(p, K.v3(v, 2)) for p, v in pts if (v.x < -POST - 0.03 or v.z < -POST - 0.03)
                  and (v.x > -0.1 or v.z > -0.1 or (WIN_ZONE[0] < v.y < WIN_ZONE[1]
                                                     and (v.x < -BEAD_REACH or v.z < -BEAD_REACH)))]
        if beyond:
            f.append(f'{tag} {len(beyond)} points beyond the post outside its rules (x, z <= -0.1, '
                     f'y outside {WIN_ZONE} unless within {BEAD_REACH} of the post), e.g. {beyond[:3]}')
    flat = [t for ts in vis.values() for t in ts]
    owner = [p for p, ts in vis.items() for _ in ts]
    zf = zfights(flat)
    if zf:
        def _n(t):
            return K.v3(((t[1] - t[0]).cross(t[2] - t[0])).normalized(), 2)
        eg = [f'{owner[i]} {K.v3(sum(flat[i], Vector()) / 3, 2)} and {owner[j]} {K.v3(sum(flat[j], Vector()) / 3, 2)} '
              f'facing {_n(flat[i])}' for i, j, _ in zf[:3]]
        f.append(f'{tag} {len(zf)} coplanar overlapping face pairs (they flicker), e.g. {eg}')
    return f


# --- Shapes ---------------------------------------------------------------------------------------

_END = None     # the current style's post bands: a wall's end face takes the post's colour (wall_body)


def _post_colour(y):
    for y0, y1, colour in _END:
        if y0 - 1e-9 <= y <= y1 + 1e-9:
            return colour
    return _END[-1][2]


def _hexa(part, xl, xr, yb, yt, col):
    """A six-sided block from x (left, right) and y (bottom, top) given per corner: xl = (outer,
    inner) x of its left end, yb = (left, right) y of its bottom; z OUT_Z..IN_Z."""
    verts = []
    for i in range(8):
        xi, yi, zi = i >> 2 & 1, i >> 1 & 1, i & 1
        x = (xr if xi else xl)[zi]
        y = (yt if yi else yb)[xi]
        verts.append(Vector((x, y, IN_Z if zi else OUT_Z)))
    K._add(part, verts, K.BOX_FACES, col)


def wall_body(part, x0, x1, bands, holes=(), ends=(True, True)):
    """The wall slab from x0 to x1, y 0..17, z -0.62..-0.02, in colour bands [(y0, y1, outer,
    inner)] covering 0..17, with rectangular holes [(hx0, hx1, hy0, hy1)]. At a piece end (`ends`)
    its end face takes the corner post's colour at that height (at a concave corner the post's
    inner face lies on it, and one colour cannot flicker), and its top and bottom slope END_DIP
    over the last END_ZONE, under the post's top (MODELS.md, "Where pieces meet"). Two pieces in a
    row meet face to face."""
    for y0, y1, outer, inner in bands:
        y0, y1 = round(y0, 4), round(y1, 4)     # a band edge a float's hair off a hole's leaves a sliver
        cuts = sorted({y0, y1} | {round(y, 4) for h in holes for y in h[2:] if y0 + 1e-4 < y < y1 - 1e-4})
        for ya, yb in zip(cuts, cuts[1:]):
            segs = [(x0, x1)]
            for hx0, hx1, hy0, hy1 in holes:
                if hy0 <= ya + 1e-4 and yb <= hy1 + 1e-4:
                    segs = [s for a, b in segs for s in ((a, min(b, hx0)), (max(a, hx1), b)) if s[1] - s[0] > 1e-6]
            for a, b in segs:
                left, right = ends[0] and abs(a - x0) < 1e-9, ends[1] and abs(b - x1) < 1e-9
                col = {'front': outer, 'back': inner, 'rest': outer}
                if _END and left:
                    col['left'] = _post_colour((ya + yb) / 2)
                if _END and right:
                    col['right'] = _post_colour((ya + yb) / 2)
                dip = (END_DIP if ya < 1e-9 else 0, END_DIP if yb > WALL - 1e-9 else 0)
                if not (left or right) or not any(dip):
                    span(part, (a, ya, OUT_Z), (b, yb, IN_Z), col)
                    continue
                ma, mb = a + (END_ZONE if left else 0), b - (END_ZONE if right else 0)
                if mb > ma:
                    span(part, (ma, ya, OUT_Z), (mb, yb, IN_Z), col)
                if left:
                    _hexa(part, (a, a), (ma, ma), (ya + dip[0], ya), (yb - dip[1], yb), col)
                if right:
                    _hexa(part, (mb, mb), (b, b), (ya, ya + dip[0]), (yb, yb - dip[1]), col)


def bands_between(bands, y0, y1):
    """The bands cut to y0..y1."""
    return [(max(a, y0), min(b, y1), o, i) for a, b, o, i in bands if b > y0 + 1e-9 and a < y1 - 1e-9]


def _cut_bands(bands, cuts):
    """Bands split at the given heights."""
    out = []
    for y0, y1, o, i in bands:
        ys = [y0] + [c for c in cuts if y0 < c < y1] + [y1]
        out += [(a, b, o, i) for a, b in zip(ys, ys[1:])]
    return out


def post(bands):
    """The corner's Post, exactly its square, in colour bands [(y0, y1, colour)]."""
    for y0, y1, colour in bands:
        span('Post', (-POST, y0, -POST), (0, y1, 0), colour)


def bead(col, r=0.1, y0=0.62, y1=16.38, segs=None):
    """A bead up the post's outer edge: at an outside corner it trims the edge, at an inside one it
    is what shows of the corner (the post is buried in the two walls there). `segs` (a length)
    alternates the colours `col` along it (a candy cane)."""
    c = (-POST - 0.02, -POST - 0.02)
    if not segs:
        cyl('Dressing', (c[0], y0, c[1]), r, y1 - y0, col, n=8)
        return
    k, y = 0, y0
    while y < y1 - 1e-6:
        h = min(segs, y1 - y)
        cyl('Dressing', (c[0], y, c[1]), r, h, col[k % len(col)], n=8)
        y, k = y + h, k + 1


def over_arch_bands(part, bands, outer, y_to):
    """The wall round and over an arch from its springing (ARCH_Y) up to y_to, in the style's bands,
    each band a strip on either side of the arch's outer outline (`outer`, left to right) and a
    full strip above its crown; each strip runs 0.05 in under the arch's ring, which stands in front."""
    right = [pt for pt in outer if pt[0] >= -1e-9]          # from the crown down to (5.5, spring)
    apex = max(y for _, y in outer)

    def half(y):
        for (xa, ya), (xb, yb) in zip(right, right[1:]):
            if yb - 1e-9 <= y <= ya + 1e-9:
                return xa + (xb - xa) * ((y - ya) / (yb - ya) if abs(yb - ya) > 1e-9 else 0)
        return 0.0
    for y0, y1, o, i in bands_between(bands, ARCH_Y, y_to):
        col = {'front': o, 'back': i, 'rest': o}
        cuts = [y0] + ([apex] if y0 < apex < y1 else []) + [y1]
        for ya, yb in zip(cuts, cuts[1:]):
            if ya >= apex - 1e-9:
                span(part, (-PIER, ya, OUT_Z), (PIER, yb, IN_Z), col)
                continue
            ha = max(half(ya) - (0.05 if ya > ARCH_Y + 1e-6 else 0.0), 0.0)     # flush at the springing,
            hb = max(half(yb) - 0.05, 0.0)                                        # where the ring stands on it
            for sx in (-1, 1):
                pts = [(sx * PIER, ya), (sx * ha, ya), (sx * hb, yb), (sx * PIER, yb)]
                prism(part, pts if sx < 0 else pts[::-1], OUT_Z, IN_Z, col)


def entrance_proxy():
    for x0, x1 in ((-12, -PIER), (PIER, 12)):
        span('LOD_Proxy', (x0, 0, OUT_Z), (x1, WALL, IN_Z), 'grey')
    for s in (-1, 1):
        span('LOD_Proxy', (min(s * ARCH_X, s * PIER), 0, OUT_Z - 0.2), (max(s * ARCH_X, s * PIER), ARCH_Y, IN_Z), 'grey')
    span('LOD_Proxy', (-PIER, ARCH_Y, OUT_Z - 0.2), (PIER, WALL, IN_Z), 'grey')


def tube(part, pts, r, col, n=6, closed=False, normal=(0, 0, -1)):
    """A tube of radius r along a polyline (a neon tube, a rope); `closed` joins it into a ring."""
    pts = [Vector(p) for p in pts]
    N = Vector(normal).normalized()
    verts, faces, rings = [], [], []
    k = len(pts)
    for i, p in enumerate(pts):
        t = (pts[(i + 1) % k] - pts[i - 1]) if closed else (pts[min(i + 1, k - 1)] - pts[max(i - 1, 0)])
        t.normalize()
        side = t.cross(N)
        if side.length < 1e-6:
            side = t.orthogonal()
        side.normalize()
        up = side.cross(t).normalized()
        ring = []
        for j in range(n):
            a = 2 * math.pi * j / n
            ring.append(len(verts))
            verts.append(p + r * (math.cos(a) * up + math.sin(a) * side))
        rings.append(ring)
    pairs = list(zip(rings, rings[1:])) + ([(rings[-1], rings[0])] if closed else [])
    for r0, r1 in pairs:
        faces += [(r0[j], r0[(j + 1) % n], r1[(j + 1) % n], r1[j]) for j in range(n)]
    if not closed:
        faces += [tuple(reversed(rings[0])), tuple(rings[-1])]
    K._add(part, verts, faces, col)


def drip(part, x, y_top, length, w, col, z_face=OUT_Z, depth=0.12):
    """A drip hanging from y_top on a face toward -Z: a round strand standing `depth` proud, thinning
    down to the fat bulb it hangs as (icing, slime)."""
    r = w / 2
    cyl(part, (x, y_top - length, z_face), r * 0.75, length, col, n=6, r_top=r, scale=(1, depth / r))
    sphere(part, (x, y_top - length, z_face - depth * 0.2), (w * 0.62, w * 0.62, depth * 1.1), col, n=6, rings=3)


def drip_row(h, y_top, col, z_face=OUT_Z, depth=0.12, clear=None):
    """Drips of uneven width, length and spacing along a top edge of a piece 2h wide, kept off its
    ends (the wedge)."""
    steps, widths = (0.8, 1.1, 0.7, 1.25, 0.9, 1.0), (0.46, 0.38, 0.52, 0.42, 0.36, 0.5)
    lengths = (0.9, 1.7, 0.6, 1.3, 0.8, 2.0, 0.7, 1.4)
    x, k = -h + 1.3, 0
    while x <= h - 1.3 + 1e-6:
        if clear is None or not clear[0] <= x <= clear[1]:
            drip('Dressing', x, y_top, lengths[k % 8], widths[k % 6], col, z_face, depth)
        x, k = x + steps[k % 6], k + 1


def hanging_lantern(x, hook, z, metal, n=1, k=1.4, cap=None, flame='lamp', chain=0.45):
    """A lantern hung in the arch's opening (the old Lobby's, k times its size: at 1.4 it is 2 studs
    tall): chain, cap, four posts, a base, the flame Glow_Warm_<n>. Returns its foot's height."""
    s, h = 0.6 * k, 1.4 * k
    top = hook - chain
    cyl('Dressing', (x, top, z), 0.04 * k, chain, metal, n=4)
    box('Dressing', (x, top - 0.05 * k, z), (s, 0.1 * k, s), cap or metal)
    box('Dressing', (x, top - h + 0.05 * k, z), (s, 0.1 * k, s), metal)
    for dx in (-s / 2 + 0.04 * k, s / 2 - 0.04 * k):
        for dz in (-s / 2 + 0.04 * k, s / 2 - 0.04 * k):
            box('Dressing', (x + dx, top - h / 2, z + dz), (0.07 * k, h - 0.2 * k, 0.07 * k), metal)
    sphere(f'Glow_Warm_{n}', (x, top - h / 2, z), (0.18 * k, 0.3 * k, 0.18 * k), flame, n=8, rings=4)
    return top - h


def zm(z):
    """The old Lobby's arch frame (the arch 0..1 deep, its wall 0..0.8, the street at z < 0) in the
    facade's: the arch 0.2 proud of the wall's outer face and never inside the edge."""
    return OUT_Z - 0.2 + 0.8 * z


DIAG = at((-POST, 0, -POST), ry=45)     # the corner's outward diagonal: local -Z points out


def arch_band(part, outer, inner, a0, a1, cols, split=1.2):
    """A band between two outlines of the same count (an arch's voussoirs, a frame, a stained-glass
    trim), each segment its own prism in alternating colours, long segments cut to about `split`."""
    k = 0
    for i in range(len(outer) - 1):
        o0, o1, i0, i1 = Vector(outer[i]), Vector(outer[i + 1]), Vector(inner[i]), Vector(inner[i + 1])
        m = max(1, round(max((o1 - o0).length, (i1 - i0).length) / split))
        for s in range(m):
            t0, t1 = s / m, (s + 1) / m
            quad = [o0.lerp(o1, t0), o0.lerp(o1, t1), i0.lerp(i1, t1), i0.lerp(i1, t0)]
            prism(part, [(q.x, q.y) for q in quad], a0, a1, cols[k % len(cols)])
            k += 1


# --- Windows: an opening's shape, and what each style dresses it in -----------------------------------

def rect(x0, x1, y0, y1):
    return {'kind': 'rect', 'bbox': (x0, x1, y0, y1)}


def lancet(x0, x1, y0, spring, apex, round_top=False):
    """An arched opening: straight sides up to `spring`, a pointed (or round) head up to `apex`."""
    return {'kind': 'arch', 'bbox': (x0, x1, y0, apex), 'spring': spring, 'round': round_top}


def disc(cx, cy, r, n=24):
    return {'kind': 'circle', 'bbox': (cx - r, cx + r, cy - r, cy + r), 'c': (cx, cy), 'r': r, 'n': n}


def outline(s, o=0.0):
    """The opening's outline, counter-clockwise, offset outward by o (inward when negative), with
    the same points for any o, so two outlines make a band (arch_band)."""
    x0, x1, y0, y1 = s['bbox']
    if s['kind'] == 'rect':
        return [(x0 - o, y0 - o), (x1 + o, y0 - o), (x1 + o, y1 + o), (x0 - o, y1 + o)]
    if s['kind'] == 'arch':
        head = (round_arch_points(x0 - o, x1 + o, s['spring'], y1 + o, n=8) if s['round']
                else arch_points(x0 - o, x1 + o, s['spring'], y1 + o, n=4))
        return [(x0 - o, y0 - o), (x1 + o, y0 - o)] + list(reversed(head))
    (cx, cy), r, n = s['c'], s['r'] + o, s['n']
    return [(cx + r * math.cos(2 * math.pi * i / n), cy + r * math.sin(2 * math.pi * i / n)) for i in range(n)]


def _closed(pts):
    return list(pts) + [pts[0]]


def infill(s, col):
    """The wall round a shaped opening inside its box (part of Wall): an arch's spandrels, a disc's
    four corners."""
    x0, x1, y0, y1 = s['bbox']
    if s['kind'] == 'arch':
        head = list(reversed(outline(s)[2:]))       # left to right, (x0, spring) .. (x1, spring)
        m = len(head) // 2
        prism('Wall', [(x0, y1)] + list(reversed(head[:m + 1])), OUT_Z, IN_Z, col)
        prism('Wall', [(x1, y1)] + head[m:], OUT_Z, IN_Z, col)
    elif s['kind'] == 'circle':
        (cx, cy), r, q = s['c'], s['r'], s['n'] // 4
        for qx, qy in ((1, 1), (-1, 1), (-1, -1), (1, -1)):
            arc = [(cx + qx * r * math.cos(math.pi / 2 * i / q), cy + qy * r * math.sin(math.pi / 2 * i / q))
                   for i in range(q + 1)]
            prism('Wall', [(cx + qx * r, cy + qy * r)] + arc, OUT_Z, IN_Z, col)


def _ring(part, s, col, w, z0, z1):
    (cx, cy), r = s['c'], s['r']
    lathe(part, [(r - 0.01, 0), (r + w, 0), (r + w, z1 - z0), (r - 0.01, z1 - z0)], col, n=s['n'], closed=True,
          m=at((cx, cy, z0), rx=90), phase=0)


def frame(s, col, w=0.25, proud=0.03, part='Dressing'):
    """A flat frame round the opening on the outer face; its back sunk into the wall, its inner edge
    0.01 over the opening (on the reveal's edge it would share the reveal's face)."""
    if s['kind'] == 'circle':
        return _ring(part, s, col, w, OUT_Z - proud, OUT_Z + 0.01)
    arch_band(part, _closed(outline(s, w)), _closed(outline(s, -0.01)), OUT_Z - proud, OUT_Z + 0.01, [col], split=99)


def inner_frame(s, col, w=0.32):
    if s['kind'] == 'circle':      # its back on the wall's inner face (the inner sill's is sunk into the wall)
        return _ring('Dressing', s, col, w, IN_Z, IN_Z + 0.02)
    arch_band('Dressing', _closed(outline(s, w)), _closed(outline(s, -0.01)), IN_Z, IN_Z + 0.02, [col], split=99)


def glass(s, col):
    prism('Glass', outline(s, 0.05), -0.35, -0.29, col)


def stained(s, cols, t=0.35):
    """Stained glass round the opening's edge, in front of the pane, in alternating colours."""
    arch_band('Glass', _closed(outline(s, 0.0)), _closed(outline(s, -t)), -0.37, -0.33, cols, split=1.1)


def sill_under(x0, x1, y_out, y_in, outer, inner, proud=0.17):
    """A sill proud of both faces: outside, its top slopes from y_out (the opening's foot, or under
    a tube) down and out; inside, a ledge 0.2 deep, its top a hair over the foot at y_in."""
    if outer:       # both backs sunk 0.02 into the wall, off the frames' backs
        prism('Dressing', [(OUT_Z + 0.02, y_out - 0.3), (OUT_Z - proud, y_out - 0.3), (OUT_Z - proud, y_out - 0.15),
                           (OUT_Z + 0.02, y_out)], x0, x1, outer, plane='zy')
    span('Dressing', (x0, y_in - 0.18, IN_Z - 0.02), (x1, y_in + 0.03, IN_Z + 0.2), inner)


def bar_v(x, y0, y1, col):
    """An upright glazing bar, outside and inside the pane, its ends into the wall round the
    opening; uprights stand prouder than rails on both sides."""
    span('Dressing', (x - 0.08, y0 - 0.07, -0.52), (x + 0.08, y1 + 0.07, -0.34), col)
    span('Dressing', (x - 0.08, y0 - 0.07, -0.3), (x + 0.08, y1 + 0.07, -0.1), col)


def bar_h(x0, x1, y, col):
    span('Dressing', (x0 - 0.07, y - 0.08, -0.5), (x1 + 0.07, y + 0.08, -0.35), col)
    span('Dressing', (x0 - 0.07, y - 0.08, -0.29), (x1 + 0.07, y + 0.08, -0.12), col)


def bars(wtype, shapes, col):
    """The glazing bars: a twin sash's meeting rails, an arch's mullion and transom, a round
    window's cross, a wide window's two mullions (three panes). Uprights stand prouder than rails."""
    for s in shapes:
        x0, x1, y0, y1 = s['bbox']
        if s['kind'] == 'rect':
            if wtype == 'Wide':
                for k in (1, 2):
                    bar_v(x0 + (x1 - x0) * k / 3, y0, y1, col)
            else:
                bar_h(x0, x1, y0 + (y1 - y0) * 0.55, col)
        elif s['kind'] == 'arch':
            bar_v((x0 + x1) / 2, y0, y1, col)
            bar_h(x0, x1, s['spring'], col)
        else:
            (cx, cy), r = s['c'], s['r']
            bar_v(cx, cy - r, cy + r, col)
            bar_h(cx - r, cx + r, cy, col)


def flower_box(x0, x1, ytop, box_col, soil, flowers, leaf, flower_part='Dressing'):
    """A box under a wide window's sill, its earth and a row of flowers (or what the style grows)."""
    span('Dressing', (x0, ytop - 1.2, OUT_Z - 0.7), (x1, ytop, OUT_Z), box_col, bevel=0.05)
    for xb in (x0 + 0.7, x1 - 0.7):
        prism('Dressing', [(OUT_Z + 0.02, ytop - 1.2), (OUT_Z - 0.55, ytop - 1.2), (OUT_Z + 0.02, ytop - 1.85)],
              xb - 0.07, xb + 0.07, box_col, plane='zy')
    span('Dressing', (x0 + 0.12, ytop - 0.2, OUT_Z - 0.6), (x1 - 0.12, ytop + 0.03, OUT_Z - 0.1), soil)
    n = max(2, int((x1 - x0) / 0.75))
    for i in range(n):
        x = x0 + 0.45 + i * (x1 - x0 - 0.9) / (n - 1)
        sphere('Dressing', (x, ytop + 0.12, OUT_Z - 0.33), (0.32, 0.18, 0.22), leaf, n=6, rings=3)
        sphere(flower_part, (x + 0.08 * (-1) ** i, ytop + 0.42 + 0.12 * (i % 3 == 0), OUT_Z - 0.3 - 0.08 * (i % 2)),
               (0.22, 0.2, 0.2), flowers[i % len(flowers)], n=6, rings=3)


DEFAULT_SHAPES = {
    'TwinSash': [rect(-3.6, -0.4, 3.0, 12.0), rect(0.4, 3.6, 3.0, 12.0)],   # two tall narrow panes
    'Arched': [lancet(-2.5, 2.5, 3.0, 9.6, 12.0)],                          # one tall pointed arch
    'Round': [disc(0.0, 7.4, 3.4)],                                          # a round moon window
    'Wide': [rect(-4.0, 4.0, 3.5, 10.0)],                                    # three panes over a flower box
}


def plain_wall(st):
    piece('Facade_Wall')
    wall_body('Wall', -6, 6, st['bands'])
    if st.get('wall_extra'):
        st['wall_extra']([])
    wall_body('LOD_Proxy', -6, 6, [(0, WALL, 'grey', 'grey')], ends=(False, False))
    finish(proxy=False, note=f"a plain wall: {st['wall_note']}")


def window_piece(st, wtype):
    """A wall section with one window of the type (MODELS.md, `Facade_Window_<Type>`): the hole(s)
    in the wall, the wall round a shaped opening, the pane, the frames out and in, the sill, the
    bars, a wide window's flower box, and the style's own (`extra`)."""
    p = piece(f'Facade_Window_{wtype}')
    shapes = st.get('shapes', {}).get(wtype) or DEFAULT_SHAPES[wtype]
    p.openings = [s['bbox'] for s in shapes]
    wall_body('Wall', -6, 6, st['bands'], p.openings)
    for s in shapes:
        infill(s, st['infill'])
        glass(s, st['glass'])
        if st.get('frame'):
            frame(s, *st['frame'])
        inner_frame(s, st['inner_frame'], st.get('inner_w', 0.32))
    if all(s['kind'] == 'circle' for s in shapes):
        sx0 = min(s['c'][0] - 0.65 * s['r'] for s in shapes)
        sx1 = max(s['c'][0] + 0.65 * s['r'] for s in shapes)
    else:
        sx0, sx1 = min(s['bbox'][0] for s in shapes) - 0.15, max(s['bbox'][1] for s in shapes) + 0.15
    foot = min(s['bbox'][2] for s in shapes)
    sy = foot - st.get('sill_drop', 0.0)
    if wtype != 'Round' or st.get('round_sill'):    # a ledge under a circle floats, outside and in
        sill_under(sx0, sx1, sy, foot, st['sill'][0], st['sill'][1])
    if callable(st.get('bars')):
        st['bars'](wtype, shapes)
    elif st.get('bars'):
        bars(wtype, shapes, st['bars'])
    if wtype == 'Wide' and st.get('flowers'):
        fb = st['flowers']
        flower_box(-4.1, 4.1, sy - 0.32 - fb.get('drop', 0.0), fb['box'], fb['soil'], fb['flowers'], fb['leaf'], fb.get('part', 'Dressing'))
    if st.get('extra'):
        st['extra'](wtype, shapes, (sx0, sx1, sy))
    if st.get('wall_extra'):
        st['wall_extra'](p.openings)
    wall_body('LOD_Proxy', -6, 6, [(0, WALL, 'grey', 'grey')], p.openings, ends=(False, False))
    finish(proxy=False, note=f"{st['wall_note']}; a {wtype} window: {st['window_note']}")


# --- Haunted Manor (Location 1): the approved Lobby front wall, carried over ----------------------

HM_BANDS = [(0, 0.6, 'stone_dark', 'plum_dark'), (0.6, 2.6, 'plum', 'plum_dark'), (2.6, 2.78, 'plum', 'gold'),
            (2.78, 3.0, 'plum', 'plum_dark'), (3.0, 12.0, 'plum', 'lilac'), (12.0, 12.5, 'gold', 'gold'),
            (12.5, 16.6, 'plum', 'lilac'), (16.6, 17.0, 'gold', 'gold')]
HM_POST = [(0, 0.6, 'stone_dark'), (0.6, 12.0, 'plum_dark'), (12.0, 12.5, 'gold'), (12.5, 16.6, 'plum_dark'),
           (16.6, 17.0, 'gold')]


def hm_entrance():
    piece('Facade_Entrance')
    wall_body('Wall_Left', -12, -PIER, HM_BANDS, ends=(True, False))
    wall_body('Wall_Right', PIER, 12, HM_BANDS, ends=(False, True))
    # The approved arch (build_hotel_haunted_manor.lobby), stone pillars and the pointed plum gable.
    for name, x in (('ArchLeft', -5), ('ArchRight', 5)):
        span(name, (x - 0.5, 0, zm(0)), (x + 0.5, 0.6, zm(1)), 'stone_dark', bevel=0.08)
        span(name, (x - 0.42, 0.6, zm(0.08)), (x + 0.42, 8.4, zm(0.92)), 'stone', bevel=0.1)
        span(name, (x - 0.5, 8.4, zm(0)), (x + 0.5, 9.0, zm(1)), 'gold', bevel=0.08)
    inner = arch_points(-4.5, 4.5, 9.0, 10.6, n=5)
    gable = [(-5.5, 9.0), (-5.5, 10.4), (0, 11.8), (5.5, 10.4), (5.5, 9.0)] + list(reversed(inner))
    prism('ArchTop', gable, zm(0.05), zm(0.95), {'front': 'plum', 'back': 'plum', 'rest': 'gold'})
    _KIT['pumpkin']('ArchTop', (0, 11.1, zm(0.05) - 0.12), 0.36)   # on the gable's face (it was buried in it)
    over = [(-5.5, 10.41), (0, 11.81), (5.5, 10.41), (5.5, 12.0), (-5.5, 12.0)]
    prism('ArchTop', over, OUT_Z, IN_Z, {'front': 'plum', 'back': 'lilac', 'rest': 'lilac'})
    wall_body('ArchTop', -PIER, PIER, bands_between(HM_BANDS, 12.0, WALL), ends=(False, False))
    for s in (-1, 1):   # the slit between each round shaft and the wall's end, filled
        lo, hi = sorted((s * 5.42, s * PIER))
        span('Dressing', (lo, 0.6, OUT_Z + 0.03), (hi, 8.4, IN_Z - 0.03), {'front': 'plum', 'back': 'lilac', 'rest': 'plum'})
    hanging_lantern(0, 10.6, zm(0.5) - 0.08, 'iron', k=1.75)
    entrance_proxy()
    finish(proxy=False, note="the Lobby's pointed arch: stone pillars, gold capitals, the plum gable and its pumpkin, "
                             "the iron lantern hung in the arch")


def hm_corner():
    piece('Facade_Corner')
    post(HM_POST)
    bead('gold')
    finish(proxy=False, note="a dark plum post with the wall's stone plinth and gold courses")


# --- Frostfang Lodge (Location 2) ------------------------------------------------------------------

FF_BANDS = ([(0, 0.6, 'stone_dark', 'wood_dark'), (0.6, 2.6, 'facade', 'wood_dark'), (2.6, 2.78, 'facade', 'snow'),
             (2.78, 3.0, 'facade', 'wood_dark')]
            + [(3.0 + k, 4.0 + k, 'facade', ('log', 'log_dark')[k % 2]) for k in range(9)]
            + [(12.0, 12.5, 'snow', 'snow')]
            + [(12.5 + k * 1.025, 12.5 + (k + 1) * 1.025, 'facade', ('log', 'log_dark')[(k + 1) % 2]) for k in range(4)]
            + [(16.6, 17.0, 'snow', 'snow')])
FF_POST = [(0, 0.6, 'stone_dark'), (0.6, 12.0, 'log_dark'), (12.0, 12.5, 'snow'), (12.5, 16.6, 'log_dark'),
           (16.6, 17.0, 'snow')]


def flake(part, c, r, col, t=0.04):
    """The Lobby's six-armed flake (build_hotel_frostfang_lodge.flake) on a face toward -Z at c.z, its
    three bars and six tips each a little prouder than the last, so no two share a face."""
    k = 0
    for i in range(3):
        k += 1
        box(part, (0, 0, 0), (2 * r, r * 0.22, t), col, m=at((c[0], c[1], c[2] - t / 2 - 0.01 * k + 0.01), rz=i * 60))
    for i in range(6):
        k += 1
        a = math.radians(i * 60)
        p = (c[0] + 0.7 * r * math.cos(a), c[1] + 0.7 * r * math.sin(a), c[2] - t / 2 - 0.01 * k + 0.01)
        box(part, (0, 0, 0), (r * 0.4, r * 0.14, t), col, m=at(p, rz=i * 60 + 90))


def ff_entrance():
    piece('Facade_Entrance')
    wall_body('Wall_Left', -12, -PIER, FF_BANDS, ends=(True, False))
    wall_body('Wall_Right', PIER, 12, FF_BANDS, ends=(False, True))
    # The approved arch (build_hotel_frostfang_lodge.lobby): log pillars and the snowy timber gable.
    for name, x in (('ArchLeft', -5), ('ArchRight', 5)):
        span(name, (x - 0.5, 0, zm(0)), (x + 0.5, 0.6, zm(1)), 'stone_dark', bevel=0.08)
        cyl(name, (x, 0.6, zm(0.5)), 0.42, 7.8, 'log', n=8)
        span(name, (x - 0.5, 8.4, zm(0)), (x + 0.5, 9.0, zm(1)), 'wood_dark', bevel=0.08)
    gable = [(-5.5, 9.0), (5.5, 9.0), (5.5, 9.5), (0, 11.2), (-5.5, 9.5)]
    prism('ArchTop', gable, zm(0.05), zm(0.95), {'front': 'facade', 'back': 'facade', 'rest': 'wood_dark'})
    snow = [(-5.9, 9.4), (-5.5, 9.45), (0, 11.15), (5.5, 9.45), (5.9, 9.4), (5.9, 9.75), (0, 11.75), (-5.9, 9.75)]
    prism('ArchTop', snow, zm(0), IN_Z - 0.06, 'snow')     # its back inside the wall, off the faces behind it
    flake('ArchTop', (0, 10.1, zm(0.05)), 0.5, 'trim')
    over = [(-5.5, 9.9), (0, 11.76), (5.5, 9.9), (5.5, 12.0), (-5.5, 12.0)]
    prism('ArchTop', over, OUT_Z, IN_Z, {'front': 'facade', 'back': 'log', 'rest': 'log'})
    wall_body('ArchTop', -PIER, PIER, bands_between(FF_BANDS, 12.0, WALL), ends=(False, False))
    for x in (-4.2, -2.6, 2.4, 4.0):
        _KIT['icicle']('Dressing', x, 9.0, zm(0.5), 0.5 + 0.2 * (abs(x) % 2), r=0.12)
    for s in (-1, 1):
        lo, hi = sorted((s * 5.42, s * PIER))
        span('Dressing', (lo, 0.6, OUT_Z + 0.03), (hi, 8.4, IN_Z - 0.03), {'front': 'facade', 'back': 'log', 'rest': 'facade'})
    # The opening is square-headed (the gable sits over it), so the lantern hangs from its lintel.
    hanging_lantern(0, ARCH_Y, zm(0.5) - 0.08, 'iron', k=1.0, chain=0.05)
    entrance_proxy()
    finish(proxy=False, note="the Lobby's log pillars and snowy timber gable with its flake and icicles, the iron "
                             "lantern hung from the lintel")


def ff_corner():
    piece('Facade_Corner')
    post(FF_POST)
    bead('snow')
    finish(proxy=False, note="a dark log post with the wall's stone plinth and snow courses")


# --- Gothic: dark slate, pointed windows, red stained-glass trim, small gargoyles on the corners ---

GOTHIC_PALETTE = [
    ('grey', (110, 110, 120)), ('slate', (64, 66, 80)), ('slate_dark', (42, 43, 54)), ('slate_light', (92, 94, 112)),
    ('stone', (150, 146, 152)), ('stone_light', (186, 182, 186)), ('stone_dark', (105, 102, 110)),
    ('ruby', (196, 32, 52)), ('ruby_light', (226, 78, 88)), ('amber', (232, 160, 64)), ('night', (24, 26, 48)),
    ('wine', (96, 34, 52)), ('wine_dark', (66, 24, 38)), ('iron', (52, 54, 62)), ('ivy', (62, 92, 64)),
    ('gargoyle', (122, 120, 128)), ('gargoyle_dark', (86, 84, 94)),
    ('flame', (255, 205, 120), 'Warm'), ('lamp', (255, 185, 110), 'Warm'),
]
GOTHIC_BANDS = [(0, 0.6, 'slate_dark', 'slate_dark'), (0.6, 3.0, 'slate', 'slate_dark'), (3.0, 16.4, 'slate', 'wine'),
                (16.4, 17.0, 'stone', 'stone')]
GOTHIC_POST = [(0, 0.6, 'slate_dark'), (0.6, 16.4, 'slate_dark'), (16.4, 17.0, 'stone')]
RUBY = ('ruby', 'ruby_light')


def gothic_bars(wtype, shapes):
    """Stone tracery: a lancet's mullion up to its spring, a rose window's eight spokes and hub,
    a wide window's two mullions; the twin lancets are plain."""
    for s in shapes:
        stained(s, RUBY)
        x0, x1, y0, y1 = s['bbox']
        if wtype == 'Arched':
            bar_v((x0 + x1) / 2, y0, y1, 'stone')
        elif wtype == 'Round':
            (cx, cy), r = s['c'], s['r']
            for k in range(4):      # four diameters, fronts and backs apart: they cross at the hub
                front, back = -0.5 - 0.012 * k, -0.35 + 0.004 * k
                box('Dressing', (0, 0, 0), (0.16, 2 * r + 0.14, back - front), 'stone',
                    m=at((cx, cy, (front + back) / 2), rz=k * 45))
            cyl('Dressing', (0, 0, 0), 0.5, 0.25, 'stone', n=10, m=at((cx, cy, -0.58), rx=90))


def gothic_entrance():
    piece('Facade_Entrance')
    wall_body('Wall_Left', -12, -PIER, GOTHIC_BANDS, ends=(True, False))
    wall_body('Wall_Right', PIER, 12, GOTHIC_BANDS, ends=(False, True))
    for name, x in (('ArchLeft', -5), ('ArchRight', 5)):
        span(name, (x - 0.5, 0, zm(0)), (x + 0.5, 0.6, zm(1)), 'slate_dark', bevel=0.06)
        span(name, (x - 0.4, 0.6, zm(0.1)), (x + 0.4, 8.4, zm(0.9)), 'stone_dark', bevel=0.08)
        span(name, (x - 0.5, 8.4, zm(0)), (x + 0.5, 9.0, zm(1)), 'stone_light', bevel=0.06)
    # A pointed arch of voussoirs, alternating stone, from the capitals; slate over it to the top.
    inner = arch_points(-4.5, 4.5, 9.0, 12.4, n=6)
    outer = arch_points(-5.5, 5.5, 9.0, 13.3, n=6)
    arch_band('ArchTop', outer, inner, zm(0), zm(0.95), ('stone', 'stone_light'), split=1.4)
    prism('ArchTop', outer + [(5.5, 16.4), (-5.5, 16.4)], OUT_Z, IN_Z, {'front': 'slate', 'back': 'wine', 'rest': 'slate'})
    span('ArchTop', (-PIER, 16.4, OUT_Z), (PIER, WALL, IN_Z), 'stone')
    # A red rose window over the arch: eight ruby panes round an amber eye, in a stone ring.
    c, r0, r1 = (0, 14.85), 0.45, 1.2      # clear of the arch's crown (13.3) and the coping (16.4)
    for k in range(8):
        a0, a1 = math.radians(k * 45 + 22.5), math.radians(k * 45 + 67.5)
        quad = [(c[0] + r0 * math.cos(a0), c[1] + r0 * math.sin(a0)), (c[0] + r1 * math.cos(a0), c[1] + r1 * math.sin(a0)),
                (c[0] + r1 * math.cos(a1), c[1] + r1 * math.sin(a1)), (c[0] + r0 * math.cos(a1), c[1] + r0 * math.sin(a1))]
        prism('Glass', quad, OUT_Z - 0.05, OUT_Z + 0.01, RUBY[k % 2])
    cyl('Glass', (0, 0, 0), r0 + 0.01, 0.075, 'amber', n=8, m=at((c[0], c[1], OUT_Z - 0.06), rx=90))
    lathe('Dressing', [(r1, 0), (r1 + 0.25, 0), (r1 + 0.25, 0.12), (r1, 0.12)], 'stone_light', n=16, closed=True,
          m=at((c[0], c[1], OUT_Z - 0.1), rx=90))
    for k in range(4):      # the windows' rose tracery, small: four diameters, fronts and backs apart, a hub
        front, back = OUT_Z - 0.1 - 0.012 * k, OUT_Z - 0.06 + 0.004 * k
        box('Dressing', (0, 0, 0), (0.12, 2 * r1 * 0.96, back - front), 'stone_light',
            m=at((c[0], c[1], (front + back) / 2), rz=k * 45))
    cyl('Dressing', (0, 0, 0), 0.3, 0.2, 'stone_light', n=10, m=at((c[0], c[1], OUT_Z - 0.2), rx=90))
    for s in (-1, 1):
        lo, hi = sorted((s * 5.4, s * PIER))
        span('Dressing', (lo, 0.6, OUT_Z + 0.03), (hi, 8.4, IN_Z - 0.03), {'front': 'slate', 'back': 'wine', 'rest': 'slate'})
    hanging_lantern(0, 12.4, zm(0.5) - 0.08, 'iron', k=1.8, chain=0.9)
    entrance_proxy()
    finish(proxy=False, note='a pointed arch of alternating stone voussoirs, a red rose window over it, an iron lantern')


def gargoyle():
    """A stone gargoyle crouching on a corbel high on the corner, looking out along the diagonal
    (local -Z), 1.6 times the first draft's (it did not read): body, head, snout, horns, folded
    wings, claws."""
    g, gd = 'gargoyle', 'gargoyle_dark'
    m = DIAG @ Matrix.Translation((0, 14.2, 0)) @ Matrix.Scale(1.6, 4)
    span('Dressing', (-0.3, -0.5, -0.95), (0.3, 0, 0.05), 'stone', bevel=0.06, m=m)          # the corbel
    span('Dressing', (-0.24, -0.9, -0.55), (0.24, -0.5, 0.05), 'stone_dark', bevel=0.05, m=m)
    sphere('Dressing', (0, 0.45, -0.45), (0.3, 0.42, 0.38), g, n=8, rings=5, m=m)            # the body
    sphere('Dressing', (0, 0.85, -0.85), (0.24, 0.22, 0.24), g, n=8, rings=4, m=m)           # the head
    span('Dressing', (-0.12, 0.68, -1.25), (0.12, 0.86, -0.9), gd, bevel=0.04, m=m)          # the snout
    for s in (-1, 1):
        cyl('Dressing', (0, 0, 0), 0.06, 0.28, gd, n=5, r_top=0.01, m=m @ at((s * 0.15, 1.0, -0.8), rz=-s * 25))
        prism('Dressing', [(-0.15, 0.2), (0.05, 0.95), (-0.05, 1.25), (-0.35, 0.85)],
              s * 0.27, s * 0.33, gd, plane='zy', m=m)                                      # a wing, folded
        sphere('Dressing', (s * 0.16, 0.06, -0.8), (0.1, 0.07, 0.14), gd, n=6, rings=3, m=m)  # a claw


def gothic_corner():
    piece('Facade_Corner')
    post(GOTHIC_POST)
    bead('stone', y1=13.0)
    gargoyle()
    finish(proxy=False, note='a dark slate post with a stone gargoyle on a corbel at the top')


# --- Neon: dark panels with glowing cyan and magenta tubes round the windows ------------------------

NEON_PALETTE = [
    ('grey', (110, 110, 120)), ('panel', (30, 28, 52)), ('panel_dark', (18, 17, 34)), ('panel_edge', (56, 52, 90)),
    ('steel', (92, 96, 114)), ('steel_dark', (60, 62, 76)), ('glass', (16, 18, 40)), ('ink', (40, 36, 66)),
    ('ink_dark', (28, 26, 48)), ('cyan', (70, 245, 255), 'Cyan'), ('magenta', (255, 60, 200), 'Magenta'),
    ('lamp', (255, 185, 110), 'Warm'),
]
NEON_BANDS = [(0, 0.6, 'panel_dark', 'ink_dark'), (0.6, 2.8, 'panel', 'ink_dark'), (2.8, 3.0, 'panel_edge', 'ink_dark'),
              (3.0, 12.0, 'panel', 'ink'), (12.0, 12.2, 'panel_edge', 'ink'), (12.2, 16.6, 'panel', 'ink'),
              (16.6, 17.0, 'panel_edge', 'panel_edge')]
NEON_POST = [(0, 0.6, 'panel_dark'), (0.6, 17.0, 'panel_edge')]
NEON_R = 0.07
NEON_TUBES = {'TwinSash': ('cyan', 'magenta'), 'Arched': ('cyan',), 'Round': ('magenta',), 'Wide': ('cyan',)}


def neon_tubes(wtype, shapes, sill):
    """A tube round each opening on the face, in the type's colours (a twin sash's two alternate)."""
    for s, col in zip(shapes, NEON_TUBES[wtype]):
        pts = [(x, y, OUT_Z - NEON_R) for x, y in outline(s, 0.12 + NEON_R)]
        tube(f'Glow_{col.capitalize()}_1', pts, NEON_R, col, closed=True)


def neon_entrance():
    piece('Facade_Entrance')
    wall_body('Wall_Left', -12, -PIER, NEON_BANDS, ends=(True, False))
    wall_body('Wall_Right', PIER, 12, NEON_BANDS, ends=(False, True))
    for name, x in (('ArchLeft', -5), ('ArchRight', 5)):
        span(name, (x - 0.5, 0, zm(0)), (x + 0.5, ARCH_Y, zm(1)), {'front': 'steel_dark', 'rest': 'panel_edge'}, bevel=0.05)
    # A square-shouldered opening: a steel lintel, the panels over it to the top.
    span('ArchTop', (-PIER, ARCH_Y, zm(0)), (PIER, ARCH_Y + 0.8, zm(1)), {'front': 'steel_dark', 'rest': 'panel_edge'}, bevel=0.05)
    wall_body('ArchTop', -PIER, PIER, [(ARCH_Y + 0.8, 12.0, 'panel', 'ink')] + bands_between(NEON_BANDS, 12.0, WALL),
              ends=(False, False))
    # Two tubes round the doorway, cyan inside magenta, up the pillars' fronts and over the lintel.
    for gname, col, o in (('Glow_Cyan_1', 'cyan', 4.72), ('Glow_Magenta_1', 'magenta', 5.25)):
        zf = zm(0) - NEON_R
        top = ARCH_Y + (0.3 if o < 5 else 0.62)
        path = [(-o, 0.3, zf), (-o, top - 0.4, zf), (-o + 0.4, top, zf), (o - 0.4, top, zf), (o, top - 0.4, zf), (o, 0.3, zf)]
        tube(gname, path, NEON_R, col)
    # A chevron of tubes over the door, the hotel's sign-light.
    zf = OUT_Z - NEON_R
    tube('Glow_Magenta_1', [(-3.0, 11.0, zf), (0, 12.6, zf), (3.0, 11.0, zf)], NEON_R, 'magenta')
    tube('Glow_Cyan_1', [(-3.0, 11.7, zf), (0, 13.3, zf), (3.0, 11.7, zf)], NEON_R, 'cyan')
    entrance_proxy()
    finish(proxy=False, note='steel pillars and lintel, a cyan and a magenta tube round the doorway and a chevron '
                             'of both over it')


def neon_corner():
    piece('Facade_Corner')
    post(NEON_POST)
    # A glowing strip set into each visible face of the post, cyan on one, magenta on the other.
    span('Glow_Cyan_1', (-0.42, 0.8, -POST - 0.02), (-0.22, 16.4, -POST + 0.01), 'cyan')
    span('Glow_Magenta_1', (-POST - 0.02, 0.8, -0.42), (-POST + 0.01, 16.4, -0.22), 'magenta')
    finish(proxy=False, note='a dark post with a cyan strip down one face and a magenta strip down the other')


# --- Candy: pink wafer walls, white icing dripping from the top, striped posts -----------------------

CANDY_PALETTE = [
    ('grey', (110, 110, 120)), ('wafer', (244, 168, 196)), ('wafer_dark', (222, 128, 166)), ('cream', (252, 236, 222)),
    ('icing', (252, 252, 250)), ('icing_shade', (232, 228, 238)), ('cherry', (224, 38, 68)), ('cherry_dark', (160, 24, 48)),
    ('choc', (112, 66, 46)), ('choc_dark', (78, 44, 32)), ('mint', (150, 228, 200)), ('night', (40, 30, 56)),
    ('stem', (90, 150, 70)), ('flame', (255, 205, 120), 'Warm'), ('lamp', (255, 185, 110), 'Warm'),
]
# The wafer as layers with cream between (a lattice of squares would be the texture grid taste.md forbids).
CANDY_BANDS = [(0, 0.6, 'choc', 'choc')]
_y = 0.6
while _y < 16.2 - 1e-6:
    _y1 = round(_y + 1.5, 4)
    if 16.2 - _y1 < 0.6:            # no sliver of wafer under the icing
        _y1 = 16.2
    CANDY_BANDS.append((_y, _y1, 'wafer', 'cream'))
    if _y1 < 16.2:
        CANDY_BANDS.append((_y1, round(_y1 + 0.25, 4), 'cream', 'cream'))
    _y = round(_y1 + 0.25, 4) if _y1 < 16.2 else 16.2
CANDY_BANDS.append((16.2, 17.0, 'icing', 'icing'))
CANDY_POST = [(0, 0.6, 'choc'), (0.6, 17.0, 'icing')]


def stripes(face, x0, x1, y0, y1, w, col, depth=0.025, period=1.6, part='Dressing', y_start=None):
    """Candy-cane stripes on a face, rising from x0 to x1 (each a parallelogram, proud `depth`, its
    ends kept off the face's edges, where they would share a face with it). `face` is (axis, the
    face's coordinate): 'z' a face toward -Z, 'x' a face toward -X (x0..x1 then run along Z)."""
    axis, at_ = face
    run = abs(x1 - x0)
    y = y0 - run if y_start is None else y_start
    while y < y1:
        quad = [(x0, y), (x1, y + run), (x1, y + run + w), (x0, y + w)]
        clipped = [(u, min(max(v, y0), y1)) for u, v in quad]
        if abs(_poly_area(clipped)) > 1e-3:
            if axis == 'z':
                prism(part, clipped, at_ - depth, at_ + 0.01, col)
            else:
                prism(part, clipped, at_ - depth, at_ + 0.01, col, plane='zy')
        y += period


def candy_corner():
    piece('Facade_Corner')
    post(CANDY_POST)
    # A round candy cane up the corner, red and white (the flat stripes read as tape on an edge).
    bead(('cherry', 'icing'), r=0.24, segs=0.7)
    finish(proxy=False, note='a white post with a round red-and-white candy cane up its corner, a chocolate foot')


def candy_entrance():
    piece('Facade_Entrance')
    wall_body('Wall_Left', -12, -PIER, CANDY_BANDS, ends=(True, False))
    wall_body('Wall_Right', PIER, 12, CANDY_BANDS, ends=(False, True))
    for name, x in (('ArchLeft', -5), ('ArchRight', 5)):
        span(name, (x - 0.5, 0, zm(0)), (x + 0.5, 0.6, zm(1)), 'choc', bevel=0.06)
        span(name, (x - 0.45, 0.6, zm(0.05)), (x + 0.45, ARCH_Y, zm(0.95)), 'icing', bevel=0.06)
        stripes(('z', zm(0.05)), x + 0.44, x - 0.44, 0.62, ARCH_Y - 0.02, 0.4, 'cherry', part=name)
    # A round arch of white icing on the capitals, wafer round it, the drips off its rim, a cherry on top.
    inner = round_arch_points(-4.5, 4.5, ARCH_Y, 13.5, n=10)
    outer = round_arch_points(-5.4, 5.4, ARCH_Y, 14.3, n=10)
    arch_band('ArchTop', outer, inner, zm(0), zm(0.95), ('icing', 'icing_shade'), split=2.0)
    over_arch_bands('ArchTop', CANDY_BANDS, [(-5.5, ARCH_Y)] + outer[1:-1] + [(5.5, ARCH_Y)], WALL)
    for t, length, w in ((0.2, 0.6, 0.42), (0.32, 1.0, 0.36), (0.42, 0.5, 0.48), (0.58, 0.9, 0.4), (0.68, 0.55, 0.5),
                         (0.8, 0.85, 0.38)):
        a = math.pi * (1 - t)
        x, y = 4.5 * math.cos(a), ARCH_Y + 4.5 * math.sin(a)
        drip('Dressing', x, y + 0.1, length, w, 'icing', z_face=zm(0), depth=0.1)
    sphere('Dressing', (0, 14.95, zm(0) - 0.4), (0.7, 0.66, 0.6), 'cherry', n=10, rings=5)
    cyl('Dressing', (0, 0, 0), 0.07, 0.75, 'stem', n=5, m=at((0.08, 15.5, zm(0) - 0.4), rz=-20))
    drip_row(12.0, 16.25, 'icing', clear=(-2.0, 2.0))
    for s in (-1, 1):
        lo, hi = sorted((s * 5.45, s * PIER))
        span('Dressing', (lo, 0.6, OUT_Z + 0.03), (hi, 8.4, IN_Z - 0.03), 'wafer')
    hanging_lantern(0, 13.5, zm(0.5) - 0.08, 'cherry_dark', cap='wafer', k=1.8, chain=0.6)
    entrance_proxy()
    finish(proxy=False, note='striped candy-cane pillars, a round icing arch with drips, a cherry on top, a pink '
                             'lantern hung in the arch')


# --- Pirate: weathered ship planks, round porthole windows, rope trim, a lantern on each corner ------

PIRATE_PALETTE = [
    ('grey', (110, 110, 120)), ('plank', (128, 90, 58)), ('plank_dark', (98, 68, 46)), ('plank_grey', (126, 112, 96)),
    ('plank_light', (146, 106, 70)), ('brass', (206, 162, 72)), ('brass_dark', (150, 112, 48)), ('rope', (204, 174, 116)),
    ('rope_dark', (150, 122, 78)), ('hemp', (228, 210, 166)), ('iron', (58, 58, 64)), ('sea', (28, 58, 78)), ('cabin', (150, 110, 72)),
    ('cabin_dark', (100, 70, 46)), ('herb', (92, 140, 70)), ('herb_dark', (60, 100, 52)), ('berry', (200, 60, 60)),
    ('flame', (255, 205, 120), 'Warm'), ('lamp', (255, 185, 110), 'Warm'),
]
# Weathered planks: narrow, in four close woods, no two neighbours alike (they read as stripes when broad).
_PL = ('plank', 'plank_grey', 'plank_dark', 'plank_light', 'plank', 'plank_dark', 'plank_grey', 'plank_light')
PIRATE_BANDS = [(0, 0.6, 'plank_dark', 'cabin_dark')]
_y, _k = 0.6, 0
while _y < 16.6 - 1e-6:
    _y1 = min(16.6, round(_y + 0.8, 4))
    PIRATE_BANDS.append((_y, _y1, _PL[_k % len(_PL)], ('cabin', 'cabin_dark')[_k % 2]))
    _y, _k = _y1, _k + 1
PIRATE_BANDS.append((16.6, 17.0, 'plank_dark', 'cabin_dark'))
PIRATE_POST = [(0, 17.0, 'plank_dark')]
ROPE_R = 0.18
_JOINTS = ((-3.7, 1.9), (-1.1, 4.3), (-4.6, 0.6), (-2.4, 3.1), (-0.3, 2.6))


def pirate_joints(openings, h=6.0):
    """The planks' butt ends, staggered from plank to plank (they read as stripes without them): a
    dark seam a hair proud, kept off the windows and the piece's ends."""
    k = 0
    for y0, y1, _, _ in PIRATE_BANDS:
        if y0 < 0.6 - 1e-9 or y1 > 16.6 + 1e-9:
            continue
        for base in _JOINTS[k % len(_JOINTS)]:
            for off in ((0.0,) if h <= 6 else (-12.0, 0.0, 12.0)):
                x = base + off
                if abs(x) > h - 0.8 or any(a - 0.6 < x < b + 0.6 and c - 0.6 < y1 and y0 < d + 0.6
                                           for a, b, c, d in openings):
                    continue
                span('Dressing', (x - 0.035, y0 + 0.05, OUT_Z - 0.012), (x + 0.035, y1 - 0.05, OUT_Z + 0.01), 'plank_dark')
        k += 1


def pirate_extra(wtype, shapes, sill):
    """Rope round every window (it ran along the wall before, and was cut at every joint), a brass
    ring round every porthole, a dark plank frame round the rest."""
    for s in shapes:
        if s['kind'] == 'circle':
            frame(s, 'brass', 0.28, 0.1)
        else:
            frame(s, 'plank_dark', 0.28, 0.06)
        pts = [(x, y, OUT_Z - ROPE_R) for x, y in outline(s, 0.28 + ROPE_R + 0.02)]
        tube('Dressing', pts, ROPE_R, 'hemp', n=6, closed=True)


def pirate_bars(wtype, shapes):
    for s in shapes:
        if s['kind'] == 'circle':
            continue
        bars(wtype, [s], 'plank_dark')


def corner_lantern():
    """A ship's lantern on an iron bracket off the corner, along the diagonal, high up; 1.5 times the
    first draft's (it did not read)."""
    m = DIAG @ Matrix.Translation((0, 16.0, 0)) @ Matrix.Scale(1.75, 4)
    span('Dressing', (-0.06, -0.06, -1.05), (0.06, 0.06, 0.03), 'iron', m=m)          # the arm
    span('Dressing', (-0.12, -0.6, -0.08), (0.12, 0.2, 0.05), 'iron', m=m)            # its plate
    span('Dressing', (-0.03, -0.35, -0.98), (0.03, -0.06, -0.92), 'iron', m=m)        # the hook
    lz, top = -0.95, -0.35
    lathe('Dressing', [(0.3, top - 0.12), (0.12, top + 0.05), (0, top + 0.08)], 'brass_dark', n=6, base=(0, 0, lz), m=m)
    box('Dressing', (0, top - 0.15, lz), (0.48, 0.08, 0.48), 'brass', m=m)
    box('Dressing', (0, top - 1.2, lz), (0.48, 0.1, 0.48), 'brass', m=m)
    for dx in (-0.2, 0.2):
        for dz in (-0.2, 0.2):
            box('Dressing', (dx, top - 0.68, lz + dz), (0.06, 0.95, 0.06), 'brass_dark', m=m)
    sphere('Glow_Warm_1', (0, top - 0.68, lz), (0.15, 0.25, 0.15), 'flame', n=8, rings=4, m=m)


def pirate_corner():
    piece('Facade_Corner')
    post(PIRATE_POST)
    bead('hemp', r=0.16, y1=12.4)
    for y in (2.0, 8.0, 12.6):   # iron bands round the timber
        span('Dressing', (-POST - 0.02, y, -POST - 0.02), (-0.01, y + 0.25, -POST + 0.01), 'iron')
        span('Dressing', (-POST - 0.02, y, -POST + 0.01), (-POST + 0.01, y + 0.25, -0.01), 'iron')
    corner_lantern()
    finish(proxy=False, note='a dark ship timber with iron bands, a brass lantern hung off it on an iron bracket')


def pirate_entrance():
    piece('Facade_Entrance')
    wall_body('Wall_Left', -12, -PIER, PIRATE_BANDS, ends=(True, False))
    wall_body('Wall_Right', PIER, 12, PIRATE_BANDS, ends=(False, True))
    for name, x in (('ArchLeft', -5), ('ArchRight', 5)):
        span(name, (x - 0.5, 0, zm(0)), (x + 0.5, ARCH_Y, zm(1)), 'plank_dark', bevel=0.06)
        for y in (1.2, 7.4):
            span('Dressing', (x - 0.53, y, zm(0) - 0.03), (x + 0.53, y + 0.3, zm(1) - 0.04), 'iron')
    inner = round_arch_points(-4.5, 4.5, ARCH_Y, 13.2, n=8)
    outer = round_arch_points(-5.5, 5.5, ARCH_Y, 14.2, n=8)
    arch_band('ArchTop', outer, inner, zm(0), zm(0.95), ('plank', 'plank_grey', 'plank_light'), split=1.5)
    over_arch_bands('ArchTop', PIRATE_BANDS, outer, WALL)
    pirate_joints([(-PIER - 0.2, PIER + 0.2, 0.0, WALL)], h=12.0)
    # The rope along the arch's rim, thick enough to read, its ends knotted on the pillars' caps.
    zr = zm(0) - 0.2
    rim = round_arch_points(-5.2, 5.2, ARCH_Y + 0.2, 13.9, n=12)
    tube('Dressing', [(x, y, zr) for x, y in rim], 0.22, 'hemp', n=6)
    for x, y in (rim[0], rim[-1]):
        sphere('Dressing', (x, y, zr), (0.3, 0.3, 0.24), 'rope_dark', n=6, rings=4)
    hanging_lantern(0, 13.2, zm(0.5) - 0.08, 'brass_dark', cap='brass', k=1.8, chain=0.7)
    entrance_proxy()
    finish(proxy=False, note='a round arch of planks between iron-banded timbers, rope along its rim, a brass '
                             'lantern hung in it')


# --- Slime: green walls with slime dripping off the sills ---------------------------------------------

SLIME_PALETTE = [
    ('grey', (110, 110, 120)), ('slime_wall', (88, 164, 96)), ('slime_wall_dark', (56, 116, 70)),
    ('slime_wall_light', (126, 192, 120)), ('slime', (170, 240, 92)), ('slime_dark', (122, 206, 70)),
    ('sill', (164, 172, 156)), ('sill_dark', (118, 126, 112)), ('night', (24, 40, 40)), ('moss', (85, 120, 70)),
    ('mint', (186, 224, 196)), ('iron', (58, 60, 64)), ('flame', (255, 205, 120), 'Warm'), ('lamp', (255, 185, 110), 'Warm'),
]
SLIME_BANDS = [(0, 0.6, 'slime_wall_dark', 'moss'), (0.6, 3.0, 'slime_wall', 'moss'), (3.0, 12.0, 'slime_wall', 'mint'),
               (12.0, 12.4, 'slime_wall_light', 'mint'), (12.4, 16.6, 'slime_wall', 'mint'), (16.6, 17.0, 'slime_wall_dark', 'moss')]
SLIME_POST = [(0, 0.6, 'slime_wall_dark'), (0.6, 12.0, 'slime_wall_dark'), (12.0, 12.4, 'slime_wall_light'),
              (12.4, 17.0, 'slime_wall_dark')]


def slime_extra(wtype, shapes, sill):
    """Slime pooled along the sill and dripping off its front edge, in lengths and widths that vary."""
    sx0, sx1, sy = sill
    wdt = sx1 - sx0
    sphere('Dressing', ((sx0 + sx1) / 2, sy - 0.02, OUT_Z - 0.16), (wdt / 2 * 0.95, 0.26, 0.2), 'slime', n=12, rings=4)
    if wtype == 'Wide':         # the box under it takes the overflow
        return
    drops = ((0.14, 1.1, 0.5), (0.33, 2.0, 0.42), (0.5, 0.8, 0.58), (0.68, 1.6, 0.46), (0.86, 1.2, 0.52))
    for t, length, w in drops:
        if wdt < 3.0 and t in (0.33, 0.68):
            continue
        drip('Dressing', sx0 + wdt * t, sy - 0.18, length, w, 'slime', z_face=OUT_Z - 0.04, depth=0.18)


def slime_corner():
    piece('Facade_Corner')
    post(SLIME_POST)
    bead('slime_wall_light', y1=15.6)
    # Slime oozing out under the slab, on both faces of the post's top, and down them.
    sphere('Dressing', (-0.33, 16.55, -POST), (0.24, 0.36, 0.13), 'slime', n=8, rings=4)
    sphere('Dressing', (-POST, 16.55, -0.33), (0.13, 0.36, 0.24), 'slime', n=8, rings=4)
    drip('Dressing', -0.3, 16.7, 1.1, 0.24, 'slime', z_face=-POST, depth=0.09)
    span('Dressing', (-POST - 0.09, 16.0, -0.44), (-POST, 16.7, -0.2), 'slime', bevel=0.03)
    sphere('Dressing', (-POST - 0.05, 16.0, -0.32), (0.08, 0.15, 0.15), 'slime', n=8, rings=4)
    finish(proxy=False, note='a dark green post with slime oozing over its top and down its faces')


def slime_entrance():
    piece('Facade_Entrance')
    wall_body('Wall_Left', -12, -PIER, SLIME_BANDS, ends=(True, False))
    wall_body('Wall_Right', PIER, 12, SLIME_BANDS, ends=(False, True))
    for name, x in (('ArchLeft', -5), ('ArchRight', 5)):
        span(name, (x - 0.5, 0, zm(0)), (x + 0.5, 0.6, zm(1)), 'sill_dark', bevel=0.06)
        span(name, (x - 0.42, 0.6, zm(0.08)), (x + 0.42, 8.4, zm(0.92)), 'sill', bevel=0.08)
        span(name, (x - 0.5, 8.4, zm(0)), (x + 0.5, ARCH_Y, zm(1)), 'sill_dark', bevel=0.06)
    inner = round_arch_points(-4.5, 4.5, ARCH_Y, 12.6, n=8)
    outer = round_arch_points(-5.5, 5.5, ARCH_Y, 13.6, n=8)
    arch_band('ArchTop', outer, inner, zm(0), zm(0.95), ('sill', 'sill_dark'), split=1.5)
    prism('ArchTop', outer + [(5.5, 16.6), (-5.5, 16.6)], OUT_Z, IN_Z, {'front': 'slime_wall', 'back': 'mint', 'rest': 'slime_wall'})
    span('ArchTop', (-PIER, 16.6, OUT_Z), (PIER, WALL, IN_Z), 'slime_wall_dark')
    # Slime heaped on the arch's ring and running down over it from each heap in long drips.
    for t, sx, drops in ((0.3, 0.8, ((-0.3, 1.8), (0.35, 1.1))), (0.5, 1.1, ((-0.5, 1.3), (0.2, 2.3), (0.7, 0.9))),
                         (0.7, 0.8, ((-0.35, 1.0), (0.3, 1.9)))):
        a = math.pi * (1 - t)
        cx, cy = 5.0 * math.cos(a), ARCH_Y + 4.1 * math.sin(a) + 0.3
        sphere('Dressing', (cx, cy, zm(0) - 0.12), (sx, 0.45, 0.3), 'slime', n=10, rings=5)
        for dx, length in drops:
            drip('Dressing', cx + dx, cy - 0.1, length, 0.42, 'slime', z_face=zm(0) - 0.02, depth=0.18)
    for s in (-1, 1):
        lo, hi = sorted((s * 5.42, s * PIER))
        span('Dressing', (lo, 0.6, OUT_Z + 0.03), (hi, 8.4, IN_Z - 0.03), 'slime_wall')
    hanging_lantern(0, 12.6, zm(0.5) - 0.08, 'iron', k=1.8, chain=0.6)
    entrance_proxy()
    finish(proxy=False, note='a round stone arch with slime heaped on its crown and dripping off its rim, an iron lantern')


# --- The styles ---------------------------------------------------------------------------------------

STYLES = {
    'haunted_manor': dict(
        title="Haunted Manor facade (the kit's own)", palette=HM_PALETTE, look="the Lobby front wall's, carried over",
        bands=HM_BANDS, post=HM_POST, entrance=hm_entrance, corner=hm_corner, infill={'front': 'plum', 'back': 'lilac', 'rest': 'plum'},
        glass='night', frame=('wood_dark', 0.25, 0.03), inner_frame='wood_dark', sill=('gold', 'gold'), bars='wood_dark',
        flowers=dict(box='wood_dark', soil='plum_deep', flowers=('violet', 'pumpkin', 'lilac'), leaf='moss'),
        wall_note="the Lobby front wall's bands (stone plinth, plum, gold courses; lilac and plum inside)",
        window_note='dark wood frames and bars, a gold sill'),
    'frostfang_lodge': dict(
        title="Frostfang Lodge facade (the kit's own)", palette=FF_PALETTE, look="the Lobby front wall's, carried over",
        bands=FF_BANDS, post=FF_POST, entrance=ff_entrance, corner=ff_corner, infill={'front': 'facade', 'back': 'log', 'rest': 'facade'},
        shapes={'Arched': [lancet(-2.5, 2.5, 3.0, 9.5, 12.0, round_top=True)]},
        glass='night', frame=('log_dark', 0.25, 0.03), inner_frame='snow', sill=('snow', 'snow'), bars='log_dark',
        flowers=dict(box='log', soil='wood_dark', flowers=('snow', 'pine', 'red'), leaf='pine_dark'),
        wall_note="the Lobby front wall's lodge blue with snow courses, logs inside",
        window_note='dark log frames and bars, a snowy sill; the arched one round-headed'),
    'gothic': dict(
        title='Cosmetic_GothicFacade', palette=GOTHIC_PALETTE,
        look='dark slate, pointed windows, red stained-glass trim, small gargoyles on the corners',
        bands=GOTHIC_BANDS, post=GOTHIC_POST, entrance=gothic_entrance, corner=gothic_corner,
        infill={'front': 'slate', 'back': 'wine', 'rest': 'slate'},
        shapes={'TwinSash': [lancet(-3.4, -0.6, 3.0, 10.6, 12.6), lancet(0.6, 3.4, 3.0, 10.6, 12.6)],
                'Arched': [lancet(-2.6, 2.6, 3.0, 10.0, 13.0)], 'Round': [disc(0.0, 7.6, 3.2)],
                'Wide': [lancet(-3.8, -1.6, 3.5, 8.4, 10.2), lancet(-1.1, 1.1, 3.5, 8.4, 10.2),
                         lancet(1.6, 3.8, 3.5, 8.4, 10.2)]},
        glass='night', frame=('stone_light', 0.22, 0.1), inner_frame='stone', inner_w=0.2, sill=('stone', 'stone'), bars=gothic_bars,
        flowers=dict(box='stone', soil='slate_dark', flowers=('ruby', 'wine', 'ruby_light'), leaf='ivy'),
        wall_note='dark slate with a stone coping, wine inside',
        window_note='a stone surround, a red stained-glass trim, stone tracery; the twin a pair of lancets, the round a rose'),
    'neon': dict(
        title='Cosmetic_NeonFacade', palette=NEON_PALETTE,
        look='dark panels with glowing cyan and magenta tubes round the windows',
        bands=NEON_BANDS, post=NEON_POST, entrance=neon_entrance, corner=neon_corner,
        infill={'front': 'panel', 'back': 'ink', 'rest': 'panel'},
        glass='glass', frame=None, inner_frame='steel_dark', sill=('steel', 'steel'), sill_drop=0.35, bars='steel_dark',
        extra=neon_tubes,
        flowers=dict(box='steel', soil='panel_dark', flowers=('magenta',), leaf='panel_edge', part='Glow_Magenta_1'),
        wall_note='dark indigo panels with lighter seams at the sill line, the heads and the top',
        window_note='a glowing tube round each opening (a twin sash cyan and magenta), a steel ledge under it'),
    'candy': dict(
        title='Cosmetic_CandyFacade', palette=CANDY_PALETTE,
        look='pink wafer walls, white icing dripping from the top, striped posts',
        bands=CANDY_BANDS, post=CANDY_POST, entrance=candy_entrance, corner=candy_corner,
        infill={'front': 'wafer', 'back': 'cream', 'rest': 'wafer'},
        shapes={'Arched': [lancet(-2.5, 2.5, 3.0, 9.5, 12.0, round_top=True)]},
        glass='night', frame=('icing', 0.22, 0.04), inner_frame='icing', sill=('choc', 'choc'), bars='icing',
        flowers=dict(box='wafer_dark', soil='choc_dark', flowers=('cherry', 'mint', 'icing'), leaf='stem'),
        wall_extra=lambda openings: drip_row(6.0, 16.25, 'icing'),
        wall_note='pink wafer layers with cream between, a chocolate plinth, white icing along the top with drips',
        window_note='white piped frames and bars, a chocolate sill; the arched one round-headed, gumdrops in the box'),
    'pirate': dict(
        title='Cosmetic_PirateFacade', palette=PIRATE_PALETTE,
        look='weathered ship planks, round porthole windows, rope trim, a lantern on each corner',
        bands=PIRATE_BANDS, post=PIRATE_POST, entrance=pirate_entrance, corner=pirate_corner,
        infill={'front': 'plank_dark', 'back': 'cabin', 'rest': 'plank_dark'},
        shapes={'TwinSash': [disc(-2.2, 7.6, 1.25, n=20), disc(2.2, 7.6, 1.25, n=20)],
                'Arched': [lancet(-2.4, 2.4, 3.0, 9.6, 12.0, round_top=True)], 'Round': [disc(0.0, 7.4, 3.2)]},
        glass='sea', frame=None, inner_frame='brass_dark', sill=(None, 'cabin_dark'),
        bars=pirate_bars, extra=pirate_extra, wall_extra=pirate_joints,
        flowers=dict(box='plank_light', soil='cabin_dark', flowers=('berry', 'herb'), leaf='herb_dark', drop=1.15),
        wall_note='narrow weathered planks in four woods, a dark plank foot and top',
        window_note='rope round every window, brass rings round the portholes; the twin two portholes, the round '
                    'one big one, the arched a round-headed stern window, a crate of herbs under the wide one'),
    'slime': dict(
        title='Cosmetic_SlimeFacade', palette=SLIME_PALETTE, look='green walls with slime dripping off the sills',
        bands=SLIME_BANDS, post=SLIME_POST, entrance=slime_entrance, corner=slime_corner,
        infill={'front': 'slime_wall', 'back': 'mint', 'rest': 'slime_wall'},
        glass='night', frame=('sill_dark', 0.22, 0.03), inner_frame='sill', sill=('sill', 'sill'), bars='sill_dark',
        extra=slime_extra, round_sill=True,
        flowers=dict(box='sill_dark', soil='moss', flowers=('slime', 'slime_dark'), leaf='slime_dark'),
        wall_note='green walls with a pale course over the windows',
        window_note='stone frames and sills, slime pooled on the sill and dripping off it'),
}


# --- The layout round a convex and a concave corner, from the FBXs -------------------------------------

# Owned cells (i along X, j along Z, the street toward -Z): a front row of three with the entrance, a
# second row of five, so the outline has convex corners and a concave one at (36, 12) seen from the street.
LAYOUT = {(0, 0), (1, 0), (2, 0)} | {(i, 1) for i in range(5)}
ENTRANCE_CELLS = ((1, 0), (2, 0))
# Which wall gets which window (cell, outward direction): every type at a corner, some walls plain.
WINDOW_AT = {((0, 0), (0, -1)): 'TwinSash', ((2, 0), (1, 0)): 'Round', ((3, 1), (0, -1)): 'Arched',
             ((4, 1), (0, -1)): 'Wide', ((4, 1), (1, 0)): 'TwinSash', ((0, 0), (-1, 0)): 'Arched',
             ((0, 1), (-1, 0)): 'Round', ((1, 1), (0, 1)): 'Wide', ((3, 1), (0, 1)): 'TwinSash'}
C = Matrix(((-1, 0, 0, 0), (0, 0, 1, 0), (0, 1, 0, 0), (0, 0, 0, 1)))   # Roblox <-> Blender (its own inverse)


def outline_pieces(cells, entrance_cells):
    """The pieces the code would place: [(name, origin (x, z), angle about Y, ends [(x, z)...])]."""
    cell = K.CELL
    out = []
    dirs = {(0, -1): 0, (1, 0): -90, (-1, 0): 90, (0, 1): 180}
    for (i, j) in sorted(cells):
        for (di, dj), ang in dirs.items():
            if (i + di, j + dj) in cells:
                continue
            cx, cz = (i + 0.5) * cell + di * cell / 2, (j + 0.5) * cell + dj * cell / 2
            tx, tz = (abs(dj) * cell / 2, abs(di) * cell / 2)
            ends = [(cx - tx, cz - tz), (cx + tx, cz + tz)]
            if (i, j) in entrance_cells and (di, dj) == (0, -1):
                if (i, j) == entrance_cells[0]:
                    out.append(('Facade_Entrance', (cx + cell / 2, cz), 0, [(cx - cell / 2, cz), (cx + 1.5 * cell, cz)]))
                continue
            w = WINDOW_AT.get(((i, j), (di, dj)))
            out.append((f'Facade_Window_{w}' if w else 'Facade_Wall', (cx, cz), ang, ends))
    vertices = {(x * cell, z * cell) for x in range(-1, 8) for z in range(-1, 5)}
    for vx, vz in sorted(vertices):
        quads = {(sx, sz): (int(vx // cell) + (0 if sx > 0 else -1), int(vz // cell) + (0 if sz > 0 else -1)) in cells
                 for sx in (-1, 1) for sz in (-1, 1)}
        owned = [q for q, o in quads.items() if o]
        if len(owned) == 1:
            d = (-owned[0][0], -owned[0][1])
        elif len(owned) == 3:
            d = next(q for q, o in quads.items() if not o)
        else:
            continue
        ang = {(-1, -1): 0, (-1, 1): 90, (1, -1): -90, (1, 1): 180}[d]
        out.append(('Facade_Corner', (vx, vz), ang, [(vx, vz)], 'convex' if len(owned) == 1 else 'concave'))
    return out


def _place(rb_pos, ang):
    return C @ (Matrix.Translation(Vector(rb_pos)) @ Matrix.Rotation(math.radians(ang), 4, 'Y')) @ C


def load_templates(fbx_dir):
    """Every piece of the set from its FBX, kept out of the render (copies are placed from them)."""
    for ob in list(bpy.data.objects):
        bpy.data.objects.remove(ob)
    templates = {}
    for name in PIECES:
        before = set(bpy.data.objects)
        bpy.context.scene.unit_settings.scale_length = .01
        bpy.ops.import_scene.fbx(filepath=str(fbx_dir / f'{name}.fbx'))
        templates[name] = [o for o in bpy.data.objects if o not in before and o.type == 'MESH']
        for o in templates[name]:
            o.hide_render = True
            o.hide_set(True)
    return templates


def place(templates, name, pos, ang, tag):
    M = _place(pos, ang)
    objs = []
    for t in templates[name]:
        base = t.name.split('.')[0]
        if base in ('Root', 'LOD_Proxy'):
            continue
        ob = bpy.data.objects.new(f'{name}_{base}', t.data)
        ob.matrix_world = M @ t.matrix_world
        ob['part'], ob['group'] = base, tag
        bpy.context.scene.collection.objects.link(ob)
        objs.append(ob)
    return objs


def layout_scene(templates):
    placed = [(entry, place(templates, entry[0], (entry[1][0], 0, entry[1][1]), entry[2], 'layout'))
              for entry in outline_pieces(LAYOUT, ENTRANCE_CELLS)]
    bpy.context.view_layer.update()
    return placed


def _world_tris(objs, parts=None, cells=False):
    out = []
    for ob in objs:
        if parts is not None and ob['part'] not in parts:
            continue
        me = ob.data
        me.calc_loop_triangles()
        mw = ob.matrix_world
        uv = me.uv_layers.active.data if me.uv_layers else None
        for t in me.loop_triangles:
            tri = tuple(mw @ me.vertices[i].co for i in t.vertices)
            if cells:
                c = tuple(int(x * K.ATLAS_N) for x in uv[t.loops[0]].uv) if uv else None
                out.append((tri, c))
            else:
                out.append(tri)
    return out


def _bvh(tris):
    verts, polys = [], []
    for t in tris:
        polys.append((len(verts), len(verts) + 1, len(verts) + 2))
        verts += list(t)
    return BVHTree.FromPolygons(verts, polys, epsilon=0.0) if polys else None


def assembly(placed):
    """Every pair of pieces that meet (at a corner, or end to end): no detail of one runs into a detail
    of the other, and no two of their faces in different colours lie on one another (they flicker;
    one colour on both cannot be seen to)."""
    ends = []
    for k, (entry, objs) in enumerate(placed):
        for e in entry[3]:
            ends.append((k, e))
    pairs = set()
    for a, ea in ends:
        for b, eb in ends:
            if a < b and abs(ea[0] - eb[0]) < 1e-6 and abs(ea[1] - eb[1]) < 1e-6:
                pairs.add((a, b, ea))
    body = {b for bs in BODY.values() for b in bs}
    report = {'pairs': 0, 'convex': 0, 'concave': 0, 'joints': 0, 'pieces': sorted({e[0] for e, _ in placed}),
              'faults': []}
    corners = {k: entry[4] for k, (entry, _) in enumerate(placed) if entry[0] == 'Facade_Corner'}
    for a, b, (vx, vz) in sorted(pairs):
        ea, oa = placed[a]
        eb, ob = placed[b]
        report['pairs'] += 1
        kind = corners.get(a) or corners.get(b) or 'joint'
        report[{'convex': 'convex', 'concave': 'concave', 'joint': 'joints'}[kind]] += 1
        tag = f'{ea[0]} and {eb[0]} at ({vx:g}, {vz:g}) ({kind})'
        da = _bvh(_world_tris(oa, {o['part'] for o in oa} - body))
        db = _bvh(_world_tris(ob, {o['part'] for o in ob} - body))
        if da and db:
            hits = da.overlap(db)
            if hits:
                report['faults'].append(f'{tag}: {len(hits)} detail triangles run into each other')
        v = K.rb2bl((vx, 0, vz))
        # The solids (walls and posts are boxes): a face whose outside lies inside one is never seen.
        solids = []
        for objs in (oa, ob):
            for o in objs:
                if o['part'] in body and o['part'] not in ('ArchLeft', 'ArchRight', 'ArchTop'):
                    cs = [o.matrix_world @ Vector(c) for c in o.bound_box]
                    solids.append(K._bounds(cs))
        near, tags, cols = [], [], []
        for k, objs in ((a, oa), (b, ob)):
            for t, cell in _world_tris(objs, cells=True):
                if (min(p.x for p in t) > v.x + 1.6 or max(p.x for p in t) < v.x - 1.6
                        or min(p.y for p in t) > v.y + 1.6 or max(p.y for p in t) < v.y - 1.6):
                    continue
                n = (t[1] - t[0]).cross(t[2] - t[0])
                if n.length < 1e-9:
                    continue
                p = sum(t, Vector()) / 3 + n.normalized() * 0.005
                if any(all(lo[i] + 1e-6 < p[i] < hi[i] - 1e-6 for i in range(3)) for lo, hi in solids):
                    continue
                near.append(t)
                tags.append(k)
                cols.append(cell)
        zf = [(i, j, ar) for i, j, ar in zfights(near, tags) if cols[i] != cols[j]]
        if zf:
            report['faults'].append(f'{tag}: {len(zf)} coplanar face pairs in two colours between them (they flicker)')
    return report


def review(style, set_dir, placed, templates):
    """The sheet: the layout from the street, the entrance with a 5-stud person, the convex corner,
    the concave corner, and the plain wall and the four windows from outside and from inside;
    each piece from its FBX. Workbench, flat atlas colours."""
    out = K.ROOT / 'blender' / set_dir / 'review'
    _REV['_block']('ground', (-30, -0.4, -40), (100, -0.02, 50), (58, 64, 60))
    _REV['_block']('slab', (0, -0.3, 0), (36, 0, 12), (74, 58, 48))       # a dark floor: an opening reads
    _REV['_block']('slab', (0, -0.3, 12), (60, 0, 24), (74, 58, 48))      # as open through it
    _REV['_person'](Vector((24, 0, 0)), -3.0)
    _REV['_person'](Vector((40.5, 0, 0)), 8.0)
    layout = [o for o in bpy.data.objects if o.type == 'MESH' and not o.hide_get()]
    # The lineup, far off: the plain wall and the four windows in a row, a person in front.
    line = []
    for k, name in enumerate(('Facade_Wall',) + WINDOWS):
        line += place(templates, name, (k * 13.0, 0, 200.0), 0, 'line')
    before = set(bpy.data.objects)
    _REV['_block']('ground', (-8, -0.4, 194), (60, -0.02, 210), (58, 64, 60))
    _REV['_person'](Vector((13 * 2 + 7.5, 0, 0)), 197.5)
    line += [o for o in bpy.data.objects if o not in before]

    def show(objs, on):
        for o in objs:
            o.hide_render = not on
    shots = [('layout', (-0.7, -1.0, 0.75), ((-2, 0, -2), (62, 17, 26)), 1.02),
             ('entrance', (-0.25, -1.0, 0.18), ((8, 0, -5), (40, 17, 1)), 1.0),
             ('convex', (-1.0, -1.0, 0.45), ((29, 0, -3), (40, 17.5, 6)), 1.0),
             ('concave', (-0.9, -1.0, 0.5), ((33, 0, 6), (44, 17.5, 16)), 1.0)]
    paths = []
    show(line, False)
    for name, d, (lo, hi), scale in shots:
        p = out / f'{name}.png'
        _REV['_render'](p, d, (800, 560), target=(Vector(lo), Vector(hi)), scale=scale)
        paths.append(p)
    show(layout, False)
    show(line, True)
    for name, d in (('windows', (0.0, -1.0, 0.12)), ('windows_inside', (0.0, 1.0, 0.25))):
        p = out / f'{name}.png'
        _REV['_render'](p, d, (800, 560), target=(Vector((-7, 0, 196)), Vector((59, 17, 201))), scale=1.02)
        paths.append(p)
    show(layout, True)
    sheet = _compose([[paths[0], paths[1]], [paths[2], paths[3]], [paths[4], paths[5]]], out / 'sheet.png')
    return paths[0], sheet


def _compose(rows, path):
    imgs = [[bpy.data.images.load(str(p)) if p else None for p in row] for row in rows]
    h, w = imgs[0][0].size[1], imgs[0][0].size[0]
    W, H = w * max(len(r) for r in rows), h * len(rows)
    canvas = np.zeros((H, W, 4), np.float32)
    canvas[..., 3] = 1
    for ri, row in enumerate(imgs):
        for ci, img in enumerate(row):
            if img is None:
                continue
            px = np.array(img.pixels[:], np.float32).reshape(img.size[1], img.size[0], 4)
            y0 = H - (ri + 1) * h
            canvas[y0:y0 + px.shape[0], ci * w:ci * w + px.shape[1]] = px
            bpy.data.images.remove(img)
    out = bpy.data.images.new(path.stem, W, H, alpha=False)
    out.pixels.foreach_set(canvas.ravel())
    out.filepath_raw = str(path)
    out.file_format = 'PNG'
    out.save()
    bpy.data.images.remove(out)
    print(f'SHEET {path}', flush=True)
    return path


def _fixup_lights(path):
    """No light on a wall, a window or a corner (one stands on every outline edge): only the entrance's lamp."""
    s = path.read_text(encoding='utf-8')
    s = s.replace('if (spec.lightAll or string.match(pname, "_1$")) and not',
                  'if spec.light > 0 and (spec.lightAll or string.match(pname, "_1$")) and not')
    out, current = [], None
    for line in s.split('\n'):
        m = re.match(r'^\t(Facade_\w+) = \{$', line)
        if m:
            current = m.group(1)
        if current and current != 'Facade_Entrance' and re.match(r'^\t\tlight = \d+,$', line):
            line = '\t\tlight = 0, -- no light: one stands on every outline edge'
        out.append(line)
    path.write_text('\n'.join(out), encoding='utf-8')


def main():
    global _END
    styles = [s for s in STYLES if STYLES_ARG is None or s in STYLES_ARG]
    refused, overview = [], []
    for style in styles:
        st = STYLES[style]
        set_dir = f'facade/{style}'
        K.BUILT.clear()
        K.use_palette(st['palette'])
        K.start_set(set_dir)
        _END = st['post']
        builds = ([('Facade_Wall', lambda: plain_wall(st))]
                  + [(f'Facade_Window_{w}', (lambda w=w: window_piece(st, w))) for w in WINDOW_TYPES]
                  + [('Facade_Entrance', st['entrance']), ('Facade_Corner', st['corner'])])
        bad = False
        for name, fn in builds:
            try:
                fn()
            except K.Refused as e:
                print(str(e), flush=True)
                refused.append(f'{style}/{name}')
                bad = True
        if bad:
            continue
        K.end_set(f"{st['title']}: the facade pieces ({st['look']})",
                  [(['Facade_Wall'] + list(WINDOWS), 2.0, 1.0), (['Facade_Entrance', 'Facade_Corner'], 4.0, 1.0)],
                  sheet=False)
        out = K.ROOT / 'blender' / set_dir
        _fixup_lights(out / 'import_fixup.luau')
        templates = load_templates(out / 'fbx')
        placed = layout_scene(templates)
        rep = assembly(placed)
        val = json.loads((out / 'validation.json').read_text())
        val['assembly'] = {'checked': 'the FBXs laid out as the code would round an L of owned cells (a front row '
                                      'of 3 with the entrance, a second row of 5, every window type at a corner): '
                                      'every pair of pieces that meet, re-imported', **rep}
        val['not_validated'] = val.get('not_validated', [])[:1] + [
            'the attachments exist only in manifest.json until import_fixup.luau makes them',
            'how it looks lit in Studio, and the code placing it (HotelKit.facade)']
        (out / 'validation.json').write_text(json.dumps(val, indent=1))
        print(f'ASSEMBLY {style}: {rep["pairs"]} pairs ({rep["convex"]} convex, {rep["concave"]} concave, '
              f'{rep["joints"]} joints), faults {rep["faults"]}', flush=True)
        if rep['faults']:
            refused.append(f'{style}/assembly')
        if not K.NOPREVIEW:
            overview.append(review(style, set_dir, placed, templates)[0])
    if overview and STYLES_ARG is None:
        rows = [overview[:4], overview[4:] + [None] * (4 - len(overview[4:]))]
        _compose(rows, K.ROOT / 'blender' / 'facade' / 'review' / 'overview.png')
    if refused:
        raise SystemExit(f'REFUSED: {refused}')


main()
