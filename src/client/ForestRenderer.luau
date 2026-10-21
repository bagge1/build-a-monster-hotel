--!strict
--[[
	The forest round Creepy Lane (GDD §5.4, his idea 2026-10-19), drawn by
	each client from `Forest.layout()`, the same seeded scatter everywhere, so
	the server holds no tree and nothing replicates. Purely visual and local:
	nothing reads it back.

	A tree is its template from `ReplicatedStorage.Scenery` (MODELS.md,
	"Street scenery: trees"), or a Luau blockout until the trees are imported.
	Its `Root` is its only collider, so a person walks into the trunk. A tree
	is drawn from its location's set (`Forest.Sets`): its street's, blended
	toward the next street's between two (one world, GDD §3, §6.4). Beyond
	`Forest.ProxyDistance` from the camera a tree is only its `Root` and its
	`LOD_Proxy`, and beyond `Forest.DrawDistance` (past the fog) it is not
	drawn at all: the rest of its model is built when the camera comes near and
	taken away when it goes, `SwapsPerPass` trees a frame, so the long forest
	(his ruling, 2026-10-19 evening) and the world's three streets cost a phone
	little, and a Travel across the world fills in over a few frames. The low
	graphics tier draws `LowGraphics` of the trees.
]]

local Players = game:GetService("Players")
local ReplicatedStorage = game:GetService("ReplicatedStorage")

local Constants = require(ReplicatedStorage.Shared.Constants)
local Forest = require(ReplicatedStorage.Shared.Forest)
local StreetLayout = require(ReplicatedStorage.Shared.StreetLayout)

local F = Constants.Forest

local ForestRenderer = {}

-- How a tree is drawn: whole, its Root and LOD_Proxy only, or not at all.
type Mode = "Near" | "Proxy" | "None"
type Drawn = {
	tree: Forest.Tree,
	model: Model?,
	mode: Mode?,
}

local me = Players.LocalPlayer
local folder: Folder
local drawn: { Drawn } = {}

--[[ Bayou Spa's swamp cypress (Forest.Sets[3]) as a Luau blockout until its
	model is imported (CLAUDE.md, "A blockout in Luau is allowed"): MODELS.md
	"Street scenery: trees"'s parts, so a delivered `Tree_Cypress` replaces it
	and nothing else: `Root` (the collider, bottom at y = 0), `Body` (the
	flared trunk and its knees), `Dark` (the flat crown), `Trim` (hanging
	moss) and a hidden `LOD_Proxy`. Every measurement stays in this function. ]]
local function cypress(part: (string, Vector3, CFrame, Color3, Enum.PartType?) -> Part): Part
	local h = 36
	local root = part("Root", Vector3.new(3, h, 3), CFrame.new(0, h / 2, 0), Color3.new())
	root.Transparency = 1
	local bark = Color3.fromRGB(85, 70, 55)
	-- The flared foot, a short drum standing on end.
	part(
		"Body",
		Vector3.new(4, 4.2, 4.2),
		CFrame.new(0, 2, 0) * CFrame.Angles(0, 0, math.pi / 2),
		bark,
		Enum.PartType.Cylinder
	)
	part("Body", Vector3.new(1.8, h * 0.8, 1.8), CFrame.new(0, h * 0.4, 0), bark)
	for _, a in { 0.6, 2.4, 4.3 } do
		-- Cypress knees round the foot.
		part(
			"Body",
			Vector3.new(0.7, 1.6, 0.7),
			CFrame.new(math.cos(a) * 3.6, 0.8, math.sin(a) * 3.6),
			bark
		)
	end
	local crown = Color3.fromRGB(70, 95, 55)
	part("Dark", Vector3.new(16, 3.5, 13), CFrame.new(0, h * 0.82, 0), crown)
	part("Dark", Vector3.new(10, 3, 9), CFrame.new(1.5, h * 0.92, -1), crown)
	part(
		"Trim",
		Vector3.new(9, 6, 7),
		CFrame.new(-1, h * 0.82 - 4.5, 1),
		Color3.fromRGB(150, 160, 120)
	)
	local proxy = part("LOD_Proxy", Vector3.new(8, h, 8), CFrame.new(0, h / 2, 0), crown)
	proxy.Transparency = 1
	return root
end

-- A Luau blockout of a tree until its model is imported: a trunk and a crown, no attachments to carry.
local function blockout(id: string): Model
	local fir = string.find(id, "Fir") ~= nil
	local h = if fir then 34 else 28
	local m = Instance.new("Model")
	m.Name = id
	local function part(
		name: string,
		size: Vector3,
		at: CFrame,
		colour: Color3,
		shape: Enum.PartType?
	)
		local p = Instance.new("Part")
		p.Name = name
		p.Size = size
		p.CFrame = at
		p.Color = colour
		p.Material = Enum.Material.SmoothPlastic
		if shape then
			p.Shape = shape
		end
		p.Parent = m
		return p
	end
	if id == "Tree_Cypress" then
		local r = cypress(part)
		m.PrimaryPart = r
		r.PivotOffset = CFrame.new(0, -r.Size.Y / 2, 0)
		return m
	end
	local root = part("Root", Vector3.new(1.6, h, 1.6), CFrame.new(0, h / 2, 0), Color3.new())
	root.Transparency = 1
	m.PrimaryPart = root
	root.PivotOffset = CFrame.new(0, -h / 2, 0)
	local bark = Color3.fromRGB(55, 42, 50)
	part("Body", Vector3.new(1.4, h * 0.7, 1.4), CFrame.new(0, h * 0.35, 0), bark)
	if fir then
		local needles = if id == "Tree_SnowFir"
			then Color3.fromRGB(215, 225, 235)
			else Color3.fromRGB(35, 60, 55)
		for i, r in { 7, 5.5, 4 } do
			part(
				"Trim",
				Vector3.new(2 * r, 7, 2 * r),
				CFrame.new(0, 6 + i * 7, 0),
				needles,
				Enum.PartType.Ball
			)
		end
	else
		for i, a in { 35, -40, 20 } do
			part(
				"Body",
				Vector3.new(0.8, 10, 0.8),
				CFrame.new(0, h * (0.45 + 0.15 * i), 0)
					* CFrame.Angles(0, i * 2, math.rad(a))
					* CFrame.new(0, 4, 0),
				bark
			)
		end
	end
	return m
end

local function make(id: string): Model
	local scenery = ReplicatedStorage:FindFirstChild("Scenery")
	local template = scenery and scenery:FindFirstChild(id)
	local m = if template and template:IsA("Model") then template:Clone() else blockout(id)
	local root = m:FindFirstChild("Root")
	if not m.PrimaryPart and root and root:IsA("BasePart") then
		m.PrimaryPart = root -- Rojo's live sync can drop it (DEVNOTES.md)
	end
	for _, p in m:GetDescendants() do
		if p:IsA("BasePart") then
			p.Anchored = true
			local isRoot = p.Name == "Root"
			p.CanCollide = isRoot
			p.CanQuery = false
			p.CanTouch = false
			p.CastShadow = not isRoot and p.Name ~= "LOD_Proxy"
		end
	end
	return m
end

-- The ground under a tree: the first thing a ray down meets, or y = 0.
local function groundAt(p: Vector3): number
	local params = RaycastParams.new()
	params.FilterType = Enum.RaycastFilterType.Exclude
	params.FilterDescendantsInstances = { folder }
	local hit = workspace:Raycast(Vector3.new(p.X, 60, p.Z), Vector3.new(0, -200, 0), params)
	return if hit then hit.Position.Y else 0
end

-- How a tree is drawn from the camera's place: whole within `ProxyDistance`, its proxy within `DrawDistance`.
local function modeFrom(d: Drawn, eye: Vector3?): Mode
	if not eye then
		return "Proxy"
	end
	local p = d.tree.position
	local dist = (Vector3.new(p.X, eye.Y, p.Z) - eye).Magnitude
	return if dist <= F.ProxyDistance
		then "Near"
		elseif dist <= F.DrawDistance then "Proxy"
		else "None"
end

-- Builds a tree: whole near the camera; far, its Root and LOD_Proxy (a tree with no proxy stays whole); past the draw distance, nothing.
local function place(d: Drawn, mode: Mode)
	if d.model then
		d.model:Destroy()
		d.model = nil
	end
	d.mode = mode
	if mode == "None" then
		return
	end
	local far = mode == "Proxy"
	local t = d.tree
	local id = Forest.pickId(t.location, t.pick)
	local m = make(id)
	m:ScaleTo(t.scale)
	-- Planted: the foot's lower lip under the ground, so the trunk rises out of it (a blind review read the
	-- whole foot as a pot), and no root floats on a slope.
	local at = Vector3.new(t.position.X, groundAt(t.position) - 0.6, t.position.Z)
	local cf = CFrame.new(at) * CFrame.Angles(0, t.yaw, 0)
	if Forest.FacesStreet[id] then
		-- Its front toward the nearest point of its street's lane, so the eyes are seen.
		local lane = Constants.Street.LaneHalfLength
		local ox = StreetLayout.originX(StreetLayout.streetAt(at))
		cf = CFrame.lookAt(at, Vector3.new(ox + math.clamp(at.X - ox, -lane, lane), at.Y, 0))
	end
	m:PivotTo(cf)
	local proxy = m:FindFirstChild("LOD_Proxy", true)
	if proxy and proxy:IsA("BasePart") then
		if far then
			for _, p in m:GetDescendants() do
				if p:IsA("BasePart") and p ~= proxy and p.Name ~= "Root" then
					p:Destroy()
				end
			end
		end
		proxy.Transparency = if far then 0 else 1
	end
	m.Parent = folder
	d.model = m
end

local function build()
	for _, d in drawn do
		if d.model then
			d.model:Destroy()
		end
	end
	table.clear(drawn)
	local low = me:GetAttribute("LowGraphics") == true
	local camera = workspace.CurrentCamera
	local eye = camera and camera.CFrame.Position
	local built = 0
	for _, tree in Forest.layout() do
		if tree.low or not low then
			local d: Drawn = { tree = tree, model = nil, mode = nil }
			table.insert(drawn, d)
			local mode = modeFrom(d, eye)
			place(d, mode)
			if mode ~= "None" then
				built += 1
				if built % 40 == 0 then
					task.wait() -- spread over frames: hundreds of trees at once would hitch a phone
				end
			end
		end
	end
end

-- Near trees whole, far trees their proxy, trees past the draw distance none: `SwapsPerPass` rebuilt a frame.
local function lod()
	local camera = workspace.CurrentCamera
	if not camera then
		return
	end
	local swaps = 0
	for _, d in drawn do
		local mode = modeFrom(d, camera.CFrame.Position)
		if mode ~= d.mode then
			place(d, mode)
			swaps += 1
			if swaps % F.SwapsPerPass == 0 then
				task.wait() -- a Travel moves the camera across the world: fill in over frames, never in one
			end
		end
	end
end

function ForestRenderer.Init()
	folder = Instance.new("Folder")
	folder.Name = "Forest"
	folder.Parent = workspace
end

function ForestRenderer.Start()
	task.spawn(function()
		build()
		me:GetAttributeChangedSignal("LowGraphics"):Connect(build)
		while true do
			task.wait(0.5)
			pcall(lod)
		end
	end)
end

return ForestRenderer
