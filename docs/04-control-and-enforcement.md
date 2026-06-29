# 04 — Control & Enforcement

This is the most important document for honest expectation-setting. The original design's headline value was **enforced** control flow. This redesign trades some of that for simplicity and portability. This document states exactly what is lost, what is preserved, and the precise path to recover the rest.

## 4.1 The core distinction: enforced vs. instructed

| | Original (LangGraph) | This redesign |
|---|---|---|
| Phase ordering | **Enforced** — skipping is structurally impossible (the graph picks the next node) | **Instructed** — `AGENTS.md` tells the orchestrator the order; the model follows it |
| Loop-backs | **Enforced** — conditional edges on parsed verdicts | **Instructed** — orchestrator re-invokes a phase subagent per the rules |
| Cycle limits | **Enforced** — per-phase counters in edge functions | **Advisory** — orchestrator tracks counts; human is the backstop |
| Quality gate | Deterministic threshold compare on (LLM-produced) scores | Same — kept deterministic via a skill |
| Human gates | `interrupt_before` hard pause | Conversational pause (model asks and waits) |

The honest summary: **we convert hard structural guarantees into soft, instruction-driven ones.** Two facts make this acceptable as a *starting* posture, and one mechanism makes it recoverable.

## 4.2 Why soft enforcement is acceptable to start

1. **The human is a continuous gate.** This is an interactive, single-user, conversation-first tool. A senior architect watching each phase will notice a skipped or out-of-order step immediately — the very autonomy the LangGraph machinery existed to constrain is largely absent in interactive use. Much of the original's rigor compensated for autonomy this usage pattern doesn't have.
2. **The original's enforcement was already partial.** In the original code, only the `intake`, `self_critique`, and `review` cycle limits are actually checked; the `analysis`, `design`, and `build` limits are declared in config but never enforced by any edge. So the bar this redesign must clear is "match *real* enforced behavior," which is narrower than the architecture diagram implies.

## 4.3 What is preserved without any hooks

- **Output precision** — fully (model + phase instructions + memory all transfer; subagents *improve* it via context isolation).
- **The quality gate's determinism** — the 6-dimension score → average → threshold comparison is a skill (`score-requirements`), so the *gate math* stays deterministic exactly as in the original (where only the math, not the scoring, was ever deterministic).
- **Human gates** — arguably stronger, since conversation is inherently turn-based and the gates read as natural questions rather than CLI verbs.
- **Capability boundaries** — subagent tool allowlists prevent whole classes of error (analysis can't write code; build can't rewrite requirements). This is a *form* of control the original did not have.

## 4.4 The recovery mechanism: hooks as the deterministic seam (deferred)

In Claude Code, **hooks** (`PreToolUse`, `PostToolUse`, `Stop`) are the one model-external, deterministic control surface — and they map almost one-to-one onto the LangGraph edges we removed. The plan is to **not build them yet**, but to design so that each lost guarantee corresponds to exactly one future hook:

| Lost guarantee | Recovering hook (deferred) |
|---|---|
| Don't build before the spec is approved | `PreToolUse` on the builder subagent: block unless `workspace/<task>/.approved` exists |
| Don't write `spec.md` before `design.md` exists | `PreToolUse` on write: block if prerequisite artifact missing |
| Cap loop-backs at N | `PreToolUse`/orchestrator: read `state.json` iteration count, block re-entry past limit |
| Don't write memory before approval | `PreToolUse` on writes to `memory/**`: block unless `learn` gate approved |
| Every completed phase wrote its artifact | `Stop` hook: verify expected artifact exists; warn/block otherwise |

This is the key reframing of the whole redesign: **the control plane moves from LangGraph edges to hooks — but only the invariants we actually refuse to lose, and only when we choose to pay for them.** Hooks are small, declarative glue (not application code), so adding them keeps the solution "low-code," not "coded."

## 4.5 The irreducible truth

> **"No-code" and "full process control" are mutually exclusive.** Deterministic guarantees require a deterministic substrate. In this ecosystem that substrate is hooks (+ a tiny `state.json`). The achievable target is **low-code with deliberately-placed deterministic seams**, not zero-code with full control.

We are choosing to start at the low-code / soft-enforcement end of that spectrum and walk toward hard enforcement **only for the specific invariants that prove to matter in practice**. The list in §4.4 is short on purpose: name the 4–5 invariants you refuse to lose, and each is one hook. That short list — not a framework — becomes the control plane.

## 4.6 Decision

- **Phase 1 (this design):** soft enforcement via `AGENTS.md` + subagents + the `score-requirements` skill + an optional orchestrator-maintained `state.json`. No hooks.
- **Phase 2 (when justified by observed misbehavior):** add hooks from the §4.4 table, one invariant at a time, measuring whether each is needed.
- **Trigger to add a hook:** a real failure mode observed in use (e.g., the agent builds before approval, or loops design > N times). We add enforcement reactively and surgically, not speculatively.
