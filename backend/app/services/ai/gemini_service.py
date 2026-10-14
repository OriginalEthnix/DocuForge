"""
Gemini AI Service — Abstract AI Provider Interface + Robust Gemini Implementation
"""
import asyncio
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional
import json
import re

import google.generativeai as genai
from loguru import logger

from app.core.config import settings

CANDIDATE_MODELS = [
    settings.GEMINI_MODEL,
    "gemini-flash-latest",
    "gemini-pro-latest",
    "gemini-2.5-flash",
    "gemini-2.5-pro",
]


class AIProvider(ABC):
    """Abstract base class for AI providers — swap to OpenAI/Claude by implementing this."""

    @abstractmethod
    async def generate(self, prompt: str, system_prompt: str = "") -> str:
        pass

    @abstractmethod
    async def generate_json(self, prompt: str, system_prompt: str = "") -> Dict[str, Any]:
        pass


class GeminiProvider(AIProvider):
    """Google Gemini AI provider implementation with dynamic model fallback and bounded retry."""

    def __init__(self):
        self.api_key_configured = bool(settings.GEMINI_API_KEY)
        self.active_model_name = settings.GEMINI_MODEL or "gemini-flash-latest"
        self.model: Optional[genai.GenerativeModel] = None

        if not self.api_key_configured:
            logger.warning("GEMINI_API_KEY not configured. AI calls will require valid key or fallback.")
            return

        genai.configure(api_key=settings.GEMINI_API_KEY)
        self._init_model(self.active_model_name)

    def _init_model(self, model_name: str) -> None:
        self.active_model_name = model_name
        self.model = genai.GenerativeModel(
            model_name=model_name,
            generation_config={
                "temperature": 0.3,
                "top_p": 0.95,
                "top_k": 40,
                "max_output_tokens": 8192,
            },
            safety_settings=[
                {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"},
                {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE"},
                {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE"},
                {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"},
            ]
        )
        logger.info(f"Gemini AI configured with model: {self.active_model_name}")

    async def generate(self, prompt: str, system_prompt: str = "") -> str:
        """Generate plain text from Gemini with automatic fallback on model deprecation/404 and retries."""
        if not self.api_key_configured or not self.model:
            raise ValueError("Gemini API key is not configured. Please set GEMINI_API_KEY in .env")

        full_prompt = f"{system_prompt}\n\n{prompt}" if system_prompt else prompt

        # Candidate models to try in order
        models_to_try: List[str] = [self.active_model_name]
        for m in CANDIDATE_MODELS:
            if m and m not in models_to_try:
                models_to_try.append(m)

        last_error = None
        for candidate in models_to_try:
            if candidate != self.active_model_name:
                logger.info(f"Switching Gemini model to candidate: {candidate}")
                self._init_model(candidate)

            # Up to 3 bounded retries for transient errors (e.g. 429 rate limit)
            for attempt in range(1, 4):
                try:
                    # Run synchronous genai call in executor so it does not block the async event loop
                    loop = asyncio.get_running_loop()
                    response = await loop.run_in_executor(None, self.model.generate_content, full_prompt)
                    if response and response.text:
                        return response.text
                    raise ValueError("Gemini returned empty response text.")
                except Exception as e:
                    err_str = str(e).lower()
                    last_error = e

                    # If model not found or deprecated, break retry loop and try next model candidate immediately
                    if "not found" in err_str or "404" in err_str or "no longer available" in err_str:
                        logger.warning(f"Model {candidate} unavailable: {e}. Trying next model candidate.")
                        break

                    # If rate limit (429) or transient server error (503), wait and retry
                    if ("429" in err_str or "quota" in err_str or "503" in err_str or "resource_exhausted" in err_str) and attempt < 3:
                        wait_seconds = attempt * 2
                        logger.warning(f"Transient error on model {candidate} (attempt {attempt}/3): {e}. Retrying in {wait_seconds}s...")
                        await asyncio.sleep(wait_seconds)
                        continue

                    # Other non-retryable error
                    logger.error(f"Gemini execution error on model {candidate}: {e}")
                    break

        raise RuntimeError(f"All Gemini generation attempts failed. Last error: {last_error}")

    async def generate_json(self, prompt: str, system_prompt: str = "") -> Dict[str, Any]:
        """Generate JSON-structured output from Gemini with robust sanitization and parsing."""
        json_system = (
            "You are an expert Software Engineering Documentation AI.\n"
            "You MUST respond with ONLY a valid, parseable JSON object.\n"
            "Do NOT wrap the output in explanation or narrative text.\n"
            "Return valid raw JSON only."
        )
        if system_prompt:
            json_system = f"{json_system}\n\n{system_prompt}"

        text = await self.generate(prompt, json_system)

        # 1. Clean markdown code blocks
        cleaned = text.strip()
        if cleaned.startswith("```json"):
            cleaned = cleaned[7:]
        elif cleaned.startswith("```"):
            cleaned = cleaned[3:]
        if cleaned.endswith("```"):
            cleaned = cleaned[:-3]
        cleaned = cleaned.strip()

        # 2. Try direct json.loads
        try:
            return json.loads(cleaned)
        except json.JSONDecodeError as direct_err:
            logger.warning(f"Direct JSON parse failed: {direct_err}. Attempting regex extraction...")

        # 3. Extract JSON with regex (greedy match from first { to last })
        match = re.search(r'(\{[\s\S]*\})', cleaned)
        if match:
            candidate_json = match.group(1).strip()
            try:
                return json.loads(candidate_json)
            except json.JSONDecodeError:
                # 4. Remove trailing commas before closing braces/brackets
                fixed = re.sub(r',\s*(\}|\])', r'\1', candidate_json)
                try:
                    return json.loads(fixed)
                except json.JSONDecodeError:
                    pass

        # Also check for array root
        array_match = re.search(r'(\[[\s\S]*\])', cleaned)
        if array_match:
            try:
                arr = json.loads(array_match.group(1).strip())
                return {"items": arr}
            except json.JSONDecodeError:
                pass

        logger.error(f"Failed to parse JSON. Raw output preview: {text[:500]}")
        raise ValueError(f"AI returned invalid JSON: {cleaned[:200]}")


# Singleton AI provider instance
_ai_provider: Optional[AIProvider] = None


def get_ai_provider() -> AIProvider:
    """Get or create the AI provider singleton."""
    global _ai_provider
    if _ai_provider is None:
        _ai_provider = GeminiProvider()
    return _ai_provider
