# The facade pieces, every style

Built by `tools/build_facades.py` to `MODELS.md`, "Facade (`Facade_*`) and
sign" and its "Where pieces meet" (written 2026-10-20 with this set). His
rulings of 2026-10-20 (GDD §5.4, A.1, decision log): walls stand only round
the tiles a player owns, so a facade is pieces the code puts on every
outline edge and corner; windows are bought and placed, one per wall
section, from four types ("CUSTOMIZATION IS KEY!!"), and a facade pack brings
its own version of all four. The kits' own pieces first, then the five
facade cosmetics, built as drafts from the one-line looks he said yes to.
**He judges the look.**

Seven pieces in every set: `Facade_Wall` (plain), `Facade_Window_TwinSash`,
`Facade_Window_Arched`, `Facade_Window_Round`, `Facade_Window_Wide`,
`Facade_Entrance`, `Facade_Corner`.

| Set | What it is | Its look |
|---|---|---|
| `haunted_manor/` | Haunted Manor's kit facade | The approved `Lobby` front wall and arch, carried over |
| `frostfang_lodge/` | Frostfang Lodge's kit facade | The approved `Lobby` front wall and arch, carried over |
| `gothic/` | `Cosmetic_GothicFacade` (pass FacadeGothic) | Dark slate, pointed windows, red stained-glass trim, small gargoyles on the corners |
| `neon/` | `Cosmetic_NeonFacade` (pass FacadeNeon) | Dark panels with glowing cyan and magenta tubes round the windows |
| `candy/` | `Cosmetic_CandyFacade` (pass FacadeCandy) | Pink wafer walls, white icing dripping from the top, striped posts |
| `pirate/` | `Cosmetic_PirateFacade` (pass FacadePirate) | Weathered ship planks, round porthole windows, rope trim, a lantern on each corner |
| `slime/` | `Cosmetic_SlimeFacade` (the Starter Pack) | Green walls with slime dripping off the sills |

Each set: `fbx/` (seven FBX), `manifest.json`, `validation.json` (with its
`assembly`), `import_fixup.luau`, `review/sheet.png` (the layout, the
entrance with a 5-stud person, an outside and an inside corner, the plain
wall and the four windows from outside and from inside). All seven layouts:
`review/overview.png` (top row Haunted Manor, Frostfang, Gothic, Neon;
bottom Candy, Pirate, Slime). Staged for import in `blender/_import/` as
`<Style>_<Piece>.fbx` (the names repeat between sets; the import renames).

## Choices made in building it (not his rulings)

- **The arch stands outside the edge.** The contract puts the wall at z
  −0.62..−0.02, so the old Lobby arch (0..1 deep) stands 0.2 proud of the
  wall's outer face (front at z −0.82) and never inside the cell. Its
  lantern hangs in the arch's opening, its foot at least 7.5 above the
  threshold.
- **The four window shapes** (the GDD's names, the opening within x −4..4,
  y 3..13): TwinSash two panes 3.2 × 9 (the contract's two 4 × 9 could not fit
  inside x −4..4; MODELS.md's row says so now), Arched one lancet 5 × 9 up to
  12 (under the courses at 12), Round a circle 6.8 across, Wide 8 × 6.5 over
  a flower box on brackets. A style may reshape them: Gothic's twin is two
  lancets, its wide three, its round a rose; Pirate's twin is two portholes,
  its round one big one, its arched a round-headed stern window; Frostfang's
  and Candy's arched are round-headed.
- **Dark panes (`Glass`)**, inside and out: through a clear pane the street
  would see a room's own wall 0.02 behind it. His call (WAITING).
- **The entrance piece has no windows** ("solid to either side of it").
- **Candy's wafer is layers with cream between**, not a lattice of squares
  (`modelling/taste.md`: no texture grid).
- **Neon's tubes**: one round each opening, a twin sash's two cyan and
  magenta; no light on any but the entrance (`_fixup_lights`).
- **The corner post has a bead up its outer edge** (a candy cane on Candy, a
  rope on Pirate): at an inside corner the post is buried in the two walls,
  and the bead is what shows there.
- **Where pieces meet** (MODELS.md): a detail proud of the wall keeps clear of
  the piece's ends, so at an inside corner it never runs into the other wall
  (Candy's drips stop short of the ends; Pirate's rope went round the windows
  after it was cut at every joint). A wall's end face takes the post's
  colour, and its top and bottom dip 0.02 over the last 0.64, so where the
  post lies on two walls at an inside corner nothing flickers. A first try
  slanted the ends instead: it left a crack of light at every joint (the
  blind review found it), so pieces in a row meet face to face.
- **Budgets, a draft** (MODELS.md's table): 1,500 a plain wall, 2,500 a
  window, 3,000 the entrance, 800 a corner. Counts are in each set's README.

## Validated (Blender only)

Every piece: `finish()` refused it until it passed, and `validate()` passed it
again on the re-imported FBX: the colliding parts' boxes exactly the
contract's (`Wall` x −6..6 y 0..17 z −0.62..−0.02, the entrance's pieces apart
round a 9 × 9 clear opening, `Post` its square), nothing else colliding, y
0..17, nothing past x ±6 (±12), nothing more than 0.2 inside the edge, the
ends' wedge, every window's openings open across their whole width and height
seen through the wall and within x −4..4, y 3..13, the rest of the face
covered, nothing hanging in the entrance below 7.5, the corner's details in
its quadrant, no coplanar overlapping faces, glow parts, budgets.

**The layout** (`validation.json`, `assembly`): the FBXs laid out as the code
would round an L of owned cells (10 outside corners, 2 inside, 13 joints,
every window type next to a corner): no detail of one piece runs into
another's, no faces of two pieces in two colours lie on each other. Each check
was proved by breaking a scratch copy (a sill too long, a window closed, the
arch lowered, the ends' dip removed, the ends' post colour removed): each
refused. The checks also found real faults on the way: overlapping colour
bands (Candy), a float's sliver at a plank edge (Pirate), frames lying on
the reveals, bars on panes, sills on frames.

**Not validated**: anything in Studio (the import, the fix-up, the look lit,
the glows), the code placing these (`HotelKit.facade`), a walker through the
entrance (its colliding boxes leave 9 × 9 clear). Studio runtime is not
tested.

## Blind reviews, 2026-10-20

Three rounds (skill `blind-review`): a reviewer per style on the first
pieces, a reviewer per style on the window pieces, one over all seven sheets.

**Confirmed and fixed**: a crack of light at every joint (the slanted ends);
the lanterns too small, Frostfang's half buried in its gable (now hung from
its lintel); windows crowding the corners (the openings are inside x −4..4
now); Pirate's two rows of portholes, its rope cut at every joint, its planks
reading as stripes (staggered plank ends, planks inside and over the arch),
its corner lanterns specks, its herb crate floating (brackets); the window
insides blank (frames out and in, the bars on both sides); the gargoyles and
the rose window too small; Gothic's stained glass a hazard checker (two reds
now); the Candy and Slime drips a comb (round strands, fat bulbs, uneven);
the slime too dark and sitting on the arch instead of running off it; sills
under round windows floating (none now but Slime's); the arched windows
breaking the courses at 12; the Gothic entrance rose unlike the window rose
(traced the same now); the inside corner showing no post (the bead); the
icing drips crowding the cherry.

**Round three** (all seven sheets): fixed: a ledge inside every round window
(no sill under a circle now, but for Slime's slime), Gothic's entrance rose
touching the coping (smaller, between the crown and the coping), Candy's cherry
lost among the drips (bigger, the drips kept off it). False: "the transom over
the arch is not glass" is the far wall seen through the arch's head; the twin
sash's pier inside is covered by its two inner frames. His call: the band of
plain wall over every window, Haunted Manor, Gothic and Neon reading alike
from above, Pirate's corner lanterns high on the corner, Neon's chevron, the
flower box's height.

**False**: views through an opening show the far wall of the layout (a
"filled tympanum", "two portholes in the lunette", "a black void in the
arch"); the inside corner's post is buried by contract (it was the bead that
was missing); gaps in the lineups are the render's spacing; the grey floor
seen through the arch read as a shut door (the review floor is dark now).

**His call** (`WAITING.md`): the approved Frostfang gable reads as a thin line
from above, and Haunted Manor's pointed gable as a wire; the windows' scale
(9-stud panes on a 17-stud storey) and their sill heights; the dark glass;
Neon's entrance reading as a loading bay; the inside faces plain colour
bands, as the old lobby wall's were.

## Known, outside these sets

- The two lobby cosmetics (`Cosmetic_BatBunting`, `Cosmetic_FairyLights`,
  `blender/cosmetics/hotel/`) were fitted to the old arch, whose front was at
  z 0; on `Facade_Entrance` they sit inside the wall (they reach z −0.29).
  `build_cosmetics_hotel.py` checks them against the kits' `Lobby.fbx` and
  needs to check against the `Facade_Entrance` FBXs instead.
- One corner piece serves both kinds of corner, so Gothic's gargoyle and
  Pirate's lantern stand in the nook of an inside corner too. A
  `Facade_CornerInner` the code puts at concave corners would let them stay
  on the outside ones only (the code knows which is which).
