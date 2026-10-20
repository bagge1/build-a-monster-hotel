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
	the goal card unlocks the Coffin Suite with one free build, and a Vampire
	Count booked to this hotel rides the third bus after it once one stands
	(§11 "the tutorial schedules it").
]]

local ReplicatedStorage = game:GetService("ReplicatedStorage")
local ServerScriptService = game:GetService("ServerScriptService")

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

TutorialService.Steps = {
	"Build",
	"CheckIn",
	"Collect",
	"SecondRoom",
	"Bus",
	"MoveIn",
	"Goal",
	"Clean",
	"Staff",
	"Preview",
	"Done",
}

local stepStarted: { [Player]: number } = {}
local slimeSent: { [Player]: boolean } = {}
local nextPressed: { [Player]: boolean } = {}

local function rooms(data: PlayerData.Data): number
	local n = 0
	for _, rec in data.layout do
		local p = Pieces.get(rec.item)
		if p and p.kind == "Room" then
			n += 1
		end
	end
	return n
end

local function stat(data: PlayerData.Data, key: string): number
	return data.stats[key] or 0
end

local function step(data: PlayerData.Data): string
	return if data.tutorial == "Start" then "Build" else data.tutorial
end

local function satisfied(player: Player, data: PlayerData.Data, s: string, since: number): boolean
	if s == "Build" then
		return rooms(data) >= 1
	elseif s == "CheckIn" then
		return stat(data, "checkIns") >= 1
	elseif s == "Collect" then
		return stat(data, "collects") >= 1
	elseif s == "SecondRoom" then
		return rooms(data) >= 2
	elseif s == "Bus" then
		return stat(data, "pitches") >= 1
			or stat(data, "busGuests") >= 1
			or os.clock() - since > 150
	elseif s == "MoveIn" then
		return next(data.residents) ~= nil
	elseif s == "Goal" then
		return os.clock() - since > 8
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
	if s == "Goal" then
		BuildService.tutorialUnlock(player, "CoffinSuite")
		BuildService.tutorialArea(player)
		data.stats.voucher_CoffinSuite = 1
		data.stats.tutorialGoal = 1
		data.stats.tutorialGoalBus = workspace:GetAttribute("BusIndex") :: number? or 0
	elseif s == "MoveIn" then
		Net.fire(player, "Moment", "OpenBook", {})
	end
	Analytics.step(player, `Tutorial_{s}`)
	StateService.mark(player)
end

local function tick(player: Player, data: PlayerData.Data)
	local s = step(data)
	if s == "Done" then
		-- The scheduled Vampire Count: on the third bus after the goal card ("A
		-- Vampire Count arrives in 3 buses", §11), booked to this hotel once a
		-- Coffin Suite stands vacant for it. Every guest comes by bus (§4.3).
		local busesSince = (workspace:GetAttribute("BusIndex") :: number? or 0)
			- stat(data, "tutorialGoalBus")
		if
			stat(data, "tutorialGoal") == 1
			and stat(data, "tutorialVampire") == 0
			and busesSince >= 2
			and HotelService.vacantFor(player, "VampireCount")
		then
			BusService.addToNext(
				"VampireCount",
				nil,
				{ booked = player, happyFloor = Constants.Stay.Happy }
			)
			data.stats.tutorialVampire = 1
			Net.fireAll(
				"Announce",
				`A Legendary Vampire Count is on the next bus, booked at {player.DisplayName}'s hotel!`,
				"Rare"
			)
		end
		return
	end
	-- The tutorial Slime: the one guest that walks in instead of riding the bus.
	if s == "CheckIn" and not slimeSent[player] then
		slimeSent[player] = true
		task.delay(Constants.Tutorial.FirstGuestDelay, function()
			if PlayerData.get(player) then
				GuestService.spawnTutorial(player, "Slime", {
					source = "Tutorial",
					happyFloor = Constants.Stay.Happy,
					tutorialFriend = true,
				})
				Net.fire(player, "Announce", "A Slime is checking in!", "Bus")
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
			s ~= "Build"
			and s ~= "CheckIn"
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
		if data.tutorial == "Start" then
			data.tutorial = "Build"
		end
		stepStarted[player] = os.clock()
		player:SetAttribute("Tutorial", step(data))
	end)
	DevGrant.register("tutorial", function(player, args)
		local data = PlayerData.get(player)
		if data and args[1] then
			setStep(player, data, args[1])
		end
		return `tutorial {data and data.tutorial} goalBus {data and data.stats.tutorialGoalBus}`
	end)
	PlayerData.onDeparted(function(player)
		stepStarted[player] = nil
		slimeSent[player] = nil
		nextPressed[player] = nil
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
