# Dev notes

Platform behaviour that cost real time to discover. Almost all of it fails
**silently** or with a misleading symptom, which is why it is written down
rather than left to be rediscovered. Search this file for the API's name before
concluding that something failed or cannot be done.

Seeded 2026-10-19 from Sector Omega's notes (2026-09-17 to 2026-10-18), with
the game-specific parts taken out and the measurements kept. Add this game's
own lessons at the end, dated, in the same shape: what happened, why it was
quiet, and the rule (→).

---

## Rojo

### `rojo serve` reads `default.project.json` once, at startup

Scripts hot-reload; the project file does not. A change to `$properties` or to
the tree appears to do nothing. → It needs a restart, and **August runs Rojo**:
tell him, never restart it yourself.

### An `optional` path that did not exist at startup is never synced

`"$path": { "optional": "assets/Monsters" }` lets the project build before
the folder exists, but `rojo serve` resolves it once, at startup: a folder
created later (the first save of an import) is not watched, and nothing
appears in Studio while every other change syncs (2026-10-19: 69 models saved,
`ReplicatedStorage.Monsters` absent, deleted modules removed fine). →
Create a mapped folder (with a `.gitkeep`) **before** August restarts
`rojo serve` for a new mapping, or ask for one more restart.

### Rojo names a file's root instance after the file

A `.rbxm` whose MeshPart was saved as `Asteroid_01_Boulder_LOD0` and filed as
`BoulderLOD0.rbxm` is called **`BoulderLOD0`** in the game. Only the root is
renamed; a model saved as the importer's `Model` wrapper keeps its inner names.
→ **The file name is the contract.** Code finds templates by the file's name,
so renaming a file renames what the code finds. Check a reorganised `assets/`
with `rojo build default.project.json -o check.rbxlx` and read the names
before anything is played.

### A folder `default.project.json` maps belongs to Rojo alone

- **Rojo syncs a copy in beside yours; it does not replace it.** An import left
  in the place under a mapped folder stands beside the file's copy, two
  identical models, and `FindFirstChild` returns either. Nothing errors.
- **Rojo deletes what exists only in Studio** when it rebuilds a mapped folder.
  Nine fresh imports sitting in `ReplicatedStorage.WeaponTemplates` were
  deleted when the files on disk were moved into subfolders, and had to be
  imported again.
- **Moving a mapping leaves the old folder behind**, unmanaged and going stale:
  2,559 instances still replicated to every client after `Structures` moved to
  `ServerStorage`.

→ Imports go into **Workspace**, never into a mapped folder. Before moving or
renaming anything under `assets/`, look in Studio for instances with no file
yet and save them first. After moving a mapping, delete the old folder in Edit
(the MCP can) and have August publish.

### A MeshPart Rojo creates again can arrive with no mesh

Moving 14 hull files into class folders made Rojo create every template again:
**ten came out with every MeshPart empty** (`MeshId` blank) and drew as
textured boxes. Nothing errored and the game ran. The files were fine; Studio
lost the meshes on the way in (under load, ~300 meshes at once, is the guess).

A script cannot set `MeshId`/`MeshContent` (capability error, even from the
MCP). → What works: `AssetService:CreateMeshPartAsync(Content.fromUri(id))`
then `part:ApplyMesh(built)`, with the part's own fidelities passed in and its
`Size` put back; the ids come from `rojo build` to XML. The repair lives in the
place, so it lasts only once August publishes. **After anything that makes Rojo
create templates again, count empty MeshParts before trusting a playtest**, and
have the server warn at start for any template part with no mesh.

### Rojo's live sync drops `PrimaryPart`

2026-10-19, eleven imports saved over or beside their `.rbxm` while `rojo
serve` ran: **six synced templates came out with `PrimaryPart` nil** (both
kits' `Lobby` and `HotelSign`, two of seven cosmetics), the rest with it. The
files are fine: the 69 models synced at Rojo's start all have it. Nothing
errored at sync; the plot build failed later on `lobby.PrimaryPart`. →
`HotelKit` sets `PrimaryPart` to `Root` on every clone it takes (`rooted`).
**After an import, count templates with no `PrimaryPart`** with the sync check
(skill `import`, step 5), and never let other code take a template's ref
properties on trust.

### `rojo serve` dies when a temp file vanishes under it

A tool that saves atomically (write `Foo.luau.tmp.<n>`, rename it over
`Foo.luau`) can panic Rojo 7.7. → `default.project.json` carries
`"globIgnorePaths": ["**/*.tmp", "**/*.tmp.*"]` from day one.

### Studio keeps running a stale copy

When the plugin is not connected, the Rojo server still answers and Studio runs
yesterday's scripts while the repository is correct. → Before trusting a
playtest, compare every script's `#Source` in Studio against the file sizes in
git (a check of only the scripts you touched missed twelve stale ones once). A
stale tree is a **Connect** for August, under Studio's **Plugins** tab.

---

## Properties a script cannot set, and values that lie

### Some properties throw from a game script

`Workspace.FallenPartsDestroyHeight`, `Workspace.StreamingEnabled` and
`MeshPart.CollisionFidelity` need plugin capability and **throw** from an
ordinary script. An unguarded throw in a system's `Init()` takes down every
system that would have loaded after it. → Set Workspace ones in the project
file under `Workspace.$properties`; set `CollisionFidelity` at import (below).
**Wrap each bootstrap phase in a `pcall`.**

### Workspace properties are clamped without a word

| Written in the project file | What the engine holds |
|---|---|
| `FallenPartsDestroyHeight: -100000` | **−50,000** |
| `StreamingTargetRadius: 2000` | **1,024** |

`StreamingTargetRadius` is also not scriptable, so nothing can read it. →
Probe behaviourally (parts at known distances, see which reach the client).
**1,024 is a hard ceiling.** A structure larger than that uses
`ModelStreamingMode = Persistent`.

### A Part larger than 2,048 a side is clamped, about its centre

`Size = (3000, 15000, 1500)` reads back `(2048, 2048, 1500)`, no warning. A
part sized to span two points and placed at their midpoint loses the overflow
at both ends (a 3,120-stud beam started 540 studs ahead of its gun). → For
something that never collides, stretch a 2,048 part with a `SpecialMesh`
(`Brick`, `Scale` is not clamped); anything solid or textured is built from
several parts.

### `Terrain` is a `BasePart`

A loop that destroys every `BasePart` under Workspace throws on it. Skip it.

---

## Imported meshes

### A `SurfaceAppearance` makes `Material` do nothing

`Material = Neon` on a MeshPart that carries its imported `SurfaceAppearance`
renders pixel-identical to Plastic. The colour map may already look lit up
close, so it is easy to miss; it never emits. → Anything meant to glow is
**its own part**, and the code destroys its `SurfaceAppearance` before setting
the material. Neon washes mid-tones toward white: deepen the colour (a blue
went from `105,147,178` to `48,110,190`).

### Studio's FBX importer can upload a texture that is not the texture

A model imported looking right and rendered as flat grey tint, with every map
set to an id that existed. The importer's own upload was broken; re-uploading
the identical PNG and repointing the map fixed it at once. A re-import goes
through the same path and reproduces it. Seen twice.

→ When a mesh draws flat tint with its maps set, **upload the PNGs yourself
and repoint the maps.** To tell a UV fault from a texture fault, build a debug
atlas (eight saturated colours in the real grid): two minutes, and the first
two "obvious" tests gave confident wrong answers. A thumbnail lookup is
**not** a check: it returns the placeholder and `Completed` either way.

### The importer bakes each part's rotation into its vertices

Every MeshPart arrives at orientation 0,0,0, centred on its own bounding box.
Rotated copies of one mesh arrive as **separate** `MeshId`s; a mirror image is
always a second mesh (no negative scale). The origin's **position** survives as
the part's pivot, but the **pivot's rotation is the FBX axis conversion** (−90°
about X on every part), so `PivotTo` on a model whose `PrimaryPart` is one of
them turns it on its side.

→ A joint (a hinge, a turret) arrives as a marker part or an attachment, or
from the set's manifest, never from a part's CFrame. Place an imported model
with `TranslateBy`, or set `WorldPivot` to a plain `CFrame.new(pos)` first.
Read positions from `GetPivot()`, never orientations.

### `CollisionFidelity`: set at import, read back in a separate call

Imported meshes arrive at `Default`, which wraps a hollow in a filled block,
and even a non-colliding part keeps its computed shape in memory. It cannot be
set from a game script; **through the Studio MCP in Edit it works**, but a
read-back *in the same call* still says `Default`. It shows the new value a
call later. → Set it, then read back in a separate call; never set it twice
because the first read looked wrong (skill `import`). The value is serialized
into the `.rbxm`, so it costs nothing at runtime.

- `Box` on everything nothing walks or flies into; `PreciseConvexDecomposition`
  only on what must stay hollow. Precise costs memory per copy.
- **A decomposition closes small openings in a connected shell**: a 3-stud door
  through one thin-walled mesh was filled, though Blender shows it open. Pieces
  that do not touch are not bridged. → A wall with a door is pieces standing
  apart around the door.
- **It lids a ring floor**: a round floor and its slope as one mesh gave an
  invisible 2-3 stud step. → Anything round and walked on is separate wedges a
  hair apart (32 wedges, 0.03 apart); check with downward rays after import.
- Setting Precise on a big batch times the MCP call out and drops the MCP for
  ~5 minutes, **but the values land**. Set a group, wait for Studio to come
  back, set the next; one read-back covers all.
- The runtime fallback (`CreateMeshPartAsync` + `ApplyMesh`) works from a
  script but takes ~0.7 s a mesh. Sampled at four seconds it looks like a hang.

### Saving an import without Save to File

The MCP cannot write a file, but it can serialize a model, and Studio's log is
on disk. `tools/save_imports.py` does the round trip
(`SerializationService:SerializeInstancesAsync` → base64 → `print` → decode
from `%LOCALAPPDATA%\Roblox\logs\*Studio*_last.log`). It keeps Box and Precise
collision alike. Traps, all silent:

- `SerializeInstancesAsync` **never returns inside the MCP call that waits for
  it**: `task.spawn` it and collect in a second call.
- The log **cuts every line at 1022 characters**, with no marker: print in
  chunks of ~800 with the byte count and check it.
- A `StringValue` refuses 200,000 characters or more: keep big models in
  pieces.

### A texture-only change needs no import

When geometry, names and collision stay the same, new images and new ids are
enough: regenerate, upload, then rewrite the ids in the file (`rojo build` a
one-model project to `.rbxmx`, substitute the `rbxassetid://` lines, build back
to `.rbxm`, convert once more and diff: only id lines may differ).
**Fingerprint every id** against the disk texture before replacing it
(`AssetService:CreateEditableImageAsync` reads an upload back; eight per-cell
mean colours are unambiguous), even on a model you think is done.

### Budgets Roblox enforces

- Every uploaded image is scaled to **1024** on its longest side. Export at
  1024 or less so the preview shows what the game will.
- Roblox caps **triangles per MeshPart** at import (20,000 for a long time;
  confirm the current value).
- A MeshPart draws each face from the front only: a camera inside a mesh sees
  straight through it. Keep cameras out rather than doubling triangles.

---

## Streaming

### `StreamingEnabled` needs a `ReplicationFocus`

Parts stream by distance from each player's `ReplicationFocus`, which defaults
to their character. With no character, nothing streams in anywhere. The
deceptive part: `Folder` and `Model` are not `BasePart`s and replicate anyway,
so a client sees a model that exists, has the right name and **zero
descendants**. → Set `player.ReplicationFocus` yourself whenever the player is
not their character; count descendants, not instances.

### Far things are not on the client

Past ~1,024 studs a part has no copy on the client, and a far model's pivot can
read as the origin there. Read positions on the server. A structure everyone
must always see is `Persistent`, and every Persistent part is on every client
all the time: count them.

---

## Physics and constraints

### A `WeldConstraint` does not carry until the model is in Workspace

Set a root's `CFrame` before parenting and the root moves alone; on parenting,
the weld takes the gap as its offset for good (a part 5 studs off sat 10,000
off, for ever). A `Motor6D` or `Weld` is not affected. Every NPC ship was
placed this way for weeks: the server held their meshes far from their roots,
so streaming never sent them. → **Place a model built outside Workspace with
`Model:PivotTo`, never its root's `CFrame`.**

### An avatar on a conveyor drifts in X

An anchored part with an `AssemblyLinearVelocity` carries a standing avatar a
little faster than the belt in world **X** and exactly right in **Z**; the
avatar's velocity reads the belt's to the digit, only its position says
otherwise (+0.63 studs over 4 s at 20 studs/s). Along an axis it is a little
speed; on a diagonal belt it is a sideways push that walks a passenger off a
4-stud lane in ~15 s. → A diagonal conveyor needs keeping (ease a standing
rider back to the centre line), not only a velocity. Physics also runs slower
than wall time at low frame rates (6-15 fps in Studio): time by
`workspace:GetServerTimeNow()`, check `GetRealPhysicsFPS()`.

### A `Destroying` handler finds the model already taken apart

Signals run deferred, so a handler on `Model.Destroying` runs after `Destroy()`
finished: `PrimaryPart` is nil and the parts have no parent. → Keep what the
handler needs from before the destroy.

### Zero gravity makes `JumpHeight` zero

`JumpHeight` is converted with gravity: at `Gravity = 0` it is a take-off speed
of 0. Use `UseJumpPower` and `JumpPower`, which is the speed itself.

---

## Characters and cameras

- **`LoadCharacter` while `CameraType` is `Scriptable`** leaves `CameraSubject`
  on the old, destroyed humanoid; switching back to `Custom` follows *that*.
  Set `CameraSubject` to the new humanoid yourself when handing the camera
  back.
- **Roblox's PlayerModule moved** to `StarterPlayer.PlayerModule` and has no
  `GetControls()`. The avatar's move, jump and rotate are
  `StarterPlayer.PlayerModule.InputContexts.CharacterContext`: set its
  `Enabled`. Code waiting on `PlayerScripts.PlayerModule` finds nothing.
- **Anything camera-locked must move every frame**: repositioning on a
  threshold reads as a stutter. Pay for it with one `Model:PivotTo`, or better,
  bake it into the skybox.
- **A cursor can be left locked and hidden** when a join's camera state races
  the UI's. Hand the mouse back explicitly once per state change, whatever the
  camera did first.

---

## Lighting and sky

- **Blank skybox faces fall through to Roblox's procedural sky**, black at
  `ClockTime = 0` and blue with clouds in daylight. So a black background and a
  sun are mutually exclusive until the six faces carry a real texture; then
  `ClockTime` is purely a light-direction control. A dead texture id quietly
  gives the blue sky back.
- `StarCount` renders nothing with blank faces. Paint stars into the faces
  instead (1,477 camera-locked star parts were the biggest avoidable client cost
  in Sector Omega). A skybox pixel never reaches Bloom's threshold: bake halos.

---

## Interface

- **A `CanvasGroup` clips nothing under `ZIndexBehavior = Global`**, which is
  what a ScreenGui made with `Instance.new` starts with. Set `Sibling` on any
  ScreenGui built in code that clips with one.
- **A Decal or SurfaceGui on a part's `Top` face** is drawn with its top
  toward the part's **−X** and its left-to-right along −Z.
- **Roblox UI has no bloom.** A glow not baked into the image does not exist.
  Draw images white on transparent with the glow in alpha, and tint in code
  (`ImageColor3`, `UIGradient`): a colour change then needs no upload.
- **Developer product and pass icons are shown as they are** in Roblox's
  prompt, so they are drawn in colour; a pass icon is cropped to a circle.
- **Roblox's purchase prompt is CoreGui**: not in a capture and not clickable
  from the MCP. A real purchase is August's click.

---

## Data

### Studio and the published game save to different stores

Studio's DataStores are the published experience's own: a playtest writes
the very store players save to. `src/server/StoreNames.luau` names every
store apart (`MonsterHotel_Live_*` on a published server, the old
`MonsterHotel_*` in Studio, 2026-10-23), so test profiles and Studio
leaderboard scores never reach players. A new store is named through it.

### DataStores need a published place, and ProfileStore fails by succeeding

A never-published place has `PlaceId = 0` and no DataStore, and Studio API
access can only be switched on after publishing (Experience Settings belongs
to an experience). Without access **ProfileStore falls back to a mock** and
every read and write succeeds for the whole session; the only symptom is that
the next session starts from the template. → Wait for
`ProfileStore.DataStoreState` (`NotReady` / `NoInternet` / `NoAccess` /
`Access`, settles asynchronously) and warn loudly on anything but `Access`.
**Verify persistence by rejoining, never by reloading**: ProfileStore writes on
session end. No local place file: open the published experience.

- `UpdateAsync` whose transform returns nil **cancels** the write and leaves
  the key. Delete with `RemoveAsync`.
- One key per day for a log that many servers write runs into the per-key
  write limit on a busy day: key by day *and* user.

### Output printed while a session is torn down never reaches the log

Stopping play, or kicking the last player, loses everything printed after it.
→ A rule that only runs at logout (a settlement, a save) needs a way to run on
demand, or it can never be observed.

---

## Audio

- **Look audio ids up, never recall them.** The 2022 privacy change killed most
  ids in old tutorials and free models, and a dead id plays silently. Search the
  Creator Store; verify with `Sound.IsLoaded` and `TimeLength`.
- **A Sound must be in the DataModel to load**: unparented, it reports
  `IsLoaded` false for ever, even after `PreloadAsync` says `Success`. Parent a
  batch to a folder in `SoundService`, wait, read, destroy the folder.

---

## The Studio MCP

How to drive a playtest with it (keys, clicks, walking, captures) is skill
`playtest`. What the platform does underneath:

- **`require` from the MCP gets its own copy of a module**, with empty state:
  a stateful service reports an empty world while the world plainly is not.
  Pure shared modules are safe; for a service's live state, read what it
  publishes (attributes, instances), or run a `Script` parented in the
  running server (it shares the game's module cache) that writes its answer to
  a `workspace` attribute. What the MCP's thread may do has changed over time
  (2026-10-02 it could not require a synced module at all; 2026-10-05 it could
  again): try the direct way first, fall back to a temporary
  `src/server/<Name>.server.luau` that Rojo syncs, never committed.
- **In Edit, the MCP's module cache outlives every Rojo sync**: it tests the
  module as it was at the first `require`. Run anything that requires shared
  modules in the **Server datamodel of a playtest**, or `require` a `:Clone()`.
- **A `require` of a module with side effects runs them again** (one that
  rolled a map seed published a second map).
- **`FireServer` works from the Client datamodel**: an end-to-end test can fire
  a remote and read the result back.
- **`DataStoreService` works from Edit and from a playtest's server** on the
  published place, and what it touches is the live store.
- **The MCP cannot start a playtest straight after stopping one**: the start
  times out and every later one says `Start play hasn't finished yet`.
  Pressing **Play** in Studio clears it. A running playtest keeps the scripts it
  started with.
- **`upload_image` takes URLs, not paths**: serve the folder with
  `python -m http.server` on 127.0.0.1 for the call. **Five images per call**:
  a 16-image call timed out after uploading, leaving ids nobody knows.
- No `HttpService`, so no fetching files from inside Studio.

---

## Windows and tools

- **`perl -pi` with a `\x{...}` escape double-encodes UTF-8**: every `§`
  becomes `Â§`, silently in two of three cases. Use the Edit tool for anything
  with a non-ASCII character; check bulk edits with `grep -rl 'Â§\|â€' src/`.
- Windows PowerShell 5.1 has no `&&`/`||`; PowerShell 7 does.
- **Claude's shell eats one level of backslashes in a heredoc** (2026-10-19):
  a doubled backslash written into a `python - <<'PY'` script reached Python as
  a single one, so a Luau `
` in a replacement became a real line break (an
  unclosed string) and a Windows path's `` became a backspace character in
  WAITING.md. → Edit Luau strings and Windows paths with the Edit tool, or
  build them in Python from `chr(92)`; check a file with a control-character
  scan after any scripted edit of a path.

---

## This game's notes

<!-- New entries below, dated: what happened, why it was quiet, the rule. -->
