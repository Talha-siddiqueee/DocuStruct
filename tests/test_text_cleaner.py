
from processing.text_cleaner import TextCleaner


sample_text = """
   INVOICE     NUMBER: INV-101


Name:    John Smith


Total Amount:     2000
"""

cleaner = TextCleaner(sample_text)

result = cleaner.clean()

print("RAW TEXT:")
print(result["raw_text"])

print("\nCLEANED TEXT:")
print(result["cleaned_text"])

print("\nSTATISTICS:")
print("Original characters:", result["original_characters"])
print("Cleaned characters:", result["cleaned_characters"])
