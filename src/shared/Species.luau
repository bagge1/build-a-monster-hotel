--!strict
--[[
	Every species, one row each (GDD §4.1, §6.7, Appendix A.6). Adding a
	monster is a row here plus its art (§13.2, "data-driven content"): nothing
	else in the code names a species, except the tutorial (§11) and the rebirth
	goal (§6.4), which name theirs in `Locations`.

	`room` is a `Rooms` id. `prefs` are preference tags (`Pieces` gives them).
	`look` is what the Luau blockout draws until a model exists (MODELS.md,
	"Monsters"): a colour, a height in studs against the 5-stud person
	(CLAUDE.md), and a body shape. Frostfang Lodge's rows are night drafts
	(Appendix A.6), every one his to change.
]]

local Constants = require(script.Parent.Constants)

export type Shape = "Blob" | "Biped" | "Float" | "Quadruped" | "Serpent"
export type Look = { colour: Color3, height: number, shape: Shape, eyes: Color3? }
export type Species = {
	id: string,
	name: string,
	location: number,
	rarity: Constants.RarityId,
	room: string,
	prefs: { string },
	staff: string,
	quirk: string,
	request: string,
	look: Look,
}

local Species = {}

local rows: { Species } = {
	-- Location 1, Haunted Manor (§6.7)
	{
		id = "Slime",
		name = "Slime",
		location = 1,
		rarity = "Common",
		room = "StandardRoom",
		prefs = { "damp", "snacks" },
		staff = "RoomService",
		quirk = "Wobbles; leaves cute goo footprints",
		request = "More snacks, please!",
		look = { colour = Color3.fromRGB(110, 220, 120), height = 3, shape = "Blob" },
	},
	{
		id = "Skeleton",
		name = "Skeleton",
		location = 1,
		rarity = "Common",
		room = "StandardRoom",
		prefs = { "music", "quiet" },
		staff = "FrontDesk",
		quirk = "Rattles; tips with a bone",
		request = "Could you play a little tune?",
		look = { colour = Color3.fromRGB(235, 230, 215), height = 5, shape = "Biped" },
	},
	{
		id = "PumpkinHead",
		name = "Pumpkin Head",
		location = 1,
		rarity = "Common",
		room = "GardenRoom",
		prefs = { "candles", "garden" },
		staff = "Entertainment",
		quirk = "Head glows brighter when happy",
		request = "My candle went out!",
		look = { colour = Color3.fromRGB(240, 140, 40), height = 4.5, shape = "Biped" },
	},
	{
		id = "Ghost",
		name = "Ghost",
		location = 1,
		rarity = "Uncommon",
		room = "AtticRoom",
		prefs = { "quiet", "antique furniture" },
		staff = "Housekeeping",
		quirk = "Floats through walls",
		request = "Shh... is it quiet up here?",
		look = { colour = Color3.fromRGB(220, 235, 255), height = 4.5, shape = "Float" },
	},
	{
		id = "Mummy",
		name = "Mummy",
		location = 1,
		rarity = "Uncommon",
		room = "SarcophagusSuite",
		prefs = { "dry", "dark" },
		staff = "Bellhop",
		quirk = "Trails bandages",
		request = "Fresh bandages, please.",
		look = { colour = Color3.fromRGB(215, 200, 160), height = 5.5, shape = "Biped" },
	},
	{
		id = "Zombie",
		name = "Zombie",
		location = 1,
		rarity = "Rare",
		room = "StandardRoom",
		prefs = { "snacks", "slow music" },
		staff = "RoomService",
		quirk = "Very slow; very loyal",
		request = "Snaaack...",
		look = { colour = Color3.fromRGB(120, 170, 110), height = 5.5, shape = "Biped" },
	},
	{
		id = "Witch",
		name = "Witch",
		location = 1,
		rarity = "Rare",
		room = "PotionLoft",
		prefs = { "cats", "cauldron" },
		staff = "Entertainment",
		quirk = "Brews colourful smoke",
		request = "My cauldron needs a stir!",
		look = { colour = Color3.fromRGB(150, 90, 200), height = 5.5, shape = "Biped" },
	},
	{
		id = "Werewolf",
		name = "Werewolf",
		location = 1,
		rarity = "Epic",
		room = "DenRoom",
		prefs = { "moonlight", "steak" },
		staff = "Security",
		quirk = "Howls at check-in",
		request = "Steak. Rare. Now. Please.",
		look = { colour = Color3.fromRGB(120, 95, 75), height = 6.5, shape = "Biped" },
	},
	{
		id = "VampireCount",
		name = "Vampire Count",
		location = 1,
		rarity = "Legendary",
		room = "CoffinSuite",
		prefs = { "darkness", "organ music" },
		staff = "FrontDesk",
		quirk = "Bows with a cape swirl; turns into bats",
		request = "Draw the curtains, would you?",
		look = {
			colour = Color3.fromRGB(60, 40, 80),
			height = 6,
			shape = "Biped",
			eyes = Color3.fromRGB(255, 60, 60),
		},
	},
	{
		id = "GrandBanshee",
		name = "Grand Banshee",
		location = 1,
		rarity = "Mythic",
		room = "OperaSuite",
		prefs = { "silence", "chandelier" },
		staff = "Entertainment",
		quirk = "Her song shakes the whole street",
		request = "Polish the chandelier, darling.",
		look = { colour = Color3.fromRGB(150, 220, 230), height = 7, shape = "Float" },
	},

	-- Location 2, Frostfang Lodge (night draft, Appendix A.6)
	{
		id = "SnowballSprite",
		name = "Snowball Sprite",
		location = 2,
		rarity = "Common",
		room = "IglooRoom",
		prefs = { "cold", "cocoa" },
		staff = "RoomService",
		quirk = "Rolls instead of walking",
		request = "Is there more cocoa?",
		look = { colour = Color3.fromRGB(245, 250, 255), height = 3, shape = "Blob" },
	},
	{
		id = "IceImp",
		name = "Ice Imp",
		location = 2,
		rarity = "Common",
		room = "IglooRoom",
		prefs = { "cold", "mischief" },
		staff = "Bellhop",
		quirk = "Leaves frost handprints",
		request = "I'm bored! Got a prank?",
		look = { colour = Color3.fromRGB(120, 200, 255), height = 3.5, shape = "Biped" },
	},
	{
		id = "FrostTroll",
		name = "Frost Troll",
		location = 2,
		rarity = "Uncommon",
		room = "IceCave",
		prefs = { "cold", "stone" },
		staff = "Security",
		quirk = "Sleeps standing up",
		request = "Bed too soft. Rocks?",
		look = { colour = Color3.fromRGB(140, 170, 190), height = 7, shape = "Biped" },
	},
	{
		id = "Yeti",
		name = "Yeti",
		location = 2,
		rarity = "Rare",
		room = "YetiDen",
		prefs = { "snow", "quiet" },
		staff = "Housekeeping",
		quirk = "Shakes off snow at check-in",
		request = "Fresh snow for the floor?",
		look = { colour = Color3.fromRGB(235, 240, 245), height = 7.5, shape = "Biped" },
	},
	{
		id = "SnowWitch",
		name = "Snow Witch",
		location = 2,
		rarity = "Epic",
		room = "FrostLoft",
		prefs = { "cocoa", "northern lights" },
		staff = "Entertainment",
		quirk = "Knits icicles",
		request = "The lights, dear. Turn them on.",
		look = { colour = Color3.fromRGB(170, 210, 255), height = 5.5, shape = "Biped" },
	},
	{
		id = "IceWyrm",
		name = "Ice Wyrm",
		location = 2,
		rarity = "Legendary",
		room = "GlacierSuite",
		prefs = { "cold", "northern lights" },
		staff = "FrontDesk",
		quirk = "Coils around the desk",
		request = "Colder. Much colder.",
		look = { colour = Color3.fromRGB(90, 170, 230), height = 6, shape = "Serpent" },
	},
	{
		id = "AuroraSpirit",
		name = "Aurora Spirit",
		location = 2,
		rarity = "Mythic",
		room = "AuroraDome",
		prefs = { "northern lights", "silence" },
		staff = "Entertainment",
		quirk = "Paints the sky green",
		request = "Hush... watch the sky with me.",
		look = { colour = Color3.fromRGB(110, 255, 190), height = 7, shape = "Float" },
	},
	-- Location 3, Bayou Spa: a draft for his picks (WAITING §2.36), every value PLACEHOLDER
	{
		id = "BogFrog",
		name = "Bog Frog",
		location = 3,
		rarity = "Common",
		room = "LilyPadRoom",
		prefs = { "steam", "jazz" },
		staff = "Entertainment",
		quirk = "Croaks a chord at check-in",
		request = "Is the band playing tonight?",
		look = { colour = Color3.fromRGB(90, 160, 70), height = 3, shape = "Blob" },
	},
	{
		id = "Mossling",
		name = "Mossling",
		location = 3,
		rarity = "Common",
		room = "LilyPadRoom",
		prefs = { "moss", "quiet" },
		staff = "Housekeeping",
		quirk = "Little sprouts grow where it sits",
		request = "Somewhere soft and green, please.",
		look = { colour = Color3.fromRGB(120, 170, 90), height = 3, shape = "Blob" },
	},
	{
		id = "FireflySprite",
		name = "Firefly Sprite",
		location = 3,
		rarity = "Common",
		room = "WillowNook",
		prefs = { "fireflies", "herbs" },
		staff = "RoomService",
		quirk = "Lights up the hallway as it goes",
		request = "More little lights!",
		look = { colour = Color3.fromRGB(250, 230, 110), height = 3, shape = "Float" },
	},
	{
		id = "MudPuppy",
		name = "Mud Puppy",
		location = 3,
		rarity = "Uncommon",
		room = "MudBath",
		prefs = { "mud", "steam" },
		staff = "Bellhop",
		quirk = "Shakes mud on the doorman",
		request = "Got any good mud?",
		look = { colour = Color3.fromRGB(130, 95, 60), height = 3, shape = "Quadruped" },
	},
	{
		id = "GatorGhoul",
		name = "Gator Ghoul",
		location = 3,
		rarity = "Uncommon",
		room = "MudBath",
		prefs = { "mud", "jazz" },
		staff = "Security",
		quirk = "Grins with far too many teeth",
		request = "Play something slow and swampy.",
		look = { colour = Color3.fromRGB(80, 120, 80), height = 5, shape = "Biped" },
	},
	{
		id = "WillOWisp",
		name = "Will-o'-Wisp",
		location = 3,
		rarity = "Rare",
		room = "WillowNook",
		prefs = { "fireflies", "quiet" },
		staff = "FrontDesk",
		quirk = "Goes out when it gets shy",
		request = "Dim the lights a little?",
		look = { colour = Color3.fromRGB(150, 230, 255), height = 4, shape = "Float" },
	},
	{
		id = "SwampHag",
		name = "Swamp Hag",
		location = 3,
		rarity = "Rare",
		room = "HerbLoft",
		prefs = { "herbs", "steam" },
		staff = "Entertainment",
		quirk = "Brews a fog that smells of mint",
		request = "I need fresh herbs.",
		look = { colour = Color3.fromRGB(110, 140, 100), height = 5, shape = "Biped" },
	},
	{
		id = "BayouHydra",
		name = "Bayou Hydra",
		location = 3,
		rarity = "Epic",
		room = "SteamGrotto",
		prefs = { "steam", "jazz" },
		staff = "RoomService",
		quirk = "Every head orders something different",
		request = "One of everything. Each.",
		look = { colour = Color3.fromRGB(60, 140, 110), height = 6, shape = "Serpent" },
	},
	{
		id = "CypressKing",
		name = "Cypress King",
		location = 3,
		rarity = "Legendary",
		room = "CypressSuite",
		prefs = { "moss", "fireflies" },
		staff = "FrontDesk",
		quirk = "Wears a crown of fireflies",
		request = "My crown needs more light.",
		look = { colour = Color3.fromRGB(100, 90, 60), height = 6, shape = "Biped" },
	},
	{
		id = "MoonHeron",
		name = "Moon Heron",
		location = 3,
		rarity = "Mythic",
		room = "MoonlitLagoon",
		prefs = { "quiet", "fireflies" },
		staff = "Entertainment",
		quirk = "Its call calms the whole street",
		request = "Shh... the moon is out.",
		look = { colour = Color3.fromRGB(225, 235, 255), height = 7, shape = "Biped" },
	},
}

Species.List = rows
Species.ById = {} :: { [string]: Species }
for _, row in rows do
	Species.ById[row.id] = row
end

-- The species of one location's family, in roster order.
function Species.ofLocation(location: number): { Species }
	local out = {}
	for _, row in rows do
		if row.location == location then
			table.insert(out, row)
		end
	end
	return out
end

function Species.get(id: string): Species?
	return Species.ById[id]
end

return Species
