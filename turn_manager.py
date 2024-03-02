from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from entity import Actor


class Node:
    def __init__(self, actor: Actor):
        self.actor = actor
        self.next: Node | None = None


class TurnManager:
    """Turn Manager is a circular linked list that keeps track of the actors."""

    def __init__(self):
        self.head: Node | None = None
        self.current: Node | None = None

    def add_actor(self, actor: Actor):
        new_node = Node(actor)
        if self.head is None:
            self.head = new_node
            self.head.next = self.head  # Point to itself, creating a circular list
        else:
            # Insert new node before the head and make it the new head
            new_node.next = self.head
            # Find the node before head to complete the circle
            last_node = self.head
            while last_node and last_node.next != self.head:
                last_node = last_node.next
            if last_node:
                last_node.next = new_node
            self.head = new_node

    def get_next_actor(self) -> Actor | None:
        if self.current is None:
            self.current = self.head
        else:
            self.current = self.current.next
        return self.current.actor if self.current else None

    def has_actors(self):
        return self.head is not None

    def remove_actor(self, actor: Actor):
        if self.head is None:
            return

        # If the list contains only one node
        if self.head == self.head.next and self.head.actor == actor:
            self.head = None
            self.current = None
            return

        # If the head needs to be removed
        if self.head.actor == actor:
            # Find the node before head to update its next pointer
            last_node = self.head
            while last_node and last_node.next != self.head:
                last_node = last_node.next
            if last_node:
                last_node.next = self.head.next
            self.head = self.head.next
            # Adjust current if necessary
            if self.current and self.current.actor == actor:
                self.current = self.current.next
            return

        # Search for the node with the actor to be removed
        current_node = self.head
        while current_node and current_node.next != self.head:
            if current_node.next and current_node.next.actor == actor:
                # Remove the node from the list
                if self.current and self.current.actor == actor:
                    self.current = (
                        current_node
                        if current_node.next.next == self.head
                        else current_node.next.next
                    )
                current_node.next = current_node.next.next
                return
            current_node = current_node.next

    def get_actor_count(self) -> int:
        count = 0
        current_node = self.head

        if current_node is None:
            return count

        # Loop through the circular linked list and count the nodes
        while True:
            count += 1
            if current_node.next is None:
                break
            current_node = current_node.next
            if current_node == self.head:
                break

        return count
