--!strict
--[[
	The events panel (GDD §8.2): what is on now (the season and its mutation,
	a Full Moon weekend, the Monster Parade and when it starts) and the
	season's shop (Candy at Halloween, Snowflakes in Winter). Its HUD button
	shows only while something is on, with the season's glyph.
	Drawn from the `event` state section; the server checks every purchase.
]]

local ReplicatedStorage = game:GetService("ReplicatedStorage")

local Format = require(ReplicatedStorage.Shared.Format)
local Net = require(ReplicatedStorage.Shared.Net)
local State = require(script.Parent.State)
local Ui = require(script.Parent.Ui)
local Hud = require(script.Parent.Hud)

local EventPanel = {}

local window: Frame
local body: Frame
local button: TextButton

local function line(text: string, order: number, colour: Color3?)
	local l =
		Ui.label(body, `Line_{order}`, text, UDim2.new(1, 0, 0, 26), 18, colour or Ui.Colour.Text)
	l.LayoutOrder = order
end

local function draw()
	for _, c in body:GetChildren() do
		if not c:IsA("UIListLayout") then
			c:Destroy()
		end
	end
	local e = State.data.event
	if not e then
		return
	end
	if e.season then
		line(`{e.season}! {e.mutation} guests can arrive on any bus.`, 1, Ui.Colour.Pumpkin)
	end
	if e.fullMoon then
		line("Full Moon weekend: more Legendary and Epic guests.", 2, Ui.Colour.Moon)
	end
	if e.parade then
		line("The Monster Parade is on: a bus every minute!", 3, Ui.Colour.Gold)
	elseif e.paradeIn then
		line(`The Monster Parade starts in {Format.duration(e.paradeIn)}.`, 3, Ui.Colour.Gold)
	end
	if e.currency then
		line(
			`{e.icon} {e.currencyName}: {e.candy}  ·  from happy stays and defended Hunter Nights`,
			4,
			Ui.Colour.Text
		)
		for i, item in e.shop do
			local row = Ui.frame(body, item.key, UDim2.new(1, 0, 0, 56), nil, Ui.Colour.PanelLight)
			row.LayoutOrder = 10 + i
			Ui.corner(row, 10)
			local name =
				Ui.label(row, "Name", item.name, UDim2.new(1, -150, 0, 24), 18, Ui.Colour.Gold)
			name.Position = UDim2.fromOffset(10, 4)
			local text =
				Ui.label(row, "Text", item.text, UDim2.new(1, -150, 0, 24), 14, Ui.Colour.Muted)
			text.Position = UDim2.fromOffset(10, 28)
			local b = Ui.button(
				row,
				"Buy",
				if item.owned then "Owned" else `{e.icon} {item.cost}`,
				UDim2.fromOffset(120, 44),
				function()
					if not item.owned then
						Net.send("EventShop", item.key)
					end
				end,
				if item.owned
					then Ui.Colour.Ink
					elseif e.candy >= item.cost then Ui.Colour.Good
					else Ui.Colour.Panel
			)
			b.Position = UDim2.new(1, -128, 0, 6)
		end
	end
end

local function refreshButton()
	local e = State.data.event
	button.Visible = e ~= nil and (e.season ~= nil or e.fullMoon or e.parade or e.paradeIn ~= nil)
	button.Text = `{if e and e.icon then e.icon else "🎃"} Events`
end

function EventPanel.Init()
	local gui = Ui.screen("Panels", 6)
	window, body = Ui.window(gui, "EventPanel", "Events", UDim2.fromScale(0.55, 0.6), nil, true)
	Ui.list(body, Enum.FillDirection.Vertical, 6)
end

function EventPanel.Start()
	button = Hud.button("EventButton", "🎃 Events", "Right", function()
		window.Visible = not window.Visible
		if window.Visible then
			draw()
		end
	end, 5)
	button.Visible = false
	State.changed:Connect(function()
		refreshButton()
		if window.Visible then
			draw()
		end
	end)
end

return EventPanel
