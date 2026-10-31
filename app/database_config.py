"""Load local database URLs and tokens from the shared credentials file."""
import os
from pathlib import Path
from dotenv import dotenv_values, load_dotenv

ENV_FILE = Path(__file__).resolve().parent.parent / ".env"
URL_KEYS = {
    "TURSO_DATABASE_URL": "sdgs-matching-game_TURSO_AUTH_URL"
}
TOKEN_KEYS = {
    "TURSO_AUTH_TOKEN": "sdgs-matching-game_TURSO_AUTH_TOKEN"
}


def load_database_config():
    # Explicit runtime settings (including SQLite tests) take priority.
    if os.environ.get("VERCEL") or any(key in os.environ for key in (
        "TURSO_DATABASE_URL", "TURSO_AUTH_TOKEN", "DATABASE_PATH", "SDGS_DB_PATH"
    )):
        return
    config = dotenv_values(ENV_FILE, encoding="utf-8-sig")
    token_file = config.get("TURSO_TOKEN_FILE")
    if not token_file:
        load_dotenv(ENV_FILE, encoding="utf-8-sig")
        return
    tokens = dotenv_values(ENV_FILE.parent / token_file, encoding="utf-8-sig")
    values = dict(config)
    for variable, token_key in {**URL_KEYS, **TOKEN_KEYS}.items():
        if not tokens.get(token_key):
            raise RuntimeError("Missing database setting: " + token_key)
        values[variable] = tokens[token_key]
    for key, value in values.items():
        if value is not None:
            os.environ.setdefault(key, value)
