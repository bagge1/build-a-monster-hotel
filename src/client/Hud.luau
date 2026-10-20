--!strict
--[[
	The HUD (UI.md, "Hud"): the wallet, the till, the rating and Moon Shards
	along the top; the menu buttons down the left and right edges (never the
	bottom corners, GDD §11); toasts, the street's announcements, and the
	floating "+$" over a tip or a collected till (and staff's "✓" at a door).

	Panels add their own button with `Hud.button(name, text, side, onClick)`.
	Every number is read from the player's attributes (`PlayerData.publish`),
	a copy for drawing.

	The gamepad (§11): ButtonY selects the first menu button (the left
	column's top, else the right's) and lets it go again; the buttons' keys
	are input actions (`Controls`, UI.md "Gamepad").
]]

local GuiService = game:GetService("GuiService")
local Players = game:GetService("Players")
local ReplicatedStorage = game:GetService("ReplicatedStorage")
local TweenService = game:GetService("TweenService")

local Format = require(ReplicatedStorage.Shared.Format)
local Net = require(ReplicatedStorage.Shared.Net)
local Controls = require(script.Parent.Controls)
local Ui = require(script.Parent.Ui)
local UiImages = require(script.Parent.UiImages)

local Hud = {}

local me = Players.LocalPlayer
local gui: ScreenGui
local left: Frame
local right: Frame
local toasts: Frame
local banner: TextLabel
local keys: InputContext -- the menu buttons' keys
local columnTop = 56 -- where the menu columns start (placeTop)

local REFUSALS: { [string]: string } = {
	Cash = "Not enough cash",
	OutOfBounds = "That doesn't fit on the plot",
	Overlap = "Something is already there",
	DoorBlocked = "The door would open into a wall",
	DoorUnreachable = "Guests couldn't reach that door",
	CutsOff = "That would cut a door off from the entrance",
	NoFloor = "Build that floor first",
	Busy = "A guest is using that room",
	MaxTier = "Already the top tier",
	FloorCap = "No more floors for now",
	-- Free building (§5.4)
	Tile = "Buy that tile of the plot first",
	Entrance = "Keep the entrance clear",
	Decor = "Move the decor out of the way first",
	NoFloorAbove = "A stair needs a floor above it",
	DeskFloor = "The desk stays on floor 1",
	LastDesk = "The hotel needs a desk: move it instead",
	NoMirror = "Can't be flipped yet: its mirror image isn't modelled",
	NotWall = "Windows go on an outer wall",
	Wall = "That hangs on a room's wall",
	Outside = "That doesn't fit in the room",
	Across = "Decor can't stand across a wall",
	Doorway = "Keep the doorway clear",
	Furniture = "The room's own furniture is there",
	NoWall = "Put its back against a wall",
	Owned = "You own that tile already",
	NotNext = "Buy a tile next to yours first",
	Unknown = "That isn't there",
	Location = "Not at this location",
	Locked = "Not unlocked yet",
}

-- A refusal's words (the server's `Refused` reasons, and the build mode's ghost).
function Hud.refusal(reason: string): string
	return REFUSALS[reason] or reason
end

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

-- Floating text that rises and fades over a world position (or over the player): a tip's
-- "+$", staff's "✓" (a BillboardGui, so it stays put in the world).
function Hud.float(text: string, at: Vector3?, colour: Color3)
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
	bb.Size = UDim2.fromOffset(240, 50) -- wide enough for "✓ Room Service"
	bb.AlwaysOnTop = true
	bb.LightInfluence = 0
	bb.Adornee = anchor
	local l = Ui.label(bb, "Amount", text, UDim2.fromScale(1, 1), 28, colour)
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

function Hud.pop(amount: number, at: Vector3?, kind: string?)
	if amount <= 0 then
		return
	end
	Hud.float(
		"+" .. Format.cash(amount),
		at,
		if kind == "Collect" then Ui.Colour.Gold else Ui.Colour.Good
	)
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

-- A key for a menu button (his ask, 2026-10-19). It works only while its
-- button is shown, so build mode, which hides the column, keeps R for
-- rotating a piece (BuildController closes itself on B; its context, of a
-- higher priority, takes both keys while it is open).
local KEYS: { [string]: Enum.KeyCode } = {
	BuildButton = Enum.KeyCode.B,
	ResidentsButton = Enum.KeyCode.R,
}

-- Whether a GUI object and every one of its ancestors is shown.
local shown = Controls.shown

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
	local key = KEYS[name]
	if key then
		Controls.press(keys, name, { key }, function()
			if shown(b) then
				onClick()
			end
		end)
	end
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
	keys = Controls.context("HudKeys", 1000, false)
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
	-- They start under the top row, or at the top when the row is up in the
	-- Roblox bar (`placeTop` below), and end 94 px above the bottom either way.
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
			right.Size = UDim2.new(0, 226, 1, -94 - columnTop)
		elseif not short and grid then
			grid:Destroy()
			Ui.list(right, Enum.FillDirection.Vertical, 6, Enum.HorizontalAlignment.Right)
			right.Size = UDim2.new(0, 110, 1, -94 - columnTop)
		end
	end
	fit()
	if workspace.CurrentCamera then
		workspace.CurrentCamera:GetPropertyChangedSignal("ViewportSize"):Connect(fit)
	end

	-- The top row sits in the middle of the Roblox top bar, between its
	-- buttons, whenever it fits there (his ask, 2026-10-19: no empty band
	-- above it); on a screen too narrow for that it drops under the bar.
	local row = top:FindFirstChildOfClass("UIListLayout") :: UIListLayout
	local function placeTop()
		local bar = GuiService.TopbarInset
		local inset = GuiService:GetGuiInset().Y
		local width = row.AbsoluteContentSize.X
		local mid = gui.AbsoluteSize.X / 2
		local up = bar.Height > 0
			and mid - width / 2 >= bar.Min.X + 8
			and mid + width / 2 <= bar.Max.X - 8
		top.Position = if up
			then UDim2.fromOffset(0, -inset + math.floor((bar.Height - 40) / 2))
			else UDim2.fromOffset(0, 6)
		columnTop = if up then 6 else 56
		left.Position = UDim2.fromOffset(10, columnTop)
		left.Size = UDim2.new(0, 110, 1, -94 - columnTop)
		right.Position = UDim2.new(1, -10, 0, columnTop)
		right.Size = UDim2.new(0, right.Size.X.Offset, 1, -94 - columnTop)
		gui:SetAttribute("TopRowUp", up)
	end
	placeTop()
	GuiService:GetPropertyChangedSignal("TopbarInset"):Connect(placeTop)
	row:GetPropertyChangedSignal("AbsoluteContentSize"):Connect(placeTop)
	gui:GetPropertyChangedSignal("AbsoluteSize"):Connect(placeTop)

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
	-- ButtonY with nothing selected (Controls' menu): the menu buttons.
	Controls.onMenu(function()
		local first = Controls.first(left) or Controls.first(right)
		if first then
			Controls.select(first)
		end
		return first ~= nil
	end)
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
