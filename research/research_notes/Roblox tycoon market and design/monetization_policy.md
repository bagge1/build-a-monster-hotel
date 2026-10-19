# Monetization of Roblox Tycoon Games and the Roblox Policies That Constrain It (research as of 18 Oct 2026)

Method note: Besides web sources, I pulled live store data from Roblox's public APIs on **2026-10-18** for 13 games (game passes, developer products, visits, concurrent players). These are first-hand, dated observations. Caveat: the APIs return each item's **default (base) price**. With Managed/Regional Pricing, players in lower-income regions can see 30–100% of that price. The API sources are:
- Game passes: `https://apis.roblox.com/game-passes/v1/universes/{universeId}/game-passes?passView=Full&pageSize=100`
- Developer products: `https://apis.roblox.com/developer-products/v2/universes/{universeId}/developerproducts?limit=100`
- Visits and players: `https://games.roblox.com/v1/games?universeIds={universeId}`

Universe IDs used: Retail Tycoon 2 = 2092410051, Restaurant Tycoon 2 = 1214576306, Restaurant Tycoon 3 = 7094518649, Theme Park Tycoon 2 = 31970568, Car Dealership Tycoon = 605887098, Military Tycoon = 2788648141, War Tycoon = 1526814825, Steal a Brainrot = 7709344486, Grow a Garden = 7436755782, Pet Simulator 99 = 3317771874, Pet Store Tycoon = 10282097014, Mansion Tycoon = 4518160318, Army Commander Tycoon = 10768458048.

---

## 1. Which monetization products do successful tycoons use, which earn most, and what do they cost?

### Takeaway
Successful 2026 tycoons sell two things. The first is a **small set of permanent game passes**: auto-collect, 2x cash/income, VIP, bigger plot/more land, more workers or item limits, sandbox/creative tools, and premium vehicles or units. These sit mostly at **149–799 Robux**, with "hero" items at 999–1,999. The second is a **large, frequently refreshed catalog of developer products**: cash packs, timed boosts, skips/"complete now," restocks, starter packs, limited-time items, crates/eggs/spins, and **gift versions of every pass**. In the big hits, developer products are clearly the main revenue engine. Roblox's own docs say dev products "generally monetize better" because they can be bought repeatedly. Premium-only perks are now obsolete: Roblox Premium closed to new sign-ups on 30 Apr 2026 and was replaced by Roblox Plus.

### Cited Findings
**Roblox's own guidance on product types**
- Developer products "generally monetize better, as they can be repeatedly purchased." Passes are one-time and "useful for things like VIP passes, content bundles, or battle passes." — [Roblox Creator Docs, Monetization get-started](https://create.roblox.com/docs/en-us/get-started/monetization.md)
- The official product types are passes (one-time), developer products (repeatable; the creator must persist purchase data), subscriptions, private servers, paid access, immersive ads, paid random items, catalog commissions, and Roblox Plus incentives. — [Roblox Creator Docs, Monetization overview](https://create.roblox.com/docs/production/monetization)
- Analytics advice from Roblox:
  - To raise ARPPU, "add repeatable purchases such as consumables, refills, and currencies… seasonal items."
  - To raise payer conversion, consider "welcome offers or discounts for first-time buyers."
  - To raise ARPDAU, offer "items across a range of price points." — [Roblox Creator Docs, Monetization analytics](https://create.roblox.com/docs/production/analytics/monetization)

**Live store data for classic tycoons (default prices, pulled 2026-10-18)**
- **Restaurant Tycoon 2** (1.65B visits, about 2.6k concurrent).
  - Passes: Auto Money Collection 200; More Worker Slots 500; 2x Faster Cooking 1,299; 2x VIP Customers 450; 2x Eating Speed 600; Earnings Booster 50; 2x Item Limit 250; Reduce Grid Size 220; Statue Pack 180; Paint Vehicles 60.
  - Dev products:
    - Cash packs: 75 (250 cash), 145, 250, 500, 900, 1,500 (10k cash).
    - Timed boosts: 1.5x for 10 min/30 min/2 h/8 h at 40/75/200/400; 2x for 10 min/30 min/2 h/8 h at 80/150/400/800.
    - Starter Pack 250, plus a "Starter Pack (Discounted)" at 175.
    - Plot and feature unlocks: Expanded Plot 120/240/320, Second Floor 1,600, MEGA Plot 3,200, Drive Thru 640, Delivery 700, Food Truck 500, Extra Save Slot 25.
  - — [Roblox API, RT2 passes](https://apis.roblox.com/game-passes/v1/universes/1214576306/game-passes?passView=Full&pageSize=100); [Roblox API, RT2 dev products](https://apis.roblox.com/developer-products/v2/universes/1214576306/developerproducts?limit=100)
- **Restaurant Tycoon 3** (381M visits, about 13.8k concurrent).
  - Passes: Sandbox Mode 1,499; Auto Money Collection 299; Precision Build 599; 3x Customer Luck 399; Allow Build Collisions 349; 2x Item Limits 299; 2x Milestone Boost 249; cosmetic bundles 349–399.
  - Dev products: Starter Pack 149; Skip Objective 15; Start Rush Hour 25; Fully Restock Stores 40; Instant Grow 35; cash 99–1,499; diamonds 199/899; 15% boost for 10 min at 50; "[Gift]" versions of passes.
  - The RT3 wiki notes that "Prices may depend on user's region due to Roblox's regional pricing feature."
  - — [Roblox API, RT3 passes](https://apis.roblox.com/game-passes/v1/universes/7094518649/game-passes?passView=Full&pageSize=100); [RT3 Wiki Shop](https://rt3.fandom.com/wiki/Shop)
- **Retail Tycoon 2** (340M visits, about 2.1k concurrent). Light monetization.
  - Passes: More Land 399; Military Clearance 499; Electric Semi 299; Custom Color Palettes 299; Custom Floors 149; Custom Radio 149.
  - Only 6 cash dev products (5 to 1,000 Robux), last updated Nov 2023.
  - — [Roblox API, Retail Tycoon 2 passes](https://apis.roblox.com/game-passes/v1/universes/2092410051/game-passes?passView=Full&pageSize=100)
- **Theme Park Tycoon 2** (1.62B visits, about 6k concurrent). Creative-tool passes only.
  - Passes: Disable collisions 270; 24 extra expansion plots 374; Enable ride operations 90; Increased height limit 74; Extra colors 90.
  - Dev products: credits and cash packs from 8 to 1,500.
  - — [Roblox API, TPT2 passes](https://apis.roblox.com/game-passes/v1/universes/31970568/game-passes?passView=Full&pageSize=100)
- **Car Dealership Tycoon** (2.54B visits, about 10k concurrent).
  - Passes on sale: VIP 500; 3x Vehicles 299; Special Colors 80. Many legacy passes (2x Money, car classes) are off-sale.
  - 416 dev products on sale, median 499:
    - Individual cars 59–325 and houses 219–299.
    - Limited cars 399–499; daily and weekly offers 199–2,199.
    - "Season Pass + 5 LVLs" 619–885; ONE-SEASON 499.
    - Test Drive tiers 5/8/15/25/40; 2X Cash Boost (15 min) 29.
    - Halloween "Pumpkin Package" ladder 49/99/249/499/999.
    - Cash packs up to "+$25,000,000 Money" at 3,000.
  - — [Roblox API, CDT dev products](https://apis.roblox.com/developer-products/v2/universes/605887098/developerproducts?limit=100)
  - Earlier season pricing (Nov 2024): Season Pass 399, Elite 599, all-seasons 1,599. — [Sportskeeda](https://sportskeeda.com/roblox-news/car-dealership-tycoon-season-14-pass-all-rewards-price)
- **Mansion Tycoon** (662M visits). VIP 400; Double Cash 650; Auto Collect 200; Auto Purchase 600; Starter Pack 80; Extra Speed 10; Jetpack 200; car packs 400–550. It has 184 dev products, many of them 29–99 cosmetic customizations. — [Roblox API, Mansion Tycoon passes](https://apis.roblox.com/game-passes/v1/universes/4518160318/game-passes?passView=Full&pageSize=100)
- **Pet Store Tycoon** (new, 13.6M visits, about 19.8k concurrent). Unbundled worker and automation passes.
  - Worker passes: Cashier #1–#5 at 199–399; Stocker #1–#5 at 199–399; Pet Keeper #1–#5 at 199–749.
  - Other passes: 2x Customer Traffic 299; Auto-Price 199; Inventory Manager 299; Quick Open 29; Unlock All Decor 199; Premium Customization 99.
  - Dev products: Grand Opening Bundle 99; Restock All 49; cash 39–1,199; Secret Ticket x5/x10/x25 at 59/99/199; pet packs 149–599; Server Boost 99; 2x XP (60 min) 59; a "Gift:" version of every pass.
  - — [Roblox API, Pet Store Tycoon passes](https://apis.roblox.com/game-passes/v1/universes/10282097014/game-passes?passView=Full&pageSize=100)

**Live store data for PvP and military tycoons**
- **War Tycoon** (1.13B visits, about 13k concurrent).
  - Passes: 2X CASH 299; Auto Collect 149; F-35 Bundle, Zumwalt and Typhoon Submarine 1,999 each; AbramsX 1,499; Explosive Sniper 1,499; Mi28 799; Double HP Armor 199; 10,000 Shield Health 199; Speedy Oil Extractor 9; Desert Eagle 49.
  - 264 dev products on sale, median 399: limited skins 49–999 (with "[Discount]" twins); crates (Primal, Elite, Halloween) 59–479; RP1–RP50 at 19–399; 20M Cash 3,499; Self Revive 19; Operation Unlock Now 499; Upgrade Skip 199; "[Gift]" versions of passes.
  - — [Roblox API, War Tycoon passes](https://apis.roblox.com/game-passes/v1/universes/1526814825/game-passes?passView=Full&pageSize=100)
- **Military Tycoon** (1.01B visits, about 3.7k concurrent).
  - Passes: Auto Collect 249; A-10 Jet 1,499; Apache 1,249; Super Himars 1,249; 2X Vehicle EXP 1,249; Explosive Sniper 999; Double Blueprints 799; Tank 749; Double HP 449; Super Worker 99; recurring seasonal "War Pass" passes.
  - 548 dev products on sale, median 999: "Complete Operation / Quest / Event" skips 299–1,999; diamonds 199–1,499; limited vehicles 2,999–3,999; Golden Crate x1/x3/x10 at 279/699/2,099 ("-30%"); "Buy … X5" bulk units 2,449–4,799.
  - — [Roblox API, Military Tycoon dev products](https://apis.roblox.com/developer-products/v2/universes/2788648141/developerproducts?limit=100)
- **Army Commander Tycoon** (new, about 10.1k concurrent). 2x Cash 799; VIP Commander 499; Bigger Army 699; vehicles and weapons 349–1,499; Auto Pump 149; cosmetic camos and emblems 99–299. — [Roblox API, Army Commander Tycoon passes](https://apis.roblox.com/game-passes/v1/universes/10768458048/game-passes?passView=Full&pageSize=100)

**Live store data for the "tycoon-adjacent" mega-hits**
- **Steal a Brainrot** (74.0B visits, about 128k concurrent).
  - Only 3 passes on sale: Admin Commands 7,999; VIP 375; 2x Money 299.
  - 112 dev products on sale, median 199:
    - Premium Skull Lucky Block 699, x3 for 2,097, x10 for 6,990.
    - Eclipse Wheel spins: 1x at 99 (a "DISCOUNT" version at 49), 3x at 199, 10x at 499.
    - Dozens of "Skip Timer – [X] Egg" products at 19–199.
    - Reaper Base cosmetic 999, with GIFT versions.
  - — [Roblox API, Steal a Brainrot passes](https://apis.roblox.com/game-passes/v1/universes/7709344486/game-passes?passView=Full&pageSize=100); [Roblox API, Steal a Brainrot dev products](https://apis.roblox.com/developer-products/v2/universes/7709344486/developerproducts?limit=100)
- **Grow a Garden** (36.0B visits, about 26.5k concurrent).
  - Zero passes on sale; the single pass is off-sale. Monetization runs entirely through developer products: 1,400+ on sale, median 249, interquartile range 149–700.
  - Seasonal seeds, pets and gear at 59–2,399.
  - Pack ladders: +1/+3/+10/+50 Exotic Seed Packs at 199/575/1,699/6,999; Premium Eggs +1/+3/+10/+50 at 149/429/1,249/4,999.
  - "Skip Crate Open [n]" priced linearly at 49 per crate (98–490).
  - "Skip Black Cat Submission" 49.
  - — [Roblox API, Grow a Garden dev products](https://apis.roblox.com/developer-products/v2/universes/7436755782/developerproducts?limit=100)
- **Pet Simulator 99** (2.67B visits, about 66k concurrent).
  - Passes: Huge Hunter 3,250; Super Drops 2,400; Double Stars 2,400; Super Shiny Hunter 1,600; Magic Eggs 1,200; Ultra Lucky 800; +15 Eggs 625; Daycare Slots 625; VIP 400; +15 Pets 375; Auto Tap 350; Lucky 275; Auto Farm 175.
  - Dev products: Starter Pack 79, Expert Starter Pack 399, Ultimate Starter Pack 799. Exclusive egg bundles of 2/8/35/170/400 eggs at 240/950/2,950/14,500/32,000.
  - — [Roblox API, PS99 passes](https://apis.roblox.com/game-passes/v1/universes/3317771874/game-passes?passView=Full&pageSize=100)
- My own rough keyword tally of dev product names (on-sale items) shows the mix differs by game:
  - Grow a Garden: about 346 crate/egg/spin-type items, about 320 "gift" items, about 101 skip/instant items, and only about 34 cash packs.
  - Military Tycoon: about 183 skip/complete items.
  - Car Dealership Tycoon: about 110 limited/offer/bundle items.
  - — [Roblox developer products API](https://apis.roblox.com/developer-products/v2/universes/7436755782/developerproducts?limit=100)

**Third-party typical ranges**
- 2x Income at 199–399 and Auto-Collect at 149–299 are typical tycoon passes; one guide suggests 3–5 passes at different price points (50–2,000). These are marketing-oriented guides, so treat the ranges as rough. — [Search summary of obby.fun / generalist guides, via DevForum-related search](https://www.obby.fun/blog/roblox-game-pass-ideas)
- An Average Tycoon prices Auto Collect at 150 and 2x Cash at 300. — [An Average Tycoon Wiki](https://rblxanaveragetycoon.miraheze.org/wiki/Gamepasses_&_Badges)

**Private servers, subscriptions and Roblox Plus**
- Private servers are a monthly Robux subscription; the creator gets a 70% share of the server price. — [Roblox Creator Docs, Roblox Plus](https://create.roblox.com/docs/production/monetization/roblox-plus)
- Roblox Plus gives subscribers **free paid private servers**. Creators earn up to 100 Robux per Plus subscriber who spends 60 or more minutes in a private server they created. — [Roblox Creator Docs, Roblox Plus](https://create.roblox.com/docs/production/monetization/roblox-plus)
- Experience subscriptions:
  - Local-currency tiers: $2.99/$4.99/$7.99/$9.99/$14.99. Robux subscriptions have a minimum of 49 Robux.
  - Up to 50 per game, single-tier only.
  - The creator earns 70% in the first month and 100% in later months for local-currency subscriptions, and 70% every month for Robux subscriptions. — [Roblox Creator Docs, Subscriptions](https://create.roblox.com/docs/production/monetization/subscriptions)
- **Roblox Premium replaced by Roblox Plus.** Plus launched 30 Apr 2026 at a reported ~$4.99/month. Premium closed to new sign-ups. The Premium 10% Robux bonus and badge were discontinued 30 May 2026. Plus has no monthly Robux stipend; optional Plus 500/1000/2000 bundles were planned. — [PCGamesN](https://www.pcgamesn.com/roblox/plus-subscription); [Roblox newsroom](https://about.roblox.com/en-au/newsroom/2026/04/introducing-roblox-plus-subscription); [Business Wire](https://secure.businesswire.com/news/home/20260410099173/en/Roblox-Announces-Roblox-Plus-a-New-Subscription-Plan-Offering-Exclusive-Platform-Benefits)
- **In-game detection of Plus** uses `Player.HasRobloxSubscription` and `MarketplaceService:GetRobloxSubscriptionDetailsAsync` (IsSubscribed, StartTime, IsOriginExperience). Roblox advises verifying status on the server before granting rewards. — [Roblox Creator Docs, Roblox Plus](https://create.roblox.com/docs/production/monetization/roblox-plus)

### Inferences
- Revenue concentration by game type:
  - Classic sandbox and management tycoons (RT2, TPT2, Retail Tycoon 2) monetize lightly through passes that unlock creative capacity: land, plots, floors, item limits, collisions, sandbox mode.
  - Modern hit "tycoon-likes" (Steal a Brainrot, Grow a Garden, PS99) get most of their revenue from consumable dev products: random boxes, eggs and spins, skips, limited items, and gifts.
- The top-earning formats appear to be the following. I did not find per-product revenue data, so this ranking rests on catalog structure and Roblox's "dev products monetize better" statement.
  - Limited-time and seasonal consumables.
  - Paid random boxes in pack ladders.
  - Time skips.
  - Gifting.
  - Among passes, 2x cash, auto-collect and VIP.
- Gift SKUs are now standard: nearly every 2026 game sampled sells a "[Gift]" twin of each pass. Gifting lets non-spenders receive items and expands paying contexts, especially for kids gifting friends.
- "Premium-only perks" should be redesigned as **Roblox Plus** perks, or dropped. Premium cannot be bought by new users after 30 Apr 2026.

### Gaps
- No public per-product revenue split, such as "% of revenue from passes vs dev products," exists for any named tycoon. The rankings above are inferred.
- I couldn't retrieve regional (localized) prices. The API gives default prices only.
- I found no official list of "top tycoon pass prices." All data above is a dated snapshot and will change.

---

## 2. Benchmarks (conversion, ARPDAU, ARPPU, revenue per visit), creator earnings, DevEx, revenue cut, and engagement payouts in 2026

### Takeaway
Roblox publishes **no genre benchmarks**. Its analytics docs only define the metrics. Credible public anchors are platform-level:
- **Q2 2026:** $1,557M bookings, 123M DAU, 27M monthly unique payers. That is roughly $0.14 of gross bookings per DAU per day, platform-wide.
- **Creator payouts:** about $1.7B over the 12 months to June 2026.
- **Concentration:** the median DevEx creator earned about $1,500, while the top 1,000 averaged $1.4M.

The economics chain is as follows:
- The creator gets **70%** of the Robux from pass and dev product sales.
- DevEx pays **$0.0038 per Robux** (since 5 Sep 2025; it was $0.0035).
- A **$0.0054** rate applies to some purchases by age-verified US adults (live June 2026).
- Net, a creator keeps roughly **21–27% of a player's dollar**, or about 38% on qualifying US 18+ spend.
- **Creator Rewards** (since 24 Jul 2025) replaced Premium Payouts. It pays 5 Robux per qualifying "Active Spender" who plays 10 minutes or more in a day, plus 35% of a new or returning user's first $100 of purchases.

Third-party conversion benchmarks (about 0.5–5%) conflict and are low-quality.

### Cited Findings
**Platform financials (dated)**
- **Q2 2026** (quarter ended 30 Jun 2026):
  - Bookings $1,557M (+8% YoY); revenue $1,469M (+36%).
  - DAU 123M (+10%); hours 29B (+5%).
  - Monthly unique payers 27M (+15%).
  - DevEx fees $363M (+15%), equal to 23% of bookings.
- Bookings came in at the low end of guidance because of "lower per-hour monetization, especially among younger U.S. and Canadian users." Headwinds cited:
  - the "Recommended for You" algorithm change, which favors retention over near-term monetization;
  - disabling cross-experience game pass sales;
  - Kids and Select accounts.
- Q3 2026 bookings guidance is $1,576–1,653M (−14% to −18% YoY).
- Age-check penetration was 57% of DAU, with over-18 users at 27% of age-checked DAU.
- — [Roblox Q2 2026 shareholder letter, SEC 8-K Ex. 99.1](https://www.sec.gov/Archives/edgar/data/0001315098/000162828026051059/ex991-robloxq22026earnin.htm); [Investing.com](https://www.investing.com/news/company-news/roblox-q2-2026-slides-bookings-growth-slows-to-8-amid-user-decline-93CH-4826401)
- **Q3 2025 (the boom quarter):**
  - Bookings $1,921.8M (+70%); DAU 151.5M; DevEx $427.9M (+85%).
  - Engagement outside the top 10 experiences grew 58% YoY, and spending outside the top 10 grew 40%.
  - Seven experiences passed 10M DAU at some point, including Grow a Garden, Steal a Brainrot and Plants vs Brainrots.
  - — [Roblox Q3 2025 shareholder letter, SEC](https://www.sec.gov/Archives/edgar/data/1315098/000131509825000326/ex991-q32025shareholderl.htm)
- **Q1 2026:** DevEx fees $423M (+50%). The 10-Q attributes this to the 8.5% DevEx increase, the July 2025 Creator Rewards launch, and "differential Robux pricing." — [Roblox 10-Q Q1 2026](https://www.sec.gov/Archives/edgar/data/0001315098/000162828026028904/rblx-20260331.htm)

**Creator earnings distribution** (12 months to 30 Jun 2026, announced at RDC 2026 in September)
- Total about $1.7B, up about 50% YoY.
- Top 10 creators averaged $65.7M; top 100 averaged $10.8M; top 1,000 averaged $1.4M.
- Median DevEx creator earned about $1,500 across 42,000+ DevEx participants.
- More than $5B has been paid cumulatively since 2013.
- — [Dexerto, 13 Sep 2026](https://www.dexerto.com/roblox/robloxs-top-creators-average-65-7-million-a-year-but-most-make-far-less-3408675/); [IBTimes UK](https://www.ibtimes.co.uk/roblox-top-creators-devex-payouts-2026-1819403)
- Prior year (2024 data): top 10 averaged $33.9M, top 100 about $6M, top 1,000 about $820K. — [Outlook Respawn](https://respawn.outlookindia.com/gaming/gaming-news/robloxs-top-developers-average-339-million-in-annual-earnings); [Roblox 2025 Economic Impact Report](https://about.roblox.com/newsroom/2025/09/roblox-annual-economic-impact-report)

**DevEx (official)**
- Standard rate 0.0038 per earned Robux, so 30,000 Robux = $114. The old rate of 0.0035 applied before 5 Sep 2025 at 10am PT.
- Pre-change balances must be cashed out at the old rate first.
- **Higher rate 0.0054** applies to "certain Earned Robux" from developer products, passes, subscriptions and private servers bought by **US players verified 18+** (facial age estimation or government ID).
- Eligibility: age 13+; 30,000 earned Robux minimum; verified email; DevEx portal account; W-9 or W-8 on file; compliance with Terms of Use and Community Standards.
- DevEx-eligible sources include Creator Rewards, Roblox Plus incentives, in-game ads and paid access.
- Not eligible: purchased Robux, gift-card or transfer Robux, and passes sold in template games with no legitimate visits.
- — [Roblox Creator Docs, Developer Exchange](https://create.roblox.com/docs/production/monetization/developer-exchange)
- The 18+ increase was announced 30 Apr 2026 and took effect 8 Jun 2026, reportedly for games using R15 avatars. It lifts the effective creator share of qualifying spend from 26.6% to 37.8%. — [Net Influencer](https://www.netinfluencer.com/roblox-to-raise-developer-exchange-rate-for-games-aimed-at-18-plus-players-as-adult-cohort-surges/)
- **Conflict on scope:** TubeFilter frames it as limited to "novel games." The Q2 2026 letter lists both "the planned increase for U.S. O18 users has launched" and, separately, "In June, a targeted DevEx rate increase was rolled out to incentivize novel game creation." — [TubeFilter](https://www.tubefilter.com/?p=192104); [Q2 2026 letter](https://www.sec.gov/Archives/edgar/data/0001315098/000162828026051059/ex991-robloxq22026earnin.htm)

**Revenue cut**
- On passes and dev products, the creator receives 70% of the Robux price. Roblox's own example: "a 100 Robux item yields 70 Robux to the creator." — [Roblox Creator Docs, Roblox Plus](https://create.roblox.com/docs/production/monetization/roblox-plus)
- Plus member discounts of 10% (first two months), rising to 20% from month three, are **funded by Roblox**, so the creator earns the same per sale. — [Roblox Creator Docs, Roblox Plus](https://create.roblox.com/docs/production/monetization/roblox-plus)

**Creator Rewards** (replaced Engagement-Based Payouts, i.e. Premium Payouts, and Creator Affiliate on 24 Jul 2025)
- **Daily Engagement Reward:** 5 Robux per qualifying **Active Spender** per experience per day ("may change").
  - The user needs 10 minutes or more in the experience that day, counted across sessions.
  - Only the first three experiences the user plays each day qualify.
  - An Active Spender is someone who spent at least $9.99 in the last 60 days on Robux, Premium or subscriptions.
- **Audience Expansion Reward:** 35% of the first $100 of Robux purchases by a **new user, or one inactive for 60+ days**, during their first two months.
  - The user must arrive via a direct link or a search for the game's name, and play 10 minutes or more.
  - The creator must average 100 DAU.
- Both rewards are held for 60 days.
- Roblox warns that experiences with "unusually long sessions may see reduced earnings" relative to the old Premium-time model.
- — [DevForum, Introducing Creator Rewards](https://devforum.roblox.com/t/introducing-creator-rewards-earn-more-by-growing-the-community/3777628); [Roblox 10-K FY2025](https://www.sec.gov/Archives/edgar/data/1315098/000131509826000024/rblx-20251231.htm)
- Creators have complained about the 60-day hold and transition-period zero payouts. — [DevForum thread](https://devforum.roblox.com/t/shorten-the-hold-period-of-engagement-payouts-or-restore-the-old-premium-payouts-system/3956591)

**Roblox Plus creator incentives** (2026)
- Sign-up bonus of 250 Robux per month for a new subscriber's first three paid months (750 max), only when sign-up happens through `PromptRobloxSubscriptionPurchase` in your game.
- Up to 100 Robux per subscriber for private-server time.
- 10% of Robux transfers (10–500 Robux) that subscribers make through `PromptRobuxTransferAsync` in your game.
- — [Roblox Creator Docs, Roblox Plus](https://create.roblox.com/docs/production/monetization/roblox-plus)

**Metric definitions and benchmarks**
- Roblox defines its metrics as follows: conversion rate is the "percent of daily active users who are also paying users"; ARPPU is average revenue per paying user; ARPDAU is average revenue per DAU. **The docs give no benchmark values.** — [Roblox Creator Docs, Monetization analytics](https://create.roblox.com/docs/production/analytics/monetization)
- Roblox docs reportedly state that "the top 15% of active payers account for roughly 50% of revenue" on average. This came via a search excerpt; I did not see it in my fetch of the page. — [Roblox Creator Docs, Monetization analytics](https://create.roblox.com/docs/production/analytics/monetization)
- Naavik, writing on Blade Ball (2023–24), treated conversion "above 0.5% and an ARPDAU of 10 Robux" as high on Roblox. This came via a search excerpt; the page fetch was blocked. — [Naavik](https://naavik.co/digest/blade-ball-ugc-success/)
- An older Naavik deep dive estimated Brookhaven ARPDAU at about $0.02 using 2021 data. It noted the platform ABPDAU was then $0.164 per day. — [Naavik deep dive](https://naavik.co/deep-dives/roblox-blox-fruits-brookhaven-adopt-me/)
- Third-party calculators claim 1–3% typical conversion, "top titles ~8%," and "simulators 4.0%, obbies 0.8%." These are unsourced and low-quality. — [zehn-studio26 glossary](https://zehn-studio26.com/glossary/conversion-rate/); [calculatorsuniverse](https://calculatorsuniverse.com/games/roblox-revenue-estimator)
- RoWatcher models net-of-everything ARPDAU at $0.003–0.006 USD for conservatively monetized games and $0.015–0.025 for well-monetized ones, assuming DAU of about 4x concurrent players. It uses the outdated $0.0035 DevEx rate and is undated, so it is weak. — [RoWatcher](https://rowatcher.com/news/devex-math-in-2026-what-you-actually-take-home-per-1-000-players)
- Rewarded video ads: Roblox expected them to contribute "up to 3%" of creator earnings initially, with a long-term goal of growing creator revenue 5–10% via ads products (Jul–Aug 2025). — [DevForum, Rewarded Video](https://devforum.roblox.com/t/more-creators-can-now-use-rewarded-video-ads/3838678)

### Inferences
- **Platform gross bookings per DAU-day in Q2 2026** ≈ $1,557M / 123M / 91 days ≈ **$0.139**. At roughly $0.010–0.0125 per Robux, that is about 11–14 Robux of total platform spend per DAU per day. This includes avatar and marketplace spend and is spread across all the experiences a user plays. A single tycoon reaching about 10 Robux ARPDAU (Naavik's "high" bar) would therefore capture a large share of its players' daily wallet.
- **Creator take-home per player dollar:**
  - Robux cost about $0.0125 each in the $4.99/400 pack, and about $0.010 each in larger or web packs.
  - Creator take-home = 0.70 × $0.0038 ÷ price per Robux ≈ **21% (small packs) to 27% (large packs)** of consumer spend.
  - On qualifying US 18+ purchases: 0.70 × 0.0054 ÷ 0.010 ≈ **38%**, which matches Net Influencer's 37.8%.
- **Back-of-envelope for a tycoon at 10,000 DAU:**
  - 10 Robux ARPDAU (gross Robux spent) → 100,000 Robux/day → creator receives 70,000 Robux → about $266/day, or about $8k/month, at $0.0038.
  - At 3 Robux ARPDAU, about $2.4k/month.
  - Creator Rewards come on top: e.g. if 15% of DAU are Active Spenders who play 10+ minutes, that is 1,500 × 5 = 7,500 Robux/day, about $28.5/day. These are hypothetical inputs, not benchmarks.
- **Monetization strategy now interacts with discovery.** Roblox's recommender change favors retention over near-term monetization, and Creator Rewards pays per daily 10-minute active-spender session rather than total minutes. Aggressive monetization that hurts D1/D7 retention will likely cost both reach and Creator Rewards. AFK-heavy tycoon designs no longer earn extra from long passive sessions.
- **Revenue concentration is extreme:** a ~$1,500 median against a $1.4M top-1,000 average. A new tycoon should plan for the median case and treat monetization as an amplifier of retention, not a substitute for it.

### Gaps
- There are no official or credible 2025–2026 genre benchmarks (tycoon or simulator) for conversion, ARPDAU, ARPPU or revenue per visit or hour. Roblox doesn't publish them, and the third-party numbers are unsourced. Creator Hub may show peer benchmarks to logged-in creators; I couldn't verify this.
- Roblox did not disclose average monthly bookings per payer or ABPDAU in the Q2 2026 letter.
- The exact qualifying rules for the 0.0054 rate are unclear: R15 requirement, "novel games" scope, and whether it is one program or two.
- Daily Engagement Reward is "may change." I found no confirmation of the current per-user amount as of Oct 2026.

---

## 3. What causes backlash or hurts retention, and how do the best tycoons balance free vs paid?

### Takeaway
The clearest friction points are:
- income multipliers and premium weapons or vehicles in **PvP** tycoons (pay-to-win);
- paywalled progression or "buy to complete";
- timers and appointment mechanics;
- "best items only for cash";
- pressure tactics on kids, which UK regulators specifically call out.

Classic creative tycoons (TPT2, Retail Tycoon 2) succeed by selling **capacity and creative tools** rather than power, with very small dev product catalogs. Hits like Steal a Brainrot and Military Tycoon draw explicit pay-to-win criticism but still earn heavily. Backlash and revenue are not mutually exclusive, but they raise reputational and regulatory risk.

### Cited Findings
- **DevForum tycoon thread (Jul 2024).** The planned 2x Cash, VIP 1.5x and cash packs (29–1,499) drew the top reply: don't include any gamepasses that directly help income, "ESPECIALLY 2x cash," because it "will easily drive away potential players." The reply suggests instead a premium currency that can also be **earned without paying**, for example via sky-dropping crates. — [DevForum, Monetization Ideas for my Tycoon Game](https://devforum.roblox.com/t/monetization-ideas-for-my-tycoon-game/3048249)
- Roblox's own monetization guide reportedly warns that users "are likely to downvote your game if they do not approve of your strategies." It says timers and appointment mechanics "are unpopular with Roblox users who take issue with their fun coming to a premature end." It also distinguishes "tourists," who buy items with immediate visible effects, from "locals," who stick with a few games. These come from a search excerpt of the Roblox docs, not verified in a full fetch. — [Roblox Creator Docs, Monetization](https://create.roblox.com/docs/production/monetization)
- **Steal a Brainrot criticism.** Polygon criticized that "the best items are only available for cash" and that server-admin abilities can be bought (the Admin Commands pass is 7,999 Robux per the API). Viral clips of children crying over stolen Brainrots drew tens of millions of views. — [Wikipedia, Steal a Brainrot](https://en.wikipedia.org/wiki/Steal_a_Brainrot); [Roblox API, Steal a Brainrot passes](https://apis.roblox.com/game-passes/v1/universes/7709344486/game-passes?passView=Full&pageSize=100)
- **Some tycoons market their restraint.** One tycoon listing advertises "no gamepass spam" and says you "can't buy money in the game." — [Search summary of Roblox game page](https://www.roblox.com/games/6676515062)
- Guides frame Auto Collect as convenience: it "removes the need to walk to the cash button." A War Tycoon guide rates 2x Cash (299) only 6/10. — [Sportskeeda, War Tycoon gamepasses](https://www.sportskeeda.com/roblox-news/5-best-gamepasses-use-roblox-war-tycoon); [War Tycoon wiki](https://war-tycoon-roblox.fandom.com/wiki/Gamepasses)
- **UK ICO Children's Code (AADC) guidance:**
  - Children "should not be manipulated into quick or rash purchases through countdown or expiring offers."
  - In-app purchases "should not appear as one-time-only offers or as necessary purchases to progress."
  - Loot boxes should be kept to a minimum, with odds disclosed.
  - — [ICO, Nudge techniques toolkit](https://ico.org.uk/for-organisations/advice-and-services/audits/data-protection-audit-framework/toolkits/age-appropriate-design/nudge-techniques/)
- **Managed Pricing transparency concern.** A developer reported a price changing from 100 to 150 Robux during a test. Roblox doesn't tell players when a price test is running, and players can't opt into standard prices. — [DevForum, Managed Pricing](https://devforum.roblox.com/t/managed-pricing-one-system-for-better-pricing-and-earnings-growth/4684738)
- **Cross-experience pass sales were disabled around 29–30 May 2026**, prompting backlash from donation games (PLS DONATE's creator said the change would "kill the game completely") and a change.org petition. — [Patreon post](https://www.patreon.com/posts/157562410); [change.org](https://www.change.org/p/bring-back-cross-game-sales-of-gamepasses-on-roblox-e1da39b1-809d-42a3-a03a-997af08075d6)
- **Lighter-touch evidence from the store data:**
  - TPT2 (1.62B visits) sells only 5 passes, at 74–374, plus currency packs.
  - Retail Tycoon 2 has had 6 cash dev products unchanged since 2023.
  - RT2's biggest unlocks are capacity rather than PvP power: plots, floors, drive-thru.
  - — [Roblox API, TPT2 passes](https://apis.roblox.com/game-passes/v1/universes/31970568/game-passes?passView=Full&pageSize=100); [Roblox API, RT2 dev products](https://apis.roblox.com/developer-products/v2/universes/1214576306/developerproducts?limit=100)

### Inferences
- **Where backlash risk peaks:**
  - **PvP or raid tycoons** (War, Military, Army Commander), where premium vehicles and weapons at 999–1,999 and "Double HP" passes give combat advantage. These players are directly harmed by others' spending.
  - **Single-player or creative tycoons**, where 2x cash mostly shortens the player's own grind. These tolerate it better, though community advice still discourages it.
- **Safer premium categories:** convenience (auto-collect), capacity (land, floors, slots), creative tools (sandbox, precision build, collisions), cosmetics, and gifting. Sell these when they don't trivialize the core loop.
- **Balancing practices observed:**
  - an earnable path to any premium currency;
  - small timed boosts (10 min to 8 h) instead of only permanent multipliers;
  - granular "Skip" products priced low (15–49) for impatience rather than gating;
  - starter packs at 79–250;
  - no hard progression walls.
- **Practices to avoid with a young audience,** given the ICO guidance and FTC precedent:
  - expiring countdown offers;
  - "one-time-only" framing;
  - "complete the whole quest/tycoon for 1,999";
  - prompts on spawn or in the middle of an action.
- An "auto-buy/auto-purchase" pass (e.g. Mansion Tycoon's at 600) plus large cash packs can amount to "buy to skip the tycoon." It boosts short-term revenue but likely shortens lifetime. This is an inference; I have no data.

### Gaps
- Reddit sentiment threads did not surface in searches, so I found no systematic player-sentiment data for tycoons.
- I found no A/B data or postmortem quantifying the retention cost of 2x cash or pay-to-win passes in Roblox tycoons.

---

## 4. Roblox policy constraints 2025–2026 and external regulation

### Takeaway
A tycoon that sells any chance-based product must:
- **disclose exact odds**, including for luck boosts, pity systems and indirect purchases;
- **gate it per player** via `PolicyService` (`ArePaidRandomItemsRestricted`, `IsPaidItemTradingAllowed`). Brazil bars under-18s entirely.

The big 2026 platform shifts are:
- **Roblox Kids (5–8) and Select (9–15)** accounts, live globally 16 Jun 2026. Reaching them requires creator ID verification, 2FA, a refundable fee or a Plus subscription, an engagement evaluation, and a Minimal or Mild label for Kids.
- **Roblox Plus** replaced Premium.
- **Cross-experience pass and dev product sales were disabled.**
- **Managed Pricing**: regional pricing plus automated price tests.

Other rules:
- Rewarded video must be opt-in, non-random, delivered as a dev product, and shown only to 13+ viewers.
- External pressure is rising: the FTC Genshin settlement, EU CPC virtual-currency principles and the October 2026 enforcement action, a Digital Fairness Act draft expected November 2026, and UK ICO nudge guidance.

### Cited Findings
**Paid random items (official)**
- Covered items:
  - capsules (eggs, chests, wheels);
  - enhancement items (random-duration potions, uncertain upgrades);
  - combination items;
  - probability modifiers (luck boosts, pity systems, enhanced drops, rate-ups);
  - **indirect purchases** (keys, re-roll tokens, spin tickets), plus anything bought with Robux-purchased currency.
- Disclosure rules:
  - Show "all possible outcomes and the actual numerical odds" as percentages summing to 100%, before spend.
  - A bare (i) icon without a descriptive word is not sufficient.
  - Odds must update for single-obtain outcomes.
  - Modifiers must be explained numerically, and their effects shown dynamically.
- Free, earned random rewards are exempt.
- For players where `ArePaidRandomItemsRestricted` is true, the creator must use one of these treatments:
  - offer a free earnable path;
  - use a predetermined disclosed order;
  - sell specific outcomes at expected value;
  - hide or remove the item;
  - block with an error;
  - remove the player from areas with paid random items.
- Trading of paid items is disallowed where `IsPaidItemTradingAllowed` is false.
- — [Roblox Creator Docs, Paid random items](https://create.roblox.com/docs/production/monetization/paid-random-items)
- Roblox's guidance indicates that if a seed bought with Robux is later traded for or grows into a random item, the odds must be disclosed before planting. This is directly relevant to Grow a Garden–style tycoons. — [Search summary of Roblox paid random items docs](https://create.roblox.com/docs/en-us/production/monetization/paid-random-items)
- **Brazil (Digital ECA).** Users under 18 are ineligible for paid random item mechanics without an 18+ age check. Games that don't use the PolicyService API "are no longer playable for users under the age of 18 in Brazil." This comes from a search excerpt of the Roblox help article; my direct fetch was blocked with a 403. — [Roblox Help, Brazil Digital ECA Updates](https://en.help.roblox.com/hc/cs/articles/48706630819476-Brazil-Digital-ECA-Updates)

**Content maturity and gambling**
- Games "cannot contain playable gambling content, including simulated gambling." Unplayable depictions are Moderate or Restricted.
- Paid random items and paid-item trading must be disclosed in the questionnaire.
- Games without maturity info are automatically restricted for all players.
- Label access:
  - Kids accounts see Minimal or Mild.
  - Select accounts see up to Moderate.
  - "Content May Vary" is shown to age-checked 16+ only.
  - Restricted is shown to verified 18+ only.
- — [Roblox Creator Docs, Content maturity](https://create.roblox.com/docs/production/promotion/content-maturity)

**Roblox Kids and Select** (announced 13 Apr 2026; rollout from 19 May in NZ, NL, AU and ID; global 16 Jun 2026)
- Creator requirements: age-checked, ID-verified, 2FA, plus either a refundable 1,000-Robux per-game fee or two consecutive months of Plus/Premium.
- Games start in a 16+ trial and must hit a "highly engaged player" threshold:
  - The docs say 250 unique plays by age-checked, highly engaged users within 60 days.
  - The June forum post says 500 HEPs to enter and 25 to maintain (down from 100 on 16 Jul).
  - These figures conflict.
- Expedited review fee: the docs say 50,000 Robux; the June 2026 DevForum says 100,000 Robux. Also conflicting.
- Ineligible games still reach 16+ users.
- — [Roblox Creator Docs, Kids and Select](https://create.roblox.com/docs/production/publishing/kids-and-select); [DevForum, Kids and Select global launch](https://devforum.roblox.com/t/roblox-kids-and-select-global-launch-upcoming-updates-to-eligibility-ads-manager-and-expedited-review/4685717); [Roblox newsroom](https://about.roblox.com/en-au/newsroom/2026/04/introducing-roblox-kids-and-select-accounts)
- The Kids and Select announcements mention parents managing "screen-time and spending limits" but give no detail on purchase rules for those accounts. — [Roblox newsroom](https://about.roblox.com/en-au/newsroom/2026/04/introducing-roblox-kids-and-select-accounts)
- Third-party guides describe a parental "Monthly Spend Restriction" setting. — [RoWatcher parental controls guide](https://rowatcher.com/news/roblox-parental-controls-2026-the-complete-setup-guide); [ParentMap](https://www.parentmap.com/article/parental-controls-roblox)

**Cross-experience sales and the Transfers API**
- Selling passes and dev products from other experiences was disabled around 29–30 May 2026. The DevForum thread is "Disabling Cross-Game Sales of Passes and Dev Products and Introducing the Transfers API."
- Robux transfers can only be initiated by Plus subscribers, at 10–500 Robux each. — [skills.sh summary](https://www.skills.sh/nonlooped/roblox-suite/roblox-monetization-gamepasses); [Roblox Creator Docs, Roblox Plus](https://create.roblox.com/docs/production/monetization/roblox-plus)
- Roblox cited this change as a Q2 2026 bookings headwind. — [Q2 2026 letter](https://www.sec.gov/Archives/edgar/data/0001315098/000162828026051059/ex991-robloxq22026earnin.htm)
- Since March 2026, passes are hidden for unpublished or unrated experiences. — [creation.dev](https://www.creation.dev/learn/how-to-fix-game-pass-visibility-unpublished-games-roblox)

**Rewarded video ads**
- Publisher requirements: 13+, good standing, 2FA plus ID verification, a public game with no free-form user creation, 2,000+ unique visitors per month, and an approved Maturity and Compliance Questionnaire.
- Reward rules:
  - Rewards must be **developer products** "normally purchasable with Robux," and **cannot be randomized**.
  - The recommended reward value is about 3–10 Robux.
- Prohibited: forcing an ad as a progress gate, screen takeover, misleading rewards, and failing to disclose the reward beforehand.
- Pay is EPM × impressions.
- — [Roblox Creator Docs, Rewarded video ads](https://create.roblox.com/docs/production/promotion/rewarded-video-ads)
- "Only users aged 13 and older will be eligible to see Rewarded Video ads." Initial eligibility was 100K+ DAU with Minimal or Mild content (Jul–Aug 2025), and was later broadened. — [DevForum, Rewarded Video](https://devforum.roblox.com/t/more-creators-can-now-use-rewarded-video-ads/3838678)
- A Studio drag-and-drop plugin for rewarded video is expected in Q4 2026. — [MediaPost / search summary](https://www.mediapost.com/publications/article/417959/)

**Immersive ads**
- Publisher eligibility matches rewarded video (13+, ID plus 2FA, 2,000 monthly unique visitors, approved questionnaire).
- Creators must hide ads where `PolicyService.AreAdsAllowed` is false.
- Formats and pay: video billboards paid per 15-second view or per impression; image billboards per impression; portals per teleport.
- Payout lands on the 25th of the following month.
- — [Roblox Creator Docs, Immersive ads](https://create.roblox.com/docs/production/monetization/immersive-ads)
- Sponsored and brand-integration labeling became mandatory 4 May 2026. Roblox plans to take a share of paid brand-integration revenue from January 2027. — [Outlook Respawn](https://respawn.outlookindia.com/amp/story/gaming/gaming-news/roblox-to-take-cut-of-creator-brand-deals-from-2027); [Campaign](https://campaignlive.com/article/roblox-violates-creator-ad-guidelines-watchdog-finds/1822703)

**Managed, regional and optimized pricing**
- Regional Pricing launched 22 Apr 2025. Example: an item at 1,000 Robux in the US shows as 700 in Brazil and 500 in India. In tests, the share of users spending rose 17% in Mexico, 26% in Brazil and 52% in the Philippines (median +26%). — [Roblox newsroom, Regional pricing](https://about.roblox.com/newsroom/2025/04/roblox-launches-regional-pricing-for-in-experience-items)
- **Managed Pricing** (15 Jun 2026) combines regional pricing and price optimization:
  - Regional prices are bounded between 30% and 100% of default.
  - New games and items are enrolled by default (the FAQ conflicts on this).
  - Tests run at least every 90 days and last about 3 weeks.
  - Hard-coded prices must be removed first.
  - Subscriptions and private servers are regionalized automatically.
  - Results: regional pricing gave a 4–10% increase in overall Robux spend, 1–6% more players and playtime, and **43–52% more pass purchases in discounted regions** (top 2,500 games). Price optimization gave about +4% earnings on average; Slap Battles saw +15% after moving to more competitive prices.
  - — [DevForum, Managed Pricing](https://devforum.roblox.com/t/managed-pricing-one-system-for-better-pricing-and-earnings-growth/4684738); [Roblox Creator Docs, Managed pricing](https://create.roblox.com/docs/production/monetization/managed-pricing)
- Price optimization eligibility was expanded to experiences with at least 60,000 transactions in the past month. — [Roblox Creator Docs, Price optimization](https://create.roblox.com/docs/production/monetization/price-optimization)

**Subscriptions and refunds**
- "Subscriptions purchased with Robux are not eligible for refunds."
- Refunds of local-currency subscriptions within the 30-day hold cancel the payout; refunds after the hold are deducted from the creator's balance.
- Creators can't revoke benefits behind the scenes or require extra tasks to unlock paid benefits (battle passes excepted). Price increases need 30 days' notice. Robux-subscription prices can change at most once per 60 days.
- Local-currency subscriptions are unavailable in AR, CN, CO, IN, ID, JP, RU, TW, TR, AE, UA and VN.
- — [Roblox Creator Docs, Subscriptions](https://create.roblox.com/docs/production/monetization/subscriptions)

**Commerce**
- Commerce APIs (Shopify) launched May 2025. They let eligible creators sell physical goods in-experience, starting with **US users 13+**, and can pair physical purchases with digital items. — [Roblox newsroom](https://about.roblox.com/newsroom/2025/05/roblox-launches-shopify-integration-amp-licensing-program); [TechCrunch](https://techcrunch.com/2025/05/15/roblox-now-lets-creators-sell-physical-products-within-their-experiences)

**External regulation**
- **US FTC vs HoYoverse (Genshin Impact), 2025.** A $20M settlement over loot boxes marketed to kids with obscured costs and misleading odds.
  - Terms: no loot-box sales to under-16s without parental consent; a direct real-money option for loot boxes; disclosure of odds and exchange rates.
  - Sources differ on whether the order is finalized.
  - — [PocketGamer.biz](https://www.pocketgamer.biz/hoyoverse-agrees-to-20-million-settlement-with-ftc-over-loot-boxes); [esportslegal.news](https://esportslegal.news/2025/11/25/ftc-vs-genshin-impact-20-million/)
- **EU CPC Network "Key Principles on in-game virtual currencies"** (March 2025):
  1. clear prices, including the real-money cost;
  2. no obscuring costs via multiple currencies or exchanges;
  3. no unwanted currency purchases required to progress;
  4. clear pre-purchase information;
  5. cancellation rights;
  6. fair terms;
  7. protection of children.
  - On 15 Oct 2026 the CPC launched coordinated action involving **nine unnamed** game companies, focused on loot boxes available to children, dark patterns and "direct exhortations to children." I can't confirm whether Roblox is among them.
  - The Commission reportedly intends to publish a draft **Digital Fairness Act** in **November 2026**.
  - — [Lewis Silkin, 15 Oct 2026](https://www.lewissilkin.com/insights/2026/10/15/eu-consumer-protection-network-launches-action-involving-nine-video-games-compani-102o5do)
- Possible DFA measures under discussion:
  - real-money equivalents shown alongside virtual prices;
  - limits on pay-to-win and loot boxes;
  - possible bans or parental consent for minors buying loot boxes.
  - — [Freshfields](https://technologyquotient.freshfields.com/post/102ltio/the-eus-proposed-digital-fairness-act-a-game-developers-guide-to-potential-imp); [euperspectives](https://euperspectives.eu/2025/11/developers-push-back-the-digital-fairness-act/)
- **UK ICO Children's Code:** no countdown or expiring offers that push children into rash purchases, no "one-time-only" framing, no "necessary to progress" framing, minimal loot boxes with odds shown. — [ICO, Nudge techniques](https://ico.org.uk/for-organisations/advice-and-services/audits/data-protection-audit-framework/toolkits/age-appropriate-design/nudge-techniques/)
- **CARU** (US) found that Roblox's creator affiliate program didn't clearly disclose paid promotion to child audiences, who were largely aged 9–12. — [Campaign](https://campaignlive.com/article/roblox-violates-creator-ad-guidelines-watchdog-finds/1822703)

### Inferences
- **Compliance checklist for a tycoon:**
  - Wrap every egg, crate, spin, lucky block or luck boost purchase, including ones bought with Robux-bought currency, in a `PolicyService` check. Give restricted players a deterministic or expected-value alternative.
  - Show odds in a labeled panel before purchase.
  - Never sell random rewards via rewarded video.
  - Avoid simulated gambling such as slot machines, even with soft currency bought with Robux.
- **Audience reach:** a tycoon aimed at under-13s needs a **Minimal or Mild** label, a passed Kids/Select evaluation, and creator verification. War or Military tycoons with heavier violence may land at Moderate, which is Select-only, not Kids.
- **Pricing mechanics:** keep all prices in the product configuration, not hard-coded, so Managed Pricing works. Expect lower realized prices but higher pass volume in emerging markets.
- **Direction of travel:** regulators in the EU, UK and US are converging on real-money price clarity, no exhortation of kids, and age-gated loot boxes. A tycoon that avoids paid randomness entirely, or offers deterministic alternatives everywhere, is the most future-proof design.

### Gaps
- I couldn't access the official text of the Brazil help article (403) or the full DevForum thread on cross-game sales, so those rely on search excerpts and secondary sources.
- I found no official document on purchase or spending rules specific to Roblox Kids accounts, for example whether under-9s can buy passes without parental approval.
- I didn't find official Roblox in-experience refund rules for passes and dev products. Search results were spam sites. Only subscription refund rules are documented.
- I found no published Roblox "monetization guidelines" that ban specific manipulative patterns. Roblox's 2026 rules focus on odds, ads, labeling and age gating.
- The current status of the Digital Fairness Act and whether Roblox is in the CPC action are unknown.

---

## 5. Case studies: how top games monetize, with public revenue figures

### Takeaway
Credible public revenue figures are scarce. Roblox doesn't break out per-game revenue. The best available figures:
- Grow a Garden: about **$12M in May 2025** (Calcalist).
- Steal a Brainrot: an unverified estimate of about **$11M/month** (Creator Exchange, Aug 2025).
- Both were among Q3 2025's seven experiences that passed 10M DAU.

Monetization archetypes differ:
- **Grow a Garden:** no passes, 1,400+ consumable dev products.
- **Steal a Brainrot:** 3 passes plus lucky blocks, spins and skips.
- **Military/War Tycoon:** many PvP power items, "complete now" skips and limited vehicles.
- **Car Dealership Tycoon:** limited cars, season passes and weekly/daily offers.
- **Classic RT2/RT3/TPT2/Retail Tycoon 2:** capacity, creative passes and cash packs.

### Cited Findings
- **Grow a Garden:**
  - Generated about $12M in May 2025 from virtual items such as seeds, upgrades and rare animals; the original creator reportedly still owns about half. — [Calcalist](https://www.calcalistech.com/ctechnews/article/dj4lxef8r)
  - Nearly 22M concurrent players, a world record at the time. — [Roblox Q3 2025 letter](https://www.sec.gov/Archives/edgar/data/1315098/000131509825000326/ex991-q32025shareholderl.htm); [Game Developer](https://www.gamedeveloper.com/business/roblox-s-grow-a-garden-had-nearly-22-million-concurrent-users-in-july)
  - A claim that JP Morgan estimated $150M grossed within 3 months is unverified. — [search summary of social posts](https://x.com/Crypticinvest1/status/2101841044383891790)
  - Modeled estimates such as profitable.app's $286.8M lifetime are formula outputs, not data. — [profitable.app](https://profitable.app/roblox/games/grow-a-garden)
  - Store structure (2026-10-18): zero passes on sale; 1,409 dev products on sale, median 249; seasonal Halloween seeds, eggs and pets; pack ladders; per-crate skip pricing. — [Roblox API, Grow a Garden dev products](https://apis.roblox.com/developer-products/v2/universes/7436755782/developerproducts?limit=100)
- **Steal a Brainrot:**
  - Released 16 May 2025; peak 25.4M concurrent (Oct 2025).
  - Monetization: buying Brainrots that generate passive income, rebirths, items for Robux, and "admin abuse" events.
  - — [Wikipedia](https://en.wikipedia.org/wiki/Steal_a_Brainrot)
  - Estimated monthly revenue of $11M (+117%) in a Creator Exchange post, date not confirmed. — [Creator Exchange on X](https://x.com/CreatorExc/status/1952868682096574520)
  - KreekCraft, a promoter or partner, said he made "over $2,000,000" from the game (Jan 2026). — [KreekCraft on X](https://x.com/KreekCraft/status/2013725910688489936)
  - Store structure (2026-10-18): VIP 375, 2x Money 299, Admin Commands 7,999; premium lucky blocks 699 to 6,990; spin bundles; skip-timer products 19–199. — [Roblox API, Steal a Brainrot passes](https://apis.roblox.com/game-passes/v1/universes/7709344486/game-passes?passView=Full&pageSize=100)
- **Car Dealership Tycoon** (Foxzie; 2.54B visits):
  - Season passes (Nov 2024: 399, Elite 599, all-seasons 1,599). — [Sportskeeda](https://sportskeeda.com/roblox-news/car-dealership-tycoon-season-14-pass-all-rewards-price)
  - 2026 dev products: limited cars, daily and weekly offers, test-drive micro-purchases at 5–40, tiered event packages, cash packs. — [Roblox API, CDT dev products](https://apis.roblox.com/developer-products/v2/universes/605887098/developerproducts?limit=100)
- **Military Tycoon / War Tycoon:**
  - Seasonal War Passes plus many premium vehicles and weapons (999–1,999 passes; limited vehicles up to 3,999).
  - "Complete Operation/Quest/Event" products at 299–1,999.
  - Crates with "-30%" bundle pricing.
  - — [Roblox API, Military Tycoon](https://apis.roblox.com/developer-products/v2/universes/2788648141/developerproducts?limit=100); [Roblox API, War Tycoon](https://apis.roblox.com/game-passes/v1/universes/1526814825/game-passes?passView=Full&pageSize=100)
- **Restaurant Tycoon 2 / 3, Theme Park Tycoon 2, Retail Tycoon 2:** see Section 1. These are capacity and creative passes plus cash packs. RT3 adds starter packs, objective skips and rush-hour triggers. — [Roblox API, RT3](https://apis.roblox.com/game-passes/v1/universes/7094518649/game-passes?passView=Full&pageSize=100)
- **Pet Simulator 99** (BIG Games):
  - Passes from 175 to 3,250.
  - Tiered starter packs at 79/399/799.
  - Very large egg bundles (up to 32,000 Robux for 400 eggs). These are paid random items subject to the disclosure and PolicyService rules.
  - — [Roblox API, PS99 passes](https://apis.roblox.com/game-passes/v1/universes/3317771874/game-passes?passView=Full&pageSize=100)
- **Q3 2025 breadth:** seven experiences passed 10M DAU at some point in the quarter: Grow a Garden, Steal a Brainrot, Brookhaven, 99 Nights in the Forest, Plants vs Brainrots, Ink Game and Blox Fruits. — [Roblox Q3 2025 earnings call summary](https://www.sec.gov/Archives/edgar/data/1315098/000131509825000326/ex991-q32025shareholderl.htm)
- **Ads benchmark anecdote:** Brookhaven reportedly earns about $65,000/month from ads, per one developer. Unverified. — [search summary of ppc.land / mediapost](https://ppc.land/roblox-expands-google-advertising-partnership-with-rewarded-video-launch/)

### Inferences
- The two mega-hits monetize mainly via **consumables tied to live events** (seasonal seeds, eggs, lucky blocks, admin-abuse windows) plus **gifting**. Weekly content cadence is what keeps dev product spending flowing.
- Classic tycoons with older, smaller catalogs (Retail Tycoon 2, TPT2) likely earn far less per DAU but have kept large lifetime audiences. Low monetization pressure fits long-lived creative tycoons.

### Gaps
- There are no credible public revenue figures for Restaurant Tycoon 2/3, Retail Tycoon 2, Theme Park Tycoon 2, Car Dealership Tycoon, War Tycoon, Military Tycoon or PS99 in 2025–2026.
- The Steal a Brainrot monthly estimate is unverified, and its exact date is unclear.

---

## 6. Pricing psychology for a young audience

### Takeaway
Observed best practice in 2026 top games:
- **cheap first-purchase or starter offers** (49–250 Robux) to convert;
- **tiered ladders** (1/3/10/50) with visible per-unit discounts to anchor value;
- **gift SKUs**;
- **micro-skips** (5–49) for impulse moments;
- a small number of **high anchors** (1,499–7,999) that make mid-tier items look reasonable.

Roblox's own data favors **lower or regionalized prices to widen the payer base**: median +26% payers in regional pricing tests, +43–52% pass purchases in discounted regions, and price optimization often recommending lower prices.

For kids, the ethical line is set by the ICO, the EU CPC and the FTC:
- no countdown pressure;
- no "one-time-only" framing;
- clear real-money value;
- no paywalls on progression.

### Cited Findings
- **Robux purchase prices.** Standard US bundles: 400 for $4.99, 800 for $9.99, 1,700 for $19.99, 4,500 for $49.99, 10,000 for $99.99, i.e. about 80–100 Robux per dollar. This source is undated and still mentions the Premium bonus, which was discontinued in May 2026. Other sources report higher web or gift-card amounts (e.g. 500 for $4.99 on web) and "up to 25% more" on web versus mobile, so prices vary by platform. — [RoWatcher Robux prices](https://rowatcher.com/news/robux-prices-bundles-2026-guide); [creation.dev](https://www.creation.dev/learn/how-much-does-robux-cost); [timesaver.gg](https://timesaver.gg/blog/robux-to-usd)
- **Differential Robux pricing** (by platform) is cited by Roblox as a contributor to DevEx growth. — [Roblox 10-Q Q1 2026](https://www.sec.gov/Archives/edgar/data/0001315098/000162828026028904/rblx-20260331.htm)
- **Ladders and anchors in live stores (2026-10-18):**
  - Grow a Garden: +1/+3/+10/+50 at 199/575/1,699/6,999, so per-unit cost falls from 199 to 140.
  - Steal a Brainrot: 1x/3x/10x spin at 99/199/499, and a 1x "DISCOUNT" at 49.
  - PS99: Starter Packs at 79 / 399 / 799.
  - RT2: Starter Pack 250 alongside a "Starter Pack (Discounted)" at 175.
  - Car Dealership Tycoon: event packs at 49/99/249/499/999.
  - Military Tycoon: Golden Crate x1/x3/x10 labeled "-30%."
  - — [Roblox API, Grow a Garden](https://apis.roblox.com/developer-products/v2/universes/7436755782/developerproducts?limit=100); [Roblox API, Steal a Brainrot](https://apis.roblox.com/developer-products/v2/universes/7709344486/developerproducts?limit=100); [Roblox API, PS99](https://apis.roblox.com/game-passes/v1/universes/3317771874/game-passes?passView=Full&pageSize=100); [Roblox API, RT2](https://apis.roblox.com/developer-products/v2/universes/1214576306/developerproducts?limit=100)
- **Roblox recommendations:** offer welcome or first-time-buyer discounts, a wide range of price points, repeatable consumables and seasonal items. — [Roblox Creator Docs, Monetization analytics](https://create.roblox.com/docs/production/analytics/monetization)
- **Price tests often lower prices.** Roblox says price tests "recommended that creators reduce prices on some in-experience items… driving higher earnings overall." Slap Battles gained over 15% after lowering prices. — [Roblox newsroom](https://about.roblox.com/newsroom/2025/04/roblox-launches-regional-pricing-for-in-experience-items); [DevForum, Managed Pricing](https://devforum.roblox.com/t/managed-pricing-one-system-for-better-pricing-and-earnings-growth/4684738)
- **DevForum folk wisdom:** 99 Robux is a common price point, and it's worth having some passes under 100. Price should scale with gameplay impact, e.g. "+50–100 Robux per multiplication." One developer found they earned less from very low-priced passes than from roughly 100-Robux passes. All of this is anecdotal. — [DevForum, high vs low pricing](https://devforum.roblox.com/t/is-it-best-to-put-your-prices-for-game-passes-developer-products-high-or-low/594287); [DevForum, price optimization guide](https://devforum.roblox.com/t/the-economic-guide-to-gamepass-price-optimization-maximize-profit/717775)
- **Young-audience constraints:**
  - The ICO says to avoid countdowns and expiring offers and "one-time-only" framing for children. — [ICO](https://ico.org.uk/for-organisations/advice-and-services/audits/data-protection-audit-framework/toolkits/age-appropriate-design/nudge-techniques/)
  - The EU CPC says to show real-money cost and not obscure prices with multiple currencies. — [Lewis Silkin](https://www.lewissilkin.com/insights/2026/10/15/eu-consumer-protection-network-launches-action-involving-nine-video-games-compani-102o5do)
  - The FTC's Genshin case involved a "confusing virtual currency system" judged unfair to kids and teens. — [PocketGamer.biz](https://www.pocketgamer.biz/hoyoverse-agrees-to-20-million-settlement-with-ftc-over-loot-boxes)
- **Monetization softness among young users.** Q2 2026 saw "lower per-hour monetization, especially among younger U.S. and Canadian users." — [Q2 2026 letter](https://www.sec.gov/Archives/edgar/data/0001315098/000162828026051059/ex991-robloxq22026earnin.htm)
- **Adult spend premium.** US 18+ verified spend now earns 42% more DevEx. — [Net Influencer](https://www.netinfluencer.com/roblox-to-raise-developer-exchange-rate-for-games-aimed-at-18-plus-players-as-adult-cohort-surges/)

### Inferences
- **"Robux value" perception for kids** maps to purchasable pack sizes. Kids often hold 400 or 800 Robux from a $4.99 or $9.99 purchase or a gift card, so items at 79–99, 199, 299, 399 and 799 fit those balances. A 299 pass is about $3.74 at the $4.99/400 rate. Ending prices just under pack sizes (399, 799) lets a single pack buy one item. This is inferred from the price clustering observed and the pack sizes; I found no direct study.
- **A defensible tycoon price architecture** (synthesized from the store data, not a measured optimum):
  - Starter pack 79–149, one-time and not time-limited for kids.
  - Auto-collect 149–249.
  - 2x cash 299–499 in non-PvP games only, or a smaller multiplier.
  - VIP 375–500.
  - Capacity unlocks (more land, floor, item limit) 249–1,599.
  - Sandbox or creative mode 999–1,499 as the anchor.
  - Cash packs scaled to the in-game economy at 49–1,499.
  - Timed boosts 40–400.
  - Skips 15–49.
  - Gift twins for all passes.
  - Use Managed Pricing to regionalize.
- **Reframing offers for kids.** Swap urgency-driven limited-time offers for **seasonal content** that returns ("Returning Limited," as in Mansion Tycoon). Use always-available bundles rather than countdown timers, to stay inside ICO and CPC guidance.

### Gaps
- I found no rigorous public A/B data on Roblox price points (99 vs 199 vs 399), first-purchase conversion lift or bundle uptake. The DevForum material is anecdotal, and Roblox shares only aggregate price-optimization lifts.
- I found no RDC 2025–2026 session data on starter-pack performance.
- Current official Robux bundle prices by platform (October 2026) couldn't be verified directly. Sources conflict and some are stale.
