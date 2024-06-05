from flask import Flask, request, Response, jsonify
import os
import socket
import logging
from zeroconf import Zeroconf, ServiceInfo
import random




app = Flask(__name__)
CHUNK_SIZE = 4096




# Setup logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)




@app.route('/upload', methods=['POST'])
def upload():
    file = request.files['file']
    file_path = os.path.join('chunks', file.filename)
   
    # Ensure the directory exists
    if not os.path.exists('chunks'):
        os.makedirs('chunks')
       
    file.save(file_path)
    logger.info(f"File {file.filename} uploaded successfully to {file_path}.")
    return 'File uploaded successfully', 200




@app.route('/download/<filename>', methods=['GET'])
def download(filename):
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
        return 'File not found', 404


@app.route('/list_files', methods=['GET'])
def list_files():
    files = os.listdir('chunks')
    return jsonify(files)




if __name__ == "__main__":
    # Zeroconf setup
    zeroconf = Zeroconf()
   
    # Dynamically get the IP address of the server
    ip_address = socket.gethostbyname(socket.gethostname())
   
    # Assign a unique name to each chunk server
    chunk_server_name = f"chunk_server_{random.randint(1000, 9999)}._http._tcp.local."
   
    service_info = ServiceInfo(
        "_http._tcp.local.",
        chunk_server_name,
        addresses=[socket.inet_aton(ip_address)],  # Use dynamically obtained IP
        port=5001,
        properties={},
    )
    zeroconf.register_service(service_info)
   
    try:
        app.run(host='0.0.0.0', port=5001)
    finally:
        zeroconf.unregister_service(service_info)
        zeroconf.close()