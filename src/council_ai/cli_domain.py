"""Backwards-compatible shim for old import path `council_ai.cli_domain`.

Re-exports selected names from `council_ai.cli.domain` and core domains.
"""

from council_ai.cli.domain import domain, domain_list, domain_show

__all__ = ["domain", "domain_show", "domain_list"]
