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
end)
