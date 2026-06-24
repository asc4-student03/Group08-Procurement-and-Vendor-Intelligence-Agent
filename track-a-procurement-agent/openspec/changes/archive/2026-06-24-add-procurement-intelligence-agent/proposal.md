## Why

FedEx procurement teams handle high request volume, and manual pre-screening consumes time that should be spent on complex decisions. A structured intelligence agent is needed now to provide consistent pre-screen recommendations with clear rationale while preserving human final approval.

## What Changes

- Add a Pydantic AI procurement agent that evaluates purchase requests and returns a structured recommendation.
- Enforce typed input and output contracts with Pydantic v2 models:
  - `PurchaseRequest` input model.
  - `ProcurementRecommendation` output model with decision constrained to `approve`, `deny`, or `escalate`.
- Add and integrate four procurement checks as callable tools:
  - `check_budget`
  - `check_vendor_duplication`
  - `check_policy_compliance`
  - `assess_risk`
- Require that mock reference data is accessed only through `data/loader.py` (no direct reads from `mock_data/` in tools or agent logic).
- Define and enforce recommendation priority rules: `escalate > deny > approve`.
- Require tool failures to be surfaced in the recommendation rationale and handled safely.
- Keep scope limited to capstone requirements only (no deployment pipeline changes, no UI work, no authentication work, no persistent storage additions).

## Capabilities

### New Capabilities
- `procurement-model-contracts`: Defines validated request and recommendation schemas, including allowed decision values and non-empty rationale.
- `procurement-data-access`: Defines centralized mock-data access behavior through `data/loader.py` for budgets, policies, vendors, and requests.
- `budget-check-tool`: Defines `check_budget` input/output/error contract and POL-008-aligned overage semantics.
- `vendor-duplication-tool`: Defines `check_vendor_duplication` input/output/error contract and POL-001 threshold behavior.
- `policy-compliance-tool`: Defines `check_policy_compliance` full-policy evaluation contract and violation-severity outputs.
- `risk-assessment-tool`: Defines `assess_risk` risk-profile contract and risk-level mapping semantics.
- `procurement-decision-agent`: Defines agent orchestration, check execution requirements, decision-priority logic, and error-aware rationale composition.

### Modified Capabilities
- None.

## Risks

- Ambiguous edge cases (for example near-threshold amounts) can produce inconsistent recommendations unless precedence rules are explicit.
- Tool output contract drift can cause incorrect decision aggregation unless output keys are fully specified in specs.
- Missing or malformed mock data can break deterministic behavior unless error-to-escalation fallback is enforced.

## Impact

- Affected code:
  - `agent.py`
  - `models.py`
  - `data/loader.py`
  - `tools/budget.py`
  - `tools/vendor_duplication.py`
  - `tools/policy_compliance.py`
  - `tools/risk_assessment.py`
  - `tests/` coverage for models, tools, and agent behavior
- APIs/contracts:
  - Structured recommendation contract is formalized and constrained.
  - Tool return payloads become decision-critical interfaces.
- Dependencies/systems:
  - Uses `pydantic-ai` for agent construction and orchestration.
  - Uses Pydantic v2 validation for all structured input/output models.
  - Uses repository mock datasets via loader abstraction only.
