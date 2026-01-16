# Integration Plan (Workspace Cross-Pollination)

**Note**: This document contains integration planning details. For active TODOs and roadmap items, see [ROADMAP.md](../ROADMAP.md).

Purpose: unify stable capabilities across the workspace with minimal duplication and clear validation.

## Repositories in scope (local workspace)
- `council-ai` (current repo)
- `shared-ai-utils` (shared package)
- `feedback-loop`
- `sono-eval`
- `memu`
- `sono-platform` / `sonotheia-examples`
- `drrweb`
- `planning-with-files`, `tex-assist-coding`, `spatial-selecta`, `doronpers-dev-toolkit` (supporting docs/utilities)

## Anchor package
- **shared-ai-utils** already consolidates LLM providers, config, assessment, FastAPI utils, patterns, and CLI helpers. Treat it as the primary reuse surface.

## Integration streams (phased)
### Phase 1 — shared-ai-utils adoption (low risk, highest leverage)
- **council-ai**: replace local provider/config glue with `shared_ai_utils.llm.LLMManager` and `shared_ai_utils.config.ConfigManager`; adopt shared CLI helpers for terminal UX; keep existing CLI flags/envs but route through shared types.
- **feedback-loop**: migrate to `LLMManager` for generation/fallback; move pattern CRUD/versioning to `shared_ai_utils.patterns.PatternManager`; use shared config base for settings.
- **sono-eval**: already integrated; export any sono-eval-specific presets back into shared-ai-utils if missing (improves reuse for other repos).

### Phase 2 — cross-repo feature hooks
- **council-ai ↔ feedback-loop**: add pattern-aware council mode (pattern recommendations from feedback-loop library or API); allow feedback-loop to call council personas for pattern review.
- **council-ai ↔ sono-eval**: optional QA command to run council outputs through sono-eval assessment engine for clarity/risk scoring; add “assessment” domain preset that points to sono-eval API.
- **council-ai ↔ memu**: add MemU-backed conversation/history persistence (profile-driven) as an optional memory backend.
- **feedback-loop ↔ memu**: store pattern usage/metrics in MemU for semantic search and long-term retrieval (leveraging existing memu integration).

### Phase 3 — product demos and domain presets
- **drrweb**: add council consult server action (using shared-ai-utils LLM manager) for creative intent detection/copy; optionally surface MemU memories for whispers.
- **sonotheia-examples / sono-platform**: import regulated-risk presets into council-ai (SAR/risk scoring personas) and reuse shared FastAPI middleware now in shared-ai-utils for any local services.
- **tex-assist-coding**: reference shared pattern library and workflows (documentation-only integration).

## Concrete next actions (ready-to-implement)
1) Council-ai
   - Swap provider glue to `shared_ai_utils.llm.LLMManager` and remove duplicate wrappers.
   - Replace config loading with `shared_ai_utils.config.ConfigManager` + presets; keep current YAML/env compatibility.
   - Use shared CLI helpers for richer terminal output.
2) Feedback-loop
   - Migrate to `LLMManager` and shared config base.
   - Replace internal pattern manager with `shared_ai_utils.patterns.PatternManager`.
3) Hooks
   - Add council “pattern-coach” mode hitting feedback-loop (library or REST) for recommendations.
   - Add council QA command that calls sono-eval assessment engine.
   - Add optional MemU backend in council for history storage.

## Validation plan
- Unit tests around provider/config swaps (mocked LLM calls) in council-ai and feedback-loop.
- CLI smoke tests: `council quickstart`, `feedback-loop analyze`, pattern CRUD via shared manager.
- If adding MemU: integration test with in-memory backend; feature-flag default off.
- For sono-eval QA hook: contract test against local sono-eval server stub.

## Risks and mitigations
- **API drift**: shared-ai-utils updates could break adopters; pin versions and add adaptor shims.
- **Behavior changes**: fallback ordering may differ; document defaults and allow overrides.
- **Config migration**: ensure backward compatibility (.env/YAML) with deprecation notices.
- **Latency**: added MemU or remote calls—feature flag and add timeouts.
