---
title: MuleSoft flow naming convention
category: standards
source: human
authority: reference
status: in-production
systems: [mulesoft]
tags: [mulesoft, naming, integration, standards]
links: [[hcm-system-service]]
owner: <integration platform team>
last_reviewed: 2026-06-29
---

# MuleSoft flow naming convention

> Reference standard. The agent must honor this as a **constraint** when proposing
> or extending MuleSoft integrations.

## Rule
Name flows `<source>-to-<target>-<entity>`, lowercase, hyphen-separated.

- `icims-to-oracle-worker`
- `oracle-hcm-to-sqlserver-worker`
- `<source>-to-<target>-<entity>`

## Sub-flows
Sub-flows are named `<parent-flow>__<step>`, e.g. `oracle-hcm-to-sqlserver-worker__enrich-bip`.

## Rationale
Predictable names make flows greppable, make the integration landscape self-documenting,
and let reuse analysis (see [[hcm-system-service]]) match existing flows by source/target/entity.

## When this applies
- Any new MuleSoft flow or sub-flow.
- Renaming during refactors.

## Exceptions
- Legacy flows predating this standard are renamed opportunistically, not urgently.
