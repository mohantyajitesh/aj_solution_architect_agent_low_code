# 08 — Open Questions & Roadmap

This design is a **draft for collaborative review**. This document lists what is deliberately unresolved and the proposed build sequence — so review can focus on the right things.

## 8.1 Open questions (for our review together)

### Orchestration & control
1. **Orchestrator dispatch reliability.** Will `AGENTS.md` reliably drive the full subagent sequence in order, or do we need a `/sdd` command body that explicitly enumerates the steps? (Affects how soft "soft enforcement" really is.)
2. **First hook to add, if any.** The §4.4 table lists candidates. Which single invariant, if violated, would hurt most — and should it be enforced from day one rather than deferred? (Strongest candidate: *no build before spec approval*.)
3. **`state.json` — include now or wait?** A tiny per-task state file enables hard cycle-limits later. Do we add it in Phase 1 for observability, or keep Phase 1 purely file-derived?

### Subagents
4. **Granularity.** Is one subagent per phase right, or should `analysis`+`design` (or `build`+`review`) be fused to cut dispatch overhead? Trade: fewer dispatches vs. less context isolation.
5. **Model per subagent.** Do reasoning-heavy phases (`design`, `critique`) warrant a different model/effort than mechanical ones (`intake` scoring)? Frontmatter allows it.
6. **Builder boundary.** Should `build` be a subagent, or should it remain the user explicitly invoking Claude Code agentic mode in `workspace/<task>/src/`? (Safety vs. automation.)

### Memory
7. **Tag vocabulary.** Controlled vocabulary up front, or let the curator infer and normalize tags emergently?
8. **Curator cadence.** After every `learn`, or batched/periodic to save tokens?
9. **Retrieval interface stability.** Lock the `memory-retrieve` contract now so a future memory MCP is a drop-in — agree on its inputs/outputs.

### Distribution & portability
10. **Plugin vs. plain repo for v1.** Ship as a packaged plugin immediately, or as a clone-and-go repo until the agent set stabilizes?
11. **Cowork validation.** Worth a spike to confirm Cowork's subagent/hook support before committing to it as a channel?

### Scope
12. **Quality threshold.** Keep the original's `70/100`, or recalibrate now that scoring feeds a conversational gate rather than a hard edge?
13. ~~**Phase set.** Keep all 8 phases, or is `self_critique` foldable into `design`?~~ **Resolved (ADR-10):** the pipeline is now *adaptive* — a `triage` step selects the phase set per request complexity (trivial skips analysis/design/critique; standard runs full; complex decomposes into Units of Work). `self_critique` stays a distinct phase but only runs on standard/complex requests.

## 8.2 Proposed build sequence (once the design is agreed)

> No code is written until the design is signed off. This is the *intended* order, not a commitment.

**Phase 0 — Skeleton (markdown only)** ✅ *strawman drafted*
- `AGENTS.md` (persona + **adaptive pipeline w/ triage** + **Verification gates** + gate rules + memory protocol)
- `/sdd` command
- `workspace/` + seeded `memory/` (`INDEX.md`, asset catalog, standard)
- *Exit test:* `/sdd` triages a request, narrates the right-sized phase plan, and cites the Verification checks it will run.

**Phase 1 — Phase subagents** 🚧 *in progress*
- ✅ `intake` ([`.claude/agents/intake.md`](../.claude/agents/intake.md)) — quality gate + clarification + **hard-gap override** + carried-gaps handoff
- ✅ `design` ([`.claude/agents/design.md`](../.claude/agents/design.md)) — reuse-first + standards + tradeoffs + carried-gap resolution (DSN-05); analysis optional
- ✅ `analysis` ([`.claude/agents/analysis.md`](../.claude/agents/analysis.md)) — problem-space framing; ANL-01..04; stays out of solution space
- ✅ `self_critique` ([`.claude/agents/self_critique.md`](../.claude/agents/self_critique.md)) — multi-angle, routing verdict, honest-not-default-PASS; CRIT-01..04
- ✅ `spec` ([`.claude/agents/spec.md`](../.claude/agents/spec.md)) — implementation contract, design-traceable (SPEC-04); SPEC-01..04
- ✅ `score-requirements` skill ([`skills/score-requirements/`](../skills/score-requirements/SKILL.md)) — deterministic confidence + hard-gap gate (tested)
- ⬜ `build` → `review` → `learn` + `memory-curator`
- ⬜ `memory-retrieve` skill
- **Reasoning chain complete:** `intake → analysis → design → self_critique → spec` is now drafted — the first end-to-end `/sdd` run to the spec-approval gate is testable (success criteria S1–S3).
- *Validated on paper:* a dry-run (Oracle HCM → BenefitsCo) surfaced F1–F4; all applied. The reuse analysis correctly rejected a greenfield poller in favor of extending HCM System Service.
- *Exit test:* a simple requirement flows end-to-end and writes all artifacts (success criteria S1–S3).

**Phase 2 — Gates & builder**
- Conversational spec-approval and memory-approval gates wired into `AGENTS.md`
- `build` (subagent or explicit invocation per Q6)
- *Exit test:* agent pauses at gates; build only after approval (S4).

**Phase 3 — Hardening (reactive)**
- Add hooks from §4.4 **only for invariants that misbehaved** in Phase 2 testing
- Optional `state.json` + hard cycle-limits if loops were observed
- *Exit test:* the chosen invariants are now deterministically enforced.

**Phase 4 — Distribution**
- Package as a Claude Code plugin; write install/onboarding docs
- *Exit test:* a second developer installs and runs a task in < 15 min, no infra (S6).

**Phase 5 — Measure**
- Run a representative set of requirements; measure the ≥80% success target (S5); feed failures back into `AGENTS.md` / subagent prompts / hooks.

## 8.3 Explicitly deferred (not in any near-term phase)
- Vector/semantic retrieval (memory MCP) — only if the corpus outgrows vectorless.
- Remote/hosted MCP and Codespaces execution — only when shared/cloud runtime is needed.
- Cowork packaging — only when a non-terminal audience is real.
- Provider abstraction / multi-LLM — only if a second model becomes a hard requirement.

## 8.4 How to review this design
Suggested order: [`README`](../README.md) → [`01`](01-overview-and-goals.md) → [`02`](02-architecture.md) → [`04`](04-control-and-enforcement.md) (the honest part) → [`06`](06-technology-justifications.md) (the scorecard) → this file. Push back hardest on **§8.1 Q1–Q3** (how soft is soft enforcement) and **ADR-05** — that's where the design's main risk concentrates.
