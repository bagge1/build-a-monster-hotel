--!strict
--[[
	Plays a rigged monster's clips (GDD §12; MODELS.md, "The rig"): every
	frame, each animated monster's pose from `MonsterMotion` becomes its
	bones' `Transform`. Nothing is uploaded and nothing replicates: the
	renderers say which clip a monster is in, this moves its bones locally.

	A model with no bones gets no animator (`attach` returns nil) and its
	renderer bobs it whole, as before the rig.

	The phone's budget (§13.4): only the `MAX_ANIMATED` nearest within
	`RADIUS` of the camera move (half as many in low graphics); the rest stand
	at rest. A clip change fades over `FADE` seconds.
]]

local Players = game:GetService("Players")
local ReplicatedStorage = game:GetService("ReplicatedStorage")
local RunService = game:GetService("RunService")

local MonsterMotion = require(ReplicatedStorage.Shared.MonsterMotion)

local MonsterAnimator = {}

local RADIUS = 70 -- studs from the camera
local MAX_ANIMATED = 16
local FADE = 0.2

type Joint = { bone: Bone, rest: CFrame }

export type Animator = {
	model: Model,
	shape: string,
	height: number,
	joints: { [string]: Joint },
	clip: string,
	speed: number,
	mood: string?, -- a clip blended over the current one (a happy or sad walk)
	moodWeight: number,
	once: string?, -- a one-shot playing over everything until it ends
	onceAt: number,
	onceLength: number,
	from: MonsterMotion.Pose?, -- the pose faded out of
	fadeAt: number,
	last: MonsterMotion.Pose?,
	cycle: number, -- the walk's cycle, advanced by its rate
	phase: number,
	dist: number,
	posed: boolean,
}

local live: { [Animator]: boolean } = {}
local me = Players.LocalPlayer

--[[ An animator for `model` if it carries a rig (any `Bone`), else nil. The
	model is the one `MonsterKit.build` just made, at rest and already scaled;
	`height` is the species' `look.height` (the scale is read from the model). ]]
function MonsterAnimator.attach(model: Model, shape: string, height: number): Animator?
	local joints: { [string]: Joint } = {}
	local pivot = model:GetPivot()
	local any = false
	for _, b in model:GetDescendants() do
		if b:IsA("Bone") then
			-- The rest orientation in the model's frame: a pose is stated about the model's axes.
			joints[b.Name] = { bone = b, rest = pivot:ToObjectSpace(b.WorldCFrame) }
			any = true
		end
	end
	if not any then
		return nil
	end
	-- The meshes ride on Root (CLAUDE.md, "The art handoff"): welded, massless, never colliding.
	local root = model.PrimaryPart
	if root then
		for _, p in model:GetDescendants() do
			if p:IsA("BasePart") and p ~= root then
				p.Anchored = false
				p.Massless = true
				p.CanCollide, p.CanQuery, p.CanTouch = false, false, false
				local w = Instance.new("WeldConstraint")
				w.Part0 = root
				w.Part1 = p
				w.Parent = p
			end
		end
	end
	local a: Animator = {
		model = model,
		shape = shape,
		height = height * model:GetScale(),
		joints = joints,
		clip = "Idle",
		speed = 0,
		mood = nil,
		moodWeight = 0,
		once = nil,
		onceAt = 0,
		onceLength = 0,
		from = nil,
		fadeAt = 0,
		last = nil,
		cycle = math.random(),
		phase = math.random() * 12,
		dist = 0,
		posed = false,
	}
	live[a] = true
	return a
end

--[[ The clip `a` is in (Walk at `speed` studs a second), with `mood` blended over
	it by `weight` (a happy walk out). A change fades from the pose it left. ]]
function MonsterAnimator.set(
	a: Animator,
	clip: string,
	speed: number?,
	mood: string?,
	weight: number?
)
	if clip ~= a.clip or mood ~= a.mood then
		a.from = a.last
		a.fadeAt = os.clock()
	end
	a.clip = clip
	a.speed = speed or 0
	a.mood = mood
	a.moodWeight = weight or 0
end

-- A one-shot (CheckIn), or any clip held for `seconds`, over whatever is playing.
function MonsterAnimator.play(a: Animator, clip: string, seconds: number?)
	a.from = a.last
	a.fadeAt = os.clock()
	a.once = clip
	a.onceAt = os.clock()
	a.onceLength = seconds or MonsterMotion.OneShot[clip] or 1
end

function MonsterAnimator.release(a: Animator?)
	if a then
		live[a] = nil
	end
end

local function rest(a: Animator)
	if a.posed then
		for _, j in a.joints do
			j.bone.Transform = CFrame.identity
		end
		a.posed = false
		a.last = nil
	end
end

local function step(a: Animator, now: number, dt: number)
	local pose: MonsterMotion.Pose
	if a.once and now - a.onceAt < a.onceLength then
		pose = MonsterMotion.pose(a.shape, a.once, now - a.onceAt)
	else
		if a.once then
			a.once = nil
			a.from = a.last
			a.fadeAt = now
		end
		local rate = MonsterMotion.walkRate(a.shape, a.speed, a.height)
		a.cycle = (a.cycle + rate * dt) % 1
		local function at(clip: string): MonsterMotion.Pose
			return MonsterMotion.pose(
				a.shape,
				clip,
				if clip == "Walk" then a.cycle else now + a.phase
			)
		end
		pose = at(a.clip)
		if a.mood and a.moodWeight > 0 then
			pose = MonsterMotion.blend(pose, at(a.mood), a.moodWeight)
		end
	end
	local fade = (now - a.fadeAt) / FADE
	if a.from and fade < 1 then
		pose = MonsterMotion.blend(a.from, pose, fade)
	end
	a.last = pose
	for name, j in a.joints do
		local bp = pose[name]
		j.bone.Transform = if bp
			then MonsterMotion.transform(j.rest, bp, a.height)
			else CFrame.identity
	end
	a.posed = true
end

local function frame(dt: number)
	local now = os.clock()
	local cap = if me:GetAttribute("LowGraphics") then MAX_ANIMATED // 2 else MAX_ANIMATED
	local near = {}
	for a in live do
		if not a.model.Parent then
			live[a] = nil
		elseif a.dist <= RADIUS then
			table.insert(near, a)
		else
			rest(a)
		end
	end
	table.sort(near, function(x, y)
		return x.dist < y.dist
	end)
	for i, a in near do
		if i <= cap then
			step(a, now, dt)
		else
			rest(a)
		end
	end
end

function MonsterAnimator.Init() end

function MonsterAnimator.Start()
	RunService.Heartbeat:Connect(frame)
end

return MonsterAnimator
