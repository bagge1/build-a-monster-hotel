# Street trees: the forest round Creepy Lane, first drafts

Built 2026-10-19 by the street session, for August's review: every look here
is a draft he judges (WAITING §0 and §2). His idea (GDD §5.4, WAITING §2.18):
a forest round the street "so it does not look like a big lawn", bare and
crooked trees and some firs for Frostfang. Rebuilt by
`tools/build_street_trees.py` on `tools/monster_kit.py` (headless Blender 5.2,
a few seconds):

```
blender -b --python-exit-code 1 -P tools/build_street_trees.py [-- norender] [-- grey] [-- only Tree_Fir]
```

**The look in one line:** low-poly night-forest trees in the monsters' toy
style: three bare purple-brown or bleached Haunted Manor trees (one with a
hollow and a pair of warm eyes in it), a dark fir for both locations and a
snowy fir for Frostfang. `review/sheet.png` (Workbench, not in git) shows the
five in a row beside a 5-stud person; `review/silhouettes.png` the first grey
silhouettes; `review/blind/` the review pictures.

## The models

| Model | Triangles (800) | LOD_Proxy (100) | Height | Root (the collider) | Parts | Forest |
|---|---|---|---|---|---|---|
| Tree_Crooked | 756 | 73 | 29.1 | 3 × 29 × 3 | Body | Haunted Manor |
| Tree_Bare | 780 | 73 | 34.8 | 3 × 35 × 3 | Body (bleached) | Haunted Manor, Frostfang (a few) |
| Tree_Hollow | 784 | 75 | 21.9 | 5 × 22 × 5 | Body, Dark, Glow_Eyes_1, Glow_Eyes_2 | Haunted Manor, rare; turned to face the street |
| Tree_Fir | 260 | 80 | 36.0 | 10 × 36 × 10 | Body, Trim (needles) | both |
| Tree_SnowFir | 350 | 80 | 33.2 | 9.5 × 33 × 9.5 | Body, Trim, Light (snow) | Frostfang Lodge |

Which trees stand where, and how many, is the code's (`src/shared/Forest.luau`,
GDD Appendix A.1): a seeded scatter of about 650–700 round the street, each
plot's band drawn from its location's set, the hollow 4 % of Haunted Manor's.

## What the models are made of

- **Frame.** Standing on z = 0, the trunk's foot centred on the origin,
  upright; no front but the hollow's eyes (Blender −Y, Roblox −Z). The code
  plants each 0.6 studs deep and turns it at random, the hollow toward the
  lane.
- **Root is the only collider** (MODELS.md, "Street scenery: trees"): a
  column the trunk's foot wide, or a fir's lowest tier's reach, so a person
  walks into the trunk or the needles, never into a branch's box.
  `ForestRenderer` sets `CanCollide` on it; every mesh is `Box`, non-colliding.
- **One part per colour, no textures**, merged by colour (MODELS.md rule 7).
  The eyes are `Glow_Eyes_1/2` (Neon; no light: hundreds of trees).
- **LOD_Proxy** per model, its colour what the tree reads as from afar (a
  fir's needles, not its trunk); `ForestRenderer` shows it beyond 260 studs.
- **The hollow is carved** (a boolean in the build script, `carve()`), the
  dark and the eyes inside it.

## Validated, and not

**Validated in Blender** (`finish()` at build, `validate()` on the re-imported
FBX, `validation.json`): part names round-trip and are the contract's (Root,
Body, LOD_Proxy, the need list per tree); at most six parts; triangle budgets
(800 + proxy 100) and the per-mesh cap; one material and one UV layer per
part; closed geometry (the carved trunk too); no coplanar faces between
pieces; height within 10 % and within 22–40 studs; nothing under the floor;
the foot centred on the origin (a gnarled trunk by its ring's centroid); the
hollow's eyes a mirrored pair on the front; Root's size and place.

**Not validated:** anything in Studio: the import, the colours arriving, the
pivot `import_settings.luau` sets, the look at night among hundreds of its kind
at 0.8–1.25 scale, the proxy swap, a person walking into a fir's collider.

## Blind review 2026-10-19 (skill `blind-review`, four rounds)

Four fresh reviewers (Fable) on new pictures after each round of fixes.
**Confirmed and fixed:** firs' lowest tiers at head height and a reviewer
walking under them (round 1: tiers raised; round 3, when that read as an open
skirt over an invisible wall: skirts brought down near the ground, the
collider out to the lowest tier); the trunks' feet reading as pots or plinths
(rounds 1–4: a steeper, shorter flare, planted 0.6 deep); bark near-black and
in three unrelated browns (one purple-brown for every living trunk, the dead
tree bleached); the hollow tree's sawn-off branch ends, flat top and a hollow
that read as a disc stuck on the bark (tapered, forked branches; the top
rising into a branch; a hollow carved into the trunk, the eyes inside it,
lowered to a person's eye height; more gnarl and a burl); the crooked and
dead trees reading alike (a real zigzag; a snapped top and a broken limb on
the dead one); twigs too thin for a phone; snow hidden under the tiers above
(now from just over each rim); fir trunks like poles; trees in the scatter as
close as 7 studs (now at least half a cell, 11); the hollow's eyes facing into
the woods (`Forest.FacesStreet`).
**False:** branch joints "not joined" (every branch starts on a point of the
trunk's own centre line, its start radius under the trunk's there); a "hole"
in the hollow (the lit lip of bark); snow missing from below (it lies on the
tops; the game's camera is raised); aliasing at forest distance (beyond 260
studs a tree is its proxy); the review grove's mix and spacing (hand-placed,
not the scatter's).
**His call (WAITING §2.20):** whether the hollow tree reads as a tree with a
face (wanted) or as a hooded figure; blunt twig tips (round 3 wanted them
blunter against shimmer, round 4 read them as cut); branches as faceted
ribbons and plain joints without a swelling (the low-poly budget: a knuckle is
about 40 of a tree's 800 triangles); the snow caps' green rims; the two bare
trees' likeness from the raised camera.
**Round 4's fixes** (the feet, the hollow's height, depth and gnarl) were
checked by Claude in the renders, not by a fifth reviewer.

## Importing (skill `import`)

Staged 2026-10-19 in the main checkout's `blender/_import/` (the five
`Tree_*.fbx`, beside another session's batch). After August's import, run
this folder's `import_settings.luau` in the Edit datamodel, read back in a
separate call, and save each as `assets/Scenery/<Tree>.rbxm`:
`ForestRenderer` looks for them in `ReplicatedStorage.Scenery`, a mapping
this branch adds to `default.project.json` (Rojo needs a restart once it is
merged). Until then the forest draws Luau blockouts.

**Imported 2026-10-19 evening.** August imported the five with both hotel
kits' batch; `import_settings.luau` ran in the Edit datamodel and was read
back in a separate call: 21 meshes, all `Box`, no `Default` left, none
colliding (`ForestRenderer` sets `CanCollide` on `Root`), no
`SurfaceAppearance`, `Root` the hidden `PrimaryPart` with the pivot at its
foot, `LOD_Proxy` hidden 5/5. Saved as `assets/Scenery/<Tree>.rbxm` with
`tools/save_imports.py` (4,966–5,420 bytes; the decoded bytes deserialized
with `Root` as `PrimaryPart`, and a `rojo build` to XML shows it on all five
with every mesh id). **Not synced yet:** `ReplicatedStorage.Scenery` does
not exist in Studio until August restarts `rojo serve`, so the synced copies
are not read back and the forest still draws its blockouts; the Workspace
copies are deleted (the files are the source). Not seen in the game.
