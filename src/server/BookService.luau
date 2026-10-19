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
	    mutation): a title, "<Mutation> Host" (§4.6's "Golden Host").

	The Book is kept through rebirth (§6.4).
]]

local ReplicatedStorage = game:GetService("ReplicatedStorage")
local ServerScriptService = game:GetService("ServerScriptService")

local Constants = require(ReplicatedStorage.Shared.Constants)
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

-- Records a find, paying what it earns. Returns whether it was new.
function BookService.find(player: Player, speciesId: string, mutation: string?): boolean
	local data = PlayerData.get(player)
	local sp = Species.get(speciesId)
	if not data or not sp then
		return false
	end
	local key = mutation or NORMAL
	local page = data.book[speciesId]
	local newSpecies = page == nil
	if not page then
		page = {}
		data.book[speciesId] = page
	end
	if page[key] then
		return false
	end
	page[key] = true
	if newSpecies then
		local bonus =
			math.floor(Economy.speciesPay(speciesId) * Constants.Book.SpeciesFoundPaySeconds)
		PlayerData.earn(player, bonus)
		Net.fire(
			player,
			"Toast",
			`New in your Monster Book: {sp.name}! +{Format.cash(bonus)}`,
			"Unlock"
		)
		PlayerData.stat(player, "speciesFound")
	elseif mutation then
		Net.fire(
			player,
			"Toast",
			`Monster Book: {Mutations.ById[mutation].name} {sp.name}!`,
			"Unlock"
		)
	end
	local loc = sp.location
	if not data.families[tostring(loc)] and familyDone(data, loc) then
		data.families[tostring(loc)] = true
		data.cosmetics[`Family_{loc}`] = true
		Net.fire(
			player,
			"Announce",
			`You completed the {Locations.get(loc).family} family! +5% income for good`,
			"Rare"
		)
	end
	if mutation then
		local title = `{Mutations.ById[mutation].name} Host`
		if not data.titles[title] and mutationSetDone(data, loc, mutation) then
			data.titles[title] = true
			Net.fire(player, "Announce", `New title: {title}!`, "Rare")
		end
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
		BookService.find(player, g.species, g.mutation)
	end)
	ResidentService.onMoveIn(function(player, _, rec)
		BookService.find(player, rec.species, if rec.mutation ~= "" then rec.mutation else nil)
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
		return tostring(BookService.find(player, args[1] or "Slime", args[2]))
	end)
end

return BookService
