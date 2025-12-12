from fastapi import APIRouter, Depends , HTTPException
from app.models import LoanRequest, LoanResponse,EMIResponse,EMIRequest,IntentRequest,SaveLoanQueryRequest,LoanQuery
from app.services.loan_eligibity_service import LoanEligibilityCalculator
from app.services.emi_calculator_service import EMI_Calculator
from app.services.intent_service import IntentDetectionService
from app.services.prompt_service import PromptService
from app.services.llm_service import LLMService
from app.services.api_call_service import APICallService
from sqlalchemy.orm import Session
from utils.db import get_db
import re

router = APIRouter()

@router.post("/save-loan-query")
def save_loan_query(request: SaveLoanQueryRequest, db: Session = Depends(get_db)):
    
    PAN_REGEX = r"^[A-Z]{5}[0-9]{4}[A-Z]$"
    AADHAAR_REGEX = r"^[2-9]{1}[0-9]{11}$"
    
    if not re.match(PAN_REGEX, request.pan_card.upper()):
        raise HTTPException(
            status_code=400,
            detail="Invalid PAN Number."
        )

    # --------------------------
    # Validate Aadhaar
    # --------------------------
    if not re.match(AADHAAR_REGEX, request.adhaar_card):
        raise HTTPException(
            status_code=400,
            detail="Invalid Aadhaar Number."
        )


    new_entry = LoanQuery(
        name=request.name,
        pan_card=request.pan_card,
        adhaar_card=request.adhaar_card,
        loan_amount=request.loan_amount,
        loan_type=request.loan_type,
        
    )

    db.add(new_entry)
    db.commit()
    db.refresh(new_entry)

    return {
        "success": True,
        "message": "Loan query saved successfully",
        "data": {
            "id": new_entry.id,
            "name": new_entry.name,
            "pan_card": new_entry.pan_card,
            "adhaar_card": new_entry.adhaar_card,
            "loan_amount": new_entry.loan_amount,
            "loan_type": new_entry.loan_type,
            "created_at": new_entry.created_at
        }
    }
    
    
@router.get("/get-all-loan-queries")
def get_all_loan_queries(db: Session = Depends(get_db)):

    entries = db.query(LoanQuery).all()

    # Convert SQLAlchemy objects → Python dict
    result = []
    for e in entries:
        result.append({
            "id": e.id,
            "name": e.name,
            "pan_card": e.pan_card,
            "adhaar_card": e.adhaar_card,
            "loan_amount": e.loan_amount,
            "loan_type": e.loan_type,
            "created_at": e.created_at
        })

    return {
        "success": True,
        "message": "All loan queries fetched successfully",
        "data": result
    }



@router.post("/loan/eligibility", response_model=LoanResponse)
def check_loan_eligibility(request: LoanRequest):

    calculator = LoanEligibilityCalculator(
        credit_score=request.credit_score,
        salary=request.salary,
        current_emi=request.current_emi,
        proposed_emi=request.proposed_emi
    )

    eligible, message = calculator.is_eligible()
    max_emi = calculator.calculate_max_allowed_emi()

    return LoanResponse(
        eligible=eligible,
        max_allowed_emi=max_emi,
        message=message
    )
    
    
@router.post("/loan/emi", response_model=EMIResponse)
def calculate_emi(request: EMIRequest):
    """
    Calculate EMI for a loan based on amount, tenure, and type of loan.
    Input validation is automatically handled by Pydantic.
    """
    calculator = EMI_Calculator(
        loan_amount=request.loan_amount,
        tenure_months=request.tenure_months,
        loan_type=request.loan_type
    )

    emi, total_payment = calculator.calculate_emi()

    return EMIResponse(
        loan_amount=request.loan_amount,
        tenure_months=request.tenure_months,
        interest_rate=calculator.interest_rate,
        emi=round(emi, 2),
        total_payment=round(total_payment, 2)
    )
    

chats= []
global_intent = ""

@router.post("/chat")
def chat(request: IntentRequest):
    """
    Detect the user's intent from a query.
    """
    
    global global_intent
     
    intent_service  = IntentDetectionService()
    prompt_service = PromptService()
    llm_service = LLMService()
    api_caller = APICallService()
    
    intent = intent_service.predict_intent(request.query)
    print("Predicted Intent:", intent)
    if intent != "no_intent":
        global_intent=intent 
    
    if intent == "no_intent" and global_intent == "":
        global_intent="faq"
    
    chats.append({"role": "user", "content": request.query})

    
    base_messages  = prompt_service.build_llm_payload(global_intent, request.query)
    
    system_prompt = base_messages[0]["content"] + "\n" + base_messages[1]["content"]
    
    llm_messages = [
        {"role": "system", "content": system_prompt},
        *chats  
    ]
    
    request_payload = llm_service.generate_from_messages(llm_messages,global_intent)
    
    if global_intent == "faq":
        chats.append({"role": "assistant", "content": request_payload['raw_response']})
        return {
            "success": True,
            "query": request.query,
            "predicted_intent": global_intent,
            "messages": base_messages,
            "llm_extracted_json": {},
            "api_result": {},
            "human_readable_response": request_payload['raw_response']
        }
    
    api_result = api_caller.post(base_messages[2]['api_endpoint'], request_payload)
    
    human_readable_response = llm_service.generate_human_response(request.query, api_result)
    
    chats.append({"role": "assistant", "content": human_readable_response})

    
    return {
        "success": True,
        "query": request.query,
        "predicted_intent": global_intent,
        "messages": base_messages,
        "llm_extracted_json": request_payload,
        "api_result": api_result,
        "human_readable_response": human_readable_response
    }