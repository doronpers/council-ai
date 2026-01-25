"""Init command for Council AI."""

import click
from rich.panel import Panel
from rich.prompt import Confirm, Prompt

from ...providers import list_providers
from ..utils import DEFAULT_PROVIDER, console


@click.command()
@click.pass_context
def init(ctx):
    """
    Initialize Council AI with a setup wizard.

    Guides you through first-time setup including API keys and preferences.
    Automatically detects all available API keys and suggests the best provider.
    """
    from ... import list_domains
    from ...core.config import (
        get_api_key,
        get_available_providers,
        get_best_available_provider,
        is_placeholder_key,
    )
    from ...core.diagnostics import diagnose_api_keys
    from ...core.personal_integration import (
        detect_personal_repo,
        integrate_personal,
        is_personal_configured,
    )

    config_manager = ctx.obj["config_manager"]

    console.print(
        Panel(
            "[bold]🏛️ Welcome to Council AI![/bold]\n\n"
            "This wizard will help you set up Council AI.\n"
            "You can change these settings later with 'council config'.",
            title="Setup Wizard",
            border_style="blue",
        )
    )

    # Step 0: Detect all available API keys
    console.print("\n[bold]Step 0: Detecting available API keys...[/bold]")
    diagnose_api_keys()  # Run diagnostics (results used by get_available_providers)
    available_providers = get_available_providers()

    # Show what we found
    found_keys = []
    for provider_name, api_key in available_providers:
        if api_key:
            found_keys.append(provider_name)
            console.print(f"[green]✓[/green] Found {provider_name.upper()} API key")

    if not found_keys:
        console.print("[yellow]⚠[/yellow] No API keys detected in environment variables")
        console.print("[dim]We'll help you configure one in the next step[/dim]")
    else:
        console.print(
            f"\n[bold]Found {len(found_keys)} available provider(s):[/bold] {', '.join(found_keys)}"
        )
        best = get_best_available_provider()
        if best:
            console.print(f"[cyan]💡 Recommended:[/cyan] {best[0]} (best supported provider)")

    # Step 1: Choose provider
    console.print("\n[bold]Step 1: Choose your LLM provider[/bold]")
    all_providers = list_providers()
    console.print(f"Supported providers: {', '.join(all_providers)}")

    # Build choices with availability indicators
    default_provider = config_manager.get("api.provider", DEFAULT_PROVIDER)
    provider_availability = {}

    from ...core.config import is_lmstudio_available

    lmstudio_active = is_lmstudio_available()

    for provider_name in all_providers:
        if provider_name == "lmstudio":
            has_key = lmstudio_active
        else:
            has_key = any(p == provider_name and k for p, k in available_providers)

        provider_availability[provider_name] = has_key
        if has_key:
            # Use first available as default if no config
            if not config_manager.get("api.provider") and default_provider == DEFAULT_PROVIDER:
                default_provider = provider_name

    # Prefer lmstudio as default if active, otherwise use best available
    if lmstudio_active:
        default_provider = "lmstudio"
    else:
        best = get_best_available_provider()
        if best and best[0] in all_providers:
            default_provider = best[0]

    console.print("\nAvailable options:")
    for provider_name in all_providers:
        has_key = provider_availability[provider_name]
        if provider_name == "lmstudio":
            status = "[green](Running locally)[/green]" if has_key else "[dim](Not running)[/dim]"
            note = " [bold cyan](Free, Default)[/bold cyan]" if has_key else " (Free, Local)"
            console.print(f"  • {provider_name}{note} {status}")
        elif has_key:
            console.print(f"  • {provider_name} [green](API key available)[/green]")
        else:
            console.print(f"  • {provider_name} [dim](no API key)[/dim]")

    provider = Prompt.ask(
        "\nWhich provider would you like to use?",
        choices=all_providers,
        default=default_provider,
    )
    config_manager.set("api.provider", provider)

    # Step 2: API Key
    if provider == "lmstudio":
        console.print("\n[bold]Step 2: Local Setup[/bold]")
        if lmstudio_active:
            console.print("[green]✓[/green] LM Studio is running and ready!")
        else:
            console.print("[yellow]⚠[/yellow] LM Studio is not detected at http://localhost:1234")
            console.print(
                "[dim]You can still proceed, but calls will fail until you start LM Studio.[/dim]"
            )
            console.print("[dim]Download it from: https://lmstudio.ai/[/dim]")

        # Still allow setting a key if they want (though not needed for LM Studio)
        if Confirm.ask(
            "Do you want to configure an API key for fallback providers?", default=False
        ):
            pass  # Continue to key config below
        else:
            existing_key = None  # Skip to domain config
            # We don't need a key for LM Studio but we might need for fallbacks
    else:
        console.print("\n[bold]Step 2: Configure API key[/bold]")
        existing_key = get_api_key(provider)

        # Also check for vercel/generic if using openai
        if provider == "openai":
            vercel_key = get_api_key("vercel")
            if vercel_key:
                existing_key = vercel_key
                console.print("[cyan]ℹ[/cyan] Using AI_GATEWAY_API_KEY (Vercel AI Gateway)")

        if existing_key and not is_placeholder_key(existing_key):
            console.print(f"[green]✓[/green] Found existing {provider.upper()} API key")
            if not Confirm.ask("Do you want to update it?", default=False):
                existing_key = None  # Skip update
        else:
            existing_key = None

        if not existing_key:
            console.print("\n[dim]You can get an API key from:[/dim]")
            if provider == "anthropic":
                console.print("  https://console.anthropic.com/")
            elif provider == "openai":
                console.print("  https://platform.openai.com/api-keys")
            elif provider == "gemini":
                console.print("  https://ai.google.dev/")

            console.print(
                f"\n[yellow]Note:[/yellow] You can also set {provider.upper()}_API_KEY in your env"
            )
            if provider == "openai":
                console.print(
                    "[dim]Or use AI_GATEWAY_API_KEY for Vercel AI Gateway (OpenAI-compatible)[/dim]"
                )

            if Confirm.ask("Do you have an API key to configure now?", default=True):
                api_key = Prompt.ask(f"{provider.capitalize()} API key", password=True)
                if api_key:
                    config_manager.set("api.api_key", api_key)
                    console.print("[green]✓[/green] API key saved to config")
        else:
            # Show fallback information
            if found_keys:
                console.print(
                    f"\n[cyan]ℹ[/cyan] You have {len(found_keys)} other provider(s) available: "
                    f"{', '.join(found_keys)}"
                )
                console.print(
                    "[dim]Council AI will automatically use these if the primary provider fails[/dim]"
                )

    # Step 3: Default domain
    console.print("\n[bold]Step 3: Choose default domain[/bold]")
    domains = list_domains()
    console.print("\nAvailable domains:")
    for d in domains[:5]:  # Show first 5
        console.print(f"  • {d.id}: {d.name}")
    console.print(f"  ... and {len(domains) - 5} more")

    default_domain = Prompt.ask(
        "Default domain",
        default=config_manager.get("default_domain", "general"),
    )
    config_manager.set("default_domain", default_domain)

    # Step 4: Personal Integration (optional)
    console.print("\n[bold]Step 4: Personal Integration (Optional)[/bold]")
    try:
        repo_path = detect_personal_repo()
        if repo_path:
            console.print(f"[green]✓[/green] Found council-ai-personal at: {repo_path}")
            if not is_personal_configured():
                if Confirm.ask("Would you like to integrate it now?", default=True):
                    console.print("Integrating...")
                    if integrate_personal(repo_path):
                        console.print("[green]✓[/green] Personal integration completed!")
                    else:
                        console.print("[yellow]⚠[/yellow] Integration failed, but continuing...")
                else:
                    console.print(
                        "[dim]You can integrate later with: council personal integrate[/dim]"
                    )
            else:
                console.print("[green]✓[/green] Personal integration already configured")
        else:
            console.print(
                "[dim]No council-ai-personal repository detected. "
                "You can set it up later if needed.[/dim]"
            )
    except Exception as e:
        console.print(f"[dim]Could not check personal integration: {e}[/dim]")

    # Step 5: Save
    config_manager.save()

    # Build summary with fallback info
    summary_lines = [
        "[green]✓ Setup complete![/green]\n",
        f"Provider: {provider}",
        f"Default domain: {default_domain}",
        f"Config saved to: {config_manager.path}",
    ]

    # Add fallback information
    if len(found_keys) > 1 or (len(found_keys) == 1 and provider not in found_keys):
        fallback_providers = [p for p in found_keys if p != provider]
        if fallback_providers:
            summary_lines.append(
                f"\n[cyan]Fallback providers:[/cyan] {', '.join(fallback_providers)}"
            )
            summary_lines.append(
                "[dim]Council AI will automatically use these if the primary provider fails[/dim]"
            )

    summary_lines.extend(
        [
            "\n[bold]Next steps:[/bold]",
            "  • Run 'council consult \"your question\"' to get started",
            "  • Run 'council interactive' for a session",
            "  • Run 'council --help' to see all commands",
            "  • Run 'council providers --diagnose' to check API key status",
        ]
    )

    console.print(
        Panel(
            "\n".join(summary_lines),
            title="Setup Complete",
            border_style="green",
        )
    )
