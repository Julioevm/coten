from map_gen import encounter_factories
from map_gen.theme_rooms import ThemeRoom


shrine = ThemeRoom("Shrine", encounter=encounter_factories.shrine, enclosed=True)
