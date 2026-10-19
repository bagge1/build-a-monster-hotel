local Constants = require(Shared.Constants)
local StreetLayout = require(Shared.StreetLayout)
local Walk = require(Shared.Walk)
local Forest = require(Shared.Forest)

local S = Constants.Street

local function onPavement(p: Vector3): boolean
	local az = math.abs(p.Z)
	return az >= S.LaneHalfWidth - 0.01 and az <= S.LaneHalfWidth + S.PavementWidth + 0.01
end

describe("Street", function()
	it(
		"every plot stands behind its forecourt, clear of the lane and of every other plot",
		function()
			for i = 1, S.Plots do
				local f = StreetLayout.plotFrame(i)
				local front = f:PointToWorldSpace(StreetLayout.EntranceLocal)
				expect.near(
					math.abs(front.Z),
					S.LaneHalfWidth + S.ForecourtDepth,
					1e-3,
					`plot {i} front`
				)
				local x0, x1 = StreetLayout.plotSpan(i)
				for j = i + 1, S.Plots do
					local y0, y1 = StreetLayout.plotSpan(j)
					if StreetLayout.side(i) == StreetLayout.side(j) then
						expect.truthy(x1 <= y0 or y1 <= x0, `plots {i} and {j} overlap`)
					end
				end
				expect.truthy(
					onPavement(StreetLayout.pavementFront(i)),
					`plot {i}'s pavement front`
				)
			end
		end
	)

	it(
		"the stops stand in the gaps between plots, on the pavement the bus's door opens onto",
		function()
			for _, stop in StreetLayout.Stops do
				expect.truthy(onPavement(stop.wait), `{stop.name} waits on the pavement`)
				expect.truthy(
					stop.wait.Z > 0,
					"the north pavement: the door is on the bus's +Z side"
				)
				expect.truthy(
					stop.kerb.Z > StreetLayout.BusLaneZ and stop.kerb.Z < S.LaneHalfWidth,
					"the kerb"
				)
				for i = 1, S.Plots do
					local x0, x1 = StreetLayout.plotSpan(i)
					expect.truthy(
						stop.x + 6 <= x0 or stop.x - 6 >= x1,
						`{stop.name}'s shelter in plot {i}`
					)
				end
				expect.eq(StreetLayout.nearestStop(stop.wait), stop, "nearest to itself")
			end
		end
	)

	it("the browse ring is closed and every point on it maps back to its place", function()
		local L = StreetLayout.RingLength
		for s = 0, L - 1, 7 do
			local p = StreetLayout.ringPoint(s)
			expect.near(StreetLayout.ringParam(p) % L, s, 1e-3, `s = {s}`)
		end
		expect.truthy(
			(StreetLayout.ringPoint(L - 0.001) - StreetLayout.ringPoint(0)).Magnitude < 0.01,
			"closed"
		)
	end)

	it(
		"a browse lasts its minute, stays by the pavements and looks at every entrance it passes",
		function()
			local B = Constants.Bus
			local looks = {}
			for i = 1, S.Plots do
				table.insert(looks, {
					s = StreetLayout.ringParam(StreetLayout.pavementFront(i)),
					toward = Vector3.new(0, 0, StreetLayout.side(i)),
				})
			end
			for _, stop in StreetLayout.Stops do
				for _, dir in { 1, -1 } do
					local path, waits = StreetLayout.browse(
						StreetLayout.ringParam(stop.wait),
						dir,
						looks,
						B.BrowseTime,
						B.BrowseSpeed,
						B.EntrancePause
					)
					local t = Walk.duration(path, waits, B.BrowseSpeed)
					expect.near(
						t,
						B.BrowseTime,
						1.5 / B.BrowseSpeed + 1e-6,
						`{stop.name} {dir}: its length`
					)
					local pauses = 0
					for i, p in path do
						local onRing = (StreetLayout.ringPoint(StreetLayout.ringParam(p)) - p).Magnitude
						expect.atMost(
							onRing,
							1.5 + 1e-3,
							`{stop.name} {dir}: point {i} off the ring`
						)
						if waits[i] then
							pauses += 1
							expect.atMost(waits[i], B.EntrancePause, "a pause")
							expect.truthy(onPavement(p), "a pause on the pavement")
						end
					end
					expect.truthy(
						pauses >= 1,
						`{stop.name} {dir}: looks at an entrance within its minute`
					)
				end
			end
		end
	)

	it("between them, a bus's guests browse past every hotel's entrance", function()
		local B = Constants.Bus
		for i = 1, S.Plots do
			local front = StreetLayout.pavementFront(i)
			local look = {
				s = StreetLayout.ringParam(front),
				toward = Vector3.new(0, 0, StreetLayout.side(i)),
			}
			local seen = false
			for _, stop in StreetLayout.Stops do
				for _, side in { 1, -1 } do
					for _, dir in { 1, -1 } do
						local start = StreetLayout.ontoPavement(stop.kerb, side)[1]
						local path, waits = StreetLayout.browse(
							StreetLayout.ringParam(start),
							dir,
							{ look },
							B.BrowseTime,
							B.BrowseSpeed,
							B.EntrancePause
						)
						for k in waits do
							if math.abs(path[k].X - front.X) < 0.01 then
								seen = true
							end
						end
					end
				end
			end
			expect.truthy(seen, `plot {i}'s entrance is passed by some browse`)
		end
	end)

	it(
		"a walker reaches the other pavement straight across the lane, or is already on it",
		function()
			for _, side in { 1, -1 } do
				for _, from in
					{
						StreetLayout.Stops[1].kerb,
						StreetLayout.pavementFront(1),
						StreetLayout.pavementFront(5),
					}
				do
					local pts = StreetLayout.ontoPavement(from, side)
					local last = pts[#pts] or from
					expect.truthy(onPavement(last) and last.Z * side > 0, "on that side's pavement")
					if #pts > 0 then
						expect.near(pts[1].X, from.X, 1e-6, "straight across")
					end
				end
			end
		end
	)

	it(
		"the bus's road runs from the forest past both stops into the forest, with no jumps",
		function()
			local route = StreetLayout.Route
			for i = 2, #route do
				expect.atMost(
					(route[i] - route[i - 1]).Magnitude,
					2 * S.LaneHalfLength + 40 + 1e-3,
					"a segment"
				)
			end
			for _, stop in StreetLayout.Stops do
				local p = StreetLayout.routePoint(StreetLayout.routeDistanceAt(stop.x))
				expect.near(p.X, stop.x, 1e-3, `{stop.name}'s x on the road`)
				expect.near(p.Z, StreetLayout.BusLaneZ, 1e-3, `{stop.name}: on the bus's line`)
			end
			for _, endPoint in { route[1], route[#route] } do
				expect.truthy(
					math.abs(endPoint.Z) > StreetLayout.BackZ + Constants.Forest.Clearing,
					"the road's ends are out among the trees"
				)
			end
		end
	)
end)

describe("Walk", function()
	it(
		"a walk starts at its first point, ends at its last, and stands still while it waits",
		function()
			local path = { Vector3.new(0, 0, 0), Vector3.new(10, 0, 0), Vector3.new(10, 0, 10) }
			local waits = { [2] = 3 }
			local speed = 5
			local total = Walk.duration(path, waits, speed)
			expect.near(total, 20 / speed + 3, 1e-6, "duration")
			expect.near((Walk.sample(path, waits, speed, 0) - path[1]).Magnitude, 0, 1e-6, "start")
			expect.near(
				(Walk.sample(path, waits, speed, total + 5) - path[3]).Magnitude,
				0,
				1e-6,
				"end"
			)
			local a, _, movingA = Walk.sample(path, waits, speed, 2.5)
			local b, _, movingB = Walk.sample(path, waits, speed, 4.5)
			expect.truthy(not movingA and not movingB, "standing during the wait")
			expect.near((a - b).Magnitude, 0, 1e-6, "still")
			local decoded, dw = Walk.decode(Walk.encode(path, waits))
			expect.eq(#decoded, 3, "round trip")
			expect.near(dw[2], 3, 0.01, "the wait survives the round trip")
		end
	)
end)

describe("Forest", function()
	it("no tree stands on the street, a plot, its forecourt or Wing, or the bus's road", function()
		local trees = Forest.layout()
		expect.truthy(#trees > 0, "a forest")
		for _, t in trees do
			local p = t.position
			expect.truthy(not Forest.cleared(p), "in the clearing")
			expect.truthy(StreetLayout.roadDistance(p) >= StreetLayout.RoadWidth / 2, "on the road")
			if math.abs(p.X) <= S.LaneHalfLength + 20 then
				expect.truthy(
					math.abs(p.Z) >= S.LaneHalfWidth + S.PavementWidth,
					"on the lane or a pavement"
				)
			end
			for i = 1, S.Plots do
				local x0, x1 = StreetLayout.plotSpan(i)
				local inside = p.X > x0
					and p.X < x1
					and p.Z * StreetLayout.side(i) > S.LaneHalfWidth
					and p.Z * StreetLayout.side(i) < StreetLayout.BackZ
				expect.truthy(not inside, `on plot {i}`)
			end
		end
	end)

	it(
		"the forest is the same every time, and every tree is one its zone's location has",
		function()
			local a, b = Forest.layout(), Forest.layout()
			expect.eq(#a, #b, "count")
			for i = 1, #a, 17 do
				expect.eq(a[i].position, b[i].position, `tree {i}`)
			end
			for location in Forest.Sets do
				for _, t in a do
					local id = Forest.pickId(location, t.pick)
					expect.truthy(table.find(Forest.Ids, id) ~= nil, id)
				end
			end
			expect.eq(
				Forest.pickId(99, 0.5),
				Forest.pickId(1, 0.5),
				"a location with no set of its own uses Location 1's"
			)
		end
	)
end)
