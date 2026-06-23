## Context

The repository contains procurement domain mock data and tool modules for budget, policy, vendor, and risk checks, but lacks a single typed agent contract that orchestrates these checks into a consistent recommendation output. The change must follow project constraints: Python 3.11+, Pydantic v2 models, Pydantic AI output_type for structured results, data access via data/loader.py, and recommendation decisions constrained to approve, deny, or escalate with non-empty rationale.

## Goals / Non-Goals

**Goals:**
- Introduce an agent orchestration flow that accepts a validated PurchaseRequest model and returns a validated ProcurementRecommendation model.
- Enforce deterministic decision precedence as escalate over deny over approve based on combined tool outcomes.
- Integrate and invoke four checks: budget, vendor duplication, policy compliance, and risk assessment.
- Ensure tool failures are surfaced in rationale text, avoiding silent failures.
- Keep data access centralized through data/loader.py for both runtime and tests.

**Non-Goals:**
- Replacing existing domain datasets or editing files under mock_data.
- Introducing live external integrations or network calls.
- Building a UI or workflow engine beyond recommendation generation.
- Redefining organizational policies outside their encoded interpretation in this change.

## Decisions

- Decision: Use Pydantic AI Agent with output_type set to ProcurementRecommendation.
  - Rationale: Enforces structured output at generation time and aligns with repository conventions.
  - Alternatives considered:
    - Returning raw dictionaries and validating after inference: rejected due to weaker output guarantees.
    - Using deprecated result_type: rejected because current guidance requires output_type.

- Decision: Validate request and recommendation payloads using Pydantic v2 models in solutions/models.py.
  - Rationale: Strong runtime validation and explicit schema documentation for tests and tool boundaries.
  - Alternatives considered:
    - Unstructured dataclasses: rejected due to weaker validation semantics.

- Decision: Implement a centralized decision combiner that consumes check outcomes and applies precedence escalate > deny > approve.
  - Rationale: Deterministic, testable decisioning and clear policy conflict handling.
  - Alternatives considered:
    - Sequential first-failure short-circuiting: rejected because it can mask escalation signals.
    - Weighted scoring model: rejected as unnecessary complexity for current policy set.

- Decision: Standardize tool response interpretation into status flags and evidence snippets used to build rationale.
  - Rationale: Ensures explainable outcomes and consistent rationale formatting.
  - Alternatives considered:
    - Free-form tool messaging only: rejected due to inconsistent downstream reasoning.

- Decision: Catch tool exceptions individually and append error context into rationale while continuing safe evaluation where possible.
  - Rationale: Meets requirement to reflect tool errors and improves resilience.
  - Alternatives considered:
    - Hard-failing the full agent on any tool error: rejected due to reduced operational utility.

- Decision: Enforce data reads through solutions/data/loader.py in all tool and agent paths.
  - Rationale: Preserves testability and adherence to repository guardrails.
  - Alternatives considered:
    - Direct JSON file reads inside tools: rejected by project convention.

## Risks / Trade-offs

- Risk: Conflicting policy interpretations can produce ambiguous outcomes. -> Mitigation: Codify explicit precedence and document tie-break behavior in tests.
- Risk: Tool error accumulation may yield long rationale strings. -> Mitigation: Use concise, structured rationale segments while preserving required error details.
- Risk: Existing tool return formats may vary. -> Mitigation: Add adapter logic and contract-focused tests per tool.
- Risk: Mock data edge cases may evolve. -> Mitigation: Keep test fixtures and scenarios aligned with domain rules via targeted regression tests.

## Migration Plan

- Implement and validate models and agent orchestration in solutions.
- Integrate four tool calls and decision combiner logic.
- Add/adjust tests for success paths, precedence behavior, and error propagation.
- Run test suite with recorded results for review.
- Rollback: revert change set to previous baseline if behavior diverges; no data migration required because storage schemas are unchanged.

## Open Questions

- Should an over-budget request near director threshold always deny or may escalate for review in exceptional cases?
- Should any tool execution error force escalate, or only appear in rationale while preserving computed decision?
- What minimum rationale content granularity is required for audit acceptance across teams?
