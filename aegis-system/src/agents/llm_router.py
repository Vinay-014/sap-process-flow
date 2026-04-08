"""
AEGIS LLM Router
Multi-provider LM routing with automatic fallback.
Tries providers in priority order: Gemini → GROQ → Together AI.
Auto-switches on quota/rate-limit errors.
"""

from typing import Optional, Dict, Any, List
from enum import Enum
import logging
import time
from datetime import datetime, timedelta

from langchain_core.language_models import BaseChatModel
from langchain_core.messages import BaseMessage, HumanMessage, SystemMessage, AIMessage
from langchain_core.outputs import ChatResult, LLMResult
from langchain_core.callbacks import CallbackManager

from src.config import settings

logger = logging.getLogger("aegis.llm_router")


class ProviderStatus(Enum):
    HEALTHY = "healthy"
    RATE_LIMITED = "rate_limited"
    UNAVAILABLE = "unavailable"


class ProviderInfo:
    """Tracks status and cooldown for a single LLM provider."""

    def __init__(self, name: str, model: BaseChatModel, priority: int):
        self.name = name
        self.model = model
        self.priority = priority
        self.status = ProviderStatus.HEALTHY
        self.last_error: Optional[str] = None
        self.error_count = 0
        self.cooldown_until: Optional[datetime] = None
        self.total_calls = 0
        self.total_failures = 0
        self.last_call: Optional[datetime] = None

    def is_available(self) -> bool:
        if self.status == ProviderStatus.UNAVAILABLE:
            return False
        if self.cooldown_until and datetime.utcnow() < self.cooldown_until:
            return False
        return True

    def record_success(self):
        self.status = ProviderStatus.HEALTHY
        self.last_error = None
        self.total_calls += 1
        self.last_call = datetime.utcnow()
        # Reset error count on success
        if self.error_count > 0:
            self.error_count = max(0, self.error_count - 1)

    def record_failure(self, error: str):
        self.total_calls += 1
        self.total_failures += 1
        self.last_error = error
        self.error_count += 1
        self.last_call = datetime.utcnow()

        error_lower = error.lower()

        # Determine cooldown based on error type
        if "429" in error_lower or "quota" in error_lower or "rate limit" in error_lower:
            self.status = ProviderStatus.RATE_LIMITED
            self.cooldown_until = datetime.utcnow() + timedelta(seconds=60)
            logger.warning(f"Provider {self.name} rate limited. Cooldown 60s.")
        elif "401" in error_lower or "unauthorized" in error_lower or "invalid api" in error_lower:
            self.status = ProviderStatus.UNAVAILABLE
            self.cooldown_until = datetime.utcnow() + timedelta(hours=1)
            logger.error(f"Provider {self.name} auth failed. Cooldown 1h.")
        else:
            self.status = ProviderStatus.HEALTHY
            # Retry immediately for non-quota errors
            self.cooldown_until = None

    def get_stats(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "status": self.status.value,
            "priority": self.priority,
            "total_calls": self.total_calls,
            "total_failures": self.total_failures,
            "success_rate": (
                round((1 - self.total_failures / self.total_calls) * 100, 1)
                if self.total_calls > 0
                else 100.0
            ),
            "last_error": self.last_error,
            "last_call": self.last_call.isoformat() if self.last_call else None,
        }


class AEGISLLMRouter:
    """
    Multi-provider LLM router with automatic fallback.

    Priority order: Gemini (primary) → GROQ (backup) → Together AI (last resort)
    Automatically switches provider when one hits quota/rate limits.
    """

    def __init__(self):
        self.providers: List[ProviderInfo] = []
        self._initialized = False
        self._current_provider_index = 0
        self._initialize_providers()

    def _initialize_providers(self):
        """Initialize all configured LLM providers."""
        # 1. Google Gemini (primary)
        if settings.GOOGLE_API_KEY.strip():
            try:
                from langchain_google_genai import ChatGoogleGenerativeAI
                gemini = ChatGoogleGenerativeAI(
                    model=settings.LLM_MODEL.strip() or "gemini-2.5-flash",
                    temperature=0.1,
                    google_api_key=settings.GOOGLE_API_KEY.strip(),
                )
                self.providers.append(ProviderInfo("gemini", gemini, priority=1))
                logger.info("Gemini provider initialized")
            except Exception as e:
                logger.warning(f"Failed to initialize Gemini: {e}")

        # 2. GROQ (backup — fast inference with Llama)
        if settings.GROQ_API_KEY.strip():
            try:
                from langchain_groq import ChatGroq
                groq = ChatGroq(
                    model="llama-3.3-70b-versatile",
                    temperature=0.1,
                    groq_api_key=settings.GROQ_API_KEY.strip(),
                )
                self.providers.append(ProviderInfo("groq", groq, priority=2))
                logger.info("GROQ provider initialized (llama-3.3-70b)")
            except Exception as e:
                logger.warning(f"Failed to initialize GROQ: {e}")

        # 3. Together AI (last resort — Meta Llama models)
        if settings.TOGETHER_API_KEY.strip():
            try:
                from langchain_together import Together
                together = Together(
                    model="meta-llama/Llama-3.3-70B-Instruct-Turbo",
                    temperature=0.1,
                    api_key=settings.TOGETHER_API_KEY.strip(),
                )
                self.providers.append(ProviderInfo("together", together, priority=3))
                logger.info("Together AI provider initialized (Llama-3.3-70B)")
            except Exception as e:
                logger.warning(f"Failed to initialize Together: {e}")

        # Sort by priority
        self.providers.sort(key=lambda p: p.priority)

        if not self.providers:
            logger.error("No LLM providers available!")
        else:
            logger.info(
                f"LLM Router initialized with {len(self.providers)} providers: "
                + ", ".join(f"{p.name}(p{p.priority})" for p in self.providers)
            )

        self._initialized = True

    @property
    def active_provider(self) -> Optional[ProviderInfo]:
        """Get the current active (healthy) provider."""
        for p in self.providers:
            if p.is_available():
                return p
        return None

    @property
    def primary_provider(self) -> Optional[ProviderInfo]:
        """Get the highest-priority available provider."""
        return self.active_provider

    def invoke(self, messages: list, **kwargs) -> Any:
        """
        Invoke LLM with automatic fallback.
        Tries providers in priority order until one succeeds.
        """
        if not self._initialized:
            raise RuntimeError("LLM Router not initialized")

        last_error = None

        for provider in self.providers:
            if not provider.is_available():
                logger.debug(f"Skipping {provider.name} (status: {provider.status.value})")
                continue

            try:
                result = provider.model.invoke(messages, **kwargs)
                provider.record_success()
                logger.debug(f"LLM call succeeded via {provider.name}")
                return result
            except Exception as e:
                error_msg = str(e)
                provider.record_failure(error_msg)
                last_error = e
                logger.warning(f"Provider {provider.name} failed: {error_msg[:200]}")

        # All providers failed
        logger.error(f"All LLM providers failed. Last error: {last_error}")
        raise RuntimeError(
            f"All LLM providers failed. Last error: {last_error}"
        )

    async def ainvoke(self, messages: list, **kwargs) -> Any:
        """Async invoke with automatic fallback."""
        if not self._initialized:
            raise RuntimeError("LLM Router not initialized")

        last_error = None

        for provider in self.providers:
            if not provider.is_available():
                logger.debug(f"Skipping {provider.name} (status: {provider.status.value})")
                continue

            try:
                result = await provider.model.ainvoke(messages, **kwargs)
                provider.record_success()
                logger.debug(f"Async LLM call succeeded via {provider.name}")
                return result
            except Exception as e:
                error_msg = str(e)
                provider.record_failure(error_msg)
                last_error = e
                logger.warning(f"Provider {provider.name} failed: {error_msg[:200]}")

        logger.error(f"All LLM providers failed. Last error: {last_error}")
        raise RuntimeError(
            f"All LLM providers failed. Last error: {last_error}"
        )

    def get_health_status(self) -> Dict[str, Any]:
        """Get health status of all providers."""
        active = self.active_provider
        return {
            "active_provider": active.name if active else "none",
            "total_providers": len(self.providers),
            "available_providers": sum(1 for p in self.providers if p.is_available()),
            "providers": [p.get_stats() for p in self.providers],
        }

    def force_provider(self, provider_name: str) -> bool:
        """Force use of a specific provider (bypass priority)."""
        for p in self.providers:
            if p.name == provider_name:
                if p.is_available():
                    # Move to front of list temporarily
                    self.providers.remove(p)
                    self.providers.insert(0, p)
                    logger.info(f"Forced provider: {provider_name}")
                    return True
                else:
                    logger.warning(f"Provider {provider_name} is not available")
                    return False
        logger.warning(f"Unknown provider: {provider_name}")
        return False


# Global router instance
llm_router = AEGISLLMRouter()
