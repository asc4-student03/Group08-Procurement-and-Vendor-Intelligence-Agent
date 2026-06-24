## ADDED Requirements

### Requirement: assess_risk tool contract
The system MUST provide an `assess_risk` tool that returns the risk profile for a vendor.

Input contract:
- `vendor_id` (string)

Output contract:
- `vendor_id` (string)
- `vendor_name` (string)
- `compliance_flag` (boolean)
- `contract_status` (string: `active`, `expired`, `none`, or `unknown`)
- `risk_level` (string: `low`, `medium`, `high`, or `critical`)
- `risk_summary` (string)
- `error` (string, optional)

#### Scenario: Critical risk for compliance-flagged vendor
- **WHEN** the vendor has an active compliance flag
- **THEN** `assess_risk` MUST return `risk_level=critical`

#### Scenario: High risk for expired contract
- **WHEN** the vendor contract status is `expired`
- **THEN** `assess_risk` MUST return `risk_level=high`

#### Scenario: Medium risk for no contract
- **WHEN** the vendor contract status is `none` and no compliance flag exists
- **THEN** `assess_risk` MUST return `risk_level=medium`

#### Scenario: Low risk for active clean vendor
- **WHEN** the vendor has `contract_status=active` and no compliance flag
- **THEN** `assess_risk` MUST return `risk_level=low`

#### Scenario: Vendor unknown or data unavailable
- **WHEN** the vendor cannot be found or vendor data cannot be loaded
- **THEN** `assess_risk` MUST include `error` and MUST return a conservative risk level suitable for escalation handling
