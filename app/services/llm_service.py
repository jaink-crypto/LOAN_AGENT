import os
import json
import requests
from dotenv import load_dotenv
import re

load_dotenv()

# from sentence_transformers import SentenceTransformer
from qdrant_client import QdrantClient

# ----------------------------
# Qdrant Setup
# ----------------------------
qdrant_client = QdrantClient(
    url=os.getenv("QDRANT_URL"),
    api_key=os.getenv("QDRANT_API_KEY")
)

collection_name = os.getenv("QDRANT_COLLECTION")
vector_name = os.getenv("QDRANT_VECTOR_NAME")

# Load embedding model from env
embedding_model_name = os.getenv("EMBEDDING_MODEL", "all-MiniLM-L12-v2")
# model = SentenceTransformer(embedding_model_name)
model  = ""

class LLMService:
    """
    Simple LLM wrapper to take:
    - system prompt
    - user query
    and return ONLY the LLM JSON output.
    """

    def __init__(self):
        self.api_key = os.getenv("GROQ_API_KEY")
        if not self.api_key:
            raise ValueError("Missing GROQ_API_KEY in environment variables")

        self.url = "https://api.groq.com/openai/v1/chat/completions"
        # self.model = "llama-3.3-70b-versatile"   # You can change model here
        self.model = os.getenv("LLM_MODEL", "llama-3.3-70b-versatile")
        
    def retrieve_chunks(self,query, top_k=2):
        # Create query embedding
        query_embedding = model.encode(query).tolist()

        # Search Qdrant
        search_results = qdrant_client.search(
            collection_name=collection_name,
            query_vector=(vector_name, query_embedding),
            limit=top_k
        )

        results = []
        for result in search_results:
            results.append({
                "text": result.payload.get("text"),
                "heading": result.payload.get("heading")
            })
        return results
        
    def clean_json(self, text: str):
        """
        Cleans LLM output:
        - removes ```json blocks
        - extracts pure JSON string
        - returns parsed dict
        """
        # remove markdown code block fencing
        cleaned = re.sub(r"```json|```", "", text).strip()

        # extract json object using regex
        match = re.search(r"\{.*\}", cleaned, re.DOTALL)
        if match:
            cleaned = match.group(0)

        # final JSON parse
        try:
            return json.loads(cleaned)
        except:
            return {"raw_response": text}
    
    
    def generate_from_messages(self, messages,global_intent):
        
        print("Last Message:", messages[-1]['content'])
        chunks = self.retrieve_chunks(messages[-1]['content'])
        
        if global_intent == "faq":
            context = "Use the following context to answer the question:\n"
            for idx, chunk in enumerate(chunks):
                context += f"Context {idx+1} - {chunk['heading']}: {chunk['text']}\n"
            
            # Append context to the last user message
            messages.append({
                "role": "system",
                "content": context
            })
        
        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": 0.0
        }
        
        
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        response = requests.post(self.url, headers=headers, json=payload)

        if response.status_code != 200:
            raise Exception(f"Groq API Error: {response.text}")

        result = response.json()
        content = result["choices"][0]["message"]["content"]

        return self.clean_json(content)
    
    
    
    def generate_human_response(self, user_query: str, api_result: dict):
        """
        Converts API numeric result into a human-readable explanation.
        """

        system_prompt = """
        You are a finance assistant. 
        Convert the loan API result into a simple human readable response.
        
        RULES:
        - Do NOT return JSON.
        - Respond in plain English.
        - Interpret the numbers and explain them clearly.
        - Mention EMI, interest rate, total amount etc.
        - Keep response short and helpful.
        """

        # Prepare readable input for LLM
        user_message = f"""
        User Query: {user_query}

        API Result:
        {json.dumps(api_result, indent=2)}
        """

        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message}
            ],
            "temperature": 0.2
        }

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        response = requests.post(self.url, headers=headers, json=payload)

        if response.status_code != 200:
            raise Exception(f"Groq API Error: {response.text}")

        output = response.json()
        content = output["choices"][0]["message"]["content"]

        # No JSON cleaning needed — return raw text
        return content.strip()