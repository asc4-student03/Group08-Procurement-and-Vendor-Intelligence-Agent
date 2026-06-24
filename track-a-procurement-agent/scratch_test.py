"""Temporary manual agent test script. Delete before Session 4."""

import asyncio

from agent import agent
from models import PurchaseRequest


TEST_REQUESTS = [
    PurchaseRequest(
        request_id="REQ-001",
        requestor="j.smith@fedex.com",
        cost_center_id="CC-001",
        vendor_name="BlueSky Cloud Solutions",
        vendor_id="V-002",
        category="software_licenses",
        item_description="Standard office paper and toner",
        quantity=1,
        unit_price=1250.00,
        total_amount=1250.00,
    ),
    PurchaseRequest(
        request_id="REQ-009",
        requestor="p.harrington@fedex.com",
        cost_center_id="CC-005",
        vendor_name="Summit Catering Co.",
        vendor_id="V-017",
        category="catering",
        item_description="Executive leadership offsite lunch service",
        quantity=1,
        unit_price=3200.00,
        total_amount=3200.00,
    ),
    PurchaseRequest(
        request_id="REQ-011",
        requestor="f.osei@fedex.com",
        cost_center_id="CC-001",
        vendor_name="Vertex Consulting Group",
        vendor_id="V-006",
        category="professional_services",
        item_description="Change management consulting",
        quantity=1,
        unit_price=35000.00,
        total_amount=35000.00,
    ),
    PurchaseRequest(
        request_id="REQ-014",
        requestor="j.mcallister@fedex.com",
        cost_center_id="CC-006",
        vendor_name="Orion Data Systems",
        vendor_id="V-016",
        category="hardware",
        item_description="Replacement server infrastructure",
        quantity=1,
        unit_price=47500.00,
        total_amount=47500.00,
    ),
]


async def main() -> None:
    for request in TEST_REQUESTS:
        result = await agent.run(str(request))
        recommendation = result.data
        print(f"{request.request_id}: decision={recommendation.decision}")
        print(f"rationale={recommendation.rationale}")
        print("-" * 80)


asyncio.run(main())
