---
title: HCM System Service (MuleSoft) — Oracle HCM → downstream sync
category: assets
source: human
authority: reference
status: in-production
systems: [oracle-hcm, atom-feed, bi-publisher, xyz-api, sql-server, mulesoft]
tags: [integration, hcm, worker-data, event-driven, polling, reuse-candidate]
links: [[mulesoft-flow-naming]]
owner: <team / person responsible>      # human owner for freshness
last_reviewed: 2026-06-29
---

# HCM System Service (MuleSoft)

> Capability catalog entry. The agent should consult this during **analysis** and
> **design** and prefer **reusing or extending** this service over designing a new
> Oracle HCM integration. See the "When to USE / When NOT to use" sections.

## What it does (capability)
Production MuleSoft application that keeps downstream systems in sync with
**Oracle HCM worker (person) data**, event-driven. It reacts to HCM change
events, fetches the full record, and hands it to a downstream API for
persistence.

## Flow
1. **Polls Oracle HCM ATOM feeds** for change events.
2. Extracts the **`person_id`** from each ATOM event.
3. Pulls the full worker record via a **BI Publisher report** (keyed on `person_id`).
4. **POSTs** the record to **XYZ API**.
5. XYZ API persists the record in **ABC format** to a **SQL Server** database.

```
Oracle HCM ATOM feed ──(poll)──▶ HCM System Service (MuleSoft)
        │ person_id                      │
        ▼                                ▼
   BI Publisher report ──record──▶ POST XYZ API ──▶ SQL Server (ABC format)
```

## Interfaces
- **In (source):** Oracle HCM ATOM feed — polling cadence `<interval>`.
- **In (enrichment):** BI Publisher report `<report name / path>`, keyed on `person_id`.
- **Out:** `POST` to XYZ API `<endpoint>`.
- **Persistence:** SQL Server `<db>.<schema>.<table>`, stored in **ABC format**.
- **Data contract (ABC format):** see [`samples/hcm-abc-sample.json`](samples/hcm-abc-sample.json) — **dummy data**.

## When to USE this
- Any requirement that needs **Oracle HCM worker/person data** moved downstream.
- **Change-driven / near-real-time** sync (one record per change event).
- Target can consume the **ABC format**, or can sit behind / be reached from XYZ API.

## When NOT to use this
- **Bulk or initial historical loads** — this is event-driven, one record per event.
- HCM objects the **BI Publisher report does not cover** (non-worker entities, custom fields not in the report).
- **Sub-second latency** needs — the ATOM polling cadence is the floor.

## Reuse / extension notes
- **New downstream target?** Prefer adding a route/consumer off **XYZ API** rather than building a second poller against Oracle HCM.
- **New fields needed?** Extend the **BI Publisher report**, not the MuleSoft flow.
- **Different source object?** Confirm ATOM feed + BI Publisher coverage before assuming reuse.

## Open items to confirm (fill in for production accuracy)
- Exact ATOM feed name(s) and polling interval.
- BI Publisher report identifier and its field coverage.
- XYZ API endpoint, auth, and idempotency behavior.
- SQL Server target table and the authoritative ABC schema.
