# Player Retention and Engagement Design for Roblox Tycoon and Idle/Incremental Games

Research date: 2026-10-18. Every claim has an inline source. Source quality varies a lot, so each finding is tagged:
- **[PRIMARY]**: Roblox official docs or posts, GameAnalytics benchmark datasets, or developer-authored posts.
- **[SECONDARY]**: press or reputable analysts.
- **[WEAK]**: marketing or SEO sites, unsourced blogs, or forum anecdotes.

Where nothing reliable exists, the gap is stated.

---

## 1. Realistic retention and engagement benchmarks on Roblox (D1/D7/D30, session length, sessions/day, playtime)

### Takeaway
Roblox retention is far lower than mobile-app benchmarks suggest. In GameAnalytics' 2026 dataset (500+ games with 1M+ MAU), the **median game has D1 10.3%, D7 1.6% and D30 0.5%**. The **top 1% reach D1 22.2%, D7 9.1% and D30 4.7%**. The median game session is 9.8 minutes (top 1%: 21.1 minutes). The median game gets 1.56 sessions per player per day (top 10%: 3.22). The widely quoted "20% D1 is good, 40% is excellent" figures are inflated. Roblox's own docs define these metrics and show percentile benchmarks against similar experiences inside Creator Analytics, but they publish no target numbers.

### Cited Findings

**GameAnalytics 2026 Roblox Benchmark Report [PRIMARY dataset]**
- Updated September 1, 2026. Sample: 500+ Roblox titles with 1M+ MAU, August 1, 2025 to July 31, 2026. 67 titles exceeded 10M monthly sessions and 253 exceeded 1M; 4.76 billion sessions in total. — [GameAnalytics 2026 Roblox Report](https://www.gameanalytics.com/reports/2026-roblox-report)
- Game-level retention:

  | Percentile | D1 | D7 | D30 |
  |---|---|---|---|
  | p25 | 8.4% | 1.0% | 0.3% |
  | p50 | 10.3% | 1.6% | 0.5% |
  | p99 | 22.2% | 9.1% | 4.7% |

  The report gives 12.9–15.9% (p75–p90) as the target range for D1. — [GameAnalytics 2026](https://www.gameanalytics.com/reports/2026-roblox-report)
- Game-level session length (minutes): p25 7.3, p50 9.8, p75 12.0, p90 14.7, p95 16.6, p99 21.1. — [GameAnalytics 2026](https://www.gameanalytics.com/reports/2026-roblox-report)
- Game-level sessions per player per day: p25 1.34, p50 1.56, p75 2.07, p90 3.22, p95 4.06, p99 8.30. — [GameAnalytics 2026](https://www.gameanalytics.com/reports/2026-roblox-report)
- Player-level figures, across all games a player touches:
  - Median player: 3 sessions/day, 7.28-minute sessions, 22.4 minutes of total daily playtime.
  - p90 player: 11 sessions/day, 26.3 minutes per session, 123.85 minutes/day.
  - p99 player: 42 sessions/day and 404.98 minutes/day.
  - The report gives no "playtime per DAU" figure; total daily playtime per user is the closest metric.
  - — [GameAnalytics 2026](https://www.gameanalytics.com/reports/2026-roblox-report); [GameDev Reports summary, Sep 25 2026](https://gamedevreports.substack.com/p/gameanalytics-key-roblox-and-roblox)
- Only 3.80% of tracked players paid anything during the period, down from 4.2% two years earlier. Median ARPPU was $0.70. — [GameDev Reports summary](https://gamedevreports.substack.com/p/gameanalytics-key-roblox-and-roblox)
- GameAnalytics' qualitative findings:
  - "D1 is usually won in the first two minutes": players who see no progress quickly don't return.
  - Strong D30 almost always comes from live-ops, seasonal events or deep persistent progression. Outstanding D30 comes "almost exclusively" from big-IP titles or heavy persistent progression.
  - The very high player-level session counts (p95–p99) are *probably* timers and offline-progression loops. GameAnalytics flags this as its inference, not a measured finding.
  - — [GameAnalytics 2026](https://www.gameanalytics.com/reports/2026-roblox-report)
- GameAnalytics calls the circulating "20% D1 = good / 40% = excellent" charts inflated, because they come from small samples of already-promoted games. Its 2023 report showed 12–15% D1, but that sample included smaller projects. The benchmarks exclude games under 1M MAU, so figures across all games would be lower. — [GameAnalytics 2026](https://www.gameanalytics.com/reports/2026-roblox-report); [GameDev Reports](https://gamedevreports.substack.com/p/gameanalytics-key-roblox-and-roblox)

**GameAnalytics 2025 Roblox Benchmark Report: retention by session-length tier [PRIMARY dataset, 2025 data]**

Median values by session-length tier:

| Avg session length | D1 | D7 | D30 | Sessions/day |
|---|---|---|---|---|
| 0–3 min | 4.31% | 0.41% | 0.13% | 1.3 |
| 4–6 min | 6.20% | 0.88% | 0.28% | 1.0 |
| 7–12 min | 7.91% | 0.90% | 0.24% | 1.0 |
| 13–18 min | 10.24% | 1.20% | 0.34% | 1.0 |
| 19–24 min | 11.46% | 1.61% | 0.46% | 1.8 |
| 25+ min | 10.76% | 1.82% | 0.50% | 2.2 |

- Upper percentiles by tier:
  - **p90 D1:** 11.55% (7–12 min sessions), 14.96% (13–18 min), 18.20% (19–24 min), 18.86% (25+ min).
  - **p90 D7:** 5.15% (19–24 min) and 5.86% (25+ min).
  - **p90 D30:** 1.44% (19–24 min) and 1.45% (25+ min).
  - — [GameAnalytics 2025 Roblox Report](https://www.gameanalytics.com/reports/2025-roblox-report)
- Platform trend, median player:
  - Total daily playtime: 16.4 min (2023), 16.44 (2024), 16.77 (2025).
  - Daily sessions: 2, 2, 2.02.
  - p90 daily playtime rose from 51.5 to 64.91 minutes between 2023 and 2025.
  - — [GameAnalytics 2025](https://www.gameanalytics.com/reports/2025-roblox-report)
- Neither GameAnalytics report breaks benchmarks out by genre, so there are no tycoon-, simulator- or idle-specific numbers. — [GameAnalytics 2025](https://www.gameanalytics.com/reports/2025-roblox-report); [GameAnalytics 2026](https://www.gameanalytics.com/reports/2026-roblox-report)
- **Conflict to note:** the 2025 medians show a clear positive relationship between session length and retention. The 2026 report says a game's rank on one metric "does not predict its rank on another." — [GameAnalytics 2025](https://www.gameanalytics.com/reports/2025-roblox-report); [GameAnalytics 2026](https://www.gameanalytics.com/reports/2026-roblox-report)

**Roblox Creator Hub (official) [PRIMARY]**
- Definitions:
  - "Day 1 retention is the percentage of new users who come back to your game after visiting it for the first time." It is measured on the day after the first visit.
  - D7 is measured on the 8th day and D30 on the 31st.
  - Cohorts are keyed to the first play date.
  - — [Roblox Docs: Retention](https://create.roblox.com/docs/production/analytics/retention)
- Roblox's levers by horizon:
  - **D1:** "focus on your game's core loop, first-time user experience, and performance." Keep the FTUE short, ideally reaching the fun within 5 minutes, and track step-by-step funnel completion.
  - **D7:** focus on the progression system, with short- and long-term goals, content variety and balanced difficulty.
  - **D30:** focus on the "ending system." Add content regularly: "A common frequency is to release smaller updates on the existing mechanics every 2-4 weeks." Add social mechanics: trading, guilds, PvP, leaderboards.
  - — [Roblox Docs: Retention](https://create.roblox.com/docs/production/analytics/retention)
- Average session time is "the total time users spend in your game divided by the number of sessions" and is "closely tied to retention." The engagement dashboard also has a "New User First Session Retention" chart: how many new users are still playing N minutes after their first join. — [Roblox Docs: Engagement](https://create.roblox.com/docs/production/analytics/engagement)
- The retention cohort table also reports 7D playtime per user, 7D payer conversion, and 7D and 30D revenue per user. — [Roblox Docs: Retention](https://create.roblox.com/docs/production/analytics/retention)
- Creator Analytics benchmarks rank a game as a percentile against similar experiences. Developers describe their stats this way: a tycoon with D1/D7 "below the 30th percentile" while other stats sit at the 60th–80th. — [DevForum: "I don't know why my game is getting low retention" (Jun 2025)](https://devforum.roblox.com/t/i-dont-know-why-my-game-is-getting-low-retention/3790969)
- Roblox says "benchmarks don't affect the algorithm"; they are only a comparison point. — [DevForum: Recommended For You algorithm improvements (Jun 15 2026)](https://devforum.roblox.com/t/recommended-for-you-algorithm-improvements-that-better-value-long-term-retention/4684575)

**Why long-term retention now matters more for discovery [PRIMARY]**
- In June 2026, Roblox moved the "Recommended For You" home ranking from a 7-day view to "a 28-day view that directly measures long-term retention." — [Roblox Newsroom, Jun 2026](https://about.roblox.com/newsroom/2026/06/optimizing-discovery-great-games-reach-millions-players-roblox)
- Signal design:
  - The signals are Playtime, Play days, Qualified play sessions, Intentional co-play days, Spend days and Robux spent.
  - Each is measured over Day 1, Days 2–7 and Days 8–28, for users who joined organically from the Recommended For You sort.
  - New signals: play-through rate (PTR) and first-play bounce rate. Qualified play-through rate was removed.
  - Relative weights appear only in Creator Analytics (Acquisition > Home Recommendations).
  - — [DevForum RFY post](https://devforum.roblox.com/t/recommended-for-you-algorithm-improvements-that-better-value-long-term-retention/4684575)
- Roblox says games creating "long-term player value through retention, co-play, and spend" get more opportunity. It cites 132M DAU (Q1 2026). — [Roblox Newsroom](https://about.roblox.com/newsroom/2026/06/optimizing-discovery-great-games-reach-millions-players-roblox)
- [SECONDARY, single source] Roblox's Q2 2026 shareholder letter reportedly called the change intentional: it gave more impressions to retentive games at the expense of near-term monetization. Bookings grew only 8%, and Q3 guidance was down 14–18% YoY. — [godisageek, Aug 2026](https://godisageek.com/2026/08/roblox-9-billion-algorithm-change/)

**Creator Rewards: a direct payout incentive for daily returns [PRIMARY]**
- Creator Rewards (launched July 2025) replaced Engagement-Based Payouts.
  - It pays 5 Robux per "Active Spender" who plays ≥10 minutes a day, but only if the experience is among the first three that user launches that day.
  - Active Spender: spent ≥$9.99 in the last 60 days.
  - It also pays a 35% share of the first $100 spent by new or returning (60+ days inactive) users in their first two months.
  - — [DevForum: Introducing Creator Rewards](https://devforum.roblox.com/t/introducing-creator-rewards-earn-more-by-growing-the-community/3777628); [Tubefilter](https://www.tubefilter.com/?p=186987); [MediaPost](https://www.mediapost.com/publications/article/406941/roblox-to-reward-creators-for-attracting-players.html)
- Analyst Andy Hall argues this pushes developers toward daily streaks and short daily sessions. He says Roblox moved away from pure time-spent payouts because they encouraged grindy, AFK-style design. — [Free Systems (Andy Hall), Dec 4 2025](https://freesystems.substack.com/p/the-algorithm-behind-steal-a-brainrot)

**Weak / vendor benchmarks (for awareness only) [WEAK]**
- BLOXG's genre thresholds (D1 Good 20%, Great 30%, Excellent 40%+) have unverifiable methodology and conflict with GameAnalytics. — [BLOXG retention benchmarks](https://bloxg.com/statistics/roblox-retention-benchmarks)
- Endsights claims "about 38% average day-7 retention for prestige tycoons" with no cited source. That is ~4x GameAnalytics' p99 D7 (9.1%), so it is almost certainly wrong. — [Endsights, Apr 25 2026](https://endsights.com/roblox-tycoon-games)
- Top *mobile-app* benchmarks are often quoted as D1 35–40%, D7 10–15%, D30 5–10%. These are not comparable to Roblox, where a "new user" can bounce at near-zero cost. — [Game-Ace idle game guide](https://game-ace.com/blog/idle-game-development/)

**Developer-reported tycoon/incremental numbers [WEAK: anecdotes]**
- *Tropical Incremental* (Jan 2026) has daily rewards, weekly updates, prestige, rare item opening and cosmetics. It reports D1 of 7–10% against a goal of 16%. — [DevForum, Jan 30 2026](https://devforum.roblox.com/t/low-d1-retention-tropical-incremental/4315335)
- A tycoon/sim hybrid (Aug 2025) shipped a larger map, new purchases, playtime rewards, a new UI and rebirth.
  - Playtime fell from 18 to 12 minutes and D1 from 8–10% to 4–6%. Peak CCU went from ~2,500 to ~300.
  - Replies suggested a denominator effect (more new, low-intent users), a client FPS-degradation bug, and new script errors.
  - — [DevForum, Aug 14 2025](https://devforum.roblox.com/t/sudden-drop-on-playtime-and-retention-with-update/3880064)
- *Samurai Tycoon* (Jun 2025) has daily rewards, daily quests and multiple rebirths that unlock weapons. D1/D7 stayed below the 30th percentile across 3 weeks of ads. — [DevForum, Jun 30 2025](https://devforum.roblox.com/t/i-dont-know-why-my-game-is-getting-low-retention/3790969)

### Inferences
- Realistic tiers for a *non-viral* tycoon, using GameAnalytics' 1M+ MAU sample. Smaller games skew lower.
  - **Poor:** D1 <8%, D7 <1%, D30 <0.3%, sessions <7 min.
  - **Average:** D1 ~10%, D7 ~1.5%, D30 ~0.5%, ~10-min sessions, ~1.5 sessions/day.
  - **Good (top quartile to top 10%):** D1 13–16%, D7 ~2.5–5%, D30 ~1–1.5%, 12–15+ min sessions, 2–3 sessions/day.
  - **Elite (top 1%):** D1 ~22%, D7 ~9%, D30 ~4.7%, 20+ min sessions.
- Session length tracks D7/D30 (2025 data). Games averaging 19+ minute sessions sit in the best tier and also get more sessions per day. Tycoons naturally produce long sessions, which is a structural advantage, but only if the long session ends with a reason to come back.
- The 2026 discovery change weights days 8–28. Under it, a tycoon that is "finished" in one or two sessions is penalized even if its D1 and session length are fine. This makes the "finish and leave" problem (Section 3) a *distribution* problem, not just a design flaw.
- Creator Rewards pays per daily qualified (10+ minute) visit. That makes "come back every day for 10+ minutes" the economically optimal pattern, which favors offline/idle earnings, timers and daily streaks.
- Daily rewards, daily quests and rebirth are now *table stakes*. All three anecdotal games had them and still sat at or below median, so they don't differentiate on their own.

### Gaps
- There are no published genre-level benchmarks (tycoon vs. simulator vs. idle) from Roblox or GameAnalytics. Every genre-specific retention figure found came from unsourced vendor sites.
- Roblox's actual relative weights for the RFY signals are visible only inside Creator Analytics, not in public text.
- No reliable public "playtime per DAU" benchmark exists for individual Roblox games.
- No reliable data on D7/D30 at the p75–p95 level from the 2026 report's text (only p25, p50 and p99 were extractable).

---

## 2. Which mechanics measurably improve retention in tycoons and idle games

### Takeaway
No public controlled experiments (A/B results with numbers) were found for Roblox tycoon mechanics, so evidence is mostly official guidance, design analysis of the mega-hits, and developer anecdotes. The convergent evidence:
- **Appointment mechanics that keep working while you're away** drive return visits: offline growth, rotating shops on short timers, timed free spins, weekly online-only drops.
- **Collection plus rarity plus trading** drives long-term retention and status.
- **Light social conflict or co-presence** drives virality and co-play, which is now an explicit discovery signal: stealing, visiting bases, multi-plot servers.
- **A reliable live-ops cadence** drives D30. Weekly is the gold standard for mega-hits; Roblox suggests every 2–4 weeks.
- **Rebirth/prestige** extends D7–D30 *only* if it gives a meaningful new payoff, not just a multiplier.

### Cited Findings

**Official Roblox guidance [PRIMARY]**
- D30 levers: "smaller updates on the existing mechanics every 2-4 weeks," plus trading, guilds, PvP and leaderboards. — [Roblox Docs: Retention](https://create.roblox.com/docs/production/analytics/retention)
- Show "short-, mid-, and long-term goals" (skill trees, season passes, quests, collections) in highly visible places. End onboarding with "an intentionally designed moment of joy" so players return. — [Roblox Docs: Onboarding](https://create.roblox.com/docs/production/game-design/onboarding)
- Discovery explicitly counts **Intentional co-play days** and **Play days** across days 1–28. Social and return-visit mechanics therefore directly affect distribution. — [DevForum RFY post](https://devforum.roblox.com/t/recommended-for-you-algorithm-improvements-that-better-value-long-term-retention/4684575)
- [SECONDARY, Roblox position quoted second-hand] "Users who play more frequently, spend more often, and intentionally co-play with friends have higher long-term retention." The source also names a "7-Day Intentional Co-Play Days per User" metric. — [Max Power Gaming](https://www.maxpowergaming.co/post/why-roblox-s-new-discovery-algorithm-favors-games-that-bring-friends-together)
- GameAnalytics restates Roblox's view: friends playing together produce stickier sessions (longer, more spend, more returns). — [GameAnalytics 2025](https://www.gameanalytics.com/reports/2025-roblox-report)
- [WEAK] Claims that friends-players retain "3–5x better" ([BLOXG](https://bloxg.com/guides/roblox-player-retention)), or that one friendship by Day 5 gives 3x D30 ([Rolearn](https://rolearn.dev/guidance/first-week-retention-optimization/)), have no traceable dataset.

**Offline / idle earnings and timers [SECONDARY analysis + PRIMARY dataset inference]**
- In Grow a Garden, crops keep growing while the player is offline. — [Wikipedia: Grow a Garden](https://en.wikipedia.org/wiki/Grow_a_Garden)
- Andy Hall's analysis of Grow a Garden lists several pull-back mechanics:
  - Plants grow while logged out, pulling players back to harvest.
  - Harvest/replant schedules require check-ins.
  - A rotating shop surfaces rare seeds only briefly.
  - Pets gain value faster for regular log-ins.
  - Randomized seed boxes and eggs provide intermittent reinforcement.
  - Weekend live events forfeit rewards if missed.
  - Gardens are visible to others, creating social status.
  - — [Free Systems (Andy Hall), Dec 2025](https://freesystems.substack.com/p/the-algorithm-behind-steal-a-brainrot)
- Grow a Garden's seed and gear shops restock on a ~5-minute global cycle, and rare-seed stock is shared across servers. Fans built browser extensions just to track restocks. — [Deltia's Gaming](https://deltiasgaming.com/?p=207402); [AverGames stock guide](https://avergames.com/games/grow-a-garden/shop-stock-guide) [WEAK, fan guides]
- Steal a Brainrot's first screen offers a "radioactive spin" that is free only after a timer. The author observed ~1 hour 27 minutes remaining; spinning sooner requires a purchase. — [Free Systems](https://freesystems.substack.com/p/the-algorithm-behind-steal-a-brainrot)
- GameAnalytics attributes the extreme player-level session counts (p95: 17/day; p99: 42/day) *likely* to timers and offline-progression loops. — [GameAnalytics 2026](https://www.gameanalytics.com/reports/2026-roblox-report)
- Mobile idle practice: Egg, Inc. caps offline earnings at 2 hours. — [Math of Idle Games Pt III (Kongregate, Feb 2017)](https://www.gamedeveloper.com/design/the-math-of-idle-games-part-iii)
- Developer guides recommend a *reduced* offline rate rather than full earnings. The rationale: an uncapped offline gain removes the reason to reopen. — [dev.to, "I Built 7 Idle Games in 30 Days"](https://dev.to/aguier/i-built-7-idle-games-in-30-days-what-i-learned-about-incremental-design-5d3f) [WEAK]; [West Games offline calculator](https://west-games.com/idle-game-offline-earnings-calculator/) [WEAK]

**Weekly online-only exclusives / limited-time events [SECONDARY]**
- Grow a Garden released exclusive items weekly that had to be claimed while online; Wikipedia credits these with boosting retention. — [Wikipedia: Grow a Garden](https://en.wikipedia.org/wiki/Grow_a_Garden)
- Its CCU peaks coincided with update and event days:
  - ~5M on May 18, 2025 (Blood Moon).
  - 11.7M after May 31 (Bizzy Bees).
  - 16M on June 14.
  - 21.3M on June 21 (Summer Update).
  - 22.3M+ on August 23 (mock "admin war").
  - CCU fell to 7.6M within an hour of the June 21 peak.
  - — [Wikipedia: Grow a Garden](https://en.wikipedia.org/wiki/Grow_a_Garden)
- Steal a Brainrot runs special "admin abuse" events offering exclusive characters. Its record peaks were also event-driven: 24M at the September 13, 2025 "Extinct Event," 25.4M in October 2025, and a 12.8M Bruno Mars concert in January 2026. — [Wikipedia: Steal a Brainrot](https://en.wikipedia.org/wiki/Steal_a_Brainrot)
- Idle Miner Tycoon's revenue had "a clear inflection point" when it integrated events offering limited-time mines as rewards. — [GDC 2019 Idle Miner Tycoon summary, MobileFreeToPlay](https://mobilefreetoplay.com/gdc-2019-deconstructing-idle-miner-tycoon/)

**Update cadence [PRIMARY / SECONDARY]**
- Pet Simulator 99 shipped weekly updates (Saturdays 5 PM GMT), a "metronome-like cadence that gives players a reliable reason to return." — [RoWatcher: Inside BIG Games (~Mar 2026)](https://rowatcher.com/news/inside-big-games-how-pet-simulator-became-a-100m-roblox-empire) [SECONDARY, undated]
- After 60 weekly updates, BIG Games announced a shift to bi-weekly. The post's date is ambiguous on the page. — [BIG Games blog](https://www.biggames.io/post/pet-simulator-99-update-69) [PRIMARY]
- Grow a Garden formed two dedicated event teams in July 2025. — [Wikipedia: Grow a Garden](https://en.wikipedia.org/wiki/Grow_a_Garden)
- Grow a Garden later announced a "new era" of deeper farming after "a series of disappointing updates." Coverage reports the developer saying weekly events were too hard to keep fresh, with changes rolling out over several weeks. (Only the headline/subtitle was retrievable; the quote detail came from the search snippet.) — [PC Gamer](https://www.pcgamer.com/games/survival-crafting/robloxs-top-experience-grow-a-garden-is-shifting-into-a-new-era-and-promises-deeper-farming-after-a-series-of-disappointing-updates-i-hope-the-community-can-see-this-change-as-a-positive-attempt-to-keep-the-game-fresh-and-enjoyable-for-everyone/)
- A fan tracker reports weekly standard patches and major themed updates every 3–6 weeks. This is not an official schedule. — [GAGData updates hub](https://www.gagdata.com/blog/updates) [WEAK]
- Adopt Me's weekly update schedule "resulted in crunch." Uplift responded by hiring producers and splitting the team across content streams. (2021 coverage, older.) — [Vice](https://www.vice.com/en/article/how-these-developers-hope-to-build-a-100-person-game-studio-inside-roblox/); [PCGamesInsider](https://www.pcgamesinsider.biz/interviews-and-opinion/72169/why-the-devs-behind-robloxs-adopt-me-are-launching-new-studio-uplift-games/)
- Theme Park Tycoon 2 logged 46 version updates in 2025. — [TPT2 Wiki Changelog/2025](https://tpt2.fandom.com/wiki/Changelog/2025) [fan wiki]

**Collection, rarity, trading [SECONDARY]**
- Pet Simulator 99's loop is hatch eggs, collect coins, unlock areas, fuse and upgrade pets. Number scaling reaches the quintillions. HUGE/TITANIC/GARGANTUAN tiers are status symbols that drive a secondary trading economy. Players could migrate pets from PSX to PS99 ("Pet Box"), carrying collections across sequels. — [RoWatcher](https://rowatcher.com/news/inside-big-games-how-pet-simulator-became-a-100m-roblox-empire)
- Adopt Me players collect and trade 150+ pets. The developers describe giving players tools to make their own fun rather than prescribing goals. (2021-era coverage.) — [Vice](https://www.vice.com/en/article/how-these-developers-hope-to-build-a-100-person-game-studio-inside-roblox/); [PCGamesInsider](https://www.pcgamesinsider.biz/interviews-and-opinion/72169/why-the-devs-behind-robloxs-adopt-me-are-launching-new-studio-uplift-games/)

**Social conflict: stealing/raiding [SECONDARY]**
- Steal a Brainrot's design:
  - Brainrots bought from a conveyor generate passive income in your base.
  - Players buy rarer ones or steal from others, likened to capture the flag.
  - A base button creates a temporary anti-theft shield, and traps can be bought.
  - — [Wikipedia: Steal a Brainrot](https://en.wikipedia.org/wiki/Steal_a_Brainrot)
- Commentary credits its tension and risk-reward cycle (versus "repetitive grinding" in most tycoons) with bringing players back. Viral clips of children crying over stolen Brainrots acted as free marketing. — [KeysforGame](https://www.keysforgame.com/behind-the-runaway-success-of-steal-a-brainrot/) [WEAK]; [Wikipedia](https://en.wikipedia.org/wiki/Steal_a_Brainrot)
- Grow a Garden also lets players steal crops; stealing is one of the things Robux can enable. — [Wikipedia: Grow a Garden](https://en.wikipedia.org/wiki/Grow_a_Garden)
- Downsides reported for Steal a Brainrot: cheaters using automation scripts for collecting and stealing (Game Rant), and pay-to-win criticism (Polygon). — [Wikipedia: Steal a Brainrot](https://en.wikipedia.org/wiki/Steal_a_Brainrot)

**Daily rewards, playtime gifts, quests [WEAK: anecdotes only]**
- No controlled data was found. Anecdotes:
  - Daily rewards gave long sessions (above the 90th percentile) but weak return rates. — [Rolearn](https://rolearn.dev/guidance/first-week-retention-optimization/) [WEAK]
  - D1 stayed at 7–10% "despite having daily rewards." — [DevForum Tropical Incremental](https://devforum.roblox.com/t/low-d1-retention-tropical-incremental/4315335)
  - Daily rewards plus daily quests plus rebirth still left D1/D7 below the 30th percentile. — [DevForum Samurai Tycoon](https://devforum.roblox.com/t/i-dont-know-why-my-game-is-getting-low-retention/3790969)
  - Adding playtime rewards and rebirth in one update coincided with a D1 drop, with confounders. — [DevForum](https://devforum.roblox.com/t/sudden-drop-on-playtime-and-retention-with-update/3880064)

**Rebirth/prestige [mixed]**
- Rebirth is the standard tycoon retention tool for veterans who finish the base path. War Tycoon uses rebirth milestones to unlock content. — [creation.dev Tycoon glossary](https://www.creation.dev/glossary/tycoon); [Rolimons: War Tycoon](https://www.rolimons.com/game/4639625707)
- Prestige creates a "ladder climbing" sense of power after a reset and reins in large numbers for pacing. — [Math of Idle Games Pt III](https://www.gamedeveloper.com/design/the-math-of-idle-games-part-iii)
- [WEAK, single dev anecdote] Adding a tooltip and animated preview to the prestige button "led to a 19% uplift in retention past Day 7," and prestige must give a noticeable speed-up right after the reset. — [dev.to](https://dev.to/aguier/i-built-7-idle-games-in-30-days-what-i-learned-about-incremental-design-5d3f)

### Inferences
- Combine three things: a real-time asset that matures while offline, a short-cycle shop restock, and an online-only weekly drop. This hits the discovery signals for multiple play days per week and the Creator Rewards incentive for daily 10-minute visits. Grow a Garden is the strongest evidence that this combination works at scale.
- Stealing/raiding adds emotional stakes and virality, but it also brings cheating, toxicity and young-player distress. If you include it, add protective counterplay: shields or locks, traps, steal windows, or offline protection.
- Weekly cadence correlates with the biggest hits, but it is costly. BIG Games stepped down to bi-weekly, Grow a Garden hit freshness limits, and Adopt Me crunched. For a small team, Roblox's 2–4 week cadence plus *weekly rotating content* (limited shop items, weekend events) is the sustainable middle ground.
- Daily rewards, playtime gifts and quests are hygiene features. On their own they don't lift a weak core loop above median.

### Gaps
- No public A/B test results for Roblox tycoons on daily login streaks, offline earnings, playtime gifts, group rewards or leaderboards.
- No data on whether the in-game "join group for reward" mechanic affects retention.
- No quantified evidence on leaderboards' retention effect in tycoons.
- No reliable data on whether "visiting other players' bases" or co-op building measurably helps tycoon retention, beyond Roblox's general co-play claims.

---

## 3. The "finish the tycoon and leave" problem and its solutions

### Takeaway
Classic button-and-dropper tycoons are linear: a fixed set of purchases leads to a completed base, so there is no reason to return. Developers on the DevForum describe tycoons as "played only once" unless they break the formula. A plain multiplier-only rebirth doesn't fix it. What works:
- Endless or collection-driven progression (pets, brainrots, crops with rarity).
- Rebirths that unlock *new* content: models, abilities, areas.
- Multiple visual worlds or tiers.
- Social conflict (PvP or war, stealing).
- Creative sandbox depth (Theme Park Tycoon 2).
- Continuous live-ops.

### Cited Findings
- A DevForum reply says most tycoons are "played only once" unless they differ from the norm, citing Military Tycoon as the exception. — [DevForum, Jun 30 2025](https://devforum.roblox.com/t/i-dont-know-why-my-game-is-getting-low-retention/3790969)
- Since 2021, war tycoons such as Military Tycoon, where troops fight at the map center, have gained traction. — [Roblox Wiki: Tycoon](https://roblox.fandom.com/wiki/Tycoon) [fan wiki]
- War Tycoon (created January 2020; 1.12B+ plays) combines a tycoon with a war using weapons and vehicles, and uses rebirth milestones to unlock content. — [Rolimons: War Tycoon](https://www.rolimons.com/game/4639625707)
- Developers report weak rebirths:
  - A tycoon with rebirth "had no re-play value."
  - In another, rebirth came too early and the post-rebirth reward (buying 14 "magic rows" at 750 each) felt weak.
  - — [DevForum search summary: Tycoon Game Feedback](https://devforum.roblox.com/t/tycoon-game-feedback/2838875) [WEAK]
- DevForum suggestions for meaningful rebirths (2020): a cash head start or multiplier, new unit models with special abilities, new building types, a "main nest upgrade" that functions as a rebirth, and a secondary rebirth currency to buy exclusive items. — [DevForum, May 3 2020](https://devforum.roblox.com/t/original-tycoon-mid-and-late-game-content-lacking/554985) [older]
- Roblox frames D30 as the "ending system": players should not run out of content. Fixes are regular content, trading, guilds, PvP and leaderboards. — [Roblox Docs: Retention](https://create.roblox.com/docs/production/analytics/retention)
- Mobile idle parallel: after "a few prestiges," idle games "feel the same." Idle Miner Tycoon addressed this with new visual mines. Players can expand to new mines without fully prestiging (keeping the original mine), so prestige is optional. — [MobileFreeToPlay GDC 2019 summary](https://mobilefreetoplay.com/gdc-2019-deconstructing-idle-miner-tycoon/)
- Steal a Brainrot is distinguished from "repetitive grinding" tycoons by its injected tension of stealing and defending. — [KeysforGame](https://www.keysforgame.com/behind-the-runaway-success-of-steal-a-brainrot/) [WEAK]
- Theme Park Tycoon 2 (Den_S; 1.4B+ visits as of 2025) is a creative-sandbox tycoon. It reached its 10th-anniversary update and was updated 46 times in 2025. — [TPT2 Wiki](https://tpt2.fandom.com/wiki/Theme_Park_Tycoon_2); [TPT2 Changelog 2025](https://tpt2.fandom.com/wiki/Changelog/2025)
- Retail Tycoon 2 (Secondhand Studios, Oct 2020; 330.5M visits) still had ~3K online and an all-time peak of 5K CCU in April 2026. Its 2025 updates added decorations and customer-pathing gates (depth and customization over new tiers). — [RoWatcher: Retail Tycoon 2](https://rowatcher.com/games/2092410051/retail-tycoon-2)
- [WEAK, unsourced] Endsights says 2026 tycoons stand apart through specialization branches (combat, racing, restaurant), multi-plot servers where friends build adjacent bases, and cooperative shared plots. It claims "good" prestige designs speed up earlier content and gate new content behind the 3rd or 4th prestige. — [Endsights, Apr 2026](https://endsights.com/roblox-tycoon-games)

### Inferences
- Design the tycoon around an **endless or collection axis**, not a finite button list. Possible axes: rarer units to buy or steal, crops with rarity or mutations, pets.
- Make each rebirth **change what the base looks like and what you can buy**: new world or theme, new generator types, new abilities. Rebirth should take a long and growing amount of time and pay out a permanent currency that buys exclusive items.
- Add at least one **open-ended expression layer**: decoration, layout freedom (the TPT2 and Retail Tycoon 2 model), or competitive status visible to others.
- Add at least one **renewable social reason to return**, such as defending or raiding, trading, or friends' adjacent plots.
- Long-lived tycoons (TPT2, Retail Tycoon 2, War/Military Tycoon) lean on creativity or PvP. Viral 2025 hits (Grow a Garden, Steal a Brainrot) lean on collection, timers and events.

### Gaps
- No retention numbers were found for Theme Park Tycoon 2, Restaurant Tycoon 2, Retail Tycoon 2, Lumber Tycoon 2, War Tycoon or Military Tycoon.
- No developer post-mortems or interviews were found for Restaurant Tycoon 2 or Lumber Tycoon 2.
- No evidence was found comparing "finite but polished" tycoons against endless tycoons on D30.

---

## 4. First-time user experience (FTUE) for a good tycoon

### Takeaway
GameAnalytics says D1 is decided in the **first ~2 minutes**: if players see no progress quickly, they don't return. Roblox's docs say players decide within minutes and the fun should arrive **within 5 minutes**. For tycoons, practitioner heuristics converge on:
- a first purchase within ~30–90 seconds,
- 3–5 upgrades by minute 5,
- the rebirth/prestige goal visible within ~15 minutes,
- short contextual tutorials rather than long ones,
- starter currency or items,
- low early thresholds,
- visible short/mid/long goals,
- a "moment of joy" at the end of the first session.

Mobile UI must keep buttons out of the default control zones and within thumb reach.

### Cited Findings
- "D1 is usually won in the first two minutes"; players who see no progress quickly don't return. — [GameAnalytics 2026](https://www.gameanalytics.com/reports/2026-roblox-report)
- Roblox: keep the FTUE short and ideally get users "to the fun within 5 minutes"; track step completion to find drop-offs. — [Roblox Docs: Retention](https://create.roblox.com/docs/production/analytics/retention)
- Roblox engagement guidance: make the fun obvious within the first five minutes, use short contextual tutorials instead of long ones, give starter items and currency, and support social play. — [Roblox Docs: Engagement](https://create.roblox.com/docs/production/analytics/engagement)
- Roblox onboarding guidance:
  - "New players typically decide their interest in a game within minutes."
  - Teach the core loop so players understand "both *what* they are expected to do and *why*."
  - Keep early XP thresholds low.
  - Give starter items and currency, "without overgiving."
  - Show short/mid/long-term goals visibly.
  - End onboarding with "an intentionally designed moment of joy."
  - A/B test tutorial steps with Experiments and tune values with Configs.
  - — [Roblox Docs: Onboarding](https://create.roblox.com/docs/production/game-design/onboarding)
- The RFY algorithm now includes **first-play bounce rate** and **play-through rate**, so early bounces directly hurt distribution. — [DevForum RFY post, Jun 2026](https://devforum.roblox.com/t/recommended-for-you-algorithm-improvements-that-better-value-long-term-retention/4684575)
- The 2025 GameAnalytics data shows games averaging 0–3 minute sessions have median D1 of only 4.31%, versus 10–11% for 13–24 minute sessions. — [GameAnalytics 2025](https://www.gameanalytics.com/reports/2025-roblox-report)
- How the mega-hits open:
  - Grow a Garden players start with an empty plot and buy carrot seeds, so the first action is a purchase and the first payoff is a growing plant. — [Wikipedia: Grow a Garden](https://en.wikipedia.org/wiki/Grow_a_Garden)
  - Steal a Brainrot players start with a base and a small amount of currency, with a conveyor of buyable Brainrots in front of them. — [Wikipedia: Steal a Brainrot](https://en.wikipedia.org/wiki/Steal_a_Brainrot)
  - Screen Rant credits Steal a Brainrot's "lack of complexity and straightforward gameplay loop." — [Screen Rant](https://screenrant.com/roblox-steal-brainrot-fad-explanation/)
- Pacing heuristics [WEAK, practitioner rules of thumb]:
  - Pacing is "broken" if the player can't afford anything within 90 seconds. Prestige should be discoverable within 15 minutes. A red flag is each upgrade costing ~10x the previous. — [Endsights](https://endsights.com/roblox-tycoon-games)
  - The first upgrade should be affordable within 30–60 seconds, with 3–5 upgrades by minute 5. Gaps between meaningful upgrades should never exceed 20–30 minutes of active play. Offer 2–3 parallel upgrade tracks. (Written for Fortnite UEFN tycoons.) — [Generalist Programmer UEFN tycoon tutorial, 2026](https://generalistprogrammer.com/tutorials/uefn-tycoon-map-tutorial-fortnite-creative)
  - One DevForum developer spaced buy buttons about a minute apart. — [DevForum: best way to make a tycoon](https://devforum.roblox.com/t/what-is-the-best-way-to-make-a-tycoon/1902356)
- Audience:
  - Jandel says ~35% of Grow a Garden players are under 13. — [Wikipedia: Grow a Garden](https://en.wikipedia.org/wiki/Grow_a_Garden)
  - A NYT figure puts ~50M Roblox DAU under 13. — [Free Systems](https://freesystems.substack.com/p/the-algorithm-behind-steal-a-brainrot)
- Mobile UI rules (official):
  - Default controls occupy the bottom-left and bottom-right corners, so keep important info and buttons out of those zones.
  - Put frequently used buttons within comfortable thumb reach.
  - A PC-fitting UI may be cramped on phones and needs a separate layout pass.
  - Test in Studio's Device Emulator.
  - — [Roblox Docs: Cross-platform UI design](https://create.roblox.com/docs/ui/cross-platform-design)
- Device mix (conflicting data):
  - GameAnalytics 2026 device split: PC + mobile 44.0%, PC only 40.76%, mobile only 11.55%, console only 0.43%. — [GameAnalytics 2026](https://www.gameanalytics.com/reports/2026-roblox-report)
  - An unverified third-party blog says ~72% of Roblox activity happens on iOS/Android. — [Voxbooster Roblox statistics 2026](https://voxbooster.com/blog/roblox-statistics-2026) [WEAK]
  - These conflict, so the "majority on phone" assumption isn't confirmed by GameAnalytics' integrated-game data. Either way, **over half of players touch mobile** (44% + 11.55% ≈ 55.6% use mobile at least sometimes, per GameAnalytics).

### Inferences
- A tycoon FTUE blueprint consistent with the sources:
  - **0–30 s:** spawn at (or auto-claim) your plot. One glowing button or arrow. First income visibly ticking.
  - **30–90 s:** first purchase completed with a satisfying visual and audio payoff (a building appears).
  - **By 5 min:** 3–5 purchases, a second income source, and the first "wow" unlock. The long-term goal is visible (rebirth bar, rare item silhouette, next world).
  - **First session (~15–20 min, the top-tier session length):** reach a mini-milestone and the rebirth tease. End with a reward plus a reason to return: an offline-earnings promise, a crop or timer that finishes later, a tomorrow's-reward preview.
- For ages 9–17 on phones:
  - Minimize text and lean on arrows, beams and icons.
  - Use large tap targets away from the corner joystick and jump zones.
  - Prefer tap-to-buy or walk-over pads near spawn. Avoid long walks between buttons on mobile.
- Track FTUE as a funnel: claim plot, first purchase, 5th purchase, first rebirth view, session end. Roblox's funnel analytics and Experiments support this.

### Gaps
- No Roblox-published data on optimal time-to-first-purchase for tycoons. All specific second counts are practitioner heuristics.
- No primary data specific to the 9–17 age group's onboarding behavior (reading level, tutorial tolerance) was found.
- No official Roblox figure on mobile share of playtime was found in this pass. The device data conflicts.

---

## 5. Case studies with numbers

### Takeaway
The 2025–26 mega-hits (Grow a Garden, Steal a Brainrot) are idle/tycoon hybrids built on simple loops, offline progression, rarity collection, light theft, rotating shops and relentless event cadence. They produced the largest CCU spikes in gaming history, but those peaks are event-driven and decay quickly. Pet Simulator shows long-term collection plus trading plus a weekly cadence. Older tycoons (TPT2, Retail Tycoon 2, War Tycoon) survive on sandbox creativity or PvP plus steady updates. Public retention percentages for specific games do not exist.

### Cited Findings

**Grow a Garden (released Mar 26, 2025; BMWLux, with Jandel's Splitting Point Studios)**
- Built in about 3 days. Splitting Point bought in at ~1,000 CCU in April 2025. — [Wikipedia: Grow a Garden](https://en.wikipedia.org/wiki/Grow_a_Garden)
- Loop: buy seeds, plant, harvest, sell for Sheckles, buy rarer seeds. Crops grow offline. Seeds rotate in and out of stock. Pets come from loot boxes. Robux speeds waiting, adds perks and enables stealing. — [Wikipedia](https://en.wikipedia.org/wiki/Grow_a_Garden)
- CCU: ~5M (May 18), 11.7M (May 31), 16M (Jun 14), 21.3M (Jun 21), 22.3M+ (Aug 23, 2025). It fell to 7.6M within an hour of the June 21 peak. It averaged 2.7M CCU on June 25. — [Wikipedia](https://en.wikipedia.org/wiki/Grow_a_Garden)
- Fastest Roblox game to 1B visits (33 days). 35.3B+ visits and ~10.9M favourites as of May 2026. #1 Top Earner by July 19, 2025. — [Wikipedia](https://en.wikipedia.org/wiki/Grow_a_Garden)
- Major updates landed roughly every 1–3 weeks in May–July 2025 (May 18, May 31, Jun 14, Jun 21, Jul 26). Two event teams were formed in July 2025. Weekly online-only exclusives. — [Wikipedia](https://en.wikipedia.org/wiki/Grow_a_Garden)
- Later a "new era" pivot toward deeper farming after "disappointing updates." — [PC Gamer](https://www.pcgamer.com/games/survival-crafting/robloxs-top-experience-grow-a-garden-is-shifting-into-a-new-era-and-promises-deeper-farming-after-a-series-of-disappointing-updates-i-hope-the-community-can-see-this-change-as-a-positive-attempt-to-keep-the-game-fresh-and-enjoyable-for-everyone/)
- TD Cowen alleged bot activity inflated visibility, then retracted the manipulation claim; Roblox disputed it. — [Wikipedia](https://en.wikipedia.org/wiki/Grow_a_Garden)

**Steal a Brainrot (released May 16, 2025; SpyderSammy, DoBig Studios)**
- Loop: buy Brainrots from a conveyor; they generate passive income in your base. Steal from others; shield your base; buy traps. Rebirth resets progress for better stats and currency. "Admin abuse" events offer exclusives. — [Wikipedia: Steal a Brainrot](https://en.wikipedia.org/wiki/Steal_a_Brainrot)
- Monetization interacts with retention through cosmetics, troll gear and rebirth mechanics. The rotating shop's limited items create urgency. — [KeysforGame](https://www.keysforgame.com/behind-the-runaway-success-of-steal-a-brainrot/) [WEAK]
- CCU:
  - 5M peak in July 2025 (7B visits); 20M in August 2025.
  - 47.4M platform record during the August 23 joint "admin war" with Grow a Garden.
  - 24M on September 13, 2025 (Extinct Event); 25.4M in October 2025.
  - September 2025 *average* was ~1M CCU, a roughly 25:1 peak-to-average ratio.
  - — [Wikipedia](https://en.wikipedia.org/wiki/Steal_a_Brainrot)
- It reportedly still appeared in Top Playing Now in May 2026, averaging hundreds of thousands of CCU daily. — [Lootbar blog](https://www.lootbar.com/blog/en/steal-a-brainrot-roblox-top-charts.html) [WEAK]
- Won Best Creative Direction at the 2025 Roblox Innovation Awards. — [Wikipedia](https://en.wikipedia.org/wiki/Steal_a_Brainrot)
- Naavik says the two games are the most-played in gaming history by CCU. It credits their popularity and "rivalry" for Roblox's 2025 engagement surge (DAU +52% and bookings +55% YoY). — [Naavik: State of UGC Games 2026](https://naavik.co/deep-dives/the-state-of-ugc-games-2026/) (via search summary; page blocked on fetch)
- Roblox Q2 2025: 111.8M DAU (+41% YoY), 27.4B hours engaged (+58%). — [Motley Fool, Jul 31 2025](https://www.fool.com/investing/2025/07/31/grow-a-garden-springs-roblox-skyward)

**Pet Simulator (BIG Games)**
- Pet Simulator (2018): 50K CCU on launch day and 1.1B+ visits. PSX: 8B+ visits and top-ranked for 2+ years. PS99: 400K+ CCU near launch, ~44.8K active around March 2026, 2.36B visits. — [RoWatcher (~Mar 2026)](https://rowatcher.com/news/inside-big-games-how-pet-simulator-became-a-100m-roblox-empire)
- Mechanics: eggs and hatching, area unlocks, fusing, quintillion-scale numbers, HUGE/TITANIC/GARGANTUAN rarity, trading economy, seasonal worlds, limited-time events, cross-game pet migration, and a 100+ creator program. — [RoWatcher](https://rowatcher.com/news/inside-big-games-how-pet-simulator-became-a-100m-roblox-empire)
- Cadence: weekly Saturday updates, moving to bi-weekly after 60 weekly updates. — [BIG Games blog](https://www.biggames.io/post/pet-simulator-99-update-69)
- Monetization interaction: Free play is described as "almost impossible" for competitive play, and 400-Robux exclusive eggs rival free outcomes. — [RoWatcher](https://rowatcher.com/news/inside-big-games-how-pet-simulator-became-a-100m-roblox-empire) [SECONDARY]

**Adopt Me! (Uplift Games)**: a collection and trading reference
- Has stayed high for years while trend games rise and fall. Weekly updates led to crunch and a producer-led split of content teams. Player-driven play ("we give them tools to create their own sort of fun"). 150+ tradeable pets. Reported ~$60M/year revenue. (2021-era coverage, older.) — [Vice](https://www.vice.com/en/article/how-these-developers-hope-to-build-a-100-person-game-studio-inside-roblox/); [PCGamesInsider](https://www.pcgamesinsider.biz/interviews-and-opinion/72169/why-the-devs-behind-robloxs-adopt-me-are-launching-new-studio-uplift-games/)

**Classic tycoons**
- Theme Park Tycoon 2: Den_S; 1.4B+ visits (2025); 46 updates in 2025; 10th-anniversary update (turntables, rides). — [TPT2 Wiki](https://tpt2.fandom.com/wiki/Theme_Park_Tycoon_2); [Changelog/2025](https://tpt2.fandom.com/wiki/Changelog/2025)
- Retail Tycoon 2: Secondhand Studios; Oct 2020; 330.5M visits; ~3K online; 5K CCU all-time peak in April 2026. Prima (2023) said updates were infrequent, but 2025 brought decoration and pathing updates. — [RoWatcher](https://rowatcher.com/games/2092410051/retail-tycoon-2); [Prima Games, Jul 2023](https://primagames.com/codes/roblox-retail-tycoon-2-codes)
- War Tycoon: Jan 2020; 1.12B+ plays; PvP war plus rebirth milestones. — [Rolimons](https://www.rolimons.com/game/4639625707)
- Restaurant Tycoon 2: codes active August 2026, rewarding cash, diamonds and furniture; no other data found. — [GFinity, Aug 2026](https://www.gfinityesports.com/article/restaurant-tycoon-2-codes)

### Inferences
- Peak CCU on Roblox is now an event phenomenon: 25:1 peak-to-average for Steal a Brainrot, and Grow a Garden lost ~2/3 of its peak within an hour. Scheduled weekend events create synchronized returns (appointment play). Baseline retention comes from the loop and timers.
- Both 2025 mega-hits are **idle tycoons with collection plus rarity plus light PvP**. They are not classic button tycoons. Their entry cost is minimal: buy one seed or one Brainrot, and watch it make money.
- Long-lived classic tycoons have modest CCU (thousands, not millions) but persist for 5–10+ years through creativity or PvP and steady updates. A developer should choose deliberately between the "viral live-ops machine" and the "durable niche" model.

### Gaps
- No D1/D7/D30 or session-length figures were found for any named game. Developers don't publish them, and third-party trackers show only CCU and visits.
- Lumber Tycoon 2 and Restaurant Tycoon 2: no reliable information was found on update cadence or retention.
- Revenue for Grow a Garden is undisclosed. Pet Simulator revenue figures are third-party estimates.

---

## 6. Mobile idle/incremental design insights that transfer to Roblox

### Takeaway
The Kongregate "Math of Idle Games" model is the standard: **exponential costs (growth rate ~1.07–1.15) against linear or polynomial production**, kept in balance by **milestone multipliers** and **prestige**. Prestige currency should scale with a flat root of earnings (square root, cube root, or ^0.14 as in Egg, Inc.), so each prestige needs a multiple of the previous run. Offline earnings are capped (Egg, Inc.: 2 hours) to preserve reasons to reopen. Visual novelty (new mines or worlds) is needed because repeated prestiges "feel the same." Events that grant limited-time content are a proven live-ops lever.

### Cited Findings
- Core formulas:
  - cost_next = cost_base × rate_growth^owned
  - production_total = production_base × owned × multipliers
  - AdVenture Capitalist's Lemonade Stand: growth 1.07, base cost ~4 (3.738), 1.67/sec.
  - Exponential cost always eventually overtakes polynomial production. Balancing decides when.
  - — [Math of Idle Games Pt I (Anthony Pecorella, Kongregate, Oct 13 2016)](https://www.gamedeveloper.com/design/the-math-of-idle-games-part-i) [older, foundational]
- Milestone multipliers: stacking ×2 bonuses at 25 and 50 owned temporarily push production back ahead of cost. Varying milestone values per generator makes different generators take priority at different times. Without this, the newest generator dominates and older ones feel irrelevant. — [Math of Idle Games Pt I](https://www.gamedeveloper.com/design/the-math-of-idle-games-part-i)
- Bulk-buy formulas:
  - Cost of n generators: b × r^k × (r^n − 1)/(r − 1).
  - Maximum affordable: floor(log_r(c(r − 1)/(b·r^k) + 1)).
  - — [Math of Idle Games Pt I](https://www.gamedeveloper.com/design/the-math-of-idle-games-part-i)
- Prestige curves:
  - Realm Grinder: square root of max earned, so doubling prestige needs ~4x.
  - AdVenture Capitalist: square root of lifetime earnings, ~3–4x.
  - Cookie Clicker: cube root, ~8x.
  - Egg, Inc.: ~^(1/7) of current-run earnings, ~128x. Paired with a 2-hour offline cap.
  - Clicker Heroes: gains based on upgrades per run, plus a steep difficulty curve.
  - Prestige creates a "ladder climbing" feeling and stabilizes number growth for pacing.
  - — [Math of Idle Games Pt III (Feb 1 2017)](https://www.gamedeveloper.com/design/the-math-of-idle-games-part-iii)
- Idle Miner Tycoon (GDC 2019):
  - Repeated prestiges feel the same; new visual mines give a reason to keep going.
  - Players expand to new mines without full prestige.
  - Upgrade choices require strategy.
  - Events with limited-time mines produced a clear revenue inflection.
  - — [MobileFreeToPlay summary](https://mobilefreetoplay.com/gdc-2019-deconstructing-idle-miner-tycoon/) [older]
- Idle Heroes puts idle progress collection inside the core loop rather than at app-open, which Deconstructor of Fun links to higher activity. It has no prestige, so prestige can't undercut monetization. — [Deconstructor of Fun, Feb 2018](https://www.deconstructoroffun.com/blog/2018/2/27/u6ap146ff5rkmm7fj1qzuhggp395l4) [older]
- Deconstructor of Fun recommended "lean live ops" for idle games to strengthen mid-to-long-term retention. — [Deconstructor of Fun 2020 predictions](https://www.deconstructoroffun.com/blog/2020-2-what-happens-when-the-hypercasual-party-ends) [older]
- [WEAK] Prestige must deliver a noticeable speed-up right after reset. Offline should pay a reduced rate, not full earnings. — [dev.to](https://dev.to/aguier/i-built-7-idle-games-in-30-days-what-i-learned-about-incremental-design-5d3f)
- Roblox transfer evidence:
  - Pet Simulator's quintillion-scale numbers ("numbers go up") support ongoing progression. — [RoWatcher](https://rowatcher.com/news/inside-big-games-how-pet-simulator-became-a-100m-roblox-empire)
  - Grow a Garden and Steal a Brainrot both use passive income and offline growth. — [Wikipedia: Grow a Garden](https://en.wikipedia.org/wiki/Grow_a_Garden); [Wikipedia: Steal a Brainrot](https://en.wikipedia.org/wiki/Steal_a_Brainrot)
  - Roblox's Creator Rewards (10+ min/day) and discovery (play days over 28 days) favor games that "change while players are away." — [Free Systems](https://freesystems.substack.com/p/the-algorithm-behind-steal-a-brainrot); [DevForum RFY](https://devforum.roblox.com/t/recommended-for-you-algorithm-improvements-that-better-value-long-term-retention/4684575)

### Inferences
- **Cost curves:**
  - Use per-item exponential growth of ~1.07–1.15 within a tier.
  - Use milestone multipliers (×2 at 10/25/50/100 owned) so players get frequent "power spikes."
  - Avoid ~10x jumps between consecutive early upgrades; Endsights flags this as an early red flag.
- **Prestige/rebirth:**
  - Base rebirth currency on run or lifetime earnings through a square-root or cube-root curve, so the second and third rebirths take noticeably longer.
  - Give an immediate visible speed-up after reset.
  - Unlock a **new visual world or tier** every few rebirths (Idle Miner Tycoon lesson).
  - Show the rebirth reward preview prominently.
- **Offline earnings:**
  - Cap them at a few hours, at a reduced rate.
  - Present them as a "welcome back" payout to collect in person. That gives the return visit a guaranteed moment of joy and nudges a 10+ minute session.
- **Roblox differs from mobile idle:**
  - Roblox sessions are multiplayer and social, so visible bases, co-play and theft or defense add value that single-player mobile idles lack.
  - Roblox players have near-zero switching cost, so the first 2 minutes matter more than on mobile.
  - Pure "idle while app closed" doesn't count toward playtime signals. Offline progress should *pull players back in*, not replace playing.

### Gaps
- No primary 2023–2026 retention benchmarks specific to mobile idle games were retrievable (GameRefinery and Sensor Tower idle reports were not fetched).
- The Kongregate and GDC sources are 2016–2019. The math is timeless, but the market data is dated.
- No evidence was found on optimal offline cap length or offline rate percentages with measured retention outcomes.
