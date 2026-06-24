## Purpose
Define policy-compliance evaluation requirements across the full procurement policy set.

## Requirements

### Requirement: check_policy_compliance tool contract
The system MUST provide a `check_policy_compliance` tool that evaluates a purchase request against all eight policies in `mock_data/policies.json` and reports violations with forced decisions.

Input contract:
- `request` object containing:
  - `request_id` (string)
  - `cost_center_id` (string)
  - `vendor_id` (string)
  - `category` (string)
  - `quantity` (integer)
  - `total_amount` (number)

Output contract:
- `violations` (array of objects), where each violation includes:
  - `policy_id` (string)
  - `rule_description` (string)
  - `forced_decision` (string: `deny` or `escalate`)
- `violation_count` (integer)
- `highest_severity` (string: `none`, `deny`, or `escalate`)
- `error` (string, optional)

#### Scenario: Tool evaluates full policy set
- **WHEN** `check_policy_compliance` is called with a valid request
- **THEN** the tool MUST evaluate policy conditions for POL-001 through POL-008 and return all applicable violations

#### Scenario: Deny policy is triggered
- **WHEN** one or more deny-forcing policy rules are violated
- **THEN** each violation MUST include `policy_id`, `rule_description`, and `forced_decision=deny`

#### Scenario: Escalate policy is triggered
- **WHEN** one or more escalate-forcing policy rules are violated
- **THEN** each violation MUST include `policy_id`, `rule_description`, and `forced_decision=escalate`

#### Scenario: Mixed severities are present
- **WHEN** both deny and escalate violations exist
- **THEN** `highest_severity` MUST be `escalate`

#### Scenario: No policy violations
- **WHEN** the request violates none of the eight policies
- **THEN** the tool MUST return `violations=[]`, `violation_count=0`, and `highest_severity=none`

#### Scenario: Policy or vendor data unavailable
- **WHEN** required policy/vendor inputs cannot be loaded
- **THEN** the tool MUST include `error` and MUST return `highest_severity=escalate`
