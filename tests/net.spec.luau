local Net = require(Shared.Net)

local GOOD = { string = "Cash", number = 3, boolean = true }

-- A well-formed message for a remote: one good value per argument.
local function message(def): { any }
	local out = {}
	for i, t in def.args or {} do
		out[i] = if t == "any" then {} else GOOD[t]
	end
	return out
end

describe("Net", function()
	it(
		"every remote has a direction, known argument types, and a client's a positive rate",
		function()
			local known = { string = true, number = true, boolean = true, any = true }
			for name, def in Net.Defs do
				expect.truthy(def.dir == "C2S" or def.dir == "S2C", `{name}'s direction`)
				for i, t in def.args or {} do
					expect.truthy(known[t], `{name}'s argument {i} ({t})`)
				end
				if def.dir == "C2S" then
					expect.truthy(def.rate ~= nil and def.rate > 0, `{name} is rate-limited`)
				end
			end
		end
	)

	-- §13.2: "Assume every piece of data sent from the client has been manipulated."
	it(
		"every client remote takes its own well-formed message, and refuses each argument spoiled",
		function()
			local spoilt = {
				number = { 0 / 0, math.huge, -math.huge, "3", true, {} },
				string = { 7, false, {}, string.rep("x", Net.MaxString + 1) },
				boolean = { 1, "true", {} },
			}
			for name, def in Net.Defs do
				if def.dir == "C2S" then
					local good = message(def)
					expect.truthy(Net._valid(def, good), `{name} with a good message`)
					for i, t in def.args or {} do
						for _, bad in spoilt[t] or {} do
							local m = table.clone(good)
							m[i] = bad
							expect.truthy(
								not Net._valid(def, m),
								`{name}'s argument {i} as {tostring(bad)}`
							)
						end
						local short = table.clone(good)
						short[i] = nil
						if t ~= "any" then
							expect.truthy(not Net._valid(def, short), `{name} without argument {i}`)
						end
					end
					local long = table.clone(good)
					table.insert(long, 1)
					expect.truthy(not Net._valid(def, long), `{name} with an argument too many`)
				end
			end
		end
	)

	it("a string of exactly the longest length passes, and finite extremes pass", function()
		local def = { dir = "C2S", args = { "string", "number", "number" } }
		expect.truthy(
			Net._valid(def, { string.rep("x", Net.MaxString), -1e300, 1e300 }),
			"at the limit"
		)
		expect.truthy(Net._valid(def, { "", -0, 0 }), "empty and zero")
		expect.truthy(not Net._valid(def, { string.rep("x", Net.MaxString + 1), 0, 0 }), "one past")
	end)
end)
