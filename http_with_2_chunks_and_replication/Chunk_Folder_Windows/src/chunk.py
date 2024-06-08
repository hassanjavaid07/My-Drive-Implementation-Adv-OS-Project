from flask import Flask, request, Response, jsonify
import os
import socket
import logging
from zeroconf import Zeroconf, ServiceInfo
import random
import sys

app = Flask(__name__)
CHUNK_SIZE = 4096

# Setup logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

@app.route('/upload', methods=['POST'])
def upload():
    try:
        file = request.files['file']
        file_path = os.path.join('chunks', file.filename)
       
        # Ensure the directory exists
        if not os.path.exists('chunks'):
            os.makedirs('chunks')
       
        file.save(file_path)
        logger.info(f"File {file.filename} uploaded successfully to {file_path}.")
        return 'File uploaded successfully', 200
    except Exception as e:
        logger.error(f"Error during file upload: {e}")
        return 'File upload failed', 500

@app.route('/download/<filename>', methods=['GET'])
def download(filename):
    try:
        file_path = os.path.join('chunks', filename)
        if os.path.exists(file_path):
            def generate():
                with open(file_path, 'rb') as f:
                    while True:
                        chunk = f.read(CHUNK_SIZE)
                        if not chunk:
                            break
                        yield chunk

            return Response(generate(), headers={
                'Content-Disposition': f'attachment; filename={filename}',
                'Content-Type': 'application/octet-stream'
            })
        else:
            logger.error(f"File not found: {filename}")
            return 'File not found', 404
    except Exception as e:
        logger.error(f"Error during file download: {e}")
        return 'File download failed', 500

@app.route('/list_files', methods=['GET'])
def list_files():
    try:
        files = os.listdir('chunks')
        return jsonify(files)
    except Exception as e:
        logger.error(f"Error listing files: {e}")
        return 'Error listing files', 500

if __name__ == "__main__":
    # Zeroconf setup
    zeroconf = Zeroconf()
   
    # Dynamically get the IP address of the server
    hostname = socket.gethostname()
    ip_address = socket.gethostbyname(hostname)
   
    # Assign a unique name to each chunk server
    chunk_server_name = f"chunk_server_{random.randint(1000, 9999)}._http._tcp.local."
   
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 5001

    service_info = ServiceInfo(
        "_http._tcp.local.",
        chunk_server_name,
        addresses=[socket.inet_aton(ip_address)],  # Use dynamically obtained IP
        port=port,
        properties={},
    )
    zeroconf.register_service(service_info)
   
    try:
        logger.info(f"Starting chunk server on {ip_address}:{port}")
        app.run(host='0.0.0.0', port=port)
    except Exception as e:
        logger.error(f"Error starting chunk server: {e}")
    finally:
        zeroconf.unregister_service(service_info)
        zeroconf.close()


