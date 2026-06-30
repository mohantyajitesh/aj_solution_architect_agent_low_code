---
name: memory-retrieve
description: Canonical index-first retrieval over the vectorless memory store. Read memory/INDEX.md, select the few relevant entries by tag/systems/summary (optionally grep), open only those, and optionally follow [[links]]. Never read the whole corpus. Used by every SDD phase so retrieval is consistent and cheap.
---

# memory-retrieve

The one way every phase retrieves memory. It guarantees **index-first** retrieval
(the affordability rule from [`docs/03` §3.3a](../../docs/03-memory-vectorless-rag.md)):
you read a compact index, select a few entries, then open only those — you never
load the whole corpus.

## When to use
Any phase that needs prior knowledge: `intake`, `analysis`, `design`,
`self_critique`, `spec`. Reuse-sensitive phases (`analysis`, `design`) must always
include `assets/` and `standards/` in the candidate set.

## Inputs (conceptual)
- `query` — the phase + key terms (e.g. "oracle hcm worker sync integration").
- `category` (optional) — restrict to `assets | standards | lessons | decisions | patterns`.
- `top_k` (optional, default ~5) — how many entries to open.

## Procedure
1. **Read `memory/INDEX.md`.** This is the entry point — one line per entry.
2. **Select candidates** by relevance to `query`: match on `tags`, `systems`, and the
   one-line summary. Reason about *conceptual* relevance, not just keyword overlap —
   this is where vectorless retrieval gets its "semantic-ish" matching.
3. **(Optional) Lexical pass.** `grep`/`ripgrep` over `memory/**` for exact terms the
   index might not surface (a system name, an error code).
4. **Open only the selected files** (cap at `top_k`). Do **not** open the whole corpus.
5. **(Optional) Follow `[[links]]`** from a strong hit to closely related entries.
6. **Return** the selected entries' content **and** a one-line note on *why* each was
   selected (transparency — the low-code analogue of a relevance score).

## Rules
- **Index-first, always.** Never `cat memory/**` or read every file to "find" something.
- **Reuse-first.** In `analysis`/`design`, always consider `assets/` candidates and
  surface any reusable/extensible system.
- **Authority.** Treat `authority: reference` entries (`assets`, `standards`) as
  constraints that outrank one-off experiential `lessons` on conflict.

## Scale note
Flat `INDEX.md` is fine into the low hundreds of entries. Past that, the
`memory-curator` derives a hierarchical/JSON index so step 1 stays cheap; this
procedure is unchanged — only the index it reads gets smarter. At thousands of
entries, a memory MCP (vector search) can sit behind this same interface without
changing any phase.
