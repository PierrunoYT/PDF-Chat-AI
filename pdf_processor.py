import os
from PyPDF2 import PdfReader

def extract_text_from_pdf(pdf_path):
    """
    Extract text from a single PDF file.
    
    :param pdf_path: Path to the PDF file
    :return: Extracted text as a string
    """
    with open(pdf_path, 'rb') as file:
        reader = PdfReader(file)
        text = ""
        for page in reader.pages:
            text += page.extract_text() + "\n"
    return text

def process_multiple_pdfs(directory):
    """
    Process multiple PDF files in a directory.
    
    :param directory: Path to the directory containing PDF files
    :return: Dictionary with PDF filenames as keys and extracted text as values
    """
    results = {}
    for filename in os.listdir(directory):
        if filename.endswith(".pdf"):
            file_path = os.path.join(directory, filename)
            results[filename] = extract_text_from_pdf(file_path)
    return results

# Example usage:
if __name__ == "__main__":
    # Extract text from a single PDF
    single_pdf_path = "path/to/your/pdf/file.pdf"
    print(extract_text_from_pdf(single_pdf_path))

    # Process multiple PDFs in a directory
    pdf_directory = "path/to/your/pdf/directory"
    results = process_multiple_pdfs(pdf_directory)
    for filename, text in results.items():
        print(f"Extracted text from {filename}:")
        print(text[:500])  # Print first 500 characters of each PDF
        print("\n" + "="*50 + "\n")
