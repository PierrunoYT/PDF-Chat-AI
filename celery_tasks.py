from celery import Celery
from indexing_pipeline import IndexingPipeline

celery = Celery('tasks', broker='redis://localhost:6379/0')

@celery.task
def run_indexing_pipeline(save_to_file=False, keyword_filter=None, max_pages=None, clean_text=False, chunk_size=1000, chunk_overlap=200):
    pipeline = IndexingPipeline()
    results = pipeline.run(
        save_to_file=save_to_file,
        keyword_filter=keyword_filter,
        max_pages=max_pages,
        clean_text=clean_text,
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap
    )
    return f'Indexed {len(results)} PDF files successfully.'

@celery.task
def generate_context_aware_response(query_text, conversation_history, k=5):
    pipeline = IndexingPipeline()
    response = pipeline.generate_context_aware_response(query_text, conversation_history, k)
    return response
