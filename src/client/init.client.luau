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

-- The server stands the character at its hotel's Spawn, facing the hotel
-- (PlotService `spawnAt`, attributes `SpawnAt`, `Spawned`), but Roblox's
-- camera keeps the way it looked: it is turned to look past the character at
-- the hotel (2026-10-26: a new player saw the street, the hotel behind them).
local function faceHotel()
	local at = player:GetAttribute("SpawnAt")
	local camera = workspace.CurrentCamera
	if typeof(at) == "CFrame" and camera then
		local stand = at.Position + Vector3.new(0, 3, 0)
		camera.CFrame = CFrame.lookAt(
			stand - at.LookVector * 14 + Vector3.new(0, 6, 0),
			stand + at.LookVector * 6
		)
	end
end
player:GetAttributeChangedSignal("Spawned"):Connect(faceHotel)
faceHotel() -- the first spawn may have come before this script

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
	require(Client.ExpeditionPanel) :: any, -- the Expedition board, its Collect pop-up, the Residents button's timer (A.11.2)
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
