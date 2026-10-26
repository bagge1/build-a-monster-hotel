local Constants = require(Shared.Constants)
local Rating = require(Shared.Rating)

local BAR = { size = 0, furniture = 0.5, decor = 0 }
local FULL = { size = 1, furniture = 1, decor = 1 }

local function inputs(over)
	local i = {
		roomBars = { BAR, BAR },
		prefsShare = 0.5,
		meanWait = 10,
		checkIns = 5,
		requestShare = 0.5,
		rooms = 2,
		dirtyRooms = 0,
		amenities = 1,
		entertainers = 0,
		decor = 2,
		roomTypes = 1,
	}
	for k, v in over or {} do
		i[k] = v
	end
	return i
end

describe("Rating", function()
	it('a ready room added never lowers Comfort (his "no room deducts points")', function()
		local rooms = {}
		local last = Rating.categories(inputs({ roomBars = rooms })).Comfort
		for _, b in
			{ { size = 0, furniture = 0, decor = 0 }, BAR, FULL, BAR, FULL, FULL, FULL, FULL }
		do
			table.insert(rooms, b)
			local now = Rating.categories(inputs({ roomBars = rooms })).Comfort
			expect.atLeast(now, last, `with {#rooms} rooms`)
			last = now
		end
	end)

	it("stars are between 1 and 5, in half steps", function()
		local cases = {
			{},
			{ roomBars = {}, rooms = 0 },
			{
				roomBars = { FULL, FULL, FULL },
				prefsShare = 1,
				requestShare = 1,
				amenities = 20,
				decor = 99,
				roomTypes = 9,
			},
		}
		for _, over in cases do
			for _, reviews in { {}, { 1, 1, 1 }, { 5, 5 } } do
				local s = Rating.stars(Rating.categories(inputs(over)), reviews)
				expect.atLeast(s, 1)
				expect.atMost(s, 5)
				expect.eq((s * 2) % 1, 0, "half step")
			end
		end
	end)

	it("every category stays within 0 and 100", function()
		local c = Rating.categories(inputs({
			meanWait = 999,
			dirtyRooms = 2,
			amenities = 99,
			entertainers = 99,
			decor = 999,
		}))
		for _, name in Rating.Order do
			expect.atLeast(c[name], 0, name)
			expect.atMost(c[name], 100, name)
		end
	end)

	it("a better category or a better review never lowers the stars", function()
		local c = Rating.categories(inputs())
		local base = Rating.stars(c, { 3, 3 })
		expect.atLeast(
			Rating.stars(Rating.categories(inputs({ amenities = 5 })), { 3, 3 }),
			base,
			"fun"
		)
		expect.atLeast(Rating.stars(c, { 3, 3, 5 }), base, "a 5-star review")
		expect.atLeast(
			Rating.stars(Rating.categories(inputs({ dirtyRooms = 0 })), {}),
			Rating.stars(Rating.categories(inputs({ dirtyRooms = 2 })), {}),
			"clean rooms"
		)
	end)

	-- §5.3: Service from staff coverage, Cleanliness from Housekeeping coverage
	-- and rooms cleaned on time. Rules, not values (Appendix A.4 PLACEHOLDER).
	it("more staff coverage never lowers Service or Cleanliness", function()
		local levels = { 0, 0.6, 1, 1.6, 3, 10 }
		for _, over in { {}, { meanWait = 0, requestShare = 1 }, { dirtyRooms = 2, rooms = 2 } } do
			for n = 1, #levels - 1 do
				local lo, hi = levels[n], levels[n + 1]
				local function cats(e)
					local o = table.clone(over)
					o.frontDesk, o.roomService, o.housekeeping = e, e, e
					return Rating.categories(inputs(o))
				end
				local a, b = cats(lo), cats(hi)
				expect.atLeast(b.Service, a.Service, `Service {lo} → {hi}`)
				expect.atLeast(b.Cleanliness, a.Cleanliness, `Cleanliness {lo} → {hi}`)
				for _, name in Rating.Order do
					if name ~= "Service" and name ~= "Cleanliness" then
						expect.eq(b[name], a[name], `{name} untouched by staff`)
					end
				end
			end
		end
		-- One role at a time, too.
		for _, role in { "frontDesk", "roomService", "housekeeping" } do
			local none = Rating.categories(inputs())
			local some = Rating.categories(inputs({ [role] = 1 }))
			expect.atLeast(some.Service, none.Service, role)
			expect.atLeast(some.Cleanliness, none.Cleanliness, role)
		end
	end)

	it("one Room Service or Housekeeping covers half as much in twice the rooms", function()
		local n = require(Shared.Constants).Rating.RoomsPerStaff
		for role, category in { roomService = "Service", housekeeping = "Cleanliness" } do
			local function gain(rooms)
				-- Low enough before the staff that nothing is clamped at 100.
				local base = { meanWait = 60, requestShare = 0, rooms = rooms, dirtyRooms = rooms }
				local with = table.clone(base)
				with[role] = 1
				return Rating.categories(inputs(with))[category]
					- Rating.categories(inputs(base))[category]
			end
			local small, big = gain(n), gain(2 * n)
			expect.truthy(small > 0, `{role} gives something`)
			expect.truthy(
				math.abs(small - 2 * big) < 1e-9,
				`{role}: {small} in {n} rooms, {big} in {2 * n}`
			)
		end
	end)

	it("on-time cleaning never scores below late cleaning", function()
		for _, over in { {}, { dirtyRooms = 1 }, { dirtyRooms = 2 }, { housekeeping = 1 } } do
			local prev = -1
			for _, share in { 0, 0.25, 0.5, 1 } do
				local o = table.clone(over)
				o.onTimeShare = share
				local c = Rating.categories(inputs(o)).Cleanliness
				expect.atLeast(c, prev, `on-time share {share}`)
				prev = c
			end
		end
	end)

	it("with or without staff, every category stays within 0 and 100", function()
		local hotels = {
			{ frontDesk = 0, roomService = 0, housekeeping = 0, onTimeShare = 0 },
			{ frontDesk = 99, roomService = 99, housekeeping = 99, onTimeShare = 1 },
			{
				frontDesk = 99,
				roomService = 99,
				housekeeping = 99,
				onTimeShare = 5,
				meanWait = 0,
				requestShare = 1,
				perks = { Service = 50, Cleanliness = 50 },
			},
			{ frontDesk = 99, roomService = 99, housekeeping = 99, meanWait = 999, dirtyRooms = 2 },
			{
				frontDesk = 5,
				housekeeping = 5,
				rooms = 0,
				roomBars = {},
				checkIns = 0,
				onTimeShare = 1,
			},
			{ onTimeShare = -1 },
		}
		for _, over in hotels do
			local c = Rating.categories(inputs(over))
			for _, name in Rating.Order do
				expect.atLeast(c[name], 0, name)
				expect.atMost(c[name], 100, name)
			end
		end
	end)

	it("staff earn nothing in a hotel nobody has stayed in or without rooms", function()
		local c = Rating.categories(inputs({
			roomBars = {},
			rooms = 0,
			checkIns = 0,
			frontDesk = 3,
			roomService = 3,
			housekeeping = 3,
			onTimeShare = 1,
		}))
		expect.eq(c.Service, 0, "no Service yet")
		expect.eq(c.Cleanliness, 0, "no Cleanliness without rooms")
	end)

	it("residents' perks earn nothing either before a stay or without rooms (A.4)", function()
		local c = Rating.categories(inputs({
			roomBars = {},
			rooms = 0,
			checkIns = 0,
			perks = { Service = 5, Cleanliness = 5, Fun = 5 },
		}))
		expect.eq(c.Service, 0, "no Service from perks yet")
		expect.eq(c.Cleanliness, 0, "no Cleanliness from perks without rooms")
		expect.atLeast(c.Fun, 5, "Fun's perk is not gated")
	end)

	it("a hotel with nothing in it rates the lowest", function()
		local empty = inputs({
			roomBars = {},
			rooms = 0,
			checkIns = 0,
			prefsShare = 0,
			requestShare = 0,
			amenities = 0,
			decor = 0,
			roomTypes = 0,
		})
		expect.eq(Rating.stars(Rating.categories(empty), {}), 1)
	end)

	-- A.9: "reach the next whole star".
	it(
		"a star request asks the next whole star, never one already met, and none at the top",
		function()
			for _, rating in { 1, 1.5, 2, 3.5, 4, 4.5 } do
				local n = Rating.nextStar(rating) :: number
				expect.truthy(n ~= nil, `a next star at {rating}`)
				expect.truthy(n > rating, `not met as drawn at {rating}`)
				expect.eq(n, math.floor(n), `a whole star at {rating}`)
				expect.atMost(n, math.floor(rating) + 1, `the next one at {rating}`)
			end
			expect.eq(Rating.nextStar(5), nil, "none at 5 stars")
		end
	)

	it("a star request counts only at the hotel it was drawn for", function()
		expect.eq(Rating.towardStar(4, 4, 1, 1), 4, "reached there")
		expect.eq(Rating.towardStar(4, 3.5, 1, 1), 3, "its whole stars there")
		expect.eq(Rating.towardStar(4, 5, 1, 2), 0, "nothing at another hotel")
		expect.eq(Rating.towardStar(4, 4.5, nil, 2), 4, "one drawn before the hotel was kept")
	end)

	it(
		"only the last reviews are kept, exactly as many as kept, the oldest dropped first",
		function()
			local kept = Constants.Stay.ReviewsKept
			local reviews = {}
			for i = 1, 100 do
				Rating.addReview(reviews, (i % 5) + 1)
			end
			expect.eq(#reviews, kept, "as many as kept")
			for j = 1, kept do
				local i = 100 - kept + j
				expect.eq(reviews[j], (i % 5) + 1, `review {i} in place {j}`)
			end
		end
	)

	-- The samples are saved per hotel (2026-10-26 review: in memory only, a
	-- rejoin read a 5★ hotel as about 4★ and a Travel saved that).
	local R = Constants.Rating

	-- A hotel played a while: every window past its cap, as the server fills it.
	local function played(n)
		local s = Rating.newSamples()
		for i = 1, n do
			Rating.push(s.waits, (i * 7) % 23 + 0.25, R.ServiceSampleSize)
			Rating.push(s.prefsShares, ((i * 3) % 5) / 4, R.ServiceSampleSize)
			Rating.push(s.cleanTimes, (i * 11) % (2 * R.CleanOnTime) + 0.5, R.CleanSampleSize)
			s.requestsAsked += 1
			if i % 3 ~= 0 then
				s.requestsDone += 1
			end
		end
		return s
	end

	local function deepCopy(t)
		if typeof(t) ~= "table" then
			return t
		end
		local out = {}
		for k, v in t do
			out[k] = deepCopy(v)
		end
		return out
	end

	local function rate(samples, overdue, over)
		local o = table.clone(over or {})
		for k, v in Rating.sampleInputs(samples, overdue) do
			o[k] = v
		end
		return Rating.categories(inputs(o))
	end

	it("the samples saved and read back give the same categories and stars", function()
		for _, n in { 1, 5, R.ServiceSampleSize, 3 * R.ServiceSampleSize + 1 } do
			for _, overdue in { 0, 1, 3 } do
				for _, over in
					{ {}, { frontDesk = 1, housekeeping = 0.6, perks = { Service = 5 } } }
				do
					local live = played(n)
					local saved = deepCopy(live) -- the profile, as the store hands it back
					local back = Rating.restoreSamples(saved)
					local a, b = rate(live, overdue, over), rate(back, overdue, over)
					for _, name in Rating.Order do
						expect.eq(b[name], a[name], `{name} after {n} stays, {overdue} overdue`)
					end
					for _, reviews in { {}, { 5, 4, 5 } } do
						expect.eq(
							Rating.stars(b, reviews),
							Rating.stars(a, reviews),
							`stars after {n}`
						)
					end
				end
			end
		end
	end)

	it("a window is read back to its cap, the newest kept, as the server keeps it", function()
		local long =
			{ waits = {}, prefsShares = {}, cleanTimes = {}, requestsAsked = 9, requestsDone = 4 }
		local live = Rating.newSamples()
		for i = 1, 3 * R.ServiceSampleSize + 3 * R.CleanSampleSize do
			table.insert(long.waits, i)
			table.insert(long.prefsShares, (i % 4) / 4)
			table.insert(long.cleanTimes, i)
			Rating.push(live.waits, i, R.ServiceSampleSize)
			Rating.push(live.prefsShares, (i % 4) / 4, R.ServiceSampleSize)
			Rating.push(live.cleanTimes, i, R.CleanSampleSize)
		end
		local back = Rating.restoreSamples(long)
		expect.eq(#back.waits, R.ServiceSampleSize, "waits capped")
		expect.eq(#back.prefsShares, R.ServiceSampleSize, "preferences capped")
		expect.eq(#back.cleanTimes, R.CleanSampleSize, "cleanings capped")
		for name, list in
			{ waits = live.waits, prefsShares = live.prefsShares, cleanTimes = live.cleanTimes }
		do
			for j, v in list do
				expect.eq((back :: any)[name][j], v, `{name} {j}`)
			end
		end
		expect.eq(back.requestsAsked, 9, "requests asked kept")
		expect.eq(back.requestsDone, 4, "requests done kept")
	end)

	it("nothing saved, or what is not a number, reads as a hotel never stayed in", function()
		for _, saved in
			{ nil, {}, "x", { waits = "x", prefsShares = { 0 / 0 }, requestsAsked = -1 } }
		do
			local back = Rating.restoreSamples(saved)
			local i = Rating.sampleInputs(back, 0)
			expect.eq(i.checkIns, 0, "no check-ins")
			expect.eq(#back.prefsShares, 0, "no preferences")
			expect.eq(back.requestsAsked, 0, "no requests")
			expect.eq(rate(back, 0).Service, 0, "no Service yet")
		end
		local mixed = Rating.restoreSamples({ waits = { 1, 0 / 0, math.huge, 3 } })
		expect.eq(#mixed.waits, 2, "only finite waits kept")
		expect.eq(mixed.waits[2], 3, "in their order")
	end)

	it("a hotel read back rates as it stood, never as one nobody stayed in", function()
		local live = played(2 * R.ServiceSampleSize)
		local back = Rating.restoreSamples(deepCopy(live))
		local stood = rate(live, 0)
		local empty = rate(Rating.newSamples(), 0)
		expect.truthy(stood.Service > 0, "Service earned")
		expect.eq(empty.Service, 0, "an empty window has none")
		expect.eq(rate(back, 0).Service, stood.Service, "read back keeps it")
		expect.atLeast(rate(back, 0).Comfort, empty.Comfort, "and Comfort's preferences")
	end)
end)
