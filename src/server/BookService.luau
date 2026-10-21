--!strict
--[[
	The Monster Book (GDD §4.6): one page per species, with every mutation
	found. A species is found when one stays in your hotel (a check-out),
	in whatever mutation it came.

	Rewards (§4.6, Appendix A.5):
	  - each species found: a cash bonus of 60 s of its pay;
	  - each family completed: a permanent +5 % income (an `Income` provider)
	    and the family's cosmetic;
	  - each mutation set completed (every species of a family found in that
	    mutation): a title, "<Mutation> Host" (§4.6's "Golden Host");
	  - a stacked mutation (A.11.5) fills its size's and its look's entries,
	    and the first stack gives a title (`find`).

	The Book is kept through rebirth (§6.4).
]]

local ReplicatedStorage = game:GetService("ReplicatedStorage")
local ServerScriptService = game:GetService("ServerScriptService")

local Constants = require(ReplicatedStorage.Shared.Constants)
local Cosmetics = require(ReplicatedStorage.Shared.Cosmetics)
local Economy = require(ReplicatedStorage.Shared.Economy)
local Format = require(ReplicatedStorage.Shared.Format)
local Locations = require(ReplicatedStorage.Shared.Locations)
local Mutations = require(ReplicatedStorage.Shared.Mutations)
local Net = require(ReplicatedStorage.Shared.Net)
local Species = require(ReplicatedStorage.Shared.Species)
local PlayerData = require(ServerScriptService.Server.PlayerData)
local GuestService = require(ServerScriptService.Server.GuestService)
local ResidentService = require(ServerScriptService.Server.ResidentService)
local StateService = require(ServerScriptService.Server.StateService)
local Income = require(ServerScriptService.Server.Income)
local DevGrant = require(ServerScriptService.Server.DevGrant)

local BookService = {}

local NORMAL = "Normal"

local function familyDone(data: PlayerData.Data, location: number): boolean
	local list = Species.ofLocation(location)
	if #list == 0 then
		return false
	end
	for _, sp in list do
		if not data.book[sp.id] then
			return false
		end
	end
	return true
end

local function mutationSetDone(data: PlayerData.Data, location: number, mutation: string): boolean
	local list = Species.ofLocation(location)
	if #list == 0 then
		return false
	end
	for _, sp in list do
		local page = data.book[sp.id]
		if not page or not page[mutation] then
			return false
		end
	end
	return true
end

-- A guest or resident that is a stack (A.11.5): the page's mark, beside its two entries.
local STACKED = "Stacked"

--[[ Records a find, paying what it earns. Returns whether anything was new.
	A STACK (a size and a look, A.11.5 decision 4a) fills both of its single
	entries, marks the page `Stacked`, and the first stack of any kind gives
	`Constants.Mutations.StackTitle`. A month's look is a Seasons entry
	(`Mutations.Seasonal`, with the season's): it gives no mutation-set
	title, so no title waits a year. ]]
function BookService.find(
	player: Player,
	speciesId: string,
	mutation: string?,
	size: string?
): boolean
	local data = PlayerData.get(player)
	local sp = Species.get(speciesId)
	if not data or not sp then
		return false
	end
	local keys = {}
	for _, id in { size, mutation } do
		if id and Mutations.ById[id :: string] then
			table.insert(keys, id :: string)
		end
	end
	if #keys == 0 then
		table.insert(keys, NORMAL)
	end
	local page = data.book[speciesId]
	local newSpecies = page == nil
	if not page then
		page = {}
		data.book[speciesId] = page
	end
	local stacked = size ~= nil and mutation ~= nil
	local fresh = {}
	for _, key in keys do
		if not page[key] then
			page[key] = true
			table.insert(fresh, key)
		end
	end
	local newStack = stacked and not page[STACKED]
	if newStack then
		page[STACKED] = true
	end
	if #fresh == 0 and not newStack then
		return false
	end
	if newSpecies then
		local bonus =
			math.floor(Economy.speciesPay(speciesId) * Constants.Book.SpeciesFoundPaySeconds)
		PlayerData.earn(player, bonus)
		Net.fire(
			player,
			"Toast",
			`New in your Monster Book: {Mutations.prefix(size, mutation)}{sp.name}! +{Format.cash(
				bonus
			)}`,
			"Unlock"
		)
		PlayerData.stat(player, "speciesFound")
	elseif #fresh > 0 and fresh[1] ~= NORMAL then
		local names = {}
		for _, key in fresh do
			table.insert(names, Mutations.ById[key].name)
		end
		Net.fire(player, "Toast", `Monster Book: {table.concat(names, " ")} {sp.name}!`, "Unlock")
	end
	local loc = sp.location
	if not data.families[tostring(loc)] and familyDone(data, loc) then
		data.families[tostring(loc)] = true
		data.cosmetics[Cosmetics.family(loc)] = true
		Net.fire(
			player,
			"Announce",
			`You completed the {Locations.get(loc).family} family! +5% income for good`,
			"Rare"
		)
	end
	for _, key in fresh do
		local row = Mutations.ById[key]
		if row and row.month == nil then -- a month's look gives no set title (A.11.5)
			local title = `{row.name} Host`
			if not data.titles[title] and mutationSetDone(data, loc, key) then
				data.titles[title] = true
				Net.fire(player, "Announce", `New title: {title}!`, "Rare")
			end
		end
	end
	local stackTitle = Constants.Mutations.StackTitle
	if stacked and not data.titles[stackTitle] then
		data.titles[stackTitle] = true
		Net.fire(
			player,
			"Announce",
			`Your first stacked mutation, a {Mutations.prefix(size, mutation)}{sp.name}! New title: {stackTitle}!`,
			"Rare"
		)
	end
	StateService.mark(player)
	return true
end

function BookService.Init() end

function BookService.Start()
	Income.addPermanent(function(player)
		local data = PlayerData.get(player)
		if not data then
			return 0
		end
		local n = 0
		for _, done in data.families do
			if done then
				n += 1
			end
		end
		return n * Constants.Book.FamilyBonus
	end)
	GuestService.onCheckout(function(player, g)
		BookService.find(player, g.species, g.mutation, g.size)
	end)
	ResidentService.onMoveIn(function(player, _, rec)
		BookService.find(
			player,
			rec.species,
			if rec.mutation ~= "" then rec.mutation else nil,
			rec.size
		)
	end)
	StateService.provide("book", function(_, data)
		local pages = {}
		for _, sp in Species.List do
			local page = data.book[sp.id]
			local found = {}
			if page then
				for k in page do
					table.insert(found, k)
				end
			end
			pages[sp.id] = found
		end
		local titles = {}
		for t in data.titles do
			table.insert(titles, t)
		end
		local families = {}
		for k, v in data.families do
			if v then
				table.insert(families, tonumber(k))
			end
		end
		return { pages = pages, titles = titles, families = families }
	end)
	DevGrant.register("find", function(player, args)
		-- `find <species> [look] [size]`
		return tostring(BookService.find(player, args[1] or "Slime", args[2], args[3]))
	end)
end

return BookService
