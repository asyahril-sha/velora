"""
VELORA - AI Client
DeepSeek API client dengan retry mechanism dan error handling.
"""

import asyncio
import logging
import openai
from typing import List, Dict, Optional, Any
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

from config import get_settings

logger = logging.getLogger(__name__)


# =============================================================================
# AI CLIENT
# =============================================================================

class AIClient:
    """
    AI Client untuk DeepSeek API.
    - Async support
    - Retry mechanism
    - Error handling
    """
    
    def __init__(self, api_key: str = None, model: str = None):
        settings = get_settings()
        self.api_key = api_key or settings.deepseek_api_key
        self.model = model or settings.ai.model
        self.base_url = "https://api.deepseek.com/v1"
        self.timeout = settings.ai.timeout
        
        self._client: Optional[openai.AsyncOpenAI] = None
        
        logger.info(f"🤖 AI Client initialized | Model: {self.model}")
    
    def _get_client(self) -> openai.AsyncOpenAI:
        """Get or create async client"""
        if self._client is None:
            self._client = openai.AsyncOpenAI(
                api_key=self.api_key,
                base_url=self.base_url,
                timeout=self.timeout
            )
        return self._client
    
    async def generate(self,
                       prompt: str,
                       temperature: float = None,
                       max_tokens: int = None,
                       system_message: str = None) -> str:
        """
        Generate response dari AI.
        
        Args:
            prompt: System prompt (atau user message jika system_message None)
            temperature: Temperature (default dari settings)
            max_tokens: Max tokens (default dari settings)
            system_message: Optional system message
        
        Returns:
            Generated response string
        """
        settings = get_settings()
        temp = temperature if temperature is not None else settings.ai.temperature
        max_tok = max_tokens if max_tokens is not None else settings.ai.max_tokens
        
        messages = []
        
        if system_message:
            messages.append({"role": "system", "content": system_message})
            messages.append({"role": "user", "content": prompt})
        else:
            messages.append({"role": "user", "content": prompt})
        
        return await self._call_api(messages, temp, max_tok)
    
    async def generate_with_context(self,
                                     context: str,
                                     user_message: str,
                                     temperature: float = None,
                                     max_tokens: int = None) -> str:
        """
        Generate response dengan context sebagai system message.
        """
        settings = get_settings()
        temp = temperature if temperature is not None else settings.ai.temperature
        max_tok = max_tokens if max_tokens is not None else settings.ai.max_tokens
        
        messages = [
            {"role": "system", "content": context},
            {"role": "user", "content": user_message}
        ]
        
        return await self._call_api(messages, temp, max_tok)
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type((openai.APITimeoutError, openai.APIError, openai.RateLimitError))
    )
    async def _call_api(self,
                        messages: List[Dict[str, str]],
                        temperature: float,
                        max_tokens: int) -> str:
        """
        Call DeepSeek API dengan retry.
        """
        client = self._get_client()
        
        try:
            response = await client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
                timeout=self.timeout
            )
            
            result = response.choices[0].message.content
            logger.debug(f"AI response: {len(result)} chars, temp={temperature}")
            
            return result.strip()
            
        except openai.APITimeoutError as e:
            logger.warning(f"API timeout: {e}")
            raise
            
        except openai.RateLimitError as e:
            logger.warning(f"Rate limit: {e}")
            raise
            
        except openai.APIError as e:
            logger.error(f"API error: {e}")
            raise
            
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            raise
    
    async def generate_fallback(self, error: Exception, fallback_message: str = None) -> str:
        """
        Generate fallback response jika AI error.
        """
        logger.warning(f"Using fallback response due to: {error}")
        
        if fallback_message:
            return fallback_message
        
        # Default fallback
        return "*Nova tersenyum*\n\n\"Iya, Mas. Nova dengerin kok.\""


# =============================================================================
# GLOBAL INSTANCE
# =============================================================================

_ai_client: Optional[AIClient] = None


def get_ai_client() -> AIClient:
    """Get global AI client instance"""
    global _ai_client
    if _ai_client is None:
        _ai_client = AIClient()
    return _ai_client


__all__ = [
    'AIClient',
    'get_ai_client'
]
