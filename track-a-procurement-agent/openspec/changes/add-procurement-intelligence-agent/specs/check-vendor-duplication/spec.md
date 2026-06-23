## ADDED Requirements

### Requirement: check_vendor_duplication SHALL detect active same-category contract conflicts
The system MUST provide a check_vendor_duplication tool that accepts vendor_id and category and determines whether another active contracted vendor exists in the same purchase category.

#### Scenario: Conflicting active vendor exists in the same category
- **WHEN** check_vendor_duplication is called with a vendor and category where at least one different vendor has an active contract for that category
- **THEN** the result MUST identify a duplication conflict

### Requirement: check_vendor_duplication SHALL return conflicting vendor details
The check_vendor_duplication tool MUST return the list of conflicting vendor IDs and contract details for each conflicting vendor.

#### Scenario: Duplication response includes required conflict fields
- **WHEN** check_vendor_duplication returns one or more conflicts
- **THEN** each conflict entry MUST include vendor_id and contract details sufficient for reviewer verification

### Requirement: check_vendor_duplication SHALL encode POL-001 threshold deny behavior
The system MUST apply POL-001 logic so that when a same-category active-contract conflict exists and the request amount is greater than 25000.00, the tool output indicates a deny-level policy conflict.

#### Scenario: Conflict above POL-001 threshold forces deny
- **WHEN** check_vendor_duplication finds an active same-category conflict and the request amount is greater than 25000.00
- **THEN** the result MUST indicate a deny policy condition under POL-001

### Requirement: check_vendor_duplication SHALL avoid false conflicts
The check_vendor_duplication tool MUST exclude the requested vendor itself from the conflict list and MUST ignore vendors without active contracts.

#### Scenario: Only requesting vendor or non-active vendors found
- **WHEN** no other active contracted vendor exists for the category
- **THEN** the result MUST return no conflicts
