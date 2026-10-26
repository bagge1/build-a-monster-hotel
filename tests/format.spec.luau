local Constants = require(Shared.Constants)
local Format = require(Shared.Format)

-- What a written number says, read back: "1.2K" -> 1200.
local function read(s: string): number
	local sign, digits, suffix = string.match(s, "^(%-?)([%d%.]+)(%a*)$")
	assert(digits, `unreadable "{s}"`)
	local scale = 1
	for i, name in Constants.Format.Suffixes do
		if name == suffix then
			scale = 1000 ^ (i - 1)
		end
	end
	return (if sign == "-" then -1 else 1) * (tonumber(digits) :: number) * scale
end

local SAMPLES = {
	0,
	0.4,
	1,
	999,
	999.99,
	1000,
	1050,
	1234,
	99999,
	999960,
	1e6,
	1.15e6,
	2.3e9,
	7.8e12,
	9.1e15,
	123456789012,
}

describe("Format", function()
	-- §6.2: 1.2K, 3.4M ...; one decimal, cut rather than rounded (Format.number).
	it("a written number never says more than it is, nor less by its last digit", function()
		for _, n in SAMPLES do
			for _, x in { n, -n } do
				local s = Format.number(x)
				local back = read(s)
				local unit = if math.abs(x) < 1000
					then 1
					else 0.1 * 1000 ^ math.floor(math.log(math.abs(x), 1000) + 1e-9)
				expect.atMost(math.abs(back), math.abs(x) * (1 + 1e-12), `{x} reads {s}`)
				expect.truthy(math.abs(x) - math.abs(back) < unit * (1 + 1e-9), `{x} reads {s}`)
				expect.truthy(not string.find(s, "%.%d%d"), `{s}: at most one decimal`)
			end
		end
	end)

	it("a number that is exactly one decimal of its suffix reads exactly so", function()
		local suffixes = Constants.Format.Suffixes
		for tenths = 10, 9999 do
			for i = 2, 3 do
				local n = tenths * 1000 ^ (i - 1) / 10
				local want = (
					if tenths % 10 == 0 then `{tenths // 10}` else `{tenths // 10}.{tenths % 10}`
				) .. suffixes[i]
				expect.eq(Format.number(n), want, `{n}`)
			end
		end
	end)

	it("a bigger number never reads smaller", function()
		local last = -math.huge
		local n = 0
		while n < 1e16 do
			local back = read(Format.number(n))
			expect.atLeast(back, last, `{n}`)
			last = back
			n = n * 1.07 + 1
		end
	end)

	local function clean(s: string, what: string)
		expect.truthy(not string.find(string.lower(s), "nan"), `{what} reads {s}`)
		expect.truthy(not string.match(s, "%-0%.?0*%f[^%d%.]"), `{what} reads {s}: a negative zero`)
	end

	it("cash never prints a NaN, and nothing reads $0", function()
		for _, x in { 0 / 0, -0, 0, 0.4 } do
			expect.eq(Format.cash(x), "$0", `{x}`)
		end
	end)

	it("cash never prints a negative zero", function()
		for _, x in { -0.5, -0.001, -1e-12 } do
			clean(Format.cash(x), `cash {x}`)
		end
	end)

	it("cash per second never prints a negative zero or a NaN", function()
		for _, x in { 0 / 0, -0.04, -0.4, 0.04, 0.4, 12 } do
			clean(Format.perSecond(x), `{x} per second`)
		end
	end)

	it("a duration is never negative and reads back to its whole seconds", function()
		for _, sec in { -5, 0 / 0, 0, 0.9, 59, 60, 61, 599, 3599 } do
			local s = Format.duration(sec)
			local m, ss = string.match(s, "^(%d+):(%d%d)$")
			expect.truthy(m ~= nil, `{sec} reads {s}`)
			expect.atMost(tonumber(ss) :: number, 59, `{s}'s seconds`)
			local want = if sec ~= sec then 0 else math.max(0, math.floor(sec))
			expect.eq(tonumber(m) * 60 + tonumber(ss), want, `{sec} reads {s}`)
		end
		for _, sec in { 3600, 3661, 86399, 200000 } do
			local s = Format.duration(sec)
			local h, mm = string.match(s, "^(%d+)h (%d%d)m$")
			expect.truthy(h ~= nil, `{sec} reads {s}`)
			expect.atMost(tonumber(mm) :: number, 59, `{s}'s minutes`)
			expect.eq(tonumber(h) * 3600 + tonumber(mm) * 60, sec - sec % 60, `{sec} reads {s}`)
		end
	end)

	it("a rating reads as its stars, whole or half", function()
		for _, r in { 1, 1.5, 2, 3.5, 5 } do
			local s = Format.stars(r)
			expect.eq(tonumber(string.match(s, "^([%d%.]+)★$")), r, s)
		end
	end)
end)
