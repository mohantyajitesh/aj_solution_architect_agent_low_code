# 09 — AWS AI-DLC: Research & Takeaways

Research into AWS's **AI-Driven Development Life Cycle (AI-DLC)** — introduced at re:Invent 2025 and open-sourced as [`awslabs/aidlc-workflows`](https://github.com/awslabs/aidlc-workflows) — and what it means for *this* design. The headline: **AI-DLC independently converges on much of our architecture**, which is strong external validation, and it offers four concrete, low-cost improvements we should adopt.

## 9.1 What AI-DLC is (accurately)

AI-DLC is an **AI-centric software methodology delivered as markdown rule files**, not a product. Two foundational dimensions:

1. **AI-Powered Execution with Human Oversight** — AI builds detailed plans, asks clarifying questions, and defers critical decisions to humans. Mental model: *AI plans → AI seeks clarification → AI implements only after human validation*, repeated rapidly.
2. **Dynamic Team Collaboration** — humans gather to validate AI's proposals at checkpoints.

**Three adaptive phases:**
- **Inception** — business intent → requirements/stories/Units of Work via "**Mob Elaboration**" (the team validates AI's questions/proposals). The "WHAT/WHY".
- **Construction** — validated context → architecture, domain models, code, tests via "**Mob Construction**". The "HOW".
- **Operations** — IaC and deployment with oversight (future).

**Key mechanics worth stealing:**
- **Intent-first** — start from a plain statement of intent (`"Using AI-DLC, …"`), not an elaborate prompt; the workflow scaffolds assess complexity and construct the pathway.
- **Adaptive stages** — "only executes stages that add value." Simple bug fixes skip most stages; complex migrations get the full workflow.
- **Verification sections** — each rule carries concrete checks; the model **verifies compliance before allowing stage progression**. Rule IDs (e.g. `COMPLIANCE-01`) appear in audit logs.
- **Structured questions in files, not chat** — clarification is captured as multiple-choice questions in artifacts.
- **Context persistence as artifacts** — plans/requirements/design live in an `aidlc-docs/` directory, propagating decisions across phases and sessions "without re-prompting."
- **Multi-platform projection** — the *same* markdown methodology is mapped to each tool's native convention.
- **Vocabulary** — "sprints"→"**bolts**" (hours/days), "epics"→"**Units of Work**" (cohesive, self-contained, measurable-value chunks decomposed from intent).

## 9.2 Convergence — what AI-DLC validates in our design

| Our decision | AI-DLC parallel | Verdict |
|---|---|---|
| Markdown-as-methodology, near-zero code | AI-DLC *is* markdown rule files | ✅ Strongly validated |
| `AGENTS.md` orchestrator, cross-tool ([ADR-07](07-decisions.md)) | Same rules projected to `CLAUDE.md`, `.cursor/rules`, `.github/copilot-instructions.md`, etc. | ✅ Validated — and they ship the mapping |
| Artifacts-as-state, no checkpointer ([§2.4](02-architecture.md)) | `aidlc-docs/` artifacts persist context across sessions | ✅ Validated |
| Conversation/intent-first ([§1.6](01-overview-and-goals.md)) | "simple statement of intent" | ✅ Validated |
| Human decision gates ([§2.5](02-architecture.md)) | "implements only after human validation" | ✅ Validated |
| Phased SDD pipeline | Inception/Construction phases ≈ our intake→spec / build→review | ✅ Validated |

That a large AWS effort (with enterprise adopters) lands on the same primitives — markdown rules, multi-platform projection, artifacts-as-context, human gates — is meaningful evidence our low-code direction is sound, not a shortcut.

## 9.3 Takeaways to adopt (prioritized)

### T1 — Adaptive, complexity-scaled pipeline *(HIGH; addresses [§8.1 Q13](08-open-questions-and-roadmap.md))*
Our pipeline runs all 8 phases regardless of size — the original's rigidity, inherited. AI-DLC's "only execute stages that add value" is the fix. **Add a triage step at the front of `/sdd`** that classifies the request (trivial / standard / complex) and selects the phase set:
- *trivial* (e.g., "rename this field across the design") → intake-lite → spec, skip analysis/design/critique;
- *standard* → the full pipeline;
- *complex* (migration, multi-system) → full pipeline + Units-of-Work decomposition (T4).

This directly improves the **≥80%-across-use-cases** target, because the failure mode of a fixed pipeline is over-processing small requests and under-decomposing large ones. It also defuses the "one message triggers a long autonomous chain" concern from [§2.3](02-architecture.md).

### T2 — Verification sections per phase *(HIGH; cheapest control win; strengthens [doc 04](04-control-and-enforcement.md))*
AI-DLC rules carry **explicit Verification checklists the model must satisfy before progressing**, with rule IDs for traceability. This is a **middle tier between our "soft instruction" and "hard hooks"** — it raises the soft-enforcement floor with *zero code*. **Give each phase subagent a `## Verification` block**, e.g. for `spec`:
```
## Verification (must pass before proceeding) — rule SPEC-01..03
- [ ] SPEC-01: every acceptance criterion is verifiable
- [ ] SPEC-02: file structure + interfaces are complete
- [ ] SPEC-03: constraints ("do NOT build…") are explicit
```
The subagent self-checks and records pass/fail in the artifact. This is *exactly* the kind of structured self-discipline that lifts reliability before we ever pay for hooks — and when we do add hooks ([§4.4](04-control-and-enforcement.md)), they can assert the same rule IDs. Adopt now.

### T3 — Multi-platform rule projection *(HIGH; de-risks [doc 05](05-portability-and-distribution.md))*
We rated the Copilot/cross-IDE port at ~60–70% reuse and "must re-author." AI-DLC **proves the pattern works** and provides the exact mapping table (one markdown source → `CLAUDE.md`, `.cursor/rules/`, `.github/copilot-instructions.md`, `.kiro/steering/`, …). **Restructure so the methodology lives in tool-neutral markdown that *projects* into each platform's convention file**, rather than authoring `AGENTS.md` as Claude-shaped. This turns the portability "re-author" into a "re-project," materially raising cross-IDE reuse. Borrow their `core-workflow.md` + `*-rule-details/` layout.

### T4 — Units of Work decomposition for large requirements *(MEDIUM; scaling)*
For complex inputs, AI-DLC decomposes intent into **Units of Work** — cohesive, independently-valuable chunks — and processes each. Our pipeline treats a task as monolithic. **For `complex` requests (from T1), add a decomposition step** that splits the requirement into Units, then runs the design pipeline per Unit (a natural subagent fan-out). This is how the architect agent handles a multi-system migration without one giant, unfocused pass.

### T5 — Structured clarification in artifacts *(MEDIUM; precision + audit)*
AI-DLC captures clarification as **structured multiple-choice questions in files, not free chat**. Our intake clarification is free-form. **Have the `intake` subagent emit a `clarifications.md` with structured (ideally multiple-choice) questions**; answers are recorded back into the artifact. This sharpens requirements gathering and leaves an audit trail — and pairs well with our quality-gate scoring.

## 9.4 What NOT to adopt

- **The "Mob" rituals (Elaboration/Construction)** are inherently *multi-human, whole-team* ceremonies. Our tool is single-user, conversation-first — the underlying "AI proposes, human validates at checkpoints" is already our gate model; the team-ceremony framing is out of scope (revisit only for a future Cowork/team distribution).
- **The Operations phase** (IaC, deployment, monitoring) is outside our remit — we delegate *build*, we don't run ops.
- **The 10–15× productivity claims** are vendor figures tied to specific enterprise engagements; treat as directional marketing, not a design assumption.
- **Full-SDLC breadth** — AI-DLC spans the whole lifecycle; our agent is deliberately *architecture/design-centric*. Borrow mechanics, not scope.

## 9.5 Proposed doc changes (for review before applying)

These takeaways imply edits we should agree on first:
- [`docs/02`](02-architecture.md): add the **triage step** (T1) and **Units-of-Work decomposition** (T4) to the control flow; add **Verification blocks** (T2) to the node pattern.
- [`docs/04`](04-control-and-enforcement.md): insert **Verification sections as a "tier 1.5"** between soft instruction and hooks (T2).
- [`docs/05`](05-portability-and-distribution.md): adopt **rule projection** as the portability mechanism (T3), referencing the AI-DLC mapping.
- [`docs/08`](08-open-questions-and-roadmap.md): fold T1/T4 into the build sequence; close Q13 with the adaptive-pipeline answer.
- [`docs/07`](07-decisions.md): a new ADR-10 if we accept the adaptive pipeline + verification tiers as settled.

## Sources
- [AI-Driven Development Life Cycle: Reimagining Software Engineering — AWS DevOps Blog](https://aws.amazon.com/blogs/devops/ai-driven-development-life-cycle/)
- [Open-Sourcing Adaptive Workflows for AI-DLC — AWS DevOps Blog](https://aws.amazon.com/blogs/devops/open-sourcing-adaptive-workflows-for-ai-driven-development-life-cycle-ai-dlc/)
- [`awslabs/aidlc-workflows` (open-source rule files)](https://github.com/awslabs/aidlc-workflows)
- [Building with AI-DLC using Amazon Q Developer — AWS DevOps Blog](https://aws.amazon.com/blogs/devops/building-with-ai-dlc-using-amazon-q-developer/)
- [AWS re:Invent 2025 — Introducing AI-DLC (DVT214)](https://dev.to/kazuya_dev/aws-reinvent-2025-introducing-ai-driven-development-lifecycle-ai-dlc-dvt214-32b)
- [AI-DLC Flow Overview — specs.md](https://specs.md/aidlc/overview)
