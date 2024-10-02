# PDFChatAI

PDFChatAI is an advanced tool for interacting with PDF documents using AI technology. It processes PDF files, extracts text, generates embeddings, and enables context-aware querying through a user-friendly web interface with asynchronous task processing.

## Features

- Extract text from single or multiple PDF files
- Clean and preprocess extracted text
- Generate embeddings for text chunks using OpenAI's models or local models
- Store extracted text, metadata, and embeddings in a SQLite database
- Use FAISS for efficient similarity search
- Perform context-aware querying with conversation history
- Web interface for uploading PDFs, indexing, and querying
- Asynchronous task processing using Python's threading module

## Requirements

- Python 3.7+
- Flask
- PyPDF2
- NLTK
- sentence-transformers
- FAISS
- OpenAI API (optional)

## Installation

1. Clone this repository:
   ```
   git clone https://github.com/yourusername/PDFChatAI.git
   cd PDFChatAI
   ```

2. Create and activate a virtual environment:
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
   ```

3. Install the required packages:
   ```
   pip install -r requirements.txt
   ```

4. Set up environment variables:
   Create a `.env` file in the project root and add the necessary variables.

## Usage

1. Run the Flask application:
   ```
   python app.py
   ```

2. Open a web browser and navigate to `http://localhost:5000` to access the web interface.

3. Use the web interface to:
   - Upload PDF files
   - Index PDF files
   - Perform context-aware queries
   - View conversation history

## File Descriptions

- `app.py`: Flask application for the web interface
- `indexing_pipeline.py`: Main pipeline for processing and indexing PDFs
- `pdf_processor.py`: Functions for extracting text from PDFs
- `database_manager.py`: Manages the SQLite database
- `embedding_model.py`: Handles embedding generation
- `faiss_manager.py`: Manages the FAISS index for similarity search
- `query_processor.py`: Processes and expands queries
- `prompt_engineer.py`: Generates prompts for context-aware responses
- `openrouter_client.py`: Client for interacting with the OpenRouter API

## License

PDFChatAI is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
