## Context

The project needs a deterministic pre-screening workflow for procurement requests that mirrors domain policies in mock data while preserving a strict structured-output contract. Current mock data shows budget, vendor, and policy outcomes that must map to recommendation decisions and rationale text. Project conventions require Python 3.11+, Pydantic v2 models, and Pydantic AI `output_type` usage, with data access routed through `data/loader.py` rather than direct `mock_data/` reads.

## Goals / Non-Goals

**Goals:**
- Implement a single recommendation pipeline that validates `PurchaseRequest` input and returns a typed `ProcurementRecommendation` output.
- Orchestrate four tool checks (`check_budget`, `check_vendor_duplication`, `check_policy_compliance`, `assess_risk`) for every request evaluation.
- Enforce final-decision priority `escalate > deny > approve` when tool outcomes conflict.
- Ensure recommendation rationale is always non-empty and includes surfaced tool errors.
- Keep domain data access behind `data/loader.py`.

**Non-Goals:**
- Building a new persistence layer or replacing mock-domain sources.
- Introducing outcome labels beyond `approve`, `deny`, `escalate`.
- Implementing direct external policy APIs or live vendor systems.

## Decisions

1. Use Pydantic v2 as the contract boundary for both inbound requests and outbound recommendations.
Rationale: Keeps schema validation centralized and explicit; aligns with project constraints.
Alternatives considered: untyped dict IO (rejected for weak validation and testability).

2. Use Pydantic AI agent construction with `output_type=ProcurementRecommendation`.
Rationale: Enforces structured decision outputs at runtime and avoids deprecated patterns.
Alternatives considered: plain text generation with post-parse (rejected due to fragile parsing and drift risk).

3. Execute all four procurement tools and aggregate their signals before selecting a final decision.
Rationale: Prevents early short-circuiting from missing escalations or denials and supports transparent rationale composition.
Alternatives considered: first-hit short-circuit evaluation (rejected because it can hide higher-priority escalation signals).

Tool selection logic:
- `check_budget` evaluates cost center remaining budget versus request amount.
- `check_vendor_duplication` evaluates contracted-vendor conflicts and single-source concerns.
- `check_policy_compliance` evaluates explicit policy triggers (for example prohibited category, expired contract constraints).
- `assess_risk` evaluates escalation-only factors such as compliance flags and governance-sensitive conditions.
- The agent runs all four for each request to avoid dropping higher-priority signals.

4. Resolve final decision via strict precedence `escalate > deny > approve`.
Rationale: Matches requested governance posture and avoids ambiguity in multi-trigger cases.
Alternatives considered: deny-first precedence and weighted scoring (rejected for mismatch with requested rule and reduced explainability).

5. Treat tool failures as explicit risk signals that must appear in rationale text.
Rationale: Silent failure is non-compliant with agent behavior constraints; surfacing error context improves auditability.
Alternatives considered: swallow and continue (rejected), hard-fail entire request (rejected for reduced operational continuity).

Error fallback path:
- If one tool fails, the agent records the error, continues with remaining tools, and still returns a contract-valid recommendation.
- If multiple tools fail, the agent aggregates all error summaries into rationale and applies precedence using available successful tool signals.
- If all tools fail, the agent returns `escalate` with explicit failure context in rationale to force human review.

6. Route all policy/vendor/budget/request reads through `data/loader.py` abstractions.
Rationale: Preserves project structure conventions and supports easier test simulation.
Alternatives considered: direct JSON file reads in tools (rejected by project rules).

## Risks / Trade-offs

- [Risk] Sample data contains edge ambiguities (for example ambiguous outcome labels in fixtures) that can conflict with strict output enum. -> Mitigation: Normalize runtime output contract to the allowed triad and treat ambiguity as rationale context, not a decision label.
- [Risk] Conflicting signals across tools may produce unstable rationale wording between runs. -> Mitigation: Use deterministic rationale assembly order and include a fixed precedence statement.
- [Risk] Over-reliance on mock assumptions could diverge from future live policy interpretation. -> Mitigation: Encode policy checks as explicit tool responsibilities and keep decision precedence centralized.
- [Risk] Tool exceptions could degrade recommendation quality. -> Mitigation: Catch per-tool exceptions, include concise error summaries, and continue evaluating remaining tools.
- [Risk] Mapping policy semantics across tools can overlap (for example deny in both budget and policy checks). -> Mitigation: Normalize each tool output to a common signal schema before precedence resolution.