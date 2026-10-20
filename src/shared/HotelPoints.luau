--!strict
--[[
	Where a hotel's shared points are, read from the plot's models (MODELS.md),
	the same on the server and on every client. Since the lobby strip went
	(his rulings 2026-10-20, GDD §5.4, A.1) no single model carries them:

	- `Entrance`: the threshold on the facade's `Facade_Entrance` (`Facade`).
	- `Spawn`: the owner's spawn, the forecourt's `PathFoot`, facing the arch.
	- `Desk`, `Clerk`, `Till`, `Queue_1`..`Queue_4`: on the hotel's first
	  desk, the `FrontDesk` piece with the lowest id (there may be several;
	  each guest queues at its own, `GuestService`).
]]

local HotelPoints = {}

local function rootOf(model: Instance?): BasePart?
	if not model or not model:IsA("Model") then
		return nil
	end
	local root = model.PrimaryPart or model:FindFirstChild("Root")
	return if root and root:IsA("BasePart") then root else nil
end

-- The hotel's desks (`Kind` "Desk" in `Pieces`), lowest piece id first.
function HotelPoints.desks(plot: Model): { Model }
	local out = {}
	local folder = plot:FindFirstChild("Pieces")
	for _, m in if folder then folder:GetChildren() else {} do
		if m:IsA("Model") and m:GetAttribute("Kind") == "Desk" then
			table.insert(out, m)
		end
	end
	table.sort(out, function(a, b)
		return (tonumber(a:GetAttribute("PieceId")) or 0)
			< (tonumber(b:GetAttribute("PieceId")) or 0)
	end)
	return out
end

-- The attachment named `name` (above), or nil.
function HotelPoints.attachment(plot: Model, name: string): Attachment?
	local root: BasePart? = nil
	local point = name
	if name == "Entrance" then
		local facade = plot:FindFirstChild("Facade")
		root = rootOf(facade and facade:FindFirstChild("Facade_Entrance"))
	elseif name == "Spawn" then
		local base = plot:FindFirstChild("Base")
		root = rootOf(base and base:FindFirstChild("Forecourt"))
		point = "PathFoot"
	else
		root = rootOf(HotelPoints.desks(plot)[1])
	end
	local a = root and root:FindFirstChild(point)
	return if a and a:IsA("Attachment") then a else nil
end

function HotelPoints.find(plot: Model, name: string): CFrame?
	local a = HotelPoints.attachment(plot, name)
	return if a then a.WorldCFrame else nil
end

return HotelPoints
