--!strict
--[[
	Activity furniture's Luau blockouts (GDD A.13.5 step 2, night draft
	2026-10-26): the pieces guests visit, in grey boxes of the piece's colour,
	carrying exactly the attachments MODELS.md "Activity furniture: visitors'
	spots" names (`Root`, `Body`, a pool's `Water`, `Use_<n>` with `Pose`), so a
	model delivered later (`Furniture_<Id>` in a location's kit, found first by
	`HotelKit.decor`) replaces the geometry and nothing else (CLAUDE.md, "A
	blockout in Luau is allowed").

	EVERY MEASUREMENT OF THESE BLOCKOUTS STAYS IN THIS FILE. The server finds a
	visitor's spot through the attachments (`ActivityKit.spots`), never through a
	part's position or size.

	Frames are MODELS.md "Furniture"'s: origin at the footprint's centre on the
	floor, front toward −Z, `w × d` squares of 3 studs (the `Pieces` row), the
	body 0.4 inside the footprint's edge. A spot (MODELS.md):
	- `Stand`, `Play`, `Lift` stood at: on the floor 1.5 in front of an edge
	  (the centre of the square there), LookVector toward the piece;
	- `Sit`, `Watch`: on the seat's top at its middle, LookVector the way the
	  sitter faces; `Lie` (and `Lift` on a bench): on the lying surface's top,
	  LookVector toward the foot end;
	- `Dance`: on the floor or the deck it is danced on, LookVector the way it faces;
	- `Swim`: at the water's surface, inside the basin's inner edge by 1.5.
	Two spots never share a 3-stud square.

	This file is a new module beside `HotelKit` (which calls `blockout` once,
	after the kit's model is not found) so the activity pieces' measurements do
	not crowd the hotel kit's.
]]

local ReplicatedStorage = game:GetService("ReplicatedStorage")

local Constants = require(ReplicatedStorage.Shared.Constants)
local Pieces = require(ReplicatedStorage.Shared.Pieces)

local G = Constants.Grid
local SQUARE = G.CellSize / G.Squares -- 3 studs
local INSET = 0.4 -- MODELS.md "Decor": the body 0.4 inside the footprint's edge
local FRONT = SQUARE / 2 -- a `Stand` spot is the centre of the square in front: 1.5 out

local ActivityKit = {}

-- The poses a spot may take (MODELS.md "Activity furniture": `Pose`).
ActivityKit.Poses = {
	Sit = true,
	Stand = true,
	Lean = true,
	Dance = true,
	Swim = true,
	Lie = true,
	Lift = true,
	Watch = true,
	Play = true,
}

type Spot = { at: Vector3, look: Vector3, pose: string }
-- A piece's spots and its body, worked out from its footprint in studs (W × D) and its row's height.
type Shape = {
	spots: (W: number, D: number, h: number) -> { Spot },
	body: ((model: Model, W: number, D: number, h: number, colour: Color3) -> ())?,
}

local FWD = Vector3.new(0, 0, 1) -- toward the piece from in front of it
local BACK = Vector3.new(0, 0, -1) -- the piece's front: a sitter's or a dancer's way

local function part(
	parent: Instance,
	name: string,
	size: Vector3,
	at: Vector3,
	colour: Color3
): Part
	local p = Instance.new("Part")
	p.Name = name
	p.Anchored = true
	p.Size = size
	p.CFrame = CFrame.new(at)
	p.Material = Enum.Material.SmoothPlastic
	p.TopSurface = Enum.SurfaceType.Smooth
	p.BottomSurface = Enum.SurfaceType.Smooth
	p.Color = colour
	p.CanCollide = false -- MODELS.md: `Body` not colliding
	p.Parent = parent
	return p
end

local function darker(c: Color3, f: number): Color3
	return Color3.new(c.R * f, c.G * f, c.B * f)
end

-- One spot stood at in front of the piece (z = −D/2 − 1.5), at x.
local function front(x: number, D: number, pose: string): Spot
	return { at = Vector3.new(x, 0, -D / 2 - FRONT), look = FWD, pose = pose }
end

-- A spot stood at in front of each of the piece's `n` front squares, centred.
local function alongFront(W: number, D: number, pose: string): { Spot }
	local out = {}
	local n = math.max(1, math.floor(W / SQUARE + 0.5))
	for i = 1, n do
		table.insert(out, front((i - (n + 1) / 2) * SQUARE, D, pose))
	end
	return out
end

-- A seat on each of the piece's front squares: `Sit`-like spots on top at `y`, facing −Z.
local function seats(W: number, y: number, pose: string): { Spot }
	local out = {}
	local n = math.max(1, math.floor(W / SQUARE + 0.5))
	for i = 1, n do
		table.insert(
			out,
			{ at = Vector3.new((i - (n + 1) / 2) * SQUARE, y, 0), look = BACK, pose = pose }
		)
	end
	return out
end

-- The default body: one box filling the footprint less the inset (MODELS.md "Decor"), flat for a rug.
local function box(model: Model, W: number, D: number, h: number, colour: Color3)
	part(
		model,
		"Body",
		Vector3.new(W - 2 * INSET, h, D - 2 * INSET),
		Vector3.new(0, h / 2, 0),
		colour
	)
end

local function rug(model: Model, W: number, D: number, h: number, colour: Color3)
	part(model, "Body", Vector3.new(W, h, D), Vector3.new(0, h / 2, 0), colour)
end

-- A wall piece's body: against the back, as HotelKit's wall decor (MODELS.md "Decor": `Wall` layer).
local function onWall(model: Model, W: number, D: number, h: number, colour: Color3)
	local depth = math.min(0.8, D - 2 * INSET)
	part(
		model,
		"Body",
		Vector3.new(W - 2 * INSET, h, depth),
		Vector3.new(0, h / 2, D / 2 - INSET - depth / 2),
		colour
	)
end

local function none(): { Spot }
	return {}
end

--[[ The pieces, by `Pieces` decor id (GDD A.13.2's key and other furniture).
	The first four types' key pieces (A.13.5 step 2: Game Room, Bar, Indoor
	Pool, Cinema) have shaped bodies; the rest are single boxes with their
	spots. A piece with no spots (a screen, a speaker) is looked at, not used. ]]
local shapes: { [string]: Shape } = {
	-- ===== Game Room, Billiard Hall (A.13.2): played round the table =====
	PoolTable = {
		-- Two players a long side, at the table's edge, facing its middle (MODELS.md `Play`).
		spots = function(_W, D, _h)
			return {
				{ at = Vector3.new(-SQUARE, 0, -D / 2 - FRONT), look = FWD, pose = "Play" },
				{ at = Vector3.new(SQUARE, 0, -D / 2 - FRONT), look = FWD, pose = "Play" },
				{ at = Vector3.new(-SQUARE, 0, D / 2 + FRONT), look = BACK, pose = "Play" },
				{ at = Vector3.new(SQUARE, 0, D / 2 + FRONT), look = BACK, pose = "Play" },
			}
		end,
		body = function(model, W, D, h, colour)
			local top = 0.4
			part(
				model,
				"Body",
				Vector3.new(W - 2 * INSET, top, D - 2 * INSET),
				Vector3.new(0, h - top / 2, 0),
				colour
			)
			part(
				model,
				"Body",
				Vector3.new(W - 2 * INSET - 2, h - top, D - 2 * INSET - 2),
				Vector3.new(0, (h - top) / 2, 0),
				darker(colour, 0.6)
			)
		end,
	},
	PingPongTable = {
		-- One player an end, facing the net, on the middle of a square there (z 0 is a square's edge).
		spots = function(W, _D, _h)
			local z = SQUARE / 2
			return {
				{
					at = Vector3.new(-W / 2 - FRONT, 0, -z),
					look = Vector3.new(1, 0, 0),
					pose = "Play",
				},
				{
					at = Vector3.new(W / 2 + FRONT, 0, z),
					look = Vector3.new(-1, 0, 0),
					pose = "Play",
				},
			}
		end,
		body = function(model, W, D, h, colour)
			local table_ = 2.5
			part(
				model,
				"Body",
				Vector3.new(W - 2 * INSET, 0.2, D - 2 * INSET),
				Vector3.new(0, table_ - 0.1, 0),
				colour
			)
			part(
				model,
				"Body",
				Vector3.new(0.1, h - table_, D - 2 * INSET),
				Vector3.new(0, (h + table_) / 2, 0),
				Color3.new(1, 1, 1)
			)
			part(
				model,
				"Body",
				Vector3.new(W - 2 * INSET - 2, table_ - 0.2, D - 2 * INSET - 2),
				Vector3.new(0, (table_ - 0.2) / 2, 0),
				darker(colour, 0.5)
			)
		end,
	},
	ArcadeCabinet = {
		spots = function(W, D, _h)
			return alongFront(W, D, "Play")
		end,
	},
	-- ===== Bar (A.13.2), as `blender/rooms/haunted_manor_bar`'s draft carries them =====
	BarCounter = {
		-- Three stood at the counter, one a front square (Use_1..3 `Stand`).
		spots = function(W, D, _h)
			return alongFront(W, D, "Stand")
		end,
		body = function(model, W, D, h, colour)
			local counter, depth = 3.7, 1.6
			local inner = D - 2 * INSET
			local z0 = -D / 2 + INSET
			part(
				model,
				"Body",
				Vector3.new(W - 2 * INSET, counter, depth),
				Vector3.new(0, counter / 2, z0 + depth / 2),
				colour
			)
			local back = inner - depth
			part(
				model,
				"Body",
				Vector3.new(W - 2 * INSET, h, back),
				Vector3.new(0, h / 2, z0 + depth + back / 2),
				darker(colour, 0.6)
			)
		end,
	},
	SmallStage = {
		-- One performer on the deck, facing the room (Use_1 `Dance`).
		spots = function(_W, _D, _h)
			return { { at = Vector3.new(0, 1.0, 0.3), look = BACK, pose = "Dance" } }
		end,
		body = function(model, W, D, h, colour)
			local deck = 1.0
			part(
				model,
				"Body",
				Vector3.new(W - 2 * INSET, deck, D - 2 * INSET),
				Vector3.new(0, deck / 2, 0),
				colour
			)
			part(
				model,
				"Body",
				Vector3.new(W - 2 * INSET, h, 0.3),
				Vector3.new(0, h / 2, D / 2 - INSET - 0.15),
				darker(colour, 0.5)
			)
		end,
	},
	BarStool = {
		spots = function(_W, _D, h)
			return { { at = Vector3.new(0, h, 0), look = BACK, pose = "Sit" } }
		end,
	},
	-- ===== Indoor Pool (A.13.2): a basin standing on the floor, its `Water` one part =====
	Pool = {
		-- Four swimmers, one a quarter of the basin, inside its inner edge by 1.5.
		spots = function(W, D, h)
			local rim = 0.4
			local surface = h - 0.3
			local x = W / 2 - INSET - rim - 1.5
			local z = D / 2 - INSET - rim - 1.5
			local out = {}
			for _, c in { { -1, -1 }, { 1, -1 }, { -1, 1 }, { 1, 1 } } do
				table.insert(out, {
					at = Vector3.new(c[1] * x, surface, c[2] * z),
					look = Vector3.new(-c[1], 0, 0), -- facing along the pool, toward its middle
					pose = "Swim",
				})
			end
			return out
		end,
		body = function(model, W, D, h, colour)
			local rim = 0.4
			local w, d = W - 2 * INSET, D - 2 * INSET
			local stone = Color3.fromRGB(200, 200, 205)
			part(
				model,
				"Body",
				Vector3.new(w, h, rim),
				Vector3.new(0, h / 2, -d / 2 + rim / 2),
				stone
			)
			part(
				model,
				"Body",
				Vector3.new(w, h, rim),
				Vector3.new(0, h / 2, d / 2 - rim / 2),
				stone
			)
			part(
				model,
				"Body",
				Vector3.new(rim, h, d - 2 * rim),
				Vector3.new(-w / 2 + rim / 2, h / 2, 0),
				stone
			)
			part(
				model,
				"Body",
				Vector3.new(rim, h, d - 2 * rim),
				Vector3.new(w / 2 - rim / 2, h / 2, 0),
				stone
			)
			part(
				model,
				"Body",
				Vector3.new(w - 2 * rim, 0.1, d - 2 * rim),
				Vector3.new(0, 0.05, 0),
				colour
			)
			-- MODELS.md: the water is one part `Water`, not colliding, `CanQuery` false; the code makes it water.
			local water = part(
				model,
				"Water",
				Vector3.new(w - 2 * rim, 0.2, d - 2 * rim),
				Vector3.new(0, h - 0.4, 0),
				Color3.fromRGB(70, 160, 220)
			)
			water.CanQuery = false
			water.CanTouch = false
			water.Material = Enum.Material.Glass
			water.Transparency = 0.4
			water.CastShadow = false
		end,
	},
	Lounger = {
		spots = function(_W, _D, h)
			return { { at = Vector3.new(0, h * 0.6, 0), look = BACK, pose = "Lie" } }
		end,
	},
	-- ===== Cinema (A.13.2): a screen to watch, a row of seats =====
	FilmScreen = {
		-- Against a wall (its row's layer), watched from the seats: no `Use`, no spots (MODELS.md).
		spots = none,
		body = function(model, W, D, h, colour)
			local z = D / 2 - INSET - 0.2
			part(
				model,
				"Body",
				Vector3.new(W - 2 * INSET, h - 1.5, 0.2),
				Vector3.new(0, (h + 1.5) / 2, z),
				colour
			)
			for _, x in { -(W / 2 - INSET - 0.2), W / 2 - INSET - 0.2 } do
				part(
					model,
					"Body",
					Vector3.new(0.4, h, 0.4),
					Vector3.new(x, h / 2, z),
					darker(colour, 0.3)
				)
			end
		end,
	},
	CinemaSeat = {
		--[[ A row of three facing its front (-Z; the player turns the row toward
			the screen): Use_1..3 `Watch` at x -2.75, 0, 2.75, y 1.7, z -0.25, as
			its model (claude/models-cinema). ]]
		spots = function(_W, _D, _h)
			local out = {}
			for _, x in { -2.75, 0, 2.75 } do
				table.insert(out, { at = Vector3.new(x, 1.7, -0.25), look = BACK, pose = "Watch" })
			end
			return out
		end,
		body = function(model, W, D, h, colour)
			local seat = 1.7
			for _, x in { -2.75, 0, 2.75 } do
				part(
					model,
					"Body",
					Vector3.new(2.4, seat, D - 2 * INSET - 0.4),
					Vector3.new(x, seat / 2, -0.2),
					colour
				)
			end
			part(
				model,
				"Body",
				Vector3.new(W - 2 * INSET, h, 0.4),
				Vector3.new(0, h / 2, D / 2 - INSET - 0.2),
				darker(colour, 0.7)
			)
		end,
	},
	Projector = { spots = none },
	PopcornCart = {
		spots = function(W, D, _h)
			return alongFront(W, D, "Stand")
		end,
	},
	-- ===== The rest of A.13.2's furniture: single boxes with their spots =====
	Scoreboard = { spots = none, body = onWall },
	CueRack = { spots = none, body = onWall },
	WallLamp = { spots = none, body = onWall },
	WallMirror = { spots = none, body = onWall },
	LightFloor = {
		-- One dancer a square of the floor.
		spots = function(W, D, h)
			local out = {}
			local nx, nz = math.floor(W / SQUARE + 0.5), math.floor(D / SQUARE + 0.5)
			for j = 1, nz do
				for i = 1, nx do
					table.insert(out, {
						at = Vector3.new(
							(i - (nx + 1) / 2) * SQUARE,
							h,
							(j - (nz + 1) / 2) * SQUARE
						),
						look = BACK,
						pose = "Dance",
					})
				end
			end
			return out
		end,
		body = rug,
	},
	Speaker = { spots = none },
	DiscoBall = { spots = none },
	Microphone = {
		spots = function(W, D, _h)
			return alongFront(W, D, "Stand")
		end,
	},
	KaraokeStage = {
		-- One singer on the deck, facing the room. PLACEHOLDER `Dance` until singing has a pose of its own.
		spots = function(_W, _D, _h)
			return { { at = Vector3.new(0, 1.0, 0), look = BACK, pose = "Dance" } }
		end,
		body = function(model, W, D, h, colour)
			part(
				model,
				"Body",
				Vector3.new(W - 2 * INSET, 1.0, D - 2 * INSET),
				Vector3.new(0, 0.5, 0),
				colour
			)
			part(
				model,
				"Body",
				Vector3.new(W - 2 * INSET, h, 0.3),
				Vector3.new(0, h / 2, D / 2 - INSET - 0.15),
				darker(colour, 0.5)
			)
		end,
	},
	Parasol = { spots = none },
	PoolLadder = { spots = none },
	DivingBoard = { spots = none },
	WeightBench = {
		-- Lain on, lifting (MODELS.md: `Lift` placed as `Lie` would be).
		spots = function(_W, _D, h)
			return { { at = Vector3.new(0, h * 0.6, 0), look = BACK, pose = "Lift" } }
		end,
	},
	Treadmill = {
		-- Stood on the belt, facing the console at the front.
		spots = function(_W, _D, _h)
			return { { at = Vector3.new(0, 0.5, 0.5), look = BACK, pose = "Lift" } }
		end,
	},
	PunchingBag = {
		spots = function(W, D, _h)
			return alongFront(W, D, "Lift")
		end,
	},
	DumbbellRack = {
		spots = function(_W, D, _h)
			return { front(-SQUARE / 2, D, "Lift") } -- the middle of a front square (x 0 is a square's edge)
		end,
	},
	ExerciseMat = {
		spots = function(_W, _D, h)
			return { { at = Vector3.new(0, h, 0), look = BACK, pose = "Lift" } }
		end,
		body = rug,
	},
	HotTub = {
		-- Four soaking, one a corner square, facing the middle (`Sit` on the bench under the water).
		spots = function(W, D, _h)
			local out = {}
			for _, c in { { -1, -1 }, { 1, -1 }, { -1, 1 }, { 1, 1 } } do
				local at = Vector3.new(c[1] * W / 4, 1.0, c[2] * D / 4)
				table.insert(
					out,
					{ at = at, look = Vector3.new(-c[1], 0, -c[2]).Unit, pose = "Sit" }
				)
			end
			return out
		end,
	},
	MassageTable = {
		spots = function(_W, _D, h)
			return { { at = Vector3.new(0, h, 0), look = BACK, pose = "Lie" } }
		end,
	},
	SteamStone = { spots = none },
	SaunaBench = {
		spots = function(W, _D, _h)
			return seats(W, 1.8, "Sit")
		end,
	},
	WaterBucket = { spots = none },
}

-- Whether this file has a blockout for the piece (an activity piece A.13 names).
function ActivityKit.has(id: string): boolean
	return shapes[id] ~= nil
end

--[[ The blockout of an activity piece (MODELS.md "Activity furniture"):
	`Furniture_<Id>` with its `Root`, `Body` parts (a pool's `Water` too) and
	its `Use_1..n` spots, each with its `Pose`; nil for a piece this file does
	not build (HotelKit's own blockout then). ]]
function ActivityKit.blockout(d: Pieces.Decor): Model?
	local shape = shapes[d.id]
	if not shape or not d.furniture then
		return nil
	end
	local W, D = d.w * SQUARE, d.d * SQUARE
	local model = Instance.new("Model")
	model.Name = `Furniture_{d.id}`
	local root = part(model, "Root", Vector3.new(W, 0.2, D), Vector3.new(0, 0.1, 0), d.colour)
	root.Transparency = 1
	root.CanQuery = false
	root.CanTouch = false
	model.PrimaryPart = root
	root.PivotOffset = root.CFrame:Inverse()
	local body = shape.body
		or (if d.layer == "Rug" then rug elseif d.layer == "Wall" then onWall else box)
	body(model, W, D, d.height, d.colour)
	for n, s in shape.spots(W, D, d.height) do
		local a = Instance.new("Attachment")
		a.Name = `Use_{n}`
		a.CFrame = root.CFrame:ToObjectSpace(CFrame.lookAt(s.at, s.at + s.look))
		a:SetAttribute("Pose", s.pose)
		a.Parent = root
	end
	return model
end

--[[ A placed piece's spots, in order (MODELS.md: `Use_1`, `Use_2`, ... from 1
	without a gap). A delivered model that has no `Use_<n>` yet (the Game
	Room's PoolTable, PingPongTable and ArcadeCabinet, today's amenities' key
	furniture, a bar stool) offers its one `Use` as its only spot, so the
	amenities A.13.2 makes activity rooms are visited before their models are
	rebuilt with spots; its build script gets the `Use_<n>` (skill `modelling`). ]]
function ActivityKit.spots(model: Model): { Attachment }
	local numbered: { [number]: Attachment } = {}
	local single: Attachment? = nil
	for _, a in model:GetDescendants() do
		if a:IsA("Attachment") then
			local n = tonumber(string.match(a.Name, "^Use_(%d+)$"))
			if n then
				numbered[n] = a
			elseif a.Name == "Use" and not single then
				single = a
			end
		end
	end
	local out = {}
	local n = 1
	while numbered[n] do
		table.insert(out, numbered[n])
		n += 1
	end
	if #out == 0 and single then
		table.insert(out, single)
	end
	return out
end

-- A spot's pose (its `Pose` attribute, MODELS.md), `Stand` when it names none the contract knows.
function ActivityKit.pose(a: Attachment): string
	local p = a:GetAttribute("Pose")
	return if type(p) == "string" and ActivityKit.Poses[p] then p else "Stand"
end

return ActivityKit
