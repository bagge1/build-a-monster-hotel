# Haunted Manor decor, grey silhouettes (2026-10-19): for his pick

The first free-building decor set he named (clocks, flowers, plants,
furniture, a piano), as **grey silhouettes beside the 5-stud person** (skill
`modelling`: he picks the shape before any detail, colour or glow). Built by
`tools/build_decor_silhouettes_haunted_manor.py` on `tools/hotel_kit.py`, each
to the decor contract (`MODELS.md`, "Decor"), so the one he picks keeps its
frame, footprint and layer when it is detailed. **Not staged for import.**

**The sheet:** `review/silhouettes.png` (not in git; rebuilt by the script):
each piece on its footprint's 3-stud squares, a grey wall behind the Wall
pieces, the 5-stud person beside it, its name, footprint and layer on the
floor. Workbench, from the front, raised.

| Id (the code's) | Footprint, layer | What the silhouette is | Triangles |
|---|---|---|---|
| `GrandfatherClock` **A** | 1x1 Floor | a longcase clock: plinth, trunk with a pendulum window, a hood with a round dial under a domed pediment and three finials, 6.9 tall | 564 |
| `GrandfatherClock` **B** | 1x1 Floor | a coffin-shaped case clock, the dial at its head, a coffin-shaped pendulum window, bat wings on its crown, 6.8 tall | 336 |
| `WallClock` | 1x1 Wall | a round wall clock over a pendulum box, hung from 3.3 to 7 | 324 |
| `BlackRoses` | 1x1 Floor | a vase of seven roses on a little round pedestal stand, 4.8 tall | 740 |
| `CarnivorousPlant` | 1x1 Floor | a flytrap in a pot: a curved stalk, two toothed lobes gaping toward the front, leaves over the rim, 3.6 tall | 538 |
| `GhostFern` | 1x1 Floor | a fern in a pot on a three-legged stand, its fronds arching out and down | 522 |
| `Armchair` | 1x1 Floor | a wingback: a tall round-topped back, wings, rolled arms, 5 tall | 396 |
| `VelvetSofa` | 2x1 Floor | a camelback sofa: rolled arms, three seat cushions, buttons in the back | 524 |
| `Bookshelf` | 2x1 Wall | a tall bookcase of four full shelves under a cornice, 6.9 tall | 788 |
| `SideTable` | 1x1 Floor | a round pedestal table on tripod feet, a candle lamp with a glass chimney, a book | 408 |
| `GrandPiano` **A** | 2x2 Floor | a grand: the case with its curved side, the lid propped open, three legs, the keyboard toward the front, a bench | 336 |
| `GrandPiano` **B** | 2x2 Floor | an upright against the back edge, candle arms on its front, a bench | 268 |

The models are named `Decor_<Id>_A` / `_B` here only; the one he picks is
built as `Decor_<Id>` in `tools/build_hotel_haunted_manor.py`, detailed in
the set's palette, with its glows (the side table's flame, the clocks' faces
if he wants them lit) as their own parts.

## His picks, and what is his to say

- **GrandfatherClock**: A (the classic longcase) or B (the coffin case).
- **GrandPiano**: A (a grand, the whole 2 × 2) or B (an upright with its
  bench). An upright alone would fit **2x1 Wall** (6 × 3, against a wall);
  as B it keeps the id's 2x2 Floor so the code needs no change. His call.
- **Armchair at 1x1 is small for the 5-stud person**: the body may be at most
  2.2 wide, so the seat between the arms is 1.44, while the person's torso is
  2 wide (3.8 with arms). It reads child-sized beside him on the sheet. A 2x1
  footprint (5.2 wide) would seat him. His call; the footprint is the code's
  (`Pieces.luau`).
- Any shape: these are first readings of his words; he improves on them.

## Validated, and not

`finish()` and the validator (12/12, `validation.json`): the decor rules on
the built and on the re-imported boxes (Root 3fw × 0.2 × 3fd; Floor and Wall
bodies 0.4 inside the footprint and at most 7 tall; each Wall piece's back on
z = 3fd/2 − 0.4; nothing collides), the names, the 1,500-triangle budget,
closed meshes, the FBX round trip. The kit refused the first flytrap (its
jaws reached 0.1 past the inset): moved back, it passes. **Not validated:**
anything in Studio; these are not for import.
