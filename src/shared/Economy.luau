--!strict
--[[
	The money rules (GDD §4.2, §5.2, §6.2, §6.4, §6.5), as pure functions of
	their inputs: the server charges and pays with them, the client shows the
	same prices, and the specs hold them to their rules. Every number is in
	`Constants`.
]]

local Constants = require(script.Parent.Constants)
local Species = require(script.Parent.Species)
local Pieces = require(script.Parent.Pieces)
local Mutations = require(script.Parent.Mutations)

local E = Constants.Economy

local Economy = {}

-- A new piece of this kind, with `owned` of the same kind already built: base × 1.15^n (§6.2).
function Economy.pieceCost(id: string, owned: number): number
	local piece = Pieces.get(id)
	if not piece then
		return math.huge
	end
	return math.floor(piece.cost * E.RoomCostGrowth ^ owned + 0.5)
end

-- From `tier` to `tier + 1`: base × 4^tier (§5.2), nil at the top tier.
function Economy.tierCost(id: string, tier: number): number?
	local piece = Pieces.get(id)
	if not piece or tier >= E.MaxTier then
		return nil
	end
	return math.floor(piece.cost * E.TierCostMultiplier ^ tier + 0.5)
end

-- What selling refunds: half of what this piece and its tiers cost (Appendix A.2).
function Economy.sellValue(id: string, ownedBefore: number, tier: number): number
	local spent = Economy.pieceCost(id, ownedBefore)
	for t = 1, tier - 1 do
		spent += Economy.tierCost(id, t) or 0
	end
	return math.floor(spent * E.SellRefund)
end

function Economy.floorCost(floor: number): number?
	return E.FloorCosts[floor]
end

-- +50 % pay per tier above T1 (§5.2).
function Economy.tierPay(tier: number): number
	return 1 + E.TierPayBonus * (tier - 1)
end

-- Owning 5, 10 and 25 rooms of a type doubles that type's pay each time (§6.2).
function Economy.milestoneMultiplier(count: number): number
	local m = 1
	for _, at in E.Milestones do
		if count >= at then
			m *= 2
		end
	end
	return m
end

-- A species' own rate at T1, unmutated: base × 20^(location − 1) × rarity (§4.2).
function Economy.speciesPay(speciesId: string): number
	local sp = Species.get(speciesId)
	if not sp then
		return 0
	end
	return E.BasePay * E.LocationPayMultiplier ^ (sp.location - 1) * Constants.Rarity[sp.rarity].pay
end

export type Bonuses = {
	permanent: number?, -- added together: Moon Tree cash, Book families, group (§6.2)
	friends: boolean?, -- +10 % with 2+ friends on the street (§7)
	boost: number?, -- a timed boost's multiplier (2 for 2x Cash)
}

--[[ Bonus stacking (§6.2): add within a category, multiply across them. ]]
function Economy.incomeMultiplier(b: Bonuses): number
	local m = 1 + (b.permanent or 0)
	if b.friends then
		m *= 1 + Constants.Social.FriendBonus
	end
	if b.boost then
		m *= b.boost
	end
	return m
end

--[[ What a guest pays per second while staying (§4.4): its species' rate,
	the room's tier, its mutation, the milestones of that room type, and the
	hotel's bonuses. ]]
function Economy.guestPay(
	speciesId: string,
	tier: number,
	mutation: string?,
	typeCount: number,
	multiplier: number
): number
	return Economy.speciesPay(speciesId)
		* Economy.tierPay(tier)
		* Mutations.payMultiplier(mutation)
		* Economy.milestoneMultiplier(typeCount)
		* multiplier
end

-- A resident's rate (§4.6): 25 % of its species' rate, times its mutation.
function Economy.residentPay(speciesId: string, mutation: string?, multiplier: number): number
	return Economy.speciesPay(speciesId)
		* Constants.Residents.EarnFraction
		* Mutations.payMultiplier(mutation)
		* multiplier
end

--[[ Offline earnings (§4.6): 50 % of the residents' rate, for at most the
	cap. `rate` is the residents' combined online rate. ]]
function Economy.offline(rate: number, seconds: number, cap: number): number
	local t = math.clamp(seconds, 0, cap)
	return math.floor(rate * Constants.Residents.OfflineFraction * t)
end

-- Moon Shards for a rebirth: floor(10 × √(run cash / $1M)) (§6.4).
function Economy.rebirthShards(runCash: number): number
	local R = Constants.Rebirth
	return math.floor(R.ShardScale * math.sqrt(math.max(runCash, 0) / R.ShardDivisor))
end

-- What a rebirth from `location` asks to have earned this run (§6.4; ×20 per location is a PLACEHOLDER).
function Economy.rebirthCash(location: number): number
	return Constants.Rebirth.RunCash * E.LocationPayMultiplier ^ (location - 1)
end

return Economy
