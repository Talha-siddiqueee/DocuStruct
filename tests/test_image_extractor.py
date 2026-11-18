
from PIL import Image, ImageDraw

from extractors.image_extractor import ImageExtractor


# Create a blank white image
image = Image.new(
    "RGB",
    (1000, 500),
    "white"
)

draw = ImageDraw.Draw(image)

# Add text to the image
draw.text(
    (50, 50),
    "DOCUSTRUCT OCR TEST",
    fill="black"
)

draw.text(
    (50, 120),
    "Name: John Smith",
    fill="black"
)

draw.text(
    (50, 180),
    "Invoice Number: INV-101",
    fill="black"
)

draw.text(
    (50, 240),
    "Total Amount: 52000",
    fill="black"
)

# Save sample image
image.save("sample.png")


# Initialize extractor
extractor = ImageExtractor("sample.png")

# Extract information
result = extractor.extract_text()


# Display results
print("OCR EXTRACTION SUCCESSFUL")

print("File:", result["file_name"])

print("Extracted text:")
print(result["extracted_text"])

print(
    "Total characters:",
    result["total_characters"]
)

print(
    "Average confidence:",
    result["average_confidence"]
)
