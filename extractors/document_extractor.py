
from pathlib import Path

from extractors.file_handler import FileHandler


from extractors.file_handler import FileHandler
from extractors.pdf_extractor import PDFExtractor
from extractors.docx_extractor import DOCXExtractor
from extractors.excel_extractor import ExcelExtractor
from extractors.text_extractor import TXTExtractor
from extractors.image_extractor import ImageExtractor

from processing.text_cleaner import TextCleaner


class DocumentExtractor:

    # Map extensions to extractor classes
    EXTRACTOR_MAP = {
        ".pdf": PDFExtractor,
        ".docx": DOCXExtractor,
        ".xlsx": ExcelExtractor,
        ".xlsm": ExcelExtractor,
        ".txt": TXTExtractor,
        ".jpg": ImageExtractor,
        ".jpeg": ImageExtractor,
        ".png": ImageExtractor,
        ".tiff": ImageExtractor,
        ".bmp": ImageExtractor
    }

    @staticmethod
    def extract(file_path):

        file_handler = FileHandler(file_path)
        file_handler.validate_files()

        extension = file_handler.get_file_extension()

        extractor_class = DocumentExtractor.EXTRACTOR_MAP.get(extension)

        if extractor_class is None:
            raise ValueError(
                f"No extractor available for {extension}"
            )

        extractor = extractor_class(file_path)

        if extension in [".xlsx", ".xlsm"]:
            data = extractor.extract_data()
        else:
            data = extractor.extract_text()

        # Clean extracted data without modifying original data
        cleaned_data = DocumentExtractor.clean_nested_data(data)

        return {
            "file_name": file_handler.get_file_name(),
            "file_extension": extension,
            "document_type": extractor_class.__name__,
            "data": data,
            "cleaned_data": cleaned_data
        }

    @staticmethod
    def clean_nested_data(value):

        if isinstance(value, str):
            return TextCleaner(value).clean()["cleaned_text"]

        if isinstance(value, list):
            return [
                DocumentExtractor.clean_nested_data(item)
                for item in value
            ]

        if isinstance(value, dict):
            return {
                key: DocumentExtractor.clean_nested_data(item)
                for key, item in value.items()
            }

        return value

