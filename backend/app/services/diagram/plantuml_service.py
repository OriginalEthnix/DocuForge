"""
PlantUML Diagram Service — Renders PlantUML code to SVG via public PlantUML server
"""
import base64
import zlib
import httpx
from typing import Optional
from loguru import logger

from app.core.config import settings


# PlantUML encoding alphabet
PLANTUML_ALPHABET = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz-_"


def _encode_plantuml(plantuml_code: str) -> str:
    """Encode PlantUML code to the compressed URL-safe format."""
    # Compress with zlib
    compressed = zlib.compress(plantuml_code.encode("utf-8"), 9)
    # Base64 encode with PlantUML's custom alphabet
    encoded = base64.b64encode(compressed).decode("ascii")

    # Convert standard base64 to PlantUML's custom alphabet
    result = ""
    for char in encoded:
        if char in "ABCDEFGHIJKLMNOPQRSTUVWXYZ":
            result += PLANTUML_ALPHABET[ord(char) - ord("A")]
        elif char in "abcdefghijklmnopqrstuvwxyz":
            result += PLANTUML_ALPHABET[ord(char) - ord("a") + 26]
        elif char in "0123456789":
            result += PLANTUML_ALPHABET[ord(char) - ord("0") + 52]
        elif char == "+":
            result += PLANTUML_ALPHABET[62]
        elif char == "/":
            result += PLANTUML_ALPHABET[63]
        elif char == "=":
            pass  # Skip padding
    return result


async def render_plantuml_to_svg(plantuml_code: str) -> Optional[str]:
    """
    Send PlantUML code to the public PlantUML server and get back SVG content.
    Returns SVG string or None on failure.
    """
    try:
        encoded = _encode_plantuml(plantuml_code)
        url = f"{settings.PLANTUML_SERVER}/svg/{encoded}"

        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(url)

        if response.status_code == 200:
            return response.text
        else:
            logger.warning(f"PlantUML server returned {response.status_code}")
            return None

    except Exception as e:
        logger.error(f"PlantUML rendering error: {e}")
        return None


def get_plantuml_url(plantuml_code: str, format: str = "svg") -> str:
    """Get the direct URL for a PlantUML diagram (for frontend direct rendering)."""
    encoded = _encode_plantuml(plantuml_code)
    return f"{settings.PLANTUML_SERVER}/{format}/{encoded}"
