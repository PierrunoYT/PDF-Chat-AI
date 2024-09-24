import os
import re
import io
import logging
from PyPDF2 import PdfReader
from PyPDF2.errors import PdfReadError
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from database_manager import DatabaseManager
from embedding_model import EmbeddingModel
from text_chunker import TextChunker
from faiss_manager import FAISSManager
import time

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def clean_and_preprocess_text(text):
    """
    Clean and preprocess the extracted text.
    
    :param text: Input text string
    :return: Cleaned and preprocessed text string
    """
    text = text.lower()
    text = re.sub(r'[^a-zA-Z\s]', '', text)
    tokens = word_tokenize(text)
    stop_words = set(stopwords.words('english'))
    tokens = [token for token in tokens if token not in stop_words]
    return ' '.join(tokens)

def process_multiple_pdfs(pdf_files, save_to_file=False, keyword_filter=None, max_pages=None, clean_text=False, chunk_size=1000, chunk_overlap=200, use_faiss=True, db_manager=None, embedding_model=None, faiss_manager=None):
    """
    Process multiple PDF files, store results in a database, and generate embeddings for text chunks.
    """
    results = {}
    if keyword_filter:
        pdf_files = [f for f in pdf_files if isinstance(f, str) and keyword_filter.lower() in os.path.basename(f).lower()]
    total_files = len(pdf_files)
    
    successful_extractions = 0
    failed_extractions = 0
    
    db_manager = db_manager or DatabaseManager()
    embedding_model = embedding_model or EmbeddingModel()
    text_chunker = TextChunker(chunk_size, chunk_overlap)

    if use_faiss and faiss_manager is None:
        faiss_manager = FAISSManager(embedding_model.get_embedding_dimension())
        db_manager.set_faiss_manager(faiss_manager)
    
    for i, file_obj in enumerate(pdf_files, 1):
        if isinstance(file_obj, str):
            filename = os.path.basename(file_obj)
            file_path = file_obj
        else:
            filename = f"uploaded_file_{i}.pdf"
            file_path = file_obj
        logging.info(f"Processing {i}/{total_files}: {filename}")
        
        text, page_count = extract_text_from_pdf(file_path, max_pages, clean_text)
        if text:
            chunks = text_chunker.chunk_text(text)
            chunk_embeddings = embedding_model.get_embeddings(chunks)
            results[filename] = list(zip(chunks, chunk_embeddings))
            successful_extractions += 1
            if save_to_file:
                output_path = f"{os.path.splitext(file_path)[0]}.txt"
                with open(output_path, 'w', encoding='utf-8') as out_file:
                    out_file.write(text)
            
            # Ensure that the number of chunks matches the number of embeddings
            if len(chunks) == len(chunk_embeddings):
                db_manager.insert_pdf_extract(filename, text, page_count, clean_text, [emb.tolist() for emb in chunk_embeddings])
            else:
                logging.warning(f"Mismatch in number of chunks ({len(chunks)}) and embeddings ({len(chunk_embeddings)}) for {filename}. Skipping database insertion.")
        else:
            failed_extractions += 1
    
    logging.info(f"\nProcessing Summary:")
    logging.info(f"Total PDFs processed: {total_files}")
    logging.info(f"Successful extractions: {successful_extractions}")
    logging.info(f"Failed extractions: {failed_extractions}")
    
    return results

def extract_text_from_pdf(pdf_file, max_pages=None, clean_text=False, max_retries=3, retry_delay=1):
    """
    Extract text from a single PDF file with retry mechanism.
    """
    for attempt in range(max_retries):
        try:
            if isinstance(pdf_file, str):
                file = open(pdf_file, 'rb')
            else:
                file = pdf_file
            
            reader = PdfReader(file)
            
            text = ""
            total_pages = len(reader.pages)
            pages_to_process = min(total_pages, max_pages) if max_pages else total_pages
            for i in range(pages_to_process):
                text += reader.pages[i].extract_text() + "\n"
            
            if clean_text:
                text = clean_and_preprocess_text(text)
            
            if isinstance(pdf_file, str):
                file.close()
            
            return text, pages_to_process
        except (IOError, PdfReadError) as e:
            if attempt < max_retries - 1:
                logging.warning(f"Error processing PDF (attempt {attempt + 1}/{max_retries}): {str(e)}. Retrying...")
                time.sleep(retry_delay)
            else:
                logging.error(f"Failed to process PDF after {max_retries} attempts: {str(e)}")
                if isinstance(pdf_file, str) and 'file' in locals():
                    file.close()
    return None, None

if __name__ == "__main__":
    # Example usage
    single_pdf_path = "path/to/your/pdf/file.pdf"
    single_result, page_count = extract_text_from_pdf(single_pdf_path, max_pages=5)
    if single_result:
        logging.info(f"Extracted text from {single_pdf_path} ({page_count} pages):")
        logging.info(single_result[:500])  # Print first 500 characters
        logging.info("=" * 50)

    pdf_directory = "path/to/your/pdf/directory"
    results = process_multiple_pdfs([os.path.join(pdf_directory, f) for f in os.listdir(pdf_directory) if f.endswith('.pdf')],
                                    save_to_file=True, keyword_filter="report", max_pages=10, clean_text=True)
    logging.info(f"\nProcessed {len(results)} PDF files successfully.")
    
    db_manager = DatabaseManager()
    for filename in results.keys():
        db_result = db_manager.get_pdf_extract(filename)
        if db_result:
            logging.info(f"Retrieved from database - {filename}:")
            logging.info(f"Extraction date: {db_result[4]}")
            logging.info(f"Page count: {db_result[3]}")
            logging.info(f"Cleaned: {'Yes' if db_result[5] else 'No'}")
            logging.info(f"Text preview: {db_result[2][:500]}")
            logging.info("=" * 50)
    db_manager.close()
