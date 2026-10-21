# Souvenir_Base: every species' souvenir

GDD A.11.3 (one souvenir per species, about 27 at launch) as the triage
proposed: **one base model the code colours and badges per species**
(Scrutiny 2026-10-21; that souvenirs share one base is August's call,
WAITING §2.38). To `MODELS.md`, "The souvenir". Built by
`tools/build_rare_decor.py`; a draft (2026-10-21). **Not seen in Studio.**

## The model (1 x 1, Floor, top 3.67, 776 triangles of 800)

A keepsake on display: a dark wood pedestal (foot, step, shaft, top) with
two bands, a gold-framed name plaque on its front, and on top a velvet
cushion with four tassels holding a medal, under a glass cloche on a ring.
No knob on the cloche: from above it would cover the emblem's middle.

| Part | What | The code |
|---|---|---|
| `Body` | Pedestal and plaque frame, atlas colours | — |
| `Cushion` | The cushion, one flat colour (crimson) | `Color` = the species' `look.colour`, texture cleared |
| `Trim` | The bands, the cloche's ring, the tassels, one flat colour (gold) | `Color` = a second colour (PLACEHOLDER: `look.colour` × 0.6, as the sheets show) |
| `Medal` | r 0.4, its top flat at y 2.67 | The emblem on its `Top` face |
| `Badge` | 0.8 x 0.5, its front flat at z -0.67 | The species' name on its `Front` face |
| `Glass` | The cloche, closed, not colliding | May make it glass |

Authored crimson and gold, so an untinted clone reads as the Vampire
Count's.

## Validated (by the build, `validation.json`)

The kit's decor checks (footprint, inset, layer, nothing colliding, no
coplanar faces, budget 800), nothing floats, no `Use`, and its own check:
every part above present, `Cushion` and `Trim` one colour each, `Medal`'s
top and `Badge`'s front each one flat plane (0.50 and 0.40 square studs)
with nothing of another part over or in front of it (the cloche excepted),
on the built and the re-imported triangles; the FBX round trip.

## Not done

- Anything in Studio; whether a `Decal` on `Medal`'s `Top` lands as
  expected (DEVNOTES: drawn with its top toward −X).
- The emblem images (UI work) and the second colour's rule (his).
- A wall-hung souvenir (A.11.3 allows `Wall`): only the floor piece.
- A blind review.

## Review

`review/souvenir_sheet.png`: four tints (Vampire Count, Slime, Ghost,
Werewolf from `Species.luau`) with the cloche hidden, as built (opaque in
Workbench), and from above. Workbench on light grey only.

## Staged

`blender/_import/Souvenir_Base.fbx`; it goes to `assets/Souvenirs/`
(`ServerStorage.Souvenirs`, a folder `default.project.json` gains at its
save, so Rojo restarts).
