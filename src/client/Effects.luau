--!strict
--[[
	Little moments (GDD §11 "the moment of joy", §12): a sparkle when a guest
	checks in, a big burst of sparkles and bats for a Legendary or Mythic one
	(the whole street sees it), hearts for a move-in. Client-only and short:
	each effect cleans itself up.
]]

local ReplicatedStorage = game:GetService("ReplicatedStorage")

local Net = require(ReplicatedStorage.Shared.Net)

local Effects = {}

local function burst(
	at: Vector3,
	colour: ColorSequence,
	count: number,
	size: number,
	speed: number,
	life: number
)
	local anchor = Instance.new("Part")
	anchor.Anchored = true
	anchor.CanCollide = false
	anchor.CanQuery = false
	anchor.CanTouch = false
	anchor.Transparency = 1
	anchor.Size = Vector3.one
	anchor.CFrame = CFrame.new(at + Vector3.new(0, 3, 0))
	local e = Instance.new("ParticleEmitter")
	e.Color = colour
	e.LightEmission = 1
	e.Size = NumberSequence.new({
		NumberSequenceKeypoint.new(0, size),
		NumberSequenceKeypoint.new(1, 0),
	})
	e.Speed = NumberRange.new(speed * 0.5, speed)
	e.SpreadAngle = Vector2.new(180, 180)
	e.Lifetime = NumberRange.new(life * 0.6, life)
	e.Rate = 0
	e.Parent = anchor
	anchor.Parent = workspace
	e:Emit(count)
	task.delay(life + 0.5, function()
		anchor:Destroy()
	end)
end

local function bats(at: Vector3)
	-- A flock of little dark bats (blocks with wings) fluttering up and away.
	for i = 1, 8 do
		local bat = Instance.new("Part")
		bat.Anchored = true
		bat.CanCollide = false
		bat.CanQuery = false
		bat.Color = Color3.fromRGB(40, 25, 60)
		bat.Material = Enum.Material.SmoothPlastic
		bat.Size = Vector3.new(1.4, 0.2, 0.6)
		local angle = i / 8 * math.pi * 2
		local dir = Vector3.new(math.cos(angle), 1.2, math.sin(angle)).Unit
		bat.CFrame = CFrame.new(at + Vector3.new(0, 3, 0))
		bat.Parent = workspace
		task.spawn(function()
			local t = 0
			while t < 2 do
				local dt = task.wait()
				t += dt
				local flap = math.sin(t * 30) * 0.4
				bat.CFrame = CFrame.new(at + Vector3.new(0, 3, 0) + dir * t * 12)
					* CFrame.Angles(flap, angle, 0)
				bat.Transparency = math.clamp(t - 1.2, 0, 1)
			end
			bat:Destroy()
		end)
	end
end

function Effects.Init() end

function Effects.Start()
	Net.listen("Moment", function(kind: string, data: any)
		local at = data and data.at
		if typeof(at) ~= "Vector3" then
			return
		end
		if kind == "CheckIn" then
			burst(at, ColorSequence.new(Color3.fromRGB(255, 230, 150)), 12, 0.6, 6, 1)
		elseif kind == "RareCheckIn" then
			burst(
				at,
				ColorSequence.new(Color3.fromRGB(255, 200, 80), Color3.fromRGB(200, 120, 255)),
				60,
				1.2,
				14,
				2
			)
			bats(at)
		end
	end)
end

return Effects
