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

- `fbx/<Name>.fbx`: 18 models, the file name the contract name
  (`ServerStorage.HotelKit.FrostfangLodge.<Name>`; the code looks the folder
  up as the Location's name without spaces). The atlas is embedded in each.
- `manifest.json`: every piece's Root, every part's box (Roblox studs, piece
  frame), triangles, whether it collides, every attachment, and the palette.
- `validation.json`: the validator's results per piece (18 of 18 ok),
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
| `IglooRoom` | Room 2x2 | 4,774 / 6,000 | 108 | Floor, the six walls, Dressing, Glow_Warm_1, Bed, Furniture, Glow_Warm_2 |
| `IceCave` | Room 2x3 | 4,036 / 6,000 | 108 | walls, Floor, Dressing, Glow_Warm_1, Bed, Furniture, Glow_Cold_1 |
| `YetiDen` | Room 3x3 | 4,662 / 6,000 | 108 | walls, Floor, Dressing, Glow_Warm_1, Bed, Furniture, Glow_Warm_2 |
| `FrostLoft` | Room 2x3 | 5,462 / 6,000 | 108 | walls, Floor, Dressing, Glow_Warm_1, Bed, Furniture |
| `GlacierSuite` | Room 3x3 | 4,566 / 6,000 | 108 | walls, Floor, Dressing, Glow_Warm_1..2, Bed, Furniture, Glow_Cold_1 |
| `AuroraDome` | Room 3x3 | 4,926 / 6,000 | 108 | walls, Floor, Dressing, Glow_Warm_1, Glow_Magic_1..3, Bed, Furniture |
| `CocoaLounge` | Amenity 2x2 | 5,312 / 6,000 | 96 | walls, Floor, Dressing, Glow_Warm_1, Centrepiece |
| `AuroraDeck` | Amenity 2x2 | 3,894 / 6,000 | 96 | walls, Floor, Dressing, Glow_Warm_1, Glow_Magic_1..2, Centrepiece |
| `Lobby` | Lobby 72x12 | 2,926 / 8,000 | 84 | Rug, Desk, Till, ArchLeft, ArchRight, ArchTop, Dressing, Glow_Warm_1..2, Planter_1, Planter_2 |
| `StairCore` | Stairs | 2,678 / 8,000 | 180 | Step_Up_1..5, Landing, Step_Down_1..5, Wall_Left, Wall_Right, Wall_Back, Divider, Dressing, Glow_Warm_1 |
| `StairCoreTop` | Stairs | 3,542 / 8,000 | 192 | as StairCore, plus Rail_Top; walls 15.5 tall |
| `HotelSign` | Sign | 516 / 3,000 (draft ceiling) | none | PostLeft, PostRight, Board, Crest, Glow_Cold_1 |
| `Decor_IceBlock` | Decor | 160 / 1,500 | none | Body |
| `Decor_CocoaMug` | Decor | 790 / 1,500 | none | Body |
| `Decor_PrankBox` | Decor | 658 / 1,500 | none | Body |
| `Decor_RockPile` | Decor | 362 / 1,500 | none | Body |
| `Decor_SnowGlobe` | Decor | 502 / 1,500 | none | Body |
| `Decor_AuroraLamp` | Decor | 392 / 1,500 | none | Body, Glow_Magic_1 |

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
compact piece on the right wall), the lobby's `Desk`, `Till`, `Arch*`,
`Planter_n`, every stair box, the sign's posts and `Board` collide;
`Dressing` (snow cornice, icicles, lanterns, windows, pictures, ribbons,
stars, the yeti footprints), `Glow_*`, `LOD_Proxy`, the lobby's `Rug`, the
sign's `Crest` and each decor `Body` do not.

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
- The lobby keeps the blockout's open plan (no walls, no fireplace: one at
  the back could block the walk to the stair core), with a plank floor, a red
  runner, a log desk with snowflakes, a snowy timber gable over the entrance
  with a lantern, and snowy pines in the far corners.

## 2026-10-19 afternoon: the sign posts

The cosmetics set found each `HotelSign` post's top ring poking ~0.07 studs out
of the Board's front face, where the sign's text goes. The posts now end under
the Board (5 tall, ring at y 4.6–5.0). Rebuilt; validation passes. The saved
`assets/HotelKit/.../HotelSign.rbxm` is the old one until the next import.
