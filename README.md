# Policy-Aware Action Agent

A FastAPI + LangGraph service that evaluates employee expense/travel requests against a travel policy PDF, an approval matrix, and employee records, then returns an automated decision (`auto_approve`, `require_approval`, `reject`, or `request_info`).

## Requirements

- Python 3.11
- An OpenAI API key

## Setup

1. **Clone/enter the project directory**
   ```bash
   cd project
   ```

2. **Create a virtual environment and install dependencies**
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

3. **Create a `.env` file** in the project root (same level as `app/`):
   ```
   OPENAI_API_KEY=sk-...
   ```

4. **Verify required data files exist** in `data/`:
   - `employee.csv`
   - `travel_policy.pdf`
   - `approval_matrix.json`

5. **Initialize the expenses database**
   ```bash
   python3 scripts/init_db.py
   ```
   This creates `data/expenses.db` with sample expense history for a few employees.

## Running the server

```bash
uvicorn app.main:app --reload
```

Server starts at `http://127.0.0.1:8000`. Startup will fail with a clear error if `OPENAI_API_KEY` is missing or any required data file isn't found.

## Verifying it's running

```bash
curl http://127.0.0.1:8000/health
```

Expected response:
```json
{
  "status": "healthy",
  "dependencies": {
    "employees_loaded": true,
    "policy_retriever_ready": true,
    "graph_compiled": true,
    "openai_key_set": true
  }
}
```

## Testing the agent

### Option A — Interactive docs
Open `http://127.0.0.1:8000/docs` in a browser, expand `POST /process-request`, click "Try it out," and submit a request body like:
```json
{
  "employee_id": "EMP001",
  "request_text": "Requesting reimbursement for a client dinner",
  "amount": 93.20,
  "category": "meals"
}
```

### Option B — curl
```bash
curl -X POST http://127.0.0.1:8000/process-request \
  -H "Content-Type: application/json" \
  -d '{
    "employee_id": "EMP001",
    "request_text": "Requesting reimbursement for a client dinner",
    "amount": 93.20,
    "category": "meals"
  }'
```

### Option C — sample test suite
`sample_requests.json` in the project root contains 8 predefined test cases covering different decision paths (auto-approve, requires approval, unknown employee, missing info, prompt-injection attempt, etc.).

Run them all at once (requires [`jq`](https://jqlang.org/)):
```bash
chmod +x run_sample_tests.sh
./run_sample_tests.sh
```

Or copy any single `payload` object out of `sample_requests.json` and paste it into Option A or B above.

## Notes

- Valid `employee_id` values are `EMP001`–`EMP015` (see `data/employee.csv`).
- The LLM call uses `temperature=0`, so results are consistent but not guaranteed identical across runs.
- If validation fails on the first attempt, the agent retries once (`MAX_RETRIES` in `app/config.py`) before returning `validation_status: "failed_after_retry"` with a reduced confidence score.