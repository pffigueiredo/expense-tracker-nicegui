from decimal import Decimal
from datetime import date, datetime
from nicegui import ui
from app.expense_service import (
    create_expense,
    get_all_expenses,
    delete_expense,
    get_total_expenses,
    get_expenses_by_category,
)
from app.models import ExpenseCreate


def create():
    """Create the expense tracking UI components."""

    # Define common categories for quick selection
    COMMON_CATEGORIES = ["Food", "Transport", "Utilities", "Entertainment", "Healthcare", "Shopping", "Other"]

    # Apply modern color theme
    ui.colors(
        primary="#2563eb",
        secondary="#64748b",
        accent="#10b981",
        positive="#10b981",
        negative="#ef4444",
        warning="#f59e0b",
        info="#3b82f6",
    )

    @ui.page("/")
    def index():
        """Main expense tracker page."""

        # Page header
        with ui.row().classes("w-full justify-between items-center mb-6"):
            ui.label("💰 Expense Tracker").classes("text-3xl font-bold text-gray-800")
            ui.button("Add Expense", on_click=lambda: add_expense_dialog()).classes(
                "bg-primary text-white px-6 py-2 rounded-lg hover:bg-blue-600 transition-colors"
            )

        # Summary cards
        create_summary_section()

        # Expenses table
        create_expenses_table()

    def create_summary_section():
        """Create the summary cards section."""
        with ui.row().classes("w-full gap-4 mb-6"):
            # Total expenses card
            total = get_total_expenses()
            with ui.card().classes("p-6 bg-white shadow-lg rounded-xl flex-1"):
                ui.label("Total Expenses").classes("text-sm text-gray-500 uppercase tracking-wider")
                ui.label(f"${total:,.2f}").classes("text-3xl font-bold text-gray-800 mt-2")

            # Category breakdown
            categories = get_expenses_by_category()
            top_category = max(categories.items(), key=lambda x: x[1]) if categories else ("None", Decimal("0"))

            with ui.card().classes("p-6 bg-white shadow-lg rounded-xl flex-1"):
                ui.label("Top Category").classes("text-sm text-gray-500 uppercase tracking-wider")
                ui.label(top_category[0]).classes("text-2xl font-bold text-gray-800 mt-2")
                ui.label(f"${top_category[1]:,.2f}").classes("text-lg text-gray-600")

    def create_expenses_table():
        """Create the expenses table with data."""
        expenses = get_all_expenses()

        if not expenses:
            with ui.card().classes("p-8 text-center"):
                ui.label("No expenses recorded yet").classes("text-gray-500 text-lg")
                ui.label('Click "Add Expense" to get started').classes("text-gray-400 mt-2")
            return

        # Table columns
        columns = [
            {"name": "date", "label": "Date", "field": "expense_date", "sortable": True},
            {"name": "description", "label": "Description", "field": "description", "sortable": True},
            {"name": "category", "label": "Category", "field": "category", "sortable": True},
            {"name": "amount", "label": "Amount", "field": "amount", "sortable": True},
            {"name": "actions", "label": "Actions", "field": "actions", "sortable": False},
        ]

        # Convert expenses to table rows
        rows = []
        for expense in expenses:
            rows.append(
                {
                    "id": expense.id,
                    "expense_date": expense.expense_date.strftime("%Y-%m-%d"),
                    "description": expense.description,
                    "category": expense.category,
                    "amount": f"${expense.amount:,.2f}",
                    "actions": expense.id,
                }
            )

        with ui.card().classes("p-4 shadow-lg rounded-lg"):
            ui.label("Recent Expenses").classes("text-xl font-bold mb-4")

            table = ui.table(columns=columns, rows=rows, row_key="id").classes("w-full")

            # Add delete button for each row
            table.add_slot(
                "body-cell-actions",
                """
                <q-td :props="props">
                    <q-btn 
                        flat 
                        round 
                        color="negative"
                        icon="delete"
                        size="sm"
                        @click="$parent.$emit('delete-expense', props.row.id)"
                    />
                </q-td>
            """,
            )

            # Handle delete event
            table.on("delete-expense", lambda e: delete_expense_handler(e.args))

    async def add_expense_dialog():
        """Show dialog to add new expense."""
        with ui.dialog() as dialog, ui.card().classes("w-96"):
            ui.label("Add New Expense").classes("text-xl font-bold mb-4")

            # Form fields
            with ui.column().classes("gap-4"):
                amount_input = ui.number(label="Amount ($)", value=0.0, step=0.01, min=0.01, format="%.2f").classes(
                    "w-full"
                )

                description_input = ui.input(label="Description", placeholder="Enter expense description").classes(
                    "w-full"
                )

                date_input = ui.date(value=date.today().isoformat()).classes("w-full")

                category_select = ui.select(
                    label="Category", options=COMMON_CATEGORIES, value=COMMON_CATEGORIES[0], with_input=True
                ).classes("w-full")

            # Dialog buttons
            with ui.row().classes("gap-2 justify-end mt-6"):
                ui.button("Cancel", on_click=dialog.close).props("flat")
                ui.button(
                    "Add Expense",
                    on_click=lambda: save_expense(dialog, amount_input, description_input, date_input, category_select),
                ).classes("bg-primary text-white")

        dialog.open()

    def save_expense(dialog, amount_input, description_input, date_input, category_select):
        """Save new expense and refresh the page."""
        try:
            # Validate inputs
            if not amount_input.value or amount_input.value <= 0:
                ui.notify("Please enter a valid amount", type="negative")
                return

            if not description_input.value or not description_input.value.strip():
                ui.notify("Please enter a description", type="negative")
                return

            if not category_select.value or not category_select.value.strip():
                ui.notify("Please select a category", type="negative")
                return

            # Create expense
            # Parse date value - could be string or date object
            expense_date = date_input.value
            if isinstance(expense_date, str):
                expense_date = datetime.fromisoformat(expense_date).date()

            expense_data = ExpenseCreate(
                amount=Decimal(str(amount_input.value)),
                description=description_input.value.strip(),
                expense_date=expense_date,
                category=category_select.value.strip(),
            )

            create_expense(expense_data)
            dialog.close()
            ui.notify("Expense added successfully!", type="positive")
            ui.navigate.reload()

        except Exception as e:
            ui.notify(f"Error adding expense: {str(e)}", type="negative")

    async def delete_expense_handler(expense_id):
        """Handle expense deletion with confirmation."""
        with ui.dialog() as dialog, ui.card():
            ui.label("Confirm Delete").classes("text-lg font-bold mb-4")
            ui.label("Are you sure you want to delete this expense?").classes("mb-4")

            with ui.row().classes("gap-2 justify-end"):
                ui.button("Cancel", on_click=dialog.close).props("flat")
                ui.button("Delete", on_click=lambda: perform_delete(dialog, expense_id)).classes(
                    "bg-negative text-white"
                )

        dialog.open()

    def perform_delete(dialog, expense_id):
        """Actually delete the expense."""
        try:
            if delete_expense(expense_id):
                dialog.close()
                ui.notify("Expense deleted successfully!", type="positive")
                ui.navigate.reload()
            else:
                ui.notify("Expense not found", type="negative")
        except Exception as e:
            ui.notify(f"Error deleting expense: {str(e)}", type="negative")
