import sc2
from sc2 import run_game, maps, Race, Difficulty
from sc2.player import Bot, Computer
from sc2.ids.unit_typeid import UnitTypeId


class MarineWaveBot(sc2.BotAI):

    def __init__(self):
        self.combinedActions = []
        self.TARGET_SUPPLY = 5
        self.target_barracks = 3

        # amount of marines to wait for until they are sent to enemy base
        self.WAVE_COUNT = 10
    
    async def on_step(self, iteration):
        self.combinedActions = []

        # increase maximum barracks if there is a lot of minerals left over
        if self.minerals > 450:
            self.target_barracks += 1

        # create more supply depots if supply is low enough
        if self.supply_left < self.TARGET_SUPPLY and self.can_afford(UnitTypeId.SUPPLYDEPOT) and self.already_pending(UnitTypeId.SUPPLYDEPOT) < 1:
            worker = self.workers.gathering[1]
            loc = await self.find_placement(UnitTypeId.SUPPLYDEPOT, self.townhalls.random.position,placement_step=3)
            self.combinedActions.append(worker.build(UnitTypeId.SUPPLYDEPOT, loc))

        # build barracks if target is not reached
        if self.units(UnitTypeId.BARRACKS).amount + self.already_pending(UnitTypeId.BARRACKS) < self.target_barracks and self.can_afford(UnitTypeId.BARRACKS):
            worker = self.workers.gathering[0]
            loc = await self.find_placement(UnitTypeId.BARRACKS, self.townhalls.random.position,placement_step=5)
            self.combinedActions.append(worker.build(UnitTypeId.BARRACKS, loc))

        # build as many marines as possible
        if self.can_afford(UnitTypeId.MARINE) and self.supply_left > 0:
            for rax in self.units(UnitTypeId.BARRACKS).idle:
                self.combinedActions.append(rax.train(UnitTypeId.MARINE))

        # loop through marines and send them to enemy starting base
        if self.units(UnitTypeId.MARINE).amount > self.WAVE_COUNT:
            for marine in self.units(UnitTypeId.MARINE):
                self.combinedActions.append(marine.attack(self.enemy_start_locations[0]))

        # send workers to mine minerals
        if iteration % 25 == 0:
            await self.distribute_workers()

        await self.do_actions(self.combinedActions)


run_game(maps.get("Abyssal Reef LE"), [
    Bot(Race.Terran, MarineWaveBot()),
    Computer(Race.Protoss, Difficulty.Medium)
], realtime=True)
