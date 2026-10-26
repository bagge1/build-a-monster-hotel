local Walk = require(Shared.Walk)

local PATH = {
	Vector3.new(0, 0, 0),
	Vector3.new(12, 0, 0),
	Vector3.new(12, 0, 0), -- a point repeated: a wait without moving
	Vector3.new(12, 18, 9),
	Vector3.new(-6.5, 18, 9),
}
local WAITS = { [1] = 1.5, [3] = 2, [5] = 0.75 }
local SPEED = 8

describe("Walk", function()
	it("a path and its waits survive their encoding", function()
		local path, waits = Walk.decode(Walk.encode(PATH, WAITS))
		expect.eq(#path, #PATH, "points")
		for i, p in PATH do
			expect.atMost((path[i] - p).Magnitude, 0.1, `point {i}`)
			expect.near(waits[i] or 0, WAITS[i] or 0, 0.01, `wait at {i}`)
		end
		local none, noWaits = Walk.decode(Walk.encode(PATH))
		expect.eq(#none, #PATH, "points without waits")
		expect.eq(next(noWaits), nil, "no waits")
		for _, s in { nil, "" } do
			local empty, w = Walk.decode(s)
			expect.eq(#empty, 0, "no path")
			expect.eq(next(w), nil, "no waits on no path")
		end
	end)

	it("a walk lasts its length at its speed plus its waits", function()
		local length = 0
		for i = 2, #PATH do
			length += (PATH[i] - PATH[i - 1]).Magnitude
		end
		local waited = 0
		for _, w in WAITS do
			waited += w
		end
		expect.near(Walk.duration(PATH, WAITS, SPEED), length / SPEED + waited, 1e-6)
		expect.near(Walk.duration(PATH, nil, SPEED), length / SPEED, 1e-6, "without waits")
		expect.eq(Walk.duration({ PATH[1] }, nil, SPEED), 0, "one point")
	end)

	it(
		"a walker starts at the first point, ends at the last, and stands still past the end",
		function()
			local total = Walk.duration(PATH, WAITS, SPEED)
			for _, t in { -5, 0 } do
				local pos, _, walking = Walk.sample(PATH, WAITS, SPEED, t)
				expect.atMost((pos - PATH[1]).Magnitude, 1e-6, `at the start ({t})`)
				expect.truthy(not walking, `waiting at the start ({t})`)
			end
			for _, t in { total, total + 0.01, total * 4 } do
				local pos, _, walking = Walk.sample(PATH, WAITS, SPEED, t)
				expect.atMost((pos - PATH[#PATH]).Magnitude, 1e-6, `at the end ({t})`)
				expect.truthy(not walking, `standing at the end ({t})`)
			end
			local pos, _, walking = Walk.sample({}, nil, SPEED, 3)
			expect.eq(pos, Vector3.zero, "no path stands at the origin")
			expect.truthy(not walking, "and does not walk")
		end
	)

	it(
		"a walker never moves faster than its speed, nor while it waits, and faces a unit way",
		function()
			local total = Walk.duration(PATH, WAITS, SPEED)
			local dt = 0.05
			local last = Walk.sample(PATH, WAITS, SPEED, 0)
			local t = dt
			while t <= total + dt do
				local pos, forward, walking = Walk.sample(PATH, WAITS, SPEED, t)
				local moved = (pos - last).Magnitude
				expect.atMost(moved, SPEED * dt * (1 + 1e-4), `speed at {t}`)
				expect.near(forward.Magnitude, 1, 1e-4, `facing at {t}`)
				if not walking then
					-- Standing: the same place a moment later, unless a walk resumes in between.
					local later, _, walkingLater = Walk.sample(PATH, WAITS, SPEED, t + 1e-3)
					if not walkingLater then
						expect.atMost((later - pos).Magnitude, 1e-4, `still while waiting at {t}`)
					end
				end
				last = pos
				t += dt
			end
		end
	)
end)
