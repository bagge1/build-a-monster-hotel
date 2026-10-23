# Bayou Spa hotel kit (Location 3): a draft

Built 2026-10-23 for the soft launch (LAUNCH.md workstream 5) by
`tools/build_hotel_bayou_spa.py` on `tools/hotel_kit.py`. **A draft for
August's one approval round**: nothing here is approved, and nothing has
been seen in Studio. Goes to `assets/HotelKit/BayouSpa/` once imported
(`ServerStorage.HotelKit.BayouSpa`; the code looks the folder up as the
location's name without spaces).

What the code reads from the kit and nothing else made: the desk, the
stairs, the sign, the plaque and the decor. The walls, door, post and
furniture are `blender/rooms/bayou_spa/` (2026-10-21); the facade is
`blender/facade/bayou_spa/`; rooms are built from walls (A.12) and the
Lobby shell is retired into `Facade_Entrance`, so neither is here.

**The look**, the built rooms' (their README): a swamp spa, cosy not grim;
weathered cypress, soft sage, woven rattan, lily greens and lotus pinks, mud
and still water, brass and copper, firefly light; the built rooms' palette
`BS_PALETTE` plus the Locations colours. **Moss used lightly**: a tuft at a
corner, never a garland along a whole edge (the kits' fourth blind review,
finding 9, recommends it; it is the reversible choice while WAITING §2.43
asks him about the walls).

Rebuild: `blender -b --python-exit-code 1 -P tools/build_hotel_bayou_spa.py`
(`-- only FrontDesk,Decor_MudPot`, `-- nopreview`), then
`tools/review_pieces.py -- hotel/bayou_spa` for the review sheet.

| Piece | Kind | Triangles / budget | What it is |
|---|---|---|---|
| `FrontDesk` | Desk 2x1 | 2,386 / 3,000 | a cypress counter with three woven rattan panels in light cypress frames on a stone plinth, a drift-grey top, a brass bell at the check-in prompt, a lily-green ledger, a copper till, a rattan-shaded lamp (`Glow_Warm_1`), the key rack (cypress, a sage board of brass, lotus and lily tags) and its clock |
| `StairCore` | Stairs | 2,160 / 8,000 | the walker-proven switchback (the blockout's boxes exactly) in cypress under a woven rattan runner, cypress wainscot and sage walls, a firefly jar on a crooked bracket (`Glow_Warm_1`), a moonlit bayou picture |
| `StairCoreTop` | Stairs | 2,696 / 8,000 | the same, railed round the stairwell (`Rail_Top`) |
| `HotelSign` | Sign | 840 / 3,000 | cypress posts flaring at their roots on stones, the 16 x 6 `Board` (dark water teal: the sign's text is light), a round cypress crest with a lotus on a lily pad and a lit crescent moon (`Glow_Cold_1`), a light moss tuft on each corner |
| `RoomPlaque` | Cosmetic | 160 / 2,000 | a cypress plaque with a sage rim and brass pins; its `Face` dark cypress (the room's text is light) |
| `Decor_MossMound` | Decor 1x1 | 366 / 1,500 | a soft moss mound with lighter cushions, two lotus-pink toadstools, pebbles |
| `Decor_FireflyJar` | Decor 1x1 | 760 / 1,500 | a jar glowing with fireflies (`Glow_Warm_1`) inside a moonstone glass cage of ribs, a brass lid, a linen cap, a wire bail, on a small stump slice |
| `Decor_MudPot` | Decor 1x1 | 624 / 1,500 | a squat clay pot of bubbling mud with a copper band on three flat stones, a cypress paddle in it |
| `Decor_HerbRack` | Decor 1x1 | 1,282 / 1,500 | an A-frame cypress drying ladder hung with sprays of sage, lavender, chamomile and herbs head down, a rattan basket of cut herbs |
| `Decor_SteamVent` | Decor 1x1 | 870 / 1,500 | an iron grate in a ring of stones over a dark pool, a thin wisp of steam curling up off it |
| `Decor_Bench` | Decor 3x1 | 628 / 1,500 | the old lobby bench (`decor_bench`) in dark cypress, a sage cushion, rattan rails |
| `Decor_UrnPlanter` | Decor 1x1 | 632 / 1,500 | a pale stone urn of cattails, fern fronds and a lotus |
| `Decor_RugRunner`, `Decor_RugCorner`, `Decor_RugSquare` | Rug 4x2, 2x2, 4x4 | 156, 120, 204 / 1,500 | woven rattan mats (`K.rug`), dark cypress borders, lily and lotus diamonds; they join edge to edge |

## Validated (validation.json, by the build)

All 15 built and re-imported from their FBX clean (`VALIDATED 15/15`): the
desk's, the stairs' and the sign's colliding boxes and attachments are the
Luau blockout's (`K.blockout_*`), the desk's clear sides, the decor's
footprint, 0.4 inset, layer and height against `Pieces.luau`, no coplanar
faces, the bench's seat by rule 6, budgets, UVs and the atlas.
`collision_precise` is empty. Refused and fixed during the build: the sign's
crest and moon over its envelope (moved in), the mound's pebbles 0.01 under
the floor, the herb rack over budget (three stems a spray), two grate bars
sharing a face (staggered 0.01).

## Blind review 2026-10-23 (first run) and its triage

A context-free reviewer (another model) on `review/pieces_sheet.png` and
close-ups of the desk, sign and stairs:

1. **Desk: the key rack far behind the counter, two unrelated pieces** —
   False: the layout is the contract (MODELS.md "Front desk": the rack on the
   back edge, the clerk's post at z 1.5 between), the Manor's and the
   Lodge's alike. **Pink bedroom lamp** — Confirmed: the shade is rattan now.
2. **The bell too small to tap** — False: check-in is a prompt at the `Desk`
   attachment, not the bell; the bell is the kit's shared `desk_bell`.
3. **Stairs: no landing guard; no standing room before the first step** —
   False: the boxes are the blockout's, walker-proven, the same as both
   kits; the cell in front is kept walkable by `Grid`.
4. **Stairs: the second flight missing** — False: it is behind the divider
   from this view (`Step_Down_1`–`7` in the manifest).
5. **Stairs: a dark slab with a streak up it** — False: the wall's outer
   face, in the colour the step ends lie in (they meet it by design, as in
   both kits); the streak is Workbench's cavity line at those ends.
6. **Sign: posts float or lean; the board huge; the crest tiny** — Posts
   False (each lathe stands on its stone from y 0.4; the camera is
   orthographic, nothing leans). Board False (16 x 6 is the contract).
   Crest Confirmed: the lotus and its lily pad are half as big again.
7. **Plaque reads as a plank lying on the floor** — False: the tile lays it
   on the plate; it hangs at the room's `Sign` attachment and is 4 x 1.3 by
   the contract.
8. **Firefly jar a cake on a stand** — Confirmed: a tall jar on a small
   stump, fourteen bigger fireflies all round it.
9. **Mud pot a cauldron, the stones dropped parts** — Not changed: a pot of
   mud is what the name asks for; the stones are its feet. August's look.
10. **Steam vent a stone cairn** — Confirmed: an iron grate, a thinner wisp
    curling up. Opaque steam still reads as stacked puffs in Workbench;
    August's look (no part of a decor piece is see-through).
11. **Herb rack an Easter display (eggs)** — Confirmed: each bundle is a
    spray of stems hung head down with leaves at the tips.
12. **The corner rug's flap; diamonds as card suits** — False: the shared
    `rug('corner')` (its inner L joins two runners); the diamonds are every
    kit's rug motif.
13. **The moss mound a bush** — Not changed (unsure; a mound of moss).

### Second run (new reviewer, new pictures)

1. **Stairs: the second flight does not read; step bumps on the outer
   wall** — False, as in the first run: the down flight is behind the
   divider from the front, and the step ends meet the wall's outer face by
   design (both kits alike).
2. **Firefly jar: specks glued on an opaque vase** — Confirmed: the jar is
   now a glowing core of fireflies (`Glow_Warm_1`) inside a moonstone glass
   cage of eight ribs, a base ring and a shoulder, the lid and bail over it.
3. **Steam vent: a snowman of white spheres; the ring a camp fire** —
   **August's call** (WAITING §2.49): opaque steam is puffs whatever their
   shape. Recommendation: keep it, or drop the steam and let the vent be a
   hot pool with a grate.
4. **Mud pot: the stick through a lid; floating on its stones; a
   cauldron** — False for the lid (the dark disc is the mud's surface, the
   paddle stands in it) and for floating (the pot's foot is inside its three
   stones); the cauldron read is his call (§2.49).
5. **The corner rug unfinished** — False: the shared `rug('corner')`.
6. **Desk: the clock sinks into the cornice; the clerk's side open; a
   green blob by the lamp** — Clock and sides False (the shared
   `desk_keyrack`; the clear sides are the contract, the clerk walks in
   round the counter's ends). The blob Confirmed: the moss tuft is gone.
7. **Moss mound faceted** — Confirmed: 18 sides (was 12).
8. **Bench back post** — False: the shared `decor_bench`, every kit's.
9. **Herb rack a ladder; sign lotus a cake, board high** — Not changed: a
   drying ladder is the piece; the board's height is the contract.

### Third run (new reviewer, the five changed pieces)

No fault of fit or construction left; the looks are **August's call**
(WAITING §2.49): the steam's puffs (again), the moss mound read as a slime
(its pink toadstools as a tongue), the jar as a lantern (its glass is a cage
of ribs, nothing being see-through; the two fireflies over it are meant),
the herb sprays as beads. False again: the desk's layout and its rack's
height (the contract, every kit's).

## Not validated

Studio: the import, `import_fixup.luau`, the glows lit, the pieces placed by
the code (`HotelKit.piece`, `stairs`, `decor`, `plaque`, the sign), a walker
on the stairs in this set's FBX. Studio runtime is not tested.

## Review pictures (not in git, rebuilt by the scripts)

- `review/pieces_sheet.png`: every piece close up beside the 5-stud person
  (`tools/review_pieces.py`); the tiles in `review/pieces/`.
- `review/contact_sheet.png`: the set laid out (the kit's sheet).

## Imported

Imported 2026-10-23 (WAITING §0.15): all 15 fixed up by `import_fixup.luau` (Box everywhere, `LOD_Proxy` hidden, Root the hidden PrimaryPart, the desk's 7 and each stair's 4 attachments, the glows lit), read back in a separate call and saved to `assets/HotelKit/BayouSpa/<Name>.rbxm`; the synced copies under `ServerStorage.HotelKit.BayouSpa` match the import part for part (mesh ids, sizes, collision, no empty MeshPart). The live sync dropped `PrimaryPart` on most; set back to `Root` in Studio (the files have it). Not yet seen in a playtest.
