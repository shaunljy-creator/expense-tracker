from services.database import init_db
from services.expense_service import add_expense, get_expenses

# Initialize database
init_db()

# Add sample expenses
add_expense("2025-01-02", "Food", 5.90, "USD","Lunch at NUS")
add_expense("2025-01-03", "Transport", 1.82, "MRT")

# Print all saved expenses
print(get_expenses())