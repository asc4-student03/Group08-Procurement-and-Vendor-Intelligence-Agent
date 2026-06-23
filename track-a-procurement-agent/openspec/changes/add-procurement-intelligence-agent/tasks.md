## 1. Models and output contract

- [ ] 1.1 Define and validate PurchaseRequest and ProcurementRecommendation in solutions/models.py using Pydantic v2 with decision constrained to approve, deny, escalate and non-empty rationale
- [ ] 1.2 Add or update model tests in solutions/tests to verify accepted and rejected decision values and rationale validation behavior

## 2. Tool contract alignment

- [ ] 2.1 Review and normalize return contracts for check_budget, check_vendor_duplication, check_policy_compliance, and assess_risk in solutions/tools for deterministic agent consumption
- [ ] 2.2 Ensure tool data access paths use solutions/data/loader.py and remove or avoid direct mock_data reads in tool code
- [ ] 2.3 Add or update tool success-path tests in solutions/tests/test_budget.py, solutions/tests/test_vendor_duplication.py, solutions/tests/test_policy_compliance.py, and solutions/tests/test_risk_assessment.py

## 3. Agent orchestration and decision policy

- [ ] 3.1 Implement procurement intelligence orchestration in solutions/agent.py with Pydantic AI Agent configured with output_type ProcurementRecommendation
- [ ] 3.2 Invoke all four tools for each request and aggregate check outcomes into a combined decision context
- [ ] 3.3 Implement deterministic precedence logic escalate over deny over approve and ensure rationale includes check evidence
- [ ] 3.4 Catch individual tool errors and append explicit error details into rationale instead of silently ignoring failures

## 4. End-to-end verification

- [ ] 4.1 Add or update solutions/tests/test_agent.py coverage for approve, deny, escalate, precedence conflicts, and tool error propagation
- [ ] 4.2 Run pytest tests/ -v --tb=short --junitxml=docs/test-results.xml and resolve failures
- [ ] 4.3 Confirm all change artifacts are apply-ready via openspec status --change add-procurement-intelligence-agent
