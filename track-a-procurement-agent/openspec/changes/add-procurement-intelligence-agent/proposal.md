## Why

Procurement review decisions are currently manual and inconsistent, which slows request processing and creates audit risk when rationale quality varies. We need a deterministic pre-screening agent now so procurement officers receive consistent approve, deny, or escalate recommendations grounded in policy, budget, vendor, and risk checks.

## What Changes

- Add a Procurement Intelligence Agent built with Pydantic AI that evaluates each purchase request and returns structured output.
- Introduce strict structured models for request input and recommendation output using Pydantic v2, including constrained decision values of approve, deny, or escalate and non-empty rationale.
- Require all request evaluation to call four domain tools: budget check, vendor duplication check, policy compliance check, and risk assessment.
- Define and enforce recommendation precedence as escalate over deny over approve.
- Require tool failures and data-access errors to be surfaced in rationale and drive escalation instead of silent failure.
- Standardize data access through data loader functions and prohibit direct reads from mock_data in tool logic.

## Capabilities

### New Capabilities
- procurement-intelligence-agent: Pre-screen purchase requests using four checks and return a structured recommendation with policy-aware rationale and deterministic decision priority.

### Modified Capabilities
- None.

## Impact

- Affected code: agent construction, structured models, data loading path, and all four procurement tool interfaces.
- Affected behavior: procurement officers receive standardized recommendation objects instead of ad hoc narrative outcomes.
- Compliance impact: stronger traceability through explicit rationale content and explicit handling of tool/data errors.
- Dependency impact: formal use of Pydantic AI and Pydantic v2 model contracts for request and recommendation validation.
