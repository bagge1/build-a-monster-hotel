--!strict
--[[
	Client entry point: the same Init()/Start() pattern as the server, each
	phase in a pcall, so one failing controller never stops the rest.
]]

local Client = script

-- A phone plays in landscape, either way up: the whole interface is laid out
-- and measured for it (UI.md), and upright its top row ran off both edges
-- (2026-10-25). Set here, so no project file changes; set again whenever
-- Roblox puts StarterGui's back (it did, just after this script started).
local player = game:GetService("Players").LocalPlayer
local playerGui = player:WaitForChild("PlayerGui") :: PlayerGui
local function landscape()
	if playerGui.ScreenOrientation ~= Enum.ScreenOrientation.LandscapeSensor then
		playerGui.ScreenOrientation = Enum.ScreenOrientation.LandscapeSensor
	end
end
landscape()
playerGui:GetPropertyChangedSignal("ScreenOrientation"):Connect(landscape)
player.CharacterAdded:Connect(landscape)

local systems: { { Init: () -> (), Start: () -> () } } = {
	require(Client.State) :: any, -- first: panels read what it receives
	require(Client.Controls) :: any, -- the gamepad's back and menu buttons (GDD §11)
	require(Client.Hud) :: any, -- before every panel that adds a button to it
	require(Client.PromptFilter) :: any,
	require(Client.GuestRenderer) :: any,
	require(Client.BuildController) :: any,
	require(Client.BusRenderer) :: any,
	require(Client.ForestRenderer) :: any, -- the trees round the street, client-only
	require(Client.RatingPanel) :: any,
	require(Client.ResidentRenderer) :: any,
	require(Client.MonsterAnimator) :: any, -- the rigged monsters' bones (GDD §12)
	require(Client.CollectionPanels) :: any,
	require(Client.ProgressionPanel) :: any,
	require(Client.LivePanels) :: any,
	require(Client.ShowcasePanel) :: any, -- the showcase (A.11.4)
	require(Client.VipPanel) :: any, -- the VIP ledger (A.11.1)
	require(Client.FindsPanel) :: any, -- a rare find's pop-up (A.11.3)
	require(Client.HunterRenderer) :: any,
	require(Client.Sound) :: any,
	require(Client.Pings) :: any,
	require(Client.EventPanel) :: any,
	require(Client.Effects) :: any,
	require(Client.Lod) :: any,
	require(Client.TutorialController) :: any, -- last: it points at every other panel's buttons
}

local function run(phase: string)
	for i, system in systems do
		local ok, err = pcall((system :: any)[phase])
		if not ok then
			warn(`[client] system {i} {phase} failed: {err}`)
		end
	end
end

run("Init")
run("Start")
