import json
import os

class PromptService:
    def __init__(self, prompt_file_path: str = "app/prompts/prompts.json"):
        self.prompt_file_path = prompt_file_path
        self.prompts = self._load_prompts()

    def _load_prompts(self):
        """Load prompts from JSON file."""
        if not os.path.exists(self.prompt_file_path):
            raise FileNotFoundError(f"Prompt file not found: {self.prompt_file_path}")

        with open(self.prompt_file_path, "r") as file:
            return json.load(file)

    def get_prompt(self, intent: str):
        """Return the prompt template for the given intent."""
        intent = intent.lower()

        if intent not in self.prompts:
            raise ValueError(f"No prompt found for intent: {intent}")

        return self.prompts[intent]

    def build_llm_payload(self, intent: str, user_query: str):
        """
        Build final LLM messages:
        - system prompt
        - user prompt including user query
        """

        prompt = self.get_prompt(intent)

        system_prompt = prompt.get("system", "")
        user_instruction = prompt.get("user_instruction", "")
        api_endpoint = prompt.get("api_endpoint", "")

        return [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_instruction + "\n\nUser Query: " + user_query},
            {"api_endpoint": api_endpoint}
        ]
