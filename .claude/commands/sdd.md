---
description: Start (or resume) a Spec-Driven Development task with the Architect Agent
argument-hint: "<requirement text, or a path to a requirements file>"
---

You are the **Architect Agent orchestrator**. Follow `AGENTS.md` exactly.

The user's requirement (or a file path to it) is:

$ARGUMENTS

## Do this now

1. **Create/resume the task.** If `$ARGUMENTS` references an existing `workspace/<task-id>/`, resume from the highest artifact present. Otherwise create a new `workspace/<task-id>/` (short id) and save the raw requirement to `requirements_input.md`.

2. **Load context.**
   - Read the **organizational constraints** (`AGENTS.md` §8) — these are always-on.
   - **Retrieve memory index-first:** read `memory/INDEX.md`, select relevant entries by tag/`systems`/summary, open only those. Pay special attention to `memory/assets/` (reuse-first) and `memory/standards/` (constraints).

3. **Triage (AGENTS.md §4).** Classify the request as **trivial / standard / complex** and choose the phase set. If **complex**, decompose into Units of Work first.

4. **State your plan to the user** before doing the work:
   - the chosen complexity and why,
   - the exact phases you will run (and any you are skipping, and why),
   - any existing **assets** you expect to reuse/extend,
   - the **Verification** checks each phase will have to pass.

5. **Run the pipeline** per `AGENTS.md` §4–§6, writing each artifact to `workspace/<task-id>/`, ending each phase with its `## Verification` block, and **stopping at every gate** (clarification, spec approval, memory approval) to wait for the user.

Begin with step 1.
