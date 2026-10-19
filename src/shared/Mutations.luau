--!strict
--[[
	Mutations (GDD §4.5): rolled on arrival, free randomness from play, and no
	purchase can change the odds. A mutation is a material, colour and size
	variant on the species' own rig, so `look` is all the art it needs.

	Seasonal mutations are event-only (`event = true`): never rolled by
	`Mutations.roll`, only granted by an event (§8.2).
]]

export type Mutation = {
	id: string,
	name: string,
	chance: number,
	pay: number,
	scale: number,
	material: Enum.Material?,
	colour: Color3?,
	event: boolean?,
}

local Mutations = {}

local rows: { Mutation } = {
	{ id = "Tiny", name = "Tiny", chance = 0.05, pay = 1.5, scale = 0.5 },
	{ id = "Giant", name = "Giant", chance = 0.04, pay = 2, scale = 1.5 },
	{
		id = "Shadow",
		name = "Shadow",
		chance = 0.02,
		pay = 3,
		scale = 1,
		colour = Color3.fromRGB(25, 20, 35),
	},
	{
		id = "Golden",
		name = "Golden",
		chance = 0.01,
		pay = 5,
		scale = 1,
		material = Enum.Material.Foil,
		colour = Color3.fromRGB(255, 200, 60),
	},
	{
		id = "Glitched",
		name = "Glitched",
		chance = 0.002,
		pay = 10,
		scale = 1,
		material = Enum.Material.Neon,
		colour = Color3.fromRGB(255, 60, 220),
	},
	{
		id = "Pumpkin",
		name = "Pumpkin",
		chance = 0,
		pay = 4,
		scale = 1,
		colour = Color3.fromRGB(240, 130, 30),
		event = true,
	},
	{
		id = "Frosted",
		name = "Frosted",
		chance = 0,
		pay = 4,
		scale = 1,
		material = Enum.Material.Ice,
		colour = Color3.fromRGB(200, 235, 255),
		event = true,
	},
}

Mutations.List = rows
Mutations.ById = {} :: { [string]: Mutation }
for _, row in rows do
	Mutations.ById[row.id] = row
end

-- The mutations a Book page lists and a "mutation set" means (§4.6): every
-- one that can be rolled, not the event ones.
Mutations.Rollable = {} :: { Mutation }
for _, row in rows do
	if not row.event then
		table.insert(Mutations.Rollable, row)
	end
end

--[[ One roll on arrival: `r` is a uniform number in [0, 1). The chances are
	independent slices of one draw, so the odds are exactly the table's, and
	what is left over is no mutation (nil). ]]
function Mutations.roll(r: number): string?
	local at = 0
	for _, row in Mutations.Rollable do
		at += row.chance
		if r < at then
			return row.id
		end
	end
	return nil
end

function Mutations.payMultiplier(id: string?): number
	local row = if id then Mutations.ById[id] else nil
	return if row then row.pay else 1
end

return Mutations
