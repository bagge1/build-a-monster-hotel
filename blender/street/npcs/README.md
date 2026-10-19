# Street NPCs: `Hunter` and `NightBus`, first drafts

Built 2026-10-19 by an unattended night session, for August's review: both
looks are drafts he judges. Rebuilt by `tools/build_street_npcs.py` on
`tools/monster_kit.py` (headless Blender 5.2, a few seconds):

```
blender -b --python-exit-code 1 -P tools/build_street_npcs.py [-- norender] [only Hunter]
```

**The look in one line:** the monsters' toy style on the street: a goofy,
harmless monster hunter, and a chunky purple night bus with an orange roof,
warm-lit windows and a friendly face (headlamp eyes and a grille smile). The
sheet is `review/sheet.png` (Workbench, not in git): the bus's door side
beside the hunter and a 5-stud person, and below it the bus's face at three
quarters.

## The models

| Model | Triangles | LOD_Proxy | Size | Parts beyond Root, Body, LOD_Proxy | Notes |
|---|---|---|---|---|---|
| Hunter | 3,612 (4,000, a monster's: MODELS.md names none for a hunter) | 251 (300) | 5.23 tall / 5 (Root 2 × 5 × 2, HunterRenderer's blockout) | Skin, Trim, Dark, Light, Glow_Warm_1, Nameplate | GDD §8.1: an oversized pith helmet, worried brows, goggly slightly crossed eyes, bushy moustache, shorts and mustard knee socks, a garlic necklace, a butterfly net held upright, an oversized flashlight whose lens is `Glow_Warm_1` |
| NightBus | 6,540 (8,000) | 478 (500) | 24 × 8.96 × 8 (Roblox x, y, z; Root 24 × 9 × 8, BusRenderer's blockout) | Trim, Dark, Light, Wheel_1..4, Glow_Warm_1..5, Door | Faces Roblox +X. `Glow_Warm_1` every window, the windscreen, the rear window and the door's panes (one part); `Glow_Warm_2` the left headlamp, `Glow_Warm_3` the right; `Glow_Warm_4` the roof lantern; `Glow_Warm_5` both tail lamps |

## What the models are made of

- **Frame.** The Hunter as a monster: standing on y = 0, facing Roblox −Z,
  origin between the feet. The NightBus faces **Roblox +X** (Blender −X; the
  way it drives in, MODELS.md), origin on the floor under its middle, wheels
  on the floor, everything inside its Root.
- **`Door`** (NightBus): a marker on the floor 0.6 studs outside the door, on
  the bus's right side, Roblox +Z (the side the stop pad is on: the lane is at
  z = −15, the pad at z = −10, StreetLayout and BusRenderer). Root-relative
  Roblox (5.0, −4.5, 4.6). The import step makes it an Attachment under Root
  **looking +Z**, out of the door (`markers_look_roblox` in the manifest).
- **Wheels** are their own parts, `Wheel_1` front-left, `Wheel_2`
  front-right, `Wheel_3` rear-left, `Wheel_4` rear-right (MODELS.md rule 2: a
  wheel moves), each centred on its axle. Nothing turns them yet. Hubcaps
  (`Light`) and arches (`Dark`) are not part of the wheels.
- **One part per colour, no textures, static**, as the monsters. The bus's
  headlamps are separate parts so the code can hang a light on one.
- **Not done:** BusRenderer's blockout puts a `SpotLight` on its own headlamp;
  a delivered `NightBus` template is cloned as is, so it arrives without one
  unless the code adds it (MODELS.md: lights are the code's).

## Importing (skill `import`)

In the same batch as the Frostfang Lodge monsters,
`blender/_import/frostfang_and_street_2026-10-19/` (nine FBX). After the
import, run this folder's `import_settings.luau` in the Edit datamodel (the
monsters' step, plus the `Door` attachment and its orientation), read back in
a separate call, and save both as `assets/Monsters/Hunter.rbxm` and
`assets/Monsters/NightBus.rbxm`: HunterRenderer and BusRenderer look for them
in `ReplicatedStorage.Monsters`.

## Validated, and not

**Validated in Blender** (`finish()` at build, `validate()` on the re-imported
FBX, `validation.json`): part names round-trip; the contract's names present
(Hunter: `Body`, `Nameplate`; NightBus: `Body`, `Door`, `Glow_Warm_1`) and
nothing outside the allowed names; triangle budgets and the per-mesh cap; one
material and one UV layer per part; closed geometry; no coplanar faces
between pieces; height within 10 %; nothing under the floor; the Hunter's
origin between his feet and his flashlight ahead of his body (he faces −Z);
the bus centred, inside and filling its Root, its left headlamp ahead of the
body along Roblox +X; the Door on the floor beside the right side, looking
out; the Root's size and place; the markers where the manifest says.
`finish()` was proven to refuse a bus facing backwards, a bus without a Door,
a bus longer than its Root, a Hunter without a Nameplate and a monster given a
Door.

**Not validated:** anything in Studio: the import, the Door attachment's
orientation after `import_settings.luau`, the look on the street at night,
the bus at BusRenderer's speed. **A finding from the numbers, not from
Studio:** at the stop the bus (lane z = −15, 8 wide: z −19 to −11, x ±12 round
`BusStop.X`) overlaps `BusStopSign` (PlotService: `BusStop + (3, 4, −12)`), as
the blockout already does; nothing collides, but the post will stand inside
the bus.
