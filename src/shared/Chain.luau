--!strict
--[[
	The hotel chain's rules (GDD §6.4, his rulings 2026-10-20), pure so the
	server, the panel and the specs agree.

	A player owns one hotel per location opened, plays one at a time and
	Travels between them; the others earn in the background at
	`Constants.Chain.BackgroundShare` of the rate they earned while played.
	Rebirth needs 5★ on every hotel of the chain and takes the chain apart.
	Floors: a hotel may have 2, and rebirths 1, 3, 5, 7… each unlock the
	right to buy one more, to `FloorCapMax`; the Extra Floor pass adds one.
	Prestige Stars come on even rebirths and on every rebirth after the cap.
]]

local Constants = require(script.Parent.Constants)

local C = Constants.Chain

local Chain = {}

-- What opening `location` costs, or nil for the first (it is never bought).
function Chain.openCost(location: number): number?
	return C.OpenCost[location]
end

-- The location a player may open next, given the ones opened, or nil when the chain is whole.
function Chain.nextToOpen(opened: { [number]: boolean }): number?
	for id = 1, C.Locations do
		if not opened[id] then
			return id
		end
	end
	return nil
end

-- The floors a hotel may have after `rebirths` rebirths (before the pass).
function Chain.floorCap(rebirths: number): number
	return math.min(C.StartFloorCap + math.ceil(math.max(rebirths, 0) / 2), C.FloorCapMax)
end

--[[ Whether rebirth number `n` (1 for the first) gives a Prestige Star: on
	even rebirths, and on every rebirth that unlocks no floor because the cap
	was already reached. ]]
function Chain.givesPrestige(n: number): boolean
	if n % 2 == 0 then
		return true
	end
	return Chain.floorCap(n) == Chain.floorCap(n - 1)
end

-- The Prestige Stars after `rebirths` rebirths.
function Chain.prestige(rebirths: number): number
	local stars = 0
	for n = 1, rebirths do
		if Chain.givesPrestige(n) then
			stars += 1
		end
	end
	return stars
end

-- The income bonus of `stars` Prestige Stars, as a fraction (0.1 is +10 %).
function Chain.prestigeIncome(stars: number): number
	return math.min(stars, C.PrestigeEffectCap) * C.PrestigeIncome
end

-- The extra chance of a rarer guest from `stars` Prestige Stars, as a fraction.
function Chain.prestigeRarity(stars: number): number
	return math.min(stars, C.PrestigeEffectCap) * C.PrestigeRarity
end

--[[ Whether the chain can be reborn: every location opened, and each
	hotel's rating (by location) at least `RebirthRating`. ]]
function Chain.rebirthReady(ratings: { [number]: number }): boolean
	for id = 1, C.Locations do
		local r = ratings[id]
		if r == nil or r < C.RebirthRating then
			return false
		end
	end
	return true
end

-- What a hotel not played earns in `seconds` at its measured `rate` ($/s).
function Chain.background(rate: number, seconds: number): number
	if rate ~= rate or rate <= 0 or seconds <= 0 then
		return 0
	end
	return rate * C.BackgroundShare * seconds
end

--[[ The played hotel's earning rate, as an exponential moving average: the
	old `rate`, the cash `earned` in the last `seconds`. ]]
function Chain.updateRate(rate: number, earned: number, seconds: number): number
	if seconds <= 0 then
		return rate
	end
	local a = 1 - math.exp(-seconds / C.RateWindow)
	return rate + (math.max(earned, 0) / seconds - rate) * a
end

return Chain
