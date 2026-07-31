class TitleService:
    @staticmethod
    def generate_fallback_title(message: str) -> str:
        cleaned_message = " ".join(message.strip().split())

        if not cleaned_message:
            return "New Chat"

        words = cleaned_message.split()
        title = " ".join(words[:5])

        return title[:255]