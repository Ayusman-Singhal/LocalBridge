from flask import Flask, request, jsonify, send_from_directory, render_template
import os
import socket
import pyperclip
from werkzeug.utils import secure_filename
import logging
from pathlib import Path

# Get the project root directory (parent of app directory)
PROJECT_ROOT = Path(__file__).parent.parent

app = Flask(__name__,
            template_folder=str(PROJECT_ROOT / 'templates'),
            static_folder=str(PROJECT_ROOT / 'static'))

# Configuration
UPLOAD_FOLDER = str(PROJECT_ROOT / 'uploads')
NOTES_FILE = str(PROJECT_ROOT / 'data' / 'notes.txt')
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif', 'doc', 'docx', 'xls', 'xlsx', 'ppt', 'pptx', 'zip', 'rar'}
MAX_FILE_SIZE = 500 * 1024 * 1024  # 500MB

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = MAX_FILE_SIZE

# Ensure directories exist
Path(UPLOAD_FOLDER).mkdir(exist_ok=True)
Path(PROJECT_ROOT / 'data').mkdir(exist_ok=True)

# Logging
logging.basicConfig(level=logging.INFO)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def get_local_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(('10.255.255.255', 1))
        IP = s.getsockname()[0]
    except:
        IP = '127.0.0.1'
    finally:
        s.close()
    return IP

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/files', methods=['GET'])
def list_files():
    try:
        files = []
        for filename in os.listdir(UPLOAD_FOLDER):
            filepath = os.path.join(UPLOAD_FOLDER, filename)
            if os.path.isfile(filepath):
                files.append({
                    'name': filename,
                    'size': os.path.getsize(filepath),
                    'url': f'/api/files/{filename}'
                })
        return jsonify(files)
    except Exception as e:
        logging.error(f"Error listing files: {e}")
        return jsonify({'error': 'Failed to list files'}), 500

@app.route('/api/files', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        return jsonify({'message': 'File uploaded successfully', 'filename': filename}), 200
    else:
        return jsonify({'error': 'File type not allowed'}), 400

@app.route('/api/files/<filename>', methods=['GET'])
def download_file(filename):
    try:
        return send_from_directory(app.config['UPLOAD_FOLDER'], filename, as_attachment=True)
    except FileNotFoundError:
        return jsonify({'error': 'File not found'}), 404
    except Exception as e:
        logging.error(f"Error downloading file: {e}")
        return jsonify({'error': 'Failed to download file'}), 500

@app.route('/api/clipboard', methods=['GET'])
def get_clipboard():
    try:
        content = pyperclip.paste()
        return jsonify({'content': content})
    except Exception as e:
        logging.error(f"Error getting clipboard: {e}")
        return jsonify({'error': 'Failed to get clipboard content'}), 500

@app.route('/api/clipboard', methods=['POST'])
def set_clipboard():
    data = request.get_json()
    if not data or 'content' not in data:
        return jsonify({'error': 'No content provided'}), 400
    try:
        pyperclip.copy(data['content'])
        return jsonify({'message': 'Clipboard updated successfully'}), 200
    except Exception as e:
        logging.error(f"Error setting clipboard: {e}")
        return jsonify({'error': 'Failed to update clipboard'}), 500

@app.route('/api/notes', methods=['GET'])
def get_notes():
    try:
        if os.path.exists(NOTES_FILE):
            with open(NOTES_FILE, 'r', encoding='utf-8') as f:
                content = f.read()
        else:
            content = ''
        return jsonify({'content': content})
    except Exception as e:
        logging.error(f"Error getting notes: {e}")
        return jsonify({'error': 'Failed to get notes'}), 500

@app.route('/api/notes', methods=['POST'])
def set_notes():
    data = request.get_json()
    if not data or 'content' not in data:
        return jsonify({'error': 'No content provided'}), 400
    try:
        with open(NOTES_FILE, 'w', encoding='utf-8') as f:
            f.write(data['content'])
        return jsonify({'message': 'Notes updated successfully'}), 200
    except Exception as e:
        logging.error(f"Error setting notes: {e}")
        return jsonify({'error': 'Failed to update notes'}), 500

if __name__ == '__main__':
    import sys
    port = 5000
    if len(sys.argv) > 1:
        try:
            port = int(sys.argv[1])
        except ValueError:
            print("Invalid port number, using default 5000")

    # Find available port
    while True:
        try:
            local_ip = get_local_ip()
            print(f"LocalBridge is running at: http://{local_ip}:{port}")
            print(f"Access from your mobile device using the above URL")
            app.run(host='0.0.0.0', port=port, debug=True)
            break
        except OSError as e:
            if e.errno == 48:  # Address already in use
                print(f"Port {port} is in use, trying {port + 1}")
                port += 1
            else:
                raise
