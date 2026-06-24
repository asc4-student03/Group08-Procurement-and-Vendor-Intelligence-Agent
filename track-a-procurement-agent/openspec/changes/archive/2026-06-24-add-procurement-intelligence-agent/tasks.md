## 1. Models (`solutions/models.py`)

- [x] 1.1 Define `PurchaseRequest` with all required request fields and strict types from domain data
- [x] 1.2 Add numeric validators (`quantity`, `unit_price`, `total_amount`) and total consistency check
- [x] 1.3 Define `ProcurementRecommendation` with decision enum constrained to `approve|deny|escalate` and required non-empty rationale

## 2. Data Loader (`solutions/data/loader.py`)

- [x] 2.1 Confirm loader functions expose requests, policies, vendors, and budgets needed by tools
- [x] 2.2 Update loader interfaces or helper methods to support tool inputs without direct `mock_data/` file reads in business logic
- [x] 2.3 Add loader-focused tests for expected domain records and error paths

## 3. Budget Tool (`solutions/tools/budget.py`)

- [x] 3.1 Implement/align `check_budget` input contract (`cost_center_id`, `total_amount`)
- [x] 3.2 Return normalized signal payload (`signal`, `summary`, `details`) and budget-overage rationale data
- [x] 3.3 Add success and failure-path tests for budget checks

## 4. Vendor Duplication Tool (`solutions/tools/vendor_duplication.py`)

- [x] 4.1 Implement/align `check_vendor_duplication` input contract (`vendor_id`, `vendor_name`, `category`, `total_amount`)
- [x] 4.2 Enforce single-source/duplication logic using loader data and normalized return shape
- [x] 4.3 Add success and failure-path tests for vendor duplication checks

## 5. Policy Compliance Tool (`solutions/tools/policy_compliance.py`)

- [x] 5.1 Implement/align `check_policy_compliance` input contract (`category`, `vendor_id`, `total_amount`, `quantity`)
- [x] 5.2 Evaluate applicable policies and return normalized signal payload with policy references
- [x] 5.3 Add success and failure-path tests for policy compliance checks

## 6. Risk Tool (`solutions/tools/risk_assessment.py`)

- [x] 6.1 Implement/align `assess_risk` input contract (`vendor_id`, `category`, `total_amount`, `cost_center_id`)
- [x] 6.2 Return normalized risk signal payload and escalation rationale data
- [x] 6.3 Add success and failure-path tests for risk assessment checks

## 7. Agent Wiring (`solutions/agent.py`)

- [x] 7.1 Configure Pydantic AI agent with `output_type=ProcurementRecommendation`
- [x] 7.2 Execute all four tools per request and aggregate normalized signals
- [x] 7.3 Apply final precedence `escalate > deny > approve`
- [x] 7.4 Build deterministic non-empty rationale including tool findings and tool errors
- [x] 7.5 Ensure tool exceptions are caught and surfaced without silent failures

## 8. Integration Tests (`solutions/tests/`)

- [x] 8.1 Add agent tests for approve, deny, and escalate recommendation outcomes
- [x] 8.2 Add precedence conflict tests to verify `escalate > deny > approve`
- [x] 8.3 Add tests asserting disallowed decisions (for example ambiguous) are never emitted
- [x] 8.4 Add tests for single-tool and multi-tool exception handling with contract-valid output

## 9. Validation and Session Deliverables

- [x] 9.1 Run `openspec validate` and fix any artifact/schema issues
- [x] 9.2 Run `pytest tests/ -v --tb=short --junitxml=docs/test-results.xml` and verify passing results
- [x] 9.3 Confirm artifacts remain the single capstone change source for Sessions 2 and 3 implementation
