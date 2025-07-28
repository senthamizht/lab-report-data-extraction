from flask import Flask, request, jsonify
from paddleocr import PaddleOCR
import tempfile
import os
from PIL import Image
import io
import base64
from paddletest import extract_data_from_file

app = Flask(__name__)
ocr = PaddleOCR(use_angle_cls=True, lang='en')  # Load the model once

@app.route('/')
def index():
    return "Flask server is running"

@app.route('/ocr', methods=['POST'])
def ocr_endpoint():
    if 'file' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400

    uploaded_file = request.files['file']
    filename = uploaded_file.filename

    with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(filename)[1]) as tmp:
        uploaded_file.save(tmp.name)
        tmp_path = tmp.name

    try:
        jsonText = extract_data_from_file(tmp_path)
        return jsonify(jsonText)
    finally:
        os.remove(tmp_path)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)
