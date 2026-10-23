-- The VIP lounge set (GDD A.2, §10.2): a pass's decor, placed at any location by whoever owns
-- the pass, and only by them. Rules only: the picks and costs are PLACEHOLDER.
local Constants = require(Shared.Constants)
local Pieces = require(Shared.Pieces)
local Store = require(Shared.Store)

describe("The VIP lounge set (A.2)", function()
	local set = {}
	for _, d in Pieces.DecorList do
		if d.pass then
			table.insert(set, d)
		end
	end

	it(
		"the VIP Lobby pass has a set of decor, every piece naming a pass the store sells",
		function()
			local keys = {}
			for _, e in Store.Entries do
				if e.kind == "Pass" then
					keys[e.key] = true
				end
			end
			local vip = 0
			for _, d in set do
				expect.truthy(
					keys[d.pass :: string] == true,
					`{d.id}'s pass {d.pass} is a store pass`
				)
				if d.pass == "VIPLobby" then
					vip += 1
				end
			end
			expect.truthy(vip >= 3, "the VIP Lobby pass grants a set")
		end
	)

	it("a pass's decor is of every location, decor and not furniture, and never found", function()
		for _, d in set do
			expect.eq(d.location, 0, `{d.id}'s location`)
			expect.truthy(not d.furniture and not d.found and not d.always, `{d.id} is plain decor`)
		end
	end)

	it("only the pass's owner may place it, at every location", function()
		for _, d in set do
			for loc = 1, Constants.Chain.Locations do
				expect.truthy(
					not Pieces.decorHere(d, loc, {}, {}),
					`{d.id} at {loc} without the pass`
				)
				expect.truthy(
					not Pieces.decorHere(d, loc, {}, {}, { [`not{d.pass}`] = true }),
					`{d.id} at {loc} with another pass`
				)
				expect.truthy(
					not Pieces.decorHere(d, loc, { [`Decor_{d.id}`] = true }, {}),
					`{d.id} at {loc} unlocked but no pass`
				)
				expect.truthy(
					Pieces.decorHere(d, loc, {}, {}, { [d.pass :: string] = true }),
					`{d.id} at {loc} with the pass`
				)
			end
		end
	end)

	it("a pass's decor gives decor points, as bought decor does", function()
		for _, d in set do
			expect.truthy(d.cost > 0, `{d.id} has a cost (its decor points)`)
		end
	end)
end)
