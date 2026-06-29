# 02 — Architecture

## 2.1 The big picture

```
┌──────────────────────────────────────────────────────────────────────┐
│  Claude Code (substrate: CLI / IDE extension)                          │
│                                                                        │
│  AGENTS.md  ── persona + pipeline contract + gate rules (orchestrator) │
│      │                                                                 │
│   /sdd  ── slash command: starts/loads a task, drives the sequence     │
│      │                                                                 │
│      ▼                                                                 │
│  ┌────────── phase subagents (.claude/agents/*.md) ───────────────┐    │
│  │ intake → analysis → design → critique → spec → build → review   │    │
│  │                                  ↑__________loop-backs_________│    │
│  │ + memory-curator   + builder                                    │    │
│  └─────────────────────────────────────────────────────────────────┘   │
│      │ read/write                          │ delegate (agentic)         │
│      ▼                                      ▼                           │
│  workspace/<task>/*.md  (artifacts)    workspace/<task>/src/ (code)     │
│      │                                                                  │
│      ▼ retrieve / propose                                               │
│  memory/{lessons,decisions,patterns}/*.md  +  memory/INDEX.md          │
│  skills/  (thin, reusable procedures)                                   │
└──────────────────────────────────────────────────────────────────────┘
            │ git push/pull (storage + sync + distribution)
            ▼
   GitHub repo  ── source of truth for memory, agents, skills, AGENTS.md
```

Everything inside the box is **markdown or config** — no application code. The only candidate for code is the deferred hooks layer ([`docs/04`](04-control-and-enforcement.md)).

## 2.2 Components

### 2.2.1 Orchestrator — `AGENTS.md`

The single source of truth for *identity* and *process*. It carries:

- the **persona** (senior solution architect — ported verbatim from the original `persona.md`),
- the **pipeline contract**: the canonical phase order, what each phase consumes/produces, and the loop-back rules (when critique fails, return to design/analysis/intake; when review finds drift, return to build),
- the **gate rules**: where to stop and ask the human (spec approval, memory write), and
- the **memory protocol**: consult `memory/INDEX.md` at task start and at each reasoning phase; propose new memory only at `learn`.

`AGENTS.md` is chosen over a Claude-only filename deliberately — it is an emerging cross-tool standard (read by Claude Code, and by other agentic IDEs), which buys portability "for free" (see [`docs/05`](05-portability-and-distribution.md)).

### 2.2.2 Entry point — `/sdd` slash command

A user-invoked command (`.claude/commands/sdd.md`) that:

- creates or resumes a task (`workspace/<task-id>/`),
- seeds the workspace with the requirement,
- and instructs the orchestrator to begin at `intake` and proceed through the pipeline, honoring gates.

Why a slash command rather than relying on skill auto-trigger: **determinism of entry.** Skills trigger by description-match (soft); a slash command is an explicit, user-controlled start — the right behavior for "begin a disciplined pipeline."

### 2.2.3 Phase subagents — `.claude/agents/*.md`

Each phase is a subagent with its own definition: a focused system prompt, a tool allowlist, and (optionally) a model choice. The set:

| Subagent | Consumes | Produces | Notes |
|---|---|---|---|
| `intake` | raw requirement + memory | `requirements.md`, `requirements_quality.md` | scores quality across 6 dimensions; computes confidence |
| `analysis` | requirements + memory | `analysis.md` | scope, constraints, dependencies, risks |
| `design` | requirements + analysis + memory | `design.md` | architecture + tradeoffs + alternatives |
| `critique` | requirements + analysis + design + lessons | `critique.md` (verdict) | multi-angle challenge; emits PASS / FAIL_* |
| `spec` | all prior artifacts | `spec.md` | the implementation contract |
| `build` | `spec.md` | `workspace/<task>/src/` | agentic; **gated by human approval first** |
| `review` | `spec.md` + build result | `review.md` (verdict) | CLEAN / SPEC_DRIFT |
| `learn` | all artifacts | memory proposals | **gated by human approval** before writing |
| `memory-curator` | `memory/**` | updated `INDEX.md`, tags | housekeeping; keeps vectorless retrieval sharp |

**Why subagents are the right unit (vs. nodes or skills):**

- **Context isolation** — each subagent runs in a fresh context with *only* the artifacts it needs. This is strictly better than the original LangGraph nodes, which shared one growing state, and far better than running every phase in one accumulating conversation. Cleaner context → higher accuracy on later phases (spec generation isn't polluted by intake's tokens).
- **Per-phase control** — tool allowlists mean the `analysis` agent can't write code and the `build` agent can't rewrite requirements. This is a *capability* boundary, achieved declaratively.
- **Low-code** — a subagent is just markdown + YAML frontmatter. No functions, no graph wiring.

### 2.2.4 Skills — `skills/` (minimal)

Skills are reserved for **reusable procedures invoked by more than one phase**, not as the carriers of phase logic. Candidate skills:

- `score-requirements` — the deterministic 6-dimension scoring + threshold check (ported from `qualification_tools.py`; the one place we *want* determinism in the quality gate).
- `write-artifact` / `read-artifact` conventions — if not handled by native file tools.
- `memory-retrieve` — the canonical "read INDEX, select, read files" procedure (so every phase retrieves the same way).

Skills are deliberately thin because they are **Claude-only** and therefore the least portable primitive (see [`docs/05`](05-portability-and-distribution.md)). Keeping them minimal reduces portability debt.

### 2.2.5 Memory — vectorless, file-based

`memory/{lessons,decisions,patterns}/*.md` plus a maintained `memory/INDEX.md`. Retrieval is **agentic + lexical**: read the index, pick relevant entries (optionally grep), read the chosen files. Full design in [`docs/03`](03-memory-vectorless-rag.md).

### 2.2.6 Workspace — per-task artifacts

`workspace/<task-id>/` holds the phase artifacts (`requirements.md`, `analysis.md`, …) and `src/` for delegated builds. **The artifacts *are* the task state** — "which files exist" tells you the phase, which makes a task resumable without a checkpointer.

### 2.2.7 Storage — git / GitHub

GitHub is the source of truth for memory, agents, skills, and `AGENTS.md`. Local machine is the execution environment. Git provides versioning, backup, sharing, and distribution. (Codespaces / remote execution is a deferred option, not a parallel store — see [`docs/05`](05-portability-and-distribution.md).)

## 2.3 Control flow (the pipeline as instructions)

The orchestrator drives this sequence; loop-backs and gates are expressed as rules in `AGENTS.md`, not as graph edges:

```
/sdd "<requirement>"
  → intake ──(confidence ≥ threshold?)──┬─ yes → analysis
                                         └─ no  → ASK USER (clarify) → intake
  → analysis → design → critique ──(verdict)──┬─ PASS          → spec
                                              ├─ FAIL_DESIGN   → design
                                              ├─ FAIL_ANALYSIS → analysis
                                              └─ FAIL_REQS     → intake
  → spec → ⟦GATE: human approves spec⟧ ──┬─ approve → build
                                          └─ reject  → design
  → build → review ──(verdict)──┬─ CLEAN      → learn
                                └─ SPEC_DRIFT → build
  → learn → ⟦GATE: human approves memory⟧ → memory-curator → done
```

Two things to be honest about here, both elaborated in [`docs/04`](04-control-and-enforcement.md):

1. **This sequence is *instructed*, not *enforced*.** The orchestrator follows it because `AGENTS.md` tells it to. A graph made skipping impossible; here it is merely strongly discouraged. The mitigation path (hooks) is designed-for but deferred.
2. **Cycle limits are advisory** until a hook (or a tiny `state.json` counter maintained by the orchestrator) makes them hard. In interactive use the human is the backstop against runaway loops.

## 2.4 State & resumption

- **Primary state = the workspace directory.** Phase = highest artifact present. A task is resumed by pointing `/sdd` at an existing `task-id`.
- **Optional `state.json`** (per task): `{current_phase, iteration_count, gate_status}`. Lightweight, human-readable, and the seed for hard cycle-limits later. Maintained by the orchestrator; promoted to hook-enforced when we add hooks.
- **No checkpointer, no SQLite.** Conversation context is transient; durable truth lives in files. This is simpler and more transparent than the original's `MemorySaver`.

## 2.5 Human gates

Gates are **conversational**, which is a UX upgrade over the original's "type `approve`" CLI gate:

- **Spec approval gate** (before `build`): the agent presents the spec summary and asks; it does not delegate to the builder until the user approves. Reject → loop to `design` with feedback. *(This also sidesteps a latent bug in the original where `interrupt_before` resume did not actually route rejections back to design.)*
- **Memory approval gate** (before writing memory in `learn`): the agent proposes entries and asks; nothing is written to `memory/**` until approved.
- **Clarification gate** (intake, below threshold): the agent asks targeted questions and waits.

The risk — an over-eager model proceeding without waiting — is mitigated today by explicit `AGENTS.md` rules ("STOP and ask; do not call the builder subagent until the user replies 'approve'") and, later, by a `PreToolUse` hook that blocks the builder subagent unless an `approved` flag exists.

## 2.6 What this architecture deliberately drops

| Dropped | Why it's safe to drop |
|---|---|
| LangGraph `StateGraph` | Replaced by `AGENTS.md` + subagents; the human-in-loop absorbs most of the lost enforcement |
| ChromaDB | Corpus is small + curated; vectorless retrieval is native and sufficient |
| Provider ABC + `subprocess` wrappers | Running *inside* Claude Code; no wrapper needed (accepted lock-in) |
| Streamlit UI | Claude Code is the surface |
| SQLite checkpointer | Files are the durable state; tasks resume from the workspace |
| Router node | The model understands intent natively; explicit classifier is redundant |
