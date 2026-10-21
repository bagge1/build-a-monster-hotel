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
Commons, Economy's cost curves and tile ladder, Furnish's tier points, Stay's
tip and review, Rating's categories, staff coverage and stars, the tutorial's
voucher, free tiles, booked Vampire and friendship, the chain's opening,
background earnings, measured rate, floor cap and rebirth check), the model
stops with an error naming the line, rather than silently simulating an old
rule.

Run:  python tools/balance_model.py [--seeds 4] [--hours 8] [--skip-tutorial] [--out <file for the raw tables>]

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
    gone). The tutorial's free Commons, Vampire Count and Coffin Suite happen
    once, at Haunted Manor.
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
  plus its first room while the played hotel stands at 5★. The model never
  travels back.

WHAT IS SIMULATED (as the code implements it, 2026-10-19 evening)
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
    the till, payRate = speciesPay x tierPay x mutation x milestone(type count),
    fixed at check-in; one request in the middle half of the stay, open
    RequestWindow s; satisfaction, tip, review, friendship at check-out; the
    room is then dirty until cleaned. Mutations are rolled from Mutations.luau.
  - Tiers from furnishing (Furnish, GDD 5.4): a room's decor is worth its
    price x PointsPerCash; T2/T3 at TierPoints scaled by cells over
    TierPointsCells.
  - The rating (HotelService.inputs, Rating): recomputed every 5 s from tiers
    (Comfort full at MaxTier), preference share, desk waits, requests, dirty
    rooms, amenities, decor items and room types, plus staff coverage (Room
    Service's efficiency over rooms / RoomsPerStaff) and the share of recent
    cleanings within CleanOnTime; averaged with the last ReviewsKept reviews,
    rounded to a half. Unlocks (Unlocks.met) are permanent once met.
  - Residents (ResidentService): +1 friendship per happy stay, move-in at the
    rarity's threshold or by the early chance; only the tutorial Slime needs
    TutorialFriendship; the tutorial's guests are happy by force. A resident in the
    Wing earns EarnFraction of its species' pay into the till; one on staff
    earns nothing but works (Room Service modelled; the others not used).
  - The Monster Book: a species found pays SpeciesFoundPaySeconds of its pay.
  - The tutorial (TutorialService): the tutorial Slime FirstGuestDelay s after
    the first room, walking in (TUTORIAL_WALK s); the Goal card's free Coffin
    Suite (voucher); a Vampire Count booked on the next bus once 2 buses have
    passed since the Goal card, the tutorial is Done and a Coffin Suite stands
    vacant (it skips browsing).
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
    the rest is hallway. Shapes are not packed: cells are counted.

WHAT IS NOT SIMULATED (stated so the numbers are read honestly)
  Hunter Night (its reward is +5 min of income every 90 min), events and
  seasonal mutations, daily rewards, likes/friends bonus, passes, the Moon
  Tree, Prestige Stars (none before the first rebirth), Book family bonuses
  (+5 %), offline earnings, other players on the street (they split the bus),
  pitching, Front Desk / Housekeeping / Bellhop / Entertainment staff,
  selling, moving rooms, replacing decor, hallway decor, windows, residents'
  perks, travelling back to a hotel left, the time Travel itself takes, and
  the room shapes (cells are counted, not packed).

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

THE GREEDY BUYING POLICY (checked every second; one purchase per check)
  1. Tutorial: first room at FIRST_ROOM_AT s; the second room as soon as it is
     affordable; the free Coffin Suite the moment the Goal card gives it. At a
     newly opened hotel, its cheapest room with no unlock at once.
  2. Goal: once the Coffin Suite is unlocked and none stands, save for it if it
     costs at most 20 minutes of income; then, while no Vampire Count lives
     in the Wing, save for its matching decor (darkness, organ music) when a
     piece costs at most 10 minutes of income.
  3. Decor that matches the room's guests: for each room, the best set of up
     to three decor pieces for the species its type serves (weighted by how
     often they come), given the amenities on its floor; a missing piece is
     bought when it costs at most 90 s of income (or 30 % of cash). Empty
     slots get the cheapest piece for Style when it costs <= 20 s of income.
     Every piece adds tier points.
  4. Amenities: up to three per floor that has rooms (satisfaction counts
     three on a guest's floor), and more while the hotel's Fun is short of
     100 (ceil(100 / FunPerAmenity) in all: with two floors three a floor is
     not enough, 2026-10-21); the most useful tags first, a duplicate when no
     new type is left; each bought, with the tiles it needs, when it costs
     <= 3 minutes of income.
  5. The first room of a newly unlocked type, when it costs <= 5 minutes of
     income.
  6. Return on cost: every new room of an owned type whose rooms are mostly
     full (mean occupancy >= ROOM_FULL) or whose next room reaches a
     milestone, and every tier upgrade, is scored by its expected extra income per second (observed occupancy of
     that room or type, the species' observed pay, tier +50 %, the milestone
     doubling when the next room reaches 5/10/25) divided by its cost
     (plus the tiles or floor it needs when there is no space). A tier
     upgrade is the decor still needed for the next tier, bought as filler
     pieces of FILLER_COST. The best is bought when affordable; otherwise the
     player saves for it (rules 2-5 still run).
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
FIRST_ROOM_AT = 15  # s: the player places the first room
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
FILLER_COST = 60  # $ per filler decor item bought for tier points (Side Table, Record Player)


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
    ("src/shared/Furnish.luau", "out[i] = math.ceil(need * scale)"),
    ("src/shared/Furnish.luau", "return if d then math.floor(d.cost * E.PointsPerCash) else 0"),
    ("src/server/GuestService.luau", "g.requestAt = now + stay * (0.25 + 0.5 * rng:NextNumber())"),
    ("src/server/GuestService.luau", "g.payRate * S.RequestTipSeconds"),
    ("src/shared/Economy.luau", "piece.cost * E.RoomCostGrowth ^ owned + 0.5"),
    ("src/shared/Economy.luau", "return 1 + E.TierPayBonus * (tier - 1)"),
    ("src/shared/Economy.luau", "* Constants.Residents.EarnFraction"),
    ("src/shared/Stay.luau", "math.floor(payRate * stay * (satisfaction / 100) * S.TipFraction)"),
    ("src/shared/Stay.luau", "math.clamp(1 + math.floor(satisfaction / 25), 1, 5)"),
    ("src/shared/Stay.luau", "math.min(S.SatisfactionAmenityMax, S.SatisfactionPerAmenity * i.amenities)"),
    # Built rooms (GDD A.12, 2026-10-21): Comfort's room part is Rooms.comfortPoints over the ready rooms'
    # bars, and a room's pay/stay/satisfaction/friendship come from Rooms.bonuses. NOT YET MODELLED here:
    # the model still runs on tiers (its numbers for Comfort and pay are the tiers' until it is updated).
    ("src/shared/Rating.luau", "local comfort = Rooms.comfortPoints(i.roomBars) + 40 * i.prefsShare"),
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
    ("src/server/BusService.luau", "nextList, nextGuaranteed = draw(busIndex + 1, now, now + interval)"),
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
    for key in ["Rarity", "Economy", "Bus", "Scoring", "Stay", "Tutorial", "Rating", "Residents", "Staff", "Book", "Chain", "Grid"]:
        G[key] = assignment(C, rf"^Constants\.{key}")
        if not isinstance(G[key], dict):
            raise ParseError(f"{C}: Constants.{key} is not a table")
    for r in ["Common", "Uncommon", "Rare", "Epic", "Legendary", "Mythic"]:
        for k in ["pay", "stay", "friendship", "weight", "moveInChance"]:
            need(need(G["Rarity"], r, C), k, f"{C} Rarity.{r}")
    for sect, keys in {
        "Economy": ["StartCash", "BasePay", "LocationPayMultiplier", "RoomCostGrowth", "TierPayBonus", "MaxTier", "TierPoints", "TierPointsCells", "PointsPerCash",
                    "TileCost", "TileGrowth", "TileFloorFactor", "Milestones", "FloorCosts"],
        "Chain": ["Locations", "RebirthRating", "OpenCost", "BackgroundShare", "RateWindow", "StartFloorCap", "FloorCapMax"],
        "Grid": ["StartTiles", "TutorialTiles", "Cells"],
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
    G["Mutations"] = [(m["id"], m["chance"], m["pay"]) for m in muts if m.get("chance", 0) > 0]
    G["AllSpecies"] = {s["id"]: s for s in species}
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
        g["Decor"] = {d["id"]: d for d in decor if d.get("location") == L or (d.get("location") == 0 and d.get("always"))}
        g["Species"] = {s["id"]: s for s in species if s.get("location") == L}
        if not g["Species"]:
            raise ParseError(f"Species.luau: no species of location {L}")
        for sid, s in g["Species"].items():
            if s["room"] not in g["Pieces"]:
                raise ParseError(f"Species {sid}: room {s['room']} is not a location-{L} piece")
        if not any(p["kind"] == "Room" and not p.get("unlock") for p in g["Pieces"].values()):
            raise ParseError(f"Pieces.luau: location {L} has no room without an unlock (its first room)")
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
        self.E, self.S, self.R = G["Economy"], G["Stay"], G["Rating"]

    def piece_cost(self, pid, owned):
        return math.floor(self.G["Pieces"][pid]["cost"] * self.E["RoomCostGrowth"] ** owned + 0.5)

    def thresholds(self, pid):
        p = self.G["Pieces"][pid]
        scale = p["w"] * p["d"] / self.E["TierPointsCells"]
        return [math.ceil(n * scale) for n in self.E["TierPoints"]]

    def tier_of(self, pid, points):
        tier = 1
        for i, n in enumerate(self.thresholds(pid)):
            if points >= n:
                tier = i + 2
        return min(tier, self.E["MaxTier"])

    def tier_cost(self, room):
        """$ of decor still needed for the room's next tier (points = price x PointsPerCash)."""
        for n in self.thresholds(room.type):
            if room.points < n:
                return math.ceil((n - room.points) / self.E["PointsPerCash"])
        return None

    def tier_pay(self, tier):
        return 1 + self.E["TierPayBonus"] * (tier - 1)

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

    def satisfaction(self, prefs, tier, amen, rp, rs, rm, wait):
        S = self.S
        s = (S["SatisfactionBase"] + S["SatisfactionPerPreference"] * prefs + S["SatisfactionPerTier"] * (tier - 1)
             + min(S["SatisfactionAmenityMax"], S["SatisfactionPerAmenity"] * amen)
             + S["SatisfactionRequestPlayer"] * rp + S["SatisfactionRequestStaff"] * rs
             + S["SatisfactionRequestMissed"] * rm - self.wait_penalty(wait))
        return max(0, min(100, s))

    def tip(self, rate, stay, sat):
        return math.floor(rate * stay * (sat / 100) * self.S["TipFraction"])

    def review(self, sat):
        return max(1, min(5, 1 + math.floor(sat / 25)))

    def categories(self, tiers, prefs_share, mean_wait, checkins, req_share, rooms, dirty, amen, decor, types,
                   desk=0.0, room_service=0.0, housekeeping=0.0, on_time=0.0):
        R = self.R
        tm = sum(tiers) / len(tiers) if tiers else 0
        comfort = min(100, tm / self.E["MaxTier"] * 100) * 0.6 + 40 * prefs_share
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
    id: int
    type: str
    floor: int
    tier: int = 1
    decor: list = field(default_factory=list)
    points: int = 0
    filler: int = 0  # decor items bought only for tier points
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
    tier: int = 1
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
        self.tstep = "Build" if tutorial else "Done"
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
        self.amenities: list[tuple[str, int]] = []
        self.guests: list[Guest] = []
        self.pending_bus = []
        self.booked = []  # tutorial guests riding the next bus to this hotel
        self.reviews: deque = deque(maxlen=G["Stay"]["ReviewsKept"])  # data.reviews: each hotel its own
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
                                  "rating": self.rating, "reviews": statistics.fmean(self.reviews) if self.reviews else 0}

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
        used = sum(self.G["Pieces"][r.type]["w"] * self.G["Pieces"][r.type]["d"] for r in self.rooms if r.floor == f)
        return used + sum(self.G["Pieces"][a]["w"] * self.G["Pieces"][a]["d"] for a, af in self.amenities if af == f)

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

    def add_decor(self, r, d):
        r.decor.append(d)
        self.add_points(r, self.G["Decor"][d]["cost"])

    def add_points(self, r, cost):
        r.points += math.floor(cost * self.G["Economy"]["PointsPerCash"])
        r.tier = self.rules.tier_of(r.type, r.points)

    def floor_for(self, cells):
        for f in range(1, self.floors + 1):
            if self.floor_used(f) + cells <= self.floor_cap(f):
                return f
        return None

    def room_tags(self, room):
        tags = set()
        for d in room.decor:
            tags.update(self.G["Decor"][d]["tags"])
        for a, f in self.amenities:
            if f == room.floor:
                tags.update(self.G["Pieces"][a]["tags"])
        return tags

    def amen_on(self, f):
        return sum(1 for _, af in self.amenities if af == f)

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
                if best is None or m > bm or (m == bm and r.tier > best.tier):
                    best, bm = r, m
        return best

    def roll_mut(self):
        x, at = self.rng.random(), 0.0
        for mid, ch, pay in self.G["Mutations"]:
            at += ch
            if x < at:
                return mid, pay
        return None, 1.0

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
        g.tier = r.tier
        g.prefs = self.matched(g.sid, self.room_tags(r))
        g.amen = self.amen_on(r.floor)
        g.rate = self.rules.species_pay(g.sid) * self.rules.tier_pay(r.tier) * g.mut_pay * self.rules.milestone(self.type_count(r.type))
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
        sat = R.satisfaction(g.prefs, g.tier, g.amen, g.rp, g.rs, g.rm, g.waited)
        if g.happy_floor:
            sat = max(sat, g.happy_floor)
        stay = R.stay_len(g.sid)
        self.earn_till(R.tip(g.rate, stay, sat))
        self.reviews.append(R.review(sat))
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
            now = self.friendship.get(g.sid, 0) + 1
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
                stay = self.rules.stay_len(g.sid)
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
        if not self.tutorial or self.tstep in ("Build", "CheckIn", "Done") or self.tut_common_buses >= T["CommonBuses"]:
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
        tiers = [r.tier for r in self.rooms]
        dirty = sum(1 for r in self.rooms if r.state == "Dirty")
        decor = sum(len(r.decor) + r.filler for r in self.rooms)
        types = len({r.type for r in self.rooms})
        cats = self.rules.categories(
            tiers,
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
        meaningful = kind in ("room", "tier", "floor", "tiles", "amenity") or (kind == "decor" and inc > 0 and cost >= inc)
        self.purchases.append((t, kind, what, cost, inc, meaningful, self.loc))

    def place_room(self, t, pid, free=False):
        cells = self.G["Pieces"][pid]["w"] * self.G["Pieces"][pid]["d"]
        f = self.floor_for(cells)
        if f is None:
            return False
        cost = 0 if free else self.rules.piece_cost(pid, self.type_count(pid))
        if cost > self.cash:
            return False
        self.buy(t, "room", pid, cost)
        occ = statistics.fmean([r.occ for r in self.rooms if r.type == pid]) if any(r.type == pid for r in self.rooms) else 0.5
        self.rooms.append(Room(self.next_id, pid, f, occ=occ))
        self.next_id += 1
        self.mark("first_room", t)
        self.mark(f"first_{pid}", t)
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
        floor_tags = set()
        for a, f in self.amenities:
            if f == room.floor:
                floor_tags.update(self.G["Pieces"][a]["tags"])
        w = self.species_weights(room.type)
        have = list(room.decor)
        free_slots = self.G["DecorSlots"] - len(have)
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

    def first_room(self):
        """The location's cheapest room with no unlock: what a new hotel places first."""
        rooms = [pid for pid, p in self.G["Pieces"].items() if p["kind"] == "Room" and not p.get("unlock")]
        return min(rooms, key=lambda pid: self.G["Pieces"][pid]["cost"])

    def open_price(self):
        """What opening the next location takes now (its price and its first room), or None at the last."""
        nxt = self.loc + 1
        if nxt > self.G0["Chain"]["Locations"]:
            return None
        g = self.G0["Loc"][nxt]
        first = min((p["cost"] for p in g["Pieces"].values() if p["kind"] == "Room" and not p.get("unlock")))
        return self.G0["Chain"]["OpenCost"][nxt] + first

    def policy(self, t):
        inc = max(self.income_rate(), 0.25)
        P = self.G["Pieces"]
        # 0. the chain: at 5 stars, save for the next location and open it once it is affordable
        saving = None
        price = self.open_price()
        if price is not None and self.tstep == "Done":
            if self.cash >= self.G0["Chain"]["OpenCost"][self.loc + 1]:
                self.mark(f"afford_open_{self.loc + 1}", t)
                self.snap(f"afford_open_{self.loc + 1}", t)
            if self.rating >= self.G0["Chain"]["RebirthRating"]:
                if self.cash >= price:
                    self.open_next(t)
                    return
                saving = (price - self.cash) / inc  # seconds still to save at the present income
        # 2. the goal: the tutorial guest's room (the Coffin Suite) and its decor, at Haunted Manor
        goal = self.G["AllSpecies"][self.G["RebirthResident"]]["room"]
        if goal in P and self.buildable(goal) and self.type_count(goal) == 0:
            cells = P[goal]["w"] * P[goal]["d"]
            if self.vouchers.get(goal):
                if self.place_room(t, goal, free=True):
                    self.vouchers[goal] -= 1
                    return
                if self.floor_for(cells) is None:
                    self.expand(t, cells)  # the goal card: save for the tiles the free suite needs
                    return
            cost = self.rules.piece_cost(goal, 0)
            if cost <= 20 * 60 * inc:
                if self.cash >= cost:
                    if self.floor_for(cells) is None:
                        self.expand(t, cells)
                        return
                    self.place_room(t, goal)
                return  # saving for it
        has_goal = any(r["sid"] == self.G["RebirthResident"] for r in self.residents)
        for r in self.rooms:
            if r.type == goal and not has_goal:
                for d in self.decor_plan(r):
                    c = self.G["Decor"][d]["cost"]
                    if c > 10 * 60 * inc:
                        break  # out of reach for now: rule 3 buys it when it is cheap
                    if self.cash >= c:
                        self.add_decor(r, d)
                        self.buy(t, "decor", d, c)
                        return
                    return  # saving for it
        # 3. matching decor
        for r in self.rooms:
            for d in self.decor_plan(r):
                c = self.G["Decor"][d]["cost"]
                if c <= self.cash and (c <= 90 * inc or c <= 0.3 * self.cash):
                    self.add_decor(r, d)
                    self.buy(t, "decor", d, c)
                    return
        cheapest = min(self.G["Decor"], key=lambda d: self.G["Decor"][d]["cost"])
        cc = self.G["Decor"][cheapest]["cost"]
        if cc <= 20 * inc and cc <= self.cash:
            for r in self.rooms:
                if len(r.decor) < self.G["DecorSlots"] and cheapest not in r.decor:
                    self.add_decor(r, cheapest)
                    self.buy(t, "decor", cheapest, cc)
                    return
        # 4. amenities: three per floor with rooms, and more while Fun is short of 100
        fun_need = math.ceil(100 / self.G["Rating"]["FunPerAmenity"])
        for f in range(1, self.floors + 1):
            if not any(r.floor == f for r in self.rooms):
                continue
            if self.amen_on(f) >= 3 and len(self.amenities) >= fun_need:
                continue
            owned = {a for a, af in self.amenities if af == f}
            best, bv = None, None
            for a, p in P.items():
                if p["kind"] != "Amenity" or not self.buildable(a):
                    continue
                c = self.rules.piece_cost(a, sum(1 for x, _ in self.amenities if x == a))
                tags = set(p["tags"])
                val = sum(self.matched(r_sid, tags) for rr in self.rooms if rr.floor == f for r_sid in self.species_weights(rr.type))
                key = (a not in owned, val > 0, -c)
                if bv is None or key > bv:
                    best, bv = (a, c, p["w"] * p["d"]), key
            if not best:
                continue
            n = 0
            if self.floor_used(f) + best[2] > self.floor_cap(f):
                n = self.tiles_needed(f, best[2])
                if n is None:
                    continue
            extra = self.tiles_cost(f, n) if n else 0
            if best[1] + extra <= 180 * inc and best[1] + extra <= self.cash:
                if n:
                    self.buy(t, "tiles", f"{n} on floor {f}", extra)
                    self.tiles[f] += n
                    self.bought[f] = self.bought.get(f, 0) + n
                self.amenities.append((best[0], f))
                self.buy(t, "amenity", best[0], best[1])
                return
        # 5. the first room of a newly unlocked type
        for pid, p in P.items():
            if p["kind"] == "Room" and pid != goal and self.type_count(pid) == 0 and self.buildable(pid):
                c = self.rules.piece_cost(pid, 0)
                cells = p["w"] * p["d"]
                if self.floor_for(cells) is None:
                    o = self.expand_option(cells)
                    if o and c + o[0] <= 300 * inc and c + o[0] <= self.cash:
                        self.expand(t, cells)
                        return
                    continue
                if c <= 300 * inc and c <= self.cash and self.place_room(t, pid):
                    return
        # 6. return on cost: new rooms of owned types and tier upgrades
        cands = []
        for pid in {r.type for r in self.rooms}:
            mine = [r for r in self.rooms if r.type == pid]
            n = len(mine)
            occ = statistics.fmean(r.occ for r in mine)
            pay = self.avg_pay(pid)
            d = pay * self.rules.milestone(n + 1) * occ ** 2
            if self.rules.milestone(n + 1) > self.rules.milestone(n):
                d += sum(pay * self.rules.tier_pay(r.tier) * r.occ for r in mine) * self.rules.milestone(n)
            cost = self.rules.piece_cost(pid, n)
            cells = P[pid]["w"] * P[pid]["d"]
            extra = 0
            if self.floor_for(cells) is None:
                o = self.expand_option(cells)
                extra = o[0] if o else None
            jump = self.rules.milestone(n + 1) > self.rules.milestone(n)
            if extra is not None and (occ >= ROOM_FULL or jump):
                cands.append((d / (cost + extra), "room", pid, cost + extra))
            for r in mine:
                tc = self.rules.tier_cost(r)
                if tc is None:
                    continue
                d = pay * self.G["Economy"]["TierPayBonus"] * self.rules.milestone(n) * r.occ
                cands.append((d / tc, "tier", r, tc))
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
        if cost > self.cash:
            return  # save for it
        if kind == "floor":
            self.buy(t, "floor", self.floors + 1, cost)
            self.floors += 1
            self.tiles.setdefault(self.floors, 0)
            self.bought.setdefault(self.floors, 0)
        elif kind == "room":
            cells = P[what]["w"] * P[what]["d"]
            if self.floor_for(cells) is None:
                self.expand(t, cells)
                return
            self.place_room(t, what)
        else:
            self.buy(t, "tier", f"{what.type} T{what.tier + 1}", cost)
            what.filler += math.ceil(cost / FILLER_COST)
            self.add_points(what, cost)

    # ---- the tutorial
    def tutorial_tick(self, t):
        s = self.tstep
        since = t - self.tstep_since
        done = False
        if s == "Build":
            done = self.room_count() >= 1
        elif s == "CheckIn":
            if self.slime_at is None:
                self.slime_at = t + self.G["Tutorial"]["FirstGuestDelay"]
            done = self.checkins >= 1
        elif s == "Collect":
            done = self.collects >= 1
        elif s == "SecondRoom":
            done = self.room_count() >= 2
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
            done = since > 5  # the player presses Next
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
            steps = ["Build", "CheckIn", "Collect", "SecondRoom", "Bus", "MoveIn", "Goal", "Clean", "Staff", "Preview", "Done"]
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
            if self.tutorial and self.tstep == "Build":
                if t >= FIRST_ROOM_AT:
                    self.place_room(t, "StandardRoom")
            elif self.tutorial and self.tstep == "SecondRoom":
                self.place_room(t, "StandardRoom")
            elif self.room_count() == 0 and (self.loc > 1 or not self.tutorial):
                if t >= FIRST_ROOM_AT:
                    self.place_room(t, self.first_room())
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
        self.end = t
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
    a = ap.parse_args()
    G = load_game()
    results = []
    for tut in ((True, False) if a.skip_tutorial else (True,)):
        sims = []
        for i in range(a.seeds):
            sims.append(Sim(G, 1000 + i, tutorial=tut, hours=a.hours).run())
            print(f"  seed {1000 + i} ({'tutorial' if tut else 'skipped'}): rebirth-ready {fmt(sims[-1].rebirth_ready)}", file=sys.stderr)
        results.append(summarize(G, sims, "with tutorial" if tut else "tutorial skipped"))
    lines = render(G, results, a)
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
        L_.append("| Moment | Time | Cash | Run cash | Income/min | Measured rate/min | Background/min | Rooms | Floors | Tiles (floor 1 / 2) | Rating | Categories (C/S/Cl/F/St) | Mean review |")
        L_.append("|---|---|---|---|---|---|---|---|---|---|---|---|---|")
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
                L_.append(f"| {k} | — | | | | | | | | | | | |")
                continue
            md = lambda f: statistics.median(f(x) for x in snaps)
            cats = "/".join(f"{md(lambda x, i=i: x['cats'][i]):.0f}" for i in range(5))
            L_.append(f"| {k} | {fmt(md(lambda x: x['t']))} | {money(md(lambda x: x['cash']))} | {money(md(lambda x: x['run_cash']))} | "
                      f"{money(md(lambda x: x['inc']))} | {money(md(lambda x: x['rate']))} | {money(md(lambda x: x['bg']))} | "
                      f"{md(lambda x: x['rooms']):.0f} | {md(lambda x: x['floors']):.0f} | "
                      f"{md(lambda x: x['tiles'].get(1, 0)):.0f} / {md(lambda x: x['tiles'].get(2, 0)):.0f} | "
                      f"{md(lambda x: x['rating']):.1f}★ | {cats} | {md(lambda x: x['reviews']):.2f} |")
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
    row("First room bought", "0:10–0:30", lambda R: f"{fmt(R['first_room'])} (by assumption)")
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
