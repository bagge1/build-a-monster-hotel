---
name: import
description: Takes a finished Blender set from FBX into the game - staging the batch in blender/_import/, August's one action (he imports into Workspace and says "importerat"), setting CollisionFidelity and hiding LOD_Proxy through the Studio MCP, reading it back in a separate call, saving the .rbxm with tools/save_imports.py, checking the synced copy and cleaning up. Use it whenever August writes "importerat", "importerad", "jag har importerat", "imported", "klart i Studio", or says the FBX is in Workspace, and whenever a model is handed to him and its batch has to be staged ("stage", "staga", "lägg i _import", "redo att importera", a model ready for Studio).
---

# Import: from FBX to `assets/`

**An import is one action of August's.** He imports the FBX and says
*importerat*; the staging, the settings, the save and the checks are Claude's.
Nothing else is asked of him. Where the files land (`assets/<folder>/<Name>.rbxm`,
the file name being the instance name, server-only templates in
`ServerStorage`) is `CLAUDE.md`, "The art handoff".

Everything below runs through the Studio MCP in the **Edit** datamodel, never
in a playtest, whose changes are thrown away.

## The steps

0. **Claude stages the batch** when handing it over: copy the batch's FBX
   files, and only those, into one folder, `blender/_import/`, so he picks them
   all in one dialog: every kind together, never a folder per kind. Look at
   what is already staged there first (another session's batch) and keep it.
   **The folder holds nothing but the FBX to import** (his ask, 2026-10-19):
   an import leaves a `<Name>.fbm/` folder per FBX (its unpacked atlas);
   delete those, and the imported FBX, once the batch is saved (step 5).
   Name the folder when asking, and put the import in `WAITING.md` §0. Once the
   game has its first sets, write `tools/import_settings.py` to stage a batch
   and print step 2's Luau from the sets' own `validation.json`
   (`D:\Roblox\sector-omega\tools\import_settings.py` is the pattern).
1. **August** imports into **Workspace** (never straight into a folder Rojo
   syncs: Rojo deletes what exists only in Studio) and says *importerat*.
2. **Claude sets**, on each imported model:
   - `CollisionFidelity = PreciseConvexDecomposition` on the meshes in
     `collision_precise` of the set's `validation.json` (what a person walks
     into or a thing flies into), and `Box` on every other mesh;
   - `Transparency = 1` on `LOD_Proxy`, **the only part hidden at import**
     (the code hides every marker).

   ```lua
   -- Edit datamodel. One model per call when it is large.
   local precise = { ["<Model>"] = { "<MeshA>", "<MeshB>" } }
   for model, list in precise do
       local m = workspace:FindFirstChild(model)
       local set = {}
       for _, n in list do set[n] = true end
       for _, p in m:GetDescendants() do
           if p:IsA("MeshPart") then
               p.CollisionFidelity = set[p.Name] and Enum.CollisionFidelity.PreciseConvexDecomposition
                   or Enum.CollisionFidelity.Box
               if p.Name == "LOD_Proxy" then p.Transparency = 1 end
           end
       end
   end
   return "set"
   ```

   **A set's script too long to paste** (a hotel kit's `import_fixup.luau` is
   30–40 KB): write it to `src/server/_ImportFixup<Set>.luau` wrapped as
   `return function(only) ... end` (its `local ONLY = {}` becomes
   `local ONLY = only or {}`), let Rojo sync it, and call
   `require(game.ServerScriptService.Server._ImportFixup<Set>)({ names })` in
   groups of about ten. The server's init requires a fixed list, so the game
   never runs it. Delete the file when the set is saved; never commit it.
   **Two sets that share names** (`Lobby`, `StairCore`... in every kit): fix up,
   save and write the first set, rename its Workspace copies (`HM_Lobby`), then
   rename the second set's prefixed imports (`FrostfangLodge_Lobby` → `Lobby`)
   and fix it up. `save_imports.py write` keeps a name's latest print in the log.

   A large batch times the call out and drops the MCP for ~5 minutes, **but the
   values land**: set a group, wait for `list_roblox_studios` to show Studio
   again, set the next.
3. **Claude reads it all back in a separate call.** A `CollisionFidelity` read
   in the same call that set it still says `Default`, and shows the new value
   only a call later (`DEVNOTES.md`). Never report a set as done from the
   first call, and never set it twice because the first read looked wrong.
   Count per model: Precise, Box, any `Default` left, `LOD_Proxy` hidden.
4. **Claude saves** each model as `assets/<folder>/<Name>.rbxm` with
   `tools/save_imports.py`: `python tools/save_imports.py luau` prints two
   snippets; run the first (serialize, returns at once), then the second in a
   separate call (prints to Studio's log), then
   `python tools/save_imports.py write assets/<folder>/<Name>.rbxm ...`. The
   script's docstring and `DEVNOTES.md`, "Saving an import without Save to
   File", say why it is two calls and why it prints in chunks. A model saved
   under another name than the FBX gave it is renamed in Workspace first.
5. **Claude reads the synced copies back once** under `ReplicatedStorage` (or
   `ServerStorage`): collision, mesh ids and sizes against the Workspace
   import, **no empty MeshPart**, and a `PrimaryPart` on each (Rojo's live
   sync can drop it, `DEVNOTES.md`). Then deletes the Workspace copies and
   `ServerStorage._ClaudeSerialize`, empties `blender/_import/` of the batch
   (its FBX and the `.fbm/` folders the import left), strikes the import in
   `WAITING.md` and updates the set's README.

## Before and after

- **A new mapped folder must exist before Rojo starts.** An `optional`
  `$path` created after `rojo serve` started is never synced (`DEVNOTES.md`):
  when a set adds a mapping, create its folder with a `.gitkeep` before
  August restarts Rojo.

- **Before moving or renaming anything under `assets/`**, look in Studio for
  imports that exist only there and save them first: Rojo deletes them.
- After anything that makes Rojo create templates again (a move, a rename, a
  deleted mapped folder), count empty MeshParts before trusting a playtest
  (`DEVNOTES.md`).
- A walked structure: after the import, cast a grid of rays down over every
  floor and across every doorway, so a lid or a closed door is found by Claude,
  not by August.
- A texture-only change needs no import (`DEVNOTES.md`).
