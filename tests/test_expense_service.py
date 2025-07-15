import pytest
from decimal import Decimal
from datetime import date
from app.database import reset_db
from app.expense_service import (
    create_expense,
    get_all_expenses,
    get_expense_by_id,
    delete_expense,
    get_total_expenses,
    get_expenses_by_category,
)
from app.models import ExpenseCreate


@pytest.fixture()
def clean_db():
    """Reset database before each test."""
    reset_db()
    yield
    reset_db()


def test_create_expense(clean_db):
    """Test creating a new expense."""
    expense_data = ExpenseCreate(
        amount=Decimal("25.50"), description="Lunch at cafe", expense_date=date(2024, 1, 15), category="Food"
    )

    expense = create_expense(expense_data)

    assert expense.id is not None
    assert expense.amount == Decimal("25.50")
    assert expense.description == "Lunch at cafe"
    assert expense.expense_date == date(2024, 1, 15)
    assert expense.category == "Food"
    assert expense.created_at is not None


def test_get_all_expenses_empty(clean_db):
    """Test getting expenses when none exist."""
    expenses = get_all_expenses()
    assert expenses == []


def test_get_all_expenses_with_data(clean_db):
    """Test getting all expenses with data."""
    # Create test expenses
    expense1 = ExpenseCreate(
        amount=Decimal("15.00"), description="Coffee", expense_date=date(2024, 1, 10), category="Food"
    )
    expense2 = ExpenseCreate(
        amount=Decimal("50.00"), description="Gas", expense_date=date(2024, 1, 12), category="Transport"
    )

    create_expense(expense1)
    create_expense(expense2)

    expenses = get_all_expenses()
    assert len(expenses) == 2

    # Should be ordered by date desc (newest first)
    assert expenses[0].expense_date == date(2024, 1, 12)
    assert expenses[1].expense_date == date(2024, 1, 10)


def test_get_expense_by_id_exists(clean_db):
    """Test getting expense by ID when it exists."""
    expense_data = ExpenseCreate(
        amount=Decimal("30.00"), description="Movie ticket", expense_date=date(2024, 1, 20), category="Entertainment"
    )

    created_expense = create_expense(expense_data)

    if created_expense.id is not None:
        retrieved_expense = get_expense_by_id(created_expense.id)
        assert retrieved_expense is not None
        assert retrieved_expense.id == created_expense.id
        assert retrieved_expense.amount == Decimal("30.00")
        assert retrieved_expense.description == "Movie ticket"


def test_get_expense_by_id_not_exists(clean_db):
    """Test getting expense by ID when it doesn't exist."""
    expense = get_expense_by_id(999)
    assert expense is None


def test_delete_expense_exists(clean_db):
    """Test deleting an expense that exists."""
    expense_data = ExpenseCreate(
        amount=Decimal("20.00"), description="Parking fee", expense_date=date(2024, 1, 15), category="Transport"
    )

    created_expense = create_expense(expense_data)

    if created_expense.id is not None:
        result = delete_expense(created_expense.id)
        assert result is True

        # Verify it's deleted
        deleted_expense = get_expense_by_id(created_expense.id)
        assert deleted_expense is None


def test_delete_expense_not_exists(clean_db):
    """Test deleting an expense that doesn't exist."""
    result = delete_expense(999)
    assert result is False


def test_get_total_expenses_empty(clean_db):
    """Test getting total expenses when none exist."""
    total = get_total_expenses()
    assert total == Decimal("0")


def test_get_total_expenses_with_data(clean_db):
    """Test getting total expenses with data."""
    expenses = [
        ExpenseCreate(amount=Decimal("15.50"), description="Lunch", expense_date=date(2024, 1, 10), category="Food"),
        ExpenseCreate(
            amount=Decimal("25.00"), description="Bus fare", expense_date=date(2024, 1, 11), category="Transport"
        ),
        ExpenseCreate(amount=Decimal("8.75"), description="Coffee", expense_date=date(2024, 1, 12), category="Food"),
    ]

    for expense in expenses:
        create_expense(expense)

    total = get_total_expenses()
    assert total == Decimal("49.25")


def test_get_expenses_by_category_empty(clean_db):
    """Test getting expenses by category when none exist."""
    categories = get_expenses_by_category()
    assert categories == {}


def test_get_expenses_by_category_with_data(clean_db):
    """Test getting expenses by category with data."""
    expenses = [
        ExpenseCreate(amount=Decimal("15.00"), description="Lunch", expense_date=date(2024, 1, 10), category="Food"),
        ExpenseCreate(amount=Decimal("25.00"), description="Dinner", expense_date=date(2024, 1, 11), category="Food"),
        ExpenseCreate(
            amount=Decimal("30.00"), description="Bus pass", expense_date=date(2024, 1, 12), category="Transport"
        ),
        ExpenseCreate(amount=Decimal("12.50"), description="Coffee", expense_date=date(2024, 1, 13), category="Food"),
    ]

    for expense in expenses:
        create_expense(expense)

    categories = get_expenses_by_category()

    assert len(categories) == 2
    assert categories["Food"] == Decimal("52.50")
    assert categories["Transport"] == Decimal("30.00")


def test_create_expense_with_decimal_precision(clean_db):
    """Test creating expense with precise decimal amounts."""
    expense_data = ExpenseCreate(
        amount=Decimal("123.45"),  # Use 2 decimal places as defined in model
        description="Test precision",
        expense_date=date(2024, 1, 15),
        category="Test",
    )

    expense = create_expense(expense_data)

    # SQLModel should handle decimal precision based on field definition
    assert expense.amount == Decimal("123.45")


def test_create_expense_edge_cases(clean_db):
    """Test creating expenses with edge case values."""
    # Test with very small amount
    expense_data = ExpenseCreate(
        amount=Decimal("0.01"), description="Penny expense", expense_date=date(2024, 1, 15), category="Test"
    )

    expense = create_expense(expense_data)
    assert expense.amount == Decimal("0.01")

    # Test with large amount
    expense_data = ExpenseCreate(
        amount=Decimal("9999.99"), description="Large expense", expense_date=date(2024, 1, 15), category="Test"
    )

    expense = create_expense(expense_data)
    assert expense.amount == Decimal("9999.99")


def test_expense_ordering_by_date(clean_db):
    """Test that expenses are ordered by date (newest first)."""
    dates = [date(2024, 1, 10), date(2024, 1, 15), date(2024, 1, 12), date(2024, 1, 8)]

    for i, expense_date in enumerate(dates):
        expense_data = ExpenseCreate(
            amount=Decimal("10.00"), description=f"Expense {i}", expense_date=expense_date, category="Test"
        )
        create_expense(expense_data)

    expenses = get_all_expenses()

    # Should be ordered by date desc
    expected_order = [date(2024, 1, 15), date(2024, 1, 12), date(2024, 1, 10), date(2024, 1, 8)]

    actual_order = [expense.expense_date for expense in expenses]
    assert actual_order == expected_order
