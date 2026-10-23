"""Review sheets of a built set's pieces, one tile each, close up beside the 5-stud person (skill `blind-review`).

The kit's contact sheet shows a whole set from far off; this renders every FBX in a set's fbx/ on its own,
re-imported (what Studio will get, Root and LOD_Proxy left out), from the front three-quarters a little
above, the person standing to its right, and lays the tiles out in a grid. A `Wall` decor piece gets a grey
wall behind it. Workbench, Studio-safe; nothing is written but the sheets.

    blender -b --python-exit-code 1 -P tools/review_pieces.py -- <set dir under blender/> [only A,B] [top]

Writes blender/<set>/review/pieces_sheet.png (`top`: pieces_top.png, straight from above), and the tiles
in review/pieces/.
"""
import ast
import json
import math
import sys
from pathlib import Path

import bpy
import numpy as np
from mathutils import Vector

sys.path.insert(0, str(Path(__file__).resolve().parent))
import hotel_kit as K  # noqa: E402

TOOLS = Path(__file__).resolve().parent
ARGS = K.ARGS
SET_DIR = K.ROOT / 'blender' / ARGS[0]
ONLY = set(ARGS[ARGS.index('only') + 1].split(',')) if 'only' in ARGS else None
TOP = 'top' in ARGS
TILE = (520, 440)
COLS = 5

_NS = {'bpy': bpy, 'K': K, 'Vector': Vector}
for node in ast.parse((TOOLS / 'build_cosmetics_hotel.py').read_text(encoding='utf8')).body:
    if isinstance(node, ast.FunctionDef) and node.name in ('_flat', '_import', '_block', '_person', '_render'):
        exec(compile(ast.Module([node], []), 'build_cosmetics_hotel.py', 'exec'), _NS)


def clear():
    for ob in list(bpy.data.objects):
        if ob.type == 'MESH':
            bpy.data.objects.remove(ob)


def tile(fbx, out, layer):
    clear()
    _NS['_import'](fbx, (0, 0, 0))
    obs = [o for o in bpy.data.objects if o.type == 'MESH']      # what it kept (Root and LOD_Proxy removed)
    pts = [ob.matrix_world @ Vector(c) for ob in obs for c in ob.bound_box]
    lo, hi = K._bounds(pts)
    rb_lo, rb_hi = K.bl2rb(lo), K.bl2rb(hi)
    xmax = max(rb_lo.x, rb_hi.x)
    zs = sorted((rb_lo.z, rb_hi.z))
    if layer == 'Wall':     # the wall the piece hangs on, behind its back
        _NS['_block']('wall', (min(rb_lo.x, rb_hi.x) - 1.5, 0, zs[1]), (xmax + 4.0, 8.0, zs[1] + 0.3), (150, 150, 158))
    _NS['_block']('floor', (min(rb_lo.x, rb_hi.x) - 1.0, -0.1, zs[0] - 1.0), (xmax + 4.0, 0.0, zs[1] + 0.5),
                  (200, 200, 205))
    if not TOP:
        _NS['_person'](Vector((xmax + 2.2, 0, 0)), (zs[0] + zs[1]) / 2)
    d = (0, 0, 1) if TOP else (-0.9, -1.5, 0.85)
    _NS['_render'](out, d, TILE)


def main():
    manifest = json.loads((SET_DIR / 'manifest.json').read_text())
    pieces = manifest['pieces']
    layers = {r['name']: (r.get('decor') or {}).get('layer') for r in (pieces.values() if isinstance(pieces, dict) else pieces)}
    names = sorted(p.stem for p in (SET_DIR / 'fbx').glob('*.fbx'))
    names = [n for n in names if ONLY is None or n in ONLY]
    tiles = []
    for n in names:
        out = SET_DIR / 'review' / 'pieces' / f'{n}{"_top" if TOP else ""}.png'
        tile(SET_DIR / 'fbx' / f'{n}.fbx', out, layers.get(n))
        tiles.append(out)
    rows = [tiles[i:i + COLS] for i in range(0, len(tiles), COLS)]
    imgs = [[bpy.data.images.load(str(p)) for p in row] for row in rows]
    w, h = TILE
    W, H = w * COLS, h * len(rows)
    canvas = np.ones((H, W, 4), np.float32) * 0.16
    canvas[..., 3] = 1
    for ri, row in enumerate(imgs):
        for ci, img in enumerate(row):
            px = np.array(img.pixels[:], np.float32).reshape(img.size[1], img.size[0], 4)
            y0 = H - (ri + 1) * h
            canvas[y0:y0 + px.shape[0], ci * w:ci * w + px.shape[1]] = px
            bpy.data.images.remove(img)
    path = SET_DIR / 'review' / ('pieces_top.png' if TOP else 'pieces_sheet.png')
    img = bpy.data.images.new(path.stem, W, H, alpha=False)
    img.pixels.foreach_set(canvas.ravel())
    img.filepath_raw = str(path)
    img.file_format = 'PNG'
    img.save()
    print(f'SHEET {path}: {", ".join(names)}', flush=True)


main()
