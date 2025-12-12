import requests
from typing import Dict, Any


class APICallService:
    """
    Service to make POST requests to internal/external APIs  
    using the extracted JSON payload.
    """

    def __init__(self):
        self.timeout = 10  # seconds

    def post(self, endpoint: str, payload: Dict[str, Any]):
        """
        Send POST request with extracted JSON payload.
        """

        try:
            response = requests.post(endpoint, json=payload, timeout=self.timeout)

            # Raise error on bad HTTP responses
            # response.raise_for_status()

            return {
                "success": True,
                "api_response": response.json()
            }

        except requests.exceptions.RequestException as e:
            return {
                "success": False,
                "error": str(e)
            }
