--!strict
--[[
	Expeditions (GDD A.11.2, on its scrutinized recommendations; his ruling on
	the pay, §18 2026-10-26), the rules only. Pure, specced
	(`tests/expeditions.spec.luau`); `ExpeditionService` runs them for each
	player. Every number is `Constants.Expeditions`, PLACEHOLDER but `Pay`.

	WHO GOES. Up to `Party` residents **from the Wing** (decision 1a: role "",
	not in the Hunter Camp, not on a trip), to a destination whose location is
	open in the current run, for one of the `Lengths`. One trip at a time.
	While away a resident is away as one in the Hunter Camp is: no Wing
	earnings, no offline earnings, no perk, not on staff (`away`). It keeps
	learning as in the Wing (§18: "XP as in the Wing"): `ResidentLevels.learning`
	reads only the camp, so it gains XP while the player plays and none
	offline, exactly what staying would have given.

	THE PAY (his ruling). A trip pays `Pay` × what its party would have earned
	by staying, **counted as staying counts**: the party's Wing rate for every
	second the player plays during the trip (`countOnline`), and for the time
	away the offline rate for at most the offline cap from that logout
	(`countOffline`, by `Economy.offline`'s rules and cap). So a trip never
	beats the cap; its edge is the find.

	A TRIP BACK BEFORE THE LOGIN does not also fill the offline till (§18):
	welcome-back pays a resident just home only for the part of the offline
	window after its trip ended (`homeSeconds`); the trip has the rest.

	THE FIND (decision 3b). On collecting, one free roll at the length's
	chance × (1 + `Match` per resident matching the destination: §18, the
	match bonus on the find, not the pay), drawn among the destination
	location's unfound pieces (`FindService`); a find is guaranteed on the
	`PityTrips`-th trip of `PityMin` or longer in a row without one.

	COMING HOME. The party is home in the Wing when the time is up (`ends`)
	and earns by staying's rules from then on; the pay and the roll wait for
	**Collect**. A rebirth calls the party home (`recall`): it pays what was
	counted so far and rolls nothing (A.11.2 "Mid-trip"). Travel changes
	nothing: the residents are the chain's.
]]

local Constants = require(script.Parent.Constants)
local Economy = require(script.Parent.Economy)
local Species = require(script.Parent.Species)

local X = Constants.Expeditions

local Expeditions = {}

-- One per location (A.11.2 "How it plays"); `id` is its location's. `likes` are
-- `Species` preference tags a resident matches by: PLACEHOLDER picks (A.11.2's
-- "cold-lovers to Frostfang Pass"), his to change.
export type Destination = { id: number, location: number, name: string, likes: { string } }

Expeditions.Destinations = {
	{
		id = 1,
		location = 1,
		name = "Haunted Woods",
		likes = { "dark", "darkness", "moonlight", "quiet", "silence" },
	},
	{
		id = 2,
		location = 2,
		name = "Frostfang Pass",
		likes = { "cold", "snow", "northern lights" },
	},
	{
		id = 3,
		location = 3,
		name = "Bayou Backwaters",
		likes = { "damp", "mud", "moss", "steam", "fireflies" },
	},
} :: { Destination }

export type Trip = {
	destination: number,
	length: number, -- seconds
	start: number, -- os.time
	ends: number, -- os.time: the party is home from then on
	party: { string }, -- resident ids
	matches: number, -- party members matching the destination, at the start
	counted: number, -- os.time up to which staying's earnings are counted
	earned: number, -- what the party would have earned by staying so far, before `Pay`
}
-- The profile's `expedition`: the trip out (nil none), long trips in a row without a find, trips collected.
export type Record = { trip: Trip?, longMisses: number, trips: number }

-- The fields of a resident record the rules read (PlayerData.ResidentRecord has them).
export type Resident = {
	species: string,
	role: string,
	campUntil: number,
	expedition: number?, -- os.time its trip ends; away while it is in the future
	level: number?,
}

function Expeditions.newRecord(): Record
	return { trip = nil, longMisses = 0, trips = 0 }
end

function Expeditions.destination(id: number): Destination?
	for _, d in Expeditions.Destinations do
		if d.id == id then
			return d
		end
	end
	return nil
end

-- Whether a resident is away on a trip at `now`.
function Expeditions.away(rec: { expedition: number? }, now: number): boolean
	return (rec.expedition or 0) > now
end

-- Whether a resident may go: in the Wing, home from the Hunter Camp and from any trip (decision 1a).
function Expeditions.mayGo(rec: Resident, now: number): boolean
	return rec.role == "" and rec.campUntil <= now and not Expeditions.away(rec, now)
end

-- Whether a destination is offered: its location open in the current run (A.11.2 "Mid-trip").
function Expeditions.offered(id: number, opened: { [number]: boolean }): boolean
	local d = Expeditions.destination(id)
	return d ~= nil and opened[d.location] == true
end

-- The lengths a trip may have, shortest first.
function Expeditions.lengths(): { number }
	local out = {}
	for seconds in X.Lengths do
		table.insert(out, seconds)
	end
	table.sort(out)
	return out
end

-- Whether a species likes something its destination has (decision 4b).
function Expeditions.matches(speciesId: string, destinationId: number): boolean
	local sp = Species.get(speciesId)
	local d = Expeditions.destination(destinationId)
	if not sp or not d then
		return false
	end
	for _, p in sp.prefs do
		if table.find(d.likes, p) then
			return true
		end
	end
	return false
end

local function rarityRank(speciesId: string): number
	local sp = Species.get(speciesId)
	return if sp then table.find(Constants.RarityOrder, sp.rarity :: any) or 0 else 0
end

--[[ **Best for this trip** (A.11.2 "Picking"): up to `n` of `candidates`,
	matching the destination first, then the highest level, then the rarest;
	ties by id, so the same Wing always gives the same party. ]]
function Expeditions.best(
	candidates: { { id: string, species: string, level: number? } },
	destinationId: number,
	n: number
): { string }
	local list = table.clone(candidates)
	table.sort(list, function(a, b)
		local ma = Expeditions.matches(a.species, destinationId)
		local mb = Expeditions.matches(b.species, destinationId)
		if ma ~= mb then
			return ma
		end
		local la, lb = a.level or 1, b.level or 1
		if la ~= lb then
			return la > lb
		end
		local ra, rb = rarityRank(a.species), rarityRank(b.species)
		if ra ~= rb then
			return ra > rb
		end
		local na, nb = tonumber(a.id), tonumber(b.id)
		if na and nb and na ~= nb then
			return na < nb
		end
		return a.id < b.id
	end)
	local out = {}
	for i = 1, math.min(n, #list) do
		table.insert(out, list[i].id)
	end
	return out
end

--[[ Why a trip cannot leave, or nil when it can: one trip at a time, an
	offered destination, a listed length, 1 to `Party` different residents
	who may go. ]]
function Expeditions.check(
	record: Record,
	residents: { [string]: Resident },
	ids: { string },
	destinationId: number,
	length: number,
	opened: { [number]: boolean },
	now: number
): string?
	if record.trip then
		return "A trip is already out"
	end
	if not Expeditions.offered(destinationId, opened) then
		return "Open that location's hotel first"
	end
	if X.Lengths[length] == nil then
		return "Pick a trip length"
	end
	if #ids < 1 or #ids > X.Party then
		return `Pick 1 to {X.Party} residents`
	end
	local seen: { [string]: boolean } = {}
	for _, id in ids do
		local rec = residents[id]
		if seen[id] or not rec then
			return "Pick each resident once"
		end
		seen[id] = true
		if not Expeditions.mayGo(rec, now) then
			return "Only residents in the Wing can go"
		end
	end
	return nil
end

-- Sends the party (after `check`): the trip, and each resident away until it ends.
function Expeditions.start(
	record: Record,
	residents: { [string]: Resident },
	ids: { string },
	destinationId: number,
	length: number,
	now: number
): Trip
	local matches = 0
	for _, id in ids do
		local rec = residents[id]
		rec.expedition = now + length
		if Expeditions.matches(rec.species, destinationId) then
			matches += 1
		end
	end
	local trip: Trip = {
		destination = destinationId,
		length = length,
		start = now,
		ends = now + length,
		party = table.clone(ids),
		matches = matches,
		counted = now,
		earned = 0,
	}
	record.trip = trip
	return trip
end

-- The seconds [a, b) and [c, d) share.
function Expeditions.overlap(a: number, b: number, c: number, d: number): number
	return math.max(0, math.min(b, d) - math.max(a, c))
end

--[[ Staying's earnings while the player plays: `rate` ($/s, the party's Wing
	rate now) for the trip's seconds since it was last counted, up to `now`.
	Returns what was added. ]]
function Expeditions.countOnline(trip: Trip, rate: number, now: number): number
	local added = rate * Expeditions.overlap(trip.counted, now, trip.start, trip.ends)
	trip.earned += added
	trip.counted = math.max(trip.counted, now)
	return added
end

--[[ Staying's earnings for the time away, on joining: the trip's part of
	the offline window (from the logout `since`, `away` seconds long, at
	most `cap`), at `rate` (the party's online rate, offline's bonuses), by
	`Economy.offline`'s rules and cap. Counts nothing already counted.
	Returns what was added. ]]
function Expeditions.countOffline(
	trip: Trip,
	rate: number,
	since: number,
	away: number,
	cap: number,
	now: number
): number
	local from = math.max(since, trip.counted)
	local to = since + math.clamp(away, 0, cap)
	local added = Economy.offline(rate, Expeditions.overlap(from, to, trip.start, trip.ends), cap)
	trip.earned += added
	trip.counted = math.max(trip.counted, now)
	return added
end

--[[ The seconds of the offline window (from `since`, `away` long, at most
	`cap`) a resident home from a trip at `ends` earns offline: only the part
	after `ends` (§18: a trip back before the login does not also fill the
	till). A resident never on a trip (`ends` 0) earns the whole window. ]]
function Expeditions.homeSeconds(since: number, away: number, cap: number, ends: number): number
	local to = since + math.clamp(away, 0, cap)
	return math.max(0, to - math.max(since, ends))
end

function Expeditions.back(trip: Trip, now: number): boolean
	return now >= trip.ends
end

function Expeditions.left(trip: Trip, now: number): number
	return math.max(0, trip.ends - now)
end

-- What the trip pays for what was counted: `Pay` × staying's earnings (his ruling).
function Expeditions.pay(trip: Trip): number
	return math.floor(X.Pay * math.max(0, trip.earned))
end

-- A find's chance for a trip of `length` with `matches` matching residents (§18: the bonus is on the find).
function Expeditions.findChance(length: number, matches: number): number
	return math.min(1, (X.Lengths[length] or 0) * (1 + X.Match * matches))
end

-- Whether this trip's roll is the guarantee: the `PityTrips`-th long trip in a row without a find.
function Expeditions.guaranteed(record: Record, length: number): boolean
	return length >= X.PityMin and record.longMisses + 1 >= X.PityTrips
end

--[[ The trip's free roll (`rand` returns 0..1): whether it finds, and the
	long trips' run without a find updated (any find ends it). ]]
function Expeditions.roll(record: Record, trip: Trip, rand: () -> number): boolean
	local found = rand() < Expeditions.findChance(trip.length, trip.matches)
		or Expeditions.guaranteed(record, trip.length)
	if found then
		record.longMisses = 0
	elseif trip.length >= X.PityMin then
		record.longMisses += 1
	end
	return found
end

-- Ends the trip: every party member still on it is home, and the record is free.
local function finish(record: Record, residents: { [string]: Resident }, trip: Trip)
	for _, id in trip.party do
		local rec = residents[id]
		if rec and rec.expedition == trip.ends then
			rec.expedition = nil
		end
	end
	record.trip = nil
end

--[[ **Collect** a trip that is back: its pay, whether its roll found, and
	the trip; nothing (0, false, nil) while none is back. ]]
function Expeditions.collect(
	record: Record,
	residents: { [string]: Resident },
	rand: () -> number,
	now: number
): (number, boolean, Trip?)
	local trip = record.trip
	if not trip or not Expeditions.back(trip, now) then
		return 0, false, nil
	end
	local cash = Expeditions.pay(trip)
	local found = Expeditions.roll(record, trip, rand)
	finish(record, residents, trip)
	record.trips += 1
	return cash, found, trip
end

--[[ A rebirth calls the party home (A.11.2 "Mid-trip"): it pays what was
	counted so far and rolls no find; the party is home at once. Returns the
	pay and the trip (0, nil with none out). ]]
function Expeditions.recall(record: Record, residents: { [string]: Resident }): (number, Trip?)
	local trip = record.trip
	if not trip then
		return 0, nil
	end
	local cash = Expeditions.pay(trip)
	finish(record, residents, trip)
	return cash, trip
end

return Expeditions
