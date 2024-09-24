from flask import Flask, render_template, request, jsonify, send_from_directory
from celery_tasks import run_indexing_pipeline, generate_context_aware_response
import os
import json
from dotenv import load_dotenv
from werkzeug.utils import secure_filename

load_dotenv()

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16 MB limit

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
    task = generate_context_aware_response.delay(query)
    return jsonify({'task_id': task.id}), 202

@app.route('/index_pdfs', methods=['POST'])
def index_pdfs():
    task = run_indexing_pipeline.delay(
        save_to_file=True,
        keyword_filter=request.form.get('keyword_filter'),
        max_pages=int(request.form.get('max_pages', 10)),
        clean_text=request.form.get('clean_text', 'true').lower() == 'true',
        chunk_size=int(request.form.get('chunk_size', os.getenv('CHUNK_SIZE', 1000))),
        chunk_overlap=int(request.form.get('chunk_overlap', os.getenv('CHUNK_OVERLAP', 200)))
    )
    return jsonify({'task_id': task.id}), 202

@app.route('/task_status/<task_id>')
def task_status(task_id):
    task = run_indexing_pipeline.AsyncResult(task_id)
    if task.state == 'PENDING':
        response = {
            'state': task.state,
            'status': 'Task is pending...'
        }
    elif task.state != 'FAILURE':
        response = {
            'state': task.state,
            'status': task.info.get('status', '')
        }
        if 'result' in task.info:
            response['result'] = task.info['result']
    else:
        response = {
            'state': task.state,
            'status': str(task.info)
        }
    return jsonify(response)

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route('/conversation', methods=['POST'])
def conversation():
    query = request.form['query']
    conversation_history = request.form.get('conversation_history', '[]')
    conversation_history = json.loads(conversation_history)
    conversation_history.append({"role": "user", "content": query})

    task = generate_context_aware_response.delay(query, conversation_history)
    return jsonify({'task_id': task.id}), 202

@app.route('/clear_conversation', methods=['POST'])
def clear_conversation():
    return jsonify({'message': 'Conversation cleared'}), 200

if __name__ == '__main__':
    app.run(debug=True)
