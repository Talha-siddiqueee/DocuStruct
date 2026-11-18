
from pathlib import Path

import cv2
import pytesseract

from pytesseract import Output

from extractors.file_handler import FileHandler


class ImageExtractor:

    def __init__(self, file_path):

        self.file_path = Path(file_path)

        self.file_handler = FileHandler(file_path)

    def extract_text(self):

        # Validate input file
        self.file_handler.validate_files()

        if self.file_handler.get_file_extension() not in {
            ".jpg", ".jpeg", ".png", ".tiff", ".bmp"
        }:
            raise ValueError("Unsupported image format.")

        try:

            # Read image using OpenCV
            image = cv2.imread(str(self.file_path))

            if image is None:
                raise ValueError("Unable to read image.")

            # Convert image to grayscale
            gray = cv2.cvtColor(
                image,
                cv2.COLOR_BGR2GRAY
            )

            # Apply Otsu thresholding
            _, processed_image = cv2.threshold(
                gray,
                0,
                255,
                cv2.THRESH_BINARY + cv2.THRESH_OTSU
            )

            # Extract text using Tesseract
            extracted_text = pytesseract.image_to_string(
                processed_image,
                lang="eng"
            )

            # Get word-level OCR information
            ocr_data = pytesseract.image_to_data(
                processed_image,
                output_type=Output.DICT,
                lang="eng"
            )
            
            recognized_words = []
            for i, word in enumerate(ocr_data["text"]):
                word = word.strip()
                confidence = float(ocr_data["conf"][i])
                if word and confidence >= 0:
                    recognized_words.append({
                        "word": word,
                        "confidence": round(confidence, 2)
                        })
            

            # Collect valid confidence scores
            confidence_scores = []

            for confidence in ocr_data["conf"]:

                score = float(confidence)

                if score >= 0:
                    confidence_scores.append(score)

            # Calculate average confidence
            average_confidence = (
                sum(confidence_scores) / len(confidence_scores)
                if confidence_scores else 0
            )

            return {

                "file_name": self.file_handler.get_file_name(),

                "extracted_text": extracted_text.strip(),

                "total_characters": len(extracted_text.strip()),

                "average_confidence": round(
                    average_confidence, 2),
                "recognized_words": recognized_words


            }

        except Exception as error:

            raise RuntimeError(
                f"Image extraction failed: {error}"
            ) from error
