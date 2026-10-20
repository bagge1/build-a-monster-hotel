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
| A room, an amenity, the lobby, the front desk, the stairs, a facade, decor, a rug | Hotel kit |
| A monster, a hunter, the bus | Monsters and street NPCs |
| A tree | Street scenery: trees |
| Code that reads a model | the section for the name the code looks up: grep the name |

---

## The rules everything else follows from

**1. If it glows, it is its own part.** An imported `SurfaceAppearance` makes
`Material` do nothing (`DEVNOTES.md`). The code strips the appearance from
emissive parts before lighting them, and it can only do that per part. Glow
parts are named `Glow_<Colour>_<n>` (`Glow_Warm_1`, `Glow_Eyes_1`); the colour
word is the code's palette key (`Warm`, `Cold`, `Eyes`, `Magic`, and the
Neon facade's `Cyan` and `Magenta`).

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
  | The lobby | 10,000 (144 × 24 studs since the doubled scale: four times the first draft's floor, one per hotel) |
| The front desk | 3,000 |
  | Stairs | 8,000 |
  | A facade piece | 1,500 a plain wall, 2,500 a window, 3,000 the entrance, 800 a corner (draft, 2026-10-20: one stands on every outline edge of every floor) |
  | A decor piece | 1,500 |
  | The hotel sign | 3,000 (draft) |
  | A sign or lobby cosmetic | 2,000 (draft) |
  | A monster | 4,000, plus `LOD_Proxy` 300 |
  | A tree | 800, plus `LOD_Proxy` 100 |
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

**The scale** (his ruling, 2026-10-19 evening, `CLAUDE.md` "The scale of a
person"): the spaces are twice the first draft's, the things in them are not.
A cell is **12 studs**, a floor **18**, and every wall reaches the slab above.
Furniture, beds, counters, decor, doors (openings at least 4 × 7) and steps
(at most 1.2 rise, at least 1.5 tread) stay built for the 5-stud person;
a room gets more room round them, never bigger furniture.

**The frame.** Every piece is authored at rotation 0, **its door toward −Z**
(the street), with its origin at the **centre of its footprint on the floor's
walking surface** (y = 0 is where feet stand). A footprint is w × d cells of
**12 studs** (`Constants.Grid.CellSize`), so a 2×2 room is 24 × 24 studs, a 2×3
is 24 × 36 (36 along Z), a 3×3 is 36 × 36. **Nothing may stand outside the
footprint**: the cell next door is somebody's hallway. A floor is **18 studs**
(`Constants.Grid.FloorHeight`): a 1-stud slab and **17 clear**. Walls are **17
tall** (`Constants.Grid.WallHeight`), so they meet the underside of the slab
above; on the top floor they stand open to the sky.

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
`ArchRight`, `ArchTop`, `Counter`, `Till`, `KeyRack`, `Crest`, `Step_Up_<n>`,
`Step_Down_<n>`, `Landing`, `Divider`, `Rail_Top`; a decor piece's mesh is
`Body`. Room walls are named as the blockout names them: `Wall_Back`,
`Wall_Left`, `Wall_Right`, `Wall_FrontLeft`, `Wall_FrontRight`, `Wall_Lintel`.
**Doorways are open arches**: no code opens a `DoorLeaf` yet, and a closed
leaf would block every guest.

### Rooms and amenities (`<PieceId>`, e.g. `StandardRoom`, `SnackBar`)

Walls 0.4 thick and 17 tall, inside the footprint: `Wall_Back` the full width,
`Wall_Left` and `Wall_Right` between it and the front, the front wall in
pieces round the door, and `Wall_Lintel` over the door from 7 to 17.

| Name | What | The code |
|---|---|---|
| `Root` | The part above | Placement; every attachment |
| `Door` (attachment) | The middle of the door's threshold, on the floor, **its LookVector pointing out** of the room | Cleaning and request prompts; the guest's last waypoint before the bed. Must sit over the cell `Grid.doorInside` names: at rotation 0 on the −Z wall, at x = (floor((w−1)/2) + 0.5) × 12 − w × 6 (−6 for a 2-wide piece, 0 for a 3-wide) |
| `Bed` (attachment) | Where a guest rests, facing the way it lies: a room's 7 studs in from the back wall (z = D/2 − 7, facing −Z), an amenity's at z = −D/6 facing +Z (the centrepiece) | The guest's destination |
| `Floor` (part) | The room's floor, **one part**, its top the room's walking surface | Placed decor stands on its top; a floor finish is laid on it |
| `Bed`, `Furniture`, `Centrepiece` (parts) | The room's own furniture | Placed decor is kept off the 3-stud squares their boxes cover |
| `Sign` (attachment) | Outside, above the door: (door x, 8.2, −D/2 − 0.3) | The room's name and its state (vacant, dirty, a request) |
| `DoorLeaf` (part) | The door that swings, hinged at its own `Hinge` attachment | Opened when a guest passes (rule 2) |
| `Glow_<Colour>_<n>` | Lamps | Lit by the code (rule 1) |
| `Wall_<n>` | Walls, **in pieces apart round the door** (`DEVNOTES.md`, "A decomposition closes small openings") | Collision `Box` each |

The door opening is at least **4 studs wide and 7 tall** (a 5-stud person).

**Every room and amenity also has its mirror image, `<PieceId>_Mirror`** (his
ask, 2026-10-20: F flips a room to move its door, GDD A.1). Roblox has no
negative scale, so a mirror is a second mesh (`DEVNOTES.md`, "The importer
bakes each part's rotation"): the kit's `finish()` writes it from the same
geometry mirrored across x = 0 (faces turned the right way out), with every
attachment's x negated and its LookVector mirrored (`Door` at x = +6 for a
2-wide piece, `Hinge` on the other jamb), the same part names, and the same
checks. Nobody models it by hand. The code places `<PieceId>_Mirror` for a
piece saved with `m`; until it exists, F does nothing for that piece.

### Lobby (`Lobby`): the shell

**Retiring (his ruling, 2026-10-20):** there is no lobby strip any more; the
lobby is wherever the player puts the desk(s) (GDD §5.4, A.1). The front
wall and the arch become facade pieces (`Facade_Wall`, `Facade_Entrance`,
above "Facade"), and the floor is the owned tiles' slab. The `Lobby` model
below stays in the game only until `Facade_Entrance` exists; the code reads
`Entrance` from `Facade_Entrance` then.

The front two rows of floor 1 (12 × 2 cells: **144 × 24 studs**), authored
with its origin at the **middle of its front edge** on the walking surface;
the street is toward −Z. The front row is z 0–12, the back row z 12–24.

**A shell, nothing more** (his ruling, 2026-10-19, GDD §5.4: everything can
be rebuilt, the reception too). The desk, the till, the key rack, the benches,
the planters and the carpet are **pieces the player places** (`FrontDesk`
below, and decor: `Decor_Bench`, `Decor_UrnPlanter`, the rugs). The shell is:

- **A front wall** on the street edge (z 0–0.8, **17 tall**, up to the slab),
  with the entrance arch in the middle (opening 9 wide, 9 tall: a door, so
  not scaled) and tall windows (6 wide, y 3–12) at x −50, ±36, ±22 and 64.
  Two pieces apart round the arch, `Wall_FrontLeft` (x −72 to −5.5) and
  `Wall_FrontRight` (x 5.5 to 72), each exactly the blockout's box; the arch
  (`ArchLeft`, `ArchRight`, `ArchTop`), its lantern and the wall's sconces.
- **`Floor`**: the lobby's own floor over the whole 144 × 24, **one part, its
  top at most 0.1** above the walking surface (a hallway meets it with no
  step). A floor finish the player picks is laid on this part (below, "Floor
  finishes").
- **Nothing else.** Behind the front wall (z 0.8 to 24) nothing collides
  between y 0.15 and 17: the whole floor is the player's to build on.

`finish()` refuses a lobby that breaks these: the walls' boxes, the clear
floor, the entrance (4 × 7), and the floor's top.

The hotel sign's `SignBoard` and the traps' `Trap_n` were the lobby's until
2026-10-19; they are the **forecourt's** now (below, "Forecourt"), and a lobby
needs neither.


| Name | What | The code |
|---|---|---|
| `Root` | 144 × 0.2 × 24, centred (0, 0.1, 12) | Placement |
| `Entrance` (attachment) | (0, 0, 0): the front door's threshold, LookVector toward the street | Where guests walk in |
| `Spawn` (attachment) | (8, 0, 18), in the back row | The plot's spawn |

**The desk's points are mirrored onto the lobby.** Wherever the player puts
the `FrontDesk`, the code copies its `Desk`, `Clerk`, `Till` and `Queue_n`
onto the lobby's `Root` under the same names (`PlotService`), so whatever
finds the desk through the lobby keeps finding it. A lobby model never
carries those names itself.

### Front desk (`FrontDesk`)

The reception desk as a piece (GDD §5.4): **2 × 1 cells, 24 × 12 studs**,
exactly one per hotel, placed on floor 1 wherever guests reach it from the
entrance. Authored like every piece: rotation 0, **served side toward −Z**,
origin at the footprint's centre on the walking surface (x −12..12,
z −6..6). Built for the 5-stud person, at the old lobby desk's sizes:

- The counter x −4.5 to 4.5, z −4.0 to −2.2, its top (−4.7..4.7 by
  −4.2..−1.9) at **3.8**; the till on its +X end, a bell at the check-in
  spot, a lamp on its −X end.
- The clerk's space behind it (z −1.9 to 5.15), reached from both sides:
  **nothing collides** in x −12..−5 or 5..12 (y 0.15 to 7), so the clerk
  walks in round the counter's ends.
- The `KeyRack` against the back edge, x −2.6..2.6, z 5.15..6.0, at most 9.6
  tall, with its clock.
- Nothing outside the footprint; the queue stands in the hallway in front.

| Name | What | The code |
|---|---|---|
| `Root` | 24 × 0.2 × 12, centred (0, 0.1, 0) | Placement |
| `Counter` (part) | The counter and its top | Collides |
| `Till` (part) | The till | — |
| `KeyRack` (part) | The rack and its clock | Collides |
| `Desk` (attachment) | (0, 3.8, −4.2): the counter's served edge, LookVector −Z, toward the guests | Check-in prompt |
| `Till` (attachment) | (3.4, 3.8, −4.2), LookVector −Z | Collect prompt |
| `Clerk` (attachment) | (0, 0, 1.5), LookVector −Z | The Front Desk resident's post |
| `Queue_1`–`Queue_4` (attachments) | (0, 0, −8), (0, 0, −11), (0, 0, −14), (0, 0, −17), LookVector +Z (at the desk); 1 nearest. Guests beyond the fourth stand on, 3 studs further back each | The desk queue |
| `Glow_Warm_1` | The lamp's shade | Lit |

`Grid` keeps the two cells in front of the desk walkable and reached from the
entrance (the queue stands there).

### Stairs (`StairCore`, `StairCoreTop`): a piece

A stair is a **2 × 2 piece the player places** (GDD §5.4), one floor high:
it stands on floor f and joins it to floor f + 1 **on the same cells**.
Several may stand anywhere on the plot; one placed on the same cells and
rotation directly above another continues it (the old core's stack). The
models are the stair core's, unchanged: 24 × 24 studs, origin at the
footprint's centre on the lower floor's walking surface, **its open side
toward −Z** (the piece's front).

**15 steps a storey**, each 1.2 rise and 1.5 tread, as a switchback: the
flight up (`Step_Up_1`–`8`, x −12 to 0) climbs +Z from z −11.5 to the
`Landing` at 9.6 (z 0.5 to 12, 11.5 deep); the flight down (`Step_Down_1`–`7`,
x 0 to 12) comes back −Z to the upper floor at 18, its last step reaching the
front edge under the upper slab's 1-stud lip. Flights 12 wide; the landing at
least 4 deep; walls on the outer sides and the back and a `Divider` between
the flights, 18 tall. **`StairCoreTop`** is used where no stair continues
above: its walls rise 3.5 over the upper floor (21.5) and `Rail_Top` rails the
hole's front over the flight up.

**What the code builds round it:** the upper floor's slab gets a hole over
the stair's cells, but for a **1-stud lip along its front edge**; a slab rail
stops where a hole meets the plot's edge. `Grid` keeps the cell in front of
the flight up (the foot, front-left) walkable on floor f, and the cell in
front of the flight down (the head, front-right) walkable on floor f + 1.

| Name | What | The code |
|---|---|---|
| `Bottom`, `Top` (attachments) | (−6, 0, −11.75) and (6, 18, −11.75): the foot and head of the storey's stairs, on the walking surface | Where a guest's walk up starts and ends |
| `Path_1`, `Path_2` (attachments) | (−6, 9.6, 6.25) and (6, 9.6, 6.25): the landing's two ends | A guest walks Bottom → Path_n → Top |

### Facade (`Facade_*`) and sign (`HotelSign`)

**Walls only round what is owned** (his ruling, 2026-10-20; GDD §5.4, A.1).
The code walks the outline of the owned tiles on every floor and puts a piece
on each outline edge and at each of its corners; buying a tile moves the
outline out. Nothing here is a whole facade: every piece is **one cell edge**
(or two, for the entrance), so the same pieces wrap any shape the player buys.

**The frame of a piece:** origin at the **middle of the cell edge, on the
walking surface** of its floor (the slab's top). The owned cell is toward
**+Z**, the outside toward **−Z**. The wall stands **outside the edge**: its
inner face at z = −0.02 (never on the cell, so it never meets a room's own
wall face), its outer face at z = −0.62 (0.6 thick). It reaches from y = 0
to **17**, the slab above (`WallHeight`); the slab's edge is the slab's.

| Piece | Size (x × y, along × up) | What |
|---|---|---|
| `Facade_Wall` | 12 × 17, x −6..6 | A **plain wall**, no window (his ruling, 2026-10-20: windows are bought and placed) |
| `Facade_Window_<Type>` | 12 × 17, x −6..6 | The same wall section **with one window**, `<Type>` one of `TwinSash` (two tall narrow panes, 3.2 × 9 each: the old wall's two 4 × 9 windows, narrowed to fit x −4..4), `Arched` (one tall pointed arch), `Round` (a round moon window), `Wide` (a broad three-pane window with a flower box). The opening stays within x −4..4 and y 3..13 (a person's sill, under the slab), the rest of the section is wall; same frame, Root and collision rules as `Facade_Wall`, the wall round the hole in pieces |
| `Facade_Entrance` | 24 × 17, x −12..12 | Floor 1's front edge at x 5–6 only: the entrance arch in the middle (opening at least 9 wide and 9 tall, the approved arch's), solid to either side of it; the old `Lobby` front wall's arch and lantern move here |
| `Facade_Corner` | 0.64 × 0.64 × 17 | A post at an outline corner, filling the square at the vertex in the quadrant **−X, −Z** of its origin (the code turns it to the right quadrant); 0.02 proud of the walls' faces both ways, so it hides a convex corner's gap and a concave corner's overlap |

Window and sill details sit 0.01–0.03 proud (rule: coplanar faces flicker).
Nothing of a facade piece collides with a person **inside** the edge
(z > −0.02), and nothing reaches past x ±6 (±12 for the entrance), so two
pieces in a row meet end to end.

**Where pieces meet** (2026-10-20, so any outline the player buys is clean;
`tools/build_facades.py` refuses a piece that breaks it and lays every set out
round a convex and a concave corner to prove it):

- Only the colliding parts (below) collide, each a `Box`; nothing inside the
  edge collides, and a non-colliding detail reaches at most **0.2** inside
  it (a sill).
- A detail proud of the outer face by p stays **0.62 + p + 0.02** from the
  piece's ends (and an inside detail 0.65): at a concave corner the other
  wall's end and its details are there.
- A wall's **end face takes the corner post's colour** at its height, and its
  top and bottom **slope 0.02 over its last 0.64** at each end, under the
  post's top: at a concave corner the post's inner face lies on the wall's
  end, and two walls and the post would otherwise share faces in two colours
  (they flicker). Two pieces in a row meet face to face (a slanted end left a
  crack of light at every joint).
- The corner's details beyond its post stand only in the outward quadrant
  (never past x or z −0.1, through a wall), and only below 2.5 or above
  12.5, clear of the walls' windows and sills, but for a bead up its outer
  edge (within x, z −0.9), the one part of a corner that shows at a concave
  one (its post is buried in the two walls there).
- The windows are holes in the wall: seen through the wall (along Z),
  everything but `Glass` leaves each opening open across its whole width and
  height, within x −4..4 and y 3..13, and covers the rest of the face; a
  plain `Facade_Wall` covers all of it.

| Name | What | The code |
|---|---|---|
| `Root` | 12 × 0.2 × 0.6 (24 for the entrance), centred (0, 0.1, −0.32); the corner's 0.64 × 0.2 × 0.64 at (−0.32, 0.1, −0.32) | Placement |
| `Wall` (`Facade_Wall`, `Facade_Window_<Type>`); `Wall_Left`, `Wall_Right`, `ArchLeft`, `ArchRight`, `ArchTop` (`Facade_Entrance`); `Post` (`Facade_Corner`) | The colliding parts: `Wall` exactly x −6..6, y 0..17, z −0.62..−0.02; `Wall_Left` x −12..−5.5 and `Wall_Right` 5.5..12 the same; the arch's pillars x ±4.5..±5.5 up to 9 and `ArchTop` over 9, so the opening is 9 × 9 clear; `Post` exactly x −0.64..0, z −0.64..0, 17 tall | `Box` collision each |
| `Glass` (part) | The window panes, one part | Not colliding; the code may make it glass |
| `Dressing`, `Glow_<Colour>_<n>`, `LOD_Proxy` | Frames, sills, trim; lamps and tubes (rule 1; no light but the entrance's); the wall with its holes, flat | — |
| `Entrance` (attachment, `Facade_Entrance` only) | (0, 0, 0): the threshold, LookVector −Z | Where guests walk in; the lobby cosmetics hang from it |

**Every outline edge of every floor is walled**, the street side included
(his ruling, 2026-10-20, replacing the open street side above floor 1). Each
floor has its own outline: tiles are bought per floor, and a floor with no
tiles has no walls. The first draft's Wing
doorway is gone: residents never walk through it.

**One set of pieces per hotel kit** (`ServerStorage.HotelKit.<Location>`,
`assets/HotelKit/<Location>/Facade_Wall.rbxm` …) and **one per facade
cosmetic** (below, "Cosmetics"). Until a kit's pieces exist, `HotelKit.facade`
draws the same outline as a Luau blockout.

`HotelSign` carries `Board`, a part whose front face (−Z) takes the sign's
SurfaceGui (a Decal or SurfaceGui on a part's `Front` face is the plain case).
The sign is not scaled: posts and a 16 × 6 board at (0, 8, 0).

### Forecourt (`Forecourt`)

The ground between the lane and the hotel's front wall (his yes, 2026-10-19,
GDD §5.4): **24 studs deep**, the plots moved 24 studs back from the lane to
make it. Its first 8 studs from the lane are the **pavement**, which is the
street's (one strip along each side of the lane, built by `StreetService`,
where the bus's guests browse); the other 16 are the plot's **yard**, with a
**path 6 wide** from the pavement to the entrance arch. Built by the code for
now (a blockout in `HotelKit.forecourt`, in the plot's ground colours), inside
the plot's `Base` folder; a delivered `Forecourt` per hotel kit replaces its
geometry and nothing else.

Authored with its origin at the **entrance** (the middle of the plot's front
edge, on the walking surface), the street toward −Z: the yard is x −72 to 72,
z −16 to 0; the pavement beyond it, z −24 to −16, is not the model's.
Nothing stands on the path (x −3 to 3) or in front of the arch.

| Name | What | The code |
|---|---|---|
| `Root` | 144 × 0.2 × 16, centred (0, 0.1, −8) | Placement |
| `PathFoot` (attachment) | (0, 0, −16): where the path meets the pavement, LookVector +Z (toward the entrance) | Where a guest leaves the pavement for the hotel, and comes back to it |
| `SignBoard` (attachment) | (60, 0, −12): the stair-side corner of the yard, the sign's base, LookVector −Z (toward the street) | The hotel sign (§3) |
| `Trap_1`–`Trap_3` (attachments) | (−8, 0, −12), (8, 0, −12), (−8, 0, −4): beside the path, each with a clear 3 × 3 square round it, LookVector −Z | Hunter Night's traps (§8.1) |

### Cosmetics (`Cosmetic_<Id>`, e.g. `Cosmetic_PumpkinSign`)

What a player wears on their hotel (GDD §8.2 event shops, §10.2 facade packs,
the login calendar's day 7, a family's completion; `src/shared/Cosmetics.luau`
lists them). Templates in `ServerStorage.Cosmetics` (`assets/Cosmetics/`),
named the cosmetic's id. Visual only; the code anchors them and turns
collision off. Each slot has its own origin:

| Slot | Origin | Front |
|---|---|---|
| `Sign` | The centre of the hotel sign's `Board` front face | −Z, toward the street |
| `Lobby` | The lobby's `Entrance` attachment (the threshold, on the floor) | −Z, toward the street |
| `Facade` | The facade's own frames: a facade cosmetic is a **Folder** `ServerStorage.Cosmetics.<Id>` (`assets/Cosmetics/<Id>/`) holding its own `Facade_Wall`, the four `Facade_Window_<Type>`, `Facade_Entrance` and `Facade_Corner`, each to the "Facade" contract above, worn on any location in place of the kit's. Until its pieces exist, a colour scheme (`colour`, `trim`) on the blockout | −Z, toward the outside |

A sign cosmetic dresses the sign (it never covers the Board's text); a lobby
cosmetic hangs above the entrance and stays clear of a 5-stud person walking
in (its lowest part at least 8 studs above the threshold).

| Name | What | The code |
|---|---|---|
| `Root` | Invisible, its pivot the slot's origin | `PivotTo` onto the Board face or the Entrance |
| `Body` | The visible mesh, as decor's | — |
| `Glow_Warm_1`… | Flames and bulbs, their own parts | Neon, a light on `_1` (the set's `import_fixup.luau`) |
| `LOD_Proxy` | Hidden at import | LOD |

The set's build script checks both kits' `HotelSign` and `Lobby` on every
build (`tools/build_cosmetics_hotel.py`): a kit change to the sign or the arch
means rebuilding this set.

### Room plaque (`RoomPlaque`, one per hotel kit)

The wooden plaque over every room's and amenity's door (his ask, 2026-10-19:
a plaque instead of floating text). Origin at the room's `Sign` attachment
(0.3 in front of the wall's outer face), front toward −Z; its back lies on
the wall. About 4 × 1.3 studs, visual only (the code anchors it and turns
collision and rays off).

| Name | What | The code |
|---|---|---|
| `Root` | Invisible, inside the board | `PivotTo` onto `Sign` |
| `Board` | The board, its rim and its screws | — |
| `Face` | The flat panel in front, its front (−Z) face clear | A `SurfaceGui` on its Front: the room's name and tier, and its state on a second line |

### Decor (`Decor_<DecorId>`, e.g. `Decor_Candles`)

Placed by the player **on a grid of 3 studs** (a quarter cell), turned in
90° steps, in rooms, the lobby and the hallways (GDD §5.4). Origin at the
**centre of its footprint's base**, front toward −Z.

- **Footprint**: `fw × fd` squares of 3 studs (`Pieces` gives them), so the
  Root is `3fw × 0.2 × 3fd`. **The body stays 0.4 inside the footprint's edge
  on every side** (a piece at a room's edge then clears the 0.4 wall), at
  most **7 tall**. The footprint of a model already built is the smallest
  that holds its body by that rule: `ceil((size + 0.8) / 3)` squares.
- **Layer** (`Pieces`'s `layer`):
  - `Floor`: furniture and things standing on the floor; two never overlap.
  - `Rug`: flat, **at most 0.15 tall**, nothing above it; it may lie under
    `Floor` decor and under a room's own furniture, never over another rug.
    A rug runs to its footprint's edge (the 0.4 inset is not a rug's), so
    rugs meet edge to edge: a runner and a corner join into one carpet.
  - `Wall`: hung on or stood against a room's wall, **its back (+Z) face at
    z = 3fd/2 − 0.4** (on the wall's inner face); placed only with its back
    against a wall, never across the doorway.
- Glows are their own parts (`Glow_Warm_1` for flames). `Body` does not
  collide (a placed piece never traps a player).
- **The model agrees with `Pieces`**: its footprint and layer are its
  entry's `w`, `d` and `layer`, and the entry's `height` is the body's top
  to 0.3 (the build mode's ghost and the stand-in block are drawn from it).
  An id every kit has (`always`) has one height for several models and is
  held to its footprint and layer only. The kit reads `Pieces.luau` and
  refuses a mismatch (2026-10-20).
- **A seat** (rule 6): a piece a person sits on declares each seat in its
  build script (the kit's `seat()`, recorded in the manifest's
  `decor.seats`): its top **1.5 to 2.0** above the floor (the person's legs
  are 2), at least **1.2 deep**, **2 wide** a person, and **nothing above it
  for 3 studs**. A narrower seat names his ruling (the `Armchair` at 1 × 1,
  2026-10-20). The kit checks it on the built and the re-imported
  triangles. No attachment: no code seats anyone yet; the day one does,
  `Seat_<n>` goes here first.
- **No coplanar faces** (they z-fight, `DEVNOTES.md`): two of a piece's
  solids never share a plane facing the same way where both are seen; a
  detail sits 0.01 to 0.03 proud. The kit refuses a pair unless it is buried
  in a third solid, lies on the floor facing down, or (a `Wall` piece) lies
  on the wall's face (2026-10-20, lifted from the monster kit).

**Where the code lets it stand** (`Grid`, `Furnish`): inside one room's walls
(never across a wall, never in the 6 × 6 just inside the door, never on the
room's own `Bed`, `Furniture` or `Centrepiece` boxes, which the code reads
from the model), or on hallway and lobby floor. In a hallway a `Floor` piece
that reaches into the middle of a cell (where guests walk) makes that cell no
hallway, and is refused if it cuts a door off; one in a cell's corner leaves
it walkable. A room's preference tags are the tags of the decor inside its
walls; its decor points (from the price) set its tier.

### Floor finishes (code only)

A floor finish is a `Material` and a colour per kit (`Pieces.Finishes`),
chosen per room, for the lobby and for the hallways. The code lays it on the
piece's `Floor` part (it removes the part's texture and sets the material and
colour) and on the hallways' slabs; no model is needed. A model's `Floor` is
therefore **one part**, the walking surface, with nothing else merged into it.

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

## Street scenery: trees (`Tree_<Name>`)

The forest round Creepy Lane (his idea, 2026-10-19, GDD §5.4): every client
places the trees itself (`ForestRenderer`, a seeded scatter from
`src/shared/Forest.luau`), so the templates go to `ReplicatedStorage.Scenery`
(`assets/Scenery/`), one `.rbxm` per tree, **named its id** (`Tree_Crooked`).
Which trees stand behind a plot follows that plot's location (`Forest.Sets`).

**The frame.** Standing on y = 0, origin at the centre of the trunk's foot,
upright along +Y; no front (the scatter turns each tree at random). Heights in
studs against the 5-stud person and the 18-stud floor: a hotel of three
floors is 54 tall, and the trees stand 22–40.

| Name | What | The code |
|---|---|---|
| `Root` | Invisible, anchored, the trunk's foot × the tree's height × the foot (a fir's: its lowest tier's reach, so nobody stands inside its crown), bottom at y = 0 | The model's `PrimaryPart`; **the tree's only collider** (the code sets `CanCollide` on it, so a person walks into the trunk, not into a branch's box) |
| `Body` | The trunk and every branch, one mesh, bark-coloured | Drawn |
| `Trim`, `Light`, `Dark` | Flat-coloured parts: needles, snow, a hollow | Drawn |
| `Glow_Eyes_1`, `Glow_Eyes_2` | A pair of eyes in a hollow, on the spooky trees only | Neon (rule 1), never a light |
| `LOD_Proxy` | Silhouette and base colour, at most 100 triangles, hidden | Shown instead of the tree beyond `Forest.ProxyDistance` |

**What a tree costs**: hundreds stand round the street on a phone, so a tree
is **at most 800 triangles** beside a 100-triangle proxy, at most six parts,
no textures (one colour a part), and nothing that collides but `Root`.

---

## Checklist before handing a set over

- [ ] Every part the rules name is its own part, called by its contract name.
- [ ] Every place the code finds is an attachment, with its orientation.
- [ ] Clearances measured against the game's person.
- [ ] `LOD_Proxy` for a large or moving model, made from the finished model.
- [ ] Triangles within the kind's budget, per mesh under the import cap.
- [ ] `collision_precise` written by the validator.
- [ ] The README says what was validated and what was not.
