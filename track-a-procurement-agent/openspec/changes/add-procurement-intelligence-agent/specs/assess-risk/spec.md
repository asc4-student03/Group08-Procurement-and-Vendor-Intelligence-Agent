## ADDED Requirements

### Requirement: assess_risk SHALL return vendor risk profile
The system MUST provide an assess_risk tool that accepts vendor_id and returns the vendor risk profile including compliance flag status, contract status, and computed risk level.

#### Scenario: Vendor exists and profile is returned
- **WHEN** assess_risk is called with a known vendor_id
- **THEN** the result MUST include compliance_flag_status, contract_status, and risk_level

### Requirement: assess_risk SHALL constrain computed risk level values
The assess_risk tool MUST compute and return risk_level as one of low, medium, high, or critical.

#### Scenario: Computed level uses allowed taxonomy
- **WHEN** assess_risk computes vendor risk
- **THEN** risk_level MUST be low, medium, high, or critical

### Requirement: assess_risk SHALL prioritize compliance and contract risk signals
The assess_risk computation MUST incorporate compliance flag status and contract status as primary risk inputs.

#### Scenario: Vendor is compliance flagged
- **WHEN** the vendor has an active compliance flag
- **THEN** assess_risk MUST return a high or critical risk_level

#### Scenario: Vendor contract is expired
- **WHEN** the vendor contract_status is expired
- **THEN** assess_risk MUST return a high or critical risk_level

### Requirement: assess_risk SHALL fail safely on unknown or unavailable data
If vendor data cannot be found or loaded, assess_risk MUST return a structured error outcome that remains machine-readable by the agent.

#### Scenario: Unknown vendor ID
- **WHEN** assess_risk is called with a vendor_id not present in vendor data
- **THEN** the result MUST include a non-empty error field and a conservative risk outcome
