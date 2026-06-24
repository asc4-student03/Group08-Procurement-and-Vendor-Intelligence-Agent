## 1. Model Contracts

- [x] 1.1 Implement `PurchaseRequest` in `models.py` with required fields and positive-value validation for quantity and amounts.
- [x] 1.2 Implement `ProcurementRecommendation` in `models.py` with decision constrained to `approve|deny|escalate` and non-empty rationale validation.
- [x] 1.3 Add model tests covering valid payloads and validation failures for invalid decision and empty rationale.

## 2. Data Access Layer

- [x] 2.1 Implement `data/loader.py` functions for budgets, vendors, policies, and requests using `pathlib.Path`-based mock data resolution.
- [x] 2.2 Ensure tools and agent modules consume loader functions only and do not directly read `mock_data/` JSON files.
- [x] 2.3 Add tests for loader success paths and missing-file error behavior.

## 3. Procurement Check Tools

- [x] 3.1 Implement `check_budget` inputs/outputs exactly as specified, including `error` handling for unknown cost centers and missing data.
- [x] 3.2 Add `check_budget` unit tests for within-budget, over-budget, boundary, and unknown-cost-center behavior.
- [x] 3.3 Implement `check_vendor_duplication` inputs/outputs exactly as specified, including conflict lists and threshold reason text.
- [x] 3.4 Add `check_vendor_duplication` unit tests for above-threshold violation, at-threshold no-violation, and data-unavailable behavior.
- [x] 3.5 Implement `check_policy_compliance` inputs/outputs exactly as specified, including `violations[]`, `violation_count`, and `highest_severity`.
- [x] 3.6 Add `check_policy_compliance` unit tests for deny trigger, escalate trigger, mixed-severity precedence, and data-unavailable behavior.
- [ ] 3.7 Implement `assess_risk` inputs/outputs exactly as specified, including risk-level mapping and `error` behavior.
- [ ] 3.8 Add `assess_risk` unit tests for critical/high/medium/low risk mapping and unknown-vendor behavior.

## 4. Agent Orchestration

- [ ] 4.1 Construct the Pydantic AI agent in `agent.py` with `output_type=ProcurementRecommendation`.
- [ ] 4.2 Register and execute all four tools for each request evaluation.
- [ ] 4.3 Encode deterministic precedence `escalate > deny > approve` in agent decision behavior.
- [ ] 4.4 Ensure tool errors are captured and reflected in rationale with escalation-safe handling.
- [ ] 4.5 Add end-to-end agent tests covering approve, deny, escalate, and error-aware rationale behavior.

## 5. Verification and Readiness

- [x] 5.1 Run `openspec validate add-procurement-intelligence-agent` and resolve any specification issues.
- [x] 5.2 Run `pytest tests/ -v --tb=short --junitxml=docs/test-results.xml` and confirm passing coverage for required scenarios.
- [ ] 5.3 Review rationale quality in test outputs to ensure check-driven evidence is consistently included.
- [ ] 5.4 Prepare implementation summary and open `/opsx:apply` for execution.
