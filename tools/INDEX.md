# tools/ index

What a session reads instead of a whole kit: each kit's purpose, its constants
and its functions with the line they start on (`:n`). Each kit's section is
kept by whoever changes that kit; add your own kit's section, never edit
another's.

## monster_kit.py

The shared kit for every monster (MODELS.md, "Monsters and street NPCs") and
the street NPCs (`Hunter`, `NightBus`, "Hunters and the bus"). A build script
is, per model, its shapes and a call to `finish()`, then `finish_set()` and
`validate()` once for the set (`build_monsters_l1.py` is the pattern). Frame:
Blender -Y is the front, +Z up, +X the monster's left, 1 unit = 1 stud;
Roblox (x, y, z) = Blender (-x, z, y). The bus alone faces Blender -X (Roblox
+X). Headless only; the one preview is a Workbench sheet (`-- norender` skips
it).

### Constants

- `MONSTER_BUDGET` :50 (4,000), `PROXY_BUDGET` :51 (300), `MESH_TRIANGLE_CAP` :52
- `HEIGHT_TOL` :53, 10 % of Species.luau's `look.height`
- `GLOW_WORDS` :56, `EXTRA_PARTS` :59 (`Skin`, `Trim`, `Dark`, `Light`), `MARKERS` :60, `PART_RE` :61, every part name a monster may have
- `BUS_BUDGET`, `BUS_PROXY_BUDGET` :71 (8,000 + 500), `VEHICLE_MARKERS` :72 (`Door`), `ALL_MARKERS` :73, `STREET_PART_RE` :74 (adds `Door`, `Wheel_<n>`)
- `NPCS` :76, the street targets (kind `npc` / `vehicle`, height, Root size, the names they need, the `front` part and `facing`, budgets), from the client blockouts
- `SPECIES` :107, Species.luau's height, colour, eyes and shape per id, read from the source

### Functions

- `start_set(set_dir)` :148 an empty scene writing to `blender/<set_dir>/`
- `begin(sid, set_dir, colours=None)` :161 start a species or a street NPC (`NPCS`); `colours` for the extra parts and glows (sRGB), and the NPC's `Body`
- `rings(part, spec, n, wave, matrix, name, radial)` :209 a closed solid through horizontal rings (the base of every shape)
- `lathe(part, profile, at, n, sy, wave, rot)` :250 revolve [(z, r)]
- `ball(part, at, r, n=12, k=6, rot, name, radial)` :256 an ellipsoid
- `on_ball(at, r, x, z, out)` :265 a point on an ellipsoid's front
- `limb(part, p0, p1, r0, r1, n=10)` :274 a tapered capsule
- `box(part, at, size, bevel, rot)` :286 (a bevel at most half the thinnest side)
- `prism(part, outline, y_front, depth, rot, pivot)` :298 a flat-fronted convex solid (carved eyes, a tiara)
- `arc_shell(part, profile, t0, t1, thick, at, n, sy)` :317 a closed shell over an arc (a cape, a collar)
- `pair(fn, *args, mirror=[...], **kw)` :345 a call and its mirror across x
- `front_y(profile, z, x, at, sy, out)` :364 a point on a lathe's front
- `eyes(at, r, pupil, shine, rr)` :376 `Glow_Eyes_1/2` with a Dark pupil and a Light glint
- `marker(name, at, look=None)` :392 `Nameplate` / `Hand` / `Door` as a 0.2 marker part; `look` the attachment's facing (manifest `markers_look_roblox`)
- `tube(part, pts, r, n=10, closed, up, name)` :407 a swept tube through a polyline (a serpent's coil, a string, a hoop); `closed` + `up` for a flat ring
- `coplanar_overlaps(objs)` :480 lifted from ship_kit; faces of two pieces in one plane, overlapping
- `finish(note='')` :665 the contract checks (per kind: a monster's eyes, Nameplate, Hand; an NPC's `need` names and `front` along `facing`; a vehicle inside and filling its Root, its Door beside the right side), Root, LOD_Proxy, budgets, FBX, the record; refuses a bad model
- `finish_set(set_dir, offsets=4.2, sheet=True, cols=5, place=None, frame=None)` :817 manifest.json, import_settings.luau, the .blend, the sheet; `place` lays out (and repeats) models by hand
- `import_luau(records)` :887 the import step's Luau (PrimaryPart, pivot, markers to attachments with their facing, colours, collision, proxy hidden)
- `validate(set_dir, species)` :1000 re-import each FBX and check it, per kind; writes validation.json

Internal: `_material` :172, `_object` :184, `_matrix` :200, `_tris` :469, `_closed` :542, `_bounds` :552, `_join` :559, `_uv` :582, `_proxy` :595, `_sheet` :967.

## build_monsters_l1.py

Location 1's ten monsters (Haunted Manor), one function per species; output
`blender/monsters/haunted_manor/`. `-- only Slime,Ghost` builds a subset.

## build_monsters_l2.py

Location 2's seven monsters (Frostfang Lodge), one function per species;
output `blender/monsters/frostfang_lodge/`. `-- only Yeti,IceImp` builds a
subset (it rewrites the set's manifest with only those).

## build_street_npcs.py

`Hunter` and `NightBus` on monster_kit's `NPCS` targets; output
`blender/street/npcs/`. The sheet shows the bus twice (door side, face).

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

- `CELL`, `WALL`, `FLOOR`, `T` :53 the grid (12), wall height (17, to the slab), floor (18), wall thickness (0.4): his ruling of 2026-10-19 evening
- `DOOR_W`, `DOOR_H` :54 the door opening's minimum, 4 x 7; `LOBBY_W`, `LOBBY_D` :55 144 x 24
- `TOL` :56 an attachment's tolerance against the blockout (0.1)
- `PERSON`, `PERSON_R` :57 the 5-stud person and the half-width the walk check sweeps
- `BUDGET` :59 triangles per kind (MODELS.md; the lobby 10,000, `Sign` 3,000 a draft), `MESH_CAP` :62, `PROXY_BUDGET` :63
- `GLOW_KEYS` :64, `GLOW_COLOURS` :65 what the fix-up lights each key as
- `PALETTE` :72 the set's flat colours, a third value marks a glow colour; one 256 px atlas of 8 x 8 cells
- `LOBBY_*` :396–422 layout A at the doubled scale: the front wall, the back row, the counter, the key rack, benches, planters, windows (`LOBBY_WIN_LO`/`HI`, 3 to 12), sconces
- `STAIR_*` :597 the stair core: 24 wide, 8 steps up and 7 on, 1.2 rise, 1.5 tread, the landing's z and y
- `RAIL_Y` :671 the picture rail in a room's 17-stud wall

### Functions

- `begin(name, kind, size, root_centre, w, d)` :155 a piece and its Root; kinds `Room`, `Amenity`, `Lobby`, `Stairs`, `Sign`, `Decor`, `Cosmetic`
- `want(name)` :163 false when `-- only A,B` leaves it out
- `attach(name, pos, look=None)` :167 an attachment (Roblox coords, LookVector)
- `declare(part, collide)` :171 whether a part collides (default: all but Root, Dressing*, Glow_*, LOD_Proxy)
- `at(pos, rx, ry, rz)` :235 a transform for `m=`
- `box(part, c, s, col, bevel, m)` :244, `span(part, lo, hi, col, bevel, m)` :267 boxes; `col` a palette name or `{'top'|'bottom'|'front'|'back'|'left'|'right'|'side'|'rest': name}`
- `lathe(part, profile, col, n, base, scale, m, phase, closed)` :273 revolve (r, y); `closed` for rings
- `cyl(...)` :308, `sphere(part, c, radii, col, n, rings)` :312
- `prism(part, pts, a0, a1, col, plane)` :321 any polygon (concave too) extruded; planes `xy`, `xz`, `zy`
- `arch_points(x0, x1, spring, apex, n)` :333 a pointed arch's outline; `round_arch_points` :347
- `door_x(w)` :357, `blockout_attachments(kind, w, d)` :361, `blockout_lobby_walls()` :401, `blockout_room_walls(w, d)` :576, `blockout_stairs(top)` :604 the Luau blockout's numbers
- `lobby_front_wall(...)` :425, `lobby_sconce` :474, `lobby_lamp` :485, `lobby_bench` :496, `lobby_bell` :512, `lobby_till` :520, `lobby_keyrack` :542 the lobby's shared shapes
- `stair_soffits(col)` :630, `stair_handrails(metal, post)` :649 the stair core's dressing
- `room_shell(w, d, paper, wainscot, crown, outside, floor, rug, lamp, lintel, stripes)` :674 floor, the six walls (the blockout's boxes, in bands), the arched lintel, the sconce and `Glow_Warm_1`, every attachment
- `picture(c, size, frame, inner, wall)` :762 a framed picture on a wall's inner face (Dressing)
- `check_piece(piece, boxes, tris, faults)` :815 the contract on boxes; used by finish() and validate()
- `finish(proxy=None, note='')` :1016 glow and attachment checks, check_piece, meshes with atlas UVs, LOD_Proxy, FBX; raises `Refused`
- `start_set(set_dir)` :1125, `end_set(title, layout_rows)` :1138 manifest (merged on `-- only`), .blend, the sheet, validate, import_fixup.luau (lights sized to the piece; the lobby lights every lamp)
- `validate()` :1217 re-import each FBX; names, boxes to 0.02, triangles, UVs, material, atlas, check_piece again; writes validation.json

Internal: `_part` :175, `_side_of` :186, `_colour` :202, `_add` :209, `_bounds` :785, `_overlap` :798, `footprint` :802, `_atlas` :965, `_uv` :1002, `_proxy` :1008, `_sheet` :1178, `_lua_v` :1302, `_fixup_luau` :1306.

## build_hotel_haunted_manor.py

Location 1's hotel kit: 8 rooms, 5 amenities, Lobby, StairCore,
StairCoreTop, HotelSign and 15 `Decor_<Id>`, one function each; output
`blender/hotel/haunted_manor/`. `-- only Lobby,StandardRoom` builds a subset,
`-- nopreview` skips the sheet.

## build_hotel_frostfang_lodge.py

Location 2's hotel kit (Frostfang Lodge): 6 rooms, 2 amenities, Lobby,
StairCore, StairCoreTop, HotelSign and 6 `Decor_<Id>`, one function each;
output `blender/hotel/frostfang_lodge/`. Its own palette (`PALETTE`, through
`K.use_palette`). `-- only Lobby,IglooRoom` builds a subset, `-- nopreview`
skips the sheet.

Lodge helpers: `flake` :63 a six-armed snowflake on a face, `icicle` :81,
`snow_edges` :85 the snow cornice and icicles on every wall top,
`lantern` :105 a wall lantern with its `Glow_Warm_<n>`, `window` :120 a night
pane with a snowy sill, `aurora_ribbon` :143 a wavy band on a wall,
`lodge_shell` :155 room_shell in the lodge's dress (round lintel, facade blue,
lantern), `lodge_bed` :168 (head `log` or `ice`, a plaid quilt), `mug` :208,
`pine_tree` :216.

Added to `hotel_kit.py` for it (2026-10-19, additive; a full Haunted Manor
rebuild after them is byte-identical): `use_palette(entries)` :95 a set's own
atlas palette; `round_arch_points(x0, x1, spring, apex, n)` :339;
`room_shell(..., lintel='pointed'|'round', stripes=7)` :431, where `paper`
may be a tuple of colours laid in horizontal stripes (logs, snow blocks).
The kit's own line numbers above, after :77, now run 17 to 33 lines later.

Added to `hotel_kit.py` for the cosmetics (2026-10-19, additive; both hotel
kits rebuilt after them give byte-identical manifest, validation and fix-up,
and FBXs of the same size): kind `Cosmetic` (`BUDGET` 2,000, a draft; no
part required; nothing may collide); `Piece.checks` :142, a list of
`fn(piece, tris, stage) -> [faults]` that `finish()` (stage `built`) and
`validate()` (stage `fbx`) run on the triangles in Roblox coordinates;
`Piece.allowed`, the (lo, hi) envelope `footprint()` :546 returns when set;
`_tris_rb(ob)` :534. Lines after :138 run about 5 to 25 later than above.

## build_cosmetics_hotel.py

The Sign- and Lobby-slot cosmetics of `Cosmetics.luau` (MODELS.md,
"Cosmetics"), kind `Cosmetic`; output `blender/cosmetics/hotel/`. Loads both
hotel kits' `HotelSign.fbx` and `Lobby.fbx` first and checks every model
against them (`sign_checks`: no triangle over the Board's face, none touching
either sign; `lobby_checks`: lowest point >= 8, inside the arch's 5.5 span, in
front of it, none touching either lobby). Helpers: `rod`, `chain` (a tapered
tube), `ring`, `swag`/`string` (a hung string), `shield_pts`, `bat_pts`,
`flake`, `icicle`. Review renders (Workbench): each cosmetic on both kits.
`-- only A,B`, `-- nopreview`.
