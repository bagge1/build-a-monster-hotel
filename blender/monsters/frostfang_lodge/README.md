# Frostfang Lodge monsters (Location 2), first drafts

Built 2026-10-19 by an unattended night session, for August's review: every
look here is a draft he judges. Rebuilt by `tools/build_monsters_l2.py` on
`tools/monster_kit.py` (headless Blender 5.2, a few seconds):

```
blender -b --python-exit-code 1 -P tools/build_monsters_l2.py [-- norender] [only Yeti,IceImp]
```

**The look in one line:** the Haunted Manor set's chunky, rounded "cozy
creepy" toys gone wintry: each in its Species.luau colour, big glowing eyes
with a dark pupil and a white glint, rosy cheeks on the soft ones, blunt
faceted ice-crystal horns, snow caps, fur trims and cold blue / aurora glows,
nothing sharp (GDD §12). The sheet is `review/sheet.png` (Workbench, not in
git): a grey 5-stud person at the start of each row.

## The models

| Species | Triangles (budget 4,000) | LOD_Proxy (300) | Height / target (studs) | Extra parts | Notes |
|---|---|---|---|---|---|
| SnowballSprite | 2,198 | 278 | 3.06 / 3 | Dark, Light, Skin, Trim | A lumpy snowball (quirk "rolls instead of walking"), teal beanie (`Skin`), pink pompom and cheeks; Hand on the right mitten nub (no arms) |
| IceImp | 2,842 | 273 | 3.56 / 3.5 | Dark, Light, Skin, Trim | Blunt faceted ice horns, pointed ears, big frosty mitts (quirk "frost handprints"), purple scarf, one-tooth lopsided grin, left hand waving, crystal-tipped tail |
| FrostTroll | 3,404 | 273 | 6.83 / 7 | Dark, Light, Skin, Trim | Slate-blue, snow on head and shoulders, heavy half-shut lids (quirk "sleeps standing up"), round tusks, pale belly, gold Security badge, big fists |
| Yeti | 3,630 | 264 | 7.47 / 7.5 | Dark, Light, Skin, Trim | Big fluffy white yeti (rippled fur), blue face, palms and toe pads, pink cheeks, two tiny fangs |
| SnowWitch | 3,312 | 272 | 5.45 / 5.5 | Dark, Light, Skin, Trim, Glow_Cold_1 | Pale-blue gown with fur hem and capelet, silver hair, violet knitted stocking cap, knitting a glowing icicle (`Glow_Cold_1`, quirk "knits icicles") |
| IceWyrm | 3,692 | 266 | 5.92 / 6 | Dark, Light, Skin, Trim | Chubby serpent coiled 1.5 turns on the floor (quirk "coils around the desk"), round horns, pale snout and belly, back fins, wing nubs; Hand is the curled tail tip |
| AuroraSpirit | 3,520 | 273 | 6.88 / 7 | Dark, Light, Skin, Trim, Glow_Cold_1, Glow_Magic_1..3 | Floating mint spirit, teal hair, gold halo (`Glow_Magic_1`), teal and violet aurora curtains down its back (`Glow_Cold_1`, `Glow_Magic_2`), a paintbrush with a green glowing tip (`Glow_Magic_3`, quirk "paints the sky green") |

Every model also has `Root`, `Body`, `Glow_Eyes_1`, `Glow_Eyes_2`, the
`Nameplate` and `Hand` markers and `LOD_Proxy`. Per-part colours and
triangles, the markers in Blender and Roblox frames, and each Root-relative
attachment position are in `manifest.json`. Species.luau gives no `look.eyes`
for this family, so each eye colour is chosen here (icy blues, the imp's
yellow) and written to the manifest.

## What a model is made of

As the Haunted Manor set (`blender/monsters/haunted_manor/README.md`): the
same frame (standing on the floor, facing Roblox −Z, origin between the feet,
under the body for the AuroraSpirit, between the coil's floor contacts for the
IceWyrm), one flat-coloured part per colour, no textures, static (no rig, no
Animations folder), `Nameplate` and `Hand` as 0.2-stud marker parts the import
step turns into attachments. New in the kit for this set: `tube()`, a swept
tube (the wyrm's coil, the halo), used by the street set too.

## Importing (skill `import`)

Staged with the street NPCs in `blender/_import/frostfang_and_street_2026-10-19/`
(seven monsters plus `Hunter` and `NightBus`, nine FBX). After August imports
them into Workspace, run this folder's `import_settings.luau` (generated) in
the Edit datamodel, then read back in a separate call; then
`blender/street/npcs/import_settings.luau` for the other two. It sets
PrimaryPart, the floor pivot, the attachments, every colour and material,
`Box` collision with collide/query/touch off, and hides `LOD_Proxy`, exactly
as for Haunted Manor. Save each as `assets/Monsters/<SpeciesId>.rbxm`
(`tools/save_imports.py`).

## Validated, and not

**Validated in Blender** (`finish()` at build, `validate()` on the re-imported
FBX, `validation.json`): the same list as Haunted Manor's: part names and the
contract's names, nothing outside the allowed names, triangle budgets and the
per-mesh cap, one material and one UV layer per part, closed geometry, no
coplanar faces between pieces, height within 10 % of Species.luau, nothing
under the floor, the origin between the feet or under the body, the eyes in
front with `Glow_Eyes_1` on the left, the Nameplate over the head, the Hand on
the model, the Root 2 × h × 2, the markers where the manifest says.

**Not validated:** anything in Studio (not imported, not seen at the game's
camera, at Tiny 0.5 / Giant 1.5 or with a mutation); whether the importer
carries plain material colours (`import_settings.luau` sets every colour);
`import_settings.luau` parses as Luau by construction but has not been run.

## Imported (2026-10-19, afternoon)

August imported the whole batch (69 FBX, one dialog). The set's import script
ran in the Edit datamodel and was read back in a separate call: no `Default`
collision, no empty mesh, Root and LOD_Proxy hidden on every model. Saved to
`assets/` with `tools/save_imports.py`. **Synced** after August's Rojo
restart (2026-10-19, 15:30): all 69 synced copies match the Workspace imports
part for part (628 parts: mesh ids, sizes, textures, collision, LOD_Proxy
hidden, no empty MeshPart), and the Workspace copies are deleted. **Studio
runtime is not tested yet**: not seen in the game, not walked.
