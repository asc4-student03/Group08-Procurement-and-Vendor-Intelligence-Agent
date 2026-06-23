## ADDED Requirements

### Requirement: Policy compliance tool evaluates request against all configured policies
The system SHALL provide a policy compliance tool that evaluates each purchase request against all eight policies in policy data.

#### Scenario: Full policy sweep executes
- **WHEN** a request is submitted to policy compliance check
- **THEN** evaluation considers all available policy definitions in the policy dataset

#### Scenario: No policy violations
- **WHEN** no policy rule is violated
- **THEN** the tool returns an empty violations list and violation_count of 0

### Requirement: Policy violations return required fields
The system SHALL return each policy violation with policy_id, rule_description, and forced_decision.

#### Scenario: Single violation returned
- **WHEN** one policy is violated
- **THEN** the violations list includes one entry containing policy_id, rule_description, and forced_decision

#### Scenario: Multiple violations returned
- **WHEN** multiple policies are violated
- **THEN** the violations list includes one entry per violated policy with all required fields

### Requirement: Forced decision values are constrained
The system SHALL constrain forced_decision values in violations to deny or escalate.

#### Scenario: Deny-forcing policy
- **WHEN** a deny policy is triggered
- **THEN** the violation entry forced_decision is deny

#### Scenario: Escalate-forcing policy
- **WHEN** an escalation policy is triggered
- **THEN** the violation entry forced_decision is escalate

### Requirement: Policy compliance output provides severity rollup
The system SHALL provide violation_count and highest_severity in policy-check output.

#### Scenario: Escalation present in any violation
- **WHEN** at least one violation has forced_decision escalate
- **THEN** highest_severity is escalate

#### Scenario: Only deny violations present
- **WHEN** violations exist and all forced_decision values are deny
- **THEN** highest_severity is deny

### Requirement: Policy compliance tool handles missing data with explicit errors
The system SHALL return error context when policy or vendor data required for evaluation is unavailable.

#### Scenario: Policy data unavailable
- **WHEN** policy records cannot be loaded
- **THEN** the response includes an error field describing failure context

#### Scenario: Vendor data unavailable for vendor-dependent checks
- **WHEN** vendor records cannot be loaded
- **THEN** the response includes an error field and fail-safe context for escalation handling

### Requirement: Policy compliance tool uses loader APIs for domain data access
The system SHALL retrieve policy and vendor data via loader functions and SHALL NOT read fixture files directly from tool code.

#### Scenario: Data access path
- **WHEN** policy evaluation requires policy and vendor data
- **THEN** the tool accesses both through the data loader module

#### Scenario: Direct fixture reads are absent
- **WHEN** tool implementation is reviewed
- **THEN** no direct mock_data file reads are present
