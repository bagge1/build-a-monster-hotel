--!strict
--[[
	Hunter Night as every client sees it (GDD §8.1): the hunters walking the
	lane, each with a **Boo!** prompt (a tap on a phone, E on a keyboard, a
	button on a gamepad), and a countdown while the night lasts. Hunters are
	published like guests (`ReplicatedStorage.Hunters`) and drawn locally.

	A delivered `ReplicatedStorage.Monsters.Hunter` wins (MODELS.md, "Hunters
	and the bus"); until then a goofy Luau blockout: a person with a garlic
	necklace and a butterfly net. Read by nothing.
]]

local ReplicatedStorage = game:GetService("ReplicatedStorage")
local RunService = game:GetService("RunService")

local Constants = require(ReplicatedStorage.Shared.Constants)
local Format = require(ReplicatedStorage.Shared.Format)
local Net = require(ReplicatedStorage.Shared.Net)
local Ui = require(script.Parent.Ui)

local HunterRenderer = {}

type Drawn = {
	config: Configuration,
	model: Model,
	path: { Vector3 },
	total: number,
	t0: number,
	speed: number,
}
local drawn: { [Configuration]: Drawn } = {}
local timer: TextLabel

local function part(
	m: Model,
	name: string,
	size: Vector3,
	at: Vector3,
	colour: Color3,
	shape: Enum.PartType?
): Part
	local p = Instance.new("Part")
	p.Name = name
	p.Size = size
	p.CFrame = CFrame.new(at)
	p.Color = colour
	p.Anchored = true
	p.CanCollide = false
	p.CanQuery = false
	p.CanTouch = false
	p.Material = Enum.Material.SmoothPlastic
	if shape then
		p.Shape = shape
	end
	p.Parent = m
	return p
end

local function build(): Model
	local folder = ReplicatedStorage:FindFirstChild("Monsters")
	local t = folder and folder:FindFirstChild("Hunter")
	if t and t:IsA("Model") then
		return t:Clone()
	end
	local m = Instance.new("Model")
	m.Name = "Hunter"
	local root = part(m, "Root", Vector3.new(2, 5, 2), Vector3.new(0, 2.5, 0), Color3.new())
	root.Transparency = 1
	m.PrimaryPart = root
	root.PivotOffset = CFrame.new(0, -2.5, 0)
	part(m, "Legs", Vector3.new(1.6, 2, 0.9), Vector3.new(0, 1, 0), Color3.fromRGB(80, 70, 60))
	part(m, "Body", Vector3.new(2, 2, 1), Vector3.new(0, 3, 0), Color3.fromRGB(90, 130, 80))
	part(
		m,
		"Head",
		Vector3.new(1.2, 1.2, 1.2),
		Vector3.new(0, 4.6, 0),
		Color3.fromRGB(240, 200, 170),
		Enum.PartType.Ball
	)
	part(m, "Hat", Vector3.new(1.6, 0.5, 1.6), Vector3.new(0, 5.3, 0), Color3.fromRGB(110, 80, 50))
	for i = 1, 5 do
		local a = (i - 3) * 0.35
		part(
			m,
			`Garlic_{i}`,
			Vector3.one * 0.4,
			Vector3.new(math.sin(a) * 0.9, 3.7 - math.abs(i - 3) * 0.15, -0.55),
			Color3.fromRGB(245, 240, 220),
			Enum.PartType.Ball
		)
	end
	part(
		m,
		"NetPole",
		Vector3.new(0.2, 4, 0.2),
		Vector3.new(1.3, 4, -0.3),
		Color3.fromRGB(150, 110, 70)
	)
	local ring = part(
		m,
		"NetRing",
		Vector3.new(0.2, 1.8, 1.8),
		Vector3.new(1.3, 6.2, -0.3),
		Color3.fromRGB(230, 230, 240),
		Enum.PartType.Cylinder
	)
	ring.Transparency = 0.4
	local plate = Instance.new("Attachment")
	plate.Name = "Nameplate"
	plate.Position = Vector3.new(0, 4, 0)
	plate.Parent = root
	return m
end

local function read(d: Drawn)
	local c = d.config
	d.path = {}
	for _, chunk in string.split(c:GetAttribute("Path") :: string? or "", ";") do
		local xyz = string.split(chunk, ",")
		if #xyz == 3 then
			table.insert(
				d.path,
				Vector3.new(tonumber(xyz[1]) or 0, tonumber(xyz[2]) or 0, tonumber(xyz[3]) or 0)
			)
		end
	end
	d.t0 = c:GetAttribute("T0") :: number? or 0
	d.speed = c:GetAttribute("Speed") :: number? or 8
	d.total = 0
	for i = 2, #d.path do
		d.total += (d.path[i] - d.path[i - 1]).Magnitude
	end
	local prompt = d.model.PrimaryPart
		and d.model.PrimaryPart:FindFirstChild("Boo") :: ProximityPrompt?
	if prompt then
		prompt.Enabled = c:GetAttribute("State") == "Approach"
	end
end

local function add(c: Instance)
	if not c:IsA("Configuration") then
		return
	end
	local model = build()
	local prompt = Instance.new("ProximityPrompt")
	prompt.Name = "Boo"
	prompt.ActionText = "Boo!"
	prompt.ObjectText = "Hunter"
	prompt.KeyboardKeyCode = Enum.KeyCode.E
	prompt.MaxActivationDistance = Constants.HunterNight.BooRange
	prompt.RequiresLineOfSight = false
	prompt.Parent = model.PrimaryPart
	prompt.Triggered:Connect(function()
		Net.send("Boo", tonumber(c.Name) or 0)
	end)
	model.Parent = workspace
	local d: Drawn = { config = c, model = model, path = {}, total = 0, t0 = 0, speed = 8 }
	drawn[c] = d
	read(d)
	c:GetAttributeChangedSignal("T0"):Connect(function()
		read(d)
	end)
end

local function remove(c: Instance)
	local d = drawn[c :: Configuration]
	if d then
		d.model:Destroy()
		drawn[c :: Configuration] = nil
	end
end

local function frame()
	local now = workspace:GetServerTimeNow()
	for _, d in drawn do
		local travelled = math.clamp((now - d.t0) * d.speed, 0, d.total)
		local pos, dir = d.path[1] or Vector3.zero, Vector3.new(-1, 0, 0)
		for i = 2, #d.path do
			local seg = (d.path[i] - d.path[i - 1]).Magnitude
			if travelled <= seg then
				pos = d.path[i - 1]:Lerp(d.path[i], if seg > 0 then travelled / seg else 1)
				dir = d.path[i] - d.path[i - 1]
				break
			end
			travelled -= seg
			pos = d.path[i]
		end
		local flat = Vector3.new(dir.X, 0, dir.Z)
		local look = if flat.Magnitude > 0.01 then flat.Unit else Vector3.new(-1, 0, 0)
		local bob = math.abs(math.sin(now * 9)) * 0.3
		d.model:PivotTo(
			CFrame.lookAt(pos + Vector3.new(0, bob, 0), pos + Vector3.new(0, bob, 0) + look)
		)
	end
	local untilT = workspace:GetAttribute("HunterNightUntil") :: number?
	timer.Visible = untilT ~= nil
	if untilT then
		timer.Text =
			`Hunter Night! {Format.duration(math.max(0, untilT - now))}  ·  get close and Boo! them`
	end
end

function HunterRenderer.Init()
	local gui = Ui.screen("Hud", 1)
	timer = Ui.label(gui, "HunterTimer", "", UDim2.fromOffset(420, 26), 18, Ui.Colour.Bad)
	timer.AnchorPoint = Vector2.new(0.5, 0)
	timer.Position = UDim2.new(0.5, 0, 0, 244)
	timer.TextXAlignment = Enum.TextXAlignment.Center
	timer.TextStrokeTransparency = 0.3
	timer.Visible = false
end

function HunterRenderer.Start()
	local folder = ReplicatedStorage:WaitForChild("Hunters")
	for _, c in folder:GetChildren() do
		add(c)
	end
	folder.ChildAdded:Connect(add)
	folder.ChildRemoved:Connect(remove)
	RunService.Heartbeat:Connect(frame)
end

return HunterRenderer
