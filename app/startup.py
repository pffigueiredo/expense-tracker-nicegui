from app.database import create_tables
from nicegui import app
import app.expense_ui


def startup() -> None:
    # this function is called before the first request
    create_tables()
    app.expense_ui.create()
