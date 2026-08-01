"""
Gemini AI Service — Abstract AI Provider Interface + Gemini Implementation
"""
from abc import ABC, abstractmethod
from typing import Any, Dict, Optional
import json
import re

import google.generativeai as genai
from loguru import logger

from app.core.config import settings


class AIProvider(ABC):
    """Abstract base class for AI providers — swap to OpenAI/Claude by implementing this."""

    @abstractmethod
    async def generate(self, prompt: str, system_prompt: str = "") -> str:
        pass

    @abstractmethod
    async def generate_json(self, prompt: str, system_prompt: str = "") -> Dict[str, Any]:
        pass


class GeminiProvider(AIProvider):
    """Google Gemini AI provider implementation."""

    def __init__(self):
        if not settings.GEMINI_API_KEY:
            logger.warning("GEMINI_API_KEY not set — AI generation will fail!")
            self.model = None
            return

        genai.configure(api_key=settings.GEMINI_API_KEY)
        self.model = genai.GenerativeModel(
            model_name=settings.GEMINI_MODEL,
            generation_config={
                "temperature": 0.3,  # Lower temp for more consistent, technical output
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
        logger.info(f"✅ Gemini AI initialized with model: {settings.GEMINI_MODEL}")

    async def generate(self, prompt: str, system_prompt: str = "") -> str:
        """Generate plain text from Gemini."""
        if not self.model:
            raise ValueError("Gemini API key not configured. Please set GEMINI_API_KEY in .env")

        full_prompt = f"{system_prompt}\n\n{prompt}" if system_prompt else prompt
        try:
            response = self.model.generate_content(full_prompt)
            return response.text
        except Exception as e:
            logger.error(f"Gemini generation error: {e}")
            raise

    async def generate_json(self, prompt: str, system_prompt: str = "") -> Dict[str, Any]:
        """Generate JSON-structured output from Gemini with parsing."""
        json_system = (
            "You are an expert Software Engineering Documentation AI. "
            "You MUST respond with ONLY valid JSON — no markdown, no explanation, no code blocks. "
            "Output only the raw JSON object."
        )
        if system_prompt:
            json_system = f"{json_system}\n\n{system_prompt}"

        text = await self.generate(prompt, json_system)

        # Clean up common JSON wrapping issues
        text = text.strip()
        if text.startswith("```json"):
            text = text[7:]
        if text.startswith("```"):
            text = text[3:]
        if text.endswith("```"):
            text = text[:-3]
        text = text.strip()

        try:
            return json.loads(text)
        except json.JSONDecodeError as e:
            logger.error(f"JSON parse error: {e}\nRaw output: {text[:500]}")
            # Attempt to extract JSON from text
            match = re.search(r'\{[\s\S]*\}', text)
            if match:
                try:
                    return json.loads(match.group())
                except json.JSONDecodeError:
                    pass
            raise ValueError(f"AI returned invalid JSON: {str(e)}")


# Singleton AI provider instance
_ai_provider: Optional[AIProvider] = None


def get_ai_provider() -> AIProvider:
    """Get or create the AI provider singleton."""
    global _ai_provider
    if _ai_provider is None:
        _ai_provider = GeminiProvider()
    return _ai_provider
