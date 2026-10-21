--!strict
--[[
	The Showcase (GDD A.11.4, §7; UI.md "Showcase"): the hotels played on this
	server, most liked this week first, each with **Visit** (the server stands
	the player at its forecourt; the like stays at the sign). Built street
	only (his call, WAITING §2.38). Also the milestone pop-up: a sign
	cosmetic earned by likes received, with **Wear it**.

	A copy for drawing: the list is the server's `showcase` state section.
]]

local ReplicatedStorage = game:GetService("ReplicatedStorage")

local Format = require(ReplicatedStorage.Shared.Format)
local Net = require(ReplicatedStorage.Shared.Net)
local State = require(script.Parent.State)
local Ui = require(script.Parent.Ui)
local Hud = require(script.Parent.Hud)

local ShowcasePanel = {}

local window: Frame
local body: Frame
local popup: Frame
local popupBody: Frame

local function clear(f: Instance)
	for _, c in f:GetChildren() do
		if not c:IsA("UIListLayout") and not c:IsA("UIPadding") then
			c:Destroy()
		end
	end
end

local function draw()
	clear(body)
	local s = State.data.showcase
	if not s then
		return
	end
	local mine =
		`Your hotel: ♥ {Format.number(s.likes)} in all · ♥ {Format.number(s.week)} this week`
	if s.nextName ~= "" then
		mine ..= `  ·  {s.nextName} at {Format.number(s.nextAt)}`
	end
	local head = Ui.label(body, "Head", mine, UDim2.new(1, -10, 0, 26), 17, Ui.Colour.Gold)
	head.LayoutOrder = 0
	local hint = Ui.label(
		body,
		"Hint",
		if s.likeIn > 0
			then `Like a hotel at its sign once you have played {s.likeIn} more minute{if s.likeIn
					== 1
				then ""
				else "s"} today.`
			else "Visit a hotel, then like it at its sign: once a day each.",
		UDim2.new(1, -10, 0, 22),
		15,
		Ui.Colour.Muted
	)
	hint.LayoutOrder = 1
	local list = table.clone(s.list)
	table.sort(list, function(a, b)
		if a.week ~= b.week then
			return a.week > b.week
		end
		if a.likes ~= b.likes then
			return a.likes > b.likes
		end
		return a.index < b.index
	end)
	for i, e in list do
		local row =
			Ui.frame(body, `Hotel_{e.index}`, UDim2.new(1, -10, 0, 56), nil, Ui.Colour.PanelLight)
		row.LayoutOrder = 10 + i
		Ui.corner(row, 10)
		local name = Ui.label(
			row,
			"Name",
			`{i}. {e.name}'s Hotel{if e.favourite then "  ★ Street Favourite" else ""}`,
			UDim2.new(1, -150, 0, 26),
			18,
			if e.favourite then Ui.Colour.Gold else Ui.Colour.Text
		)
		name.Position = UDim2.fromOffset(10, 3)
		local likes = Ui.label(
			row,
			"Likes",
			`{e.street}  ·  ♥ {Format.number(e.week)} this week  ·  ♥ {Format.number(e.likes)} in all{if e.liked
				then "  ·  you liked it today"
				else ""}`,
			UDim2.new(1, -150, 0, 22),
			14,
			Ui.Colour.Muted
		)
		likes.Position = UDim2.fromOffset(10, 29)
		local visit = Ui.button(
			row,
			"Visit",
			if e.mine then "Yours" else "Visit",
			UDim2.fromOffset(120, 44),
			function()
				if not e.mine then
					Net.send("Visit", e.index)
					window.Visible = false
				end
			end,
			if e.mine then Ui.Colour.Ink else Ui.Colour.Teal
		)
		visit.Position = UDim2.new(1, -128, 0, 6)
	end
	if #list <= 1 then
		local none = Ui.label(
			body,
			"Empty",
			"Nobody else is playing here yet. Their hotels will show up as they join.",
			UDim2.new(1, -10, 0, 40),
			15,
			Ui.Colour.Muted
		)
		none.LayoutOrder = 100
	end
end

-- The milestone pop-up: the cosmetic earned and a button to wear it at once.
local function milestone(data: any)
	clear(popupBody)
	local text = Ui.label(
		popupBody,
		"Text",
		`♥ {Format.number(data.likes)} likes! You earned the {data.name}.`,
		UDim2.new(1, 0, 0, 60),
		22,
		Ui.Colour.Gold
	)
	text.TextWrapped = true
	text.TextXAlignment = Enum.TextXAlignment.Center
	text.LayoutOrder = 1
	local wear = Ui.button(popupBody, "Wear", "Wear it", UDim2.new(1, 0, 0, 48), function()
		Net.send("Equip", "Sign", data.id)
		popup.Visible = false
	end, Ui.Colour.Good)
	wear.LayoutOrder = 2
	popup.Visible = true
end

function ShowcasePanel.Init()
	local gui = Ui.screen("Showcase", 6)
	window, body = Ui.window(gui, "ShowcasePanel", "Showcase", UDim2.fromScale(0.6, 0.7), nil, true)
	Ui.list(body, Enum.FillDirection.Vertical, 6)
	popup, popupBody = Ui.window(gui, "ShowcaseMilestone", "Liked!", UDim2.fromOffset(380, 210))
	Ui.list(popupBody, Enum.FillDirection.Vertical, 8)
end

function ShowcasePanel.Start()
	Hud.button("ShowcaseButton", "♥ Showcase", "Left", function()
		window.Visible = not window.Visible
		if window.Visible then
			draw()
		end
	end, 5)
	State.changed:Connect(function()
		if window.Visible then
			draw()
		end
	end)
	Net.listen("Moment", function(kind: string, data: any)
		if kind == "LikeMilestone" and typeof(data) == "table" then
			milestone(data)
		end
	end)
end

return ShowcasePanel
