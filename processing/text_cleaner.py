
import re
import unicodedata


class TextCleaner:

    def __init__(self, text):
        self.raw_text = text

    def normalize_unicode(self):
        """Normalize Unicode characters."""
        return unicodedata.normalize("NFKC", self.raw_text)

    def normalize_line_endings(self, text):
        """Convert different line endings into \n."""
        return text.replace("\r\n", "\n").replace("\r", "\n")

    def remove_extra_spaces(self, text):
        """Remove unnecessary spaces and tabs."""
        lines = text.split("\n")

        cleaned_lines = [
            re.sub(r"[ \t]+", " ", line).strip()
            for line in lines
        ]

        return "\n".join(cleaned_lines)

    def remove_extra_blank_lines(self, text):
        """Keep at most one blank line between paragraphs."""
        return re.sub(r"\n{3,}", "\n\n", text).strip()

    def clean(self):
        """Run the complete cleaning pipeline."""

        text = self.normalize_unicode()

        text = self.normalize_line_endings(text)

        text = self.remove_extra_spaces(text)

        text = self.remove_extra_blank_lines(text)

        return {
            "raw_text": self.raw_text,
            "cleaned_text": text,
            "original_characters": len(self.raw_text),
            "cleaned_characters": len(text)
        }
