# ui/ — the interface's images

Every file here is drawn by `tools/draw_ui.py` (Python, PIL + numpy; run
`python tools/draw_ui.py`). Nothing is downloaded or hand-edited: change the
script and re-run it. It is deterministic (the same script writes the same
pixels). **All of it is a first draft for August's review** (2026-10-19 night);
none of it is uploaded yet, so `src/client/UiImages.luau` has no ids for it.

Rules (UI.md "Images"): a **tintable** image is white on transparent with its
glow baked into alpha, and the code colours it (`ImageColor3` or a
`UIGradient`). Pass and developer-product icons are shown as they are, so they
are drawn in colour, with everything that matters inside the circle a pass icon
is cropped to. Everything is ≤ 1024 px, except the review sheet, which is not
uploaded.

The look: "cozy creepy" (GDD §12) — chunky shapes with a dark ink outline
(`Ui.Colour.Ink`), soft top light and shaded feet, purples, teal, pumpkin, gold
and moonlight blue from `Ui.Colour`, big friendly eyes on anything that can
have them (the bus's headlights, the book, the slime, the heart, Gloom).

## HUD icons — `hud/`, 256 × 256, tintable

The glow is only round the outside of the silhouette; holes (eyes, cut-outs)
stay clear so they read when small.

| File | Shape | For |
|---|---|---|
| `hud/Icon_Build.png` | hammer | `BuildButton` (left) |
| `hud/Icon_Rating.png` | star | `RatingButton` (left); rating stars |
| `hud/Icon_Residents.png` | little house, heart window | `ResidentsButton` (left) |
| `hud/Icon_Book.png` | book with a monster face | `BookButton` (left), the Monster Book |
| `hud/Icon_Moon.png` | crescent and a sparkle | `ProgressionButton` (right): Moon Shards, the Moon Tree |
| `hud/Icon_Store.png` | shopping bag with a star | a store button (passes and products) — not in the HUD yet |
| `hud/Icon_Daily.png` | calendar with a tick | daily reward / daily requests — not in the HUD yet |
| `hud/Icon_Bus.png` | bus front, headlights as eyes | the Night Bus timer; Call the Bus |
| `hud/Icon_Pitch.png` | megaphone | the Pitch prompt on a guest |
| `hud/Icon_Boo.png` | ghost going "boo" (arms up, round mouth) | a boo / scare action — not in the HUD yet |
| `hud/Icon_Cash.png` | coin with "$" | the cash counter |
| `hud/Icon_Till.png` | cash register | the till readout / collect |

## Panels — `panel/`, 512 × 512, tintable 9-slices

| File | What | Use |
|---|---|---|
| `panel/PanelFill.png` | rounded rectangle, radius 72, inset 24 | panel body, tinted `Ui.Colour.Panel` |
| `panel/PanelFrame.png` | its 8 px edge line, glow outward, faint sheen inward | panel border, tinted `Ui.Colour.Line` (or a gradient) |

Both: `ScaleType = Slice`, `SliceCenter = Rect(112, 112, 400, 400)`, laid on
top of each other at the same size. The 24 px inset is room for the frame's
glow, so the panel's frame should be 24 px larger than its content on every side
at `SliceScale` 1 (or scale the slice down, e.g. `SliceScale` 0.5 for a tighter
corner).

## Gloom — `Gloom.png`, 512 × 512, colour, transparent background

Gloom the bat concierge (GDD §17 q6, his first look): a round purple fuzzball
with pink-lined ears, a tuft, big teal eyes, one little fang, rosy cheeks, a teal
bow tie and spread bat wings. For the tutorial's speech panel and anywhere
Gloom talks. **August decides the look.**

## Pass icons — `pass/`, 512 × 512, colour

A round night badge with a coloured ring at r ≈ 0.93; the content stays inside
r ≈ 0.85 so the circular crop never cuts it.

| File | Pass (GDD §10.2) | Picture |
|---|---|---|
| `pass/Pass_AutoCollectTill.png` | Auto-Collect Till (149) | register, coins flying along a teal arrow |
| `pass/Pass_NightManager.png` | Night Manager (249) | sleeping crescent moon, Zzz, desk bell, clock |
| `pass/Pass_ResidentWingPlus.png` | Resident Wing+ (249) | house with someone in the window, green "+" |
| `pass/Pass_ExtraFloor.png` | Extra Floor (299) | two lit floors and a new teal floor on top, up arrow |
| `pass/Pass_VipLobby.png` | VIP Lobby (399) | gold crown above a velvet rope |

Facade packs (99–249) have no icons yet: they want a picture of each facade.

## Developer product icons — `product/`, 512 × 512, colour

Same badge, filling the square (no transparent corners).

| File | Product (GDD §10.2) | Picture |
|---|---|---|
| `product/Product_StarterPack.png` | Starter Pack (99) | gift box with a slime (the Slime facade) wearing a bow, coins, a 30-min clock |
| `product/Product_CallTheBus.png` | Call the Bus (39) | the bus front coming at you, ringing and speed lines |
| `product/Product_2xCash15m.png` | 2x Cash, 15 min (49) | coin, "2x", clock with a quarter filled |
| `product/Product_2xCash1h.png` | 2x Cash, 1 h (149) | coin and a stack, "2x", clock filled |
| `product/Product_2xFriendship.png` | 2x Friendship, 30 min (79) | smiling heart, "2x", clock half filled |
| `product/Product_CashSmall.png` | Cash pack small (49) | a short stack and a coin |
| `product/Product_CashMedium.png` | Cash pack medium (149) | two stacks and loose coins |
| `product/Product_CashLarge.png` | Cash pack large (449) | a money sack, stacks and coins |

Text used: "$" and "2x" only, in Arial Black (`C:\Windows\Fonts\ariblk.ttf`).

## Review

`_sheet.png` (1600 × 1470, not uploaded): every image on the game's dark ground —
the HUD icons tinted at 104 px and at 36 px (plain and on a button), the panel
9-slices stretched to two sizes, Gloom on a panel and alone, the passes
circle-cropped, the products square, each also at 64 px.
