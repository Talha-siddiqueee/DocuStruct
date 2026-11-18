
from openpyxl import load_workbook
from pathlib import Path

from extractors.file_handler import FileHandler


class ExcelExtractor:

    def __init__(self, file_path):

        self.file_path = Path(file_path)

        self.file_handler = FileHandler(file_path)

    def extract_data(self):

        # Validate file
        self.file_handler.validate_files()

        if self.file_handler.get_file_extension() not in [".xlsx", ".xlsm"]:
            raise ValueError("Only XLSX and XLSM files are supported.")

        workbook = None

        try:

            # Open Excel workbook
            workbook = load_workbook(
                filename=self.file_path,
                read_only=True,
                data_only=True
            )

            extracted_sheets = []

            # Iterate through worksheets
            for sheet in workbook.worksheets:

                sheet_data = []

                # Iterate through rows
                for row in sheet.iter_rows(values_only=True):

                    # Convert row tuple into list
                    row_data = list(row)

                    # Skip completely empty rows
                    if any(value is not None for value in row_data):

                        sheet_data.append(row_data)

                extracted_sheets.append({

                    "sheet_name": sheet.title,

                    "total_rows": len(sheet_data),

                    "data": sheet_data

                })

            return {

                "file_name": self.file_handler.get_file_name(),

                "total_sheets": len(extracted_sheets),

                "sheets": extracted_sheets

            }

        except Exception as error:

            raise RuntimeError(
                f"Excel extraction failed: {error}"
            ) from error

        finally:

            if workbook is not None:
                workbook.close()
