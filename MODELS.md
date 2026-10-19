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
| A room, an amenity, the lobby, the stairs, a facade, decor | Hotel kit |
| A monster, a hunter, the bus | Monsters and street NPCs |
| Code that reads a model | the section for the name the code looks up: grep the name |

---

## The rules everything else follows from

**1. If it glows, it is its own part.** An imported `SurfaceAppearance` makes
`Material` do nothing (`DEVNOTES.md`). The code strips the appearance from
emissive parts before lighting them, and it can only do that per part. Glow
parts are named `Glow_<Colour>_<n>` (`Glow_Warm_1`, `Glow_Eyes_1`); the colour
word is the code's palette key (`Warm`, `Cold`, `Eyes`, `Magic`).

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

**6. A person is 5 studs tall (the standard avatar, his ruling 2026-10-19),
and everything a person uses is built for that.** Seats, doors, stairs, railings, walkways, counters: all sized for
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
  | A room or amenity | 6,000 (a 3×3 suite with its decor slots empty) |
  | Lobby, stairs | 8,000 each |
  | A facade | 10,000 |
  | A decor piece | 1,500 |
  | The hotel sign | 3,000 (draft) |
  | A monster | 4,000, plus `LOD_Proxy` 300 |
  | The bus | 8,000, plus `LOD_Proxy` 500 |

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

## Hotel kit

Everything a hotel is built from (GDD §5, Appendix A.1–A.2). One set per
location (`blender/hotel/<location>/`); one `.rbxm` per piece in
`assets/HotelKit/<Location>/`, which `default.project.json` maps to
`ServerStorage.HotelKit.<Location>`: **only the server reads these** (it builds
every hotel in Workspace, and the built hotel replicates).

**The frame.** Every piece is authored at rotation 0, **its door toward −Z**
(the street), with its origin at the **centre of its footprint on the floor's
walking surface** (y = 0 is where feet stand). A footprint is w × d cells of
**6 studs** (`Constants.Grid.CellSize`), so a 2×2 room is 12 × 12 studs, a 2×3
is 12 × 18 (18 along Z), a 3×3 is 18 × 18. **Nothing may stand outside the
footprint**: the cell next door is somebody's hallway. A floor is 12 studs; walls
stop at 10 (`Constants.Grid.WallHeight`), so the slab above has room.

**Every piece has one `Root` part**: invisible, anchored, `CanCollide` off,
`CanQuery` off, the footprint's size × 0.2 tall, centred on the origin. It
carries every attachment below. The code places a piece with `PivotTo` on the
model's pivot (= `Root`), never by a part's `CFrame` (`DEVNOTES.md`).

**How attachments travel** (the first set, 2026-10-19). FBX carries no
attachments: they live in the set's `manifest.json`, and the set's generated
`import_fixup.luau` creates them after import, sets `Root` as the invisible
`PrimaryPart` with the pivot on the origin, sets `Box` collision, and lights
the glows (Neon, the palette colour, one light on each `_1` glow), so a
delivered model needs no runtime set-up.

**Part names a set may use** besides those below: `Floor`, `Bed` (the bed
part), `Centrepiece`, `Furniture`, `Dressing`, `Rug`, `ArchLeft`,
`ArchRight`, `ArchTop`, `Planter_<n>`, `Crest`, `Step_Up_<n>`,
`Step_Down_<n>`, `Landing`, `Divider`, `Rail_Top`; a decor piece's mesh is
`Body`. Room walls are named as the blockout names them: `Wall_Back`,
`Wall_Left`, `Wall_Right`, `Wall_FrontLeft`, `Wall_FrontRight`, `Wall_Lintel`.
**Doorways are open arches**: no code opens a `DoorLeaf` yet, and a closed
leaf would block every guest.

### Rooms and amenities (`<PieceId>`, e.g. `StandardRoom`, `SnackBar`)

| Name | What | The code |
|---|---|---|
| `Root` | The part above | Placement; every attachment |
| `Door` (attachment) | The middle of the door's threshold, on the floor, **its LookVector pointing out** of the room | Cleaning and request prompts; the guest's last waypoint before the bed. Must sit over the cell `Grid.doorInside` names: at rotation 0 on the −Z wall, at x = (floor((w−1)/2) + 0.5) × 6 − w × 3 |
| `Bed` (attachment) | Where a guest rests, facing the way it lies | The guest's destination |
| `Decor_1`–`Decor_3` (attachments) | Where a decor piece stands, its LookVector the way the piece faces | Decor placement (`Pieces.DecorSlots`) |
| `Sign` (attachment) | Outside, above the door | The room's name and its state (vacant, dirty, a request) |
| `DoorLeaf` (part) | The door that swings, hinged at its own `Hinge` attachment | Opened when a guest passes (rule 2) |
| `Glow_<Colour>_<n>` | Lamps | Lit by the code (rule 1) |
| `Wall_<n>` | Walls, **in pieces apart round the door** (`DEVNOTES.md`, "A decomposition closes small openings") | Collision `Box` each |

The door opening is at least **4 studs wide and 7 tall** (a 5-stud person).

### Lobby (`Lobby`)

The front two rows of floor 1 (12 × 2 cells: 72 × 12 studs), authored with its
origin at the **middle of its front edge** on the walking surface; the street
is toward −Z.

| Name | What | The code |
|---|---|---|
| `Root` | 72 × 0.2 × 12 | Placement |
| `Entrance` (attachment) | The front door's threshold, LookVector toward the street | Where guests walk in |
| `Desk` (attachment) | The front desk's counter, LookVector toward the guests | Check-in prompt |
| `Queue_1`–`Queue_4` (attachments) | Where waiting guests stand, 1 nearest the desk | The desk queue |
| `Till` (attachment) | The till | Collect prompt |
| `Spawn` (attachment) | Where the owner appears | The plot's spawn |
| `SignBoard` (attachment) | Out front, the sign's face, LookVector toward the street | The hotel sign (§3) |
| `Trap_1`–`Trap_3` (attachments) | Trap slots for Hunter Night (§8.1) | Not used yet |

### Stair core (`StairCore`)

Cells x 10–11, z 2–3 of every floor: 12 × 12 studs, one floor high (12 studs),
origin at its footprint's centre on the lower floor's walking surface. Steps at
most **1.2 studs** rise and at least **1.5 studs** tread; flights at least 4
studs wide; **the landing at least 4 studs deep** (a 2-stud landing jammed a
walker against the divider, 2026-10-19); a railing on every open side.

| Name | What | The code |
|---|---|---|
| `Bottom`, `Top` (attachments) | The foot and head of the storey's stairs, on the walking surface | Where a guest's walk up starts and ends |
| `Path_1`, `Path_2`… (attachments) | The turns between, in order (the landing's two ends) | A guest walks Bottom → Path_n → Top |

### Facade (`Facade`) and sign (`HotelSign`)

The exterior shell round a hotel of `Floors` floors is built by the code from
pieces per floor: `Facade_Wall` (one cell wide, one floor high) and
`Facade_Corner`, each origin at its base centre, outside face toward −Z.
`HotelSign` carries `Board`, a part whose front face (−Z) takes the sign's
SurfaceGui (a Decal or SurfaceGui on a part's `Front` face is the plain case).

### Decor (`Decor_<DecorId>`, e.g. `Decor_Candles`)

Origin at the **centre of its base**, front toward −Z. At most 4 × 4 studs of
footprint and 7 studs tall, so three fit a 2×2 room. Glows are their own parts
(`Glow_Warm_1` for the candles' flames).

---

## Monsters and street NPCs

Monsters are drawn **by each client** (GDD §13.2): the server sends where a guest
is, and the client clones its model. So these templates go to
`ReplicatedStorage.Monsters` (`assets/Monsters/`), one `.rbxm` per species,
**named the species' id** (`Slime`, `VampireCount`, `Species.luau`).

**The frame.** Authored standing on y = 0, facing −Z, origin at the centre
between its feet (or under its body). Heights against the 5-stud person:
`Species.luau`'s `look.height` is the target (a Slime 3, a Werewolf 6.5).

| Name | What | The code |
|---|---|---|
| `Root` | Invisible, anchored, `CanCollide`/`CanQuery`/`CanTouch` off, 2 × height × 2, bottom at y = 0 | Moved along the path; the model's `PrimaryPart` |
| `Body` | The main mesh: one part, so a mutation's colour and material land on it | Tinted for Shadow, Golden, Glitched, the event ones (§4.5) |
| `Glow_Eyes_1`… | Eyes, their own parts | Lit; the Shadow mutation's "glowing eyes" |
| `Nameplate` (attachment) | Above the head | The guest's wish list (§4.3), the request bubble (§4.4) |
| `Hand` (attachment) | The hand that holds a staff prop | Staff roles (§4.6) |
| `Animations` (folder) | `Walk`, `Idle`, `Happy`, `Sad`, `CheckIn`, `Staff` (GDD §12) | Played by the client |

A mutation's scale is the client's `Model:ScaleTo` (Tiny 0.5, Giant 1.5), so a
model must look right at both.

**How markers travel** (the first set, 2026-10-19). FBX carries no
attachments: `Nameplate` and `Hand` (the right hand) arrive as 0.2-stud marker
parts, and the import step turns each into an Attachment of that name under
`Root` and deletes the part. The same step sets `PrimaryPart = Root`, hides
`Root`, sets a pivot on the floor (cancelling the importer's −90° X turn,
`DEVNOTES.md`), sets every part's colour from the set's `manifest.json`, and
removes any imported SurfaceAppearance (it would stop a mutation's tint). The
set's `import_settings.luau` does all of it.

**Colour parts.** Besides `Body`, a monster may have one flat-coloured part
each called `Skin`, `Trim`, `Dark` and `Light`, untextured. A mutation tints
every one of them; the eyes and `Glow_*` parts keep their own colour.

### Hunters (`Hunter`) and the bus (`NightBus`)

Same frame and `Root` rule. `Hunter` carries `Nameplate`. `NightBus` is
authored facing +X (the way it drives in, from the west), its `Root` the size
of the bus, with `Door` (attachment) where guests step out, and
`Glow_Warm_<n>` for its windows and lamps.

**Hunter** (the first set, 2026-10-19): Root 2 × 5 × 2; `Nameplate`; no `Hand`
and no eyes; budget a monster's (4,000 + 300); colour parts as a monster's.

**NightBus**: Root 24 × 9 × 8, no `Nameplate`. `Door` (a marker with its
facing) on the floor 0.6 studs outside the right side (+Z, the stop's side),
looking +Z. `Wheel_1`–`Wheel_4` (front-left, front-right, rear-left,
rear-right) are their own parts. `Glow_Warm_1` all the glass, `Glow_Warm_2`
and `Glow_Warm_3` the left and right headlamps (the code hangs its headlight
on `_2`), `Glow_Warm_4` the roof lantern, `Glow_Warm_5` the tail lamps.

---

## Checklist before handing a set over

- [ ] Every part the rules name is its own part, called by its contract name.
- [ ] Every place the code finds is an attachment, with its orientation.
- [ ] Clearances measured against the game's person.
- [ ] `LOD_Proxy` for a large or moving model, made from the finished model.
- [ ] Triangles within the kind's budget, per mesh under the import cap.
- [ ] `collision_precise` written by the validator.
- [ ] The README says what was validated and what was not.
