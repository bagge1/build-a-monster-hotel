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

	it("only the last reviews are kept", function()
		local reviews = {}
		for i = 1, 100 do
			Rating.addReview(reviews, (i % 5) + 1)
		end
		expect.atMost(#reviews, 30)
		expect.eq(reviews[#reviews], (100 % 5) + 1, "newest last")
	end)
end)
