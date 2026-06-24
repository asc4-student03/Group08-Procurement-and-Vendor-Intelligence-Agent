## Purpose
Define the contract and expected behavior for budget evaluation in procurement decisions.

## Requirements

### Requirement: check_budget tool contract
The system MUST provide a `check_budget` tool that evaluates whether a purchase amount fits within a cost center's remaining quarterly budget.

Input contract:
- `cost_center_id` (string)
- `requested_amount` (number)

Output contract:
- `within_budget` (boolean)
- `cost_center_id` (string)
- `remaining_budget` (number)
- `requested_amount` (number)
- `overage` (number)
- `error` (string, optional)

#### Scenario: Request is within remaining budget
- **WHEN** `requested_amount` is less than or equal to the cost center `remaining_budget`
- **THEN** `check_budget` MUST return `within_budget=true` and `overage=0`

#### Scenario: Request exceeds remaining budget
- **WHEN** `requested_amount` is greater than the cost center `remaining_budget`
- **THEN** `check_budget` MUST return `within_budget=false` and `overage > 0`

#### Scenario: Exact boundary amount
- **WHEN** `requested_amount` exactly equals the cost center `remaining_budget`
- **THEN** `check_budget` MUST treat the request as within budget

#### Scenario: Unknown cost center
- **WHEN** `cost_center_id` is not present in budget data
- **THEN** `check_budget` MUST include `error` and MUST return `within_budget=false`

#### Scenario: Budget data unavailable
- **WHEN** budget records cannot be loaded
- **THEN** `check_budget` MUST include `error` and MUST still return all non-error output keys