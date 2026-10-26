--!strict
--[[
	Calls that must not take their loop down with them (2026-10-26 review: a
	throw in one hotel's recompute, one guest's tick or one street's draw ended
	the loop it ran in for the server's life, or starved every item after it).

	`Safe.call(label, fn, ...)` runs `fn` in a pcall and reports a failure with
	its traceback; it returns what pcall returns. `Safe.each(t, fn, label)`
	calls `fn(key, value)` for every entry of `t`, each in its own pcall, so
	one bad item is skipped and the rest still run. `Safe.warn(label, message)`
	is the report alone, for a pcall that has its own.

	A report prints at most once per label per minute, then says how many it
	held back: an error that repeats every tick does not bury the log. The
	label is the key, so put the system and the job in it ("[hotel]
	recompute"), and the item (a player, a street) in what is reported.
]]

local Safe = {}

local QUIET = 60 -- seconds between two reports under one label

local lastAt: { [string]: number } = {}
local held: { [string]: number } = {}

function Safe.warn(label: string, message: string)
	local now = os.clock()
	local at = lastAt[label]
	if at and now - at < QUIET then
		held[label] = (held[label] or 0) + 1
		return
	end
	lastAt[label] = now
	local more = held[label]
	held[label] = nil
	if more then
		warn(`{label} {message} ({more} more in the last minute)`)
	else
		warn(`{label} {message}`)
	end
end

local function trace(err: any): string
	return debug.traceback(tostring(err), 2)
end

function Safe.call(label: string, fn: (...any) -> ...any, ...: any): (boolean, ...any)
	local result = table.pack(xpcall(fn, trace, ...))
	if not result[1] then
		Safe.warn(label, tostring(result[2]))
	end
	return table.unpack(result, 1, result.n)
end

function Safe.each<K, V>(t: { [K]: V }, fn: (K, V) -> (), label: string)
	for k, v in t do
		local ok, err = xpcall(fn, trace, k, v)
		if not ok then
			Safe.warn(label, `{tostring(k)}: {err}`)
		end
	end
end

return Safe
