# The VIP lounge set (every location; the VIP Lobby pass): a draft

The decor set the VIP Lobby pass promises (GDD §10.2, "VIP lounge decor
set"; its rows are GDD A.2, drafted 2026-10-23, every pick, tag and cost
PLACEHOLDER). Built by `tools/build_vip_lounge.py` on `tools/hotel_kit.py`.
**A draft for August's one approval round**: nothing here is approved, and
nothing has been seen in Studio.

Decor of every location (`Pieces.luau`: location 0, `pass = "VIPLobby"`), so
**one model for all three hotels** (MODELS.md "Decor"): saved into
`assets/HotelKit/HauntedManor/Decor_Vip*.rbxm`, where `HotelKit.decor` looks
after the location's own kit. Its own palette, none a location's: black
lacquer, gold, red velvet. Placed only by a player who owns the pass
(`Pieces.decorHere`), **bought with cash** as other decor (its cost is its
decor points; event decor is free to place, `BuildService`).

| Piece | Footprint | Triangles / budget | What it is |
|---|---|---|---|
| `Decor_VipRope` (Velvet Rope) | 3x1 Floor | 1,308 / 1,500 | two waist-high gold stanchions on domed feet, a thick red velvet rope swagged between them on gold clips |
| `Decor_VipSofa` (VIP Sofa) | 2x1 Floor | 756 / 1,500 | a red velvet sofa for two (a seat by rule 6 at 1.8, 4.1 wide, 1.5 deep) on a black lacquer plinth with gold ball feet, rolled arms with gold caps, a gold crest with a black inset and a gold star |
| `Decor_VipCupcakes` (Cupcake Tower) | 1x1 Floor | 1,464 / 1,500 | a gold three-tier stand of cupcakes in chocolate, cream and red velvet icing, cherries on the top tier, a gold ball on its pole |
| `Decor_VipCarpet` (Red Carpet) | 4x2 Rug | 156 / 1,500 | a red runner with gold borders and diamonds (`K.rug('runner')`); its ends open, so two join |
| `Decor_VipSign` (VIP Sign) | 2x1 Wall | 1,480 / 1,500 | a black marquee in a gold frame with a shallow arched top, "VIP" in lit bulbs and a border of small bulbs all round it (`Glow_Warm_1`), a gold star |

Rebuild: `blender -b --python-exit-code 1 -P tools/build_vip_lounge.py`
(`-- only Decor_VipSign`), then `tools/review_pieces.py -- decor/vip_lounge`.

## Validated (validation.json, by the build)

All 5 built and re-imported clean (`VALIDATED 5/5`): footprint, 0.4 inset,
layer, height against `Pieces.luau` (the rope's 2.9 since it was lowered),
the sign's back on the wall's plane, the sofa's seat (`K.seat`, rays on the
built and re-imported triangles), no coplanar faces, budgets. Refused and
fixed during the build: the rope and the sign over budget, the sofa's roll
ends in the arms' faces, the sign 0.02 past the footprint's inset.

## Blind review 2026-10-23 (first run) and its triage

A context-free reviewer (another model) on `review/pieces_sheet.png` and
close-ups of the sofa and the sign. Before it: the sign read mirrored
("qIV": a guest facing it has +X on their left); the letters are drawn at -x.

1. **The sofa's back a black slab, the gold crest stuck on its front** —
   Confirmed: the crest is gold over the back's whole depth, a black inset
   on its front, the star on that.
2. **Seat too high** — False: 1.8, inside rule 6's 1.5-2.0 for the 5-stud
   person (the build checks it).
3. **Three gold spikes under the sign** — Confirmed as a read (two wall
   brackets): removed; the sign hangs on the wall's plane.
4. **The marquee half lit, no bulbs round the frame** — Confirmed: a border
   of small bulbs all round it (the foot row gone), the letters 0.1 higher.
5. **The cupcakes pastel, off the set's palette** — Confirmed: chocolate,
   cream and red velvet icing. Its height (a floor piece to 4.2) not changed.
6. **The tufting flecks** — Confirmed: the buttons are gone.
7. **The rope a thin cord on chest-high posts** — Confirmed: posts to 2.9
   (were 3.4; `Pieces` height with them), the rope 0.21 thick at 2.2.
8. **The runner a red rectangle from above** — Not changed: the kits'
   shared runner, so the carpets join; August's look.
9. **The arm caps draw the eye** — Not changed (unsure, taste).

### Second run (new reviewer, new pictures)

1. **Sofa seat too high** — False (1.8 by rule 6, checked by the build).
2. **The cupcake tower a Christmas tree** — Confirmed as a read (both
   runs): the star on its spike is gone, a gold ball tops the pole (height
   3.9). A tabletop size is **August's call** (WAITING §2.50).
3. **Stanchions shoulder-high; the rope a hose** — False by geometry: the
   balls' tops are at 2.9 and the rope at 2.2, waist-high on the 5-stud
   person (the nearer post is nearer the camera); a thick rope is the look.
4. **No back cushion; a black slab** — False: the back is red velvet from
   1.2 to 3.4 (`review/pieces/Decor_VipSofa.png`); the black is the crest's
   inset.
5. **The sign's letters sparse dots until lit** — Not changed: the bulbs
   glow in the game (`Glow_Warm_1`); solid letters behind them would cost
   the budget (1,480 / 1,500). His look.
6. **The runner plain** — as the first run's 8.
7. **The sign's frame deep** — Not changed (0.34 off the wall; unsure).

No third run: the one change after it (the star) took a part away.

## Not validated

Studio: the import, `import_fixup.luau`, the bulbs lit, the pieces placed
in any of the three hotels, the pass gate on a real server. Studio runtime
is not tested.

## Review pictures (not in git)

`review/pieces_sheet.png` (each piece close up beside the 5-stud person,
the sign on a wall), the tiles in `review/pieces/`; `review/contact_sheet.png`.

## Imported

Imported 2026-10-23 (WAITING §0.15): all 5 fixed up by `import_fixup.luau` (Box everywhere, Root the hidden PrimaryPart, the sign's bulbs lit), read back in a separate call and saved to `assets/HotelKit/HauntedManor/Decor_Vip*.rbxm`; the synced copies under `ServerStorage.HotelKit.HauntedManor` match the import part for part (mesh ids, sizes, collision, no empty MeshPart). The live sync dropped `PrimaryPart`; set back to `Root` in Studio (the files have it). Not yet seen in a playtest.
