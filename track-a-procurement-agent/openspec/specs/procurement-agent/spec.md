## Purpose
Define orchestration behavior, output contract, and decision precedence for the procurement decision agent.

## Requirements

### Requirement: Agent Input And Output Contracts
The system SHALL define `agent.py` to accept a `PurchaseRequest` input and return a `ProcurementRecommendation` output.

Input contract:
- `PurchaseRequest` from `models.py`

Output contract:
- `ProcurementRecommendation` from `models.py`
- `decision` MUST be exactly one of `approve`, `deny`, or `escalate`
- `rationale` MUST be a non-empty string

#### Scenario: Valid request yields typed recommendation
- **WHEN** the agent receives a valid `PurchaseRequest`
- **THEN** it returns a `ProcurementRecommendation` with contract-valid `decision` and non-empty `rationale`

#### Scenario: Invalid output is prevented
- **WHEN** internal logic attempts to emit unsupported decision values or empty rationale
- **THEN** the agent MUST prevent emission and return only contract-valid output

### Requirement: Agent Executes All Four Tools
The system SHALL execute all four procurement tools for every request evaluation.

Required tools:
- `check_budget` from `tools/budget.py`
- `check_vendor_duplication` from `tools/vendor_duplication.py`
- `check_policy_compliance` from `tools/policy_compliance.py`
- `assess_risk` from `tools/risk_assessment.py`

#### Scenario: Request evaluation starts
- **WHEN** a valid request is accepted for recommendation
- **THEN** all four tools are invoked before final decision synthesis

#### Scenario: Early deny signal appears
- **WHEN** one tool indicates deny before other tools execute
- **THEN** the agent still executes remaining tools for complete evidence and rationale quality

### Requirement: Deterministic Decision Priority
The system SHALL resolve multiple tool outcomes using strict priority order `escalate > deny > approve`.

#### Scenario: Escalate and deny are both present
- **WHEN** at least one tool outcome indicates escalate and another indicates deny
- **THEN** the final decision MUST be `escalate`

#### Scenario: Deny present without escalate
- **WHEN** one or more tools indicate deny and none indicate escalate
- **THEN** the final decision MUST be `deny`

#### Scenario: No deny or escalate signals
- **WHEN** all tool outcomes are approve-compatible
- **THEN** the final decision MUST be `approve`

### Requirement: Tool Error Handling Is Safe And Explicit
The system SHALL surface tool failures in recommendation rationale and MUST NOT crash recommendation generation due to tool exceptions.

#### Scenario: One tool fails and others succeed
- **WHEN** any tool raises an exception or returns structured error context
- **THEN** the agent continues processing remaining tools and includes failure context in rationale

#### Scenario: Any tool error occurs
- **WHEN** one or more tool errors are present in a request evaluation
- **THEN** the final decision MUST be `escalate` to ensure safe human review

#### Scenario: All tools fail
- **WHEN** all tool calls fail for one request
- **THEN** the agent returns `escalate` with rationale that lists each tool failure context

### Requirement: System Prompt Enforces Agent Constraints
The system SHALL define a system prompt that constrains the agent's behavior for tool usage, precedence, and rationale evidence.

The prompt MUST instruct the agent to:
- use all four tools on every request
- follow precedence `escalate > deny > approve`
- include concrete evidence in rationale (for example policy IDs, budget values, duplication conflicts, risk findings, or tool errors)
- avoid unsupported decision labels

#### Scenario: Prompt-constrained recommendation
- **WHEN** the agent produces a recommendation
- **THEN** output reflects tool-driven evidence and prompt-defined decision constraints
