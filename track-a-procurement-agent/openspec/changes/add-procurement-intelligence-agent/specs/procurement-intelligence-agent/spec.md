## ADDED Requirements

### Requirement: Agent returns structured procurement recommendation
The system MUST accept a purchase request represented by PurchaseRequest and produce a ProcurementRecommendation output constrained to decision values approve, deny, or escalate, with a non-empty rationale.

#### Scenario: Valid request yields constrained structured response
- **WHEN** a valid purchase request is evaluated by the procurement intelligence agent
- **THEN** the returned recommendation MUST conform to ProcurementRecommendation with decision in {approve, deny, escalate} and rationale length greater than zero

### Requirement: Agent SHALL invoke four domain checks per request
The system MUST execute budget sufficiency, vendor duplication, policy compliance, and risk assessment checks for each evaluated request using check_budget, check_vendor_duplication, check_policy_compliance, and assess_risk.

#### Scenario: All check tools are invoked for a request
- **WHEN** the agent evaluates a purchase request
- **THEN** all four check tools MUST be called and their outputs incorporated into decision reasoning

### Requirement: Decision precedence SHALL be deterministic
The system MUST apply decision priority in this exact order: escalate over deny over approve.

#### Scenario: Escalation and denial signals both present
- **WHEN** one or more checks produce an escalation signal and one or more checks produce a denial signal
- **THEN** the final decision MUST be escalate

#### Scenario: Denial signal without escalation
- **WHEN** one or more checks produce a denial signal and no checks produce escalation signals
- **THEN** the final decision MUST be deny

#### Scenario: No escalation or denial signals
- **WHEN** all checks pass without escalation or denial signals
- **THEN** the final decision MUST be approve

### Requirement: Tool failures MUST be reflected in rationale
The system MUST catch individual tool execution errors and include error context in the recommendation rationale instead of silently ignoring failures.

#### Scenario: One tool raises an exception during evaluation
- **WHEN** any check tool fails while processing a request
- **THEN** the recommendation rationale MUST include a clear error statement identifying the failed check and failure context

### Requirement: Data access SHALL use loader abstraction
The system MUST load mock procurement datasets via data/loader.py and MUST NOT read mock_data files directly from agent or tool modules.

#### Scenario: Agent and tools require domain reference data
- **WHEN** the evaluation flow needs budgets, policies, vendors, or request context
- **THEN** data retrieval MUST occur through data/loader.py APIs only
