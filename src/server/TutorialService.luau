--!strict
--[[
	The first fifteen minutes with Gloom, the bat concierge (GDD §11,
	Appendix A.7). Each step is closed by something the server SEES happen,
	read from the profile (a room built, a check-in counted, a resident moved
	in), never by the client saying so; a step whose condition is already met
	when it starts closes at once, so the order never traps anyone.

	Offered once, skippable at any step (the `Tutorial` remote), and it never
	locks movement. The step is the profile's `tutorial` (published as the
	player's `Tutorial` attribute); the client draws Gloom's bubble for it.

	What it arranges: the tutorial Slime, the only guest in the game that does
	not come on the Night Bus (his ruling, 2026-10-19), walks in from the
	pavement before the first bus (§11 0:30); its stay counts as happy and it
	needs 1 friendship (§6.3); the first `Tutorial.CommonBuses` buses once
	the Slime is in bring Commons for the hotel's vacant rooms, weighted toward
	it ("The tutorial weights Commons toward your hotel", §11 1:45; BusService);
	the goal card unlocks the Coffin Suite with its key piece free (a voucher), and a Vampire
	Count booked to this hotel rides the third bus after it once one stands
	(§11 "the tutorial schedules it").
]]

local ReplicatedStorage = game:GetService("ReplicatedStorage")
local ServerScriptService = game:GetService("ServerScriptService")

local Bus = require(ReplicatedStorage.Shared.Bus)
local Constants = require(ReplicatedStorage.Shared.Constants)
local Net = require(ReplicatedStorage.Shared.Net)
local Pieces = require(ReplicatedStorage.Shared.Pieces)
local PlayerData = require(ServerScriptService.Server.PlayerData)
local BuildService = require(ServerScriptService.Server.BuildService)
local GuestService = require(ServerScriptService.Server.GuestService)
local HotelService = require(ServerScriptService.Server.HotelService)
local BusService = require(ServerScriptService.Server.BusService)
local StateService = require(ServerScriptService.Server.StateService)
local Analytics = require(ServerScriptService.Server.Analytics)
local DevGrant = require(ServerScriptService.Server.DevGrant)

local TutorialService = {}

-- A new hotel starts with its one built room (his ruling 2026-10-20, A.12), so
-- the first step is the Slime's check-in; the second room is built by walls, a
-- door and a type (`SecondRoom`), then furnished (`Furnish`).
TutorialService.Steps = {
	"CheckIn",
	"Collect",
	"SecondRoom",
	"Furnish",
	"Bus",
	"MoveIn",
	"Goal",
	"Clean",
	"Staff",
	"Preview",
	"Done",
}

local stepStarted: { [Player]: number } = {}
local slimeSent: { [Player]: number } = {} -- when this session last sent the tutorial Slime
local nextPressed: { [Player]: boolean } = {}
local vampireOnBus: { [Player]: boolean } = {} -- the tutorial's Vampire Count is on a bus this session
local vampireTold: { [Player]: boolean } = {} -- the street has heard of this player's Vampire this session
-- This server's BusIndex at the goal card, when it was shown in this session: every server
-- counts its buses from 0, so the index means nothing on another (2026-10-26 review).
local goalBusHere: { [Player]: number } = {}
-- The step's counts at its start: a Common that chose the hotel during Furnish closed the
-- Bus step the moment it began (2026-10-26 review: `busGuests` is a lifetime count).
local stepBase: { [Player]: { pitches: number, busGuests: number } } = {}

local function rooms(data: PlayerData.Data): number
	local n = 0
	for _, rec in data.rooms do
		local p = Pieces.get(rec.type)
		if p and p.kind == "Room" then
			n += 1
		end
	end
	return n
end

-- Rooms ready for guests (A.12): their key furniture in, their size, a door.
local function readyRooms(player: Player, data: PlayerData.Data): number
	local n = 0
	for id, rec in data.rooms do
		local p = Pieces.get(rec.type)
		if p and p.kind == "Room" and HotelService.ready(player, id) then
			n += 1
		end
	end
	return n
end

local function stat(data: PlayerData.Data, key: string): number
	return data.stats[key] or 0
end

local function step(data: PlayerData.Data): string
	-- "Build" was the first step before rooms were built from walls (A.12).
	return if data.tutorial == "Start" or data.tutorial == "Build" then "CheckIn" else data.tutorial
end

-- The steps the tutorial Slime is needed through: checked in, then moving in.
local WAITS_FOR_SLIME = {
	CheckIn = true,
	Collect = true,
	SecondRoom = true,
	Furnish = true,
	Bus = true,
	MoveIn = true,
}
local SLIME_RETRY = 30 -- seconds: a Slime sent with no room for it is tried again after this

-- Whether this player's tutorial Slime is a guest now (walking in, queued or staying).
local function slimeHere(player: Player): boolean
	for _, g in GuestService.of(player) do
		if g.tutorialFriend then
			return true
		end
	end
	return false
end

-- Whether this player's tutorial Slime stands in the desk's line now, waiting to be checked in.
local function slimeAtDesk(player: Player): boolean
	for _, g in GuestService.of(player) do
		if g.tutorialFriend and g.state == "Queued" then
			return true
		end
	end
	return false
end

local function setBase(player: Player, data: PlayerData.Data)
	stepBase[player] = { pitches = stat(data, "pitches"), busGuests = stat(data, "busGuests") }
end

local function satisfied(player: Player, data: PlayerData.Data, s: string, since: number): boolean
	if s == "CheckIn" then
		return stat(data, "checkIns") >= 1
	elseif s == "Collect" then
		-- With Auto-Collect the till never fills (GuestService pays the wallet): nothing to collect.
		return stat(data, "collects") >= 1 or data.passes.AutoCollect == true
	elseif s == "SecondRoom" then
		return rooms(data) >= 2
	elseif s == "Furnish" then
		return readyRooms(player, data) >= 2
	elseif s == "Bus" then
		local base = stepBase[player] or { pitches = 0, busGuests = 0 }
		return stat(data, "pitches") > base.pitches
			or stat(data, "busGuests") > base.busGuests
			or os.clock() - since > 150
	elseif s == "MoveIn" then
		return next(data.residents) ~= nil
	elseif s == "Goal" then
		-- Closed by the client once the card has been on screen, uncovered, for
		-- `Tutorial.GoalCardTime`, or by its Got it! (2026-10-26 review: 8 s of wall
		-- clock ran out under build mode or the Book, the card never seen).
		return nextPressed[player] == true
	elseif s == "Clean" then
		return stat(data, "cleaned") >= 1
	elseif s == "Staff" then
		for _, r in data.residents do
			if r.role ~= "" then
				return true
			end
		end
		return false
	elseif s == "Preview" then
		return nextPressed[player] == true or os.clock() - since > 25
	end
	return false
end

local function setStep(player: Player, data: PlayerData.Data, s: string)
	data.tutorial = s
	player:SetAttribute("Tutorial", s)
	stepStarted[player] = os.clock()
	nextPressed[player] = nil
	setBase(player, data)
	if s == "Goal" then
		BuildService.tutorialUnlock(player, "CoffinSuite")
		BuildService.tutorialTiles(player)
		data.stats.voucher_CoffinSuite = 1
		data.stats.tutorialGoal = 1
		-- The goal's time, the same on every server, for "in 3 buses" after a rejoin (Bus.busesSince).
		data.stats.tutorialGoalAt = os.time()
		goalBusHere[player] = workspace:GetAttribute("BusIndex") :: number? or 0
	elseif s == "MoveIn" then
		Net.fire(player, "Moment", "OpenBook", {})
	end
	Analytics.step(player, `Tutorial_{s}`)
	StateService.mark(player)
end

--[[ The scheduled Vampire Count: on the third bus after the goal card ("A
	Vampire Count arrives in 3 buses", §11), booked to this hotel once a
	Coffin Suite stands vacant for it, whatever step the player is on by then
	(2026-10-26 review: booked only at Done, a player who never gave a resident
	a job never got the Vampire the card promised). Every guest comes by bus
	(§4.3). `tutorialVampire` is 1 once it has reached the hotel (walking to its
	desk); one that missed at step-off (its room gone, no way to it) went home
	and is offered again on a later bus (Bus.tutorialVampire). Being on a bus
	lives only in this session, so a player who left before it came is owed it
	on coming back. ]]
local function bookVampire(player: Player, data: PlayerData.Data)
	if stat(data, "tutorialGoal") ~= 1 or stat(data, "tutorialVampire") ~= 0 then
		return
	end
	local here = goalBusHere[player]
	local busesSince = Bus.busesSince(
		stat(data, "tutorialGoalAt"),
		os.time(),
		Constants.Bus.Interval,
		if here then (workspace:GetAttribute("BusIndex") :: number? or 0) - here else nil
	)
	if
		Bus.tutorialVampire({
			goal = true,
			arrived = false,
			onBus = vampireOnBus[player] == true,
			busesSince = busesSince,
			vacant = HotelService.vacantFor(player, "VampireCount") ~= nil,
		})
	then
		vampireOnBus[player] = true
		BusService.addToNext("VampireCount", nil, {
			booked = player,
			happyFloor = Constants.Stay.Happy,
			onBooked = function(reached)
				vampireOnBus[player] = nil
				local now = PlayerData.get(player)
				if reached and now then
					now.stats.tutorialVampire = 1
				elseif player.Parent then
					-- No suite it could get to from the desk (one ready from the street only,
					-- or gone): say so, or it comes back every bus with no reason given.
					Net.fire(
						player,
						"Toast",
						"The Vampire Count couldn't get to a Coffin Suite from your front desk: it will try a later bus",
						"Bad"
					)
				end
			end,
		})
		-- Told to the street once (2026-10-26 review: a suite ready from the street but
		-- not from the desk booked it again every bus, announced to everyone each time).
		if not vampireTold[player] then
			vampireTold[player] = true
			Net.fireAll(
				"Announce",
				`A Legendary Vampire Count is on the next bus, booked at {player.DisplayName}'s hotel!`,
				"Rare"
			)
		end
	end
end

local function tick(player: Player, data: PlayerData.Data)
	local s = step(data)
	bookVampire(player, data)
	-- A tutorial Slime in the desk's line (one sent again after a rejoin or a Hunter's net)
	-- waits there for good, with no patience (GuestService): Gloom points at the desk while it
	-- does (2026-10-26 review: MoveIn said "nearly ready" and pointed at the Book).
	local atDesk = if s ~= "Done" and slimeAtDesk(player) then true else nil
	if player:GetAttribute("TutorialSlimeAtDesk") ~= atDesk then
		player:SetAttribute("TutorialSlimeAtDesk", atDesk)
	end
	if s == "Done" then
		return
	end
	-- The tutorial Slime: the one guest that walks in instead of riding the bus.
	-- A guest lives only in this session, so a player who left before it moved
	-- in finds a new one on coming back, or MoveIn would wait for a friend that
	-- never comes (2026-10-24 evening: a rejoin mid-tutorial). Sent again only
	-- when none is on its way and the last one has had time to walk in.
	if
		WAITS_FOR_SLIME[s]
		and next(data.residents) == nil
		and os.clock() - (slimeSent[player] or -math.huge) > SLIME_RETRY
		and not slimeHere(player)
	then
		slimeSent[player] = os.clock()
		task.delay(Constants.Tutorial.FirstGuestDelay, function()
			if PlayerData.get(player) then
				local g = GuestService.spawnTutorial(player, "Slime", {
					source = "Tutorial",
					happyFloor = Constants.Stay.Happy,
					tutorialFriend = true,
				})
				if g then
					Net.fire(player, "Announce", "A Slime is checking in!", "Bus")
				end
			end
		end)
	end
	if satisfied(player, data, s, stepStarted[player] or os.clock()) then
		local i = table.find(TutorialService.Steps, s) or #TutorialService.Steps
		setStep(player, data, TutorialService.Steps[i + 1] or "Done")
	end
end

function TutorialService.Init()
	Net.on("Tutorial", function(player, what)
		local data = PlayerData.get(player)
		if not data then
			return
		end
		if what == "Skip" then
			setStep(player, data, "Done")
		elseif what == "Next" then
			nextPressed[player] = true
		end
	end)
end

--[[ The hotels the next bus brings Commons (§11 1:45): those in their
	tutorial once the Slime has its room (past CheckIn, so a Common never
	takes the room the Slime walks in to), until `CommonBuses` buses have
	brought them some (BusService counts `tutorialCommonBuses`). ]]
local function commonsWanted(): { Player }
	local out = {}
	for player, data in PlayerData.loaded() do
		local s = step(data)
		if
			s ~= "CheckIn"
			and s ~= "Done"
			and stat(data, "tutorialCommonBuses") < Constants.Tutorial.CommonBuses
		then
			table.insert(out, player)
		end
	end
	return out
end

function TutorialService.Start()
	BusService.setTutorialHotels(commonsWanted)
	PlayerData.onLoaded(function(player, data)
		-- A new profile's "Start" is the first step, stored as such so every
		-- publish of the profile shows the same step.
		if data.tutorial == "Start" or data.tutorial == "Build" then
			data.tutorial = "CheckIn"
		end
		stepStarted[player] = os.clock()
		setBase(player, data)
		player:SetAttribute("Tutorial", step(data))
		-- The goal card's early Coffin Suite lives in BuildService's memory: given again on
		-- every join, or a player who left before building the suite could not type one
		-- on coming back and the Vampire never came (2026-10-26 review).
		if stat(data, "tutorialGoal") == 1 then
			BuildService.tutorialUnlock(player, "CoffinSuite")
		end
	end)
	DevGrant.register("tutorial", function(player, args)
		local data = PlayerData.get(player)
		if data and args[1] then
			setStep(player, data, args[1])
		end
		return `tutorial {data and data.tutorial} goalAt {data and data.stats.tutorialGoalAt} goalBusHere {goalBusHere[player]}`
	end)
	PlayerData.onDeparted(function(player)
		stepStarted[player] = nil
		slimeSent[player] = nil
		nextPressed[player] = nil
		vampireOnBus[player] = nil
		vampireTold[player] = nil
		goalBusHere[player] = nil
		stepBase[player] = nil
	end)
	task.spawn(function()
		while true do
			task.wait(1)
			for player, data in PlayerData.loaded() do
				local ok, err = pcall(tick, player, data)
				if not ok then
					warn(`[tutorial] {player.Name}: {err}`)
				end
			end
		end
	end)
end

return TutorialService
