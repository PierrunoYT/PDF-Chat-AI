import os
import re
import string
from PyPDF2 import PdfReader
from PyPDF2.errors import PdfReadError
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize

# This function is now redundant and can be removed

def clean_and_preprocess_text(text):
    """
    Clean and preprocess the extracted text.
    
    :param text: Input text string
    :return: Cleaned and preprocessed text string
    """
    # Convert to lowercase
    text = text.lower()
    
    # Remove special characters and digits
    text = re.sub(r'[^a-zA-Z\s]', '', text)
    
    # Tokenize the text
    tokens = word_tokenize(text)
    
    # Remove stopwords
    stop_words = set(stopwords.words('english'))
    tokens = [token for token in tokens if token not in stop_words]
    
    # Join the tokens back into a string
    cleaned_text = ' '.join(tokens)
    
    return cleaned_text

def process_multiple_pdfs(directory, save_to_file=False, keyword_filter=None, max_pages=None, clean_text=False):
    """
    Process multiple PDF files in a directory.
    
    :param directory: Path to the directory containing PDF files
    :param save_to_file: If True, save extracted text to individual text files
    :param keyword_filter: If provided, only process PDFs with this keyword in the filename
    :param max_pages: If provided, limit the number of pages processed per PDF
    :return: Dictionary with PDF filenames as keys and extracted text as values
    """
    results = {}
    pdf_files = [f for f in os.listdir(directory) if f.endswith(".pdf")]
    if keyword_filter:
        pdf_files = [f for f in pdf_files if keyword_filter.lower() in f.lower()]
    total_files = len(pdf_files)
    
    successful_extractions = 0
    failed_extractions = 0
    
    for i, filename in enumerate(pdf_files, 1):
        file_path = os.path.join(directory, filename)
        print(f"Processing {i}/{total_files}: {filename}")
        
        text = extract_text_from_pdf(file_path, max_pages, clean_text)
        if text:
            results[filename] = text
            successful_extractions += 1
            if save_to_file:
                output_path = os.path.join(directory, f"{os.path.splitext(filename)[0]}.txt")
                with open(output_path, 'w', encoding='utf-8') as out_file:
                    out_file.write(text)
        else:
            failed_extractions += 1
    
    print(f"\nProcessing Summary:")
    print(f"Total PDFs processed: {total_files}")
    print(f"Successful extractions: {successful_extractions}")
    print(f"Failed extractions: {failed_extractions}")
    
    return results

def extract_text_from_pdf(pdf_path, max_pages=None, clean_text=False):
    """
    Extract text from a single PDF file.
    
    :param pdf_path: Path to the PDF file
    :param max_pages: Maximum number of pages to process (None for all pages)
    :return: Extracted text as a string, or None if an error occurs
    """
    try:
        with open(pdf_path, 'rb') as file:
            reader = PdfReader(file)
            text = ""
            pages_to_process = min(len(reader.pages), max_pages) if max_pages else len(reader.pages)
            for i in range(pages_to_process):
                text += reader.pages[i].extract_text() + "\n"
        return text
    except (IOError, PdfReadError) as e:
        print(f"Error processing {pdf_path}: {str(e)}")
        return None

# Example usage:
if __name__ == "__main__":
    # Extract text from a single PDF
    single_pdf_path = "path/to/your/pdf/file.pdf"
    single_result = extract_text_from_pdf(single_pdf_path, max_pages=5)
    if single_result:
        print(f"Extracted text from {single_pdf_path} (first 5 pages):")
        print(single_result[:500])  # Print first 500 characters
        print("\n" + "="*50 + "\n")

    # Process multiple PDFs in a directory
    pdf_directory = "path/to/your/pdf/directory"
    results = process_multiple_pdfs(pdf_directory, save_to_file=True, keyword_filter="report", max_pages=10)
    print(f"\nProcessed {len(results)} PDF files successfully.")
    for filename, text in results.items():
        print(f"Extracted text from {filename} (first 10 pages):")
        print(text[:500])  # Print first 500 characters of each PDF
        print("\n" + "="*50 + "\n")
