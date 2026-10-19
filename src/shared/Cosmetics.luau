--!strict
--[[
	What a player can wear on their hotel (GDD §8.2 event shops, §10.2 facade
	packs, the login calendar's day 7, a completed family): one row each, the
	slot it goes in, and where it comes from. A player owns cosmetics in their
	profile's `cosmetics` and wears one per slot (`equipped`); the build
	mode's **Style** tool picks them. Cosmetic only: nothing here changes a
	number in the game (§10.1 "never sell winning").

	How each slot is drawn is MODELS.md, "Cosmetics". Every row is a night
	draft (GDD Appendix A.10), its name and look his to change.
]]

export type Slot = "Sign" | "Lobby" | "Facade"
export type Cosmetic = {
	id: string,
	name: string,
	slot: Slot,
	from: string, -- where it is earned, for the Style list
	colour: Color3, -- the blockout's colour (the facade's, for a facade cosmetic)
	trim: Color3?, -- a facade cosmetic's trim
}

local Cosmetics = {}

Cosmetics.Slots = { "Sign", "Lobby", "Facade" } :: { Slot }

Cosmetics.List = {
	{
		id = "Cosmetic_PumpkinSign",
		name = "Pumpkin sign",
		slot = "Sign",
		from = "Halloween's Candy shop",
		colour = Color3.fromRGB(245, 140, 30),
	},
	{
		id = "Cosmetic_IcicleSign",
		name = "Icicle sign",
		slot = "Sign",
		from = "the Winter shop",
		colour = Color3.fromRGB(200, 235, 255),
	},
	{
		id = "Cosmetic_LanternSign",
		name = "Lantern sign",
		slot = "Sign",
		from = "day 7 of the login calendar",
		colour = Color3.fromRGB(255, 200, 110),
	},
	{
		id = "Cosmetic_Family1",
		name = "Haunted Manor crest",
		slot = "Sign",
		from = "completing the Haunted Manor family",
		colour = Color3.fromRGB(150, 90, 200),
	},
	{
		id = "Cosmetic_Family2",
		name = "Frostfang crest",
		slot = "Sign",
		from = "completing the Frostfang family",
		colour = Color3.fromRGB(170, 220, 255),
	},
	{
		id = "Cosmetic_BatBunting",
		name = "Bat bunting",
		slot = "Lobby",
		from = "Halloween's Candy shop",
		colour = Color3.fromRGB(40, 30, 50),
	},
	{
		id = "Cosmetic_FairyLights",
		name = "Fairy lights",
		slot = "Lobby",
		from = "the Winter shop",
		colour = Color3.fromRGB(255, 230, 150),
	},
	{
		id = "Cosmetic_SlimeFacade",
		name = "Slime facade",
		slot = "Facade",
		from = "the Starter Pack",
		colour = Color3.fromRGB(90, 170, 100),
		trim = Color3.fromRGB(190, 255, 150),
	},
} :: { Cosmetic }

Cosmetics.ById = {} :: { [string]: Cosmetic }
for _, c in Cosmetics.List do
	Cosmetics.ById[c.id] = c
end

function Cosmetics.get(id: string): Cosmetic?
	return Cosmetics.ById[id]
end

-- A completed family's cosmetic (BookService), by location id.
function Cosmetics.family(location: number): string
	return `Cosmetic_Family{location}`
end

return Cosmetics
