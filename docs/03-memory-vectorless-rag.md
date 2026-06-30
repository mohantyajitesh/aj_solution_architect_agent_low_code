# 03 — Memory & Vectorless RAG

## 3.1 Decision

**No vector database. Memory is curated markdown, retrieved by the model's reasoning over a structured index plus lexical search.** This is the "vectorless RAG" pattern, and for this corpus it is not a compromise — it is the better fit.

## 3.2 Why vectorless is the right call here

### It is native to the substrate
Claude Code already performs retrieval over large codebases **without embeddings** — it greps, globs, reads files, and reasons about relevance. Memory-as-markdown + index + grep is therefore *the substrate's own retrieval model*, not a bolt-on. We work with the grain instead of against it.

### The corpus is small and curated
Memory is a single architect's accumulated `lessons` / `decisions` / `patterns` — tens to low-hundreds of entries, growing slowly, each deliberately written. The regime where vector search wins (thousands of documents, fuzzy semantic matching at scale) is far from where this corpus will ever sit.

### The properties we gain
- **Zero infrastructure** — no ChromaDB, no embedding model, no index server. Nothing to install, nothing to break, nothing to keep in sync.
- **Transparency** — you can see *why* a file was retrieved (it matched a tag / keyword / was selected from the index). Vector similarity is opaque by comparison.
- **Freshness** — no stale index, no re-embedding on edit. The markdown *is* the index's source and the retrieval target.
- **Portability** — plain files move anywhere; there is no index artifact to rebuild or migrate (see [`docs/05`](05-portability-and-distribution.md)).

### The cost we accept
- **No semantic fuzziness** — pure keyword/index retrieval can miss a conceptually-related entry that shares no terms. We mitigate this with **agentic retrieval** (the model reasons about relevance from summaries, not just keywords) and disciplined tagging.
- **Token/latency at scale** — agentic traversal reads files into context; at very large corpus sizes this grows. Bounded by curation (below) and re-examined only if the corpus explodes.

## 3.3 Retrieval techniques, layered

In increasing order of how much we lean on each:

1. **Index-first selection.** `memory/INDEX.md` holds one line per entry: title, category, tags, path, one-sentence summary. The model reads the index (cheap, one file) and selects candidates before opening anything.
2. **Lexical search.** `grep`/`ripgrep` over `memory/**` for exact-term matches — fast, deterministic, zero-cost.
3. **Agentic retrieval.** The model decides, from the index summaries, which entries are *conceptually* relevant to the current phase, then reads only those. This is where "semantic-ish" matching comes from — supplied by the reasoner, not by embeddings.
4. **Link traversal.** Entries cross-reference each other with `[[wikilink]]`-style references; the model follows links from a retrieved entry to related ones.

A single canonical retrieval procedure (`skills/memory-retrieve`) ensures every phase retrieves the same way: *read INDEX → select by tag/summary relevance → optionally grep → read selected files → optionally follow links.*

## 3.3a Token economics — retrieval is index-first, always

Vectorless retrieval is cheap **only if it never loads the whole corpus.** The cost is governed by the retrieval *pattern*, not the file format. There are two patterns, with very different cost curves:

| Pattern | Loaded per retrieval | Cost | Verdict |
|---|---|---|---|
| **Naive** ("read everything") | the entire corpus into context | O(total entries) | ❌ the expensive failure mode — **forbidden** |
| **Index-first** (this design) | one compact index → then only the ~3–5 selected entries | O(index) + O(k) | ✅ cheap and bounded |

**Index-first is mandatory, not optional.** The `memory-retrieve` skill must always (1) read a compact index, (2) select the few relevant entries, then (3) open only those. A phase must never `cat memory/**` or read all files to "find" something.

### The cost math

Assume an index line ≈ 30 tokens and a full entry ≈ 500 tokens; fetch ~4 entries per retrieval:

| Corpus | Flat index (Stage 1) | Fetch ~4 entries (Stage 2) | Total / retrieval |
|---|---|---|---|
| 30 entries | ~0.9k | ~2k | **~3k** — negligible |
| 300 entries | ~9k | ~2k | ~11k — noticeable |
| 2,000 entries | ~60k | ~2k | ~62k — expensive |

The cost that *grows* is **Stage 1 (reading the index)**, because a flat index is O(n). Stage 2 is always just the top few entries, so it stays flat regardless of corpus size.

### When to switch the index to a derived tree

The JSON/hierarchical tree is a **scale optimization for the index**, not a prerequisite for affordability. A *hierarchical* index (by category/branch) lets the model descend only the relevant branch instead of reading the whole index — turning Stage 1 from O(n) toward O(branch):

- 2,000 entries, flat index → ~60k tokens just to look
- 2,000 entries, descend one ~50-entry category → ~1.5k tokens

**Crossover thresholds (the recurring rule of thumb):**

| Corpus size | Index strategy |
|---|---|
| dozens | flat `INDEX.md` — tree saves nothing worth doing |
| hundreds | **curator-derived hierarchical index** (JSON or nested markdown) to keep Stage 1 lean |
| thousands | reconsider a **memory MCP** (vector search) behind the same `memory-retrieve` interface |

The curator-derived index is a **derived artifact** (markdown stays source of truth) — regenerated from front-matter, cheap to inspect, and a drop-in because the retrieval interface doesn't change.

### Three additional cost levers (mostly already in the design)

1. **Prompt caching** — the index is stable between edits, so after the first read it is nearly free to re-read within a session.
2. **Subagent isolation** — memory loads into the specific phase subagent that needs it, not dragged through the whole conversation, so retrieval cost does not compound across phases.
3. **Atomic entries** — one asset/lesson per file keeps each Stage-2 fetch lean (you pull one asset, not a 60-page document).

**Bottom line:** affordability comes from index-first retrieval (Stage 1 + Stage 2), which is mandatory here; the derived tree is what stops the *index itself* from getting fat once the corpus reaches the hundreds. You do not need the tree to be cheap today — you need to never read the whole corpus.

## 3.4 Memory layout

```
memory/
├── INDEX.md                    # maintained table of contents (the retrieval entry point)
├── lessons/
│   └── 2026-06-29_task-ab12_lesson-provider-abstraction.md
├── decisions/
│   └── 2026-06-29_task-ab12_adr-vectorless-memory.md
└── patterns/
    └── 2026-06-29_task-ab12_pattern-event-driven-integration.md
```

### Entry format (with front-matter for filtering)
```markdown
---
title: Provider abstraction saves time on LLM swaps
category: lessons
tags: [architecture, abstraction, providers, refactoring]
task_id: task-ab12
created: 2026-06-29
links: [[adr-vectorless-memory]]
---

# Provider abstraction saves time on LLM swaps

<body — 2–5 paragraphs>
```

Front-matter `tags` + `links` are what make lexical and traversal retrieval effective without vectors. Filenames keep the original convention (`YYYY-MM-DD_task-id_category-slug.md`) so they remain human-scannable and sortable.

### `INDEX.md` shape
```markdown
# Memory Index

## Lessons
- **Provider abstraction saves time on LLM swaps** — `lessons/2026-06-29_task-ab12_lesson-provider-abstraction.md`
  tags: architecture, abstraction · When swapping LLMs, an interface layer pays for itself.

## Decisions
- **Vectorless memory over ChromaDB** — `decisions/2026-06-29_task-ab12_adr-vectorless-memory.md`
  tags: memory, retrieval · For small curated corpora, files+index beat a vector DB.

## Patterns
- ...
```

## 3.5 Keeping retrieval sharp: the `memory-curator` subagent

Vectorless retrieval degrades only if the corpus becomes large, untagged, or redundant. The `memory-curator` subagent is the antidote and runs after `learn` (and on demand):

- **regenerates `INDEX.md`** from front-matter,
- **normalizes tags** (merges synonyms, enforces a controlled vocabulary),
- **adds `[[links]]`** between related entries,
- **flags duplicates / near-duplicates** for merge,
- **summarizes** long entries into the index line.

This converts "curation discipline" from a hope into an automated housekeeping step — the single most important investment for making vectorless memory hold up over time.

## 3.6 Write lifecycle (propose → approve → curate)

1. `learn` subagent proposes 1–3 entries (category, title, content, tags) — **does not write**.
2. **Human gate**: user approves / edits / discards.
3. On approval, entries are written as markdown files (next sequence number per task/category).
4. `memory-curator` updates `INDEX.md` and links.
5. `git commit` (optionally `push`) captures the new knowledge — versioned and shareable.

This mirrors the original's propose/approve lifecycle but removes the reindex-into-ChromaDB step entirely; "reindex" is now just "regenerate `INDEX.md`," a markdown operation.

## 3.7 When we would revisit vectors

Re-introduce embeddings **only if** all of these become true:
- corpus grows past the low-hundreds into thousands of entries, **and**
- retrieval starts missing relevant entries that lack shared keywords, **and**
- agentic traversal cost/latency becomes noticeable in practice.

At that point a **memory MCP** (vector search behind the same `memory-retrieve` interface) is the clean upgrade — the phases would not change, only the retrieval implementation behind the skill. Designing the retrieval call as a stable interface now keeps that door open. This is explicitly **deferred**, not designed-in.
