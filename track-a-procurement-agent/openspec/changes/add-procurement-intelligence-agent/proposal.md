## Why

FedEx procurement teams need a consistent pre-screening step that applies budget, vendor, and policy checks before manual review. This change introduces a structured AI recommendation flow now so Sessions 2 and 3 can implement and validate deterministic approve, deny, or escalate outcomes.

This capstone change is intentionally limited to domain validation, tool orchestration, and recommendation quality. It excludes deployment, UI work, authentication changes, and persistent storage design.

## What Changes

- Add a procurement intelligence agent using Pydantic AI with structured output constrained to a Pydantic v2 `ProcurementRecommendation` model.
- Define and enforce request input validation with a Pydantic v2 `PurchaseRequest` model.
- Require the agent to produce only `approve`, `deny`, or `escalate` decisions with a non-empty rationale.
- Integrate four tool checks in the recommendation flow: budget, vendor duplication, policy compliance, and risk assessment.
- Enforce decision priority resolution of `escalate > deny > approve` when multiple tool signals apply.
- Require tool failures to be caught and surfaced in the rationale rather than silently ignored.
- Require mock-domain data access to flow through `data/loader.py` only, not direct reads from `mock_data/`.
- Keep implementation scope limited to Python models, data loader usage, tool contracts, and agent wiring under `solutions/`.

## Capabilities

### New Capabilities
- `procurement-intelligence-agent`: Pre-screen purchase requests using validated inputs, tool-driven policy checks, and structured recommendation outputs.
- `budget-tool`: Evaluate cost center budget sufficiency and return structured deny/approve signals with overage details.
- `vendor-duplication-tool`: Evaluate active-contract duplication conflicts by vendor and category with POL-001 deny-threshold awareness.
- `policy-compliance-tool`: Evaluate purchase requests against all eight policies and emit structured violation records with forced decisions.
- `risk-assessment-tool`: Produce vendor risk profile with compliance status, contract status, and computed risk level.

### Modified Capabilities
- None.

## Impact

- Affected code:
  - `solutions/agent.py` for agent orchestration and decision synthesis.
  - `solutions/models.py` for request/recommendation schema contracts.
  - `solutions/tools/budget.py`, `solutions/tools/vendor_duplication.py`, `solutions/tools/policy_compliance.py`, and `solutions/tools/risk_assessment.py` for integrated checks.
  - `solutions/data/loader.py` as the sole data access path.
- Tests:
  - `solutions/tests/` expanded to cover primary success paths and outcome-priority behavior.
- Runtime/dependencies:
  - Uses existing `pydantic-ai` and Pydantic v2 setup; no new external runtime dependencies required.
- Operational behavior:
  - Recommendation output contract is standardized for downstream review workflows.

## Risks

- Sample fixtures include ambiguous and near-threshold cases that can cause decision drift unless precedence is enforced consistently.
- Missing or inconsistent tool return shapes could undermine deterministic final-decision synthesis.
- Tool exceptions could hide critical context unless error details are always included in rationale output.