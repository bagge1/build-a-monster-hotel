--!strict
--[[
	Where everything on Creepy Lane is (GDD §3, Appendix A.1), in world space.
	Shared: the server builds the street and lays guests' paths with it, the
	client's build mode finds the plot's frame with it.

	The lane runs along world X through z = 0; the bus stop is at its west
	end. Plots 1–3 are on the north side (z > 0), plots 4–6 on the south. A
	plot's frame has its origin at the front-left corner of its grid on the
	ground (y = 0), +X along the street and +Z away from it, with no mirroring:
	the south side's frame is the north side's turned 180°.
]]

local Constants = require(script.Parent.Constants)

local G = Constants.Grid
local S = Constants.Street

local StreetLayout = {}

StreetLayout.PlotSize = G.Cells * G.CellSize -- 72 studs

-- The walking surface of the lane and of every plot's ground floor: one slab up from y = 0.
StreetLayout.GroundY = G.SlabThickness

-- The x of each plot's centre along the lane, centre-first so the nearest free plot is claimed first.
local PER_SIDE = S.Plots // 2
local function centreX(column: number): number
	local pitch = StreetLayout.PlotSize + S.PlotGap
	return (column - (PER_SIDE + 1) / 2) * pitch
end

-- The order plots are claimed in (§3: "the nearest free plot"): the middle of each side first.
StreetLayout.ClaimOrder = { 2, 5, 1, 4, 3, 6 }

function StreetLayout.plotFrame(index: number): CFrame
	local side = if index <= PER_SIDE then 1 else -1
	local column = if index <= PER_SIDE then index else index - PER_SIDE
	local cx = centreX(column)
	local half = StreetLayout.PlotSize / 2
	if side == 1 then
		return CFrame.new(cx - half, 0, S.FrontOffset)
	end
	return CFrame.new(cx + half, 0, -S.FrontOffset) * CFrame.Angles(0, math.pi, 0)
end

-- The lobby entrance (the middle of the plot's front edge), plot-local.
StreetLayout.EntranceLocal = Vector3.new(StreetLayout.PlotSize / 2, G.SlabThickness, 0)

-- The point on the lane's centre line in front of a plot.
function StreetLayout.laneFront(index: number): Vector3
	local e = StreetLayout.plotFrame(index):PointToWorldSpace(StreetLayout.EntranceLocal)
	return Vector3.new(e.X, StreetLayout.GroundY, 0)
end

StreetLayout.BusStop = Vector3.new(S.BusStopX, StreetLayout.GroundY, 0)
StreetLayout.LaneEnd = Vector3.new(S.LaneHalfLength, StreetLayout.GroundY, 0)
StreetLayout.HunterCamp = Vector3.new(S.HunterCampX, StreetLayout.GroundY, 0)

return StreetLayout
