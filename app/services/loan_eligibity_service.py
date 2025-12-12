class LoanEligibilityCalculator:
    def __init__(self, credit_score: int = None, salary: float = None, current_emi: float = None, proposed_emi: float = None):
        
        if credit_score is None:
            raise ValueError("credit_score is required")
        if salary is None:
            raise ValueError("salary is required")
        if current_emi is None:
            raise ValueError("current_emi is required")
        if proposed_emi is None:
            raise ValueError("proposed_emi is required")
 
        self.credit_score = credit_score
        self.salary = salary
        self.current_emi = current_emi
        self.proposed_emi = proposed_emi
        self.max_emi_ratio = 0.4  # 40% rule

    def calculate_max_allowed_emi(self):
        return self.salary * self.max_emi_ratio - self.current_emi

    def is_eligible(self):
        if self.credit_score < 500:
            return False, "Credit score too low for eligibility."

        max_allowed = self.calculate_max_allowed_emi()
        if self.proposed_emi > max_allowed:
            return False, f"Proposed EMI exceeds your 40% limit. Max allowed EMI: {max_allowed:.2f}"

        return True, f"You are eligible. Maximum allowed EMI: {max_allowed:.2f}"