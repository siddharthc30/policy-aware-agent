from dataclasses import dataclass, field
from typing import List, Optional

from app.config import MIN_REASON_LENGTH
from app.models import DecisionDraft, ProcessRequest, EmployeeInfo

from app import approval_matrix as matrix

VALID_DECISIONS = {"auto_approve", "require_approval", "reject", "request_info"}

@dataclass
class ValidationResult:
    is_valid: bool
    issues: List[str] = field(default_factory=list)

def validate_decision(
        draft: DecisionDraft,
        request: ProcessRequest,
        employee: Optional[EmployeeInfo],
) -> ValidationResult:

    issues: List[str]= []

    if draft.decision not in VALID_DECISIONS:
        issues.append(f"'{draft.decision}' is not a valid decision value.")
        return ValidationResult(False, issues)

    if employee is None:
        if draft.decision not in {"reject", "request_info"}:
            issues.append(
                "Unkonown employee must result in 'reject' or 'request_info', "
                "not an approval decision."
            )

        return ValidationResult(len(issues) == 0, issues)
    if request.amount is not None:
        if draft.decision == "auto_approve":
            limit = matrix.auto_approve_limit(employee.department)
            if request.amount > limit:
                issues.append(
                    f"Cannot auto-approve ${request.amount:.2f}; auto-approve limit"
                    f"for {employee.department} is $ {limit:.2f}."
                )
        if draft.decision == "require_approval":
            expected_approver = matrix.required_approver(request.amount)
            if draft.required_approver != expected_approver:
                issues.append(
                    f"Wrong approver for ${request.amount:.2f}: expected '{expected_approver}' , got '{draft.required_approver}'."
                )

    if draft.decision in {"auto_approve", "require_approval", "reject"} and not draft.policy_sources:
        issues.append("Decision must cite at lease one policy source.")

    if len(draft.reason.strip()) < MIN_REASON_LENGTH:
        issues.append("Reason is too short to be evidence-backed.")

    return ValidationResult(len(issues) == 0, issues)