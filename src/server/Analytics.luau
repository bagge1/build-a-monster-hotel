--!strict
--[[
	The analytics funnel (GDD §13.5, §15.4): where new players drop off.

	The onboarding funnel is Gloom's steps, numbered in order, through
	`AnalyticsService:LogOnboardingFunnelStepEvent`. The "firsts" §13.5 lists
	(join, first room, first guest, first bus, first move-in, first themed
	room, first rare, session end, rebirth) are custom events, each "first"
	logged once per player (remembered in the profile's `funnel`).

	Every call is in a pcall: analytics never stops play, and in Studio the
	service may refuse.
]]

local AnalyticsService = game:GetService("AnalyticsService")
local ServerScriptService = game:GetService("ServerScriptService")

local PlayerData = require(ServerScriptService.Server.PlayerData)

local Analytics = {}

local ONBOARDING = {
	Tutorial_Build = 1,
	Tutorial_CheckIn = 2,
	Tutorial_Collect = 3,
	Tutorial_SecondRoom = 4,
	Tutorial_Bus = 5,
	Tutorial_MoveIn = 6,
	Tutorial_Goal = 7,
	Tutorial_Clean = 8,
	Tutorial_Staff = 9,
	Tutorial_Preview = 10,
	Tutorial_Done = 11,
}

-- A tutorial step reached (logged once per player).
function Analytics.step(player: Player, name: string)
	local n = ONBOARDING[name]
	if n then
		Analytics.first(player, name, function()
			AnalyticsService:LogOnboardingFunnelStepEvent(player, n, name)
		end)
	end
end

-- Runs `log` the first time `key` happens for this player.
function Analytics.first(player: Player, key: string, log: (() -> ())?)
	local data = PlayerData.get(player)
	if not data or data.funnel[key] then
		return
	end
	data.funnel[key] = true
	pcall(log or function()
		AnalyticsService:LogCustomEvent(player, key, 1)
	end)
end

-- An event that may happen many times.
function Analytics.event(player: Player, name: string, value: number?)
	pcall(function()
		AnalyticsService:LogCustomEvent(player, name, value or 1)
	end)
end

function Analytics.Init() end

function Analytics.Start()
	PlayerData.onLoaded(function(player)
		Analytics.first(player, "Join")
		Analytics.event(player, "Session")
	end)
	PlayerData.onRelease(function(player, data)
		Analytics.event(player, "SessionEnd", data.stats.stays or 0)
	end)
	-- The firsts of §13.5, from the systems that see them (required here, at
	-- Start, so none of them has to know about analytics).
	local Server = ServerScriptService.Server
	local ReplicatedStorage = game:GetService("ReplicatedStorage")
	local Species = require(ReplicatedStorage.Shared.Species) :: any
	local BuildService = require(Server.BuildService) :: any
	local GuestService = require(Server.GuestService) :: any
	local ResidentService = require(Server.ResidentService) :: any
	local ProgressionService = require(Server.ProgressionService) :: any
	BuildService.onChanged(function(player, what)
		local data = PlayerData.get(player)
		if what == "Place" and data then
			Analytics.first(player, "FirstRoom")
			for _, rec in data.layout do
				if rec.item ~= "StandardRoom" then
					Analytics.first(player, "FirstThemedRoom")
				end
			end
		end
	end)
	GuestService.onCheckIn(function(player, g)
		Analytics.first(player, "FirstGuest")
		if g.source == "Bus" then
			Analytics.first(player, "FirstBusGuest")
		end
		local sp = Species.get(g.species)
		if sp and (sp.rarity ~= "Common" and sp.rarity ~= "Uncommon") then
			Analytics.first(player, "FirstRare")
		end
	end)
	ResidentService.onMoveIn(function(player)
		Analytics.first(player, "FirstMoveIn")
	end)
	ProgressionService.onRebirth(function(player, from)
		Analytics.event(player, "Rebirth", from)
	end)
end

return Analytics
