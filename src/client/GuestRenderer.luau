--!strict
--[[
	Draws every guest on the street (GDD §13.2: the client paints). The server
	publishes each guest as a Configuration in `ReplicatedStorage.Guests` with
	its path and the server time it started walking; this clones its model
	(`MonsterKit`) and moves it along the path by the same arithmetic the
	server uses, every frame, locally. Nothing here is read back.

	Over each guest: its wish list while it browses (§4.3), its request (§4.4),
	"!" while it waits at the desk. A browsing guest carries a **Pitch** prompt
	(§4.3: "press E, tap, or a gamepad button").

	The render budget (§13.4): at most `MAX_DRAWN` guests, the nearest first.
]]

local Players = game:GetService("Players")
local ReplicatedStorage = game:GetService("ReplicatedStorage")
local RunService = game:GetService("RunService")

local Net = require(ReplicatedStorage.Shared.Net)
local Species = require(ReplicatedStorage.Shared.Species)
local Mutations = require(ReplicatedStorage.Shared.Mutations)
local MonsterKit = require(script.Parent.MonsterKit)
local Ui = require(script.Parent.Ui)

local GuestRenderer = {}

local MAX_DRAWN = 40 -- §13.4
local DRAW_RADIUS = 300

type Drawn = {
	config: Configuration,
	model: Model?,
	path: { Vector3 },
	lengths: { number },
	total: number,
	t0: number,
	speed: number,
	label: TextLabel?,
	prompt: ProximityPrompt?,
	phase: number,
}

local drawn: { [Configuration]: Drawn } = {}
local me = Players.LocalPlayer
local folder: Instance

local function parse(s: string?): { Vector3 }
	local out = {}
	if not s or s == "" then
		return out
	end
	for _, chunk in string.split(s, ";") do
		local xyz = string.split(chunk, ",")
		table.insert(
			out,
			Vector3.new(tonumber(xyz[1]) or 0, tonumber(xyz[2]) or 0, tonumber(xyz[3]) or 0)
		)
	end
	return out
end

local function readPath(d: Drawn)
	local c = d.config
	d.path = parse(c:GetAttribute("Path") :: string?)
	d.t0 = c:GetAttribute("T0") :: number? or 0
	d.speed = c:GetAttribute("Speed") :: number? or 8
	d.lengths = {}
	d.total = 0
	for i = 2, #d.path do
		local l = (d.path[i] - d.path[i - 1]).Magnitude
		d.lengths[i] = l
		d.total += l
	end
end

local function at(d: Drawn, now: number): (Vector3, Vector3)
	local path = d.path
	if #path == 0 then
		return Vector3.zero, Vector3.new(0, 0, -1)
	end
	local travelled = math.clamp((now - d.t0) * d.speed, 0, d.total)
	for i = 2, #path do
		local l = d.lengths[i]
		if travelled <= l then
			local dir = path[i] - path[i - 1]
			return path[i - 1]:Lerp(path[i], if l > 0 then travelled / l else 1),
				if dir.Magnitude > 0.01 then dir.Unit else Vector3.new(0, 0, -1)
		end
		travelled -= l
	end
	local last = path[#path]
	local prev = if #path > 1 then path[#path - 1] else last
	local dir = last - prev
	return last, if dir.Magnitude > 0.01 then dir.Unit else Vector3.new(0, 0, -1)
end

local function labelText(c: Configuration): (string, Color3)
	local state = c:GetAttribute("State")
	local sp = Species.get(c:GetAttribute("Species") :: string)
	local mutation = c:GetAttribute("Mutation") :: string?
	local name = (if mutation then Mutations.ById[mutation].name .. " " else "")
		.. (if sp then sp.name else "?")
	if state == "Browsing" then
		return `{name}\n{c:GetAttribute("Wish") or ""}`,
			if sp and sp.rarity ~= "Common" then Ui.Colour.Gold else Ui.Colour.Text
	elseif c:GetAttribute("Request") then
		return `💬 {c:GetAttribute("Request")}`, Ui.Colour.Pumpkin
	elseif state == "Queued" then
		return `{name}  ❗`, Ui.Colour.Teal
	end
	return name, Ui.Colour.Muted
end

local function makeLabel(model: Model): TextLabel?
	local root = model.PrimaryPart
	local plate = root and root:FindFirstChild("Nameplate")
	if not plate then
		return nil
	end
	local bb = Instance.new("BillboardGui")
	bb.Name = "Label"
	bb.Size = UDim2.fromOffset(220, 56)
	bb.StudsOffset = Vector3.new(0, 0.5, 0)
	bb.MaxDistance = 90
	bb.LightInfluence = 0
	bb.Adornee = plate :: Attachment
	local l = Ui.label(bb, "Text", "", UDim2.fromScale(1, 1), 16)
	l.TextXAlignment = Enum.TextXAlignment.Center
	l.TextStrokeTransparency = 0.3
	l.TextScaled = true
	bb.Parent = model
	return l
end

local function refreshDecor(d: Drawn)
	if not d.model then
		return
	end
	if d.label then
		local text, colour = labelText(d.config)
		d.label.Text = text
		d.label.TextColor3 = colour
	end
	local browsing = d.config:GetAttribute("State") == "Browsing"
	if browsing and not d.prompt and d.model.PrimaryPart then
		local p = Instance.new("ProximityPrompt")
		p.Name = "Pitch"
		p.ActionText = "Pitch"
		p.ObjectText = "Invite to your hotel"
		p.KeyboardKeyCode = Enum.KeyCode.E
		p.MaxActivationDistance = 12
		p.RequiresLineOfSight = false
		p.Parent = d.model.PrimaryPart
		p.Triggered:Connect(function()
			Net.send("Pitch", tonumber(d.config.Name) or 0)
			p.Enabled = false
			p.ActionText = "Pitched!"
		end)
		d.prompt = p
	elseif not browsing and d.prompt then
		d.prompt:Destroy()
		d.prompt = nil
	end
end

local function spawnModel(d: Drawn)
	local model = MonsterKit.build(
		d.config:GetAttribute("Species") :: string,
		d.config:GetAttribute("Mutation") :: string?
	)
	if not model then
		return
	end
	d.model = model
	d.label = makeLabel(model)
	model.Parent = workspace:FindFirstChild("ClientGuests")
		or (function()
			local f = Instance.new("Folder")
			f.Name = "ClientGuests"
			f.Parent = workspace
			return f
		end)()
	refreshDecor(d)
end

local function add(c: Instance)
	if not c:IsA("Configuration") or drawn[c] then
		return
	end
	local d: Drawn = {
		config = c,
		model = nil,
		path = {},
		lengths = {},
		total = 0,
		t0 = 0,
		speed = 8,
		label = nil,
		prompt = nil,
		phase = math.random() * 10,
	}
	drawn[c] = d
	readPath(d)
	c:GetAttributeChangedSignal("Path"):Connect(function()
		readPath(d)
	end)
	c:GetAttributeChangedSignal("T0"):Connect(function()
		readPath(d)
	end)
	for _, a in { "State", "Request", "Wish", "Queue" } do
		c:GetAttributeChangedSignal(a):Connect(function()
			refreshDecor(d)
		end)
	end
end

local function remove(c: Instance)
	local d = drawn[c :: Configuration]
	if d then
		if d.model then
			d.model:Destroy()
		end
		drawn[c :: Configuration] = nil
	end
end

local function frame()
	local now = workspace:GetServerTimeNow()
	local character = me.Character
	local camera = workspace.CurrentCamera
	local eye = if camera
		then camera.CFrame.Position
		elseif character then character:GetPivot().Position
		else Vector3.zero
	-- Nearest first, within the budget.
	local order = {}
	for _, d in drawn do
		local pos = at(d, now)
		table.insert(order, { d = d, dist = (pos - eye).Magnitude, pos = pos })
	end
	table.sort(order, function(a, b)
		return a.dist < b.dist
	end)
	for i, entry in order do
		local d = entry.d
		local show = i <= MAX_DRAWN and entry.dist <= DRAW_RADIUS
		if show and not d.model then
			spawnModel(d)
		elseif not show and d.model then
			d.model:Destroy()
			d.model = nil
			d.label = nil
			d.prompt = nil
		end
		if d.model then
			local pos, dir = at(d, now)
			local moving = (now - d.t0) * d.speed < d.total
			local bob = if moving
				then math.abs(math.sin((now + d.phase) * 8)) * 0.25
				else math.sin((now + d.phase) * 2) * 0.05
			local flat = Vector3.new(dir.X, 0, dir.Z)
			local look = if flat.Magnitude > 0.01 then flat.Unit else Vector3.new(0, 0, -1)
			d.model:PivotTo(
				CFrame.lookAt(pos + Vector3.new(0, bob, 0), pos + Vector3.new(0, bob, 0) + look)
			)
		end
	end
end

function GuestRenderer.Init() end

function GuestRenderer.Start()
	folder = ReplicatedStorage:WaitForChild("Guests")
	for _, c in folder:GetChildren() do
		add(c)
	end
	folder.ChildAdded:Connect(add)
	folder.ChildRemoved:Connect(remove)
	RunService.Heartbeat:Connect(frame)
end

return GuestRenderer
