# tools/ index

What a session reads instead of a whole kit: each kit's purpose, its constants
and its functions with the line they start on (`:n`). Each kit's section is
kept by whoever changes that kit; add your own kit's section, never edit
another's.

## monster_kit.py

The shared kit for every monster (MODELS.md, "Monsters and street NPCs"). A
build script is, per species, its shapes and a call to `finish()`, then
`finish_set()` and `validate()` once for the set (`build_monsters_l1.py` is
the pattern). Frame: Blender -Y is the front, +Z up, +X the monster's left,
1 unit = 1 stud; Roblox (x, y, z) = Blender (-x, z, y). Headless only; the
one preview is a Workbench sheet (`-- norender` skips it).

### Constants

- `MONSTER_BUDGET` :50 (4,000), `PROXY_BUDGET` :51 (300), `MESH_TRIANGLE_CAP` :52
- `HEIGHT_TOL` :53, 10 % of Species.luau's `look.height`
- `GLOW_WORDS` :56, `EXTRA_PARTS` :59 (`Skin`, `Trim`, `Dark`, `Light`), `MARKERS` :60, `PART_RE` :61, every part name a monster may have
- `SPECIES` :84, Species.luau's height, colour, eyes and shape per id, read from the source

### Functions

- `start_set(set_dir)` :119 an empty scene writing to `blender/<set_dir>/`
- `begin(sid, set_dir, colours=None)` :132 start a species; `colours` for the extra parts and glows (sRGB)
- `rings(part, spec, n, wave, matrix, name, radial)` :179 a closed solid through horizontal rings (the base of every shape)
- `lathe(part, profile, at, n, sy, wave, rot)` :220 revolve [(z, r)]
- `ball(part, at, r, n=12, k=6, rot, name, radial)` :226 an ellipsoid
- `on_ball(at, r, x, z, out)` :235 a point on an ellipsoid's front
- `limb(part, p0, p1, r0, r1, n=10)` :244 a tapered capsule
- `box(part, at, size, bevel, rot)` :256
- `prism(part, outline, y_front, depth, rot, pivot)` :268 a flat-fronted convex solid (carved eyes, a tiara)
- `arc_shell(part, profile, t0, t1, thick, at, n, sy)` :287 a closed shell over an arc (a cape, a collar)
- `pair(fn, *args, mirror=[...], **kw)` :315 a call and its mirror across x
- `front_y(profile, z, x, at, sy, out)` :334 a point on a lathe's front
- `eyes(at, r, pupil, shine, rr)` :346 `Glow_Eyes_1/2` with a Dark pupil and a Light glint
- `marker(name, at)` :362 `Nameplate` / `Hand` as a 0.2 marker part
- `coplanar_overlaps(objs)` :385 lifted from ship_kit; faces of two pieces in one plane, overlapping
- `finish(note='')` :569 the contract checks, Root, LOD_Proxy, budgets, FBX, the model's record; refuses a bad model
- `finish_set(set_dir, offsets=4.2, sheet=True)` :680 manifest.json, import_settings.luau, the .blend, the sheet
- `import_luau(records)` :721 the import step's Luau (PrimaryPart, pivot, markers to attachments, colours, collision, proxy hidden)
- `validate(set_dir, species)` :819 re-import each FBX and check it; writes validation.json

Internal: `_material` :142, `_object` :154, `_matrix` :170, `_tris` :374, `_closed` :447, `_bounds` :457, `_join` :464, `_uv` :487, `_proxy` :500, `_sheet` :786.

## build_monsters_l1.py

Location 1's ten monsters (Haunted Manor), one function per species; output
`blender/monsters/haunted_manor/`. `-- only Slime,Ghost` builds a subset.
