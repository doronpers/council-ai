# Personas and Domains

This guide describes the built-in personas and domain presets shipped with Council AI.

## Built-in personas

Personas live in `src/council_ai/personas/*.yaml`.

### Advisory council (build it right)

- `rams` (🎨) — simplification, design clarity
- `dempsey` (🎖️) — mission clarity, autonomy, execution
- `kahneman` (🧠) — cognitive load, bias-aware decision making
- `treasure` (🔊) — communication, listening, clarity of expression

### Red team (break & survive)

- `holman` (🔓) — security and attack mindset
- `taleb` (🦢) — tail risk, antifragility, hidden failure modes
- `grove` (🎯) — strategy, competition, leverage points
- `fraud_examiner` (🔍) — fraud tactics, evidence chain reasoning

### Specialists (security & compliance)

- `signal_analyst` (🔬) — audio forensics, deepfake detection
- `compliance_auditor` (⚖️) — compliance / regulated-industry lens

### Specialists (audio & post-production)

- `adr_supervisor` (🎭) — ADR performance matching and sync
- `dialogue_editor` (🎙️) — dialogue clarity, continuity, and noise management
- `rerecording_mixer` (🎚️) — mix translation, dynamics, delivery standards
- `sound_designer` (🎬) — narrative impact, creative sound design

## Domain presets

Domains are defined in `src/council_ai/domains/__init__.py`.

List domains via CLI:

```bash
council domain list
```

Built-in domains:

- `coding`
- `business`
- `startup`
- `product`
- `leadership`
- `creative`
- `writing`
- `audio_post`
- `career`
- `decisions`
- `devops`
- `data`
- `general`
- `llm_review`
- `sonotheia`
