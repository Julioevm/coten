from map_gen.encounter import Encounter
import actor_factories

hound_pack = Encounter(enemies=[actor_factories.hound for _ in range(3)], items=[])
