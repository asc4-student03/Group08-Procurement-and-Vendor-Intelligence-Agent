## ADDED Requirements

### Requirement: PurchaseRequest field contract
The system MUST define a `PurchaseRequest` model that represents request input fields from `mock_data/requests.json` as follows:
- Required model fields: `request_id`, `requestor`, `cost_center_id`, `vendor_name`, `vendor_id`, `category`, `item_description`, `quantity`, `unit_price`, `total_amount`.
- Dataset reference-only fields: `expected_outcome`, `outcome_reason` MUST be documented as test-oracle fields and MUST NOT be required to construct `PurchaseRequest`.

#### Scenario: Operational request fields are present
- **WHEN** a purchase payload includes the 10 operational fields
- **THEN** the payload MUST be accepted as a valid `PurchaseRequest`

#### Scenario: Reference-only fields are omitted
- **WHEN** `expected_outcome` and `outcome_reason` are absent from input payload
- **THEN** `PurchaseRequest` validation MUST still succeed

### Requirement: PurchaseRequest numeric validators
The system MUST apply Pydantic validators for numeric safety on `PurchaseRequest`.

#### Scenario: Positive numeric constraint enforcement
- **WHEN** `quantity <= 0` or `unit_price <= 0` or `total_amount <= 0`
- **THEN** model validation MUST fail with field-specific validation errors

#### Scenario: Amount arithmetic consistency check
- **WHEN** `total_amount` materially differs from `quantity * unit_price`
- **THEN** model validation SHOULD fail or normalize based on a documented tolerance rule

### Requirement: ProcurementRecommendation output contract
The system MUST define a `ProcurementRecommendation` model containing `request_id`, `decision`, and `rationale`.

#### Scenario: Decision domain is constrained
- **WHEN** the agent produces a recommendation
- **THEN** `decision` MUST be exactly one of `approve`, `deny`, or `escalate`

#### Scenario: Invalid decision value is rejected
- **WHEN** `decision` is any value outside `approve|deny|escalate`
- **THEN** output validation MUST fail

#### Scenario: Rationale is required and non-empty
- **WHEN** `rationale` is missing, empty, or whitespace-only
- **THEN** output validation MUST fail and the recommendation MUST NOT be treated as valid
