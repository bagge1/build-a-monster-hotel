--!strict
--[[
	The forest round Creepy Lane (GDD §5.4, his idea 2026-10-19: so the street
	is not a bare lawn), as a seeded scatter: pure and the same on every
	client, which places the trees itself (`ForestRenderer`), so the server
	holds none and nothing replicates.

	Two bands round the street's clearing (his ruling, 2026-10-19 evening: "the
	forest should stretch out much longer, and be thicker near the actual
	playarea"): a thicket `ThicketDepth` deep along it, one tree to a jittered
	cell of `ThicketSpacing` studs, `ThicketFill` of the cells; and beyond it the
	forest out to `Depth`, `Spacing` and `Fill`. Nothing on the lane, the
	pavements, a plot, its forecourt or its Resident Wing, or the bus's road,
	and `Clearing` studs kept free round each. The gaps between plots keep a
	line of trees down their middle.

	ONE WORLD (GDD §3, §6.4, his ruling 2026-10-20): the forest covers every
	location's street and the road between them (`StreetLayout.link`), with a
	meadow `World.MeadowHalfWidth` either side of that road, so a street-end
	plot sees the next street's hotels down it. Each tree belongs to a
	**location**: its street's own, and between two streets the next one's
	more and more often along X (`StreetLayout.blend`), so Haunted Manor's
	crooked trees give way to Frostfang's snowy firs, and those to Bayou Spa's
	cypresses, gradually. Its trees are drawn from that location's set
	(`Forest.Sets`).
]]

local Constants = require(script.Parent.Constants)
local StreetLayout = require(script.Parent.StreetLayout)

local F = Constants.Forest
local S = Constants.Street
local W = Constants.World

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
	-- Bayou Spa: swamp cypresses, a few bare and crooked trees. PLACEHOLDER (his picks): `Tree_Cypress` has no
	-- model yet, `ForestRenderer` draws a blockout with MODELS.md's tree parts until one is imported.
	[3] = {
		{ id = "Tree_Cypress", weight = 5 },
		{ id = "Tree_Bare", weight = 1.5 },
		{ id = "Tree_Crooked", weight = 1 },
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
	pick: number, -- in [0, 1): which tree of its location's set
	location: number, -- whose set it is drawn from: its street's, blended toward the next between two
	low: boolean, -- drawn by the low graphics tier too
}

-- True where no tree may stand: every street's clearing and road, and the meadow between two streets.
-- With `margin`, the clearing widened by that many studs (the thicket's reach).
function Forest.cleared(p: Vector3, margin: number?): boolean
	local C = F.Clearing + (margin or 0)
	local street = StreetLayout.streetAt(p)
	local lx = p.X - StreetLayout.originX(street)
	local ax, az = math.abs(lx), math.abs(p.Z)
	local laneEnd = StreetLayout.LaneEnd
	-- The lane and its pavements, end to end.
	if az < S.LaneHalfWidth + S.PavementWidth + C and ax < laneEnd + C then
		return true
	end
	-- The meadow along the road to the next street (or from the one before), from past the last plots on.
	local toward = (lx > StreetLayout.RingX and street < StreetLayout.Streets)
		or (lx < -StreetLayout.RingX and street > 1)
	if toward and az < W.MeadowHalfWidth + C then
		return true
	end
	-- A plot: its forecourt, its grid and its Wing.
	if az > S.LaneHalfWidth - C and az < StreetLayout.BackZ + C then
		local side = if p.Z > 0 then 1 else -1
		for index = 1, S.Plots do
			if StreetLayout.side(index) == side then
				local x0, x1 = StreetLayout.plotSpan(index, street)
				if p.X > x0 - C and p.X < x1 + C then
					return true
				end
			end
		end
	end
	return StreetLayout.roadDistance(p) < StreetLayout.RoadWidth / 2 + C
end

--[[ The location whose trees stand at `p`: its street's, and between two
	streets the next one's with a chance growing along X (`StreetLayout.blend`).
	`roll` in [0, 1) is the tree's own, so the forest is the same everywhere. ]]
function Forest.locationAt(p: Vector3, roll: number): number
	local a, b, t = StreetLayout.blend(p.X)
	return if roll < t then b else a
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

-- One band's trees: a jittered grid of `step`-stud cells over the box out
-- to `reach` from the clearing, `share` of the cells, where `keep` says.
local function band(
	out: { Tree },
	seed: number,
	step: number,
	share: number,
	reach: number,
	keep: (Vector3) -> boolean
)
	local rng = Random.new(seed)
	local xMax = StreetLayout.LaneEnd + F.Clearing + reach
	local zMax = StreetLayout.BackZ + F.Clearing + reach
	-- From west of the first street to east of the last: Creepy Lane's cells first, as they always were.
	local xEnd = StreetLayout.originX(StreetLayout.Streets) + xMax
	local x = -xMax
	while x < xEnd do
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
			local p = Vector3.new(x + (0.25 + 0.5 * jx) * step, 0, z + (0.25 + 0.5 * jz) * step)
			if fill < share and keep(p) then
				table.insert(out, {
					position = p,
					yaw = yaw * 2 * math.pi,
					scale = 0.8 + 0.45 * scale,
					pick = pick,
					-- The blend's roll from the tree's own numbers, so no cell draws one more and the forest stays put.
					location = Forest.locationAt(p, (pick * 7919 + yaw * 104729) % 1),
					low = low < F.LowGraphics,
				})
			end
			z += step
		end
		x += step
	end
end

-- Every tree, the same on every call and every machine: the thicket, then the forest beyond it.
function Forest.layout(): { Tree }
	local out: { Tree } = {}
	band(out, F.Seed, F.ThicketSpacing, F.ThicketFill, F.ThicketDepth, function(p)
		return not Forest.cleared(p) and Forest.cleared(p, F.ThicketDepth)
	end)
	band(out, F.Seed + 1, F.Spacing, F.Fill, F.Depth, function(p)
		return not Forest.cleared(p, F.ThicketDepth)
	end)
	return out
end

return Forest
