import os
from PyPDF2 import PdfReader
from PyPDF2.errors import PdfReadError

def extract_text_from_pdf(pdf_path):
    """
    Extract text from a single PDF file.
    
    :param pdf_path: Path to the PDF file
    :return: Extracted text as a string, or None if an error occurs
    """
    try:
        with open(pdf_path, 'rb') as file:
            reader = PdfReader(file)
            text = ""
            for page in reader.pages:
                text += page.extract_text() + "\n"
        return text
    except (IOError, PdfReadError) as e:
        print(f"Error processing {pdf_path}: {str(e)}")
        return None

def process_multiple_pdfs(directory, save_to_file=False):
    """
    Process multiple PDF files in a directory.
    
    :param directory: Path to the directory containing PDF files
    :param save_to_file: If True, save extracted text to individual text files
    :return: Dictionary with PDF filenames as keys and extracted text as values
    """
    results = {}
    pdf_files = [f for f in os.listdir(directory) if f.endswith(".pdf")]
    total_files = len(pdf_files)
    
    for i, filename in enumerate(pdf_files, 1):
        file_path = os.path.join(directory, filename)
        print(f"Processing {i}/{total_files}: {filename}")
        
        text = extract_text_from_pdf(file_path)
        if text:
            results[filename] = text
            if save_to_file:
                output_path = os.path.join(directory, f"{os.path.splitext(filename)[0]}.txt")
                with open(output_path, 'w', encoding='utf-8') as out_file:
                    out_file.write(text)
    
    return results

# Example usage:
if __name__ == "__main__":
    # Extract text from a single PDF
    single_pdf_path = "path/to/your/pdf/file.pdf"
    single_result = extract_text_from_pdf(single_pdf_path)
    if single_result:
        print(f"Extracted text from {single_pdf_path}:")
        print(single_result[:500])  # Print first 500 characters
        print("\n" + "="*50 + "\n")

    # Process multiple PDFs in a directory
    pdf_directory = "path/to/your/pdf/directory"
    results = process_multiple_pdfs(pdf_directory, save_to_file=True)
    print(f"\nProcessed {len(results)} PDF files successfully.")
    for filename, text in results.items():
        print(f"Extracted text from {filename}:")
        print(text[:500])  # Print first 500 characters of each PDF
        print("\n" + "="*50 + "\n")
