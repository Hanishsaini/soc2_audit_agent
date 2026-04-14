# from pydantic import BaseModel
# from typing import List, Optional

# class ControlFinding(BaseModel):
#     control_id: str
#     status: str  # "covered", "partial", "gap"
#     confidence: float
#     rationale: str
#     evidence_snippet: str = ""

# class RunRequest(BaseModel):
#     control_ids: List[str]

# class LoginRequest(BaseModel):
#     username: str
#     password: str
from pydantic import BaseModel
from typing import List, Optional

class ControlFinding(BaseModel):
    control_id: str
    status: str  # "covered", "partial", "gap"
    confidence: float
    rationale: str
    recommendation: str = ""
    evidence_snippet: str = ""

class RunRequest(BaseModel):
    control_ids: List[str]

class LoginRequest(BaseModel):
    username: str
    password: str