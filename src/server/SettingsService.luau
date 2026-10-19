--!strict
--[[
	A player's settings (GDD §9 "settings: music, SFX, low graphics"), kept in
	the profile so they follow the player. The client applies them; this only
	stores what the client asks for, for the keys that exist.
]]

local ReplicatedStorage = game:GetService("ReplicatedStorage")
local ServerScriptService = game:GetService("ServerScriptService")

local Net = require(ReplicatedStorage.Shared.Net)
local PlayerData = require(ServerScriptService.Server.PlayerData)
local StateService = require(ServerScriptService.Server.StateService)

local SettingsService = {}

local KEYS = { music = true, sfx = true, lowGraphics = true }

function SettingsService.Init()
	Net.on("Settings", function(player, key, value)
		local data = PlayerData.get(player)
		if data and KEYS[key] then
			data.settings[key] = value
			StateService.mark(player)
		end
	end)
end

function SettingsService.Start()
	StateService.provide("settings", function(_, data)
		return {
			music = data.settings.music ~= false,
			sfx = data.settings.sfx ~= false,
			lowGraphics = data.settings.lowGraphics == true,
		}
	end)
end

return SettingsService
