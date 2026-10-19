--!strict
--[[
	The long road (GDD §6.6): each location is a family of species, a facade
	and a set of rooms. Rebirth moves a hotel to the next one (§6.4).

	`rebirthResident` is the named monster §6.4 asks for ("a Vampire Count
	resident"); Location 2's is a night draft (Appendix A.6). Locations 3–5 are
	listed for the street's facades and the preview, with no family built yet
	(`playable = false`).
]]

export type Location = {
	id: number,
	name: string,
	family: string,
	rebirthResident: string?,
	playable: boolean,
	ground: Color3,
	facade: Color3,
	trim: Color3,
}

local Locations = {}

local rows: { Location } = {
	{
		id = 1,
		name = "Haunted Manor",
		family = "Classic spooks",
		rebirthResident = "VampireCount",
		playable = true,
		ground = Color3.fromRGB(60, 50, 70),
		facade = Color3.fromRGB(90, 70, 110),
		trim = Color3.fromRGB(240, 150, 60),
	},
	{
		id = 2,
		name = "Frostfang Lodge",
		family = "Ice and snow",
		rebirthResident = "IceWyrm",
		playable = true,
		ground = Color3.fromRGB(200, 215, 230),
		facade = Color3.fromRGB(120, 160, 200),
		trim = Color3.fromRGB(240, 250, 255),
	},
	{
		id = 3,
		name = "Bayou Spa",
		family = "Swamp",
		playable = false,
		ground = Color3.fromRGB(60, 80, 50),
		facade = Color3.fromRGB(80, 110, 70),
		trim = Color3.fromRGB(200, 230, 120),
	},
	{
		id = 4,
		name = "Volcano Resort",
		family = "Fire",
		playable = false,
		ground = Color3.fromRGB(60, 40, 35),
		facade = Color3.fromRGB(130, 60, 40),
		trim = Color3.fromRGB(255, 140, 40),
	},
	{
		id = 5,
		name = "Sky Castle",
		family = "Sky and storm",
		playable = false,
		ground = Color3.fromRGB(200, 210, 230),
		facade = Color3.fromRGB(150, 160, 210),
		trim = Color3.fromRGB(255, 230, 120),
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
