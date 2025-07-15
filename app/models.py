from sqlmodel import SQLModel, Field
from datetime import datetime, date as Date
from typing import Optional
from decimal import Decimal


# Persistent models (stored in database)
class Expense(SQLModel, table=True):
    __tablename__ = "expenses"  # type: ignore[assignment]

    id: Optional[int] = Field(default=None, primary_key=True)
    amount: Decimal = Field(decimal_places=2, max_digits=10)
    description: str = Field(max_length=500)
    expense_date: Date = Field()
    category: str = Field(max_length=100)
    created_at: datetime = Field(default_factory=datetime.utcnow)


# Non-persistent schemas (for validation, forms, API requests/responses)
class ExpenseCreate(SQLModel, table=False):
    amount: Decimal = Field(decimal_places=2, max_digits=10)
    description: str = Field(max_length=500)
    expense_date: Date
    category: str = Field(max_length=100)


class ExpenseUpdate(SQLModel, table=False):
    amount: Optional[Decimal] = Field(default=None, decimal_places=2, max_digits=10)
    description: Optional[str] = Field(default=None, max_length=500)
    expense_date: Optional[Date] = Field(default=None)
    category: Optional[str] = Field(default=None, max_length=100)


class ExpenseResponse(SQLModel, table=False):
    id: int
    amount: Decimal
    description: str
    expense_date: Date
    category: str
    created_at: datetime
