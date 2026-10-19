--!strict
--[[
	Residents' passive perks (GDD §4.6 "each resident gives one passive perk";
	Appendix A.5). Every resident gives its species' perk, in the Wing or on
	staff (not while it is away in the Hunter Camp), and perks of a kind add
	up (§6.2's stacking: add within a category).

	Kinds, and the system that reads each:
	  Income, HunterIncome  fractions of income (Income; HunterIncome only during Hunter Night)
	  ResidentIncome        a fraction more for the Wing's earnings (ResidentService)
	  Tips, RequestTips     fractions more on check-out and request tips (GuestService)
	  Bus                   a fraction of bus score (BusService)
	  Speed                 a fraction faster guests (GuestService)
	  Service, Fun, Cleanliness  rating points (HotelService → Rating)
]]

export type Perk = { kind: string, amount: number, text: string }

local Perks = {}

Perks.BySpecies = {
	Slime = { kind = "Tips", amount = 0.05, text = "+5% tips" },
	Skeleton = { kind = "Service", amount = 5, text = "+5 Service" },
	PumpkinHead = { kind = "Fun", amount = 5, text = "+5 Fun" },
	Ghost = { kind = "Cleanliness", amount = 5, text = "+5 Cleanliness" },
	Mummy = { kind = "Speed", amount = 0.05, text = "+5% guest walking speed" },
	Zombie = { kind = "ResidentIncome", amount = 0.05, text = "+5% resident income" },
	Witch = { kind = "RequestTips", amount = 0.05, text = "+5% request tips" },
	Werewolf = { kind = "HunterIncome", amount = 0.10, text = "+10% income during Hunter Night" },
	VampireCount = { kind = "Bus", amount = 0.05, text = "+5% bus score" },
	GrandBanshee = { kind = "Income", amount = 0.10, text = "+10% income" },
	SnowballSprite = { kind = "Tips", amount = 0.05, text = "+5% tips" },
	IceImp = { kind = "Fun", amount = 5, text = "+5 Fun" },
	FrostTroll = { kind = "Service", amount = 5, text = "+5 Service" },
	Yeti = { kind = "Cleanliness", amount = 5, text = "+5 Cleanliness" },
	SnowWitch = { kind = "RequestTips", amount = 0.05, text = "+5% request tips" },
	IceWyrm = { kind = "Bus", amount = 0.05, text = "+5% bus score" },
	AuroraSpirit = { kind = "Income", amount = 0.10, text = "+10% income" },
} :: { [string]: Perk }

export type Resident = { species: string, campUntil: number }

-- The sum of one kind of perk over a set of residents, at time `now` (os.time).
function Perks.total(residents: { [any]: Resident }, kind: string, now: number): number
	local sum = 0
	for _, r in residents do
		local perk = Perks.BySpecies[r.species]
		if perk and perk.kind == kind and r.campUntil <= now then
			sum += perk.amount
		end
	end
	return sum
end

return Perks
