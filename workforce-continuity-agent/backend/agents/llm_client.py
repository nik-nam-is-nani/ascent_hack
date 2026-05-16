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
            timeout=httpx.Timeout(15.0, connect=5.0)
        )

        # Configurable model — fast free options:
        #   google/gemini-2.0-flash-exp:free
        #   mistralai/mistral-small-3.2-24b-instruct:free
        #   google/gemma-3-12b-it:free
        self.model = os.getenv("OPENROUTER_MODEL", "google/gemini-2.0-flash-exp:free")

    def generate(
        self,
        system_prompt: str,
        user_prompt: str,
        max_tokens: int = 4096,
        temperature: float = 0.7
    ) -> str:
        """Generate a response from the LLM"""
        try:
            print(f"[LLM] Calling {self.model}...", flush=True)
            response = self.client.chat.completions.create(
                model=self.model,
                max_tokens=max_tokens,
                temperature=temperature,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ]
            )
            # Null-safe response parsing
            if not response or not response.choices or len(response.choices) == 0:
                print(f"[LLM] Empty response from API", flush=True)
                return "Error: Empty response from API"
            content = response.choices[0].message.content
            if not content:
                print(f"[LLM] Null content in response", flush=True)
                return "Error: Null content in response"
            print(f"[LLM] Response received ({len(content)} chars)", flush=True)
            return content
        except Exception as e:
            print(f"[LLM] ERROR: {e}", flush=True)
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
            return json.loads(response)
        except json.JSONDecodeError:
            import re
            match = re.search(r'```json\s*(.*?)\s*```', response, re.DOTALL)
            if match:
                return json.loads(match.group(1))
            return {"error": "Failed to parse JSON", "raw_response": response}


# Global client instance
llm_client: Optional[LLMClient] = None


def get_llm_client() -> LLMClient:
    """Get or create the LLM client instance. Recreates if API key changes."""
    global llm_client
    current_key = os.environ.get("OPENROUTER_API_KEY", "")
    if llm_client is None or llm_client.api_key != current_key:
        llm_client = LLMClient()
    return llm_client
