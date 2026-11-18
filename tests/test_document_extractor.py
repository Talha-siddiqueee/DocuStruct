
from pathlib import Path
from extractors.document_extractor import DocumentExtractor

# Create a temporary sample text file
sample_path = Path("sample_dirty.txt")

sample_path.write_text(
    "   INVOICE     NUMBER: INV-101\n\n\n"
    "Name:    John Smith\n\n"
    "Total Amount:     2000",
    encoding="utf-8"
)

try:
    result = DocumentExtractor.extract(sample_path)

    print("DOCUMENT EXTRACTION SUCCESSFUL")

    print("\nRAW DATA:")
    print(result["data"]["content"])

    print("\nCLEANED DATA:")
    print(result["cleaned_data"]["content"])

    print("\nFILE NAME:")
    print(result["file_name"])

finally:
    sample_path.unlink(missing_ok=True)
