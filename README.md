# PDF Text Extractor and Processor

This project provides a set of tools for extracting text from PDF files, processing the extracted text, and storing the results in a SQLite database.

## Features

- Extract text from single or multiple PDF files
- Clean and preprocess extracted text (optional)
- Filter PDFs by keyword in filename
- Limit the number of pages processed per PDF
- Save extracted text to individual text files (optional)
- Store extracted text and metadata in a SQLite database

## Requirements

- Python 3.6+
- PyPDF2
- NLTK

## Installation

1. Clone this repository:
   ```
   git clone https://github.com/yourusername/pdf-text-extractor.git
   cd pdf-text-extractor
   ```

2. Install the required packages:
   ```
   pip install PyPDF2 nltk
   ```

3. Download the necessary NLTK data:
   ```python
   import nltk
   nltk.download('punkt')
   nltk.download('stopwords')
   ```

## Usage

### Processing multiple PDFs

```python
from pdf_processor import process_multiple_pdfs

pdf_directory = "path/to/your/pdf/directory"
results = process_multiple_pdfs(
    directory=pdf_directory,
    save_to_file=True,
    keyword_filter="report",
    max_pages=10,
    clean_text=True
)
```

### Extracting text from a single PDF

```python
from pdf_processor import extract_text_from_pdf

single_pdf_path = "path/to/your/pdf/file.pdf"
text, page_count = extract_text_from_pdf(single_pdf_path, max_pages=5, clean_text=True)
```

### Working with the database

```python
from database_manager import DatabaseManager

db_manager = DatabaseManager()

# Retrieve a PDF extract
filename = "example.pdf"
pdf_extract = db_manager.get_pdf_extract(filename)

if pdf_extract:
    print(f"Extraction date: {pdf_extract[4]}")
    print(f"Page count: {pdf_extract[3]}")
    print(f"Cleaned: {'Yes' if pdf_extract[5] else 'No'}")
    print(f"Text preview: {pdf_extract[2][:500]}")  # Print first 500 characters

db_manager.close()
```

## File Descriptions

- `pdf_processor.py`: Contains functions for extracting text from PDFs and processing multiple PDFs.
- `database_manager.py`: Manages the SQLite database for storing extracted text and metadata.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
