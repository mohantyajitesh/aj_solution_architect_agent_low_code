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

**Phase 1 (in progress)** — the first two phase subagents are drafted:
- [`.claude/agents/intake.md`](.claude/agents/intake.md) — structures + quality-scores the requirement, runs the clarification gate, carries `REQ-01..04` Verification.
- [`.claude/agents/design.md`](.claude/agents/design.md) — reuse-first analysis against the asset catalog, tradeoffs + alternatives, standards compliance, `DSN-01..04` Verification.

Remaining subagents (`analysis`, `self_critique`, `spec`, `build`, `review`, `learn`, `memory-curator`) and the thin skills are next.

## The one-paragraph thesis

The original design's value was an **enforced** pipeline — control flow guaranteed *outside* the LLM. A low-code Claude-native rebuild necessarily converts those hard structural guarantees into **subagent-orchestrated, instruction-driven** guarantees: softer, but recoverable to ~90% via hooks if and when we choose to add them. In exchange we get dramatically less code, cleaner per-phase context (subagents beat nodes for context isolation), zero retrieval infrastructure (vectorless memory), native human gates, and first-class distribution (plugins). We accept two conscious costs: **Claude lock-in** (the provider abstraction is gone) and **soft process enforcement until hooks are added**. Both are deliberate, reversible, and justified for a single-user conversational architect tool.
