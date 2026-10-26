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
- `TREE_BUDGET`, `TREE_PROXY_BUDGET`, `TREE_MAX_PARTS`, `TREE_HEIGHTS`, `SCENERY` :92, a tree's budgets and its targets, registered by `scenery()`
- `SPECIES` :130, Species.luau's height, colour, eyes and shape per id, read from the source

### Functions

- `start_set(set_dir)` :171 an empty scene writing to `blender/<set_dir>/`
- `scenery(sid, height, foot, need, proxy_colour)` :98 register a tree (`Tree_<Name>`, kind `tree`: a column Root, at most six parts, 800 + proxy 100, 22-40 studs; MODELS.md "Street scenery: trees")
- `begin(sid, set_dir, colours=None)` :184 start a species or a street NPC (`NPCS`); `colours` for the extra parts and glows (sRGB), and the NPC's `Body`
- `rings(part, spec, n, wave, matrix, name, radial)` :233 a closed solid through horizontal rings (the base of every shape)
- `lathe(part, profile, at, n, sy, wave, rot)` :274 revolve [(z, r)]
- `ball(part, at, r, n=12, k=6, rot, name, radial)` :280 an ellipsoid
- `on_ball(at, r, x, z, out)` :289 a point on an ellipsoid's front
- `limb(part, p0, p1, r0, r1, n=10)` :298 a tapered capsule
- `box(part, at, size, bevel, rot)` :310 (a bevel at most half the thinnest side)
- `prism(part, outline, y_front, depth, rot, pivot)` :322 a flat-fronted convex solid (carved eyes, a tiara)
- `arc_shell(part, profile, t0, t1, thick, at, n, sy)` :341 a closed shell over an arc (a cape, a collar)
- `pair(fn, *args, mirror=[...], **kw)` :369 a call and its mirror across x
- `front_y(profile, z, x, at, sy, out)` :388 a point on a lathe's front
- `eyes(at, r, pupil, shine, rr)` :400 `Glow_Eyes_1/2` with a Dark pupil and a Light glint
- `marker(name, at, look=None)` :416 `Nameplate` / `Hand` / `Door` as a 0.2 marker part; `look` the attachment's facing (manifest `markers_look_roblox`)
- `tube(part, pts, r, n=10, closed, up, name)` :431 a swept tube through a polyline (a serpent's coil, a string, a hoop); `closed` + `up` for a flat ring
- `coplanar_overlaps(objs)` :504 lifted from ship_kit; faces of two pieces in one plane, overlapping
- `finish(note='')` :689 the contract checks (per kind: a monster's eyes, Nameplate, Hand; an NPC's `need` names and `front` along `facing`; a vehicle inside and filling its Root, its Door beside the right side; a tree's six parts), Root, LOD_Proxy, budgets, FBX, the record; refuses a bad model
- `finish_set(set_dir, offsets=4.2, sheet=True, cols=5, place=None, frame=None)` :849 manifest.json, import_settings.luau, the .blend, the sheet; `place` lays out (and repeats) models by hand
- `import_luau(records)` :919 the import step's Luau (PrimaryPart, pivot, markers to attachments with their facing, colours, collision, proxy hidden)
- `validate(set_dir, species)` :1032 re-import each FBX and check it, per kind; writes validation.json

Internal: `_material` :196, `_object` :208, `_matrix` :224, `_tris` :493, `_closed` :566, `_bounds` :576, `_join` :583, `_uv` :606, `_proxy` :619, `_sheet` :999.

## build_monsters_l1.py

Location 1's ten monsters (Haunted Manor), one function per species; output
`blender/monsters/haunted_manor/`. `-- only Slime,Ghost` builds a subset.

## build_monsters_l2.py

Location 2's seven monsters (Frostfang Lodge), one function per species;
output `blender/monsters/frostfang_lodge/`. `-- only Yeti,IceImp` builds a
subset (it rewrites the set's manifest with only those).

## build_monsters_l3.py

Location 3's ten monsters (Bayou Spa), one function per species; output
`blender/monsters/bayou_spa/`. Adds `rig_shape` to each manifest record (the
armature it takes, LAUNCH.md #6). Renders its own review pictures, not the
kit: `review/silhouettes.png` (grey Workbench) always, and with `-- final` the
finished sheets (`review/final_*.png`, Cycles on the CPU, 4 threads).
Local helpers: `smile()`, `eye()` (one eye at any centre), `recentre_y()`.

## build_street_npcs.py

`Hunter` and `NightBus` on monster_kit's `NPCS` targets; output
`blender/street/npcs/`. The sheet shows the bus twice (door side, face).

## build_street_trees.py

The forest's five trees (`Tree_Crooked`, `Tree_Bare`, `Tree_Hollow`, `Tree_Fir`,
`Tree_SnowFir`) on monster_kit's `scenery()` targets; output
`blender/street/trees/`. `-- grey` writes the silhouette sheet; `-- only
Tree_Fir` builds a subset. Its own `carve()` cuts the hollow with a boolean.

## hotel_kit.py

The shared kit for every hotel piece (MODELS.md, "Hotel kit"): rooms,
amenities, the lobby shell, the front desk, the stair core, the sign, decor.
A build script is, per piece, `begin()` (or `decor()`) + its shapes +
`finish()`, then `end_set()` once (`build_hotel_haunted_manor.py` is the
pattern). Shapes are authored in **Roblox coordinates** (X right, Y up, door
toward -Z, y = 0 where feet stand); `rb2bl()` makes Blender's (-x, z, y), the
same mapping as monster_kit. `finish()` refuses a piece that breaks the
contract; the blockout's numbers (`src/server/HotelKit.luau`) are ported in
`blockout_*()` for the checks. Attachments travel in `manifest.json` and are
made by the generated `import_fixup.luau`. Headless only; the one preview is
a Workbench sheet.

### Constants

- `CELL`, `WALL`, `FLOOR`, `T` :56 the grid (12), wall height (17, to the slab), floor (18), wall thickness (0.4): his ruling of 2026-10-19 evening
- `DOOR_W`, `DOOR_H` :57 the door opening's minimum, 4 x 7; `LOBBY_W`, `LOBBY_D` :58 144 x 24
- `TOL` :59 an attachment's tolerance against the blockout (0.1)
- `PERSON`, `PERSON_R` :60 the 5-stud person and the half-width the walk check sweeps
- `BUDGET` :62 triangles per kind (MODELS.md; the lobby 10,000, `Desk` 3,000, `Sign` 3,000 a draft), `MESH_CAP` :65, `PROXY_BUDGET` :66
- `GLOW_KEYS` :67, `GLOW_COLOURS` :68 what the fix-up lights each key as
- `PALETTE` :75 the set's flat colours, a third value marks a glow colour; one 256 px atlas of 8 x 8 cells
- `LOBBY_*` :405–426 the shell: the front wall (`LOBBY_WALL_*`, `LOBBY_ARCH_X`), `LOBBY_FLOOR_TOP` (0.1), `LOBBY_CLEAR` (nothing collides behind the wall), the arch's place (`LOBBY_ARCH_PARTS`, `_DEPTH`, `_SPAN`), windows (`LOBBY_WIN_LO`/`HI`, 3 to 12), sconces
- `DESK_*` :431–436 the front desk (MODELS.md, "Front desk"): 24 x 12, the counter, its top at 3.8, the key rack's zone, the clear sides (|x| >= 5), the till's x
- `DECOR_*` :575–577 the decor grid: 3-stud squares, the 0.4 inset, 7 tall, a rug 0.15; the layers `Floor`, `Rug`, `Wall`; `DECOR_REFIT_MAX` (0.5); `RUG_BORDER`, `RUG_PIN` :856
- `STAIR_*` :933 the stair core: 24 wide, 8 steps up and 7 on, 1.2 rise, 1.5 tread, the landing's z and y
- `RAIL_Y` :1010 the picture rail in a room's 17-stud wall

### Functions

- `begin(name, kind, size, root_centre, w, d)` :161 a piece and its Root; kinds `Room`, `Amenity`, `Lobby`, `Desk`, `Stairs`, `Sign`, `Decor`, `Cosmetic`
- `want(name)` :170 false when `-- only A,B` leaves it out
- `attach(name, pos, look=None)` :174 an attachment (Roblox coords, LookVector)
- `declare(part, collide)` :178 whether a part collides (default: all but Root, Dressing*, Glow_*, LOD_Proxy)
- `at(pos, rx, ry, rz)` :242 a transform for `m=`
- `box(part, c, s, col, bevel, m)` :251, `span(part, lo, hi, col, bevel, m)` :274 boxes; `col` a palette name or `{'top'|'bottom'|'front'|'back'|'left'|'right'|'side'|'rest': name}`
- `lathe(part, profile, col, n, base, scale, m, phase, closed)` :280 revolve (r, y); `closed` for rings
- `cyl(...)` :315, `sphere(part, c, radii, col, n, rings)` :319
- `prism(part, pts, a0, a1, col, plane)` :328 any polygon (concave too) extruded; planes `xy`, `xz`, `zy`
- `arch_points(x0, x1, spring, apex, n)` :340 a pointed arch's outline; `round_arch_points` :354
- `door_x(w)` :364, `blockout_attachments(kind, w, d)` :368 (rooms: Door, Sign, Bed; the lobby: Entrance, Spawn, SignBoard, Trap_1..3; the desk: Desk, Till, Clerk, Queue_1..4), `blockout_lobby_walls()` :416, `blockout_room_walls(w, d)` :912, `blockout_stairs(top)` :940 the Luau blockout's numbers
- `lobby_front_wall(...)` :440, `lobby_sconce` :489 the lobby shell's shared shapes
- `desk_lamp(metal, shade)` :500 (its bulb `Glow_Warm_1`), `desk_bell(part, x, y, z, metal)` :511, `desk_till(body, keys, drawer, screen)` :519, `desk_keyrack(...)` :544 the front desk's shared shapes, in the desk's frame
- `decor(id_, fw, fd, layer)` :581 begin `Decor_<id_>` on fw x fd 3-stud squares; `decor_bounds(piece)` :590 its envelope; `refit_decor()` :597 fits a pre-grid body (scale down at most 0.5, the least shift, a Wall piece's back onto the wall), recorded in the manifest
- `IMPORT_CHECKS`, `HEIGHT_TOL` :632, `pieces_decor()` :638 the decor table read from `Pieces.luau`: a decor model's w, d, layer and (to 0.3; not an `always` id) height must be its entry's (MODELS.md, "Decor"); a draft set (the silhouettes) sets `IMPORT_CHECKS = False`, which also skips the coplanar check
- `SEAT_Y`, `SEAT_DEPTH`, `SEAT_W`, `SEAT_CLEAR` :656, `seat(x0, x1, z0, z1, y, people, narrow)` :660 a seat (MODELS.md, "Decor", rule 6): top 1.5 to 2.0, 1.2 deep, 2 wide a person (or `narrow` names his ruling), nothing over it for 3; `_seat_check` :687 rays on the built and the re-imported triangles; recorded as `decor.seats`
- `coplanar_shells(objs, wall_z)` :722 faces of two solids in one plane facing the same way and overlapping (they z-fight), unless buried in a third solid, on the floor facing down, or on a Wall piece's wall; lifted from monster_kit; `finish()` refuses decor with any
- `decor_bench(length, frame, cushion, back)` :834 the old lobby bench as `Decor_Bench` (its seat for 3); `rug(kind, border, field, pin, motif, motif_inner)` :859 `runner` (4x2), `corner` (2x2), `square` (4x4) rugs that join edge to edge
- `stair_soffits(col)` :966, `stair_handrails(metal, post)` :985 the stair core's dressing
- `room_shell(w, d, paper, wainscot, crown, outside, floor, rug, lamp, lintel, stripes)` :1013 floor, the six walls (the blockout's boxes, in bands), the arched lintel, the sconce and `Glow_Warm_1`, its own non-colliding `Rug`, every attachment
- `picture(c, size, frame, inner, wall)` :1104 a framed picture on a wall's inner face (Dressing)
- `check_piece(piece, boxes, tris, faults)` :1157 the contract on boxes, per kind (a room's Floor alone; the lobby shell; the desk; the decor layers); used by finish() and validate()
- `finish(proxy=None, note='')` :1400 glow and attachment checks, check_piece, meshes with atlas UVs, LOD_Proxy, FBX, the record (a decor's fw, fd, layer and refit); raises `Refused`
- `start_set(set_dir)` :1521, `end_set(title, layout_rows)` :1534 manifest (merged on `-- only`), .blend, the sheet, validate, import_fixup.luau (lights sized to the piece; the lobby lights every lamp)
- `validate()` :1613 re-import each FBX; names, boxes to 0.02, triangles, UVs, material, atlas, check_piece again; writes validation.json

Internal: `_part` :182, `_side_of` :193, `_colour` :209, `_add` :216, `_bounds` :1127, `_tris_rb` :1132, `_overlap` :1140, `footprint` :1144, `_atlas` :1349, `_uv` :1386, `_proxy` :1392, `_sheet` :1574, `_lua_v` :1712, `_fixup_luau` :1716.

Free building (2026-10-19): the lobby became a shell (its desk, benches,
planters and carpet removed; `Floor` one part), kind `Desk` was added for the
`FrontDesk` (the old desk's shapes re-authored in its frame as `desk_*`), the
decor rules became the 3-stud grid's (`decor`, `refit_decor`, `rug`,
`decor_bench`), a room's rug moved out of its `Floor`, and `Decor_1..3` left
the rooms. Pieces not named there rebuild with identical manifest records.

## build_hotel_haunted_manor.py

Location 1's hotel kit: 8 rooms, 5 amenities, the Lobby shell, FrontDesk,
StairCore, StairCoreTop, HotelSign, RoomPlaque and 30 `Decor_<Id>` (five the old
lobby's: Bench, UrnPlanter, RugRunner, RugCorner, RugSquare; the last ten what
he named, 2026-10-20: GrandfatherClock, WallClock, BlackRoses,
CarnivorousPlant, GhostFern, Armchair, VelvetSofa, Bookshelf, SideTable,
GrandPiano), one function each; output `blender/hotel/haunted_manor/`. `-- only
Lobby,StandardRoom` builds a subset, `-- nopreview` skips the sheet.

Decor helpers (the ten, 2026-10-20): `limb(part, a, b, r0, r1, col, n)` a
tapered rod between two points; `tilt_to(pos, direction)` a transform putting
+Y along a direction; `clock_face(c, r)` a dial on a front face (bezel, face,
hour marks, hands at ten past ten); `GRAND` the grand piano's outline from
above and `_inset(pts, t)` a polygon moved inward (its rim, soundboard, plate).

## build_decor_silhouettes_haunted_manor.py

Haunted Manor's first free-building decor as grey silhouettes for August's
pick (not for import): GrandfatherClock A/B, WallClock, BlackRoses,
CarnivorousPlant, GhostFern, Armchair, VelvetSofa, Bookshelf, SideTable,
GrandPiano A/B, each `K.decor()` to its footprint and layer; output
`blender/hotel/haunted_manor/silhouettes/`. `sheet()` renders
`review/silhouettes.png`: each on its 3-stud squares beside the 5-stud
person, labelled. `-- nopreview` skips the sheet.

## build_hotel_frostfang_lodge.py

Location 2's hotel kit (Frostfang Lodge): 6 rooms, 2 amenities, the Lobby
shell, FrontDesk, StairCore, StairCoreTop, HotelSign, RoomPlaque and 11
`Decor_<Id>` (the last five the old lobby's, ids shared with Haunted Manor),
one function each;
output `blender/hotel/frostfang_lodge/`. Its own palette (`PALETTE`, through
`K.use_palette`). `-- only Lobby,IglooRoom` builds a subset, `-- nopreview`
skips the sheet.

Lodge helpers: `flake` :65 a six-armed snowflake on a face (`stagger=True` keeps its bars out of one plane; only the cocoa mug's so far), `icicle` :81,
`snow_edges` :85 the snow cornice and icicles on every wall top,
`lantern` :105 a wall lantern with its `Glow_Warm_<n>`, `window` :120 a night
pane with a snowy sill, `aurora_ribbon` :143 a wavy band on a wall,
`lodge_shell` :155 room_shell in the lodge's dress (round lintel, facade blue,
lantern), `lodge_bed` :169 (head `log` or `ice`, a plaid quilt), `mug` :209,
`pine_tree` :217.

Added to `hotel_kit.py` for it (2026-10-19, additive; a full Haunted Manor
rebuild after them is byte-identical): `use_palette(entries)` :101 a set's own
atlas palette; `round_arch_points(x0, x1, spring, apex, n)` :353;
`room_shell(..., lintel='pointed'|'round', stripes=7)` :808, where `paper`
may be a tuple of colours laid in horizontal stripes (logs, snow blocks).

Added to `hotel_kit.py` for the cosmetics (2026-10-19, additive; both hotel
kits rebuilt after them give byte-identical manifest, validation and fix-up,
and FBXs of the same size): kind `Cosmetic` (`BUDGET` 2,000, a draft; no
part required; nothing may collide); `Piece.checks` :149, a list of
`fn(piece, tris, stage) -> [faults]` that `finish()` (stage `built`) and
`validate()` (stage `fbx`) run on the triangles in Roblox coordinates;
`Piece.allowed`, the (lo, hi) envelope `footprint()` :939 returns when set;
`_tris_rb(ob)` :927.

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

## build_facades.py

The facade pieces (MODELS.md, "Facade" and its "Where pieces meet"): seven
per style, `Facade_Wall` (plain), `Facade_Window_<Type>` (`TwinSash`,
`Arched`, `Round`, `Wide`), `Facade_Entrance`, `Facade_Corner`, in seven
styles, each its own set `blender/facade/<style>/` (the names repeat):
`haunted_manor`, `frostfang_lodge` (the Lobby front wall and arch carried
over), `bayou_spa` (2026-10-23, a draft: sage clapboard, green
shutters by `bs_shutters`, a round cypress arch) and the five facade cosmetics `gothic`, `neon`, `candy`, `pirate`,
`slime`. On hotel_kit, extended from the script, not in the kit: kind
`Facade` through a wrapped `check_piece` (the kit's generic rules via kind
Cosmetic, then `facade_boxes`), `Piece.checks` += `facade_tris`, glow keys
`Cyan` and `Magenta`, `_fixup_lights` (no light but the entrance's). Runs
one style at a time with `-- styles a,b`; `-- nopreview`.

- The contract: the frame (`OUT_Z`, `IN_Z`, `POST`), `WINDOW_TYPES`,
  `WIN_BOUNDS` (an opening within x -4..4, y 3..13), the entrance's opening
  (`ARCH_X`, `ARCH_Y`, `PIER`), the join rules (`INNER_MAX`, `WEDGE`,
  `INNER_END`, `END_ZONE`, `END_DIP`, `WIN_ZONE`), `BODY` (the colliding
  parts), `BUDGETS`
- Checks: `facade_boxes` (boxes, the opening, `Entrance`), `facade_tris`
  (height, ends and wedge, inside, each window's openings seen along Z with
  `coverage`, the entrance's opening, the corner's quadrant, `zfights`:
  coplanar same-facing overlaps); `assembly()`: the FBXs laid out round an L
  (`LAYOUT`, `WINDOW_AT`, `outline_pieces()`: convex and concave corners,
  joints, every window type at a corner), details running into each other
  (BVH) and faces of two colours lying on each other, into validation.json's
  `assembly`
- Shapes: `wall_body` (bands, holes, the end faces in the post's colour via
  `_END`, the dip), `post`; openings `rect`, `lancet`, `disc` with
  `outline(s, o)` (offset, same points for any o), `infill` (an arch's
  spandrels, a disc's corners), `frame`, `inner_frame`, `glass`, `stained`,
  `sill_under`, `bars`, `flower_box`; `window_piece(st, type)` and
  `plain_wall(st)` dress any style from its `STYLES` entry (bands, post,
  shapes per type, colours, `extra`, `wall_extra`); `tube`, `drip`,
  `drip_row`, `hanging_lantern`, `zm` (the old Lobby arch's z in the facade
  frame), `DIAG` (the corner's outward diagonal), `arch_band`; an entrance
  and a corner function per style
- Lifted without running them (`_lift`, by ast): the Haunted Manor's
  `pumpkin`, the Frostfang `PALETTE`, `icicle`; the cosmetics' review helpers
  `_block`, `_person`, `_render`
- Review: `review()` renders the layout, the entrance with a 5-stud person,
  both corners, and the plain wall and four windows from outside and inside
  into `review/sheet.png`; `blender/facade/review/overview.png`

## run_specs.luau

The pure specs (`tests/*.spec.luau`) under Lune, outside Studio:
`lune run tools/run_specs.luau . [spec ...]`. Resolves `script.Parent.X` and
`Shared.X` to `src/shared/X.luau`, Roblox datatypes from `@lune/roblox`, a
seeded `Random`. `data` needs the engine (Net) and runs only in Studio
(`test_bundle.py`). Lune is global (`rokit add --global lune-org/lune`).

## build_built_rooms.py

Built rooms' art (MODELS.md, "Inner walls, doors and furniture"; his ruling
2026-10-21): per location kit `Wall_Half`, `Wall_Door`, `Wall_Post` and
`Furniture_<Id>` for every Pieces row with `furniture = true` (the Manor also
gets the location-0 rows); output `blender/rooms/<set>/` (`haunted_manor`,
`frostfang_lodge`; `STYLES` holds each set's palette, wall bands, trims and
its furniture table). `-- sets a,b`, `-- only Bed,Wall_Door`, `-- nopreview`.
On hotel_kit, extended from the script: kind `Wall` through a wrapped
`check_piece` (generic rules via kind Cosmetic, then `wall_boxes`), furniture
as kind Decor named `Furniture_<Id>` (Pieces' height a finding in
validation.json `height_findings`, not a fault), `use()`/`stand()` and
`use_check` (the `Use` attachment and its `Pose`), `turned_twin_faults`
(a wall the same turned 180 degrees), `coplanar_faults`, `lintel()` (bands cut
round the arch), `assembly_check` (pieces laid round a room, overlaps outside
the posts), `patch_fixup` (the Pose attribute in import_fixup.luau). Shapes:
`hm_bed`, `ff_bed` (the rooms' beds centred, any width) and one `f_<id>` per
piece. Review: Workbench on light grey, `review_walls`, `review_furniture`.

`build_built_rooms_more.py` (run by it, in its namespace, not on its own):
the 21 pieces by purpose of 2026-10-21 (dining, games, lounge, bathroom,
garden, lobby, spooky) for the Manor: `mfurn()`, `mdecor()` (a `Decor_<Id>`
in this set, `STYLES`' `decor`), `hung_check` (a `Wall` piece may hang on
the wall's plane), `gothic()` and `ellipse()` outlines, `candle()`, and
`review_more` (their sheets in `review/more/`).

## build_hotel_bayou_spa.py

Location 3's hotel kit (Bayou Spa, 2026-10-23, LAUNCH.md workstream 5):
FrontDesk, StairCore, StairCoreTop, HotelSign, RoomPlaque and 10
`Decor_<Id>` (the five of Pieces' location 3, then every kit's five), one
function each, on hotel_kit; output `blender/hotel/bayou_spa/`. No rooms (built
from walls, A.12, in `blender/rooms/bayou_spa/`) and no Lobby (retired into
`Facade_Entrance`). Its palette is the built rooms' `BS_PALETTE` plus the
Locations colours, lifted by `_lift` (ast, without running the script) with
the Bayou shapes `seg`, `firefly_lantern`, `lotus`, `frog`, `lily_pad`,
`cattails`, `boulder`. Helpers: `into(part, fn, ...)` runs a lifted shape
(they draw into `Body`) and moves it into `part`; `tuft` one short light moss
tuft. `-- only A,B`, `-- nopreview`.

## build_vip_lounge.py

The VIP lounge set (GDD A.2, the VIP Lobby pass): five `Decor_Vip<Id>` of
every location, one model for all kits (MODELS.md "Decor"); output
`blender/decor/vip_lounge/`, its own black, gold and velvet palette. Helpers:
`rod`, `stanchion`, `star` (a five-point star on a -Z face), `cupcake`,
`arched` (a panel outline under a shallow round arch), `LETTERS` (the sign's
bulb positions, drawn at -x so they read from the front). `-- only A,B`,
`-- nopreview`.

## review_pieces.py

Review sheets for any set built on hotel_kit: each FBX re-imported alone
(Root and LOD_Proxy left out), from the front three-quarters a little above,
the 5-stud person to its right, a grey wall behind a `Wall` decor piece,
tiled five a row into `review/pieces_sheet.png` (`top`: straight down,
`pieces_top.png`); the tiles in `review/pieces/`. `-- <set dir> [only A,B]
[top]`. The render helpers are build_cosmetics_hotel's, lifted.

## build_activity_bar.py

The Bar's key pieces for Haunted Manor (GDD A.13): `Furniture_BarCounter`
(3 x 1, `Use_1..Use_3` `Stand`) and `Furniture_SmallStage` (2 x 2, `Use_1`
`Dance`); output `blender/rooms/haunted_manor_bar/`. Runs
build_built_rooms.py's definitions (ast, without its main) and adds the
visitors' spots (MODELS.md, "Activity furniture"): `bfurn()` (a piece on its
`PENDING` row while Pieces.luau has none), `spot()`, `stand_spots()`,
`spots_check` (numbering, Pose, squares, Stand's square free, Dance's
figure clear), `sdone()`, `patch_fixup` (each `Use_<n>`'s Pose); shapes
`loft`, `bottle`, `arc`, `apron`, `mic`, `backdrop`. `-- grey` writes the
silhouettes (three a piece) to `silhouettes/`; `-- nopreview`.
