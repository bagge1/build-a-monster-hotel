# Bayou Spa monsters (Location 3), first drafts

Built 2026-10-23 for the soft launch (LAUNCH.md workstream #4), for August's
one approval round: every look here is a draft he judges. Rebuilt by
`tools/build_monsters_l3.py` on `tools/monster_kit.py` (headless Blender 5.2,
about 40 s with the renders):

```
blender -b --python-exit-code 1 -t 4 -P tools/build_monsters_l3.py [-- norender] [final] [only BogFrog,MudPuppy]
```

**The look in one line:** the Haunted Manor and Frostfang sets' chunky,
rounded "cozy creepy" toys gone swampy: each in its Species.luau colour, big
glowing eyes with a dark pupil and a white glint, rosy cheeks on the soft
ones, moss, lily pads, mud, steam, jazz bow ties, warm firefly glows and cool
moonlight, nothing sharp (GDD §12). Species and their rows: WAITING §2.36
(August's ruling 2026-10-20: location 3 at launch, the family his to pick;
the rows are the draft he has not struck).

## The pictures (not in git; rebuilt by the script)

All with the grey 5-stud person at the start of each row:

- `review/silhouettes.png`: grey silhouettes (Workbench, shapes only)
- `review/sheet.png`: the kit's colour sheet (Workbench)
- `review/final_front_row1.png`: finished, front three-quarter, BogFrog to GatorGhoul (Cycles)
- `review/final_front_row2.png`: finished, front three-quarter, WillOWisp to MoonHeron (Cycles)
- `review/final_back.png`: finished, from behind, both rows (Cycles)
- `review/final_game_camera.png`: finished, raised 38° like the game's camera (Cycles)

## The models

| Species | Body shape (rig) | Triangles (4,000) | LOD_Proxy (300) | Height / target | Extra parts | What it is |
|---|---|---|---|---|---|---|
| BogFrog | Blob | 3,488 | 271 | 2.90 / 3 | Dark, Light, Skin, Trim | Squat frog on its haunches, eye domes, wide grin, puffed throat sac (croaks a chord), black bow tie, lily-pad cap with a pink flower |
| Mossling | Blob | 2,984 | 272 | 3.06 / 3 | Dark, Light, Skin, Trim | Soft moss ball, light-green tufts, a two-leaf sprout and a pink bud on top (sprouts grow where it sits) |
| FireflySprite | Float | 2,644 | 274 | 3.00 / 3 | Dark, Light, Skin, Trim, Glow_Warm_1..2 | A long glowing amber lantern tail (`Glow_Warm_1`), a dark hood, dark wing cases and two pale wings, glowing antenna tips (`Glow_Warm_2`) |
| MudPuppy | Quadruped | 3,780 | 273 | 2.84 / 3 | Dark, Light, Skin, Trim | Chubby pup dipped in mud to its middle with a drippy edge, muddy socks, mud on its head, cream muzzle, floppy ears, red pillbox bellhop cap with a cream band |
| GatorGhoul | Biped | 3,878 | 260 | 5.00 / 5 | Dark, Light, Skin, Trim | Upright gator, a far-too-wide grin with a row of round teeth, ghoul-green eyes on eye bumps, pale belly, Security vest, cap and gold badge, tail swept aside off the floor |
| WillOWisp | Float | 2,162 | 278 | 3.95 / 4 | Dark, Light, Trim, Glow_Cold_1 | Pale-blue spirit under a glowing mint three-tongued flame and three motes (`Glow_Cold_1`), a shy "o" mouth and blush, little arms, wispy tail |
| SwampHag | Biped | 3,898 | 270 | 4.86 / 5 | Dark, Light, Skin, Trim, Glow_Magic_1 | Hunched kindly hag: sage robe with a ragged hem, purple shawl, wild grey hair, a droopy witch hat tilted back, big round nose and one tooth, a teapot puffing mint fog (`Glow_Magic_1`) |
| BayouHydra | Serpent | 3,864 | 241 | 6.11 / 6 | Dark, Light, Skin, Trim | Tubby teal body on two stubby front legs, three S-curved necks; the heads differ: the middle smiles under a crest, the left says "ooh" with a lily behind its ear, the right sticks its tongue out; a curled tail |
| CypressKing | Biped | 3,656 | 240 | 6.17 / 6 | Dark, Light, Skin, Trim, Glow_Warm_1 | Bald-cypress king: fluted bark trunk on root legs, a kind carved face, a moss beard, moss hanging off raised branch arms, cypress-green shoulders, a splayed twig crown with a firefly on each point and a few loose (`Glow_Warm_1`) |
| MoonHeron | Biped | 3,044 | 269 | 7.30 / 7 | Dark, Light, Skin, Trim, Glow_Cold_1 | Tall moon-white heron: periwinkle legs, an S-curved neck, a long blunt gold beak, crest plumes, periwinkle wing tips and tail, a glowing crescent moon behind its head (`Glow_Cold_1`) |

Every model also has `Root`, `Body`, `Glow_Eyes_1`, `Glow_Eyes_2`, the
`Nameplate` and `Hand` markers and `LOD_Proxy`. Per-part colours and
triangles, the markers in Blender and Roblox frames, `rig_shape`, and each
Root-relative attachment are in `manifest.json`. Species.luau gives no
`look.eyes` for this family, so each eye colour is chosen here.

**`Hand`**, where it is not a right hand: the BogFrog's right front hand (on
the floor), the MudPuppy's mouth (a pup carries in its mouth), the
BayouHydra's curled tail tip, the MoonHeron's right wing.

**BayouHydra's eyes**: three heads, so `Glow_Eyes_1` is the three left eyes
joined and `Glow_Eyes_2` the three right eyes, a mirrored pair as the contract
checks.

## Rigs (LAUNCH.md #6)

Rigged (2026-10-23): the kit gives each model the armature of its
Species.luau `look.shape` (MODELS.md, "The rig"), `review/pose.png` a test
pose. The MudPuppy takes the fifth, Quadruped rig made for it (it stands on
four legs; its landmarks are its own). The BayouHydra's middle neck takes
`Neck` and `Head` and its two side necks the Serpent's two tail bones, both
hung on `Coil`, so the side heads look about on their own.

## What a model is made of

As the Haunted Manor and Frostfang sets: standing on the floor facing Roblox
−Z, origin between the feet (under the body for the floaters, between the
floor contacts for the hydra, moved there by `recentre_y()`), one
flat-coloured part per colour, no textures, `Nameplate` and `Hand` as 0.2-stud
marker parts the import step turns into attachments.

## Blind review 2026-10-23 (three rounds, each a fresh reviewer on new pictures)

**Round 1** (the first Cycles pictures):

1. Firefly reads as a bee: **confirmed**, fixed (bigger lantern, wing cases); it came back in round 2, see there.
2. Wisp reads as a raindrop: **confirmed**, fixed with a glowing three-tongued flame crown.
3. Cypress King: a hand on its face (strand beard), angry V brows, candle crown: **confirmed**, fixed (round beard, kind brows, circling fireflies); came back in round 2.
4. Gator's teeth a thin dotted line: **confirmed**, fewer and bigger teeth.
5. Heron's crescent reads as a hook, legs thin, beak short: **confirmed** in part: crescent fattened, legs thickened, beak lengthened.
6. Firefly far too small: **false**, it is 3.00 studs, Species.luau's height; its mass grew with the lantern.
7. Mud Puppy not muddy, tail an antenna: **confirmed**, darker mud, socks, a real tail.
8. Hydra eyes through the backs of the heads: **false**: the eyes' rims bulge past the head's edge seen from three-quarters behind; the eye's rear is 0.24 in front of the head's centre, the back of the head 0.5 behind.
9. Hydra reads as a cactus: came back in round 2, see there.
10. Hag's fog three bubbles: **confirmed**, a five-puff cloud.
11. Four guests 2.5 to 3 studs beside a desk for a 5-stud person: **false** as a model fault: heights are Species.luau's (the Haunted Manor set has the same).

**Round 2:**

1. Firefly still a bee (yellow and black bands, the lantern a separate faceted ball): **confirmed**: no striped collar, a smooth long lantern under the wing cases, a firefly's dark hood. The yellow Body is Species.luau's colour: **his call** (below).
2. Hydra a rubber glove or cactus: **confirmed** (two reviewers): bigger heads on tapered S-necks, two stubby front legs.
3. Gator has no tail: **false**: its bounds run 2.6 studs behind the body; from straight behind the tail points at the camera. Swept to one side anyway so it shows in silhouette. Teeth a pearl necklace: **confirmed**, set on a thicker mouth line. Vest flat slabs: **false**, an arc shell round the torso.
4. Cypress King a sad man in a bark coat, nest crown, cauliflower beard, worried brows: **confirmed**: level brows, a single teardrop moss beard, no hair ball under the crown, raised branch arms, the trunk tapering into the legs, a firefly on each crown point.
5. Heron's crescent floats: **his call** (below). Legs thin: as round 1.
6. Wisp a water drop with a crystal spike, standing on its tip, a "moustache": **confirmed**: a curvier flame, the tail lifted, the hands (the moustache) moved to its sides. Does not glow: **his call** (below).
7. Pup not muddy: **confirmed**, dipped in mud to its middle with a drippy edge, a band on the cap.
8. Hag's teapot tiny, fog stuck on, brim paper-thin: **confirmed**, a bigger teapot, fog curling from the spout, a thicker brim.

**Round 3:**

1. Pup still not muddy from the front: **confirmed** (the dip hides behind the head): darker mud, mud on its head and face.
2. Gator does not read as a ghoul: **his call** (below). The vest's open front reads as a hole: **his call**, minor.
3. Cypress King reads as a robot / Groot, the crown as antennae: **his call** (below).
4. Hag's face in the brim's shadow, fog detached: **confirmed**, the hat tilted back, the fog starts at the spout.
5. Heron's crescent clips the head and neck: **false**: it stands 0.9 behind the head, clear of the neck (0.1 front edge against the neck's −0.15 back) and of the plumes; it overlaps only in projection.
6. Wisp a water drop, does not glow: as round 2, **his call**.
7. Mossling and frog the same silhouette: **confirmed** in part, a bigger sprout on the Mossling.
8. Hydra arrowhead slab on the tail: **false**, the curled tail tip seen from behind. Heads identical: **his call**, minor.
9. Firefly's lantern a lit egg, blown out: **confirmed** for the picture: a deeper amber, the renders' glow lowered.
10. Hats and antennae under a stud: the heights are Species.luau's.

The final round's fixes were not re-reviewed by a fourth reviewer.

## His calls (for the approval round, LAUNCH.md "Looks")

- **FireflySprite's colour.** Its Body is Species.luau's yellow (250, 230, 110), which keeps reading as a bee to two reviewers. *Keep yellow* or *a firefly's dark brown body*. **Recommendation:** dark brown (a Species.luau colour change, one line).
- ~~**MudPuppy's rig.**~~ Answered by the build (2026-10-23): a fifth, Quadruped rig was made, so it takes Species.luau's own shape (Rigs, above).
- **GatorGhoul, how ghoulish.** A cheerful gator in a Security cap; nothing says ghoul. *Keep cozy* or *paler and drooping, a tattered edge*. **Recommendation:** keep cozy for launch.
- **WillOWisp's glow.** Its Body cannot be Neon (a mutation tints and re-materials it); the flame and motes glow. *As it is* or *a PointLight on it in the code*. **Recommendation:** a PointLight, after launch.
- **MoonHeron's moon floats** behind its head, unattached, like the AuroraSpirit's halo. **Recommendation:** keep.
- **CypressKing** reads to one reviewer as a tree-man robot. **Recommendation:** judge it in the game.

## Validated, and not

**Validated in Blender** (`finish()` at build, `validate()` on the
re-imported FBX, `validation.json`): part names and the contract's names,
nothing outside the allowed names, triangle budgets and the per-mesh cap, one
material and one UV layer per part, closed geometry, no coplanar faces between
pieces, height within 10 % of Species.luau, nothing under the floor, the
origin between the feet or under the body, the eyes in front with
`Glow_Eyes_1` on the left, the Nameplate over the head, the Hand on the model,
the Root 2 × h × 2, the markers where the manifest says.

**Not validated:** anything in Studio (not imported, not seen at the game's
camera, at Tiny 0.5 / Giant 1.5 or with a mutation); the rigs (none yet);
`import_settings.luau` is generated but not run.

## Importing

**Not staged.** The FBX are in this worktree's `fbx/` (not in git); the
orchestrator stages them in `blender/_import/` after August's approval round
(skill `import`), then this folder's `import_settings.luau` runs in the Edit
datamodel as for the other sets.

## Imported rigged (2026-10-24, night)

August imported all 27 rigged monsters in one dialog with Rig Type Custom
(WAITING §0.16). The set's `import_settings.luau` ran in the Edit datamodel;
read back in a separate call: every model `PrimaryPart = Root`, every MeshPart
`Box`, `LOD_Proxy` hidden, `Nameplate`/`Hand` as attachments on `Root`, the
`AnimationController` and `InitialPoses` gone, the Motor6Ds kept, only `Root`
anchored. Saved over `assets/Monsters/<Name>.rbxm` with
`tools/save_imports.py`. The synced copies under `ReplicatedStorage.Monsters`
match the imports part for part (mesh id, size, collision, anchoring, bones,
Motor6Ds), no empty MeshPart; 26 of 27 came out of Rojo's live sync with
`PrimaryPart` nil (DEVNOTES), so `MonsterKit.build` sets it to `Root` on each
clone. Not yet seen bending in a playtest (night log 2026-10-24).
