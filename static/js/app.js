// File upload functionality
document.addEventListener('DOMContentLoaded', function() {
    loadFiles();
    loadClipboard();
    loadNotes();
    
    // File input change
    document.getElementById('fileInput').addEventListener('change', function(e) {
        uploadFiles(e.target.files);
    });
    
    // Drag and drop
    const uploadArea = document.getElementById('uploadArea');
    uploadArea.addEventListener('dragover', function(e) {
        e.preventDefault();
        uploadArea.classList.add('dragover');
    });
    
    uploadArea.addEventListener('dragleave', function(e) {
        e.preventDefault();
        uploadArea.classList.remove('dragover');
    });
    
    uploadArea.addEventListener('drop', function(e) {
        e.preventDefault();
        uploadArea.classList.remove('dragover');
        const files = e.dataTransfer.files;
        uploadFiles(files);
    });
    
    // Notes auto-save
    const notesTextarea = document.getElementById('notesContent');
    let notesTimeout;
    notesTextarea.addEventListener('input', function() {
        clearTimeout(notesTimeout);
        notesTimeout = setTimeout(saveNotes, 500);
    });
    
    // Clipboard refresh every 2 seconds
    setInterval(refreshClipboard, 2000);
});

function uploadFiles(files) {
    const progressBar = document.querySelector('#uploadProgress .progress-bar');
    const progressDiv = document.getElementById('uploadProgress');
    const statusDiv = document.getElementById('uploadStatus');
    
    progressDiv.style.display = 'block';
    statusDiv.style.display = 'none';
    
    let uploaded = 0;
    const total = files.length;
    
    function uploadNext() {
        if (uploaded >= total) {
            progressDiv.style.display = 'none';
            showStatus('All files uploaded successfully!', 'success');
            loadFiles();
            return;
        }
        
        const file = files[uploaded];
        const formData = new FormData();
        formData.append('file', file);
        
        fetch('/api/files', {
            method: 'POST',
            body: formData
        })
        .then(response => response.json())
        .then(data => {
            if (data.error) {
                throw new Error(data.error);
            }
            uploaded++;
            progressBar.style.width = (uploaded / total * 100) + '%';
            uploadNext();
        })
        .catch(error => {
            progressDiv.style.display = 'none';
            showStatus('Upload failed: ' + error.message, 'danger');
        });
    }
    
    uploadNext();
}

function loadFiles() {
    fetch('/api/files')
        .then(response => response.json())
        .then(files => {
            const fileList = document.getElementById('fileList');
            fileList.innerHTML = '';
            
            if (files.length === 0) {
                fileList.innerHTML = '<p class="text-muted mb-0">No files available</p>';
                return;
            }
            
            files.forEach(file => {
                const item = document.createElement('a');
                item.href = file.url;
                item.className = 'list-group-item list-group-item-action d-flex justify-content-between align-items-center';
                item.innerHTML = `
                    <div>
                        <i class="fas fa-file"></i> ${file.name}
                        <small class="text-muted">(${formatBytes(file.size)})</small>
                    </div>
                    <i class="fas fa-download"></i>
                `;
                fileList.appendChild(item);
            });
        })
        .catch(error => {
            console.error('Error loading files:', error);
        });
}

function loadClipboard() {
    fetch('/api/clipboard')
        .then(response => response.json())
        .then(data => {
            const content = data.content || '';
            document.getElementById('clipboardContent').value = content;
        })
        .catch(error => {
            console.error('Error loading clipboard:', error);
        });
}

function refreshClipboard() {
    loadClipboard();
}

function setClipboard() {
    const content = document.getElementById('clipboardInput').value;
    const statusDiv = document.getElementById('clipboardStatus');
    
    fetch('/api/clipboard', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ content: content })
    })
    .then(response => response.json())
    .then(data => {
        if (data.error) {
            throw new Error(data.error);
        }
        showClipboardStatus('Clipboard updated successfully!', 'success');
        document.getElementById('clipboardInput').value = '';
        loadClipboard();
    })
    .catch(error => {
        showClipboardStatus('Failed to update clipboard: ' + error.message, 'danger');
    });
}

function loadNotes() {
    fetch('/api/notes')
        .then(response => response.json())
        .then(data => {
            const content = data.content || '';
            document.getElementById('notesContent').value = content;
        })
        .catch(error => {
            console.error('Error loading notes:', error);
        });
}

function saveNotes() {
    const content = document.getElementById('notesContent').value;
    const statusDiv = document.getElementById('notesStatus');
    
    fetch('/api/notes', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ content: content })
    })
    .then(response => response.json())
    .then(data => {
        if (data.error) {
            throw new Error(data.error);
        }
        showNotesStatus('Notes saved automatically');
    })
    .catch(error => {
        showNotesStatus('Failed to save notes: ' + error.message, 'danger');
    });
}

function showStatus(message, type) {
    const statusDiv = document.getElementById('uploadStatus');
    statusDiv.className = `alert alert-${type}`;
    statusDiv.textContent = message;
    statusDiv.style.display = 'block';
    setTimeout(() => {
        statusDiv.style.display = 'none';
    }, 5000);
}

function showClipboardStatus(message, type = 'success') {
    const statusDiv = document.getElementById('clipboardStatus');
    statusDiv.className = `alert alert-${type}`;
    statusDiv.textContent = message;
    statusDiv.style.display = 'block';
    setTimeout(() => {
        statusDiv.style.display = 'none';
    }, 3000);
}

function showNotesStatus(message, type = 'success') {
    const statusDiv = document.getElementById('notesStatus');
    statusDiv.className = `alert alert-${type}`;
    statusDiv.textContent = message;
    statusDiv.style.display = 'block';
    setTimeout(() => {
        statusDiv.style.display = 'none';
    }, 2000);
}

function formatBytes(bytes) {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
}
