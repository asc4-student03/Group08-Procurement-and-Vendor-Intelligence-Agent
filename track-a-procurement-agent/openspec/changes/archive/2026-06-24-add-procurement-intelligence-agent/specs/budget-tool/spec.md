## ADDED Requirements

### Requirement: Evaluate Budget Sufficiency
The `check_budget` tool SHALL accept `cost_center_id` and `total_amount` and evaluate whether the request fits within the cost center remaining quarterly budget.

#### Scenario: Request amount is within remaining budget
- **WHEN** `total_amount` is less than or equal to the remaining budget for the provided cost center
- **THEN** the tool returns an approve-compatible signal

#### Scenario: Request amount exceeds remaining budget
- **WHEN** `total_amount` is greater than the remaining budget for the provided cost center
- **THEN** the tool returns a deny signal with overage details

### Requirement: Return Standard Tool Payload
The tool MUST return the standard tool payload shape: `{ "signal": "approve|deny|escalate", "summary": string, "details": object }`.

The `details` object MUST include:
- `cost_center_id`
- `remaining_budget`
- `total_amount`
- `overage`

#### Scenario: Budget overage computed
- **WHEN** a budget overage exists
- **THEN** `details.overage` is populated with the positive overage amount

#### Scenario: No budget overage
- **WHEN** no budget overage exists
- **THEN** `details.overage` is `0`

### Requirement: Enforce POL-008 Deny Semantics
The tool SHALL align with POL-008 by signaling deny when a request exceeds the remaining quarterly budget.

#### Scenario: POL-008 triggered
- **WHEN** a request would cause quarterly spend to exceed remaining budget
- **THEN** the tool `signal` is `deny` and summary references budget overage prohibition

### Requirement: Handle Missing Budget Records Safely
The tool MUST handle unknown cost centers or unavailable budget data without crashing and MUST return structured error context.

#### Scenario: Unknown cost center
- **WHEN** provided `cost_center_id` is not found in budget records
- **THEN** the tool returns an error payload that can be surfaced in rationale

#### Scenario: Budget data unavailable
- **WHEN** budget records cannot be loaded from the loader layer
- **THEN** the tool returns an error payload that can be surfaced in rationale
