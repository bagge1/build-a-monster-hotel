--!strict
--[[
	A find's moment (GDD A.11.3, UI.md "Found"): the `Moment` "Found" from
	`FindService` opens a pop-up with the piece, its set's count and where it
	goes (the build mode's Decor tab, under Found), with **Place it** (build
	mode opens on the Decor tab with the piece chosen) and **Later**. A
	duplicate says what it paid. Mobile first: one window, buttons at least
	44 tall.
]]

local ReplicatedStorage = game:GetService("ReplicatedStorage")

local Format = require(ReplicatedStorage.Shared.Format)
local Net = require(ReplicatedStorage.Shared.Net)
local BuildController = require(script.Parent.BuildController)
local Ui = require(script.Parent.Ui)

local FindsPanel = {}

local popup: Frame
local body: Frame

local function clear()
	for _, c in body:GetChildren() do
		if c:IsA("GuiObject") then
			c:Destroy()
		end
	end
end

local function where(data: any): string
	local size = `{data.w or 1}×{data.d or 1}`
	local layer = if data.layer == "Wall"
		then "on a wall"
		elseif data.layer == "Rug" then "a rug"
		else "on the floor"
	return `{size}, {layer} · Build → Decor, under Found · each copy {Format.cash(
		data.price or 0
	)}`
end

local function show(data: any)
	clear()
	local title = popup:FindFirstChild("Title", true)
	if title and title:IsA("TextLabel") then
		title.Text = if data.kind == "Souvenir"
			then "A souvenir!"
			elseif data.kind == "Duplicate" then "Found again"
			else "★ Found!"
	end
	local lines = {}
	if data.kind == "Duplicate" then
		table.insert(lines, `{data.name} again: you have it already.`)
		table.insert(lines, `+{Format.cash(data.cash or 0)}`)
	else
		table.insert(lines, data.name)
		if data.set then
			table.insert(lines, `{data.set}: {data.have}/{data.total} found`)
		end
	end
	if data.why then
		table.insert(lines, `From {data.why}.`)
	end
	local text = Ui.label(
		body,
		"Text",
		table.concat(lines, "\n"),
		UDim2.new(1, 0, 0, 96),
		20,
		Ui.Colour.Gold
	)
	text.TextXAlignment = Enum.TextXAlignment.Center
	text.LayoutOrder = 1
	if data.kind ~= "Duplicate" then
		local hint =
			Ui.label(body, "Where", where(data), UDim2.new(1, 0, 0, 36), 14, Ui.Colour.Muted)
		hint.TextXAlignment = Enum.TextXAlignment.Center
		hint.LayoutOrder = 2
	end
	local buttons = Ui.frame(body, "Buttons", UDim2.new(1, 0, 0, 48))
	buttons.BackgroundTransparency = 1
	buttons.LayoutOrder = 3
	Ui.list(buttons, Enum.FillDirection.Horizontal, 8)
	if data.kind ~= "Duplicate" then
		local place = Ui.button(buttons, "Place", "Place it", UDim2.new(0.5, -4, 1, 0), function()
			popup.Visible = false
			BuildController.placeDecor(data.id)
		end, Ui.Colour.Good)
		place.LayoutOrder = 1
	end
	local ok = Ui.button(
		buttons,
		"Ok",
		if data.kind == "Duplicate" then "Lovely" else "Later",
		UDim2.new(if data.kind == "Duplicate" then 1 else 0.5, -4, 1, 0),
		function()
			popup.Visible = false
		end,
		Ui.Colour.Panel
	)
	ok.LayoutOrder = 2
	popup.Visible = true
end

function FindsPanel.Init()
	local gui = Ui.screen("Finds", 7)
	popup, body = Ui.window(gui, "FoundPopup", "★ Found!", UDim2.fromOffset(420, 260))
	Ui.list(body, Enum.FillDirection.Vertical, 8)
end

function FindsPanel.Start()
	Net.listen("Moment", function(kind: string, data: any)
		if kind == "Found" and typeof(data) == "table" then
			show(data)
		end
	end)
end

return FindsPanel
