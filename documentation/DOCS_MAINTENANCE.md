# Documentation Maintenance

## Purpose

This short guide explains how to contribute, maintain, and propose consolidations for the project's documentation.

## Where to add documentation

- Feature guides and user-facing docs: `documentation/`
- Top-level reference docs or high-level overviews: repository root (e.g. `README.md`) or `documentation/` if appropriate
- Internal planning or design notes: `documentation/` but mark clearly (e.g., “INTERNAL” in the title or header)

## Style & formatting

- Use Markdown with clear H2/H3 headings and short paragraphs.
- Keep examples small and executable (use `examples/` or link to example files when relevant).
- Run `pre-commit` hooks (formatters, linters) locally before opening a PR.
- Update cross-links and references when moving or removing files.

## PR checklist for docs changes

- [ ] Ensure text is clear and concise; prefer short sections and examples.
- [ ] Run `pre-commit` and fix any formatting or lint issues.
- [ ] Verify internal links work and update `documentation/README.md` TOC if adding/removing top-level pages.
- [ ] If the change is substantive (feature docs or migration), add a brief entry to `CHANGELOG.md` under "Unreleased - Docs".
- [ ] Provide a short PR description that explains the purpose and scope of the doc change.

## When to consolidate

Consider consolidation when:

- Two or more pages duplicate the same guidance or examples.
- A guide is short (a few paragraphs) and is better folded into a canonical page.
- Content is out-of-date and can be replaced by a short canonical reference.

## How to propose a consolidation

1. Document your proposal in `documentation/CONSOLIDATION_PLAN.md` with:
   - pages to merge
   - suggested canonical home for the content
   - short migration steps (redirects, link updates)
2. Open an issue describing the proposed consolidation and link the plan.
3. Open a small PR that performs the consolidation, updates links, and runs `pre-commit`.

## Contact & review

For questions about structure or scope, mention `@doronpers` (or the repo maintainers) in the PR description and request a docs review.

---

Happy documenting! ✨
