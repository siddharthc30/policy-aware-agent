from typing import TypedDict, List, Literal, Optional
from pydantic import BaseModel, Field

Decision = Literal["auto_approve", "require_approval", "reject", "request_info"]


class ProcessRequest(BaseModel):
    employee_id : str
    request_text : str
    amount : Optional[float] = None
    category : Optional[str] = None

class EmployeeInfo(BaseModel):
    employee_id : str
    name : str
    department: str
    role : str
    manager : str

class PolicyChunk(BaseModel):
    source : str
    section : str
    text : str

class DecisionDraft(BaseModel):
    decision : Decision
    reason : str
    employee : Optional[EmployeeInfo] = None
    policy_sources : List[str]
    required_approver : Optional[str] = None
    confidence : float
    validation_status : Literal ["passed", "failed_after_retry"]
    retry_count : int
    validation_issues : Optional[List[str]] = None 


class ProcessResponse(BaseModel):
    decision: Decision
    reason: str
    employee: Optional[EmployeeInfo] = None
    policy_sources: List[str] = []
    required_approver: Optional[str] = None
    confidence: float
    validation_status: Literal["passed", "failed_after_retry"]
    retry_count: int
    validation_issues: Optional[List[str]] = None

    