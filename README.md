# PDF Processing and Querying System

This project provides a comprehensive system for processing PDF files, extracting text, generating embeddings, and performing context-aware querying. It includes a web interface for easy interaction and asynchronous task processing.

## Features

- Extract text from single or multiple PDF files
- Clean and preprocess extracted text
- Generate embeddings for text chunks using OpenAI's models or local models
- Store extracted text, metadata, and embeddings in a SQLite database
- Use FAISS for efficient similarity search
- Perform context-aware querying with conversation history
- Web interface for uploading PDFs, indexing, and querying
- Asynchronous task processing with Celery and Redis

## Requirements

- Python 3.7+
- Flask
- Celery
- Redis
- PyPDF2
- NLTK
- sentence-transformers
- FAISS
- OpenAI API (optional)

## Installation

1. Clone this repository:
   ```
   git clone https://github.com/yourusername/pdf-processing-system.git
   cd pdf-processing-system
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
   Create a `.env` file in the project root and add the following variables:
   ```
   OPENROUTER_API_KEY=your_openrouter_api_key_here
   SITE_URL=https://your-site-url.com
   SITE_NAME=Your Site Name
   DB_NAME=pdf_extracts.db
   FAISS_INDEX_FILE=pdf_embeddings.faiss
   PDF_DIRECTORY=path/to/your/pdf/directory
   USE_OPENROUTER=True
   LOCAL_MODEL_NAME=all-MiniLM-L6-v2
   OPENAI_EMBEDDING_MODEL=openai/text-embedding-3-small
   EMBEDDING_DIMENSIONS=1536
   CHUNK_SIZE=1000
   CHUNK_OVERLAP=200
   TOP_K_RESULTS=5
   ```

5. Set up Redis:
   Make sure Redis is installed and running on your system.

## Usage

1. Start the Celery worker:
   ```
   celery -A celery_tasks worker --loglevel=info
   ```

2. Run the Flask application:
   ```
   python app.py
   ```

3. Open a web browser and navigate to `http://localhost:5000` to access the web interface.

4. Use the web interface to:
   - Upload PDF files
   - Index PDF files
   - Perform context-aware queries
   - View conversation history

## File Descriptions

- `app.py`: Flask application for the web interface
- `celery_tasks.py`: Celery tasks for asynchronous processing
- `indexing_pipeline.py`: Main pipeline for processing and indexing PDFs
- `pdf_processor.py`: Functions for extracting text from PDFs
- `database_manager.py`: Manages the SQLite database
- `embedding_model.py`: Handles embedding generation
- `faiss_manager.py`: Manages the FAISS index for similarity search
- `query_processor.py`: Processes and expands queries
- `prompt_engineer.py`: Generates prompts for context-aware responses
- `openrouter_client.py`: Client for interacting with the OpenRouter API

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
