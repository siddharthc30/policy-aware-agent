import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent.parent / "data" / "expenses.db"

SCHEMA = """
CREATE TABLE IF NOT EXISTS expenses (
    expense_id TEXT PRIMARY KEY,
    employee_id TEXT NOT NULL,
    amount REAL NOT NULL,
    category TEXT NOT NULL,
    date TEXT NOT NULL,
    description TEXT NOT NULL,
    status TEXT NOT NULL
);
"""

SAMPLE_ROWS = [
    ("X001", "EMP001", 85.50, "meals", "2026-06-02", "Client lunch", "approved"),
    ("X002", "EMP001", 450.00, "travel", "2026-06-10", "Flight to Chicago", "approved"),
    ("X003", "EMP002", 1899.00, "equipment", "2026-05-20", "Monitor and dock", "approved"),
    ("X004", "EMP003", 2200.00, "marketing", "2026-06-15", "Trade show booth", "pending"),
    ("X005", "EMP004", 620.00, "equipment", "2026-07-01", "Keyboard and mouse", "approved"),
    ("X006", "EMP005", 3100.00, "travel", "2026-07-05", "International client visit", "approved"),
]

INSERT_SQL = (
    "INSERT OR IGNORE INTO expenses "
    "(expense_id, employee_id, amount, category, date, description, status) "
    "VALUES (?, ?, ?, ?, ?, ?, ?)"
)


def main():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    try:
        conn.execute(SCHEMA)
        conn.executemany(INSERT_SQL, SAMPLE_ROWS)
        conn.commit()
        print(f"Initialized {DB_PATH} with {len(SAMPLE_ROWS)} sample rows.")
    finally:
        conn.close()


if __name__ == "__main__":
    main()