local HotelPoints = require(Shared.HotelPoints)

-- A model with a `Root` part (its PrimaryPart) carrying attachments by name.
local function model(name: string, points: { string }, parent: Instance?): Model
	local m = Instance.new("Model")
	m.Name = name
	local root = Instance.new("Part")
	root.Name = "Root"
	root.Parent = m
	m.PrimaryPart = root
	for _, p in points do
		local a = Instance.new("Attachment")
		a.Name = p
		a.Parent = root
	end
	m.Parent = parent
	return m
end

local function desk(folder: Instance, id: any, kind: string?): Model
	local m = model(`Desk{id}`, { "Desk", "Clerk", "Till", "Queue_1" }, folder)
	m:SetAttribute("Kind", kind or "Desk")
	m:SetAttribute("PieceId", id)
	return m
end

describe("HotelPoints", function()
	it("a hotel's desks are its Desk pieces only, the lowest piece id first, as numbers", function()
		local plot = Instance.new("Model")
		local folder = Instance.new("Folder")
		folder.Name = "Pieces"
		folder.Parent = plot
		local ids = { 10, 9, 100, 2 }
		for _, id in ids do
			desk(folder, id)
		end
		desk(folder, 1, "Stairs") -- not a desk
		desk(folder, "11") -- an id saved as a string still sorts as a number
		local found = HotelPoints.desks(plot)
		expect.eq(#found, #ids + 1, "only desks")
		local last = -math.huge
		for _, m in found do
			local id = tonumber(m:GetAttribute("PieceId")) :: number
			expect.truthy(id > last, `{id} after {last}`)
			last = id
		end
		expect.eq(#HotelPoints.desks(Instance.new("Model")), 0, "a plot with no pieces")
	end)

	it(
		"each point is read from its own model: the facade's entrance, the forecourt, the first desk",
		function()
			local plot = Instance.new("Model")
			local facade = Instance.new("Folder")
			facade.Name = "Facade"
			facade.Parent = plot
			model("Facade_Entrance", { "Entrance", "Desk" }, facade)
			local base = Instance.new("Folder")
			base.Name = "Base"
			base.Parent = plot
			model("Forecourt", { "PathFoot", "Spawn" }, base)
			local folder = Instance.new("Folder")
			folder.Name = "Pieces"
			folder.Parent = plot
			local second = desk(folder, 8)
			local first = desk(folder, 3)

			local e = HotelPoints.attachment(plot, "Entrance")
			expect.truthy(
				e and e.Parent and e.Parent.Parent and e.Parent.Parent.Name == "Facade_Entrance",
				"Entrance on the facade"
			)
			local s = HotelPoints.attachment(plot, "Spawn")
			expect.truthy(s and s.Name == "PathFoot", "Spawn is the forecourt's PathFoot")
			for _, name in { "Desk", "Clerk", "Till", "Queue_1" } do
				local a = HotelPoints.attachment(plot, name)
				expect.truthy(
					a and a.Parent and a.Parent.Parent == first,
					`{name} on the first desk`
				)
				expect.truthy(a.Parent.Parent ~= second, `{name} not on another desk`)
			end
		end
	)

	it("a point whose model or attachment is missing is nil, never an error", function()
		local plot = Instance.new("Model")
		for _, name in { "Entrance", "Spawn", "Desk", "Queue_4", "NoSuchPoint" } do
			expect.eq(HotelPoints.attachment(plot, name), nil, name)
			expect.eq(HotelPoints.find(plot, name), nil, `{name} found`)
		end
		expect.eq(HotelPoints.find(plot, "FrontDesk"), nil, "no desk, no FrontDesk")
		local folder = Instance.new("Folder")
		folder.Name = "Pieces"
		folder.Parent = plot
		desk(folder, 1)
		expect.eq(HotelPoints.attachment(plot, "Queue_4"), nil, "an attachment the desk lacks")
	end)
end)
