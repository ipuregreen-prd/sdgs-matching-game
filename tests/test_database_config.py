"""Local credential loading tests; never connect to a database."""
import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from app import database_config


class DatabaseConfigTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.env_file = self.root / ".env"
        self.env_file.write_text(
            "TURSO_DATABASE_URL=libsql://obsolete.example\n"
            "TURSO_TOKEN_FILE=tokens.env\n", encoding="utf-8")
        self.tokens = {key: "fake-token-" + str(i)
                       for i, key in enumerate(database_config.TOKEN_KEYS.values())}
        self.tokens.update({
            key.replace("_TOKEN", "_URL"): "libsql://production.example"
            for key in database_config.TOKEN_KEYS.values()
        })
        self.tokens.update(GITHUB_TOKEN="fake-github-token", VERCEL_TOKEN="fake-vercel-token")
        self.write_tokens()
        env_patch = patch.dict(os.environ, {}, clear=True)
        env_patch.start()
        self.addCleanup(env_patch.stop)
        file_patch = patch.object(database_config, "ENV_FILE", self.env_file)
        file_patch.start()
        self.addCleanup(file_patch.stop)

    def write_tokens(self):
        (self.root / "tokens.env").write_text(
            "\n".join(key + "=" + value for key, value in self.tokens.items()),
            encoding="utf-8-sig")

    def test_loads_matching_tokens_from_relative_file(self):
        database_config.load_database_config()
        self.assertEqual(os.environ["TURSO_DATABASE_URL"], "libsql://production.example")
        for variable, key in database_config.TOKEN_KEYS.items():
            self.assertEqual(os.environ[variable], self.tokens[key])
        for variable, key in database_config.URL_KEYS.items():
            self.assertEqual(os.environ[variable], self.tokens[key])
        self.assertNotIn("GITHUB_TOKEN", os.environ)
        self.assertNotIn("VERCEL_TOKEN", os.environ)

    def test_loads_urls_even_when_project_env_only_references_shared_file(self):
        self.env_file.write_text("TURSO_TOKEN_FILE=tokens.env\n", encoding="utf-8")
        database_config.load_database_config()
        self.assertEqual(os.environ["TURSO_DATABASE_URL"], "libsql://production.example")

    def test_missing_url_fails_before_changing_environment(self):
        self.tokens.pop(next(iter(database_config.TOKEN_KEYS.values())).replace("_TOKEN", "_URL"))
        self.write_tokens()
        with self.assertRaises(RuntimeError):
            database_config.load_database_config()
        self.assertNotIn("TURSO_DATABASE_URL", os.environ)
        self.assertNotIn("TURSO_AUTH_TOKEN", os.environ)

    def test_explicit_runtime_database_settings_take_priority(self):
        for settings in (
            {"TURSO_DATABASE_URL": "libsql://explicit.example", "TURSO_AUTH_TOKEN": "explicit"},
            {"DATABASE_PATH": ":memory:"},
            {"SDGS_DB_PATH": ":memory:"},
            {"TURSO_DATABASE_URL": "", "TURSO_AUTH_TOKEN": ""},
        ):
            with self.subTest(settings=settings), patch.dict(os.environ, settings, clear=True):
                database_config.load_database_config()
                self.assertEqual(dict(os.environ), settings)

    def test_vercel_uses_deployment_environment(self):
        os.environ["VERCEL"] = "1"
        database_config.load_database_config()
        self.assertNotIn("TURSO_DATABASE_URL", os.environ)

    def test_missing_token_fails_before_changing_environment(self):
        self.tokens.clear()
        self.write_tokens()
        with self.assertRaises(RuntimeError):
            database_config.load_database_config()
        self.assertNotIn("TURSO_DATABASE_URL", os.environ)
        self.assertNotIn("TURSO_AUTH_TOKEN", os.environ)

    def test_existing_dotenv_credentials_remain_supported(self):
        self.env_file.write_text(
            "TURSO_DATABASE_URL=libsql://explicit.example\nTURSO_AUTH_TOKEN=fake-token\n",
            encoding="utf-8")
        database_config.load_database_config()
        self.assertEqual(os.environ["TURSO_AUTH_TOKEN"], "fake-token")
