"""Pydantic v2 model contracts for procurement request input and recommendation output."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator


class PurchaseRequest(BaseModel):
    """Operational purchase request fields.

    Test-oracle fields from dataset records (``expected_outcome`` and
    ``outcome_reason``) are intentionally not part of this model.
    """

    model_config = ConfigDict(str_strip_whitespace=True)

    request_id: str
    requestor: str
    cost_center_id: str
    vendor_name: str
    vendor_id: str
    category: str
    item_description: str
    quantity: int = Field(gt=0)
    unit_price: float = Field(gt=0)
    total_amount: float = Field(gt=0)

    @model_validator(mode="after")
    def validate_total_amount(self) -> "PurchaseRequest":
        """Enforce arithmetic consistency with a small tolerance for float values."""
        expected_total = self.quantity * self.unit_price
        tolerance = 0.01
        if abs(self.total_amount - expected_total) > tolerance:
            raise ValueError(
                "total_amount must match quantity * unit_price within a tolerance of 0.01"
            )
        return self


class ProcurementRecommendation(BaseModel):
    """Structured recommendation produced by the procurement agent."""

    model_config = ConfigDict(str_strip_whitespace=True)

    request_id: str
    decision: Literal["approve", "deny", "escalate"]
    rationale: str = Field(min_length=1)