# What the code needs from a model

For whoever builds geometry for this game: Claude (`CLAUDE.md`).

**What arrives from Blender is visual only.** Collision, mass, welds, physics,
emissive materials, sound, and anything that moves or glows are added on the
code side at runtime. That separation is what lets the art be replaced without
changing how anything behaves.

It only works if the model can **say where things are**, and the only language
it has for that is **names and attachments**. Every name in this document is a
load-bearing interface, not a convention. A part called by its contract name
is lit, driven or found; the same geometry called `thing_final_2` gets nothing,
silently, and looks like a modelling mistake. Names are nearly free to add
while a set is being built and expensive to retrofit: when in doubt, split the
part and name it.

**Write a kind's section before its first model**, and make the kit's
`finish()` and the set's validator enforce it. Sector Omega wrote its
mounting rules after twenty hulls and rebuilt every one of them
(`D:\Roblox\playbook\RETROSPECTIVE.md`).

**What to read.** Grep this file for `^#{2,4} ` and read the sections the job
names:

| Job | Sections |
|---|---|
| Any model | The rules; What a model costs to draw; Checklist before handing a set over |
| <!-- a kind --> | <!-- its section --> |
| Code that reads a model | the section for the name the code looks up: grep the name |

---

## The rules everything else follows from

**1. If it glows, it is its own part.** An imported `SurfaceAppearance` makes
`Material` do nothing (`DEVNOTES.md`). The code strips the appearance from
emissive parts before lighting them, and it can only do that per part. Glow
parts are named `Glow_<Colour>_<n>` <!-- confirm the scheme for this game -->.

**2. If it moves, it is its own part.** A door that opens, a lift that rises,
a lid, a wheel: each is a separate part so a constraint or a weld can drive it.
Anything merged into its parent is welded solid for ever.

**3. One physical feature, one part.** Five nozzles modelled into one mesh get
one effect, centred in the middle of nothing: nothing in the code can know
where five mouths sit inside one mesh.

**4. Modules that belong together share one origin.** A set delivered as
separate models is authored in one frame, so placing one places them all.
Where two modules join, an attachment on each says so (`Connect_<name>`).

**5. Attachments name the places code has to find**: a spot a player stands,
a pad, a door threshold, a slot something is placed in. Geometry cannot be
searched for meaning; an attachment called `Pad_3` is found in one line. **An
attachment's orientation matters as much as its position.** The importer loses
every part's rotation (`DEVNOTES.md`): a direction is an attachment or a
marker, never a part's orientation.

**6. A person is <!-- N --> studs tall, and everything a person uses is built
for that.** Seats, doors, stairs, railings, walkways, counters: all sized for
the game's person (`CLAUDE.md`, "The scale of a person"), never for Roblox's
default avatar.

**7. Split what the rules name, and merge everything else.** Rules 1-3 pull
toward many parts, and Roblox charges for parts: every part of a moving model
has its transform updated every frame. A part earns its own existence by
glowing, by moving, or by being something the code has to find. Everything
else (trim, plating, struts) is merged into as few meshes as its materials
allow.

---

## What a model costs to draw

- **A distant model is one mesh: `LOD_Proxy`.** Every large or moving model
  carries one: a few hundred triangles (500 is the starting ceiling),
  silhouette and base colour only, no texture, authored in the model's own
  frame so it overlays exactly. **It arrives hidden** (`Transparency = 1` at
  import, the only part an import hides). Made last, from the finished model.
- **Repeated features are one mesh**, copied: parts sharing a mesh and a
  material are instanced and draw nearly as cheaply as one. A mirror image is a
  second mesh (no negative scale), and the importer uploads **rotated** copies
  as separate meshes.
- **Textures: 1024 at most, and shared.** Roblox scales every image to 1024.
  Parts of one material share one texture set; a `SurfaceAppearance` is up to
  four images, so each unique material costs four. No texture grid
  (`taste.md`).
- **Triangles**: `RenderFidelity` stays `Automatic`. Roblox caps triangles per
  MeshPart at import (20,000 for a long time; confirm). A budget per kind of
  model, stated in each set's README beside its real count:

  | Kind | Triangles |
  |---|---|
  | <!-- kind --> | <!-- budget --> |

- **Transparent surfaces: few and large.** Every transparent part is
  depth-sorted against every other, every frame. A window strip is one part.
- **Collision is set at import.** A mesh the code makes non-colliding still
  keeps a computed shape in memory: `Box` on every mesh at import,
  `PreciseConvexDecomposition` only where a person or a thing must get inside
  (the set's `validation.json` lists them as `collision_precise`). A round
  walked floor is wedges; a wall with a door is pieces apart round the door.
- **What a client holds**: a template only the server reads goes to
  `ServerStorage`. Count Persistent parts: each is on every client all the time.

---

## Checklist before handing a set over

- [ ] Every part the rules name is its own part, called by its contract name.
- [ ] Every place the code finds is an attachment, with its orientation.
- [ ] Clearances measured against the game's person.
- [ ] `LOD_Proxy` for a large or moving model, made from the finished model.
- [ ] Triangles within the kind's budget, per mesh under the import cap.
- [ ] `collision_precise` written by the validator.
- [ ] The README says what was validated and what was not.
