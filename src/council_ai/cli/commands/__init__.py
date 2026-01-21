"""CLI Commands Package."""

from .init import init as init_command
from .misc import quickstart as quickstart_command
from .consult import consult as consult_command, q as q_command
from .interactive import interactive as interactive_command
from .tui import tui as tui_command
from .history import history_group
from .review import review as review_command
from .web import web as web_command, ui as ui_command
from .doctor import (
    doctor as doctor_command,
    cost_group,
    show_providers as show_providers_command,
    test_key as test_key_command,
)

__all__ = [
    "init_command",
    "quickstart_command",
    "consult_command",
    "q_command",
    "interactive_command",
    "tui_command",
    "history_group",
    "review_command",
    "web_command",
    "ui_command",
    "cost_group",
    "doctor_command",
    "show_providers_command",
    "test_key_command",
]
