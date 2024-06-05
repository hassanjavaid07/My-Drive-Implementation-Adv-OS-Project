import os
import json
import requests
import warnings
import logging
import time
import socket
from zeroconf import Zeroconf, ServiceBrowser
from dfscontrol_copy import readConfigFile, getChunkServer, splitFile, mergeChunks, encryptChunk, decryptChunk, writeJsonFile, generateChecksum, decryptFile
import sys
import os
import requests
import logging


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
            logger.info(f"Chunk server added: {address}:{info.port}")
            logger.info(f"Currently connected chunk servers: {len(self.services)}")

zeroconf = Zeroconf()
listener = MyListener()
browser = ServiceBrowser(zeroconf, "_http._tcp.local.", listener)

config_file_path = 'src\dfs_setup.config'

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

metadata_uploaded_file = "metadata_uploaded.json"
metadata_uploaded = {}

def read_metadata_uploaded(file_path):
    try:
        with open(file_path, 'r') as file:
            data = json.load(file)
        return data
    except Exception as e:
        logger.error(f"Error reading metadata file {file_path}: {e}")
        return {}

# Load existing metadata if available
if os.path.exists(metadata_uploaded_file):
    with open(metadata_uploaded_file, 'r') as f:
        metadata_uploaded = json.load(f)

def save_metadata_uploaded():
    with open(metadata_uploaded_file, 'w') as f:
        json.dump(metadata_uploaded, f, indent=4)

def readJsonFile(file_path):
    try:
        with open(file_path, 'r') as file:
            data = json.load(file)
        return data
    except Exception as e:
        logger.error(f"Error reading JSON file {file_path}: {e}")
        return None



def upload_file(file_path, chunk_servers, chunk_size, master_key, replication_factor):
    file_name = os.path.basename(file_path)
    temp_dir = 'temp_chunks'
    os.makedirs(temp_dir, exist_ok=True)
    metadata = splitFile(file_path, chunk_servers, chunk_size, master_key, temp_dir)
    writeJsonFile(metadata, os.path.join(temp_dir, f"{file_name}_metadata.json"))

    for chunk_info in metadata['chunks']:
        uploaded_to = set()
        print(f"Starting upload for chunk {chunk_info['chunk_index']}...")
        for replication_index in range(replication_factor):
            chunk_server = getChunkServer(chunk_info['chunk_index'], chunk_servers)
            while chunk_server['upload_url'] in uploaded_to:
                if len(uploaded_to) >= len(chunk_servers):
                    print("Not enough chunk servers for replication. Continuing without further replication.")
                    break
                chunk_info['chunk_index'] += 1
                chunk_server = getChunkServer(chunk_info['chunk_index'], chunk_servers)
            uploaded_to.add(chunk_server['upload_url'])

            files = {'file': open(chunk_info['chunk_path'], 'rb')}
            print(f"Uploading {chunk_info['chunk_path']} to {chunk_server['upload_url']} (replication {replication_index + 1}/{replication_factor})")
            try:
                response = requests.post(chunk_server['upload_url'], files=files, timeout=10)
                if response.status_code == 200:
                    print(f"{chunk_info['chunk_path']} uploaded successfully to {chunk_server['upload_url']}.")
                else:
                    print(f"Failed to upload {chunk_info['chunk_path']} to {chunk_server['upload_url']}. Status code: {response.status_code}")
                    return
            except requests.exceptions.RequestException as e:
                print(f"Exception occurred while uploading {chunk_info['chunk_path']} to {chunk_server['upload_url']}: {e}")
                return
            finally:
                files['file'].close()

            time.sleep(1)  # Sleep for 1 second to ensure server processes each chunk properly

        # Remove the local chunk file after uploading
        os.remove(chunk_info['chunk_path'])
        print(f"{chunk_info['chunk_path']} removed locally after upload.")
        print(f"Chunk {chunk_info['chunk_index']} upload completed.")
    
    metadata_uploaded[file_name] = metadata
    save_metadata_uploaded()
    print("All chunks uploaded successfully.")


def download_file_from_chunk_servers(file_name, output_path, chunk_servers, master_key):
    metadata_file_path = 'C:\\Users\\saadh\\OneDrive\\Desktop\\My-Drive-Implementation-Adv-OS-Project\\Project Submission # 3\\metadata_uploaded.json'
    metadata_uploaded = readJsonFile(metadata_file_path)

    if file_name not in metadata_uploaded:
        logger.error(f"No metadata found for file {file_name}")
        print(f"Invalid file name or file not found in metadata.")
        return

    metadata = metadata_uploaded[file_name]
    decrypted_chunks = []

    for chunk_info in metadata["chunks"]:
        chunk_downloaded = False
        for chunk_server in chunk_servers:
            url = f"{chunk_server['download_url']}/{chunk_info['chunk_name']}"
            try:
                response = requests.get(url, stream=True, timeout=10)
                if response.status_code == 200:
                    chunk_data = response.content
                    decrypted_chunk = decryptChunk(chunk_data, master_key)
                    decrypted_chunks.append(decrypted_chunk)
                    chunk_downloaded = True
                    print(f"Chunk {chunk_info['chunk_index']} downloaded successfully from {url}")
                    break
                else:
                    print(f"Failed to download chunk {chunk_info['chunk_index']} from {url}. Status code: {response.status_code}")
            except requests.exceptions.RequestException as e:
                print(f"Exception occurred while downloading chunk {chunk_info['chunk_index']} from {url}: {e}")

        if not chunk_downloaded:
            print(f"Failed to download chunk {chunk_info['chunk_index']} from all chunk servers.")
            return

    with open(output_path, "wb") as output_f:
        for chunk in decrypted_chunks:
            output_f.write(chunk)

    print(f"File {file_name} downloaded successfully to {output_path}.")





def download_file(file_name, chunk_servers):
    if file_name not in metadata_uploaded:
        logger.error(f"Metadata for file {file_name} not found in metadata_uploaded.")
        return
    
    metadata = metadata_uploaded[file_name]
    temp_dir = 'temp_chunks'
    os.makedirs(temp_dir, exist_ok=True)
    output_file_path = os.path.join('output', 'output.txt')

    if not os.path.exists('output'):
        os.makedirs('output')

    # Download chunks
    for chunk_info in metadata['chunks']:
        chunk_downloaded = False
        for chunk_server in chunk_servers:
            chunk_url = chunk_server['download_url'] + os.path.basename(chunk_info['chunk_path'])
            logger.debug(f"Trying to download {chunk_info['chunk_path']} from {chunk_url}")
            try:
                response = requests.get(chunk_url, stream=True)
                if response.status_code == 200:
                    chunk_file_path = os.path.join(temp_dir, chunk_info['chunk_name'])
                    with open(chunk_file_path, 'wb') as chunk_file:
                        for chunk in response.iter_content(chunk_size=4096):
                            chunk_file.write(chunk)
                    logger.info(f"{chunk_info['chunk_path']} downloaded successfully from {chunk_server['download_url']}.")
                    chunk_downloaded = True
                    break  # Exit the loop if the chunk is successfully downloaded
                else:
                    logger.warning(f"Failed to download chunk {chunk_info['chunk_path']} from {chunk_server['download_url']}. Status code: {response.status_code}")
                    logger.warning(response.text)
            except requests.exceptions.RequestException as e:
                logger.warning(f"Exception occurred while downloading {chunk_info['chunk_path']} from {chunk_server['download_url']}: {e}")

        if not chunk_downloaded:
            logger.error(f"Failed to download chunk {chunk_info['chunk_path']} from all chunk servers.")
            return  # Exit the function if a chunk could not be downloaded

    # Merge and decrypt chunks
    mergeChunks(metadata, temp_dir, output_file_path, master_key)

    logger.info(f"File '{file_name}' downloaded and merged successfully.")


def ensure_upload_list_dir():
    if not os.path.exists('upload_list'):
        os.makedirs('upload_list')
    logger.info("Please place all of your uploads in the upload_list directory.")

def list_files(directory):
    files = [file for file in os.listdir(directory) if not (file.endswith('.dat') or file.endswith('.json'))]
    for idx, file in enumerate(files, start=1):
        logger.info(f"{idx}. {file}")
    return files


def wait_for_chunk_servers(num_chunk_servers):
    zeroconf = Zeroconf()
    listener = MyListener()
    browser = ServiceBrowser(zeroconf, "_http._tcp.local.", listener)

    logger.info(f"Waiting for {num_chunk_servers} chunk servers to connect...")
    while len(listener.services) < num_chunk_servers:
        time.sleep(1)

    chunk_servers = listener.services[:num_chunk_servers]
    logger.info(f"Connected to {num_chunk_servers} chunk servers.")
    return chunk_servers

def main():
    ensure_upload_list_dir()
    
    # Wait until the services are discovered
    while not listener.services:
        pass

    chunk_servers = listener.services

    # Prompt user for the number of chunk servers
    while True:
        try:
            num_chunk_servers = int(input("How many chunk servers would you like to connect? ").strip())
            break
        except ValueError:
            print("Invalid input. Please enter a valid integer.")
    
    wait_for_chunk_servers(num_chunk_servers)
    
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

