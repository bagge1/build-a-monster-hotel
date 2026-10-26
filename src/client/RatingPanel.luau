--!strict
--[[
	The hotel rating's breakdown (GDD §5.3: "the breakdown is shown in the UI",
	as in Restaurant Tycoon 2): the stars, and a bar per category with what
	feeds it, from the plot's published `Rating` and `Categories`.
]]

local HttpService = game:GetService("HttpService")
local Players = game:GetService("Players")
local ReplicatedStorage = game:GetService("ReplicatedStorage")

local Format = require(ReplicatedStorage.Shared.Format)
local Rating = require(ReplicatedStorage.Shared.Rating)
local Ui = require(script.Parent.Ui)
local Hud = require(script.Parent.Hud)

local RatingPanel = {}

local me = Players.LocalPlayer
local window: Frame
local body: Frame

local FEEDS = {
	Comfort = "Room tiers, matched preferences",
	Service = "Check-in waits, requests fulfilled",
	Cleanliness = "Rooms cleaned on time",
	Fun = "Amenities, Entertainment staff",
	Style = "Decor, variety of room types",
}

local function redraw()
	for _, c in body:GetChildren() do
		if not c:IsA("UIListLayout") then
			c:Destroy()
		end
	end
	local plots = workspace:FindFirstChild("Plots")
	local plot = plots and plots:FindFirstChild(`Plot_{me:GetAttribute("Plot")}`)
	if not plot then
		return
	end
	local stars = plot:GetAttribute("Rating") :: number? or 1
	local head = Ui.label(
		body,
		"Stars",
		`{Format.stars(stars)}  ·  from the last 30 reviews and these five`,
		UDim2.new(1, 0, 0, 30),
		22,
		Ui.Colour.Gold
	)
	head.LayoutOrder = 0
	local ok, categories = pcall(function()
		return HttpService:JSONDecode(plot:GetAttribute("Categories") :: string)
	end)
	if not ok or typeof(categories) ~= "table" then
		return
	end
	for i, name in Rating.Order do
		local value = categories[name] or 0
		local row = Ui.frame(body, name, UDim2.new(1, 0, 0, 52))
		row.BackgroundTransparency = 1
		row.LayoutOrder = i
		Ui.label(row, "Name", `{name}  {math.floor(value)}`, UDim2.new(0.4, 0, 0, 26), 20)
		local feeds =
			Ui.label(row, "Feeds", FEEDS[name], UDim2.new(0.6, 0, 0, 26), 15, Ui.Colour.Muted)
		feeds.Position = UDim2.fromScale(0.4, 0)
		local bar =
			Ui.frame(row, "Bar", UDim2.new(1, 0, 0, 14), UDim2.fromOffset(0, 30), Ui.Colour.Ink)
		Ui.corner(bar, 7)
		local fill = Ui.frame(
			bar,
			"Fill",
			UDim2.fromScale(math.clamp(value / 100, 0, 1), 1),
			nil,
			Ui.Colour.Teal
		)
		Ui.corner(fill, 7)
	end
end

function RatingPanel.Init()
	local gui = Ui.screen("Panels", 6)
	window, body =
		Ui.window(gui, "RatingPanel", "Hotel rating", UDim2.fromScale(0.45, 0.6), nil, true)
	Ui.list(body, Enum.FillDirection.Vertical, 8)
end

function RatingPanel.Start()
	Hud.button("RatingButton", "★ Rating", "Left", function()
		window.Visible = not window.Visible
		if window.Visible then
			redraw()
		end
	end, 2)
	local function changed()
		if window.Visible then
			redraw()
		end
	end
	me:GetAttributeChangedSignal("Rating"):Connect(changed)
	-- The bars are the plot's `Categories`, which move without the stars; a Travel is another
	-- plot (2026-10-26: an open breakdown kept the old numbers, or the hotel left behind).
	local watched: { RBXScriptConnection } = {}
	local function watch()
		for _, c in watched do
			c:Disconnect()
		end
		table.clear(watched)
		local plots = workspace:FindFirstChild("Plots")
		local plot = plots and plots:FindFirstChild(`Plot_{me:GetAttribute("Plot")}`)
		if plot then
			for _, a in { "Categories", "Rating" } do
				table.insert(watched, plot:GetAttributeChangedSignal(a):Connect(changed))
			end
		end
	end
	for _, a in { "Plot", "Street" } do
		me:GetAttributeChangedSignal(a):Connect(function()
			watch()
			changed()
		end)
	end
	window:GetPropertyChangedSignal("Visible"):Connect(function()
		if window.Visible then
			watch() -- the plot's model may have streamed in since
		end
	end)
	watch()
end

return RatingPanel
