from flask import Flask, request, jsonify, send_from_directory, render_template
import os
import socket
import pyperclip
from werkzeug.utils import secure_filename
import logging
from logging.handlers import TimedRotatingFileHandler
from pathlib import Path

# Get the project root directory (parent of app directory)
PROJECT_ROOT = Path(__file__).parent.parent

app = Flask(__name__,
            template_folder=str(PROJECT_ROOT / 'templates'),
            static_folder=str(PROJECT_ROOT / 'static'))

# Configuration
UPLOAD_FOLDER = str(PROJECT_ROOT / 'uploads')
NOTES_FILE = str(PROJECT_ROOT / 'data' / 'notes.txt')
PC_CLIPBOARD_FILE = str(PROJECT_ROOT / 'data' / 'pc_clipboard.txt')
MOBILE_CLIPBOARD_FILE = str(PROJECT_ROOT / 'data' / 'mobile_clipboard.txt')
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif', 'doc', 'docx', 'xls', 'xlsx', 'ppt', 'pptx', 'zip', 'rar'}
MAX_FILE_SIZE = 500 * 1024 * 1024  # 500MB

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = MAX_FILE_SIZE

# Ensure directories exist
Path(UPLOAD_FOLDER).mkdir(exist_ok=True)
Path(PROJECT_ROOT / 'data').mkdir(exist_ok=True)
Path(PROJECT_ROOT / 'logs').mkdir(exist_ok=True)

# Logging Configuration
def setup_logging():
    # Create logger
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)

    # Remove default handlers
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)

    # Create timed rotating file handler (rotates every hour)
    log_file = str(PROJECT_ROOT / 'logs' / 'localbridge.log')
    file_handler = TimedRotatingFileHandler(
        log_file,
        when='H',      # Rotate every hour
        interval=1,    # Every 1 hour
        backupCount=24 # Keep 24 hours of logs
    )

    # Create formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    file_handler.setFormatter(formatter)

    # Add handler to logger
    logger.addHandler(file_handler)

    # Disable Werkzeug access logging to console
    werkzeug_logger = logging.getLogger('werkzeug')
    werkzeug_logger.setLevel(logging.WARNING)
    werkzeug_logger.handlers = []  # Remove all handlers

    return logger

# Setup logging
app_logger = setup_logging()

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
        app_logger.info(f"Listed {len(files)} files")
        return jsonify(files)
    except Exception as e:
        app_logger.error(f"Error listing files: {e}")
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
        file_size = os.path.getsize(filepath)
        app_logger.info(f"File uploaded: {filename} ({file_size} bytes)")
        return jsonify({'message': 'File uploaded successfully', 'filename': filename}), 200
    else:
        app_logger.warning(f"Rejected file upload: {file.filename if file else 'None'}")
        return jsonify({'error': 'File type not allowed'}), 400

@app.route('/api/files/<filename>', methods=['GET'])
def download_file(filename):
    try:
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        if os.path.exists(filepath):
            file_size = os.path.getsize(filepath)
            app_logger.info(f"File downloaded: {filename} ({file_size} bytes)")
        return send_from_directory(app.config['UPLOAD_FOLDER'], filename, as_attachment=True)
    except FileNotFoundError:
        app_logger.warning(f"File not found for download: {filename}")
        return jsonify({'error': 'File not found'}), 404
    except Exception as e:
        app_logger.error(f"Error downloading file {filename}: {e}")
        return jsonify({'error': 'Failed to download file'}), 500

@app.route('/api/clipboard', methods=['GET'])
def get_clipboard():
    try:
        content = pyperclip.paste()
        # Only log if there's actual content and it's not too frequent
        if content and len(content.strip()) > 0:
            app_logger.debug(f"Clipboard accessed: {len(content)} characters")
        return jsonify({'content': content})
    except Exception as e:
        app_logger.error(f"Error getting clipboard: {e}")
        return jsonify({'error': 'Failed to get clipboard content'}), 500

@app.route('/api/clipboard', methods=['POST'])
def set_clipboard():
    data = request.get_json()
    if not data or 'content' not in data:
        return jsonify({'error': 'No content provided'}), 400
    try:
        content = data['content']
        pyperclip.copy(content)
        app_logger.info(f"Clipboard updated: {len(content)} characters")
        return jsonify({'message': 'Clipboard updated successfully'}), 200
    except Exception as e:
        app_logger.error(f"Error setting clipboard: {e}")
        return jsonify({'error': 'Failed to update clipboard'}), 500

@app.route('/api/clipboard/pc', methods=['GET'])
def get_pc_clipboard():
    try:
        if os.path.exists(PC_CLIPBOARD_FILE):
            with open(PC_CLIPBOARD_FILE, 'r', encoding='utf-8') as f:
                content = f.read()
        else:
            content = ''
        return jsonify({'content': content})
    except Exception as e:
        app_logger.error(f"Error getting PC clipboard: {e}")
        return jsonify({'error': 'Failed to get PC clipboard content'}), 500

@app.route('/api/clipboard/pc', methods=['POST'])
def set_pc_clipboard():
    data = request.get_json()
    if not data or 'content' not in data:
        return jsonify({'error': 'No content provided'}), 400
    try:
        content = data['content']
        with open(PC_CLIPBOARD_FILE, 'w', encoding='utf-8') as f:
            f.write(content)
        app_logger.info(f"PC clipboard updated: {len(content)} characters")
        return jsonify({'message': 'PC clipboard updated successfully'}), 200
    except Exception as e:
        app_logger.error(f"Error setting PC clipboard: {e}")
        return jsonify({'error': 'Failed to update PC clipboard'}), 500

@app.route('/api/clipboard/mobile', methods=['GET'])
def get_mobile_clipboard():
    try:
        if os.path.exists(MOBILE_CLIPBOARD_FILE):
            with open(MOBILE_CLIPBOARD_FILE, 'r', encoding='utf-8') as f:
                content = f.read()
        else:
            content = ''
        return jsonify({'content': content})
    except Exception as e:
        app_logger.error(f"Error getting mobile clipboard: {e}")
        return jsonify({'error': 'Failed to get mobile clipboard content'}), 500

@app.route('/api/clipboard/mobile', methods=['POST'])
def set_mobile_clipboard():
    data = request.get_json()
    if not data or 'content' not in data:
        return jsonify({'error': 'No content provided'}), 400
    try:
        content = data['content']
        with open(MOBILE_CLIPBOARD_FILE, 'w', encoding='utf-8') as f:
            f.write(content)
        app_logger.info(f"Mobile clipboard updated: {len(content)} characters")
        return jsonify({'message': 'Mobile clipboard updated successfully'}), 200
    except Exception as e:
        app_logger.error(f"Error setting mobile clipboard: {e}")
        return jsonify({'error': 'Failed to update mobile clipboard'}), 500

@app.route('/api/notes', methods=['GET'])
def get_notes():
    try:
        if os.path.exists(NOTES_FILE):
            with open(NOTES_FILE, 'r', encoding='utf-8') as f:
                content = f.read()
        else:
            content = ''
        # Only log if there are notes
        if content and len(content.strip()) > 0:
            app_logger.debug(f"Notes accessed: {len(content)} characters")
        return jsonify({'content': content})
    except Exception as e:
        app_logger.error(f"Error getting notes: {e}")
        return jsonify({'error': 'Failed to get notes'}), 500

@app.route('/api/notes', methods=['POST'])
def set_notes():
    data = request.get_json()
    if not data or 'content' not in data:
        return jsonify({'error': 'No content provided'}), 400
    try:
        content = data['content']
        with open(NOTES_FILE, 'w', encoding='utf-8') as f:
            f.write(content)
        app_logger.info(f"Notes updated: {len(content)} characters")
        return jsonify({'message': 'Notes updated successfully'}), 200
    except Exception as e:
        app_logger.error(f"Error setting notes: {e}")
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
            app_logger.info(f"LocalBridge server starting on http://{local_ip}:{port}")
            print(f"LocalBridge is running at: http://{local_ip}:{port}")
            print(f"Access from your mobile device using the above URL")
            print(f"Logs are being written to: {PROJECT_ROOT / 'logs' / 'localbridge.log'}")
            app.run(host='0.0.0.0', port=port, debug=False)  # Disable debug mode to reduce console output
            break
        except OSError as e:
            if e.errno == 48:  # Address already in use
                app_logger.warning(f"Port {port} is in use, trying {port + 1}")
                print(f"Port {port} is in use, trying {port + 1}")
                port += 1
            else:
                app_logger.error(f"Failed to start server: {e}")
                raise