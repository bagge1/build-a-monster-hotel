# Haunted Manor hotel kit (Location 1): first draft

Built 2026-10-19 during the night sprint, by `tools/build_hotel_haunted_manor.py`
on `tools/hotel_kit.py`. **A draft for August's review**: nothing here is
approved, and nothing has been seen in Studio.

**The look, in one line:** cozy-creepy chunky rooms with chamfered edges in one
flat palette atlas: wainscot, coloured paper and a gold crown band on every
wall, plank floors, a pointed-arch doorway, a candle sconce on the back wall,
and one themed bed and piece of furniture per room (a gothic bed, an ivy bed
with pumpkins, a mattress on crates under rafters, a gold sarcophagus, a
witch's bed and potion shelf, a straw nest, a coffin with its lid against the
wall, a crimson-and-gold canopy bed).

Rebuild: `blender -b --python-exit-code 1 -P tools/build_hotel_haunted_manor.py`
(`-- nopreview` skips the sheet, `-- only Lobby,StandardRoom` rebuilds some and
keeps the rest of the manifest). About 30 s, headless, Workbench only.

## What is here

- `fbx/<Name>.fbx`: 39 models, the file name the contract name
  (`ServerStorage.HotelKit.HauntedManor.<Name>`). The atlas is embedded in each.
- `manifest.json`: every piece's Root, every part's box (Roblox studs, piece
  frame), triangles, whether it collides, and **every attachment** (position,
  LookVector).
- `validation.json`: the validator's results per piece, `collision_precise`
  (empty for every piece), and what was not validated.
- `import_fixup.luau`: the import's step 2 (skill `import`), generated from
  the manifest. Attachments do not travel through FBX; this makes them.
- `textures/HotelAtlas.png`: the 256 px palette atlas (8 x 8 flat cells).
- `review/contact_sheet.png`: the one Workbench sheet (decor shown at 2x).
- `haunted_manor.blend`: every piece laid out side by side (the FBXs are at
  their own origins).

| Piece | Kind | Triangles / budget | LOD_Proxy | Parts besides Root |
|---|---|---|---|---|
| `StandardRoom` | Room 2x2 | 3,360 / 6,000 | 108 | the six walls, Floor, Rug, Dressing, Bed, Furniture, Glow_Warm_1..2 |
| `Lobby` | Lobby 144x24 (shell) | 3,604 / 10,000 | 60 | Floor, Wall_FrontLeft, Dressing, Wall_FrontRight, ArchLeft, ArchRight, ArchTop, Glow_Warm_1..7 |
| `FrontDesk` | Desk 2x1 | 2,318 / 3,000 | 36 | Counter, Dressing, Till, KeyRack, Glow_Warm_1 |
| `StairCore` | Stairs | 1,692 / 8,000 | 240 | Step_Up_1..8, Landing, Step_Down_1..7, Wall_Left, Wall_Right, Wall_Back, Divider, Dressing, Glow_Warm_1 |
| `StairCoreTop` | Stairs | 2,228 / 8,000 | 252 | Step_Up_1..8, Landing, Step_Down_1..7, Wall_Left, Wall_Right, Wall_Back, Divider, Rail_Top, Dressing, Glow_Warm_1 |
| `HotelSign` | Sign | 400 / 3,000 (draft ceiling) | none | PostLeft, PostRight, Board, Crest, Glow_Cold_1 |
| `RoomPlaque` | Cosmetic | 160 / 2,000 (draft ceiling) | none | Board, Face |
| `GardenRoom` | Room 2x2 | 3,728 / 6,000 | 108 | the six walls, Floor, Rug, Dressing, Bed, Furniture, Glow_Warm_1 |
| `AtticRoom` | Room 2x2 | 3,432 / 6,000 | 108 | the six walls, Floor, Dressing, Bed, Furniture, Glow_Warm_1 |
| `SarcophagusSuite` | Room 2x3 | 3,200 / 6,000 | 108 | the six walls, Floor, Rug, Dressing, Bed, Furniture, Glow_Warm_1..2 |
| `PotionLoft` | Room 2x3 | 3,960 / 6,000 | 108 | the six walls, Floor, Rug, Dressing, Bed, Furniture, Glow_Warm_1, Glow_Magic_1 |
| `DenRoom` | Room 3x3 | 3,332 / 6,000 | 108 | the six walls, Floor, Rug, Dressing, Bed, Furniture, Glow_Warm_1 |
| `CoffinSuite` | Room 3x3 | 3,288 / 6,000 | 108 | the six walls, Floor, Rug, Dressing, Bed, Furniture, Glow_Warm_1..4 |
| `OperaSuite` | Room 3x3 | 3,956 / 6,000 | 108 | the six walls, Floor, Rug, Dressing, Bed, Furniture, Glow_Warm_1 |
| `SnackBar` | Amenity 2x2 | 3,314 / 6,000 | 96 | the six walls, Floor, Dressing, Centrepiece, Glow_Warm_1 |
| `MusicRoom` | Amenity 2x2 | 2,912 / 6,000 | 96 | the six walls, Floor, Rug, Dressing, Centrepiece, Glow_Warm_1 |
| `GraveyardGarden` | Amenity 2x2 | 3,252 / 6,000 | 96 | the six walls, Floor, Dressing, Centrepiece, Glow_Warm_1..2 |
| `QuietLibrary` | Amenity 2x2 | 4,700 / 6,000 | 96 | the six walls, Floor, Rug, Dressing, Centrepiece, Glow_Warm_1..2 |
| `OrganHall` | Amenity 2x2 | 3,146 / 6,000 | 96 | the six walls, Floor, Rug, Dressing, Centrepiece, Glow_Warm_1..3 |
| `Decor_PuddleRug` | Decor 2x2 Floor | 228 / 1,500 | none | Body |
| `Decor_SnackBasket` | Decor 1x1 Floor | 384 / 1,500 | none | Body |
| `Decor_RecordPlayer` | Decor 1x1 Floor | 336 / 1,500 | none | Body |
| `Decor_Candles` | Decor 1x1 Floor | 312 / 1,500 | none | Body, Glow_Warm_1..3 |
| `Decor_Planter` | Decor 1x1 Floor | 456 / 1,500 | none | Body |
| `Decor_AntiqueWardrobe` | Decor 2x1 Floor | 544 / 1,500 | none | Body |
| `Decor_BlackoutCurtains` | Decor 2x1 Wall | 304 / 1,500 | none | Body |
| `Decor_SandTray` | Decor 2x1 Floor | 354 / 1,500 | none | Body |
| `Decor_CatBasket` | Decor 1x1 Floor | 440 / 1,500 | none | Body |
| `Decor_Cauldron` | Decor 1x1 Floor | 478 / 1,500 | none | Body, Glow_Magic_1 |
| `Decor_SteakPlatter` | Decor 1x1 Floor | 282 / 1,500 | none | Body |
| `Decor_MoonWindow` | Decor 2x1 Wall | 432 / 1,500 | none | Body, Glow_Cold_1 |
| `Decor_PipeOrgan` | Decor 2x2 Wall | 566 / 1,500 | none | Body |
| `Decor_SoundproofWalls` | Decor 2x1 Wall | 972 / 1,500 | none | Body |
| `Decor_Chandelier` | Decor 1x1 Floor | 784 / 1,500 | none | Body, Glow_Warm_1..5 |
| `Decor_Bench` | Decor 3x1 Floor | 628 / 1,500 | none | Body |
| `Decor_UrnPlanter` | Decor 1x1 Floor | 268 / 1,500 | none | Body |
| `Decor_RugRunner` | Decor 4x2 Rug | 156 / 1,500 | none | Body |
| `Decor_RugCorner` | Decor 2x2 Rug | 120 / 1,500 | none | Body |
| `Decor_RugSquare` | Decor 4x4 Rug | 204 / 1,500 | none | Body |

Triangles exclude `Root` and `LOD_Proxy` are counted separately (500 ceiling).

## How each piece is cut (MODELS.md rule 7)

- **Collides:** `Floor`, every `Wall_*`, `Bed` / `Centrepiece`, `Furniture`
  (one compact piece on the right wall), the lobby's `Wall_Front*` and
  `Arch*`, the front desk's `Counter`, `Till` and `KeyRack`, every stair box,
  the sign's posts and `Board`. Each is a compact shape, so `Box` collision is
  its true shape.
- **Does not collide:** `Root`, `Dressing` (pictures, sconces, trims, rafters,
  ivy, awnings: everything on the walls, merged into one mesh), `Glow_*`,
  `LOD_Proxy`, a room's `Rug`, the lobby's `Floor` and the sign's `Crest` (as
  the blockout), and every decor `Body` (a placed piece never traps a player).
- **Walls are exactly the blockout's boxes** (`Wall_Back`, `Wall_Left`,
  `Wall_Right`, `Wall_FrontLeft`, `Wall_FrontRight`, `Wall_Lintel`): the bands,
  chamfers and the door jambs are inside those boxes, and the lintel is a
  pointed arch whose box is the blockout's 4 x 3 x 0.4. The door opening is
  4 wide, 7 tall at the jambs and 8.6 at the arch's point.
- **The stair core's walked boxes are the blockout's, to 0.01 stud** (five
  1.2-stud steps, 1.5 tread, the 4-stud landing, the divider, the walls,
  `Rail_Top`): only colour and 0.06 chamfers are added. Step ends lying in the
  walls' outer faces take the wall's colour, so the coplanar faces cannot show
  a fight.

## Validated (Blender, headless)

`finish()` refuses a piece, and the validator re-checks every piece on its
re-imported FBX, for:

- names: plain ASCII; glows `Glow_<Warm|Cold|Eyes|Magic>_<n>`; the parts the
  kind requires (rooms: Floor, Bed and the six walls; amenities: Centrepiece;
  lobby: Desk, Till; sign: Board and both posts; stairs: every blockout box);
- `Root` the footprint x 0.2 at the blockout's centre, not colliding;
- every attachment the Luau blockout makes, within 0.1 stud of its position and
  with its LookVector (Door, Bed, Sign, Decor_1..3; Entrance, Desk,
  Queue_1..4, Till, Spawn, SignBoard, Trap_1..3; Bottom, Path_1, Path_2, Top);
- nothing outside the footprint (rooms under 10, decor 4 x 4 x 7 at most);
- each wall's box equal to the blockout's; the door opening 4 x 7 with nothing
  colliding in it; a 5-stud person (1.6 wide) walking Door -> Bed in a straight
  line meets nothing colliding; each decor slot's 4 x 4 square free of
  furniture; the lobby's entrance 4 x 7 clear and the walks from inside it to
  Queue_1..4, Spawn and Trap_1..3 clear;
- the Board 16 x 6 x 0.6 at (0, 8, 0), so the SurfaceGui's face is unchanged;
- glow colours only in glow parts, and glow parts only glow colours;
- triangles within MODELS.md's budget per kind, every mesh under 20,000, the
  proxy under 500; closed meshes (no open edges);
- after the FBX round trip: the same part names, every box within 0.02 stud
  (this is what proves the axis conversion and the scale on Blender's side),
  the same triangle counts, one UV layer and one material each, the atlas
  embedded.

## Not validated

- **Nothing has run in Studio.** Not imported, not seen, not walked.
- **Roblox's side of the axis conversion**: the kit uses Sector Omega's export
  (and the monster kit's mapping, Roblox (x, y, z) = Blender (-x, z, y)), but
  `import_fixup.luau` checks every part's position against the manifest
  first and stops, touching nothing, if a set arrives mirrored or turned.
- **The attachments exist only in the manifest** until `import_fixup.luau`
  runs. It also sets PrimaryPart = Root, `Root.PivotOffset` onto the piece
  origin, CanCollide / CanQuery / CanTouch per the manifest, `Box` on every
  mesh, the glows (SurfaceAppearance off, Neon, colour, one PointLight on each
  `_1` glow) and hides `Root` and `LOD_Proxy`. Then the read-back (the
  commented chunk at the end of the file) in a separate call.
- **Walking**: the stair boxes are the walker-proven blockout's, and the room
  checks are box sweeps in Blender; no walker has run on the imported meshes.
- **How it looks lit** in Studio; the atlas upload (one embedded copy per FBX:
  32 identical images, which Studio may or may not deduplicate).
- **A door leaf** (`DoorLeaf`, MODELS.md) is not modelled: the blockout has none
  and the code opens none, and a closed leaf would block every guest. The
  doorways are open arches.
- **The sign's triangle ceiling (3,000)** is the kit's draft; MODELS.md's table
  has no row for a sign.

## Decisions taken without him (reversible, for his review)

- The palette (`hotel_kit.PALETTE`) and every colour pairing per room.
- Each room's theme object and its furniture; each amenity's centrepiece;
  each decor piece's shape (the Chandelier stands on a floor post, since decor
  stands in floor slots at most 7 tall).
- (Superseded 2026-10-19 evening by the lobby rework below.) The lobby kept the blockout's open plan (no walls), with a checkerboard
  floor, a crimson runner, the arch with a jack-o'-lantern and two pumpkin
  planters in the far corners.

## 2026-10-19 afternoon: the sign posts

The cosmetics set found each `HotelSign` post's top ring poking ~0.07 studs out
of the Board's front face, where the sign's text goes. The posts now end under
the Board (5 tall, ring at y 4.6–5.0). Rebuilt; validation passes. The saved
`assets/HotelKit/.../HotelSign.rbxm` is the old one until the next import.

## Imported (2026-10-19, afternoon)

August imported the whole batch (69 FBX, one dialog). The set's import script
ran in the Edit datamodel and was read back in a separate call: no `Default`
collision, no empty mesh, Root and LOD_Proxy hidden on every model. Saved to
`assets/` with `tools/save_imports.py`. **Synced** after August's Rojo
restart (2026-10-19, 15:30): all 69 synced copies match the Workspace imports
part for part (628 parts: mesh ids, sizes, textures, collision, LOD_Proxy
hidden, no empty MeshPart), and the Workspace copies are deleted. **Studio
runtime is not tested yet**: not seen in the game, not walked.

## Blind review 2026-10-19 (the first; skill `blind-review`)

Three playtest pictures of a built hotel (street at eye height, raised
three-quarter, inside the lobby), the reviewer told only what a lobby is for.
Fable, no context, 3 minutes. August had found faults 1, 6 and the patio in
the same pictures; the reviewer was not told them.

| # | The reviewer's finding | Triage |
|---|---|---|
| 1 | The sign stands in the entrance and hides the lobby | **Confirmed**: Sign at z 17, Entrance at z 24, both x 0. His ruling too (`taste.md`). Fix: the lobby rework |
| 2 | The sign is blank from straight ahead; reads as a menu (name and room list) | To verify: why its text did not draw in picture 1 |
| 3 | Floor-2 rooms read as open coloured boxes | Likely false: those are the rooms' solid side walls (rotated pieces); the flat colour is a look, his |
| 4 | The stair's top bay is a black void | To verify: floor 3 has no rooms; lighting in the stair core |
| 5 | A ground-floor room looks empty (no bed) | Likely false: the Sarcophagus Suite's bed is out of the doorway's view |
| 6 | The desk is small, pinched, against the column line, no served side | **Confirmed**: 1.8 studs to the wall (TESTRUN phase 9, rays). His ruling too |
| 7 | Red slivers on edges (balcony ends, low wall tops, roof corner) | To verify: the code's facade trims, or z-fighting |
| 8 | Placeholder street dressing: white chevrons, a pale rectangle, a crate | To verify: the pale rectangle is likely Studio's `SpawnLocation` on the street |
| 9 | No readable roof from a raised view | His call (a look); floor 3 is an empty slab with rails |
| 10 | Seams: a teal line along the wall base, trim edges | To verify, small |
| 11 | Street lamps read as flat glowing discs | His call (a look) |

Not found by the reviewer, found by August: that the lobby as a whole reads as
an outdoor patio (the reviewer called it a "colonnade" without objecting).

## 2026-10-19 evening: the lobby rework (layout A) and the sign's place

**He approved the look, 2026-10-19** (the renders after three blind reviews,
`archive/screens/2026-10-19_lobby_rework.jpg`).

His rulings (`modelling/taste.md`, "A hotel works as a hotel") and his pick of
three grey drafts: **A**, the desk across the end away from the stairs, and
the sign on its posts at the stair-side corner of the forecourt. The contract
is `MODELS.md`, "Lobby"; the shapes every kit shares are in `tools/hotel_kit.py`
(`LOBBY_*`, `lobby_front_wall`, `lobby_bench`, `lobby_bell`, `lobby_till`,
`lobby_keyrack`, `lobby_lamp`, `lobby_sconce`). The `HotelSign` model is unchanged:
only `SignBoard` moved, from (0, 0, −7) to (24, 0, −5).

- The front wall (`Wall_FrontLeft`, `Wall_FrontRight`, exactly the blockout's
  boxes) round the arch, windows at x −20, −11, 11 (none behind the desk's end
  or the sign), candle sconces, a rail at the wainscot.
- The desk x −27 to −25.2, served toward +X, with a bell at the check-in
  prompt, a ledger, the till (an antique register) and a lamp; the `KeyRack`
  with a clock behind the clerk; a carpet from the door along the queue.
- Two benches and two pumpkin planters in the front row on the stair side.
- `finish()` now refuses a lobby whose back row (z 7 to 12) holds anything that
  collides, whose walls are not the blockout's boxes, or where a 5-stud person
  cannot walk from the entrance to each queue spot, trap, the spawn and,
  through the back row, the `Clerk`. All of these pass: 6,818 triangles, 21
  parts, validated by re-import.
- **Not run in Studio.** Waiting for the import (WAITING §0.4); then rays
  through every doorway, a walker to the desk, and a blind review in the game.

### Blind reviews of the renders (2026-10-19, Fable, three rounds)

The pictures were the lobby assembled with the sign, floor-1 rooms and the
stair core, from the street, raised, behind a guest at the desk, from behind
the desk, and close up at the desk. Each round had a new reviewer and new pictures.

| Round, # | The finding | Triage |
|---|---|---|
| 1.1 | Bare window holes in the end walls behind the key rack | **Confirmed**: the code's facade had windows there. Fixed: floor 1's sides are solid along the lobby (`HotelKit.facade`) |
| 1.2 | The sign hides a window | **Confirmed**: no window behind the sign now |
| 1.2b | The sign's feet sit below the facade's base | **False**: both at y 0 |
| 1.3, 2.1, 3.8 | Steps or a block in the room doorways | **False**, proven: the rooms' `Floor` is 0.25 tall, level with the lobby; nothing that collides stands in any doorway (kit door check, TESTRUN phase 9 rays). What shows is the bed's foot, 6 studs in, seen head-on |
| 1.4, 2.2 | The lobby is a corridor; the desk is out of sight from the door | **His call**, already made (layout A, 2 rows). Added a carpet from the door to the desk. WAITING §2 |
| 1.5 | No recognisable waiting area | **Confirmed**: new benches (legs, cushion, rails, arms) |
| 1.6, 2.5 | The arch's pale columns; the facade is a flat slab | **His call** (a look): WAITING §2 |
| 1.7, 2.7 | The bell read as a cone; the thin lamp pole fused with a sconce | **Confirmed**: a domed bell at the prompt, a squat lamp with a wide shade, no sconce over it |
| 1.9, 2.6, 3.5 | Floor patches with hard edges | Ground showing at the threshold and the ends: **confirmed**, the floor now reaches the edges. The light patches are the render's window shadows on the checker floor: **false** |
| 1.10 | The window sill juts over the desk's end | **Confirmed**: no window behind the desk |
| 1.10b | The clock face is blank | **Confirmed**: a clock with hands |
| 2.3 | The far end has no wall of its own | **False**: the code's side wall, as at the desk end; facade pieces are `Facade_Wall`'s, later |
| 2.4 | The sign is a billboard (board 16 × 6) | **His call** (its size is the contract's Board): WAITING §2 |
| 2.8 | The desk is crowded at one end | Bell moved to the check-in prompt |
| 2.9 | Doorway edges show the room's inner colour | **False** for this work: the rooms are unchanged |
| 3.1 | The key rack hangs above head height | **His call**: round 1 found the clerk's head hiding it; the tags now run from 5 to 7.3 studs. WAITING §2 |
| 3.2, 3.6, 3.9 | A detached sill; flakes off line; the guest off centre | **False**: perspective (the sill is in the opening, the flakes at one height, the guest stands at the prompt) |
| 3.3 | The till reads as a modern terminal | **Confirmed**: an antique register with a marquee plate and a crank. Not yet seen by a reviewer: the in-game review covers it |
| 3.4 | The counter items sit at the back edge | **False**: the bell is 0.7 studs from the guest's edge |
| 3.7 | The keys do not read at game distance | Kept: larger tags would clutter. Look at it in the game |

## 2026-10-19 night: the doubled scale

His ruling, 2026-10-19 evening (`CLAUDE.md`, "The scale of a person"): a cell
is 12 studs, a floor 18, every wall reaches the slab above; furniture, doors,
counters, decor and steps keep the 5-stud person's size. The contract was
rewritten first (`MODELS.md`, "Hotel kit"), then the kit, this script and the
Luau blockout (`src/server/HotelKit.luau`) to the same boxes.

- **Rooms and amenities**: 24 × 24 (2×2), 24 × 36, 36 × 36; walls 17 tall in
  bands (wainscot to 3.2, paper, a picture rail at 10.6, paper, a crown under
  the slab); the door jamb's trim stops at the arch's head (8.6). Beds and
  furniture are the first draft's, against the same walls; rugs keep their
  place by the bed (rooms) or at the guest's spot (amenities, now z −D/6); the
  attic's rafters and the potion loft's herbs hang from under the slab; the
  organ's console stands against its pipes. The front wall's outer face (the
  lobby's or a hallway's) carries the room's wainscot, rail and crown round
  the hotel's outside colour.
- **Lobby**: 144 × 24. The front wall 17 tall, up to the slab, with six tall
  windows (6 × 9), a string course over them, a cornice, the inside wainscot
  to the sills, and the wall carried on over the arch (the arch is a door's
  size, 9 × 9). Layout A at the new size: the counter x −63 to −61.2 across
  z 1.5 to 10.5 (3.8 tall, 9 long), the clerk's space and the key rack behind
  it, the queue along z 5, three benches and three planters on the stair
  side, the back row z 12 to 24 clear. 6-stud floor tiles. The entrance
  lantern hangs above the arch's head (its bottom 9.24; the tallest guest is
  7.5). 8,562 triangles: the lobby budget is 10,000 now (`MODELS.md`, four
  times the floor).
- **Stair core**: 24 × 24, 15 steps a storey (8 up to a landing 11.5 deep at
  9.6, 7 on to 18), 1.2 rise, 1.5 tread, flights 12 wide; a handrail on each
  outer wall and a soffit under the flight down (Dressing).
- **The sign and the decor are unchanged** (their manifest records are
  identical); only `SignBoard` moved, to (48, 0, −5).

Validated (Blender, headless): every piece builds through `finish()` and
re-imports clean (32/32), including the lobby's walls, back row, entrance and
the 5-stud walks to every queue spot, trap, the spawn and the clerk; the
cosmetics set still fits both kits' new lobby and sign
(`tools/build_cosmetics_hotel.py`, 7/7). **Not run in Studio.**

### Blind reviews of the renders (2026-10-19 night, Fable, three rounds)

Floor 1 assembled from the FBX at the plot's layout (lobby, sign, four rooms,
the stair core, grey placeholders for the code's facade and slab, a 5-stud
figure at the queue, the clerk's post, the entrance, a door and the stairs):
the street at eye height, the raised camera, the lobby both ways, a room from
its door, the stairs, the desk from the queue. Each round a new reviewer and
new pictures.

| Round, # | The finding | Triage |
|---|---|---|
| 1.1 | The entrance is a full-height slot, a void over the arch | **Confirmed**: the wall went to 17, the arch stayed 9 (11.8 at its apex). Fixed: `ArchTop` carries the wall on to the slab, in the kit and the blockout |
| 1.2, 2.2, 3.4 | The facade reads as a warehouse; blank above the windows; the entrance is small | Blank band: **confirmed**, a string course over the windows and a cornice. Flatness and the entrance's size: **his call**, WAITING §2.13 |
| 1.3, 3.4 | Chrome pillars; posts that carry nothing | **His call**, already put (WAITING §2.11, the pale columns); the shine is Workbench's |
| 1.4, 2.9, 3.3 | The lobby's room-side wall is glossy black, unlike its street wall | Shine: **false**, the preview's specular. The mismatch: **confirmed**, the rooms' front walls show the wainscot, rail and crown outside too |
| 1.5, 2.1, 3.1 | The lobby is a long empty corridor; the desk a speck from the door | **His call**: WAITING §2.13 (144 long now, the desk 60 from the door) |
| 1.6 | The 12-stud checker reads as patchy light | **Confirmed**: 6-stud tiles |
| 1.7 | The runner leaks onto the street | **False**: it starts at z 0.8, inside the wall; `finish()` refuses anything at z < 0 |
| 1.8, 2.6, 3.2 | The room is an empty box | **His call**: WAITING §2.13. The rug far from the bed: **confirmed**, rugs keep their place by the bed |
| 1.9, 2.6 | Door jambs: a fat gold slab beside the door | **Confirmed**: the jamb ran the wall's 17; it stops at the arch's head (8.6) |
| 1.10, 3.8 | Room doorways read as green windows | **False**: the Garden Room's and the Den's own colours seen through their doors |
| 1.11, 2.3, 3.7 | Stairs: no rail, a floating ladder from below | **Confirmed**: a handrail on each outer wall, a soffit under the flight down. The inner side is the divider wall; the "ledge" is the landing's edge under the first step down |
| 1.12, 2.7 | White blocks on the counter | **False**: the avatars' heads and the till's plate (picture 8) |
| 1.13, 2.5, 3.9 | The sign hides a window | **False**, parallax: the board spans x 40 to 56, the windows 33 to 39 and 61 to 67, and it stands 5 in front |
| 1.14 | The lobby has no wainscot, the room has | **Confirmed**: the wainscot to the sills inside |
| 2.4 | The bottom step juts past the stairwell wall | **False**: the step's end lies inside `Wall_Left` (x −12 to −11.6), the step starts at z −11.5 |
| 2.8 | A dotted band over the door (z-fighting) | **Confirmed**: the string course overlapped the infill's face; now separate pieces |
| 2.10 | The entrance lantern clips a tall guest | **Confirmed** (7.74 against the tallest guest's 7.5): it hangs above the arch's head, its bottom at 9.24 |
| 3.5 | Two window types | **False**: all six are 6 × 9; the camera stands 20 off centre |
| 3.6 | The counter is neck-high | **His call** (his approved desk, 3.8): WAITING §2.13 |
| 3.10 | A gold fitting at knee height by the desk | **False** as far as can be found: nothing is mounted there but the wainscot rail, which runs the whole wall |

Not yet seen by a reviewer: the hallway faces' wainscot (round 3's fix). The
in-game review after the import covers it (`TESTRUN.md` phase 11).

### Imported and in the game (2026-10-19 night)

The 27 rescaled models imported, set, saved and synced (27/27 match); a
three-floor hotel of Coffin Suites built from them, walked and rayed
(`TESTRUN.md` phase 11).

**In-game blind review** (Fable; the street, the raised camera, the lobby, a
room's door, the stairs):

| # | The finding | Triage |
|---|---|---|
| 1 | The entrance is a bare cut-out; the lamps flank a window, not the door | Entrance: **his call** (WAITING §2.13). Lamps: **confirmed**, the code laid them every 32 studs blind to the plots; now six to a plot's pitch, a pair flanking each entrance |
| 2 | Upper floors unfinished: open to the sky, a stair in the air, an orange plank stuck through the floor | The plank: **confirmed**, the flight down's handrail rose 3 studs through the upper floor; it now stops under it (17.9). The open top floor: **his call** (no roof; the first review's 9) |
| 3 | The lobby is a tunnel; the desk tiny from the door | **His call**, already put (WAITING §2.13) |
| 4 | The carpet's dog-leg | **False**: the carpet he approved (door to queue), unchanged |
| 5 | The door's posts rise past the arch | **Confirmed**: the jamb trim ran to the arch's apex (8.6); it stops where the arch springs (7) |
| 6 | The Coffin Suite is sparse; the standing coffin reads as a wardrobe | **His call** (WAITING §2.13, the rooms) |
| 7 | A blank wall, an orange hairline, a floating handrail | **False**: the hairline is the facade's sill along the lobby's end; the handrail has four brackets (small at this distance); the landing has no open edge |
| 8 | Window frames orange and trims yellow; windows without glass | **His call** (a look): open windows are the first draft's |
| 9 | Lamps inside the facade line | **False**: 3 studs in front of the plot, perspective |
| 10 | The sign is far from the door | **False**: his ruling (the forecourt's corner) |
| 11 | The steps are too tall | **False**: 1.2 rise, 1.5 tread (the contract), walked |

The handrail and the jambs are rebuilt and re-staged with every room and
both stair cores, imported, saved and synced the same night (25/25); the
stair cores' dressing tops out at 17.85, under the upper floor. The jambs and
the lamps are not yet seen in a playtest.

## 2026-10-19: free building (the lobby shell, the front desk, decor on the 3-stud grid)

His ruling (GDD §5.4): everything in the hotel can be rebuilt, the reception
too. Built to the contract `MODELS.md` was rewritten to the same day ("Lobby
(`Lobby`): the shell", "Front desk", "Decor", "Floor finishes"), and enforced
by `finish()` and the validator (`tools/hotel_kit.py`).

- **`Lobby` is the shell.** The front wall (`Wall_FrontLeft`, `Wall_FrontRight`,
  the blockout's boxes) with its windows, the pointed arch, its lantern
  (`Glow_Warm_1`), the six sconces (`Glow_Warm_2..7`, renumbered), and the plum
  tiled `Floor` (renamed from `Rug`): one part over the whole 144 × 24, y 0 to
  0.1, not colliding, as the blockout's floor (people walk on the plot's slab
  under it). The desk, till, key rack, benches, planters and carpet are gone
  from it. Attachments: `Entrance` (0, 0, 0), `Spawn` (8, 0, 18), `SignBoard`
  (48, 0, −5), `Trap_1..3` (x −16, 16, 48; z 6), all looking −Z; no desk
  points (the code mirrors them from the `FrontDesk`). 3,604 triangles.
- **`FrontDesk`** (new, kind `Desk`, 24 × 12, served toward −Z): the old desk
  re-laid in its own frame. The counter x −4.5..4.5, z −4.0..−2.2, with five
  violet panels and gold rosettes on its served face; its gold top x ±4.7,
  z −4.2..−1.9, **at 3.8**; the bell at (0, 3.8, −3.6) and the ledger beside it,
  the antique till on the +X end (x 2.8..4.0, keys toward the clerk), the
  teal-shaded lamp (`Glow_Warm_1`) on the −X end; bell, ledger and lamp are
  `Dressing`, so the `Counter` box tops out at 3.8. The `KeyRack` with its
  clock: x −2.6..2.6, z 5.15..6.0, 9.5 tall. Attachments `Desk` (0, 3.8, −4.2),
  `Till` (3.4, 3.8, −4.2), `Clerk` (0, 0, 1.5), all looking −Z; `Queue_1..4`
  at (0, 0, −8 / −11 / −14 / −17) looking +Z. 2,318 triangles of 3,000,
  `LOD_Proxy` 36. The shapes are the kit's (`desk_till`, `desk_keyrack`,
  `desk_lamp`, `desk_bell`, re-authored in the desk's frame).
- **The old lobby's furniture as decor** (ids shared with Frostfang Lodge, one
  model per kit): `Decor_Bench` 3x1 Floor (the bench, 7 long, its back toward
  +Z), `Decor_UrnPlanter` 1x1 Floor (the stone urn with a pumpkin), and the
  gold-and-crimson carpet as three rugs (`hotel_kit.rug`): `Decor_RugRunner`
  4x2 (12 × 6, gold borders on ±Z, its ends open), `Decor_RugCorner` 2x2
  (borders on +X and +Z, open on −X and −Z, the inner borders turning in its
  −X −Z corner), `Decor_RugSquare` 4x4 (bordered all round, a medallion).
  Rugs are 0.12 tall and run to their footprint's edges: the border colour
  under all, the field on it, a pin line and diamond motifs a hair proud,
  one motif every 3 studs along a runner, so runners join end to end and a
  corner turns two into an L with the borders and pin lines unbroken
  (close-ups rendered and looked at).
- **Every existing decor refitted to the 3-stud grid** (`refit_decor`: a
  uniform scale down when at most 0.5 too wide, the least shift that brings it
  inside, a Wall piece's back onto z = 3fd/2 − 0.4; nothing else changed;
  each refit is in the manifest's `decor.refit`):

  | Decor | Footprint, layer | Triangles | Refit |
  |---|---|---|---|
  | `Decor_PuddleRug` | 2x2 Floor | 228 | none |
  | `Decor_SnackBasket` | 1x1 Floor | 384 | none |
  | `Decor_RecordPlayer` | 1x1 Floor | 336 | shifted 0.07 toward −Z (its horn) |
  | `Decor_Candles` | 1x1 Floor | 312 | none |
  | `Decor_Planter` | 1x1 Floor | 456 | none |
  | `Decor_AntiqueWardrobe` | 2x1 Floor | 544 | none |
  | `Decor_BlackoutCurtains` | 2x1 Wall | 304 | back onto the wall (+0.65 z) |
  | `Decor_SandTray` | 2x1 Floor | 354 | none |
  | `Decor_CatBasket` | 1x1 Floor | 440 | scale 0.911 |
  | `Decor_Cauldron` | 1x1 Floor | 478 | scale 0.990 |
  | `Decor_SteakPlatter` | 1x1 Floor | 282 | scale 0.917 |
  | `Decor_MoonWindow` | 2x1 Wall | 432 | back onto the wall (+0.65 z) |
  | `Decor_PipeOrgan` | 2x2 Wall | 566 | back onto the wall (+1.35 z) |
  | `Decor_SoundproofWalls` | 2x1 Wall | 972 | back onto the wall (+0.76 z) |
  | `Decor_Chandelier` | 1x1 Floor | 784 | scale 0.870 (its ring was 2.53 across; now 5.8 tall) |
  | `Decor_Bench` | 3x1 Floor | 628 | new |
  | `Decor_UrnPlanter` | 1x1 Floor | 268 | new |
  | `Decor_RugRunner` | 4x2 Rug | 156 | new |
  | `Decor_RugCorner` | 2x2 Rug | 120 | new |
  | `Decor_RugSquare` | 4x4 Rug | 204 | new |

- **Rooms and amenities**: each has exactly one `Floor`, now the walking
  surface alone (y 0..0.2, colliding; `finish()` checks it). The rugs that were
  merged into it are their own `Rug` part, not colliding, so a floor finish
  laid on `Floor` recolours the planks and not the rug: `StandardRoom`,
  `GardenRoom`, `SarcophagusSuite`, `PotionLoft`, `DenRoom`, `CoffinSuite`,
  `OperaSuite`, `MusicRoom`, `QuietLibrary`, `OrganHall`. Their furniture
  stays in `Bed` / `Furniture` / `Centrepiece`. `Decor_1..3` are gone from
  every room and amenity (and their slot check from the kit): `AtticRoom`,
  `SnackBar` and `GraveyardGarden` differ from HEAD only by those
  attachments, their geometry identical, so they are not re-staged.
- `StairCore`, `StairCoreTop`, `HotelSign` and `RoomPlaque` are unchanged
  (their manifest records are identical to HEAD's).

**Validated** (Blender, headless): 39/39 pieces through `finish()` and
re-imported: the shell's rules (the front wall = the blockout's boxes, the
entrance 4 × 7 clear, `Floor` one part over 144 × 24 with its top at most 0.1,
nothing colliding behind the front wall from z 0.8 to 24 and y 0.15 to 17, no
desk points on the lobby); the desk's (Root 24 × 0.2 × 12, nothing outside it,
the `Counter`'s top at 3.8, `Desk` and `Till` on its served edge, nothing
colliding in x −12..−5 or 5..12 up to y 7, `KeyRack` inside its zone, a 5-stud
person walking to the `Clerk` from both side edges and from `Queue_1` to the
counter, `Glow_Warm_1`, 3,000 triangles); each decor inside its layer's
envelope. The cosmetics set still passes against the new shell (7/7,
`tools/build_cosmetics_hotel.py`). **Studio runtime is not tested**: nothing
here is imported, placed, walked or lit; how the code stands decor on a
`Floor`'s top, turns it, and mirrors the desk's points onto the lobby is not
seen.

**One contract number held differently:** the arch stands 0.2 proud of the
front wall's inner face (to z 1.0), as approved and as the cosmetics are
fitted to it. The clear-floor check counts `ArchLeft`, `ArchRight` and
`ArchTop` as the front wall and holds them to |x| ≤ 6, z ≤ 1.0 (Frostfang's
snow cap overhangs the pillars to 5.9).

**Staged** in the main checkout's `blender/_import/` (52 FBX with
Frostfang's): this set's `Lobby`, `FrontDesk`, the 20 decor and the ten rooms
and amenities with a `Rug` part.

### Blind review 2026-10-19 (free building; Fable, one round)

Five pictures in `review/blind/free_building/` (not in git): both kits' lobby
with a `FrontDesk`, a runner, a square rug, a bench and two urn planters
placed, from just inside the entrance, from behind the desk, and raised over
the whole lobby; the lodge's rug pieces joined into an L with the bench and
planter; a close-up of where two runners meet the corner.

| # | The reviewer's finding | Triage |
|---|---|---|
| 1 | The queue spot is not at the bell; in the lodge the guest stands at the arch | **False**: `Queue_1` is (0, 0, −8), straight in front of the bell at x 0 (picture 1 looks from 8 studs to the left); the figure at the arch is a player coming in |
| 2 | The till reads as a birdhouse from the guest's side | **His call** (a look): its keys face the clerk by his report (2026-10-19); the guests see its marquee plate. Recommendation: keep |
| 3 | The key rack stands a full cell behind the counter | **False** against the contract: the clerk's space (z −1.9 to 5.15) is `MODELS.md`'s, the approved desk's sizes (the rack stood 8 behind the counter there too) |
| 4 | The figures' heads are white boxes with a slot | **False**: the render's stand-in person (the slot marks its facing), not a game model |
| 5 | The manor's bell is gold on a gold top | **His call** (a look, the approved desk's colours). Recommendation: keep; the check-in prompt marks the spot |
| 6 | The floor checker is a cell per square, reads as the grid | Size: **false** (6-stud tiles, half a cell, chosen in an earlier review over 12). The look: **his call**, and the floor finish he picks replaces it |
| 7 | The lodge's window sill is above head height | **False**: both kits' windows are the kit's 6 × 9 at y 3 to 12; the sill at 3, under a 5-stud person's shoulder |
| 8 | The manor is murky; the desk a dark slab | **False** for this work: the approved desk's palette, unchanged; the dark is the preview's light |
| 9 | A notch where the lodge's runner meets the corner | **False**: the close-up shows the borders and pin lines unbroken; the corner's inner border square (−3 to −2.5) meets the runner's border (−3 to −2.5) exactly |
| 10 | The key tags do not read | Kept, as decided in the lobby rework (round 3.7: larger tags would clutter) |

Not judged by the reviewer: the counter's height (3.8, the contract's and his
approved desk's; already his call, WAITING §2.13); whether the clerk passes
round both ends (proven: the kit walks a 5-stud person from both side edges
to the `Clerk`); the arch's size (unchanged); the runner's open ends (by
design, so runners join).

### Imported (2026-10-19 evening)

August imported the staged batch (57 FBX with Frostfang's and the trees);
this set's 32 (`Lobby`, `FrontDesk`, the 20 decor, the ten rooms and
amenities with a `Rug` part) were fixed up by `import_fixup.luau` (every part
where the manifest says, no model stopped) and read back in a separate call:
219 meshes, all `Box`, no `Precise`, no `Default` left, Root hidden, the
attachments the manifest names, `LOD_Proxy` hidden on the 12 that have one
(decor has none). Saved over and beside `assets/HotelKit/HauntedManor/` with
`tools/save_imports.py` before Frostfang's prints of the shared names. The
live-synced copies under `ServerStorage.HotelKit.HauntedManor` match the
imports 32/32 (mesh ids, sizes, textures, collision, attachments; no empty
MeshPart), but **31 arrived with `PrimaryPart` nil** (all but the new
`FrontDesk`; `DEVNOTES.md`, "Rojo's live sync drops `PrimaryPart`"): the
files have it (a `rojo build` to XML shows `Root` on all 39), and `HotelKit`
sets it on every clone. Workspace copies deleted. **Studio runtime is not
tested**: the shell, the desk and the decor are not yet placed, walked or lit.

## 2026-10-20: the ten decor pieces he named (WAITING §2.24)

His picks from the grey silhouettes (`silhouettes/README.md`,
`archive/screens/2026-10-19_decor_silhouettes.jpg`): the **longcase** clock
(A), the **grand** piano (A), the **Armchair kept at 1 × 1**, and the tags and
prices GDD A.2 proposed. Each keeps its silhouette's frame, footprint and
outline; detail, colour and glows are added here.

**The contract first** (`MODELS.md`, "Decor", 2026-10-20), enforced by the kit
(`tools/hotel_kit.py`) in `finish()` and again in `validate()` on the
re-imported FBX:

- **The model agrees with `Pieces.luau`**: footprint and layer equal to the
  entry's `w`, `d`, `layer`; its `height` the body's top to 0.3 (the build
  mode's ghost is drawn from it). Proving it on both kits found seven stand-in
  heights off by up to 0.6 (Candles, CatBasket, Cauldron, SteakPlatter,
  Chandelier; Frostfang's IceBlock, CocoaMug): `Pieces.luau` now says the
  models' heights. The ids every kit shares (`always`: Bench, UrnPlanter, the
  rugs) are held to footprint and layer only.
- **Seats** (rule 6): `seat()` declares each; top 1.5 to 2.0, at least 1.2
  deep, 2 wide a person, nothing over it for 3 studs, checked by rays on the
  triangles. Declared: the Armchair (1.6 wide, his ruling named), the Velvet
  Sofa (two seats, one a cushion, 2.08 each), the Grand Piano's bench (2.0 × 1.2), and the old
  `Decor_Bench` in both kits (three, 6.1 wide; only its manifest record
  changed).
- **Proof**: both kits rebuilt in full (49/49 and 25/25 through `finish()` and
  re-imported); every earlier piece's manifest record identical to HEAD but
  the Bench's added seat.

| Decor | Footprint, layer | What it is | Top | Triangles |
|---|---|---|---|---|
| `Decor_GrandfatherClock` | 1x1 Floor | his A: a longcase in dark wood, bracket feet, a panelled plinth, the trunk door's pointed glass window with the brass pendulum, gilt hood columns, the dial (gold bezel, bone face, hour marks, hands at ten past ten) under a moon arch with a crescent, a round pediment with three gilt finials | 6.95 | 1,422 |
| `Decor_WallClock` | 1x1 Wall | a round dark-wood case with the same dial over a pendulum box with a pointed glass window and a brass bob, a drop finial below, a gilt finial on top; hung from 2.9 to 7.0, its back on the wall | 6.98 | 694 |
| `Decor_BlackRoses` | 1x1 Floor | seven black roses with red hearts and three leaves in a teal vase with a gold band, on a slim turned plum pedestal | 4.78 | 1,164 |
| `Decor_CarnivorousPlant` | 1x1 Floor | a flytrap in a stone pot with a teal band: a thick curved stalk, two lobes gaping toward the front (dark green outside, wine-red inside, nine straw-coloured cilia each), a small closed trap on a side stalk, leaves over the rim | 3.58 | 788 |
| `Decor_GhostFern` | 1x1 Floor | a pale teal fern in a plum pot on a sturdy three-legged stand: eight fronds, each one blade with its edges folded down and pinched to a third at every other station (the pinnae) along a jade rib, arching out and down | 3.31 | 1,474 |
| `Decor_Armchair` | 1x1 Floor | his ruling 1 × 1: a wingback, crimson-dark frame, crimson cushion and inner back with five tufting buttons, rolled arms, wings, a round-topped back, turned legs; the seat 1.6 wide at 1.72 | 5.00 | 788 |
| `Decor_VelvetSofa` | 2x1 Floor | a camelback for two: plum frame, two violet cushions (a seat each) and a violet inner back with eight buttons, rolled arms, turned legs; the seats at 1.68 | 3.90 | 932 |
| `Decor_Bookshelf` | 2x1 Wall | a gothic bookcase: two bays under pointed arches, a plum back, four shelves of books in the set's colours (two leaning, a flat stack), a skull bookend, a teal potion bottle, a cornice with a gilt finial; its back on the wall | 6.98 | 1,284 |
| `Decor_SideTable` | 1x1 Floor | a round pedestal table on three curved feet, a brass lantern (dish, candlestick, four ribs, cap) round a cream candle whose flame is `Glow_Warm_1`, a wine-red book | 4.00 | 1,018 |
| `Decor_GrandPiano` | 2x2 Floor | his A: a black baby grand, keyboard toward −Z, its spine on the player's left, the lid propped on a stick over a gold plate on a pale soundboard, five octaves of black keys, a low music desk with a sheet, three turned legs with brass castors, the pedal lyre, and its bench with a crimson cushion | 5.14 | 1,396 |

All are `Root` + `Body` (the side table also `Glow_Warm_1`); nothing collides;
no `LOD_Proxy` (decor has none). Nothing moves: the pendulums and hands are
part of `Body` (MODELS.md rule 2 would split them the day code swings them).
Helpers in the build script: `limb`, `tilt_to`, `clock_face`, `GRAND`, `_inset`.

**Renders** (`review/decor/`, not in git; Cycles, the 5-stud figure beside
each, seated in the armchair and on the sofa): `1_row_a_front`,
`2_row_b_front`, `3_build_camera` (the build camera's ~51° from the front),
`4_seats`, `5_clock_close`, `6_piano_close`, `7_plants_close`. Rendered by a
scratch script, not kept.

**Iterations before the review** (Claude's own look): the piano's treble cheek
rendered as a black patch (smoothing across a thin bevelled block; with
backface culling it is solid, no flipped face): its bevel removed. The Ghost
Fern read first as loose chips, then as tentacles: each frond is now one lobed
blade, wider and lower.

**A seated person at the piano** does not fit under its keys: the blocky
avatar's thighs reach 0.9 above the bench, past the key bed (1.8). Kept at a
real piano's proportions to the standing person (keys at 2.48, half his
height); no code seats anyone at it.

### Blind review 2026-10-20 (the ten; Fable, round 1)

Seven pictures in `review/decor/` (the two rows from the front with the
standing figure, the build camera, the seats with sitters, the clock, the
piano and the plants close). Triage:

| # | The reviewer's finding | Triage |
|---|---|---|
| 1 | The Armchair cannot seat the avatar: the body is narrower than torso and arms; seated, the arms pass through the armrests | **His ruling** (2026-10-20, "keep 1×1", after WAITING §2.24 told him the seat is 1.44 against a 2-wide person): kept; the arms slimmed so the seat is 1.6 |
| 2 | The sofa's end clips a seated arm; three cushions for one sitter | **False**: the contract's seat is 2 wide a person, and the sofa seats two on 4.16; a Roblox avatar's arms (4 wide with the torso) pass through any armrest of a real sofa's proportion. Three cushions are the camelback's look, as on the silhouette he saw |
| 3 | The piano's pedal lyre is white | **False**: a crop shows the lyre black; the pale is the floor tile between its posts |
| 4 | The piano is toy-scaled; the bench jammed under the keys, a sitter's legs inside the piano | Scale: **false** by proportion (keyboard 3.28 wide, 82 % of the figure's 4-stud span; a real one is about 70 % of a person's). The sitter: **his call**, WAITING §2.24: the blocky avatar's thighs (0.9 thick) do not fit under a key bed at a real piano's height |
| 5 | The flytrap reads as Mario's Piranha Plant (red-white jaws, green stalk, orange pot) | **Confirmed** (taste: check against famous designs) and fixed: a stone pot with a teal band, dark green lobes, wine-red inside, green cilia instead of white teeth |
| 6 | The fern is thin, a spider plant; its stand's legs vanish from the build camera | **Confirmed**, fixed: legs 0.11 thick (from 0.07), blades 20 % wider |
| 7 | The side table and the roses are twins from above (dark round top on a dark pedestal) | **Confirmed**, fixed: the roses stand on a pale stone pedestal |
| 8 | The clock's bob touches the window's foot; the moon is a dot | **Confirmed**, fixed: the bob raised 0.28 (its foot 0.41 above the window's); the moon a crescent |
| 9 | The wall clock is twice life size | **His call**, WAITING §2.24 (the silhouette's size; readable on a phone) |
| 10 | The bookcase looks under 1 stud deep | **False**: the case is 1.4 deep (z −0.3 to the wall at 1.1), the cornice 1.55 |
| 11 | The sofa's crest is too small to read | **False** as a fault: a carved crest at the camelback's hump, a detail for close view, not a bat |

Could not judge: whether the tiles are 3 studs and the wall pieces touch
their wall: both proven by the validator (Root 3fw × 0.2 × 3fd; a Wall
piece's back at z = 3fd/2 − 0.4 to 0.05). Added for round 2: both sofa seats
taken, and a straight-down orthographic view (`8_top_ortho`).

### Blind review 2026-10-20 (round 2, a new reviewer on new pictures)

| # | The reviewer's finding | Triage |
|---|---|---|
| 1 | The seats do not fit the avatar: arms through the armchair's armrests; two sitters on the sofa overlap | Armchair: **his ruling** (1 × 1). The sofa: the contract's seat is 2 wide a person (the torso); with its arms the avatar is 4. **His call**, WAITING §2.24 |
| 2 | A black hole in the sofa's back between the two heads | **False**: the two stand-in sitters' boxes overlap there (an arm of each inside the other's chest) and Cycles renders the shared faces black; the sofa is closed (the validator) and whole in every view without sitters |
| 3 | Three cushions for a sofa that seats two | **False** (as round 1) |
| 4 | A flat black box under the piano's key bed; the pedals on the floor | The box: **confirmed**: the cheek blocks' sides and bottoms lay in the key bed's planes (it would flicker in Roblox). Fixed (the cheeks 0.03 proud at the sides, 0.05 lower), and **the kit now refuses it** (below). The pedals: **false** (a lyre's pedals are a hand above the floor; these 0.08 to 0.12) |
| 5 | From the build camera the roses are a smudge, the wall clock's face a dot, the flytrap's teeth the lids' green | Roses: **confirmed**, fixed (red hearts, not dark red). Teeth: **confirmed**, fixed (straw). The wall clock: **false** (a 1.4-wide dial seen from the whole-plot camera; the zoom brings it close) |
| 6 | The armchair's armrests nearly flush with the seat | **False**: 0.53 to 0.7 above the cushion, a real armchair's 20 cm |
| 7 | A leaning book pokes out of the bookcase | **False**: both leaning books measured inside their bays (x −1.15..−0.47 and 1.30..1.82) and under the shelf above |
| 8 | The moon arch reads as a sticker; the clock is as deep as it is wide | **False** as faults: a longcase's moon dial is painted in its arch; the depth (1.6 of 2.08) is the silhouette he picked |
| 9 | The rose pedestal reads as a birdbath, and is the wall stand-ins' colour | **Confirmed**, fixed: a slim plum pedestal, its top 1.12 across (from 1.56) |
| 10 | The flytrap's open-jaw pose is still the Piranha Plant's | **False**: the open jaws are what a flytrap is; the colours that made it Mario's (red head, white teeth, orange pot) are gone |

**A rule the kit now enforces: no coplanar faces** (`MODELS.md`, "Decor").
`coplanar_shells()` in `tools/hotel_kit.py`, lifted from the monster kit, runs
in `finish()` on every decor piece: two solids' faces in one plane, facing the
same way and overlapping, refuse the piece, unless the pair is buried in a
third solid, lies on the floor facing down, or lies on a Wall piece's wall
face. It found, besides the piano's cheeks: the two clocks' hands (now 0.012
apart), the grandfather clock's crescent on its bezel's face, the wall
clock's case front on its pendulum box's, the piano's cover over the action
on its rim, and in four pieces already in the game: `Decor_SandTray` (the
rake's two bars), `Decor_Cauldron` (the three logs, now 0.006 apart in
radius), `Decor_MoonWindow` (the mullion and transom) and `Decor_Chandelier`
(its three feet and the spokes' boxes), each fixed by a hair with no change of
look, and in Frostfang's `Decor_CocoaMug` (the snowflake's bars, now
staggered by `flake(..., stagger=True)`). **Those five need a new import.**
Not checked: rooms, amenities, the lobby, the desk, the stairs and the sign
(the check is decor's only); the lodge's other snowflakes share the same
crossed bars.

### Blind review 2026-10-20 (round 3, a new reviewer on new pictures)

| # | The reviewer's finding | Triage |
|---|---|---|
| 1 | A sitter clips the armchair's arms | **His ruling** (1 × 1), as before |
| 2 | The armchair is as tall as a standing avatar (5.0); a sitter's head hides in its hood | **His call**, WAITING §2.24 (the silhouette he picked) |
| 3 | The flytrap's leaves pass through the pot wall below the rim | **Confirmed**, fixed: fanned out over the soil and the rim |
| 4 | The flytrap still reads as the Piranha Plant | **His call**, WAITING §2.24 (twice now; Claude's reading: false, see round 2) |
| 5 | The black roses read red | **His call**, WAITING §2.24 (round 2 found them a smudge; red hearts were that fix) |
| 6 | The fern reads as an agave or spider plant | **Confirmed**, fixed: each blade pinched nearly to its rib at every other station of 17 (the pinnae), the upright frond arched, the bud removed |
| 7 | The piano's lyre and pedals lie on the floor | **Confirmed** (raised twice now), fixed: the lyre's foot 0.22 up, the pedals at 0.26 to 0.3 |
| 8 | The clock's crescent is cut by the dial's bezel | **Confirmed**, fixed: the dial 0.05 lower, the crescent clear above it |
| 9 | Three cushions on a sofa that seats two | **Confirmed** (raised twice), fixed: two cushions, a seat each |
| 10 | The sitters' hips look high | **False**: the stand-in's boxes; the seats measure 1.68 to 1.75 |
| 11 | The wall pieces take a whole tile | **False** against the contract: a Wall piece's footprint is its squares (`MODELS.md`, "Decor") |
| 12 | Small details vanish from the build camera | **False** as a fault: the whole-plot zoom; they read at the zooms a player decorates at |

### Blind review 2026-10-20 (round 4, a new reviewer on new pictures)

| # | The reviewer's finding | Triage |
|---|---|---|
| 1 | The fern's fronds are broken shards, pieces seemingly detached | **Confirmed** (the pinches at 0.15 read as gaps), fixed: pinched to a third, a jade rib along each frond |
| 2 | No knee room at the piano | **His call**, already in WAITING §2.24 |
| 3 | The armchair narrower than a torso; two sitters bury the sofa's arms | **His ruling** / **his call**, already in WAITING §2.24 |
| 4 | The flytrap reads as the Piranha Plant | **His call**, already in WAITING §2.24 |
| 5 | The seat heights disagree (1.2, 1.3, 1.7 by eye) | **False**: measured 1.72, 1.75 and 1.68 (the kit's seat check) |
| 6 | The fern's and the side table's legs are hairlines from the build camera | **False** as a fault: the whole-plot zoom; the fern's legs are 0.22 thick since round 2 |
| 7 | The roses are maroon, like the armchair | **His call**, already in WAITING §2.24 |
| 8 | A teal zigzag on the fern's pot | **False**: a frond hanging in front of the pot |
| 9 | From above, the armchair's hood hides its seat | Part of the armchair's height, **his call** |
| 10 | A speck on the piano's lid | **Confirmed**: the music desk's corner came through the lid near the hinge. Fixed: the desk 2.0 wide and 0.5 tall (from 2.3 and 0.64); a crop shows the lid clean. The stick's end also kept 0.1 under the lid |
| 11 | The sofa's crest reads as dirt from above | **Confirmed** (the third reviewer to name it), removed: the hump is the back's own shape |

Not judged and settled by measurement: the bookcase stands on y 0 and its
back lies on the wall (the validator: a Wall piece's back at z = 1.1 to 0.05);
the backs of the clocks and the bookcase are closed solids (no open edges),
plain wood.

**Round 4's fixes were not shown to a fifth reviewer**: checked in Claude's own
renders only (the fern, the piano's lid, the sofa).

### Validated, and not (the ten, 2026-10-20)

**Validated** (Blender, headless): the ten and the Bench through `finish()`
and re-imported (11/11): Root 3fw × 0.2 × 3fd, the layer's envelope, nothing
colliding, the `Pieces.luau` agreement, every seat, no coplanar faces, the
1,500 budget, closed meshes, names, boxes and triangle counts after the FBX
round trip. Both kits rebuilt in full with the new checks (49/49 and 25/25).
**Not validated:** anything in Studio. Not imported, not placed, not seen lit.


**His yes to the ten, 2026-10-20** (GDD §18). **Staged** in `blender/_import/`
with the four refitted pieces (`Decor_SandTray`, `Decor_Cauldron`,
`Decor_MoonWindow`, `Decor_Chandelier`) and Frostfang's `Decor_CocoaMug`:
15 FBX, WAITING §0 punkt 10. Not yet imported.
