--!strict
--[[
	The Moon Tree (GDD §6.5): permanent upgrades bought with Moon Shards and
	kept through every rebirth. Each node's cost grows ×1.5 per level. The
	nodes are §6.5's examples; their levels and base cost are night drafts
	(Appendix A.6, PLACEHOLDER).

	`effect(level)` is what the node gives at that level, in the unit its
	system reads: a fraction for income and bus score, slots for the Wing,
	seconds for the offline cap, a fraction off cleaning, rerolls.
]]

local Constants = require(script.Parent.Constants)

export type Node = {
	id: string,
	name: string,
	text: string,
	levels: number,
	baseCost: number,
	per: number,
}

local MoonTree = {}

MoonTree.Nodes = {
	{
		id = "Cash",
		name = "Silver Coins",
		text = "+10% cash",
		levels = 5,
		baseCost = 5,
		per = 0.10,
	},
	{
		id = "Wing",
		name = "Bigger Wing",
		text = "+1 Resident Wing slot",
		levels = 5,
		baseCost = 5,
		per = 1,
	},
	{
		id = "Offline",
		name = "Night Owl",
		text = "+15 min offline cap",
		levels = 4,
		baseCost = 5,
		per = 15 * 60,
	},
	{
		id = "Bus",
		name = "Moonlit Sign",
		text = "+5% bus score",
		levels = 5,
		baseCost = 5,
		per = 0.05,
	},
	{
		id = "Cleaning",
		name = "Swift Brooms",
		text = "-10% cleaning time",
		levels = 3,
		baseCost = 5,
		per = 0.10,
	},
	{
		id = "Reroll",
		name = "Second Thoughts",
		text = "+1 daily request reroll",
		levels = 2,
		baseCost = 5,
		per = 1,
	},
} :: { Node }

MoonTree.ById = {} :: { [string]: Node }
for _, n in MoonTree.Nodes do
	MoonTree.ById[n.id] = n
end

-- What the next level costs, from `level` (nil at the top).
function MoonTree.cost(id: string, level: number): number?
	local n = MoonTree.ById[id]
	if not n or level >= n.levels then
		return nil
	end
	return math.floor(n.baseCost * Constants.MoonTree.CostGrowth ^ level + 0.5)
end

function MoonTree.effect(id: string, level: number): number
	local n = MoonTree.ById[id]
	if not n then
		return 0
	end
	return n.per * math.clamp(level, 0, n.levels)
end

return MoonTree
