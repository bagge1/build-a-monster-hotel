# `Cosmetic_NeonFacade` (pass FacadeNeon)

The look (a draft he said yes to, GDD decision log 2026-10-20): dark panels with glowing cyan and magenta tubes round the windows.
Built by `tools/build_facades.py -- styles neon` to `MODELS.md`, "Facade";
what all seven sets share, the choices made in building them and the blind
reviews are in `blender/facade/README.md`. Goes to `assets/Cosmetics/Cosmetic_NeonFacade/` once imported.

| Piece | Triangles / budget | Parts | Validated | What it is |
|---|---|---|---|---|
| `Facade_Wall` | 144 / 1,500 | Wall, LOD_Proxy | passed | a plain wall: dark indigo panels with lighter seams at the sill line, the heads and the top |
| `Facade_Window_TwinSash` | 456 / 2,500 | Wall, Glass, Dressing, Glow_Cyan_1, Glow_Magenta_1, LOD_Proxy | passed | dark indigo panels with lighter seams at the sill line, the heads and the top; a TwinSash window: a glowing tube round each opening (a twin sash cyan and magenta), a steel ledge under it |
| `Facade_Window_Arched` | 572 / 2,500 | Wall, Glass, Dressing, Glow_Cyan_1, LOD_Proxy | passed | dark indigo panels with lighter seams at the sill line, the heads and the top; a Arched window: a glowing tube round each opening (a twin sash cyan and magenta), a steel ledge under it |
| `Facade_Window_Round` | 912 / 2,500 | Wall, Glass, Dressing, Glow_Magenta_1, LOD_Proxy | passed | dark indigo panels with lighter seams at the sill line, the heads and the top; a Round window: a glowing tube round each opening (a twin sash cyan and magenta), a steel ledge under it |
| `Facade_Window_Wide` | 912 / 2,500 | Wall, Glass, Dressing, Glow_Magenta_1, Glow_Cyan_1, LOD_Proxy | passed | dark indigo panels with lighter seams at the sill line, the heads and the top; a Wide window: a glowing tube round each opening (a twin sash cyan and magenta), a steel ledge under it |
| `Facade_Entrance` | 608 / 3,000 | Wall_Left, Wall_Right, ArchLeft, ArchRight, ArchTop, Glow_Cyan_1, Glow_Magenta_1, LOD_Proxy | passed | steel pillars and lintel, a cyan and a magenta tube round the doorway and a chevron of both over it |
| `Facade_Corner` | 60 / 800 | Post, Glow_Cyan_1, Glow_Magenta_1 | passed | a dark post with a cyan strip down one face and a magenta strip down the other |

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
