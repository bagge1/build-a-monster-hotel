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

	A rigged model plays its clips (GDD §12, `MonsterAnimator`): Walk while it
	moves, a happy or sad walk out after its stay, CheckIn when the desk sends
	it to its room, Sad while its request waits, Idle otherwise. A model with no
	bones bobs whole, as before.

	A visitor (state `Visiting`, GDD A.13.1) walks as any guest, with its
	activity's icon over its head on the way; at its spot (the path's end) it
	turns to the spot's `Face` and plays its `Pose`'s clip
	(`MonsterMotion.poseClip`, PLACEHOLDER until the poses have clips of their
	own), a swimmer sunk in the water.
]]

local Players = game:GetService("Players")
local ReplicatedStorage = game:GetService("ReplicatedStorage")
local RunService = game:GetService("RunService")

local Net = require(ReplicatedStorage.Shared.Net)
local Species = require(ReplicatedStorage.Shared.Species)
local Walk = require(ReplicatedStorage.Shared.Walk)
local Mutations = require(ReplicatedStorage.Shared.Mutations)
local MonsterMotion = require(ReplicatedStorage.Shared.MonsterMotion)
local MonsterKit = require(script.Parent.MonsterKit)
local MonsterAnimator = require(script.Parent.MonsterAnimator)
local Ui = require(script.Parent.Ui)

local GuestRenderer = {}

local MAX_DRAWN = 40 -- §13.4
local DRAW_RADIUS = 300
--[[ A drawn guest stays drawn until it is clearly out: past the radius by `KEEP_SLACK` studs or
	past the budget by `KEEP_RANKS` (2026-10-26: the 40th and 41st, or a guest pacing the radius,
	were destroyed and rebuilt frame after frame). The budget itself is never exceeded: a newly
	near guest waits for a free place. Not a design value: it changes no limit a player sees. ]]
local KEEP_SLACK = 30
local KEEP_RANKS = 4
GuestRenderer.DrawRadius = DRAW_RADIUS -- the residents' radius too (ResidentRenderer)

type Drawn = {
	config: Configuration,
	model: Model?,
	path: { Vector3 },
	waits: Walk.Waits,
	t0: number,
	speed: number,
	label: TextLabel?,
	prompt: ProximityPrompt?,
	phase: number,
	anim: MonsterAnimator.Animator?,
	state: string?,
	height: number, -- its species' height, for a swimmer's depth (A.13.1)
	pitched: boolean, -- pitched and not refused: kept off the model, which may be rebuilt meanwhile
}

local drawn: { [Configuration]: Drawn } = {}

-- A visitor's icon over its head, by its spot's pose (A.13.1 "Seen"). PLACEHOLDER icons, Claude's.
local POSE_ICON: { [string]: string } = {
	Dance = "💃",
	Swim = "🏊",
	Lift = "💪",
	Play = "🎮",
	Watch = "🎬",
}
local me = Players.LocalPlayer
local folder: Instance

local function readPath(d: Drawn)
	local c = d.config
	d.path, d.waits = Walk.decode(c:GetAttribute("Path") :: string?)
	d.t0 = c:GetAttribute("T0") :: number? or 0
	d.speed = c:GetAttribute("Speed") :: number? or 8
end

-- Where the guest is, which way it faces, and whether it is walking (the server's arithmetic, `Walk`).
local function at(d: Drawn, now: number): (Vector3, Vector3, boolean)
	return Walk.sample(d.path, d.waits, d.speed, now - d.t0)
end

local function labelText(c: Configuration): (string, Color3)
	local state = c:GetAttribute("State")
	local sp = Species.get(c:GetAttribute("Species") :: string)
	local mutation = c:GetAttribute("Mutation") :: string?
	local name = Mutations.prefix(c:GetAttribute("Size") :: string?, mutation)
		.. (if sp then sp.name else "?")
	-- A VIP of a contract (A.11.1): who it is booked to, in gold, whatever it is doing.
	local vipFor = c:GetAttribute("VipFor") :: string?
	if vipFor and not c:GetAttribute("Request") then
		return `👑 VIP for {vipFor}\n{name}{if state == "Queued" then "  ❗" else ""}`,
			Ui.Colour.Gold
	end
	if state == "Browsing" then
		return `{name}\n{c:GetAttribute("Wish") or ""}`,
			if sp and sp.rarity ~= "Common" then Ui.Colour.Gold else Ui.Colour.Text
	elseif c:GetAttribute("Request") then
		return `💬 {c:GetAttribute("Request")}`, Ui.Colour.Pumpkin
	elseif state == "Queued" then
		return `{name}  ❗`, Ui.Colour.Teal
	elseif state == "Visiting" and c:GetAttribute("Pose") then
		return `{POSE_ICON[c:GetAttribute("Pose") :: string] or "✨"} {name}`, Ui.Colour.Text
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
	-- A VIP's glow (A.11.1: "a gold nameplate and a glow (code)").
	local root = d.model.PrimaryPart
	if root and d.config:GetAttribute("VipFor") and not root:FindFirstChild("VipGlow") then
		local light = Instance.new("PointLight")
		light.Name = "VipGlow"
		light.Color = Ui.Colour.Gold
		light.Range = 10
		light.Brightness = 1.5
		light.Parent = root
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
		p.Enabled = not d.pitched
		p.ActionText = if d.pitched then "Pitched!" else "Pitch"
		p.Parent = d.model.PrimaryPart
		p.Triggered:Connect(function()
			Net.send("Pitch", tonumber(d.config.Name) or 0)
			d.pitched = true
			p.Enabled = false
			p.ActionText = "Pitched!"
		end)
		d.prompt = p
	elseif not browsing and d.prompt then
		d.prompt:Destroy()
		d.prompt = nil
	end
	if not browsing then
		d.pitched = false
	end
end

local function spawnModel(d: Drawn)
	local model = MonsterKit.build(
		d.config:GetAttribute("Species") :: string,
		d.config:GetAttribute("Mutation") :: string?,
		d.config:GetAttribute("Size") :: string?
	)
	if not model then
		return
	end
	d.model = model
	local sp = Species.get(d.config:GetAttribute("Species") :: string)
	d.anim = if sp then MonsterAnimator.attach(model, sp.look.shape, sp.look.height) else nil
	d.height = if sp then sp.look.height else 5
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
		waits = {},
		t0 = 0,
		speed = 8,
		label = nil,
		prompt = nil,
		phase = math.random() * 10,
		anim = nil,
		state = c:GetAttribute("State") :: string?,
		height = 5,
		pitched = false,
	}
	drawn[c] = d
	readPath(d)
	c:GetAttributeChangedSignal("Path"):Connect(function()
		readPath(d)
	end)
	c:GetAttributeChangedSignal("T0"):Connect(function()
		readPath(d)
	end)
	c:GetAttributeChangedSignal("State"):Connect(function()
		local state = c:GetAttribute("State") :: string?
		-- The desk sends it to its room: the check-in flourish (§12).
		if d.anim and state == "ToRoom" and d.state == "Queued" then
			MonsterAnimator.play(d.anim, "CheckIn")
		end
		d.state = state
	end)
	for _, a in { "State", "Request", "Wish", "Queue", "VipFor", "Pose" } do
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
		MonsterAnimator.release(d.anim)
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
	-- The low graphics tier draws half as many (§13.4's budget for a low-end phone).
	local cap = if me:GetAttribute("LowGraphics") then MAX_DRAWN // 2 else MAX_DRAWN
	-- First the drawn guests not clearly out, nearest first; then the nearest new ones, into what is free.
	local keep: { [Drawn]: boolean } = {}
	local kept = 0
	for i, entry in order do
		if
			entry.d.model
			and kept < cap
			and i <= cap + KEEP_RANKS
			and entry.dist <= DRAW_RADIUS + KEEP_SLACK
		then
			keep[entry.d] = true
			kept += 1
		end
	end
	for i, entry in order do
		if kept >= cap or i > cap then
			break
		end
		if not entry.d.model and entry.dist <= DRAW_RADIUS then
			keep[entry.d] = true
			kept += 1
		end
	end
	for _, entry in order do
		local d = entry.d
		local show = keep[d] == true
		if show and not d.model then
			spawnModel(d)
		elseif not show and d.model then
			d.model:Destroy()
			d.model = nil
			MonsterAnimator.release(d.anim)
			d.anim = nil
			d.label = nil
			d.prompt = nil
		end
		if d.model then
			local pos, dir, moving = at(d, now)
			-- A visitor at its spot (A.13.1): the spot's pose and the way it faces.
			local c = d.config
			local pose = if not moving and c:GetAttribute("State") == "Visiting"
				then c:GetAttribute("Pose") :: string?
				else nil
			if pose then
				local face = c:GetAttribute("Face")
				if typeof(face) == "Vector3" then
					dir = face
				end
				pos -= Vector3.new(0, MonsterMotion.poseDrop(pose, d.height), 0)
			end
			local anim = d.anim
			local bob = if anim
				then 0 -- its clips carry the bounce
				elseif moving then math.abs(math.sin((now + d.phase) * 8)) * 0.25
				else math.sin((now + d.phase) * 2) * 0.05
			if anim then
				anim.dist = entry.dist
				local mood = if c:GetAttribute("State") == "Leaving"
						and c:GetAttribute("Happy") ~= nil
					then (if c:GetAttribute("Happy") then "Happy" else "Sad")
					else nil
				if moving then
					MonsterAnimator.set(anim, "Walk", d.speed, mood, if mood then 0.35 else 0)
				elseif pose then
					MonsterAnimator.set(anim, MonsterMotion.poseClip(pose))
				elseif c:GetAttribute("Request") then
					MonsterAnimator.set(anim, "Sad")
				else
					MonsterAnimator.set(anim, mood or "Idle")
				end
			end
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
	-- A refused pitch (too far away, BusService) may be tried again: its prompt comes back
	-- (2026-10-26: it stayed "Pitched!" and dead for the guest's whole visit).
	Net.listen("Refused", function(remote: string, _reason: string, guestId: number?)
		if remote ~= "Pitch" or guestId == nil then
			return
		end
		for c, d in drawn do
			if c.Name == tostring(guestId) then
				d.pitched = false
				if d.prompt then
					d.prompt.Enabled = true
					d.prompt.ActionText = "Pitch"
				end
			end
		end
	end)
end

return GuestRenderer
