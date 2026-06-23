## 1. Define Models and Agent Contract

- [ ] 1.1 Create PurchaseRequest and ProcurementRecommendation Pydantic v2 models with typed fields and decision constrained to approve, deny, or escalate.
- [ ] 1.2 Enforce non-empty rationale validation and ensure recommendation output schema includes request_id, decision, and rationale.
- [ ] 1.3 Construct the Pydantic AI procurement agent with output_type bound to ProcurementRecommendation and prompt guidance for deterministic decisioning.

## 2. Implement and Wire Core Checks

- [ ] 2.1 Implement or confirm check_budget behavior to validate request amount against remaining cost center budget and return machine-readable findings.
- [ ] 2.2 Implement or confirm check_vendor_duplication behavior for single-source restriction evaluation and conflict reporting.
- [ ] 2.3 Implement or confirm check_policy_compliance behavior for deny and escalate policy triggers across relevant policies.
- [ ] 2.4 Implement or confirm assess_risk behavior for contract-status and compliance-flag risk classification.
- [ ] 2.5 Ensure agent evaluation flow executes all four checks for every request and aggregates findings for rationale composition.

## 3. Enforce Decision Resolution and Error Handling

- [ ] 3.1 Implement deterministic decision resolver that applies precedence escalate over deny over approve.
- [ ] 3.2 Treat any tool or data-access error as an escalation trigger and include failure details in rationale.
- [ ] 3.3 Ensure no tool reads mock_data files directly and that all domain fixture access occurs through data loader functions.

## 4. Validate Behavior with Simulated Tests

- [ ] 4.1 Add or update tests for approve path where all checks pass and rationale is non-empty.
- [ ] 4.2 Add or update tests for deny paths including budget overage, prohibited category, expired contract, and single-source breach.
- [ ] 4.3 Add or update tests for escalate paths including compliance-flagged vendor, threshold escalation, and tool/data error conditions.
- [ ] 4.4 Verify tests assert structured output contract and decision enumeration constraints.

## 5. Readiness and Documentation

- [ ] 5.1 Confirm implementation aligns with capability spec scenarios for procurement-intelligence-agent.
- [ ] 5.2 Update repository documentation where needed to describe agent behavior, check sequence, and fail-safe escalation rules.
- [ ] 5.3 Run full test command with results capture and confirm go/no-go readiness for review.
