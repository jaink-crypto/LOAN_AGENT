from pydantic import BaseModel, Field, validator,BaseModel, model_validator
from sqlalchemy import Column, Integer, String, DateTime, func,Float
from utils.db import Base

class SaveLoanQueryRequest(BaseModel):
    name: str
    pan_card: str
    adhaar_card: str
    loan_amount: float
    loan_type: str
    
class LoanRequest(BaseModel):
    proposed_emi: float = Field(..., description="Proposed EMI")
    credit_score: int = Field(..., description="Credit score")
    salary: float = Field(..., description="Salary")
    current_emi: float = Field(..., description="Current EMI")


class LoanResponse(BaseModel):
    eligible: bool
    max_allowed_emi: float
    message: str


class EMIRequest(BaseModel):
    loan_amount: float
    tenure_months: int
    loan_type: str  # e.g., "personal", "home", "car"
    

class EMIResponse(BaseModel):
    loan_amount: float
    tenure_months: int
    interest_rate: float
    emi: float
    total_payment: float
    
class IntentRequest(BaseModel):
    # intent : str
    query: str
    
    
class LoanQuery(Base):
    __tablename__ = "loan_queries"

    id = Column(Integer, primary_key=True, index=True)

    # New fields
    name = Column(String, nullable=False)
    pan_card = Column(String, nullable=False)
    adhaar_card = Column(String, nullable=False)
    loan_amount = Column(Float, nullable=False)
    loan_type = Column(String, nullable=False)

    created_at = Column(DateTime, server_default=func.now())