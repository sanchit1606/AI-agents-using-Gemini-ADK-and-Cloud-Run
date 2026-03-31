from pydantic import BaseModel
from typing import List, Optional

class AnalyzeRequest(BaseModel):
    error_text: str

class FixStep(BaseModel):
    step_number: int
    action: str

class AnalyzeResponse(BaseModel):
    error_summary: str
    probable_cause: str
    fix_steps: List[FixStep]
    commands: List[str]
    confidence: str
    notes: Optional[str] = None
