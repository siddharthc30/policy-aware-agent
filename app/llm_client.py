import logging
from typing import List, Optional

from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage


from app.config import OPENAI_MODEL
from app.models import DecisionDraft, ProcessRequest, EmployeeInfo, PolicyChunk
from app.prompts import DECIDE_SYSTEM, build_decide_prompt

logger = logging.getLogger("policy_agent")

_llm = None

class LLMServiceError(Exception):
    pass

def _get_llm():
    global _llm

    if _llm is None:
        _llm = ChatOpenAI(model = OPENAI_MODEL, temperature = 0).with_structured_output(
            DecisionDraft
        )
    return _llm

def get_decision_draft(
        request: ProcessRequest,
        employee: Optional[EmployeeInfo],
        policy_chunks: List[PolicyChunk],
        recent_expenses: List[dict],
        previous_issues: Optional[List[str]] = None,
) -> DecisionDraft:

    prompt = build_decide_prompt(request, employee, policy_chunks, recent_expenses, previous_issues)

    try:
        result = _get_llm().invoke(
            [SystemMessage(content=DECIDE_SYSTEM), HumanMessage(content = prompt)]
        )
    except Exception as e:
        raise LLMServiceError(f"LLM call failed:{e}") from e

    if not isinstance(result, DecisionDraft):
        raise LLMServiceError(f"LLM returned unexpected type: {type(result)}")

    return result