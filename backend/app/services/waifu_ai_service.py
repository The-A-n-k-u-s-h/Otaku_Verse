import json
import os
import urllib.request
import urllib.error

from dotenv import load_dotenv

load_dotenv()


class AIConfigurationError(RuntimeError):
    pass


class AIProviderError(RuntimeError):
    pass


def _chat_completion(system_prompt, user_prompt, temperature=0.4):
    """OpenAI-compatible chat completion using Python's standard library."""
    api_key = os.getenv("OPENAI_API_KEY", "").strip()
    if not api_key:
        raise AIConfigurationError("Set OPENAI_API_KEY before using AI generation.")
    
    base_url = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1").rstrip("/")
    model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
    
    payload = {
        "model": model,
        "temperature": temperature,
        "response_format": {"type": "json_object"},
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
    }
    
    req = urllib.request.Request(
        base_url + "/chat/completions",
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Authorization": "Bearer " + api_key,
            "Content-Type": "application/json",
        },
        method="POST",
    )
    
    try:
        with urllib.request.urlopen(req, timeout=60) as response:
            result = json.loads(response.read().decode("utf-8"))
        content = result["choices"][0]["message"]["content"]
        parsed = json.loads(content)
        if not isinstance(parsed, dict):
            raise ValueError("AI response must be a JSON object.")
        return parsed
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")[:1000]
        raise AIProviderError(f"AI provider returned HTTP {exc.code}: {detail}") from exc
    except (urllib.error.URLError, TimeoutError, KeyError, IndexError, json.JSONDecodeError) as exc:
        raise AIProviderError(f"Could not generate valid JSON from the AI provider: {exc}") from exc


def generate_question_drafts(topic, profile_type, trait_key, count=3, audience="adult anime fans"):
    system = """You create thoughtful, non-clinical anime soulmate questionnaire drafts.
Return JSON only: {"questions":[{"prompt":"...","category":"...","profile_type":"personality or romantic","trait_key":"...","explanation":"...","options":[{"text":"...","score":0}]}]}.
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
Return JSON only: {"characters":[{"name":"...","anime_title":"...","aliases":"","description":"...","biography":"...","image_url":"","image_source_url":"","personality_traits":{"introversion":50},"romantic_traits":{"affection":50},"source_suggestions":[{"name":"...","url":"https://...","notes":"..."}]}]}.
Do not invent source URLs or image URLs. If you cannot confidently provide a real URL, leave it blank. Traits are editorial estimates from publicly portrayed character behaviour, not facts or psychological assessments. Use only female characters. Never invent canon details."""
    user = f"""Suggest up to {count} female character candidates from anime: {anime_title}.
Additional operator research notes: {notes}
Use known characters only. If uncertain, omit rather than guess."""
    data = _chat_completion(system, user, 0.3)
    characters = data.get("characters")
    if not isinstance(characters, list) or not characters:
        raise AIProviderError("AI returned no character candidates.")
    return characters[:count]