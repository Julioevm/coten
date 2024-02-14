from map_gen.encounter import Encounter
import actor_factories
import item_factories
import entity_factories

hound_pack = Encounter(
    enemies=[actor_factories.hound for _ in range(3)],
    decorations=[entity_factories.bones for _ in range(3)],
)

zombie_mob = Encounter(
    enemies=[actor_factories.zombie for _ in range(4)],
    items=[item_factories.health_potion],
    decorations=[entity_factories.grave for _ in range(4)],
)

shrine = Encounter(
    enemies=[],
    items=[item_factories.health_potion],
    decorations=[entity_factories.shrine],
)
