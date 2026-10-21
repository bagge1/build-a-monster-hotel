--!strict
--[[
	Mutations (GDD §4.5, A.11.5): rolled on arrival, free randomness from play,
	and no purchase can change the odds. A mutation is a material, colour and
	size variant on the species' own rig, so `look` is all the art it needs.

	TWO GROUPS THAT STACK (A.11.5 decision 1a): a SIZE (Tiny, Giant) and a
	LOOK (Shadow, Golden, Glitched, the season's, the month's), rolled
	independently, so a guest can be a Giant Golden Slime. A guest and a
	resident keep them in two fields, `size` and `mutation` (the look, as
	before), so every `mutation == "Golden"` keeps meaning the look. Their pay
	is ADDED (decision 2b): Giant ×2 and Golden ×5 pay ×6, not ×10.

	Seasonal and monthly mutations are event rows (`event = true`): never in
	the plain roll, only a row of the look table in their season or month
	(`Events.rollMutation`). The month's are `Constants.Mutations.Monthly`.
]]

local Constants = require(script.Parent.Constants)

export type Group = "Size" | "Look"
export type Mutation = {
	id: string,
	name: string,
	group: Group,
	chance: number,
	pay: number,
	scale: number,
	material: Enum.Material?,
	colour: Color3?,
	event: boolean?,
	month: number?, -- a mutation of the month (A.11.5): the month it is rolled in
}

local Mutations = {}

local M = Constants.Mutations

local rows: { Mutation } = {
	{ id = "Tiny", name = "Tiny", group = "Size", chance = 0.05, pay = 1.5, scale = 0.5 },
	{ id = "Giant", name = "Giant", group = "Size", chance = 0.04, pay = 2, scale = 1.5 },
	{
		id = "Shadow",
		name = "Shadow",
		group = "Look",
		chance = 0.02,
		pay = 3,
		scale = 1,
		colour = Color3.fromRGB(25, 20, 35),
	},
	{
		id = "Golden",
		name = "Golden",
		group = "Look",
		chance = 0.01,
		pay = 5,
		scale = 1,
		material = Enum.Material.Foil,
		colour = Color3.fromRGB(255, 200, 60),
	},
	{
		id = "Glitched",
		name = "Glitched",
		group = "Look",
		chance = 0.002,
		pay = 10,
		scale = 1,
		material = Enum.Material.Neon,
		colour = Color3.fromRGB(255, 60, 220),
	},
	{
		id = "Pumpkin",
		name = "Pumpkin",
		group = "Look",
		chance = 0,
		pay = 4,
		scale = 1,
		colour = Color3.fromRGB(240, 130, 30),
		event = true,
	},
	{
		id = "Frosted",
		name = "Frosted",
		group = "Look",
		chance = 0,
		pay = 4,
		scale = 1,
		material = Enum.Material.Ice,
		colour = Color3.fromRGB(200, 235, 255),
		event = true,
	},
	-- The mutations of the month (A.11.5, night drafts: names and looks his to change).
	{
		id = "Mossy",
		name = "Mossy",
		group = "Look",
		chance = 0,
		pay = M.MonthlyPay,
		scale = 1,
		material = Enum.Material.Grass,
		colour = Color3.fromRGB(95, 150, 70),
		event = true,
	},
	{
		id = "Rainbow",
		name = "Rainbow",
		group = "Look",
		chance = 0,
		pay = M.MonthlyPay,
		scale = 1,
		material = Enum.Material.Glass,
		colour = Color3.fromRGB(150, 220, 255),
		event = true,
	},
	{
		id = "Sunburnt",
		name = "Sunburnt",
		group = "Look",
		chance = 0,
		pay = M.MonthlyPay,
		scale = 1,
		colour = Color3.fromRGB(225, 95, 70),
		event = true,
	},
	{
		id = "Moonlit",
		name = "Moonlit",
		group = "Look",
		chance = 0,
		pay = M.MonthlyPay,
		scale = 1,
		material = Enum.Material.Neon,
		colour = Color3.fromRGB(150, 170, 255),
		event = true,
	},
}
for month, id in M.Monthly do
	for _, row in rows do
		if row.id == id then
			row.month = month
		end
	end
end

Mutations.List = rows
Mutations.ById = {} :: { [string]: Mutation }
for _, row in rows do
	Mutations.ById[row.id] = row
end

-- The mutations a Book page lists and a "mutation set" means (§4.6): every
-- one that can be rolled, not the event ones.
Mutations.Rollable = {} :: { Mutation }
-- The season's and the month's (a Book page's Seasons row, A.11.5): no mutation-set title.
Mutations.Seasonal = {} :: { Mutation }
for _, row in rows do
	table.insert(if row.event then Mutations.Seasonal else Mutations.Rollable, row)
end

-- Whether `id` is a size (Tiny, Giant) rather than a look.
function Mutations.isSize(id: string?): boolean
	local row = if id then Mutations.ById[id] else nil
	return row ~= nil and row.group == "Size"
end

--[[ One roll of a group's plain rows: `r` uniform in [0, 1). The chances
	are independent slices of one draw, so the odds are exactly the table's,
	and what is left over is none (nil). ]]
local function rollGroup(group: Group, r: number): string?
	local at = 0
	for _, row in Mutations.Rollable do
		if row.group == group then
			at += row.chance
			if r < at then
				return row.id
			end
		end
	end
	return nil
end

function Mutations.rollSize(r: number): string?
	return rollGroup("Size", r)
end

--[[ The look roll. `extra` is a row of its season or month with its chance,
	taken first, the rest of the draw scaled over the plain looks, so every
	look can still come in every month (A.11.5 scrutiny). ]]
function Mutations.rollLook(r: number, extra: { id: string, chance: number }?): string?
	if extra and extra.chance > 0 then
		if r < extra.chance then
			return extra.id
		end
		r = (r - extra.chance) / (1 - extra.chance)
	end
	return rollGroup("Look", r)
end

--[[ The pay multiplier of a size and a look, ADDED (A.11.5 decision 2b):
	each one's extra over ×1 summed, so Giant (×2) and Golden (×5) pay ×6.
	Either may be nil. ]]
function Mutations.payMultiplier(size: string?, look: string?): number
	local s = if size then Mutations.ById[size] else nil
	local l = if look then Mutations.ById[look] else nil
	return 1 + (if s then s.pay - 1 else 0) + (if l then l.pay - 1 else 0)
end

-- A size and a look as words before a species' name ("Giant Golden "), or "".
function Mutations.prefix(size: string?, look: string?): string
	local out = ""
	for _, id in { size, look } do
		local row = Mutations.ById[id :: string]
		if row then
			out ..= row.name .. " "
		end
	end
	return out
end

-- The scale a size gives (1 without one).
function Mutations.scale(size: string?): number
	local row = if size then Mutations.ById[size] else nil
	return if row then row.scale else 1
end

return Mutations
