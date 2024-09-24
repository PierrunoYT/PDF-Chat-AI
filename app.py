from flask import Flask, render_template, request, jsonify, send_from_directory
from indexing_pipeline import IndexingPipeline
import os
import json
from dotenv import load_dotenv
from werkzeug.utils import secure_filename
import threading
import uuid

load_dotenv()

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16 MB limit

# Dictionary to store task results
task_results = {}

def run_indexing_pipeline_task(task_id, save_to_file, keyword_filter, max_pages, clean_text, chunk_size, chunk_overlap):
    pipeline = IndexingPipeline()
    pdf_files = [os.path.join(app.config['UPLOAD_FOLDER'], f) for f in os.listdir(app.config['UPLOAD_FOLDER']) if f.lower().endswith('.pdf')]
    results = pipeline.run(
        pdf_files,
        save_to_file=save_to_file,
        keyword_filter=keyword_filter,
        max_pages=max_pages,
        clean_text=clean_text,
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap
    )
    task_results[task_id] = f'Indexed {len(results)} PDF files successfully.'

def generate_context_aware_response_task(task_id, query_text, conversation_history, k=5):
    pipeline = IndexingPipeline()
    response = pipeline.generate_context_aware_response(query_text, conversation_history, k)
    task_results[task_id] = {'response': response, 'conversation_history': conversation_history + [{"role": "assistant", "content": response}]}

@app.route('/')
def index():
    if not os.path.exists(app.config['UPLOAD_FOLDER']):
        os.makedirs(app.config['UPLOAD_FOLDER'])
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'document' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    file = request.files['document']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    if file and file.filename.lower().endswith('.pdf'):
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)
        return jsonify({'message': f'File {filename} uploaded successfully'}), 200
    else:
        return jsonify({'error': 'Invalid file type. Please upload a PDF.'}), 400

@app.route('/search', methods=['POST'])
def search():
    query = request.form['query']
    conversation_history = json.loads(request.form.get('conversation_history', '[]'))
    task_id = str(uuid.uuid4())
    thread = threading.Thread(target=generate_context_aware_response_task, args=(task_id, query, conversation_history))
    thread.start()
    return jsonify({'task_id': task_id}), 202

@app.route('/index_pdfs', methods=['POST'])
def index_pdfs():
    task_id = str(uuid.uuid4())
    thread = threading.Thread(target=run_indexing_pipeline_task, args=(
        task_id,
        True,
        request.form.get('keyword_filter'),
        int(request.form.get('max_pages', 10)),
        request.form.get('clean_text', 'true').lower() == 'true',
        int(request.form.get('chunk_size', os.getenv('CHUNK_SIZE', 1000))),
        int(request.form.get('chunk_overlap', os.getenv('CHUNK_OVERLAP', 200)))
    ))
    thread.start()
    return jsonify({'task_id': task_id}), 202

@app.route('/task_status/<task_id>')
def task_status(task_id):
    if task_id in task_results:
        return jsonify({'state': 'SUCCESS', 'result': task_results[task_id]})
    else:
        return jsonify({'state': 'PENDING', 'status': 'Task is pending...'})

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

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
