"""
Simple Ollama connection test utility
"""

import logging
from .ollama_client import OllamaClient

logger = logging.getLogger(__name__)


def test_ollama_connection():
    """
    Test Ollama connection with simple error handling
    """
    try:
        client = OllamaClient()
        return client.test_connection()
    except Exception as e:
        logger.error(f"Ollama connection test failed: {e}")
        return False
