## ADDED Requirements

### Requirement: Budget tool evaluates request against cost center remaining budget
The system SHALL provide a budget tool that accepts cost_center_id and requested_amount and determines whether the request is within the cost center's remaining quarterly budget.

#### Scenario: Request is within remaining budget
- **WHEN** requested_amount is less than remaining budget for the supplied cost_center_id
- **THEN** the tool returns within_budget as true and overage as 0

#### Scenario: Request exceeds remaining budget
- **WHEN** requested_amount is greater than remaining budget for the supplied cost_center_id
- **THEN** the tool returns within_budget as false and overage as requested_amount minus remaining_budget

#### Scenario: Request equals remaining budget
- **WHEN** requested_amount is exactly equal to remaining budget for the supplied cost_center_id
- **THEN** the tool returns within_budget as true and overage as 0

### Requirement: Budget tool returns a deterministic result contract
The system SHALL return budget-tool output with fields cost_center_id, requested_amount, remaining_budget, within_budget, and overage.

#### Scenario: Successful budget lookup
- **WHEN** a valid cost center is found in budget data
- **THEN** the response includes cost_center_id, requested_amount, remaining_budget, within_budget, and overage

#### Scenario: Numeric overage normalization
- **WHEN** overage is calculated
- **THEN** overage is never negative and is rounded to two decimal places

### Requirement: Budget overage maps to POL-008 deny signal
The system SHALL treat an over-budget result as a policy-triggering condition aligned to POL-008 (Budget Overage Prohibition).

#### Scenario: Overage triggers deny condition
- **WHEN** within_budget is false
- **THEN** the budget finding indicates a deny-driving overage condition for final decision resolution

#### Scenario: No overage does not trigger budget deny
- **WHEN** within_budget is true
- **THEN** the budget check does not add a deny signal

### Requirement: Budget tool handles data failures with explicit error context
The system SHALL return explicit error context when budget data cannot be loaded or cost_center_id is not found.

#### Scenario: Budget data unavailable
- **WHEN** budget records cannot be loaded
- **THEN** the tool response contains an error field describing the failure

#### Scenario: Unknown cost center
- **WHEN** cost_center_id is not present in budget records
- **THEN** the tool response contains an error field indicating missing cost center

### Requirement: Budget tool uses loader APIs for domain data access
The system SHALL obtain budget data via data loader functions and SHALL NOT read fixture files directly from tool code.

#### Scenario: Budget lookup path
- **WHEN** budget data is required
- **THEN** the tool retrieves data through the data loader module

#### Scenario: Direct fixture reads are absent
- **WHEN** the budget tool implementation is reviewed
- **THEN** it contains no direct file reads from mock_data paths
