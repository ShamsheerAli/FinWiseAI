from pydantic import BaseModel

class UserFinanceProfile(BaseModel):
    income: float
    expenses: float
    goals: str
    risk_tolerance: str