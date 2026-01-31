import instructor
from openai import OpenAI

from app.db.session import settings
from app.schemas.ai import ProjectBreakdown


class AIService:
    def __init__(self):
        # Patch the OpenAI client with Instructor to support structured output
        self.client = instructor.from_openai(
            OpenAI(
                base_url=settings.OLLAMA_BASE_URL,
                api_key="ollama",
            ),
            mode=instructor.Mode.JSON,
        )

    def breakdown_feature(self, feature_description: str) -> ProjectBreakdown:
        """
        Sends the prompt to Ollama and enforces a JSON response matching ProjectBreakdown.
        """
        system_prompt = (
            "You are an experienced Agile Project Manager. "
            "Your goal is to break down a high-level feature request into small, actionable engineering tasks."
        )

        return self.client.chat.completions.create(
            model=settings.OLLAMA_MODEL,
            response_model=ProjectBreakdown,
            messages=[
                {"role": "system", "content": system_prompt},
                {
                    "role": "user",
                    "content": f"Break down this feature: {feature_description}",
                },
            ],
        )


ai_service = AIService()
