import pymupdf
from pathlib import Path

from extractors.file_handler import FileHandler

class PDFExtractor:
    def __init__(self,file_path):
        self.file_path = Path(file_path)
        self.file_handler = FileHandler(file_path)
    def extract_text(self):
        #validate the file
        self.file_handler.validate_files()
        if self.file_handler.get_file_extension()!= ".pdf":
            raise ValueError("Only PDF files are supported.")
        extracted_pages = []
        try:
            #open pdf doc
            document = pymupdf.open(self.file_path)
            #Extract text page by page
            for page_number,page in enumerate(document,start = 1):
                text = page.get_text("text")

                extracted_pages.append({
                    "page_number":page_number,
                    "text": text.strip(),
                    "character_count": len(text.strip())
                })
            document.close()
            return {
                "file_name": self.file_handler.get_file_name(),
                "total_pages": len(extracted_pages),
                "pages": extracted_pages
            }

        except Exception as error:

            raise RuntimeError(
                f"PDF extraction failed: {error}"
            ) from error



