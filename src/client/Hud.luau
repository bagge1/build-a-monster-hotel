--!strict
--[[
	The HUD (UI.md, "Hud"): the wallet, the till, the rating and Moon Shards
	along the top; the menu buttons down the left and right edges (never the
	bottom corners, GDD §11); toasts, the street's announcements, and the
	floating "+$" over a tip or a collected till.

	Panels add their own button with `Hud.button(name, text, side, onClick)`.
	Every number is read from the player's attributes (`PlayerData.publish`),
	a copy for drawing.
]]

local Players = game:GetService("Players")
local ReplicatedStorage = game:GetService("ReplicatedStorage")
local TweenService = game:GetService("TweenService")

local Format = require(ReplicatedStorage.Shared.Format)
local Net = require(ReplicatedStorage.Shared.Net)
local Ui = require(script.Parent.Ui)
local UiImages = require(script.Parent.UiImages)

local Hud = {}

local me = Players.LocalPlayer
local gui: ScreenGui
local left: Frame
local right: Frame
local toasts: Frame
local banner: TextLabel

local REFUSALS: { [string]: string } = {
	Cash = "Not enough cash",
	OutOfBounds = "That doesn't fit on the plot",
	Overlap = "Something is already there",
	Reserved = "Keep the lobby and stairs clear",
	DoorBlocked = "The door would open into a wall",
	DoorUnreachable = "Guests couldn't reach that door",
	CutsOff = "That would block another room's door",
	NoFloor = "Build that floor first",
	Busy = "A guest is using that room",
	MaxTier = "Already the top tier",
	FloorCap = "No more floors for now",
	Location = "Not at this location",
	Locked = "Not unlocked yet",
}

function Hud.toast(text: string, colour: Color3?)
	if not toasts then
		return
	end
	local t = Ui.label(toasts, "Toast", text, UDim2.new(1, 0, 0, 34), 20, colour or Ui.Colour.Text)
	t.TextXAlignment = Enum.TextXAlignment.Center
	t.BackgroundColor3 = Ui.Colour.Ink
	t.BackgroundTransparency = 0.25
	Ui.corner(t, 10)
	task.delay(3.5, function()
		local tw = TweenService:Create(
			t,
			TweenInfo.new(0.4),
			{ TextTransparency = 1, BackgroundTransparency = 1 }
		)
		tw:Play()
		tw.Completed:Wait()
		t:Destroy()
	end)
end

function Hud.announce(text: string, kind: string?)
	if not banner then
		return
	end
	banner.Text = text
	banner.TextColor3 = if kind == "Rare"
		then Ui.Colour.Gold
		elseif kind == "Hunter" then Ui.Colour.Bad
		else Ui.Colour.Moon
	banner.Visible = true
	local stamp = os.clock()
	banner:SetAttribute("Stamp", stamp)
	task.delay(7, function()
		if banner:GetAttribute("Stamp") == stamp then
			banner.Visible = false
		end
	end)
end

-- Floating "+$" over a world position (a BillboardGui, so it stays put in the world).
function Hud.pop(amount: number, at: Vector3?, kind: string?)
	if amount <= 0 then
		return
	end
	local anchor = Instance.new("Part")
	anchor.Anchored = true
	anchor.CanCollide = false
	anchor.CanQuery = false
	anchor.CanTouch = false
	anchor.Transparency = 1
	anchor.Size = Vector3.one * 0.2
	local character = me.Character
	local pos = at
		or (
			if character then character:GetPivot().Position + Vector3.new(0, 3, 0) else Vector3.zero
		)
	anchor.CFrame = CFrame.new(pos + Vector3.new(0, 2, 0))
	anchor.Parent = workspace
	local bb = Instance.new("BillboardGui")
	bb.Size = UDim2.fromOffset(160, 50)
	bb.AlwaysOnTop = true
	bb.LightInfluence = 0
	bb.Adornee = anchor
	local l = Ui.label(
		bb,
		"Amount",
		"+" .. Format.cash(amount),
		UDim2.fromScale(1, 1),
		28,
		if kind == "Collect" then Ui.Colour.Gold else Ui.Colour.Good
	)
	l.TextXAlignment = Enum.TextXAlignment.Center
	l.TextStrokeTransparency = 0.3
	bb.Parent = anchor
	TweenService
		:Create(anchor, TweenInfo.new(1.4), { CFrame = anchor.CFrame + Vector3.new(0, 4, 0) })
		:Play()
	TweenService:Create(l, TweenInfo.new(1.4), { TextTransparency = 1, TextStrokeTransparency = 1 })
		:Play()
	task.delay(1.5, function()
		anchor:Destroy()
	end)
end

-- The drawn icon (UiImages) and its tint for each menu button; a button
-- without one keeps its text's own emoji.
local ICONS: { [string]: { string | Color3 } } = {
	BuildButton = { "Icon_Build", Ui.Colour.Pumpkin },
	RatingButton = { "Icon_Rating", Ui.Colour.Gold },
	ResidentsButton = { "Icon_Residents", Ui.Colour.Teal },
	BookButton = { "Icon_Book", Color3.fromRGB(200, 150, 255) },
	ProgressionButton = { "Icon_Moon", Ui.Colour.Moon },
	StoreButton = { "Icon_Store", Ui.Colour.Good },
	DailyButton = { "Icon_Daily", Color3.fromRGB(255, 130, 160) },
}

-- A menu button on the left or right edge, in `order`.
function Hud.button(
	name: string,
	text: string,
	side: "Left" | "Right",
	onClick: () -> (),
	order: number?
): TextButton
	local parent = if side == "Left" then left else right
	local icon = ICONS[name]
	local id = icon and UiImages[icon[1] :: string]
	if id and id ~= "" then
		text = (string.gsub(text, "^[^%w]+", ""))
	end
	local b = Ui.button(parent, name, text, UDim2.fromOffset(110, 44), onClick)
	b.LayoutOrder = order or 0
	if id and id ~= "" then
		local img = Instance.new("ImageLabel")
		img.Name = "Icon"
		img.BackgroundTransparency = 1
		img.Image = id
		img.ImageColor3 = icon[2] :: Color3
		img.Size = UDim2.fromOffset(34, 34)
		img.Position = UDim2.new(0, -30, 0.5, -17) -- the padding below moves children too
		img.Parent = b
		local pad = Instance.new("UIPadding")
		pad.PaddingLeft = UDim.new(0, 34)
		pad.Parent = b
	end
	return b
end

local function stat(parent: Frame, name: string, order: number, colour: Color3): TextLabel
	local box = Ui.frame(parent, name, UDim2.fromOffset(130, 40), nil, Ui.Colour.Ink)
	box.BackgroundTransparency = 0.2
	box.LayoutOrder = order
	Ui.corner(box, 12)
	Ui.stroke(box, colour, 2)
	local l = Ui.label(box, "Value", "", UDim2.fromScale(1, 1), 22, colour)
	l.TextXAlignment = Enum.TextXAlignment.Center
	return l
end

function Hud.Init()
	gui = Ui.screen("Hud", 1)
	local top = Ui.frame(gui, "Top", UDim2.new(1, 0, 0, 44), UDim2.fromOffset(0, 6))
	top.BackgroundTransparency = 1
	Ui.list(top, Enum.FillDirection.Horizontal, 8, Enum.HorizontalAlignment.Center)
	local cash = stat(top, "Cash", 1, Ui.Colour.Good)
	local till = stat(top, "Till", 2, Ui.Colour.Gold)
	local rating = stat(top, "Rating", 3, Ui.Colour.Pumpkin)
	local shards = stat(top, "Shards", 4, Ui.Colour.Moon)

	local function refresh()
		cash.Text = Format.cash(me:GetAttribute("Cash") :: number? or 0)
		till.Text = "Till " .. Format.cash(me:GetAttribute("Till") :: number? or 0)
		rating.Text = Format.stars(me:GetAttribute("Rating") :: number? or 1)
		shards.Text = "🌙 " .. Format.number(me:GetAttribute("Shards") :: number? or 0)
		shards.Parent.Visible = (me:GetAttribute("Shards") :: number? or 0) > 0
			or (me:GetAttribute("Location") :: number? or 1) > 1
	end
	for _, a in { "Cash", "Till", "Rating", "Shards", "Location" } do
		me:GetAttributeChangedSignal(a):Connect(refresh)
	end
	refresh()

	-- The menu columns start under the top bar and stop well above the bottom
	-- corners, where Roblox puts the thumbstick and jump on a phone (§11).
	left = Ui.frame(gui, "Left", UDim2.new(0, 110, 1, -150), UDim2.fromOffset(10, 56))
	left.BackgroundTransparency = 1
	Ui.list(left, Enum.FillDirection.Vertical, 6)
	right = Ui.frame(gui, "Right", UDim2.new(0, 110, 1, -150), UDim2.new(1, -10, 0, 56))
	right.AnchorPoint = Vector2.new(1, 0)
	right.BackgroundTransparency = 1
	Ui.list(right, Enum.FillDirection.Vertical, 6, Enum.HorizontalAlignment.Right)
	-- A short screen (a phone in landscape) takes the right column in two
	-- columns, so it stops above the jump button (§11).
	local function fit()
		local camera = workspace.CurrentCamera
		local short = camera ~= nil and camera.ViewportSize.Y < 500
		local list = right:FindFirstChildOfClass("UIListLayout")
		local grid = right:FindFirstChildOfClass("UIGridLayout")
		if short and list then
			list:Destroy()
			local g = Instance.new("UIGridLayout")
			g.CellSize = UDim2.fromOffset(110, 44)
			g.CellPadding = UDim2.fromOffset(6, 6)
			g.SortOrder = Enum.SortOrder.LayoutOrder
			g.HorizontalAlignment = Enum.HorizontalAlignment.Right
			g.Parent = right
			right.Size = UDim2.new(0, 226, 1, -150)
		elseif not short and grid then
			grid:Destroy()
			Ui.list(right, Enum.FillDirection.Vertical, 6, Enum.HorizontalAlignment.Right)
			right.Size = UDim2.new(0, 110, 1, -150)
		end
	end
	fit()
	if workspace.CurrentCamera then
		workspace.CurrentCamera:GetPropertyChangedSignal("ViewportSize"):Connect(fit)
	end

	toasts = Ui.frame(gui, "Toasts", UDim2.fromOffset(420, 200), UDim2.new(0.5, 0, 0, 110))
	toasts.AnchorPoint = Vector2.new(0.5, 0)
	toasts.BackgroundTransparency = 1
	Ui.list(toasts, Enum.FillDirection.Vertical, 6, Enum.HorizontalAlignment.Center)

	banner = Ui.label(gui, "Banner", "", UDim2.new(0.8, 0, 0, 50), 28, Ui.Colour.Moon)
	banner.AnchorPoint = Vector2.new(0.5, 0)
	banner.Position = UDim2.new(0.5, 0, 0, 192) -- under the bus countdown and Gloom's bubble
	banner.TextXAlignment = Enum.TextXAlignment.Center
	banner.TextStrokeTransparency = 0.2
	banner.Visible = false
end

function Hud.Start()
	Net.listen("Toast", function(text: string, kind: string?)
		Hud.toast(
			text,
			if kind == "Unlock" then Ui.Colour.Gold elseif kind == "Bad" then Ui.Colour.Bad else nil
		)
	end)
	Net.listen("Announce", function(text: string, kind: string?)
		Hud.announce(text, kind)
	end)
	Net.listen("Pop", function(amount: number, at: Vector3?, kind: string?)
		Hud.pop(amount, at, kind)
	end)
	Net.listen("Refused", function(_remote: string, reason: string)
		Hud.toast(REFUSALS[reason] or reason, Ui.Colour.Bad)
	end)
end

return Hud
