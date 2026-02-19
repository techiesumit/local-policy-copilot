"""Provider interface for model backends.

This module defines the abstract `ModelProvider` class that all concrete
providers must implement. Implementations live in `app.providers` and
are instantiated by `app.main.get_provider()`.
"""

from abc import ABC, abstractmethod


class ModelProvider(ABC):
    """Abstract base class for model providers.

    Concrete subclasses must implement `chat()` to accept a user-provided
    string and return the model's textual response.
    """

    @abstractmethod
    def chat(self, user_text: str) -> str:
        """Send `user_text` to the model and return a text response.

        The body here is intentionally empty because subclasses are
        required to override this method. The `pass` serves only as a
        syntactic placeholder.

        Example:

        >>> from app.providers.base import ModelProvider
        >>> class EchoProvider(ModelProvider):
        ...     def chat(self, user_text: str) -> str:
        ...         return f"echo: {user_text}"

        >>> EchoProvider().chat("hi")
        'echo: hi'

        """
        pass
