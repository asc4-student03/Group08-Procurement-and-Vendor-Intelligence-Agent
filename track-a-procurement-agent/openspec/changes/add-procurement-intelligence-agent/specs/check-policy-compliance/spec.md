## ADDED Requirements

### Requirement: check_policy_compliance SHALL evaluate all policy rules
The system MUST provide a check_policy_compliance tool that evaluates each purchase request against all eight policies defined in mock_data/policies.json using loader-based access.

#### Scenario: Request is evaluated against all eight policies
- **WHEN** check_policy_compliance is called with a purchase request
- **THEN** the evaluation MUST consider policy IDs POL-001 through POL-008 before returning a result

### Requirement: check_policy_compliance SHALL return structured violations
The check_policy_compliance tool MUST return a list of violated policies, if any, and each violation MUST include policy_id, rule_description, and forced_decision.

#### Scenario: Policy violations are present
- **WHEN** one or more policies are violated during evaluation
- **THEN** each returned violation MUST include policy_id, rule_description, and forced_decision

### Requirement: check_policy_compliance SHALL constrain forced decisions
For each policy violation, forced_decision MUST be either deny or escalate.

#### Scenario: Violation includes decision directive
- **WHEN** check_policy_compliance returns a violation entry
- **THEN** the forced_decision field MUST be deny or escalate only

### Requirement: check_policy_compliance SHALL report no-violation outcomes
If no policy is violated, the tool MUST return an empty violations list and indicate no active policy severity.

#### Scenario: Clean request has no policy violations
- **WHEN** check_policy_compliance evaluates a request that violates no policies
- **THEN** the result MUST contain an empty violations list and no deny or escalate policy directive
