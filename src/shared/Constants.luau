--!strict
--[[
	Every value in the game, in one place, so balancing never means reading
	gameplay code. A value August has set is a decision (user-level CLAUDE.md):
	never changed in passing or to make a test pass.

	The GDD's numbers are starting values for tuning (GDD, preamble). A value
	the GDD does not give carries `-- PLACEHOLDER` and is listed in GDD
	Appendix A: the night sprint of 2026-10-19 chose it so the game could run,
	and it is his to set.
]]

local Constants = {}

-- A.1, his rulings 2026-10-20: windows are bought and placed, one per facade
-- wall section, from four types (MODELS.md `Facade_Window_<Type>`).
Constants.Windows = {
	Types = { "TwinSash", "Arched", "Round", "Wide" }, -- his picks
	Names = { TwinSash = "Twin sash", Arched = "Arched", Round = "Round", Wide = "Wide" },
	-- A new hotel's: a Twin sash on each front wall beside the entrance (his ruling).
	Start = {
		{ floor = 1, x = 4, z = 0, side = 0, type = "TwinSash" },
		{ floor = 1, x = 7, z = 0, side = 0, type = "TwinSash" },
	},
}

-- §3, Appendix A.1: the street, the plot and the grid.
Constants.Grid = {
	CellSize = 12, -- his ruling, 2026-10-19 evening (§3, §18): 2×2 room = 24 × 24 studs
	Cells = 12, -- a 12 × 12 grid per floor (§3)
	FloorHeight = 18, -- his ruling, 2026-10-19 evening: a 1-stud slab and 17 clear
	-- §5.4, A.1, his rulings 2026-10-20: the plot is bought a cell (a tile) at a
	-- time, on each floor apart; no lobby strip, no areas.
	StartTiles = { x = 4, z = 0, w = 4, d = 4 }, -- his pick: a new hotel's 4 × 4 square, centred on the entrance
	TutorialTiles = { w = 3, d = 4 }, -- PLACEHOLDER: the goal card's free block beside the start square, so the 3×3 Coffin Suite fits
	Squares = 4, -- decor squares along a cell: a grid of 3 studs (his yes, §5.4)
	DeskStart = { x = 5, z = 1, r = 0 }, -- his ruling 2026-10-20: across from the arch, served toward the street
	SlabThickness = 1,
	WallHeight = 17, -- walls reach the slab above (his ruling): FloorHeight − SlabThickness
	WingDepth = 48, -- his pick, 2026-10-19 (doubled with the grid): the Resident Wing garden behind the hotel
}

Constants.Street = {
	Plots = 10, -- PLACEHOLDER in his 8–12 (his ruling, 2026-10-20, §3; WAITING §2.35): five a side
	PlotGap = 36, -- Claude's pick in his range 24–48, 2026-10-19 (GDD §18): five 144-stud plots a side span ±432
	LaneHalfWidth = 24, -- his pick, 2026-10-19: kept, the lane stays 48 wide
	ForecourtDepth = 24, -- his yes, 2026-10-19 (§5.4): the lane's edge to the facade; the plots moved 24 back
	PavementWidth = 8, -- his yes (§5.4): along the lane's edge, the guests walk on it
	PathWidth = 6, -- his yes (§5.4): from the pavement to the entrance arch
	LaneHalfLength = 458, -- the lane runs x -458..458, 26 past the last plot (as it did with six)
	BusStopX = 270, -- his ruling, 2026-10-19 (§3): the stops between the first two plots and the last two
	HunterCampX = 458,
	BendRadius = 60, -- PLACEHOLDER: the road's bend into the forest at each end of the lane
	ForestRoad = 360, -- PLACEHOLDER: how far from the lane the road runs on into the forest
}

-- §3, §6.4: one world, every location's street in it (his ruling, 2026-10-20:
-- "All the hotels stand in one world, far apart, seen from the other plots;
-- the environment changes gradually from one place into the next"). A street
-- per location of the chain (`Chain.Locations`), Creepy Lane's layout moved
-- along world X; street s is location s's. PLACEHOLDER all.
Constants.World = {
	-- PLACEHOLDER: studs between two streets' centres. A street's own things reach ±546 in X (its road's
	-- bends), so 1400 leaves 308 studs of forest and road between two, and the last plot of one street is
	-- ~540 studs from the first of the next: inside the fog's end (900), down the meadow below.
	StreetSpacing = 1400,
	-- PLACEHOLDER: the open strip either side of the road between two streets (and the forest's clearing on
	-- top of it), so a street-end plot sees the next street's first hotels down it instead of a wall of trees.
	MeadowHalfWidth = 50,
	RoadWidth = 16, -- PLACEHOLDER: the road between two streets' lanes, as wide as the bus's road
}

-- §5.4: the forest round the street (his idea, 2026-10-19; longer and thicker
-- near the play area, his ruling the same evening). PLACEHOLDER all.
Constants.Forest = {
	Seed = 1019, -- the same forest on every client and every server
	Spacing = 22, -- studs: one tree to a jittered cell of this size, beyond the thicket
	Fill = 0.75, -- the share of those cells that get a tree
	Depth = 600, -- studs from the street's clearing to the forest's outer edge
	ThicketDepth = 60, -- studs of thicket along the clearing
	ThicketSpacing = 14, -- studs: the thicket's cells
	ThicketFill = 0.95, -- the share of the thicket's cells that get a tree
	Clearing = 14, -- studs kept clear round the plots, the lane and the road
	LowGraphics = 0.5, -- the share of trees the low graphics tier draws
	ProxyDistance = 260, -- studs from the camera beyond which a tree is its Root and LOD_Proxy only
	SwapsPerPass = 40, -- trees built or stripped per LOD pass, so a camera jump never hitches
	DrawDistance = 1100, -- PLACEHOLDER: studs from the camera beyond which a tree is not drawn at all (the fog ends at 900)
}

-- §4.2: rarity values (starting numbers).
export type RarityId = "Common" | "Uncommon" | "Rare" | "Epic" | "Legendary" | "Mythic"
Constants.RarityOrder =
	{ "Common", "Uncommon", "Rare", "Epic", "Legendary", "Mythic" } :: { RarityId }
Constants.Rarity = {
	Common = {
		pay = 1,
		stay = 180, -- doubled from 90 (his go, 2026-10-20, GDD §4.2)
		friendship = 2,
		weight = 60,
		moveInChance = 0.15,
		releaseShards = 1,
	},
	Uncommon = {
		pay = 3,
		stay = 240, -- doubled from 120 (his go, 2026-10-20, GDD §4.2)
		friendship = 3,
		weight = 25,
		moveInChance = 0.10,
		releaseShards = 2,
	},
	Rare = {
		pay = 8,
		stay = 360, -- doubled from 180 (his go, 2026-10-20, GDD §4.2)
		friendship = 5,
		weight = 10,
		moveInChance = 0.07,
		releaseShards = 4,
	},
	Epic = {
		pay = 20,
		stay = 480, -- doubled from 240 (his go, 2026-10-20, GDD §4.2)
		friendship = 7,
		weight = 4,
		moveInChance = 0.05,
		releaseShards = 8,
	},
	Legendary = {
		pay = 60,
		stay = 600, -- doubled from 300 (his go, 2026-10-20, GDD §4.2)
		friendship = 5, -- from 10 (his go, 2026-10-20, GDD §4.2)
		weight = 1,
		moveInChance = 0.03,
		releaseShards = 15,
	},
	Mythic = {
		pay = 200,
		stay = 720, -- doubled from 360 (his go, 2026-10-20, GDD §4.2)
		friendship = 15,
		weight = 0,
		moveInChance = 0.01,
		releaseShards = 30,
	},
}
-- moveInChance: Common 15 %, Legendary 3 %, Mythic 1 % are §4.6; Uncommon,
-- Rare and Epic are PLACEHOLDER. releaseShards is PLACEHOLDER (Appendix A.5).
-- Mythic's weight 0: "scheduled only" (§4.2).

-- §4.2, §6.2: the economy.
Constants.Economy = {
	StartCash = 100, -- §6.3
	BasePay = 1, -- $1/s for a Common at Location 1 (§4.2)
	-- His yes 2026-10-23 (the balance run, `archive/BALANCE-2026-10-23.md`, GDD §18): ×5 per later location,
	-- from §4.2's ×20. The pieces' rows stay ×20 a location, so a later hotel's rooms cost more minutes of
	-- income than the Manor's: with pay ×20 as well, Frostfang Lodge was built out in 20 minutes and Bayou Spa in 10.
	LocationPayMultiplier = 5,
	RoomCostGrowth = 1.15, -- base × 1.15^n (§6.2)
	TierPayBonus = 0.5, -- +50 % pay per tier (§5.2; kept by his yes, §5.4)
	MaxTier = 3, -- T1..T3, reached by furnishing (§5.4, his yes 2026-10-19)
	-- §5.4: a room's decor points (each item's from its price) take a 2×2 room to
	-- T2 at 100 and T3 at 300; a larger room needs more, in proportion to its cells.
	TierPoints = { 100, 300 }, -- PLACEHOLDER (his yes to the proposal, numbers his to set)
	TierPointsCells = 4, -- the room size TierPoints are for: 2×2
	PointsPerCash = 1, -- PLACEHOLDER: a decor item's points per $ of its price
	TileCost = 50, -- PLACEHOLDER (his "cheap", §5.4, A.1): the n-th tile bought costs TileCost × TileGrowth^n
	TileGrowth = 1.03, -- PLACEHOLDER: the whole ground floor then costs about what the six areas did (~$72,000)
	TileFloorFactor = 2, -- PLACEHOLDER (his "more expensive" upstairs): floor f's ladder × TileFloorFactor^(f−1)
	DeskCost = 500, -- PLACEHOLDER: a second or later FrontDesk (the first is free, §5.4)
	WindowCost = 100, -- PLACEHOLDER: a window on a facade wall (A.1); selling refunds what was paid
	Milestones = { 5, 10, 25 }, -- each doubles that type's pay (§6.2)
	SellRefund = 0.5, -- PLACEHOLDER
	FloorCosts = { 0, 500, 5000, 50000, 500000, 5000000, 50000000 }, -- PLACEHOLDER: floor 1 free; the cap is Chain.floorCap (§6.4)
	TillCap = math.huge, -- PLACEHOLDER: no cap until one is designed
	-- His yes 2026-10-23 (the balance run; was BasePay × 10 in two places): the floor under every reward that
	-- is "minutes of income" (the login calendar, a daily request, a VIP contract, Hunter Night, the Starter
	-- Pack), × BasePay. At × 10 the first login paid ten times what the first room earned.
	RewardFloor = 2,
}

-- §4.3: the Night Bus and how a guest picks a hotel.
Constants.Bus = {
	Interval = 180, -- every 3 minutes (his ruling, 2026-10-19, §4.3)
	EpicEvery = 3, -- an Epic guaranteed every 3rd bus (§4.3)
	LegendaryEvery = 1800, -- on the :00 and :30 buses, server clock (§4.3)
	MythicEvery = 7200, -- the Midnight Bus every 2 hours (§4.3)
	VacantShare = 0.4, -- 40 % of the street's vacant rooms, rounded up (his ruling, 2026-10-19)
	MinPerPlayer = 3, -- at least 3 guests per player on the server (his go, 2026-10-20; was 2)
	MaxPerPlayer = 8, -- at most 8 per player (his go, 2026-10-20; was 4)
	FirstBusDelay = 105, -- PLACEHOLDER: a fresh server's first bus at 1:45 (§11)
	BrowseTime = 60, -- about a minute browsing before a guest picks (his yes, 2026-10-19)
	EntrancePause = 2, -- a couple of seconds at each entrance (his yes, 2026-10-19)
	BrowseSpeed = 8, -- PLACEHOLDER: studs/s along the pavement
	Speed = 50, -- PLACEHOLDER: the bus's cruising speed, studs/s
	Brake = 50, -- PLACEHOLDER: studs to slow from cruising to a stop (and to speed up again)
	StopTime = 7, -- PLACEHOLDER: seconds at each stop
	StepOff = 0.6, -- PLACEHOLDER: seconds between guests stepping off
}

Constants.Scoring = {
	RatingPower = 1.5, -- ratingStars^1.5 × 1.0 (§4.3)
	RatingWeight = 1.0,
	PreferenceWeight = 0.6, -- preferencesMatched × 0.6
	AmenityWeight = 0.3, -- amenityBonus × 0.3
	PitchBonus = 0.15, -- +15 % score toward the pitcher's hotel (§4.3)
	NewcomerBoost = 1.0, -- PLACEHOLDER (Appendix A.3)
	NewcomerMaxRating = 2, -- PLACEHOLDER: hotels at or under 2★
	TutorialBoost = 10, -- PLACEHOLDER: a tutorial Common's score toward the hotel it came for (§11 1:45, Appendix A.7)
	JitterLow = 0.9, -- score *= random(0.9, 1.1)
	JitterHigh = 1.1,
	PitchRange = 14, -- PLACEHOLDER: studs from the guest
}

-- §4.4, Appendix A.3: a stay.
Constants.Stay = {
	WalkSpeed = 10, -- PLACEHOLDER: studs/s for a guest on its way in
	DeskPatience = 60, -- PLACEHOLDER
	SatisfactionBase = 50, -- PLACEHOLDER, and every Satisfaction* below (50: both preferences at T1 make 80, Appendix A.3)
	SatisfactionPerPreference = 15,
	SatisfactionPerTier = 5,
	SatisfactionPerAmenity = 5,
	SatisfactionAmenityMax = 15,
	SatisfactionRequestPlayer = 10,
	SatisfactionRequestStaff = 5,
	SatisfactionRequestMissed = -10,
	WaitFree = 10, -- seconds at the desk before it costs anything
	WaitPerPoint = 5, -- −1 per 5 s beyond
	WaitMaxPenalty = 20,
	Happy = 80, -- satisfaction ≥ 80 is a happy stay (§4.4, §4.6)
	TipFraction = 0.25, -- PLACEHOLDER
	RequestWindow = 30, -- PLACEHOLDER: seconds a request stays open
	RequestTipSeconds = 10, -- PLACEHOLDER: a personal fulfilment tips 10 s of pay
	CleanHold = 2, -- PLACEHOLDER: seconds to hold at the door
	CheckInHold = 0, -- a tap (§11)
	ReviewsKept = 30, -- the last 30 reviews (§5.3)
}

-- §11: the tutorial's first guest, the only one that does not come on the bus (his ruling, 2026-10-19).
Constants.Tutorial = {
	FirstGuestDelay = 6, -- PLACEHOLDER: the first Slime after the first room (§11 0:30)
	CommonBuses = 2, -- PLACEHOLDER: the buses that bring a new hotel its Commons (§11 1:45)
	CommonsPerBus = 2, -- PLACEHOLDER: at most this many Commons per hotel on such a bus
}

-- §5.3, Appendix A.4: the rating.
Constants.Rating = {
	Min = 1,
	Max = 5,
	FunPerAmenity = 15, -- PLACEHOLDER, and every value below
	FunPerEntertainer = 20,
	StylePerDecor = 4,
	StylePerRoomType = 10,
	ServiceWaitPerPoint = 1, -- −1 service per second of mean desk wait
	ServiceSampleSize = 20, -- recent check-ins
	CategoryCurve = 1.5, -- stars from categories: 1 + 4 × (mean/100)^1.5
	-- Staff coverage and rooms cleaned on time (§5.3; PLACEHOLDER, every value
	-- below, WAITING §2.26): points added on top, so a hotel without staff
	-- scores as it did before them.
	ServicePerDeskCoverage = 10, -- Service at full Front Desk coverage
	ServicePerRoomServiceCoverage = 10, -- Service at full Room Service coverage
	CleanPerHousekeepingCoverage = 10, -- Cleanliness at full Housekeeping coverage
	CleanPerOnTime = 10, -- Cleanliness when every recent cleaning was on time
	DesksCovered = 1, -- Front Desk efficiency that covers the desk
	RoomsPerStaff = 4, -- rooms one Room Service or Housekeeping at 100 % covers
	CleanOnTime = 40, -- seconds a room may stay dirty and still be cleaned on time
	CleanSampleSize = 20, -- recent cleanings
}

-- §4.6, Appendix A.5: residents and staff.
Constants.Residents = {
	EarnFraction = 0.25, -- 25 % of the species' pay rate (§4.6)
	OfflineFraction = 0.5, -- offline at 50 % of that (§4.6)
	OfflineCap = 2 * 3600, -- capped at 2 hours (§4.6)
	NightManagerCap = 8 * 3600, -- 8 hours with the pass (§4.6, §10.2)
	WingCapacity = 6, -- capacity 6 at start (§4.6)
	WingPassSlots = 6, -- Resident Wing+ (§10.2)
	TutorialFriendship = 1, -- the tutorial Slime needs 1 (§6.3)
	-- A.11.6 residents level up (night brief step 9): every value below PLACEHOLDER.
	LevelCap = 10, -- PLACEHOLDER: one cap for every rarity (decision 2)
	LevelWing = 0.10, -- PLACEHOLDER: Wing earnings +10 % a level above 1
	LevelEfficiency = 0.03, -- PLACEHOLDER: staff efficiency +3 % a level above 1
	LevelXpPerMinute = 1, -- PLACEHOLDER: XP a minute at work while the player plays, in the Wing or at a post alike
	LevelXpBar = 20, -- PLACEHOLDER: the bar from level L to L+1 is this × L XP (900 to the cap)
	LevelPriceMinutes = 10, -- PLACEHOLDER: level L to L+1 costs this × L minutes of the resident's own Wing rate
}

Constants.Staff = {
	BestEfficiency = 1.0, -- PLACEHOLDER, and every value below (Appendix A.5)
	OtherEfficiency = 0.6,
	FrontDeskDelay = 6,
	HousekeepingDelay = 20,
	RoomServiceDelay = 12,
	BellhopSpeedBonus = 0.25,
	BellhopCheckInBonus = 0.25, -- PLACEHOLDER (A.5): a Bellhop also shortens Front Desk's check-in
	SecurityInterval = 8,
	WalkSpeed = 10, -- studs/s on an errand: a guest's pace (§4.6 "Staff are seen working")
	AtDoor = 2, -- seconds at the door at least before the job is done
}

Constants.Book = {
	SpeciesFoundPaySeconds = 60, -- PLACEHOLDER: a cash bonus of 60 s of its pay
	FamilyBonus = 0.05, -- +5 % income per family completed (§4.6)
}

-- §5.4, Appendix A.12 (his rulings 2026-10-21): rooms built from walls. PLACEHOLDER all.
Constants.Rooms = {
	HalfCells = 2, -- half cells to a cell side: walls stand on half-cell edges (6 studs)
	WallCost = 5, -- a half edge of inner wall
	DoorCost = 10, -- a door in a half edge (it replaces the wall)
	FullSizeFactor = 2, -- a type's full size is its minimum × this
	FurnitureTargetFactor = 2, -- a type's Furniture target is its old price × this …
	FurnitureTargetMin = 100, -- … and at least this many points
	DecorTargetPer4Cells = 300, -- the Decor bar is full at this per 4 cells (the old T3)
	SizePay = 0.5, -- pay × (1 + this × Size)
	SizeStay = 0.5, -- stay × (1 + this × Size)
	FurniturePay = 0.5, -- pay × (1 + this × Furniture)
	FurnitureSatisfaction = 15, -- satisfaction points × Furniture
	DecorSatisfaction = 15, -- satisfaction points × Decor
	DecorFriendship = 1, -- friendship per happy stay × (1 + this × Decor)
	-- His yes 2026-10-23 (the balance run): 2.5 Comfort points per ready room at full bars, from 12, so the
	-- cap takes about 24 full rooms instead of 5 and 5★ waits for a hotel, not for five furnished rooms
	ComfortPerRoom = 2.5,
	ComfortRoomsCap = 60, -- … summed, to this (it was the mean tier's 60 %)
	-- A new hotel's one room (his ruling 2026-10-20: "the reception in the middle and one
	-- room to its right", as a guest sees it from the street, the −x side; built from walls
	-- since 2026-10-21). PLACEHOLDER shape: walls may touch neither the desk nor the mouth
	-- (A.12), so no 2 × 2 fits the start square; this is an L of four cells, (4, 2) and the
	-- back row (4..6, 3), its door off cell (4, 1).
	Start = {
		type = "StandardRoom",
		seed = { hx = 9, hz = 5 }, -- a half cell of the room (Rooms: a room is the area holding it)
		walls = { { 4, 2, 0 }, { 4, 2, 3 }, { 5, 3, 0 }, { 6, 3, 0 }, { 6, 3, 3 } }, -- whole cell edges on floor 1: x, z, side (Rooms.cellEdges)
		door = { hx = 9, hz = 4, o = 0 }, -- the half edge with the door (Rooms.edgeKey)
		furniture = { { item = "Bed", x = 17, z = 13, r = 0 } }, -- squares, its head on the back wall
	},
}

-- §6.4, §6.5: rebirth and the Moon Tree.
Constants.Rebirth = {
	ShardScale = 10, -- floor(10 × √(run cash / $1M)) (§6.4)
	ShardDivisor = 1e6,
}

-- §6.4, his rulings 2026-10-20: the hotel chain, the new rebirth, floors and Prestige Stars.
Constants.Chain = {
	Locations = 3, -- Haunted Manor, Frostfang Lodge, Bayou Spa at launch (§6.6)
	RebirthRating = 5, -- 5★ on every hotel of the chain (his ruling)
	-- His yes 2026-10-23 (the balance run; WAITING §2.35 answered): opening each location, from $250k and
	-- $10M. Bayou Spa at $1M keeps his "each exponentially dearer" (×2.5) at the cost of 3 minutes on its
	-- leg: the third hotel's time is its rooms (the rows ×400 the Manor's at pay ×25), not its price.
	OpenCost = { [2] = 400000, [3] = 1000000 },
	BackgroundShare = 0.25, -- PLACEHOLDER (WAITING §2.35): a hotel not played earns this share of its rate
	RateWindow = 300, -- seconds the played hotel's earning rate is averaged over (an EMA's time constant)
	StartFloorCap = 2, -- floors a hotel may have before any rebirth (his ruling)
	FloorCapMax = 6, -- PLACEHOLDER (WAITING §2.35): the cap by rebirth, before the Extra Floor pass
	PrestigeIncome = 0.05, -- PLACEHOLDER (WAITING §2.35): + income per Prestige Star
	PrestigeRarity = 0.02, -- PLACEHOLDER (WAITING §2.35): + chance of a rarer guest per Prestige Star
	PrestigeEffectCap = 10, -- PLACEHOLDER: stars past this add no more effect
}

Constants.MoonTree = {
	CostGrowth = 1.5, -- ×1.5 per level (§6.5)
}

-- §8.1, Appendix A.8: Hunter Night.
Constants.HunterNight = {
	Interval = 90 * 60, -- every 90 minutes (§8.1)
	Duration = 3 * 60, -- lasting 3 minutes (§8.1)
	FirstDelay = 20 * 60, -- PLACEHOLDER: a fresh server's first night
	HuntersPerHotel = 2, -- PLACEHOLDER
	ApproachTime = 45, -- PLACEHOLDER
	BooRange = 40, -- PLACEHOLDER
	RewardIncomeSeconds = 300, -- PLACEHOLDER: 5 minutes of income
	CampReturn = 24 * 3600, -- comes back after 24 hours (§8.1)
	DefendedShare = 0.5, -- PLACEHOLDER: fewer than half reached a door
	BonusBusSize = 6, -- PLACEHOLDER
}

-- §8.1, Appendix A.8: traps in the forecourt's three trap slots (§5.4). Each scares the
-- first hunter that comes within reach of it, once a night. PLACEHOLDER all.
Constants.Traps = {
	{
		id = "SlimePuddle",
		name = "Slime Puddle",
		cost = 500,
		colour = Color3.fromRGB(110, 220, 120),
	},
	{
		id = "CreakyBoards",
		name = "Creaky Floorboards",
		cost = 2000,
		colour = Color3.fromRGB(140, 100, 70),
	},
	{
		id = "PortraitEyes",
		name = "Portrait with Eyes",
		cost = 8000,
		colour = Color3.fromRGB(200, 170, 90),
	},
}
Constants.TrapReach = 10 -- studs from the trap

-- §7: social.
Constants.Social = {
	FriendBonus = 0.10, -- +10 % while 2+ friends play together (§7)
	LikesPerDay = 1, -- one like per hotel per day (§7)
}

--[[ A.11.5 deeper mutations (night brief step 9): a size and a look stack,
	their pay added; a mutation of the month. Every value PLACEHOLDER. ]]
Constants.Mutations = {
	MonthlyChance = 0.03, -- PLACEHOLDER: the month's mutation, a row of the look table in its month (as Pumpkin's 3 %)
	MonthlyPay = 4, -- PLACEHOLDER: ×4 pay, as Pumpkin
	Monthly = { [3] = "Mossy", [5] = "Rainbow", [7] = "Sunburnt", [9] = "Moonlit" }, -- PLACEHOLDER: month → mutation id (Halloween and Winter as they are)
	StackTitle = "Stacked Host", -- PLACEHOLDER: the title for a first stack of any kind (his to name)
}

--[[ A.11.4 the showcase, built street only (his call, WAITING §2.38: the
	draft's recommendation, reversible). Every number PLACEHOLDER. ]]
Constants.Showcase = {
	Milestones = { 10, 50, 200, 1000 }, -- PLACEHOLDER: lifetime likes for the ribbon, rosette, trophy and gold star (Cosmetics.luau)
	LikeAfterPlay = 10 * 60, -- PLACEHOLDER: a like counts only from a player with 10 minutes of play that day
	VisitDaily = 3, -- PLACEHOLDER: the daily request "Visit 3 hotels" (other players' lobbies)
}

--[[ A.11.1 VIP contracts, on the draft's scrutinized recommendations (his
	calls, WAITING §2.38; reversible). Every value PLACEHOLDER. ]]
Constants.Contracts = {
	UnlockStars = 2, -- PLACEHOLDER: the front desk's VIP ledger opens at 2★
	Offers = 3, -- PLACEHOLDER: offers in the ledger, counting the contracts taken from it at that hotel
	Active = 1, -- PLACEHOLDER: contracts running at once (decision 5b) …
	ActiveFromStars = 4, -- … and one more from 4★ …
	ActiveMore = 2, -- … making two
	Swaps = 1, -- PLACEHOLDER: free swaps of an offer a UTC day (+1 with VIP Lobby, as the daily reroll); a Book request costs one
	Deadline = 45 * 60, -- PLACEHOLDER: seconds of play at the contract's own hotel (decision 3a)
	DailyCap = 3, -- PLACEHOLDER: contracts completed per UTC day, all hotels together; none accepted past it
	-- His yes 2026-10-23 (the balance run): minutes of income, from 15: three contracts a day at 15 paid
	-- a hotel's opening price on their own …
	RewardMinutes = 4,
	RarityReward = { Common = 1, Uncommon = 1.5, Rare = 2, Epic = 3, Legendary = 4, Mythic = 6 }, -- … × this by the VIP's rarity
	-- PLACEHOLDER: the rarest VIP drawn at a rating (its whole stars); none below UnlockStars.
	RarityByStars = { [2] = "Rare", [3] = "Epic", [4] = "Legendary", [5] = "Mythic" },
	RarityWeights = { Common = 6, Uncommon = 5, Rare = 4, Epic = 3, Legendary = 2, Mythic = 1 }, -- PLACEHOLDER: a VIP's draw by rarity
	Thresholds = { 0.5, 1.0 }, -- PLACEHOLDER: the first bar asked for (one set above the best room's now)
	SecondBarStars = 3.5, -- PLACEHOLDER: a second bar is asked from this rating …
	SecondThreshold = 0.5, -- … at this
	MutationChance = 0.1, -- PLACEHOLDER: a VIP named with a look (Shadow, Golden, Glitched; never a season's or a month's)
	VipPay = 2, -- PLACEHOLDER: the VIP's pay × this for its stay
	ArrivalGrace = 150, -- seconds a VIP taken by the bus may take to step off before its contract is Accepted again
}

--[[ GDD A.11.3: rare decor sets and souvenirs, on the draft's scrutinized
	recommendations (his calls, WAITING §2.38). Every number PLACEHOLDER. A
	set piece's price (`Pieces`, `cost`) is what placing a copy costs and
	gives its points: twice a shop piece of its size's. ]]
Constants.Finds = {
	StayChance = 0.02, -- PLACEHOLDER: a set piece's roll per happy stay of a guest of MinRarity or rarer …
	MinRarity = "Rare", -- … (A.11.3 Numbers)
	Pity = 40, -- PLACEHOLDER: after 40 rolls in a row without a find, the next gives the location's next unfound piece
	HunterChance = 0.25, -- PLACEHOLDER: one roll per player on a defended Hunter Night (decision 5: per street, every player on it)
	SetBonus = 0.25, -- PLACEHOLDER: a whole set in one room adds this to its Decor bar, once per set per hotel
	DuplicateMinutes = 5, -- PLACEHOLDER: a find once a location's sets are all found: minutes of income in cash (at least the piece's price)
	SouvenirMoveIns = 3, -- PLACEHOLDER: a species' souvenir on its 3rd move-in, or its first VIP contract, whichever first
	SouvenirCost = { 200, 4000, 80000 }, -- PLACEHOLDER: placing a souvenir, by its species' location (×20 a location, as the pieces' rows)
	KeepThroughRebirth = true, -- PLACEHOLDER (decision 4a, his call with §6.4): found stays found; placed copies go with the hotel
}

-- GDD A.13.1: visits to activity rooms (`Shared/Visits`, GuestService). Every number is A.13's, PLACEHOLDER.
Constants.Visits = {
	EveryMin = 90, -- PLACEHOLDER: seconds of a stay between visits ("every 90–150 s") …
	EveryMax = 150, -- … PLACEHOLDER
	DecisionGap = 10, -- PLACEHOLDER: at most one visit decision a guest per this many seconds (the server's cost)
	MaxWalking = 12, -- PLACEHOLDER: visitors walking (to a room or back) at once per hotel (the server's cost)
	DoMin = 20, -- PLACEHOLDER: seconds a visit's action lasts ("20–40 s") …
	DoMax = 40, -- … PLACEHOLDER
	Satisfaction = 5, -- PLACEHOLDER: what a visit meeting a preference adds, once a stay
}

-- §6.2: number format.
Constants.Format = {
	Suffixes = { "", "K", "M", "B", "T", "Qa", "Qi" },
}

return Constants
