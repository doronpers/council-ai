# GitHub Issue to Create

## Title
Re-enable strict mypy checks after ConsultationResult migration completes

## Labels
- `enhancement`
- `technical-debt`
- `type-checking`

## Body

## Background

During the strategy return type migration (PR #56, #78), we temporarily relaxed mypy checks in `.pre-commit-config.yaml`:
- `--no-strict-optional`: Allows None-related flexibility
- `--disable-error-code=no-any-return`: Permits implicit Any returns

## Completion Criteria

Re-enable strict mypy checks once ALL strategies return `ConsultationResult`:
- [x] IndividualStrategy ✅ (done in PR #56)
- [x] SequentialStrategy ✅ (done in PR #56)
- [x] SynthesisStrategy ✅ (done in PR #56)
- [x] DebateStrategy ✅ (verified - returns ConsultationResult)
- [x] VoteStrategy ✅ (verified - returns ConsultationResult)
- [ ] All backward compatibility code removed from `council.py` (lines 750-753)

## Actions Required

1. Remove mypy relaxed flags from `.pre-commit-config.yaml`:
   - Remove `--no-strict-optional`
   - Remove `--disable-error-code=no-any-return`
2. Fix any new type errors that appear
3. Update strategy type hints to remove legacy `Union` types if present
4. Remove backward compatibility code from `council.py` (lines 750-753)

## References

- Original review: PR #56 review comment by @gemini-code-assist[bot]
- Related PRs: #56, #78
- Tracking issue: #77
- Migration status: See `.agent/migration-status.md`

---

**Note:** Once this issue is created, update `.pre-commit-config.yaml` line 73 with the issue number.
