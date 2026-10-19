--!strict
--[[
	The interface's builders and its look (UI.md). Every panel in the game is
	built from these, so the look lives in one place and a designed panel can
	replace a built one by carrying the same names (UI.md, "How a panel is
	found").

	THE LOOK IS A NIGHT DRAFT for August's review (WAITING.md §1): the GDD's
	"cozy creepy" palette (§12) of purples, teal, pumpkin orange and moonlight
	blue, chunky rounded panels, Fredoka One.

	Mobile rules (§11): nothing in the bottom corners (Roblox's thumbstick and
	jump live there), tap targets at least 44 px, everything reachable by
	gamepad (`Selectable` on every button).
]]

local Players = game:GetService("Players")

local Ui = {}

Ui.Colour = {
	Ink = Color3.fromRGB(24, 16, 38),
	Panel = Color3.fromRGB(46, 32, 70),
	PanelLight = Color3.fromRGB(70, 50, 104),
	Line = Color3.fromRGB(120, 95, 170),
	Text = Color3.fromRGB(246, 240, 255),
	Muted = Color3.fromRGB(180, 168, 210),
	Pumpkin = Color3.fromRGB(245, 145, 45),
	Teal = Color3.fromRGB(60, 205, 190),
	Moon = Color3.fromRGB(170, 200, 255),
	Good = Color3.fromRGB(120, 220, 120),
	Bad = Color3.fromRGB(240, 90, 100),
	Gold = Color3.fromRGB(255, 205, 80),
}
Ui.Font = Enum.Font.FredokaOne
Ui.MinTap = 44

local player = Players.LocalPlayer

function Ui.screen(name: string, order: number?): ScreenGui
	local pg = player:WaitForChild("PlayerGui")
	local existing = pg:FindFirstChild(name)
	if existing and existing:IsA("ScreenGui") then
		return existing
	end
	local gui = Instance.new("ScreenGui")
	gui.Name = name
	gui.ResetOnSpawn = false
	gui.ZIndexBehavior = Enum.ZIndexBehavior.Sibling
	gui.IgnoreGuiInset = false
	gui.DisplayOrder = order or 1
	gui.Parent = pg
	return gui
end

-- Whether the HUD's top row sits up in the Roblox top bar (Hud decides and
-- sets it on its ScreenGui); calls `fn` now and whenever the row moves, so
-- what hangs under the row (the bus countdown, Gloom's bubble) can follow.
function Ui.onTopRow(fn: (up: boolean) -> ())
	local hud = Ui.screen("Hud", 1)
	local function call()
		fn(hud:GetAttribute("TopRowUp") == true)
	end
	hud:GetAttributeChangedSignal("TopRowUp"):Connect(call)
	call()
end

local function corner(parent: Instance, radius: number?)
	local c = Instance.new("UICorner")
	c.CornerRadius = UDim.new(0, radius or 12)
	c.Parent = parent
end
Ui.corner = corner

local function stroke(parent: Instance, colour: Color3?, thickness: number?)
	local s = Instance.new("UIStroke")
	s.Color = colour or Ui.Colour.Line
	s.Thickness = thickness or 2
	s.ApplyStrokeMode = Enum.ApplyStrokeMode.Border
	s.Parent = parent
end
Ui.stroke = stroke

function Ui.padding(parent: Instance, px: number)
	local p = Instance.new("UIPadding")
	p.PaddingLeft = UDim.new(0, px)
	p.PaddingRight = UDim.new(0, px)
	p.PaddingTop = UDim.new(0, px)
	p.PaddingBottom = UDim.new(0, px)
	p.Parent = parent
end

function Ui.list(
	parent: Instance,
	dir: Enum.FillDirection?,
	gap: number?,
	align: Enum.HorizontalAlignment?
): UIListLayout
	local l = Instance.new("UIListLayout")
	l.FillDirection = dir or Enum.FillDirection.Vertical
	l.Padding = UDim.new(0, gap or 6)
	l.SortOrder = Enum.SortOrder.LayoutOrder
	l.HorizontalAlignment = align or Enum.HorizontalAlignment.Left
	l.VerticalAlignment = Enum.VerticalAlignment.Top
	l.Parent = parent
	return l
end

function Ui.frame(parent: Instance, name: string, size: UDim2, pos: UDim2?, colour: Color3?): Frame
	local f = Instance.new("Frame")
	f.Name = name
	f.Size = size
	f.Position = pos or UDim2.new()
	f.BackgroundColor3 = colour or Ui.Colour.Panel
	f.BorderSizePixel = 0
	f.Parent = parent
	return f
end

-- A rounded panel with a border.
function Ui.panel(parent: Instance, name: string, size: UDim2, pos: UDim2?, anchor: Vector2?): Frame
	local f = Ui.frame(parent, name, size, pos)
	f.AnchorPoint = anchor or Vector2.zero
	f.BackgroundTransparency = 0.05
	corner(f, 16)
	stroke(f)
	return f
end

function Ui.label(
	parent: Instance,
	name: string,
	text: string,
	size: UDim2,
	textSize: number?,
	colour: Color3?
): TextLabel
	local l = Instance.new("TextLabel")
	l.Name = name
	l.Size = size
	l.BackgroundTransparency = 1
	l.Font = Ui.Font
	l.Text = text
	l.TextSize = textSize or 18
	l.TextColor3 = colour or Ui.Colour.Text
	l.TextXAlignment = Enum.TextXAlignment.Left
	l.TextWrapped = true
	l.Parent = parent
	return l
end

function Ui.button(
	parent: Instance,
	name: string,
	text: string,
	size: UDim2,
	onClick: () -> (),
	colour: Color3?
): TextButton
	local b = Instance.new("TextButton")
	b.Name = name
	b.Size = size
	b.BackgroundColor3 = colour or Ui.Colour.PanelLight
	b.AutoButtonColor = true
	b.Font = Ui.Font
	b.Text = text
	b.TextSize = 18
	b.TextColor3 = Ui.Colour.Text
	b.TextWrapped = true
	b.Selectable = true
	b.Parent = parent
	corner(b, 10)
	stroke(b, Color3.fromRGB(20, 12, 30), 2)
	local c = Instance.new("UISizeConstraint")
	c.MinSize = Vector2.new(Ui.MinTap, Ui.MinTap)
	c.Parent = b
	b.Activated:Connect(onClick)
	return b
end

function Ui.scroll(
	parent: Instance,
	name: string,
	size: UDim2,
	pos: UDim2?,
	horizontal: boolean?
): ScrollingFrame
	local s = Instance.new("ScrollingFrame")
	s.Name = name
	s.Size = size
	s.Position = pos or UDim2.new()
	s.BackgroundTransparency = 1
	s.BorderSizePixel = 0
	s.ScrollBarThickness = 6
	s.ScrollBarImageColor3 = Ui.Colour.Line
	s.CanvasSize = UDim2.new()
	s.AutomaticCanvasSize = if horizontal then Enum.AutomaticSize.X else Enum.AutomaticSize.Y
	s.ScrollingDirection = if horizontal
		then Enum.ScrollingDirection.X
		else Enum.ScrollingDirection.Y
	s.Parent = parent
	return s
end

-- A window with a title and a cross in its top-right corner (UI.md, "Pop-ups close with a cross").
function Ui.window(
	gui: ScreenGui,
	name: string,
	title: string,
	size: UDim2,
	onClose: (() -> ())?,
	scroll: boolean?
): (Frame, Frame)
	-- A short screen (a phone in landscape) gets nearly the whole screen.
	local camera = workspace.CurrentCamera
	if camera and camera.ViewportSize.Y < 500 then
		size = UDim2.fromScale(0.94, 0.9)
	end
	local w = Ui.panel(gui, name, size, UDim2.fromScale(0.5, 0.5), Vector2.new(0.5, 0.5))
	local t = Ui.label(w, "Title", title, UDim2.new(1, -70, 0, 40), 26, Ui.Colour.Gold)
	t.Position = UDim2.fromOffset(16, 8)
	local close = Ui.button(w, "Close", "X", UDim2.fromOffset(44, 44), function()
		w.Visible = false
		if onClose then
			onClose()
		end
	end, Ui.Colour.Bad)
	close.Position = UDim2.new(1, -52, 0, 8)
	-- `scroll`: the body scrolls when its rows outgrow it (a list of fixed-height
	-- rows; a body whose children are sized by scale keeps a plain frame).
	local body: Frame = if scroll
		then Ui.scroll(w, "Body", UDim2.new(1, -24, 1, -64), UDim2.fromOffset(12, 56)) :: any
		else Ui.frame(w, "Body", UDim2.new(1, -24, 1, -64), UDim2.fromOffset(12, 56))
	body.BackgroundTransparency = 1
	local sizeConstraint = Instance.new("UISizeConstraint")
	sizeConstraint.MaxSize = Vector2.new(900, 640)
	sizeConstraint.Parent = w
	w.Visible = false
	return w, body
end

return Ui
