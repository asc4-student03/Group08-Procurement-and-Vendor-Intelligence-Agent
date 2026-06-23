## Context

Procurement requests are currently reviewed manually, which creates latency and inconsistency for low-risk, high-volume purchases. This change introduces a structured recommendation agent that evaluates each request against budget, vendor, policy, and risk dimensions and returns one of three advisory outcomes: `approve`, `deny`, or `escalate`.

The solution must follow project constraints:
- Python 3.11+ with type hints and Pydantic v2 models.
- `pydantic-ai` agent with `output_type=ProcurementRecommendation`.
- Mock data read only through `data/loader.py`.
- All four tools executed for each request.
- Tool failures surfaced in rationale with safe handling.

Stakeholders include procurement officers (primary users), legal/compliance reviewers (escalation path), and engineering/test reviewers (quality gates).

## Goals / Non-Goals

**Goals:**
- Define a deterministic decision framework with strict priority `escalate > deny > approve`.
- Standardize request and recommendation schemas for reliable validation.
- Encapsulate domain checks in four focused tools with stable output contracts.
- Ensure the final recommendation includes a non-empty, evidence-based rationale.
- Preserve explainability by requiring policy IDs, budget context, and risk cues in rationale.

**Non-Goals:**
- Replacing procurement officer authority with autonomous approval execution.
- Introducing live enterprise integrations or non-mock data sources.
- Building a workflow engine for manager/director sign-off persistence.
- Redesigning policy catalogs beyond what is needed for recommendation behavior.
- Building deployment pipelines, UI surfaces, authentication flows, or persistent storage.

## Decisions

1. Use layered architecture: models, data access, tools, then agent orchestration.
- Rationale: Keeps decision logic composable and testable at tool/unit level and at full-agent level.
- Alternative considered: monolithic agent prompt with inline policy text and no tool modules.
- Why not: lower testability, weak error isolation, and less deterministic behavior.

2. Enforce typed contracts with Pydantic v2 models for both input and output.
- Rationale: Prevents malformed requests and guarantees output shape/allowed decision values.
- Alternative considered: ad hoc dict-based inputs/outputs.
- Why not: weaker validation and increased runtime ambiguity.

3. Route all dataset access through `data/loader.py`.
- Rationale: centralizes file resolution and prevents direct coupling to `mock_data/` paths.
- Alternative considered: each tool reads JSON files directly.
- Why not: duplication, inconsistency, and violation of project conventions.

4. Execute all four tools for every request.
- Rationale: supports complete rationale composition and avoids silent omission of important checks.
- Alternative considered: short-circuit after first hard violation.
- Why not: partial evidence and weaker auditability for procurement officers.

Tool selection logic:
- Always call `check_budget`, `check_vendor_duplication`, `check_policy_compliance`, and `assess_risk` for each request.
- Aggregate all tool outputs before applying final recommendation precedence.
- Do not skip checks even when an early deny/escalate trigger appears.

5. Apply explicit decision precedence (`escalate > deny > approve`).
- Rationale: protects governance-sensitive scenarios where escalation should override direct denial/approval.
- Alternative considered: deny-first precedence.
- Why not: may bypass required legal/compliance review when escalation conditions apply.

6. Treat tool/data errors as escalation triggers and require error mention in rationale.
- Rationale: safe-fail behavior with transparent uncertainty signaling.
- Alternative considered: default deny or silent fallback.
- Why not: silent fallback is unsafe; default deny can be overly punitive without context.

Fallback path:
- Any tool payload containing an `error` key forces final decision to `escalate`.
- Rationale must explicitly name the failed tool context and why uncertainty requires escalation.

## Risks / Trade-offs

- [Risk] Prompt-level interpretation may drift from intended precedence. -> Mitigation: encode precedence in system prompt and verify with targeted tests (approve/deny/escalate/edge cases).
- [Risk] Policy overlap can produce multiple simultaneous triggers and rationale bloat. -> Mitigation: define concise rationale format with specific policy IDs and key numbers only.
- [Risk] Mock data shape drift could break tools. -> Mitigation: loader-level checks, tool-level error handling, and escalation fallback.
- [Risk] Ambiguous scenarios (for example near-threshold or tight-budget no-policy-violation) may produce variable recommendations. -> Mitigation: document ambiguity explicitly and add test fixtures that pin expected behavior where required.
- [Risk] Strict always-run-all-tools increases latency relative to short-circuiting. -> Mitigation: acceptable for mock-data scope; revisit only if scale/performance constraints change.

## Implementation Sequence

1. Introduce/confirm model contracts and validation behavior.
2. Implement or align data loader interfaces.
3. Implement or align the four tool contracts and error keys.
4. Wire agent with `output_type=ProcurementRecommendation` and all tool calls.
5. Enforce precedence (`escalate > deny > approve`) and error fallback behavior.
6. Add/refresh tests for tools and end-to-end recommendation outcomes.
7. Validate OpenSpec artifacts and run required test commands.

## Open Questions

- Should near-director-threshold escalation be governed solely by policy compliance output, or also by budget-check context independent of policy output?
- For unknown vendor IDs, should policy compliance also emit explicit violations, or is risk escalation plus error context sufficient?
- How strict should rationale length/format enforcement be (minimum sentence count versus semantic content checks)?
