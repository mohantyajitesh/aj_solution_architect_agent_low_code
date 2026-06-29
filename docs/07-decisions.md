# 07 — Decision Record (ADRs)

Short, ADR-style records of the settled decisions behind this design. Each: context → decision → consequences. These are the decisions we treat as **settled for the design draft**; all remain open to revision during review.

---

## ADR-01 — Substrate is Claude Code (not Desktop, not Cowork)

**Context.** The redesign leans on subagents and a future hooks-based control plane. Claude Desktop is a chat client with no subagents/hooks. Cowork is a guided, connector-centric surface built on the same plugin substrate, more skill-oriented.

**Decision.** Build on **Claude Code**. Treat Cowork as a *downstream distribution channel* (package as a plugin so the option stays open). Do not target Desktop.

**Consequences.** (+) Full access to subagents, tool allowlists, plugins, and the hooks escape hatch. (+) Plugin-based distribution. (−) Not usable in the Desktop chat app. (−) Cowork distribution needs later validation of its subagent/hook support.

---

## ADR-02 — Subagent-driven orchestration, minimal skills

**Context.** Phase logic could live in skills (auto-triggered) or subagents (explicitly dispatched). Skills are Claude-only and the least portable primitive.

**Decision.** Express each phase as a **subagent**; reserve **skills** for genuinely reusable, determinism-worthy procedures (`score-requirements`, `memory-retrieve`).

**Consequences.** (+) Per-phase context isolation → higher late-phase accuracy. (+) Capability boundaries via tool allowlists. (+) Minimal portability tax from skills. (−) Subagent orchestration becomes the non-portable layer when leaving Claude (must flatten). (−) Slight per-phase dispatch latency.

---

## ADR-03 — Vectorless, file-based memory (no vector DB)

**Context.** The original used ChromaDB for semantic retrieval. The corpus is a single architect's curated lessons/decisions/patterns (tens-to-hundreds of entries). A custom memory MCP was the biggest distribution friction.

**Decision.** **No vector database.** Memory is curated markdown with `INDEX.md` + front-matter tags + `[[links]]`, retrieved agentically + lexically (read index → select → grep → read → traverse). A `memory-curator` subagent maintains it.

**Consequences.** (+) Zero infra, transparent, fresh, fully portable; removes the only custom MCP. (+) Native to Claude Code's grep/read retrieval model. (−) No semantic fuzziness (mitigated by tags + agentic relevance + curation). (−) Known ceiling at large corpus size — revisit with a memory MCP behind the same retrieval interface only if the corpus explodes.

---

## ADR-04 — Git/GitHub for storage, local for execution

**Context.** Memory and the solution itself need persistence, versioning, sync, and distribution. "Storage" and "execution environment" are separate axes that were being conflated (GitHub vs. Codespaces vs. local).

**Decision.** **GitHub repo** is the source of truth (storage/sync/distribution). **Local machine** is the default execution environment. **Codespaces** is a deferred cloud-execution option, fed by the same repo via git.

**Consequences.** (+) Versioned, shareable, backup-friendly, rebuild-free memory. (+) Clean distribution. (−) Multi-machine sync is manual (git pull/push). (−) Cloud/anywhere access waits for the Codespaces upgrade.

---

## ADR-05 — Soft enforcement now, hooks deferred

**Context.** The original's value was *enforced* control flow. Low-code Claude-native orchestration is *instructed*, not *enforced*. Hooks can restore determinism but are Claude-specific glue (re-introducing some code).

**Decision.** Start with **soft enforcement** (`AGENTS.md` + subagents + `score-requirements` + optional `state.json`). Add **hooks reactively**, one invariant at a time, only when a real failure mode is observed. Keep the design hook-ready (each lost guarantee maps to exactly one future hook).

**Consequences.** (+) Maximum simplicity to start; human-in-loop is the backstop. (+) Clear, surgical path to ~90% of original enforcement. (−) No structural guarantee until hooks exist. (−) The ≥80% target is model/instruction-coupled until then.

---

## ADR-06 — Accept Claude lock-in (drop provider abstraction)

**Context.** The original prized a `ReasoningProvider`/`BuilderProvider` abstraction for swapping to Ollama/Bedrock. Running natively inside Claude Code, that abstraction is moot.

**Decision.** **Drop the provider abstraction.** Commit to Claude.

**Consequences.** (+) Removes a whole layer (interfaces, factory, subprocess wrappers, `_clean_env` nesting hacks). (+) Simpler, less code. (−) No multi-LLM swap. (−) Cross-IDE ports re-validate quality on whatever model that platform runs. Revisit only if a second model becomes a hard requirement.

---

## ADR-07 — `AGENTS.md` over `CLAUDE.md` for the orchestrator filename

**Context.** Inside Claude Code, `CLAUDE.md` and `AGENTS.md` play the same role. Other agentic IDEs increasingly read `AGENTS.md`.

**Decision.** Author the orchestrator as **`AGENTS.md`**.

**Consequences.** (+) Cross-tool portability of the orchestration content at zero cost. (−) None material within Claude Code.

---

## ADR-08 — Distribute as a Claude Code plugin

**Context.** Other developers need to install and run this with minimal setup; the original required clone + pip + Docker + per-machine config.

**Decision.** Package agents + commands + thin skills + `AGENTS.md` + memory seed as a **Claude Code plugin**.

**Consequences.** (+) One-step install, no infra, marketplace-shareable, keeps the Cowork door open. (−) Plugin packaging is Claude-Code-specific (but the underlying markdown remains portable).
