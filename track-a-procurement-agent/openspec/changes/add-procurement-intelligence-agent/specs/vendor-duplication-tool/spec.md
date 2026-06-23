## ADDED Requirements

### Requirement: Vendor duplication tool identifies contracted alternatives in category
The system SHALL provide a vendor duplication tool that accepts vendor_id, category, and amount, and identifies other vendors with active contracts in the same category.

#### Scenario: Active contracted alternatives exist
- **WHEN** one or more vendors other than vendor_id have contract_status active in the same category
- **THEN** the tool returns those conflicting vendor IDs and associated contract details

#### Scenario: No contracted alternatives exist
- **WHEN** no other vendor in the category has contract_status active
- **THEN** the tool returns an empty conflict list

### Requirement: Vendor duplication tool returns conflict details
The system SHALL return conflict entries containing vendor_id, vendor_name, contract_id, and contract_status for each conflicting active-contract vendor.

#### Scenario: Conflict details are complete
- **WHEN** conflicts are detected
- **THEN** each conflict includes vendor_id, vendor_name, contract_id, and contract_status

#### Scenario: Requested vendor excluded from conflicts
- **WHEN** conflicts are computed
- **THEN** the input vendor_id is not included in the conflicting vendor list

### Requirement: POL-001 threshold governs deny trigger from duplication findings
The system SHALL apply POL-001 threshold logic so duplication findings become deny-driving only when amount exceeds the single-source threshold.

#### Scenario: Amount above POL-001 threshold with conflicts
- **WHEN** amount is greater than the POL-001 threshold and active contracted alternatives exist
- **THEN** the tool marks violation true and returns a deny-driving single-source finding

#### Scenario: Amount at or below POL-001 threshold
- **WHEN** amount is less than or equal to the POL-001 threshold
- **THEN** the tool returns violation false for POL-001 enforcement

### Requirement: Vendor duplication tool handles data failures safely
The system SHALL return explicit error context when vendor data cannot be loaded.

#### Scenario: Vendor data unavailable
- **WHEN** vendor records cannot be loaded
- **THEN** the response includes an error field describing the failure

#### Scenario: Failure does not fabricate conflicts
- **WHEN** a data-loading error occurs
- **THEN** conflict lists are empty and error context is returned for fail-safe escalation by decision logic

### Requirement: Vendor duplication tool uses loader APIs for domain data access
The system SHALL retrieve vendor data through data loader functions and SHALL NOT read fixture files directly from tool code.

#### Scenario: Vendor data access path
- **WHEN** vendor data is needed
- **THEN** the tool uses the data loader module

#### Scenario: Direct fixture reads are absent
- **WHEN** the tool implementation is reviewed
- **THEN** it contains no direct reads from mock_data paths
