import json 

from app.config import APPROVAL_MATRIX_PATH

with open(APPROVAL_MATRIX_PATH, encoding="utf-8") as f:
    _MATRIX = json.load(f)

def auto_approve_limit(department:str) -> float:
    limit = _MATRIX["auto_approve_limits"]
    return limit.get(department, limit["default"])

def required_approver(amount:float) -> str:
    for tier in _MATRIX["approval_tiers"]:
        if tier["max_amount"] is None or amount <= tier["max_amount"]:
            return tier["approver"]

    return _MATRIX["approval_tiers"][-1]["approver"]