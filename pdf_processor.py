import os
import re
import string
from PyPDF2 import PdfReader
from PyPDF2.errors import PdfReadError
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from database_manager import DatabaseManager
from embedding_model import EmbeddingModel
from text_chunker import TextChunker
from faiss_manager import FAISSManager
import numpy as np

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

def process_multiple_pdfs(directory, save_to_file=False, keyword_filter=None, max_pages=None, clean_text=False, chunk_size=1000, chunk_overlap=200, use_faiss=True, db_manager=None, embedding_model=None, faiss_manager=None):
    """
    Process multiple PDF files in a directory, store results in a database, and generate embeddings for text chunks.
    
    :param directory: Path to the directory containing PDF files
    :param save_to_file: If True, save extracted text to individual text files
    :param keyword_filter: If provided, only process PDFs with this keyword in the filename
    :param max_pages: If provided, limit the number of pages processed per PDF
    :param clean_text: If True, clean and preprocess the extracted text
    :param chunk_size: Size of text chunks for embedding
    :param chunk_overlap: Overlap between text chunks
    :param use_faiss: If True, use FAISS for similarity search
    :param db_manager: DatabaseManager instance
    :param embedding_model: EmbeddingModel instance
    :param faiss_manager: FAISSManager instance
    :return: Dictionary with PDF filenames as keys and lists of tuples (chunk_text, chunk_embedding) as values
    """
    results = {}
    pdf_files = [f for f in os.listdir(directory) if f.endswith(".pdf")]
    if keyword_filter:
        pdf_files = [f for f in pdf_files if keyword_filter.lower() in f.lower()]
    total_files = len(pdf_files)
    
    successful_extractions = 0
    failed_extractions = 0
    
    if db_manager is None:
        db_manager = DatabaseManager()
    if embedding_model is None:
        embedding_model = EmbeddingModel()
    text_chunker = TextChunker(chunk_size, chunk_overlap)

    if use_faiss and faiss_manager is None:
        faiss_manager = FAISSManager(embedding_model.get_embedding_dimension())
        db_manager.set_faiss_manager(faiss_manager)
    
    for i, filename in enumerate(pdf_files, 1):
        file_path = os.path.join(directory, filename)
        print(f"Processing {i}/{total_files}: {filename}")
        
        text, page_count = extract_text_from_pdf(file_path, max_pages, clean_text)
        if text:
            chunks = text_chunker.chunk_text(text)
            chunk_embeddings = embedding_model.get_embeddings(chunks)
            results[filename] = list(zip(chunks, chunk_embeddings))
            successful_extractions += 1
            if save_to_file:
                output_path = os.path.join(directory, f"{os.path.splitext(filename)[0]}.txt")
                with open(output_path, 'w', encoding='utf-8') as out_file:
                    out_file.write(text)
            
            # Store in database
            db_manager.insert_pdf_extract(filename, text, page_count, clean_text, [emb.tolist() for emb in chunk_embeddings])
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
    :param clean_text: If True, clean and preprocess the extracted text
    :return: Tuple of (extracted text as a string, page count), or (None, None) if an error occurs
    """
    try:
        with open(pdf_path, 'rb') as file:
            reader = PdfReader(file)
            text = ""
            total_pages = len(reader.pages)
            pages_to_process = min(total_pages, max_pages) if max_pages else total_pages
            for i in range(pages_to_process):
                text += reader.pages[i].extract_text() + "\n"
        
        if clean_text:
            text = clean_and_preprocess_text(text)
        
        return text, pages_to_process
    except (IOError, PdfReadError) as e:
        print(f"Error processing {pdf_path}: {str(e)}")
        return None, None

# Example usage:
if __name__ == "__main__":
    # Extract text from a single PDF
    single_pdf_path = "path/to/your/pdf/file.pdf"
    single_result, page_count = extract_text_from_pdf(single_pdf_path, max_pages=5)
    if single_result:
        print(f"Extracted text from {single_pdf_path} ({page_count} pages):")
        print(single_result[:500])  # Print first 500 characters
        print("\n" + "="*50 + "\n")

    # Process multiple PDFs in a directory
    pdf_directory = "path/to/your/pdf/directory"
    results = process_multiple_pdfs(pdf_directory, save_to_file=True, keyword_filter="report", max_pages=10, clean_text=True)
    print(f"\nProcessed {len(results)} PDF files successfully.")
    
    # Demonstrate database retrieval
    db_manager = DatabaseManager()
    for filename in results.keys():
        db_result = db_manager.get_pdf_extract(filename)
        if db_result:
            print(f"Retrieved from database - {filename}:")
            print(f"Extraction date: {db_result[4]}")
            print(f"Page count: {db_result[3]}")
            print(f"Cleaned: {'Yes' if db_result[5] else 'No'}")
            print(f"Text preview: {db_result[2][:500]}")  # Print first 500 characters
            print("\n" + "="*50 + "\n")
    db_manager.close()
