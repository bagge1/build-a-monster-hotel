# `Cosmetic_CandyFacade` (pass FacadeCandy)

The look (a draft he said yes to, GDD decision log 2026-10-20): pink wafer walls, white icing dripping from the top, striped posts.
Built by `tools/build_facades.py -- styles candy` to `MODELS.md`, "Facade";
what all seven sets share, the choices made in building them and the blind
reviews are in `blender/facade/README.md`. Goes to `assets/Cosmetics/Cosmetic_CandyFacade/` once imported.

| Piece | Triangles / budget | Parts | Validated | What it is |
|---|---|---|---|---|
| `Facade_Wall` | 728 / 1,500 | Wall, Dressing, LOD_Proxy | passed | a plain wall: pink wafer layers with cream between, a chocolate plinth, white icing along the top with drips |
| `Facade_Window_TwinSash` | 1,304 / 2,500 | Wall, Glass, Dressing, LOD_Proxy | passed | pink wafer layers with cream between, a chocolate plinth, white icing along the top with drips; a TwinSash window: white piped frames and bars, a chocolate sill; the arched one round-headed, gumdrops in the box |
| `Facade_Window_Arched` | 1,300 / 2,500 | Wall, Glass, Dressing, LOD_Proxy | passed | pink wafer layers with cream between, a chocolate plinth, white icing along the top with drips; a Arched window: white piped frames and bars, a chocolate sill; the arched one round-headed, gumdrops in the box |
| `Facade_Window_Round` | 1,484 / 2,500 | Wall, Glass, Dressing, LOD_Proxy | passed | pink wafer layers with cream between, a chocolate plinth, white icing along the top with drips; a Round window: white piped frames and bars, a chocolate sill; the arched one round-headed, gumdrops in the box |
| `Facade_Window_Wide` | 1,592 / 2,500 | Wall, Glass, Dressing, LOD_Proxy | passed | pink wafer layers with cream between, a chocolate plinth, white icing along the top with drips; a Wide window: white piped frames and bars, a chocolate sill; the arched one round-headed, gumdrops in the box |
| `Facade_Entrance` | 2,524 / 3,000 | Wall_Left, Wall_Right, ArchLeft, ArchRight, ArchTop, Dressing, Glow_Warm_1, LOD_Proxy | passed | striped candy-cane pillars, a round icing arch with drips, a cherry on top, a pink lantern hung in the arch |
| `Facade_Corner` | 680 / 800 | Post, Dressing | passed | a white post with a round red-and-white candy cane up its corner, a chocolate foot |

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
