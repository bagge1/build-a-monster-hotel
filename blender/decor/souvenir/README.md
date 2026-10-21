# Souvenir_Base: every species' souvenir

GDD A.11.3 (one souvenir per species, about 27 at launch) as the triage
proposed: **one base model the code colours and badges per species**
(Scrutiny 2026-10-21; that souvenirs share one base is August's call,
WAITING §2.38). To `MODELS.md`, "The souvenir". Built by
`tools/build_rare_decor.py`; a draft (2026-10-21). **Not seen in Studio.**

## The model (1 x 1, Floor, top 3.70, 778 triangles of 800)

A prize rosette under a tall bell jar on a low plinth. A dark wood plinth
(foot, shaft, top at 1.65) with two bands and a gold-mounted name plaque
on its front; on its top a rosette lying level, its middle 0.08 behind the
plinth's: 16 rounded pleats (r 0.7 to 0.8), a rim, the medal 1.2 across,
and two tails splayed 20 degrees that run to the top's front edge and fold
over it, notched. Over it a bell jar (r 0.96, straight to 2.8, domed to
3.7) on a foot ring. No knob: from above it would cover the emblem.

**Blind review 2026-10-21** (context-free, on the first sheets): the first
model (a crimson cushion with a 0.8 medal, four tassels at the rim, a
square top) read from above as a loudspeaker, and its 0.8 emblem as too
small. Confirmed; redesigned as above: from above a scalloped ribbon disc
with its two tails (an award's sign) and a medal 1.2 across (2.25 times the
first's face); from the front and the raised camera the jar's dome and the
plaque (1.08 x 0.46, was 0.8 x 0.5). The medal's face stays level rather
than tilted to the camera, as the reviewer offered: the importer loses part
rotation, so only a level face takes a `Top` decal, and level reads best
from the build camera. `Cushion` is renamed `Ribbon` (`MODELS.md` with it;
no code read the name).

| Part | What | The code |
|---|---|---|
| `Body` | Plinth and the plaque's gold mount, atlas colours | — |
| `Ribbon` | The rosette's pleats and tails, one flat colour (crimson) | `Color` = the species' `look.colour`, texture cleared |
| `Trim` | The bands, the jar's foot ring, the medal's rim, one flat colour (gold) | `Color` = a second colour (PLACEHOLDER: `look.colour` x 0.6, as the sheets show) |
| `Medal` | r 0.6, its top flat at y 1.88 | The emblem on its `Top` face |
| `Badge` | 1.08 x 0.46, its front flat at z -0.86 | The species' name on its `Front` face |
| `Glass` | The bell jar, closed, not colliding | May make it glass |

Authored crimson and gold, so an untinted clone reads as the Vampire
Count's.

## Validated (by the build, `validation.json`)

The kit's decor checks (footprint, inset, layer, nothing colliding, no
coplanar faces, budget 800), nothing floats, no `Use`, and its own check:
every part above present, `Ribbon` and `Trim` one colour each, `Medal`'s
top and `Badge`'s front each one flat plane (1.13 and 0.50 square studs)
with nothing of another part over or in front of it (the cloche excepted),
on the built and the re-imported triangles; the FBX round trip.

## Not done

- Anything in Studio; whether a `Decal` on `Medal`'s `Top` lands as
  expected (DEVNOTES: drawn with its top toward −X).
- The emblem images (UI work) and the second colour's rule (his).
- A wall-hung souvenir (A.11.3 allows `Wall`): only the floor piece.
- A second blind review of the redesign.

## Review

`review/souvenir_sheet.png`: four tints (Vampire Count, Slime, Ghost,
Werewolf from `Species.luau`) with the jar hidden, with it as built (opaque
in Workbench: its shape, not its glass), and from above with it hidden.
Workbench on light grey only. The set's `topdown.png`, `topdown_phone.png`
and `raised.png` show four in a study.

## Staged

`blender/_import/Souvenir_Base.fbx` (re-staged, the redesign); it goes to `assets/Souvenirs/`
(`ServerStorage.Souvenirs`, a folder `default.project.json` gains at its
save, so Rojo restarts).
