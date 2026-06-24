## 1. Risk Tool Implementation

- [x] 1.1 Implement `assess_risk(vendor_id: str)` in `tools/risk_assessment.py` using `data/loader.py`.
- [x] 1.2 Ensure output includes required keys and risk mapping for low/medium/high/critical.
- [x] 1.3 Handle unknown vendor and data-unavailable cases with `error` and conservative risk output.

## 2. Verification

- [x] 2.1 Add tests in `tests/test_risk_assessment.py` for all required scenarios.
- [x] 2.2 Run `openspec validate add-risk-assessment-tool` and resolve findings.
