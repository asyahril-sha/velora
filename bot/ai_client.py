"""
VELORA - AI Client
DeepSeek API client dengan retry mechanism, error handling, dan fallback.
Fitur:
- Async support
- Retry mechanism (max 3 attempts)
- Exponential backoff
- Error categorization (timeout, rate limit, API error)
- Fallback response generator
- Connection pooling
- Timeout configuration
"""

import asyncio
import logging
import random
from typing import List, Dict, Optional, Any, Tuple
from enum import Enum

import openai
from tenacity import (
    retry, 
    stop_after_attempt, 
    wait_exponential, 
    retry_if_exception_type,
    before_sleep_log
)

from config import get_settings

logger = logging.getLogger(__name__)


# =============================================================================
# ENUMS
# =============================================================================

class AIErrorType(str, Enum):
    """Jenis error yang bisa terjadi"""
    TIMEOUT = "timeout"
    RATE_LIMIT = "rate_limit"
    API_ERROR = "api_error"
    AUTHENTICATION = "authentication"
    NETWORK = "network"
    UNKNOWN = "unknown"


# =============================================================================
# FALLBACK RESPONSES
# =============================================================================

class FallbackResponseGenerator:
    """
    Generator untuk fallback response ketika AI tidak tersedia.
    """
    
    def __init__(self):
        self._fallbacks = {
            'greeting': [
                "*Nova tersenyum* \"Halo Mas. Ada yang bisa Nova bantu?\"",
                "*Nova duduk manis* \"Mas, cerita dong.\"",
                "*Nova mendekat* \"Mas, aku dengerin kok.\""
            ],
            'confused': [
                "*Nova garuk kepala* \"Hmm... Mas bicara apa ya? Aku kurang paham.\"",
                "*Nova mikir* \"Mas... maksudnya gimana?\"",
                "*Nova bingung* \"Aku gak ngerti, Mas. Coba jelasin lagi.\""
            ],
            'affection': [
                "*Nova tersenyum manis* \"Aku sayang Mas.\"",
                "*Nova pegang tangan Mas* \"Mas, kamu baik banget.\"",
                "*Nova peluk Mas* \"Aku seneng ada Mas.\""
            ],
            'default': [
                "*Nova tersenyum* \"Iya, Mas. Nova dengerin kok.\"",
                "*Nova angguk* \"Hmm... gitu ya.\"",
                "*Nova duduk di samping Mas* \"Cerita lagi, Mas.\""
            ]
        }
    
    def get(self, error_type: AIErrorType = AIErrorType.UNKNOWN) -> str:
        """Dapatkan fallback response berdasarkan tipe error"""
        if error_type == AIErrorType.TIMEOUT:
            return "*Nova mikir sebentar*\n\n\"Maaf, Mas. Jaringan agak lambat. Coba ulang ya.\""
        elif error_type == AIErrorType.RATE_LIMIT:
            return "*Nova napas*\n\n\"Mas, coba nanti lagi ya. Aku lagi ngantri.\""
        elif error_type == AIErrorType.AUTHENTICATION:
            return "*Nova bingung*\n\n\"Mas... ada yang salah dengan API key-nya.\""
        elif error_type == AIErrorType.NETWORK:
            return "*Nova cek sinyal*\n\n\"Mas, sinyal lagi jelek. Coba lagi nanti.\""
        else:
            return random.choice(self._fallbacks['default'])


# =============================================================================
# AI CLIENT
# =============================================================================

class AIClient:
    """
    AI Client untuk DeepSeek API.
    - Async support
    - Retry mechanism with exponential backoff
    - Error handling with categorization
    - Fallback responses
    - Connection pooling
    """
    
    def __init__(self, api_key: str = None, model: str = None):
        settings = get_settings()
        self.api_key = api_key or settings.deepseek_api_key
        self.model = model or settings.ai.model
        self.base_url = "https://api.deepseek.com/v1"
        self.timeout = settings.ai.timeout
        self.max_retries = 3
        self.fallback = FallbackResponseGenerator()
        
        self._client: Optional[openai.AsyncOpenAI] = None
        self._last_error: Optional[Tuple[AIErrorType, str]] = None
        self._request_count = 0
        self._error_count = 0
        self._total_tokens = 0
        
        logger.info(f"🤖 AI Client initialized | Model: {self.model} | Timeout: {self.timeout}s")
    
    # =========================================================================
    # CLIENT MANAGEMENT
    # =========================================================================
    
    def _get_client(self) -> openai.AsyncOpenAI:
        """Get or create async client with connection pooling"""
        if self._client is None:
            self._client = openai.AsyncOpenAI(
                api_key=self.api_key,
                base_url=self.base_url,
                timeout=self.timeout,
                max_retries=0  # We handle retries ourselves
            )
            logger.debug("🤖 AI Client created")
        return self._client
    
    def _categorize_error(self, error: Exception) -> AIErrorType:
        """Categorize error type for better handling"""
        error_str = str(error).lower()
        
        if isinstance(error, openai.APITimeoutError):
            return AIErrorType.TIMEOUT
        elif isinstance(error, openai.RateLimitError):
            return AIErrorType.RATE_LIMIT
        elif isinstance(error, openai.AuthenticationError):
            return AIErrorType.AUTHENTICATION
        elif isinstance(error, openai.APIError):
            if "timeout" in error_str:
                return AIErrorType.TIMEOUT
            return AIErrorType.API_ERROR
        elif isinstance(error, (asyncio.TimeoutError, ConnectionError)):
            return AIErrorType.NETWORK
        else:
            return AIErrorType.UNKNOWN
    
    # =========================================================================
    # RETRY DECORATOR
    # =========================================================================
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=1, max=10),
        retry=retry_if_exception_type((
            openai.APITimeoutError,
            openai.RateLimitError,
            openai.APIError,
            asyncio.TimeoutError
        )),
        before_sleep=before_sleep_log(logger, logging.DEBUG)
    )
    async def _call_api_with_retry(
        self, 
        messages: List[Dict[str, str]], 
        temperature: float, 
        max_tokens: int
    ) -> str:
        """
        Call API with retry mechanism.
        Retries on timeout, rate limit, and certain API errors.
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
            usage = response.usage
            
            # Update statistics
            self._request_count += 1
            if usage:
                self._total_tokens += usage.total_tokens
            
            logger.debug(f"🤖 API call #{self._request_count} | Tokens: {usage.total_tokens if usage else '?'} | Temp: {temperature}")
            
            return result.strip()
            
        except Exception as e:
            error_type = self._categorize_error(e)
            self._error_count += 1
            self._last_error = (error_type, str(e))
            
            logger.warning(f"⚠️ API error ({error_type.value}): {e}")
            raise
    
    # =========================================================================
    # PUBLIC METHODS
    # =========================================================================
    
    async def generate(
        self,
        prompt: str,
        temperature: float = None,
        max_tokens: int = None,
        system_message: str = None
    ) -> str:
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
        
        return await self._generate_with_messages(messages, temp, max_tok)
    
    async def generate_with_context(
        self,
        context: str,
        user_message: str,
        temperature: float = None,
        max_tokens: int = None
    ) -> str:
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
        
        return await self._generate_with_messages(messages, temp, max_tok)
    
    async def generate_with_history(
        self,
        system_prompt: str,
        history: List[Dict[str, str]],
        user_message: str,
        temperature: float = None,
        max_tokens: int = None
    ) -> str:
        """
        Generate response dengan history percakapan.
        
        Args:
            system_prompt: System prompt
            history: List of previous messages [{"role": "user/assistant", "content": "..."}]
            user_message: Current user message
            temperature: Temperature
            max_tokens: Max tokens
        """
        settings = get_settings()
        temp = temperature if temperature is not None else settings.ai.temperature
        max_tok = max_tokens if max_tokens is not None else settings.ai.max_tokens
        
        messages = [{"role": "system", "content": system_prompt}]
        messages.extend(history[-10:])  # Last 10 messages
        messages.append({"role": "user", "content": user_message})
        
        return await self._generate_with_messages(messages, temp, max_tok)
    
    async def _generate_with_messages(
        self,
        messages: List[Dict[str, str]],
        temperature: float,
        max_tokens: int
    ) -> str:
        """
        Internal method to generate with messages.
        Handles retries and fallbacks.
        """
        try:
            response = await self._call_api_with_retry(messages, temperature, max_tokens)
            
            # Validate response
            if not response or len(response.strip()) < 2:
                logger.warning("Empty response from API, using fallback")
                return self.fallback.get(AIErrorType.UNKNOWN)
            
            return response
            
        except openai.AuthenticationError as e:
            logger.error(f"❌ Authentication error: {e}")
            return self.fallback.get(AIErrorType.AUTHENTICATION)
            
        except openai.RateLimitError as e:
            logger.error(f"⚠️ Rate limit exceeded: {e}")
            return self.fallback.get(AIErrorType.RATE_LIMIT)
            
        except openai.APITimeoutError as e:
            logger.error(f"⏰ Timeout: {e}")
            return self.fallback.get(AIErrorType.TIMEOUT)
            
        except asyncio.TimeoutError as e:
            logger.error(f"⏰ Async timeout: {e}")
            return self.fallback.get(AIErrorType.TIMEOUT)
            
        except Exception as e:
            error_type = self._categorize_error(e)
            logger.error(f"❌ Unexpected error ({error_type.value}): {e}")
            return self.fallback.get(error_type)
    
    # =========================================================================
    # STREAMING (OPTIONAL)
    # =========================================================================
    
    async def generate_stream(
        self,
        context: str,
        user_message: str,
        temperature: float = None,
        max_tokens: int = None
    ):
        """
        Generate response dengan streaming (token by token).
        Untuk implementasi real-time response.
        """
        settings = get_settings()
        temp = temperature if temperature is not None else settings.ai.temperature
        max_tok = max_tokens if max_tokens is not None else settings.ai.max_tokens
        
        messages = [
            {"role": "system", "content": context},
            {"role": "user", "content": user_message}
        ]
        
        client = self._get_client()
        
        try:
            stream = await client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=temp,
                max_tokens=max_tok,
                stream=True,
                timeout=self.timeout
            )
            
            async for chunk in stream:
                if chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content
                    
        except Exception as e:
            logger.error(f"Stream error: {e}")
            yield self.fallback.get(self._categorize_error(e))
    
    # =========================================================================
    # STATISTICS
    # =========================================================================
    
    def get_stats(self) -> Dict[str, Any]:
        """Dapatkan statistik penggunaan AI"""
        error_rate = (self._error_count / self._request_count * 100) if self._request_count > 0 else 0
        
        return {
            'model': self.model,
            'request_count': self._request_count,
            'error_count': self._error_count,
            'error_rate': f"{error_rate:.1f}%",
            'total_tokens': self._total_tokens,
            'last_error': self._last_error[1] if self._last_error else None,
            'last_error_type': self._last_error[0].value if self._last_error else None
        }
    
    def format_stats(self) -> str:
        """Format statistik untuk display"""
        stats = self.get_stats()
        
        return f"""
╔══════════════════════════════════════════════════════════════╗
║                    🤖 AI CLIENT STATS                        ║
╠══════════════════════════════════════════════════════════════╣
║ MODEL: {stats['model']}
║ REQUESTS: {stats['request_count']}
║ ERRORS: {stats['error_count']} ({stats['error_rate']})
║ TOKENS: {stats['total_tokens']}
║ LAST ERROR: {stats['last_error_type'] or '-'}
╚══════════════════════════════════════════════════════════════╝
"""
    
    def reset_stats(self) -> None:
        """Reset statistik"""
        self._request_count = 0
        self._error_count = 0
        self._total_tokens = 0
        self._last_error = None
        logger.info("🤖 AI Client stats reset")
    
    # =========================================================================
    # HEALTH CHECK
    # =========================================================================
    
    async def health_check(self) -> Tuple[bool, str]:
        """
        Check kesehatan AI client dengan test call.
        Returns: (is_healthy, message)
        """
        try:
            # Test call with minimal tokens
            response = await self.generate(
                prompt="Say 'OK'",
                max_tokens=5,
                temperature=0.5
            )
            
            if response and "OK" in response.upper():
                return True, "AI client healthy"
            else:
                return False, f"Unexpected response: {response[:50]}"
                
        except openai.AuthenticationError:
            return False, "Authentication failed - check API key"
        except openai.RateLimitError:
            return False, "Rate limit exceeded"
        except Exception as e:
            return False, f"Health check failed: {e}"
    
    # =========================================================================
    # RESET
    # =========================================================================
    
    def reset_client(self) -> None:
        """Reset client (close and recreate)"""
        if self._client:
            # Close existing client (if has close method)
            if hasattr(self._client, 'close'):
                try:
                    # Async close would need await, but we're recreating anyway
                    pass
                except:
                    pass
            self._client = None
        self._last_error = None
        logger.info("🤖 AI Client reset")


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


def reset_ai_client() -> None:
    """Reset AI client (untuk testing)"""
    global _ai_client
    if _ai_client:
        _ai_client.reset_client()
    _ai_client = None
    logger.info("🔄 AI Client reset")


__all__ = [
    'AIErrorType',
    'AIClient',
    'get_ai_client',
    'reset_ai_client'
]
