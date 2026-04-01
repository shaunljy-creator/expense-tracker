from services.database import get_connection

def add_expense(date, category, amount, currency, converted_amount, split_type, participants, notes=""):
    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("""
            INSERT INTO expenses (date, category, amount, currency, converted_amount, split_type, participants, notes)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (date, category, amount, currency, converted_amount, split_type, participants, notes))
        conn.commit()

    except Exception as e:
        print("Error adding expense:", e)

    finally:
        conn.close()

def get_expenses():
    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("SELECT * FROM expenses ORDER BY date DESC")
        rows = cursor.fetchall()
        return rows

    except Exception as e:
        print("Error fetching expenses:", e)
        return []

    finally:
        conn.close()


def update_expense(id, date, category, amount, currency, converted_amount, split_type, participants, notes):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            UPDATE expenses
            SET date=?, category=?, amount=?, currency=?, converted_amount=?, split_type=?, participants=?, notes=?
            WHERE id=?
        """, (date, category, amount, currency, converted_amount, split_type, participants, notes, id))
        conn.commit()

    except Exception as e:
        print("Error updating expense:", e)

    finally:
        conn.close()

def delete_expense(id):
    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("DELETE FROM expenses WHERE id=?", (id,))
        conn.commit()

    except Exception as e:
        print("Error deleting expense:", e)

    finally:
        conn.close()