## ADDED Requirements

### Requirement: Identify Vendor Duplication Conflicts
The `check_vendor_duplication` tool SHALL accept `vendor_id` and `category` and determine whether another vendor in the same category has an active contract.

#### Scenario: Active contract conflict exists
- **WHEN** the provided category has at least one active contracted vendor with a different `vendor_id`
- **THEN** the tool returns a conflict result containing each conflicting vendor and contract details

#### Scenario: No active contract conflict exists
- **WHEN** no other active contracted vendor exists in the provided category
- **THEN** the tool returns an empty conflict list

### Requirement: Return Structured Conflict Details
The tool MUST return a structured payload including `input_vendor_id`, `category`, and `conflicts`.

Each `conflicts` entry MUST include:
- `vendor_id`
- `vendor_name`
- `contract_id`
- `contract_status`

#### Scenario: Contract metadata available
- **WHEN** conflicts are found
- **THEN** each conflict entry includes vendor and contract identifiers needed for downstream rationale

### Requirement: Enforce POL-001 Deny Trigger Context
The tool MUST evaluate POL-001 amount threshold context and mark denial eligibility when request amount is greater than $25,000 and a conflicting active contract exists.

#### Scenario: Threshold exceeded with conflict
- **WHEN** request `total_amount` is greater than 25000 and one or more conflicts are present
- **THEN** the tool signal indicates deny eligibility under POL-001

#### Scenario: Threshold not exceeded with conflict
- **WHEN** request `total_amount` is less than or equal to 25000 and conflicts are present
- **THEN** the tool returns conflict details without forcing deny

### Requirement: Handle Unknown Vendor or Category Safely
The tool MUST handle missing vendor or category records without crashing and MUST return structured error context.

#### Scenario: Vendor or category not found
- **WHEN** input `vendor_id` or `category` does not map to known records
- **THEN** the tool returns an error payload with diagnostic details for agent rationale inclusion
