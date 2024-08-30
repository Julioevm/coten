from typing import Optional, TYPE_CHECKING
import tcod
import textwrap
from tcod.event_constants import K_KP_ENTER
from equipment_types import EquipmentType
from event_handlers.ask_user_event_handler import AskUserEventHandler
from event_handlers.base_event_handler import ActionOrHandler
import color
from actions import DropItem, EquipAction
from entity import Item

if TYPE_CHECKING:
    from components.equippable import Ammo


class InventoryEventHandler(AskUserEventHandler):
    """This handler lets the user select an item.

    What happens then depends on the subclass.
    """

    TITLE = "<missing title>"

    def __init__(self, engine):
        super().__init__(engine)
        self.selected_index = 0  # Track the currently selected item

    def on_render(self, console: tcod.console.Console) -> None:
        """Render an inventory menu, which displays the items in the inventory, and the letter to select them.
        Will move to a different position based on where the player is located, so the player can always see where
        they are.
        """
        super().on_render(console)
        number_of_items_in_inventory = len(self.engine.player.inventory.items)

        height = console.height - 8
        width = console.width - 6
        x = 3
        y = 3
        
        description_x = (width // 3) + 5

        console.draw_frame(
            x=x,
            y=y,
            width=description_x,
            height=height // 3,
            title=self.TITLE,
            clear=True,
            fg=(255, 255, 255),
            bg=(0, 0, 0),
        )
        
        # Draw smaller frame for item description
        console.draw_frame(
            x=x + description_x,
            y=y,
            width=width //  3 * 2,
            height=height,
            title="Description",
            clear=True,
            fg=(255, 255, 255),
            bg=(0, 0, 0),
        )

        if number_of_items_in_inventory > 0:
            # Group items by type and count occurrences
            item_counts = {}
            for item in self.engine.player.inventory.items:
                item_name = item.name
                if item_name in item_counts:
                    item_counts[item_name]['count'] += 1
                else:
                    item_counts[item_name] = {'count': 1, 'item': item}

            for i, (item_name, item_info) in enumerate(item_counts.items()):
                item = item_info['item']
                item_key = chr(ord("a") + i)
                is_equipped = self.engine.player.equipment.item_is_equipped(item)
                is_ammo = item.equippable and item.equippable.equipment_type == EquipmentType.AMMO
                item_string = f"({item_key}) {item_name} (x{item_info['count']})"

                if is_ammo:
                    ammo = item.equippable
                    if isinstance(ammo, Ammo):  # Type check to satisfy mypy
                        ammo_amount = ammo.amount
                        item_string = f"{item_string} ({ammo_amount})"

                if is_equipped:
                    item_string = f"{item_string} (E)"

                # Highlight the selected item
                if i == self.selected_index:
                    console.print(x + 1, y + i + 1, item_string, fg=color.white, bg=color.blue)
                else:
                    console.print(x + 1, y + i + 1, item_string)

                # Display item description on the right side
                if i == self.selected_index and item.description:
                    desc_x = description_x + 5
                    desc_y = y + 1
                    max_desc_width = width // 2 - 2
                    wrapped_description = textwrap.wrap(item.description, width=max_desc_width)
                    for j, line in enumerate(wrapped_description):
                        if desc_y + j < y + height - 1:
                            console.print(desc_x, desc_y + j, line)
        else:
            console.print(x + 1, y + 1, "(Empty)")

    def ev_keydown(self, event: tcod.event.KeyDown) -> Optional[ActionOrHandler]:
        player = self.engine.player
        key = event.sym
        index = key - tcod.event.KeySym.a

        if 0 <= index <= 26:
            try:
                selected_item = player.inventory.items[index]
            except IndexError:
                self.engine.message_log.add_message("Invalid entry.", color.invalid)
                return None
            return self.on_item_selected(selected_item)

        if key == tcod.event.KeySym.UP:
            if self.selected_index > 0:
                self.selected_index -= 1
            return None
        elif key == tcod.event.KeySym.DOWN:
            if self.selected_index < len(player.inventory.items) - 1:
                self.selected_index += 1
            return None
        elif key in (tcod.event.KeySym.RETURN, tcod.event.KeySym,K_KP_ENTER):
            return self.on_item_selected(player.inventory.items[self.selected_index])

        return super().ev_keydown(event)

    def on_item_selected(self, item: Item) -> Optional[ActionOrHandler]:
        if item.consumable:
            return item.consumable.get_action(self.engine.player)
        elif item.equippable:
            return EquipAction(self.engine.player, item)
        else:
            return None


class InventoryActivateHandler(InventoryEventHandler):
    """Handle using an inventory item."""

    TITLE = "Inventory"

    def on_item_selected(self, item: Item) -> Optional[ActionOrHandler]:
        if item.consumable:
            return item.consumable.get_action(self.engine.player)
        elif item.equippable:
            return EquipAction(self.engine.player, item)
        else:
            return None


class InventoryDropHandler(InventoryEventHandler):
    """Handle dropping an inventory item."""

    TITLE = "Select an item to drop"

    def on_item_selected(self, item: Item) -> Optional[ActionOrHandler]:
        """Drop this item."""
        return DropItem(self.engine.player, item)
