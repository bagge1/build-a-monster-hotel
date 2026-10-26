--!strict
--[[
	The Night Bus's schedule, passenger list and drive (GDD §4.3), pure:

	  - every `Interval` seconds; its size is 40 % of the street's vacant
	    rooms, rounded up, at least 2 and at most 4 per player on the server
	    (his ruling, 2026-10-19; the bounds are PLACEHOLDER), so one bus
	    never fills every room;
	  - an Epic guaranteed every 3rd bus;
	  - a Legendary on the :00 and :30 buses: the first bus at or after each
	    half hour of the server clock (a bus called early, §10.2, keeps the
	    rule, since it is about crossing the boundary, not about a slot);
	  - a Mythic on the Midnight Bus, the first at or after each 2 hours;
	  - the rest drawn by rarity weight, then uniformly within the rarity
	    among the families present on the street (§3);
	  - during a new player's tutorial, Commons for that hotel's vacant rooms
	    in place of some of the rest (`Bus.commonsFor`, §11 1:45);
	  - the drive: out of the forest to the west stop, the east stop, and
	    away into the forest (`Bus.drive`), the same on the server (when
	    guests step off) and on every client (where the bus is drawn).
]]

local Constants = require(script.Parent.Constants)
local Species = require(script.Parent.Species)
local StreetLayout = require(script.Parent.StreetLayout)

local B = Constants.Bus

local Bus = {}

export type Flags = { epic: boolean, legendary: boolean, mythic: boolean }

-- What the bus arriving at `now` (the previous one at `previous`) guarantees.
function Bus.flags(index: number, previous: number, now: number): Flags
	local function crossed(period: number): boolean
		return math.floor(now / period) > math.floor(previous / period)
	end
	return {
		epic = index % B.EpicEvery == 0,
		legendary = crossed(B.LegendaryEvery),
		mythic = crossed(B.MythicEvery),
	}
end

-- How many ride (his ruling): 40 % of the street's vacant rooms rounded up, within 2–4 per player.
function Bus.size(vacant: number, players: number): number
	local p = math.max(1, players)
	return math.clamp(math.ceil(B.VacantShare * vacant), B.MinPerPlayer * p, B.MaxPerPlayer * p)
end

-- A rarity by weight (the GDD's, or an event's: `Events.weights`), from a uniform `r` in [0, 1).
function Bus.rollRarity(r: number, weights: { [string]: number }?): Constants.RarityId
	local function w(id: string): number
		return if weights then (weights[id] or 0) else Constants.Rarity[id].weight
	end
	local total = 0
	for _, id in Constants.RarityOrder do
		total += w(id)
	end
	local at = 0
	local last = "Common"
	for _, id in Constants.RarityOrder do
		at += w(id) / total
		if w(id) > 0 then
			last = id
		end
		if r < at then
			return id
		end
	end
	-- The fractions can sum to just under 1: a draw in that sliver is the last
	-- weighted rarity, as it would be with exact sums (2026-10-26 review).
	return last
end

-- The species of `rarity` among `locations`, in roster order.
function Bus.pool(rarity: string, locations: { [number]: boolean }): { string }
	local out = {}
	for _, sp in Species.List do
		if sp.rarity == rarity and locations[sp.location] then
			table.insert(out, sp.id)
		end
	end
	return out
end

--[[ The passengers' species, given the guarantees and a random source
	`rand()` in [0, 1). A rarity with no species among the locations present
	falls down a rarity until one has some. ]]
function Bus.passengers(
	flags: Flags,
	size: number,
	locations: { [number]: boolean },
	rand: () -> number,
	weights: { [string]: number }?
): { string }
	local out: { string } = {}
	local function pickOf(rarity: string): string?
		local order = Constants.RarityOrder
		local i = table.find(order, rarity :: any) or 1
		while i >= 1 do
			local pool = Bus.pool(order[i], locations)
			if #pool > 0 then
				return pool[1 + math.floor(rand() * #pool)]
			end
			i -= 1
		end
		return nil
	end
	local function add(rarity: string)
		local id = pickOf(rarity)
		if id then
			table.insert(out, id)
		end
	end
	if flags.mythic then
		add("Mythic")
	end
	if flags.legendary then
		add("Legendary")
	end
	if flags.epic then
		add("Epic")
	end
	while #out < size do
		add(Bus.rollRarity(rand(), weights))
	end
	return out
end

--[[ The rarest of `ids` (species ids), the first of them on a tie, or nil
	for none: the guest a bus announces (§4.3) and the room a "Need a ...!"
	ping names (§7). ]]
function Bus.rarest(ids: { string }): string?
	local best, bestRank = nil, 0
	for _, id in ids do
		local sp = Species.get(id)
		local rank = sp and table.find(Constants.RarityOrder, sp.rarity) or 0
		if rank > bestRank then
			best, bestRank = id, rank
		end
	end
	return best
end

--[[ Whether the tutorial's Vampire Count rides the next bus (§11: "A Vampire
	Count arrives in 3 buses", booked to the hotel once a Coffin Suite stands
	vacant): owed since the goal card (`goal`) until it has reached its hotel
	(`arrived`), never while one is already on a bus (`onBus`), from the third
	bus after the goal card (`busesSince`, the buses gone by since it, at least
	2, so it rides the third) and only with a room for it (`vacant`). One that
	stepped off and missed its hotel (the room taken, no way to it, the player
	gone) has not arrived, so it is offered again on a later bus. ]]
function Bus.tutorialVampire(t: {
	goal: boolean,
	arrived: boolean,
	onBus: boolean,
	busesSince: number,
	vacant: boolean,
}): boolean
	return t.goal and not t.arrived and not t.onBus and t.busesSince >= 2 and t.vacant
end

--[[ The buses gone by since a moment `at` (os.time), for "A Vampire Count
	arrives in 3 buses" (§11): one every `interval` since then, the same on any
	server, since each server counts its own buses from 0 (2026-10-26 review: a
	rejoin on a younger server owed the Vampire for hours). `here`, the buses
	this server has run since, when the moment was on this server: a bus called
	early or a Parade's (§8.2) count too, never fewer than by the clock. ]]
function Bus.busesSince(at: number, now: number, interval: number, here: number?): number
	local byClock = math.floor(math.max(0, now - at) / interval)
	return if here then math.max(here, byClock) else byClock
end

--[[ The Commons the tutorial brings a new hotel (§11 1:45: "The tutorial
	weights Commons toward your hotel"): at most `n`, never more for a room
	type than `vacant` (room id → rooms of it standing vacant) has, each a
	Common of `locations` that takes that room, drawn uniformly by `rand()` in
	[0, 1). Round the room types in turn (sorted, so it is the same every
	time), so two vacant types both get a guest before either gets two. A room
	no Common takes gets none. ]]
function Bus.commonsFor(
	vacant: { [string]: number },
	n: number,
	locations: { [number]: boolean },
	rand: () -> number
): { string }
	local takers: { [string]: { string } } = {}
	for _, id in Bus.pool("Common", locations) do
		local room = (Species.get(id) :: Species.Species).room
		takers[room] = takers[room] or {}
		table.insert(takers[room], id)
	end
	local rooms: { string } = {}
	local left: { [string]: number } = {}
	for room, count in vacant do
		if takers[room] and count > 0 then
			table.insert(rooms, room)
			left[room] = count
		end
	end
	table.sort(rooms)
	local out: { string } = {}
	local any = true
	while #out < n and any do
		any = false
		for _, room in rooms do
			if #out < n and left[room] > 0 then
				local pool = takers[room]
				table.insert(out, pool[1 + math.floor(rand() * #pool)])
				left[room] -= 1
				any = true
			end
		end
	end
	return out
end

-- ===== The drive =====

--[[ One leg of the drive: `dist` studs, cruising at `Speed`, speeding up over
	`Brake` studs from a stop if `fromStop`, slowing over `Brake` to a stop if
	`toStop` (a short leg never reaches cruising). Returns its seconds and
	where along it the bus is `t` seconds in. ]]
local function leg(dist: number, fromStop: boolean, toStop: boolean): (number, (number) -> number)
	local v, b = B.Speed, B.Brake
	local ends = (if fromStop then 1 else 0) + (if toStop then 1 else 0)
	if ends == 0 then
		return dist / v, function(t)
			return t * v
		end
	end
	local a = v * v / (2 * b)
	local ramp = math.min(b, dist / ends) -- each speeding-up or slowing-down stretch
	local top = math.sqrt(2 * a * ramp)
	local tRamp = top / a
	local cruise = dist - ramp * ends
	local tCruise = cruise / top
	local total = tRamp * ends + tCruise
	return total,
		function(t)
			t = math.clamp(t, 0, total)
			local s = 0
			if fromStop then
				local u = math.min(t, tRamp)
				s += 0.5 * a * u * u
				t -= u
				if t <= 0 then
					return s
				end
			end
			local u = math.min(t, tCruise)
			s += top * u
			t -= u
			if t > 0 and toStop then
				s += top * t - 0.5 * a * t * t
			end
			return s
		end
end

export type Drive = {
	start: number, -- seconds, from the west stop's arrival (negative: it leaves the forest before)
	eastAt: number, -- when it reaches the east stop
	finish: number, -- when it is gone into the forest
	at: (t: number) -> number, -- how far along the road its door is, `t` seconds from the west stop
	stops: { number }, -- seconds each stop is reached, West then East
}

--[[ The bus's drive, timed from its arrival at the west stop (t = 0, when
	`BusArrivedAt` is published and the first guests step off). It moves the
	bus's **door** from stop to stop, so a guest steps off where the door is;
	the client draws the bus's centre behind it by the delivered model's
	`Door` attachment (BusRenderer). ]]
function Bus.drive(): Drive
	local route = StreetLayout.RouteLength
	local west = StreetLayout.routeDistanceAt(StreetLayout.Stops[1].x)
	local east = StreetLayout.routeDistanceAt(StreetLayout.Stops[2].x)
	local tIn, sIn = leg(west, false, true)
	local tMid, sMid = leg(east - west, true, true)
	local tOut, sOut = leg(route - east, true, false)
	local dwell = B.StopTime
	local eastAt = dwell + tMid
	local finish = eastAt + dwell + tOut
	return {
		start = -tIn,
		eastAt = eastAt,
		finish = finish,
		stops = { 0, eastAt },
		at = function(t: number): number
			if t < 0 then
				return sIn(t + tIn)
			elseif t < dwell then
				return west
			elseif t < eastAt then
				return west + sMid(t - dwell)
			elseif t < eastAt + dwell then
				return east
			end
			return east + sOut(t - eastAt - dwell)
		end,
	}
end

return Bus
