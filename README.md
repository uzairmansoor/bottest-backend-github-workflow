# bottest.ai backend monolith service

Setup:

```
python3.10 -m venv .venv
```

MacOS:

```
. .venv/bin/activate
```

Windows:

```
. .venv/Scripts/activate
```

```
pip install -r requirements.txt
alembic upgrade head
pre-commit install
```

Then, add the following environment variables to `.env`:

```
ENVIRONMENT="development"
DATABASE_URI="sqlite:///local.db"
JWKS_URL="evolved-shad-78.clerk.accounts.dev"
CLERK_API_KEY="api_key_here"
OPENAI_API_KEY="api_key_here"
SLACK_TOKEN="token_here"
```
