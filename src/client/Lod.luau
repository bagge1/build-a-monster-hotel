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

	ONE WORLD (GDD §3, §6.4): the hotels a chain draws on its other streets
	(`workspace.WorldPlots`, static) get the same, and in low graphics their
	lights stay off like every other hotel not played by this player. A whole
	far street is mostly out of the client's hands: streaming (on in
	`default.project.json`) sends a plot only within its radius.
	The street lamps of every street light only within `LAMP_LIGHT` of the
	camera; their bulbs glow on (measured 2026-10-21: three streets are 180
	lamps, 104 of them lit on a client at Creepy Lane before this).
]]

local Players = game:GetService("Players")
local ReplicatedStorage = game:GetService("ReplicatedStorage")

local Constants = require(ReplicatedStorage.Shared.Constants)
local StreetLayout = require(ReplicatedStorage.Shared.StreetLayout)

local Lod = {}

-- Studs from the camera to a plot's centre: about one plot and a gap away.
local FAR = (StreetLayout.PlotSize + Constants.Street.PlotGap) * 1.25
local me = Players.LocalPlayer

local DETAIL =
	{ Bed = true, Pillow = true, Centrepiece = true, Furniture = true, Dressing = true, Rug = true }

local far: { [Model]: boolean } = {}
--[[ The parts this hid, per plot: it shows again only those (2026-10-26: it set every detail part
	back to 0 on a near plot, so placing a piece in build mode on floor 1 brought back the upper
	floors' beds and lamps BuildController had hidden, floating over the floor being edited). ]]
local hiddenBy: { [Model]: { [BasePart]: boolean } } = {}

local function isDetail(p: BasePart): boolean
	if DETAIL[p.Name] or string.sub(p.Name, 1, 5) == "Glow_" then
		return true
	end
	local model = p:FindFirstAncestorOfClass("Model")
	return model ~= nil and string.sub(model.Name, 1, 6) == "Decor_"
end

local function apply(plot: Model, hide: boolean)
	local pieces = plot:FindFirstChild("Pieces")
	local mine = plot:GetAttribute("Index") == me:GetAttribute("Plot")
		and not plot:GetAttribute("Static")
	if not hide then
		for p in hiddenBy[plot] or {} do
			p.LocalTransparencyModifier = 0
		end
		hiddenBy[plot] = nil
	end
	local mineHidden: { [BasePart]: boolean } = {}
	if hide then
		for p in hiddenBy[plot] or {} do
			if p:IsDescendantOf(plot) then
				mineHidden[p] = true -- a part taken away since is let go
			end
		end
		hiddenBy[plot] = mineHidden
	end
	for _, d in (if pieces then pieces:GetDescendants() else {}) do
		if d:IsA("BasePart") and isDetail(d) then
			if hide then
				d.LocalTransparencyModifier = 1
				mineHidden[d] = true
			end
		elseif d:IsA("PointLight") then
			d.Enabled = not hide and not (me:GetAttribute("LowGraphics") == true and not mine)
		end
	end
end

-- Every hotel in the world: the ones played (`Plots`) and the chains' others (`WorldPlots`).
local function allPlots(): { Instance }
	local out = {}
	for _, name in { "Plots", "WorldPlots" } do
		local folder = workspace:FindFirstChild(name)
		for _, plot in (if folder then folder:GetChildren() else {}) do
			table.insert(out, plot)
		end
	end
	return out
end

-- Street lamps (every street's `Street*` folder): their light only near the camera; the bulb glows on.
local LAMP_LIGHT = 500 -- PLACEHOLDER: studs; a lamp's light (range 24) is lost in the fog well before the fog's end
local function lamps(eye: Vector3)
	for _, folder in workspace:GetChildren() do
		if folder:IsA("Folder") and string.sub(folder.Name, 1, 6) == "Street" then
			for _, d in folder:GetDescendants() do
				if d:IsA("PointLight") and d.Parent and d.Parent:IsA("BasePart") then
					local p = (d.Parent :: BasePart).Position
					d.Enabled = (Vector3.new(p.X, eye.Y, p.Z) - eye).Magnitude <= LAMP_LIGHT
				end
			end
		end
	end
end

local function step()
	local camera = workspace.CurrentCamera
	if not camera then
		return
	end
	local eye = camera.CFrame.Position
	lamps(eye)
	for _, plot in allPlots() do
		if plot:IsA("Model") then
			local origin = plot:GetAttribute("Origin")
			if typeof(origin) == "CFrame" then
				local centre = origin:PointToWorldSpace(
					Vector3.new(StreetLayout.PlotSize / 2, 0, StreetLayout.PlotSize / 2)
				)
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
	-- A rebuilt hotel brings new parts, a moved one (Travel) a new place: reapply to it on the next step.
	local watched: { [Model]: { RBXScriptConnection } } = {}
	local function watch(plot: Instance)
		if not plot:IsA("Model") or watched[plot] then
			return
		end
		local conns: { RBXScriptConnection } = {}
		watched[plot] = conns
		table.insert(
			conns,
			plot.DescendantAdded:Connect(function()
				far[plot] = nil
			end)
		)
		table.insert(
			conns,
			plot:GetAttributeChangedSignal("Origin"):Connect(function()
				far[plot] = nil
			end)
		)
		-- A plot streamed out or taken away is forgotten (2026-10-26: `far` kept every plot model ever seen).
		table.insert(
			conns,
			plot.AncestryChanged:Connect(function()
				if not plot:IsDescendantOf(workspace) then
					for _, c in conns do
						c:Disconnect()
					end
					watched[plot] = nil
					far[plot] = nil
					hiddenBy[plot] = nil
				end
			end)
		)
	end
	for _, name in { "Plots", "WorldPlots" } do
		task.spawn(function()
			local folder = workspace:WaitForChild(name)
			for _, plot in folder:GetChildren() do
				watch(plot)
			end
			folder.ChildAdded:Connect(watch) -- streamed in later
		end)
	end
	me:GetAttributeChangedSignal("LowGraphics"):Connect(function()
		table.clear(far)
	end)
	task.spawn(function()
		while true do
			task.wait(2)
			pcall(step)
		end
	end)
end

return Lod
