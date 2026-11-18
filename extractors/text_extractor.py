
from pathlib import Path

from extractors.file_handler import FileHandler


class TXTExtractor:

    def __init__(self, file_path):

        self.file_path = Path(file_path)

        self.file_handler = FileHandler(file_path)

    def extract_text(self):

        # Validate file
        self.file_handler.validate_files()

        if self.file_handler.get_file_extension() != ".txt":
            raise ValueError("Only TXT files are supported.")

        try:

            # Read the complete text file
            with open(
                self.file_path,
                "r",
                encoding="utf-8-sig"
            ) as file:

                content = file.read()

            # Extract individual lines
            lines = [
                line.strip()
                for line in content.splitlines()
                if line.strip()
            ]

            # Extract paragraphs
            paragraphs = [
                paragraph.strip()
                for paragraph in content.split("\n\n")
                if paragraph.strip()
            ]

            # Count words
            words = content.split()

            return {

                "file_name": self.file_handler.get_file_name(),

                "total_characters": len(content),

                "total_words": len(words),

                "total_lines": len(lines),

                "total_paragraphs": len(paragraphs),

                "content": content,

                "lines": lines,

                "paragraphs": paragraphs

            }

        except UnicodeDecodeError as error:

            raise ValueError(
                f"Unable to decode text file: {error}"
            ) from error

        except OSError as error:

            raise RuntimeError(
                f"TXT extraction failed: {error}"
            ) from error
