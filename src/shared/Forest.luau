--!strict
--[[
	The forest round Creepy Lane (GDD §5.4, his idea 2026-10-19: so the street
	is not a bare lawn), as a seeded scatter: pure and the same on every
	client, which places the trees itself (`ForestRenderer`), so the server
	holds none and nothing replicates.

	One tree to a jittered cell of `Spacing` studs, `Fill` of the cells, in a
	band `Depth` deep round the street's clearing: nothing on the lane, the
	pavements, a plot, its forecourt or its Resident Wing, or the bus's road,
	and `Clearing` studs kept free round each. The gaps between plots keep a
	line of trees down their middle.

	Each tree belongs to a **zone**: the plot it stands behind or beside, or 0
	at the street's ends. A zone's trees are drawn from its plot's location's
	set (`Forest.Sets`), so a Frostfang lodge stands among snowy firs.
]]

local Constants = require(script.Parent.Constants)
local StreetLayout = require(script.Parent.StreetLayout)

local F = Constants.Forest
local S = Constants.Street

local Forest = {}

-- Which trees a location's forest is made of, by weight (MODELS.md, "Street scenery: trees").
Forest.Sets = {
	[1] = { -- Haunted Manor: bare and crooked, a few dark firs, now and then a pair of eyes
		{ id = "Tree_Crooked", weight = 3 },
		{ id = "Tree_Bare", weight = 3 },
		{ id = "Tree_Fir", weight = 2 },
		{ id = "Tree_Hollow", weight = 0.35 },
	},
	[2] = { -- Frostfang Lodge: snowy firs
		{ id = "Tree_SnowFir", weight = 5 },
		{ id = "Tree_Fir", weight = 2 },
		{ id = "Tree_Bare", weight = 1 },
	},
} :: { [number]: { { id: string, weight: number } } }

-- Trees that look at the street, not into the woods: the hollow's eyes are on its front (−Z).
Forest.FacesStreet = { Tree_Hollow = true } :: { [string]: boolean }

-- Every tree id any set uses.
Forest.Ids = {} :: { string }
do
	local seen = {}
	for _, set in Forest.Sets do
		for _, e in set do
			if not seen[e.id] then
				seen[e.id] = true
				table.insert(Forest.Ids, e.id)
			end
		end
	end
	table.sort(Forest.Ids)
end

export type Tree = {
	position: Vector3, -- the trunk's foot, on the ground
	yaw: number, -- radians
	scale: number,
	pick: number, -- in [0, 1): which tree of its zone's set
	zone: number, -- a plot index, or 0
	low: boolean, -- drawn by the low graphics tier too
}

-- True where no tree may stand: the street's clearing and the road.
function Forest.cleared(p: Vector3): boolean
	local C = F.Clearing
	local ax, az = math.abs(p.X), math.abs(p.Z)
	local laneEnd = S.LaneHalfLength + 20
	-- The lane and its pavements, end to end.
	if az < S.LaneHalfWidth + S.PavementWidth + C and ax < laneEnd + C then
		return true
	end
	-- A plot: its forecourt, its grid and its Wing.
	if az > S.LaneHalfWidth - C and az < StreetLayout.BackZ + C then
		local side = if p.Z > 0 then 1 else -1
		for index = 1, S.Plots do
			if StreetLayout.side(index) == side then
				local x0, x1 = StreetLayout.plotSpan(index)
				if p.X > x0 - C and p.X < x1 + C then
					return true
				end
			end
		end
	end
	return StreetLayout.roadDistance(p) < StreetLayout.RoadWidth / 2 + C
end

-- The plot a point stands behind or beside (the nearest on its side), or 0 past the street's ends.
function Forest.zone(p: Vector3): number
	if math.abs(p.X) > StreetLayout.RingX + S.PlotGap / 2 then
		return 0
	end
	local side = if p.Z > 0 then 1 else -1
	local best, bestD = 0, math.huge
	for index = 1, S.Plots do
		if StreetLayout.side(index) == side then
			local x0, x1 = StreetLayout.plotSpan(index)
			local d = math.abs((x0 + x1) / 2 - p.X)
			if d < bestD then
				best, bestD = index, d
			end
		end
	end
	return best
end

-- The tree id for a zone's location and a tree's `pick`.
function Forest.pickId(location: number, pick: number): string
	local set = Forest.Sets[location] or Forest.Sets[1]
	local total = 0
	for _, e in set do
		total += e.weight
	end
	local at = 0
	for _, e in set do
		at += e.weight / total
		if pick < at then
			return e.id
		end
	end
	return set[#set].id
end

-- Every tree, the same on every call and every machine.
function Forest.layout(): { Tree }
	local rng = Random.new(F.Seed)
	local out: { Tree } = {}
	local xMax = S.LaneHalfLength + 20 + F.Clearing + F.Depth
	local zMax = StreetLayout.BackZ + F.Clearing + F.Depth
	local step = F.Spacing
	local y = 0
	local x = -xMax
	while x < xMax do
		local z = -zMax
		while z < zMax do
			-- Every cell draws the same numbers whether or not it gets a tree, so the forest is stable.
			local jx, jz = rng:NextNumber(), rng:NextNumber()
			local fill, yaw, scale, pick, low =
				rng:NextNumber(),
				rng:NextNumber(),
				rng:NextNumber(),
				rng:NextNumber(),
				rng:NextNumber()
			-- Jittered within the middle half of its cell: neighbours never closer than half a cell.
			local p = Vector3.new(x + (0.25 + 0.5 * jx) * step, y, z + (0.25 + 0.5 * jz) * step)
			if fill < F.Fill and not Forest.cleared(p) then
				table.insert(out, {
					position = p,
					yaw = yaw * 2 * math.pi,
					scale = 0.8 + 0.45 * scale,
					pick = pick,
					zone = Forest.zone(p),
					low = low < F.LowGraphics,
				})
			end
			z += step
		end
		x += step
	end
	return out
end

return Forest
