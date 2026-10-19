--!strict
--[[
	The Night Bus as every client sees it (GDD §4.3, §13.2 "Bus model, arrival
	VFX, announcements"): it drives in from the west when `workspace.BusArrivedAt`
	changes, waits at the stop while its guests step off, and drives on east.
	A countdown to `NextBusAt` sits under the HUD.

	A delivered `ReplicatedStorage.Monsters.NightBus` wins (MODELS.md, "Hunters
	and the bus"); until then a Luau blockout. Client-only and read by nothing.
]]

local ReplicatedStorage = game:GetService("ReplicatedStorage")
local RunService = game:GetService("RunService")

local Format = require(ReplicatedStorage.Shared.Format)
local StreetLayout = require(ReplicatedStorage.Shared.StreetLayout)
local Ui = require(script.Parent.Ui)

local BusRenderer = {}

local IN_TIME, STOP_TIME, OUT_TIME = 3, 7, 6
local LANE_Z = -15

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
		local bus = template:Clone()
		-- A delivered bus brings no lights (MODELS.md: lights are the code's):
		-- its headlamp (`Glow_Warm_2`) gets the blockout's.
		local lamp = bus:FindFirstChild("Glow_Warm_2", true)
		if lamp and lamp:IsA("BasePart") and not lamp:FindFirstChildOfClass("SpotLight") then
			local light = Instance.new("SpotLight")
			light.Range = 40
			light.Brightness = 3
			light.Face = Enum.NormalId.Right
			light.Parent = lamp
		end
		return bus
	end
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
	-- t: seconds since the bus arrived at the stop.
	local stop = StreetLayout.BusStop
	local y = stop.Y
	local function at(x: number): CFrame
		return CFrame.new(x, y, LANE_Z) -- authored facing +X, the way it drives
	end
	if t < -IN_TIME then
		return nil
	elseif t < 0 then
		local a = 1 + t / IN_TIME -- 0..1
		local eased = 1 - (1 - a) ^ 2
		return at(stop.X - 120 + 120 * eased)
	elseif t < STOP_TIME then
		return at(stop.X)
	elseif t < STOP_TIME + OUT_TIME then
		local a = (t - STOP_TIME) / OUT_TIME
		return at(stop.X + 420 * a * a)
	end
	return nil
end

local function frame()
	local now = workspace:GetServerTimeNow()
	local arrived = workspace:GetAttribute("BusArrivedAt") :: number?
	local nextAt = workspace:GetAttribute("NextBusAt") :: number?
	-- The bus is drawn arriving IN_TIME before its guests appear, so it is there when they step off.
	local cf: CFrame? = nil
	if arrived then
		cf = busAt(now - arrived)
	end
	if not cf and nextAt and nextAt - now < IN_TIME then
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
	countdown.Position = UDim2.new(0.5, 0, 0, 52)
	countdown.TextXAlignment = Enum.TextXAlignment.Center
	countdown.TextStrokeTransparency = 0.4
end

function BusRenderer.Start()
	RunService.Heartbeat:Connect(frame)
end

return BusRenderer
