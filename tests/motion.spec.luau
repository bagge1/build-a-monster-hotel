local MonsterMotion = require(Shared.MonsterMotion)
local Species = require(Shared.Species)

local function close(a: CFrame, b: CFrame, eps: number): boolean
	local d = a:Inverse() * b
	local _, angle = d:ToAxisAngle()
	return d.Position.Magnitude <= eps and math.abs(angle) <= eps
end

local function allPoses(fn: (shape: string, clip: string, t: number, pose: MonsterMotion.Pose) -> ())
	for shape in MonsterMotion.Bones do
		for _, clip in MonsterMotion.Clips do
			for i = 0, 40 do
				local t = i * 0.137
				fn(shape, clip, t, MonsterMotion.pose(shape, clip, t))
			end
		end
	end
end

describe("Monster motion (GDD §12, MODELS.md \"The rig\")", function()
	it("every species' body shape has a rig, and every rig every clip", function()
		for _, sp in Species.List do
			expect.truthy(MonsterMotion.Bones[sp.look.shape] ~= nil, `{sp.id}: {sp.look.shape}`)
		end
		for shape in MonsterMotion.Bones do
			for _, clip in MonsterMotion.Clips do
				expect.truthy(next(MonsterMotion.pose(shape, clip, 0.3)) ~= nil, `{shape} {clip} poses nothing`)
			end
		end
	end)

	it("a clip poses only its shape's bones, never RigRoot, with finite values", function()
		allPoses(function(shape, clip, t, pose)
			local own = {}
			for _, b in MonsterMotion.Bones[shape] do
				own[b] = true
			end
			for name, bp in pose do
				expect.truthy(own[name], `{shape} {clip}: {name} is not its bone`)
				for _, v in { bp.r.X, bp.r.Y, bp.r.Z, bp.p.X, bp.p.Y, bp.p.Z } do
					expect.truthy(v == v and math.abs(v) < math.huge, `{shape} {clip} {name} at {t}`)
				end
				expect.truthy(math.abs(bp.r.X) <= math.pi and math.abs(bp.r.Y) <= math.pi, `{name} wrapped`)
				-- An offset is a fraction of the height: a body never leaves itself.
				expect.truthy(bp.p.Magnitude <= 0.5, `{shape} {clip} {name} moves {bp.p.Magnitude} heights`)
			end
		end)
	end)

	it("a looping clip loops: its pose a period later is the same", function()
		for shape in MonsterMotion.Bones do
			for _, clip in MonsterMotion.Clips do
				local period = if clip == "Walk" then 1 else MonsterMotion.Period[clip]
				if period then
					for _, t in { 0.05, 0.4, 1.3 } do
						local a, b = MonsterMotion.pose(shape, clip, t), MonsterMotion.pose(shape, clip, t + period)
						for name, pa in a do
							local q = CFrame.fromEulerAnglesXYZ(pa.r.X, pa.r.Y, pa.r.Z)
							local pb = b[name]
							local qb = CFrame.fromEulerAnglesXYZ(pb.r.X, pb.r.Y, pb.r.Z)
							expect.truthy(
								close(q, qb, 1e-4) and (pa.p - pb.p).Magnitude < 1e-4,
								`{shape} {clip} {name} at {t}`
							)
						end
					end
				end
			end
		end
	end)

	it("a one-shot starts and ends at rest, so it fades in and out without a jump", function()
		for shape in MonsterMotion.Bones do
			for clip, length in MonsterMotion.OneShot do
				for _, t in { 0, length } do
					for name, bp in MonsterMotion.pose(shape, clip, t) do
						local tf = MonsterMotion.transform(CFrame.identity, bp, 5)
						expect.truthy(close(tf, CFrame.identity, 1e-3), `{shape} {clip} {name} at {t}`)
					end
				end
			end
		end
	end)

	it("a pose lands about the model's axes whatever the bone's own rest orientation", function()
		local bp = { r = Vector3.new(0.4, -0.3, 0.2), p = Vector3.new(0.05, -0.1, 0.02) }
		local want = CFrame.fromEulerAnglesXYZ(0.4, -0.3, 0.2)
		for _, rest in { CFrame.identity, CFrame.Angles(1.2, 0.3, -2), CFrame.Angles(-math.pi / 2, 0, math.pi) } do
			local tf = MonsterMotion.transform(rest, bp, 4)
			local world = rest * tf
			expect.truthy(close(world.Rotation, (want * rest).Rotation, 1e-4), "rotation about the model's axes")
			expect.truthy((world.Position - bp.p * 4).Magnitude < 1e-4, "offset in heights along the model's axes")
		end
	end)

	it("a blend runs from the one pose to the other, a missing bone at rest", function()
		local a = MonsterMotion.pose("Biped", "Walk", 0.2)
		local b = MonsterMotion.pose("Biped", "Idle", 1.1)
		for name, bp in MonsterMotion.blend(a, b, 0) do
			local want = a[name] or { r = Vector3.zero, p = Vector3.zero }
			expect.truthy((bp.r - want.r).Magnitude < 1e-9 and (bp.p - want.p).Magnitude < 1e-9, name)
		end
		for name, bp in MonsterMotion.blend(a, b, 1) do
			local want = b[name] or { r = Vector3.zero, p = Vector3.zero }
			expect.truthy((bp.r - want.r).Magnitude < 1e-9 and (bp.p - want.p).Magnitude < 1e-9, name)
		end
	end)

	it("a walk's pace rises with the speed and falls with the size, within bounds", function()
		for shape in MonsterMotion.Bones do
			local slow = MonsterMotion.walkRate(shape, 4, 5)
			local fast = MonsterMotion.walkRate(shape, 8, 5)
			local giant = MonsterMotion.walkRate(shape, 8, 7.5)
			expect.truthy(fast >= slow and giant <= fast, shape)
			expect.truthy(MonsterMotion.walkRate(shape, 0, 5) > 0, `{shape}: a stopped walk still cycles`)
			expect.truthy(MonsterMotion.walkRate(shape, 1000, 1) < 5, `{shape}: a dash is capped`)
		end
	end)
end)
