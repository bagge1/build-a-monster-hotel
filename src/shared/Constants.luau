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
	CellSize = 6, -- his ruling, 2026-10-19
	Cells = 12, -- a 12 × 12 grid per floor (§3)
	FloorHeight = 12, -- about 12 studs (§3)
	LobbyRows = 2, -- PLACEHOLDER: floor 1's front rows z 0..1 are the lobby
	StairCore = { x = 10, z = 2, w = 2, d = 2 }, -- PLACEHOLDER: cells on every floor
	SlabThickness = 1,
	WallHeight = 10, -- PLACEHOLDER: room walls, under the 12-stud floor
	WingDepth = 24, -- PLACEHOLDER: the Resident Wing garden behind the hotel
}

Constants.Street = {
	Plots = 6, -- §3
	PlotGap = 24, -- PLACEHOLDER
	FrontOffset = 24, -- PLACEHOLDER: plot fronts from the lane's centre line
	LaneHalfLength = 170, -- PLACEHOLDER: the lane runs x -170..170
	BusStopX = -170,
	HunterCampX = 170,
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
	TierCostMultiplier = 4, -- ×4 per tier (§5.2, §6.2)
	TierPayBonus = 0.5, -- +50 % pay per tier (§5.2)
	TierComfort = 10, -- +10 comfort per tier (§5.2)
	MaxTier = 5, -- T1..T5 (§5.1)
	Milestones = { 5, 10, 25 }, -- each doubles that type's pay (§6.2)
	SellRefund = 0.5, -- PLACEHOLDER
	FloorCosts = { 0, 500, 5000, 50000 }, -- PLACEHOLDER: floor 1 free; floor 4 needs the pass
	FloorCap = 3, -- floors 1–3 at start (§3)
	TillCap = math.huge, -- PLACEHOLDER: no cap until one is designed
}

-- §4.3: the Night Bus and how a guest picks a hotel.
Constants.Bus = {
	Interval = 240, -- every 4 minutes (§4.3)
	EpicEvery = 3, -- an Epic guaranteed every 3rd bus (§4.3)
	LegendaryEvery = 1800, -- on the :00 and :30 buses, server clock (§4.3)
	MythicEvery = 7200, -- the Midnight Bus every 2 hours (§4.3)
	BaseSize = 6, -- 6–10 guests scaled by player count (§4.3)
	SizePerPlayer = 1, -- PLACEHOLDER: +1 per player beyond the first
	MaxSize = 10,
	FirstBusDelay = 105, -- PLACEHOLDER: a fresh server's first bus at 1:45 (§11)
	BrowseSpeed = 8, -- PLACEHOLDER: studs/s down the lane
	GuestSpacing = 4, -- PLACEHOLDER: studs between guests leaving the bus
}

Constants.Scoring = {
	RatingPower = 1.5, -- ratingStars^1.5 × 1.0 (§4.3)
	RatingWeight = 1.0,
	PreferenceWeight = 0.6, -- preferencesMatched × 0.6
	AmenityWeight = 0.3, -- amenityBonus × 0.3
	PitchBonus = 0.15, -- +15 % score toward the pitcher's hotel (§4.3)
	NewcomerBoost = 1.0, -- PLACEHOLDER (Appendix A.3)
	NewcomerMaxRating = 2, -- PLACEHOLDER: hotels at or under 2★
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

Constants.WalkIn = {
	BaseInterval = 30, -- PLACEHOLDER (Appendix A.3)
	PerRoom = 0.15,
	RatingPivot = 3,
	MinInterval = 8,
	MaxInterval = 60,
	TutorialDelay = 6, -- PLACEHOLDER: the first Slime after the first room (§11 0:30)
}

-- §5.3, Appendix A.4: the rating.
Constants.Rating = {
	Min = 1,
	Max = 5,
	FunPerAmenity = 15, -- PLACEHOLDER, and every value below
	FunPerEntertainer = 20,
	StylePerDecor = 4,
	StylePerRoomType = 10,
	ComfortPerTier = 20,
	ServiceWaitPerPoint = 1, -- −1 service per second of mean desk wait
	ServiceSampleSize = 20, -- recent check-ins
	CategoryCurve = 1.5, -- stars from categories: 1 + 4 × (mean/100)^1.5
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
	SecurityInterval = 8,
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
