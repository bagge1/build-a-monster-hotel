--!strict
--[[
	The monsters' six clips (GDD §12, ruling §18 2026-10-23), as curves: no
	Animation asset, nothing uploaded. A clip is a pose at a time, a pose is
	each bone's rotation and offset, and `MonsterAnimator` (client) turns a
	pose into each `Bone.Transform` every frame. Pure arithmetic, so a spec
	runs it outside Studio (tests/motion.spec.luau).

	The bones are the rig's (MODELS.md, "The rig"), one set per body shape. A
	pose states each rotation in radians about the MODEL's axes at rest
	(X the monster's right, Y up, Z its back: it faces -Z), so one curve fits
	every species of a shape whatever the importer did to a bone's own axes;
	an offset is in the species' heights, so it fits Tiny and Giant too.
	Signs: +X swings a hanging limb forward and tips an upright one back; +Z
	swings a hanging limb toward the monster's right; +Y turns the face to its
	left.

	The clips, by how they should feel (what August judges):
	- Walk: a bouncy toy stride (Biped and Quadruped), a squishy hop (Blob), a
	  forward-leaning glide with a trailing tail (Float), an S-slither of the
	  tail with the head held level (Serpent); its pace follows the speed.
	- Idle: breathing, a slow look around, a tail or hem that drifts.
	- Happy: little hops with arms up in a V and a head wobble; a Blob bounces
	  and wiggles, a Serpent sways its neck.
	- Sad: head hung, shoulders slumped, a slow sway; a Blob sags and spreads.
	- CheckIn: a one-shot flourish at the desk: a Biped sweeps its right arm
	  out and bows, a Blob squashes and twirls in a hop, a Float twirls, a
	  Serpent rears up and bows.
	- Staff: the right hand at work (knocking, wiping, serving) with a lean;
	  a Blob and a Serpent nod-bump instead.
]]

local MonsterMotion = {}

export type Clip = "Walk" | "Idle" | "Happy" | "Sad" | "CheckIn" | "Staff"
export type BonePose = { r: Vector3, p: Vector3 }
export type Pose = { [string]: BonePose }

MonsterMotion.Clips = { "Walk", "Idle", "Happy", "Sad", "CheckIn", "Staff" } :: { Clip }

-- The bones a clip may pose, per shape (MODELS.md, "The rig"; RigRoot is never posed).
MonsterMotion.Bones = {
	Biped = { "Hips", "Spine", "Head", "Arm_L", "Arm_R", "Thigh_L", "Shin_L", "Thigh_R", "Shin_R" },
	Quadruped = { "Hips", "Spine", "Head", "Tail", "Leg_FL", "Leg_FR", "Leg_BL", "Leg_BR" },
	Blob = { "Base", "Middle", "Top", "Side_L", "Side_R" },
	Float = { "Body", "Head", "Arm_L", "Arm_R", "Tail_1", "Tail_2" },
	Serpent = { "Coil", "Neck", "Head", "Tail_1", "Tail_2" },
} :: { [string]: { string } }

-- Each looping clip's period in seconds, a multiple of every wave in it (Walk's comes from the speed), and
-- each clip's length when played once.
MonsterMotion.Period = { Idle = 12, Happy = 1.4, Sad = 6, Staff = 0.8 } :: { [string]: number }
MonsterMotion.OneShot = { CheckIn = 1.4 } :: { [string]: number }

-- Studs a body shape covers in one walk cycle (two steps), in heights.
MonsterMotion.Stride =
	{ Biped = 1.1, Quadruped = 1.0, Blob = 2.0, Float = 1.6, Serpent = 1.4 } :: { [string]: number }
local MIN_RATE, MAX_RATE = 0.6, 2.2 -- walk cycles a second, so a crawl or a dash still reads as walking

local TAU = 2 * math.pi
local ZERO = Vector3.zero

local function wave(t: number, period: number, shift: number?): number
	return math.sin(TAU * (t / period + (shift or 0)))
end

-- A hump from 0 to 1 and back over [a, b] of a one-shot's progress u, zero outside.
local function bump(u: number, a: number, b: number): number
	if u <= a or u >= b then
		return 0
	end
	return math.sin(math.pi * (u - a) / (b - a))
end

local function smooth(u: number): number
	u = math.clamp(u, 0, 1)
	return u * u * (3 - 2 * u)
end

local function rot(x: number, y: number, z: number): BonePose
	return { r = Vector3.new(x, y, z), p = ZERO }
end

local function move(
	x: number,
	y: number,
	z: number,
	rx: number?,
	ry: number?,
	rz: number?
): BonePose
	return { r = Vector3.new(rx or 0, ry or 0, rz or 0), p = Vector3.new(x, y, z) }
end

--[[ Walk cycles a second for a monster of `height` (studs, after its scale)
	moving at `speed` studs a second. ]]
function MonsterMotion.walkRate(shape: string, speed: number, height: number): number
	local stride = (MonsterMotion.Stride[shape] or 1.2) * math.max(height, 0.5)
	return math.clamp(speed / stride, MIN_RATE, MAX_RATE)
end

-- The shapes' clips: (clip, t) -> Pose. For Walk `t` is the cycle (1 a stride);
-- for the rest it is seconds, and for a one-shot u = t / its length.
local shapes: { [string]: (clip: string, t: number) -> Pose } = {}

function shapes.Biped(clip, t)
	if clip == "Walk" then
		local a, c = math.sin(TAU * t), math.cos(TAU * t)
		return {
			-- The stance leg straight: the hips drop as the legs spread, so the feet stay down.
			Hips = move(0, -0.3 * (1 - math.cos(0.45 * a)), 0, 0, 0.12 * a, 0),
			Spine = rot(-0.04, -0.15 * a, 0.03 * c),
			Head = rot(0.04 * math.abs(c), 0.05 * a, 0),
			Thigh_L = rot(0.45 * a, 0, 0),
			Thigh_R = rot(-0.45 * a, 0, 0),
			Shin_L = rot(-0.7 * math.max(0, c), 0, 0),
			Shin_R = rot(-0.7 * math.max(0, -c), 0, 0),
			Arm_L = rot(-0.35 * a, 0, -0.08),
			Arm_R = rot(0.35 * a, 0, 0.08),
		}
	elseif clip == "Idle" then
		local b = wave(t, 3)
		return {
			Spine = rot(0.03 * b, 0, 0),
			Head = rot(0.04 * wave(t, 3, 0.15), 0.15 * wave(t, 6), 0),
			Arm_L = rot(0.02 * b, 0, -0.05 - 0.03 * b),
			Arm_R = rot(0.02 * b, 0, 0.05 + 0.03 * b),
		}
	elseif clip == "Happy" then
		local hop = math.abs(wave(t, 1.4))
		local w = wave(t, 0.35)
		return {
			Hips = move(0, 0.06 * hop, 0),
			Spine = rot(0.05, 0, 0.06 * wave(t, 1.4)),
			Head = rot(0.06, 0, 0.15 * wave(t, 0.7)),
			Arm_L = rot(0, 0, -2.2 - 0.25 * w),
			Arm_R = rot(0, 0, 2.2 + 0.25 * w),
			Thigh_L = rot(0.15 * hop, 0, 0),
			Thigh_R = rot(0.15 * hop, 0, 0),
			Shin_L = rot(-0.3 * hop, 0, 0),
			Shin_R = rot(-0.3 * hop, 0, 0),
		}
	elseif clip == "Sad" then
		local s = wave(t, 3)
		return {
			Hips = move(0, -0.01, 0),
			Spine = rot(-0.18, 0, 0.05 * s),
			Head = rot(-0.45 + 0.03 * s, 0.1 * wave(t, 6), 0),
			Arm_L = rot(0.1, 0, 0.06),
			Arm_R = rot(0.1, 0, -0.06),
		}
	elseif clip == "CheckIn" then
		local u = t / MonsterMotion.OneShot.CheckIn
		local bow = bump(u, 0.35, 1)
		return {
			Spine = rot(-0.5 * bow, 0, 0),
			Head = rot(-0.3 * bow, 0, 0),
			Arm_R = rot(1.2 * bow, 0, 1.6 * bump(u, 0, 0.55)),
			Arm_L = rot(-0.3 * bow, 0, -0.1 * bow),
			Hips = move(0, -0.015 * bow, 0),
		}
	elseif clip == "Staff" then
		local k = wave(t, 0.8)
		return {
			Spine = rot(-0.08, 0.06, 0),
			Head = rot(-0.05 + 0.04 * k, 0, 0),
			Arm_R = rot(1.1 + 0.45 * k, 0, 0.1),
			Arm_L = rot(0.1, 0, -0.08),
			Hips = move(0, 0.008 * wave(t, 0.4), 0),
		}
	end
	return {}
end

function shapes.Quadruped(clip, t)
	if clip == "Walk" then
		local a, c = math.sin(TAU * t), math.cos(TAU * t)
		return {
			Hips = move(0, 0.02 * math.abs(c), 0),
			Spine = rot(0, 0.06 * a, 0),
			Head = rot(0.05 * math.cos(2 * TAU * t), -0.06 * a, 0),
			Tail = rot(0, 0.4 * a, 0),
			Leg_FL = rot(0.4 * a, 0, 0),
			Leg_BR = rot(0.4 * a, 0, 0),
			Leg_FR = rot(-0.4 * a, 0, 0),
			Leg_BL = rot(-0.4 * a, 0, 0),
		}
	elseif clip == "Idle" then
		return {
			Spine = rot(0.02 * wave(t, 3), 0, 0),
			Head = rot(0.05 * wave(t, 3, 0.2), 0.2 * wave(t, 6), 0),
			Tail = rot(0, 0.25 * wave(t, 2), 0),
		}
	elseif clip == "Happy" then
		local hop = math.abs(wave(t, 1.4))
		return {
			Hips = move(0, 0.08 * hop, 0),
			Head = rot(0.15, 0, 0.15 * wave(t, 0.7)),
			Tail = rot(-0.3, 0.6 * wave(t, 0.35), 0),
			Leg_FL = rot(0.3 * hop, 0, 0),
			Leg_FR = rot(0.3 * hop, 0, 0),
			Leg_BL = rot(-0.3 * hop, 0, 0),
			Leg_BR = rot(-0.3 * hop, 0, 0),
		}
	elseif clip == "Sad" then
		return {
			Spine = rot(-0.06, 0, 0),
			Head = rot(-0.45 + 0.03 * wave(t, 3), 0.1 * wave(t, 6), 0),
			Tail = rot(0.6, 0, 0),
			Hips = move(0, -0.02, 0),
		}
	elseif clip == "CheckIn" then
		local u = t / MonsterMotion.OneShot.CheckIn
		local bow = bump(u, 0.3, 1)
		return {
			Spine = rot(-0.3 * bow, 0, 0),
			Head = rot(-0.3 * bow, 0, 0),
			Leg_FL = rot(0.3 * bow, 0, 0),
			Leg_FR = rot(0.3 * bow, 0, 0),
			Tail = rot(-0.4 * bow, 0.5 * wave(t, 0.3) * bow, 0),
		}
	elseif clip == "Staff" then
		local k = wave(t, 0.8)
		return {
			Leg_FR = rot(0.9 + 0.4 * k, 0, 0),
			Head = rot(-0.1, 0, 0),
			Tail = rot(0, 0.2 * k, 0),
		}
	end
	return {}
end

function shapes.Blob(clip, t)
	local function squish(hop: number, lift: number): Pose
		local sq = (1 - hop) ^ 3
		return {
			Base = move(0, lift * hop, 0),
			Top = move(0, -0.12 * sq + 0.06 * hop, 0),
			Side_L = move(-0.08 * sq, 0, 0),
			Side_R = move(0.08 * sq, 0, 0),
		}
	end
	if clip == "Walk" then
		local pose = squish(math.abs(math.sin(TAU * t)), 0.15)
		pose.Middle = rot(-0.1 * math.cos(TAU * t), 0, 0)
		return pose
	elseif clip == "Idle" then
		local b = wave(t, 3)
		return {
			Top = move(0, 0.025 * b, 0),
			Side_L = move(0.015 * b, 0, 0),
			Side_R = move(-0.015 * b, 0, 0),
			Middle = rot(0, 0, 0.04 * wave(t, 4)),
		}
	elseif clip == "Happy" then
		local pose = squish(math.abs(wave(t, 1.4)), 0.25)
		pose.Middle = rot(0, 0.3 * wave(t, 0.7), 0)
		return pose
	elseif clip == "Sad" then
		local s = wave(t, 3)
		return {
			Top = move(0, -0.12 + 0.01 * s, 0),
			Side_L = move(-0.06, -0.02, 0),
			Side_R = move(0.06, -0.02, 0),
			Middle = rot(-0.12, 0, 0.03 * s),
		}
	elseif clip == "CheckIn" then
		local u = t / MonsterMotion.OneShot.CheckIn
		-- Squash, a hop with a whole twirl in the air, squash on landing.
		local air = bump(u, 0.3, 0.85)
		local sq = bump(u, 0, 0.32) + bump(u, 0.82, 1)
		return {
			Base = move(0, 0.4 * air, 0, 0, TAU * smooth((u - 0.3) / 0.55), 0),
			Top = move(0, -0.15 * sq + 0.08 * air, 0),
			Side_L = move(-0.1 * sq, 0, 0),
			Side_R = move(0.1 * sq, 0, 0),
		}
	elseif clip == "Staff" then
		local k = math.max(0, wave(t, 0.4))
		return {
			Middle = rot(-0.25 * k, 0, 0),
			Top = move(0, -0.03 * k, 0),
		}
	end
	return {}
end

function shapes.Float(clip, t)
	if clip == "Walk" then
		local a = math.sin(TAU * t)
		return {
			Body = move(0, 0.03 * a, 0, -0.18, 0, 0),
			Head = rot(0.1, 0, 0),
			Tail_1 = rot(-0.35 + 0.1 * a, 0, 0),
			Tail_2 = rot(-0.25 + 0.15 * math.sin(TAU * t - 1), 0, 0),
			Arm_L = rot(-0.3 + 0.1 * a, 0, -0.1),
			Arm_R = rot(-0.3 - 0.1 * a, 0, 0.1),
		}
	elseif clip == "Idle" then
		return {
			Body = move(0, 0.04 * wave(t, 2.4), 0),
			Head = rot(0, 0.12 * wave(t, 6), 0),
			Tail_1 = rot(0, 0, 0.12 * wave(t, 2.4, -0.13)),
			Tail_2 = rot(0, 0, 0.15 * wave(t, 2.4, -0.26)),
			Arm_L = rot(0, 0, -0.05 * wave(t, 3)),
			Arm_R = rot(0, 0, 0.05 * wave(t, 3)),
		}
	elseif clip == "Happy" then
		local w = wave(t, 0.35)
		return {
			Body = move(0, 0.08 * math.abs(wave(t, 1.4)), 0),
			Head = rot(0, 0, 0.15 * wave(t, 0.7)),
			Arm_L = rot(0, 0, -2.0 - 0.25 * w),
			Arm_R = rot(0, 0, 2.0 + 0.25 * w),
			Tail_1 = rot(0, 0, 0.2 * wave(t, 0.35)),
			Tail_2 = rot(0, 0, 0.3 * wave(t, 0.35, -0.2)),
		}
	elseif clip == "Sad" then
		return {
			Body = move(0, -0.05 + 0.01 * wave(t, 3), 0, -0.15, 0, 0),
			Head = rot(-0.4, 0, 0),
			Arm_L = rot(0.1, 0, 0.08),
			Arm_R = rot(0.1, 0, -0.08),
		}
	elseif clip == "CheckIn" then
		local u = t / MonsterMotion.OneShot.CheckIn
		return {
			Body = move(0, 0.1 * bump(u, 0, 1), 0, 0, TAU * smooth(u), 0),
			Arm_R = rot(0, 0, 2.0 * bump(u, 0, 1)),
			Arm_L = rot(0, 0, -0.6 * bump(u, 0, 1)),
			Tail_1 = rot(0, 0, -0.3 * bump(u, 0.1, 1)),
			Tail_2 = rot(0, 0, -0.4 * bump(u, 0.2, 1)),
		}
	elseif clip == "Staff" then
		return {
			Body = rot(-0.1, 0, 0),
			Arm_R = rot(1.0 + 0.3 * wave(t, 0.8), 0, 0.3 * wave(t, 0.8, 0.25)),
		}
	end
	return {}
end

function shapes.Serpent(clip, t)
	if clip == "Walk" then
		return {
			Coil = move(0, 0.01 * math.abs(math.sin(TAU * t)), 0, 0, 0.08 * math.sin(TAU * t), 0),
			Neck = rot(0, 0, 0.15 * math.sin(TAU * t + 0.5)),
			Head = rot(0, 0, -0.12 * math.sin(TAU * t + 1)),
			Tail_1 = rot(0, 0.35 * math.sin(TAU * t + 1.5), 0),
			Tail_2 = rot(0, 0.45 * math.sin(TAU * t + 2.5), 0),
		}
	elseif clip == "Idle" then
		return {
			Neck = rot(0.04 * wave(t, 3), 0, 0.06 * wave(t, 4)),
			Head = rot(0, 0.2 * wave(t, 6), 0),
			Tail_2 = rot(0, 0.3 * wave(t, 2), 0),
		}
	elseif clip == "Happy" then
		return {
			Coil = move(0, 0.04 * math.abs(wave(t, 1.4)), 0),
			Neck = rot(0, 0, 0.3 * wave(t, 0.7)),
			Head = rot(0.1, 0, -0.3 * wave(t, 0.7)),
			Tail_2 = rot(0, 0.6 * wave(t, 0.35), 0),
		}
	elseif clip == "Sad" then
		return {
			Neck = rot(-0.35, 0, 0.04 * wave(t, 3)),
			Head = rot(-0.3, 0, 0),
		}
	elseif clip == "CheckIn" then
		local u = t / MonsterMotion.OneShot.CheckIn
		local bow = bump(u, 0.35, 1)
		return {
			Neck = rot(0.2 * bump(u, 0, 0.4) - 0.5 * bow, 0, 0),
			Head = rot(-0.4 * bow, 0, 0),
			Tail_2 = rot(0, 0.6 * bump(u, 0, 0.5), 0),
		}
	elseif clip == "Staff" then
		local k = math.max(0, wave(t, 0.8))
		return {
			Neck = rot(-0.2 - 0.2 * k, 0, 0),
			Head = rot(-0.2 * k, 0, 0),
		}
	end
	return {}
end

local function wrap(a: number): number
	return (a + math.pi) % TAU - math.pi
end

--[[ The pose of `shape` playing `clip` at `t` (Walk: cycles; else seconds since
	it began). Angles are wrapped to [-pi, pi), so a twirl ends where it began. An
	unknown shape or clip is the rest pose (empty). ]]
function MonsterMotion.pose(shape: string, clip: string, t: number): Pose
	local fn = shapes[shape]
	if not fn then
		return {}
	end
	local pose = fn(clip, t)
	for name, bp in pose do
		pose[name] = { r = Vector3.new(wrap(bp.r.X), wrap(bp.r.Y), wrap(bp.r.Z)), p = bp.p }
	end
	return pose
end

local REST: BonePose = { r = ZERO, p = ZERO }

--[[ `a` blended toward `b` by `alpha` (0 is `a`, 1 is `b`); a bone missing on one
	side is at rest there. ]]
function MonsterMotion.blend(a: Pose, b: Pose, alpha: number): Pose
	local out: Pose = {}
	for name, pa in a do
		local pb = b[name] or REST
		out[name] = { r = pa.r:Lerp(pb.r, alpha), p = pa.p:Lerp(pb.p, alpha) }
	end
	for name, pb in b do
		if not a[name] then
			out[name] = { r = pb.r * alpha, p = pb.p * alpha }
		end
	end
	return out
end

--[[ A bone's `Transform` for `bp`, given its rest orientation in the model's
	frame (`rest`, only its rotation is read) and the monster's height in studs:
	the rotation is about the model's axes, the offset in heights along them. ]]
function MonsterMotion.transform(rest: CFrame, bp: BonePose, height: number): CFrame
	local q = rest.Rotation
	local qi = q:Inverse()
	local r = CFrame.fromEulerAnglesXYZ(bp.r.X, bp.r.Y, bp.r.Z)
	return CFrame.new(qi:VectorToWorldSpace(bp.p * height)) * (qi * r * q)
end

return MonsterMotion
