from flask import Flask, render_template, request, jsonify, send_from_directory
from indexing_pipeline import IndexingPipeline
import os
from dotenv import load_dotenv
from werkzeug.utils import secure_filename

load_dotenv()

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = os.getenv('PDF_DIRECTORY')
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16 MB limit

pipeline = IndexingPipeline()

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
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)
        return jsonify({'message': f'File {filename} uploaded successfully'}), 200
    else:
        return jsonify({'error': 'Invalid file type. Please upload a PDF.'}), 400

@app.route('/search', methods=['POST'])
def search():
    query = request.form['query']
    response = pipeline.generate_context_aware_response(query)
    return jsonify({'response': response})

@app.route('/index_pdfs', methods=['POST'])
def index_pdfs():
    results = pipeline.run(
        save_to_file=True,
        keyword_filter=request.form.get('keyword_filter'),
        max_pages=int(request.form.get('max_pages', 10)),
        clean_text=request.form.get('clean_text', 'true').lower() == 'true',
        chunk_size=int(request.form.get('chunk_size', os.getenv('CHUNK_SIZE', 1000))),
        chunk_overlap=int(request.form.get('chunk_overlap', os.getenv('CHUNK_OVERLAP', 200)))
    )
    return jsonify({'message': f'Indexed {len(results)} PDF files successfully.'})

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

if __name__ == '__main__':
    app.run(debug=True)
