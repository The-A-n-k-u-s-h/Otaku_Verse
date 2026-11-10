
from app import create_app
from app.services.waifu_catalog_service import (
    create_question,
    list_questions
)

QUESTIONS = [
    {
        "prompt": "When you face a difficult situation, what is your first reaction?",
        "category": "Personality",
        "profile_type": "personality",
        "trait_key": "conflict_style",
        "explanation": "Measures how the user handles challenges and disagreements.",
        "options": [
            {"text": "Face the situation directly and confidently.", "score": 95},
            {"text": "Think carefully before taking action.", "score": 75},
            {"text": "Discuss it with someone I trust.", "score": 55},
            {"text": "Avoid unnecessary confrontation.", "score": 25}
        ]
    },
    {
        "prompt": "What kind of person do you naturally admire?",
        "category": "Personality",
        "profile_type": "personality",
        "trait_key": "ambition",
        "explanation": "Measures admiration for ambition and determination.",
        "options": [
            {"text": "Someone who never gives up on their dreams.", "score": 95},
            {"text": "Someone who works steadily towards their goals.", "score": 75},
            {"text": "Someone who values a peaceful life.", "score": 50},
            {"text": "Someone who prefers going with the flow.", "score": 25}
        ]
    },
    {
        "prompt": "How do you usually express care for someone?",
        "category": "Personality",
        "profile_type": "personality",
        "trait_key": "emotionality",
        "explanation": "Measures emotional responsiveness and care.",
        "options": [
            {"text": "I openly express my feelings.", "score": 95},
            {"text": "I listen and offer emotional support.", "score": 80},
            {"text": "I show care through practical actions.", "score": 60},
            {"text": "I find it difficult to express emotions.", "score": 25}
        ]
    },
    {
        "prompt": "What would make you feel most secure in a relationship?",
        "category": "Romantic Preference",
        "profile_type": "romantic",
        "trait_key": "trust",
        "explanation": "Measures the importance of trust and reliability.",
        "options": [
            {"text": "Complete honesty and mutual trust.", "score": 100},
            {"text": "Consistent support and loyalty.", "score": 80},
            {"text": "Freedom with mutual understanding.", "score": 60},
            {"text": "Excitement and spontaneity.", "score": 35}
        ]
    },
    {
        "prompt": "How would you prefer your ideal partner to support you?",
        "category": "Romantic Preference",
        "profile_type": "romantic",
        "trait_key": "support_style",
        "explanation": "Measures preferred emotional and practical support.",
        "options": [
            {"text": "Stay beside me and listen patiently.", "score": 95},
            {"text": "Help me find solutions to my problems.", "score": 75},
            {"text": "Give me space but check on me later.", "score": 55},
            {"text": "Make me laugh and distract me from stress.", "score": 35}
        ]
    }
]


def main():
    app = create_app({
        "TESTING": True
    })

    with app.app_context():
        existing = {
            q["prompt"].strip().casefold()
            for q in list_questions()
        }

        added = 0
        skipped = 0

        for index, question in enumerate(QUESTIONS, start=1):
            if question["prompt"].strip().casefold() in existing:
                print(f"SKIPPED: Question {index} already exists.")
                skipped += 1
                continue

            try:
                created = create_question(
                    question,
                    actor="manual_sqlite_seed"
                )

                print(
                    f"ADDED: {created['id']} | "
                    f"{question['prompt']}"
                )

                added += 1

            except Exception as error:
                print(f"ERROR on question {index}: {error}")

        print("\n========== IMPORT SUMMARY ==========")
        print("Added:", added)
        print("Skipped:", skipped)
        print("Total:", len(QUESTIONS))
        print("Status: Newly created questions are drafts.")
        print("====================================")


if __name__ == "__main__":
    main()
