# Working on Build a Monster Hotel

How August and Claude work together is the user-level `CLAUDE.md`, which every
session loads: he decides and Claude builds, consult don't conclude, values
are his, no terminal, Rojo is his, the Nordic keyboard, the session and night
rules. This file is what this game adds. Where it came from, and why each rule
is here, is `D:\Roblox\playbook\RETROSPECTIVE.md`.

## The game

**Build a Monster Hotel** (`MonsterHotel` in code): a co-op venue-management
tycoon with a collection layer. Six hotels share one street and compete for the
guests the Night Bus brings, and rare monsters check in only at the best hotel
on the street. Mobile-first.

- **The design is `docs/GDD.md`** (v0.1 draft, 2026-10-19). It plays the part
  Sector Omega's `PLAN.md` did: design goes in before it is built, code comments
  point into its §-numbers, and his rulings are dated in its decision log (§18).
  Its numbers are starting values for tuning until he sets them.
- **The research behind it** is `research/reports/Roblox tycoon market and
  design.md` (2026-10-18), with its notes in `research/research_notes/`.
- Nothing is built yet: memory `phase-status`.

## Who builds what

**Claude builds the whole project**: the code under `src/`,
`default.project.json`, the notes (`DEVNOTES.md`, `MODELS.md`, `UI.md`),
**every model and texture**, and every panel and image in the interface. Every
mesh is built in Blender by a script in `tools/`, into
`blender/<kind>/<set>/` (skill `modelling`). **August decides** what each thing
is and approves the look, and does what only he can do in Studio and Creator
Hub (user-level `CLAUDE.md`).

**Geometry is modelled in Blender, never in Luau.** When a model needs to change
(a part in the wrong place, a missing marker, the wrong scale), change its build
script, rebuild it and stage it for his import (skill `import`). The code does
not work around a model it could fix.

**A blockout in Luau is allowed** when the art does not exist yet and the phase
cannot wait, and only if:

- it carries the attachments `MODELS.md` specifies, so a delivered model
  replaces geometry and nothing else, and
- no measurement from it leaks into gameplay code: positions and offsets stay in
  the file that builds the blockout; everything else reads the attachments.

## The scale of a person `[decide on day one]`

**Not ruled yet: ask him before anything a person uses is modelled.** The GDD
sets the plot grid (12 × 12 cells of 4 studs, GDD §3) and gives monsters their
own rigs (§12), but not the height of a player or a monster against that grid.
Sector Omega ruled 2 studs a week in, and every clearance measured before that
was wrong.

Everything a person uses (seats, doors, stairs, counters, railings, walkways)
is built for that height, and a clearance is measured against it, never against
Roblox's default avatar.

## The art handoff

A finished set arrives as:

- `blender/<kind>/<set>/`: the `.blend`, `fbx/`, `textures/`, `manifest.json`,
  `validation.json` and a `README.md` stating what was validated and what was
  not. Only the README, manifest, validation and his reference pictures are in
  git (`.gitignore`); the rest is rebuilt by the set's script.
- `assets/`: **one `.rbxm` per model**, in folders `default.project.json` maps.
  A template only the server reads goes to `ServerStorage`, never
  `ReplicatedStorage`: every client receives what is replicated.

**The file name is the instance name** (Rojo renames every root to its file),
so renaming a file renames what the code finds. A property changed in Studio on
anything from `assets/` lasts only once the model is saved again over its
`.rbxm` (skill `import`).

**What arrives is visual only.** Collision, mass, welds, constraints, emissive
materials, sound and anything that moves are added by the code at runtime. A
moving model has one invisible `Root` part carrying collision, mass and every
constraint, with the imported meshes welded to it, massless, non-colliding and
invisible to raycasts. That separation lets the art be replaced without
changing how anything behaves.

**An import is one action of August's**: he imports the FBX into Workspace and
says *importerat*. The staging, settings, save and checks are Claude's (skill
`import`). Markers are hidden by the code, glows and glass are set up by the
code: never ask him to hide a part, strip a SurfaceAppearance or set a
material.

## What the code needs from a model

**`MODELS.md` is the contract**: which parts must be separate, what they are
called, and which attachments the code looks for. A part called by the
contract's name is lit, driven or found; the same geometry under another name
gets nothing, silently. **If the code starts wanting a name that is not in
`MODELS.md`, put it there first.** Write the contract's rules for a kind of
model *before* its first model, and enforce them in the build script and the
set's validator, not only in the document. A rule that lived only in a
document was broken by every hull in Sector Omega.

## The game is not live

Nobody plays it but August. No save, name or DataStore key has to be kept for
anyone's sake: rename outright, everywhere, with no alias or migration. This
holds until August says the game is live, and he will change this section when
it is.

## How a session is run

The user-level `CLAUDE.md` has the rules (batch lookups, hand over at a review
point past ~250k, `WAITING.md`, memory as state, skills as recipes, shared
tree). Here:

- **Memory is in the repo**, `memory/`, read by Claude Code through a junction
  (skill `machine-setup`). A memory file a session changes is committed with
  its work.
- **Several sessions may share this tree.** Look at `git status` before
  editing a contract file (`MODELS.md`, `UI.md`, `docs/GDD.md`) or a shared kit in
  `tools/`.
- **Claude plays the game from the first phase** (skill `playtest`,
  `TESTRUN.md`): no phase closes on "verified by script". Walkability is
  checked by a walker and by rays, not left for August to find.

## What to read, by job

| Job | Read first | Then, only as needed |
|---|---|---|
| Code | memory `phase-status`; the `docs/GDD.md` § a comment or the task names | `MODELS.md` for the name the code reads; `DEVNOTES.md` by searching it |
| Something that looks impossible | search `DEVNOTES.md` for the API's name | the rest of that note |
| A model, or a picture from him | skill `modelling` | the set's `README.md` when resuming it |
| An import (*importerat*), or staging one | skill `import` | what it points to |
| The interface: a panel, the HUD, an image | `UI.md` | `src/client/UiView.luau` |
| A playtest, or "does it work in the game" | skill `playtest`; `TESTRUN.md` | — |
| Design | memory `phase-status`; the `docs/GDD.md` sections concerned | the research report |
| What waits on August | `WAITING.md` | — |
| A night sprint | skill `night-sprint`; `WAITING.md` | `archive/NATTLOGG-*.md` |
| Ending a session | skill `wrap-up` | — |
| A new machine, a fresh clone, the cloud | skill `machine-setup` | — |
| A code pattern another game already solved | `D:\Roblox\playbook\PATTERNS.md` | the file it names in `D:\Roblox\sector-omega` |

- `docs/GDD.md`: the design document. §-numbers in code comments point into
  it; grep for the § and read that section, never the whole file once it is
  large.
- `DEVNOTES.md`: platform behaviour that cost real time, seeded with Sector
  Omega's. Most of it fails silently.
- `MODELS.md`, `UI.md`: the contracts for models and panels.
- `WAITING.md`: everything that waits on August, in one list, in Swedish.
- `TESTRUN.md`: the playtest Claude runs, item by item.

## Commands

```bash
rojo serve
```

```bash
wally install
```

```bash
stylua src/ && selene src/
```

```bash
rojo build default.project.json -o check.rbxlx
```

**August runs `rojo serve`** (user-level `CLAUDE.md`); the rest Claude runs. A
fresh clone has no `ServerPackages/` until `wally install`, and without
ProfileStore the server cannot load profiles.

**Publish before anything persistent is tested.** DataStores need a published
place with Studio API access on (`File → Experience Settings`, his), and
without it ProfileStore quietly uses a mock (`DEVNOTES.md`). Open the
published experience, never a local `.rbxl`. Check that a sync actually landed
before trusting a playtest: Studio will run a stale copy of every script while
the repository is correct. Never start a playtest while August is importing.
