
import re


class InformationExtractor:

    def __init__(self, text):
        self.text = text

    def extract_emails(self):

        pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b'

        emails = re.findall(pattern, self.text)

        return list(set(emails))

    def extract_phone_numbers(self):

        pattern = r'(?<!\d)(?:\+91[-\s]?)?[6-9]\d{9}(?!\d)'

        phone_numbers = re.findall(pattern, self.text)

        return list(set(phone_numbers))
    def extract_dates(self):

        patterns = [
                r'\b\d{2}/\d{2}/\d{4}\b',
                r'\b\d{2}-\d{2}-\d{4}\b',
                r'\b\d{4}-\d{2}-\d{2}\b',
                r'\b\d{1,2}\s+'
                r'(?:January|February|March|April|May|June|July|August|September|October|November|December)'
                r'\s+\d{4}\b',
                r'\b\d{1,2}\s+'
                r'(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)'
                r'\s+\d{4}\b'
            ]
        dates = []

        for pattern in patterns:
            matches = re.findall(
                pattern,
                self.text,
                flags=re.IGNORECASE
            )
            dates.extend(matches)

        return list(set(dates))
