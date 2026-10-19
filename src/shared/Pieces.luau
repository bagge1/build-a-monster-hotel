--!strict
--[[
	What a hotel is built from (GDD §5.1, §5.2, Appendix A.2, A.6): rooms and
	amenities, which take cells on a floor, and decor, which sits in a room's
	decor slots. One row each; nothing else in the code names a piece except
	the tutorial (`Locations`).

	`cost` is the base cost: a new room costs base × 1.15^n (§6.2), a tier
	×4 per tier. Every cost but the Standard Room's is a PLACEHOLDER
	(Appendix A.2). `unlock` is what §5.2 asks before the piece can be built:
	`rooms` owned, a `floor` reached, a `rating`, a Legendary resident.

	`colour` is the Luau blockout's (MODELS.md, "Hotel kit") until the kit's
	models exist.
]]

export type Unlock =
	{ rooms: number?, floor: number?, rating: number?, legendaryResident: boolean? }
export type Piece = {
	id: string,
	name: string,
	kind: "Room" | "Amenity",
	w: number,
	d: number,
	cost: number,
	location: number,
	unlock: Unlock?,
	tags: { string }?, -- an amenity's tags, given to every room on its floor
	colour: Color3,
}
export type Decor = {
	id: string,
	name: string,
	tags: { string },
	cost: number,
	location: number,
	colour: Color3,
}

local Pieces = {}

local pieces: { Piece } = {
	-- Location 1 rooms (§5.2)
	{
		id = "StandardRoom",
		name = "Standard Room",
		kind = "Room",
		w = 2,
		d = 2,
		cost = 50,
		location = 1,
		colour = Color3.fromRGB(160, 120, 200),
	},
	{
		id = "GardenRoom",
		name = "Garden Room",
		kind = "Room",
		w = 2,
		d = 2,
		cost = 150,
		location = 1,
		unlock = { rooms = 3 },
		colour = Color3.fromRGB(110, 170, 90),
	},
	{
		id = "AtticRoom",
		name = "Attic Room",
		kind = "Room",
		w = 2,
		d = 2,
		cost = 400,
		location = 1,
		unlock = { floor = 2 },
		colour = Color3.fromRGB(150, 130, 110),
	},
	{
		id = "SarcophagusSuite",
		name = "Sarcophagus Suite",
		kind = "Room",
		w = 2,
		d = 3,
		cost = 1500,
		location = 1,
		unlock = { rating = 2 },
		colour = Color3.fromRGB(210, 180, 100),
	},
	{
		id = "PotionLoft",
		name = "Potion Loft",
		kind = "Room",
		w = 2,
		d = 3,
		cost = 4000,
		location = 1,
		unlock = { rating = 2.5 },
		colour = Color3.fromRGB(120, 200, 170),
	},
	{
		id = "DenRoom",
		name = "Den Room",
		kind = "Room",
		w = 3,
		d = 3,
		cost = 12000,
		location = 1,
		unlock = { rating = 3 },
		colour = Color3.fromRGB(140, 100, 70),
	},
	{
		id = "CoffinSuite",
		name = "Coffin Suite",
		kind = "Room",
		w = 3,
		d = 3,
		cost = 40000,
		location = 1,
		unlock = { rating = 3.5 },
		colour = Color3.fromRGB(120, 30, 50),
	},
	{
		id = "OperaSuite",
		name = "Opera Suite",
		kind = "Room",
		w = 3,
		d = 3,
		cost = 250000,
		location = 1,
		unlock = { rating = 4, legendaryResident = true },
		colour = Color3.fromRGB(200, 170, 230),
	},

	-- Location 1 amenities (Appendix A.2)
	{
		id = "SnackBar",
		name = "Snack Bar",
		kind = "Amenity",
		w = 2,
		d = 2,
		cost = 300,
		location = 1,
		tags = { "snacks" },
		colour = Color3.fromRGB(240, 190, 80),
	},
	{
		id = "MusicRoom",
		name = "Music Room",
		kind = "Amenity",
		w = 2,
		d = 2,
		cost = 800,
		location = 1,
		tags = { "music", "slow music" },
		colour = Color3.fromRGB(90, 140, 220),
	},
	{
		id = "GraveyardGarden",
		name = "Graveyard Garden",
		kind = "Amenity",
		w = 2,
		d = 2,
		cost = 2500,
		location = 1,
		unlock = { rating = 2 },
		tags = { "garden", "darkness" },
		colour = Color3.fromRGB(80, 110, 80),
	},
	{
		id = "QuietLibrary",
		name = "Quiet Library",
		kind = "Amenity",
		w = 2,
		d = 2,
		cost = 6000,
		location = 1,
		unlock = { rating = 2.5 },
		tags = { "quiet", "antique furniture" },
		colour = Color3.fromRGB(130, 90, 60),
	},
	{
		id = "OrganHall",
		name = "Organ Hall",
		kind = "Amenity",
		w = 2,
		d = 2,
		cost = 30000,
		location = 1,
		unlock = { rating = 3.5 },
		tags = { "organ music", "music" },
		colour = Color3.fromRGB(90, 50, 110),
	},

	-- Location 2 rooms (night draft, Appendix A.6)
	{
		id = "IglooRoom",
		name = "Igloo Room",
		kind = "Room",
		w = 2,
		d = 2,
		cost = 1000,
		location = 2,
		colour = Color3.fromRGB(220, 240, 255),
	},
	{
		id = "IceCave",
		name = "Ice Cave",
		kind = "Room",
		w = 2,
		d = 3,
		cost = 8000,
		location = 2,
		unlock = { rating = 2 },
		colour = Color3.fromRGB(150, 200, 240),
	},
	{
		id = "YetiDen",
		name = "Yeti Den",
		kind = "Room",
		w = 3,
		d = 3,
		cost = 60000,
		location = 2,
		unlock = { rating = 3 },
		colour = Color3.fromRGB(200, 210, 220),
	},
	{
		id = "FrostLoft",
		name = "Frost Loft",
		kind = "Room",
		w = 2,
		d = 3,
		cost = 200000,
		location = 2,
		unlock = { rating = 3.5 },
		colour = Color3.fromRGB(170, 190, 255),
	},
	{
		id = "GlacierSuite",
		name = "Glacier Suite",
		kind = "Room",
		w = 3,
		d = 3,
		cost = 800000,
		location = 2,
		unlock = { rating = 4 },
		colour = Color3.fromRGB(100, 170, 220),
	},
	{
		id = "AuroraDome",
		name = "Aurora Dome",
		kind = "Room",
		w = 3,
		d = 3,
		cost = 5000000,
		location = 2,
		unlock = { rating = 4, legendaryResident = true },
		colour = Color3.fromRGB(110, 230, 180),
	},
	{
		id = "CocoaLounge",
		name = "Cocoa Lounge",
		kind = "Amenity",
		w = 2,
		d = 2,
		cost = 6000,
		location = 2,
		tags = { "cocoa" },
		colour = Color3.fromRGB(150, 100, 70),
	},
	{
		id = "AuroraDeck",
		name = "Aurora Deck",
		kind = "Amenity",
		w = 2,
		d = 2,
		cost = 120000,
		location = 2,
		unlock = { rating = 3 },
		tags = { "northern lights", "cold" },
		colour = Color3.fromRGB(90, 220, 170),
	},
}

local decor: { Decor } = {
	{
		id = "PuddleRug",
		name = "Puddle Rug",
		tags = { "damp" },
		cost = 30,
		location = 1,
		colour = Color3.fromRGB(80, 160, 200),
	},
	{
		id = "SnackBasket",
		name = "Snack Basket",
		tags = { "snacks" },
		cost = 40,
		location = 1,
		colour = Color3.fromRGB(230, 170, 70),
	},
	{
		id = "RecordPlayer",
		name = "Record Player",
		tags = { "music", "slow music" },
		cost = 60,
		location = 1,
		colour = Color3.fromRGB(60, 60, 70),
	},
	{
		id = "Candles",
		name = "Candles",
		tags = { "candles", "darkness" },
		cost = 40,
		location = 1,
		colour = Color3.fromRGB(255, 220, 140),
	},
	{
		id = "Planter",
		name = "Planter",
		tags = { "garden" },
		cost = 50,
		location = 1,
		colour = Color3.fromRGB(90, 160, 70),
	},
	{
		id = "AntiqueWardrobe",
		name = "Antique Wardrobe",
		tags = { "antique furniture" },
		cost = 300,
		location = 1,
		colour = Color3.fromRGB(120, 80, 50),
	},
	{
		id = "BlackoutCurtains",
		name = "Blackout Curtains",
		tags = { "dark", "darkness", "quiet" },
		cost = 250,
		location = 1,
		colour = Color3.fromRGB(40, 30, 50),
	},
	{
		id = "SandTray",
		name = "Sand Tray",
		tags = { "dry" },
		cost = 250,
		location = 1,
		colour = Color3.fromRGB(220, 200, 140),
	},
	{
		id = "CatBasket",
		name = "Cat Basket",
		tags = { "cats" },
		cost = 1200,
		location = 1,
		colour = Color3.fromRGB(200, 120, 60),
	},
	{
		id = "Cauldron",
		name = "Cauldron",
		tags = { "cauldron" },
		cost = 1500,
		location = 1,
		colour = Color3.fromRGB(50, 60, 50),
	},
	{
		id = "SteakPlatter",
		name = "Steak Platter",
		tags = { "steak" },
		cost = 4000,
		location = 1,
		colour = Color3.fromRGB(170, 60, 50),
	},
	{
		id = "MoonWindow",
		name = "Moon Window",
		tags = { "moonlight" },
		cost = 5000,
		location = 1,
		colour = Color3.fromRGB(200, 220, 255),
	},
	{
		id = "PipeOrgan",
		name = "Pipe Organ",
		tags = { "organ music", "music" },
		cost = 15000,
		location = 1,
		colour = Color3.fromRGB(150, 120, 80),
	},
	{
		id = "SoundproofWalls",
		name = "Soundproof Walls",
		tags = { "silence", "quiet" },
		cost = 50000,
		location = 1,
		colour = Color3.fromRGB(100, 90, 110),
	},
	{
		id = "Chandelier",
		name = "Chandelier",
		tags = { "chandelier" },
		cost = 60000,
		location = 1,
		colour = Color3.fromRGB(255, 230, 150),
	},
	-- Event decor (location 0: any location once bought in the Candy shop, Events.CandyShop)
	{
		id = "JackOLantern",
		name = "Jack-o'-Lantern",
		tags = { "candles", "garden" },
		cost = 0,
		location = 0,
		colour = Color3.fromRGB(245, 140, 30),
	},
	-- Location 2 (night draft, Appendix A.6)
	{
		id = "IceBlock",
		name = "Ice Block",
		tags = { "cold" },
		cost = 600,
		location = 2,
		colour = Color3.fromRGB(180, 230, 255),
	},
	{
		id = "CocoaMug",
		name = "Cocoa Mug",
		tags = { "cocoa" },
		cost = 800,
		location = 2,
		colour = Color3.fromRGB(130, 80, 50),
	},
	{
		id = "PrankBox",
		name = "Prank Box",
		tags = { "mischief" },
		cost = 1000,
		location = 2,
		colour = Color3.fromRGB(230, 90, 160),
	},
	{
		id = "RockPile",
		name = "Rock Pile",
		tags = { "stone" },
		cost = 5000,
		location = 2,
		colour = Color3.fromRGB(120, 120, 130),
	},
	{
		id = "SnowGlobe",
		name = "Snow Globe",
		tags = { "snow" },
		cost = 30000,
		location = 2,
		colour = Color3.fromRGB(230, 240, 255),
	},
	{
		id = "AuroraLamp",
		name = "Aurora Lamp",
		tags = { "northern lights" },
		cost = 150000,
		location = 2,
		colour = Color3.fromRGB(110, 255, 190),
	},
}

Pieces.List = pieces
Pieces.ById = {} :: { [string]: Piece }
for _, p in pieces do
	Pieces.ById[p.id] = p
end

Pieces.DecorList = decor
Pieces.DecorById = {} :: { [string]: Decor }
for _, d in decor do
	Pieces.DecorById[d.id] = d
end

-- Decor slots per room (MODELS.md, "Hotel kit": `Decor_1`..`Decor_3`).
Pieces.DecorSlots = 3

function Pieces.get(id: string): Piece?
	return Pieces.ById[id]
end

function Pieces.decor(id: string): Decor?
	return Pieces.DecorById[id]
end

return Pieces
