"""Optional starter questions for the Waifu question bank.

Run from the backend directory:
    python -m app.cli.seed_waifu_questions
The script does not auto-approve any questions.
"""
import os
from app import create_app
from app.services.waifu_catalog_service import create_question

STARTER_QUESTIONS = [
    {
        "prompt": "When you meet someone new, how do you usually behave?",
        "category": "Social energy", "profile_type": "personality",
        "trait_key": "introversion", "explanation": "Measures preferred social energy.",
        "options": [
            {"text":"I prefer to observe before speaking.","score":90},
            {"text":"I speak when I find a shared interest.","score":65},
            {"text":"I comfortably start conversations.","score":30},
            {"text":"I enjoy meeting and talking to almost everyone.","score":10}
        ]
    },
    {
        "prompt": "When someone you care about is upset, what do you usually do first?",
        "category": "Emotional support", "profile_type": "personality",
        "trait_key": "emotionality", "explanation": "Measures emotional responsiveness.",
        "options": [
            {"text":"Listen carefully and understand their feelings.","score":90},
            {"text":"Offer comfort and practical help.","score":75},
            {"text":"Give them space and check in later.","score":55},
            {"text":"Focus on solving the problem quickly.","score":35}
        ]
    },
    {
        "prompt": "How important is personal space in a relationship?",
        "category": "Relationship boundaries", "profile_type": "romantic",
        "trait_key": "personal_space", "explanation": "Measures preference for independence and space.",
        "options": [
            {"text":"Very important. We should both have our own time.","score":95},
            {"text":"Important, but I also enjoy spending time together.","score":70},
            {"text":"I prefer doing most things together.","score":35},
            {"text":"I want to spend nearly all my free time together.","score":10}
        ]
    },
    {
        "prompt": "What kind of affection would make you feel most appreciated?",
        "category": "Affection", "profile_type": "romantic",
        "trait_key": "affection", "explanation": "Measures preference for expressed affection.",
        "options": [
            {"text":"Small thoughtful gestures and quiet care.","score":35},
            {"text":"Honest words and regular reassurance.","score":70},
            {"text":"Open affection and frequent expressions of love.","score":95},
            {"text":"A balanced mix of actions and words.","score":80}
        ]
    }
]

def main():
    app = create_app({"TESTING": True, "SECRET_KEY": os.environ.get("SECRET_KEY","local-seed-only")})
    with app.app_context():
        for item in STARTER_QUESTIONS:
            create_question(item, "starter-seed")
    print(f"Created {len(STARTER_QUESTIONS)} starter question drafts. Review and approve them in the operator dashboard.")

if __name__ == "__main__":
    main()
