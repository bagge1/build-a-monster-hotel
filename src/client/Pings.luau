--!strict
--[[
	Quick pings (GDD §7: co-play without chat): a few set phrases a player can
	show over their head with one tap. The server shows them to everyone
	(`SocialService`); this is the menu. The server words "Need a room": it
	names the room the rarest guest on the street wants ("Need a Coffin
	Suite!"), so the button only asks for it.
]]

local ReplicatedStorage = game:GetService("ReplicatedStorage")

local Net = require(ReplicatedStorage.Shared.Net)
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
	menu.Visible = false
	Ui.padding(menu, 8)
	local grid = Instance.new("UIGridLayout")
	grid.CellPadding = UDim2.fromOffset(6, 6)
	grid.SortOrder = Enum.SortOrder.LayoutOrder
	grid.Parent = menu
	-- A short screen (a phone in landscape) takes the phrases in two columns,
	-- so the menu stays above the bottom edge (TESTRUN, the phone).
	local function fit()
		local camera = workspace.CurrentCamera
		local columns = if camera and camera.ViewportSize.Y < 500 then 2 else 1
		local rows = math.ceil(#ORDER / columns)
		grid.CellSize = UDim2.fromOffset(234, 44)
		menu.Size = UDim2.fromOffset(columns * 240 + 10, rows * 50 + 16)
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
