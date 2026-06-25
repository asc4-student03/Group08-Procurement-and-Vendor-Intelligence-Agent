## Purpose
Define how policy-compliance evaluation must process requests and report violations.

## Requirements

### Requirement: Evaluate Request Against All Policies
The `check_policy_compliance` tool SHALL evaluate each purchase request against all eight policies defined in `mock_data/policies.json`.

#### Scenario: Full policy sweep completes
- **WHEN** a valid purchase request is submitted
- **THEN** the tool evaluates POL-001 through POL-008 in one pass

### Requirement: Return Structured Policy Violations
The tool MUST return `violations` as a list and include one entry per violated policy.

Each violation entry MUST include:
- `policy_id`
- `violated_rule`
- `forced_decision` constrained to `deny` or `escalate`

#### Scenario: Violations detected
- **WHEN** one or more policy rules are violated
- **THEN** the tool returns all violations with required fields and decision constraints

#### Scenario: No violations detected
- **WHEN** no policy rules are violated
- **THEN** the tool returns an empty `violations` list

### Requirement: Map Policy Outcomes to Forced Decisions
The tool SHALL map each violated policy to a forced decision according to policy intent.

#### Scenario: Deny policy triggered
- **WHEN** a policy with deny outcome semantics is violated
- **THEN** the violation entry `forced_decision` is `deny`

#### Scenario: Escalate policy triggered
- **WHEN** a policy with escalate outcome semantics is violated
- **THEN** the violation entry `forced_decision` is `escalate`

### Requirement: Support Multiple Violations Per Request
The tool MUST return all applicable violations and MUST NOT stop evaluation after the first failure.

#### Scenario: Multiple policies violated
- **WHEN** a request violates more than one policy
- **THEN** the tool returns each violated policy in the `violations` list

### Requirement: Provide Deterministic Error Reporting
The tool MUST return structured error context when policy data is unavailable or malformed.

#### Scenario: Policy source unavailable
- **WHEN** policy records cannot be loaded through the loader layer
- **THEN** the tool returns a structured error payload for rationale inclusion by the agent
