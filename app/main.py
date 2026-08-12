import os
import asyncio
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException

from app.config import EMPLOYEES_CSV_PATH, TRAVEL_POLICY_PATH, APPROVAL_MATRIX_PATH
from app.models import ProcessRequest, ProcessResponse
from app import data_access, policy_retrieval
from app.graph import build_graph, make_initial_state
from app.llm_client import LLMServiceError

logger = logging.getLogger("policy_agent")
logging.basicConfig(level=logging.INFO)


@asynccontextmanager
async def lifespan(app: FastAPI):
    if not os.getenv("OPENAI_API_KEY"):
        raise RuntimeError("OPENAI_API_KEY not set. Create a .env file with OPENAI_API_KEY=sk-...")

    for path, label in [
        (EMPLOYEES_CSV_PATH, "employee directory CSV"),
        (TRAVEL_POLICY_PATH, "travel policy document"),
        (APPROVAL_MATRIX_PATH, "approval matrix"),
    ]:
        if not path.exists():
            raise RuntimeError(f"Required {label} not found at {path}. Check the data/ directory.")

    app.state.employees = data_access.load_employees()
    app.state.retriever = policy_retrieval.get_retriever()
    app.state.graph = build_graph()
    yield


app = FastAPI(title="Policy-Aware Action Agent (LangGraph)", lifespan=lifespan)


@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "dependencies": {
            "employees_loaded": getattr(app.state, "employees", None) is not None,
            "policy_retriever_ready": getattr(app.state, "retriever", None) is not None,
            "graph_compiled": getattr(app.state, "graph", None) is not None,
            "openai_key_set": bool(os.getenv("OPENAI_API_KEY")),
        },
    }


@app.post("/process-request", response_model=ProcessResponse)
async def process_request(request: ProcessRequest):
    try:
        initial_state = make_initial_state(request)
        result = await asyncio.to_thread(app.state.graph.invoke, initial_state)

        draft = result["draft"]
        if draft is None:
            raise HTTPException(status_code = 500, detail = "Agent produced no decision.")
        passed = result["validation_status"] == "passed"
        confidence = draft.confidence if passed else round(min(draft.confidence, 0.3), 2)

        return ProcessResponse(
            decision=draft.decision,
            reason=draft.reason,
            employee=result["employee"],
            policy_sources=draft.policy_sources,
            required_approver=draft.required_approver,
            confidence=confidence,
            validation_status="passed" if passed else "failed_after_retry",
            retry_count=result["retry_count"],
            validation_issues=None if passed else result["final_issues"],
        )

    except LLMServiceError as e:
        logger.error(f"LLM service error: {e}")
        raise HTTPException(status_code=503, detail="Decision service temporarily unavailable")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception:
        logger.exception("Unexpected error in /process-request")
        raise HTTPException(status_code=500, detail="Internal server error")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="127.0.0.1", port = 8000, reload = True)
    