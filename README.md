# Architect Agent — Low-Code Redesign

A low-code, **Claude Code–native** redesign of the Spec-Driven Development (SDD) Architect Agent.

The original ([`aj_solution_architect_agent`](https://github.com/mohantyajitesh/aj_solution_architect_agent)) implements an enforced SDD pipeline as a LangGraph `StateGraph` in ~1,500 lines of Python: cyclic edges, conditional routing, a ChromaDB vector store, a provider-abstraction layer, and a Streamlit UI. It works, but the orchestration machinery is heavy for what is, in practice, a single-user conversational tool.

This repository is the **design** (not yet the build) for re-expressing that same agent using Claude-native primitives — an `AGENTS.md` orchestrator, phase **subagents**, minimal **skills**, **vectorless** file-based memory, and **git** as the storage/sync layer — while consciously preserving as much *output precision* and *process control* as the low-code substrate allows.

> Status: **design draft for review.** No code yet. The intent is to perfect this design collaboratively before any implementation.

---

## What changed, in one table

| Concern | Original (LangGraph) | This redesign (Claude Code–native) |
|---|---|---|
| Orchestration | `StateGraph` cyclic edges (code) | `AGENTS.md` orchestrator + `/sdd` command |
| Phase logic | Graph nodes (Python functions) | **Subagents** (`.claude/agents/*.md`) |
| Reusable procedures | Prompt templates | Minimal **skills** (only where reused) |
| LLM access | Provider ABC + `subprocess` | Native Claude Code (no wrapper) |
| Memory store | ChromaDB vector index | **Vectorless** markdown + `INDEX.md` + grep |
| Memory sync | Git (markdown) + local index | **Git repo** (markdown only) |
| Human gates | LangGraph `interrupt_before` | Native conversational turns |
| Hard enforcement | Conditional edges + cycle counters | **Deferred** — hooks when needed |
| UI | Streamlit | Claude Code (chat/IDE) |
| Distribution | Clone + pip + Docker | Claude Code **plugin** (+ Cowork later) |

---

## Document map

Read in order; each builds on the last.

1. [`docs/01-overview-and-goals.md`](docs/01-overview-and-goals.md) — problem, goals, non-goals, success criteria
2. [`docs/02-architecture.md`](docs/02-architecture.md) — the full architecture, components, control/data flow
3. [`docs/03-memory-vectorless-rag.md`](docs/03-memory-vectorless-rag.md) — file-based memory and vectorless retrieval design
4. [`docs/04-control-and-enforcement.md`](docs/04-control-and-enforcement.md) — soft vs. hard control, the deferred hooks plane
5. [`docs/05-portability-and-distribution.md`](docs/05-portability-and-distribution.md) — across developers and across IDEs
6. [`docs/06-technology-justifications.md`](docs/06-technology-justifications.md) — per-component scorecard (performance / simplicity / portability / reusability / accuracy)
7. [`docs/07-decisions.md`](docs/07-decisions.md) — ADR-style record of the settled decisions
8. [`docs/08-open-questions-and-roadmap.md`](docs/08-open-questions-and-roadmap.md) — what's unresolved, build sequence
9. [`docs/09-aidlc-takeaways.md`](docs/09-aidlc-takeaways.md) — AWS AI-DLC research + takeaways (adaptive pipeline, verification sections, rule projection)

---

## Seeded memory example

The repo includes a small **seeded memory store** ([`memory/`](memory/)) so retrieval can be designed against something concrete — not just described:

- [`memory/assets/hcm-system-service.md`](memory/assets/hcm-system-service.md) — a **capability-catalog** entry for an existing MuleSoft integration (Oracle HCM → SQL Server), with explicit *when-to-use / when-NOT-to-use* fields that drive **reuse-first** design.
- [`memory/standards/mulesoft-flow-naming.md`](memory/standards/mulesoft-flow-naming.md) — a **standards** entry the agent treats as a constraint.
- [`memory/INDEX.md`](memory/INDEX.md) — the index-first retrieval entry point.
- [`memory/README.md`](memory/README.md) — categories and conventions.

This demonstrates manual enrichment with **organizational context** — see [`docs/03` §3.6a](docs/03-memory-vectorless-rag.md).

## Phase 0 strawman (buildable skeleton)

A first runnable skeleton now exists alongside the design:

- [`AGENTS.md`](AGENTS.md) — the orchestrator: persona + **adaptive pipeline (triage)** + **Verification gates** + human gates + the index-first/reuse-first memory protocol. (Adaptive pipeline and Verification adopted from AWS AI-DLC — see [`docs/09`](docs/09-aidlc-takeaways.md), [ADR-10](docs/07-decisions.md).)
- [`.claude/commands/sdd.md`](.claude/commands/sdd.md) — the `/sdd "<requirement>"` entry point that triages, states a right-sized plan, and runs the pipeline against the seeded memory.

**Phase 1 (in progress)** — the full **reasoning chain** is drafted: `intake → analysis → design → self_critique → spec`.
- [`.claude/agents/intake.md`](.claude/agents/intake.md) — structures + quality-scores the requirement, hard-gap override, clarification gate (`REQ-01..04`).
- [`.claude/agents/analysis.md`](.claude/agents/analysis.md) — frames the problem space (scope/constraints/dependencies/risks), stays out of solution space (`ANL-01..04`).
- [`.claude/agents/design.md`](.claude/agents/design.md) — reuse-first analysis, tradeoffs + alternatives, standards compliance, carried-gap resolution (`DSN-01..05`).
- [`.claude/agents/self_critique.md`](.claude/agents/self_critique.md) — multi-angle challenge, routing verdict (PASS/FAIL_*), honest-not-default-PASS (`CRIT-01..04`).
- [`.claude/agents/spec.md`](.claude/agents/spec.md) — the implementation contract, traceable to the design (`SPEC-01..04`).
- [`skills/score-requirements/`](skills/score-requirements/SKILL.md) — deterministic confidence + hard-gap gate (tested).

The execution + learning half is also drafted:
- [`.claude/agents/build.md`](.claude/agents/build.md) — implements the *approved* spec into `src/` (the one phase with code/Bash; `BLD-01..04`).
- [`.claude/agents/review.md`](.claude/agents/review.md) — spec-vs-build verdict CLEAN/SPEC_DRIFT (`REV-01..03`).
- [`.claude/agents/learn.md`](.claude/agents/learn.md) — proposes memory + asset-catalog updates, propose-only (`LRN-01..04`).
- [`.claude/agents/memory-curator.md`](.claude/agents/memory-curator.md) — files entries, regenerates `INDEX.md`, normalizes tags/links (`CUR-01..03`).
- [`skills/memory-retrieve/`](skills/memory-retrieve/SKILL.md) — canonical index-first retrieval used by every phase.

**The full pipeline is now drafted** — all 9 phase subagents + 2 skills. `intake → analysis → design → self_critique → spec → ⟦approve⟧ → build → review → learn → ⟦approve⟧ → curate` runs end-to-end on paper, and the **outer feedback loop closes**: a completed task proposes memory that, once approved, sharpens future tasks. Next: real end-to-end testing, then optional hooks (`docs/04` §4.4).

## How to run it (fresh Claude Code)

> Strawman — validated on paper, not yet hardened by live runs. Expect to iterate on the agent prompts.

**Prerequisites**
- [Claude Code](https://claude.com/claude-code) (CLI or IDE extension) with an active Claude login.
- `git` and `python3` (3.11+) — Python is only used by the `score-requirements` skill.

**Setup**
1. Clone and enter the repo:
   ```bash
   git clone https://github.com/mohantyajitesh/aj_solution_architect_agent_low_code.git
   cd aj_solution_architect_agent_low_code
   ```
2. **Launch Claude Code from the repo root.** It auto-discovers the orchestrator (`AGENTS.md`), the subagents (`.claude/agents/`), and the `/sdd` command (`.claude/commands/`). The two skills under `skills/` are invoked by the agents directly — `score-requirements` by script path, `memory-retrieve` as a documented procedure — so no extra registration is needed.
3. **Tailor it to your org before the first real run** (recommended):
   - Fill in `AGENTS.md` **§8** (always-on organizational constraints — your platform commitments, hard boundaries).
   - Replace the placeholders in `memory/assets/hcm-system-service.md` (report names, endpoints, the ABC schema), or delete it and add your own assets/standards under `memory/`.
4. *(Optional)* Sanity-check the scoring skill:
   ```bash
   echo '{"dimensions":{"a":{"score":80,"rating":"clear","blocking":false}}}' \
     | python3 skills/score-requirements/score.py
   ```

**Run a task**
1. In Claude Code: `/sdd "<your requirement>"` (or a path to a requirements file).
2. The agent **triages**, states a right-sized plan, and runs the pipeline.
3. Respond at the **gates**:
   - *Clarification* (if requirements score low or have a blocking gap) — answer the questions.
   - *Spec approval* — `approve`, or `reject: <feedback>` to loop back to design.
   - *Memory approval* — `approve` to save the proposed lessons, or `skip`.
4. Artifacts land in `workspace/<task-id>/`; approved memory lands in `memory/`. **Commit memory to persist the learning:**
   ```bash
   git add memory && git commit -m "Memory from <task>"
   ```

**Good to know**
- Control is currently **soft** — instructions + per-phase Verification self-checks. If you see the agent build before approval or loop too long, that's the signal to add the optional hooks in [`docs/04` §4.4](docs/04-control-and-enforcement.md).
- Everything is plain files: `workspace/` is per-task scratch; `memory/` is your durable, git-versioned knowledge base.

## The one-paragraph thesis

The original design's value was an **enforced** pipeline — control flow guaranteed *outside* the LLM. A low-code Claude-native rebuild necessarily converts those hard structural guarantees into **subagent-orchestrated, instruction-driven** guarantees: softer, but recoverable to ~90% via hooks if and when we choose to add them. In exchange we get dramatically less code, cleaner per-phase context (subagents beat nodes for context isolation), zero retrieval infrastructure (vectorless memory), native human gates, and first-class distribution (plugins). We accept two conscious costs: **Claude lock-in** (the provider abstraction is gone) and **soft process enforcement until hooks are added**. Both are deliberate, reversible, and justified for a single-user conversational architect tool.
