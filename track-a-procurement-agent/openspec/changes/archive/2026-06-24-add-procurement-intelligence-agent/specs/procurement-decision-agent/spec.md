## ADDED Requirements

### Requirement: Agent executes all four checks
The procurement intelligence agent SHALL invoke `check_budget`, `check_vendor_duplication`, `check_policy_compliance`, and `assess_risk` for every purchase request evaluation.

#### Scenario: Request evaluation is initiated
- **WHEN** a valid `PurchaseRequest` is submitted to the agent
- **THEN** the agent SHALL call all four tools before finalizing a recommendation

### Requirement: Decision precedence is deterministic
The agent SHALL apply recommendation priority in this strict order: `escalate` over `deny` over `approve`.

#### Scenario: Escalate and deny triggers coexist
- **WHEN** at least one escalation condition and one denial condition are both present
- **THEN** the final recommendation SHALL be `escalate`

#### Scenario: Denial trigger exists without escalation trigger
- **WHEN** one or more denial conditions exist and no escalation conditions exist
- **THEN** the final recommendation SHALL be `deny`

#### Scenario: No deny or escalate triggers exist
- **WHEN** all checks complete without deny or escalate outcomes
- **THEN** the final recommendation SHALL be `approve`

### Requirement: Tool error handling is explicit and safe
The agent SHALL treat tool failures as safety-significant and SHALL reflect those failures in the recommendation rationale.

#### Scenario: Any tool returns an error
- **WHEN** one or more tools return an error field or unavailable-data signal
- **THEN** the agent SHALL return `escalate` and SHALL include error context in rationale text

### Requirement: Recommendation rationale quality
The agent SHALL return a non-empty rationale that references the check results that drove the decision.

#### Scenario: Recommendation is returned
- **WHEN** the agent emits a `ProcurementRecommendation`
- **THEN** rationale text SHALL be non-empty and SHALL identify decision-driving evidence such as policy IDs, budget values, or risk findings
