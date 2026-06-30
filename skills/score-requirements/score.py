#!/usr/bin/env python3
"""Deterministic requirements quality gate for the SDD intake phase.

Reads a JSON object on stdin describing the 6 scored dimensions and writes a
JSON verdict on stdout. The model supplies scores/ratings/blocking flags; this
script only does the arithmetic and the gate logic, so the decision is exact
and the hard-gap override is applied consistently.

    proceed == (confidence >= threshold) AND (no blocking gaps)

Usage:
    python score.py < scores.json
"""

import json
import sys

GAP_RATINGS = {"needs_clarification", "missing"}


def evaluate(payload: dict) -> dict:
    """Compute the gate verdict from a scored-dimensions payload."""
    threshold = int(payload.get("threshold", 70))
    dims = payload.get("dimensions", {})
    if not dims:
        return {"error": "no dimensions provided"}

    scores = [int(d.get("score", 0)) for d in dims.values()]
    confidence = round(sum(scores) / len(scores))

    gaps = [name for name, d in dims.items() if d.get("rating") in GAP_RATINGS]
    blocking_gaps = [name for name, d in dims.items() if d.get("blocking") is True]

    meets_threshold = confidence >= threshold
    proceed = meets_threshold and not blocking_gaps

    if proceed:
        reason = f"confidence {confidence} >= {threshold} and no blocking gaps"
    elif not meets_threshold and blocking_gaps:
        reason = (
            f"confidence {confidence} < {threshold} and "
            f"blocking gap(s): {', '.join(blocking_gaps)}"
        )
    elif not meets_threshold:
        reason = f"confidence {confidence} < {threshold}"
    else:
        reason = f"blocking gap(s) present: {', '.join(blocking_gaps)}"

    return {
        "confidence": confidence,
        "threshold": threshold,
        "meets_threshold": meets_threshold,
        "gaps": gaps,
        "blocking_gaps": blocking_gaps,
        "proceed": proceed,
        "reason": reason,
    }


def main() -> None:
    try:
        payload = json.load(sys.stdin)
    except json.JSONDecodeError as exc:
        print(json.dumps({"error": f"invalid JSON on stdin: {exc}"}))
        sys.exit(1)
    print(json.dumps(evaluate(payload), indent=2))


if __name__ == "__main__":
    main()
