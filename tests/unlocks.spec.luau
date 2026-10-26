local Pieces = require(Shared.Pieces)
local Unlocks = require(Shared.Unlocks)

-- A context that meets everything a piece of `location` asks.
local function rich(location: number)
	return {
		location = location,
		unlocked = {},
		rating = 5,
		rooms = 999,
		floors = 99,
		legendaryResident = true,
	}
end

describe("Unlocks", function()
	it("a piece is never met before each of its conditions, and met once all are", function()
		for _, p in Pieces.List do
			local loc = if p.location == 0 then 1 else p.location
			expect.truthy((Unlocks.met(p.id, rich(loc))), `{p.id} met with everything`)
			local u = p.unlock
			if u then
				local function short(field: string, value: any)
					local c = rich(loc)
					c[field] = value
					local ok, why = Unlocks.met(p.id, c)
					expect.truthy(not ok, `{p.id} without {field}`)
					expect.truthy(why ~= nil, `{p.id} says why`)
					expect.truthy(
						not Unlocks.buildable(p.id, c),
						`{p.id} not buildable without {field}`
					)
				end
				if u.rooms then
					short("rooms", u.rooms - 1)
				end
				if u.floor then
					short("floors", u.floor - 1)
				end
				if u.rating then
					short("rating", u.rating - 0.5)
				end
				if u.legendaryResident then
					short("legendaryResident", false)
				end
				-- Exactly at each requirement is enough.
				local exact = rich(loc)
				exact.rooms = u.rooms or 0
				exact.floors = u.floor or 1
				exact.rating = u.rating or 1
				exact.legendaryResident = u.legendaryResident == true
				expect.truthy((Unlocks.met(p.id, exact)), `{p.id} met exactly at its requirement`)
			end
		end
	end)

	it("more rooms, floors, rating or a Legendary never take an unlock away", function()
		local steps = {
			{ rooms = 0, floors = 1, rating = 1, legendaryResident = false },
			{ rooms = 3, floors = 1, rating = 2, legendaryResident = false },
			{ rooms = 5, floors = 2, rating = 3, legendaryResident = false },
			{ rooms = 9, floors = 3, rating = 4, legendaryResident = true },
			{ rooms = 50, floors = 9, rating = 5, legendaryResident = true },
		}
		for _, p in Pieces.List do
			for loc = 1, 3 do
				local was = false
				for _, s in steps do
					local c = rich(loc)
					for k, v in s do
						c[k] = v
					end
					local now = (Unlocks.met(p.id, c))
					expect.truthy(
						now or not was,
						`{p.id} at location {loc} lost at rating {s.rating}`
					)
					was = now
				end
			end
		end
	end)

	it(
		"a piece of another location is never met; a piece of location 0 is every location's",
		function()
			for _, p in Pieces.List do
				for loc = 1, 5 do
					local ok, why = Unlocks.met(p.id, rich(loc))
					if p.location == 0 or p.location == loc then
						expect.truthy(ok, `{p.id} at {loc}`)
					else
						expect.truthy(not ok, `{p.id} (location {p.location}) at {loc}`)
						expect.eq(why, "Location", `{p.id}'s reason`)
					end
				end
			end
			expect.truthy(not Unlocks.met("NoSuchPiece", rich(1)), "an unknown piece")
		end
	)

	-- §6.4: "every room type already unlocked" stays after a rebirth; §11, A.7: the tutorial unlocks early.
	it(
		"once unlocked a piece stays buildable with nothing, and the tutorial unlocks early",
		function()
			for _, p in Pieces.List do
				if p.unlock then
					local loc = if p.location == 0 then 1 else p.location
					local poor = {
						location = loc,
						unlocked = {},
						rating = 1,
						rooms = 0,
						floors = 1,
						legendaryResident = false,
					}
					expect.truthy(not Unlocks.buildable(p.id, poor), `{p.id} locked with nothing`)
					poor.unlocked = { [p.id] = true }
					expect.truthy((Unlocks.buildable(p.id, poor)), `{p.id} kept after a rebirth`)
					poor.unlocked = {}
					poor.tutorial = { [p.id] = true }
					expect.truthy(
						(Unlocks.buildable(p.id, poor)),
						`{p.id} unlocked by the tutorial`
					)
				end
			end
		end
	)
end)
