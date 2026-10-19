# Hotel cosmetics (Sign and Lobby slots): first draft

Built 2026-10-19 by `tools/build_cosmetics_hotel.py` on `tools/hotel_kit.py`
(kind `Cosmetic`). **A draft for August's review**: nothing here is approved,
nothing has been imported or seen in Studio.

One model per Sign- or Lobby-slot row of `src/shared/Cosmetics.luau`, named the
cosmetic's id (MODELS.md, "Cosmetics"; templates go to
`ServerStorage.Cosmetics`, `assets/Cosmetics/`). The Facade slot has no models:
a facade cosmetic is a colour scheme.

**The look, each in one line:**

| Model | Slot | What it is |
|---|---|---|
| `Cosmetic_PumpkinSign` | Sign | The board set in a big seven-lobed pumpkin (the board is its carved face), a curved stem, two leaves, a vine curl; warm light (`Glow_Warm_1`) round the board's edge |
| `Cosmetic_IcicleSign` | Sign | Lumpy snow along the board's top, in front of and behind the kit's crest (which rises out of it), drifts over both ends, icicles off the ends and under the board |
| `Cosmetic_LanternSign` | Sign | Two iron lanterns with candle flames (`Glow_Warm_1`, `Glow_Warm_2`) hanging from scroll brackets on the board's ends, at its top corners |
| `Cosmetic_Family1` | Sign | Haunted Manor crest: a violet heater shield with a gold rim and a little ghost, spread bat wings, a gold crescent finial |
| `Cosmetic_Family2` | Sign | Frostfang crest: a frost-blue shield with an ice rim and a white snowflake, snow on its top, two curved fangs rising beside it |
| `Cosmetic_BatBunting` | Lobby | Paper bats (plum and violet, amber eyes) on a string in two swags from the arch's corners to a bow at its top, a big bat under the bow |
| `Cosmetic_FairyLights` | Lobby | A dark green wire in four swags across the arch with 12 warm bulbs (`Glow_Warm_1..12`) |

Rebuild: `blender -b --python-exit-code 1 -P tools/build_cosmetics_hotel.py`
(`-- nopreview` skips the review renders, `-- only Cosmetic_Family1` rebuilds
some and keeps the rest of the manifest). About 20 s, headless, Workbench only.
It reads both hotel kits' `fbx/HotelSign.fbx` and `fbx/Lobby.fbx`, so those
sets must be built first.

## What is here

- `fbx/<Name>.fbx`: the 7 models, the atlas embedded in each.
- `manifest.json`: per model its Root, every part's box (Roblox studs, the
  slot's frame), triangles, `collide: false` everywhere, the `slot`, the
  `origin` and the measured `clearances`.
- `validation.json`: the validator's results, `collision_precise` (empty for
  every model), the clearances on the re-imported FBX, what was not validated.
- `import_fixup.luau`: the import's step 2 (skill `import`), generated from the
  manifest: anchors everything, CanCollide / CanQuery / CanTouch off on every
  part, `Box` on every mesh, the glows Neon in the Warm colour (one PointLight
  on each `_1`), Root the invisible PrimaryPart with the pivot on the slot's
  origin, LOD_Proxy hidden. It checks every part against the manifest first.
- `textures/HotelAtlas.png`: the set's 256 px palette atlas (its own palette,
  the Cosmetics.luau colours first).
- `review/` (not in git): `front.png` and `angle.png` (every sign cosmetic on
  the Manor's sign, top row, and the Lodge's, middle row; the lobby cosmetics
  on both arches with a 5-stud person and red marks at 8 studs, bottom row),
  `closeup.png` (the lantern bracket), `closeup_icicle.png` (the snow over the
  board's end), `lobby_BatBunting.png`, `lobby_FairyLights.png`. Note: from the
  front, Roblox +X is on the left, so the sign order is reversed.
- `hotel.blend`: the models laid out (the FBXs are at their own origins).

## The frames

- **Sign slot**: the origin is the centre of the `Board`'s front face, front
  toward −Z (`PlotService.drawCosmetics` pivots it onto
  `board.CFrame * CFrame.new(0, 0, -board.Size.Z / 2)`). In this frame the
  Board is x −8..8, y −3..3, z 0..0.6. Root is 1 × 0.2 × 1 at (0, 0, 0.3),
  inside the Board.
- **Lobby slot**: the origin is the lobby's `Entrance` attachment, on the
  floor at the threshold, front toward −Z. Root is 1 × 0.2 × 1 at (0, 0.1, 0).

**Measured from the kits' own FBX** (both checked at every build): the Board
is 16 × 6 × 0.6 at (0, 8, 0) of `HotelSign` in both kits, so one fit serves
both. Each kit also has a `Crest` above the board (the Manor's gable with a
lit moon, z 0.05..0.55 in the cosmetic frame, up to y 5.6; the Lodge's snowy
gable with a lit snowflake, z −0.05..0.65, up to y 5.75, plus a snow strip
along the board's top and icicles under it) and posts reaching y −2. The
arches: pillars |x| 4.5..5.5, front at z 0, both kits; the Manor's `ArchTop`
is 11 wide, a pointed top from y 9.0, its front at z 0.05; the Lodge's is 11.8
wide with its snow, a gable from y 9.0. **The narrower span, |x| ≤ 5.5, is the
one fitted.** The string's hooks sit where both arches are solid:
(±5, 9.45), (±2.5, 10.3), (0, 10.8).

## Clearances (validator, on the re-imported FBX)

| Model | Triangles / budget | Nearest to the Board face | Lowest point | Nearest to the Manor's / the Lodge's |
|---|---|---|---|---|
| `Cosmetic_PumpkinSign` | 1,540 / 2,000 | 0.16 (the glow, beside the edge) | | 0.23 Board / 0.19 Crest |
| `Cosmetic_IcicleSign` | 1,900 / 2,000 | 0.03 (snow on the top, icicles under) | | 0.03 Board / 0.03 Board |
| `Cosmetic_LanternSign` | 1,372 / 2,000 | 0.02 (the bracket on the end face) | | 0.02 Board / 0.02 Board |
| `Cosmetic_Family1` | 636 / 2,000 | 0.12 (the shield's point over the top edge) | | 0.17 Crest / 0.10 Crest |
| `Cosmetic_Family2` | 840 / 2,000 | 0.12 | | 0.17 Crest / 0.10 Crest |
| `Cosmetic_BatBunting` | 1,240 / 2,000 | | **8.77** (headroom 3.77 over a 5-stud person) | 0.08 ArchTop / 0.08 ArchTop |
| `Cosmetic_FairyLights` | 1,508 / 2,000 | | **8.74** (a bulb; headroom 3.74) | 0.08 ArchTop / 0.07 ArchTop |

"Nearest to the Board face" is the nearest vertex to the face extruded
forward (x −8..8, y −3..3, z < 0.6): no triangle of any sign cosmetic enters
it (exact triangle-box test, 0.015 margin). No triangle of any model
intersects either kit's sign or lobby (exact BVH triangle overlap); the
distances to the kits are nearest-vertex. Lobby cosmetics: |x| ≤ 5.13 (inside
the 5.5 span), z ≤ −0.03 (in front of the arch). Sizes are in `manifest.json`
(`clearances.bounds`): the pumpkin 20.5 × 12.1 × 3.0, the icicles 19.1 × 8.8 ×
2.2, the lanterns 21.3 × 3.9 × 1.4, the crests 13.2 × 5.3 and 7.8 × 4.8, the
bunting 10.3 × 2.3, the lights 10.3 × 2.2.

## How each model is cut (MODELS.md rule 7)

`Root`, one `Body` (everything that does not glow, one mesh), a `Glow_Warm_<n>`
per flame or bulb (rule 1, one physical light each, rule 3), `LOD_Proxy` (2-4
boxes, 12-48 triangles, held to the same Board-face and arch rules). Nothing
collides.

## Validated (Blender, headless)

`finish()` refuses a model, and the validator re-checks it on its re-imported
FBX, for: plain ASCII names, glows `Glow_Warm_<n>` holding only glow colours;
Root 1 × 0.2 × 1 at its centre, not colliding; nothing colliding; the
model inside its envelope; the Board face clear (sign) or the lowest point
≥ 8, |x| ≤ 5.5 and z ≤ 0 (lobby); no triangle touching either kit's sign or
lobby; triangles within the draft 2,000, every mesh under 20,000, the proxy
under 500; closed meshes; after the FBX round trip the same part names, every
box within 0.02 stud, the same triangle counts, one UV layer and one material
each, the atlas embedded.

## Not validated

- **Nothing has run in Studio.** Not imported, not placed by
  `HotelKit.cosmetic`, not seen lit.
- Roblox's side of the axis conversion (`import_fixup.luau` stops, touching
  nothing, if a model arrives mirrored or turned).
- The kit clearances are against the two kits' FBX as built today; a change
  to a kit's sign or arch needs this set rebuilt (the build re-checks).
- The fix-up lights only each `_1` glow: the right-hand lantern and 11 of the
  12 bulbs are Neon without a PointLight (the kit's rule, kept).
- **The 2,000-triangle ceiling is a draft**: MODELS.md's budget table has no
  row for a cosmetic.

## Decisions taken without him (reversible, for his review)

- Every shape, colour and size above, and the set's palette.
- **Sign cosmetics stand with the kit's own `Crest`, not instead of it.** The
  crests (Family1/2) stand on the board's top edge in front of the kit's gable
  and hide its middle, moon or snowflake included; the pumpkin sits behind
  the gable; the icicle snow lies in front of and behind it. Whether the code
  should hide the kit's `Crest` and `Glow_Cold_1` while a Sign cosmetic is
  worn is his call (it would be a `PlotService` change).
- Lanterns hang beside the board (off its ends), not in front of it, so they
  never cross the face.
- The lobby strings hang in swags following both arches' gables, the hooks
  where both arches are solid.

## Seen in the kits while fitting (not changed here)

- **Both kits' `HotelSign` posts poke through the Board's front face**: each
  post's top ring (radius 0.4 at y 5.8..6.0 of the sign) stands about 0.07 in
  front of the face near its lower corners, inside the SurfaceGui's area. It
  shows as two small bumps in `review/closeup.png`. The fix is in the kits'
  `hotel_sign()` (a ring no wider than the board is thick, or the post ending
  under the board).
