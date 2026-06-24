## Purpose
Define vendor duplication checks to enforce single-source and active-contract policy constraints.

## Requirements

### Requirement: check_vendor_duplication tool contract
The system MUST provide a `check_vendor_duplication` tool that determines whether a request uses a non-contracted vendor in a category where another vendor has an active contract.

Input contract:
- `vendor_id` (string)
- `category` (string)
- `amount` (number)

Output contract:
- `violation` (boolean)
- `vendor_id` (string)
- `category` (string)
- `amount` (number)
- `conflicting_vendor_ids` (array of strings)
- `conflicting_contracts` (array of objects), where each object includes:
  - `vendor_id` (string)
  - `vendor_name` (string)
  - `contract_id` (string)
  - `contract_status` (string)
- `reason` (string)
- `error` (string, optional)

#### Scenario: Above-threshold non-contracted vendor conflict
- **WHEN** `amount` is greater than the POL-001 threshold ($25,000) and at least one different vendor in the same category has an active contract
- **THEN** `check_vendor_duplication` MUST return `violation=true` and MUST include `conflicting_vendor_ids` and `conflicting_contracts`

#### Scenario: At-threshold or below-threshold request
- **WHEN** `amount` is less than or equal to the POL-001 threshold
- **THEN** `check_vendor_duplication` MUST return `violation=false` and MUST include a threshold-based reason

#### Scenario: No active conflicting contract exists
- **WHEN** no other active-contract vendor exists in the category
- **THEN** `check_vendor_duplication` MUST return `violation=false` and an empty conflicts list

#### Scenario: Vendor data unavailable
- **WHEN** vendor records cannot be loaded
- **THEN** `check_vendor_duplication` MUST include `error` and MUST still return all non-error output keys
