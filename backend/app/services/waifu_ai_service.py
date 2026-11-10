"""Multi-provider AI service with key rotation, useful diagnostics and failover.

All configured providers use the OpenAI-compatible Chat Completions protocol.
Public function names/signatures are kept compatible with existing callers.
API keys and raw provider response bodies are never logged or returned.
"""
import json
import logging
import os
import random
import re
import time
import urllib.error
import urllib.request
from dataclasses import dataclass
from email.utils import parsedate_to_datetime
from typing import Any

from dotenv import load_dotenv
from pathlib import Path

# Load backend/.env when present, otherwise fall back to the project-root .env.
# override=False preserves environment variables already supplied by the OS.
_PROJECT_ROOT = Path(__file__).resolve().parents[3]
_BACKEND_ENV = _PROJECT_ROOT / "backend" / ".env"
_ROOT_ENV = _PROJECT_ROOT / ".env"
if _BACKEND_ENV.is_file():
    load_dotenv(_BACKEND_ENV, override=False)
elif _ROOT_ENV.is_file():
    load_dotenv(_ROOT_ENV, override=False)
else:
    load_dotenv(override=False)

logger = logging.getLogger(__name__)


class AIConfigurationError(RuntimeError):
    pass


class AIProviderError(RuntimeError):
    def __init__(self, message: str, *, retryable: bool = False, retry_after: float | None = None):
        super().__init__(message)
        self.retryable = retryable
        self.retry_after = retry_after


@dataclass(frozen=True)
class Provider:
    name: str
    base_url: str
    model: str
    keys: tuple[str, ...]
    timeout: int = 12
    max_retries: int = 0

    @property
    def enabled(self) -> bool:
        return bool(self.base_url and self.model and self.keys)


def _csv_env(name: str) -> list[str]:
    return [item.strip() for item in os.getenv(name, "").split(",") if item.strip()]


def _provider_config(name: str) -> Provider | None:
    name = name.strip().lower()
    presets = {
        "openai": {"url": "https://api.openai.com/v1", "key_env": "OPENAI_API_KEYS", "single_key_env": "OPENAI_API_KEY", "model_env": "OPENAI_MODEL", "default_model": "gpt-4o-mini"},
        "gemini": {"url": "https://generativelanguage.googleapis.com/v1beta/openai", "key_env": "GEMINI_API_KEYS", "single_key_env": "GEMINI_API_KEY", "model_env": "GEMINI_MODEL", "default_model": "gemini-3.8-flash"},
        "groq": {"url": "https://api.groq.com/openai/v1", "key_env": "GROQ_API_KEYS", "single_key_env": "GROQ_API_KEY", "model_env": "GROQ_MODEL", "default_model": "llama-3.3-70b-versatile"},
        "openrouter": {"url": "https://openrouter.ai/api/v1", "key_env": "OPENROUTER_API_KEYS", "single_key_env": "OPENROUTER_API_KEY", "model_env": "OPENROUTER_MODEL", "default_model": ""},
        "custom": {"url": "", "key_env": "CUSTOM_AI_API_KEYS", "single_key_env": "CUSTOM_AI_API_KEY", "model_env": "CUSTOM_AI_MODEL", "default_model": ""},
    }
    preset = presets.get(name)
    if not preset:
        logger.warning("Ignoring unknown AI provider name: %s", name)
        return None

    # Combine singular and plural variables. Previously the plural variable
    # silently shadowed the singular variable whenever it contained a key.
    keys = _csv_env(preset["key_env"]) + _csv_env(preset["single_key_env"])
    # Backward compatibility with the CUSTOM_AI_KEYS name used in older .env files.
    if name == "custom":
        keys += _csv_env("CUSTOM_AI_KEYS")
    keys = list(dict.fromkeys(keys))

    # CUSTOM_BASE_URL is the documented custom endpoint variable. Other
    # providers retain their PROVIDER_BASE_URL naming convention.
    base_env = "CUSTOM_BASE_URL" if name == "custom" else f"{name.upper()}_BASE_URL"
    base_url = os.getenv(base_env, preset["url"]).strip().rstrip("/")
    model = os.getenv(preset["model_env"], preset["default_model"]).strip()
    if not base_url or not model or not keys:
        return None

    try:
        timeout = max(5, min(20, int(os.getenv("AI_PROVIDER_TIMEOUT", "12"))))
        retries = max(0, min(2, int(os.getenv("AI_PROVIDER_RETRIES", "0"))))
    except ValueError:
        timeout, retries = 12, 0
    return Provider(name, base_url, model, tuple(keys), timeout, retries)


def get_provider_status() -> list[dict[str, Any]]:
    """Safe configuration status. Never exposes API keys."""
    order = _csv_env("AI_PROVIDER_ORDER") or ["gemini", "groq", "openrouter", "openai", "custom"]
    result = []
    for name in order:
        config = _provider_config(name)
        result.append({
            "provider": name,
            "configured": bool(config and config.enabled),
            "model": config.model if config else None,
            "key_count": len(config.keys) if config else 0,
        })
    return result


def _extract_json(content: Any) -> dict:
    if isinstance(content, list):
        content = "\n".join(str(part.get("text", "")) for part in content if isinstance(part, dict))
    if not isinstance(content, str) or not content.strip():
        raise AIProviderError("Provider returned an empty response.")
    text = content.strip()
    text = re.sub(r"^```(?:json)?\s*", "", text, flags=re.IGNORECASE)
    text = re.sub(r"\s*```$", "", text)
    try:
        value = json.loads(text)
    except json.JSONDecodeError:
        start, end = text.find("{"), text.rfind("}")
        if start < 0 or end <= start:
            raise AIProviderError("Provider did not return a JSON object.")
        try:
            value = json.loads(text[start:end + 1])
        except json.JSONDecodeError as exc:
            raise AIProviderError("Provider returned malformed JSON.") from exc
    if not isinstance(value, dict):
        raise AIProviderError("AI response must be a JSON object.")
    return value


def _safe_provider_detail(raw: bytes) -> str:
    """Extract a short provider error message, excluding secrets and payloads."""
    try:
        body = json.loads(raw[:8192].decode("utf-8", errors="replace"))
        error = body.get("error", body) if isinstance(body, dict) else {}
        if isinstance(error, dict):
            message = str(error.get("message") or error.get("status") or "").strip()
        else:
            message = str(error).strip()
    except (ValueError, TypeError):
        message = ""
    message = re.sub(r"Bearer\s+\S+", "Bearer [REDACTED]", message, flags=re.I)
    message = re.sub(r"AIza[0-9A-Za-z_-]{20,}", "[REDACTED]", message)
    message = re.sub(r"sk-[A-Za-z0-9_-]{12,}", "[REDACTED]", message)
    message = re.sub(r"\s+", " ", message)
    return message[:240]


def _retry_after_seconds(exc: urllib.error.HTTPError) -> float | None:
    value = exc.headers.get("Retry-After") if exc.headers else None
    if not value:
        return None
    try:
        return max(0.0, min(30.0, float(value)))
    except ValueError:
        try:
            dt = parsedate_to_datetime(value)
            return max(0.0, min(30.0, dt.timestamp() - time.time()))
        except (TypeError, ValueError, OverflowError):
            return None


def _request_once(provider: Provider, api_key: str, system_prompt: str,
                  user_prompt: str, temperature: float, timeout: float | None = None) -> dict:
    payload = {
        "model": provider.model,
        "temperature": temperature,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
    }
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "Accept": "application/json",
    }
    if provider.name == "openrouter":
        headers["HTTP-Referer"] = os.getenv("OPENROUTER_SITE_URL", "https://otakuverse.local")
        headers["X-Title"] = os.getenv("OPENROUTER_APP_NAME", "OtakuVerse")

    request = urllib.request.Request(
        provider.base_url + "/chat/completions",
        data=json.dumps(payload).encode("utf-8"),
        headers=headers,
        method="POST",
    )
    try:
        request_timeout = provider.timeout if timeout is None else max(1.0, min(float(provider.timeout), timeout))
        with urllib.request.urlopen(request, timeout=request_timeout) as response:
            result = json.loads(response.read().decode("utf-8"))
        content = result["choices"][0]["message"]["content"]
        return _extract_json(content)
    except urllib.error.HTTPError as exc:
        detail = _safe_provider_detail(exc.read())
        suffix = f" Details: {detail}" if detail else ""
        retryable = exc.code == 429 or 500 <= exc.code <= 599
        raise AIProviderError(
            f"{provider.name} returned HTTP {exc.code}.{suffix}",
            retryable=retryable,
            retry_after=_retry_after_seconds(exc),
        ) from exc
    except (urllib.error.URLError, TimeoutError, OSError) as exc:
        raise AIProviderError(
            f"{provider.name} connection failed: {type(exc).__name__}.", retryable=True
        ) from exc
    except (KeyError, IndexError, TypeError, json.JSONDecodeError) as exc:
        raise AIProviderError(f"{provider.name} returned an unexpected response format.") from exc


def _chat_completion(system_prompt, user_prompt, temperature=0.4):
    """Try configured providers in order within one overall time budget."""
    order = _csv_env("AI_PROVIDER_ORDER") or ["gemini", "groq", "openrouter", "openai", "custom"]
    configured = []
    for name in order:
        provider = _provider_config(name)
        if provider and provider.enabled:
            configured.append(provider)

    if not configured:
        raise AIConfigurationError(
            "No AI provider is configured. Check API keys, base URLs and model names in the root .env file."
        )

    try:
        total_timeout = max(5, min(60, int(os.getenv("AI_TOTAL_TIMEOUT", "25"))))
    except ValueError:
        total_timeout = 25

    deadline = time.monotonic() + total_timeout
    failures = []

    for provider in configured:
        if time.monotonic() >= deadline:
            failures.append("Overall AI time limit reached before all providers could be tried.")
            break

        keys = list(provider.keys)
        random.shuffle(keys)

        for key in keys:
            attempt = 0
            while True:
                remaining = deadline - time.monotonic()
                if remaining <= 1:
                    failures.append("Overall AI time limit reached.")
                    break

                try:
                    answer = _request_once(
                        provider, key, system_prompt, user_prompt, temperature,
                        timeout=min(provider.timeout, remaining - 0.25)
                    )
                    logger.info(
                        "AI request succeeded with provider=%s model=%s",
                        provider.name, provider.model
                    )
                    return answer
                except AIProviderError as exc:
                    # Never log API keys. Provider errors are sanitized before reaching here.
                    failures.append(str(exc))
                    logger.warning(
                        "AI provider attempt failed: provider=%s attempt=%s reason=%s",
                        provider.name, attempt + 1, exc
                    )

                    if not exc.retryable or attempt >= provider.max_retries:
                        break

                    remaining = deadline - time.monotonic()
                    if remaining <= 1:
                        break

                    delay = exc.retry_after if exc.retry_after is not None else min(1.0 * (2 ** attempt), 3.0)
                    delay = min(delay, max(0.0, remaining - 1.0))
                    if delay > 0:
                        time.sleep(delay)
                    attempt += 1

            if time.monotonic() >= deadline:
                break

    summary = "; ".join(failures[-8:])
    raise AIProviderError(
        f"AI providers could not complete the request within {total_timeout} seconds. "
        "Check provider keys, model access, quotas and network connectivity. "
        f"Provider diagnostics: {summary}"
    )


def generate_question_drafts(topic, profile_type, trait_key, count=3, audience="adult anime fans"):
    system = """You create thoughtful, non-clinical anime soulmate questionnaire drafts.
Return JSON only: {\"questions\":[{\"prompt\":\"...\",\"category\":\"...\",\"profile_type\":\"personality or romantic\",\"trait_key\":\"...\",\"explanation\":\"...\",\"options\":[{\"text\":\"...\",\"score\":0}]}]}.
Create 2-8 balanced answer options per question. Scores are illustrative 0-100 trait intensity, not diagnosis. Avoid leading, offensive, sexual, or age-inappropriate content. Do not claim scientific validity."""
    user = f"""Create {count} distinct draft questions about: {topic}.
Profile type: {profile_type}. Trait key: {trait_key}. Audience: {audience}.
Use exactly this profile_type and trait_key for every question. Scores should span a useful range. Keep prompts concise."""
    data = _chat_completion(system, user, 0.65)
    questions = data.get("questions")
    if not isinstance(questions, list) or not questions:
        raise AIProviderError("AI returned no question drafts.")
    return questions[:count]


def discover_character_candidates(anime_title, count=3, notes=""):
    system = """You help an operator research female anime character candidates for a fictional compatibility catalogue.
Return JSON only: {\"characters\":[{\"name\":\"...\",\"anime_title\":\"...\",\"aliases\":\"\",\"description\":\"...\",\"biography\":\"...\",\"image_url\":\"\",\"image_source_url\":\"\",\"personality_traits\":{\"introversion\":50},\"romantic_traits\":{\"affection\":50},\"source_suggestions\":[{\"name\":\"...\",\"url\":\"https://...\",\"notes\":\"...\"}]}]}.
Do not invent source URLs or image URLs. If you cannot confidently provide a real URL, leave it blank. Traits are editorial estimates from publicly portrayed character behaviour, not facts or psychological assessments. Use only female characters. Never invent canon details."""
    user = f"""Suggest up to {count} female character candidates from anime: {anime_title}.
Additional operator research notes: {notes}
Use known characters only. If uncertain, omit rather than guess."""
    data = _chat_completion(system, user, 0.3)
    characters = data.get("characters")
    if not isinstance(characters, list) or not characters:
        raise AIProviderError("AI returned no character candidates.")
    return characters[:count]
