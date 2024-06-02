import os
import json
import requests
import warnings
import logging
import time
import socket
from zeroconf import Zeroconf, ServiceBrowser
from dfscontrol_copy import readConfigFile, getChunkServer, splitFile, mergeChunks, encryptChunk, decryptChunk, writeJsonFile, generateChecksum, decryptFile

# Suppress FutureWarning
warnings.simplefilter(action='ignore', category=FutureWarning)

# Setup logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

class MyListener:
    def __init__(self):
        self.services = []

    def add_service(self, zeroconf, type, name):
        info = zeroconf.get_service_info(type, name)
        if info:
            address = socket.inet_ntoa(info.addresses[0])
            self.services.append({
                "upload_url": f"http://{address}:{info.port}/upload",
                "download_url": f"http://{address}:{info.port}/download/",
                "list_files_url": f"http://{address}:{info.port}/list_files"
            })

zeroconf = Zeroconf()
listener = MyListener()
browser = ServiceBrowser(zeroconf, "_http._tcp.local.", listener)

config_file_path = 'dfs_setup.config'

# Handle FileNotFoundError
try:
    config = readConfigFile(config_file_path)
except FileNotFoundError:
    logger.error(f"Config file not found at: {config_file_path}")
    exit(1)

chunk_size = int(config['chunk_size'])
num_chunk_servers = int(config['num_chunk_servers'])
master_key = bytes.fromhex(config['master_key'])
replication_factor = 2

metadata_uploaded_file = 'metadata_uploaded.json'
metadata_uploaded = {}

# Load existing metadata if available
if os.path.exists(metadata_uploaded_file):
    with open(metadata_uploaded_file, 'r') as f:
        metadata_uploaded = json.load(f)

def save_metadata_uploaded():
    with open(metadata_uploaded_file, 'w') as f:
        json.dump(metadata_uploaded, f, indent=4)

def upload_file(file_path, chunk_servers):
    file_name = os.path.basename(file_path)
    temp_dir = 'temp_chunks'
    os.makedirs(temp_dir, exist_ok=True)
    metadata = splitFile(file_path, chunk_servers, chunk_size, master_key, temp_dir)
    writeJsonFile(metadata, os.path.join(temp_dir, f"{file_name}_metadata.json"))

    for chunk_info in metadata['chunks']:
        uploaded_to = set()
        logger.debug(f"Starting upload for chunk {chunk_info['chunk_index']}...")
        for replication_index in range(replication_factor):
            chunk_server = getChunkServer(chunk_info['chunk_index'], chunk_servers)
            while chunk_server['upload_url'] in uploaded_to:
                if len(uploaded_to) >= len(chunk_servers):
                    logger.warning("Not enough chunk servers for replication. Continuing without further replication.")
                    break
                chunk_info['chunk_index'] += 1
                chunk_server = getChunkServer(chunk_info['chunk_index'], chunk_servers)
            uploaded_to.add(chunk_server['upload_url'])

            files = {'file': open(chunk_info['chunk_path'], 'rb')}
            logger.debug(f"Uploading {chunk_info['chunk_path']} to {chunk_server['upload_url']} (replication {replication_index + 1}/{replication_factor})")
            try:
                response = requests.post(chunk_server['upload_url'], files=files, timeout=10)
                if response.status_code == 200:
                    logger.info(f"{chunk_info['chunk_path']} uploaded successfully to {chunk_server['upload_url']}.")
                else:
                    logger.error(f"Failed to upload {chunk_info['chunk_path']} to {chunk_server['upload_url']}. Status code: {response.status_code}")
                    logger.error(response.text)
                    return
            except requests.exceptions.RequestException as e:
                logger.error(f"Exception occurred while uploading {chunk_info['chunk_path']} to {chunk_server['upload_url']}: {e}")
                return
            finally:
                files['file'].close()

            time.sleep(1)  # Sleep for 1 second to ensure server processes each chunk properly

        # Remove the local chunk file after uploading
        os.remove(chunk_info['chunk_path'])
        logger.debug(f"{chunk_info['chunk_path']} removed locally after upload.")
        logger.debug(f"Chunk {chunk_info['chunk_index']} upload completed.")
    
    metadata_uploaded[file_name] = metadata
    save_metadata_uploaded()
    logger.debug("All chunks uploaded successfully.")


def download_file(file_name, chunk_servers):
    if file_name not in metadata_uploaded:
        logger.error(f"Metadata for file {file_name} not found in metadata_uploaded.")
        return
    
    metadata = metadata_uploaded[file_name]
    temp_dir = 'temp_chunks'
    os.makedirs(temp_dir, exist_ok=True)

    merged_file_path = os.path.join(temp_dir, file_name + '_merged')
    output_file_path = 'output/output.txt'
    if not os.path.exists('output'):
        os.makedirs('output')

    with open(merged_file_path, 'wb') as merged_file:
        for chunk_info in metadata['chunks']:
            chunk_server = getChunkServer(chunk_info['chunk_index'], chunk_servers)
            chunk_url = chunk_server['download_url'] + chunk_info['chunk_name']
            logger.debug(f"Downloading {chunk_info['chunk_name']} from {chunk_url}")
            try:
                response = requests.get(chunk_url, stream=True)
                if response.status_code == 200:
                    chunk_path = os.path.join(temp_dir, chunk_info['chunk_name'])
                    with open(chunk_path, 'wb') as chunk_file:
                        for chunk in response.iter_content(chunk_size=4096):
                            chunk_file.write(chunk)
                    logger.info(f"{chunk_info['chunk_name']} downloaded successfully from {chunk_server['download_url']}.")
                    
                    with open(chunk_path, 'rb') as chunk_file:
                        merged_file.write(chunk_file.read())
                else:
                    logger.error(f"Failed to download chunk {chunk_info['chunk_name']} from {chunk_server['download_url']}. Status code: {response.status_code}")
                    logger.error(response.text)
                    return
            except requests.exceptions.RequestException as e:
                logger.error(f"Exception occurred while downloading {chunk_info['chunk_name']} from {chunk_server['download_url']}: {e}")
                return

    # Merge and decrypt the merged file
    mergeChunks(metadata, temp_dir, output_file_path, master_key)
    
    logger.info(f"File '{file_name}' downloaded, merged, and decrypted successfully to {output_file_path}.")




def ensure_upload_list_dir():
    if not os.path.exists('upload_list'):
        os.makedirs('upload_list')
    logger.info("Please place all of your uploads in the upload_list directory.")

def list_files(directory):
    files = [file for file in os.listdir(directory) if not (file.endswith('.dat') or file.endswith('.json'))]
    for idx, file in enumerate(files, start=1):
        logger.info(f"{idx}. {file}")
    return files

def main():
    ensure_upload_list_dir()
    
    # Wait until the services are discovered
    while not listener.services:
        pass

    chunk_servers = listener.services

    while True:
        command = input("Enter command (1: upload, 2: download, 3: exit): ").strip()

        if command == "1":
            logger.info("Available files for upload:")
            files = list_files('upload_list')
            if not files:
                logger.info("No files available for upload.")
                continue
            file_index = int(input("Enter the number of the file to upload: ").strip()) - 1
            if 0 <= file_index < len(files):
                file_path = os.path.join('upload_list', files[file_index])
                upload_file(file_path, chunk_servers)
            else:
                logger.error("Invalid file number.")
        elif command == "2":
            logger.info("Available files for download:")
            files = list(metadata_uploaded.keys())
            if not files:
                logger.info("No files available for download.")
                continue
            for idx, file in enumerate(files, start=1):
                logger.info(f"{idx}. {file}")
            file_index = int(input("Enter the number of the file to download: ").strip()) - 1
            if 0 <= file_index < len(files):
                file_name = files[file_index]
                download_file(file_name, chunk_servers)
            else:
                logger.error("Invalid file number.")
        elif command == "3":
            break
        else:
            logger.error("Unknown command.")

if __name__ == "__main__":
    main()
    zeroconf.close()
