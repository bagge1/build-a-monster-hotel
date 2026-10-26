--!strict
--[[
	The game's sound (GDD §12): the harpsichord music, a ding when cash comes
	in, a bell at the desk, a horn when the bus arrives, a fanfare for a rare
	check-in or a move-in. Played locally, from what the server says happened
	(`Pop`, `Moment`, `Announce`), and only when the player's settings allow
	(`settings` state section, the Settings panel).

	Also the Settings panel itself (music, effects, low graphics), and the low
	graphics tier: shadows off and other hotels' lamps dark, never anything a
	player acts on (D:\Roblox\playbook\PATTERNS.md, "Device tier").
]]

local Lighting = game:GetService("Lighting")
local Players = game:GetService("Players")
local ReplicatedStorage = game:GetService("ReplicatedStorage")
local SoundService = game:GetService("SoundService")

local Audio = require(ReplicatedStorage.Shared.Audio)
local Net = require(ReplicatedStorage.Shared.Net)
local Species = require(ReplicatedStorage.Shared.Species)
local State = require(script.Parent.State)
local Ui = require(script.Parent.Ui)
local Hud = require(script.Parent.Hud)

local Sound = {}

local me = Players.LocalPlayer
local folder: Folder
local music: Sound
local sfxOn = true
local window: Frame
local body: Frame

local function settings(): any
	return State.data.settings or { music = true, sfx = true, lowGraphics = false }
end

function Sound.play(id: string, volume: number?)
	if not sfxOn then
		return
	end
	local s = Instance.new("Sound")
	s.SoundId = id
	s.Volume = volume or 0.6
	s.Parent = folder
	s:Play()
	s.Ended:Connect(function()
		s:Destroy()
	end)
	task.delay(10, function()
		if s.Parent then
			s:Destroy()
		end
	end)
end

--[[ Low graphics darkens the lamps of the hotels this player is not playing, and turned off it
	lights again only the ones it darkened (2026-10-26: run on every state send, it set every lamp
	in every plot, lighting the Expedition board's dark lantern, HotelKit.lightBoard, and walked
	every plot each send). The lamps among a plot's `Pieces` are Lod's, which reads `LowGraphics`. ]]
local darkened: { [PointLight]: boolean } = setmetatable({}, { __mode = "k" }) :: any
local appliedLow: boolean? = nil

local function darken()
	local mine = me:GetAttribute("Plot")
	local plots = workspace:FindFirstChild("Plots")
	for _, plot in (if plots then plots:GetChildren() else {}) do
		local pieces = plot:FindFirstChild("Pieces")
		if plot:GetAttribute("Index") ~= mine then
			for _, d in plot:GetDescendants() do
				if
					d:IsA("PointLight")
					and d.Enabled
					and not (pieces and d:IsDescendantOf(pieces))
				then
					d.Enabled = false
					darkened[d] = true
				end
			end
		end
	end
end

local function applyLowGraphics(low: boolean)
	appliedLow = low
	me:SetAttribute("LowGraphics", low)
	Lighting.GlobalShadows = not low
	for light in darkened do
		light.Enabled = true
	end
	table.clear(darkened)
	if low then
		darken()
	end
end

local function apply()
	local s = settings()
	sfxOn = s.sfx
	if s.music and not music.IsPlaying then
		music:Play()
	elseif not s.music and music.IsPlaying then
		music:Stop()
	end
	if s.lowGraphics ~= appliedLow then
		applyLowGraphics(s.lowGraphics)
	end
end

local function drawSettings()
	for _, c in body:GetChildren() do
		if not c:IsA("UIListLayout") then
			c:Destroy()
		end
	end
	local s = settings()
	for i, entry in
		{ { "music", "Music" }, { "sfx", "Sound effects" }, { "lowGraphics", "Low graphics" } }
	do
		local key, label = entry[1], entry[2]
		local on = s[key] == true
		local b = Ui.button(
			body,
			key,
			`{label}: {if on then "On" else "Off"}`,
			UDim2.new(1, 0, 0, 48),
			function()
				Net.send("Settings", key, not on)
			end,
			if on then Ui.Colour.Teal else Ui.Colour.Panel
		)
		b.LayoutOrder = i
	end
end

function Sound.Init()
	folder = Instance.new("Folder")
	folder.Name = "GameSounds"
	folder.Parent = SoundService
	music = Instance.new("Sound")
	music.Name = "Music"
	music.SoundId = Audio.Music
	music.Looped = true
	music.Volume = 0.25
	music.Parent = folder
	local gui = Ui.screen("Panels", 6)
	window, body =
		Ui.window(gui, "SettingsPanel", "Settings", UDim2.fromScale(0.35, 0.45), nil, true)
	Ui.list(body, Enum.FillDirection.Vertical, 8)
end

function Sound.Start()
	Hud.button("SettingsButton", "⚙ Settings", "Right", function()
		window.Visible = not window.Visible
		if window.Visible then
			drawSettings()
		end
	end, 9)
	State.changed:Connect(function()
		apply()
		if window.Visible then
			drawSettings()
		end
	end)
	Net.listen("Pop", function(_amount: number, _at: Vector3?, kind: string?)
		Sound.play(Audio.Cash, if kind == "Collect" then 0.8 else 0.4)
	end)
	Net.listen("Moment", function(kind: string, data: any)
		if kind == "CheckIn" then
			local sp = data and Species.get(data.species)
			if
				sp and (sp.rarity == "Legendary" or sp.rarity == "Mythic" or sp.rarity == "Epic")
			then
				Sound.play(Audio.Fanfare, 0.7)
			else
				Sound.play(Audio.Bell, 0.5)
			end
		elseif kind == "MoveIn" then
			Sound.play(Audio.Fanfare, 0.7)
		end
	end)
	Net.listen("Announce", function(_text: string, kind: string?)
		if kind == "Bus" then
			Sound.play(Audio.BusHorn, 0.5)
		end
	end)
	-- Low graphics also covers hotels rebuilt later.
	local plots = workspace:WaitForChild("Plots")
	local pending = false
	plots.DescendantAdded:Connect(function(d)
		if d:IsA("PointLight") and me:GetAttribute("LowGraphics") and not pending then
			pending = true
			task.delay(0.5, function()
				pending = false
				if appliedLow then
					darken()
				end
			end)
		end
	end)
	-- A Travel makes another plot this player's: its lamps lit again, the one left darkened.
	me:GetAttributeChangedSignal("Plot"):Connect(function()
		if appliedLow then
			applyLowGraphics(true)
		end
	end)
	apply()
end

return Sound
