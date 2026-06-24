## Context

The main spec for risk assessment exists, but the root tool module is not present. The tool must return a consistent structured payload and conservative behavior for unknown or unavailable data.

## Goals / Non-Goals

**Goals:**
- Implement the `assess_risk` contract exactly as specified.
- Map vendor attributes deterministically to `low|medium|high|critical`.
- Return explicit `error` output for unknown vendor and data-unavailable cases.

**Non-Goals:**
- Agent orchestration logic.
- Policy check logic beyond risk summary.

## Decisions

- Load vendor data via `data.loader.load_vendors` only.
- Compute risk levels in strict order: compliance flag, expired contract, no contract, active clean.
- Treat unknown or unavailable data as escalation-safe by returning `error` with conservative risk level.

## Risks / Trade-offs

- [Risk] Vendor dataset shape drift could break lookups. -> Mitigation: use defensive field access and explicit error output.
- [Risk] Ambiguous unknown-vendor severity. -> Mitigation: use conservative `critical` for unknown/unavailable data.
