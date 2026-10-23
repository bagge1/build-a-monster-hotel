# Bayou Spa facade (the kit's own): a draft

Built 2026-10-23 (LAUNCH.md workstream 5) by `tools/build_facades.py --
styles bayou_spa` to `MODELS.md`, "Facade"; what every style shares, the
choices made in building them and the earlier blind reviews are in
`blender/facade/README.md`. **A draft for August's one approval round**;
nothing has been seen in Studio. Goes to `assets/HotelKit/BayouSpa/` once
imported (the code draws a blockout until then).

**The look**: a Creole cottage on the bayou. Sage clapboard in two close
sages (0.8 boards) over a dark cypress skirting and a stone plinth, a light
cypress course at 12, a dark cypress cap; inside a cypress wainscot under
sage. Light cypress window frames, bars and sills, green louvred
shutters folded back beside every window but the round one; the arched
window round-headed, lotus, lavender and chamomile in the wide one's box. The
entrance: square cypress posts on stone under a round arch of cypress
voussoirs, a lotus on its light cypress keystone, two light tufts of Spanish
moss off its shoulders, a firefly lantern hung in it (`Glow_Warm_1`, the one
light). The built rooms' palette (`BS_PALETTE`) plus `sage_mid`.

| Piece | Triangles / budget | Parts |
|---|---|---|
| `Facade_Wall` | 336 / 1,500 | Wall, LOD_Proxy |
| `Facade_Window_TwinSash` | 1,596 / 2,500 | Wall, Glass, Dressing, LOD_Proxy |
| `Facade_Window_Arched` | 1,412 / 2,500 | Wall, Glass, Dressing, LOD_Proxy |
| `Facade_Window_Round` | 1,092 / 2,500 | Wall, Glass, Dressing, LOD_Proxy |
| `Facade_Window_Wide` | 1,848 / 2,500 | Wall, Glass, Dressing, LOD_Proxy |
| `Facade_Entrance` | 1,672 / 3,000 | Wall_Left, Wall_Right, ArchLeft, ArchRight, ArchTop, Dressing, Glow_Warm_1, LOD_Proxy |
| `Facade_Corner` | 88 / 800 | Post, Dressing |

**Validated in Blender** (`validation.json`): every piece held by
`finish()` to the contract and checked again on its re-imported FBX (boxes,
envelope, ends, the openings seen through the wall, the entrance's clear 9 x 9,
the corner's quadrant, no flickering faces, glows, budgets); the layout round
an L of owned cells: 25 pairs that meet (10 convex, 2 concave, 13 end to
end), no faults. Refused and fixed during the build: the shutters' foot and
head on the clapboards' band edges (moved 0.07 off), the arch's springing and
the wide window's sill on a band edge (9.5; the wide window's foot 3.6), the
entrance's round posts 0.04 inside the edge.

**Not validated**: anything in Studio (the import, `import_fixup.luau`, the
lantern lit, the code placing the pieces). Studio runtime is not tested.

## Blind review 2026-10-23 (first run) and its triage

1. **The theme does not read: an olive clapboard barracks; the swamp cues
   (lotus, lantern) vanish at phone distance** — **August's call** (WAITING
   §2.49): the look. Recommendation: see it in the game first (Workbench's
   flat light darkens the sage); if it is still a barn, moss tufts along the
   cap and a lily-pad frieze on the course.
2. **The entrance a dark hole straight through, no door** — False: doorways
   are open arches in every kit (MODELS.md "Hotel kit": no code opens a door
   leaf, and a closed one would block every guest); the "fanlight" is the
   far wall's window through the opening.
3. **The arch's posts read as metal poles** — Confirmed: square chamfered
   cypress posts now, a light cypress capital.
4. **The arched window's head touches the course band** — Confirmed (the
   frame ran to 12.25, the course is 12.0-12.5): the head is at 11.6.
5. **The flower box over the shutters, no brackets** — False: the box runs
   x -4.1..4.1, the shutters start at 4.32; it has two brackets
   (`flower_box`); the three-quarter view overlaps them in the picture.
6. **A sliver at the concave joint** — False: the assembly check found no
   face of one piece on another's (validation.json `assembly`).
7. **Inside and outside frames differ** — Not changed: every style dresses
   the inside in its own wall colours (the inner frame cypress here).
8. **Sills at head height** — False: the contract's window zone (y 3-13).
9. **Clapboard contrast may shimmer** — Not changed (unsure): the two
   sages are 12 apart in each channel; to see in the game.
10. **The cap past the corner post** — False: the post stands 0.02 proud of
    both walls by the contract.

### Second run (new reviewer, new pictures)

1. **The window heads at four heights, two in the belt course** —
   Confirmed (the twin sash's frame ran to 12.25, the course is 12-12.5):
   every head but the round one's is at 11.6 now (the twin sash and the wide
   window 11.6, the arch's crown 11.6).
2. **The shutters the glass's teal** — Confirmed: green louvred shutters
   (`lily_dark`, `lily` louvres).
3. **Pale frames outside read as PVC; brown inside** — Confirmed: light
   cypress frames, bars and sills outside.
4. **The flower box a trough on legs** — Not changed: the shared
   `flower_box` (every style's), its brackets on the wall.
5. **The corner's light bead reads as a seam** — Confirmed: the bead is
   dark cypress, the post's colour.
6. **The keystone's lotus a potted tulip; the lantern hung from it** —
   Confirmed as a read: a light cypress keystone block with the lotus on it,
   no lily pad. The lantern's foot is 9.8 over the threshold (the contract
   asks 7.5).
7. **Two wall bases; the walls stand on a plinth** — False: the plinth is
   the wall's 0..0.6 band, on the walking surface.
8. **An empty band above the windows** — **August's call**, already asked
   in WAITING §2.34 for every style.

### Third run (new reviewer, new pictures)

1. **The entrance closed at the top by a glazed transom** — False (the
   reviewer was unsure): it is the far wall's window seen through the arch;
   the build holds the opening clear 9 x 9 (`facade_boxes`).
2. **The rear block a second storey that does not match** — False: the
   layout is one storey; the back row's walls are seen past the front wing.
3. **The shutters too narrow to read, green near the wall's** — **August's
   call** (WAITING §2.49): a 12-stud section with an 8-wide window leaves
   1.0-1.5 a side, under the half window a real shutter is.
4. **The arch top-heavy; the keystone's lotus and the moss tufts too small
   for a phone** — August's look (§2.49).
5. **The windows over-scaled** — the contract's zone; already asked for every
   style (WAITING §2.34, recommendation keep).
6. **The panes flush, no reveal** — False: `Glass` sits 0.27 inside the
   wall's outer face (z -0.35..-0.29 in a wall -0.62..-0.02).

## Review pictures (not in git, rebuilt by the script)

`review/sheet.png` (the layout, the entrance with a 5-stud person, both
corners, the five sections outside and in) and its parts `layout.png`,
`entrance.png`, `convex.png`, `concave.png`, `windows.png`,
`windows_inside.png`.

## Imported

Imported 2026-10-23 (WAITING §0.15): all 7 fixed up by `import_fixup.luau` (Box everywhere, `LOD_Proxy` hidden, Root the hidden PrimaryPart, the entrance's `Entrance` attachment and its lantern lit), read back in a separate call and saved unprefixed to `assets/HotelKit/BayouSpa/Facade_*.rbxm`; the synced copies match the import part for part (mesh ids, sizes, collision, no empty MeshPart). The live sync dropped `PrimaryPart`; set back to `Root` in Studio (the files have it). Not yet seen in a playtest.
