"""Lightweight mock model provider used for local development and tests.

`MockProvider` implements the `ModelProvider` interface and returns a
deterministic, human-readable response useful for development when an
external model service is not configured.
"""

from app.providers.base import ModelProvider


class MockProvider(ModelProvider):
    """A minimal provider that echoes and annotates input text.

    Useful for fast local feedback and unit tests.
    """

    def chat(self, user_text: str) -> str:
        """Return a predictable mock response for `user_text`."""

        # Keep responses short and deterministic to simplify tests and
        # demos. This can be replaced with canned scenarios if needed.
        return f"[mock response] received: {user_text}"