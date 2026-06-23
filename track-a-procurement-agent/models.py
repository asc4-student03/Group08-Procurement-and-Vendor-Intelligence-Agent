from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field, field_validator, model_validator


class PurchaseRequest(BaseModel):
    """Validated purchase request input for procurement pre-screening."""

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
    def validate_total_amount_consistency(self) -> "PurchaseRequest":
        tolerance = 0.01
        expected_total = self.quantity * self.unit_price
        if abs(expected_total - self.total_amount) > tolerance:
            raise ValueError(
                "total_amount must match quantity * unit_price within currency tolerance"
            )
        return self


class ProcurementRecommendation(BaseModel):
    """Structured procurement decision output with required rationale."""

    decision: Literal["approve", "deny", "escalate"]
    rationale: str = Field(min_length=1)

    @field_validator("rationale")
    @classmethod
    def validate_non_empty_rationale(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("rationale must be non-empty")
        return value
