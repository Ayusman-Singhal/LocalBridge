#!/usr/bin/env python3
"""
LocalBridge - Run Script
Starts the LocalBridge web application
"""

from app.app import app
import sys

if __name__ == '__main__':
    port = 5000
    if len(sys.argv) > 1:
        try:
            port = int(sys.argv[1])
        except ValueError:
            print("Invalid port number, using default 5000")
            port = 5000

    print("Starting LocalBridge...")
    print("Make sure you're running this from the virtual environment!")
    print()

    # Import the main app logic
    from app.app import get_local_ip

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
