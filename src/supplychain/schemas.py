from datetime import datetime
from typing import Literal
from pydantic import BaseModel, Field

Status = Literal["planned", "in_transit", "delivered", "exception"]

class ShipmentCreate(BaseModel):
    reference: str = Field(min_length=3, max_length=40)
    origin: str = Field(min_length=2, max_length=100)
    destination: str = Field(min_length=2, max_length=100)
    carrier: str = Field(min_length=2, max_length=100)
    expected_arrival: datetime

class StatusUpdate(BaseModel):
    status: Status
    note: str = Field(default="", max_length=500)

class StockAdjustment(BaseModel):
    delta: int = Field(ge=-100000, le=100000)
    reason: str = Field(min_length=3, max_length=300)

class InventoryCreate(BaseModel):
    sku: str = Field(min_length=2, max_length=40)
    description: str = Field(min_length=2, max_length=160)
    on_hand: int = Field(ge=0)
    reorder_point: int = Field(ge=0)
