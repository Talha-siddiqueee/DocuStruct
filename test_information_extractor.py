
from processing.information_extractor import InformationExtractor

sample_text = """
Invoice Date: 18/11/2026

Due Date: 25-11-2026

Registration Date: 2026-11-18

Joining Date: 18 November 2026

Birth Date: 5 Jan 2005
"""

extractor = InformationExtractor(sample_text)

print("EXTRACTED DATES:")

for date in extractor.extract_dates():
    print(date)


