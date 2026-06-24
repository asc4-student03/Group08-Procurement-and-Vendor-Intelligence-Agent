## ADDED Requirements

### Requirement: Return Vendor Risk Profile
The `assess_risk` tool SHALL accept `vendor_id` and return a risk profile containing compliance flag status, contract status, and computed risk level.

#### Scenario: Vendor found
- **WHEN** the input vendor exists
- **THEN** the tool returns profile fields `vendor_id`, `compliance_flag`, `contract_status`, and `risk_level`

### Requirement: Constrain Risk Level Enumeration
The tool MUST constrain `risk_level` to exactly one of `low`, `medium`, `high`, or `critical`.

#### Scenario: Valid risk assignment
- **WHEN** profile computation completes
- **THEN** the returned `risk_level` is one of the allowed enumeration values

### Requirement: Compute Risk Using Compliance and Contract Signals
The tool SHALL compute risk level from vendor compliance status and contract status with deterministic mapping rules.

#### Scenario: Compliance flag active
- **WHEN** vendor `compliance_flag` is true
- **THEN** computed `risk_level` is `critical`

#### Scenario: Contract expired
- **WHEN** vendor `contract_status` is `expired` and compliance flag is false
- **THEN** computed `risk_level` is at least `high`

#### Scenario: No contract and no compliance flag
- **WHEN** vendor `contract_status` is `none` and compliance flag is false
- **THEN** computed `risk_level` is `medium`

#### Scenario: Active contract and no compliance flag
- **WHEN** vendor `contract_status` is `active` and compliance flag is false
- **THEN** computed `risk_level` is `low`

### Requirement: Return Structured Errors for Unknown Vendors
The tool MUST handle unknown vendor IDs without unhandled exceptions and return structured diagnostic error information.

#### Scenario: Vendor not found
- **WHEN** the input `vendor_id` does not exist in loaded vendor records
- **THEN** the tool returns a structured error payload suitable for agent rationale inclusion
