local Rating = require(Shared.Rating)

local function inputs(over)
	local i = {
		roomTiers = { 1, 1 },
		prefsShare = 0.5,
		meanWait = 10,
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
	it("stars are between 1 and 5, in half steps", function()
		local cases = {
			{},
			{ roomTiers = {}, rooms = 0 },
			{
				roomTiers = { 5, 5, 5 },
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
		local c = Rating.categories(
			inputs({
				meanWait = 999,
				dirtyRooms = 2,
				amenities = 99,
				entertainers = 99,
				decor = 999,
			})
		)
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

	it("only the last reviews are kept", function()
		local reviews = {}
		for i = 1, 100 do
			Rating.addReview(reviews, (i % 5) + 1)
		end
		expect.atMost(#reviews, 30)
		expect.eq(reviews[#reviews], (100 % 5) + 1, "newest last")
	end)
end)
