# Memory Store

The agent's accumulated knowledge — plain markdown, retrieved **vectorlessly**
(index-first, no vector DB). Full design: [`docs/03`](../docs/03-memory-vectorless-rag.md).

## Categories
| Category | Authored by | Purpose |
|---|---|---|
| `assets/` | human | **Capability catalog** of systems we already own — drives reuse-first design |
| `standards/` | human | Dev standards & architectural practices — treated as constraints |
| `lessons/` | agent (`learn` phase) | What went well/wrong; what to do differently |
| `decisions/` | agent | Architectural choices + rationale (ADR-style) |
| `patterns/` | agent | Reusable design/spec patterns |

## How retrieval works
1. Read **`INDEX.md`** (compact, the entry point).
2. Select the few relevant entries by tag / `systems` / summary.
3. Open **only** those files; optionally `grep` and follow `[[links]]`.

Never read the whole corpus. See [`docs/03` §3.3a](../docs/03-memory-vectorless-rag.md) (token economics).

## Conventions
- **Atomic entries** — one asset/lesson/standard per file.
- **Front-matter** — `title, category, tags`; reference content adds `source, authority, status, systems, owner`.
- **Filenames** — reference (`assets`/`standards`): clean slug (`hcm-system-service.md`).
  Experiential (`lessons`/`decisions`/`patterns`): dated `YYYY-MM-DD_task-id_category-slug.md`.
- **`authority: reference`** entries outrank one-off experiential lessons on conflict.
- Always-true constraints belong in **`AGENTS.md`**, not here (retrieval is probabilistic).

## Where to put what
- Existing system we own → `assets/` (with "when to use / when NOT to use").
- A rule the agent must always obey → `AGENTS.md` (always-on) or `standards/` (situational).
- Something the agent learned from a task → it proposes a `lessons/decisions/patterns` entry at `learn`; you approve.
