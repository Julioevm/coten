from __future__ import annotations
import tcod.event


ROOT_CONSOLE: tcod.console.Console | None = None
CONTEXT: tcod.context.Context | None = None


def set_root_console(value: tcod.console.Console):
    global ROOT_CONSOLE
    ROOT_CONSOLE = value


def get_root_console():
    return ROOT_CONSOLE


def set_context(value: tcod.context.Context):
    global CONTEXT
    CONTEXT = value


def get_context() -> tcod.context.Context:
    return CONTEXT
