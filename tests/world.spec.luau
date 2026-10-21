local Constants = require(Shared.Constants)
local StreetLayout = require(Shared.StreetLayout)
local Forest = require(Shared.Forest)

local S = Constants.Street
local N = StreetLayout.Streets

-- Every point a street is made of: its plots' corners and entrances, its stops, its ring and its road.
local function pointsOf(street: number): { Vector3 }
	local out = {}
	for i = 1, S.Plots do
		local f = StreetLayout.plotFrame(i, street)
		table.insert(out, f.Position)
		table.insert(
			out,
			f:PointToWorldSpace(Vector3.new(StreetLayout.PlotSize, 0, StreetLayout.PlotSize))
		)
		table.insert(out, StreetLayout.pavementFront(i, street))
		table.insert(out, StreetLayout.laneFront(i, street))
	end
	for _, stop in StreetLayout.stops(street) do
		table.insert(out, stop.kerb)
		table.insert(out, stop.wait)
	end
	for s = 0, StreetLayout.RingLength, 11 do
		table.insert(out, StreetLayout.ringPoint(s, street))
	end
	for _, p in StreetLayout.route(street) do
		table.insert(out, p)
	end
	return out
end

describe("World", function()
	it(
		"there is a street for every location of the chain, the first where Creepy Lane stands",
		function()
			expect.eq(N, Constants.Chain.Locations, "streets")
			for i = 1, S.Plots do
				expect.eq(
					StreetLayout.plotFrame(i, 1),
					StreetLayout.plotFrame(i),
					`plot {i}: street 1 by default`
				)
				expect.eq(
					StreetLayout.pavementFront(i, 1),
					StreetLayout.pavementFront(i),
					`plot {i}'s pavement`
				)
			end
			expect.eq(StreetLayout.stops(1), StreetLayout.Stops, "Creepy Lane's stops")
			expect.eq(StreetLayout.route(1), StreetLayout.Route, "Creepy Lane's road")
		end
	)

	it("every street is Creepy Lane's layout moved along X, nothing else", function()
		for street = 2, N do
			local dx = StreetLayout.originX(street)
			for i = 1, S.Plots do
				local a, b = StreetLayout.plotFrame(i), StreetLayout.plotFrame(i, street)
				expect.near(
					(b.Position - a.Position - Vector3.new(dx, 0, 0)).Magnitude,
					0,
					1e-6,
					`plot {i}`
				)
				expect.near(b.LookVector:Dot(a.LookVector), 1, 1e-6, `plot {i} turned`)
			end
			for k, stop in StreetLayout.stops(street) do
				expect.near(stop.x - StreetLayout.Stops[k].x, dx, 1e-6, stop.name)
				expect.eq(stop.street, street, `{stop.name}'s street`)
			end
		end
	end)

	it("streets never overlap: each keeps to its own stretch of X, apart from the next", function()
		for street = 1, N do
			local lo = StreetLayout.originX(street) - StreetLayout.HalfExtent
			local hi = StreetLayout.originX(street) + StreetLayout.HalfExtent
			for _, p in pointsOf(street) do
				expect.truthy(
					p.X >= lo - 1e-6 and p.X <= hi + 1e-6,
					`street {street}: a point at x {p.X}`
				)
			end
			if street < N then
				expect.truthy(
					hi < StreetLayout.originX(street + 1) - StreetLayout.HalfExtent,
					`streets {street} and {street + 1} overlap`
				)
			end
		end
	end)

	it(
		"every street's plots are disjoint, from each other and from every other street's",
		function()
			local all = {}
			for street = 1, N do
				for i = 1, S.Plots do
					local x0, x1 = StreetLayout.plotSpan(i, street)
					table.insert(
						all,
						{ street = street, i = i, x0 = x0, x1 = x1, side = StreetLayout.side(i) }
					)
				end
			end
			for a = 1, #all do
				for b = a + 1, #all do
					local p, q = all[a], all[b]
					if p.side == q.side then
						expect.truthy(
							p.x1 <= q.x0 or q.x1 <= p.x0,
							`street {p.street} plot {p.i} and street {q.street} plot {q.i} overlap`
						)
					end
				end
			end
		end
	)

	it("a point's inferred street is the street it lies on", function()
		for street = 1, N do
			for _, p in pointsOf(street) do
				expect.eq(StreetLayout.streetAt(p), street, `street {street}: a point at x {p.X}`)
			end
			for _, stop in StreetLayout.stops(street) do
				expect.eq(
					StreetLayout.nearestStop(stop.wait),
					stop,
					`{stop.name} nearest to itself`
				)
				expect.eq(StreetLayout.stopNamed(stop.name), stop, `{stop.name} by its name`)
				local p = StreetLayout.routePoint(StreetLayout.routeDistanceAt(stop.x), street)
				expect.near(p.X, stop.x, 1e-3, `{stop.name}'s x on its street's road`)
			end
			for s = 0, StreetLayout.RingLength - 1, 13 do
				local p = StreetLayout.ringPoint(s, street)
				expect.near(
					StreetLayout.ringParam(p) % StreetLayout.RingLength,
					s,
					1e-3,
					`street {street} ring {s}`
				)
			end
		end
	end)

	it("a browse on a street stays on that street's pavements", function()
		local B = Constants.Bus
		for street = 1, N do
			local stop = StreetLayout.stops(street)[1]
			local path = StreetLayout.browse(
				StreetLayout.ringParam(stop.wait),
				1,
				{},
				B.BrowseTime,
				B.BrowseSpeed,
				B.EntrancePause,
				street
			)
			for _, p in path do
				expect.eq(StreetLayout.streetAt(p), street, `street {street}'s browse at x {p.X}`)
			end
		end
	end)

	it(
		"the road between two streets runs from one lane's end to the next lane's start, clear of every plot",
		function()
			for street = 1, N - 1 do
				local a, b = StreetLayout.link(street)
				expect.truthy(a ~= nil and b ~= nil, `a road from street {street}`)
				local x0, x1 = (a :: Vector3).X, (b :: Vector3).X
				expect.truthy(x0 < x1, "it runs east")
				for s = street, street + 1 do
					for i = 1, S.Plots do
						local p0, p1 = StreetLayout.plotSpan(i, s)
						expect.truthy(p1 <= x0 or p0 >= x1, `street {s} plot {i} on the road`)
					end
				end
			end
			expect.truthy(StreetLayout.link(N) == nil, "none after the last street")
		end
	)

	it(
		"the look changes gradually: never back, and each street's own stretch is its own",
		function()
			for street = 1, N do
				local a, _, t = StreetLayout.blend(StreetLayout.originX(street))
				expect.eq(a, street, `street {street}'s centre`)
				expect.eq(t, 0, `street {street}'s centre is its own look`)
			end
			local last = -1
			local lastA = 1
			for x = StreetLayout.originX(1), StreetLayout.originX(N), 25 do
				local a, _, t = StreetLayout.blend(x)
				local u = a + t -- how far along the streets' looks
				expect.truthy(u >= last - 1e-9, `the look goes back at x {x}`)
				expect.truthy(a >= lastA, "streets in order")
				last, lastA = u, a
			end
		end
	)
end)

describe("World forest", function()
	local trees = Forest.layout()

	it("no tree stands on any street's lane, plots or road", function()
		for _, t in trees do
			local p = t.position
			expect.truthy(not Forest.cleared(p), "in a clearing")
			local street = StreetLayout.streetAt(p)
			for i = 1, S.Plots do
				local x0, x1 = StreetLayout.plotSpan(i, street)
				local side = StreetLayout.side(i)
				local inside = p.X > x0
					and p.X < x1
					and p.Z * side > S.LaneHalfWidth
					and p.Z * side < StreetLayout.BackZ
				expect.truthy(not inside, `on street {street}'s plot {i}`)
			end
			expect.truthy(StreetLayout.roadDistance(p) >= StreetLayout.RoadWidth / 2, "on a road")
		end
	end)

	it("every tree is its street's location's, or the next one's between two streets", function()
		local seen = {}
		for _, t in trees do
			local a, b, blend = StreetLayout.blend(t.position.X)
			expect.truthy(t.location == a or t.location == b, "a location from elsewhere")
			if blend == 0 then
				expect.eq(t.location, a, "a street's own stretch")
			end
			seen[t.location] = true
		end
		for street = 1, N do
			expect.truthy(seen[street], `trees of location {street}`)
		end
	end)
end)
