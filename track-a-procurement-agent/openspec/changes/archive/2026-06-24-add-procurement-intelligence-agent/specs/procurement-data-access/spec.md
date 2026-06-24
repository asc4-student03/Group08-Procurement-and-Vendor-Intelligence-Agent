## ADDED Requirements

### Requirement: Centralized mock data loading
The system SHALL access all mock procurement datasets through `data/loader.py` and SHALL NOT read files in `mock_data/` directly from tool or agent modules.

#### Scenario: Tool loads budget data through loader
- **WHEN** the budget check executes
- **THEN** it SHALL obtain budget records via a loader function rather than direct file I/O to `mock_data/budgets.json`

#### Scenario: Agent and tools avoid direct mock_data access
- **WHEN** static analysis or code review inspects agent and tool modules
- **THEN** no direct JSON file reads from `mock_data/` SHALL be present outside `data/loader.py`

### Requirement: Loader provides canonical dataset interfaces
The system SHALL expose loader functions for budgets, vendors, policies, and requests with predictable list-of-record outputs.

#### Scenario: Requested dataset exists
- **WHEN** a loader function is called for an available dataset
- **THEN** it SHALL return parsed records in a consistent structure usable by tools and tests

#### Scenario: Requested dataset is unavailable
- **WHEN** a required mock data file is missing or unreadable
- **THEN** the loader path SHALL raise a detectable error that can be handled by calling logic
