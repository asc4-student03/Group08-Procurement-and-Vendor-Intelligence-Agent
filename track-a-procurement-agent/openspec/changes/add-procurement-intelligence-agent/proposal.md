## Why

Purchase request pre-screening is currently manual and inconsistent, which can delay decisions and increase policy and budget risk. We need a deterministic, structured recommendation flow now so reviewers receive fast and auditable approve, deny, or escalate guidance before human approval.

## What Changes

- Add a procurement intelligence agent that pre-screens purchase requests and returns a structured recommendation with a required non-empty rationale.
- Constrain recommendation decisions to approve, deny, or escalate.
- Use Pydantic v2 models for validated request input and structured output contracts.
- Route all data access through data/loader.py and prohibit direct reads from mock_data in agent and tools.
- Integrate four domain checks from tools/: budget, vendor duplication, policy compliance, and risk assessment.
- Define deterministic recommendation precedence as escalate over deny over approve.
- Capture tool execution errors in the recommendation rationale instead of failing silently.

## Capabilities

### New Capabilities
- procurement-intelligence-agent: Validate purchase requests against budgets, vendor and policy controls, and risk signals to produce a typed approve, deny, or escalate recommendation with rationale.

### Modified Capabilities
- None.

## Impact

- Affected code:
  - solutions/agent.py
  - solutions/models.py
  - solutions/tools/budget.py
  - solutions/tools/vendor_duplication.py
  - solutions/tools/policy_compliance.py
  - solutions/tools/risk_assessment.py
  - solutions/data/loader.py
  - solutions/tests/test_agent.py
  - solutions/tests/test_budget.py
  - solutions/tests/test_vendor_duplication.py
  - solutions/tests/test_policy_compliance.py
  - solutions/tests/test_risk_assessment.py
- APIs and contracts:
  - Structured output contract for recommendations constrained to approve, deny, escalate with non-empty rationale.
  - Tool result contracts consumed by the agent decision policy.
- Dependencies and systems:
  - Pydantic AI agent construction with output_type set to ProcurementRecommendation.
  - Pydantic v2 validation for input and output data models.
  - Mock data loading constrained to data/loader.py.
