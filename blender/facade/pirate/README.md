# `Cosmetic_PirateFacade` (pass FacadePirate)

The look (a draft he said yes to, GDD decision log 2026-10-20): weathered ship planks, round porthole windows, rope trim, a lantern on each corner.
Built by `tools/build_facades.py -- styles pirate` to `MODELS.md`, "Facade";
what all seven sets share, the choices made in building them and the blind
reviews are in `blender/facade/README.md`. Goes to `assets/Cosmetics/Cosmetic_PirateFacade/` once imported.

| Piece | Triangles / budget | Parts | Validated | What it is |
|---|---|---|---|---|
| `Facade_Wall` | 804 / 1,500 | Wall, Dressing, LOD_Proxy | passed | a plain wall: narrow weathered planks in four woods, a dark plank foot and top |
| `Facade_Window_TwinSash` | 2,304 / 2,500 | Wall, Glass, Dressing, LOD_Proxy | passed | narrow weathered planks in four woods, a dark plank foot and top; a TwinSash window: rope round every window, brass rings round the portholes; the twin two portholes, the round one big one, the arched a round-headed stern window, a crate of herbs under the wide one |
| `Facade_Window_Arched` | 1,304 / 2,500 | Wall, Glass, Dressing, LOD_Proxy | passed | narrow weathered planks in four woods, a dark plank foot and top; a Arched window: rope round every window, brass rings round the portholes; the twin two portholes, the round one big one, the arched a round-headed stern window, a crate of herbs under the wide one |
| `Facade_Window_Round` | 1,596 / 2,500 | Wall, Glass, Dressing, LOD_Proxy | passed | narrow weathered planks in four woods, a dark plank foot and top; a Round window: rope round every window, brass rings round the portholes; the twin two portholes, the round one big one, the arched a round-headed stern window, a crate of herbs under the wide one |
| `Facade_Window_Wide` | 1,476 / 2,500 | Wall, Glass, Dressing, LOD_Proxy | passed | narrow weathered planks in four woods, a dark plank foot and top; a Wide window: rope round every window, brass rings round the portholes; the twin two portholes, the round one big one, the arched a round-headed stern window, a crate of herbs under the wide one |
| `Facade_Entrance` | 1,776 / 3,000 | Wall_Left, Wall_Right, ArchLeft, Dressing, ArchRight, ArchTop, Glow_Warm_1, LOD_Proxy | passed | a round arch of planks between iron-banded timbers, rope along its rim, a brass lantern hung in it |
| `Facade_Corner` | 302 / 800 | Post, Dressing, Glow_Warm_1 | passed | a dark ship timber with iron bands, a brass lantern hung off it on an iron bracket |

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
