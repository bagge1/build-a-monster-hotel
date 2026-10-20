# Haunted Manor's facade (the hotel kit's own)

The look (a draft he said yes to, GDD decision log 2026-10-20): the approved `Lobby` front wall's bands and its pointed arch, pumpkin and lantern, carried over.
Built by `tools/build_facades.py -- styles haunted_manor` to `MODELS.md`, "Facade";
what all seven sets share, the choices made in building them and the blind
reviews are in `blender/facade/README.md`. Goes to `assets/HotelKit/HauntedManor/` once imported.

| Piece | Triangles / budget | Parts | Validated | What it is |
|---|---|---|---|---|
| `Facade_Wall` | 156 / 1,500 | Wall, LOD_Proxy | passed | a plain wall: the Lobby front wall's bands (stone plinth, plum, gold courses; lilac and plum inside) |
| `Facade_Window_TwinSash` | 468 / 2,500 | Wall, Glass, Dressing, LOD_Proxy | passed | the Lobby front wall's bands (stone plinth, plum, gold courses; lilac and plum inside); a TwinSash window: dark wood frames and bars, a gold sill |
| `Facade_Window_Arched` | 584 / 2,500 | Wall, Glass, Dressing, LOD_Proxy | passed | the Lobby front wall's bands (stone plinth, plum, gold courses; lilac and plum inside); a Arched window: dark wood frames and bars, a gold sill |
| `Facade_Window_Round` | 840 / 2,500 | Wall, Glass, Dressing, LOD_Proxy | passed | the Lobby front wall's bands (stone plinth, plum, gold courses; lilac and plum inside); a Round window: dark wood frames and bars, a gold sill |
| `Facade_Window_Wide` | 924 / 2,500 | Wall, Glass, Dressing, LOD_Proxy | passed | the Lobby front wall's bands (stone plinth, plum, gold courses; lilac and plum inside); a Wide window: dark wood frames and bars, a gold sill |
| `Facade_Entrance` | 852 / 3,000 | Wall_Left, Wall_Right, ArchLeft, ArchRight, ArchTop, Dressing, Glow_Warm_1, LOD_Proxy | passed | the Lobby's pointed arch: stone pillars, gold capitals, the plum gable and its pumpkin, the iron lantern hung in the arch |
| `Facade_Corner` | 100 / 800 | Post, Dressing | passed | a dark plum post with the wall's stone plinth and gold courses |

**Validated in Blender** (`validation.json`): every piece refused by
`finish()` until it met the contract, then checked again on its re-imported
FBX (boxes, envelope, ends, openings seen through the wall, the entrance's
clear 9 × 9, the corner's quadrant, no flickering faces, glows, budgets).
The layout round an L of owned cells: 25 pairs of pieces that meet
(10 at outside corners, 2 at the inside one, 13 end to end),
no faults.

**Not validated**: anything in Studio (the import, `import_fixup.luau`, the
look lit, the glows), the code placing the pieces (`HotelKit.facade`).
Studio runtime is not tested.

Review pictures (not in git, rebuilt by the script): `review/sheet.png` (the
layout, the entrance with a 5-stud person, the outside and inside corners,
the plain wall and the four windows from outside and inside).
