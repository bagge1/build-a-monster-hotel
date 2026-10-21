---
name: modelling
description: How Claude models every model in this game in Blender, from August's picture to "importerat" - reading his picture, grey silhouettes beside a person, the shared kit, the set folder, validation, the LOD proxy, renders and image economy. Use it whenever August sends a picture, a sketch or a drawing ("en bild", "en skiss", "jag ritade", "så här ska den se ut"), says "modellera", "bygg", "gör en ny modell", "silhuetter", "varianter", "rendera", "ändra modellen", "flytta delen", "fel på modellen", or "model", "build", "silhouettes", "render"; whenever a model needs to change (a part in the wrong place, a missing marker, the wrong scale, a texture), a build script in tools/ is edited or run, the kit is touched, or a blockout in Luau is considered; and whenever he rejects something about how a model looks ("nej", "inte så", "ser fel ut"), since his no is written into taste.md.
---

# Modelling

The rules every job keeps are `CLAUDE.md`'s, "Who builds what": geometry in
Blender, never in Luau; a wrong model is fixed in its build script, never
worked round in code; the blockout exception and its two conditions. This is
the recipe.

Read before starting, and only what the job needs:

- `taste.md` (this folder): August's taste and how to read his pictures. Every
  rule there was a rejection. **A new no from him is written into it**, in his
  words, dated, in the same commit as the work that drew it.
- `MODELS.md`: the rules every model keeps, its cost section, and the section
  for this kind of model. Grep `^#{2,4} ` for headings; never work from memory
  of it.
- The kit's index (`tools/INDEX.md` once it exists), then only the functions
  you call.
- When resuming a set, its `README.md`: the set's state and his rulings live
  there, not in memory.

## The loop

His picture or sketch → Claude's reading of it plus questions → **grey
silhouettes beside a person at the game's scale** → he picks → detail, atlas,
`LOD_Proxy`, FBX, validator, set README → **blind review** of the renders and
triage (skill `blind-review`) → stage the batch and put it in
`WAITING.md` (skill `import`) → he imports and says *importerat* → skill
`import` → he looks in Studio. Given artistic freedom, he still reviews.
Before asking for a yes on a draft, describe it in one line. For a mechanism
he cannot picture from words, three grey variants and he picks one.

## One kit from the first model

Sector Omega's ship scripts were ~900 lines each, 600 of them copied helpers,
until the kit existed. **Anything that is not this model's own shape goes into
the kit** (`tools/<game>_kit.py`) before the second model: the materials and
atlas, the export, `finish()`, the validator, the silhouettes, the preview
renders, the proxy. A new model is then its geometry plus `finish()`.
`D:\Roblox\sector-omega\tools\ship_kit.py` and its `INDEX.md` are the pattern
to lift from.

**`finish()` refuses a bad model.** A rule that lived only in a document was
broken by every hull. Whatever `MODELS.md` requires (names, markers,
attachments, connected moving parts, no coplanar faces, clearances for a
person, triangle budgets) is checked by the build, and a fault stops it.

## Where a set lives

`blender/<kind>/<set>/`: the `.blend`, `fbx/`, `textures/`, `manifest.json`
(every part, joint and axis), `validation.json` (what the validator checked,
`collision_precise` among it), `review/` (his picture as
`review/reference.png`, the sheets) and a `README.md`. Only the README,
manifest, validation and his references are in git; the rest is rebuilt by
the script.

## Running Blender

```
"C:\Program Files\Blender Foundation\Blender 5.2\blender.exe" -b --python-exit-code 1 -P tools/build_x.py -- fast
```

`-- fast` for quick half-size previews while iterating (~5 s against ~35 s
for Cycles), the final Cycles sheet once before handing it over. Set
`scene.unit_settings.scale_length = 0.01` before export, or everything is
100× off. Run it yourself: August does not use a terminal. A script with
`'''` inside breaks an inline heredoc: write it to the scratchpad and run the
file.

## Geometry lessons

- Details sit 0.01-0.03 proud, never flush: coplanar faces z-fight in Studio.
- A moving part is one connected piece; check connectivity on any assembly of
  small pieces.
- The exact boolean fails silently, usually by losing the whole mesh: cutter
  shells never overlap, lofted cutters are triangulated first, and a cutter
  never shares faces or vertices with the skin it cuts.
- Anything laid on a curved skin follows its built facets (a ray onto the
  mesh), not the formula that made it.
- A detail placed from a side view must land on solid in 3D.
- **Render close-ups of joints** before handing over: overview previews do
  not show them.
- **The importer loses part rotation** (`DEVNOTES.md`): any joint or direction
  the code needs is a marker or an attachment, never a part's orientation.
- A piece a person uses is checked against the **whole 5-stud figure**, arms
  included (3.8 across): lying in a vessel means inside its walls, on its
  floor; sitting means a sheet with the person seated (thighs under a
  counter, feet on a foot ring). A line down the body's middle missed both.
- Anything meant to be seen in play is checked **from the game's own camera**,
  at its angle and its zooms, not only from the preview's.
- A measurement that must hold to hundredths is taken on the exported
  triangles, not the scene's faces.
- A walked floor that is round is separate wedges a hair apart; a wall with a
  door is pieces standing apart around the door (collision decomposition closes
  small openings, `DEVNOTES.md`).
- File and instance names are ASCII; a display name with å, ä or ö lives in the
  code's config.
- Roblox caps every part at 2,048 studs an axis: chain long things.
- Several sets built in parallel by agents stay one family only if the shared
  pieces and names exist first: the kit and the `MODELS.md` names before
  launching them.

## Proving a kit change

Build every affected set with the old and the new kit in scratch copies of
`tools/` and compare the FBXs mesh by mesh; a triangle count per part against
git HEAD is the quick check. Check `git status` for another session's edits to
the kit before touching it.

## Images are the largest cost in a session

- His reference: view it once whole; crops for detail at ≤ 800 px.
- Measuring a picture: read pixels with numpy, don't view it again. Fit a
  camera to a perspective picture rather than reading proportions by eye (a
  hull's wings came out a third too small by eye).
- While iterating: the fast half-size sheets. Never re-view an image that has
  not changed.

## Before a set is handed over

- [ ] `MODELS.md`'s checklist gone through for this kind of model.
- [ ] `finish()` ran clean; the set's validator passed and wrote
      `validation.json` with `collision_precise`.
- [ ] `LOD_Proxy` made last, from the finished model, for anything large.
- [ ] Close-ups of the joints rendered and looked at; the full sheet rendered
      once and sent to him.
- [ ] **Blind review** (skill `blind-review`): the sheet and close-ups with
      the 5-stud person sent to a fresh reviewer; every finding triaged in the
      README (confirmed and fixed, false with the reason, or his call in
      `WAITING.md`). He sees the set only after this.
- [ ] The README states what was validated and what was not; "Studio runtime
      is not tested" until something has been seen running.
- [ ] Staged in `blender/_import/`, the folder named to him, the import in
      `WAITING.md` (skill `import`).
