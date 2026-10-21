--!strict
--[[
	The VIP ledger (GDD A.11.1; UI.md "VIP ledger"): the contracts running
	and the offers for the hotel being played, with Accept, Swap, Ready and
	Cancel. Opened by the HUD's VIP button (left column) and the front
	desk's "VIP ledger" prompt (the server's Moment `VipLedger`). Mobile
	first: rows of big buttons, one contract to a row.

	A copy for drawing: everything is the server's `vip` state section; the
	clock counts down here between sends from the `left` it was sent.
]]

local ReplicatedStorage = game:GetService("ReplicatedStorage")

local Format = require(ReplicatedStorage.Shared.Format)
local Net = require(ReplicatedStorage.Shared.Net)
local State = require(script.Parent.State)
local Ui = require(script.Parent.Ui)
local Hud = require(script.Parent.Hud)

local VipPanel = {}

local window: Frame
local body: Frame
local popup: Frame
local popupBody: Frame

-- The running contracts' status lines, redrawn each second (the clock and the bus).
local live: { { label: TextLabel, row: any } } = {}
local sentAt = os.clock()

local RARITY_COLOUR: { [string]: Color3 } = {
	Common = Ui.Colour.Text,
	Uncommon = Ui.Colour.Good,
	Rare = Ui.Colour.Moon,
	Epic = Color3.fromRGB(200, 130, 255),
	Legendary = Ui.Colour.Gold,
	Mythic = Ui.Colour.Pumpkin,
}

local function clear(f: Instance)
	for _, c in f:GetChildren() do
		if not c:IsA("UIListLayout") and not c:IsA("UIPadding") then
			c:Destroy()
		end
	end
end

local function clock(seconds: number): string
	local s = math.max(0, math.floor(seconds))
	return string.format("%d:%02d", s // 60, s % 60)
end

-- A running contract's status line now.
local function statusText(c: any): string
	if c.state == "Accepted" then
		if not c.here then
			return `At your {c.locationName}: its clock waits there`
		end
		local left = c.left - (os.clock() - sentAt)
		local best = if c.best ~= "" then ` · your best {c.typeName} now: {c.best}` else ""
		local ready = if c.canReady then " · ready to book: tap Ready" else `\n{c.why}`
		return `{clock(left)} of play left{best}{ready}`
	elseif c.state == "Booked" then
		local at = workspace:GetAttribute("NextBusAt") :: number?
		local wait = if at then at - workspace:GetServerTimeNow() else 0
		return `Room held · comes on the next Night Bus ({clock(wait)})`
	elseif c.state == "Arriving" then
		return "On its way to your front desk"
	end
	return "Staying · pays ×2 · a happy stay completes it"
end

local function row(parent: Instance, name: string, order: number, c: any, running: boolean): Frame
	local f = Ui.frame(parent, name, UDim2.new(1, -10, 0, 132), nil, Ui.Colour.PanelLight)
	f.LayoutOrder = order
	Ui.corner(f, 10)
	Ui.stroke(f, RARITY_COLOUR[c.rarity] or Ui.Colour.Line, 2)
	local title = Ui.label(
		f,
		"Name",
		`👑 VIP {c.name}  ·  {c.rarity}`,
		UDim2.new(1, -150, 0, 26),
		20,
		RARITY_COLOUR[c.rarity] or Ui.Colour.Text
	)
	title.Position = UDim2.fromOffset(10, 4)
	local spec = Ui.label(
		f,
		"Spec",
		`{c.typeName} · {c.needsText}`,
		UDim2.new(1, -150, 0, 22),
		17,
		Ui.Colour.Teal
	)
	spec.Position = UDim2.fromOffset(10, 30)
	local likes = Ui.label(
		f,
		"Likes",
		`Likes {table.concat(c.prefs, ", ")} (a happy stay needs them)`,
		UDim2.new(1, -150, 0, 20),
		14,
		Ui.Colour.Muted
	)
	likes.Position = UDim2.fromOffset(10, 54)
	local reward = Ui.label(
		f,
		"Reward",
		`Reward {Format.cash(c.reward)} at today's income`
			.. (
				if running then "" else ` · {math.floor(State.data.vip.deadline / 60)} min of play`
			),
		UDim2.new(1, -150, 0, 20),
		15,
		Ui.Colour.Gold
	)
	reward.Position = UDim2.fromOffset(10, 76)
	if running then
		local status =
			Ui.label(f, "Status", statusText(c), UDim2.new(1, -150, 0, 34), 14, Ui.Colour.Text)
		status.Position = UDim2.fromOffset(10, 96)
		status.TextYAlignment = Enum.TextYAlignment.Top
		table.insert(live, { label = status, row = c })
	end
	return f
end

local function draw()
	clear(body)
	table.clear(live)
	local v = State.data.vip
	if not v then
		return
	end
	if not v.unlocked then
		local shut = Ui.label(
			body,
			"Head",
			`The VIP ledger opens at {v.unlockStars}★. Your hotel is {Format.stars(v.stars)} now.`,
			UDim2.new(1, -10, 0, 50),
			18,
			Ui.Colour.Muted
		)
		shut.LayoutOrder = 0
		return
	end
	local head = Ui.label(
		body,
		"Head",
		`VIPs hosted today {v.done}/{v.cap}  ·  {v.swaps} swap{if v.swaps == 1 then "" else "s"} left  ·  {v.activeCap} at a time`,
		UDim2.new(1, -10, 0, 26),
		17,
		Ui.Colour.Gold
	)
	head.LayoutOrder = 0
	if not v.canAccept and v.why ~= "" then
		local note = Ui.label(body, "Note", v.why, UDim2.new(1, -10, 0, 22), 15, Ui.Colour.Pumpkin)
		note.LayoutOrder = 1
	end
	for i, c in v.active do
		local f = row(body, `Contract_{c.id}`, 10 + i, c, true)
		if c.state == "Accepted" and c.here then
			local b = Ui.button(f, "Ready", "Ready", UDim2.fromOffset(130, 52), function()
				Net.send("Vip", "Ready", tostring(c.id))
			end, if c.canReady then Ui.Colour.Good else Ui.Colour.Ink)
			b.Position = UDim2.new(1, -138, 0, 10)
		elseif c.state == "Booked" then
			local b = Ui.button(
				f,
				"Cancel",
				"Let the room go",
				UDim2.fromOffset(130, 52),
				function()
					Net.send("Vip", "Cancel", tostring(c.id))
				end,
				Ui.Colour.Bad
			)
			b.Position = UDim2.new(1, -138, 0, 10)
		end
	end
	if #v.offers > 0 then
		local h =
			Ui.label(body, "OffersHead", "Offers", UDim2.new(1, -10, 0, 24), 19, Ui.Colour.Text)
		h.LayoutOrder = 50
	end
	for i, o in v.offers do
		local f = row(body, `Offer_{o.id}`, 50 + i, o, false)
		local accept = Ui.button(f, "Accept", "Accept", UDim2.fromOffset(130, 52), function()
			Net.send("Vip", "Accept", tostring(o.id))
		end, if v.canAccept then Ui.Colour.Teal else Ui.Colour.Ink)
		accept.Position = UDim2.new(1, -138, 0, 10)
		local swap = Ui.button(f, "Swap", "Swap", UDim2.fromOffset(130, 52), function()
			Net.send("Vip", "Swap", tostring(o.id))
		end, if v.swaps > 0 then Ui.Colour.PanelLight else Ui.Colour.Ink)
		swap.Position = UDim2.new(1, -138, 0, 70)
	end
	if #v.offers == 0 and #v.active == 0 then
		local none = Ui.label(
			body,
			"Empty",
			"No VIP wants a room you can build yet. Build more room types, or raise your rating.",
			UDim2.new(1, -10, 0, 44),
			15,
			Ui.Colour.Muted
		)
		none.LayoutOrder = 100
	end
	local hint = Ui.label(
		body,
		"Hint",
		"Accept a VIP, build or furnish a room to its ask, tap Ready: it rides the next Night Bus, booked to you. "
			.. "A happy stay pays the reward. A Book page's 👑 asks for that monster (a swap).",
		UDim2.new(1, -10, 0, 52),
		14,
		Ui.Colour.Muted
	)
	hint.LayoutOrder = 200
end

local function done(data: any)
	clear(popupBody)
	local text = Ui.label(
		popupBody,
		"Text",
		`VIP {data.name} hosted! +{Format.cash(data.reward)}\nVIPs today {data.done}/{data.cap}`,
		UDim2.new(1, 0, 0, 70),
		22,
		Ui.Colour.Gold
	)
	text.TextXAlignment = Enum.TextXAlignment.Center
	text.LayoutOrder = 1
	local ok = Ui.button(popupBody, "Ok", "Lovely", UDim2.new(1, 0, 0, 48), function()
		popup.Visible = false
	end, Ui.Colour.Good)
	ok.LayoutOrder = 2
	popup.Visible = true
end

function VipPanel.open()
	window.Visible = true
	sentAt = os.clock()
	draw()
end

function VipPanel.Init()
	local gui = Ui.screen("Vip", 6)
	window, body = Ui.window(gui, "VipPanel", "VIP ledger", UDim2.fromScale(0.62, 0.78), nil, true)
	Ui.list(body, Enum.FillDirection.Vertical, 6)
	popup, popupBody = Ui.window(gui, "VipDone", "VIP hosted", UDim2.fromOffset(400, 220))
	Ui.list(popupBody, Enum.FillDirection.Vertical, 8)
end

function VipPanel.Start()
	Hud.button("VipButton", "👑 VIP", "Left", function()
		if window.Visible then
			window.Visible = false
		else
			VipPanel.open()
		end
	end, 6)
	State.changed:Connect(function()
		sentAt = os.clock()
		if window.Visible then
			draw()
		end
	end)
	Net.listen("Moment", function(kind: string, data: any)
		if kind == "VipLedger" then
			VipPanel.open()
		elseif kind == "VipDone" and typeof(data) == "table" then
			done(data)
		end
	end)
	task.spawn(function()
		while true do
			task.wait(1)
			if window.Visible then
				for _, e in live do
					if e.label.Parent then
						e.label.Text = statusText(e.row)
					end
				end
			end
		end
	end)
end

return VipPanel
