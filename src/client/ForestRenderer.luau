--!strict
--[[
	The forest round Creepy Lane (GDD §5.4, his idea 2026-10-19), drawn by
	each client from `Forest.layout()`, the same seeded scatter everywhere, so
	the server holds no tree and nothing replicates. Purely visual and local:
	nothing reads it back.

	A tree is its template from `ReplicatedStorage.Scenery` (MODELS.md,
	"Street scenery: trees"), or a Luau blockout until the trees are imported.
	Its `Root` is its only collider, so a person walks into the trunk. A tree
	behind a plot is drawn from that plot's location's set (`Forest.Sets`),
	and redrawn when the plot changes hands or location. Beyond
	`Forest.ProxyDistance` from the camera a tree shows its `LOD_Proxy`
	instead; the low graphics tier draws `LowGraphics` of the trees.
]]

local Players = game:GetService("Players")
local ReplicatedStorage = game:GetService("ReplicatedStorage")

local Constants = require(ReplicatedStorage.Shared.Constants)
local Forest = require(ReplicatedStorage.Shared.Forest)

local F = Constants.Forest

local ForestRenderer = {}

type Drawn = {
	tree: Forest.Tree,
	model: Model?,
	proxy: BasePart?,
	shown: { BasePart }, -- the parts drawn near (all but Root and LOD_Proxy)
	far: boolean?,
}

local me = Players.LocalPlayer
local folder: Folder
local drawn: { Drawn } = {}
local zoneLocation: { [number]: number } = {}

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

local function place(d: Drawn)
	if d.model then
		d.model:Destroy()
		d.model = nil
	end
	local t = d.tree
	local id = Forest.pickId(zoneLocation[t.zone] or 1, t.pick)
	local m = make(id)
	m:ScaleTo(t.scale)
	-- Planted: the foot's lower lip under the ground, so the trunk rises out of it (a blind review read the
	-- whole foot as a pot), and no root floats on a slope.
	local at = Vector3.new(t.position.X, groundAt(t.position) - 0.6, t.position.Z)
	local cf = CFrame.new(at) * CFrame.Angles(0, t.yaw, 0)
	if Forest.FacesStreet[id] then
		-- Its front toward the nearest point of the lane, so the eyes are seen.
		local lane = Constants.Street.LaneHalfLength
		cf = CFrame.lookAt(at, Vector3.new(math.clamp(at.X, -lane, lane), at.Y, 0))
	end
	m:PivotTo(cf)
	d.proxy = nil
	d.shown = {}
	d.far = nil
	for _, p in m:GetDescendants() do
		if p:IsA("BasePart") then
			if p.Name == "LOD_Proxy" then
				d.proxy = p
			elseif p.Name ~= "Root" then
				table.insert(d.shown, p)
			end
		end
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
	for i, tree in Forest.layout() do
		if tree.low or not low then
			local d: Drawn = { tree = tree, model = nil, proxy = nil, shown = {}, far = nil }
			table.insert(drawn, d)
			place(d)
			if i % 40 == 0 then
				task.wait() -- spread over frames: hundreds of trees at once would hitch a phone
			end
		end
	end
end

-- Near trees whole, far trees their proxy (a tree with no proxy stays whole).
local function lod()
	local camera = workspace.CurrentCamera
	if not camera then
		return
	end
	local eye = camera.CFrame.Position
	for _, d in drawn do
		local proxy = d.proxy
		if proxy then
			local p = d.tree.position
			local far = (Vector3.new(p.X, eye.Y, p.Z) - eye).Magnitude > F.ProxyDistance
			if far ~= d.far then
				d.far = far
				proxy.Transparency = if far then 0 else 1
				for _, part in d.shown do
					part.Transparency = if far then 1 else 0
				end
			end
		end
	end
end

-- A plot's location decides its zone's trees: redraw them when it changes.
local function watchPlot(plot: Instance)
	local index = plot:GetAttribute("Index")
	if typeof(index) ~= "number" then
		return
	end
	local function update()
		local location = plot:GetAttribute("Location")
		local loc = if typeof(location) == "number" then location else 1
		if zoneLocation[index] ~= loc then
			zoneLocation[index] = loc
			for _, d in drawn do
				if d.tree.zone == index then
					place(d)
				end
			end
		end
	end
	plot:GetAttributeChangedSignal("Location"):Connect(update)
	update()
end

function ForestRenderer.Init()
	folder = Instance.new("Folder")
	folder.Name = "Forest"
	folder.Parent = workspace
end

function ForestRenderer.Start()
	task.spawn(function()
		local plots = workspace:WaitForChild("Plots", 30)
		if plots then
			for _, plot in plots:GetChildren() do
				watchPlot(plot)
			end
			plots.ChildAdded:Connect(watchPlot) -- a plot streamed in later
		end
		build()
		me:GetAttributeChangedSignal("LowGraphics"):Connect(build)
		while true do
			task.wait(2)
			pcall(lod)
		end
	end)
end

return ForestRenderer
