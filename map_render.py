import tcod
import time
from engine import Engine
from game_world import GameWorld
from map_gen.generate_cave import generate_cave
from map_gen.generate_dungeon import generate_dungeon
from map_gen.generate_cathedral import generate_dungeon as generate_cathedral

floor_map_generator = [
    lambda **kwargs: generate_cave(
        max_rooms=8, room_min_size=6, room_max_size=10, **kwargs
    ),
    lambda **kwargs: generate_cathedral(**kwargs),
    lambda **kwargs: generate_dungeon(
        max_rooms=16, room_min_size=6, room_max_size=10, **kwargs
    ),
]


def main():
    screen_width = 80
    screen_height = 50

    tileset = tcod.tileset.load_tilesheet(
        "assets/Alloy_curses_12x12.png",
        16,
        16,
        tcod.tileset.CHARMAP_CP437,
    )

    title = "Map Render tool"
    map_width = 80
    map_height = 43

    generator_index = 0

    # We don't need a player to render the map in this case.
    engine = Engine(player=None, debug_mode=False)  # type: ignore

    engine.game_world = GameWorld(
        engine=engine,
        map_width=map_width,
        map_height=map_height,
    )

    with tcod.context.new_terminal(
        screen_width,
        screen_height,
        tileset=tileset,
        title=title,
        vsync=True,
    ) as context:

        try:
            root_console = tcod.console.Console(screen_width, screen_height, order="F")
            first_render = True
            while True:
                render_required = False

                for event in tcod.event.wait():
                    
                    if isinstance(event, tcod.event.Quit):
                        raise SystemExit(0)
                    if isinstance(event, tcod.event.KeyDown):
                        if event.sym == tcod.event.KeySym.UP:
                            generator_index = min(
                                len(floor_map_generator) - 1, generator_index + 1
                            )
                            render_required = True
                        if event.sym == tcod.event.KeySym.DOWN:
                            generator_index = max(0, generator_index - 1)
                            render_required = True
                        if event.sym == tcod.event.KeySym.r:
                            render_required = True
                        if event.sym == tcod.event.KeySym.ESCAPE:
                            raise SystemExit(0)

                        time.sleep(0.2)
                        
                    map_generator = floor_map_generator[generator_index]
                    engine.game_map = map_generator(
                        map_width=map_width, map_height=map_height, engine=engine
                    )
                
                    if render_required or first_render:
                        root_console.clear()
                        engine.game_map.render(console=root_console)
                        context.present(root_console)
                        first_render = False

        except Exception:
            raise


if __name__ == "__main__":
    main()
