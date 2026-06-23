## ADDED Requirements

### Requirement: Agent returns structured procurement recommendation
The system SHALL accept a purchase request and return a structured recommendation object containing request identifier, decision, and rationale.

#### Scenario: Recommendation schema is enforced
- **WHEN** a purchase request is evaluated
- **THEN** the system returns a recommendation object with fields request_id, decision, and rationale

#### Scenario: Decision values are constrained
- **WHEN** a recommendation is generated
- **THEN** decision MUST be exactly one of approve, deny, or escalate

#### Scenario: Rationale is mandatory
- **WHEN** a recommendation is generated
- **THEN** rationale MUST be a non-empty string

### Requirement: Agent executes four procurement checks per request
The system SHALL execute budget, vendor duplication, policy compliance, and risk assessment checks for every purchase request before resolving a final decision.

#### Scenario: All checks execute on every request
- **WHEN** any purchase request is evaluated
- **THEN** the system invokes check_budget, check_vendor_duplication, check_policy_compliance, and assess_risk

#### Scenario: Check outputs are available for rationale composition
- **WHEN** the final recommendation is formed
- **THEN** rationale includes relevant findings from all checks that influence the outcome

### Requirement: Decision precedence is deterministic
The system SHALL resolve recommendation outcomes using strict precedence where escalate overrides deny and deny overrides approve.

#### Scenario: Escalate and deny signals both present
- **WHEN** at least one check requires escalation and another indicates denial
- **THEN** the final decision is escalate

#### Scenario: Deny signal present without escalation
- **WHEN** no escalation signal exists and one or more deny conditions are true
- **THEN** the final decision is deny

#### Scenario: No blocking signals present
- **WHEN** no escalation or deny conditions are triggered
- **THEN** the final decision is approve

### Requirement: Tool and data failures are fail-safe
The system SHALL treat tool execution or data access failures as escalation conditions and SHALL disclose the failure context in rationale.

#### Scenario: Tool returns error context
- **WHEN** any check reports an error or required data is unavailable
- **THEN** the final decision is escalate

#### Scenario: Error details are visible to reviewer
- **WHEN** escalation occurs due to tool or data failure
- **THEN** rationale explicitly describes which check failed and the reported error context

### Requirement: Domain data access is centralized through loader APIs
The system SHALL retrieve mock domain data through loader functions and SHALL NOT read fixture files directly from tool modules.

#### Scenario: Tool reads vendor and policy context
- **WHEN** a tool requires vendor, budget, or policy data
- **THEN** it accesses data through loader functions in data loader module

#### Scenario: Direct fixture reads are disallowed in tools
- **WHEN** procurement tool modules are reviewed
- **THEN** they do not contain direct file reads from fixture directories
