local Constants = require(Shared.Constants)
local Cosmetics = require(Shared.Cosmetics)
local Grid = require(Shared.Grid)
local Showcase = require(Shared.Showcase)

describe("Showcase (A.11.4)", function()
	it("the weekly count counts each liker once a week, and starts again the next", function()
		local rec = { week = 0, count = 0, by = {} }
		expect.truthy(Showcase.countWeekly(rec, "1", 10), "first like counts")
		expect.truthy(not Showcase.countWeekly(rec, "1", 10), "same liker, same week")
		expect.truthy(Showcase.countWeekly(rec, "2", 10), "another liker")
		expect.eq(Showcase.weekly(rec, 10), 2)
		expect.eq(Showcase.weekly(rec, 11), 0)
		expect.truthy(Showcase.countWeekly(rec, "1", 11), "the next week counts again")
		expect.eq(Showcase.weekly(rec, 11), 1)
	end)

	it("a week starts on a Monday", function()
		local monday = 4 * 86400 + 7 * 86400 * 100 -- 1970-01-05 is a Monday
		expect.eq(Showcase.week(monday), Showcase.week(monday + 6 * 86400 + 86399))
		expect.truthy(
			Showcase.week(monday) ~= Showcase.week(monday - 1),
			"Sunday is the week before"
		)
	end)

	it("a like counts only after the day's play time", function()
		expect.truthy(not Showcase.canLike(0), "no play")
		expect.truthy(not Showcase.canLike(Constants.Showcase.LikeAfterPlay - 1), "just short")
		expect.truthy(Showcase.canLike(Constants.Showcase.LikeAfterPlay), "enough")
	end)

	it("milestones are sign cosmetics, rising, one per threshold, never paid", function()
		local seen = 0
		for _, n in Constants.Showcase.Milestones do
			local at = Showcase.milestones(n)
			local below = Showcase.milestones(n - 1)
			expect.eq(#at, #below + 1)
			local c = at[#at]
			expect.eq(c.slot, "Sign")
			expect.truthy(c.pass == nil, `{c.id} is not sold`)
			seen += 1
		end
		expect.eq(#Showcase.milestones(0), 0)
		expect.eq(seen, #Showcase.milestones(math.huge))
		expect.truthy(Showcase.nextMilestone(math.huge) == nil, "none past the last")
		local first = Showcase.nextMilestone(0)
		expect.truthy(first and Cosmetics.get(first.id), "the first is a cosmetic")
	end)

	it("each street's favourite has the most weekly likes; none without any", function()
		local best = Showcase.favourites({
			{ key = "1", street = 1, week = 3, likes = 5 },
			{ key = "2", street = 1, week = 4, likes = 1 },
			{ key = "3", street = 2, week = 0, likes = 99 },
			{ key = "4", street = 3, week = 2, likes = 7 },
			{ key = "5", street = 3, week = 2, likes = 9 },
		})
		expect.eq(best[1], "2")
		expect.truthy(best[2] == nil, "lifetime likes alone make no favourite")
		expect.eq(best[3], "5")
	end)

	it("the panel's order puts the street's favourite first, ties included", function()
		-- 2026-10-26 night: two hotels at 1 weekly and 1 lifetime like; the
		-- panel ordered by plot index and showed the favourite second.
		local list = {
			{ key = "-3", street = 1, week = 1, likes = 1, index = 2 },
			{ key = "-1", street = 1, week = 1, likes = 1, index = 3 },
		}
		local best = Showcase.favourites(list)
		table.sort(list, Showcase.before)
		expect.eq(list[1].key, best[1])
	end)

	it("a lobby is the hotel's own floor-1 tiles", function()
		local tiles = {}
		for _, c in Grid.startTiles() do
			tiles[tostring(Grid.tileKey(1, c.x, c.z))] = true
		end
		local c = Grid.startTiles()[1]
		local centre = Grid.cellCentre(1, c) + Vector3.new(0, 3, 0)
		expect.truthy(Showcase.inside(tiles, centre), "on a start tile")
		expect.truthy(
			not Showcase.inside(tiles, centre + Vector3.new(0, Constants.Grid.FloorHeight, 0)),
			"not upstairs"
		)
		expect.truthy(not Showcase.inside(tiles, Vector3.new(-5, 3, -5)), "not outside the plot")
		expect.truthy(not Showcase.inside({}, centre), "not on a tile the hotel lacks")
	end)
end)
