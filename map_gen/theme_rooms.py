from map_gen.encounter import Encounter


class ThemeRoom:
    def __init__(
        self,
        name: str,
        encounter: Encounter,
        enclosed: bool,
    ):
        self.name = name
        self.encounter = encounter
        self.enclosed = enclosed
