from flask import Flask, render_template, request, jsonify
from indexing_pipeline import IndexingPipeline
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
pipeline = IndexingPipeline()

@app.route('/')
def index():
    return render_template('index.html')

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

if __name__ == '__main__':
    app.run(debug=True)
