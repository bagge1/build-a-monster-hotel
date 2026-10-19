--!strict
--[[
	Level of detail for other hotels (GDD §13.4: "LOD for hotels beyond the
	player's own and adjacent plots"). Every two seconds, each plot whose
	centre is far from the camera hides its interior detail locally: beds,
	pillows, centrepieces, decor and lamps (and their lights). Walls, floors
	and slabs stay, so the street still reads as a street. Purely visual and
	local (`LocalTransparencyModifier`); nothing the server reads.

	A delivered model's `LOD_Proxy` (MODELS.md, "What a model costs to draw")
	is a later step; this works on blockouts and models alike by part name.
]]

local Players = game:GetService("Players")

local Lod = {}

local FAR = 120 -- studs from the camera to a plot's centre (about one plot and a gap away)
local me = Players.LocalPlayer

local DETAIL =
	{ Bed = true, Pillow = true, Centrepiece = true, Furniture = true, Dressing = true, Rug = true }

local far: { [Model]: boolean } = {}

local function isDetail(p: BasePart): boolean
	if DETAIL[p.Name] or string.sub(p.Name, 1, 5) == "Glow_" then
		return true
	end
	local model = p:FindFirstAncestorOfClass("Model")
	return model ~= nil and string.sub(model.Name, 1, 6) == "Decor_"
end

local function apply(plot: Model, hide: boolean)
	local pieces = plot:FindFirstChild("Pieces")
	for _, d in (if pieces then pieces:GetDescendants() else {}) do
		if d:IsA("BasePart") and isDetail(d) then
			d.LocalTransparencyModifier = if hide then 1 else 0
		elseif d:IsA("PointLight") then
			d.Enabled = not hide
				and not (
					me:GetAttribute("LowGraphics") == true
					and plot:GetAttribute("Index") ~= me:GetAttribute("Plot")
				)
		end
	end
end

local function step()
	local camera = workspace.CurrentCamera
	local plots = workspace:FindFirstChild("Plots")
	if not camera or not plots then
		return
	end
	local eye = camera.CFrame.Position
	for _, plot in plots:GetChildren() do
		if plot:IsA("Model") then
			local origin = plot:GetAttribute("Origin")
			if typeof(origin) == "CFrame" then
				local centre = origin:PointToWorldSpace(Vector3.new(36, 0, 36))
				local isFar = (Vector3.new(centre.X, eye.Y, centre.Z) - eye).Magnitude > FAR
				if far[plot] ~= isFar then
					far[plot] = isFar
					apply(plot, isFar)
				end
			end
		end
	end
end

function Lod.Init() end

function Lod.Start()
	-- A rebuilt hotel brings new parts: reapply to it on the next step.
	local plots = workspace:WaitForChild("Plots")
	for _, plot in plots:GetChildren() do
		if plot:IsA("Model") then
			plot.DescendantAdded:Connect(function()
				far[plot] = nil
			end)
		end
	end
	task.spawn(function()
		while true do
			task.wait(2)
			pcall(step)
		end
	end)
end

return Lod
