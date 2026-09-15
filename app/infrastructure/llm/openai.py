"""OpenAI-compatible LLM provider."""

from langchain_openai import ChatOpenAI

from app.application.rag.service import RAGLLMProvider
from app.infrastructure.config.settings import Settings


class OpenAILLMProvider(RAGLLMProvider):
    """Generate grounded answers through an OpenAI-compatible API."""

    def __init__(self, settings: Settings) -> None:
        api_key = settings.openai_api_key.get_secret_value().strip()

        if not api_key:
            raise ValueError("OPENAI_API_KEY is required for RAG.")

        self._model = ChatOpenAI(
            model=settings.chat_model,
            api_key=api_key,
            base_url=settings.openai_base_url,
            temperature=0,
        )

    def generate(self, query: str, context: str) -> str:
        """Generate a grounded answer from the supplied context."""
        response = self._model.invoke(
            [
                (
                    "system",
                    (
                        "Ты — корпоративный AI-ассистент EgoTech Solutions. "
                        "Отвечай только на основе предоставленного контекста. "
                        "Не используй внешние знания и не выдумывай факты. "
                        "Если контекст не содержит достаточно информации для "
                        "достоверного ответа, верни строго этот текст без кавычек: "
                        "В базе знаний не найдено достаточно информации "
                        "для достоверного ответа на этот вопрос. "
                        "Отвечай на русском языке."
                    ),
                ),
                (
                    "human",
                    f"Вопрос:\n{query}\n\nКонтекст:\n{context}",
                ),
            ]
        )

        return str(response.content)
