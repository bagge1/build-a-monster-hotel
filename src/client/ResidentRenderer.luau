--!strict
--[[
	Every hotel's residents, as every client sees them (GDD §4.6, §7 "Visit
	and like: see its residents"): the Wing's residents wander its garden;
	staff stand at their posts (`Staff.post`, found by the hotel's shared
	points, `HotelPoints`), in the order the server's `Slot` gives.

	STAFF ARE SEEN WORKING (§4.6, §5.4, Appendix A.5): a resident on an
	errand carries `Path`, `T0` and `Speed`, and this walks it along them by
	the same arithmetic the server times it with; at the door (`Phase`
	"Work") it faces in and knocks, and when the job is done (`Phase` turns
	"Done") a "✓" rises at the `Door`. The server publishes them in
	`ReplicatedStorage.Residents`; this draws and moves them locally. Read by
	nothing.

	A rigged model plays its clips (GDD §12, `MonsterAnimator`): Walk on the
	move, Staff at the door, Happy for an entertainer and for a moment when a
	job is done, Idle at its post. A model with no bones bobs whole, as before.

	The render budget (§13.4): a resident has a model only within the guests'
	draw radius (`GuestRenderer.DrawRadius`) of the camera; beyond it only its
	place is kept, so ten streamed-in hotels' residents cost nothing to draw
	(2026-10-26: every one was built and moved every frame). A republish
	updates the Configurations in place (ResidentService), so a resident keeps
	its model and its spot in the garden.
]]

local ReplicatedStorage = game:GetService("ReplicatedStorage")
local RunService = game:GetService("RunService")

local Constants = require(ReplicatedStorage.Shared.Constants)
local HotelPoints = require(ReplicatedStorage.Shared.HotelPoints)
local Species = require(ReplicatedStorage.Shared.Species)
local Staff = require(ReplicatedStorage.Shared.Staff)
local MonsterKit = require(script.Parent.MonsterKit)
local MonsterAnimator = require(script.Parent.MonsterAnimator)
local GuestRenderer = require(script.Parent.GuestRenderer)
local Hud = require(script.Parent.Hud)
local Ui = require(script.Parent.Ui)

local ResidentRenderer = {}

local G = Constants.Grid
local P = G.Cells * G.CellSize
local POP_RADIUS = 150 -- a "✓" further from the camera than this is not drawn
local DRAW_RADIUS = GuestRenderer.DrawRadius
-- A drawn resident stays until clearly out, as a guest does (GuestRenderer's `KEEP_SLACK`): no flicker at the edge.
local KEEP_SLACK = 30

type Drawn = {
	config: Configuration,
	plot: number,
	model: Model?,
	pos: Vector3,
	target: Vector3,
	waitUntil: number,
	key: string,
	errand: { Vector3 }, -- the leg being walked, decoded from `Path`
	errandCode: string?,
	connections: { RBXScriptConnection },
	anim: MonsterAnimator.Animator?,
	placed: boolean, -- `pos` is a place in its hotel (kept while it has no model, beyond the radius)
	origin: any, -- the plot's `Origin` when it was placed: a new one is a Travel
	post: Vector3?, -- its post, cached (2026-10-26: HotelPoints.find sorted the plot's Pieces each frame)
	postKey: string, -- the role and slot the cached post is for
	postGen: number, -- the plot's points generation it was found in (`pointsGen`)
}

local drawn: { [Configuration]: Drawn } = {}
local rng = Random.new()

--[[ Each plot's points generation: bumped when anything is added to or taken from the plot or it
	moves (Travel sets `Origin`), so a cached post is found again only then. A piece is moved by
	being rebuilt (PlotService), which adds it anew. ]]
local pointsGen: { [Model]: number } = {}
local function genOf(plot: Model): number
	local gen = pointsGen[plot]
	if gen then
		return gen
	end
	pointsGen[plot] = 1
	local conns: { RBXScriptConnection } = {}
	local function bump()
		pointsGen[plot] = (pointsGen[plot] or 1) + 1
	end
	table.insert(conns, plot.DescendantAdded:Connect(bump))
	table.insert(conns, plot.DescendantRemoving:Connect(bump))
	table.insert(conns, plot:GetAttributeChangedSignal("Origin"):Connect(bump))
	table.insert(
		conns,
		plot.AncestryChanged:Connect(function()
			if not plot:IsDescendantOf(workspace) then
				for _, c in conns do
					c:Disconnect()
				end
				pointsGen[plot] = nil
			end
		end)
	)
	return 1
end

-- A resident's post (`Staff.post`), found again only when its role, slot or the plot's points change.
local function postOf(d: Drawn, plot: Model, role: string, slot: number): Vector3?
	local key = `{role}|{slot}`
	local gen = genOf(plot)
	if d.postKey ~= key or d.postGen ~= gen then
		d.postKey = key
		d.postGen = gen
		d.post = Staff.post(role, slot, function(name)
			return HotelPoints.find(plot, name)
		end)
	end
	return d.post
end

local function plotModel(index: number): Model?
	local plots = workspace:FindFirstChild("Plots")
	local m = plots and plots:FindFirstChild(`Plot_{index}`)
	return if m and m:IsA("Model") then m else nil
end

local function wingPoint(plot: Model): Vector3?
	local origin = plot:GetAttribute("Origin")
	if typeof(origin) ~= "CFrame" then
		return nil
	end
	local l = Vector3.new(
		rng:NextNumber(6, P - 6),
		G.SlabThickness,
		rng:NextNumber(P + 4, P + G.WingDepth - 4)
	)
	return origin:PointToWorldSpace(l)
end

-- The "✓" at the door when a job is done (Appendix A.5).
local function popDone(c: Configuration)
	local door = c:GetAttribute("Door")
	local text = Staff.DoneText[c:GetAttribute("Role") :: string? or ""]
	local camera = workspace.CurrentCamera
	if typeof(door) ~= "Vector3" or not text then
		return
	end
	if camera and (camera.CFrame.Position - door).Magnitude > POP_RADIUS then
		return
	end
	Hud.float(text, door + Vector3.new(0, 3, 0), Ui.Colour.Good)
end

--[[ The level over a resident's head (A.11.6): "Lv n", gold at the cap,
	redrawn when `Level` changes. ]]
local function levelBadge(m: Model, level: number)
	local cf, size = m:GetBoundingBox()
	local anchor = m.PrimaryPart or m:FindFirstChildWhichIsA("BasePart", true)
	if not anchor then
		return
	end
	local bb = Instance.new("BillboardGui")
	bb.Name = "LevelBadge"
	bb.Adornee = anchor
	bb.Size = UDim2.fromOffset(64, 24)
	bb.StudsOffsetWorldSpace = Vector3.new(0, cf.Position.Y + size.Y / 2 - anchor.Position.Y + 1, 0)
	bb.MaxDistance = 60
	bb.LightInfluence = 0
	local l = Ui.label(
		bb,
		"Value",
		`Lv {level}`,
		UDim2.fromScale(1, 1),
		16,
		if level >= Constants.Residents.LevelCap then Ui.Colour.Gold else Ui.Colour.Text
	)
	l.TextXAlignment = Enum.TextXAlignment.Center
	l.BackgroundColor3 = Ui.Colour.Ink
	l.BackgroundTransparency = 0.3
	Ui.corner(l, 8)
	bb.Parent = m
end

local function add(c: Instance, plotIndex: number)
	if not c:IsA("Configuration") or drawn[c] then
		return
	end
	local d: Drawn = {
		config = c,
		plot = plotIndex,
		model = nil,
		pos = Vector3.zero,
		target = Vector3.zero,
		waitUntil = 0,
		key = "",
		errand = {},
		errandCode = nil,
		connections = {},
		anim = nil,
		placed = false,
		post = nil,
		postKey = "",
		postGen = 0,
	}
	drawn[c] = d
	table.insert(
		d.connections,
		c:GetAttributeChangedSignal("Phase"):Connect(function()
			if c:GetAttribute("Phase") == "Done" then
				popDone(c)
				if d.anim then
					MonsterAnimator.play(d.anim, "Happy", 1.2) -- the job done (§12)
				end
			end
		end)
	)
	-- A level-up arrives on the same Configuration (a republish updates in place): its badge follows.
	table.insert(
		d.connections,
		c:GetAttributeChangedSignal("Level"):Connect(function()
			local m = d.model
			if m then
				local old = m:FindFirstChild("LevelBadge")
				if old then
					old:Destroy()
				end
				levelBadge(m, c:GetAttribute("Level") :: number? or 1)
			end
		end)
	)
end

local function remove(c: Instance)
	local d = drawn[c :: Configuration]
	if d then
		if d.model then
			d.model:Destroy()
		end
		MonsterAnimator.release(d.anim)
		for _, conn in d.connections do
			conn:Disconnect()
		end
		drawn[c :: Configuration] = nil
	end
end

local function watchPlot(f: Instance)
	local index = tonumber(string.match(f.Name, "%d+")) or 0
	for _, c in f:GetChildren() do
		add(c, index)
	end
	f.ChildAdded:Connect(function(c)
		add(c, index)
	end)
	f.ChildRemoved:Connect(remove)
end

-- Where a resident on an errand is now, the way it faces, and whether it is still walking.
local function onErrand(d: Drawn, serverNow: number): (Vector3?, Vector3, boolean)
	local c = d.config
	local code = c:GetAttribute("Path") :: string?
	if code ~= d.errandCode then
		d.errandCode = code
		d.errand = Staff.decode(code)
	end
	if not code or #d.errand == 0 then
		return nil, Vector3.new(0, 0, -1), false
	end
	local speed = c:GetAttribute("Speed") :: number? or Constants.Staff.WalkSpeed
	local travelled = (serverNow - (c:GetAttribute("T0") :: number? or serverNow)) * speed
	local pos, dir = Staff.along(d.errand, travelled)
	local walking = travelled < Staff.length(d.errand)
	if not walking and c:GetAttribute("Phase") == "Work" then
		-- At the door: face it.
		local door = c:GetAttribute("Door")
		if typeof(door) == "Vector3" then
			local toward = Vector3.new(door.X - pos.X, 0, door.Z - pos.Z)
			if toward.Magnitude > 0.1 then
				dir = toward.Unit
			end
		end
	end
	return pos, dir, walking
end

local function dropModel(d: Drawn)
	if d.model then
		d.model:Destroy()
		d.model = nil
	end
	MonsterAnimator.release(d.anim)
	d.anim = nil
end

local function frame(dt: number)
	local now = os.clock()
	local serverNow = workspace:GetServerTimeNow()
	local camera = workspace.CurrentCamera
	local eye = camera and camera.CFrame.Position
	local counts: { [string]: number } = {}
	for c, d in drawn do
		-- A Wing taken away (its owner gone) takes its Configurations with it: drop what went.
		if not c:IsDescendantOf(game) then
			remove(c)
			continue
		end
		local plot = plotModel(d.plot)
		local away = c:GetAttribute("Away") == true
		local key =
			`{c:GetAttribute("Species")}|{c:GetAttribute("Mutation")}|{c:GetAttribute("Size")}`
		if d.model and (d.key ~= key or away or not plot) then
			dropModel(d)
		end
		if away or not plot then
			d.placed = false -- back from the camp, or streamed in again: a new spot in the garden
			continue
		end
		-- A Travel or a rebirth moves the plot to another street (its `Origin`) and keeps
		-- each Configuration: the resident starts again in the new garden, not 1400 studs
		-- away walking there (2026-10-26, the regression review).
		local origin = plot:GetAttribute("Origin")
		if d.placed and origin ~= d.origin then
			d.placed = false
		end
		if not d.placed then
			d.pos = wingPoint(plot) or Vector3.zero
			d.target = d.pos
			d.placed = true
			d.origin = origin
		end
		local role = c:GetAttribute("Role") :: string? or ""
		local ck = `{d.plot}|{role}`
		counts[ck] = (counts[ck] or 0) + 1
		local slot = c:GetAttribute("Slot") :: number? or counts[ck]
		local errandPos, errandDir, walking = onErrand(d, serverNow)
		local dir: Vector3
		if errandPos then
			d.pos = errandPos
			d.target = errandPos
			dir = errandDir
		else
			local goal = if role ~= "" then postOf(d, plot, role, slot) else nil
			if goal then
				d.target = goal
			elseif (d.pos - d.target).Magnitude < 0.5 and now >= d.waitUntil then
				d.target = wingPoint(plot) or d.pos
				d.waitUntil = now + rng:NextNumber(2, 6)
			end
			local delta = d.target - d.pos
			local step = math.min(delta.Magnitude, (if role ~= "" then 12 else 3) * dt)
			dir = if delta.Magnitude > 0.01 then delta.Unit else Vector3.new(0, 0, -1)
			walking = delta.Magnitude > 0.05
			-- A new post far away: appear there. A Wing resident walks to its next spot in the
			-- garden, however far (2026-10-26: it jumped there, up to 20 studs at a time).
			if goal and delta.Magnitude > 20 then
				d.pos = d.target
			else
				d.pos += dir * step
			end
		end
		-- Drawn within the radius; once drawn, until clearly out of it.
		local dist = if eye then (d.pos - eye).Magnitude else 0
		local show = dist <= DRAW_RADIUS or (d.model ~= nil and dist <= DRAW_RADIUS + KEEP_SLACK)
		if not show then
			dropModel(d)
		elseif not d.model then
			local m = MonsterKit.build(
				c:GetAttribute("Species") :: string,
				c:GetAttribute("Mutation") :: string?,
				c:GetAttribute("Size") :: string?
			)
			if m then
				levelBadge(m, c:GetAttribute("Level") :: number? or 1)
				m.Parent = workspace:FindFirstChild("ClientGuests") or workspace
				d.model = m
				local sp = Species.get(c:GetAttribute("Species") :: string)
				d.anim = if sp
					then MonsterAnimator.attach(m, sp.look.shape, sp.look.height)
					else nil
				d.key = key
			end
		end
		if d.model then
			local flat = Vector3.new(dir.X, 0, dir.Z)
			local look = if flat.Magnitude > 0.01 then flat.Unit else Vector3.new(0, 0, -1)
			local phase = c:GetAttribute("Phase")
			local anim = d.anim
			if anim then
				anim.dist = dist
				if walking then
					MonsterAnimator.set(
						anim,
						"Walk",
						if errandPos
							then c:GetAttribute("Speed") :: number? or Constants.Staff.WalkSpeed
							elseif role ~= "" then 12
							else 3
					)
				elseif phase == "Work" then
					MonsterAnimator.set(anim, "Staff")
				elseif role == "Entertainment" then
					MonsterAnimator.set(anim, "Happy")
				else
					MonsterAnimator.set(anim, "Idle")
				end
			end
			local bob = if anim
				then 0 -- its clips carry the motion
				elseif walking and errandPos then math.abs(math.sin(now * 8))
					* 0.25 -- a guest's stride (GuestRenderer)
				elseif phase == "Work" then math.abs(math.sin(now * 5)) * 0.4 -- knocking
				elseif role == "Entertainment" then math.abs(math.sin(now * 6)) * 0.6
				else 0
			d.model:PivotTo(
				CFrame.lookAt(d.pos + Vector3.new(0, bob, 0), d.pos + Vector3.new(0, bob, 0) + look)
			)
		end
	end
end

function ResidentRenderer.Init() end

function ResidentRenderer.Start()
	local folder = ReplicatedStorage:WaitForChild("Residents")
	for _, f in folder:GetChildren() do
		watchPlot(f)
	end
	folder.ChildAdded:Connect(watchPlot)
	folder.ChildRemoved:Connect(function(f)
		for _, c in f:GetChildren() do
			remove(c)
		end
	end)
	RunService.Heartbeat:Connect(frame)
end

return ResidentRenderer
