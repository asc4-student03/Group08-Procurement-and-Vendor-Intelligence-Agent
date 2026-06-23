## ADDED Requirements

### Requirement: Risk assessment tool returns vendor risk profile
The system SHALL provide a risk assessment tool that accepts vendor_id and returns compliance flag status, contract status, and computed risk level.

#### Scenario: Vendor found in dataset
- **WHEN** vendor_id exists in vendor records
- **THEN** response includes vendor_id, vendor_name, compliance_flag, compliance_notes, contract_status, risk_level, and risk_summary

#### Scenario: Vendor not found
- **WHEN** vendor_id does not exist in vendor records
- **THEN** response includes an error field and a conservative risk profile for fail-safe handling

### Requirement: Risk level is deterministically computed from vendor attributes
The system SHALL compute risk_level using vendor compliance flag and contract status with fixed mapping logic.

#### Scenario: Compliance flagged vendor
- **WHEN** compliance_flag is true
- **THEN** risk_level is critical

#### Scenario: Expired contract vendor
- **WHEN** compliance_flag is false and contract_status is expired
- **THEN** risk_level is high

#### Scenario: No-contract vendor
- **WHEN** compliance_flag is false and contract_status is none
- **THEN** risk_level is medium

#### Scenario: Active contract without compliance flag
- **WHEN** compliance_flag is false and contract_status is active
- **THEN** risk_level is low

### Requirement: Risk output includes reviewer-readable summary
The system SHALL include risk_summary text that explains the computed risk level and reviewer action context.

#### Scenario: Summary for critical risk
- **WHEN** risk_level is critical
- **THEN** risk_summary describes compliance-hold context and escalation expectation

#### Scenario: Summary for lower risks
- **WHEN** risk_level is low or medium
- **THEN** risk_summary states contract/compliance posture and review guidance

### Requirement: Risk assessment tool handles data failures with explicit errors
The system SHALL return explicit error context when vendor data cannot be loaded.

#### Scenario: Vendor data unavailable
- **WHEN** vendor records cannot be loaded
- **THEN** response includes an error field and conservative risk classification

#### Scenario: Error response supports fail-safe handling
- **WHEN** risk computation cannot be completed due to data failure
- **THEN** response contains enough context for the decision resolver to escalate safely

### Requirement: Risk assessment tool uses loader APIs for domain data access
The system SHALL retrieve vendor data through loader functions and SHALL NOT read fixture files directly from tool code.

#### Scenario: Vendor data access path
- **WHEN** risk assessment requires vendor details
- **THEN** the tool retrieves data via data loader module

#### Scenario: Direct fixture reads are absent
- **WHEN** implementation is reviewed
- **THEN** risk tool contains no direct mock_data file reads
