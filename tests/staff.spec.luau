local Staff = require(Shared.Staff)

local PATH = {
	Vector3.new(0, 0, 0),
	Vector3.new(10, 0, 0),
	Vector3.new(10, 6, 8),
	Vector3.new(-4, 6, 8),
}

local function close(a: Vector3, b: Vector3, what: string)
	expect.atMost((a - b).Magnitude, 0.1, what)
end

describe("Staff", function()
	it("an errand starts at its post and ends at the door", function()
		local total = Staff.length(PATH)
		close((Staff.along(PATH, 0)), PATH[1], "start")
		close((Staff.along(PATH, total)), PATH[#PATH], "end")
		close((Staff.along(PATH, total * 3)), PATH[#PATH], "past the end")
		local _, _, nextIndex = Staff.along(PATH, total)
		expect.eq(nextIndex, #PATH + 1, "arrived")
	end)

	it("a walker is as far along the path as it has walked", function()
		local total = Staff.length(PATH)
		for _, f in { 0.1, 0.35, 0.5, 0.8 } do
			local pos, _, nextIndex = Staff.along(PATH, total * f)
			-- What remains: to the next point, then the rest of the path.
			local rest = (PATH[nextIndex] - pos).Magnitude
			for i = nextIndex + 1, #PATH do
				rest += (PATH[i] - PATH[i - 1]).Magnitude
			end
			expect.near(rest, total * (1 - f), 0.01, `remaining at {f}`)
		end
	end)

	it("the way back starts where it stands and ends at its post", function()
		local total = Staff.length(PATH)
		for _, f in { 0, 0.2, 0.5, 1 } do
			local back = Staff.backFrom(PATH, total * f)
			close(back[1], (Staff.along(PATH, total * f)), `from where it stands at {f}`)
			close(back[#back], PATH[1], `back at the post from {f}`)
			expect.near(Staff.length(back), total * f, 0.01, `as far back as it came at {f}`)
		end
	end)

	it("a path survives its encoding", function()
		local back = Staff.decode(Staff.encode(PATH))
		expect.eq(#back, #PATH, "points")
		for i, p in PATH do
			close(back[i], p, `point {i}`)
		end
		expect.eq(#Staff.decode(nil), 0, "no path")
		expect.eq(#Staff.decode(""), 0, "an empty path")
	end)

	it(
		"a job is never done before its delay nor before the resident has stood at the door",
		function()
			for _, case in
				{
					{ opened = 0, delay = 12, eff = 1, arrive = 3, atDoor = 2 },
					{ opened = 0, delay = 12, eff = 0.6, arrive = 30, atDoor = 2 },
					{ opened = 5, delay = 20, eff = 1, arrive = 5, atDoor = 0 },
				}
			do
				local due = Staff.due(case.opened, case.delay, case.eff, case.arrive, case.atDoor)
				expect.atLeast(due, case.opened + case.delay / case.eff, "the delay")
				expect.atLeast(due, case.arrive + case.atDoor, "the time at the door")
			end
		end
	)

	it("better staff are never slower", function()
		expect.atMost(Staff.due(0, 12, 1, 3, 2), Staff.due(0, 12, 0.6, 3, 2), "efficiency")
	end)

	it("a Bellhop never slows check-in, and more desk staff never do", function()
		for _, desk in { 0.6, 1, 1.6, 2 } do
			local alone = Staff.deskDelay(6, desk, 0, 0.25)
			expect.atMost(Staff.deskDelay(6, desk, 0.6, 0.25), alone, "a Bellhop at 60 %")
			expect.atMost(
				Staff.deskDelay(6, desk, 1, 0.25),
				Staff.deskDelay(6, desk, 0.6, 0.25),
				"a better Bellhop"
			)
			expect.atMost(Staff.deskDelay(6, desk + 1, 0, 0.25), alone, "more desk staff")
			expect.atLeast(Staff.deskDelay(6, desk, 1, 0.25), 0, "never negative")
		end
	end)

	-- A guest still walking in at the head of the queue never holds up the ones at the desk.
	it("Front Desk serves the first guest waiting at the desk, as check-in does", function()
		local states = { a = "ToHotel", b = "Queued", c = "Queued", d = "ToHotel" }
		local function queued(id: string): boolean
			return states[id] == "Queued"
		end
		expect.eq(Staff.nextAtDesk({ "a", "b", "c" }, queued), "b", "behind one walking in")
		expect.eq(Staff.nextAtDesk({ "c", "b" }, queued), "c", "the first at the desk")
		expect.eq(Staff.nextAtDesk({ "a", "d" }, queued), nil, "nobody at the desk yet")
		expect.eq(Staff.nextAtDesk({}, queued), nil, "an empty queue")
	end)

	-- §8.1: a resident whose camp time runs out while the player plays is on staff again.
	it("a resident is home from the camp once its time has passed, and only then", function()
		local residents = {
			["1"] = { campUntil = 0 }, -- never taken, or rescued
			["2"] = { campUntil = 100 },
		}
		expect.truthy(not Staff.backFromCamp(residents, 90, 99), "still away")
		expect.truthy(Staff.backFromCamp(residents, 99, 100), "its time is up")
		expect.truthy(Staff.backFromCamp(residents, 95, 105), "passed within the check")
		expect.truthy(not Staff.backFromCamp(residents, 100, 110), "already counted home")
		expect.truthy(not Staff.backFromCamp({ ["1"] = { campUntil = 0 } }, 0, 10), "nobody away")
	end)

	it("every errand has its tick at the door, and the Wing has no post", function()
		for role in Staff.Errands do
			expect.truthy(Staff.DoneText[role], `{role}'s text`)
		end
		expect.eq(
			Staff.post("", 1, function()
				return CFrame.new()
			end),
			nil,
			"the Wing"
		)
		expect.truthy(
			Staff.post("RoomService", 1, function()
				return CFrame.new()
			end),
			"a post"
		)
	end)

	--[[ 2026-10-26: Room Service's third post stood past the desk's end, in the
		next cell, at a height taken off the counter's; Bellhop and Security
		stood outside the facade. A hotel turned and lifted off the origin, its
		points where MODELS.md puts them; the areas are where nothing is built. ]]
	it("every post stands on its floor, inside its area, whatever the count", function()
		local Constants = require(Shared.Constants)
		local Grid = require(Shared.Grid)
		local Pieces = require(Shared.Pieces)
		local CELL = Constants.Grid.CellSize
		local piece = assert(Pieces.get("FrontDesk"))
		local halfW, halfD = piece.w * CELL / 2, piece.d * CELL / 2
		local desk = CFrame.new(140, 19, 60) * CFrame.Angles(0, math.pi / 2, 0)
		local entrance = CFrame.new(100, 1, 20) * CFrame.Angles(0, -math.pi / 2, 0)
		local points = {
			FrontDesk = desk,
			Clerk = desk * CFrame.new(0, 0, 1.5),
			Till = desk * CFrame.new(3.4, 3.8, -4.2),
			Queue_4 = desk * CFrame.new(0, 0, -17),
			Entrance = entrance,
		}
		local function point(name: string): CFrame?
			return points[name]
		end
		local mouthHalf = #Grid.entrance() * CELL / 2
		local areas = {
			FrontDesk = { desk, -halfW, halfW, -halfD, halfD },
			RoomService = { desk, -halfW, halfW, -halfD, halfD },
			Housekeeping = { desk, -halfW, halfW, -halfD - CELL, -halfD },
			Bellhop = { entrance, -mouthHalf, mouthHalf, 0, CELL },
			Security = { entrance, -mouthHalf, mouthHalf, 0, CELL },
			Entertainment = { entrance, -mouthHalf, mouthHalf, 0, CELL },
		}
		for role, a in areas do
			local frame: CFrame, x0: number, x1: number, z0: number, z1: number =
				a[1], a[2], a[3], a[4], a[5]
			local seen: { Vector3 } = {}
			for slot = 1, 40 do
				local p = assert(Staff.post(role, slot, point), `{role} {slot}`)
				local l = frame:PointToObjectSpace(p)
				expect.near(l.Y, 0, 0.01, `{role} {slot} on the floor`)
				expect.atLeast(l.X, x0, `{role} {slot} within the area (x)`)
				expect.atMost(l.X, x1, `{role} {slot} within the area (x)`)
				expect.atLeast(l.Z, z0, `{role} {slot} within the area (z)`)
				expect.atMost(l.Z, z1, `{role} {slot} within the area (z)`)
				if slot <= 4 then
					for i, q in seen do
						expect.atLeast((p - q).Magnitude, 2, `{role} {slot} apart from {i}`)
					end
					table.insert(seen, p)
				end
			end
		end
	end)

	-- WAITING §2.48 (his yes 2026-10-26): the staff of a hotel not played are counted in its background rate.
	it(
		"a resident on staff at another hotel is moved only there; the Wing's and the played hotel's anywhere",
		function()
			expect.truthy(Staff.movable({ role = "" }, 2), "in the Wing")
			expect.truthy(
				Staff.movable({ role = "FrontDesk", hotel = 2 }, 2),
				"on staff at the hotel played"
			)
			expect.truthy(
				Staff.movable({ role = "FrontDesk" }, 3),
				"on staff, its hotel the played one's (an old record)"
			)
			expect.truthy(
				not Staff.movable({ role = "Housekeeping", hotel = 1 }, 2),
				"on staff at another hotel"
			)
			expect.truthy(
				Staff.movable({ role = "Housekeeping", hotel = 1 }, 1),
				"once the player is there"
			)
		end
	)
end)
