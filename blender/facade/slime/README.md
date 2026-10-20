# `Cosmetic_SlimeFacade` (the Starter Pack)

The look (a draft he said yes to, GDD decision log 2026-10-20): green walls with slime dripping off the sills.
Built by `tools/build_facades.py -- styles slime` to `MODELS.md`, "Facade";
what all seven sets share, the choices made in building them and the blind
reviews are in `blender/facade/README.md`. Goes to `assets/Cosmetics/Cosmetic_SlimeFacade/` once imported.

| Piece | Triangles / budget | Parts | Validated | What it is |
|---|---|---|---|---|
| `Facade_Wall` | 132 / 1,500 | Wall, LOD_Proxy | passed | a plain wall: green walls with a pale course over the windows |
| `Facade_Window_TwinSash` | 736 / 2,500 | Wall, Glass, Dressing, LOD_Proxy | passed | green walls with a pale course over the windows; a TwinSash window: stone frames and sills, slime pooled on the sill and dripping off it |
| `Facade_Window_Arched` | 852 / 2,500 | Wall, Glass, Dressing, LOD_Proxy | passed | green walls with a pale course over the windows; a Arched window: stone frames and sills, slime pooled on the sill and dripping off it |
| `Facade_Window_Round` | 1,120 / 2,500 | Wall, Glass, Dressing, LOD_Proxy | passed | green walls with a pale course over the windows; a Round window: stone frames and sills, slime pooled on the sill and dripping off it |
| `Facade_Window_Wide` | 972 / 2,500 | Wall, Glass, Dressing, LOD_Proxy | passed | green walls with a pale course over the windows; a Wide window: stone frames and sills, slime pooled on the sill and dripping off it |
| `Facade_Entrance` | 1,320 / 3,000 | Wall_Left, Wall_Right, ArchLeft, ArchRight, ArchTop, Dressing, Glow_Warm_1, LOD_Proxy | passed | a round stone arch with slime heaped on its crown and dripping off its rim, an iron lantern |
| `Facade_Corner` | 320 / 800 | Post, Dressing | passed | a dark green post with slime oozing over its top and down its faces |

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
