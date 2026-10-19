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

- `fbx/<Name>.fbx`: 32 models, the file name the contract name
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
| `StandardRoom` | Room 2x2 | 2,480 / 6,000 | 108 | Floor, Wall_Back, Wall_Left, Wall_Right, Wall_Lintel, Wall_FrontLeft, Wall_FrontRight, Dressing, Glow_Warm_1, Bed, Furniture, Glow_Warm_2 |
| `GardenRoom` | Room 2x2 | 2,848 / 6,000 | 108 | walls, Floor, Dressing, Glow_Warm_1, Bed, Furniture |
| `AtticRoom` | Room 2x2 | 2,420 / 6,000 | 108 | walls, Floor, Dressing, Glow_Warm_1, Bed, Furniture |
| `SarcophagusSuite` | Room 2x3 | 2,320 / 6,000 | 108 | walls, Floor, Dressing, Glow_Warm_1, Bed, Furniture, Glow_Warm_2 |
| `PotionLoft` | Room 2x3 | 3,080 / 6,000 | 108 | walls, Floor, Dressing, Glow_Warm_1, Bed, Furniture, Glow_Magic_1 |
| `DenRoom` | Room 3x3 | 2,276 / 6,000 | 108 | walls, Floor, Dressing, Glow_Warm_1, Bed, Furniture |
| `CoffinSuite` | Room 3x3 | 2,232 / 6,000 | 108 | walls, Floor, Dressing, Glow_Warm_1..4, Bed, Furniture |
| `OperaSuite` | Room 3x3 | 2,900 / 6,000 | 108 | walls, Floor, Dressing, Glow_Warm_1, Bed, Furniture |
| `SnackBar` | Amenity 2x2 | 2,434 / 6,000 | 96 | walls, Floor, Dressing, Glow_Warm_1, Centrepiece |
| `MusicRoom` | Amenity 2x2 | 2,032 / 6,000 | 96 | walls, Floor, Dressing, Glow_Warm_1, Centrepiece |
| `GraveyardGarden` | Amenity 2x2 | 2,372 / 6,000 | 96 | walls, Floor, Dressing, Glow_Warm_1..2, Centrepiece |
| `QuietLibrary` | Amenity 2x2 | 3,820 / 6,000 | 96 | walls, Floor, Dressing, Glow_Warm_1..2, Centrepiece |
| `OrganHall` | Amenity 2x2 | 2,266 / 6,000 | 96 | walls, Floor, Dressing, Glow_Warm_1..3, Centrepiece |
| `Lobby` | Lobby 72x12 | 2,934 / 8,000 | 84 | Rug, Desk, Till, ArchLeft, ArchRight, ArchTop, Dressing, Glow_Warm_1..2, Planter_1, Planter_2 |
| `StairCore` | Stairs | 1,276 / 8,000 | 180 | Step_Up_1..5, Landing, Step_Down_1..5, Wall_Left, Wall_Right, Wall_Back, Divider, Dressing, Glow_Warm_1 |
| `StairCoreTop` | Stairs | 1,612 / 8,000 | 192 | as StairCore, plus Rail_Top; walls 15.5 tall |
| `HotelSign` | Sign | 400 / 3,000 (draft ceiling) | none | PostLeft, PostRight, Board, Crest, Glow_Cold_1 |
| `Decor_PuddleRug` | Decor | 228 / 1,500 | none | Body |
| `Decor_SnackBasket` | Decor | 384 / 1,500 | none | Body |
| `Decor_RecordPlayer` | Decor | 336 / 1,500 | none | Body |
| `Decor_Candles` | Decor | 312 / 1,500 | none | Body, Glow_Warm_1..3 |
| `Decor_Planter` | Decor | 456 / 1,500 | none | Body |
| `Decor_AntiqueWardrobe` | Decor | 544 / 1,500 | none | Body |
| `Decor_BlackoutCurtains` | Decor | 304 / 1,500 | none | Body |
| `Decor_SandTray` | Decor | 354 / 1,500 | none | Body |
| `Decor_CatBasket` | Decor | 440 / 1,500 | none | Body |
| `Decor_Cauldron` | Decor | 478 / 1,500 | none | Body, Glow_Magic_1 |
| `Decor_SteakPlatter` | Decor | 282 / 1,500 | none | Body |
| `Decor_MoonWindow` | Decor | 432 / 1,500 | none | Body, Glow_Cold_1 |
| `Decor_PipeOrgan` | Decor | 566 / 1,500 | none | Body |
| `Decor_SoundproofWalls` | Decor | 972 / 1,500 | none | Body |
| `Decor_Chandelier` | Decor | 784 / 1,500 | none | Body, Glow_Warm_1..5 |

Triangles exclude `Root` and `LOD_Proxy` are counted separately (500 ceiling).

## How each piece is cut (MODELS.md rule 7)

- **Collides:** `Floor`, every `Wall_*`, `Bed` / `Centrepiece`, `Furniture`
  (one compact piece on the right wall), the lobby's `Desk`, `Till`, `Arch*`,
  `Planter_n`, every stair box, the sign's posts and `Board`. Each is a
  compact shape, so `Box` collision is its true shape.
- **Does not collide:** `Root`, `Dressing` (pictures, sconces, trims, rafters,
  ivy, awnings: everything on the walls, merged into one mesh), `Glow_*`,
  `LOD_Proxy`, the lobby's `Rug` and the sign's `Crest` (as the blockout), and
  each decor `Body` (the blockout's Body does not collide either).
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
- The lobby keeps the blockout's open plan (no walls), with a checkerboard
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
