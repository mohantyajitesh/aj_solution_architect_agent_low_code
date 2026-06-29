# 01 — Overview, Goals & Non-Goals

## 1.1 Background

The original **Architect Agent** is a personal AI solution architect that runs an enforced Spec-Driven Development (SDD) pipeline: it takes a requirement from intake → analysis → design → self-critique → spec generation → build delegation → review → learn, with human approval gates and an accumulating, model-agnostic memory.

It is implemented as a **LangGraph `StateGraph`**: every phase is a node, transitions are edges, loop-backs are conditional edges keyed on parsed LLM verdicts, infinite loops are bounded by per-phase cycle counters, and human gates use `interrupt_before` / `interrupt_after`. Memory is markdown indexed into ChromaDB for semantic retrieval. LLM calls are funnelled through a `ReasoningProvider` / `BuilderProvider` abstraction so the underlying model can be swapped. The UI is Streamlit.

It works and has produced real enterprise designs (e.g. an iCIMS → Oracle HCM integration). But for a **single-user, conversational** tool, the orchestration machinery is heavy: ~1,500 lines of Python whose primary job is to *force* an order that a disciplined user-in-the-loop largely enforces anyway.

## 1.2 What we are designing

A **low-code, Claude Code–native** re-expression of the same agent that:

- replaces the LangGraph control plane with an **`AGENTS.md` orchestrator + phase subagents**,
- replaces ChromaDB with **vectorless, file-based memory**,
- uses **git** as the storage / sync / distribution layer,
- keeps human gates as **natural conversational turns**,
- and is packaged as a **Claude Code plugin** for distribution.

The redesign is the product of a deliberate reasoning chain (captured in [`docs/07-decisions.md`](07-decisions.md)). The headline conclusions:

1. **Substrate = Claude Code**, not Claude Desktop (Desktop has no subagents/hooks) and not Cowork yet (Cowork is a downstream distribution surface on the same plugin substrate).
2. **Subagent-driven, minimal skills** — subagents give per-phase context isolation and are the right unit for phase logic; skills are reserved for genuinely reusable procedures.
3. **No vector DB** — vectorless retrieval over curated markdown is native to Claude Code (it already navigates codebases by grep/read, not embeddings) and is sufficient for a corpus of tens-to-hundreds of curated entries.

## 1.3 Goals (in priority order)

1. **Preserve output precision.** The quality of analysis/design/critique/spec must match or exceed the original. This is mostly a function of model + phase instructions + retrieved memory — all of which transfer.
2. **Preserve as much process control as a low-code substrate allows**, and keep a clean path to *full* control (hooks) without re-architecting.
3. **Radically reduce code.** Target: orchestration and phases expressed as markdown (agent defs, `AGENTS.md`, skills), with near-zero application code.
4. **Maximize portability** — across other developers' machines, and (secondarily) toward other AI IDEs.
5. **Target ≥ 80% success across use-cases/requirements** in interactive use.

## 1.4 Non-Goals (explicitly out of scope for now)

- **Provider abstraction / multi-LLM swap.** We accept Claude lock-in. (Revisit only if a second model becomes a hard requirement.)
- **Hard, structural enforcement on day one.** Ordering and cycle limits are *soft* (subagent-orchestrated) initially; hooks are the deferred upgrade. See [`docs/04`](04-control-and-enforcement.md).
- **Semantic vector retrieval.** Deferred; reconsidered only if the memory corpus outgrows vectorless retrieval. See [`docs/03`](03-memory-vectorless-rag.md).
- **Remote/hosted MCP and cloud execution (Codespaces).** Deferred; local execution + git sync first. See [`docs/05`](05-portability-and-distribution.md).
- **Cowork packaging.** Deferred distribution channel; build on Claude Code first.
- **A bespoke UI.** Claude Code (chat/IDE) is the surface. No Streamlit equivalent.

## 1.5 Success criteria

| # | Criterion | How we'll judge it |
|---|---|---|
| S1 | A requirement flows through all SDD phases conversationally | End-to-end run produces all expected artifacts |
| S2 | Each phase produces its artifact in the workspace | `requirements.md`, `analysis.md`, … exist after a run |
| S3 | Memory is retrieved and influences reasoning | Phase outputs reference relevant prior lessons |
| S4 | Human gates pause for approval (spec, memory) | Agent waits; does not auto-build or auto-write memory |
| S5 | ≥ 80% of representative requirements complete without manual pipeline correction | Sampled trials across use-case types |
| S6 | Another developer can install and run it | Plugin install + first task in < 15 min, no custom infra |

## 1.6 Audience & usage assumptions

- **Primary user:** a senior solution architect, technically comfortable, working interactively. The human is continuously in the loop — which is *why* soft enforcement is acceptable as a starting point (the user catches deviations live).
- **Workload shape:** design-heavy. The agent's main output is *design artifacts* (markdown), with optional delegated build into `workspace/<task>/src/`.
- **Corpus size:** memory grows slowly and is curated — well within vectorless retrieval's comfortable range for the foreseeable future.
