--!strict
--[[
	The Night Bus as every client sees it (GDD §4.3, §13.2 "Bus model, arrival
	VFX, announcements"): out of the forest round the west bend, to the west
	stop when `workspace.BusArrivedAt` is reached, on to the east stop, and
	round the east bend back into the trees (his ruling, 2026-10-19), along
	`StreetLayout.Route` by `Bus.drive`'s timing, which the server's guests
	step off by. A countdown to `NextBusAt` sits under the HUD.

	A delivered `ReplicatedStorage.Monsters.NightBus` wins (MODELS.md, "Hunters
	and the bus"); until then a Luau blockout. Client-only and read by nothing.
]]

local ReplicatedStorage = game:GetService("ReplicatedStorage")
local RunService = game:GetService("RunService")

local Bus = require(ReplicatedStorage.Shared.Bus)
local Format = require(ReplicatedStorage.Shared.Format)
local StreetLayout = require(ReplicatedStorage.Shared.StreetLayout)
local Ui = require(script.Parent.Ui)

local BusRenderer = {}

local drive = Bus.drive()
local doorAhead = 0 -- how far ahead of the bus's centre its door is: the model's `Door` attachment

local bus: Model?
local countdown: TextLabel

local function part(
	model: Model,
	name: string,
	size: Vector3,
	offset: Vector3,
	colour: Color3,
	material: Enum.Material?
): Part
	local p = Instance.new("Part")
	p.Name = name
	p.Size = size
	p.CFrame = CFrame.new(offset)
	p.Color = colour
	p.Material = material or Enum.Material.SmoothPlastic
	p.Anchored = true
	p.CanCollide = false
	p.CanQuery = false
	p.CanTouch = false
	p.Parent = model
	return p
end

local function build(): Model
	local folder = ReplicatedStorage:FindFirstChild("Monsters")
	local template = folder and folder:FindFirstChild("NightBus")
	if template and template:IsA("Model") then
		local clone = template:Clone()
		local root = clone.PrimaryPart
		local door = root and root:FindFirstChild("Door")
		doorAhead = if door and door:IsA("Attachment") then door.Position.X else 0
		-- A delivered bus brings no lights (MODELS.md: lights are the code's):
		-- its headlamp (`Glow_Warm_2`) gets the blockout's.
		local lamp = clone:FindFirstChild("Glow_Warm_2", true)
		if lamp and lamp:IsA("BasePart") and not lamp:FindFirstChildOfClass("SpotLight") then
			local light = Instance.new("SpotLight")
			light.Range = 40
			light.Brightness = 3
			light.Face = Enum.NormalId.Right
			light.Parent = lamp
		end
		return clone
	end
	doorAhead = 0
	local m = Instance.new("Model")
	m.Name = "NightBus"
	local root = part(m, "Root", Vector3.new(24, 9, 8), Vector3.new(0, 4.5, 0), Color3.new(), nil)
	root.Transparency = 1
	m.PrimaryPart = root
	root.PivotOffset = CFrame.new(0, -4.5, 0)
	part(m, "Body", Vector3.new(24, 7, 8), Vector3.new(0, 5, 0), Color3.fromRGB(80, 50, 120))
	part(m, "Roof", Vector3.new(23, 1, 7.6), Vector3.new(0, 9, 0), Color3.fromRGB(240, 145, 45))
	part(
		m,
		"Glow_Warm_1",
		Vector3.new(20, 2.4, 8.2),
		Vector3.new(-1, 6.2, 0),
		Color3.fromRGB(255, 205, 120),
		Enum.Material.Neon
	)
	for i, x in { -8, 8 } do
		local w = part(
			m,
			`Wheel_{i}`,
			Vector3.new(3, 3, 8.4),
			Vector3.new(x, 1.5, 0),
			Color3.fromRGB(30, 25, 35)
		)
		w.Shape = Enum.PartType.Cylinder
		w.CFrame = CFrame.new(x, 1.5, 0) * CFrame.Angles(0, math.rad(90), 0)
	end
	local lamp = part(
		m,
		"Glow_Warm_2",
		Vector3.new(0.6, 1.2, 1.2),
		Vector3.new(12.2, 3, 2.5),
		Color3.fromRGB(255, 240, 180),
		Enum.Material.Neon
	)
	local light = Instance.new("SpotLight")
	light.Range = 40
	light.Brightness = 3
	light.Face = Enum.NormalId.Right
	light.Parent = lamp
	return m
end

local function busAt(t: number): CFrame?
	-- t: seconds since the bus reached the west stop (negative while it drives in).
	if t < drive.start or t > drive.finish then
		return nil
	end
	local s = drive.at(t) - doorAhead
	local p = StreetLayout.routePoint(s)
	-- Its heading from the road a little behind and ahead, so it swings round a bend, not by the segment.
	local behind = StreetLayout.routePoint(s - 6)
	local ahead = StreetLayout.routePoint(s + 6)
	local d = ahead - behind
	local forward = if d.Magnitude > 0.01 then Vector3.new(d.X, 0, d.Z).Unit else Vector3.xAxis
	-- Authored facing +X (MODELS.md, "NightBus"): a quarter turn from lookAt's −Z.
	return CFrame.lookAt(p, p + forward) * CFrame.Angles(0, math.pi / 2, 0)
end

local function frame()
	local now = workspace:GetServerTimeNow()
	local arrived = workspace:GetAttribute("BusArrivedAt") :: number?
	local nextAt = workspace:GetAttribute("NextBusAt") :: number?
	-- The bus drives in before its guests appear, so it is at the stop when they step off.
	local cf: CFrame? = nil
	if arrived then
		cf = busAt(now - arrived)
	end
	if not cf and nextAt then
		cf = busAt(now - nextAt)
	end
	if cf then
		if not bus then
			bus = build()
			bus.Parent = workspace
		end
		(bus :: Model):PivotTo(cf)
	elseif bus then
		bus:Destroy()
		bus = nil
	end
	if nextAt then
		countdown.Text = `Night Bus in {Format.duration(math.max(0, nextAt - now))}`
	end
end

function BusRenderer.Init()
	local gui = Ui.screen("Hud", 1)
	countdown = Ui.label(gui, "BusCountdown", "", UDim2.fromOffset(260, 26), 18, Ui.Colour.Moon)
	countdown.AnchorPoint = Vector2.new(0.5, 0)
	-- Right under the HUD's top row, wherever that sits.
	Ui.onTopRow(function(up: boolean)
		countdown.Position = UDim2.new(0.5, 0, 0, if up then 4 else 52)
	end)
	countdown.TextXAlignment = Enum.TextXAlignment.Center
	countdown.TextStrokeTransparency = 0.4
end

function BusRenderer.Start()
	RunService.Heartbeat:Connect(frame)
end

return BusRenderer
