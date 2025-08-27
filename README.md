# LocalBridge

A self-hosted web application for seamless file transfer, clipboard synchronization, and text sharing between PC and mobile devices over a local network.

## Features

- **File Transfer**: Upload files from mobile to PC, download files from PC to mobile
- **Clipboard Sync**: View and update PC clipboard content from mobile
- **Quick Notes**: Shared text area accessible from all devices
- **Responsive Design**: Mobile-friendly interface
- **Security**: File type validation, size limits, secure file handling

## Requirements

- Python 3.7+
- Internet connection for initial setup (dependencies only)

## Quick Start (Windows)

1. **Double-click `run.bat`** - This will:
   - Create a virtual environment
   - Install all dependencies
   - Start the LocalBridge server

2. **Access from mobile**: Open the displayed URL in your browser

## Manual Setup

If you prefer to set up manually:

### 1. Create Virtual Environment
```bash
python -m venv venv
```

### 2. Activate Virtual Environment
**Windows:**
```bash
venv\Scripts\activate
```

**Linux/Mac:**
```bash
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Run the Application
```bash
python run.py
```

Or with custom port:
```bash
python run.py 8080
```

## Project Structure

```
local-transfer/
├── app/                    # Main application package
│   ├── __init__.py
│   └── app.py             # Flask application
├── static/                # CSS and JavaScript files
│   ├── css/
│   └── js/
├── templates/             # HTML templates
├── data/                  # Application data (notes, etc.)
├── uploads/               # Uploaded files
├── venv/                  # Virtual environment (created automatically)
├── requirements.txt       # Python dependencies
├── run.py                 # Application entry point
├── run.bat               # Windows batch script
├── README.md             # This file
└── .gitignore            # Git ignore rules
```

## Usage

1. Start the application using one of the methods above
2. The application will display the local network URL (e.g., http://192.168.1.100:5000)
3. Open the URL in your mobile browser
4. Use the interface to:
   - Upload files by dragging/dropping or selecting
   - View available files for download
   - Sync clipboard content
   - Share quick notes

## Security Notes

- The application binds to all local network interfaces (0.0.0.0)
- File uploads are limited to 500MB per file
- Only specific file types are allowed
- All operations are logged for monitoring

## Troubleshooting

- If port 5000 is in use, the application will automatically try the next available port
- Ensure your firewall allows local network connections
- For clipboard functionality, ensure pyperclip can access the system clipboard

## Future Enhancements

- QR code generation for easy mobile access
- Real-time updates using WebSockets
- Enhanced drag-and-drop interface
- Remote PC control capabilities
