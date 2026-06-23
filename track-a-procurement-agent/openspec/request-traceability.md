# Request Traceability

## Scope and assumptions

- This table traces all sample requests in `mock_data/requests.json` through the four tool specs.
- Tools called for every request: `check_budget`, `check_vendor_duplication`, `check_policy_compliance`, `assess_risk`.
- Decision precedence used: `escalate > deny > approve`.
- Where policy metadata is informational (for example POL-002 manager-approval workflow note), only forced `deny`/`escalate` outcomes are treated as decision triggers.

## Traceability table

| Request | Tools called | check_budget (expected) | check_vendor_duplication (expected) | check_policy_compliance (expected) | assess_risk (expected) | Decision rule | Expected outcome | Rationale text the agent should produce |
|---|---|---|---|---|---|---|---|---|
| REQ-001 | All four | within_budget=true, remaining=187550, overage=0 | violation=false (amount <= 25000) | no forced violation | risk_level=low | Approve rule | approve | Budget is sufficient in CC-001, no single-source conflict applies at this amount, no forced policy action exists, and vendor risk is low. |
| REQ-002 | All four | within_budget=true, remaining=210800, overage=0 | violation=false (contracted hardware vendor) | no forced violation | risk_level=low | Approve rule | approve | Request is within CC-004 budget, vendor duplication check is clean for a contracted hardware vendor, and no deny/escalate policy trigger is present. |
| REQ-003 | All four | within_budget=true, remaining=348700, overage=0 | violation=false (amount <= 25000) | no forced violation | risk_level=low | Approve rule | approve | CC-006 budget covers the request, there is no duplication or policy trigger, and risk is low. |
| REQ-004 | All four | within_budget=true, remaining=83600, overage=0 | violation=false (amount <= 25000) | no forced violation | risk_level=low | Approve rule | approve | Amount is within CC-008 remaining budget and no policy, duplication, or risk escalation condition applies. |
| REQ-005 | All four | within_budget=true, remaining=187550, overage=0 | violation=false (amount <= 25000) | no forced violation | risk_level=low | Approve rule | approve | The purchase is within budget, no single-source threshold breach exists, and there are no policy violations or elevated risk conditions. |
| REQ-006 | All four | within_budget=false, remaining=6900, overage=4300 | violation=false (amount <= 25000) | violation includes POL-008 forced_decision=deny | risk_level=low | Deny rule (no escalate trigger) | deny | Request exceeds CC-003 remaining budget by 4300, triggering budget-overage denial under policy with no higher-priority escalation trigger. |
| REQ-007 | All four | within_budget=true, remaining=8550, overage=0 | violation=false (amount <= 25000) | violation includes POL-005 forced_decision=deny | risk_level=high (expired contract) | Deny rule | deny | Vendor contract is expired, policy requires denial, and risk is high due to expired contract status. |
| REQ-008 | All four | within_budget=true, remaining=210800, overage=0 | violation=true, conflicting_vendor_ids include V-001 and V-003 | violation includes POL-001 forced_decision=deny | risk_level=medium (no contract) | Deny rule | deny | Amount is above POL-001 threshold and the requested vendor is non-contracted while active contracted office-supplies vendors exist, so the request is denied. |
| REQ-009 | All four | within_budget=true, remaining=5500, overage=0 | violation=false (amount <= 25000) | violation includes POL-004 forced_decision=deny | risk_level=medium (no contract) | Deny rule | deny | Category is catering, which is prohibited by policy, so the request must be denied regardless of budget status. |
| REQ-010 | All four | within_budget=false, remaining=37900, overage=11700 | violation=false (no conflicting active fleet-part vendor) | violation includes POL-003 forced_decision=escalate (near director threshold); may also include POL-008 deny | risk_level=low | Escalate priority over deny | escalate | The request is over budget and within near-director-threshold policy range, so escalation is required and takes priority over denial conditions. |
| REQ-011 | All four | within_budget=true, remaining=187550, overage=0 | violation=false (no conflicting active professional-services vendor) | violation includes POL-006 forced_decision=escalate | risk_level=critical (compliance flag) | Escalate rule | escalate | Vendor has an active compliance flag and policy requires legal/compliance review, so the request is escalated. |
| REQ-012 | All four | within_budget=true, remaining=51250, overage=0 | violation=false (amount <= 25000) | no forced violation (staffing vendor is contracted) | risk_level=low | Approve rule | approve | Budget is sufficient, staffing vendor is contracted, and no deny/escalate policy trigger or elevated risk condition is present. |
| REQ-013 | All four | within_budget=true, remaining=18000, overage=0 | violation=false (amount <= 25000) | no forced violation | risk_level=medium (no contract) | Approve rule | approve | Request is within budget and has no forced policy or duplication violation; medium vendor risk alone does not force denial or escalation. |
| REQ-014 | All four | within_budget=true, remaining=348700, overage=0 | violation=false (contracted hardware vendor) | violation includes POL-003 forced_decision=escalate (near director threshold) | risk_level=low | Escalate rule | escalate | Although budget and baseline risk are acceptable, the amount is within the near-director threshold range and must be escalated. |
| REQ-015 | All four | within_budget=true, remaining=5500, overage=0 | violation=false (amount <= 25000; category not single-source constrained) | no forced violation | risk_level=medium (no contract) | Approve rule by strict precedence; optional conservative escalate posture | ambiguous | No mandatory deny/escalate trigger appears, so strict rules produce approve, but a conservative governance posture may escalate due to low remaining budget headroom and non-contracted vendor status. |

## Outcome coverage summary

- Approve: REQ-001, REQ-002, REQ-003, REQ-004, REQ-005, REQ-012, REQ-013
- Deny: REQ-006, REQ-007, REQ-008, REQ-009
- Escalate: REQ-010, REQ-011, REQ-014
- Ambiguous: REQ-015
