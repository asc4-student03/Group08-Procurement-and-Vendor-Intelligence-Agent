# Request Traceability Matrix

## Scope

This matrix manually traces each sample request in mock_data/requests.json through the four tool specifications:
- check_budget
- check_vendor_duplication
- check_policy_compliance
- assess_risk

By spec, all four tools are called for every valid request.

## Decision precedence

Final decision precedence is:
1. escalate
2. deny
3. approve

## Table

| Request | Tools Called | check_budget return | check_vendor_duplication return | check_policy_compliance return | assess_risk return | Decision rule applied | Final decision | Agent rationale text (expected) |
|---|---|---|---|---|---|---|---|---|
| REQ-001 | All 4 tools | signal=approve; summary=Within budget; details={remaining:187550, amount:24000} | signal=approve; conflicts=[V-008 (CTR-2023-0304 active)]; deny_eligible=false (amount <= 25000) | signal=approve; violations=[] | signal=approve; profile={compliance_flag:false, contract_status:active, risk_level:low} | No escalate or deny signals present | approve | Request is within CC-001 budget; no policy violations forcing deny/escalate; vendor risk is low. |
| REQ-002 | All 4 tools | signal=approve; summary=Within budget; details={remaining:210800, amount:38400} | signal=approve; conflicts=[V-016 (CTR-2024-0188 active)]; deny_eligible=false because selected vendor V-005 is also actively contracted | signal=approve; violations=[] (POL-002 treated as process note) | signal=approve; profile={compliance_flag:false, contract_status:active, risk_level:low} | No escalate or deny signals present | approve | Amount is within budget and selected vendor is contracted for hardware; no forced policy violation and risk is low. |
| REQ-003 | All 4 tools | signal=approve; summary=Within budget; details={remaining:348700, amount:8500} | signal=approve; conflicts=[] | signal=approve; violations=[] | signal=approve; profile={compliance_flag:false, contract_status:active, risk_level:low} | No escalate or deny signals present | approve | Request is budget-safe, no duplication conflict, no policy violation, and vendor risk is low. |
| REQ-004 | All 4 tools | signal=approve; summary=Within budget; details={remaining:83600, amount:9960} | signal=approve; conflicts=[] | signal=approve; violations=[] | signal=approve; profile={compliance_flag:false, contract_status:active, risk_level:low} | No escalate or deny signals present | approve | Budget check passes and there are no policy or vendor-risk conditions requiring deny/escalate. |
| REQ-005 | All 4 tools | signal=approve; summary=Within budget; details={remaining:187550, amount:14200} | signal=approve; conflicts=[] | signal=approve; violations=[] (POL-002 treated as process note) | signal=approve; profile={compliance_flag:false, contract_status:active, risk_level:low} | No escalate or deny signals present | approve | Active contracted vendor, budget available, and no forced policy violation; recommendation is approve. |
| REQ-006 | All 4 tools | signal=deny; summary=Budget overage; details={remaining:6900, amount:11200, overage:4300} | signal=approve; conflicts=[] | signal=deny; violations=[{policy_id:POL-008, forced_decision:deny}] | signal=approve; profile={compliance_flag:false, contract_status:active, risk_level:low} | Deny signal present and no escalate signal present | deny | Request exceeds CC-003 remaining budget and violates POL-008; no higher-priority escalation override exists. |
| REQ-007 | All 4 tools | signal=approve; summary=Within budget; details={remaining:8550, amount:5400} | signal=approve; conflicts=[] | signal=deny; violations=[{policy_id:POL-005, forced_decision:deny, violated_rule:expired contract vendor}] | signal=deny; profile={compliance_flag:false, contract_status:expired, risk_level:high} | Deny signal present and no escalate signal present | deny | Vendor contract is expired, triggering POL-005 denial; budget status does not override policy denial. |
| REQ-008 | All 4 tools | signal=approve; summary=Within budget; details={remaining:210800, amount:28500} | signal=deny; conflicts=[V-001 (CTR-2024-0041 active), V-003 (CTR-2023-0198 active)]; deny_eligible=true under POL-001 (>25000 with non-contracted vendor) | signal=deny; violations=[{policy_id:POL-001, forced_decision:deny}] | signal=approve; profile={compliance_flag:false, contract_status:none, risk_level:medium} | Deny signal present and no escalate signal present | deny | Office supplies request above POL-001 threshold uses a non-contracted vendor while active contracted alternatives exist. |
| REQ-009 | All 4 tools | signal=approve; summary=Within budget; details={remaining:5500, amount:2550} | signal=approve; conflicts=[] | signal=deny; violations=[{policy_id:POL-004, forced_decision:deny, violated_rule:catering prohibited}] | signal=approve; profile={compliance_flag:false, contract_status:none, risk_level:medium} | Deny signal present and no escalate signal present | deny | Catering category is prohibited by POL-004 and must be denied regardless of budget or amount. |
| REQ-010 | All 4 tools | signal=deny; summary=Budget overage; details={remaining:37900, amount:49600, overage:11700} | signal=approve; conflicts=[] | signal=deny; violations=[{policy_id:POL-008, forced_decision:deny}] | signal=escalate; profile={compliance_flag:false, contract_status:active, risk_level:high, governance_near_director_threshold:true} | Escalate signal present, so escalate overrides deny | escalate | Request is over budget, but governance risk is elevated due near-director-threshold exposure; precedence escalates for human review. |
| REQ-011 | All 4 tools | signal=approve; summary=Within budget; details={remaining:187550, amount:35000} | signal=approve; conflicts=[] | signal=escalate; violations=[{policy_id:POL-006, forced_decision:escalate, violated_rule:compliance-flagged vendor}] | signal=escalate; profile={compliance_flag:true, contract_status:active, risk_level:critical} | Escalate signal present | escalate | Vendor has an active compliance flag, requiring Legal/Compliance escalation under POL-006. |
| REQ-012 | All 4 tools | signal=approve; summary=Within budget; details={remaining:51250, amount:4620} | signal=approve; conflicts=[] | signal=approve; violations=[] | signal=approve; profile={compliance_flag:false, contract_status:active, risk_level:low} | No escalate or deny signals present | approve | Staffing request is within budget, uses enterprise contracted vendor, and has no policy violations. |
| REQ-013 | All 4 tools | signal=approve; summary=Within budget; details={remaining:18000, amount:14400} | signal=approve; conflicts=[] | signal=approve; violations=[] (training not restricted by single-source policy) | signal=approve; profile={compliance_flag:false, contract_status:none, risk_level:medium} | No escalate or deny signals present | approve | Training request is budget-compliant with no deny/escalate policy triggers; risk profile does not force escalation. |
| REQ-014 | All 4 tools | signal=approve; summary=Within budget; details={remaining:348700, amount:47500} | signal=approve; conflicts=[V-005 (CTR-2025-0012 active)]; deny_eligible=false because selected vendor V-016 is also actively contracted | signal=approve; violations=[] (POL-003 strict trigger not met at <50000) | signal=escalate; profile={compliance_flag:false, contract_status:active, risk_level:high, governance_near_director_threshold:true} | Escalate signal present | escalate | Amount is near director threshold and routed for governance escalation despite no hard policy deny. |
| REQ-015 | All 4 tools | signal=approve; summary=Within budget; details={remaining:5500, amount:1200} | signal=approve; conflicts=[] | signal=approve; violations=[] | signal=escalate; profile={compliance_flag:false, contract_status:none, risk_level:medium, budget_headroom_tight:true} | Escalate signal present | escalate | No hard deny policy is triggered, but tight budget headroom and non-contracted vendor context drive conservative escalation. |

## Notes for Session 4 assertions

- This table normalizes final outputs to the required decision set: approve, deny, escalate.
- REQ-015 is labeled ambiguous in fixture data; for contract-compliant agent tests, this matrix treats it as escalate under conservative risk handling.
- For REQ-010 and REQ-014, escalation comes from risk/governance signals and wins by precedence over deny/approve signals.
