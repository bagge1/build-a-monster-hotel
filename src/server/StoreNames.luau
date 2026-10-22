--!strict
--[[
	The DataStore names, apart for Studio and the published game (LAUNCH.md #2,
	his ruling 2026-10-23: everyone starts from zero at launch, and no test
	profile lives in the store players save to).

	Studio keeps the names every playtest so far has written, so its test
	profiles (`Player_Test_*`) stay; the published game reads names of its own
	that nothing in Studio ever writes.
]]

local RunService = game:GetService("RunService")

local StoreNames = {}

local live = not RunService:IsStudio()

-- "Players_v1" → "MonsterHotel_Live_Players_v1" on a published server, "MonsterHotel_Players_v1" in Studio.
function StoreNames.of(base: string): string
	return if live then `MonsterHotel_Live_{base}` else `MonsterHotel_{base}`
end

return StoreNames
