# Request Traceability Matrix (Session 4 Assertion Reference)

This matrix manually traces each sample request in mock_data/requests.json through the four tool specifications:
- check_budget
- check_vendor_duplication
- check_policy_compliance
- assess_risk

Assumed decision policy for assertions: escalate > deny > approve.

| Request | Tools Called | check_budget (expected) | check_vendor_duplication (expected) | check_policy_compliance (expected) | assess_risk (expected) | Decision Rule Applied | Final Decision | Agent Rationale Text (assertion target) |
|---|---|---|---|---|---|---|---|---|
| REQ-001 | All 4 | within_budget=true; remaining=187550; overage=0 | amount=24000 <= POL-001 threshold; no deny trigger | no violations; highest_severity=none | V-002 active + no flag -> low | No escalate/deny signals -> approve | approve | Approved: request is within CC-001 budget, no policy violations, no single-source deny condition, vendor risk is low. |
| REQ-002 | All 4 | within_budget=true; remaining=210800; overage=0 | category hardware; amount>25000; other active hardware vendor exists, but requested vendor is contracted so no forced deny | no violations; highest_severity=none | V-005 active + no flag -> low | No escalate/deny signals -> approve | approve | Approved: budget is sufficient, selected hardware vendor has active contract, no policy violation requiring deny/escalate, risk is low. |
| REQ-003 | All 4 | within_budget=true; remaining=348700; overage=0 | amount=8500 <= threshold; no deny trigger | no violations | V-007 active + no flag -> low | No escalate/deny signals -> approve | approve | Approved: request is within budget, no policy violations, no single-source restriction trigger, and vendor risk is low. |
| REQ-004 | All 4 | within_budget=true; remaining=83600; overage=0 | amount=9960 <= threshold; no deny trigger | no violations | V-013 active + no flag -> low | No escalate/deny signals -> approve | approve | Approved: budget check passed, policy checks are clean, no duplication deny trigger, and vendor risk is low. |
| REQ-005 | All 4 | within_budget=true; remaining=187550; overage=0 | amount=14200 <= threshold; no deny trigger | no violations | V-011 active + no flag -> low | No escalate/deny signals -> approve | approve | Approved: in-budget security purchase with active contracted vendor, no policy violations, and low vendor risk. |
| REQ-006 | All 4 | within_budget=false; remaining=6900; overage=4300 | amount=11200 <= threshold; no deny trigger | policy includes budget overage prohibition context; no separate escalate signal | V-007 active + no flag -> low | Deny signal present and no escalate signal -> deny | deny | Denied: request exceeds CC-003 remaining budget by 4300, which violates budget overage prohibition. |
| REQ-007 | All 4 | within_budget=true; remaining=8550; overage=0 | amount=5400 <= threshold; no deny trigger | POL-005 violated (expired contract) -> forced_decision=deny | V-010 contract expired -> high | Deny signal present and no escalate signal -> deny | deny | Denied: vendor contract is expired (POL-005), so purchase cannot proceed until renewal or vendor change. |
| REQ-008 | All 4 | within_budget=true; remaining=210800; overage=0 | amount=28500 > threshold; active contracted office_supplies vendors exist (V-001, V-003); non-contracted request vendor -> POL-001 deny condition | POL-001 violation -> forced_decision=deny | V-012 no contract -> medium | Deny signal present and no escalate signal -> deny | deny | Denied: request exceeds POL-001 threshold and uses non-contracted vendor while active contracted alternatives exist in office_supplies. |
| REQ-009 | All 4 | within_budget=true; remaining=5500; overage=0 | amount=2550 <= threshold; no deny trigger | POL-004 violated (catering prohibited) -> forced_decision=deny | V-017 no contract -> medium | Deny signal present and no escalate signal -> deny | deny | Denied: catering category is prohibited by policy (POL-004) regardless of amount or budget availability. |
| REQ-010 | All 4 | within_budget=false; remaining=37900; overage=11700 | category fleet_parts; no alternate active contracted conflict for deny | POL-003 near-threshold escalation signal (49600 is within 5% of 50000) -> forced_decision=escalate | V-013 active + no flag -> low | Escalate and deny both present -> escalate wins by precedence | escalate | Escalated: request is over budget and near director threshold, so escalation is required under precedence rules (escalate overrides deny). |
| REQ-011 | All 4 | within_budget=true; remaining=187550; overage=0 | no deny-level duplication trigger | POL-006 violated (compliance-flagged vendor) -> forced_decision=escalate | V-006 compliance_flag=true -> critical | Escalate signal present -> escalate | escalate | Escalated: vendor has active compliance flag (POL-006), requiring Legal/Compliance review before any approval. |
| REQ-012 | All 4 | within_budget=true; remaining=51250; overage=0 | amount=4620 <= threshold; no deny trigger | staffing quantity high but vendor is contracted; no violation | V-014 active + no flag -> low | No escalate/deny signals -> approve | approve | Approved: staffing request is in budget, contracted staffing vendor is used, no policy violation, and risk is low. |
| REQ-013 | All 4 | within_budget=true; remaining=18000; overage=0 | amount=14400 <= threshold; no deny trigger | no violations | V-015 no contract -> medium | No escalate/deny signals -> approve | approve | Approved: request is in budget with no policy violations and no deny/escalate trigger; medium vendor risk alone does not force escalation. |
| REQ-014 | All 4 | within_budget=true; remaining=348700; overage=0 | amount=47500 > threshold; another active hardware vendor exists, but requested vendor is contracted so no forced deny | POL-003 near-threshold escalation signal -> forced_decision=escalate | V-016 active + no flag -> low | Escalate signal present -> escalate | escalate | Escalated: amount is within 5% of director threshold, so director-awareness escalation is required despite passing budget and contract checks. |
| REQ-015 | All 4 | within_budget=true; remaining=5500; overage=0 | amount=1200 <= threshold; no deny trigger | no violations | V-004 no contract -> medium | No escalate/deny signals -> approve | approve | Approved under deterministic precedence: no policy, budget, or escalation trigger is present; rationale notes non-contracted vendor but no single-source restriction for courier_services. |

## Notes for Session 4 Assertions

- Every request should assert that all four tools were invoked.
- Decision precedence assertions should explicitly test REQ-010 (escalate over deny).
- Policy-specific assertions should include:
  - POL-004 deny (REQ-009)
  - POL-005 deny (REQ-007)
  - POL-006 escalate (REQ-011)
  - POL-001 deny condition (REQ-008)
- REQ-015 is marked ambiguous in source sample metadata, but under the current deterministic precedence contract it resolves to approve.
