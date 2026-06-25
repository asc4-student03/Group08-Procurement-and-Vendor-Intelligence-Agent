## Purpose
Define the formal behavior contract for `agent.py`, including typed input/output, required tools,
deterministic decision priority, error handling, and system prompt constraints.

## Requirements

### Requirement: Agent input and output type contracts
The procurement agent MUST accept request context represented by `PurchaseRequest` from `models.py`
and MUST return `ProcurementRecommendation` from `models.py` as structured output.

Input contract:
- `PurchaseRequest` fields: `request_id`, `requestor`, `cost_center_id`, `vendor_name`, `vendor_id`,
  `category`, `item_description`, `quantity`, `unit_price`, `total_amount`.

Output contract:
- `ProcurementRecommendation` fields: `request_id`, `decision`, `rationale`.
- `decision` MUST be one of `approve`, `deny`, or `escalate`.
- `rationale` MUST be non-empty.

#### Scenario: Valid request produces typed recommendation
- **WHEN** the agent evaluates a valid `PurchaseRequest`
- **THEN** it MUST return a `ProcurementRecommendation` with a valid `decision` value and non-empty `rationale`

#### Scenario: Structured output contract is enforced
- **WHEN** the agent is constructed
- **THEN** it MUST use `output_type=ProcurementRecommendation`
- **AND** raw string-only or untyped dictionary outputs MUST NOT be considered valid behavior

### Requirement: Agent invokes all four procurement tools
The agent MUST invoke all four checks for each request evaluation and MUST NOT short-circuit after
finding a single issue.

Required tools:
- `check_budget(cost_center_id: str, requested_amount: float)`
- `check_vendor_duplication(vendor_id: str, category: str, amount: float)`
- `check_policy_compliance(request: PurchaseRequest)`
- `assess_risk(vendor_id: str)`

#### Scenario: Evaluation runs complete tool suite
- **WHEN** a request is processed
- **THEN** the agent MUST execute all four tools before issuing the final recommendation

### Requirement: Deterministic decision priority across concurrent findings
The agent MUST resolve multiple simultaneous findings using strict precedence:
`escalate` over `deny` over `approve`.

Escalation conditions include:
- Any tool returns an `error`
- `assess_risk` indicates escalation-driving risk (for example `risk_level=critical`)
- `check_policy_compliance` reports any violation with `forced_decision=escalate`

Denial conditions include:
- `check_budget` indicates budget breach
- `check_vendor_duplication` indicates violation
- `check_policy_compliance` reports any violation with `forced_decision=deny`
- `assess_risk` indicates denial-driving risk (for example `risk_level=high`) and no escalation condition exists

Approval condition:
- All checks complete without escalation or denial triggers

#### Scenario: Escalate and deny triggers occur together
- **WHEN** at least one escalation trigger and one denial trigger are present
- **THEN** the final recommendation MUST be `escalate`

#### Scenario: Deny triggers occur without escalation triggers
- **WHEN** one or more denial triggers exist and no escalation trigger exists
- **THEN** the final recommendation MUST be `deny`

#### Scenario: No escalation or denial triggers occur
- **WHEN** all tools return non-triggering outcomes
- **THEN** the final recommendation MUST be `approve`

### Requirement: Error handling is explicit, conservative, and user-visible
The agent MUST treat tool/data failures as safety-significant and MUST surface error context in
its output rationale.

#### Scenario: Any tool reports an error
- **WHEN** one or more tools return an `error` field or unavailable-data signal
- **THEN** the recommendation MUST be `escalate`
- **AND** the `rationale` MUST include which tool failed and why the failure prevents a lower-severity decision

### Requirement: System prompt constraints for behavior and rationale quality
The system prompt used by the agent MUST enforce constraints aligned with procurement governance.

System prompt constraints:
- Must state the agent is advisory and procurement officers make final decisions
- Must require execution of all four tools for every request
- Must codify deterministic priority (`escalate` > `deny` > `approve`)
- Must require rationale content to reference decision-driving evidence from checks
  (for example policy IDs, budget values, overage, risk findings)
- Must require escalation on tool/data errors

#### Scenario: Prompt-level conflict between findings
- **WHEN** prompt-guided reasoning encounters conflicting findings
- **THEN** the prompt constraints MUST force the deterministic priority order without ambiguity

#### Scenario: Recommendation rationale quality check
- **WHEN** the agent emits `ProcurementRecommendation`
- **THEN** the rationale MUST be specific and decision-traceable to at least one tool outcome
