import os
import json
import anthropic
from typing import List, Dict, Any, Optional


class LLMClient:
    """LLM client using OpenRouter API (Anthropic-compatible)"""

    def __init__(self):
        self.api_key = os.getenv("OPENROUTER_API_KEY", "")
        if not self.api_key:
            raise ValueError("OPENROUTER_API_KEY not set in environment")

        # Configure Anthropic client to use OpenRouter
        self.client = anthropic.Anthropic(
            api_key=self.api_key,
            base_url="https://openrouter.ai/api/v1"
        )

        # Default model
        self.model = "anthropic/claude-3.5-sonnet-20241022"

    def generate(
        self,
        system_prompt: str,
        user_prompt: str,
        max_tokens: int = 4096,
        temperature: float = 0.7
    ) -> str:
        """Generate a response from the LLM"""
        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=max_tokens,
                temperature=temperature,
                system=system_prompt,
                messages=[
                    {"role": "user", "content": user_prompt}
                ]
            )
            return response.content[0].text
        except Exception as e:
            return f"Error: {str(e)}"

    def generate_json(
        self,
        system_prompt: str,
        user_prompt: str,
        max_tokens: int = 4096
    ) -> Dict[str, Any]:
        """Generate a JSON response from the LLM"""
        prompt = f"{user_prompt}\n\nRespond ONLY with valid JSON. No markdown formatting."
        response = self.generate(system_prompt, prompt, max_tokens)
        try:
            # Try to parse JSON from response
            return json.loads(response)
        except json.JSONDecodeError:
            # Try to extract JSON from markdown code block
            import re
            match = re.search(r'```json\s*(.*?)\s*```', response, re.DOTALL)
            if match:
                return json.loads(match.group(1))
            # Return error dict
            return {"error": "Failed to parse JSON", "raw_response": response}


# Global client instance
llm_client: Optional[LLMClient] = None


def get_llm_client() -> LLMClient:
    """Get or create the LLM client instance"""
    global llm_client
    if llm_client is None:
        llm_client = LLMClient()
    return llm_client