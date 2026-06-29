# 06 — Technology Justifications

Each major design and technology choice is justified against five dimensions:

- **Performance** — latency, token cost, runtime overhead
- **Simplicity** — moving parts, setup burden, cognitive load
- **Portability** — ease of moving across machines / users / platforms
- **Reusability** — how well the component is reused across phases / projects
- **Accuracy** — effect on the precision/correctness of the agent's output

Ratings: ●●● strong · ●●○ moderate · ●○○ weak. Ratings are *relative to the original LangGraph design* and to plausible alternatives, not absolute.

---

## 6.0 Overall design selection — Claude Code–native, low-code

**Chosen over:** (a) keeping the LangGraph framework; (b) Claude Desktop + Skills + MCP (no subagents); (c) Cowork-first.

| Dimension | Rating | Justification |
|---|---|---|
| Performance | ●●○ | Removes Python orchestration overhead and the ChromaDB index; per-phase subagents add some dispatch latency but isolate context, reducing token bloat on later phases. Net neutral-to-positive. |
| Simplicity | ●●● | ~1,500 lines of Python → markdown agent defs + `AGENTS.md`. The single biggest simplification in the redesign. |
| Portability | ●●● | Plugin-based distribution; no infra; markdown + git core. |
| Reusability | ●●● | Subagents/skills are reusable across tasks and packageable for other users; `AGENTS.md` is cross-tool. |
| Accuracy | ●●○ | Output precision preserved (same model + instructions + memory) and *helped* by context isolation; the one risk is soft process enforcement, mitigated by the human-in-loop and deferred hooks. |

**Why not keep LangGraph?** It buys *enforced* control we've judged largely redundant for an interactive single-user tool, at the cost of heavy code and infra. Its enforcement was also only partially wired in the original (half the cycle limits are dead config).

**Why not Claude Desktop?** No subagents, no hooks — it cannot host the chosen design or its future control plane. Desktop is a chat client; we need the power/builder surface.

**Why not Cowork-first?** Cowork is a downstream distribution surface on the same substrate; it is more skill/connector-centric and may not expose subagent/hook control. Build on Claude Code, distribute via Cowork later if audience warrants.

---

## 6.1 `AGENTS.md` orchestrator (vs. LangGraph graph; vs. `CLAUDE.md`)

| Dimension | Rating | Justification |
|---|---|---|
| Performance | ●●● | Zero runtime cost — it's context, not code. |
| Simplicity | ●●● | One human-readable file replaces graph construction + edge functions. |
| Portability | ●●● | `AGENTS.md` is an emerging cross-tool standard (Claude Code + other agentic IDEs read it), maximizing reuse beyond Claude. |
| Reusability | ●●● | The pipeline contract is reused on every task and portable to other tools. |
| Accuracy | ●●○ | Strong *guidance* to the model, but *instructional* not *structural* — the soft-enforcement caveat. |

**Why `AGENTS.md` over `CLAUDE.md`:** identical role inside Claude Code, but `AGENTS.md` ports to other IDEs for free. A pure portability hedge at no cost.

---

## 6.2 Phase subagents (vs. graph nodes; vs. skills; vs. one mega-prompt)

| Dimension | Rating | Justification |
|---|---|---|
| Performance | ●●○ | Each subagent is a dispatch with fresh context — modest overhead, but avoids dragging the whole conversation into late phases (net token win on long tasks). |
| Simplicity | ●●● | Markdown + YAML frontmatter; no graph wiring, no Python. |
| Portability | ●●○ | Easy within Claude Code (plugin), but the **non-portable primitive** when leaving Claude (must flatten). Accepted trade. |
| Reusability | ●●● | Each phase agent is reusable across tasks; tool allowlists make them safe to reuse. |
| Accuracy | ●●● | **The accuracy win.** Context isolation means `spec` reasons over clean inputs, not intake's noise. Tool allowlists prevent cross-phase corruption (analysis can't write code). Strictly better than shared-state nodes or one accumulating prompt. |

**Why subagents over skills for phase logic:** skills auto-trigger by description match (soft, nondeterministic sequencing); subagents are dispatched explicitly by the orchestrator and carry isolated context + capability boundaries. For a disciplined pipeline, explicit dispatch + isolation beats auto-trigger.

**Why subagents over one mega-prompt:** a single conversation accumulates context across all phases, degrading late-phase accuracy and inflating tokens. Subagents reset context per phase.

---

## 6.3 Minimal skills (vs. skills-as-phases; vs. no skills)

| Dimension | Rating | Justification |
|---|---|---|
| Performance | ●●● | Negligible overhead; invoked only where a procedure repeats. |
| Simplicity | ●●● | Few skills = little to maintain. |
| Portability | ●○○ | Skills are **Claude-only** — the least portable primitive; kept minimal to limit portability debt. |
| Reusability | ●●● | By definition: a skill exists only when a procedure is reused across phases (e.g. `score-requirements`, `memory-retrieve`). |
| Accuracy | ●●● | The one place we *want* determinism — `score-requirements` keeps the quality-gate math exact, as in the original. |

**Why minimal:** skills are sticky (Claude-only). Using them only for genuinely reused, determinism-worthy procedures keeps portability high and avoids the "skills auto-trigger as soft orchestration" anti-pattern.

---

## 6.4 Vectorless, file-based memory (vs. ChromaDB / vector DB)

| Dimension | Rating | Justification |
|---|---|---|
| Performance | ●●● | No embedding/index step; index is one small markdown file read. At this corpus size, faster and cheaper than vector round-trips. |
| Simplicity | ●●● | Deletes an entire subsystem (vector DB + indexer + staleness logic). |
| Portability | ●●● | Plain files + git; nothing to rebuild or migrate. Removed the only custom MCP — the biggest distribution friction. |
| Reusability | ●●● | Memory files are reusable knowledge; the `memory-retrieve` procedure is reused by every phase. |
| Accuracy | ●●○ | Retrieval relevance rides on the model + tags + index, not embeddings — strong for a curated corpus, with a known ceiling at large scale (mitigated by the curator subagent; revisited only if the corpus explodes). |

**Why vectorless wins here:** native to Claude Code's grep/read model, sufficient for tens-to-hundreds of curated entries, and infra-free. Vector search only pays off at large scale + semantic fuzziness — a regime this corpus won't reach soon. See [`docs/03`](03-memory-vectorless-rag.md).

---

## 6.5 `memory-curator` subagent

| Dimension | Rating | Justification |
|---|---|---|
| Performance | ●●○ | Runs occasionally (after `learn` / on demand); not on the hot path. |
| Simplicity | ●●○ | One extra agent, but it *automates* the discipline vectorless retrieval depends on. |
| Portability | ●●● | Operates purely on markdown. |
| Reusability | ●●● | Reusable maintenance across all memory. |
| Accuracy | ●●● | Directly protects retrieval accuracy over time (tags, links, dedup, index freshness) — the key to vectorless memory aging well. |

---

## 6.6 Git / GitHub as storage & distribution (vs. SQLite checkpointer; vs. ad-hoc local)

| Dimension | Rating | Justification |
|---|---|---|
| Performance | ●●● | No runtime cost; git operations are off the interaction path. |
| Simplicity | ●●● | One well-understood tool for versioning, backup, sync, and sharing. |
| Portability | ●●● | The backbone of portability — clone to move anywhere; the plugin and memory ship as a repo. |
| Reusability | ●●● | The whole solution (agents, skills, `AGENTS.md`, memory) is reused via clone/install. |
| Accuracy | ●○○ | Indirect — version history aids auditability/rollback of memory, but doesn't affect output precision. |

**Why git over the original's checkpointer:** durable truth lives in files; tasks resume from the workspace directory. Git adds versioning + distribution that the SQLite checkpointer never provided. Simpler *and* more capable for this use.

---

## 6.7 Native human gates (vs. `interrupt_before`)

| Dimension | Rating | Justification |
|---|---|---|
| Performance | ●●● | No machinery; a turn in the conversation. |
| Simplicity | ●●● | No interrupt wiring, no resume-command parsing. |
| Portability | ●●● | Conversational pause works on any chat/agent surface. |
| Reusability | ●●● | Same gate pattern at every checkpoint. |
| Accuracy | ●●● | Cleaner than the original — and avoids the original's latent bug where a `reject` resume did not actually route back to design. |

---

## 6.8 Deferred hooks control plane (vs. LangGraph conditional edges)

| Dimension | Rating | Justification |
|---|---|---|
| Performance | ●●● | Hooks fire on tool events; negligible cost, only when added. |
| Simplicity | ●●○ | Hooks are small declarative glue — the one place "code" re-enters; kept minimal and added reactively. |
| Portability | ●○○ | Hooks are Claude-Code-specific; they don't port (but they're optional and additive). |
| Reusability | ●●● | Each hook enforces one invariant reused across all tasks. |
| Accuracy | ●●● | When added, restores deterministic process guarantees (≈90% of the original's enforcement) for the specific invariants we choose. |

**Why deferred:** adding hooks pre-emptively reintroduces the complexity we set out to shed. We add them *reactively*, one invariant at a time, only when a real failure mode appears. See [`docs/04`](04-control-and-enforcement.md).

---

## 6.9 Summary heatmap

| Component | Perf | Simpl | Port | Reuse | Acc |
|---|:--:|:--:|:--:|:--:|:--:|
| Claude Code–native (overall) | ●●○ | ●●● | ●●● | ●●● | ●●○ |
| `AGENTS.md` orchestrator | ●●● | ●●● | ●●● | ●●● | ●●○ |
| Phase subagents | ●●○ | ●●● | ●●○ | ●●● | ●●● |
| Minimal skills | ●●● | ●●● | ●○○ | ●●● | ●●● |
| Vectorless memory | ●●● | ●●● | ●●● | ●●● | ●●○ |
| `memory-curator` | ●●○ | ●●○ | ●●● | ●●● | ●●● |
| Git / GitHub | ●●● | ●●● | ●●● | ●●● | ●○○ |
| Native gates | ●●● | ●●● | ●●● | ●●● | ●●● |
| Deferred hooks | ●●● | ●●○ | ●○○ | ●●● | ●●● |

**Reading the heatmap:** simplicity and portability are strong across the board (the redesign's whole point). Accuracy is strong where it counts (subagents, gates, curator, skills) with two deliberate ●●○ caveats — overall accuracy and vectorless memory — each tied to a *known, bounded, and deferred* risk (soft enforcement; large-corpus retrieval). The only ●○○ cells are (a) skill portability and (b) hook portability — both accepted, both isolated to optional/minimal layers.
