---
name: score-requirements
description: Deterministic quality gate for the SDD intake phase. Given per-dimension scores (0-100), ratings, and blocking flags, returns the integer confidence (average), the gap list, the blocking-gap list, and a proceed/clarify decision. proceed is true only if confidence >= threshold AND there are no blocking gaps. Use in intake so the gate is exact arithmetic, not an LLM estimate.
---

# score-requirements

Keeps the SDD quality gate **deterministic**. The `intake` subagent decides the
*scores* and which gaps are *blocking* (it understands the domain); this skill
does only the *arithmetic and gate logic*, so a marginal pass is never an LLM
rounding error and the **hard-gap override** is applied consistently.

## When to use
In `intake`, after scoring the 6 dimensions, before deciding proceed-vs-clarify.

## Input (stdin JSON)
```json
{
  "threshold": 70,
  "dimensions": {
    "business_objectives":     {"score": 85, "rating": "clear",               "blocking": false},
    "acceptance_criteria":     {"score": 70, "rating": "needs_clarification", "blocking": false},
    "constraints_boundaries":  {"score": 80, "rating": "clear",               "blocking": false},
    "ambiguity_check":         {"score": 60, "rating": "needs_clarification", "blocking": false},
    "scope_definition":        {"score": 75, "rating": "clear",               "blocking": false},
    "dependencies_assumptions":{"score": 65, "rating": "needs_clarification", "blocking": true}
  }
}
```
- `rating` ∈ `clear | needs_clarification | missing`.
- `blocking: true` marks an unknown the **design phase cannot proceed without**
  (undefined external API/contract, unspecified integration target, missing
  system of record). The model sets this; the skill enforces its effect.

## Output (stdout JSON)
```json
{
  "confidence": 72,
  "threshold": 70,
  "meets_threshold": true,
  "gaps": ["acceptance_criteria", "ambiguity_check", "dependencies_assumptions"],
  "blocking_gaps": ["dependencies_assumptions"],
  "proceed": false,
  "reason": "blocking gap(s) present: dependencies_assumptions"
}
```

## Gate rule (the hard-gap override)
```
proceed = (confidence >= threshold) AND (no blocking gaps)
```
So a 72/100 with a blocking external-contract unknown returns `proceed: false`
→ intake stops at the clarification gate instead of designing on assumptions.

## Run
```
python skills/score-requirements/score.py < scores.json
```
Pure Python standard library — no dependencies.
