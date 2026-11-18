
import pymupdf

from extractors.pdf_extractor import PDFExtractor


# Create a sample PDF
pdf = pymupdf.open()

page = pdf.new_page()

page.insert_text(
    (72, 72),
    "DOCUSTRUCT PDF EXTRACTION TEST"
)

page.insert_text(
    (72, 110),
    "Name: John Smith"
)

page.insert_text(
    (72, 140),
    "Invoice Number: INV-101"
)

# Save the complete PDF document
pdf.save("sample.pdf")

# Close the document
pdf.close()


# Extract text from the sample PDF
extractor = PDFExtractor("sample.pdf")

result = extractor.extract_text()


# Display extracted information
print("PDF EXTRACTION SUCCESSFUL")

print("File:", result["file_name"])

print("Total pages:", result["total_pages"])

for page in result["pages"]:

    print("\nPage:", page["page_number"])

    print("Text:", page["text"])

    print("Characters:", page["character_count"])
