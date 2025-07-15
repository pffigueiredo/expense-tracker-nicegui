from decimal import Decimal
from typing import List, Optional
from sqlmodel import select, desc
from app.database import get_session
from app.models import Expense, ExpenseCreate


def create_expense(expense_data: ExpenseCreate) -> Expense:
    """Create a new expense record."""
    with get_session() as session:
        expense = Expense(
            amount=expense_data.amount,
            description=expense_data.description,
            expense_date=expense_data.expense_date,
            category=expense_data.category,
        )
        session.add(expense)
        session.commit()
        session.refresh(expense)
        return expense


def get_all_expenses() -> List[Expense]:
    """Get all expenses ordered by date (newest first)."""
    with get_session() as session:
        statement = select(Expense).order_by(desc(Expense.expense_date))
        return list(session.exec(statement))


def get_expense_by_id(expense_id: int) -> Optional[Expense]:
    """Get a specific expense by ID."""
    with get_session() as session:
        return session.get(Expense, expense_id)


def delete_expense(expense_id: int) -> bool:
    """Delete an expense by ID. Returns True if deleted, False if not found."""
    with get_session() as session:
        expense = session.get(Expense, expense_id)
        if expense is None:
            return False
        session.delete(expense)
        session.commit()
        return True


def get_total_expenses() -> Decimal:
    """Calculate total amount of all expenses."""
    expenses = get_all_expenses()
    return sum((expense.amount for expense in expenses), Decimal("0"))


def get_expenses_by_category() -> dict[str, Decimal]:
    """Get expenses grouped by category with totals."""
    expenses = get_all_expenses()
    category_totals = {}
    for expense in expenses:
        if expense.category not in category_totals:
            category_totals[expense.category] = Decimal("0")
        category_totals[expense.category] += expense.amount
    return category_totals
