# Economy pacing after the street and free building, 2026-10-19 evening

These are measurements: no value was changed. `tools/balance_model.py` no longer
runs on main (seven formula guards fail), so a copy outside the repo was updated
to 376cb39. The copy has:

- no walk-ins;
- a bus every 180 s, sized clamp(ceil(0.4 × vacant), 2, 4);
- a 60 s browse, then 30 s to the desk;
- rooms 20 s from the desk on floor 1, plus 25 s a floor (floor 3 at 70 s, as
  measured);
- tiers from decor points;
- about 12 usable cells per area per floor;
- the tutorial Vampire booked on a bus.

"Before" is the old model at 5e36115, rerun. Every figure is a median of 8
seeds, and each cell gives the tutorial path / the tutorial skipped.

| Measure | Before | After | Target |
|---|---|---|---|
| Guests/h, first 15 min | 284 / 136 | 16 / 8 | |
| Guests/h, first hour | 466 / 402 | 49 / 21 | |
| Guests/h, 60–120 min | — / 527 | 79 / 61 (cap 80) | |
| Paying occupancy, first hour | 34 / 41 % | 16 / 13 % | |
| Paying occupancy, 60–120 min | — / 31 % | 10 / 12 % | |
| $/min, average over 0–15 min | 4.4k / 394 | 86 / 26 | |
| $/min, average over 0–60 min | 16.0k / 9.5k | 3.4k / 225 | |
| First guest pays | 0:36 / 1:13 | 0:59 / 5:15 | ≤1:00 |
| First Vampire stay | 2:34 / 0:35 h | 15:49 / 2:32 h | 10–15 min |
| 4★ | 8:10 / 16:45 | 17:20 / 29:33 | |
| $1M this run | 1:02 / 1:19 h | **2:33 / 4:25 h** | |
| Vampire resident | 0:08 / 4:04 h | 3:33 / 5:24 h | |
| Rebirth available | 1:02 / 4:04 h | **3:33 / 5:24 h** | 60–90 min |

## What changed most

1. **Guests fell about tenfold.** A solo bus brings at most 4 guests every 3
   minutes, so 80 an hour, where walk-ins brought up to 450. A hotel with 8 or
   more vacant rooms already gets the maximum. Early on, the bus brings 2
   guests, and only about 45 % of them want a Standard Room.
2. **Rooms stand empty 84–90 % of the time.** More rooms add only milestones.
3. **$1M takes 2.5–3.4 times longer.** Tiers became cheap ($300 of decor for
   T3), so guests are the limit, not cash.
4. **The tutorial's free 3×3 Coffin Suite does not fit** beside two Standard
   Rooms in the start area. Its $500 floor is affordable only at about 13:46.
   The Vampire is no longer a gift, so its residency (friendship 10) is the
   slowest rebirth requirement.
5. **Without the tutorial, the first guest pays at 5:15**, because nobody walks
   in.

Faster walks (floor 1 at 10 s, 20 s to the desk) move $1M without the tutorial
from 4:25 to 3:46.

## Proposals for August (numbers only)

| Change | $1M (tutorial / skipped) | Rebirth |
|---|---|---|
| Bus bounds 2–4 → 3–8 per player (PLACEHOLDER) | 2:12 / 2:58 h | 3:26 / 5:12 h |
| Stays doubled (Common 180 s … Legendary 600 s; §4.2 starting values) | 1:39 / 2:41 h | 3:33 / 4:37 h |
| Both | **1:20 / 1:54 h** | 3:08 / 4:30 h |
| Both, and Legendary friendship 10 → 5 | 1:20 / 1:54 h | **1:40 / 2:41 h** |
| RunCash $1M → $250k alone | 1:07 / 2:40 h | still needs the resident |

- The tutorial Coffin Suite needs a placeable spot: for example a free floor 2
  at the goal card, or a start area that fits a 3×3.
- Not proposed: the bus interval, the 40 % share and BasePay (his rulings).

**Not modelled:** other players, pitching, Hunter Night, events, perks,
offline income.
