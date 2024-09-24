from flask import Flask, render_template, request, jsonify
from indexing_pipeline import IndexingPipeline
import json
from dotenv import load_dotenv
import threading
import uuid
import io
import os

load_dotenv()

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16 MB limit
app.config['UPLOAD_FOLDER'] = 'uploads'

# Dictionary to store task results
task_results = {}

def run_indexing_pipeline_task(task_id, pdf_files, save_to_file, keyword_filter, max_pages, clean_text, chunk_size, chunk_overlap):
    pipeline = IndexingPipeline()
    total_indexed = 0
    for pdf_file in pdf_files:
        try:
            results = pipeline.run(
                pdf_files=[pdf_file],
                save_to_file=save_to_file,
                keyword_filter=keyword_filter,
                max_pages=max_pages,
                clean_text=clean_text,
                chunk_size=chunk_size,
                chunk_overlap=chunk_overlap
            )
            total_indexed += len(results)
        except Exception as e:
            print(f"Error processing {pdf_file}: {str(e)}")
    task_results[task_id] = f'Indexed {total_indexed} PDF files successfully.'

def generate_context_aware_response_task(task_id, query_text, conversation_history, k=5):
    pipeline = IndexingPipeline()
    response = pipeline.generate_context_aware_response(query_text, conversation_history, k)
    task_results[task_id] = {'response': response, 'conversation_history': conversation_history + [{"role": "assistant", "content": response}]}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'document' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    file = request.files['document']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    if file and file.filename.lower().endswith('.pdf'):
        filename = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
        file.save(filename)
        return jsonify({'message': f'File {file.filename} uploaded successfully'}), 200
    else:
        return jsonify({'error': 'Invalid file type. Please upload a PDF.'}), 400

@app.route('/index_pdfs', methods=['POST'])
def index_pdfs():
    task_id = str(uuid.uuid4())
    pdf_files = [os.path.join(app.config['UPLOAD_FOLDER'], f) for f in os.listdir(app.config['UPLOAD_FOLDER']) if f.lower().endswith('.pdf')]
    thread = threading.Thread(target=run_indexing_pipeline_task, args=(
        task_id,
        pdf_files,
        True,
        request.form.get('keyword_filter'),
        int(request.form.get('max_pages', 10)),
        request.form.get('clean_text', 'true').lower() == 'true',
        int(request.form.get('chunk_size', 1000)),
        int(request.form.get('chunk_overlap', 200))
    ))
    thread.start()
    return jsonify({'message': 'Indexing started', 'task_id': task_id}), 202

@app.route('/search', methods=['POST'])
def search():
    query = request.form['query']
    conversation_history = json.loads(request.form.get('conversation_history', '[]'))
    task_id = str(uuid.uuid4())
    thread = threading.Thread(target=generate_context_aware_response_task, args=(task_id, query, conversation_history))
    thread.start()
    return jsonify({'task_id': task_id}), 202

@app.route('/task_status/<task_id>')
def task_status(task_id):
    if task_id in task_results:
        return jsonify({'state': 'SUCCESS', 'result': task_results[task_id]})
    else:
        return jsonify({'state': 'PENDING', 'status': 'Task is pending...'})

@app.route('/conversation', methods=['POST'])
def conversation():
    query = request.form['query']
    conversation_history = json.loads(request.form.get('conversation_history', '[]'))
    conversation_history.append({"role": "user", "content": query})

    task_id = str(uuid.uuid4())
    thread = threading.Thread(target=generate_context_aware_response_task, args=(task_id, query, conversation_history))
    thread.start()
    return jsonify({'task_id': task_id}), 202

@app.route('/clear_conversation', methods=['POST'])
def clear_conversation():
    return jsonify({'message': 'Conversation cleared'}), 200

if __name__ == '__main__':
    app.run(debug=True)
