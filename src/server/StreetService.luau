--!strict
--[[
	Creepy Lane itself (GDD §3, §5.4): the lane, the pavements along both its
	edges, the two bus stops, the lamps, and the road that runs on from each
	end of the lane round a bend into the forest (the bus drives in out of the
	trees, his ruling 2026-10-19). Built once, on the server, in
	`workspace.Street`; every measurement is `StreetLayout`'s. The plots are
	`PlotService`'s, the forest is drawn by each client (`ForestRenderer`).

	The street's surfaces are a Luau blockout (CLAUDE.md, "A blockout in Luau
	is allowed"): flat slabs and posts, nothing a guest path or the bus reads
	back. The lighting and the night ground are set here too.
]]

local Lighting = game:GetService("Lighting")
local ReplicatedStorage = game:GetService("ReplicatedStorage")

local Constants = require(ReplicatedStorage.Shared.Constants)
local StreetLayout = require(ReplicatedStorage.Shared.StreetLayout)

local G = Constants.Grid
local S = Constants.Street

local StreetService = {}

local LANE = Color3.fromRGB(75, 70, 90)
local PAVEMENT = Color3.fromRGB(105, 98, 122)
local KERB = Color3.fromRGB(120, 110, 140)

local function block(
	parent: Instance,
	name: string,
	size: Vector3,
	at: CFrame,
	colour: Color3,
	material: Enum.Material?
): Part
	local p = Instance.new("Part")
	p.Name = name
	p.Anchored = true
	p.Size = size
	p.CFrame = at
	p.Color = colour
	p.Material = material or Enum.Material.Cobblestone
	p.TopSurface = Enum.SurfaceType.Smooth
	p.BottomSurface = Enum.SurfaceType.Smooth
	p.Parent = parent
	return p
end

local function lamp(parent: Instance, at: Vector3)
	local post = block(
		parent,
		"LampPost",
		Vector3.new(0.6, 10, 0.6),
		CFrame.new(at + Vector3.new(0, 5, 0)),
		Color3.fromRGB(40, 35, 50),
		Enum.Material.Metal
	)
	post.CanCollide = true
	local bulb = block(
		parent,
		"Glow_Warm_1",
		Vector3.new(1.4, 1.4, 1.4),
		CFrame.new(at + Vector3.new(0, 10.5, 0)),
		Color3.fromRGB(255, 190, 110),
		Enum.Material.Neon
	)
	bulb.Shape = Enum.PartType.Ball
	bulb.CanCollide = false
	local light = Instance.new("PointLight")
	light.Range = 24
	light.Brightness = 0.9
	light.Color = Color3.fromRGB(255, 190, 120)
	light.Parent = bulb
end

-- A stop (§3): a shelter in the gap between two plots, behind the pavement, open to it.
local function shelter(parent: Instance, stop: StreetLayout.Stop)
	local y = StreetLayout.GroundY
	local back = S.LaneHalfWidth + S.PavementWidth -- the pavement's far edge
	local model = Instance.new("Model")
	model.Name = `BusStop_{stop.name}`
	local wood = Color3.fromRGB(70, 50, 75)
	local roof = Color3.fromRGB(240, 145, 45)
	local w, d, h = 12, 4, 8
	local cz = back + d / 2
	-- Its floor stands on the ground between the plots, up to the pavement's height and a step.
	block(
		model,
		"Floor",
		Vector3.new(w, y + 0.3, d),
		CFrame.new(stop.x, (y + 0.3) / 2, cz),
		PAVEMENT,
		Enum.Material.Pavement
	)
	block(
		model,
		"Back",
		Vector3.new(w, h, 0.4),
		CFrame.new(stop.x, y + 0.3 + h / 2, back + d - 0.2),
		wood,
		Enum.Material.WoodPlanks
	)
	for _, side in { -1, 1 } do
		block(
			model,
			"Side",
			Vector3.new(0.4, h, d),
			CFrame.new(stop.x + side * (w / 2 - 0.2), y + 0.3 + h / 2, cz),
			wood,
			Enum.Material.WoodPlanks
		)
	end
	block(
		model,
		"Roof",
		Vector3.new(w + 1, 0.5, d + 2),
		CFrame.new(stop.x, y + 0.3 + h + 0.25, cz - 1),
		roof,
		Enum.Material.SmoothPlastic
	)
	block(
		model,
		"Bench",
		Vector3.new(w - 2, 1.8, 1.4),
		CFrame.new(stop.x, y + 0.3 + 0.9, back + d - 1.1),
		Color3.fromRGB(90, 60, 45),
		Enum.Material.WoodPlanks
	)
	-- The sign on its pole at the kerb, ahead of where the bus's door stops.
	block(
		model,
		"SignPole",
		Vector3.new(0.6, 9, 0.6),
		CFrame.new(stop.x + 5, y + 4.5, S.LaneHalfWidth + 1),
		Color3.fromRGB(60, 50, 70),
		Enum.Material.Metal
	)
	local sign = block(
		model,
		"Sign",
		Vector3.new(3, 3, 0.3),
		CFrame.new(stop.x + 5, y + 9.5, S.LaneHalfWidth + 1),
		roof,
		Enum.Material.SmoothPlastic
	)
	local gui = Instance.new("SurfaceGui")
	gui.Face = Enum.NormalId.Front
	gui.LightInfluence = 0
	gui.CanvasSize = Vector2.new(120, 120)
	local text = Instance.new("TextLabel")
	text.Size = UDim2.fromScale(1, 1)
	text.BackgroundTransparency = 1
	text.Text = "BUS"
	text.Font = Enum.Font.FredokaOne
	text.TextScaled = true
	text.TextColor3 = Color3.fromRGB(46, 32, 70)
	text.Parent = gui
	gui.Parent = sign
	sign:SetAttribute("BusStop", stop.name)
	model.Parent = parent
end

-- The road off each end of the lane: slabs along the route, a disc under each joint to close the bend's gaps.
local function road(parent: Instance)
	local route = StreetLayout.Route
	local th = G.SlabThickness
	local width = StreetLayout.RoadWidth
	local folder = Instance.new("Folder")
	folder.Name = "Road"
	local laneEnd = S.LaneHalfLength + 20
	for i = 2, #route do
		local a, b = route[i - 1], route[i]
		-- The lane's own slab covers its straight.
		if not (math.abs(a.X) <= laneEnd + 0.01 and math.abs(b.X) <= laneEnd + 0.01) then
			local mid = (a + b) / 2
			local len = (b - a).Magnitude
			block(
				folder,
				"Road",
				Vector3.new(width, th, len),
				CFrame.lookAt(Vector3.new(mid.X, th / 2, mid.Z), Vector3.new(b.X, th / 2, b.Z)),
				LANE
			)
			if i < #route then
				local disc = block(
					folder,
					"RoadJoint",
					Vector3.new(th - 0.06, width, width),
					CFrame.new(b.X, (th - 0.06) / 2, b.Z) * CFrame.Angles(0, 0, math.pi / 2),
					LANE
				)
				disc.Shape = Enum.PartType.Cylinder
			end
		end
	end
	folder.Parent = parent
end

local function build()
	local old = workspace:FindFirstChild("Street")
	if old then
		old:Destroy()
	end
	local street = Instance.new("Folder")
	street.Name = "Street"
	local half = S.LaneHalfLength
	local th = G.SlabThickness
	local lane = S.LaneHalfWidth
	local length = 2 * half + 40
	block(street, "Lane", Vector3.new(length, th, 2 * lane), CFrame.new(0, th / 2, 0), LANE)
	for _, side in { 1, -1 } do
		local tag = if side == 1 then "North" else "South"
		block(
			street,
			`Kerb_{tag}`,
			Vector3.new(length, 0.3, 1),
			CFrame.new(0, th + 0.15, side * (lane - 0.5)),
			KERB,
			Enum.Material.SmoothPlastic
		)
		-- The pavement (§5.4): the forecourt's first 8 studs, one strip the length of the lane.
		local pavement = block(
			street,
			`Pavement_{tag}`,
			Vector3.new(length, th, S.PavementWidth),
			CFrame.new(0, th / 2, side * (lane + S.PavementWidth / 2)),
			PAVEMENT,
			Enum.Material.Pavement
		)
		pavement:SetAttribute("Pavement", true)
	end
	for _, stop in StreetLayout.Stops do
		shelter(street, stop)
	end
	-- Lamps on the pavements' kerb side: six to a plot's pitch, a pair flanking each entrance.
	local step = (StreetLayout.PlotSize + S.PlotGap) / 6
	for x = -math.floor((half - step / 2) / step) * step - step / 2, half, step do
		for _, side in { 1, -1 } do
			lamp(street, Vector3.new(x, th, side * (lane + 1)))
		end
	end
	road(street)
	street.Parent = workspace

	-- Cozy-creepy night (GDD §12): moonlight blue and purple, never black.
	Lighting.ClockTime = 0.5
	Lighting.Brightness = 2
	Lighting.Ambient = Color3.fromRGB(105, 95, 140)
	Lighting.OutdoorAmbient = Color3.fromRGB(125, 115, 165)
	Lighting.FogColor = Color3.fromRGB(40, 30, 70)
	Lighting.FogStart = 250
	Lighting.FogEnd = 900
	-- The place's own spawn and baseplate stay; the baseplate becomes night ground.
	local baseplate = workspace:FindFirstChild("Baseplate")
	if baseplate and baseplate:IsA("BasePart") then
		baseplate.Color = Color3.fromRGB(45, 55, 50)
		baseplate.Material = Enum.Material.Grass
	end
end

function StreetService.Init()
	build()
end

function StreetService.Start() end

return StreetService
