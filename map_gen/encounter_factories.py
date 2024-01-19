from map_gen.encounter import Encounter
import actor_factories
import item_factories

hound_pack = Encounter(enemies=[actor_factories.hound for _ in range(3)], items=[])

zombie_mob = Encounter(
    enemies=[actor_factories.zombie for _ in range(5)],
    items=[item_factories.health_potion],
)
