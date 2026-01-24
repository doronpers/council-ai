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

1. **Propose**: Open an issue describing the pages to consolidate, the proposed canonical location, and the reason for the change. This allows for discussion before implementation.
2. **Implement**: Once the proposal is approved, open a small PR that performs the consolidation.
   - Update links, run `pre-commit`, and add a changelog entry if the change is significant.
   - For larger efforts, you may be asked to update `documentation/CONSOLIDATION_PLAN.md` to track the items.

## Contact & review

For questions about structure or scope, mention `@doronpers` (or the repo maintainers) in the PR description and request a docs review.

---

Happy documenting! ✨
