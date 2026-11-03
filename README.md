
# HOT TAKES

An AI-powered anime discovery and entertainment platform designed to help fans find anime, take part in community discussions, play anime quizzes, and discover characters that match their personality.

> **Project status:** In development. The repository currently contains the planned project structure. Features will be implemented and tested phase by phase.

## Features

### 1. Anime Community and Discussions
- Create discussion threads and reply to other users.
- Share opinions, recommendations, and anime-related questions.
- Browse anime-related discussions and participate in the community.
- Support moderation and reporting tools.

### 2. AI Anime Recommendations
- Discover anime based on preferences, mood, and similar titles.
- Explore hidden gems and recommendations from different genres.
- See explanations for why an anime was recommended.
- Save recommendations and provide likes, dislikes, or feedback.
- Improve future recommendations using user feedback and preference history.

### 3. Anime Quiz
- Play quizzes across categories such as characters, scenes, quotes, openings, endings, relationships, and trivia.
- Choose from multiple difficulty levels.
- Participate in timed quizzes, daily challenges, and weekly competitions.
- Track scores, streaks, achievements, and leaderboard rankings.
- Support weekly and annual rewards with published eligibility and competition rules.

### 4. Character Matching
- Answer a personality and preferences questionnaire.
- Discover anime characters that match the selected traits.
- View compatibility scores and explanations.
- Save, compare, and share character matches.

Character matching is intended for entertainment and is not a psychological assessment.

### 5. AI Hot Takes
- Explore anime opinions and discussion prompts.
- Vote, share viewpoints, and participate in debates.
- Browse popular, unpopular, and controversial opinions.
- Use AI-generated drafts only after operator review and approval.

### 6. Operator Dashboard
- Manage anime and character information.
- Review and approve AI-generated content.
- Manage quiz questions, hot takes, and community content.
- Monitor AI performance and user feedback.
- Maintain content controls and review history.

## AI and Content Review

The platform is planned to use separate AI systems for recommendations, quizzes, character matching, and hot takes. These systems may generate suggestions or draft content, but generated public content will go through an operator review process.

The planned workflow is:

1. The AI generates a recommendation or content draft.
2. The draft enters a review queue.
3. An operator checks, edits, approves, or rejects it.
4. Approved content can be published.
5. User interactions and feedback help improve future ranking and generation.

The project does not plan to retrain a model after every user interaction. Initial improvements will use preference data, feedback, ranking logic, approved content, and quiz performance.

## Technology Stack

| Area | Planned technologies |
|---|---|
| Backend | Python, Flask |
| Frontend | HTML, CSS, JavaScript |
| 3D and visual effects | Three.js, where useful |
| Database | SQLite for local development, PostgreSQL for production |
| ORM | SQLAlchemy |
| Authentication | Flask-Login |
| Forms and validation | Flask-WTF, WTForms |
| AI features | LLM API and Python-based recommendation logic |
| Data analysis | Pandas, NumPy |
| Recommendation experiments | scikit-learn |
| Background jobs | Celery and Redis, if required |
| Testing | pytest |
| Version control | Git and GitHub |

Three.js is an optional visual layer. Core features such as authentication, discussions, quizzes, recommendations, and the operator dashboard should remain usable without 3D effects.

## Project Structure

```text
anime-discovery-platform/
├── run.py
├── config.py
├── requirements.txt
├── .env.example
├── .gitignore
├── README.md
│
├── app/
│   ├── __init__.py
│   ├── extensions.py
│   ├── models/
│   ├── blueprints/
│   │   ├── main/
│   │   ├── auth/
│   │   ├── anime/
│   │   ├── discussions/
│   │   ├── recommendations/
│   │   ├── quiz/
│   │   ├── character_match/
│   │   ├── hot_takes/
│   │   ├── profile/
│   │   └── operator/
│   ├── services/
│   ├── ai/
│   │   └── prompts/
│   ├── operator/
│   ├── utils/
│   ├── templates/
│   ├── static/
│   │   ├── css/
│   │   ├── js/
│   │   ├── images/
│   │   ├── icons/
│   │   └── media/
│   ├── tasks/
│   └── cli/
│
├── migrations/
├── tests/
├── instance/
└── docs/
```

## Development Roadmap

Development is organized into six phases.

### Phase 1: Foundation and Community
- Set up the Flask application and database.
- Implement authentication and operator permissions.
- Build the shared anime database.
- Develop discussions and basic moderation.

### Phase 2: Recommendation AI
- Build preference collection and recommendation pages.
- Add mood-based, similar-anime, and hidden-gem recommendations.
- Add explanations, saved recommendations, and feedback.
- Test and refine recommendation ranking.

### Phase 3: Quiz and Leaderboard
- Implement quiz categories, difficulty levels, timers, scoring, and results.
- Add daily challenges, weekly competitions, and leaderboards.
- Add reward tracking and anti-cheating checks.
- Keep quiz content subject to operator review.

### Phase 4: Character Matching
- Build the questionnaire and character database.
- Implement matching scores and explanations.
- Add saved matches and sharing.
- Prepare the first four core features for launch.

### Phase 5: Hot Takes
- Generate and review anime discussion prompts.
- Add voting, debate threads, and opinion categories.
- Publish only approved content.

### Phase 6: Additional Features and Improvements
- Add remaining planned community and entertainment features.
- Improve performance, moderation, analytics, and reliability.
- Expand AI features based on reviewed feedback and usage data.

## Getting Started

### Requirements
- Python 3.10 or newer
- Git
- Visual Studio Code or another code editor

### 1. Clone the repository

```bash
git clone https://github.com/YOUR-USERNAME/anime-discovery-platform.git
cd anime-discovery-platform
```

Replace `YOUR-USERNAME` with the GitHub account or organization that owns the repository.

### 2. Create a virtual environment

**Windows PowerShell:**

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

**macOS or Linux:**

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure environment variables

Copy `.env.example` to `.env` and fill in the required values.

Do not commit `.env` or publish API keys, database credentials, or other secrets.

### 5. Run the application

Once the Flask application and its configuration are implemented:

```bash
python run.py
```

The local development address will be shown in the terminal. The exact setup commands may change as the application is developed.

## Working with the Project

The project is being developed one feature at a time. Each feature should be implemented, tested, and stabilized before being connected to other features.

Suggested workflow:

1. Create a feature branch.
2. Make changes for that feature.
3. Test the relevant functionality.
4. Commit the changes.
5. Open a pull request into `main`.
6. Review and merge after testing.

Example:

```bash
git checkout -b feature/discussions
git add .
git commit -m "Build discussions feature"
git push -u origin feature/discussions
```

## Security and Responsible Use

- Keep API keys and credentials in environment variables.
- Validate and sanitize user input.
- Protect operator routes with role-based permissions.
- Use server-side scoring for competitive quizzes.
- Publish clear reward eligibility, tie-breaking, and payout rules before launching competitions.
- Review AI-generated content before publication.
- Provide moderation and reporting controls for community content.

## Contributing

Contributions and suggestions are welcome. For substantial changes, open an issue or discuss the planned work before submitting a pull request.

Please keep changes focused on one feature or task per branch.

## License

No license has been selected yet. Until a license is added, the repository should not be treated as granting permission to reuse, distribute, or modify the project.
