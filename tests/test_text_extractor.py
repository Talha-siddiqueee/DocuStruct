
from extractors.text_extractor import TXTExtractor


# Create sample TXT file
sample_content = """
DOCUSTRUCT DOCUMENT

Name: John Smith
Age: 25
Email: john@example.com

Skills:
Python
Machine Learning
Data Analysis

Experience: 2 years
"""

with open("sample.txt", "w", encoding="utf-8") as file:
    file.write(sample_content)


# Initialize extractor
extractor = TXTExtractor("sample.txt")

# Extract information
result = extractor.extract_text()


# Display results
print("TXT EXTRACTION SUCCESSFUL")

print("File:", result["file_name"])

print("Characters:", result["total_characters"])

print("Words:", result["total_words"])

print("Lines:", result["total_lines"])

print("Paragraphs:", result["total_paragraphs"])


print("\nEXTRACTED LINES:")

for line in result["lines"]:
    print(line)


print("\nEXTRACTED PARAGRAPHS:")

for paragraph in result["paragraphs"]:
    print(paragraph)
