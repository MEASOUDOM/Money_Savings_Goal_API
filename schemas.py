from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import date, datetime
from decimal import Decimal

class CurrencyOut(BaseModel):
    id: int
    code: str
    symbol: str
    name: str
    is_active: int

    class Config:
        from_attributes = True

class GoalCreate(BaseModel):
    name: str = Field(min_length=1, max_length=120)
    currency_id: int
    goal_amount: Decimal = Field(gt=0)
    note: Optional[str] = None
    image_path: Optional[str] = None
    target_date: Optional[date] = None

class GoalOut(BaseModel):
    id: int
    name: str
    image_path: Optional[str]
    note: Optional[str]
    currency: CurrencyOut
    goal_amount: Decimal
    saved_amount: Decimal
    target_date: Optional[date]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class MoneyRequest(BaseModel):
    amount: Decimal = Field(gt=0)
    note: Optional[str] = None

class TransferRequest(BaseModel):
    from_goal_id: int
    to_goal_id: int
    amount: Decimal = Field(gt=0)
    note: Optional[str] = None

class TransactionOut(BaseModel):
    id: int
    goal_id: int
    type: int
    amount: Decimal
    note: Optional[str]
    txn_date: datetime
    from_goal_id: Optional[int] = None
    to_goal_id: Optional[int] = None

    class Config:
        from_attributes = True

class SimpleMsg(BaseModel):
    message: str
