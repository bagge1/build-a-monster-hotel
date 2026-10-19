# Build a Monster Hotel — Game Design Document

| | |
|---|---|
| **Title** | Build a Monster Hotel (name in code: `MonsterHotel`) |
| **Genre** | Co-op venue-management tycoon with a collection layer (concepts A + B from the research) |
| **Platform** | Roblox: phone, PC, tablet, console |
| **Doc version** | 0.1 draft, 2026-10-19 |
| **Research** | [research/reports/Roblox tycoon market and design.md](../research/reports/Roblox%20tycoon%20market%20and%20design.md) |

> **"Build a hotel for monsters. Rare monsters only check in to the best hotel on the street."**

All numbers in this doc are **starting values for tuning**, not final balance. Figures cited from the research are marked as such; everything else is our own design choice.

---

## 1. Vision

### 1.1 Pillars

1. **Every monster is a character.** Each species has a look, a personality, needs and a signature check-in moment. Players collect monsters they're attached to, and those monsters are what make the hotel worth visiting.
2. **The street is alive and contested.** Six hotels share one street and compete for the guests the Night Bus brings. Players compete for arrivals. Nobody can take what another player already owns.
3. **The hotel is never finished.** Open-ended layout, a star rating, residents, new locations. There is no "final statue" (the research's main reason classic tycoons die).
4. **Come back for 10 minutes every day.** Residents earn while you're away, friendship meters fill, the daily featured monster changes, and new families arrive every few weeks. This targets Roblox's 28-day ranking window (play days on Day 1, Days 2–7 and Days 8–28).
5. **Cozy-spooky, fair and kid-safe.** Cute rather than scary. No stealing between players, no paid random items at launch, no countdown offers.

### 1.2 Target audience

- **Core:** ages 9–15 (Roblox *Select* accounts) and 16+.
- New games are shown only to age-checked 16+ players until they pass the Kids/Select evaluation (see §14.3), so the **launch audience is 16+**. The first-session experience must work for teens, not just young kids.
- **Devices:** design mobile-first. Research: 55.6% of players use mobile at least some of the time (GameAnalytics 2026).
- **Content rating target:** Minimal (cartoon spooky, no gore, no jump scares). Confirm through Roblox's maturity questionnaire.

### 1.3 Positioning

| Competitor | Overlap | How we differ |
|---|---|---|
| **Run a Monster Tavern** (launched 29 Sep 2026; 408 CCU, 103k visits on 19 Oct) | Monster customers and staff, building, visits, offline earnings | Rooms matched to species (not food); the shared Night Bus competition; residents, mutations and the Monster Book; Hunter Night; new locations through rebirth |
| Restaurant Tycoon 3, Pet Store Tycoon | Venue sim with NPC customers | Monsters are collectible characters with friendship and mutations |
| Steal a Brainrot, Steal An Egg | Rarity collection, shared arrivals, timers | No player theft; competition is over arrivals, not other players' bases |

**Watch item:** track Run a Monster Tavern's CCU every few weeks until launch.

---

## 2. Core loop

```
            ┌──────────────────────────────────────────────────────────┐
            │                                                          │
   Night Bus arrives ──► monsters walk the street ──► each picks the   │
   (every ~4 min)         and show their wish list     best-matching   │
                                                       hotel           │
                                                          │            │
                                                          ▼            │
   spend cash on rooms,  ◄── guest pays per second ◄── check-in,       │
   decor, amenities,         + tip on check-out         stay, requests │
   staff                                                  │            │
        │                                                 ▼            │
        │                              happy stay → friendship +1 ──► move-in:
        │                                                              resident (passive income)
        └──► better rating + right rooms ──► better and rarer guests ──┘   or staff (automation)
```

| Loop | Length | What happens |
|---|---|---|
| **Moment** | 30 s – 2 min | Catch a bus, pitch a rare guest, check guests in, clean rooms, fulfil a request, buy something |
| **Session** | 10–20 min | Collect residents' earnings, catch 3–5 buses, finish the daily requests, upgrade a room tier, try to win today's featured monster |
| **Long** | Days to weeks | Fill friendship meters, complete the Monster Book, find mutations, rebirth to a new location, seasonal events, new families |

---

## 3. The street and the server

- **Server:** 6 players, 6 plots on one street ("Creepy Lane"). Friends can join friends; private servers are cheap (§10.3).
- **Plot claim:** on joining, the player gets the nearest free plot automatically. Their saved hotel is rebuilt there (the layout is saved relative to the plot, so any plot works).
- **Plot size:** a 12 × 12 cell grid (1 cell = 12 studs, so a 2×2 room is 24 × 24 studs; a floor is 18 studs tall, walls up to the slab above; players are the standard ~5-stud avatar, and furniture, doors and steps are sized for them, not scaled with the grid) per floor. Floors 1–3 at start; more through progression (and a capacity pass).
- **Two bus stops** (his ruling, 2026-10-19): the Night Bus stops twice on the lane, midway between the first two plots and midway between the last two (x = ±90). Monsters walk the pavement and "browse" each hotel (§4.3). Each hotel sign shows its **star rating, its featured room types and its like count**.
- **Mixed locations on one street:** each plot renders its owner's current location (Haunted Manor, Frostfang Lodge…) as a themed facade and ground tile. The bus carries families for every location present on the server. Players who have rebirthed have neighbours who can see what's coming, which builds aspiration.

---

## 4. Monsters

### 4.1 Attributes

| Attribute | Description |
|---|---|
| **Species** | e.g. Slime, Ghost, Vampire Count |
| **Family** | The location it belongs to (Haunted Manor, Frostfang Lodge…) |
| **Rarity** | Common, Uncommon, Rare, Epic, Legendary, Mythic |
| **Required room** | The room type it needs (a vacant room of this type is required to check in) |
| **Preferences** | 2 extra likes (e.g. darkness, organ music, cold, snacks). Each one matched adds score and satisfaction |
| **Pay rate** | Cash per second while staying |
| **Stay length** | How long it stays |
| **Staff affinity** | The staff role it's best at if it moves in |
| **Quirk** | A signature check-in animation, a voice bark, and one in-stay request type |
| **Mutation** | Optional variant rolled on arrival (§4.5) |

### 4.2 Rarity values (starting numbers)

| Rarity | Pay multiplier | Stay | Friendship to move in | Bus slot weight |
|---|---|---|---|---|
| Common | 1× | 90 s | 2 | 60 |
| Uncommon | 3× | 2 min | 3 | 25 |
| Rare | 8× | 3 min | 5 | 10 |
| Epic | 20× | 4 min | 7 | 4 |
| Legendary | 60× | 5 min | 10 | 1 + scheduled |
| Mythic | 200× | 6 min | 15 | scheduled only |

Base pay at Location 1 is **$1/s for a Common**. Each later location multiplies base pay by ×20 (tune).

### 4.3 The Night Bus (shared arrivals)

- **Every 3 minutes** a bus arrives (his ruling, 2026-10-19; it was 4). **How many ride it scales with the players on the server and the rooms vacant on the street, and one bus never fills every room** (his ruling): **40 % of the street's vacant rooms, rounded up** (his), at least 2 and at most 4 per player on the server (PLACEHOLDER bounds, Claude's). It stops at both stops (§3) and lets half its guests off at each.
- **Scheduled rare arrivals** make appointments players can plan around:
  - Epic guaranteed every 3rd bus (~12 min).
  - **Legendary on the :00 and :30 buses** (server clock).
  - **Mythic on the "Midnight Bus"** every 2 hours.
- **One bus ahead, the rare guest is announced** to the whole server: *"A Legendary Vampire Count is on the next bus! Wants: Coffin Suite · darkness · organ music."* Players then rush to build or free up the right room.
- **Browsing** (his ruling, 2026-10-19): the guests do not walk straight off the end of the street. They walk round the lane past the hotels, look at them, and go to one by what they prefer (the score below); players can Pitch them the whole time they are browsing. From its stop a guest walks the lane past the hotels, pausing a couple of seconds at each entrance, and after about a minute goes to the hotel that scored highest (his yes to Claude's proposal, 2026-10-19). A guest no hotel can take walks back to a stop and leaves on the next bus, never off the map's edge.
- **How a guest picks a hotel:**

  ```
  eligible = hotel has a vacant room of the guest's required type
  score    = ratingStars^1.5 × 1.0
           + preferencesMatched × 0.6
           + amenityBonus × 0.3
           + pitchBonus
           + newcomerBoost (Common/Uncommon guests only, low-rated hotels)
  score   *= random(0.9, 1.1)
  → walk to the highest-scoring eligible hotel; ties go to the nearest
  ```

- **Pitching (active play):** when a guest is on the street, a player can run up and **Pitch** it (press E, tap, or a gamepad button): +15% score toward their hotel. One pitch per player per guest. This is the "conveyor sniping" excitement of Steal a Brainrot without anyone losing anything.
- ~~**Never starved:** each hotel also gets private walk-in guests~~ **No walk-ins** (his ruling, 2026-10-19: "monsters spawning at random and walking into the hotel take the point out of the bus"). Every guest comes on the Night Bus. **The only exception is the tutorial's first guest** (his ruling, 2026-10-19: "the tutorial can be the only time a monster spawns from nowhere"), who walks in before the first bus so Gloom can teach check-in.

### 4.4 Stays

1. **Check-in** at the front desk: tapped by the player early on, automated by Front Desk staff later.
2. **In the room:** pays per second into the hotel's **till**. Collect at the till, or automatically with the Auto-Collect pass.
3. **Requests** pop up (room service, extra blanket, a scare-show…). The player can fulfil one personally for a bigger tip; staff fulfil them automatically at lower efficiency. **Active play beats idle play.**
4. **Satisfaction (0–100)** comes from preferences matched, room tier, cleanliness, requests fulfilled and amenities on the floor.
5. **Check-out:** a tip based on satisfaction, a 1–5 star review that feeds the hotel rating, and a friendship point if satisfaction ≥ 80. The room then needs **cleaning** before the next guest (by the player early, Housekeeping staff later). Manual first, automated later is the classic progression.

### 4.5 Mutations

Rolled on arrival (free randomness from play; no purchase can change the odds at launch).

| Mutation | Chance | Pay | Look |
|---|---|---|---|
| Tiny | 5% | ×1.5 | 50% scale, squeaky voice |
| Giant | 4% | ×2 | 150% scale |
| Shadow | 2% | ×3 | Dark silhouette, glowing eyes |
| Golden | 1% | ×5 | Gold material, sparkle |
| Glitched | 0.2% | ×10 | Flicker shader, pixel particles |
| Seasonal (e.g. Pumpkin, Frosted) | Event only | ×4 | Event costume |

Mutations are **material, colour and size variants**: cheap content that doesn't need new rigs.

### 4.6 Friendship and residents (the collection)

- **Friendship is deterministic.** Every happy stay (satisfaction ≥ 80) adds +1 friendship with that species. At the threshold (§4.2), the next happy stay ends with **"Your Vampire Count wants to move in!"**
- **Bonus chance:** each happy stay also has a small free chance of an early move-in (Common 15%, Legendary 3%, Mythic 1%) for surprise moments.
- **Friendship is tracked per species.** A mutated guest that moves in becomes a mutated resident.
- **Residents** live in the **Resident Wing** (capacity 6 at start; grows with progression and a capacity pass). Each resident:
  - earns **25% of its species' pay rate continuously**, times its mutation multiplier;
  - earns **offline at 50% of that, capped at 2 hours** (8 hours with the Night Manager pass);
  - gives one passive perk (e.g. Ghost: +5% cleanliness on its floor; Werewolf: +10% income during Hunter Night).
- **Staff:** a resident can be assigned to a staff role instead of earning passively. Each species has a role it's best at.

| Staff role | Automates | Example best-fit species |
|---|---|---|
| Front Desk | Check-ins | Skeleton, Vampire Count |
| Housekeeping | Cleaning | Ghost (walks through walls) |
| Room Service | Requests | Zombie (slow but tireless) |
| Bellhop | Guest walking speed, check-in time | Mummy |
| Entertainment | Floor fun bonus | Pumpkin Head, Witch |
| Security | Hunter Night defence | Werewolf |

- **Monster Book:** one page per species with all mutations. Rewards:
  - each species found: a cash bonus;
  - each family completed: a permanent +5% income and a cosmetic;
  - each mutation set completed: a title (e.g. "Golden Host").
- **Duplicates:** several residents of the same species are allowed (more income). Choosing who to keep under the capacity cap is part of the game. Residents can be **sent on holiday** (released) for Moon Shards (§5.3).

---

## 5. Building the hotel

### 5.1 Pieces

| Piece | Placement | Purpose |
|---|---|---|
| **Rooms** | 2×2 to 3×3 cells on a floor | Required room types for species; tiers T1–T5 |
| **Lobby** | Ground floor: front desk, till, waiting area, sign | Check-in, rating display |
| **Amenities** | Any floor | Boost needs on that floor (buffet, spa, game room, graveyard garden, organ hall…) |
| **Decor** | Free placement inside rooms and the lobby | Style score, preferences (candles add "darkness", etc.) |
| **Floors** | Vertical expansion; ~~stairs and elevator placed automatically~~ the player buys and places the stairs (§5.4) | Capacity |
| **Facade and sign** | Exterior | Cosmetic; facade styles are a monetization item |

### 5.2 Room types (Location 1)

| Room | Size | Unlock | Serves |
|---|---|---|---|
| Standard Room | 2×2 | Start | Slime, Skeleton, Zombie |
| Garden Room | 2×2 | 3 rooms owned | Pumpkin Head |
| Attic Room | 2×2 | Floor 2 | Ghost |
| Sarcophagus Suite | 2×3 | Rating 2★ | Mummy |
| Potion Loft | 2×3 | Rating 2.5★ | Witch |
| Den Room | 3×3 | Rating 3★ | Werewolf |
| Coffin Suite | 3×3 | Rating 3.5★ | Vampire Count |
| Opera Suite | 3×3 | Rating 4★ + 1 Legendary resident | Grand Banshee |

Each room tier (T1→T5) costs about ×4 the previous tier and adds +50% pay and +10 comfort.

### 5.3 Hotel rating

The rating is 1–5 stars in half steps. It's computed from five categories, each 0–100, and the breakdown is shown in the UI (as in Restaurant Tycoon 2):

| Category | Inputs |
|---|---|
| **Comfort** | Room tiers, matched preferences |
| **Service** | Check-in wait, requests fulfilled, staff coverage |
| **Cleanliness** | Rooms cleaned on time, Housekeeping coverage |
| **Fun** | Amenities, Entertainment staff |
| **Style** | Decor score, variety of room types |

- The rating is a rolling average over the **last 30 reviews** plus the live category scores, so it reacts to play within a session.
- A higher rating brings more and rarer guests through bus scoring and walk-in rate. It also unlocks room types.

### 5.4 Building freely (his rulings, 2026-10-19)

From his first long playtest: a hotel that starts as the whole empty plot
"looks very empty", and a fixed stair core and a fixed reception leave
nothing to arrange. **Customizing the hotel is the most important thing in
the game** (his words, 2026-10-19: "det ska vara mycket customizable, detta
är det viktigaste i spelet"). What he ruled:

- **The plot is bought in areas**, not given whole. One starts as the
  hotel's; the rest are bought, and rooms are built on what is owned. **A new
  hotel starts with only a reception and room for about 2–4 Standard Rooms**
  (his words, 2026-10-19).
- **Stairs are a piece the player buys and places**, one or several, instead
  of a stair core fixed on every floor.
- **Everything can be rebuilt as often as the player likes**, the reception
  too: the front desk is moved like any piece, and so is the lobby's carpet
  (redone, removed or moved with the desk: rugs are pieces, not part of the
  lobby model).
- **Staff are seen working:** a resident on Room Service does not just stand
  by the desk (his report, twice, 2026-10-19).
- **Decorating:** the floor can be changed, and rugs and decorations placed:
  clocks, flowers, plants, furniture, a piano and so on.
- **A room's tier comes from furnishing it:** furniture, rugs and decor in a
  room add up to points that take it to T2 and at last T3, each tier raising
  what the room is worth (replacing tiers T1–T5 bought with cash, §5.2).
- **A forecourt in front of every hotel:** a wider space between the lane and
  the facade, with a pavement the guests walk on and a path from it to the
  entrance; the traps are placed there.
- **A forest round the street**, so the plot is not a bare lawn, and the
  Night Bus drives in round a bend out of the forest instead of appearing.

Open (WAITING §2), with Claude's proposal: an area's size (4 × 5 cells
behind the lobby, six to a floor, so two 2×2 rooms either side of a
hallway fit one), whether an area is bought for every floor at once, how a
stair joins two floors, where the desk may stand, and how freely decor is
placed. Until he answers, §5.1, Appendix A.1 and A.2 describe what is built.

---

## 6. Economy

### 6.1 Currencies

| Currency | Source | Spent on | Rebirth |
|---|---|---|---|
| **Cash ($)** | Guests, tips, residents | Rooms, tiers, decor, amenities, floors | Resets |
| **Moon Shards** | Rebirth; releasing residents; Book milestones | The **Moon Tree** (permanent upgrades) | Kept |
| **Candy** (event currency) | Event play only | Event shop (cosmetics, event rooms, seasonal mutations) | Kept for the event's duration |

**There's no premium currency.** Robux buys passes and products directly, so players always see the real price. This is simpler and safer under the regulatory direction in the research (EU and UK scrutiny of virtual currencies and nudges for children).

### 6.2 Cost curves and pacing

- **New room cost:** `base × 1.15^n`, where n is rooms owned of that type. Room tiers are ×4 per tier.
- **Milestones:** owning 5, 10 and 25 rooms of a type doubles that type's pay each time. Without these, the newest item always dominates (from Kongregate's "Math of Idle Games", cited in the research).
- **Rule of thumb:** each next meaningful purchase costs **2–5 minutes of current income**. Never more than 10 minutes between meaningful purchases (a community rule of thumb from the research).
- **Bonus stacking:** add bonuses within a category (+10% + +5% = +15%) and multiply only across categories. Tune assuming payers own the capacity passes.
- **Numbers:** Luau numbers are exact up to 2^53 (~9 Qa). Location 1–3 balance stays below 1e15. Decide on a big-number library before Location 4 (§13.6).
- **Format:** 1.2K, 3.4M, 5.6B, 7.8T, 9.1Qa.

### 6.3 First-run pacing targets

| Moment | Target |
|---|---|
| First room bought | 0:10–0:30 (starter cash $100; Standard Room $50) |
| First guest pays | by 1:00 (private walk-in Slime) |
| First bus | by 2:00 |
| 3–5 purchases | by 5:00 |
| First resident | by 3:00–5:00 (the tutorial Slime needs 1 friendship) |
| First rare (Vampire Count) | by 10:00–15:00 (the tutorial schedules it) |
| Rebirth visible as a goal | by 15:00 |
| Rebirth available | 60–90 min of active play, or about 3–4 days for a daily 15–20 min player |
| Second run | about 70% of the first |

### 6.4 Rebirth: "Move to a new location"

- **Requirement:** rating ≥ 4★, **$1M earned this run** (tune), and **a Vampire Count resident**. A named monster is a concrete goal, as in Steal a Brainrot.
- **Resets:** cash, rooms, amenities, decor, floors.
- **Kept:** residents, the Monster Book, cosmetics, Moon Shards, Moon Tree, friendship progress, and every room type already unlocked (still buildable at its normal price).
- **Gained:** a new location with a new facade and biome, **a new family of 8–10 species**, new room types and amenities, and **Moon Shards = floor(10 × √(run cash / $1M))**. That's 10 at $1M and 20 at $4M: a square-root curve, so doubling the reward needs 4× the earnings.
- **Why keep residents:** your collection travels with you and becomes the head start for the next run. The research found that rebirths that only add a multiplier "feel the same"; rebirth has to change what the hotel looks like and what you can buy.

### 6.5 Moon Tree (permanent upgrades)

Examples:
- +10% cash (5 levels)
- +1 Resident Wing slot
- +15 min offline cap (no levels beyond +1 h, so the Night Manager pass stays meaningful)
- +5% bus score
- −10% cleaning time
- +1 daily request reroll

Each node costs Moon Shards that grow ×1.5 per level.

### 6.6 Locations (the long road)

| # | Location | Family (8–10 species) | Example species | Status |
|---|---|---|---|---|
| 1 | Haunted Manor | Classic spooks | Slime, Skeleton, Pumpkin Head, Ghost, Mummy, Zombie, Witch, Werewolf, Vampire Count, Grand Banshee | Launch |
| 2 | Frostfang Lodge | Ice and snow | Snowball Sprite, Ice Imp, Frost Troll, Yeti, Snow Witch, Ice Wyrm, Aurora Spirit | Launch |
| 3 | Bayou Spa | Swamp | Bog Frog, Mossling, Gator Ghoul, Will-o'-Wisp, Swamp Hag | +1 month |
| 4 | Volcano Resort | Fire | Fire Imp, Magma Golem, Salamander, Phoenix, Elder Dragon | +2–3 months |
| 5 | Sky Castle | Sky and storm | Gargoyle, Harpy, Cloud Giant, Storm Djinn, Thunderbird | +4–5 months |

All species are original designs. **Avoid protected names and looks** (e.g. no Monsters, Inc., Hotel Transylvania or Phantom of the Opera references).

### 6.7 Location 1 roster

| Species | Rarity | Required room | Preferences | Staff role | Quirk |
|---|---|---|---|---|---|
| Slime | Common | Standard Room | Damp, snacks | Room Service | Wobbles; leaves cute goo footprints |
| Skeleton | Common | Standard Room | Music, quiet | Front Desk | Rattles; tips with a bone |
| Pumpkin Head | Common | Garden Room | Candles, garden | Entertainment | Head glows brighter when happy |
| Ghost | Uncommon | Attic Room | Quiet, antique furniture | Housekeeping | Floats through walls |
| Mummy | Uncommon | Sarcophagus Suite | Dry, dark | Bellhop | Trails bandages |
| Zombie | Rare | Standard Room | Snacks, slow music | Room Service | Very slow; very loyal |
| Witch | Rare | Potion Loft | Cats, cauldron | Entertainment | Brews colourful smoke |
| Werewolf | Epic | Den Room | Moonlight, steak | Security | Howls at check-in |
| Vampire Count | Legendary | Coffin Suite | Darkness, organ music | Front Desk | Bows with a cape swirl; turns into bats |
| Grand Banshee | Mythic | Opera Suite | Silence, chandelier | Entertainment | Her song shakes the whole street (server-wide moment) |

---

## 7. Social and multiplayer

The ranking signal "intentional co-play days" counts, and since age checks cut on-platform chat, **co-play must work without chat**.

| Feature | Description |
|---|---|
| **Contested bus** | §4.3 |
| **Visit and like** | Walk into any hotel on the street, see its residents, give one **like** per hotel per day. Likes show on the sign; the most-liked hotel gets a "Street Favourite" badge |
| **Co-managers** | Invite a friend to co-manage your hotel (build rights as in Theme Park Tycoon 2). The helper earns 10% of the income they generate while helping, on top of their own hotel's income |
| **Friend bonus** | +10% income for everyone on the street while 2+ friends play together |
| **Hunter Night** | Co-op defence of the whole street (§8.1) |
| **Quick pings and emotes** | "Need a Coffin Suite!", "Pitching!", "Thanks!", plus emotes. No typing needed |
| **Leaderboards** | Street (current server): rating. Global: Book completion, lifetime guests, weekly event score |
| **Trading** | **Not at launch.** Duplication exploits wrecked Lumber Tycoon 2's economy. Revisit after launch with atomic, server-validated swaps on one server |

---

## 8. Events and live ops

### 8.1 Hunter Night (co-op PvE raid)

- **When:** every 90 minutes on each server, lasting 3 minutes (tune). Plus the bigger weekly **Full Moon Hunt** on Saturdays.
- **What:** goofy NPC monster hunters (garlic necklaces, butterfly nets, oversized flashlights) come down the street and try to net guests and residents.
- **Defence:**
  - Traps placed in the hotel (slime puddles, creaky floorboards, portrait eyes that scare).
  - Security staff.
  - The player's **Boo!** tool: tap a hunter to scare them off screaming.
  - No damage and no death: hunters run away. This keeps the Minimal rating.
- **Rewards:** Candy or cash, and a **"thankful" bonus bus** of Rare-or-better guests right after a successful defence.
- **Soft failure:** a netted resident goes to the Hunter Camp. The owner rescues it with a short free mini-mission, or it returns on its own after 24 hours. **Never permanent loss, and never a paid rescue.**

### 8.2 Recurring schedule

| Cadence | Content |
|---|---|
| **Daily** | Featured Monster of the Day (double friendship); 3 daily requests (e.g. "Serve 5 Ghosts", "Reach 3★"); 7-day login calendar (cosmetic on day 7; missing a day pauses the streak instead of resetting it) |
| **Weekly** | Full Moon weekend (Werewolf family, more Legendaries); Full Moon Hunt; a "Monster Parade" live window announced in advance (lots of rare guests) |
| **Every 2 weeks** | A new species, room type or amenity (Roblox suggests updates every 2–4 weeks; the research shows weekly cadence burned out Pet Simulator 99 and Adopt Me teams) |
| **Monthly** | Themed event with Candy, an event shop and a seasonal mutation |
| **Quarterly** | A new location and family |
| **Seasonal** | Halloween (our biggest event), Winter (Frostfang crossover), Valentine's, Summer |

---

## 9. Retention design, mapped to Roblox's ranking signals

Source of the signal list: Roblox Creator Docs on discovery (summarised in the research, §6).

| Signal | What we do |
|---|---|
| **Play-through rate** | Honest icon and thumbnail: cute monsters stepping off the bus at a glowing hotel. Test 2–3 variants (§15.2) |
| **First-play bounce** (< 60 s, 61–180 s) | Income visible within the first minute; first purchase in 30 s; first bus by 2 min (§6.3) |
| **Play days (D1, D2–7, D8–28)** | Residents' offline earnings (capped), friendship meters, daily featured monster and requests, scheduled Legendary and Mythic buses, a family every few weeks |
| **Playtime** (counted up to 60 min per user per day) | Good 10–30 min sessions. **Nothing requires AFK farming.** |
| **Intentional co-play days** | Friend bonus, co-managers, Hunter Night, pitching race |
| **Spend days** | Cheap repeatable products (Call the Bus, short boosts) |
| **Return prompts** | Opt-in Experience Notifications, used sparingly: "Your Vampire Count is ready to move in", "Full Moon tonight", "Your residents' till is full" |

**Other hygiene:** a codes system (social media), a group join reward (free decor and +5% cash), settings (music, SFX, low graphics), localization (start with English, Spanish, Portuguese and Japanese; the research shows the fastest DAU growth is outside the US).

---

## 10. Monetization

### 10.1 Principles

1. **Sell convenience, capacity, cosmetics and gifts. Never sell winning.**
2. **No paid random items at launch.** If one is added later: exact odds shown before purchase, and a `PolicyService:GetPolicyInfoForPlayerAsync` check (`ArePaidRandomItemsRestricted`) with a free alternative.
3. **No countdown or "one time only" offers.** Seasonal items come back next year.
4. **Gift versions of every pass.**
5. **Turn on Managed Pricing** (regional prices at 30–100% of default; the research reports more pass purchases in discounted regions).
6. **No 2x Cash pass at launch.** It speeds up the contested bus race, so it's mildly pay-to-win. Timed boosts cover the same desire as repeatable purchases. Revisit with data (§17).
7. **Never monetize loss.** No paid Hunter Camp rescue.

### 10.2 Launch catalog (default prices in Robux; tune with price tests)

**Game passes**

| Pass | Price | What it does |
|---|---|---|
| Auto-Collect Till | 149 | Till cash goes straight to your wallet |
| Night Manager | 249 | Offline cap 2 h → 8 h |
| Resident Wing+ | 249 | +6 resident slots |
| Extra Floor | 299 | +1 floor beyond the progression cap |
| VIP Lobby | 399 | VIP badge, gold name tag, VIP lounge decor set, +1 daily request reroll |
| Facade packs (Gothic, Neon, Candy, Pirate…) | 99–249 each | Exterior styles (cosmetic only) |

**Developer products (repeatable)**

| Product | Price | Notes |
|---|---|---|
| Starter Pack | 99 | Cash, an exclusive Slime facade, a 30-min boost. Always available, no timer |
| Call the Bus | 39 | Brings the next bus early **for the whole server**, announced as "<name> called the bus!". A purchase that helps everyone |
| 2x Cash boost | 49 (15 min) · 149 (1 h) | Timed |
| 2x Friendship boost | 79 (30 min) | Timed; affects friendship only, not odds |
| Cash packs | 49 / 149 / 449 | Scaled to the player's current income (e.g. 10 / 35 / 120 minutes' worth) |
| Private server | ~100 / month | Free for Roblox Plus subscribers (Roblox pays the creator a bonus) |

**Rewarded video ads:** watch an ad for a 15-minute 2x Cash boost, granted through `ProcessReceipt`. Rules from the research:
- optional and never required to progress;
- shown only to players 13+;
- the reward is a non-random developer product;
- the game needs 2,000+ monthly unique visitors to qualify.

### 10.3 Revenue expectations

Research: a creator keeps about 21–27% of each player dollar (more on qualifying US adult spend). The median DevEx creator earned about $1,500 in the year to June 2026. **Plan for modest revenue and treat upside as a bonus.** Creator Rewards also pays 5 Robux per active spender who plays 10+ minutes in a day (if we're among their first three games that day), which is another reason to design for daily returns.

---

## 11. First-time user experience (first 15 minutes)

Guide: **Gloom, the bat concierge** (our mascot). Short speech bubbles, an arrow to the next action, nothing blocks movement for more than a few seconds.

| Time | Beat |
|---|---|
| 0:00 | Spawn on your plot: a tiny lobby with a desk, a till and a sign with your name on it. Gloom: "Welcome, new manager!" |
| 0:10 | Arrow to **Build → Standard Room** ($50 of your $100) |
| 0:30 | A Slime walks in (private walk-in). Tap the desk to check it in |
| 1:00 | Collect from the till. Buy a second room |
| 1:45 | **First Night Bus.** The tutorial weights Commons toward your hotel. Pitch one |
| 3:00 | The first Slime checks out happy → **"Slime wants to move in!"** (tutorial friendship = 1). The Monster Book opens |
| 5:00 | 3–5 purchases done. Goal card: *"A Vampire Count arrives in 3 buses. Build a Coffin Suite!"* (the tutorial schedules it) |
| 8:00 | Clean a room, fulfil a request. Staff tab unlocks (assign the Slime to Room Service) |
| 10:00–15:00 | **The Vampire Count arrives.** If the room is ready: a flashy cape-swirl check-in, bats, a street-wide announcement. This is the "moment of joy" (Roblox onboarding guidance) |
| 15:00 | Preview of Frostfang Lodge, the rebirth goal |
| Session end | Daily requests done → reward. Gloom: "Your residents keep earning while you're away, up to 2 hours." |

**Mobile UI rules:**
- No buttons in the bottom corners (the default movement and jump controls live there).
- Large tap targets; build mode works with one thumb.
- Gamepad navigation for everything.
- Input Action System for all inputs.

---

## 12. Art and audio direction

- **Style:** "cozy creepy". Saturated purples, teals, pumpkin orange and moonlight blue. Chunky stylized shapes, big eyes, soft lighting. Never gore, never jump scares. *(Search for "Monster Hotel" surfaces horror anomaly games, so the icon must read as cute and friendly instantly.)*
- **Monsters:** custom rigs (not avatars), each with 6 animations: walk, idle, happy, sad, check-in flourish, staff action. Mutations reuse rigs with material, colour and scale changes.
- **Hotel kit:** modular, low part count. Textures and meshes over many parts. LODs for neighbours' hotels.
- **Audio:** playful harpsichord, organ and pizzicato music; a short bark per species; a satisfying "ding" on cash; a big fanfare for rare check-ins.
- **AI tooling:** Studio Assistant and Cube/4D generation can speed up props and decor (research §4). Every generated asset gets reviewed for style and part count.
- **Asset safety:** no unvetted Creator Store models. The research found obfuscated scripts in free models that inject purchase prompts.

---

## 13. Technical design

### 13.1 Tooling

- **Rojo** (filesystem ↔ Studio sync), **Rokit** (tool versions), **Wally** (packages), **luau-lsp**, **Selene** (lint), **StyLua** (format), strict Luau types.
- **Git** on this repo; small commits; CI runs Selene and StyLua.
- **No Knit** (archived July 2024). Use plain ModuleScript services and controllers with a typed remote layer (a thin wrapper, or a buffer-based library such as Blink or Zap; decide in M0).

### 13.2 Architecture: the server simulates, the client paints

| Area | Server (authoritative) | Client (visual) |
|---|---|---|
| **Guests** | State machine: Arriving → Browsing → WalkingToHotel → CheckIn → InRoom → Requesting → CheckOut / MoveIn → Leaving. Logical position on a path graph | Renders monster models locally, interpolating along the path. Animations and VFX |
| **Bus** | Spawns the guest list, runs scoring, assigns hotels | Bus model, arrival VFX, announcements |
| **Economy** | Income tick once per second per hotel; batches updates to the client | Animated counters, floating "+$" text |
| **Building** | Validates every placement request | Ghost preview, snapping, rotate UI |
| **Hunter Night** | Hunter AI, net and scare outcomes | Hunter models, scare VFX |

- **Why client-rendered NPCs:** six hotels × many guests as replicated physics models would be too expensive on phones. The server sends compact state changes; clients draw.
- **Remotes:** every remote validated (ownership, funds, bounds, cooldown) and rate-limited. Roblox's rule: "Assume every piece of data sent from the client has been manipulated."
- **Placement:** the client sends only `{itemId, floor, cell, rotation}`. The server rechecks funds, unlocks, collisions and bounds.
- **Data-driven content:** species, rooms, amenities, decor, mutations and locations live in typed data tables (one source of truth). Adding a monster is data plus art, not new code.

### 13.3 Data and saving

- **ProfileStore** (replaces ProfileService): session locking, autosave (default 300 s), save on leave and on shutdown (`BindToClose` gets 30 s).
- **Schema version** with migration functions from day one.
- **Saved:** currencies; layout (item IDs and plot-relative cells, rotations, tiers); residents (species, mutation, friendship, assignment); Monster Book; Moon Tree; unlocked room types; owned passes cache; settings; daily and login state; **processed PurchaseIds**.
- **Purchases:** one `ProcessReceipt` handler. Grant, save, *then* return `PurchaseGranted`. Dedupe by PurchaseId so retries never double-grant.

### 13.4 Streaming and performance

- **StreamingEnabled** on. Each plot model uses the right `ModelStreamingMode`. Client scripts handle plots streaming in and out cleanly.
- **Budgets (starting):** at most ~40 rendered guests per client, at most ~3,000 parts per hotel, and LOD for hotels beyond the player's own and adjacent plots.
- **Test devices:** a low-end Android phone and an older iPhone from M1 onwards.

### 13.5 Platform features

- `PolicyService`, for any future paid random items.
- Rewarded Video Ads API.
- `ExperienceNotificationService` (opt-in prompts).
- `AnalyticsService` funnel events: join, first room, first guest, first bus, first move-in, first themed room, first rare, session end, rebirth.
- Managed Pricing for passes and products.
- **Server Authority mode** (released 9 July 2026) isn't needed: there's no PvP and economy security comes from validated remotes.

### 13.6 Open technical decisions

- Networking library (thin wrapper vs Blink/Zap). Decide in M0.
- Big-number library before Location 4.
- Pathing: precomputed path graph per hotel layout vs PathfindingService. Leaning toward a graph, which is cheaper and deterministic.

---

## 14. Production plan

### 14.1 Milestones (team of 2–4 with one strong scripter; our estimates)

| # | Milestone | Contents | Est. |
|---|---|---|---|
| M0 | Project setup | Rojo project, tooling, CI lint/format, folder structure, data-table format, remote layer | 1 week |
| M1 | Greybox core | Plot claim, grid build (rooms), walk-in guests, check-in, pay, till, save/load with ProfileStore | 3 weeks |
| M2 | The street | Night Bus, guest scoring, wish lists, pitching, rating v1, cleaning and requests | 2 weeks |
| M3 | Collection | Friendship, residents, staff, Monster Book, mutations | 3 weeks |
| — | **First playable** | Friends and family playtest; first thumbnail tests | — |
| M4 | Progression | Economy pass, rebirth, Location 2 (Frostfang Lodge), Moon Tree, FTUE with Gloom, mobile UI | 3 weeks |
| M5 | Live systems | Passes, products, receipts, rewarded ads, daily requests, login calendar, codes, notifications, analytics funnel | 2 weeks |
| M6 | Polish | Hunter Night v1, art and audio pass, performance, localization, QA | 4 weeks |
| — | **Soft launch** | About 18 weeks from start (≈ late February 2027 if we start now) | — |

### 14.2 Soft launch goals

The research targets are **inferred from GameAnalytics percentiles, not tycoon-specific data**:

| Metric | Median Roblox game | Our target |
|---|---|---|
| D1 retention | 10.3% | **13–16%** |
| D7 | 1.6% | **2.5–5%** |
| D30 | 0.5% | **1–1.5%** |
| Session length | 9.8 min | **12–15+ min** |
| Payer share | 3.8% (GameAnalytics sample) | Track |

Iterate on the FTUE until D1 hits the target **before** spending on ads. Ad-acquired players don't count toward ranking, so use ads to *measure* thumbnails and onboarding, not to buy rank.

### 14.3 Reaching Kids and Select accounts

After the soft launch we apply for Kids/Select eligibility:
- creator ID verification and 2FA;
- a refundable fee or a Plus subscription;
- a Minimal or Mild rating;
- an engagement bar: current docs say **250 unique plays from highly engaged, age-checked players within 60 days**, while the June forum post said 500. **Check the live docs before planning.**

### 14.4 After launch

- Every 2 weeks: a new species, room or amenity.
- Monthly: an event.
- Quarterly: a new location.
- Halloween 2027 is the first big tentpole.
- **Plan for a sequel from day one:** keep data portable so a future "Build a Monster Hotel 2" could carry players' residents across (as Pet Simulator carried pets from PSX into PS99).

---

## 15. Validation before and during development

1. **Competitor watch:** check Run a Monster Tavern's CCU, updates and features at each milestone.
2. **Thumbnail and title test** (during M2–M3): 2–3 honest icon and thumbnail variants on small ad budgets. Measure click-through and choose the winner. Research benchmark: tycoon ads with generic icons got 0.1–0.6% click-through; aim for 2%+ before scaling any ad spend.
3. **First-playable playtests** after M3: watch where new players stall in the first 5 minutes.
4. **Soft-launch funnel:** the AnalyticsService events in §13.5 show where players drop off.

---

## 16. Risks

| Risk | Impact | Mitigation |
|---|---|---|
| Run a Monster Tavern grows into the space first | High | Differentiate hard (bus, residents, Book, Hunter Night, locations); a faster first playable; watch it |
| Character art and animation cost | High | 10 species at launch for Location 1 + 7 for Location 2; mutations as cheap variants; reuse rig templates; AI-assisted props |
| NPC simulation too heavy on phones | High | Client-rendered NPCs, render caps, LOD, low-end device testing from M1 |
| The contested bus feels unfair to new players | Medium | Private walk-ins, newcomer boost, scheduled rares that everyone can plan for |
| Players finish Location 1 and leave | High | Rebirth unlocks new content; friendship and Book goals; events; 2-week updates |
| Search confusion with horror games | Medium | Cute art, clear icon, "cozy" wording in the description |
| Content treadmill burnout | Medium | A 2-week cadence (not weekly); data-driven content pipeline |
| Policy changes (paid random items, ads, age tiers) | Medium | Deterministic store; recheck policies at each milestone |
| Unknown real retention | High | Validate early (§15); don't scale spend until D1 hits target |

---

## 17. Open questions

1. **Room pricing:** can players set their own room prices (Restaurant Tycoon 2 style), or are prices fixed per tier? *(Leaning: fixed at launch.)*
2. **Residents through rebirth:** keeping them is the current plan. Check that it doesn't trivialise later runs.
3. **2x Cash pass:** excluded at launch. Revisit after soft-launch data.
4. **Trading residents** after launch: yes or no?
5. **Server size:** 6, or 8 with 2 visitor slots?
6. **Mascot:** is Gloom the bat right? Name and look.
7. **Hunter Night frequency:** every 90 min, or only scheduled windows?
8. **Launch timing:** soft launch around late February 2027, or hold for a bigger spring launch?
9. **Team:** who owns art and animation? This is the critical path.

---

## 18. Decision log

| Date | Decision | Why |
|---|---|---|
| 2026-10-18 | Research completed (6 topics) | See `research/` |
| 2026-10-19 | Blend concepts A (co-op venue sim) and B (collect-and-protect idle) | Durability of venue sims plus the return hooks of the 2025–26 hits |
| 2026-10-19 | Theme: monster hotel | The theme was empty in Roblox search on 19 Oct (largest game: 3 players); characters drive attachment and clips |
| 2026-10-19 | Title: **Build a Monster Hotel** | The verb-noun format of current hits; "Monster Hotel Tycoon" is already taken by a dead game; avoid "Run a…" (Run a Monster Tavern) |
| 2026-10-19 | No stealing between players; PvE Hunter Night instead | The most copied mechanic, look-alike risk, child-safety and pay-to-win criticism |
| 2026-10-19 | No paid random items and no 2x Cash pass at launch | Policy simplicity, fairness in the contested bus |
| 2026-10-19 | Iron Frontier (C+D) stashed as the next game | `D:\Roblox\iron-frontier\CONCEPT.md` |
| 2026-10-19 | Standard ~5-stud avatar, 6-stud grid cells | His ruling on the scale of a person (CLAUDE.md) |
| 2026-10-19 | **The grid doubles: 12-stud cells, 18-stud floors**, walls up to the slab; furniture, doors and steps stay person-sized | His ruling after walking the new lobby in the game: "its a bit cramped. Could probably double everything just about. The roof is also a couple studs above the walls, not connected." Picked over "only the lobby" and 1.5×, and 18 over 12 or 24 studs a floor |
| 2026-10-19 | The street at the doubled scale: the lane stays 48 wide, the Resident Wing 48 deep, **36-stud gaps** between the 144-stud plots, the lane to ±278 | His picks for the lane and the Wing; the gap was Claude's pick within the 24–48 he gave ("Do what you think seems reasonable"): twice the room between hotels without stretching the lane more than needed (about 70 s to browse it at BrowseSpeed 8). His clarification: "only things that made sense to double, like making the hotel less cramped" (`CLAUDE.md`) |
| 2026-10-19 | GitHub repo `build-a-monster-hotel`, private; folder renamed to match | His ruling |
| 2026-10-19 | Night sessions may commit, push and run DataStore-writing playtests | His go (the game is not live) |
| 2026-10-19 | The lobby is an indoor reception: a front wall with the entrance arch and windows; the desk across the end away from the stairs, served toward the entrance, a key rack behind the clerk; the back row clear for the floor-1 doors; the hotel sign on its posts at the stair-side corner of the forecourt, off the entrance (layout A and the corner sign of three grey drafts; `MODELS.md`, "Lobby") | His rulings: nothing in front of an entrance, a counter a person can stand at, a lobby that reads as a reception and not a patio (`modelling/taste.md`) |
| 2026-10-19 | A forecourt in front of each hotel: a pavement the guests walk on, a path to the entrance, the traps placed there (§5.4) | His ask from playing |
| 2026-10-19 | A room's tier (up to T3) comes from the furniture, rugs and decor in it, not cash; a forest round the street, the Night Bus driving in out of it; room names on a wooden plaque over the door (§5.4, `MODELS.md`) | His asks from playing |
| 2026-10-19 | The plot is bought in areas; stairs are bought and placed (one or several), not a fixed core; everything can be rebuilt, the reception too; the floor can be changed and rugs and decorations (clocks, flowers, plants, furniture, a piano) placed (§5.4) | His rulings from playing: the whole empty plot at the start looks empty, and a fixed stair and desk leave nothing to arrange |
| 2026-10-19 | The bus every 3 minutes, 40 % of the street's vacant rooms per bus, guests browse past the entrances for about a minute, and the tutorial's first guest is the only walk-in (§4.3) | His answers to WAITING §2.14 |
| 2026-10-19 | The Night Bus stops twice (between the first two plots and between the last two); its guests browse round the lane and pick a hotel by preference, Pitchable the whole time, instead of walking off the end; no walk-ins; the bus's size scales with the players and the street's vacant rooms and never fills every room with one bus (§3, §4.3, A.3) | His rulings from playing: guests vanishing at the map's edge, and walk-ins that make the bus pointless |
| 2026-10-19 | *Night draft:* remote layer is a thin typed wrapper over RemoteEvents (`src/shared/Net.luau`), not Blink/Zap (§13.6) | Reversible: every remote is declared in one file, so swapping the transport touches one module |
| 2026-10-19 | *Night draft:* guest paths are a grid graph over free cells (§13.6) | Cheaper and deterministic, as the section leaned; Appendix A.1 |

---

## Appendix A. Night drafts (2026-10-19), for August's review

The first night sprint built the game from this document. Where the document
leaves a value or a shape open, the night took a **reversible draft**, written
here before it was built. **Nothing in this appendix is his decision yet.**
Every number below is a **placeholder** (tagged `PLACEHOLDER` in
`src/shared/Constants.luau`); the questions that are his are in `WAITING.md` §2.

### A.1 The street and the plot (§3)

- **Street:** one straight pedestrian lane along world X. Plots 1–3 on the north
  side face south, plots 4–6 on the south side face north. Plot fronts are 24
  studs from the centre line (the lane stays 48 wide); plots are 144 studs wide
  with 36-stud gaps, so the lane runs to ±278 (26 past the last plot). The
  **bus stop is at the west end**. Guests from a bus walk east down the centre
  of the lane ("browsing"), then turn to the hotel they picked.
- **The plot frame:** cell (x, z), x 0–11 along the street, z 0–11 away from it;
  floor 1 at ground level, each floor 18 studs above the last (his ruling, 2026-10-19 evening).
- **Reserved cells** (to be replaced by §5.4: areas, placed stairs, a movable desk): the **Lobby** is the front two rows of floor 1 (z 0–1):
  entrance in the middle, front desk, till, waiting spots. The **stair core** is
  cells x 10–11, z 2–3 on every floor (stairs for players; guests glide up it).
- **The Resident Wing** is a garden behind the hotel (48 studs deep), where
  residents wander.
- **The facade:** walls with window openings along the left, right and back
  edges of every floor, just outside the grid (never on a cell); floor 1's
  back wall has an 8-stud doorway to the Wing, and its sides are solid along
  the lobby. The street side is the lobby's front wall on floor 1 (his ruling,
  2026-10-19, below) and stays open above it.
- **Hallways are the free cells.** A room's door opens onto the cell in front
  of its front edge. A placement is refused if its door cell is not free and
  connected to the floor's way in (the lobby on floor 1, the stair core above),
  or if it would cut off another room's door. That connectivity graph is also
  the guests' path graph (§13.6, "a graph").

### A.2 Pieces and prices (§5, §6.2)

| Room | Base cost (PLACEHOLDER except Standard) |
|---|---|
| Standard Room | $50 (GDD §6.3) |
| Garden Room | $150 |
| Attic Room | $400 |
| Sarcophagus Suite | $1,500 |
| Potion Loft | $4,000 |
| Den Room | $12,000 |
| Coffin Suite | $40,000 |
| Opera Suite | $250,000 |

- **Floors:** floor 1 is free; floor 2 $500, floor 3 $5,000 (PLACEHOLDER). Cap
  3, +1 with the Extra Floor pass.
- **Decor** sits in a room's decor slots (three per room, attachments
  `Decor_1`–`Decor_3`) and gives that room preference tags:

  | Decor | Tags | Cost (PLACEHOLDER) |
  |---|---|---|
  | Puddle Rug | damp | $30 |
  | Snack Basket | snacks | $40 |
  | Record Player | music, slow music | $60 |
  | Candles | candles, darkness | $40 |
  | Planter | garden | $50 |
  | Antique Wardrobe | antique furniture | $300 |
  | Blackout Curtains | dark, darkness, quiet | $250 |
  | Sand Tray | dry | $250 |
  | Cat Basket | cats | $1,200 |
  | Cauldron | cauldron | $1,500 |
  | Moon Window | moonlight | $5,000 |
  | Steak Platter | steak | $4,000 |
  | Pipe Organ | organ music, music | $15,000 |
  | Chandelier | chandelier | $60,000 |
  | Soundproof Walls | silence, quiet | $50,000 |

- **Amenities** are 2×2 pieces on a floor: they add their tags to every room on
  that floor and score **Fun**.

  | Amenity | Tags | Cost (PLACEHOLDER) |
  |---|---|---|
  | Snack Bar | snacks | $300 |
  | Music Room | music, slow music | $800 |
  | Graveyard Garden | garden, darkness | $2,500 |
  | Quiet Library | quiet, antique furniture | $6,000 |
  | Organ Hall | organ music, music | $30,000 |

- **Upgrading a room tier** costs base × 4^tier (T1→T2 is 4× the base).
- **Selling** a room refunds half of what it cost (PLACEHOLDER); an occupied or
  reserved room cannot be sold.

### A.3 Guests (§4.3, §4.4)

- **Satisfaction** (0–100) = 50 + 15 per preference matched + 5 per tier above
  T1 + 5 per amenity on the floor (at most 15) + 10 per request fulfilled by the
  player (5 by staff) − 10 per request that ran out − 1 per 5 s waited at the
  desk past 10 s (at most −20). **Matching both preferences makes a T1 stay
  happy (80).**
- **Tip** on check-out = pay rate × stay × satisfaction/100 × 0.25.
- **Review** = 1 + floor(satisfaction / 25) stars, 1–5.
- **Requests:** one per stay, at a random moment in its middle half, open for
  30 s. Fulfilled at the room's door.
- **Cleaning:** a hold of 2 s at the room's door; Housekeeping staff clean a
  room after 20 s.
- ~~**Walk-ins:** each hotel gets one every 30 s ÷ (1 + 0.15 × rooms) × (3 ÷
  rating), clamped to 8–60 s.~~ Struck by his ruling, 2026-10-19 (§4.3: no
  walk-ins).
- ~~**Browsing** lasts as long as the walk down the lane (~40 s). Each guest
  decides at the east end.~~ Replaced by his ruling, 2026-10-19 (§4.3: two
  stops, guests browse round the lane for about a minute). A
  guest waits at most 60 s at the desk, then leaves unhappy (a 1★ review).
- **Newcomer boost** (§4.3): +1.0 score for hotels rated 2★ or less, Common and
  Uncommon guests only.
- ~~**Bus size:** 6 guests for one player, +1 per extra player, at most 10.~~
  Replaced by his ruling, 2026-10-19 (§4.3: by players and vacant rooms).

### A.4 Rating (§5.3)

Each category 0–100: **Comfort** from room tiers and the share of preferences
matched in recent stays; **Service** from desk waits and requests fulfilled;
**Cleanliness** from the share of rooms clean now; **Fun** 15 per amenity and
20 per Entertainment staff; **Style** 4 per decor piece and 10 per distinct room
type. A hotel nobody has stayed in has no Service, and one with no rooms no
Cleanliness. The rating = the mean of (1 + 4 × (category mean / 100)^1.5) and
the mean of the last 30 reviews (the category part alone with no reviews),
rounded to a half star, 1–5. (First draft used a straight line and gave an
empty hotel 2.5★, unlocking §5.2's 2★ and 2.5★ rooms at once; seen in the
first playtest, 2026-10-19.)

### A.5 Collection (§4.5, §4.6)

- **Resident Wing** capacity 6, +1 per Moon Tree level, +6 with the pass.
- **Staff effect:** a staff member of its species' best role works at 100 %, any
  other at 60 %. Front Desk checks a waiting guest in after 6 s ÷ efficiency;
  Housekeeping cleans after 20 s ÷ efficiency; Room Service fulfils after 12 s ÷
  efficiency (counting as staff); Bellhop makes guests walk 25 % faster;
  Entertainment adds 20 Fun; Security scares a hunter in reach every 8 s.
- **Book rewards:** a species found pays 60 s of that species' pay; a family
  completed is +5 % income; a mutation set completed gives a title.
- **Releasing a resident** ("holiday") gives Moon Shards by rarity: 1 / 2 / 4 /
  8 / 15 / 30.
- **Perks** (§4.6 "one passive perk"; two are the GDD's own examples, the rest
  night drafts): every resident gives its perk, in the Wing or on staff, and
  perks of a kind add up. Slime +5 % tips; Skeleton +5 Service; Pumpkin Head +5
  Fun; Ghost +5 Cleanliness (§4.6); Mummy +5 % guest walking speed; Zombie +5 %
  resident income; Witch +5 % request tips; Werewolf +10 % income during Hunter
  Night (§4.6); Vampire Count +5 % bus score; Grand Banshee +10 % income.
  Frostfang: Snowball Sprite +5 % tips; Ice Imp +5 Fun; Frost Troll +5 Service;
  Yeti +5 Cleanliness; Snow Witch +5 % request tips; Ice Wyrm +5 % bus score;
  Aurora Spirit +10 % income.

### A.6 Progression (§6.4–§6.6)

- **Moon Tree nodes:** Cash +10 % (5 levels), Wing +1 slot (5), Offline +15 min
  (4, so +1 h), Bus score +5 % (5), Cleaning −10 % (3), Daily reroll +1 (2).
  Base cost 5 shards, ×1.5 per level.
- **Frostfang Lodge** (Location 2) draft roster, all original:

  | Species | Rarity | Room | Preferences | Staff | Quirk |
  |---|---|---|---|---|---|
  | Snowball Sprite | Common | Igloo Room | cold, cocoa | Room Service | Rolls instead of walking |
  | Ice Imp | Common | Igloo Room | cold, mischief | Bellhop | Leaves frost handprints |
  | Frost Troll | Uncommon | Ice Cave | cold, stone | Security | Sleeps standing up |
  | Yeti | Rare | Yeti Den | snow, quiet | Housekeeping | Shakes off snow at check-in |
  | Snow Witch | Epic | Frost Loft | cocoa, northern lights | Entertainment | Knits icicles |
  | Ice Wyrm | Legendary | Glacier Suite | cold, northern lights | Front Desk | Coils around the desk |
  | Aurora Spirit | Mythic | Aurora Dome | northern lights, silence | Entertainment | Paints the sky green |

  Rooms (PLACEHOLDER costs, ×20 Location 1's ladder): Igloo Room 2×2 $1,000;
  Ice Cave 2×3 $8,000 (2★); Yeti Den 3×3 $60,000 (3★); Frost Loft 2×3 $200,000
  (3.5★); Glacier Suite 3×3 $800,000 (4★); Aurora Dome 3×3 $5M (4★ + 1
  Legendary resident). Decor adds Ice Block (cold), Cocoa Mug (cocoa), Snow
  Globe (snow), Rock Pile (stone), Prank Box (mischief), Aurora Lamp (northern
  lights).
- **Second-run rebirth** needs 4★, $20M earned this run (×20) and an Ice Wyrm
  resident (PLACEHOLDER, mirrors the first).

### A.7 First-time experience (§11)

Gloom's steps, each seen happen on the server: Build a Standard Room → check in
the walk-in Slime → collect the till → buy a second room → see a bus (pitch one)
→ the Slime moves in (the tutorial Slime's stay counts as happy and needs 1
friendship) → the goal card (the tutorial unlocks the Coffin Suite and sends a
Vampire Count once one is built) → clean a room → assign the Slime to staff →
the Frostfang preview. Skippable at any step, never locking movement.

### A.8 Hunter Night (§8.1)

Hunters walk from the east end of the street, each toward one hotel, and take
45 s to reach its entrance. A hunter at the door nets one guest (or, with none, a
resident) and leaves. **Boo!** scares a hunter within 40 studs (a click or tap
on it). **Traps** (the lobby's `Trap_1`–`Trap_3`): Slime Puddle $500, Creaky
Floorboards $2,000, Portrait with Eyes $8,000 (PLACEHOLDER; all three act
alike for now); each scares the first hunter within 10 studs, once a night. A defended night (fewer than half the
hunters reached a door) pays every player on the street 5 minutes of their
income and sends a bonus bus of Rare-or-better guests. A netted resident is in
the Hunter Camp at the east end; a prompt there rescues it, or it comes back by
itself after 24 h.

### A.9 Live systems (§8.2, §9, §10)

- **Daily requests:** three a day (UTC), drawn from: host 5 happy stays, check
  in 10 guests, clean 5 rooms, pitch 3 bus guests, answer 4 requests, collect
  the till 6 times, reach the next whole star, serve 3 of a Common/Uncommon
  species. Each pays 8 minutes of current income; all three, +1 Moon Shard.
  One free reroll a day, +1 per Moon Tree level, +1 with VIP Lobby.
- **Login calendar:** days 1–7 pay 3/4/5/6/8/10/15 minutes of income; day 7
  gives a cosmetic (a lantern for the sign). A missed day pauses the streak.
- **Featured Monster of the Day:** one species of the hotel's family by UTC
  day, the same on every server; its happy stays count double.
- **Codes:** `WELCOME` ($500) and `SPOOKY` (3 Moon Shards) as placeholders.
- **Cash packs** are 10 / 35 / 120 minutes of current income (§10.2), where
  income is the guests in rooms plus the Wing, at least $10/s. The Starter
  Pack gives 10 minutes of income (at least $500), the Slime facade and a
  30-minute 2x Cash boost, once per player. Timed boosts count down in play
  time.
- **Notifications:** the opt-in is offered once, after the first move-in.
  Sending them needs Open Cloud from outside the game (not built).
- **Gift passes** (§10.1 point 4; built 2026-10-19 as WAITING §2.6's
  recommended option, reversible): one developer product per pass, "Gift:
  <pass>", at the pass's own price. The giver picks a player **on the same
  street** (server) who does not own the pass; the purchase sends the pass to
  the recipient's profile as a ProfileStore message, so it arrives even if
  they leave before the purchase finishes, and it is kept **as if bought**
  (never cleared by the join's ownership check). If the recipient is lost
  (a receipt retried on another server after a crash), the giver gets the
  pass rather than nothing.

### A.10 Events (§8.2)

All by the UTC clock, the same on every server:

- **Full Moon weekend** (Saturday and Sunday): Legendary bus weight ×3, Epic ×2.
- **Full Moon Hunt** (Saturday 20:00): a Hunter Night with twice the hunters.
- **Monster Parade** (Friday 18:00–18:10, announced at 17:45): a bus every
  minute; Common ×0.5, Rare ×2, Epic ×3, Legendary ×4.
- **Seasons:** Halloween (1 October – 3 November) rolls the Pumpkin mutation
  at 3 % and has Candy; Winter (10 December – 5 January) rolls Frosted.
- **Candy:** +1 per happy stay (+2 Epic, +3 Legendary and up), +10 for a
  defended Hunter Night; starts from zero each season.
- **Candy shop (Halloween):** Jack-o'-Lantern decor (30; candles, garden, any
  location), Pumpkin sign (60) and Bat bunting (90) cosmetics. The cosmetics
  are not drawn yet (no facade or sign models).
- **Winter** (built 2026-10-19 as a night draft, every part his to change):
  §8.2 names it "the Frostfang crossover". Winter has its own event currency,
  **Snowflakes** ❄, earned exactly as Candy is and starting from zero each
  Winter, and a **Winter shop** of Frostfang-flavoured things for any
  location: Snowman decor (30; cold, snow, so a Frostfang hotel's guests like
  it), an Icicle sign (60) and Fairy lights across the lobby (90), the same
  costs as the Candy shop. Each season has its own shop (`Events.Shops`).
  Not built: Frostfang guests on the Haunted Manor bus during Winter (a
  bigger crossover; WAITING §2).
- **Wearing cosmetics** (built 2026-10-19, night draft): a hotel wears one
  cosmetic per slot, **Sign**, **Lobby** and **Facade**, picked with the
  build mode's **🎨 Style** tool (`src/shared/Cosmetics.luau`). Sign: Pumpkin
  sign, Icicle sign, the Lantern sign (login day 7), a crest per completed
  family. Lobby: Bat bunting, Fairy lights. Facade: the Slime facade (Starter
  Pack), a colour scheme until the kit has facade styles. The §10.2 facade
  packs (Gothic, Neon, Candy, Pirate) will be Facade-slot cosmetics sold as
  passes. Every one is drawn as a Luau blockout until its model exists
  (MODELS.md, "Cosmetics").

