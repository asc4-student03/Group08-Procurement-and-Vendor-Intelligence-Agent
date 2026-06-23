## Context

The project needs a deterministic pre-screening layer for procurement requests that returns a structured recommendation before human review. Current domain data exists as mock fixtures accessed through loader functions, and project conventions require tools to consume loader APIs rather than reading fixture files directly. The design must preserve a strict recommendation contract, enforce a fixed decision priority, and surface all tool/data failures in recommendation rationale.

## Goals / Non-Goals

**Goals:**
- Define an agent architecture that always produces structured output constrained to approve, deny, or escalate.
- Ensure every request evaluation runs all four domain checks: budget, vendor duplication, policy compliance, and risk.
- Enforce decision precedence as escalate over deny over approve.
- Ensure tool failures are captured and reflected in rationale, with fail-safe escalation.
- Keep domain data access centralized through data loader functions.

**Non-Goals:**
- Replacing human procurement approval authority.
- Building UI or workflow orchestration beyond recommendation generation.
- Introducing live external systems or real-time integrations in this change.

## Decisions

1. Use Pydantic AI agent with typed output contract.
- Decision: Construct the main agent with a typed output model for recommendation.
- Rationale: Guarantees structured output and prevents free-form responses that violate decision schema.
- Alternative considered: Prompt-only JSON formatting; rejected because it is less reliable than schema-constrained output.

2. Use Pydantic v2 models for both request and recommendation contracts.
- Decision: Model input and output entities with validation constraints, including a non-empty rationale and enumerated decision values.
- Rationale: Enforces domain correctness at system boundaries and reduces downstream handling ambiguity.
- Alternative considered: Untyped dictionaries; rejected due to weak validation and auditability.

3. Execute all four tools for every request.
- Decision: No short-circuiting after first failure or violation.
- Rationale: Procurement reviewers need complete context in rationale, not a partial check result.
- Alternative considered: Early exit on first deny/escalate trigger; rejected because it weakens explanatory completeness.

4. Apply deterministic decision resolver with explicit precedence.
- Decision: Resolve final recommendation via precedence graph escalate > deny > approve.
- Rationale: Prevents inconsistent outcomes when multiple checks trigger conflicting signals.
- Alternative considered: Weighted scoring; rejected because it obscures policy intent and is harder to audit.

5. Adopt fail-safe error handling.
- Decision: Any tool/data error becomes an escalation signal and must appear in rationale text.
- Rationale: Missing evidence should never silently produce approve or deny outcomes.
- Alternative considered: Ignore unavailable checks; rejected as unsafe for compliance-sensitive decisions.

6. Restrict data access through loader APIs.
- Decision: Tools must call data loader functions as sole data access point.
- Rationale: Centralizes file-path assumptions and supports controlled data evolution.
- Alternative considered: Direct fixture reads in each tool; rejected due to duplicated logic and higher drift risk.

## Risks / Trade-offs

- Risk: Conflicting tool outputs may still create borderline interpretation cases. -> Mitigation: enforce deterministic precedence and include explicit rationale requirements.
- Risk: Fixture schema drift can break tool assumptions. -> Mitigation: validate fields at loader/model boundaries and treat failures as escalation.
- Risk: Strict escalation on errors may increase manual review load. -> Mitigation: keep error messages specific so reviewers can quickly triage root causes.
- Trade-off: Running all checks increases compute per request. -> Mitigation: accepted because completeness and audit quality are higher priority than minimal latency in this phase.

## Migration Plan

- Introduce models, tools, and agent construction in repository-aligned modules.
- Validate behavior with simulated-data tests for approve, deny, and escalate paths.
- Rollback strategy: revert to prior manual recommendation flow if structured agent path is unstable.

## Open Questions

- Should near-threshold director escalation rules be encoded as policy-derived configuration or fixed logic?
- What minimum rationale template should be standardized for audit consistency across all outcomes?
- Should ambiguous no-violation cases with low remaining budget default to approve or escalate?
