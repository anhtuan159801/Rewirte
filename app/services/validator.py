from app.schemas.llm import RewriteResponse
from app.utils.text import similarity


class ValidationError(Exception):
    pass


class Validator:
    def validate(self, original_text: str, result: RewriteResponse) -> float:
        if not result.rewritten_text.strip():
            raise ValidationError("rewritten_text is empty")
        if len(result.rewritten_text.strip()) < max(10, len(original_text.strip()) // 5):
            raise ValidationError("rewritten_text is unexpectedly short")

        score = similarity(original_text, result.rewritten_text)
        if score < 0.35:
            raise ValidationError("meaning drift is too high")
        return round(score, 3)


validator = Validator()
