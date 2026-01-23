"""
CLI Error Handling Utilities

Provides consistent, helpful error messages with actionable suggestions
across all CLI commands.
"""

from typing import Dict, List, Optional

from rich.console import Console

console = Console()


class CLIError(Exception):
    """Base exception for CLI errors with helpful context"""

    def __init__(
        self,
        message: str,
        suggestion: Optional[str] = None,
        context: Optional[Dict[str, str]] = None,
    ):
        self.message = message
        self.suggestion = suggestion
        self.context = context or {}
        super().__init__(message)

    def display(self) -> None:
        """Display error with suggestions"""
        console.print(f"[red]Error:[/red] {self.message}")
        if self.suggestion:
            console.print(f"[yellow]💡 Suggestion:[/yellow] {self.suggestion}")
        if self.context:
            console.print("[dim]Context:[/dim]")
            for key, value in self.context.items():
                console.print(f"  {key}: {value}")


class APIKeyError(CLIError):
    """Missing or invalid API key"""

    def __init__(self, provider: str, message: str = ""):
        full_message = f"No API key found for {provider}"
        if message:
            full_message += f": {message}"

        suggestion = (
            f"Set your {provider.upper()} API key:\n"
            f"  • council config set {provider}_key YOUR_KEY\n"
            f"  • Or set environment variable: export {provider.upper()}_API_KEY=YOUR_KEY"
        )

        super().__init__(full_message, suggestion)


class ProviderError(CLIError):
    """Provider connectivity or configuration error"""

    def __init__(self, provider: str, error: str = ""):
        full_message = f"Provider '{provider}' error"
        if error:
            full_message += f": {error}"

        suggestion = (
            f"Check {provider} configuration:\n"
            f"  • Run: council doctor\n"
            f"  • Verify API key: council config get {provider}_key\n"
            f"  • Check internet connection"
        )

        super().__init__(full_message, suggestion)


class ValidationError(CLIError):
    """Input validation error"""

    def __init__(self, field: str, issue: str, hint: str = ""):
        message = f"Invalid {field}: {issue}"
        suggestion = hint or f"Verify your {field} and try again"
        super().__init__(message, suggestion)


class StreamingError(CLIError):
    """Streaming operation failed"""

    def __init__(self, message: str = ""):
        full_message = "Streaming consultation failed"
        if message:
            full_message += f": {message}"

        suggestion = (
            "Attempting fallback to non-streaming mode...\n"
            "If this persists, try:\n"
            "  • Check internet connection\n"
            "  • Run: council doctor\n"
            "  • Try: council consult 'query' --mode synthesis"
        )

        super().__init__(full_message, suggestion)


class StorageError(CLIError):
    """History or cache storage error"""

    def __init__(self, operation: str, message: str = ""):
        full_message = f"Storage error during {operation}"
        if message:
            full_message += f": {message}"

        suggestion = (
            "Try one of:\n"
            "  • Check disk space: df -h\n"
            "  • Check permissions: ls -la ~/.council\n"
            "  • Clear cache: council history clear (WARNING: deletes history)"
        )

        super().__init__(full_message, suggestion)


def suggest_command_fixes(command: str, error_type: str) -> str:
    """
    Suggest similar commands or common fixes based on error type
    """
    suggestions: Dict[str, Dict[str, List[str]]] = {
        "typo": {
            "consult": ["Did you mean: council consult"],
            "consulte": ["Did you mean: council consult"],
            "consult ": ["Did you mean: council consult"],
            "interactive": ["Did you mean: council interactive"],
            "interactiv": ["Did you mean: council interactive"],
            "history": ["Did you mean: council history"],
            "histroy": ["Did you mean: council history"],
            "doctor": ["Did you mean: council doctor"],
            "dcotor": ["Did you mean: council doctor"],
            "tui": ["Did you mean: council tui"],
            "web": ["Did you mean: council web"],
        },
        "missing_args": {
            "consult": [
                "Usage: council consult 'YOUR_QUERY'",
                "Example: council consult 'What is AI?'",
            ],
            "review": [
                "Usage: council review <repository_path>",
                "Example: council review ./my-repo",
            ],
        },
    }

    if error_type in suggestions and command in suggestions[error_type]:
        return "\n".join(suggestions[error_type][command])

    return ""


def format_provider_status(status: Dict[str, bool]) -> str:
    """Format provider availability status"""
    lines = ["[dim]Provider Status:[/dim]"]
    for provider, available in status.items():
        icon = "✓" if available else "✗"
        status_text = "[green]available[/green]" if available else "[red]unavailable[/red]"
        lines.append(f"  {icon} {provider.capitalize()}: {status_text}")
    return "\n".join(lines)


def handle_network_error(error: str) -> None:
    """Handle network-related errors with helpful info"""
    console.print(
        "[red]Network Error:[/red] Could not reach API endpoint",
        error,
        sep="\n",
    )
    console.print(
        "[yellow]💡 Suggestions:[/yellow]",
        "  • Check internet connection",
        "  • Verify API endpoint configuration",
        "  • Try: council doctor",
        sep="\n",
    )


def handle_timeout_error(operation: str, timeout_seconds: int) -> None:
    """Handle timeout errors with recovery suggestions"""
    console.print(
        f"[yellow]⏱️  Timeout:[/yellow] {operation} took longer than {timeout_seconds}s",
    )
    console.print(
        "[yellow]💡 Try:[/yellow]",
        "  • Simplify your query",
        "  • Try a different provider: council config set provider openai",
        "  • Reduce the number of council members",
        sep="\n",
    )


def display_success_summary(operation: str, details: Optional[Dict[str, str]] = None) -> None:
    """Display successful operation summary"""
    console.print(f"[green]✓[/green] {operation} completed successfully")
    if details:
        for key, value in details.items():
            console.print(f"  {key}: {value}")
