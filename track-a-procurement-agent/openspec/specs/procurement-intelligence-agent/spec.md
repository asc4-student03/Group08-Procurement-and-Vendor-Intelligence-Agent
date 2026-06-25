## Purpose
Define end-to-end procurement intelligence capability contracts across models, tools, and decision synthesis.

## Requirements

### Requirement: Validate Purchase Request Input
The system SHALL validate each incoming purchase request against the `PurchaseRequest` Pydantic v2 model before running any procurement checks.

The `PurchaseRequest` model MUST represent the following request fields from domain input:
- `request_id` (string)
- `requestor` (string)
- `cost_center_id` (string)
- `vendor_name` (string)
- `vendor_id` (string)
- `category` (string)
- `item_description` (string)
- `quantity` (integer)
- `unit_price` (number)
- `total_amount` (number)

Model validation MUST include the following numeric constraints:
- `quantity` MUST be greater than 0.
- `unit_price` MUST be greater than 0.
- `total_amount` MUST be greater than 0.
- `total_amount` SHOULD match `quantity * unit_price` within a configured currency tolerance.

#### Scenario: Request matches schema
- **WHEN** a request includes all required `PurchaseRequest` fields with valid types
- **THEN** the system accepts the request and proceeds to tool evaluation

#### Scenario: Request violates schema
- **WHEN** a request is missing required fields or has invalid field types
- **THEN** the system returns an `escalate` recommendation with rationale that identifies input validation failure

### Requirement: Produce Structured Recommendation Output
The system SHALL produce recommendations using the `ProcurementRecommendation` Pydantic v2 model with `decision` constrained to `approve`, `deny`, or `escalate` and a non-empty `rationale`.

The `ProcurementRecommendation` model MUST contain:
- `decision` as an enum constrained to exactly `approve`, `deny`, or `escalate`
- `rationale` as a non-empty string

#### Scenario: Valid recommendation emitted
- **WHEN** tool evaluation completes for a valid request
- **THEN** the recommendation output conforms to `ProcurementRecommendation`, uses an allowed decision value, and includes a non-empty rationale

#### Scenario: Unsupported decision prevented
- **WHEN** any internal branch attempts to emit a decision outside `approve`, `deny`, or `escalate`
- **THEN** the system prevents emission of that value and returns only a contract-compliant decision

### Requirement: Run Required Procurement Checks
The system SHALL evaluate each request using all four checks: `check_budget`, `check_vendor_duplication`, `check_policy_compliance`, and `assess_risk`.

Each tool contract MUST be defined with name, inputs, return shape, and error behavior:
- `check_budget`
	- Inputs: `cost_center_id`, `total_amount`
	- Return shape: `{ "signal": "approve|deny|escalate", "summary": string, "details": object }`
	- Error behavior: MUST raise a typed tool error or return a structured failure payload captured by the agent rationale path.
- `check_vendor_duplication`
	- Inputs: `vendor_id`, `category`, `total_amount`
	- Return shape: `{ "signal": "approve|deny|escalate", "summary": string, "details": object }`
	- Error behavior: MUST raise a typed tool error or return a structured failure payload captured by the agent rationale path.
- `check_policy_compliance`
	- Inputs: `category`, `vendor_id`, `total_amount`, `quantity`
	- Return shape: `{ "signal": "approve|deny|escalate", "summary": string, "details": object }`
	- Error behavior: MUST raise a typed tool error or return a structured failure payload captured by the agent rationale path.
- `assess_risk`
	- Inputs: `vendor_id`
	- Return shape: `{ "signal": "approve|deny|escalate", "summary": string, "details": object }`
	- Error behavior: MUST raise a typed tool error or return a structured failure payload captured by the agent rationale path.

#### Scenario: All tools execute successfully
- **WHEN** a valid request is submitted
- **THEN** the system invokes all four tools and captures each result for decision synthesis

#### Scenario: Multiple policy signals returned
- **WHEN** tool results include more than one outcome signal
- **THEN** the system preserves all signals for precedence resolution and rationale composition

### Requirement: Apply Decision Priority Rule
The system SHALL determine final recommendation decision by applying priority `escalate > deny > approve` across aggregated tool signals.

#### Scenario: Escalate and deny signals both present
- **WHEN** at least one tool signals escalate and at least one tool signals deny
- **THEN** the final decision is `escalate`

#### Scenario: Deny and approve signals present without escalate
- **WHEN** one or more tools signal deny and no tools signal escalate
- **THEN** the final decision is `deny`

#### Scenario: Only approve-compatible signals present
- **WHEN** no tool signals escalate or deny
- **THEN** the final decision is `approve`

#### Scenario: All tools fail
- **WHEN** every tool invocation fails and no successful signal is available
- **THEN** the final decision is `escalate` and rationale includes explicit failure context for human review

### Requirement: Surface Tool Errors In Rationale
The system SHALL catch tool-level exceptions and include error context in the recommendation rationale instead of silently ignoring failures.

#### Scenario: One tool fails and others succeed
- **WHEN** a tool raises an exception during evaluation
- **THEN** the system continues evaluation, produces a recommendation, and includes the tool failure summary in rationale text

#### Scenario: Multiple tools fail
- **WHEN** two or more tools raise exceptions in one evaluation
- **THEN** the system includes all encountered tool errors in rationale text and still returns a contract-valid recommendation

### Requirement: Use Loader-Mediated Domain Data Access
The system SHALL access requests, policies, vendors, and budgets through `data/loader.py` pathways and SHALL NOT read files under `mock_data/` directly from agent or tool logic.

#### Scenario: Tool needs domain records
- **WHEN** any tool requires policy, vendor, budget, or request context
- **THEN** the tool obtains records via `data/loader.py` interfaces

#### Scenario: Direct file-read attempt in business logic
- **WHEN** agent or tool code attempts to read `mock_data/` directly
- **THEN** the implementation is considered non-compliant with this capability requirement