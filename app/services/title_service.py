class TitleService:
    """Create concise display titles for chat conversations."""

    @staticmethod
    def generate_fallback_title(message: str) -> str:
        """Derive a normalized fallback title from the first five message words."""

        cleaned_message = " ".join(message.strip().split())

        if not cleaned_message:
            return "New Chat"

        words = cleaned_message.split()
        title = " ".join(words[:5])

        return title[:255]
