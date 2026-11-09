import re
from urllib.parse import urlparse

PERSONALITY_TRAITS = {
    "introversion": "Introversion",
    "emotionality": "Emotionality",
    "ambition": "Ambition",
    "independence": "Independence",
    "playfulness": "Playfulness",
    "communication": "Communication",
    "loyalty": "Loyalty",
    "conflict_style": "Conflict style",
}
ROMANTIC_TRAITS = {
    "affection": "Affection",
    "communication_preference": "Communication preference",
    "support_style": "Support style",
    "personal_space": "Personal space",
    "temperament": "Temperament",
    "relationship_dynamic": "Relationship dynamic",
    "trust": "Trust",
    "shared_values": "Shared values",
}
ALL_TRAITS = {"personality": PERSONALITY_TRAITS, "romantic": ROMANTIC_TRAITS}
STATUSES = {"draft", "pending_review", "approved", "rejected", "inactive"}

def clean_text(value, field, maximum=5000, required=False):
    value = str(value or "").strip()
    if required and not value:
        raise ValueError(f"{field} is required.")
    if len(value) > maximum:
        raise ValueError(f"{field} must be {maximum} characters or fewer.")
    return value

def safe_slug(value):
    value = re.sub(r"[^a-z0-9]+", "-", str(value or "").lower()).strip("-")
    return value[:100] or "character"

def validate_http_url(value, field, required=False):
    value = clean_text(value, field, 1000, required)
    if value:
        parsed = urlparse(value)
        if parsed.scheme not in ("http", "https") or not parsed.netloc:
            raise ValueError(f"{field} must be a valid http or https URL.")
    return value

def validate_traits(traits):
    if not isinstance(traits, dict):
        raise ValueError("Traits must be an object.")
    cleaned = {"personality": {}, "romantic": {}}
    for profile_type, allowed in ALL_TRAITS.items():
        supplied = traits.get(profile_type, {}) or {}
        if not isinstance(supplied, dict):
            raise ValueError(f"{profile_type} traits must be an object.")
        for key, score in supplied.items():
            if key not in allowed:
                raise ValueError(f"Unknown {profile_type} trait: {key}")
            try:
                score = int(score)
            except (TypeError, ValueError):
                raise ValueError(f"Score for {key} must be an integer.")
            if not 0 <= score <= 100:
                raise ValueError(f"Score for {key} must be between 0 and 100.")
            cleaned[profile_type][key] = score
    return cleaned

def validate_options(options):
    if not isinstance(options, list) or not 2 <= len(options) <= 8:
        raise ValueError("A question must have between 2 and 8 answer options.")
    result = []
    for index, item in enumerate(options):
        if isinstance(item, str):
            item = {"text": item, "score": 50}
        if not isinstance(item, dict):
            raise ValueError("Each answer option must be an object.")
        text = clean_text(item.get("text"), "Option text", 300, True)
        try:
            score = int(item.get("score", 50))
        except (TypeError, ValueError):
            raise ValueError("Option score must be an integer.")
        if not 0 <= score <= 100:
            raise ValueError("Option score must be between 0 and 100.")
        result.append({"text": text, "score": score, "order": index})
    return result
