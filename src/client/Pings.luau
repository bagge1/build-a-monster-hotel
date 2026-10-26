--!strict
--[[
	Quick pings (GDD §7: co-play without chat): a few set phrases a player can
	show over their head with one tap. The server shows them to everyone
	(`SocialService`); this is the menu. The server words "Need a room": it
	names the room the rarest guest on the street wants ("Need a Coffin
	Suite!"), so the button only asks for it.
]]

local ReplicatedStorage = game:GetService("ReplicatedStorage")
local UserInputService = game:GetService("UserInputService")

local Net = require(ReplicatedStorage.Shared.Net)
local Controls = require(script.Parent.Controls)
local Ui = require(script.Parent.Ui)
local Hud = require(script.Parent.Hud)

local Pings = {}

local ORDER = {
	{ "Hello", "Hello, neighbour!" },
	{ "Visit", "Come visit my hotel!" },
	{ "NeedRoom", "Need a room for that guest!" },
	{ "Pitching", "Pitching!" },
	{ "Hunters", "Hunters coming!" },
	{ "Thanks", "Thanks!" },
}

local menu: Frame

function Pings.Init()
	local gui = Ui.screen("Panels", 6)
	menu = Ui.panel(
		gui,
		"PingMenu",
		UDim2.fromOffset(250, 6 * 50 + 16),
		UDim2.new(1, -130, 0, 56),
		Vector2.new(1, 0)
	)
	menu.Active = true -- a tap between its phrases never reaches a HUD button behind it
	menu.Visible = false
	-- The gamepad (§11): the first phrase selected when it opens, ButtonB closes it.
	Controls.panel(menu, function()
		menu.Visible = false
	end)
	Ui.padding(menu, 8)
	local grid = Instance.new("UIGridLayout")
	grid.CellPadding = UDim2.fromOffset(6, 6)
	grid.SortOrder = Enum.SortOrder.LayoutOrder
	grid.Parent = menu
	-- A short screen (a phone in landscape) takes the phrases in two columns,
	-- so the menu stays above the bottom edge (TESTRUN, the phone). It opens
	-- left of the HUD's right column, which is two buttons wide there, so the
	-- Ping button that shuts it is never under it (2026-10-24: it was).
	local function fit()
		local camera = workspace.CurrentCamera
		local short = camera ~= nil and camera.ViewportSize.Y < 500
		local columns = if short then 2 else 1
		local rows = math.ceil(#ORDER / columns)
		grid.CellSize = UDim2.fromOffset(234, 44)
		menu.Size = UDim2.fromOffset(columns * 240 + 10, rows * 50 + 16)
		-- On a computer the column's buttons sit at its foot, under Roblox's
		-- player list (Hud's `fit`), and the menu opens down there beside them.
		local foot = not short and not UserInputService.TouchEnabled
		menu.AnchorPoint = if foot then Vector2.new(1, 1) else Vector2.new(1, 0)
		menu.Position = if foot
			then UDim2.new(1, -(10 + 110 + 10), 1, -94)
			else UDim2.new(1, -(10 + (if short then 226 else 110) + 10), 0, 56)
	end
	fit()
	workspace.CurrentCamera:GetPropertyChangedSignal("ViewportSize"):Connect(fit)
	for i, entry in ORDER do
		local b = Ui.button(menu, entry[1], entry[2], UDim2.new(1, 0, 0, 44), function()
			Net.send("Ping", entry[1])
			menu.Visible = false
		end)
		b.LayoutOrder = i
		b.TextSize = 16
	end
end

function Pings.Start()
	Hud.button("PingButton", "💬 Ping", "Right", function()
		menu.Visible = not menu.Visible
	end, 4)
end

return Pings
