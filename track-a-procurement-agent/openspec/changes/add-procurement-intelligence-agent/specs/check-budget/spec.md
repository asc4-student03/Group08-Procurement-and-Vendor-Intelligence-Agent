## ADDED Requirements

### Requirement: check_budget SHALL evaluate remaining budget by cost center
The system MUST provide a check_budget tool that accepts cost_center_id and requested_amount, loads budget data through data/loader.py, and determines whether the request is within the cost center's remaining budget.

#### Scenario: Request is within remaining budget
- **WHEN** check_budget is called with a known cost_center_id and requested_amount less than or equal to remaining_budget
- **THEN** the result MUST set within_budget to true and overage to 0.0

### Requirement: check_budget SHALL return structured budget evidence
The check_budget tool MUST return a structured dictionary containing within_budget, cost_center_id, remaining_budget, requested_amount, and overage for all executions.

#### Scenario: Required keys are always present
- **WHEN** check_budget returns a result
- **THEN** the result MUST include within_budget, cost_center_id, remaining_budget, requested_amount, and overage keys

### Requirement: check_budget SHALL detect budget overage amounts
The check_budget tool MUST calculate overage as max(0, requested_amount - remaining_budget) and MUST set within_budget to false when overage is greater than zero.

#### Scenario: Request exceeds remaining budget
- **WHEN** check_budget is called with requested_amount greater than remaining_budget
- **THEN** the result MUST set within_budget to false and overage to the positive difference between requested_amount and remaining_budget

### Requirement: check_budget SHALL handle unknown cost centers safely
If the provided cost_center_id does not exist in budget data, the check_budget tool MUST return within_budget as false and include a non-empty error message in the result.

#### Scenario: Unknown cost center ID
- **WHEN** check_budget is called with a cost_center_id that is not found in budget data
- **THEN** the result MUST include an error message and within_budget MUST be false

### Requirement: check_budget SHALL surface loader failures as errors
If budget data cannot be loaded, the check_budget tool MUST return a structured error result and MUST NOT raise an unhandled exception to the agent.

#### Scenario: Budget data load failure
- **WHEN** data/loader.py raises a data-loading error during check_budget execution
- **THEN** check_budget MUST return within_budget as false and include a non-empty error field describing the failure
