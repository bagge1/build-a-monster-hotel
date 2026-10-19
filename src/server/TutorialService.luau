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

	What it arranges: walk-ins wait until the tutorial Slime has come (§11
	0:30); that Slime's stay counts as happy and it needs 1 friendship (§6.3);
	the goal card unlocks the Coffin Suite with one free build and sends a
	Vampire Count once one stands (§11 "the tutorial schedules it").
]]

local ReplicatedStorage = game:GetService("ReplicatedStorage")
local ServerScriptService = game:GetService("ServerScriptService")

local Constants = require(ReplicatedStorage.Shared.Constants)
local Net = require(ReplicatedStorage.Shared.Net)
local Pieces = require(ReplicatedStorage.Shared.Pieces)
local PlayerData = require(ServerScriptService.Server.PlayerData)
local BuildService = require(ServerScriptService.Server.BuildService)
local GuestService = require(ServerScriptService.Server.GuestService)
local StateService = require(ServerScriptService.Server.StateService)
local Analytics = require(ServerScriptService.Server.Analytics)

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
	if s ~= "Build" and s ~= "CheckIn" then
		GuestService.setWalkIns(player, true)
	end
	if s == "Goal" then
		BuildService.tutorialUnlock(player, "CoffinSuite")
		data.stats.voucher_CoffinSuite = 1
		data.stats.tutorialGoal = 1
	elseif s == "MoveIn" then
		Net.fire(player, "Moment", "OpenBook", {})
	end
	Analytics.step(player, `Tutorial_{s}`)
	StateService.mark(player)
end

local function tick(player: Player, data: PlayerData.Data)
	local s = step(data)
	if s == "Done" then
		-- The scheduled Vampire Count, once a Coffin Suite stands (§11 10:00–15:00).
		if stat(data, "tutorialGoal") == 1 and stat(data, "tutorialVampire") == 0 then
			for _, rec in data.layout do
				if rec.item == "CoffinSuite" then
					local g = GuestService.spawnWalkIn(
						player,
						"VampireCount",
						{ source = "Tutorial", happyFloor = Constants.Stay.Happy }
					)
					if g then
						data.stats.tutorialVampire = 1
						Net.fireAll(
							"Announce",
							`A Legendary Vampire Count is arriving at {player.DisplayName}'s hotel!`,
							"Rare"
						)
					end
					break
				end
			end
		end
		return
	end
	-- The tutorial Slime: walk-ins wait for it.
	if s == "CheckIn" and not slimeSent[player] then
		slimeSent[player] = true
		task.delay(Constants.WalkIn.TutorialDelay, function()
			if PlayerData.get(player) then
				GuestService.spawnWalkIn(
					player,
					"Slime",
					{ source = "Tutorial", happyFloor = Constants.Stay.Happy }
				)
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

function TutorialService.Start()
	PlayerData.onLoaded(function(player, data)
		-- A new profile's "Start" is the first step, stored as such so every
		-- publish of the profile shows the same step.
		if data.tutorial == "Start" then
			data.tutorial = "Build"
		end
		stepStarted[player] = os.clock()
		if step(data) == "Build" or step(data) == "CheckIn" then
			GuestService.setWalkIns(player, false)
		end
		player:SetAttribute("Tutorial", step(data))
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
