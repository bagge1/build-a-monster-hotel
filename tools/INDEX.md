# tools/ index

What a session reads instead of a whole kit: each kit's purpose, its constants
and its functions with the line they start on (`:n`). Each kit's section is
kept by whoever changes that kit; add your own kit's section, never edit
another's.

## monster_kit.py

The shared kit for every monster (MODELS.md, "Monsters and street NPCs"). A
build script is, per species, its shapes and a call to `finish()`, then
`finish_set()` and `validate()` once for the set (`build_monsters_l1.py` is
the pattern). Frame: Blender -Y is the front, +Z up, +X the monster's left,
1 unit = 1 stud; Roblox (x, y, z) = Blender (-x, z, y). Headless only; the
one preview is a Workbench sheet (`-- norender` skips it).

### Constants

- `MONSTER_BUDGET` :50 (4,000), `PROXY_BUDGET` :51 (300), `MESH_TRIANGLE_CAP` :52
- `HEIGHT_TOL` :53, 10 % of Species.luau's `look.height`
- `GLOW_WORDS` :56, `EXTRA_PARTS` :59 (`Skin`, `Trim`, `Dark`, `Light`), `MARKERS` :60, `PART_RE` :61, every part name a monster may have
- `SPECIES` :84, Species.luau's height, colour, eyes and shape per id, read from the source

### Functions

- `start_set(set_dir)` :119 an empty scene writing to `blender/<set_dir>/`
- `begin(sid, set_dir, colours=None)` :132 start a species; `colours` for the extra parts and glows (sRGB)
- `rings(part, spec, n, wave, matrix, name, radial)` :179 a closed solid through horizontal rings (the base of every shape)
- `lathe(part, profile, at, n, sy, wave, rot)` :220 revolve [(z, r)]
- `ball(part, at, r, n=12, k=6, rot, name, radial)` :226 an ellipsoid
- `on_ball(at, r, x, z, out)` :235 a point on an ellipsoid's front
- `limb(part, p0, p1, r0, r1, n=10)` :244 a tapered capsule
- `box(part, at, size, bevel, rot)` :256
- `prism(part, outline, y_front, depth, rot, pivot)` :268 a flat-fronted convex solid (carved eyes, a tiara)
- `arc_shell(part, profile, t0, t1, thick, at, n, sy)` :287 a closed shell over an arc (a cape, a collar)
- `pair(fn, *args, mirror=[...], **kw)` :315 a call and its mirror across x
- `front_y(profile, z, x, at, sy, out)` :334 a point on a lathe's front
- `eyes(at, r, pupil, shine, rr)` :346 `Glow_Eyes_1/2` with a Dark pupil and a Light glint
- `marker(name, at)` :362 `Nameplate` / `Hand` as a 0.2 marker part
- `coplanar_overlaps(objs)` :385 lifted from ship_kit; faces of two pieces in one plane, overlapping
- `finish(note='')` :569 the contract checks, Root, LOD_Proxy, budgets, FBX, the model's record; refuses a bad model
- `finish_set(set_dir, offsets=4.2, sheet=True)` :680 manifest.json, import_settings.luau, the .blend, the sheet
- `import_luau(records)` :721 the import step's Luau (PrimaryPart, pivot, markers to attachments, colours, collision, proxy hidden)
- `validate(set_dir, species)` :819 re-import each FBX and check it; writes validation.json

Internal: `_material` :142, `_object` :154, `_matrix` :170, `_tris` :374, `_closed` :447, `_bounds` :457, `_join` :464, `_uv` :487, `_proxy` :500, `_sheet` :786.

## build_monsters_l1.py

Location 1's ten monsters (Haunted Manor), one function per species; output
`blender/monsters/haunted_manor/`. `-- only Slime,Ghost` builds a subset.

## hotel_kit.py

The shared kit for every hotel piece (MODELS.md, "Hotel kit"): rooms,
amenities, the lobby, the stair core, the sign, decor. A build script is, per
piece, `begin()` + its shapes + `finish()`, then `end_set()` once
(`build_hotel_haunted_manor.py` is the pattern). Shapes are authored in
**Roblox coordinates** (X right, Y up, door toward -Z, y = 0 where feet stand);
`rb2bl()` makes Blender's (-x, z, y), the same mapping as monster_kit.
`finish()` refuses a piece that breaks the contract; the blockout's numbers
(`src/server/HotelKit.luau`) are ported in `blockout_*()` for the checks.
Attachments travel in `manifest.json` and are made by the generated
`import_fixup.luau`. Headless only; the one preview is a Workbench sheet.

### Constants

- `CELL`, `WALL`, `FLOOR`, `T` :51 the grid (6), wall height (10), floor (12), wall thickness (0.4)
- `DOOR_W`, `DOOR_H` :52 the door opening's minimum, 4 x 7
- `TOL` :54 an attachment's tolerance against the blockout (0.1)
- `PERSON`, `PERSON_R` :55 the 5-stud person and the half-width the walk check sweeps
- `BUDGET` :57 triangles per kind (MODELS.md; `Sign` 3,000 is a draft), `MESH_CAP` :59, `PROXY_BUDGET` :60
- `GLOW_KEYS` :61, `GLOW_COLOURS` :62 what the fix-up lights each key as
- `PALETTE` :69 the set's flat colours, a third value marks a glow colour; one 256 px atlas of 8 x 8 cells

### Functions

- `begin(name, kind, size, root_centre, w, d)` :130 a piece and its Root; kinds `Room`, `Amenity`, `Lobby`, `Stairs`, `Sign`, `Decor`
- `want(name)` :138 false when `-- only A,B` leaves it out
- `attach(name, pos, look=None)` :142 an attachment (Roblox coords, LookVector)
- `declare(part, collide)` :146 whether a part collides (default: all but Root, Dressing*, Glow_*, LOD_Proxy)
- `at(pos, rx, ry, rz)` :210 a transform for `m=`
- `box(part, c, s, col, bevel, m)` :219, `span(part, lo, hi, col, bevel, m)` :242 boxes; `col` a palette name or `{'top'|'bottom'|'front'|'back'|'left'|'right'|'side'|'rest': name}`
- `lathe(part, profile, col, n, base, scale, m, phase, closed)` :248 revolve (r, y); `closed` for rings
- `cyl(...)` :283, `sphere(part, c, radii, col, n, rings)` :287
- `prism(part, pts, a0, a1, col, plane)` :296 any polygon (concave too) extruded; planes `xy`, `xz`, `zy`
- `arch_points(x0, x1, spring, apex, n)` :308 a pointed arch's outline
- `door_x(w)` :324, `blockout_attachments(kind, w, d)` :328, `blockout_room_walls(w, d)` :357, `blockout_stairs(top)` :376 the Luau blockout's numbers
- `room_shell(w, d, paper, wainscot, crown, outside, floor, rug, lamp)` :406 floor, the six walls (the blockout's boxes, in bands), the arched lintel, the sconce and `Glow_Warm_1`, every attachment
- `picture(c, size, frame, inner, wall)` :467 a framed picture on a wall's inner face (Dressing)
- `check_piece(piece, boxes, tris, faults)` :510 the contract on boxes; used by finish() and validate()
- `finish(proxy=None, note='')` :672 glow and attachment checks, check_piece, meshes with atlas UVs, LOD_Proxy, FBX; raises `Refused`
- `start_set(set_dir)` :776, `end_set(title, layout_rows)` :789 manifest (merged on `-- only`), .blend, the sheet, validate, import_fixup.luau
- `validate()` :868 re-import each FBX; names, boxes to 0.02, triangles, UVs, material, atlas, check_piece again; writes validation.json

Internal: `_part` :150, `_side_of` :161, `_colour` :177, `_add` :184, `_bounds` :490, `_overlap` :495, `footprint` :499, `_atlas` :621, `_uv` :658, `_proxy` :664, `_sheet` :829, `_lua_v` :947, `_fixup_luau` :951.

## build_hotel_haunted_manor.py

Location 1's hotel kit: 8 rooms, 5 amenities, Lobby, StairCore,
StairCoreTop, HotelSign and 15 `Decor_<Id>`, one function each; output
`blender/hotel/haunted_manor/`. `-- only Lobby,StandardRoom` builds a subset,
`-- nopreview` skips the sheet.
