--!strict
--[[
	The long road (GDD §6.6): each location is a family of species, a facade
	and a set of rooms, and a hotel of the player's chain (§6.4). Haunted
	Manor, Frostfang Lodge and Bayou Spa are the launch chain (his ruling,
	2026-10-20); Bayou Spa's family is a draft for his picks (WAITING §2.36).
	Locations 4–5 are listed for the preview, with no family built yet
	(`playable = false`).
]]

export type Location = {
	id: number,
	name: string,
	family: string,
	playable: boolean,
	ground: Color3,
	facade: Color3,
	trim: Color3,
	-- One world (GDD §3, §6.4): the ground round its street and the forest's floor, blended into the
	-- next street's along the road between them, and the colour of its street lamps. Haunted Manor's are
	-- Creepy Lane's as they always were; the others PLACEHOLDER.
	world: Color3,
	worldMaterial: Enum.Material,
	lamp: Color3,
}

local Locations = {}

local rows: { Location } = {
	{
		id = 1,
		name = "Haunted Manor",
		family = "Classic spooks",
		playable = true,
		ground = Color3.fromRGB(60, 50, 70),
		facade = Color3.fromRGB(90, 70, 110),
		trim = Color3.fromRGB(240, 150, 60),
		world = Color3.fromRGB(45, 55, 50),
		worldMaterial = Enum.Material.Grass,
		lamp = Color3.fromRGB(255, 190, 120),
	},
	{
		id = 2,
		name = "Frostfang Lodge",
		family = "Ice and snow",
		playable = true,
		ground = Color3.fromRGB(200, 215, 230),
		facade = Color3.fromRGB(120, 160, 200),
		trim = Color3.fromRGB(240, 250, 255),
		world = Color3.fromRGB(150, 165, 190),
		worldMaterial = Enum.Material.Snow,
		lamp = Color3.fromRGB(185, 215, 255),
	},
	{
		id = 3,
		name = "Bayou Spa",
		family = "Swamp",
		playable = true,
		ground = Color3.fromRGB(60, 80, 50),
		facade = Color3.fromRGB(80, 110, 70),
		trim = Color3.fromRGB(200, 230, 120),
		world = Color3.fromRGB(42, 58, 40),
		worldMaterial = Enum.Material.Mud,
		lamp = Color3.fromRGB(200, 235, 130),
	},
	{
		id = 4,
		name = "Volcano Resort",
		family = "Fire",
		playable = false,
		ground = Color3.fromRGB(60, 40, 35),
		facade = Color3.fromRGB(130, 60, 40),
		trim = Color3.fromRGB(255, 140, 40),
		world = Color3.fromRGB(50, 35, 32),
		worldMaterial = Enum.Material.Basalt,
		lamp = Color3.fromRGB(255, 150, 70),
	},
	{
		id = 5,
		name = "Sky Castle",
		family = "Sky and storm",
		playable = false,
		ground = Color3.fromRGB(200, 210, 230),
		facade = Color3.fromRGB(150, 160, 210),
		trim = Color3.fromRGB(255, 230, 120),
		world = Color3.fromRGB(150, 160, 185),
		worldMaterial = Enum.Material.Grass,
		lamp = Color3.fromRGB(255, 230, 150),
	},
}

Locations.List = rows

function Locations.get(id: number): Location
	return rows[id] or rows[1]
end

-- The furthest location a hotel can move to: the last playable one.
function Locations.last(): number
	local last = 1
	for _, row in rows do
		if row.playable then
			last = row.id
		end
	end
	return last
end

return Locations
