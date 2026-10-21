--!strict
--[[
	Gloom, the bat concierge (GDD §11, Appendix A.7): a speech bubble with what
	to do next, an arrow at the thing to press or the place to go, and Skip.
	The step is the server's (`Tutorial` attribute, `TutorialService`); this
	only draws it. Nothing here blocks movement.

	Gloom's look is a night draft (WAITING.md §1); his name is GDD §17's open
	question 6.
]]

local Players = game:GetService("Players")
local ReplicatedStorage = game:GetService("ReplicatedStorage")
local RunService = game:GetService("RunService")

local HotelPoints = require(ReplicatedStorage.Shared.HotelPoints)
local Net = require(ReplicatedStorage.Shared.Net)
local Ui = require(script.Parent.Ui)
local UiImages = require(script.Parent.UiImages)

local TutorialController = {}

local me = Players.LocalPlayer

type Step = { text: string, ui: string?, world: string? }
local STEPS: { [string]: Step } = {
	CheckIn = {
		text = "Welcome, new manager! I'm Gloom. Your first room is ready and a Slime is on its way: check it in at the front desk.",
		world = "Desk",
	},
	Collect = {
		text = "Guests pay into your till every second. Collect it at the till!",
		world = "Till",
	},
	SecondRoom = {
		text = "Build a second room! In Build: buy gold tiles beside the hotel, draw Walls round them, put in a Door, then tap inside and choose Standard Room.",
		ui = "Hud.Left.BuildButton",
	},
	Furnish = {
		text = "Now put a Bed in it (Build, Furniture). A room is ready once its key furniture stands in it.",
		ui = "Hud.Left.BuildButton",
	},
	Bus = {
		text = "The Night Bus brings guests for every hotel on the street. Walk up to one and Pitch it!",
		ui = "Hud.BusCountdown",
	},
	MoveIn = {
		text = "Happy guests become friends, and friends move in. Your Slime is nearly ready...",
		ui = "Hud.Left.BookButton",
	},
	Goal = {
		text = "Big news: a Vampire Count arrives in 3 buses! Build a Coffin Suite on your new tiles: walls, a door, then a Coffin. The tiles and the Coffin are on me.",
		ui = "Hud.Left.BuildButton",
	},
	Clean = {
		text = "Rooms need cleaning after a stay. Hold Clean at a dirty room's door.",
		world = nil,
	},
	Staff = {
		text = "Residents can work! Open Residents and give your Slime a job (Room Service suits it).",
		ui = "Hud.Left.ResidentsButton",
	},
	Preview = {
		text = "Reach 4★, earn $1M and befriend a Vampire Count, and Frostfang Lodge awaits. Your residents earn while you're away, up to 2 hours!",
		ui = "Hud.Right.ProgressionButton",
	},
}

local bubble: Frame
local text: TextLabel
local nextButton: TextButton
local arrow: TextLabel
local worldArrow: BillboardGui?

local function find(path: string): GuiObject?
	local inst: Instance? = me:FindFirstChild("PlayerGui")
	for _, part in string.split(path, ".") do
		inst = inst and inst:FindFirstChild(part, true)
	end
	return if inst and inst:IsA("GuiObject") then inst else nil
end

-- Whether a GUI object and every one of its ancestors is shown.
local function shown(g: GuiObject): boolean
	local node: Instance? = g
	while node and node:IsA("GuiObject") do
		if not node.Visible then
			return false
		end
		node = node.Parent
	end
	return true
end

local function plotModel(): Model?
	local plots = workspace:FindFirstChild("Plots")
	local m = plots and plots:FindFirstChild(`Plot_{me:GetAttribute("Plot")}`)
	return if m and m:IsA("Model") then m else nil
end

local function setWorldArrow(name: string?)
	if worldArrow then
		worldArrow:Destroy()
		worldArrow = nil
	end
	local plot = plotModel()
	local a = if name and plot then HotelPoints.attachment(plot, name) else nil
	if not a then
		return
	end
	local bb = Instance.new("BillboardGui")
	bb.Name = "GloomArrow"
	bb.Size = UDim2.fromOffset(80, 80)
	bb.StudsOffset = Vector3.new(0, 4, 0)
	bb.AlwaysOnTop = true
	bb.Adornee = a
	local l = Ui.label(bb, "Arrow", "⬇", UDim2.fromScale(1, 1), 60, Ui.Colour.Gold)
	l.TextXAlignment = Enum.TextXAlignment.Center
	l.TextStrokeTransparency = 0
	bb.Parent = me:WaitForChild("PlayerGui")
	worldArrow = bb
end

local function refresh()
	local step = me:GetAttribute("Tutorial") :: string?
	if step == "Start" or step == "Build" then
		step = "CheckIn"
	end
	local s = step and STEPS[step]
	bubble.Visible = s ~= nil
	arrow.Visible = false
	setWorldArrow(nil)
	if not s then
		return
	end
	text.Text = s.text
	nextButton.Visible = step == "Preview"
	setWorldArrow(s.world)
end

function TutorialController.Init()
	local gui = Ui.screen("Tutorial", 5)
	-- Top centre, under the bus countdown: never the bottom corners (§11), and
	-- narrow enough on a phone to leave the hotel in view.
	bubble = Ui.panel(
		gui,
		"Gloom",
		UDim2.new(0.36, 0, 0, 104),
		UDim2.new(0.5, 0, 0, 80),
		Vector2.new(0.5, 0)
	)
	-- Clear of the countdown and of the arrow pointing at it (26 px of
	-- countdown, the arrow 12 px past it, then 14 px of air), wherever the
	-- HUD's top row sits.
	Ui.onTopRow(function(up: boolean)
		bubble.Position = UDim2.new(0.5, 0, 0, if up then 56 else 104)
	end)
	local cap = Instance.new("UISizeConstraint")
	cap.MaxSize = Vector2.new(460, 104)
	cap.MinSize = Vector2.new(270, 0)
	cap.Parent = bubble
	bubble.Visible = false
	-- Gloom's portrait (ui/Gloom.png, UiImages); the bat emoji if it is not uploaded.
	local portrait = UiImages.Gloom
	if portrait and portrait ~= "" then
		local face = Instance.new("ImageLabel")
		face.Name = "Face"
		face.BackgroundTransparency = 1
		face.Image = portrait
		face.Size = UDim2.fromOffset(52, 52)
		face.Position = UDim2.fromOffset(4, 4)
		face.Parent = bubble
	else
		local face = Ui.label(bubble, "Face", "🦇", UDim2.fromOffset(48, 48), 36)
		face.Position = UDim2.fromOffset(6, 6)
		face.TextXAlignment = Enum.TextXAlignment.Center
	end
	local name = Ui.label(bubble, "Name", "Gloom", UDim2.fromOffset(60, 18), 14, Ui.Colour.Gold)
	name.Position = UDim2.fromOffset(0, 54)
	name.TextXAlignment = Enum.TextXAlignment.Center
	text = Ui.label(bubble, "Text", "", UDim2.new(1, -70, 1, -54), 16)
	text.Position = UDim2.fromOffset(62, 6)
	text.TextYAlignment = Enum.TextYAlignment.Top
	-- Shrinks to fit a narrow (phone) bubble, never above its normal size.
	text.TextScaled = true
	local maxSize = Instance.new("UITextSizeConstraint")
	maxSize.MaxTextSize = 16
	maxSize.Parent = text
	local skip = Ui.button(bubble, "Skip", "Skip tutorial", UDim2.fromOffset(110, 44), function()
		Net.send("Tutorial", "Skip")
	end, Ui.Colour.Panel)
	skip.Position = UDim2.new(1, -116, 1, -48)
	skip.TextSize = 14
	nextButton = Ui.button(bubble, "Next", "Got it!", UDim2.fromOffset(96, 44), function()
		Net.send("Tutorial", "Next")
	end, Ui.Colour.Teal)
	nextButton.Position = UDim2.new(1, -218, 1, -48)
	arrow = Ui.label(gui, "Arrow", "◀", UDim2.fromOffset(50, 50), 44, Ui.Colour.Gold)
	arrow.TextStrokeTransparency = 0
	arrow.Visible = false
end

function TutorialController.Start()
	me:GetAttributeChangedSignal("Tutorial"):Connect(refresh)
	me:GetAttributeChangedSignal("Plot"):Connect(refresh)
	refresh()
	-- The arrow follows its UI target and bobs.
	RunService.Heartbeat:Connect(function()
		local step = me:GetAttribute("Tutorial") :: string?
		local s = step and STEPS[step]
		local target = s and s.ui and find(s.ui)
		if target and shown(target) then
			local p = target.AbsolutePosition
			local size = target.AbsoluteSize
			-- A centred label points at its text, not its (wider) box.
			local rightEdge = p.X + size.X
			if target:IsA("TextLabel") and target.TextXAlignment == Enum.TextXAlignment.Center then
				rightEdge = p.X + size.X / 2 + target.TextBounds.X / 2
			end
			local bob = math.sin(os.clock() * 6) * 6
			arrow.Position = UDim2.fromOffset(rightEdge + 8 + bob, p.Y + size.Y / 2 - 25)
			arrow.Visible = true
		else
			arrow.Visible = false
		end
	end)
	Net.listen("Moment", function(kind: string)
		if kind == "OpenBook" then
			local panels = require(script.Parent.CollectionPanels) :: any
			panels.openBook()
		end
	end)
end

return TutorialController
