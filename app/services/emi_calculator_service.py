class EMI_Calculator:
    # Hardcoded interest rates per loan type
    interest_rates = {
        "personal": 12.0,  # annual %
        "home": 8.5,
        "car": 10.0
    }

    def __init__(self, loan_amount: float = None, tenure_months: int = None, loan_type: str = None):
        # Validation: all three fields are required
        # if loan_amount is None:
        #     raise ValueError("loan_amount is required")
        # if tenure_months is None:
        #     raise ValueError("tenure_months is required")
        # if loan_type is None:
        #     raise ValueError("loan_type is required")
        
        errors = {}

        if loan_amount is None:
            errors["loan_amount"] = "loan_amount is required"

        if tenure_months is None:
            errors["tenure_months"] = "tenure_months is required"

        if loan_type is None:
            errors["loan_type"] = "loan_type is required"

        if errors:
            return {
                "success": False,
                "message": "Validation failed",
                "errors": errors
            }
        
        self.loan_amount = loan_amount
        self.tenure_months = tenure_months
        self.loan_type = loan_type.lower()

  
        self.interest_rate = self.get_interest_rate()

    def get_interest_rate(self):
      return self.interest_rates.get(self.loan_type, 12.0)

    def calculate_emi(self):
        P = self.loan_amount
        N = self.tenure_months
        R = self.interest_rate / (12 * 100)  # monthly interest rate

        EMI = (P * R * (1 + R)**N) / ((1 + R)**N - 1)
        total_payment = EMI * N
        return EMI, total_payment
