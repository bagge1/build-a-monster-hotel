--!strict
--[[
	Where everything on Creepy Lane is (GDD §3, §5.4, Appendix A.1), in world
	space. Shared: the server builds the street and lays guests' paths with it,
	the client draws the bus and the forest and finds a plot's frame with it.

	The lane runs along world X through z = 0, 48 wide. Along each edge runs
	an 8-stud **pavement** the bus's guests browse on; behind it each plot's
	16-stud yard, the two together the 24-stud **forecourt** (his yes,
	2026-10-19), so a plot's front edge is 48 from the lane's centre. The
	first half of the plots are on the north side (z > 0), the rest on the
	south (`Constants.Street.Plots`, 10 now: 1–5 north, 6–10 south). A plot's frame
	has its origin at the front-left corner of its grid on the ground (y = 0),
	+X along the street and +Z away from it, with no mirroring: the south
	side's frame is the north side's turned 180°.

	The Night Bus drives east along the lane's north half, its door toward the
	north pavement, and **stops twice**, between the first two plots and the
	last two (his ruling, 2026-10-19; `BusStopX`). It comes out of the forest round a bend at the west end and
	goes back into it round a bend at the east end (`route`).

	ONE WORLD (GDD §3, §6.4, his ruling 2026-10-20): a street per location of
	the chain, street s being location s's, each Creepy Lane's layout moved
	`World.StreetSpacing` along +X from the one before; street 1 is Creepy Lane
	where it always stood. A function that cannot tell the street from what it
	is given takes it as its last argument, `street`, street 1 when left out;
	one given a world point infers it from the point's X (`streetAt`). The
	streets are joined by a road through the forest along the lanes' line
	(`link`), and their looks blend into each other across it (`blend`).
]]

local Constants = require(script.Parent.Constants)

local G = Constants.Grid
local S = Constants.Street
local W = Constants.World

local StreetLayout = {}

-- ===== The world (GDD §3, §6.4) =====

StreetLayout.Streets = Constants.Chain.Locations -- one per location of the chain
StreetLayout.Spacing = W.StreetSpacing

-- The world X of a street's centre: Creepy Lane's x = 0 moved along.
function StreetLayout.originX(street: number?): number
	return ((street or 1) - 1) * W.StreetSpacing
end

local function offset(street: number?): Vector3
	return Vector3.new(StreetLayout.originX(street), 0, 0)
end

-- The street a world point stands on or nearest to, from its X alone.
function StreetLayout.streetAt(p: Vector3): number
	return math.clamp(math.floor(p.X / W.StreetSpacing + 0.5) + 1, 1, StreetLayout.Streets)
end

-- A world X in its street's own frame (Creepy Lane's numbers).
local function localX(x: number): number
	return x - StreetLayout.originX(StreetLayout.streetAt(Vector3.new(x, 0, 0)))
end

StreetLayout.PlotSize = G.Cells * G.CellSize -- 144 studs

-- The walking surface of the lane, the pavements and every plot's ground floor: one slab up from y = 0.
StreetLayout.GroundY = G.SlabThickness

-- The distance from the lane's centre line to a plot's front edge: the lane's half and the forecourt.
StreetLayout.PlotFront = S.LaneHalfWidth + S.ForecourtDepth -- 48

-- The pavement's centre line, either side: where browsing guests walk.
StreetLayout.PavementZ = S.LaneHalfWidth + S.PavementWidth / 2 -- 28

-- The x of each plot's centre along the lane, centre-first so the nearest free plot is claimed first.
local PER_SIDE = S.Plots // 2
local PITCH = StreetLayout.PlotSize + S.PlotGap
local function centreX(column: number): number
	return (column - (PER_SIDE + 1) / 2) * PITCH
end

-- The order plots are claimed in (§3: "the nearest free plot"): the middle of each side first, then outward.
StreetLayout.ClaimOrder = (function(): { number }
	local columns = {}
	for c = 1, PER_SIDE do
		table.insert(columns, c)
	end
	local mid = (PER_SIDE + 1) / 2
	table.sort(columns, function(a, b)
		local da, db = math.abs(a - mid), math.abs(b - mid)
		return if da ~= db then da < db else a < b
	end)
	local order = {}
	for _, c in columns do
		table.insert(order, c)
		table.insert(order, c + PER_SIDE)
	end
	return order
end)()

-- +1 for the north side's plots, −1 for the south's.
function StreetLayout.side(index: number): number
	return if index <= PER_SIDE then 1 else -1
end

function StreetLayout.plotFrame(index: number, street: number?): CFrame
	local side = StreetLayout.side(index)
	local column = if side == 1 then index else index - PER_SIDE
	local cx = centreX(column) + StreetLayout.originX(street)
	local half = StreetLayout.PlotSize / 2
	if side == 1 then
		return CFrame.new(cx - half, 0, StreetLayout.PlotFront)
	end
	return CFrame.new(cx + half, 0, -StreetLayout.PlotFront) * CFrame.Angles(0, math.pi, 0)
end

-- The lobby entrance (the middle of the plot's front edge), plot-local.
StreetLayout.EntranceLocal = Vector3.new(StreetLayout.PlotSize / 2, G.SlabThickness, 0)

local function entrance(index: number, street: number?): Vector3
	return StreetLayout.plotFrame(index, street):PointToWorldSpace(StreetLayout.EntranceLocal)
end

-- The point on the lane's centre line in front of a plot.
function StreetLayout.laneFront(index: number, street: number?): Vector3
	local e = entrance(index, street)
	return Vector3.new(e.X, StreetLayout.GroundY, 0)
end

-- The point on the pavement's centre line in front of a plot's entrance.
function StreetLayout.pavementFront(index: number, street: number?): Vector3
	local e = entrance(index, street)
	return Vector3.new(e.X, StreetLayout.GroundY, StreetLayout.side(index) * StreetLayout.PavementZ)
end

-- The x span of a plot's footprint (its forecourt has the same span).
function StreetLayout.plotSpan(index: number, street: number?): (number, number)
	local x = entrance(index, street).X
	return x - StreetLayout.PlotSize / 2, x + StreetLayout.PlotSize / 2
end

-- How far the street reaches from the lane: the plots' backs and the Resident Wing behind them.
StreetLayout.BackZ = StreetLayout.PlotFront + StreetLayout.PlotSize + G.WingDepth -- 240

-- ===== The bus stops =====

-- The bus's line: the lane's north half, its door side (+Z, MODELS.md "NightBus") toward the north pavement.
StreetLayout.BusLaneZ = S.LaneHalfWidth - 9

export type Stop = {
	name: string, -- unique in the world: West and East on Creepy Lane, West_<s> and East_<s> on street s
	street: number,
	x: number,
	kerb: Vector3, -- where guests step off the bus and on again, at the pavement's edge
	wait: Vector3, -- where guests wait for the bus, on the pavement
}
local stopsOf: { { Stop } } = {}
for street = 1, StreetLayout.Streets do
	local list: { Stop } = {}
	for i, name in { "West", "East" } do
		local x = (if i == 1 then -1 else 1) * S.BusStopX + StreetLayout.originX(street)
		table.insert(list, {
			name = if street == 1 then name else `{name}_{street}`,
			street = street,
			x = x,
			kerb = Vector3.new(x, StreetLayout.GroundY, S.LaneHalfWidth - 1),
			wait = Vector3.new(x, StreetLayout.GroundY, StreetLayout.PavementZ),
		})
	end
	stopsOf[street] = list
end
StreetLayout.Stops = stopsOf[1] -- Creepy Lane's

-- A street's two stops, West then East.
function StreetLayout.stops(street: number?): { Stop }
	return stopsOf[street or 1] or stopsOf[1]
end

-- The stop of that name, on any street, or nil.
function StreetLayout.stopNamed(name: string): Stop?
	for _, list in stopsOf do
		for _, s in list do
			if s.name == name then
				return s
			end
		end
	end
	return nil
end

-- The nearest stop on the street the point stands on.
function StreetLayout.nearestStop(p: Vector3): Stop
	local list = StreetLayout.stops(StreetLayout.streetAt(p))
	local best = list[1]
	for _, s in list do
		if math.abs(s.x - p.X) < math.abs(best.x - p.X) then
			best = s
		end
	end
	return best
end

StreetLayout.WestEnd = Vector3.new(-S.LaneHalfLength, StreetLayout.GroundY, 0)
StreetLayout.HunterCamp = Vector3.new(S.HunterCampX, StreetLayout.GroundY, 0)

-- A street's Hunter Camp end (§8.1): Creepy Lane's `HunterCamp`, moved along.
function StreetLayout.hunterCamp(street: number?): Vector3
	return StreetLayout.HunterCamp + offset(street)
end

-- Where a street's lane surface ends, either side of its centre.
StreetLayout.LaneEnd = S.LaneHalfLength + 20

--[[ Where a world X is between two streets' looks (§3: "the environment
	changing gradually from one into the next"): the street below it, the one
	above, and how far from the first's look to the second's, 0 up to the
	first's lane end and 1 from the second's lane start on. Before the first
	street and past the last, that street's own look. ]]
function StreetLayout.blend(x: number): (number, number, number)
	local a = math.clamp(math.floor(x / W.StreetSpacing) + 1, 1, StreetLayout.Streets)
	local b = math.min(a + 1, StreetLayout.Streets)
	if a == b then
		return a, b, 0
	end
	local lx = x - StreetLayout.originX(a)
	local span = W.StreetSpacing - 2 * StreetLayout.LaneEnd
	return a, b, math.clamp((lx - StreetLayout.LaneEnd) / span, 0, 1)
end

-- The road between `street` and the next, along the lanes' line: its two ends (nil from the last street on).
function StreetLayout.link(street: number): (Vector3?, Vector3?)
	if street < 1 or street >= StreetLayout.Streets then
		return nil, nil
	end
	local y = StreetLayout.GroundY
	return Vector3.new(StreetLayout.originX(street) + StreetLayout.LaneEnd, y, 0),
		Vector3.new(StreetLayout.originX(street + 1) - StreetLayout.LaneEnd, y, 0)
end

-- ===== Walking the pavements (§4.3: browsing) =====

--[[ The browse ring: the north pavement west to east, across the lane at its
	east end, the south pavement back west, and across at the west end. A
	point on it is its distance `s` from the ring's start (the north-west
	corner) in the +1 direction; −1 walks it the other way. ]]
local RING_X = (PER_SIDE - 1) / 2 * PITCH + StreetLayout.PlotSize / 2 + 10 -- 10 past the last plot's edge
local PZ = StreetLayout.PavementZ
local RING = {
	Vector3.new(-RING_X, StreetLayout.GroundY, PZ),
	Vector3.new(RING_X, StreetLayout.GroundY, PZ),
	Vector3.new(RING_X, StreetLayout.GroundY, -PZ),
	Vector3.new(-RING_X, StreetLayout.GroundY, -PZ),
}
local RING_AT = { 0, 2 * RING_X, 2 * RING_X + 2 * PZ, 4 * RING_X + 2 * PZ } -- each corner's s
StreetLayout.RingLength = 4 * RING_X + 4 * PZ
StreetLayout.RingX = RING_X

local function wrap(s: number): number
	return s % StreetLayout.RingLength
end

-- The point at `s` along a street's ring.
function StreetLayout.ringPoint(s: number, street: number?): Vector3
	s = wrap(s)
	for i = 4, 1, -1 do
		if s >= RING_AT[i] then
			local a, b = RING[i], RING[i % 4 + 1]
			local len = (b - a).Magnitude
			return a:Lerp(b, (s - RING_AT[i]) / len) + offset(street)
		end
	end
	return RING[1] + offset(street)
end

-- The ring's `s` nearest to a point on or by a pavement, on the point's own street.
function StreetLayout.ringParam(p: Vector3): number
	local x = localX(p.X)
	if x >= RING_X - 0.01 then
		return RING_AT[2] + math.clamp(PZ - p.Z, 0, 2 * PZ)
	elseif x <= -RING_X + 0.01 then
		return RING_AT[4] + math.clamp(p.Z + PZ, 0, 2 * PZ)
	elseif p.Z >= 0 then
		return x + RING_X
	end
	return RING_AT[3] + (RING_X - x)
end

export type Look = { s: number, toward: Vector3 } -- an entrance on the ring, and which way its hotel is

--[[ A browse (§4.3, his yes 2026-10-19): from the ring's `s0`, walking in
	`dir` at `speed`, pausing `pause` seconds a step in front of every entrance
	in `looks`, until `budget` seconds have passed, on `street`'s ring.
	Returns the path, its waits, and the ring's `s` where it ends. ]]
function StreetLayout.browse(
	s0: number,
	dir: number,
	looks: { Look },
	budget: number,
	speed: number,
	pause: number,
	street: number?
): ({ Vector3 }, { [number]: number }, number)
	local path: { Vector3 } = { StreetLayout.ringPoint(s0, street) }
	local waits: { [number]: number } = {}
	local left = budget
	-- Every event ahead along the walk: corners and entrances, by distance from s0.
	local events = {}
	local L = StreetLayout.RingLength
	local function ahead(s: number): number
		local d = if dir > 0 then wrap(s - s0) else wrap(s0 - s)
		return if d < 0.01 then L else d -- one at the very start is met a lap later
	end
	for _, c in RING_AT do
		table.insert(events, { d = ahead(c), look = nil :: Look? })
	end
	for _, look in looks do
		table.insert(events, { d = ahead(look.s), look = look :: Look? })
	end
	table.sort(events, function(a, b)
		return a.d < b.d
	end)
	local walked, lap = 0, 0
	while left > 0 do
		for _, e in events do
			local d = e.d + lap * L
			local t = (d - walked) / speed
			if t >= left then
				-- Out of time on the way: stop where the minute ends.
				walked += left * speed
				table.insert(path, StreetLayout.ringPoint(s0 + dir * walked, street))
				left = 0
				break
			end
			left -= t
			walked = d
			local at = StreetLayout.ringPoint(s0 + dir * d, street)
			table.insert(path, at)
			local look = e.look
			if look then
				-- A step toward the hotel, a look, and back onto the pavement's line.
				local step = at + look.toward * 1.5
				local w = math.min(pause, math.max(0, left - 1.5 / speed))
				table.insert(path, step)
				waits[#path] = w
				left -= 1.5 / speed + w
				if left <= 0 then
					break
				end
				local back = math.min(left, 1.5 / speed)
				table.insert(path, step:Lerp(at, back * speed / 1.5))
				left -= back
				if left <= 0 then
					break
				end
			end
		end
		lap += 1
	end
	return path, waits, wrap(s0 + dir * walked)
end

--[[ The points that take a walker from `from` onto the pavement on `side`
	(+1 north, −1 south): straight across the lane where it stands, or none
	if it is on that pavement already. ]]
function StreetLayout.ontoPavement(from: Vector3, side: number): { Vector3 }
	local z = side * PZ
	if from.Z * side >= S.LaneHalfWidth - 0.5 then
		return {}
	end
	return { Vector3.new(from.X, StreetLayout.GroundY, z) }
end

-- ===== The bus's road =====

--[[ The road the bus drives, from deep in the forest to deep in the forest:
	south out of the trees west of the street, round the west bend onto the
	lane, along the lane, round the east bend and away south into the trees.
	A polyline along the bus's centre line. ]]
local function buildRoute(): { Vector3 }
	local y = StreetLayout.GroundY
	local R = S.BendRadius
	local zLane = StreetLayout.BusLaneZ
	local xEnd = S.LaneHalfLength + 20 -- where the lane's surface ends
	local pts: { Vector3 } = {}
	local steps = 9
	-- West: south out of the trees, then round (−xEnd, zLane + R) onto the lane, heading east.
	table.insert(pts, Vector3.new(-xEnd - R, y, zLane + R + S.ForestRoad))
	for i = 0, steps do
		local a = math.rad(180 - 90 * i / steps) -- from pointing −X to pointing −Z from the centre
		table.insert(pts, Vector3.new(-xEnd + R * math.cos(a), y, zLane + R - R * math.sin(a)))
	end
	-- East: round (xEnd, zLane − R) off the lane, then south into the trees.
	for i = 0, steps do
		local a = math.rad(90 - 90 * i / steps) -- from pointing +Z to pointing +X from the centre
		table.insert(pts, Vector3.new(xEnd + R * math.cos(a), y, zLane - R + R * math.sin(a)))
	end
	table.insert(pts, Vector3.new(xEnd + R, y, zLane - R - S.ForestRoad))
	return pts
end
StreetLayout.Route = buildRoute() -- Creepy Lane's
StreetLayout.RoadWidth = 16
-- How far either side of its centre a street reaches in X: its road's bends into the forest.
StreetLayout.HalfExtent = StreetLayout.LaneEnd + S.BendRadius + StreetLayout.RoadWidth / 2

local routesOf: { { Vector3 } } = { StreetLayout.Route }
for street = 2, StreetLayout.Streets do
	local list = {}
	for _, p in StreetLayout.Route do
		table.insert(list, p + offset(street))
	end
	routesOf[street] = list
end

-- A street's road, from deep in the forest to deep in the forest.
function StreetLayout.route(street: number?): { Vector3 }
	return routesOf[street or 1] or StreetLayout.Route
end

local routeAt: { number } = { 0 }
for i = 2, #StreetLayout.Route do
	routeAt[i] = routeAt[i - 1] + (StreetLayout.Route[i] - StreetLayout.Route[i - 1]).Magnitude
end
StreetLayout.RouteLength = routeAt[#routeAt]

-- The point at `s` studs along a street's road, and the way the road runs there.
function StreetLayout.routePoint(s: number, street: number?): (Vector3, Vector3)
	local route = StreetLayout.route(street)
	s = math.clamp(s, 0, StreetLayout.RouteLength)
	for i = 2, #route do
		if s <= routeAt[i] or i == #route then
			local a, b = route[i - 1], route[i]
			local len = routeAt[i] - routeAt[i - 1]
			return a:Lerp(b, if len > 0 then (s - routeAt[i - 1]) / len else 0), (b - a).Unit
		end
	end
	return route[#route], Vector3.xAxis
end

-- How far along its street's road a point on the lane's straight is (the stops), the same on every street.
function StreetLayout.routeDistanceAt(x: number): number
	-- The lane's straight is the segment between the two bends.
	local i = 11 -- the west bend's last point: the straight starts here
	return routeAt[i] + (localX(x) - StreetLayout.Route[i].X)
end

-- The shortest distance from a point to its own street's road's centre line, on the ground.
function StreetLayout.roadDistance(p: Vector3): number
	local best = math.huge
	local q = Vector3.new(p.X, 0, p.Z)
	local route = StreetLayout.route(StreetLayout.streetAt(p))
	for i = 2, #route do
		local a = Vector3.new(route[i - 1].X, 0, route[i - 1].Z)
		local b = Vector3.new(route[i].X, 0, route[i].Z)
		local ab = b - a
		local t = math.clamp((q - a):Dot(ab) / ab:Dot(ab), 0, 1)
		best = math.min(best, (a + ab * t - q).Magnitude)
	end
	return best
end

return StreetLayout
