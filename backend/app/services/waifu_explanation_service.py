
from app.services.waifu_ai_service import (
    _chat_completion,
    AIConfigurationError,
    AIProviderError
)


def generate_match_explanation(match_result, user_profiles):
    character = match_result["character"]

    personality_score = match_result["personality_score"]
    romantic_score = match_result["romantic_score"]
    compatibility_score = match_result["compatibility_score"]

    character_name = character["name"]
    anime_title = character["anime_title"]

    personality_traits = user_profiles["personality"]
    romantic_traits = user_profiles["romantic"]

    system_prompt = """
You are an anime character compatibility explanation assistant.

Your task is to explain why a fictional female anime character
was selected as a user's romantic soulmate match.

Rules:
1. Use only the information supplied in the user data.
2. Do not invent character behaviour or anime story details.
3. Explain personality compatibility separately from romantic compatibility.
4. Explain the overall compatibility score.
5. Be warm, engaging and personalised.
6. Do not claim that the result is scientifically proven.
7. Do not make sexual or inappropriate statements.
8. Return valid JSON only.

Required JSON structure:
{
    "headline": "A short personalised headline",
    "summary": "A personalised explanation",
    "personality_reason": "Why the personality profiles match",
    "romantic_reason": "Why the romantic preferences match",
    "strongest_connections": [
        "Connection one",
        "Connection two"
    ],
    "compatibility_message": "A final personalised message"
}
"""

    user_prompt = f"""
Character:
{character_name}

Anime:
{anime_title}

Overall compatibility:
{compatibility_score}%

Personality compatibility:
{personality_score}%

Romantic compatibility:
{romantic_score}%

User personality profile:
{personality_traits}

User romantic preference profile:
{romantic_traits}

Character personality traits:
{character["traits"]["personality"]}

Character romantic traits:
{character["traits"]["romantic"]}

Generate a personalised explanation using these details.
"""

    result = _chat_completion(
        system_prompt,
        user_prompt,
        temperature=0.6
    )

    required_fields = [
        "headline",
        "summary",
        "personality_reason",
        "romantic_reason",
        "strongest_connections",
        "compatibility_message"
    ]

    for field in required_fields:
        if field not in result:
            raise AIProviderError(
                f"AI explanation is missing the {field} field."
            )

    if not isinstance(result["strongest_connections"], list):
        raise AIProviderError(
            "AI returned an invalid strongest_connections field."
        )

    return result


def get_match_explanation(match_result, user_profiles):
    """
    Try AI explanation first.
    If AI is unavailable, return a basic explanation
    based on the calculated compatibility scores.
    """
    try:
        return {
            "source": "ai",
            "explanation": generate_match_explanation(
                match_result,
                user_profiles
            )
        }

    except (AIConfigurationError, AIProviderError, ValueError):
        character = match_result["character"]

        return {
            "source": "fallback",
            "explanation": {
                "headline": (
                    f"{character['name']} is your best anime match!"
                ),
                "summary": (
                    f"{character['name']} from {character['anime_title']} "
                    "has the highest compatibility score among the "
                    "approved characters in the database."
                ),
                "personality_reason": (
                    f"Your personality compatibility score is "
                    f"{match_result['personality_score']}%."
                ),
                "romantic_reason": (
                    f"Your romantic preference compatibility score is "
                    f"{match_result['romantic_score']}%."
                ),
                "strongest_connections": [],
                "compatibility_message": (
                    f"Your overall estimated compatibility is "
                    f"{match_result['compatibility_score']}%. "
                    "This is an entertainment-based matching result."
                )
            }
        }
