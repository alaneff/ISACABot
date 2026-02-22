"""
Centralized configuration for the Agentic Pipeline Factory.

All settings are read from environment variables (or a .env file).
Import `settings` anywhere in the project — no repeated os.getenv() calls.

Usage:
    from config.settings import settings
    print(settings.model)
"""

import logging
import os

from dotenv import load_dotenv

# Load .env file if present (does nothing if missing — safe for prod)
load_dotenv()


class Settings:
    """Single source of truth for all pipeline configuration."""

    # ── Anthropic ──────────────────────────────────────────────────────────

    @property
    def anthropic_api_key(self) -> str:
        key = os.getenv("ANTHROPIC_API_KEY", "")
        if not key:
            raise EnvironmentError(
                "ANTHROPIC_API_KEY is not set. "
                "Copy .env.example to .env and add your key."
            )
        return key

    @property
    def model(self) -> str:
        """Default Claude model. Override per-pipeline when needed."""
        return os.getenv("ANTHROPIC_MODEL", "claude-sonnet-4-6")

    # ── Claude generation defaults ─────────────────────────────────────────
    # These are the recommended defaults for agentic work.
    # Agents can override them via default_options={}.

    @property
    def max_tokens(self) -> int:
        return int(os.getenv("MAX_TOKENS", "8096"))

    @property
    def extended_thinking(self) -> bool:
        return os.getenv("EXTENDED_THINKING", "false").lower() == "true"

    @property
    def thinking_budget_tokens(self) -> int:
        return int(os.getenv("THINKING_BUDGET_TOKENS", "5000"))

    @property
    def default_options(self) -> dict:
        """
        Build the default_options dict to pass to agent.as_agent().
        Extended thinking is only included when enabled — it requires
        max_tokens > thinking_budget_tokens to leave room for the response.
        """
        opts: dict = {"max_tokens": self.max_tokens}
        if self.extended_thinking:
            opts["thinking"] = {
                "type": "enabled",
                "budget_tokens": self.thinking_budget_tokens,
            }
            # Ensure max_tokens can fit both thinking and response
            if self.max_tokens <= self.thinking_budget_tokens:
                opts["max_tokens"] = self.thinking_budget_tokens + 4096
        return opts

    # ── Azure AD B2C (authentication for the web API) ──────────────────────
    # These are only required when running the FastAPI web API (api/app.py).
    # The CLI / local chatbot does not need them.

    @property
    def b2c_tenant_name(self) -> str:
        """B2C tenant name (e.g. 'isacasdorg' for isacasdorg.b2clogin.com)."""
        return os.getenv("B2C_TENANT_NAME", "")

    @property
    def b2c_client_id(self) -> str:
        """App registration Client ID from the B2C tenant."""
        return os.getenv("B2C_CLIENT_ID", "")

    @property
    def b2c_policy_name(self) -> str:
        """User Flow / policy name (e.g. 'B2C_1_signupsignin')."""
        return os.getenv("B2C_POLICY_NAME", "B2C_1_signupsignin")

    @property
    def api_key(self) -> str:
        """
        Static API key for beta / local access when Azure AD B2C is not configured.
        Set API_KEY in .env to enable this auth mode.
        If neither B2C nor API_KEY is configured, the /api/chat endpoint will reject all requests.
        """
        return os.getenv("API_KEY", "")

    # ── Azure ──────────────────────────────────────────────────────────────

    @property
    def azure_app_name(self) -> str:
        return os.getenv("AZURE_APP_NAME", "agentic-pipeline-factory")

    @property
    def azure_resource_group(self) -> str:
        return os.getenv("AZURE_RESOURCE_GROUP", "")

    @property
    def azure_location(self) -> str:
        return os.getenv("AZURE_LOCATION", "eastus")

    @property
    def applicationinsights_connection_string(self) -> str:
        return os.getenv("APPLICATIONINSIGHTS_CONNECTION_STRING", "")

    # ── Logging ────────────────────────────────────────────────────────────

    @property
    def log_level(self) -> str:
        return os.getenv("LOG_LEVEL", "INFO").upper()


# Module-level singleton — import this everywhere
settings = Settings()


def configure_logging() -> logging.Logger:
    """
    Set up application-wide logging.
    Call once from main.py before running any pipeline.
    """
    level = getattr(logging, settings.log_level, logging.INFO)
    logging.basicConfig(
        level=level,
        format="%(asctime)s  %(levelname)-8s  %(name)s  %(message)s",
        datefmt="%Y-%m-%dT%H:%M:%S",
    )
    # Suppress noisy SDK debug logs unless we're at DEBUG ourselves
    if level > logging.DEBUG:
        logging.getLogger("httpx").setLevel(logging.WARNING)
        logging.getLogger("httpcore").setLevel(logging.WARNING)
        logging.getLogger("anthropic").setLevel(logging.WARNING)

    return logging.getLogger("pipeline_factory")
