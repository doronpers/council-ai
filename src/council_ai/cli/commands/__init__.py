"""CLI Commands Package."""

from .consult import consult as consult_command
from .consult import q as q_command
from .doctor import (
    cost_group,
)
from .doctor import (
    doctor as doctor_command,
)
from .doctor import (
    show_providers as show_providers_command,
)
from .doctor import (
    test_key as test_key_command,
)
from .history import history_group
from .init import init as init_command
from .interactive import interactive as interactive_command
from .misc import quickstart as quickstart_command
from .review import review as review_command
from .tui import tui as tui_command
from .web import ui as ui_command
from .web import web as web_command

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
