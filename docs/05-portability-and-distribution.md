# 05 — Portability & Distribution

Portability is a primary goal, so it gets its own analysis. The central principle:

> **Portability is inversely proportional to reliance on platform-specific primitives.** Open/emerging standards (MCP, `AGENTS.md`, plain markdown, git) are portability *assets*. Claude-specific constructs (Skills, subagents, plugins) are portability *taxes*. Design choices are, in part, choices about which side of that line to sit on.

## 5.1 The four layers and their portability

The solution decomposes into four layers with very different mobility:

| Layer | Form | Across other Claude Code users | To another AI IDE (e.g. Copilot/VSCode) |
|---|---|---|---|
| Orchestration logic | `AGENTS.md` (markdown) | **Trivial** | **Easy** — `AGENTS.md` is increasingly cross-tool |
| Memory + artifacts | plain markdown + git | **Trivial** | **Trivial** — just files |
| Phase logic | **subagents** (`.claude/agents/*.md`) | **Easy** (ships in the plugin) | **Hard** — no subagent concept; must flatten |
| Reusable procedures | **skills** (minimal) | **Easy** (ships in the plugin) | **Medium** — re-author as prompt files |

Two layers are essentially free to move; two carry a tax. We deliberately **minimized the taxed layers** (thin skills) and **standardized the free ones** (`AGENTS.md`, markdown, git).

## 5.2 Dimension 1 — across other developers' Claude Code

**Verdict: Easy.** The "no vector DB" decision removed the single biggest friction (a custom memory MCP requiring per-machine Python setup). What remains is clean:

- **Distribution vehicle = a Claude Code plugin.** Agents + commands + (thin) skills + `AGENTS.md` + memory seed bundle into one installable unit, shareable via a plugin marketplace or a git repo. No per-machine infra, no config-file path surgery.
- **Memory travels as a git repo** — versioned, shareable, rebuild-free (there is no index to rebuild). A receiving developer either starts empty or inherits a curated knowledge base by cloning.
- **Execution is local** by default — fast, private, zero setup.
- **Target:** install + first task in < 15 minutes, no custom services (success criterion S6).

What a receiving developer does:
1. Install the plugin (marketplace or `git clone` + add to Claude Code).
2. Optionally clone/seed the `memory/` repo.
3. Run `/sdd "<requirement>"`.

That's it — no runtime to provision, no `claude_desktop_config.json` paths to edit, no vector store to build.

## 5.3 Dimension 2 — toward another AI IDE (Copilot on VSCode, etc.)

**Verdict: Moderate, ~60–70% reuse.** The portable core carries most of the weight; the Claude-specific orchestration is what gets re-expressed.

**Ports cleanly:**
- **`AGENTS.md`** — Copilot and several agentic IDEs read `AGENTS.md` / equivalent custom-instruction files. The orchestration *content* transfers.
- **Memory + artifacts** — plain markdown, readable anywhere; no MCP even required for file access.
- **MCP servers (if any are added later)** — MCP is an open standard supported by VSCode agent mode and Copilot, so any future tool server ports unchanged.

**Must be re-expressed:**
- **Subagents** — there is no portable named-subagent-with-isolated-context concept on Copilot. You **flatten** the pipeline into sequential prompt-file / instruction steps under a single agent following `AGENTS.md`. It runs, but you lose per-phase context isolation, so output quality may dip more than the prompt text alone implies.
- **Skills** → Copilot **prompt files** / custom instructions. The content transfers; the packaging is rebuilt.

**Must be re-validated:**
- **The ≥80% target is model- and platform-coupled.** Soft enforcement means quality rides on the model interpreting instructions. On a different model behind Copilot, re-measure. Selecting Claude models inside Copilot minimizes drift.

**Conceptual mismatch to expect:**
- Claude Code/IDE is repo-oriented; the original Desktop notion was chat-oriented. Our tool is design-artifact-centric, so it sits comfortably in either, but the "agent operating in your repo" framing differs from "chat with an architect."

## 5.4 The portability trade we consciously made

By choosing **subagents over skills** (for quality and context isolation), we **moved the non-portable primitive** from Skills to subagent orchestration. Within Claude Code this is a clear win (better isolation, plugin distribution). Leaving Claude Code, subagent orchestration is precisely the part that flattens. This is an accepted trade, stated plainly so it is never a surprise:

- **Optimize for in-Claude quality and easy developer distribution now** (subagents + plugin).
- **Preserve a portable escape hatch** by keeping orchestration in `AGENTS.md` and all data in markdown — so a Copilot port is a *flatten-and-retune*, not a rewrite.

## 5.5 Storage vs. execution (do not conflate)

| Axis | Choice now | Deferred upgrade |
|---|---|---|
| **Storage / sync / distribution** | **GitHub repo** (markdown source of truth) | — (already the right layer) |
| **Execution environment** | **Local machine** | **GitHub Codespaces** (cloud, anywhere-access, team-shared) — when zero-setup or shared runtime is needed |

GitHub is not an *alternative* to local — it is the storage layer that *feeds* either a local or a Codespaces runtime via git. Codespaces is the same idea as "host it remotely," parked until distribution demands it.

## 5.6 Cowork as a future distribution surface

Cowork runs on the **same plugin / skill / MCP substrate** as Claude Code — it is a *consumption* surface, not a different foundation. The plan:

- **Build and harden on Claude Code** (full subagent + future-hook control lives here).
- **Package as a plugin** so the option to distribute via Cowork stays open at zero extra cost.
- **Consider Cowork later, driven by audience** — specifically if non-terminal colleagues need a guided, connector-rich experience.

Caveat to verify before betting on it: Cowork appears more **skill/connector-centric**, which is in mild tension with our **subagent-heavy** design. Whether Cowork fully supports subagent/hook-level control should be confirmed before relying on it as a distribution channel — flagged, not assumed.
