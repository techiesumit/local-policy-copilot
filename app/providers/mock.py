from .base import ModelProvider

class MockProvider(ModelProvider):
    def chat(self, user_text: str) -> str:
        return f"[MOCK] {user_text}"
