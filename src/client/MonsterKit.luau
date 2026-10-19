--!strict
--[[
	A monster to draw (MODELS.md, "Monsters and street NPCs"). A delivered
	model wins: `ReplicatedStorage.Monsters.<SpeciesId>` is cloned when it
	exists. Until the monsters are modelled (WAITING.md §0), this builds a
	**Luau blockout** from the species' `look` (CLAUDE.md, "A blockout in Luau
	is allowed"): a few shapes in its colour at its height against the 5-stud
	person, carrying the contract's `Root`, `Body`, `Glow_Eyes_1` and
	`Nameplate`. Every measurement of the blockout stays in this file.

	Client-only: these are visuals nothing reads (GDD §13.2). Nothing
	collides, is queried or is touched.
]]

local ReplicatedStorage = game:GetService("ReplicatedStorage")

local Species = require(ReplicatedStorage.Shared.Species)
local Mutations = require(ReplicatedStorage.Shared.Mutations)

local MonsterKit = {}

local function part(
	model: Model,
	name: string,
	size: Vector3,
	offset: Vector3,
	colour: Color3,
	shape: Enum.PartType?
): Part
	local p = Instance.new("Part")
	p.Name = name
	p.Size = size
	p.CFrame = CFrame.new(offset)
	p.Color = colour
	p.Material = Enum.Material.SmoothPlastic
	p.Anchored = true
	p.CanCollide = false
	p.CanQuery = false
	p.CanTouch = false
	p.CastShadow = false
	if shape then
		p.Shape = shape
	end
	p.Parent = model
	return p
end

local function blockout(sp: Species.Species): Model
	local model = Instance.new("Model")
	model.Name = sp.id
	local h = sp.look.height
	local c = sp.look.colour
	local eyes = sp.look.eyes or Color3.fromRGB(255, 255, 255)
	local root = part(model, "Root", Vector3.new(2, h, 2), Vector3.new(0, h / 2, 0), c)
	root.Transparency = 1
	model.PrimaryPart = root
	root.PivotOffset = CFrame.new(0, -h / 2, 0)

	local eyeY, eyeZ, eyeGap
	if sp.look.shape == "Blob" then
		part(
			model,
			"Body",
			Vector3.new(h * 1.1, h * 0.85, h * 1.1),
			Vector3.new(0, h * 0.42, 0),
			c,
			Enum.PartType.Ball
		)
		eyeY, eyeZ, eyeGap = h * 0.55, -h * 0.5, h * 0.2
	elseif sp.look.shape == "Float" then
		local body = part(
			model,
			"Body",
			Vector3.new(h * 0.6, h * 0.7, h * 0.6),
			Vector3.new(0, h * 0.62, 0),
			c,
			Enum.PartType.Ball
		)
		body.Transparency = 0.15
		local tail = part(
			model,
			"Tail",
			Vector3.new(h * 0.4, h * 0.45, h * 0.4),
			Vector3.new(0, h * 0.25, 0.1),
			c,
			Enum.PartType.Ball
		)
		tail.Transparency = 0.3
		eyeY, eyeZ, eyeGap = h * 0.7, -h * 0.28, h * 0.14
	elseif sp.look.shape == "Serpent" then
		part(
			model,
			"Body",
			Vector3.new(h * 0.35, h * 0.35, h * 0.9),
			Vector3.new(0, h * 0.18, 0.4),
			c,
			Enum.PartType.Cylinder
		)
		part(
			model,
			"Neck",
			Vector3.new(h * 0.3, h * 0.6, h * 0.3),
			Vector3.new(0, h * 0.5, -h * 0.15),
			c
		)
		part(
			model,
			"Head",
			Vector3.new(h * 0.4, h * 0.3, h * 0.5),
			Vector3.new(0, h * 0.85, -h * 0.25),
			c
		)
		eyeY, eyeZ, eyeGap = h * 0.9, -h * 0.5, h * 0.12
	else -- Biped, Quadruped
		local bodyH = h * 0.45
		part(
			model,
			"LegLeft",
			Vector3.new(h * 0.13, h * 0.3, h * 0.13),
			Vector3.new(-h * 0.1, h * 0.15, 0),
			c
		)
		part(
			model,
			"LegRight",
			Vector3.new(h * 0.13, h * 0.3, h * 0.13),
			Vector3.new(h * 0.1, h * 0.15, 0),
			c
		)
		part(
			model,
			"Body",
			Vector3.new(h * 0.38, bodyH, h * 0.26),
			Vector3.new(0, h * 0.3 + bodyH / 2, 0),
			c
		)
		part(
			model,
			"Head",
			Vector3.new(h * 0.3, h * 0.26, h * 0.28),
			Vector3.new(0, h * 0.88, 0),
			c
		)
		eyeY, eyeZ, eyeGap = h * 0.9, -h * 0.145, h * 0.07
	end
	local eyeSize = math.max(0.25, h * 0.07)
	for i, side in { -1, 1 } do
		part(
			model,
			`Glow_Eyes_{i}`,
			Vector3.one * eyeSize,
			Vector3.new(side * eyeGap, eyeY, eyeZ),
			eyes,
			Enum.PartType.Ball
		).Material =
			Enum.Material.Neon
	end
	local plate = Instance.new("Attachment")
	plate.Name = "Nameplate"
	plate.Position = Vector3.new(0, h / 2 + 1, 0)
	plate.Parent = root
	return model
end

-- A monster of `speciesId` with its mutation applied (§4.5: colour, material, size).
function MonsterKit.build(speciesId: string, mutation: string?): Model?
	local sp = Species.get(speciesId)
	if not sp then
		return nil
	end
	local folder = ReplicatedStorage:FindFirstChild("Monsters")
	local template = folder and folder:FindFirstChild(speciesId)
	local model = if template and template:IsA("Model") then template:Clone() else blockout(sp)
	local m = if mutation then Mutations.ById[mutation] else nil
	if m then
		for _, d in model:GetDescendants() do
			if d:IsA("BasePart") and d.Name ~= "Root" and not string.find(d.Name, "^Glow") then
				if m.colour then
					d.Color = m.colour
				end
				if m.material then
					d.Material = m.material
				end
			end
		end
		if m.id == "Shadow" then
			for _, d in model:GetDescendants() do
				if d:IsA("BasePart") and string.find(d.Name, "^Glow_Eyes") then
					d.Color = Color3.fromRGB(255, 220, 80)
				end
			end
		end
		if m.scale ~= 1 then
			model:ScaleTo(m.scale)
		end
	end
	return model
end

return MonsterKit
