---
name: machine-setup
description: Setting up a machine or a session to work on this game - a fresh clone or the laptop (tools/setup_machine.py, the memory junction, rokit, wally, Blender, Python), and what a cloud session on claude.ai/code can and cannot do (no Studio, renders as files, an import batch committed). Use it when August says "ny dator", "laptopen", "klona", "sätt upp", "installera", "det funkar inte på andra datorn", "minnet saknas", "molnet", "cloud", "new machine", "fresh clone", "setup", when a tool such as rojo, wally, blender or numpy is missing, when the memory folder looks empty or unlinked, and at the start of any session running in the cloud.
---

# Machines and cloud sessions

## A machine

- **The repo**, cloned anywhere, then `python tools/setup_machine.py`, run by
  Claude, once. It makes Claude Code's memory folder for that path
  (`~/.claude/projects/<encoded path>/memory`) a directory junction to the
  repo's `memory/` (no admin needed), installs the tools `rokit.toml` names
  (`rokit install`: rojo, wally, stylua, selene), runs `wally install`, and
  reports what is missing. `--check` only reports. A memory folder Claude Code
  had already made is merged into `memory/` first and kept beside the junction.
- **Memory travels with git**: pull before starting, and commit a memory file
  with the work that changed it.
- **Not in git:** Roblox Studio with the Rojo plugin; the Claude desktop app,
  whose Studio MCP is how Claude drives Studio; the model and effort, set in
  the app; Blender 5.2 at `C:\Program Files\Blender Foundation\Blender 5.2\`;
  Python 3.12 with numpy and Pillow; rokit; the user-level
  `~/.claude/CLAUDE.md` (copy it from the other machine); the playbook at
  `D:\Roblox\playbook\`. The heavy parts of `blender/` are rebuilt by each
  set's script, or copied from the other machine.

## A cloud session

A session on claude.ai/code can model (Blender as the Python module `bpy`,
installed by a SessionStart hook; Sector Omega's
`.claude/hooks/cloud_blender.sh` is the pattern) but **cannot reach Studio**:
no import, upload, playtest or spec run. Its renders go to August as files in
the chat. An import batch it stages is committed (`git add -f
blender/_import/` plus the textures the FBX names), and the session that saves
it deletes them again. Nothing else under `blender/` that `.gitignore` keeps
out is committed.
