## Why

The root implementation is missing the `assess_risk` tool that is required by the procurement checks. This leaves an open gap in vendor risk screening and blocks full tool-level coverage.

## What Changes

- Add root `tools/risk_assessment.py` implementing `assess_risk(vendor_id: str)`.
- Add root `tests/test_risk_assessment.py` covering required risk-level mapping and error behavior.
- Keep data access centralized through `data/loader.py`.

## Capabilities

### New Capabilities
- None.

### Modified Capabilities
- `risk-assessment-tool`: Implement and verify the defined output contract and risk mapping scenarios.

## Impact

- Affected code: `tools/risk_assessment.py`, `tests/test_risk_assessment.py`
- No dependency changes
- No API surface changes beyond adding the missing tool module
