import logging
from typing import List, Optional, TypedDict

from langgraph.graph import StateGraph, END

from app.config import MAX_RETRIES
from app.models import ProcessRequest, EmployeeInfo, PolicyChunk, DecisionDraft

from app import data_access, policy_retrieval, validation
from app.llm_client import get_decision_draft

logger = logging.getLogger("plociy_agent")

class AgentState(TypedDict):
    request: ProcessRequest
    employee: Optional[EmployeeInfo]
    recent_expenses: List[dict]
    policy_chunks : List[PolicyChunk]
    draft: Optional[DecisionDraft]
    previous_issues :Optional[List[str]]
    retry_count: int
    validation_status: str
    final_issues: List[str]


def fetch_context_node(state:AgentState) -> dict:
    request = state["request"]
    employee = data_access.get_employee(request.employee_id)
    recent_expense = data_access.get_recent_expenses(request.employee_id)

    retriever = policy_retrieval.get_retriever()

    query = f"{request.category or ''} {request.request_text}"
    policy_chunks = retriever.retrieve(query)
    return {
        "employee" : employee,
        "recent_expenses" : recent_expense,
        "policy_chunks" : policy_chunks,
    }

def validate_node(state:AgentState) -> dict:
    result = validation.validate_decision(state["draft"], state["request"], state["employee"])

    if result.is_valid:
        return {"validation_status": "passed", "final_issues": []}

    return {
        "validation_status": "invalid",
        "previous_issues": result.issues,
        "final_issues": result.issues,
    }


def decide_node(state:AgentState) -> dict:
    draft = get_decision_draft(
        request=state["request"],
        employee= state["employee"],
        policy_chunks= state["policy_chunks"],
        recent_expenses = state["recent_expenses"],
        previous_issues = state.get("previous_issues")
        )
    
    return {"draft" : draft}

def increment_retry_node(state: AgentState) -> dict:
    return {"retry_count" : state["retry_count"] + 1}

def route_after_validation(state: AgentState) -> str:
    if state["validation_status"] == "passed":
        return "end"
    if state["retry_count"] < MAX_RETRIES:
        return "retry"
    return "end"

def build_graph():
    graph = StateGraph(AgentState)

    graph.add_node("fetch_context", fetch_context_node)
    graph.add_node("decide", decide_node)
    graph.add_node("validate", validate_node)
    graph.add_node("increment_retry", increment_retry_node)

    graph.set_entry_point("fetch_context")
    graph.add_edge("fetch_context", "decide")
    graph.add_edge("decide", "validate")
    graph.add_conditional_edges(
        "validate",
        route_after_validation,
        {
            "retry" : "increment_retry",
            "end" : END
        },
    )
    graph.add_edge("increment_retry", "decide")

    return graph.compile()

def make_initial_state(request: ProcessRequest) -> AgentState:
    return {
        "request": request,
        "employee": None,
        "recent_expenses": [],
        "policy_chunks": [],
        "draft": None,
        "previous_issues": None,
        "retry_count": 0,
        "validation_status": "pending",
        "final_issues": [],
    }
