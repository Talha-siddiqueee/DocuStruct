
from docx import Document
from pathlib import Path

from extractors.file_handler import FileHandler


class DOCXExtractor:

    def __init__(self, file_path):

        self.file_path = Path(file_path)

        self.file_handler = FileHandler(file_path)

    def extract_text(self):

        self.file_handler.validate_files()

        if self.file_handler.get_file_extension() != ".docx":
            raise ValueError("Only DOCX files are supported.")

        try:

            document = Document(self.file_path)

            paragraphs = []

            for paragraph in document.paragraphs:

                text = paragraph.text.strip()

                if text:
                    paragraphs.append({
                        "text": text,
                        "style": paragraph.style.name
                    })

            tables = []

            for table_index, table in enumerate(document.tables, start=1):

                table_data = []

                for row in table.rows:

                    row_data = []

                    for cell in row.cells:
                        row_data.append(cell.text.strip())

                    table_data.append(row_data)

                tables.append({
                    "table_number": table_index,
                    "rows": table_data
                })

            return {
                "file_name": self.file_handler.get_file_name(),
                "total_paragraphs": len(paragraphs),
                "total_tables": len(tables),
                "paragraphs": paragraphs,
                "tables": tables
            }

        except Exception as error:

            raise RuntimeError(
                f"DOCX extraction failed: {error}"
            ) from error
