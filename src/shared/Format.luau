--!strict
--[[
	How numbers are written for a player (GDD §6.2): 1.2K, 3.4M, 5.6B, 7.8T,
	9.1Qa. Shared, so every panel writes money the same way.
]]

local Constants = require(script.Parent.Constants)

local Format = {}

function Format.number(n: number): string
	if n ~= n then
		return "0"
	end
	local sign = if n < 0 then "-" else ""
	n = math.abs(n)
	if n < 1000 then
		-- No sign on a whole part of 0 (2026-10-26 spec: -0.5 read "-0").
		local whole = math.floor(n)
		return (if whole > 0 then sign else "") .. tostring(whole)
	end
	local suffixes = Constants.Format.Suffixes
	local i = 1
	while n >= 1000 and i < #suffixes do
		n /= 1000
		i += 1
	end
	-- One decimal, cut rather than rounded so 999.96K never reads 1000.0K.
	local whole = math.floor(n * 10) / 10
	local text = if whole % 1 == 0 then string.format("%d", whole) else string.format("%.1f", whole)
	return sign .. text .. suffixes[i]
end

function Format.cash(n: number): string
	return "$" .. Format.number(n)
end

function Format.perSecond(n: number): string
	if n < 10 and n % 1 ~= 0 then
		local text = string.format("%.1f", n)
		if text == "-0.0" then
			text = "0.0" -- a tiny negative rate reads no "-0.0" (2026-10-26 spec)
		end
		return "$" .. text .. "/s"
	end
	return Format.cash(n) .. "/s"
end

-- A rating as stars: 3.5 -> "3.5★".
function Format.stars(rating: number): string
	return (if rating % 1 == 0 then string.format("%d", rating) else string.format("%.1f", rating))
		.. "★"
end

function Format.duration(seconds: number): string
	seconds = math.max(0, math.floor(seconds))
	if seconds >= 3600 then
		return string.format("%dh %02dm", seconds // 3600, (seconds % 3600) // 60)
	end
	return string.format("%d:%02d", seconds // 60, seconds % 60)
end

return Format
