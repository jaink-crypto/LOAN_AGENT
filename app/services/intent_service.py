import os
from groq import Groq
import json
from dotenv import load_dotenv


load_dotenv()
class IntentDetectionService:
    def __init__(self):
        """
        Initialize LLM client and valid intents.
        """
        self.client = Groq(api_key=os.getenv("GROQ_API_KEY"))

        self.valid_intents = {
            "check_eligibility",
            "calculate_emi",
            "faq",
            "save_user_query",
            "no_intent"
        }

        # Prompt template
        self.prompt_template = """
You are an intent classification AI for a loan assistant.

Classify the user's message into EXACTLY one of the following intents:
1. check_eligibility  
2. calculate_emi  
3. faq  
4. save_user_query
5. no_intent

Definitions:
- check_eligibility → ONLY when the user explicitly asks about their loan eligibility. 
  Examples: "Am I eligible?", "Check my eligibility", "Can I get a loan?"
  NOTE: Providing information like salary, credit score, or EMI alone is NOT eligibility intent unless a direct question about eligibility is asked.

- calculate_emi → ONLY when the user asks to calculate EMI or mentions things like monthly payment, interest + tenure, etc.

- faq → General banking or loan-related questions (interest rate, documents, greetings, support, etc.)

- save_user_query -> When the user asks to raise or submit a query reagrding loan.
   Examples: "I want to raise a loan request", "I want to submit my loan details", "Save my loan application"

- no_intent → When the user gives information but does NOT ask any question or does not match any of the above intents.

Rules:
- Respond ONLY in valid JSON.
- Use "no_intent" when the query does not clearly belong to the above four intent categories.
- JSON format:
{{ "intent": "<one_of_the_intents>" }}

User message: "{query}"
        """


    def _call_llm(self, query: str) -> str:
        """
        Send the prompt to LLM and extract the intent safely.
        """
        prompt = self.prompt_template.format(query=query)

        response = self.client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.1,
            max_tokens=50
        )

        raw_output = response.choices[0].message.content.strip()
        print(f"LLM Raw Output: {raw_output}")
        try:
            data = json.loads(raw_output)
            intent = data.get("intent", "no_intent")
            if intent not in self.valid_intents:
                intent = "no_intent"
        except:
            intent = "no_intent"

        return intent


    def predict_intent(self, query: str):
        """
        Public method: return ONLY intent (matches your old API).
        """
        return self._call_llm(query)


    def get_intent_confidence(self, query: str):
        """
        LLM does not return confidence. We keep API structure same.
        Confidence is always None.
        """
        intent = self._call_llm(query)
        return {
            "intent": intent,
            "confidence": None   # LLM doesn't provide similarity score
        }
