import os
import json
from openai import OpenAI
from typing import List, Dict, Any, Optional
import httpx


class LLMClient:
    """LLM client using OpenRouter API (OpenAI-compatible)"""

    def __init__(self):
        self.api_key = os.getenv("OPENROUTER_API_KEY", "")
        if not self.api_key:
            raise ValueError("OPENROUTER_API_KEY not set in environment")

        # OpenRouter uses OpenAI-compatible format
        self.client = OpenAI(
            api_key=self.api_key,
            base_url="https://openrouter.ai/api/v1",
            timeout=httpx.Timeout(30.0, connect=10.0)  # 30s timeout
        )

        # Free model on OpenRouter
        self.model = "deepseek/deepseek-v4-flash:free"

    def generate(
        self,
        system_prompt: str,
        user_prompt: str,
        max_tokens: int = 4096,
        temperature: float = 0.7
    ) -> str:
        """Generate a response from the LLM"""
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                max_tokens=max_tokens,
                temperature=temperature,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ]
            )
            return response.choices[0].message.content
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