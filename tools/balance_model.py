#!/usr/bin/env python3
"""
Economy pacing model for Build a Monster Hotel: one solo player's first run of
the hotel chain (GDD §6.4, his rulings 2026-10-20) from a new save to
rebirth-ready, simulated second by second: Haunted Manor (location 1), then
Frostfang Lodge (2), then Bayou Spa (3), measured against the pacing targets
of GDD §6.3 and the rule of thumb of §6.2.

It MEASURES; it never tunes. Every number is read from the game's Luau files
(src/shared/Constants.luau, Pieces.luau, Species.luau, Mutations.luau) with a
small Luau-literal parser, and the formulas it mirrors are guarded: if a
formula's source line changes shape (the bus's size and the tutorial's
Commons, the tile ladder, a piece's points, Stay's satisfaction, tip and
review, Rating's categories, staff coverage and stars, the built rooms'
requirement, bars, bonuses, Comfort points, wall, door and furniture prices,
the start room, how GuestService and ResidentService apply the bonuses, the
tutorial's steps, voucher, free tiles, booked Vampire and friendship, the
chain's opening, background earnings, measured rate, floor cap and rebirth
check), the model stops with an error naming the line, rather than silently
simulating an old rule.

Run:  python tools/balance_model.py [--seeds 4] [--hours 8] [--skip-tutorial] [--out <file for the raw tables>]
      [--set Section.Key=value ...]   a WHAT-IF in memory only (e.g. --set Chain.OpenCost.2=500000):
                                      nothing is written to src/, and the report says which values were set.
      [--expeditions [--exp-set Key=value ...]]
                                      the EXPEDITIONS WHAT-IF (GDD A.11.2, not built): off by default, so the
                                      normal run is unchanged. It records the Wing as the run goes and adds a
                                      section comparing, for players who log out N times a day for H hours,
                                      (a) residents earning offline in the Wing to the cap against (b) the
                                      best residents sent on trips, by A.11.2's revised rules and PLACEHOLDER
                                      numbers (EXP below; not in src/), and the pace of the finds. See
                                      "THE EXPEDITIONS WHAT-IF" below.

THE CHAIN (as ChainService, Chain.luau and Constants.Chain implement it, 2026-10-21)
  - Opening location L+1 costs Chain.OpenCost[L+1] from the one purse and
    starts a new hotel there from the start square (PlayerData.resetHotel:
    Grid.StartTiles, the desk, one floor, its own tile ladder, no reviews,
    a measured rate of 0). Locations open in order. Nothing is wiped.
  - The hotel left is put away with its rating as it stood (HotelService.rating
    at the moment of leaving: frozen) and its measured rate. Every TICK s
    (ChainService) each hotel put away pays rate x BackgroundShare x dt
    straight into cash. The played hotel's rate is an EMA (time constant
    RateWindow) of what its guests paid: pay, tips and request tips
    (GuestService.income), not residents, not Book bonuses.
  - The new hotel's reviews start empty (data.reviews), but HotelService's
    other rating samples (desk waits, preference shares, requests done,
    cleaning times) are made once per session and Travel does not clear them:
    the new hotel's Comfort, Service and Cleanliness start from the last
    hotel's samples. Mirrored as the code does it.
  - The new location brings its own room types, amenities, decor and species
    (Pieces/Species rows of that location; prices are already x20 a location
    in the rows); species pay BasePay x LocationPayMultiplier^(location-1) x
    rarity (Economy.speciesPay). The bus draws only the played location's
    species (BusService.locationsPresent, solo). Unlocks are judged on the
    played hotel's rating; the unlocked set is the player's.
  - Residents are the player's (one Wing): Wing residents earn into the till
    wherever the player is; staff work only at the hotel they were assigned at
    (ResidentService), so each new hotel needs its own Room Service.
  - Floors: Chain.floorCap(0) before any rebirth (the old FloorCap of 3 is
    gone). The tutorial's free Commons, Vampire Count and Coffin happen
    once, at Haunted Manor.
  - Every new hotel starts with its one built room (PlayerData.startRoom,
    Constants.Rooms.Start, free): an L of 4 cells, the location's first room
    type with no unlock, its key piece in it (a Bed at Haunted Manor, the
    type's first key elsewhere). So opening costs OpenCost alone.
  - Rebirth-ready (Chain.rebirthReady): every location opened, each hotel's
    rating >= RebirthRating (5): the played one live, the others as left.

THE OPENING POLICY (the model's choice, stated)
  The player opens the next location only once the hotel played holds 5★,
  because a hotel left below 5★ keeps that rating frozen and rebirth needs 5★
  on all three: leaving early means travelling back to finish it. From the
  moment the played hotel first holds 5★ the player SAVES for the opening:
  rules 2-5 below still run (they are cheap against income), but a rule-6
  investment is bought only when it pays itself back (cost / expected extra
  income) before the opening price would be saved anyway at the present
  income. The next location is opened the first second cash covers its price
  while the played hotel stands at 5★ (the new hotel's first room is free).
  The model never travels back.

WHAT IS SIMULATED (as the code implements it, 2026-10-21: built rooms, GDD 5.4, A.12)
  - No walk-ins (GDD 4.3): every guest but the tutorial Slime rides the bus.
  - The Night Bus (BusService, Bus): first bus at FirstBusDelay on a fresh
    server, then every Interval; its size clamp(ceil(VacantShare x vacant
    rooms), MinPerPlayer, MaxPerPlayer) for one player, its guarantees inside
    it: an Epic every EpicEvery-th bus, a Legendary when a :00/:30 wall-clock
    boundary falls between buses (the phase random per seed), a Mythic on
    2-hour boundaries; the rest by rarity weight. Half step off at each stop
    (StepOff apart, the east stop EAST_STOP_AFTER s later), browse BrowseTime
    s, then take a vacant room of their type if the hotel has one (solo, the
    one hotel), or leave. From the decision to the desk BUS_TO_HOTEL s.
  - The tutorial's Commons (BusService.weightCommons, Bus.commonsFor): on its
    first CommonBuses buses past CheckIn, up to CommonsPerBus Commons for the
    hotel's vacant room types replace drawn guests from the end of the list.
    Their Scoring.TutorialBoost does nothing solo (no other hotel to beat).
  - A stay (GuestService, Stay): desk -> room -> pays payRate per second into
    the till, payRate = speciesPay x mutation x milestone(ready rooms of the
    type) x the room's pay bonus, fixed at check-in (the tier is always 1:
    tierPay 1, SatisfactionPerTier adds 0); the stay is the rarity's x the
    stay bonus; one request in the middle half of the stay, open
    RequestWindow s; satisfaction (Stay's, clamped, + the satisfaction
    bonus, clamped), tip, review, friendship (+ the friendship bonus per happy
    stay) at check-out; the room is then dirty until cleaned. Mutations are
    rolled from Mutations.luau.
  - Built rooms (Rooms, A.12): a room of a type is walls, a door, its key
    furniture and at least its minimum cells (the type's w x d); making the
    area a room is free. Walls cost WallCost a half edge, a door DoorCost + the
    WallCost of its half edge; furniture and decor their price, no growth
    with the count (the old 1.15^n room price is gone with the placed rooms).
    Its three bars (Rooms.bars): Size = (cells - min) / (full - min), full =
    min x FullSizeFactor; Furniture = furniture points / max(type's price x
    FurnitureTargetFactor, FurnitureTargetMin); Decor = decor points /
    (DecorTargetPer4Cells x cells / 4); points = price x PointsPerCash. Their
    bonuses (Rooms.bonuses) exactly: pay x (1 + SizePay s)(1 + FurniturePay f),
    stay x (1 + SizeStay s), satisfaction + FurnitureSatisfaction f +
    DecorSatisfaction d, friendship x (1 + DecorFriendship d). Amenities are
    built the same way (their key furniture, their minimum cells); a ready
    amenity counts for Fun, for the satisfaction of its floor's guests, gives
    its tags to its floor, and its bars count in Comfort like a room's
    (HotelService.inputs inserts every ready room's and amenity's bars).
  - The rating (HotelService.inputs, Rating): recomputed every 5 s: Comfort =
    Rooms.comfortPoints (each ready room's and amenity's (s + f + d) / 3 x
    ComfortPerRoom, summed, to ComfortRoomsCap) + 40 x preference share;
    desk waits, requests, dirty rooms, ready amenities, every furniture and
    decor item in the hotel (Style) and room types, plus staff coverage (Room
    Service's efficiency over rooms / RoomsPerStaff) and the share of recent
    cleanings within CleanOnTime; averaged with the last ReviewsKept reviews,
    rounded to a half. Unlocks (Unlocks.met) are permanent once met.
  - Residents (ResidentService): + the friendship bonus per happy stay, move-in at the
    rarity's threshold or by the early chance; only the tutorial Slime needs
    TutorialFriendship; the tutorial's guests are happy by force. A resident in the
    Wing earns EarnFraction of its species' pay into the till; one on staff
    earns nothing but works (Room Service modelled; the others not used).
  - The Monster Book: a species found pays SpeciesFoundPaySeconds of its pay.
  - The tutorial (TutorialService, steps CheckIn, Collect, SecondRoom,
    Furnish, Bus, MoveIn, Goal, Clean, Staff, Preview, Done): the tutorial
    Slime FirstGuestDelay s after CheckIn starts (the start room is there),
    walking in (TUTORIAL_WALK s); the Goal card's voucher makes the Coffin
    (the Coffin Suite's key piece) free, its walls and space are paid; a
    Vampire Count booked on the next bus once 2 buses have passed since the
    Goal card, the tutorial is Done and a Coffin Suite stands vacant (it
    skips browsing).
  - Space (GDD 5.4, Appendix A.1, his rulings 2026-10-20): rooms and
    amenities only on owned tiles. A hotel starts with the StartTiles square;
    the tutorial's Goal card gives the TutorialTiles block free. More space is
    tiles bought one cell at a time, each floor its own ladder
    (Economy.tileCost: TileCost x TileFloorFactor^(floor-1) x TileGrowth^n),
    a floor up only over owned tiles below (Grid.canBuyTile), or the next
    floor (FloorCosts) up to the cap, whichever is cheaper for the cells
    needed. ASSUMPTION (no number in the code): USABLE_SHARE of a floor's
    owned tiles, after the entrance's mouth and the desk (4 cells, floor 1)
    and a stair (4 cells on each floor it joins), takes rooms and amenities;
    the rest is hallway (the corridors to the rooms' doors). Shapes are not
    packed: cells are counted.

WHAT IS NOT SIMULATED (stated so the numbers are read honestly)
  Hunter Night (its reward is +5 min of income every 90 min), events and
  seasonal mutations, daily rewards, likes/friends bonus, passes, the Moon
  Tree, Prestige Stars (none before the first rebirth), Book family bonuses
  (+5 %), offline earnings, other players on the street (they split the bus),
  pitching, Front Desk / Housekeeping / Bellhop / Entertainment staff,
  selling, enlarging, moving or retyping a room, replacing decor, hallway
  decor and furniture, floor finishes, windows, residents' perks, travelling
  back to a hotel left, the time Travel itself takes, the walk from the door
  to the key furniture, and the room shapes (cells are counted, walls priced
  by an assumed share of a compact rectangle's perimeter, furniture by its
  squares, nothing packed or routed).

THE PLAYER (assumptions that most affect the result)
  - Plays continuously and well: checks a guest in CHECKIN_DELAY s after it
    reaches the desk (always under the 10 s free wait), cleans a dirty room
    CLEAN_DELAY s after check-out, collects the till every COLLECT_EVERY s.
  - Fulfils an open request personally with probability P_REQUEST_PLAYER,
    REQ_PLAYER_TIME s after it opens; the first resident is put on Room
    Service staff (the tutorial teaches it), which fulfils any request still
    open after max(RoomServiceDelay / efficiency, its walk to the room) s.
  - Walks inside: desk -> room ROOM_WALK s on floor 1, +ROOM_WALK_PER_FLOOR a
    floor (floor 3 at 70 s, measured in Studio 2026-10-19 evening).
  - When the Wing is full and a better-paying monster (or the tutorial's
    Vampire Count) wants to move in, the player has released the lowest
    earner in time (the game itself refuses a move-in while the Wing is full).
  - At every hotel, STAFF_ASSIGN_DELAY s after an idle resident is there to
    take it, one resident goes on Room Service at that hotel (a species whose
    best job it is, if one idles in the Wing; else the lowest earner).

HOW THE PLAYER BUILDS A ROOM (ASSUMPTIONS: the code prices walls, not shapes)
  - A room or amenity is built in one go: its walls, its door, the type
    chosen, its key furniture (the cheapest key piece placeable at the
    location, Pieces.decorHere: the location's own or location-0 furniture),
    so it is ready at once.
  - Its walls: the most compact rectangle of its cells (a x b, a <= b, a at
    least the type's shorter side); it pays WALL_SHARE of that rectangle's
    perimeter in half edges, one of them its door. The rest is the facade
    (free) or a neighbour's wall paid already: rooms stand in rows.
  - Size: a new room is built either at its minimum cells (Size bar 0) or
    at its full size (min x FullSizeFactor, Size bar 1); which, rule 6
    decides by return on cost, the cells charged at the marginal tile price
    (they use up owned space too); --size min|full forces one (a policy
    what-if). Rooms are never enlarged afterwards. The score does not count
    the Size bar's longer stay, which is worth most when the bus, not the
    rooms, limits the guests.
  - Furniture and decor stand on at most FILL_SHARE of a room's squares
    (Grid.Squares^2 a cell), so a door, a path and the key spot stay free.
    A "fill" buys the pieces still missing from a bar: repeatedly the
    cheapest piece placeable here (of that bar's kind) worth the points
    still missing, else the dearest; paid at price, overshoot included.

THE GREEDY BUYING POLICY (checked every second; one purchase per check)
  1. Tutorial: the second room (a Standard Room at its minimum, the Bed) as
     soon as it is affordable; the Coffin Suite with the voucher's free
     Coffin the moment the Goal card gives it (saving for its walls and the
     tiles it needs).
  2. Goal: once the Coffin Suite is unlocked and none stands, save for it if it
     costs at most 20 minutes of income; then, while no Vampire Count lives
     in the Wing, save for its matching pieces (darkness, organ music) when a
     piece costs at most 10 minutes of income.
  3. Pieces that match the room's guests: for each room, the best set of up
     to three furniture or decor pieces for the species its type serves
     (weighted by how often they come), given its key piece's tags and the
     amenities on its floor; a missing piece is bought when it costs at most
     90 s of income (or 30 % of cash). Every piece adds points to its bar
     (furniture to Furniture, decor to Decor) and one item to Style.
     3b. Bars: a room's Furniture fill, then its Decor fill, when it costs at
     most BAR_FILL_S s of income (rooms in the order built).
  4. Amenities: up to three per floor that has rooms (satisfaction counts
     three on a guest's floor), and more while the hotel's Fun is short of
     100 (ceil(100 / FunPerAmenity) in all); the most useful tags first, a
     duplicate when no new type is left or the new one is still too dear;
     each built at its minimum with its key piece only (its bars are not
     filled), with the tiles it needs, when it costs <= 3 minutes of income.
     Rules 5 and 6 build a room only if the space left on the floors the cap
     allows (every tile bought) still holds the amenities Fun lacks: without
     that, rooms fill both floors first and Fun stays short of 5★ for good.
  5. The first room of a newly unlocked type (at its minimum), when it costs
     <= 5 minutes of income.
  6. Return on cost: a new room of an owned type whose rooms are mostly full
     (mean occupancy >= ROOM_FULL) or whose next room reaches a milestone, at
     its minimum or at its full size; every unfilled Furniture or Decor bar
     of a room; and a floor a room type waits for. Each is scored by its
     expected extra income per second (observed occupancy, the species'
     observed pay, the pay bonus of its bars, the milestone doubling at
     5/10/25 ready rooms of the type, and the tip on the satisfaction a bar
     adds) divided by its cost (plus the tiles or floor it needs when there is
     no space). The best is bought when affordable; otherwise the player
     saves for it (rules 2-5 still run).

THE EXPEDITIONS WHAT-IF (--expeditions; GDD A.11.2 with its scrutiny lines of 2026-10-21)
  The run itself is the normal one; the flag only records, every minute, the
  Wing's residents (role "") and their rates, the income, and each happy stay
  of a Rare-or-better guest by location. Then, at stages of the run (30, 60,
  120 min of play and rebirth-ready), it plays days of a player who logs in n
  times a day for s minutes (sessions evenly spaced, away H = 24h/n - s each
  time), minute by minute, for 14 days (cash, days 2-14 averaged) and 120
  days (finds), and compares:
    (a) STAY: every Wing resident earns its rate while the player plays and
        OfflineFraction of it while away, for at most the offline cap from
        the logout (Economy.offline, ResidentService.welcomeBack);
    (b) TRIP: the party (the 3 best earners, A.11.2's "Best for this trip"
        with no level and no matching) leaves on a trip of length L at each
        logout when the board is free (policy "logout"; "busy" also resends at
        once whenever a trip ends while the player plays). The party earns
        nothing in the Wing while away; the trip pays EXP.Pay x what the party
        would have earned by staying over the trip's own time, counted as
        staying counts (the Wing rate while the player plays, the offline rate
        while away, nothing past the cap measured from that logout). The party
        is back in the Wing at the trip's end (the Hunter Camp's campUntil,
        which A.11.2 builds on) and earns by staying's rules after it.
        Variant LEAK: welcomeBack credits rate(at join) x min(away, cap), and
        rate() counts every resident whose campUntil has passed, so a party
        back before the login is paid the WHOLE absence's offline till on top
        of the trip. That is how the code stands; whether Expeditions keep it
        is an implementation choice.
  The +20 % per matching resident is read two ways (the draft does not say on
  what): on the reward, or on the find chance. Finds: per trip at
  EXP.Lengths' chance, among the destination location's unfound pieces (so
  each find is a new piece), the guarantee read as the PityTrips-th trip of
  PityMin or more in a row without a find; A.11.3's happy-stay roll (StayFind
  per happy stay of a Rare-or-better guest, guaranteed after StayPity misses)
  at the rate the run measured at Haunted Manor. The cash is the Wing's only
  (the guests' income is the same in (a) and (b)); XP is A.11.6's.
  NOT SIMULATED: levels (both sides scale alike), perks lost while the party
  is away (perks are not in the model), the Moon Tree's offline nodes, the
  Night Manager beyond one line at its 8 h cap, a second trip slot, the value
  of a find beyond its shop price, rebirth mid-trip, and the player's own
  income multipliers (both sides scale alike).
"""

from __future__ import annotations

import argparse
import math
import os
import random
import re
import statistics
import sys
from collections import deque
from dataclasses import dataclass, field
from itertools import combinations

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# ---------------------------------------------------------------- player model
CHECKIN_DELAY = 4  # s at the desk before the player taps check-in
CLEAN_DELAY = 5  # s after check-out before the player cleans (plus the hold)
COLLECT_EVERY = 30  # s between till collections
P_REQUEST_PLAYER = 0.6  # chance the player fulfils a request in person
REQ_PLAYER_TIME = (4, 20)  # s after it opens, uniform
STAFF_ASSIGN_DELAY = 10  # s after the first move-in, it goes on Room Service
TUTORIAL_WALK = 12  # s: the tutorial Slime from the pavement 40 studs along to the desk
BUS_TO_HOTEL = 30  # s from the end of the browse to the desk (~300 studs at 10/s)
ROOM_WALK = 20  # s desk -> room on floor 1, +ROOM_WALK_PER_FLOOR per floor up
ROOM_WALK_PER_FLOOR = 25  # floor 3 = 70 s (measured in Studio, 2026-10-19 evening)
EAST_STOP_AFTER = 13  # s: the bus reaches the east stop 13 s after the west (A.1)
USABLE_SHARE = 0.75  # ASSUMPTION: share of a floor's free tiles rooms/amenities take; the rest is hallway
ENTRANCE_DESK_CELLS = 4  # floor 1: the entrance's mouth (2 cells, Grid.entrance) and the 2x1 FrontDesk
STAIR_CELLS = 4  # a 2x2 Stairs on the floor it stands on, and its well on the floor above
ROOM_FULL = 0.6  # a type's rooms are "full" when, on average, not vacant 60 % of the time
DECOR_MATCH_SLOTS = 3  # the policy furnishes for preferences with up to 3 pieces a room
WALL_SHARE = 0.75  # ASSUMPTION: a room pays this share of its rectangle's perimeter (the rest: facade, a neighbour's wall)
FILL_SHARE = 0.5  # ASSUMPTION: furniture and decor cover at most half of a room's squares (door, path, key spot free)
BAR_FILL_S = 120  # policy: a room's Furniture or Decor bar is filled when the fill costs <= 2 min of income
SIZE_POLICY = "roi"  # rule 6's new rooms: "roi" (min or full, by return on cost), "min" or "full" (--size)
START_CELLS = 4  # Constants.Rooms.Start is "an L of four cells" (its comment; the model does not flood-fill walls)

# ------------------------------------------------- the Expeditions what-if (--expeditions)
EXPEDITIONS = False  # set by --expeditions: record the Wing during the run and report the what-if
# GDD A.11.2's numbers, all PLACEHOLDER, as the revised draft has them (scrutiny 2026-10-21). They are not in src/
# (Expeditions are not built): when src/shared/Expeditions.luau exists the model stops and must read them from there.
EXP = {
    "Lengths": {1800: 0.05, 7200: 0.15, 28800: 0.35},  # trip length (s) -> a find's chance per trip
    "Pay": 1.5,  # the fixed reward = Pay x what the party would have earned by staying, counted as staying counts
    "Party": 3,  # up to three residents, Wing residents only (decision 1 (a))
    "Match": 0.20,  # +20 % for each resident matching the destination (on what: read both ways)
    "PityTrips": 10,  # "a guaranteed find every 10 trips of 2 h or more": the 10th such trip in a row without a find
    "PityMin": 7200,
    "XpPerHour": 20,  # A.11.6: XP per hour on an expedition
    "PiecesPerLocation": 5,  # A.11.3: one set of five per location at launch
    "StayFind": 0.02,  # A.11.3: a set piece at 2 % per happy stay of a Rare-or-better guest
    "StayPity": 40,  # ... guaranteed after 40 misses
}
# The players: (name, sessions a day, minutes a session); sessions evenly spaced.
EXP_PROFILES = [("daily 20 min (1 x 20 min)", 1, 20), ("2 h a day, 2 x 1 h", 2, 60),
                ("2 h a day, 4 x 30 min", 4, 30), ("2 h a day, 8 x 15 min", 8, 15)]
EXP_STAGES = [30, 60, 120, None]  # minutes of play; None = rebirth-ready (the run's end)
EXP_PAY_SWEEP = [1.5, 1.25, 1.0, 0.75, 0.5, 0.25]
EXP_GUARDS = [  # the offline rules the what-if mirrors
    ("src/shared/Economy.luau", "local t = math.clamp(seconds, 0, cap)"),
    ("src/shared/Economy.luau", "return math.floor(rate * Constants.Residents.OfflineFraction * t)"),
    ("src/server/ResidentService.luau", "if r.role == \"\" and r.campUntil <= os.time() then total += Economy.residentPay("),
    ("src/server/ResidentService.luau", "local away = os.time() - data.lastSeen"),
    ("src/server/ResidentService.luau", "local earned = Economy.offline(ResidentService.rate(player, data), away, cap)"),
    ("src/server/ResidentService.luau", "local cap = if data.passes.NightManager then Constants.Residents.NightManagerCap else Constants.Residents.OfflineCap"),
]


# ------------------------------------------------------- a Luau literal parser
class ParseError(RuntimeError):
    pass


def strip_comments(src: str) -> str:
    out, i, n = [], 0, len(src)
    while i < n:
        c = src[i]
        if c in "\"'`":
            j = i + 1
            while j < n and src[j] != c:
                j += 2 if src[j] == "\\" else 1
            out.append(src[i : j + 1])
            i = j + 1
        elif src.startswith("--", i):
            m = re.match(r"--\[(=*)\[", src[i:])
            if m:
                end = src.find("]" + m.group(1) + "]", i)
                i = n if end < 0 else end + len(m.group(1)) + 2
            else:
                end = src.find("\n", i)
                i = n if end < 0 else end
        else:
            out.append(c)
            i += 1
    return "".join(out)


TOKEN = re.compile(
    r"\s*(?:(?P<num>\d+\.?\d*(?:[eE][+-]?\d+)?)|(?P<str>\"[^\"]*\"|'[^']*'|`[^`]*`)"
    r"|(?P<name>[A-Za-z_][A-Za-z0-9_]*(?:\.[A-Za-z_][A-Za-z0-9_]*)*)|(?P<op>::|[{}\[\]=,;()*/+\-^]))"
)


class LuauParser:
    def __init__(self, text: str, pos: int, where: str):
        self.text, self.pos, self.where = text, pos, where
        self.peeked = None

    def _next(self):
        if self.peeked is not None:
            t, self.peeked = self.peeked, None
            return t
        m = TOKEN.match(self.text, self.pos)
        if not m or m.end() == self.pos:
            raise ParseError(f"{self.where}: cannot read at …{self.text[self.pos:self.pos+40]!r}")
        self.pos = m.end()
        kind = m.lastgroup
        return kind, m.group(kind)

    def peek(self):
        if self.peeked is None:
            self.peeked = self._next()
        return self.peeked

    def expect(self, op):
        k, v = self._next()
        if v != op:
            raise ParseError(f"{self.where}: expected {op!r}, got {v!r}")

    def expr(self):
        v = self.term()
        while self.peek()[1] in ("+", "-"):
            op = self._next()[1]
            r = self.term()
            v = v + r if op == "+" else v - r
        return v

    def term(self):
        v = self.power()
        while self.peek()[1] in ("*", "/"):
            op = self._next()[1]
            r = self.power()
            v = v * r if op == "*" else v / r
        return v

    def power(self):
        v = self.atom()
        if self.peek()[1] == "^":
            self._next()
            v = v ** self.power()
        return v

    def atom(self):
        k, v = self._next()
        if k == "num":
            return float(v) if any(c in v for c in ".eE") else int(v)
        if k == "str":
            return v[1:-1]
        if v == "{":
            return self.table()
        if v == "(":
            x = self.expr()
            self.expect(")")
            return x
        if v == "-":
            return -self.atom()
        if k == "name":
            if v == "true":
                return True
            if v == "false":
                return False
            if v == "nil":
                return None
            if v == "math.huge":
                return math.inf
            if self.peek()[1] == "(":  # a call such as Color3.fromRGB(...): kept as its name
                self._next()
                depth = 1
                while depth:
                    t = self._next()[1]
                    depth += {"(": 1, ")": -1}.get(t, 0)
                return ("call", v)
            if v.startswith("Enum."):
                return ("enum", v)
            if re.fullmatch(r"[A-Z]\.\w+", v):  # a constant through a one-letter alias (M.MonthlyPay): kept as its name
                return ("ref", v)
            raise ParseError(f"{self.where}: a name the model cannot evaluate: {v}")
        raise ParseError(f"{self.where}: unexpected {v!r}")

    def table(self):
        arr, rec = [], {}
        while True:
            k, v = self.peek()
            if v == "}":
                self._next()
                break
            if k == "name" and "." not in v:
                save = (self.pos, self.peeked)
                self._next()
                if self.peek()[1] == "=":
                    self._next()
                    rec[v] = self.expr()
                else:
                    self.pos, self.peeked = save
                    arr.append(self.expr())
            elif v == "[":
                self._next()
                key = self.expr()
                self.expect("]")
                self.expect("=")
                rec[key] = self.expr()
            else:
                arr.append(self.expr())
            if self.peek()[1] in (",", ";"):
                self._next()
        if arr and rec:
            raise ParseError(f"{self.where}: mixed table")
        return rec if rec else arr


def read(rel: str) -> str:
    path = os.path.join(ROOT, rel)
    with open(path, encoding="utf-8") as f:
        return f.read()


def assignment(rel: str, lhs_pattern: str):
    src = strip_comments(read(rel))
    m = re.search(lhs_pattern + r"\s*=\s*", src, re.M)
    if not m:
        raise ParseError(f"{rel}: no assignment matching {lhs_pattern!r}")
    return LuauParser(src, m.end(), f"{rel} {lhs_pattern}").expr()


def need(d: dict, key: str, where: str):
    if key not in d:
        raise ParseError(f"{where}: missing key {key!r}")
    return d[key]


# The formulas the model mirrors, as their source lines (whitespace ignored).
FORMULA_GUARDS = [
    ("src/shared/Bus.luau", "math.clamp(math.ceil(B.VacantShare * vacant), B.MinPerPlayer * p, B.MaxPerPlayer * p)"),
    ("src/server/BusService.luau", "while #list > math.max(want, guaranteed) do"),
    ("src/server/BusService.luau", "local n = math.min(Constants.Tutorial.CommonsPerBus, slot - guaranteed)"),
    ("src/server/BusService.luau", "list[slot] = { species = id, mutation = nil, tutorialFor = player }"),
    ("src/server/TutorialService.luau", "and stat(data, \"tutorialCommonBuses\") < Constants.Tutorial.CommonBuses"),
    ("src/shared/Scoring.luau", "if c.tutorial and rarity == \"Common\" then"),
    ("src/shared/Rating.luau", "local roomsNeed = math.max(1, i.rooms / R.RoomsPerStaff)"),
    ("src/shared/Rating.luau", "return if need > 0 then math.clamp(efficiency / need, 0, 1) else 0"),
    ("src/shared/Rating.luau", "R.CleanPerOnTime * math.clamp(i.onTimeShare or 0, 0, 1)"),
    ("src/server/HotelService.luau", "if room.dirtySince and now - room.dirtySince > Constants.Rating.CleanOnTime then"),
    ("src/shared/Furnish.luau", "return if d then math.floor(d.cost * E.PointsPerCash) else 0"),
    ("src/server/GuestService.luau", "g.requestAt = now + stay * (0.25 + 0.5 * rng:NextNumber())"),
    ("src/server/GuestService.luau", "g.payRate * S.RequestTipSeconds"),
    ("src/shared/Economy.luau", "* Constants.Residents.EarnFraction"),
    ("src/shared/Economy.luau", "return Economy.speciesPay(speciesId) * Economy.tierPay(tier) * Mutations.payMultiplier(size, mutation) * Economy.milestoneMultiplier(typeCount) * multiplier"),
    ("src/shared/Stay.luau", "math.floor(payRate * stay * (satisfaction / 100) * S.TipFraction)"),
    ("src/shared/Stay.luau", "math.clamp(1 + math.floor(satisfaction / 25), 1, 5)"),
    ("src/shared/Stay.luau", "math.min(S.SatisfactionAmenityMax, S.SatisfactionPerAmenity * i.amenities)"),
    ("src/shared/Stay.luau", "+ S.SatisfactionPerTier * (i.tier - 1)"),
    # Built rooms (GDD 5.4, A.12, 2026-10-21): what a type needs, its bars, their bonuses, Comfort
    ("src/shared/Rooms.luau", "fullCells = minCells * R.FullSizeFactor,"),
    ("src/shared/Rooms.luau", "furnitureTarget = math.max(p.cost * R.FurnitureTargetFactor, R.FurnitureTargetMin),"),
    ("src/shared/Rooms.luau", "return R.DecorTargetPer4Cells * cells / 4"),
    ("src/shared/Rooms.luau", "if d.furniture and d.keyFor and table.find(d.keyFor, typeId) then"),
    ("src/shared/Rooms.luau", "local minCells = p.w * p.d"),
    ("src/shared/Rooms.luau", "then clamp01((a.size - req.minCells) / span)"),
    ("src/shared/Rooms.luau", "furniture = if req.furnitureTarget > 0 then clamp01(fp / req.furnitureTarget) else 1,"),
    ("src/shared/Rooms.luau", "decor = if decorTarget > 0 then clamp01(dp / decorTarget) else 0,"),
    ("src/shared/Rooms.luau", "table.insert(if row and row.furniture then out.furniture else out.decor, d)"),
    ("src/shared/Rooms.luau", "pay = (1 + R.SizePay * s) * (1 + R.FurniturePay * f),"),
    ("src/shared/Rooms.luau", "stay = 1 + R.SizeStay * s,"),
    ("src/shared/Rooms.luau", "satisfaction = R.FurnitureSatisfaction * f + R.DecorSatisfaction * d,"),
    ("src/shared/Rooms.luau", "friendship = 1 + R.DecorFriendship * d,"),
    ("src/shared/Rooms.luau", "sum += (clamp01(b.size) + clamp01(b.furniture) + clamp01(b.decor)) / 3 * R.ComfortPerRoom"),
    ("src/shared/Rooms.luau", "return math.min(sum, R.ComfortRoomsCap)"),
    ("src/shared/Rooms.luau", "if #keyPieces(world, roomId) == 0 then"),
    ("src/shared/Rooms.luau", "if a.size < req.minCells then"),
    ("src/shared/Rating.luau", "local comfort = Rooms.comfortPoints(i.roomBars) + 40 * i.prefsShare"),
    # ... how the server applies them
    ("src/server/GuestService.luau", "g.tier = 1"),
    ("src/server/GuestService.luau", "g.stayMult = if bonus then bonus.stay else 1"),
    ("src/server/GuestService.luau", "g.satBonus = if bonus then bonus.satisfaction else 0"),
    ("src/server/GuestService.luau", "g.friendshipMult = if bonus then bonus.friendship else 1"),
    ("src/server/GuestService.luau", "local typeCount = HotelService.readyOfType(player, data, rec.type)"),
    ("src/server/GuestService.luau", "g.payRate = Economy.guestPay( g.species, 1, g.mutation, typeCount, Income.multiplier(player), g.size ) * (if bonus then bonus.pay else 1)"),
    ("src/server/GuestService.luau", "deskWait = g.waited, }) + g.satBonus, -- the Furniture and Decor bars (A.12) 0, 100 )"),
    ("src/server/GuestService.luau", "local stay = Constants.Rarity[sp.rarity].stay * g.stayMult"),
    ("src/server/ResidentService.luau", "local gain = g.friendshipMult or 1"),
    ("src/server/ResidentService.luau", "local now = before + gain"),
    ("src/server/HotelService.luau", "if p and ok then table.insert(bars, Rooms.bars(w, id)) end"),
    ("src/server/HotelService.luau", "for _ in data.decor do decor += 1 end"),
    ("src/server/HotelService.luau", "if not best or matched > best.prefsMatched then"),
    # ... and what building costs: walls, doors, furniture and decor at their price; a room's type is free
    ("src/server/BuildService.luau", "if not PlayerData.spend(player, R.WallCost) then"),
    ("src/server/BuildService.luau", "local cost = R.DoorCost + (if rec then 0 else R.WallCost)"),
    ("src/server/BuildService.luau", "local cost = if d.location == 0 and not d.always and not d.furniture then 0 else d.cost"),
    ("src/server/BuildService.luau", "data.rooms[newId(data)] = { type = typeId, floor = floor, hx = hx, hz = hz, finish = \"\" }"),
    # a new hotel's start room, and the tutorial's steps and free key piece
    ("src/server/PlayerData.luau", "if p.kind == \"Room\" and p.location == data.location and p.unlock == nil then"),
    ("src/server/PlayerData.luau", "item = req.keys[1] or item"),
    ("src/server/PlayerData.luau", "{ item = item, floor = 1, x = f.x, z = f.z, r = f.r, room = \"\", paid = 0 }"),
    ("src/server/TutorialService.luau", "\"CheckIn\", \"Collect\", \"SecondRoom\", \"Furnish\", \"Bus\", \"MoveIn\", \"Goal\", \"Clean\", \"Staff\", \"Preview\", \"Done\","),
    ("src/server/TutorialService.luau", "return readyRooms(player, data) >= 2"),
    ("src/server/TutorialService.luau", "if s == \"CheckIn\" and not slimeSent[player] then"),
    ("src/server/BuildService.luau", "local voucher = voucherFor(data, d)"),
    ("src/shared/Rating.luau", "math.clamp(100 - i.meanWait * R.ServiceWaitPerPoint, 0, 100) * 0.6 + 40 * i.requestShare"),
    ("src/shared/Rating.luau", "100 * (1 - i.dirtyRooms / i.rooms)"),
    ("src/shared/Rating.luau", "math.min(100, i.amenities * R.FunPerAmenity + i.entertainers * R.FunPerEntertainer)"),
    ("src/shared/Rating.luau", "math.min(100, i.decor * R.StylePerDecor + i.roomTypes * R.StylePerRoomType)"),
    ("src/shared/Rating.luau", "R.Min + (R.Max - R.Min) * (mean / 100) ^ R.CategoryCurve"),
    ("src/shared/Rating.luau", "stars = (fromCategories + sum / #reviews) / 2"),
    ("src/server/ResidentService.luau", "then Constants.Residents.TutorialFriendship"),
    ("src/server/ResidentService.luau", "local early = rng:NextNumber() < Constants.Rarity[sp.rarity].moveInChance"),
    ("src/server/TutorialService.luau", "data.stats.voucher_CoffinSuite = 1"),
    ("src/server/TutorialService.luau", "BuildService.tutorialTiles(player)"),
    ("src/server/BuildService.luau", "local S, T = G.StartTiles, G.TutorialTiles"),
    ("src/server/PlayerData.luau", "data.tiles = startTiles()"),
    # tiles, floors and the cap (§5.4, §6.4)
    ("src/shared/Economy.luau", "math.floor(E.TileCost * E.TileFloorFactor ^ (floor - 1) * E.TileGrowth ^ bought + 0.5)"),
    ("src/shared/Grid.luau", "if floor > 1 and not tiles[fkey(floor - 1, x, z)] then"),
    ("src/shared/Chain.luau", "return math.min(C.StartFloorCap + math.ceil(math.max(rebirths, 0) / 2), C.FloorCapMax)"),
    ("src/server/BuildService.luau", "return Chain.floorCap(data.rebirths) + (if data.passes.ExtraFloor then 1 else 0)"),
    ("src/server/BuildService.luau", "if next > BuildService.maxFloors(data) then"),
    # pay by location, pieces by location
    ("src/shared/Economy.luau", "return E.BasePay * E.LocationPayMultiplier ^ (sp.location - 1) * Constants.Rarity[sp.rarity].pay"),
    ("src/shared/Unlocks.luau", "if piece.location ~= 0 and piece.location ~= c.location then"),
    ("src/shared/Pieces.luau", "return d.always == true or d.location == location or (d.furniture == true and d.location == 0) or unlocked[`Decor_{d.id}`] == true"),
    ("src/shared/Bus.luau", "if sp.rarity == rarity and locations[sp.location] then"),
    ("src/server/HotelService.luau", "elseif p and ok and p.kind == \"Amenity\" then amenities += 1"),
    # the chain (§6.4)
    ("src/server/ChainService.luau", "if Chain.nextToOpen(opened) ~= location then"),
    ("src/server/ChainService.luau", "local cost = Chain.openCost(location) or 0"),
    ("src/server/ChainService.luau", "PlayerData.resetHotel(data) -- a new hotel: the start square and the desk (§5.4) data.reviews = {} data.rate = 0"),
    ("src/server/ChainService.luau", "rating = HotelService.rating(player), rate = data.rate,"),
    ("src/server/ChainService.luau", "data.rate = Chain.updateRate(data.rate, GuestService.income(player) - s.income, dt)"),
    ("src/server/ChainService.luau", "pay += Chain.background(rec.rate, dt)"),
    ("src/shared/Chain.luau", "return rate * C.BackgroundShare * seconds"),
    ("src/shared/Chain.luau", "local a = 1 - math.exp(-seconds / C.RateWindow)"),
    ("src/shared/Chain.luau", "return rate + (math.max(earned, 0) / seconds - rate) * a"),
    ("src/shared/Chain.luau", "if r == nil or r < C.RebirthRating then"),
    ("src/server/ProgressionService.luau", "local ratings = ChainService.ratings(player, data)"),
    ("src/server/GuestService.luau", "countIncome(player, tip)"),
    ("src/server/GuestService.luau", "countIncome(player, bonus)"),
    ("src/server/GuestService.luau", "countIncome(player, amount)"),
    ("src/server/ResidentService.luau", "return (r.hotel or data.location) == data.location"),
    # Travel clears the desk queue only: HotelService's samples (waits, preference shares, requests, cleanings) carry over
    ("src/server/ChainService.luau", "if hotel then table.clear(hotel.queue) end"),
    ("src/server/HotelService.luau", "waits = {}, prefsShares = {}, requestsAsked = 0, requestsDone = 0, cleanTimes = {},"),
    ("src/server/TutorialService.luau", "{ booked = player, happyFloor = Constants.Stay.Happy }"),
    ("src/server/TutorialService.luau", "and busesSince >= 2"),
    ("src/server/ResidentService.luau", "local threshold = if g.tutorialFriend"),
    ("src/server/BookService.luau", "math.floor(Economy.speciesPay(speciesId) * Constants.Book.SpeciesFoundPaySeconds)"),
    ("src/server/BusService.luau", "l.nextList, l.nextGuaranteed = draw(street, busIndex + 1, now, now + interval)"),  # each street's bus a bus ahead (one world, 2026-10-21)
]


def check_formulas():
    norm = lambda s: re.sub(r"\s+", "", s)
    cache = {}
    bad = []
    for rel, line in FORMULA_GUARDS:
        if rel not in cache:
            cache[rel] = norm(read(rel))
        if norm(line) not in cache[rel]:
            bad.append(f"  {rel}: {line}")
    if bad:
        raise ParseError(
            "the game's formulas changed; update tools/balance_model.py to match:\n" + "\n".join(bad)
        )


def load_game() -> dict:
    check_formulas()
    C = "src/shared/Constants.luau"
    G = {}
    for key in ["Rarity", "Economy", "Bus", "Scoring", "Stay", "Tutorial", "Rating", "Residents", "Staff", "Book", "Chain", "Grid", "Rooms"]:
        G[key] = assignment(C, rf"^Constants\.{key}")
        if not isinstance(G[key], dict):
            raise ParseError(f"{C}: Constants.{key} is not a table")
    for r in ["Common", "Uncommon", "Rare", "Epic", "Legendary", "Mythic"]:
        for k in ["pay", "stay", "friendship", "weight", "moveInChance"]:
            need(need(G["Rarity"], r, C), k, f"{C} Rarity.{r}")
    for sect, keys in {
        "Economy": ["StartCash", "BasePay", "LocationPayMultiplier", "PointsPerCash",
                    "TileCost", "TileGrowth", "TileFloorFactor", "Milestones", "FloorCosts"],
        "Chain": ["Locations", "RebirthRating", "OpenCost", "BackgroundShare", "RateWindow", "StartFloorCap", "FloorCapMax"],
        "Grid": ["StartTiles", "TutorialTiles", "Cells", "Squares"],
        "Rooms": ["HalfCells", "WallCost", "DoorCost", "FullSizeFactor", "FurnitureTargetFactor", "FurnitureTargetMin", "DecorTargetPer4Cells",
                  "SizePay", "SizeStay", "FurniturePay", "FurnitureSatisfaction", "DecorSatisfaction", "DecorFriendship",
                  "ComfortPerRoom", "ComfortRoomsCap", "Start"],
        "Bus": ["Interval", "EpicEvery", "LegendaryEvery", "MythicEvery", "VacantShare", "MinPerPlayer", "MaxPerPlayer", "FirstBusDelay", "BrowseTime", "StepOff"],
        "Stay": ["SatisfactionBase", "SatisfactionPerPreference", "SatisfactionPerTier", "SatisfactionPerAmenity", "SatisfactionAmenityMax", "SatisfactionRequestPlayer", "SatisfactionRequestStaff", "SatisfactionRequestMissed", "WaitFree", "WaitPerPoint", "WaitMaxPenalty", "Happy", "TipFraction", "RequestWindow", "RequestTipSeconds", "CleanHold", "ReviewsKept"],
        "Tutorial": ["FirstGuestDelay", "CommonBuses", "CommonsPerBus"],
        "Scoring": ["TutorialBoost"],
        "Rating": ["Min", "Max", "FunPerAmenity", "StylePerDecor", "StylePerRoomType",
                   "ServicePerDeskCoverage", "ServicePerRoomServiceCoverage", "CleanPerHousekeepingCoverage",
                   "CleanPerOnTime", "DesksCovered", "RoomsPerStaff", "CleanOnTime", "CleanSampleSize", "ServiceWaitPerPoint", "ServiceSampleSize", "CategoryCurve"],
        "Residents": ["EarnFraction", "WingCapacity", "TutorialFriendship"],
        "Staff": ["BestEfficiency", "OtherEfficiency", "RoomServiceDelay"],
        "Book": ["SpeciesFoundPaySeconds"],
    }.items():
        for k in keys:
            need(G[sect], k, f"{C} Constants.{sect}")
    G["LaneHalfLength"] = need(assignment(C, r"^Constants\.Street"), "LaneHalfLength", C)
    for loc_id in range(2, G["Chain"]["Locations"] + 1):
        need(G["Chain"]["OpenCost"], loc_id, f"{C} Constants.Chain.OpenCost")
    tick = re.search(r"^local TICK = (\d+)", read("src/server/ChainService.luau"), re.M)
    if not tick:
        raise ParseError("src/server/ChainService.luau: no `local TICK = <seconds>`")
    G["ChainTick"] = int(tick.group(1))

    pieces = assignment("src/shared/Pieces.luau", r"^local pieces\s*:\s*\{\s*Piece\s*\}")
    decor = assignment("src/shared/Pieces.luau", r"^local decor\s*:\s*\{\s*Decor\s*\}")
    species = assignment("src/shared/Species.luau", r"^local rows\s*:\s*\{\s*Species\s*\}")
    muts = assignment("src/shared/Mutations.luau", r"^local rows\s*:\s*\{\s*Mutation\s*\}")
    G["DecorSlots"] = DECOR_MATCH_SLOTS
    # A size and a look are rolled apart, their pay ADDED (Mutations.payMultiplier, A.11.5);
    # the month's or season's own row (`event`) is not simulated.
    G["Mutations"] = [(m["id"], m["chance"], m["pay"], m.get("group", "Look")) for m in muts
                      if m.get("chance", 0) > 0 and not m.get("event")]
    G["AllSpecies"] = {s["id"]: s for s in species}
    G["AllDecor"] = {d["id"]: d for d in decor}
    start = G["Rooms"]["Start"]
    if not isinstance(start, dict) or not start.get("type") or not start.get("furniture"):
        raise ParseError(f"{C}: Constants.Rooms.Start has no type or furniture")
    goal = re.search(r'HotelService\.vacantFor\(player, "(\w+)"\)', read("src/server/TutorialService.luau"))
    if not goal:
        raise ParseError("src/server/TutorialService.luau: no booked tutorial guest (HotelService.vacantFor(player, \"<id>\"))")
    G["RebirthResident"] = goal.group(1)  # the tutorial's booked Legendary (no longer a rebirth condition)
    # One view of the game per location: its pieces, decor and species (Unlocks.met, Pieces.decorHere, Bus.pool).
    G["Loc"] = {}
    for L in range(1, G["Chain"]["Locations"] + 1):
        g = dict(G)
        g["Location"] = L
        g["Pieces"] = {p["id"]: p for p in pieces if p.get("location") == L}
        # Pieces.decorHere: the location's own, `always`, and location-0 furniture (event decor not simulated)
        g["Decor"] = {d["id"]: d for d in decor if d.get("cost", 0) > 0 and (
            d.get("location") == L or (d.get("location") == 0 and (d.get("always") or d.get("furniture"))))}
        g["Species"] = {s["id"]: s for s in species if s.get("location") == L}
        if not g["Species"]:
            raise ParseError(f"Species.luau: no species of location {L}")
        for sid, s in g["Species"].items():
            if s["room"] not in g["Pieces"]:
                raise ParseError(f"Species {sid}: room {s['room']} is not a location-{L} piece")
        firsts = [pid for pid, p in g["Pieces"].items() if p["kind"] == "Room" and not p.get("unlock")]
        if not firsts:
            raise ParseError(f"Pieces.luau: location {L} has no room without an unlock (its first room)")
        # Rooms.requirement's keys (every furniture row naming the type, in Pieces order); the player can place only those here
        g["Keys"] = {}
        for pid, p in g["Pieces"].items():
            if p["kind"] not in ("Room", "Amenity"):
                continue
            keys = [d["id"] for d in decor if d.get("furniture") and pid in (d.get("keyFor") or [])]
            here = [k for k in keys if k in g["Decor"]]
            if not here:
                raise ParseError(f"Pieces.luau: {pid} has no key furniture placeable at location {L}")
            g["Keys"][pid] = (keys, min(here, key=lambda k: g["Decor"][k]["cost"]))
        # PlayerData.startRoom: Start.type at its location, else the first room type with no unlock (Pieces order)
        stype = start["type"] if start["type"] in g["Pieces"] else firsts[0]
        item = start["furniture"][0]["item"]
        sd = G["AllDecor"].get(item)
        if sd and start["type"] in (sd.get("keyFor") or []) and item not in g["Keys"][stype][0]:
            item = g["Keys"][stype][0][0]
        g["StartRoom"] = (stype, item)
        G["Loc"][L] = g
    if "StandardRoom" not in G["Loc"][1]["Pieces"] or G["AllSpecies"][G["RebirthResident"]]["room"] not in G["Loc"][1]["Pieces"]:
        raise ParseError("Pieces: StandardRoom / the tutorial guest's room missing at location 1")
    return G


def floor_cap(G, rebirths=0):
    """Chain.floorCap: the floors a hotel may have after `rebirths` rebirths (before the pass)."""
    C = G["Chain"]
    return min(C["StartFloorCap"] + math.ceil(max(rebirths, 0) / 2), C["FloorCapMax"])


# ------------------------------------------------------------- the game rules
class Rules:
    def __init__(self, G):
        self.G = G
        self.E, self.S, self.R, self.RM = G["Economy"], G["Stay"], G["Rating"], G["Rooms"]

    # ---- built rooms (Rooms.requirement, bars, bonuses, comfortPoints)
    def min_cells(self, pid):
        p = self.G["Pieces"][pid]
        return p["w"] * p["d"]

    def full_cells(self, pid):
        return self.min_cells(pid) * self.RM["FullSizeFactor"]

    def furniture_target(self, pid):
        return max(self.G["Pieces"][pid]["cost"] * self.RM["FurnitureTargetFactor"], self.RM["FurnitureTargetMin"])

    def decor_target(self, cells):
        return self.RM["DecorTargetPer4Cells"] * cells / 4

    def points(self, item):
        """Furnish.points: a piece's points from its price."""
        return math.floor(self.G["Decor"][item]["cost"] * self.E["PointsPerCash"])

    def bars(self, pid, cells, fp, dp):
        lo, hi = self.min_cells(pid), self.full_cells(pid)
        span = hi - lo
        c01 = lambda v: max(0.0, min(1.0, v))
        size = c01((cells - lo) / span) if span > 0 else (1 if cells >= lo else 0)
        ft = self.furniture_target(pid)
        dt = self.decor_target(cells)
        return (size, c01(fp / ft) if ft > 0 else 1, c01(dp / dt) if dt > 0 else 0)

    def bonuses(self, bars):
        """Rooms.bonuses: (pay, stay, satisfaction, friendship)."""
        R = self.RM
        s, f, d = (max(0.0, min(1.0, b)) for b in bars)
        return ((1 + R["SizePay"] * s) * (1 + R["FurniturePay"] * f), 1 + R["SizeStay"] * s,
                R["FurnitureSatisfaction"] * f + R["DecorSatisfaction"] * d, 1 + R["DecorFriendship"] * d)

    def comfort_points(self, ready):
        total = sum((max(0, min(1, s)) + max(0, min(1, f)) + max(0, min(1, d))) / 3 * self.RM["ComfortPerRoom"] for s, f, d in ready)
        return min(total, self.RM["ComfortRoomsCap"])

    def shape(self, pid, cells):
        """ASSUMPTION: the most compact a x b rectangle of `cells` (a <= b, a at least the type's shorter side)."""
        p = self.G["Pieces"][pid]
        lo = min(p["w"], p["d"])
        for a in range(int(math.isqrt(cells)), 0, -1):
            if cells % a == 0 and a >= lo:
                return a, cells // a
        return lo, math.ceil(cells / lo)

    def walls_cost(self, pid, cells):
        """WALL_SHARE of the rectangle's perimeter in half edges at WallCost, one of them a door (DoorCost + its WallCost)."""
        a, b = self.shape(pid, cells)
        half_edges = max(1, round(WALL_SHARE * 2 * (a + b) * self.RM["HalfCells"]))
        return half_edges * self.RM["WallCost"] + self.RM["DoorCost"]

    def key_cost(self, pid):
        return self.G["Decor"][self.G["Keys"][pid][1]]["cost"]

    def build_cost(self, pid, cells, free_key=False):
        """Walls, the door and the cheapest key piece placeable here; making the area a room is free."""
        return self.walls_cost(pid, cells) + (0 if free_key else self.key_cost(pid))

    def milestone(self, count):
        m = 1
        for at in self.E["Milestones"]:
            if count >= at:
                m *= 2
        return m

    def species_pay(self, sid):
        sp = self.G["AllSpecies"][sid]
        return self.E["BasePay"] * self.E["LocationPayMultiplier"] ** (sp["location"] - 1) * self.G["Rarity"][sp["rarity"]]["pay"]

    def tile_cost(self, floor, bought):
        E = self.E
        return math.floor(E["TileCost"] * E["TileFloorFactor"] ** (floor - 1) * E["TileGrowth"] ** bought + 0.5)

    def stay_len(self, sid):
        return self.G["Rarity"][self.G["AllSpecies"][sid]["rarity"]]["stay"]

    def wait_penalty(self, s):
        over = max(0, s - self.S["WaitFree"])
        return min(self.S["WaitMaxPenalty"], math.floor(over / self.S["WaitPerPoint"]))

    def satisfaction(self, prefs, amen, rp, rs, rm, wait, sat_bonus):
        """Stay.satisfaction (the tier always 1: its term adds 0), clamped, + the bars' bonus, clamped (GuestService.checkout)."""
        S = self.S
        tier = 1
        s = (S["SatisfactionBase"] + S["SatisfactionPerPreference"] * prefs + S["SatisfactionPerTier"] * (tier - 1)
             + min(S["SatisfactionAmenityMax"], S["SatisfactionPerAmenity"] * amen)
             + S["SatisfactionRequestPlayer"] * rp + S["SatisfactionRequestStaff"] * rs
             + S["SatisfactionRequestMissed"] * rm - self.wait_penalty(wait))
        return max(0, min(100, max(0, min(100, s)) + sat_bonus))

    def tip(self, rate, stay, sat):
        return math.floor(rate * stay * (sat / 100) * self.S["TipFraction"])

    def review(self, sat):
        return max(1, min(5, 1 + math.floor(sat / 25)))

    def categories(self, ready_bars, prefs_share, mean_wait, checkins, req_share, rooms, dirty, amen, decor, types,
                   desk=0.0, room_service=0.0, housekeeping=0.0, on_time=0.0):
        R = self.R
        comfort = self.comfort_points(ready_bars) + 40 * prefs_share
        service = (max(0, min(100, 100 - mean_wait * R["ServiceWaitPerPoint"])) * 0.6 + 40 * req_share) if checkins > 0 else 0
        clean = 100 * (1 - dirty / rooms) if rooms > 0 else 0
        # staff coverage and rooms cleaned on time (Rating.categories): points on top
        cover = lambda eff, need: max(0, min(1, eff / need)) if need > 0 else 0
        need = max(1, rooms / R["RoomsPerStaff"])
        if checkins > 0:
            service += R["ServicePerDeskCoverage"] * cover(desk, R["DesksCovered"]) + R["ServicePerRoomServiceCoverage"] * cover(room_service, need)
        if rooms > 0:
            clean += R["CleanPerHousekeepingCoverage"] * cover(housekeeping, need) + R["CleanPerOnTime"] * max(0, min(1, on_time))
        fun = min(100, amen * R["FunPerAmenity"])
        style = min(100, decor * R["StylePerDecor"] + types * R["StylePerRoomType"])
        return [max(0, min(100, comfort)), max(0, min(100, service)), max(0, min(100, clean)), fun, style]

    def stars(self, cats, reviews):
        R = self.R
        mean = sum(cats) / 5
        fc = R["Min"] + (R["Max"] - R["Min"]) * (mean / 100) ** R["CategoryCurve"]
        s = (fc + sum(reviews) / len(reviews)) / 2 if reviews else fc
        return max(R["Min"], min(R["Max"], math.floor(s * 2 + 0.5) / 2))


# --------------------------------------------------------------- the simulation
@dataclass
class Room:
    """A built room or amenity (Rooms): its cells, and the furniture and decor standing in it."""
    id: int
    type: str
    floor: int
    cells: int
    items: list = field(default_factory=list)  # every furniture and decor piece in it, the key piece first
    fp: int = 0  # furniture points
    dp: int = 0  # decor points
    squares: int = 0  # squares its pieces cover
    state: str = "Vacant"  # Vacant | Reserved | Occupied | Dirty
    dirty_since: int = 0
    occ: float = 0.5  # EMA of not-vacant


@dataclass
class Guest:
    sid: str
    mut: str | None
    mut_pay: float
    source: str  # Bus | Tutorial
    room: Room
    state: str  # ToHotel | Queued | ToRoom | InRoom
    at: int  # when the current state ends
    desk_since: int = 0
    waited: int = 0
    prefs: int = 0
    amen: int = 0
    stay_mult: float = 1.0  # the room's bonuses (Rooms.bonuses), fixed at check-in
    sat_bonus: float = 0.0
    fr_mult: float = 1.0
    rate: float = 0.0
    stay_end: int = 0
    req_at: int | None = None
    req_open: int | None = None
    req_player_at: int | None = None
    rp: int = 0
    rs: int = 0
    rm: int = 0
    happy_floor: int | None = None


PLAN_CACHE: dict = {}
FILL_CACHE: dict = {}


class Sim:
    def __init__(self, G, seed, tutorial=True, hours=6.0):
        self.G0 = G
        self.seed = seed
        self.rng = random.Random(seed)
        self.tutorial = tutorial
        self.T = int(hours * 3600)
        E = G["Economy"]
        # the player's, kept across the chain
        self.cash = E["StartCash"]
        self.till = 0.0
        self.run_cash = 0.0
        self.floor_cap_max = floor_cap(G, 0)
        self.metrics_checkins = []  # (t, rarity) of every check-in
        self.occ_log = []  # per minute: (t, room-seconds, paying room-seconds, not-vacant room-seconds)
        self._occ_pay = self._occ_busy = self._occ_rooms = 0
        self.tut_goal_bus = None
        self.next_id = 1
        self.unlocked: set = set()
        self.tut_unlocked: set = set()
        self.vouchers: dict = {}
        self.residents: list[dict] = []
        self.friendship: dict = {}
        self.book: set = set()
        self.tut_common_buses = 0
        self.bus_index = 0
        self.next_bus = G["Bus"]["FirstBusDelay"]
        self.wall0 = self.rng.uniform(0, 7200)  # wall clock phase (s) at join
        self.last_bus_wall = self.wall0
        # tutorial
        self.tstep = "CheckIn" if tutorial else "Done"  # TutorialService.Steps[1]: the start room stands already
        self.tstep_since = 0
        self.slime_at = None
        self.tut_goal = False
        self.tut_vampire_sent = False
        self.collects = self.checkins = self.cleaned = 0
        # the chain (ChainService): hotels put away, by location: {"rate", "rating", "left"}
        self.chain: dict = {}
        self.guest_income = 0.0  # GuestService.income: what the played hotel's guests paid
        self.sample_at, self.sample_income = 0, 0.0
        self.bg_paid = 0.0
        # metrics
        self.events: dict = {}
        self.at_event: dict = {}  # event -> a snapshot (cash, income ...)
        self.purchases: list = []  # (t, kind, what, cost, income_per_min, meaningful, location)
        self.timeline: list = []  # (t, income/min, rating, cash, runCash, rooms, cats, location, background/min)
        self.cat_first: dict = {}  # (location, what) -> first t a category reached 95 / reviews 4.5
        self.rebirth_ready = None
        self.wing_log: list = []  # --expeditions: per minute (t, location, the Wing's rates $/s, income $/s)
        self.rare_happy: dict = {}  # --expeditions: location -> happy stays of Rare-or-better guests
        self.start_hotel(1, 0)

    def start_hotel(self, loc, t):
        """PlayerData.resetHotel and ChainService.takeOut for a new hotel: the start square, the desk, no reviews, rate 0."""
        G = self.G0
        self.loc = loc
        self.G = G["Loc"][loc]
        self.rules = Rules(self.G)
        st = G["Grid"]["StartTiles"]
        self.floors = 1
        self.tiles = {1: st["w"] * st["d"]}
        self.bought = {1: 0}
        self.rooms: list[Room] = []
        self.amenities: list[Room] = []
        self.guests: list[Guest] = []
        self.pending_bus = []
        self.booked = []  # tutorial guests riding the next bus to this hotel
        self.reviews: deque = deque(maxlen=G["Stay"]["ReviewsKept"])  # data.reviews: each hotel its own
        self.sats: deque = deque(maxlen=G["Stay"]["ReviewsKept"])  # the satisfaction behind them (a metric)
        if loc == 1:
            # HotelService's per-player samples (made once, on load; Travel does not clear them, so a new
            # hotel's rating starts from the last hotel's desk waits, preference shares, requests and cleanings)
            n = G["Rating"]["ServiceSampleSize"]
            self.waits, self.prefs_shares = deque(maxlen=n), deque(maxlen=n)
            self.req_asked = self.req_done = 0
            self.clean_times: deque = deque(maxlen=G["Rating"]["CleanSampleSize"])
        self.rating = 1.0
        self.cats = [0] * 5
        self.observed_pay: dict = {}  # room type -> deque of base pay of its guests
        self.income_log: deque = deque(maxlen=120)  # $ earned per second (till and background)
        self.this_second = 0.0
        self.rate = 0.0  # data.rate: the played hotel's measured guest income ($/s, EMA)
        self.sample_at, self.sample_income = t, self.guest_income
        self.staff_assigned_at = None
        self.loc_started = t
        # PlayerData.startRoom: one built room, free (Constants.Rooms.Start: an L of START_CELLS cells, its key piece)
        stype, item = self.G["StartRoom"]
        if self.rules.min_cells(stype) > START_CELLS:
            raise ParseError(f"the start room ({START_CELLS} cells) is smaller than {stype}'s minimum: update the model")
        r = Room(self.next_id, stype, 1, START_CELLS)
        self.next_id += 1
        self.add_piece(r, item)
        self.rooms.append(r)

    def open_next(self, t):
        """ChainService.travel to the next location not opened: pay, put this hotel away, start the new one."""
        nxt = self.loc + 1
        cost = self.G0["Chain"]["OpenCost"][nxt]
        if self.cash < cost:
            return False
        self.snap(f"leave_{self.loc}", t)  # the cash before the price
        self.cash -= cost
        self.purchases.append((t, "open", nxt, cost, self.income_rate() * 60, True, self.loc))
        self.chain[self.loc] = {"rate": self.rate, "rating": self.rating, "left": t}
        self.mark(f"open_{nxt}", t)
        self.start_hotel(nxt, t)
        self.snap(f"open_{nxt}", t)
        return True

    def chain_tick(self, t):
        """ChainService.tick: measure the played hotel's rate; pay the hotels put away."""
        C = self.G0["Chain"]
        dt = t - self.sample_at
        if dt <= 0:
            return
        earned = self.guest_income - self.sample_income
        a = 1 - math.exp(-dt / C["RateWindow"])
        self.rate = self.rate + (max(earned, 0) / dt - self.rate) * a
        pay = 0.0
        for rec in self.chain.values():
            if rec["rate"] > 0:
                pay += rec["rate"] * C["BackgroundShare"] * dt
        pay = math.floor(pay)
        self.sample_at, self.sample_income = t, self.guest_income
        if pay > 0:
            self.cash += pay
            self.run_cash += pay
            self.bg_paid += pay
            self.this_second += pay

    def background_rate(self):
        return sum(r["rate"] for r in self.chain.values()) * self.G0["Chain"]["BackgroundShare"]

    def snap(self, key, t):
        if key not in self.at_event:
            self.at_event[key] = {"t": t, "cash": self.cash, "run_cash": self.run_cash, "inc": self.income_rate() * 60,
                                  "bg": self.background_rate() * 60, "rate": self.rate * 60, "rooms": len(self.rooms),
                                  "floors": self.floors, "tiles": dict(self.tiles), "cats": list(self.cats),
                                  "rating": self.rating, "reviews": statistics.fmean(self.reviews) if self.reviews else 0,
                                  "bars": [statistics.fmean(self.room_bars(r)[i] for r in self.rooms) if self.rooms else 0 for i in range(3)],
                                  "cells": statistics.fmean(r.cells / self.rules.min_cells(r.type) for r in self.rooms) if self.rooms else 0,
                                  "sat": statistics.fmean(self.sats) if self.sats else 0}

    # ---- helpers
    def mark(self, key, t):
        if key not in self.events:
            self.events[key] = t

    def income_rate(self):
        return sum(self.income_log) / max(1, len(self.income_log))

    def earn_till(self, amt, guest=True):
        self.till += amt
        self.this_second += amt
        if guest:
            self.guest_income += amt

    def room_count(self):
        return len(self.rooms)

    def type_count(self, pid):
        return sum(1 for r in self.rooms if r.type == pid)

    def floor_used(self, f):
        return sum(r.cells for r in self.rooms + self.amenities if r.floor == f)

    def reserved(self, f, floors=None):
        floors = self.floors if floors is None else floors
        return (ENTRANCE_DESK_CELLS if f == 1 else 0) + (STAIR_CELLS if f < floors else 0) + (STAIR_CELLS if f > 1 else 0)

    def usable(self, f, tiles, floors=None):
        return max(0, math.floor(USABLE_SHARE * (tiles - self.reserved(f, floors))))

    def floor_cap(self, f):
        return self.usable(f, self.tiles.get(f, 0))

    def tile_room(self, f):
        """Tiles still buyable on floor f: the grid, and upstairs only over owned tiles below (Grid.canBuyTile)."""
        top = self.G0["Grid"]["Cells"] ** 2
        if f > 1:
            top = min(top, self.tiles.get(f - 1, 0))
        return top - self.tiles.get(f, 0)

    def tiles_cost(self, f, n, start=None):
        b = self.bought.get(f, 0) if start is None else start
        return sum(self.rules.tile_cost(f, b + i) for i in range(n))

    def tiles_needed(self, f, cells, floors=None, have=None):
        """The fewest tiles on floor f that make `cells` free there, or None when the floor cannot."""
        have = self.tiles.get(f, 0) if have is None else have
        used = self.floor_used(f)
        room = (self.G0["Grid"]["Cells"] ** 2 if f == 1 else self.tiles.get(f - 1, 0)) - have
        for n in range(0, room + 1):
            if self.usable(f, have + n, floors) - used >= cells:
                return n
        return None

    def expand_option(self, cells):
        """The cheapest way to `cells` more free cells: tiles on a floor owned, or the next floor and its tiles.
        Returns (cost, kind, floor, tiles) or None."""
        E = self.G["Economy"]
        opts = []
        for f in range(1, self.floors + 1):
            n = self.tiles_needed(f, cells)
            if n is not None and n > 0:
                opts.append((self.tiles_cost(f, n), "tiles", f, n))
        if self.floors < self.floor_cap_max and self.floors < len(E["FloorCosts"]):
            f = self.floors + 1
            below = self.tiles_needed(f - 1, 0, floors=f)  # the stair takes cells on the floor below
            n = None
            if below is not None:
                for k in range(0, min(self.G0["Grid"]["Cells"] ** 2, self.tiles.get(f - 1, 0) + below) + 1):
                    if self.usable(f, k, f) >= cells:
                        n = k
                        break
            if n is not None:
                cost = E["FloorCosts"][f - 1] + self.tiles_cost(f - 1, below) + self.tiles_cost(f, n, start=0)
                opts.append((cost, "floor", f, (below, n)))
        return min(opts, key=lambda o: o[0]) if opts else None

    def expand(self, t, cells):
        o = self.expand_option(cells)
        if o is None or self.cash < o[0]:
            return False
        cost, kind, f, n = o
        if kind == "tiles":
            self.buy(t, "tiles", f"{n} on floor {f}", cost)
            self.tiles[f] += n
            self.bought[f] = self.bought.get(f, 0) + n
        else:
            below, up = n
            self.buy(t, "floor", f, cost)
            self.floors = f
            self.tiles[f - 1] += below
            self.bought[f - 1] = self.bought.get(f - 1, 0) + below
            self.tiles[f], self.bought[f] = up, up
            self.mark(f"floor_{f}_L{self.loc}", t)
        return True

    def add_piece(self, r, item):
        """A furniture or decor piece set in room r (Rooms.contents: furniture to its Furniture bar, decor to Decor)."""
        d = self.G["Decor"][item]
        r.items.append(item)
        if d.get("furniture"):
            r.fp += self.rules.points(item)
        else:
            r.dp += self.rules.points(item)
        r.squares += d["w"] * d["d"]

    def room_bars(self, r):
        return self.rules.bars(r.type, r.cells, r.fp, r.dp)

    def free_squares(self, r):
        return FILL_SHARE * r.cells * self.G0["Grid"]["Squares"] ** 2 - r.squares

    def fill_plan(self, r, kind):
        """The pieces the policy buys to fill a bar ("furniture" or "decor"): repeatedly the cheapest piece worth
        the points still missing, else the dearest, while they fit (FILL_SHARE). Returns (items, cost, gain in bar)."""
        bars = self.room_bars(r)
        if kind == "furniture":
            missing = self.rules.furniture_target(r.type) * (1 - bars[1])
        else:
            missing = self.rules.decor_target(r.cells) * (1 - bars[2])
        if missing <= 0:
            return [], 0, 0
        key = (self.loc, kind, math.ceil(missing), math.floor(self.free_squares(r)))
        if key not in FILL_CACHE:
            pool = [(self.G["Decor"][i]["cost"], self.rules.points(i), self.G["Decor"][i]["w"] * self.G["Decor"][i]["d"], i)
                    for i in self.G["Decor"] if bool(self.G["Decor"][i].get("furniture")) == (kind == "furniture") and self.rules.points(i) > 0]
            room, left, out, cost = self.free_squares(r), missing, [], 0
            while left > 0:
                fits = [p for p in pool if p[2] <= room]
                if not fits:
                    break
                enough = [p for p in fits if p[1] >= left]
                p = min(enough) if enough else max(fits, key=lambda q: (q[1], -q[2]))
                out.append(p[3])
                cost += p[0]
                left -= p[1]
                room -= p[2]
            FILL_CACHE[key] = (out, cost)
        out, cost = FILL_CACHE[key]
        if not out:
            return [], 0, 0
        pts = sum(self.rules.points(i) for i in out)
        if kind == "furniture":
            after = self.rules.bars(r.type, r.cells, r.fp + pts, r.dp)[1] - bars[1]
        else:
            after = self.rules.bars(r.type, r.cells, r.fp, r.dp + pts)[2] - bars[2]
        return out, cost, after

    def floor_for(self, cells):
        for f in range(1, self.floors + 1):
            if self.floor_used(f) + cells <= self.floor_cap(f):
                return f
        return None

    def room_tags(self, room):
        """HotelService.roomTags: its furniture's and decor's tags, and every ready amenity's on its floor."""
        tags = set()
        for d in room.items:
            tags.update(self.G["Decor"][d]["tags"])
        for a in self.amenities:
            if a.floor == room.floor:
                tags.update(self.G["Pieces"][a.type]["tags"])
        return tags

    def amen_on(self, f):
        return sum(1 for a in self.amenities if a.floor == f)

    def matched(self, sid, tags):
        return sum(1 for p in self.G["Species"][sid]["prefs"] if p in tags)

    def met(self, pid):
        u = self.G["Pieces"][pid].get("unlock")
        if not u:
            return True
        if "rooms" in u and self.room_count() < u["rooms"]:
            return False
        if "floor" in u and self.floors < u["floor"]:
            return False
        if "rating" in u and self.rating < u["rating"]:
            return False
        if u.get("legendaryResident") and not any(
            self.G["AllSpecies"][r["sid"]]["rarity"] == "Legendary" for r in self.residents
        ):
            return False
        return True

    def refresh_unlocks(self, t):
        for pid in self.G["Pieces"]:
            if pid not in self.unlocked and self.met(pid):
                self.unlocked.add(pid)
                self.mark(f"unlock_{pid}", t)

    def buildable(self, pid):
        return pid in self.unlocked or pid in self.tut_unlocked or self.met(pid)

    def vacant_for(self, sid):
        want = self.G["AllSpecies"][sid]["room"]
        best, bm = None, -1
        for r in self.rooms:
            if r.state == "Vacant" and r.type == want:
                m = self.matched(sid, self.room_tags(r))
                if best is None or m > bm:  # HotelService.vacantFor: the most preferences matched, the first on a tie
                    best, bm = r, m
        return best

    def roll_mut(self):
        # Mutations.rollSize and rollLook: one draw each over its group's rows; pay = 1 + the extras.
        got, extra = [], 0.0
        for group in ("Size", "Look"):
            x, at = self.rng.random(), 0.0
            for mid, ch, pay, g in self.G["Mutations"]:
                if g != group:
                    continue
                at += ch
                if x < at:
                    got.append(mid)
                    extra += pay - 1
                    break
        return ("+".join(got) or None), 1.0 + extra

    # ---- guests
    def spawn(self, t, sid, source, room, walk, happy_floor=None):
        mut, mp = self.roll_mut()
        room.state = "Reserved"
        g = Guest(sid, mut, mp, source, room, "ToHotel", t + walk, happy_floor=happy_floor)
        self.guests.append(g)
        return g

    def spawn_direct(self, t, sid, source, walk, happy_floor=None):
        room = self.vacant_for(sid)
        if not room:
            return None
        return self.spawn(t, sid, source, room, walk, happy_floor)

    def staff_eff(self):
        best, other = self.G["Staff"]["BestEfficiency"], self.G["Staff"]["OtherEfficiency"]
        return sum(best if self.G["AllSpecies"][r["sid"]]["staff"] == "RoomService" else other
                   for r in self.residents if r["role"] == "RoomService" and r.get("hotel") == self.loc)

    def check_in(self, t, g):
        g.waited = t - g.desk_since
        self.waits.append(g.waited)
        r = g.room
        g.prefs = self.matched(g.sid, self.room_tags(r))
        g.amen = self.amen_on(r.floor)
        pay, g.stay_mult, g.sat_bonus, g.fr_mult = self.rules.bonuses(self.room_bars(r))
        g.rate = self.rules.species_pay(g.sid) * g.mut_pay * self.rules.milestone(self.type_count(r.type)) * pay
        self.observed_pay.setdefault(r.type, deque(maxlen=20)).append(self.rules.species_pay(g.sid) * g.mut_pay)
        r.state = "Occupied"
        g.state = "ToRoom"
        g.at = t + ROOM_WALK + ROOM_WALK_PER_FLOOR * (r.floor - 1)
        self.checkins += 1
        self.metrics_checkins.append((t, self.G["Species"][g.sid]["rarity"]))
        if g.sid == self.G["RebirthResident"]:
            self.mark("first_vampire_checkin", t)

    def checkout(self, t, g):
        R = self.rules
        sat = R.satisfaction(g.prefs, g.amen, g.rp, g.rs, g.rm, g.waited, g.sat_bonus)
        if g.happy_floor:
            sat = max(sat, g.happy_floor)
        stay = R.stay_len(g.sid) * g.stay_mult
        self.earn_till(R.tip(g.rate, stay, sat))
        self.reviews.append(R.review(sat))
        self.sats.append(sat)
        sp = self.G["Species"][g.sid]
        self.prefs_shares.append(g.prefs / max(1, len(sp["prefs"])))
        g.room.state, g.room.dirty_since = "Dirty", t
        if g.sid not in self.book:
            self.book.add(g.sid)
            bonus = math.floor(R.species_pay(g.sid) * self.G["Book"]["SpeciesFoundPaySeconds"])
            self.cash += bonus
            self.run_cash += bonus
        if sat >= self.G["Stay"]["Happy"]:
            self.mark("first_happy_stay", t)
            if EXPEDITIONS and sp["rarity"] not in ("Common", "Uncommon"):
                self.rare_happy[self.loc] = self.rare_happy.get(self.loc, 0) + 1
            now = self.friendship.get(g.sid, 0) + g.fr_mult  # the Decor bar's friendship (ResidentService)
            self.friendship[g.sid] = now
            thr = self.G["Residents"]["TutorialFriendship"] if getattr(g, "tutorial_friend", False) else self.G["Rarity"][sp["rarity"]]["friendship"]
            early = self.rng.random() < self.G["Rarity"][sp["rarity"]]["moveInChance"]
            if now >= thr or early:
                self.move_in(t, g)

    def resident_pay(self, r):
        return self.rules.species_pay(r["sid"]) * self.G["Residents"]["EarnFraction"] * r["mp"]

    def move_in(self, t, g):
        cap = self.G["Residents"]["WingCapacity"]
        new = {"sid": g.sid, "mp": g.mut_pay, "role": "", "hotel": None}
        if len(self.residents) >= cap:
            # The Wing is full: no move-in (ResidentService). A player releases the lowest earner first
            # when a better one is coming; modelled as: the lowest idle earner was released in time.
            idle = [r for r in self.residents if r["role"] == "" and r["sid"] != self.G["RebirthResident"]]
            if not idle:
                return
            low = min(idle, key=self.resident_pay)
            if g.sid == self.G["RebirthResident"] or self.resident_pay(new) > self.resident_pay(low):
                self.residents.remove(low)
            else:
                return
        self.residents.append(new)
        self.friendship[g.sid] = 0
        self.mark("first_resident", t)
        if g.sid == self.G["RebirthResident"]:
            self.mark("vampire_resident", t)

    def tick_guests(self, t):
        S = self.G["Stay"]
        eff = self.staff_eff()
        keep = []
        for g in self.guests:
            if g.state == "ToHotel" and t >= g.at:
                g.state, g.desk_since = "Queued", t
            if g.state == "Queued" and t - g.desk_since >= CHECKIN_DELAY:
                self.check_in(t, g)
            if g.state == "ToRoom" and t >= g.at:
                g.state = "InRoom"
                stay = self.rules.stay_len(g.sid) * g.stay_mult  # the Size bar's longer stay
                g.stay_end = t + stay
                g.req_at = t + int(stay * (0.25 + 0.5 * self.rng.random()))
                self.mark("first_guest_pays", t)
            if g.state == "InRoom":
                self.earn_till(g.rate)
                if g.req_at is not None and t >= g.req_at:
                    g.req_at, g.req_open = None, t
                    g.req_player_at = t + self.rng.randint(*REQ_PLAYER_TIME) if self.rng.random() < P_REQUEST_PLAYER else None
                if g.req_open is not None:
                    walk = ROOM_WALK + ROOM_WALK_PER_FLOOR * (g.room.floor - 1) + 2
                    staff_at = max(g.req_open + self.G["Staff"]["RoomServiceDelay"] / eff, g.req_open + walk) if eff > 0 else math.inf
                    if g.req_player_at is not None and t >= g.req_player_at and g.req_player_at <= staff_at:
                        g.rp += 1
                        self.earn_till(math.floor(g.rate * S["RequestTipSeconds"]))
                        self.req_asked += 1
                        self.req_done += 1
                        g.req_open = None
                    elif t >= staff_at:
                        g.rs += 1
                        self.req_asked += 1
                        self.req_done += 1
                        g.req_open = None
                    elif t >= g.req_open + S["RequestWindow"]:
                        g.rm += 1
                        self.req_asked += 1
                        g.req_open = None
                if t >= g.stay_end:
                    self.checkout(t, g)
                    continue
            keep.append(g)
        self.guests = keep

    # ---- the bus
    def bus(self, t):
        B = self.G["Bus"]
        self.bus_index += 1
        wall = self.wall0 + t
        crossed = lambda p: math.floor(wall / p) > math.floor(self.last_bus_wall / p)
        flags = {"epic": self.bus_index % B["EpicEvery"] == 0, "leg": crossed(B["LegendaryEvery"]), "myth": crossed(B["MythicEvery"])}
        self.last_bus_wall = wall
        order = ["Common", "Uncommon", "Rare", "Epic", "Legendary", "Mythic"]
        pools = {r: [s for s, sp in self.G["Species"].items() if sp["rarity"] == r] for r in order}

        def pick(r):
            i = order.index(r)
            while i >= 0:
                if pools[order[i]]:
                    p = pools[order[i]]
                    return p[int(self.rng.random() * len(p))]
                i -= 1

        out = []
        if flags["myth"]:
            out.append(pick("Mythic"))
        if flags["leg"]:
            out.append(pick("Legendary"))
        if flags["epic"]:
            out.append(pick("Epic"))
        total = sum(self.G["Rarity"][r]["weight"] for r in order)
        vacant = sum(1 for r in self.rooms if r.state == "Vacant")
        size = max(B["MinPerPlayer"], min(B["MaxPerPlayer"], math.ceil(B["VacantShare"] * vacant - 1e-9)))
        self.bus_sizes.append(size)
        while len(out) < size:
            x, at, rr = self.rng.random(), 0.0, "Common"
            for r in order:
                at += self.G["Rarity"][r]["weight"] / total
                if x < at:
                    rr = r
                    break
            out.append(pick(rr))
        self.tutorial_commons(out, sum(1 for f in flags.values() if f))
        half = math.ceil(len(out) / 2)
        for i, sid in enumerate(out):
            off = (i * B["StepOff"]) if i < half else (EAST_STOP_AFTER + (i - half) * B["StepOff"])
            self.pending_bus.append((t + int(off + B["BrowseTime"]), sid))
            if sid == self.G["RebirthResident"]:
                self.mark("first_vampire_on_bus", t)
        # a booked guest (the tutorial's Vampire Count) skips browsing
        for sid, hf in self.booked:
            g = self.spawn_direct(t, sid, "Tutorial", BUS_TO_HOTEL, hf)
            if g:
                self.mark("tutorial_vampire_arrives", t)
        self.booked = []
        self.mark("first_bus", t)

    def tutorial_commons(self, out, guaranteed):
        """BusService.weightCommons and Bus.commonsFor (§11 1:45): during the tutorial (past CheckIn, before
        Done), on its first CommonBuses buses that bring some, up to CommonsPerBus Commons for the hotel's
        vacant room types replace drawn guests from the end of the list, never a guarantee nor the announced
        Legendary+. Solo, their TutorialBoost toward the hotel changes nothing: no other hotel competes."""
        T = self.G["Tutorial"]
        if not self.tutorial or self.tstep in ("CheckIn", "Done") or self.tut_common_buses >= T["CommonBuses"]:
            return
        slot = len(out) - 1  # 0-based: the last drawn guest
        if slot < guaranteed:
            return
        n = min(T["CommonsPerBus"], slot + 1 - guaranteed)
        takers: dict = {}
        for sid, sp in self.G["Species"].items():
            if sp["rarity"] == "Common":
                takers.setdefault(sp["room"], []).append(sid)
        left = {}
        for r in self.rooms:
            if r.state == "Vacant" and r.type in takers:
                left[r.type] = left.get(r.type, 0) + 1
        rooms = sorted(left)
        ids, more = [], True
        while len(ids) < n and more:
            more = False
            for room in rooms:
                if len(ids) < n and left[room] > 0:
                    pool = takers[room]
                    ids.append(pool[int(self.rng.random() * len(pool))])
                    left[room] -= 1
                    more = True
        rare = ("Legendary", "Mythic")
        placed = 0
        for sid in ids:
            while slot >= guaranteed and self.G["Species"][out[slot]]["rarity"] in rare:
                slot -= 1
            if slot < guaranteed:
                break
            out[slot] = sid
            slot -= 1
            placed += 1
        if placed:
            self.tut_common_buses += 1

    def decide_bus(self, t):
        keep = []
        for at, sid in self.pending_bus:
            if t >= at:
                room = self.vacant_for(sid)
                if room:
                    self.spawn(t, sid, "Bus", room, BUS_TO_HOTEL)
                    self.mark("first_bus_guest", t)
                elif sid == self.G["RebirthResident"]:
                    self.events["vampires_missed"] = self.events.get("vampires_missed", 0) + 1
            else:
                keep.append((at, sid))
        self.pending_bus = keep

    # ---- rating
    def on_time_share(self, t):
        """HotelService.inputs: recent cleanings within CleanOnTime, every room overdue now counted late."""
        lim = self.G["Rating"]["CleanOnTime"]
        overdue = sum(1 for r in self.rooms if r.state == "Dirty" and t - r.dirty_since > lim)
        judged = len(self.clean_times) + overdue
        return sum(1 for x in self.clean_times if x <= lim) / judged if judged else 0

    def recompute(self, t):
        ready_bars = [self.room_bars(r) for r in self.rooms + self.amenities]  # every ready room's and amenity's
        dirty = sum(1 for r in self.rooms if r.state == "Dirty")
        decor = sum(len(r.items) for r in self.rooms + self.amenities)  # data.decor: every furniture and decor piece
        types = len({r.type for r in self.rooms})
        cats = self.rules.categories(
            ready_bars,
            statistics.fmean(self.prefs_shares) if self.prefs_shares else 0,
            statistics.fmean(self.waits) if self.waits else 0,
            len(self.waits),
            self.req_done / self.req_asked if self.req_asked else 0,
            len(self.rooms), dirty, len(self.amenities), decor, types,
            0.0, self.staff_eff(), 0.0, self.on_time_share(t),
        )
        self.cats = cats
        self.rating = self.rules.stars(cats, list(self.reviews))
        self.refresh_unlocks(t)

    # ---- buying
    def buy(self, t, kind, what, cost):
        inc = self.income_rate() * 60
        self.cash -= cost
        meaningful = kind in ("room", "furnish", "floor", "tiles", "amenity") or (kind == "decor" and inc > 0 and cost >= inc)
        self.purchases.append((t, kind, what, cost, inc, meaningful, self.loc))

    def place_room(self, t, pid, cells=None, free_key=False):
        """A room or amenity built in one go (walls, door, type, key piece): ready at once."""
        cells = cells or self.rules.min_cells(pid)
        f = self.floor_for(cells)
        if f is None:
            return False
        cost = self.rules.build_cost(pid, cells, free_key)
        if cost > self.cash:
            return False
        amenity = self.G["Pieces"][pid]["kind"] == "Amenity"
        self.buy(t, "amenity" if amenity else "room", pid, cost)
        mine = [r.occ for r in self.rooms if r.type == pid]
        r = Room(self.next_id, pid, f, cells, occ=statistics.fmean(mine) if mine else 0.5)
        self.next_id += 1
        self.add_piece(r, self.G["Keys"][pid][1])
        (self.amenities if amenity else self.rooms).append(r)
        if not amenity:
            self.mark("first_room", t)
            self.mark(f"first_{pid}", t)
        return True

    def fill(self, t, r, kind, plan):
        items, cost, _ = plan
        if not items or cost > self.cash:
            return False
        for i in items:
            self.add_piece(r, i)
        self.buy(t, "furnish", f"{r.type} {kind}", cost)
        return True

    def species_weights(self, pid):
        """How often each species of a room type comes: walk-in species 1, bus-only by rarity weight."""
        out = {}
        for s, sp in self.G["Species"].items():
            if sp["room"] != pid:
                continue
            r = sp["rarity"]
            out[s] = 1.0 if r in ("Common", "Uncommon") else max(0.15, self.G["Rarity"][r]["weight"] / 25)
        if pid == "CoffinSuite":
            out = {k: 1.0 for k in out}
        return out

    def decor_plan(self, room):
        """The best set of up to DECOR_MATCH_SLOTS pieces (furniture or decor placeable here) for the preferences
        of the species the room's type serves, given its pieces' and its floor's amenities' tags."""
        floor_tags = set()
        for a in self.amenities:
            if a.floor == room.floor:
                floor_tags.update(self.G["Pieces"][a.type]["tags"])
        w = self.species_weights(room.type)
        have = list(room.items)
        free_slots = self.G["DecorSlots"] - (len(have) - 1)  # the key piece is not a slot
        if free_slots <= 0:
            return []
        ckey = (self.loc, room.type, tuple(sorted(have)), frozenset(floor_tags))
        if ckey in PLAN_CACHE:
            return list(PLAN_CACHE[ckey])
        best, best_key = [], None
        wanted = {p for sid in w for p in self.G["Species"][sid]["prefs"]}
        cands = [d for d in self.G["Decor"] if d not in have and wanted & set(self.G["Decor"][d]["tags"])]
        for k in range(0, free_slots + 1):
            for combo in combinations(cands, k):
                tags = set(floor_tags)
                for d in have + list(combo):
                    tags.update(self.G["Decor"][d]["tags"])
                val = sum(wt * self.matched(s, tags) for s, wt in w.items())
                cost = sum(self.G["Decor"][d]["cost"] for d in combo)
                key = (round(val, 6), -cost)
                if best_key is None or key > best_key:
                    best, best_key = list(combo), key
        PLAN_CACHE[ckey] = sorted(best, key=lambda d: self.G["Decor"][d]["cost"])
        return list(PLAN_CACHE[ckey])

    def avg_pay(self, pid):
        obs = self.observed_pay.get(pid)
        if obs:
            return statistics.fmean(obs)
        w = self.species_weights(pid)
        return sum(self.rules.species_pay(s) * x for s, x in w.items()) / max(1e-9, sum(w.values()))

    def open_price(self):
        """What opening the next location takes now (its price: its first room is free), or None at the last."""
        nxt = self.loc + 1
        if nxt > self.G0["Chain"]["Locations"]:
            return None
        return self.G0["Chain"]["OpenCost"][nxt]

    def space_cost(self, f, cells):
        """What `cells` of owned space are worth at floor f's next tile price (the policy's opportunity cost)."""
        return cells / USABLE_SHARE * self.rules.tile_cost(f, self.bought.get(f, 0))

    def leaves_amenity_space(self, cells):
        """Policy: a new room leaves room (on the floors the cap allows, every tile bought) for the amenities
        Fun still needs (ceil(100 / FunPerAmenity) in all), each at the location's smallest amenity size."""
        missing = math.ceil(100 / self.G["Rating"]["FunPerAmenity"]) - len(self.amenities)
        if missing <= 0:
            return True
        smallest = min(self.rules.min_cells(a) for a, p in self.G["Pieces"].items() if p["kind"] == "Amenity")
        top = min(self.floor_cap_max, len(self.G["Economy"]["FloorCosts"]))
        free = sum(self.usable(f, self.G0["Grid"]["Cells"] ** 2, top) - self.floor_used(f) for f in range(1, top + 1))
        return free - cells >= missing * smallest

    def bar_gain(self, r, kind, plan, n):
        """Expected extra $/s of filling a bar: the pay bonus (Furniture) and the tip on the satisfaction it adds."""
        _, _, db = plan
        if db <= 0:
            return 0
        RM, S = self.G0["Rooms"], self.G0["Stay"]
        s, f, d = self.room_bars(r)
        base = self.avg_pay(r.type) * self.rules.milestone(n) * r.occ
        pay = self.rules.bonuses((s, f, d))[0]
        if kind == "furniture":
            dpay = self.rules.bonuses((s, f + db, d))[0] - pay
            dsat = RM["FurnitureSatisfaction"] * db
        else:
            dpay, dsat = 0, RM["DecorSatisfaction"] * db
        return base * (dpay + pay * S["TipFraction"] * dsat / 100)

    def policy(self, t):
        inc = max(self.income_rate(), 0.25)
        P = self.G["Pieces"]
        # 0. the chain: at 5 stars, save for the next location and open it once it is affordable
        saving = None
        price = self.open_price()
        if price is not None and self.tstep == "Done":
            if self.cash >= price:
                self.mark(f"afford_open_{self.loc + 1}", t)
                self.snap(f"afford_open_{self.loc + 1}", t)
            if self.rating >= self.G0["Chain"]["RebirthRating"]:
                if self.cash >= price:
                    self.open_next(t)
                    return
                saving = (price - self.cash) / inc  # seconds still to save at the present income
        # 2. the goal: the tutorial guest's room (the Coffin Suite) and its pieces, at Haunted Manor
        goal = self.G["AllSpecies"][self.G["RebirthResident"]]["room"]
        if goal in P and self.buildable(goal) and self.type_count(goal) == 0:
            cells = self.rules.min_cells(goal)
            free = bool(self.vouchers.get(goal))
            if self.floor_for(cells) is None:
                o = self.expand_option(cells)
                if free or (o and o[0] + self.rules.build_cost(goal, cells) <= 20 * 60 * inc):
                    self.expand(t, cells)  # save for the tiles the suite needs
                    return
            else:
                cost = self.rules.build_cost(goal, cells, free)
                if free or cost <= 20 * 60 * inc:
                    if self.place_room(t, goal, cells, free_key=free) and free:
                        self.vouchers[goal] -= 1
                    return  # built, or saving for it
        has_goal = any(r["sid"] == self.G["RebirthResident"] for r in self.residents)
        for r in self.rooms:
            if r.type == goal and not has_goal:
                for d in self.decor_plan(r):
                    c = self.G["Decor"][d]["cost"]
                    if c > 10 * 60 * inc:
                        break  # out of reach for now: rule 3 buys it when it is cheap
                    if self.G["Decor"][d]["w"] * self.G["Decor"][d]["d"] > self.free_squares(r):
                        continue
                    if self.cash >= c:
                        self.add_piece(r, d)
                        self.buy(t, "decor", d, c)
                        return
                    return  # saving for it
        # 3. pieces that match the guests' preferences
        for r in self.rooms:
            for d in self.decor_plan(r):
                c = self.G["Decor"][d]["cost"]
                fits = self.G["Decor"][d]["w"] * self.G["Decor"][d]["d"] <= self.free_squares(r)
                if fits and c <= self.cash and (c <= 90 * inc or c <= 0.3 * self.cash):
                    self.add_piece(r, d)
                    self.buy(t, "decor", d, c)
                    return
        # 3b. the bars: a room's Furniture fill, then its Decor fill, when cheap against income
        for r in self.rooms:
            for kind in ("furniture", "decor"):
                plan = self.fill_plan(r, kind)
                if plan[0] and plan[1] <= BAR_FILL_S * inc and plan[1] <= self.cash:
                    self.fill(t, r, kind, plan)
                    return
        # 4. amenities: three per floor with rooms, and more while Fun is short of 100
        fun_need = math.ceil(100 / self.G["Rating"]["FunPerAmenity"])
        for f in range(1, self.floors + 1):
            if not any(r.floor == f for r in self.rooms):
                continue
            if self.amen_on(f) >= 3 and len(self.amenities) >= fun_need:
                continue
            owned = {a.type for a in self.amenities if a.floor == f}
            ranked = []
            for a, p in P.items():
                if p["kind"] != "Amenity" or not self.buildable(a):
                    continue
                c = self.rules.build_cost(a, self.rules.min_cells(a))
                tags = set(p["tags"])
                val = sum(self.matched(r_sid, tags) for rr in self.rooms if rr.floor == f for r_sid in self.species_weights(rr.type))
                ranked.append(((a not in owned, val > 0, -c), (a, c, self.rules.min_cells(a))))
            ranked.sort(key=lambda x: x[0], reverse=True)
            for _, best in ranked:  # the most useful first; a duplicate when the new type is still too dear
                n = 0
                if self.floor_used(f) + best[2] > self.floor_cap(f):
                    n = self.tiles_needed(f, best[2])
                    if n is None:
                        break
                extra = self.tiles_cost(f, n) if n else 0
                if best[1] + extra <= 180 * inc and best[1] + extra <= self.cash:
                    break
            else:
                continue
            if n is None:
                continue
            if best[1] + extra <= 180 * inc and best[1] + extra <= self.cash:
                if n:
                    self.buy(t, "tiles", f"{n} on floor {f}", extra)
                    self.tiles[f] += n
                    self.bought[f] = self.bought.get(f, 0) + n
                # the amenity on this floor (place_room takes the first floor with room: this one has it now)
                cells = best[2]
                cost = self.rules.build_cost(best[0], cells)
                r = Room(self.next_id, best[0], f, cells)
                self.next_id += 1
                self.add_piece(r, self.G["Keys"][best[0]][1])
                self.amenities.append(r)
                self.buy(t, "amenity", best[0], cost)
                return
        # 5. the first room of a newly unlocked type, at its minimum
        for pid, p in P.items():
            if p["kind"] == "Room" and pid != goal and self.type_count(pid) == 0 and self.buildable(pid):
                cells = self.rules.min_cells(pid)
                if not self.leaves_amenity_space(cells):
                    continue
                c = self.rules.build_cost(pid, cells)
                if self.floor_for(cells) is None:
                    o = self.expand_option(cells)
                    if o and c + o[0] <= 300 * inc and c + o[0] <= self.cash:
                        self.expand(t, cells)
                        return
                    continue
                if c <= 300 * inc and c <= self.cash and self.place_room(t, pid, cells):
                    return
        # 6. return on cost: new rooms of owned types (at their minimum or full size), bar fills, a floor
        cands = []
        for pid in {r.type for r in self.rooms}:
            mine = [r for r in self.rooms if r.type == pid]
            n = len(mine)
            occ = statistics.fmean(r.occ for r in mine)
            pay = self.avg_pay(pid)
            jump = self.rules.milestone(n + 1) > self.rules.milestone(n)
            if occ >= ROOM_FULL or jump:
                key_bar = self.rules.bars(pid, self.rules.min_cells(pid), self.rules.points(self.G["Keys"][pid][1]), 0)[1]
                sizes = {"roi": (self.rules.min_cells(pid), self.rules.full_cells(pid)),
                         "min": (self.rules.min_cells(pid),), "full": (self.rules.full_cells(pid),)}[SIZE_POLICY]
                for cells in sizes:
                    if not self.leaves_amenity_space(cells):
                        continue
                    size = self.rules.bars(pid, cells, 0, 0)[0]
                    d = pay * self.rules.bonuses((size, key_bar, 0))[0] * self.rules.milestone(n + 1) * occ ** 2
                    if jump:
                        d += sum(pay * self.rules.bonuses(self.room_bars(r))[0] * r.occ for r in mine) * self.rules.milestone(n)
                    cost = self.rules.build_cost(pid, cells)
                    f = self.floor_for(cells)
                    if f is None:
                        o = self.expand_option(cells)
                        if o is None:
                            continue
                        extra = o[0]
                    else:
                        extra = self.space_cost(f, cells)
                    cands.append((d / (cost + extra), "room", (pid, cells), cost + extra))
            for r in mine:
                for kind in ("furniture", "decor"):
                    plan = self.fill_plan(r, kind)
                    if plan[0] and plan[1] > 0:
                        cands.append((self.bar_gain(r, kind, plan, n) / plan[1], "furnish", (r, kind, plan), plan[1]))
        # a room type that needs a floor more: the floor is a candidate of its own while it is missing
        wants_floor = any((p.get("unlock") or {}).get("floor", 0) > self.floors for p in P.values())
        if wants_floor and self.floors < self.floor_cap_max and self.room_count() >= 2:
            fc = self.G["Economy"]["FloorCosts"][self.floors]
            if fc <= 300 * inc:
                cands.append((math.inf, "floor", None, fc))
        if saving is not None:
            # saving for the next location: only what pays itself back before the price is saved anyway
            cands = [c for c in cands if c[0] > 0 and 1 / c[0] <= saving]  # payback = cost / gain
        if not cands:
            return
        cands.sort(key=lambda c: -c[0])
        _, kind, what, cost = cands[0]
        if kind == "floor":
            if cost > self.cash:
                return  # save for it
            self.buy(t, "floor", self.floors + 1, cost)
            self.floors += 1
            self.tiles.setdefault(self.floors, 0)
            self.bought.setdefault(self.floors, 0)
        elif kind == "room":
            pid, cells = what
            if self.floor_for(cells) is None:
                self.expand(t, cells)  # its space first (saving for it while it is dearer than cash)
                return
            self.place_room(t, pid, cells)
        else:
            r, k, plan = what
            self.fill(t, r, k, plan)

    # ---- the tutorial
    def tutorial_tick(self, t):
        s = self.tstep
        since = t - self.tstep_since
        done = False
        if s == "CheckIn":
            if self.slime_at is None:
                self.slime_at = t + self.G["Tutorial"]["FirstGuestDelay"]
            done = self.checkins >= 1
        elif s == "Collect":
            done = self.collects >= 1
        elif s == "SecondRoom":
            done = self.room_count() >= 2
        elif s == "Furnish":
            done = self.room_count() >= 2  # ready rooms: the model's rooms are ready when built
        elif s == "Bus":
            done = self.events.get("first_bus_guest") is not None or since > 150
        elif s == "MoveIn":
            done = bool(self.residents)
        elif s == "Goal":
            done = since > 8
        elif s == "Clean":
            done = self.cleaned >= 1
        elif s == "Staff":
            done = any(r["role"] for r in self.residents)
        elif s == "Preview":
            done = since > 5  # the player presses Next (else 25 s)
        elif s == "Done":
            # TutorialService: booked on the next bus once 2+ buses passed since the goal and a Coffin Suite is vacant
            if (self.tut_goal and not self.tut_vampire_sent and self.bus_index - self.tut_goal_bus >= 2
                    and self.vacant_for(self.G["RebirthResident"])):
                self.booked.append((self.G["RebirthResident"], self.G["Stay"]["Happy"]))
                self.tut_vampire_sent = True
        if self.slime_at is not None and t == self.slime_at:
            g = self.spawn_direct(t, "Slime", "Tutorial", TUTORIAL_WALK, self.G["Stay"]["Happy"])
            if g:
                g.tutorial_friend = True
        if done:
            steps = ["CheckIn", "Collect", "SecondRoom", "Furnish", "Bus", "MoveIn", "Goal", "Clean", "Staff", "Preview", "Done"]
            nxt = steps[steps.index(s) + 1]
            self.tstep, self.tstep_since = nxt, t
            if nxt == "Goal":
                self.tut_goal_bus = self.bus_index
                self.tut_unlocked.add("CoffinSuite")
                self.vouchers["CoffinSuite"] = 1
                tt = self.G0["Grid"]["TutorialTiles"]
                self.tiles[1] += tt["w"] * tt["d"]  # BuildService.tutorialTiles: a free block beside the start square
                self.tut_goal = True
            if nxt == "Done":
                self.mark("tutorial_done", t)

    def assign_staff(self, t):
        """One Room Service at the hotel played (ResidentService: staff work where they were assigned)."""
        if any(r["role"] == "RoomService" and r["hotel"] == self.loc for r in self.residents):
            self.staff_assigned_at = None
            return
        idle = [r for r in self.residents if r["role"] == ""]
        if not idle:
            return
        if self.staff_assigned_at is None:
            self.staff_assigned_at = t + STAFF_ASSIGN_DELAY
        if t >= self.staff_assigned_at:
            best = [r for r in idle if self.G["AllSpecies"][r["sid"]]["staff"] == "RoomService"]
            pick = best[0] if best else min(idle, key=self.resident_pay)
            pick["role"], pick["hotel"] = "RoomService", self.loc

    # ---- the run
    def run(self):
        self.pending_bus = []
        self.bus_sizes = []
        C = self.G0["Chain"]
        for t in range(0, self.T + 1):
            self.this_second = 0.0
            if self.tutorial:
                self.tutorial_tick(t)
            if t >= self.next_bus:
                self.bus(t)
                self.next_bus = t + self.G["Bus"]["Interval"]
            self.decide_bus(t)
            self.tick_guests(t)
            # occupancy: rooms with a paying guest, and rooms not vacant
            self._occ_pay += sum(1 for g in self.guests if g.state == "InRoom")
            self._occ_busy += sum(1 for r in self.rooms if r.state != "Vacant")
            self._occ_rooms += len(self.rooms)
            # residents into the till
            self.earn_till(sum(self.resident_pay(r) for r in self.residents if r["role"] == ""), guest=False)
            self.assign_staff(t)
            if t > 0 and t % self.G0["ChainTick"] == 0:
                self.chain_tick(t)
            # the player: clean, collect, buy
            for r in self.rooms:
                if r.state == "Dirty" and t - r.dirty_since >= CLEAN_DELAY + self.G["Stay"]["CleanHold"]:
                    r.state = "Vacant"
                    self.cleaned += 1
                    self.clean_times.append(t - r.dirty_since)
                r.occ += ((r.state != "Vacant") - r.occ) / 120
            if self.till > 0 and (t % COLLECT_EVERY == 0 or self.tstep == "Collect"):
                self.cash += math.floor(self.till)
                self.run_cash += math.floor(self.till)
                self.till -= math.floor(self.till)
                self.collects += 1
            if self.tutorial and self.tstep == "SecondRoom":
                self.place_room(t, self.G["StartRoom"][0])  # a Standard Room at its minimum, its Bed
            elif self.tstep not in ("CheckIn", "Collect"):
                self.policy(t)
            self.income_log.append(self.this_second)
            if t % 5 == 0:
                self.recompute(t)
                L = self.loc
                for x in (3, 4, 4.5, 5):
                    if self.rating >= x:
                        self.mark(f"rating_{x}_L{L}", t)
                for i, c in enumerate(self.cats):
                    if c >= 95:
                        self.cat_first.setdefault((L, i), t)
                if len(self.reviews) >= 10 and statistics.fmean(self.reviews) >= 4.5:
                    self.cat_first.setdefault((L, "reviews"), t)
                if self.rating >= C["RebirthRating"]:
                    self.mark(f"five_star_{L}", t)
                    self.snap(f"five_star_{L}", t)
                # Chain.rebirthReady: every location opened, each rating (live here, as left elsewhere) at 5
                ratings = {k: v["rating"] for k, v in self.chain.items()}
                ratings[L] = self.rating
                if all(ratings.get(k, 0) >= C["RebirthRating"] for k in range(1, C["Locations"] + 1)):
                    self.rebirth_ready = t
                    self.mark("rebirth_ready", t)
                    self.snap("rebirth_ready", t)
                    break
            if t % 60 == 0:
                self.occ_log.append((t, self._occ_rooms, self._occ_pay, self._occ_busy))
                self._occ_pay = self._occ_busy = self._occ_rooms = 0
                self.timeline.append((t, self.income_rate() * 60, self.rating, self.cash, self.run_cash, len(self.rooms), list(self.cats),
                                      self.loc, self.background_rate() * 60))
                if EXPEDITIONS:
                    self.wing_log.append((t, self.loc, sorted((self.resident_pay(r) for r in self.residents if r["role"] == ""),
                                                              reverse=True), self.income_rate()))
        self.end = t
        if EXPEDITIONS:  # the Wing as the run ends (rebirth-ready breaks before the minute's record)
            self.wing_log.append((t, self.loc, sorted((self.resident_pay(r) for r in self.residents if r["role"] == ""),
                                                      reverse=True), self.income_rate()))
        return self


# ------------------------------------------------------------------- reporting
def fmt(t):
    if t is None or t == math.inf:
        return "—"
    t = int(t)
    return f"{t // 3600}:{t % 3600 // 60:02d}:{t % 60:02d}" if t >= 3600 else f"{t // 60}:{t % 60:02d}"


def med(xs):
    xs = [x for x in xs]
    if any(x is None for x in xs):
        n = sum(1 for x in xs if x is None)
        rest = [x for x in xs if x is not None]
        if n > len(xs) / 2:
            return None
        rest += [math.inf] * n
        return statistics.median(rest)
    return statistics.median(xs)


def summarize(G, sims, label):
    def ev(key):
        return med([s.events.get(key) for s in sims])

    def purch_by(sim, t, meaningful_only):
        return sum(1 for p in sim.purchases if p[0] <= t and (p[5] or not meaningful_only))

    return {
        "label": label,
        "first_room": ev("first_room"),
        "first_pays": ev("first_guest_pays"),
        "first_bus": ev("first_bus"),
        "first_bus_guest": ev("first_bus_guest"),
        "buys5_all": statistics.median(purch_by(s, 300, False) for s in sims),
        "buys5_meaningful": statistics.median(purch_by(s, 300, True) for s in sims),
        "first_resident": ev("first_resident"),
        "vamp_checkin": ev("first_vampire_checkin"),
        "vamp_resident": ev("vampire_resident"),
        "bus_size": statistics.fmean(x for s in sims for x in s.bus_sizes) if any(s.bus_sizes for s in sims) else 0,
        "sims": sims,
    }


def timeline_rows(sims, marks_min):
    rows = []
    for m in marks_min:
        pick = []
        for s in sims:
            pts = [p for p in s.timeline if p[0] <= m * 60]
            if pts and pts[-1][0] >= m * 60 - 60 and s.end >= m * 60 - 60:
                pick.append(pts[-1])
        if len(pick) >= max(1, len(sims) // 2 + 1):
            md = lambda i: statistics.median(p[i] for p in pick)
            locs = sorted(p[7] for p in pick)
            rows.append((m, md(1), md(2), md(5), md(3), md(8), locs, len(pick)))
    return rows


def money(x):
    if x is None:
        return "—"
    for unit, d in (("B", 1e9), ("M", 1e6), ("k", 1e3)):
        if abs(x) >= d:
            return f"${x / d:.1f}{unit}"
    return f"${x:.0f}"


# ------------------------------------------------------ the Expeditions what-if
def exp_check(G):
    """--expeditions: the offline rules it mirrors, and the numbers it holds that are not in src/ yet."""
    if os.path.exists(os.path.join(ROOT, "src/shared/Expeditions.luau")):
        raise ParseError("src/shared/Expeditions.luau exists: read the Expeditions numbers from it instead of EXP")
    norm = lambda x: re.sub(r"\s+", "", x)
    bad = [f"  {rel}: {line}" for rel, line in EXP_GUARDS if norm(line) not in norm(read(rel))]
    if bad:
        raise ParseError("the offline rules changed; update the Expeditions what-if:\n" + "\n".join(bad))
    for k in ("OfflineFraction", "OfflineCap", "NightManagerCap", "LevelXpPerMinute"):
        need(G["Residents"], k, "src/shared/Constants.luau Constants.Residents")


def exp_days(n, s, cap_s, length_s, policy, leak, days, off_frac, xp_wing):
    """Days of a player who logs in n times a day for s minutes (evenly spaced), minute by minute, for unit
    rates ($1/s). Per day (days 2.. averaged): `stay` = what $1/s of Wing rate earns by staying (online and
    offline); `counted` = the party's staying-equivalent over its trips (the reward before Pay); `party` = what
    the party earns in the Wing outside its trips; `trips` collected; `xa`/`xb` = one party member's XP by
    staying / with trips. `ends` = (minute, length in minutes) of every trip's end, day 1 included."""
    P, cap_m, L_m = 1440 // n, cap_s // 60, length_s // 60
    H = P - s
    trip_end = None
    acc = dict(stay=0.0, counted=0.0, party=0.0, trips=0, xa=0.0, xb=0.0)
    ends = []
    for t in range(days * 1440):
        phase = t % P
        online = phase < s
        count = t >= 1440
        if online and phase == 0 and t > 0 and leak:
            # welcomeBack: rate(at join) counts every resident back from its trip, for the whole absence
            if count and (trip_end is None or trip_end <= t):
                acc["party"] += off_frac * 60 * min(H, cap_m)
        if trip_end is not None and t >= trip_end and online:
            trip_end = None  # collected
        if trip_end is None and ((policy == "busy" and online) or phase == s):
            trip_end = t + L_m
        w = 60.0 if online else (60.0 * off_frac if phase - s < cap_m else 0.0)
        on_trip = trip_end is not None and t < trip_end
        if count:
            acc["stay"] += w
            acc["xa"] += xp_wing if online else 0
            if on_trip:
                acc["counted"] += w
                acc["xb"] += EXP["XpPerHour"] / 60
            elif online:
                acc["party"] += w
                acc["xb"] += xp_wing
            elif not leak:
                acc["party"] += w
        if on_trip and t + 1 == trip_end:
            ends.append((trip_end, L_m))
            if count:
                acc["trips"] += 1
    out = {k: v / (days - 1) for k, v in acc.items()}
    out["ends"] = ends
    return out


def exp_poisson(rng, lam):
    if lam <= 0:
        return 0
    if lam > 60:
        return max(0, round(rng.gauss(lam, math.sqrt(lam))))
    k, p, lim = 0, 1.0, math.exp(-lam)
    while True:
        p *= rng.random()
        if p <= lim:
            return k
        k += 1


def exp_finds(ends, days, chance_mult=1.0, stay_per_day=0.0, targets=(5, 15), runs=1000, seed=7):
    """Monte Carlo of the finds: each trip's chance by its length (x chance_mult), among unfound pieces only (a find
    is a new piece), the guarantee on the PityTrips-th trip of PityMin or more in a row without a find; optionally
    A.11.3's happy-stay rolls (stay_per_day of them a day, counted toward the first target only). Returns, per
    target, the sorted days at which it was reached (math.inf when not within `days`)."""
    rng = random.Random(seed)
    E = EXP
    res = {k: [] for k in targets}
    trips = [(m / 1440, "trip", L) for m, L in ends]
    for _ in range(runs):
        found, miss_long, stay_miss = 0, 0, 0
        reached = {}
        events = trips
        if stay_per_day > 0:
            events = list(trips)
            for d in range(days):
                events += [(d + rng.random(), "stay", 0) for _ in range(exp_poisson(rng, stay_per_day))]
            events.sort()
        for when, kind, L in events:
            if found >= max(targets):
                break
            if kind == "stay":
                if found >= targets[0]:
                    continue
                stay_miss += 1
                hit = rng.random() < E["StayFind"] or stay_miss >= E["StayPity"]
                if hit:
                    stay_miss = 0
            else:
                p = min(1.0, E["Lengths"][L * 60] * chance_mult)
                long_ = L * 60 >= E["PityMin"]
                hit = rng.random() < p or (long_ and miss_long + 1 >= E["PityTrips"])
                if long_:
                    miss_long = 0 if hit else miss_long + 1
                elif hit:
                    miss_long = 0
            if hit:
                found += 1
                for k in targets:
                    if found == k:
                        reached[k] = when
        for k in targets:
            res[k].append(reached.get(k, math.inf))
    return {k: sorted(v) for k, v in res.items()}


def exp_inputs(sims, minute):
    """Per seed, the Wing and income at `minute` of play (None = the run's end): (location, rates desc, income $/s)."""
    out = []
    for s in sims:
        if not s.wing_log:
            continue
        if minute is None:
            out.append(s.wing_log[-1][1:])
            continue
        pts = [p for p in s.wing_log if p[0] <= minute * 60]
        if pts and s.end >= minute * 60:
            out.append(pts[-1][1:])
    return out


def fdays(x):
    if x is None or x == math.inf:
        return "—"
    return f"{x:.1f} d" if x < 10 else f"{x:.0f} d"


def exp_report(G, sims):
    R = G["Residents"]
    off, cap, nm, xpw = R["OfflineFraction"], R["OfflineCap"], R["NightManagerCap"], R["LevelXpPerMinute"]
    E = EXP
    lens = sorted(E["Lengths"])
    lname = lambda L: f"{L // 3600} h" if L >= 3600 else f"{L // 60} min"
    out = ["", "## Expeditions what-if (GDD A.11.2, revised 2026-10-21; numbers PLACEHOLDER, not in src/)", ""]
    out.append("Rules as the draft states them: the trip pays Pay x what its party would have earned by staying, "
               "counted as staying counts (Wing rate while playing, offline rate while away, nothing past the cap). "
               f"EXP = Pay {E['Pay']}, party {E['Party']}, lengths/chances "
               + ", ".join(f"{lname(L)} {p:.0%}" for L, p in sorted(E['Lengths'].items()))
               + f", guarantee on the {E['PityTrips']}th trip of {lname(E['PityMin'])}+ without a find, +{E['Match']:.0%} a matching resident, "
               f"{E['XpPerHour']} XP/h away, {E['PiecesPerLocation']} pieces a location; offline {off:.0%} of the rate to "
               f"{cap // 3600} h ({nm // 3600} h with Night Manager), Wing XP {xpw}/min while playing (Constants).")
    # the stages
    out += ["", "### The Wing at each stage (medians over seeds)", "",
            "| Stage | Location(s) | Wing residents | Wing rate/min | Best 3/min (share) | Lowest 3/min | Income/min while playing |",
            "|---|---|---|---|---|---|---|"]
    stage_in = {}
    for m in EXP_STAGES:
        ins = exp_inputs(sims, m)
        if len(ins) <= len(sims) / 2:
            continue
        stage_in[m] = ins
        md = lambda f: statistics.median(f(x) for x in ins)
        top = lambda x: sum(x[1][:E["Party"]])
        low = lambda x: sum(x[1][-E["Party"]:])
        tot = lambda x: sum(x[1])
        name = "rebirth-ready" if m is None else f"{m} min"
        out.append(f"| {name} | {','.join(str(x[0]) for x in ins)} | {md(lambda x: len(x[1])):.0f} | {money(md(tot) * 60)} | "
                   f"{money(md(top) * 60)} ({md(lambda x: top(x) / tot(x) if tot(x) else 0):.0%}) | {money(md(low) * 60)} | {money(md(lambda x: x[2]) * 60)} |")
    # the day coefficients
    coef = {}
    for name, n, s in EXP_PROFILES:
        for L in lens:
            for pol in ("logout", "busy"):
                for leak in (False, True):
                    for c in (cap, nm):
                        if c == nm and leak:
                            continue
                        coef[(n, s, L, pol, leak, c)] = exp_days(n, s, c, L, pol, leak, 14, off, xpw)

    def cash(ins, n, s, L, pol="logout", leak=False, c=cap, pay=None, match=0, party="top"):
        """Per day: (a) the Wing's cash, (b) with trips, the day's whole cash in (a) (play income + offline)."""
        k = coef[(n, s, L, pol, leak, c)]
        W = ins[1]
        Pn = E["Party"]
        pr = sum(W[:Pn]) if party == "top" else sum(W[-Pn:])
        rest = sum(W) - pr
        pay = E["Pay"] if pay is None else pay
        a = k["stay"] * sum(W)
        b = pay * (1 + E["Match"] * match) * k["counted"] * pr + k["party"] * pr + k["stay"] * rest
        day = ins[2] * 60 * n * s + (k["stay"] - 60 * n * s) * sum(W)
        return a, b, day

    out += ["", "### (a) staying against (b) the best three on a trip at every logout: cash a day (medians over seeds)", "",
            "The Wing's cash only (the guests pay the same either way). 'Offline (a)' is what the Wing earns while the player is away; "
            "'Δ' is (b) − (a) a day, and its share of the whole day's cash in (a) (play income + offline). "
            "'3 matching' reads the +20 % a matching resident as on the reward (x1.6 for three); 'leak' is the code's "
            "welcomeBack counting a party back before the login for the whole absence.", "",
            "| Player | Away each time | Stage | Play income/day | Offline (a)/day | Δ 30 min trip | Δ 2 h trip | Δ 8 h trip | Δ 8 h, 3 matching | Δ 8 h, leak | Trips/day 30m/2h/8h |",
            "|---|---|---|---|---|---|---|---|---|---|---|"]
    for name, n, s in EXP_PROFILES:
        H = 1440 // n - s
        for m, ins_all in stage_in.items():
            sname = "rebirth-ready" if m is None else f"{m} min"
            row = []
            md = lambda f: statistics.median(f(x) for x in ins_all)
            play = md(lambda x: x[2] * 60 * n * s)
            offa = md(lambda x: cash(x, n, s, lens[0])[0] - sum(x[1]) * 60 * n * s)
            for L in lens:
                d = md(lambda x: cash(x, n, s, L)[1] - cash(x, n, s, L)[0])
                sh = md(lambda x: (cash(x, n, s, L)[1] - cash(x, n, s, L)[0]) / cash(x, n, s, L)[2])
                row.append(f"{money(d)} ({sh:+.1%})")
            Lb = lens[-1]
            dm = md(lambda x: cash(x, n, s, Lb, match=3)[1] - cash(x, n, s, Lb, match=3)[0])
            dl = md(lambda x: cash(x, n, s, Lb, leak=True)[1] - cash(x, n, s, Lb, leak=True)[0])
            shl = md(lambda x: (cash(x, n, s, Lb, leak=True)[1] - cash(x, n, s, Lb, leak=True)[0]) / cash(x, n, s, Lb)[2])
            trips = "/".join(f"{coef[(n, s, L, 'logout', False, cap)]['trips']:.1f}" for L in lens)
            out.append(f"| {name} | {H // 60}:{H % 60:02d} | {sname} | {money(play)} | {money(offa)} | " + " | ".join(row)
                       + f" | {money(dm)} | {money(dl)} ({shl:+.1%}) | {trips} |")
    # the ratio, independent of the stage
    out += ["", "The same as a ratio, the same at every stage: what the party brings home a day with trips over what it "
            "brings by staying (1.00 = equal; Pay 1.5, no matching).", "",
            "| Player | Policy | 30 min | 2 h | 8 h | 8 h, leak | 8 h, Night Manager (8 h cap) | Party XP/day: stay → 8 h trips |",
            "|---|---|---|---|---|---|---|---|"]
    for name, n, s in EXP_PROFILES:
        for pol in ("logout", "busy"):
            def ratio(L, leak=False, c=cap):
                k = coef[(n, s, L, pol, leak, c)]
                return (E["Pay"] * k["counted"] + k["party"]) / k["stay"]
            k8 = coef[(n, s, lens[-1], pol, False, cap)]
            out.append(f"| {name} | {pol} | " + " | ".join(f"{ratio(L):.2f}" for L in lens)
                       + f" | {ratio(lens[-1], True):.2f} | {ratio(lens[-1], c=nm):.2f} | {k8['xa']:.0f} → {k8['xb']:.0f} |")
    # the finds
    rh = []
    for s_ in sims:
        t1 = s_.events.get("open_2", s_.end)
        if t1:
            rh.append(s_.rare_happy.get(1, 0) / (t1 / 60))
    r1 = statistics.median(rh) if rh else 0
    out += ["", "### The finds' pace (Monte Carlo, 1000 runs, 120 days; median and 90th percentile, days from the first trip)", "",
            f"A location's {E['PiecesPerLocation']} pieces, and all {3 * E['PiecesPerLocation']} (three locations, one after another), by trips "
            f"at every logout ('logout') or resent whenever one ends while playing ('busy'). 'With stays' adds A.11.3's roll "
            f"({E['StayFind']:.0%} a happy stay of a Rare-or-better guest, guaranteed after {E['StayPity']}) at the rate the run measured at "
            f"Haunted Manor, {r1:.2f} such stays a minute of play, to the first location's {E['PiecesPerLocation']} (the same pool). "
            "'x1.6' reads the +20 % a matching resident as on the find's chance, three matching.", "",
            "| Player | Policy | Trip | Trips/day | 5 pieces | 5, with stays | 5, x1.6 | All 15 |",
            "|---|---|---|---|---|---|---|---|"]
    q = lambda xs, f: xs[min(len(xs) - 1, int(f * len(xs)))]
    cell = lambda xs: f"{fdays(q(xs, .5))} ({fdays(q(xs, .9))})"
    for name, n, s in EXP_PROFILES:
        for pol in ("logout", "busy"):
            for L in lens:
                k = exp_days(n, s, cap, L, pol, False, 120, off, xpw)
                f = exp_finds(k["ends"], 120)
                fs = exp_finds(k["ends"], 120, stay_per_day=r1 * n * s, targets=(5,))
                fm = exp_finds(k["ends"], 120, chance_mult=1 + 3 * E["Match"], targets=(5,))
                out.append(f"| {name} | {pol} | {lname(L)} | {k['trips']:.1f} | {cell(f[5])} | {cell(fs[5])} | {cell(fm[5])} | {cell(f[15])} |")
    for name, n, s in EXP_PROFILES:
        fs = exp_finds([], 120, stay_per_day=r1 * n * s, targets=(5,))
        out.append(f"| {name} | no trips (stays alone) | — | 0 | — | {cell(fs[5])} | — | — |")
    # what would make it a choice: the Pay sweep
    dec = {}
    for L in (1, 2, 3):
        prices = sorted(d["cost"] for d in G["Loc"][L]["Decor"].values() if d.get("location") == L and not d.get("furniture"))
        dec[L] = (statistics.median(prices), prices[-1]) if prices else (0, 0)
    out += ["", "### What Pay would make it a choice (the trip's cash against its find)", "",
            "Δ a day with the best three and with the lowest three sent (the finds do not depend on who goes), and what one find "
            "costs in cash given up (−Δ / expected finds a day; '—' when the trip gains cash) and in minutes of play income at that stage. "
            "A shop decor piece of the location costs (median / dearest) "
            + ", ".join(f"L{L} {money(a)} / {money(b)}" for L, (a, b) in dec.items())
            + "; a set piece is worth a decor piece of twice its listed price (A.11.3).", "",
            "| Player | Trip | Stage | Pay | Δ/day, best 3 | Δ/day, lowest 3 | A find costs (best 3) | … in play minutes | A find costs (lowest 3) | … in play minutes |",
            "|---|---|---|---|---|---|---|---|---|---|"]
    for name, n, s, L in ((EXP_PROFILES[0][0], 1, 20, lens[-1]), (EXP_PROFILES[2][0], 4, 30, lens[1]), (EXP_PROFILES[2][0], 4, 30, lens[-1])):
        k = coef[(n, s, L, "logout", False, cap)]
        fpd = k["trips"] * E["Lengths"][L]
        for m in (60, None):
            if m not in stage_in:
                continue
            ins_all = stage_in[m]
            md = lambda f: statistics.median(f(x) for x in ins_all)
            inc = md(lambda x: x[2] * 60)
            for pay in EXP_PAY_SWEEP:
                dt = md(lambda x: cash(x, n, s, L, pay=pay)[1] - cash(x, n, s, L, pay=pay)[0])
                dl = md(lambda x: cash(x, n, s, L, pay=pay, party="low")[1] - cash(x, n, s, L, pay=pay, party="low")[0])
                cf = lambda d: (money(-d / fpd), f"{-d / fpd / inc:.1f}") if d < -1e-9 and fpd > 0 else ("—", "—")
                a1, a2 = cf(dt)
                b1, b2 = cf(dl)
                sname = "rebirth-ready" if m is None else f"{m} min"
                out.append(f"| {name} | {lname(L)} | {sname} | {pay:g} | {money(dt)} | {money(dl)} | {a1} | {a2} | {b1} | {b2} |")
    return out


def main():
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass
    ap = argparse.ArgumentParser()
    ap.add_argument("--seeds", type=int, default=4)
    ap.add_argument("--hours", type=float, default=8)
    ap.add_argument("--skip-tutorial", action="store_true", help="also run the chain with the tutorial skipped")
    ap.add_argument("--out", default=None)
    ap.add_argument("--set", action="append", default=[], metavar="Section.Key=value",
                    help="a what-if, in memory only: override a value read from Constants (e.g. Chain.OpenCost.2=500000)")
    ap.add_argument("--size", choices=("roi", "min", "full"), default="roi",
                    help="the player's size policy for new rooms in rule 6 (a policy what-if, not a value)")
    ap.add_argument("--expeditions", action="store_true",
                    help="the Expeditions what-if (GDD A.11.2, not built): (a) the Wing offline against (b) trips, and the finds' pace")
    ap.add_argument("--exp-set", action="append", default=[], metavar="Key=value",
                    help="with --expeditions: override one of EXP's PLACEHOLDER numbers in memory (e.g. Pay=0.75)")
    a = ap.parse_args()
    global SIZE_POLICY, EXPEDITIONS
    SIZE_POLICY = a.size
    EXPEDITIONS = a.expeditions
    G = load_game()
    if EXPEDITIONS:
        exp_check(G)
        for spec in a.exp_set:
            k, _, v = spec.partition("=")
            if k not in EXP or isinstance(EXP[k], dict):
                raise ParseError(f"--exp-set {spec}: no such number in EXP")
            EXP[k] = float(v) if "." in v else int(v)
            print(f"  EXPEDITIONS WHAT-IF (memory only): {k} = {v}", file=sys.stderr)
    for spec in a.set:
        path, _, val = spec.partition("=")
        keys = path.split(".")
        node = G
        for k in keys[:-1]:
            node = node[int(k) if k.isdigit() else k]
        last = int(keys[-1]) if keys[-1].isdigit() else keys[-1]
        if last not in node:
            raise ParseError(f"--set {spec}: no such value")
        node[last] = float(val) if "." in val or "e" in val else int(val)
        print(f"  WHAT-IF (memory only): {path} = {val}", file=sys.stderr)
    results = []
    for tut in ((True, False) if a.skip_tutorial else (True,)):
        sims = []
        for i in range(a.seeds):
            sims.append(Sim(G, 1000 + i, tutorial=tut, hours=a.hours).run())
            print(f"  seed {1000 + i} ({'tutorial' if tut else 'skipped'}): rebirth-ready {fmt(sims[-1].rebirth_ready)}", file=sys.stderr)
        results.append(summarize(G, sims, "with tutorial" if tut else "tutorial skipped"))
    lines = render(G, results, a)
    if EXPEDITIONS:
        if a.exp_set:
            lines += ["", "**EXPEDITIONS WHAT-IF, numbers changed in memory only:** " + ", ".join(a.exp_set)]
        lines += exp_report(G, results[0]["sims"])
    text = "\n".join(lines)
    print(text)
    if a.out:
        with open(os.path.join(ROOT, a.out) if not os.path.isabs(a.out) else a.out, "w", encoding="utf-8") as f:
            f.write(text + "\n")


# GDD §6.3 (his targets, 2026-10-20): minutes, measured as the GDD words them.
TARGETS = {
    "five_star_1": (30, 60),  # 5★ at Haunted Manor: 30-60 min of active play
    "d2": (60, 90),  # 5★ at Frostfang Lodge: a further 60-90 min
    "d3": (90, 120),  # 5★ at Bayou Spa: a further 90-120 min
    "rebirth_ready": (180, 270),  # rebirth available: about 3-4.5 h
}
CAT_NAMES = ["Comfort", "Service", "Cleanliness", "Fun", "Style"]


def chain_row(s, G):
    e = s.events
    out = {}
    nL = G["Chain"]["Locations"]
    for L in range(1, nL + 1):
        out[f"five_star_{L}"] = e.get(f"five_star_{L}")
        if L > 1:
            out[f"open_{L}"] = e.get(f"open_{L}")
            out[f"afford_open_{L}"] = e.get(f"afford_open_{L}")
    for L in range(2, nL + 1):
        a, b = out.get(f"five_star_{L - 1}"), out.get(f"five_star_{L}")
        out[f"d{L}"] = b - a if a is not None and b is not None else None
        o = out.get(f"open_{L}")
        out[f"in{L}"] = b - o if b is not None and o is not None else None
        out[f"save{L}"] = o - a if o is not None and a is not None else None
    out["in1"] = out.get("five_star_1")
    out["rebirth_ready"] = s.rebirth_ready
    return out


def render(G, results, a):
    C, E = G["Chain"], G["Economy"]
    nL = C["Locations"]
    names = {1: "Haunted Manor", 2: "Frostfang Lodge", 3: "Bayou Spa"}
    L_ = []
    if a.size != "roi":
        L_.append(f"**POLICY WHAT-IF:** new rooms in rule 6 always at their {a.size} size.")
        L_.append("")
    if a.set:
        L_.append("**WHAT-IF, values changed in memory only (nothing in src/):** " + ", ".join(a.set))
        L_.append("")
    L_.append(f"Model: {a.seeds} seeds per scenario, up to {a.hours:g} h of play; medians over seeds ('—' = not reached in "
              f"most seeds). Floor cap Chain.floorCap(0) = {floor_cap(G, 0)}; opening "
              + ", ".join(f"{names.get(k, k)} {money(v)}" for k, v in sorted(C['OpenCost'].items()))
              + f"; background share {C['BackgroundShare']:.0%}; rebirth needs {C['RebirthRating']}★ on all {nL}.")
    for R in results:
        sims = R["sims"]
        rows = [chain_row(s, G) for s in sims]
        L_.append("")
        L_.append(f"### The chain, {R['label']}")
        L_.append("")
        hdr = ["Seed", "5★ L1"]
        for L in range(2, nL + 1):
            hdr += [f"L{L} affordable", f"Open L{L}", f"5★ L{L}"]
        hdr += ["Rebirth-ready"]
        L_.append("| " + " | ".join(hdr) + " |")
        L_.append("|" + "---|" * len(hdr))

        def cells(r):
            c = [fmt(r["five_star_1"])]
            for L in range(2, nL + 1):
                c += [fmt(r[f"afford_open_{L}"]), fmt(r[f"open_{L}"]), fmt(r[f"five_star_{L}"])]
            return c + [fmt(r["rebirth_ready"])]

        for s, r in zip(sims, rows):
            L_.append(f"| {s.seed} | " + " | ".join(cells(r)) + " |")
        medr = {k: med([r[k] for r in rows]) for k in rows[0]}
        L_.append("| **median** | " + " | ".join(f"**{x}**" for x in cells(medr)) + " |")
        L_.append("")

        def verdict(v, lo, hi):
            if v is None or v == math.inf:
                return "not reached"
            m = v / 60
            return "yes" if lo <= m <= hi else (f"no, {m - hi:+.0f} min over" if m > hi else f"no, {lo - m:.0f} min under")

        L_.append("| §6.3 target | Target | Median | Per seed | Meets? |")
        L_.append("|---|---|---|---|---|")
        tgt = [("5★ at Haunted Manor (from the start)", "five_star_1"),
               ("5★ at Frostfang Lodge (after 5★ at Haunted Manor)", "d2"),
               ("5★ at Bayou Spa (after 5★ at Frostfang Lodge)", "d3"),
               ("Rebirth available (5★ on all three)", "rebirth_ready")]
        for label, k in tgt:
            lo, hi = TARGETS[k]
            per = ", ".join(fmt(r[k]) for r in rows)
            L_.append(f"| {label} | {lo}–{hi} min | {fmt(medr[k])} | {per} | {verdict(medr[k], lo, hi)} |")
        L_.append("")
        L_.append("Where the time goes, per location (medians): **saving** = from 5★ at the hotel before to the opening "
                  "(the open price); **in the hotel** = from its opening to its 5★.")
        L_.append("")
        L_.append("| Location | Saving for it | In the hotel to 5★ | 3★ / 4★ / 4.5★ after opening | Last to reach 95: categories, reviews ≥ 4.5 (after opening) |")
        L_.append("|---|---|---|---|---|")
        for L in range(1, nL + 1):
            start = (lambda s: 0) if L == 1 else (lambda s, L=L: s.events.get(f"open_{L}"))
            rel = lambda s, key: (s.events[key] - start(s)) if s.events.get(key) is not None and start(s) is not None else None
            ms = " / ".join(fmt(med([rel(s, f"rating_{x}_L{L}") for s in sims])) for x in (3, 4, 4.5))
            parts = []
            for i, nm in list(enumerate(CAT_NAMES)) + [("reviews", "reviews ≥ 4.5")]:
                v = med([(s.cat_first.get((L, i)) - start(s)) if s.cat_first.get((L, i)) is not None and start(s) is not None else None for s in sims])
                parts.append((v if v is not None else math.inf, nm))
            parts.sort(key=lambda x: -x[0])
            last = ", ".join(f"{nm} {fmt(v) if v != math.inf else '—'}" for v, nm in parts[:3])
            save = fmt(medr.get(f"save{L}")) if L > 1 else "—"
            L_.append(f"| {L} {names.get(L, '')} | {save} | {fmt(medr[f'in{L}'])} | {ms} | {last} |")
        L_.append("")
        L_.append("Snapshots (medians over seeds): cash and income at each moment. Income is all of it per minute "
                  "(guests, tips, Wing, background); 'measured' is the played hotel's ChainService rate, 'background' what the hotels left pay.")
        L_.append("")
        L_.append("| Moment | Time | Cash | Run cash | Income/min | Measured rate/min | Background/min | Rooms | Floors | Tiles (floor 1 / 2) | Rating | Categories (C/S/Cl/F/St) | Mean review | Mean satisfaction | Rooms' bars Size/Furniture/Decor | Cells / minimum |")
        L_.append("|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|")
        keys = []
        for L in range(1, nL + 1):
            if L > 1:
                keys += [f"afford_open_{L}", f"leave_{L - 1}", f"open_{L}"]
            keys.append(f"five_star_{L}")
        keys.append("rebirth_ready")
        for k in keys:
            snaps = [s.at_event.get(k) for s in sims]
            snaps = [x for x in snaps if x]
            if len(snaps) <= len(sims) / 2:
                L_.append(f"| {k} | — | | | | | | | | | | | | | | |")
                continue
            md = lambda f: statistics.median(f(x) for x in snaps)
            cats = "/".join(f"{md(lambda x, i=i: x['cats'][i]):.0f}" for i in range(5))
            L_.append(f"| {k} | {fmt(md(lambda x: x['t']))} | {money(md(lambda x: x['cash']))} | {money(md(lambda x: x['run_cash']))} | "
                      f"{money(md(lambda x: x['inc']))} | {money(md(lambda x: x['rate']))} | {money(md(lambda x: x['bg']))} | "
                      f"{md(lambda x: x['rooms']):.0f} | {md(lambda x: x['floors']):.0f} | "
                      f"{md(lambda x: x['tiles'].get(1, 0)):.0f} / {md(lambda x: x['tiles'].get(2, 0)):.0f} | "
                      f"{md(lambda x: x['rating']):.1f}★ | {cats} | {md(lambda x: x['reviews']):.2f} | {md(lambda x: x['sat']):.0f} | "
                      + "/".join(f"{md(lambda x, i=i: x['bars'][i]):.2f}" for i in range(3)) + f" | {md(lambda x: x['cells']):.2f} |")
        L_.append("")
        L_.append("§6.2 rule of thumb per location (meaningful purchases after its first 5 minutes; minutes of income each; "
                  "longest gap between meaningful purchases, median over seeds):")
        L_.append("")
        for L in range(1, nL + 1):
            mins, gaps = [], []
            for s in sims:
                t0 = 0 if L == 1 else s.events.get(f"open_{L}")
                if t0 is None:
                    continue
                t1 = s.events.get(f"open_{L + 1}", s.end)
                ps = [p for p in s.purchases if p[6] == L and p[5] and p[1] != "open"]
                mins += [p[3] / p[4] for p in ps if p[4] > 0 and p[0] >= t0 + 300]
                ts = [p[0] for p in ps]
                g = [b - a_ for a_, b in zip([t0] + ts, ts + [t1])]
                gaps.append(max(g) if g else None)
            m = sorted(mins)
            if m:
                q = lambda p: m[min(len(m) - 1, int(p * len(m)))]
                in_band = sum(1 for x in m if 2 <= x <= 5) / len(m)
                L_.append(f"- L{L}: n={len(m)}, median {q(.5):.2f} min (p10 {q(.1):.2f}, p90 {q(.9):.2f}, max {m[-1]:.1f}); "
                          f"in the 2–5 min band {in_band:.0%}; longest gap {fmt(med(gaps))}.")
        L_.append("")
        L_.append("Timeline (medians over the seeds still running; the location column lists each seed's):")
        L_.append("")
        L_.append("| Minute | Location | Rating | Rooms | Income/min | Background/min | Cash |")
        L_.append("|---|---|---|---|---|---|---|")
        marks = [5, 15, 30, 45, 60, 75, 90, 105, 120, 150, 180, 210, 240, 270, 300, 330, 360, 420, 480]
        for (m, inc, rat, rooms, cash, bg, locs, n) in timeline_rows(sims, marks):
            L_.append(f"| {m} | {','.join(str(x) for x in locs)} | {rat:.1f}★ | {rooms:.0f} | {money(inc)} | {money(bg)} | {money(cash)} |")
    # the first minutes at Haunted Manor (§6.3's early rows), as before
    L_.append("")
    L_.append("### The first minutes at Haunted Manor (§6.3)")
    L_.append("")
    L_.append("| §6.3 moment | Target | " + " | ".join(R["label"] for R in results) + " |")
    L_.append("|---|---|" + "---|" * len(results))
    row = lambda name, tgt, f: L_.append(f"| {name} | {tgt} | " + " | ".join(f(R) for R in results) + " |")
    row("First room bought (the start room stands from 0:00, free)", "0:10–0:30", lambda R: f"{fmt(R['first_room'])} (the second room)")
    row("First guest pays", "by 1:00", lambda R: fmt(R["first_pays"]))
    row("First bus", "by 2:00", lambda R: f"{fmt(R['first_bus'])} (first bus guest at the desk {fmt(R['first_bus_guest'])})")
    row("3–5 purchases", "by 5:00", lambda R: f"{R['buys5_all']:.0f} ({R['buys5_meaningful']:.0f} meaningful)")
    row("First resident", "3:00–5:00", lambda R: fmt(R["first_resident"]))
    row("First rare: Vampire Count checks in", "10:00–15:00", lambda R: fmt(R["vamp_checkin"]))
    row("… Vampire Count resident", "(no longer a rebirth condition)", lambda R: fmt(R["vamp_resident"]))
    row("Mean bus size", "", lambda R: f"{R['bus_size']:.1f}")
    return L_


if __name__ == "__main__":
    try:
        main()
    except ParseError as e:
        print(f"balance_model: {e}", file=sys.stderr)
        sys.exit(2)
