--!strict
--[[
	The Night Bus's schedule and passenger list (GDD §4.3), pure:

	  - every `Interval` seconds, 6–10 guests scaled by player count;
	  - an Epic guaranteed every 3rd bus;
	  - a Legendary on the :00 and :30 buses: the first bus at or after each
	    half hour of the server clock (a bus called early, §10.2, keeps the
	    rule, since it is about crossing the boundary, not about a slot);
	  - a Mythic on the Midnight Bus, the first at or after each 2 hours;
	  - the rest drawn by rarity weight, then uniformly within the rarity
	    among the families present on the street (§3).
]]

local Constants = require(script.Parent.Constants)
local Species = require(script.Parent.Species)

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

function Bus.size(players: number): number
	return math.clamp(
		B.BaseSize + B.SizePerPlayer * math.max(0, players - 1),
		B.BaseSize,
		B.MaxSize
	)
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
	for _, id in Constants.RarityOrder do
		at += w(id) / total
		if r < at then
			return id
		end
	end
	return "Common"
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

return Bus
