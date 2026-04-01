import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from services.database import init_db
from services.expense_service import add_expense, get_expenses

def test_add_and_get():
    init_db()
    add_expense("2025-01-01", "Test", 1.23, "Test note")
    results = get_expenses()
    assert len(results) >= 1