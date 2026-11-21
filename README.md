# DocuStruct 📄

### Intelligent Document Data Extraction using Python

DocuStruct is a Python-based document extraction system designed to extract, process, and clean information from multiple document formats. It combines specialized extraction techniques with text processing and OCR to turn unstructured document content into structured data.

## ✨ Features

- **Multi-format Support:** Extract data from PDF, DOCX, XLSX, XLSM, TXT, and images.
- **PDF Extraction:** Extract text and page-level information using PyMuPDF.
- **Word Extraction:** Extract paragraphs and tables from DOCX files.
- **Excel Extraction:** Read spreadsheet data using OpenPyXL.
- **Image OCR:** Extract text from images using Tesseract OCR and OpenCV.
- **Text Processing:** Clean and normalize extracted text.
- **Information Extraction:** Process text to identify useful information.
- **Interactive UI:** Upload documents and view extraction results through Streamlit.
- **JSON Output:** View and download structured extraction results.

## 🛠️ Tech Stack

- Python
- Streamlit
- PyMuPDF
- python-docx
- OpenPyXL
- Pandas
- OpenCV
- Tesseract OCR
- Pytesseract

## 📁 Project Structure

```text
DocuStruct/
│
├── app.py
├── requirements.txt
│
├── extractors/
│   ├── document_extractor.py
│   ├── file_handler.py
│   ├── pdf_extractor.py
│   ├── docx_extractor.py
│   ├── excel_extractor.py
│   ├── image_extractor.py
│   └── text_extractor.py
│
├── processing/
│   ├── information_extractor.py
│   └── text_cleaner.py
│
├── tests/
│
├── uploads/
├── output/
└── README.md
```

## ⚙️ Installation

### 1. Clone the repository

```bash
git clone https://github.com/Talha-siddiqueee/DocuStruct.git
```

### 2. Navigate to the project directory

```bash
cd DocuStruct
```

### 3. Create a virtual environment

```bash
python -m venv venv
```

### 4. Activate the virtual environment

Windows PowerShell:

```powershell
.\venv\Scripts\Activate.ps1
```

### 5. Install dependencies

```bash
pip install -r requirements.txt
```

### 6. Install Tesseract OCR

Image text extraction requires Tesseract OCR to be installed separately.

Download it from:

https://github.com/UB-Mannheim/tesseract/wiki

Make sure Tesseract is available in your system PATH.

### 7. Run the application

```bash
python -m streamlit run app.py
```

The application will open in your browser.

## 🧪 Testing

Run the project tests using:

```bash
python -m pytest
```

## 🚀 Future Improvements

- Advanced document layout detection
- Improved OCR accuracy
- Table extraction from scanned documents
- AI-powered information extraction
- Support for additional document formats
- Cloud deployment and API integration

## 👨‍💻 Author

**Talha Siddique**

GitHub: https://github.com/Talha-siddiqueee

---

⭐ If you find this project interesting, consider giving it a star!
