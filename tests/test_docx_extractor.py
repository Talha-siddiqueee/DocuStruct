
from docx import Document

from extractors.docx_extractor import DOCXExtractor


# Create sample DOCX document
document = Document()

document.add_heading("Employee Information", level=1)

document.add_paragraph("This is a DocuStruct extraction test.")

document.add_paragraph("Employee: John Smith")

# Create a table
table = document.add_table(rows=1, cols=3)

table.style = "Table Grid"

headers = ["Name", "Age", "Department"]

for index, header in enumerate(headers):
    table.rows[0].cells[index].text = header

row = table.add_row().cells

row[0].text = "John Smith"
row[1].text = "25"
row[2].text = "Engineering"

# Save document
document.save("sample.docx")


# Extract document
extractor = DOCXExtractor("sample.docx")

result = extractor.extract_text()


# Display results
print("DOCX EXTRACTION SUCCESSFUL")

print("File:", result["file_name"])

print("Total paragraphs:", result["total_paragraphs"])

print("Total tables:", result["total_tables"])

print("\nPARAGRAPHS:")

for paragraph in result["paragraphs"]:
    print(paragraph)

print("\nTABLES:")

for table in result["tables"]:
    for row in table["rows"]:
        print(row)
