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

-- §3, Appendix A.1: the street, the plot and the grid.
Constants.Grid = {
	CellSize = 12, -- his ruling, 2026-10-19 evening (§3, §18): 2×2 room = 24 × 24 studs
	Cells = 12, -- a 12 × 12 grid per floor (§3)
	FloorHeight = 18, -- his ruling, 2026-10-19 evening: a 1-stud slab and 17 clear
	LobbyRows = 2, -- PLACEHOLDER: floor 1's front rows z 0..1 are the lobby (a gallery above it)
	-- §5.4, his yes 2026-10-19: the plot behind the lobby is bought in areas of
	-- 4 × 5 cells, three across and two deep, each for every floor at once.
	AreaW = 4, -- PLACEHOLDER
	AreaD = 5, -- PLACEHOLDER
	StartArea = 2, -- the front middle one (areas count from the front left, row by row)
	Squares = 4, -- decor squares along a cell: a grid of 3 studs (his yes, §5.4)
	DeskStart = { x = 0, z = 0, r = 1 }, -- a new hotel's FrontDesk: the lobby's end, served toward the entrance (as the old desk)
	SlabThickness = 1,
	WallHeight = 17, -- walls reach the slab above (his ruling): FloorHeight − SlabThickness
	WingDepth = 48, -- his pick, 2026-10-19 (doubled with the grid): the Resident Wing garden behind the hotel
}

Constants.Street = {
	Plots = 6, -- §3
	PlotGap = 36, -- Claude's pick in his range 24–48, 2026-10-19 (GDD §18): 144-stud plots span ±252
	LaneHalfWidth = 24, -- his pick, 2026-10-19: kept, the lane stays 48 wide
	ForecourtDepth = 24, -- his yes, 2026-10-19 (§5.4): the lane's edge to the facade; the plots moved 24 back
	PavementWidth = 8, -- his yes (§5.4): along the lane's edge, the guests walk on it
	PathWidth = 6, -- his yes (§5.4): from the pavement to the entrance arch
	LaneHalfLength = 278, -- the lane runs x -278..278, 26 past the last plot
	BusStopX = 90, -- his ruling, 2026-10-19 (§3): stops at x = ±90, between the first two plots and the last two
	HunterCampX = 278,
	BendRadius = 60, -- PLACEHOLDER: the road's bend into the forest at each end of the lane
	ForestRoad = 360, -- PLACEHOLDER: how far from the lane the road runs on into the forest
}

-- §5.4: the forest round the street (his idea, 2026-10-19). PLACEHOLDER all.
Constants.Forest = {
	Seed = 1019, -- the same forest on every client and every server
	Spacing = 22, -- studs: one tree to a jittered cell of this size
	Fill = 0.75, -- the share of cells that get a tree
	Depth = 150, -- studs from the street's clearing to the forest's outer edge
	Clearing = 14, -- studs kept clear round the plots, the lane and the road
	LowGraphics = 0.5, -- the share of trees the low graphics tier draws
	ProxyDistance = 260, -- studs from the camera beyond which a tree is its LOD_Proxy
}

-- §4.2: rarity values (starting numbers).
export type RarityId = "Common" | "Uncommon" | "Rare" | "Epic" | "Legendary" | "Mythic"
Constants.RarityOrder =
	{ "Common", "Uncommon", "Rare", "Epic", "Legendary", "Mythic" } :: { RarityId }
Constants.Rarity = {
	Common = {
		pay = 1,
		stay = 90,
		friendship = 2,
		weight = 60,
		moveInChance = 0.15,
		releaseShards = 1,
	},
	Uncommon = {
		pay = 3,
		stay = 120,
		friendship = 3,
		weight = 25,
		moveInChance = 0.10,
		releaseShards = 2,
	},
	Rare = {
		pay = 8,
		stay = 180,
		friendship = 5,
		weight = 10,
		moveInChance = 0.07,
		releaseShards = 4,
	},
	Epic = {
		pay = 20,
		stay = 240,
		friendship = 7,
		weight = 4,
		moveInChance = 0.05,
		releaseShards = 8,
	},
	Legendary = {
		pay = 60,
		stay = 300,
		friendship = 10,
		weight = 1,
		moveInChance = 0.03,
		releaseShards = 15,
	},
	Mythic = {
		pay = 200,
		stay = 360,
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
	LocationPayMultiplier = 20, -- ×20 per later location (§4.2)
	RoomCostGrowth = 1.15, -- base × 1.15^n (§6.2)
	TierPayBonus = 0.5, -- +50 % pay per tier (§5.2; kept by his yes, §5.4)
	MaxTier = 3, -- T1..T3, reached by furnishing (§5.4, his yes 2026-10-19)
	-- §5.4: a room's decor points (each item's from its price) take a 2×2 room to
	-- T2 at 100 and T3 at 300; a larger room needs more, in proportion to its cells.
	TierPoints = { 100, 300 }, -- PLACEHOLDER (his yes to the proposal, numbers his to set)
	TierPointsCells = 4, -- the room size TierPoints are for: 2×2
	PointsPerCash = 1, -- PLACEHOLDER: a decor item's points per $ of its price
	AreaCosts = { 0, 1000, 3000, 8000, 20000, 50000 }, -- PLACEHOLDER: the n-th area owned
	Milestones = { 5, 10, 25 }, -- each doubles that type's pay (§6.2)
	SellRefund = 0.5, -- PLACEHOLDER
	FloorCosts = { 0, 500, 5000, 50000 }, -- PLACEHOLDER: floor 1 free; floor 4 needs the pass
	FloorCap = 3, -- floors 1–3 at start (§3)
	TillCap = math.huge, -- PLACEHOLDER: no cap until one is designed
}

-- §4.3: the Night Bus and how a guest picks a hotel.
Constants.Bus = {
	Interval = 180, -- every 3 minutes (his ruling, 2026-10-19, §4.3)
	EpicEvery = 3, -- an Epic guaranteed every 3rd bus (§4.3)
	LegendaryEvery = 1800, -- on the :00 and :30 buses, server clock (§4.3)
	MythicEvery = 7200, -- the Midnight Bus every 2 hours (§4.3)
	VacantShare = 0.4, -- 40 % of the street's vacant rooms, rounded up (his ruling, 2026-10-19)
	MinPerPlayer = 2, -- PLACEHOLDER: at least 2 guests per player on the server (Claude's bound)
	MaxPerPlayer = 4, -- PLACEHOLDER: at most 4 per player (Claude's bound)
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

-- §6.4, §6.5: rebirth and the Moon Tree.
Constants.Rebirth = {
	MinRating = 4, -- §6.4
	RunCash = 1e6, -- $1M earned this run (§6.4), ×20 per location
	ShardScale = 10, -- floor(10 × √(run cash / $1M)) (§6.4)
	ShardDivisor = 1e6,
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

-- §6.2: number format.
Constants.Format = {
	Suffixes = { "", "K", "M", "B", "T", "Qa", "Qi" },
}

return Constants
