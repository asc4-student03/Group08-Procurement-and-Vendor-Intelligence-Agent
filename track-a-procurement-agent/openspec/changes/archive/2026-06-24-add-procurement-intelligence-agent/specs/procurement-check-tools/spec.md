## ADDED Requirements

### Requirement: check_budget contract
The system MUST provide a `check_budget(cost_center_id: str, requested_amount: float)` tool.

Required return shape:
- `within_budget` (bool)
- `cost_center_id` (str)
- `remaining_budget` (float)
- `requested_amount` (float)
- `overage` (float)
- `error` (str, optional)

#### Scenario: Request exceeds remaining budget
- **WHEN** `requested_amount` is greater than remaining budget for `cost_center_id`
- **THEN** `check_budget` MUST return `within_budget=false` and `overage > 0`

#### Scenario: Request is within budget
- **WHEN** `requested_amount` is less than or equal to remaining budget
- **THEN** `check_budget` MUST return `within_budget=true` and `overage=0`

#### Scenario: Cost center is unknown or data unavailable
- **WHEN** budget data is missing or `cost_center_id` is not found
- **THEN** `check_budget` MUST return `within_budget=false` and MUST include `error`

### Requirement: check_vendor_duplication contract
The system MUST provide a `check_vendor_duplication(vendor_id: str, category: str, amount: float)` tool.

Required return shape:
- `violation` (bool)
- `vendor_id` (str)
- `category` (str)
- `amount` (float)
- `conflicting_vendor_ids` (list[str])
- `conflicting_vendor_names` (list[str])
- `reason` (str)
- `error` (str, optional)

#### Scenario: Single-source violation above threshold
- **WHEN** `amount` is above policy threshold and one or more other active-contract vendors exist in the same category
- **THEN** `check_vendor_duplication` MUST return `violation=true` with non-empty conflict lists

#### Scenario: Amount at or below threshold
- **WHEN** `amount` is at or below policy threshold
- **THEN** `check_vendor_duplication` MUST return `violation=false` and MUST include a threshold-based reason

#### Scenario: Vendor data unavailable
- **WHEN** vendor data cannot be loaded
- **THEN** `check_vendor_duplication` MUST include `error` and MUST still return the standard non-error keys

### Requirement: check_policy_compliance contract
The system MUST provide a `check_policy_compliance(vendor_id: str, category: str, amount: float, quantity: int)` tool.

Required return shape:
- `violations` (list[object]) where each violation includes:
	- `policy_id` (str)
	- `rule_description` (str)
	- `forced_decision` (str: `deny` or `escalate`)
- `violation_count` (int)
- `highest_severity` (str: `none`, `deny`, or `escalate`)
- `error` (str, optional)

#### Scenario: Prohibited category policy triggers denial
- **WHEN** category-level prohibition applies
- **THEN** `check_policy_compliance` MUST include a violation with `forced_decision=deny`

#### Scenario: Escalation policy triggers escalation
- **WHEN** legal/compliance hold or director-threshold conditions apply
- **THEN** `check_policy_compliance` MUST include a violation with `forced_decision=escalate`

#### Scenario: Mixed deny and escalate violations
- **WHEN** both deny and escalate policy violations are present
- **THEN** `highest_severity` MUST be `escalate`

#### Scenario: Policy data unavailable
- **WHEN** policies or vendor records are unavailable
- **THEN** `check_policy_compliance` MUST include `error` and MUST return `highest_severity=escalate`

### Requirement: assess_risk contract
The system MUST provide an `assess_risk(vendor_id: str)` tool.

Required return shape:
- `vendor_id` (str)
- `vendor_name` (str)
- `compliance_flag` (bool)
- `compliance_notes` (str)
- `contract_status` (str)
- `risk_level` (str: `low`, `medium`, `high`, or `critical`)
- `risk_summary` (str)
- `error` (str, optional)

#### Scenario: Compliance flag exists
- **WHEN** vendor record has an active compliance flag
- **THEN** `assess_risk` MUST return `risk_level=critical`

#### Scenario: Expired contract exists
- **WHEN** vendor contract status is `expired`
- **THEN** `assess_risk` MUST return `risk_level=high`

#### Scenario: Vendor is unknown or data unavailable
- **WHEN** vendor lookup fails or vendor data cannot be loaded
- **THEN** `assess_risk` MUST include `error` and MUST return a risk level that drives escalation-safe handling
