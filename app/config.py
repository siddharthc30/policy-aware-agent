import os
from pathlib import Path

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
DB_PATH = Path(__file__).resolve().parent.parent / "data" / "expenses.db"

EMPLOYEES_CSV_PATH = DATA_DIR / "employee.csv"
EXPENSE_DB_PATH = DATA_DIR / "expenses.db"
TRAVEL_POLICY_PATH = DATA_DIR / "travel_policy.pdf"
APPROVAL_MATRIX_PATH = DATA_DIR / "approval_matrix.json"

load_dotenv(BASE_DIR / ".env")

OPENAI_MODEL = "gpt-4o-mini"

MAX_RETRIES = 1

MIN_REASON_LENGTH = 50

POLICY_RETRIEVAL_TOP_K = 3

FALLBACK_ERROR_MESSAGE = "Unable to process this request due to an internal error."
UNKNOWN_EMPLOYEE_NOTE = "No employee record found for this provided employee_id."