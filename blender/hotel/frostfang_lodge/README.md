# Frostfang Lodge hotel kit (Location 2): first draft

Built 2026-10-19 during the night sprint, by `tools/build_hotel_frostfang_lodge.py`
on `tools/hotel_kit.py`. **A draft for August's review**: nothing here is
approved, and nothing has been seen in Studio.

**The look, in one line:** a cosy-frosty timber lodge: log-striped walls
(snow blocks in the Igloo Room, ice bricks in the Ice Cave, glacier blue in
the Glacier Suite, a starry navy night in the Aurora Dome) with a snow
cornice and icicles along every wall top, the facade blue outside, round
doorways, a red-roofed iron lantern as each room's lamp, red and violet
plaid quilts, cocoa browns, and one themed bed and piece of furniture per
room (an igloo-dome headboard and ice dresser, a stone slab under furs and a
glowing crystal cluster, a round fur nest and stone stove, a log bed and a
yarn shelf with knitted icicles, a gold-banded coiled bed between ice
pillars, a cloud bed under glowing northern lights with a telescope).

Rebuild: `blender -b --python-exit-code 1 -P tools/build_hotel_frostfang_lodge.py`
(`-- nopreview` skips the sheet, `-- only Lobby,IglooRoom` rebuilds some and
keeps the rest of the manifest). About 40 s, headless, Workbench only.

## What is here

- `fbx/<Name>.fbx`: 25 models, the file name the contract name
  (`ServerStorage.HotelKit.FrostfangLodge.<Name>`; the code looks the folder
  up as the Location's name without spaces). The atlas is embedded in each.
- `manifest.json`: every piece's Root, every part's box (Roblox studs, piece
  frame), triangles, whether it collides, every attachment, and the palette.
- `validation.json`: the validator's results per piece (25 of 25 ok),
  `collision_precise` (empty for every piece), and what was not validated.
- `import_fixup.luau`: the import's step 2 (skill `import`), generated from
  the manifest; it makes the attachments, Root, the pivot, collision, glows.
- `textures/HotelAtlas.png`: the lodge's own 256 px palette atlas (50 flat
  cells; `hotel_kit.use_palette`), including the Locations.luau colours
  `ground`, `facade` and `trim`.
- `review/contact_sheet.png`: the one Workbench sheet (decor shown at 2x).
- `frostfang_lodge.blend`: every piece laid out side by side.

| Piece | Kind | Triangles / budget | LOD_Proxy | Parts besides Root |
|---|---|---|---|---|
| `IglooRoom` | Room 2x2 | 4,726 / 6,000 | 108 | the six walls, Floor, Rug, Dressing, Bed, Furniture, Glow_Warm_1..2 |
| `Lobby` | Lobby 144x24 (shell) | 4,372 / 10,000 | 60 | Floor, Wall_FrontLeft, Dressing, Wall_FrontRight, ArchLeft, ArchRight, ArchTop, Glow_Warm_1..7 |
| `FrontDesk` | Desk 2x1 | 2,278 / 3,000 | 36 | Counter, Dressing, Till, KeyRack, Glow_Warm_1 |
| `StairCore` | Stairs | 4,018 / 8,000 | 240 | Step_Up_1..8, Landing, Step_Down_1..7, Wall_Left, Wall_Right, Wall_Back, Divider, Dressing, Glow_Warm_1 |
| `StairCoreTop` | Stairs | 5,082 / 8,000 | 252 | Step_Up_1..8, Landing, Step_Down_1..7, Wall_Left, Wall_Right, Wall_Back, Divider, Rail_Top, Dressing, Glow_Warm_1 |
| `HotelSign` | Sign | 516 / 3,000 (draft ceiling) | none | PostLeft, PostRight, Board, Crest, Glow_Cold_1 |
| `RoomPlaque` | Cosmetic | 160 / 2,000 (draft ceiling) | none | Board, Face |
| `IceCave` | Room 2x3 | 4,084 / 6,000 | 108 | the six walls, Floor, Rug, Dressing, Bed, Furniture, Glow_Warm_1, Glow_Cold_1 |
| `YetiDen` | Room 3x3 | 4,886 / 6,000 | 108 | the six walls, Floor, Rug, Dressing, Bed, Furniture, Glow_Warm_1..2 |
| `FrostLoft` | Room 2x3 | 5,718 / 6,000 | 108 | the six walls, Floor, Rug, Dressing, Bed, Furniture, Glow_Warm_1 |
| `GlacierSuite` | Room 3x3 | 4,790 / 6,000 | 108 | the six walls, Floor, Rug, Dressing, Bed, Furniture, Glow_Warm_1..2, Glow_Cold_1 |
| `AuroraDome` | Room 3x3 | 5,726 / 6,000 | 108 | the six walls, Floor, Rug, Dressing, Bed, Furniture, Glow_Warm_1, Glow_Magic_1..3 |
| `CocoaLounge` | Amenity 2x2 | 5,264 / 6,000 | 96 | the six walls, Floor, Rug, Dressing, Centrepiece, Glow_Warm_1 |
| `AuroraDeck` | Amenity 2x2 | 3,846 / 6,000 | 96 | the six walls, Floor, Dressing, Centrepiece, Glow_Warm_1, Glow_Magic_1..2 |
| `Decor_IceBlock` | Decor 1x1 Floor | 160 / 1,500 | none | Body |
| `Decor_CocoaMug` | Decor 1x1 Floor | 790 / 1,500 | none | Body |
| `Decor_PrankBox` | Decor 1x1 Floor | 658 / 1,500 | none | Body |
| `Decor_RockPile` | Decor 2x2 Floor | 362 / 1,500 | none | Body |
| `Decor_SnowGlobe` | Decor 1x1 Floor | 502 / 1,500 | none | Body |
| `Decor_AuroraLamp` | Decor 1x1 Floor | 392 / 1,500 | none | Body, Glow_Magic_1 |
| `Decor_Bench` | Decor 3x1 Floor | 628 / 1,500 | none | Body |
| `Decor_UrnPlanter` | Decor 1x1 Floor | 162 / 1,500 | none | Body |
| `Decor_RugRunner` | Decor 4x2 Rug | 156 / 1,500 | none | Body |
| `Decor_RugCorner` | Decor 2x2 Rug | 120 / 1,500 | none | Body |
| `Decor_RugSquare` | Decor 4x4 Rug | 204 / 1,500 | none | Body |

Triangles exclude `Root`; `LOD_Proxy` is counted separately (500 ceiling).
The rooms are about twice the Haunted Manor's (2.2k-3.1k): the log stripes
(each a chamfered box) and the icicles. All are under budget; `FrostLoft` and
`CocoaLounge` are the closest (91 %, 89 %). Fewer stripes (`stripes=`) is the
lever if a neighbour's hotel costs too much to draw.

## How each piece is cut (MODELS.md rule 7)

As the Haunted Manor's (its README): walls exactly the blockout's boxes, in
pieces round the door, with the stripes, chamfers and jambs inside them; the
lintel a **round** arch here (`room_shell(lintel='round')`), its box the
blockout's 4 x 3 x 0.4, the opening 4 wide, 7 tall at the jambs and 8.6 at
the crown. `Floor`, every `Wall_*`, `Bed` / `Centrepiece`, `Furniture` (one
compact piece on the right wall), the lobby's `Wall_Front*` and `Arch*`, the
front desk's `Counter`, `Till` and `KeyRack`, every stair box, the sign's
posts and `Board` collide;
`Dressing` (snow cornice, icicles, lanterns, windows, pictures, ribbons,
stars, the yeti footprints), `Glow_*`, `LOD_Proxy`, a room's `Rug`, the
lobby's `Floor`, the sign's `Crest` and every decor `Body` do not.

**The shared structure against the Haunted Manor's** (compared from the two
manifests): `StairCore`, `StairCoreTop` and `HotelSign` have **identical
colliding boxes** (to 0.01 stud) and identical attachments; the stair steps
are the blockout's, and the stair walls' outer faces are one colour, since
the step ends lie in them. The `Lobby`'s attachments, `Desk`, `Till`,
`ArchLeft` and `ArchRight` are identical; two boxes differ and both stay
inside the footprint and off every walk the validator sweeps: `ArchTop` is
11.8 wide instead of 11.0 (the snow on the gable overhangs 0.4 each side,
from y 9 up) and `Planter_1/2` are 5.8 tall instead of 2.9 (snowy pines in
tubs, same 2 x 2 base).

## Validated (Blender, headless)

Everything the Haunted Manor README lists, by the same `finish()` and
validator, for all 18 pieces: names; Root; every attachment the Luau blockout
makes, within 0.1 stud and with its LookVector; nothing outside the
footprint; each wall's box equal to the blockout's; the door opening 4 x 7
with nothing colliding in it; a 5-stud person walking Door -> Bed meets
nothing colliding; each decor slot's 4 x 4 square free; the lobby's entrance
and the walks to Queue_1..4, Spawn and Trap_1..3 clear; the Board 16 x 6 x 0.6
at (0, 8, 0); glow colours only in glow parts; triangle budgets; closed
meshes; after the FBX round trip the same names, every box within 0.02 stud,
the same triangle counts, one UV layer and one material each, the atlas
embedded.

The kit changes made for this set (`use_palette`, `round_arch_points`,
`room_shell(lintel=, stripes=)`) are additive: a full Haunted Manor rebuild
after them wrote a byte-identical `manifest.json`, `validation.json` and
`import_fixup.luau`.

## Not validated

- **Nothing has run in Studio.** Not imported, not seen, not walked.
- Roblox's side of the axis conversion (`import_fixup.luau` checks every part
  against the manifest first and stops, touching nothing, if it is wrong).
- The attachments exist only in the manifest until `import_fixup.luau` runs.
- Walking: the stair boxes are the walker-proven blockout's; the room checks
  are box sweeps in Blender; no walker has run on the imported meshes.
- How it looks lit in Studio, the atlas upload (18 embedded copies).
- The northern lights are `Glow_Magic_<n>`: the fix-up lights them in its
  `Magic` colour (120, 255, 170), green; a violet or teal band would need a
  glow key MODELS.md does not have.

## Decisions taken without him (reversible, for his review)

- The palette and every colour pairing; each room's theme object and
  furniture; each amenity's centrepiece; each decor piece's shape.
- **The doorway is a round arch** (the manor's is pointed), and every room's
  lamp is a wall lantern instead of the manor's candle sconce.
- **The snow globe is opaque**: MODELS.md has no glass part for decor, so the
  scene "inside" (a pine, a red cabin, snowflakes) sits on the dome's front.
  A `Glass` part name would let the code make it see-through.
- **Ice is opaque** everywhere (the ice block, crystals, ice furniture): the
  fix-up sets only glows, nothing translucent.
- (Superseded 2026-10-19 evening by the lobby rework below.) The lobby kept the blockout's open plan (no walls, no fireplace: one at
  the back could block the walk to the stair core), with a plank floor, a red
  runner, a log desk with snowflakes, a snowy timber gable over the entrance
  with a lantern, and snowy pines in the far corners.

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

## 2026-10-19 evening: the lobby rework (layout A) and the sign's place

**He approved the look, 2026-10-19** (the renders after three blind reviews,
`archive/screens/2026-10-19_lobby_rework.jpg`).

The same layout as Haunted Manor's, from the kit's shared lobby shapes (see
that set's README, "the lobby rework", for the layout, the checks and the
first rounds' triage). The lodge's own: the front wall's inside in log
stripes as its rooms (`lobby_front_wall(paper=('log', 'log_dark'))`), snow
along the wall's top, a plank floor (the 6-stud checker read as vinyl), a log
desk with snowflakes, log benches, pines in tubs, an iron lamp and sconces. 6,358
triangles, 21 parts, validated by re-import. **Not run in Studio.**

The reviewers' lodge-only findings:

| Round, # | The finding | Triage |
|---|---|---|
| 1.2, 2.1 | Inside the front wall is flat khaki, the rooms are logs; outside is a flat blue slab | Inside: **confirmed**, now logs. Outside: **his call** (WAITING §2), blue as the code's facade |
| 1.1, 2.2, 2.6 | The sign is a billboard; its crest is narrower than its board; icicles at head height under it | **His call** (the sign model is unchanged; it stands off the walk at the forecourt corner). WAITING §2 |
| 1.5 | The key board reads as a second sign (gable and snowflake) | **Confirmed**: a cornice and a clock instead, as Haunted Manor's |
| 1.6 | The floor checker reads as vinyl | **Confirmed**: planks |
| 1.9 | The front wall has no snow cap; a slit beside the porch posts | **Confirmed**: snow along its top; the slit between each pillar and the wall filled (both kits) |
| 2.3 | The till faces the guest | **False** by design: the owner collects at the till from the served side, where its prompt is |
| 2.7 | Room arches are tall and narrow | **False** for this work: the rooms are unchanged (4 wide, the contract) |
| 2.8 | The rooms are bare | **False**: the players place the decor |

## 2026-10-19 night: the doubled scale

The same rescale as Haunted Manor's (that README, "the doubled scale"): rooms
24 × 24 to 36 × 36 with 17-stud walls, the lobby 144 × 24, the stair core
24 × 24 with 15 steps a storey, the sign and decor unchanged. The lodge's
own: the log and snow-block walls keep their courses' size (twice as many,
unchamfered, so the rooms stay under 6,000 triangles), the snow cornice and
icicles under the slab, the ice cave's stalactites longer, the frost loft's
rafters under the slab with its stars on threads, the aurora dome's lights
and stars across its wider walls, no snow on the lobby wall's top (it meets
the slab). Every piece validates (18/18). **Not run in Studio.**

### Blind reviews of the renders (2026-10-19 night, Fable, two rounds)

| Round, # | The finding | Triage |
|---|---|---|
| 1.1, 2.1 | The facade does not read as a log lodge | **His call**, already put (WAITING §2.11: logs outside the front wall now, if he wants) |
| 1.2, 2.2 | The entrance is lost; the sign's crest looks like a second entrance | **His call**: WAITING §2.13 |
| 1.3 | "The stairs are at the desk" | **False**: that is the Igloo Room's snow-block wall seen through its door; the stairs are at the far end (x 120 to 144) |
| 1.4, 2.3 | The lobby is a tunnel; the desk is unreadable from the door | **His call**: WAITING §2.13 |
| 1.5 | The room doorway is a 3-stud slot | **False**: 4 × 7 clear, checked by `finish()` |
| 1.6 | The room-side wall: flat panels, bright seams | **Confirmed**: the seams were the doors' 17-stud snow jambs, now to the arch's head; the wainscot and crown now run round the outside |
| 1.7, 2.4 | Stairwell: the floor looks missing, a lip at its mouth, a picture at floor level, a tall bottom riser | **False**: the floor is the code's ground; the lip is the lobby planks' 0.1 edge; the picture is 3.6 over the landing; every rise is 1.2. The open underside: **confirmed**, a soffit |
| 1.8, 2.5 | The room is empty; the pictures hang high | **His call**: WAITING §2.13 |
| 1.9 | The posts' bases read as pipe couplers | **His call**, already put (the arch's columns) |
| 1.10, 2.7 | Two window sizes | **False**: all 6 × 9, the camera stands off centre |
| 2.6 | The till reads as a toy house; the key board as a calendar; the counter at the chin | Till and keys: kept from the lobby rework, to be seen in the game. The counter: **his call** |
| 2.8 | Stairs through a room doorway | **False**: the Igloo Room's wall courses |

## 2026-10-19: free building (the lobby shell, the front desk, decor on the 3-stud grid)

The same rework as Haunted Manor's, on the same kit and contract (that
README, "free building", for the rules, the checks and the blind review,
which looked at both kits). The lodge's own:

- **`Lobby` is the shell**: the front wall in log stripes inside and facade
  blue outside, the snowy timber gable over the arch with its icicles, the
  lantern (`Glow_Warm_1`), six iron sconces (`Glow_Warm_2..7`), and the plank
  `Floor` (renamed from `Rug`), one part over 144 × 24, y 0 to 0.1, not
  colliding. The same attachments as Haunted Manor's (`Entrance`, `Spawn`,
  `SignBoard`, `Trap_1..3`). 4,372 triangles.
- **`FrontDesk`** (24 × 12, served toward −Z): three logs laid along the
  counter's served face (their fronts at the top's edge, z −4.2) with three
  snowflakes on them (`Dressing`), a light wood top at 3.8 with a strip of
  snow along the clerk's edge (to 3.82), the bell, a red ledger, the red till,
  the red-shaded iron lamp (`Glow_Warm_1`), the log key rack with its clock.
  The same boxes, attachments and checks as Haunted Manor's. 2,278 triangles
  of 3,000, `LOD_Proxy` 36.
- **The old lobby's furniture as decor**: `Decor_Bench` 3x1 Floor (dark logs, a
  red cushion), `Decor_UrnPlanter` 1x1 Floor (a snowy pine in a wooden tub,
  162 triangles), and the red-and-cream carpet as `Decor_RugRunner` 4x2,
  `Decor_RugCorner` 2x2 and `Decor_RugSquare` 4x4 (cream borders and pin
  lines, cream diamonds).
- **Every existing decor refitted** (`refit_decor`, recorded in the manifest):

  | Decor | Footprint, layer | Triangles | Refit |
  |---|---|---|---|
  | `Decor_IceBlock` | 1x1 Floor | 160 | scale 0.818: it was 0.49 too deep with the fish 0.09 proud of its face, past the 0.4 the brief allowed |
  | `Decor_CocoaMug` | 1x1 Floor | 790 | scale 0.892, shifted 0.23 toward −X (its handle) |
  | `Decor_PrankBox` | 1x1 Floor | 658 | shifted 0.05 toward −X (its crank) |
  | `Decor_RockPile` | 2x2 Floor | 362 | none |
  | `Decor_SnowGlobe` | 1x1 Floor | 502 | scale 0.990 |
  | `Decor_AuroraLamp` | 1x1 Floor | 392 | none |
  | `Decor_Bench` | 3x1 Floor | 628 | new |
  | `Decor_UrnPlanter` | 1x1 Floor | 162 | new |
  | `Decor_RugRunner` | 4x2 Rug | 156 | new |
  | `Decor_RugCorner` | 2x2 Rug | 120 | new |
  | `Decor_RugSquare` | 4x4 Rug | 204 | new |

- **Rooms and amenities**: one `Floor` each, the walking surface alone; the
  merged rugs are their own non-colliding `Rug` part in `IglooRoom`,
  `IceCave`, `YetiDen`, `FrostLoft`, `GlacierSuite`, `AuroraDome` and
  `CocoaLounge`. `Decor_1..3` are gone; `AuroraDeck` differs from HEAD only by
  them and is not re-staged. `StairCore`, `StairCoreTop`, `HotelSign` and
  `RoomPlaque` are unchanged.

**Validated** (Blender, headless): 25/25 through `finish()` and re-imported,
with the shell's, the desk's and the decor layers' rules. **Studio runtime is
not tested.**

**Staged** in the main checkout's `blender/_import/`: the seven whose names
are Haunted Manor's too as `FrostfangLodge_Lobby`, `FrostfangLodge_FrontDesk`,
`FrostfangLodge_Decor_Bench`, `FrostfangLodge_Decor_UrnPlanter`,
`FrostfangLodge_Decor_RugRunner`, `FrostfangLodge_Decor_RugCorner`,
`FrostfangLodge_Decor_RugSquare` (renamed after the fix-up, skill `import`);
the six refitted decor and the seven rooms with a `Rug` part under their own
names.

### Imported (2026-10-19 evening)

August imported the batch (57 FBX with Haunted Manor's and the trees). Once
Haunted Manor's were saved and renamed out of the way, the seven prefixed
imports were renamed to their own names and all 20 fixed up by
`import_fixup.luau` (every part where the manifest says, no model stopped),
then read back in a separate call: 151 meshes, all `Box`, no `Precise`, no
`Default` left, Root hidden, the manifest's attachments, `LOD_Proxy` hidden
on the 9 that have one (decor has none). Saved to
`assets/HotelKit/FrostfangLodge/` with `tools/save_imports.py`, each shared
name checked to differ from Haunted Manor's file. The live-synced copies
under `ServerStorage.HotelKit.FrostfangLodge` match the imports 20/20 (mesh
ids, sizes, textures, collision, attachments; no empty MeshPart), but **19
arrived with `PrimaryPart` nil** (all but the new `FrontDesk`; `DEVNOTES.md`):
the files have it (the serialized bytes deserialized, and a `rojo build` to
XML: `Root` on all 25), and `HotelKit` sets it on every clone. Workspace
copies deleted. **Studio runtime is not tested.**
