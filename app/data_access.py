import sqlite3
from typing import Optional
import pandas as pd

from app.config import EMPLOYEES_CSV_PATH, EXPENSE_DB_PATH
from app.models import EmployeeInfo

_employees_df: Optional[pd.DataFrame] = None

def load_employees() ->pd.DataFrame:
    global _employees_df
    if _employees_df is None:
        _employees_df = pd.read_csv(EMPLOYEES_CSV_PATH, dtype = str)

    return _employees_df

def get_employee(employee_id : str) -> Optional[EmployeeInfo]:
    df = load_employees()
    match = df[df["employee_id"] == employee_id]
    if match.empty: 
        return None

    row = match.iloc[0]
    return EmployeeInfo(
        employee_id = row["employee_id"],
        name = row["name"],
        department = row["department"],
        role = row["role"],
        manager = row["manager"],
    )

def get_recent_expenses(employee_id : str, limit: int = 5) -> list[dict]:
    if not EXPENSE_DB_PATH.exists():
        return []

    conn = sqlite3.connect(EXPENSE_DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        cursor = conn.execute(
            "SELECT expense_id, amount, category, date, description, status "
            "FROM expenses WHERE employee_id = ? ORDER BY date DESC LIMIT ?",
            (employee_id, limit),
        )
        return [dict(row) for row in cursor.fetchall()]
    finally:
        conn.close()

        