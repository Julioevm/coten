from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from engine import Engine
    from entity import Actor

def whirlwind_attack(engine: "Engine", actor: "Actor") -> None:
    """Perform a whirlwind attack, hitting all adjacent enemies."""
    for dx in [-1, 0, 1]:
        for dy in [-1, 0, 1]:
            if dx == 0 and dy == 0:
                continue
            target = engine.game_map.get_actor_at_location(actor.x + dx, actor.y + dy)
            if target and target != engine.player:
                damage = actor.fighter.melee_damage
                engine.message_log.add_message(
                    f"You hit {target.name} with your whirlwind attack for {damage} damage!"
                )
                target.fighter.hp -= damage
