"""
###<u> **ADVANCED OPERATING SYSTEM PROJECT INTERMEDIATE SUBMISSION # 1 ** </u>
* **NAME = HASSAN JAVAID, SAAD BIN HAMMAD**
* **ROLL NO. = MSCS23001, MSCS23008**'
* **PROJECT_ABSTRACT =  Implementation of Distributed File System (DFS) with 
                        master-slave MapReduce file processing and client/server 
                        communicaiton**
* **DATE OF SUBMISSION = MAY 14, 2024**
"""


import os
import json
import hashlib
from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes
from Crypto.Util.Padding import pad, unpad


# Implements the creation of output folder which represent our chunk server VMs at this stage
def getChunkServer(chunk_identifier, chunk_servers):
    # Use a cryptographic hash function (e.g., SHA-256) to hash the chunk identifier
    # and map it to one of the output folders
    hash_value = hash(chunk_identifier) % len(chunk_servers)
    return chunk_servers[hash_value]


# Implements the encryption of file chunk. AES-256 CBC mode.
def encryptChunk(chunk_data, key):
    iv = get_random_bytes(16)
    cipher = AES.new(key, AES.MODE_CBC, iv)
    padded_data = chunk_data + b'\0' * (16 - len(chunk_data) % 16)    
    encrypted_data = cipher.encrypt(padded_data)
    
    return iv + encrypted_data


# Implements the decryption of file chunk. AES-256 CBC mode.
def decryptChunk(encrypted_chunk, key):
    iv = encrypted_chunk[:16]    
    cipher = AES.new(key, AES.MODE_CBC, iv)   
    decrypted_data = cipher.decrypt(encrypted_chunk[16:])
    
    return decrypted_data.rstrip(b'\0')


# Implements file encryption. AES-256 CBC mode.
def encryptFile(file_path, key):
    with open(file_path, 'rb') as f:
        file_data = f.read()

    iv = get_random_bytes(AES.block_size)
    cipher = AES.new(key, AES.MODE_CBC, iv)
    encrypted_data = cipher.encrypt(pad(file_data, AES.block_size))

    with open(file_path, 'wb') as f:
        f.write(iv + encrypted_data)



# Implements file decryption. AES-256 CBC mode.
def decryptFile(file_path, key):
    with open(file_path, 'rb') as f:
        iv = f.read(AES.block_size)
        encrypted_data = f.read()

    cipher = AES.new(key, AES.MODE_CBC, iv)
    decrypted_data = cipher.decrypt(encrypted_data)
    unpadded_data = unpad(decrypted_data, AES.block_size)

    return unpadded_data



# Implements the splitting of file into chunks, encrypt them, and store in output folders.
# Also create a metadata file to track chunk storage locations.
def splitFile(file_path, chunk_servers, chunk_size, encryption_key, ROOT_DIR):
    # Create output folders if they don't exist
    for server in chunk_servers:
        os.makedirs(os.path.join(ROOT_DIR, server), exist_ok=True)
    
    total_chunks = (os.path.getsize(file_path) + chunk_size - 1) // chunk_size
    
    metadata = {
        "file_name": os.path.basename(file_path),
        "chunks": []
    }
    
    with open(file_path, "rb") as f:
        for i in range(total_chunks):
            chunk_data = f.read(chunk_size)
            chunk_index = i
            
            encrypted_chunk = encryptChunk(chunk_data, encryption_key)
            
            chunk_server = getChunkServer(str(chunk_index), chunk_servers)
            
            chunk_filename = f"chunk_{chunk_index}.dat"
            chunk_path = os.path.join(ROOT_DIR, chunk_server, chunk_filename)
            with open(chunk_path, "wb") as chunk_file:
                chunk_file.write(encrypted_chunk)
            
            metadata["chunks"].append({
                "chunk_index": chunk_index,
                "chunk_server": chunk_server,
                "chunk_path": chunk_path
            })
    
    return metadata


# Reads a JSON file and returns its contents.
def read_json_file(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            data = json.load(file)
        return data
    except FileNotFoundError:
        print(f"The file {file_path} was not found.")
        return None
    except json.JSONDecodeError:
        print(f"Error decoding JSON from the file {file_path}.")
        return None
    except Exception as e:
        print(f"An error occurred: {e}")
        return None


def save_to_text_file(data, file_path):
    """
    Saves data to a text file.
    
    Parameters:
    data (str): The data to be saved to the file.
    file_path (str): The path to the text file.
    
    Returns:
    bool: True if the data was successfully written to the file, False otherwise.
    """
    try:
        with open(file_path, 'w', encoding='utf-8') as file:
            file.write(data)
        return True
    except Exception as e:
        print(f"An error occurred while writing to the file: {e}")
        return False



# Implements the merging of encrypted file chunks using metadata file and create a new merged file.
def mergeChunks(metadata_file, output_file, encryption_key, master_key, ROOT_DIR):
    # Decrypt the metadata file using the master key
    decrypted_metadata = decryptFile(metadata_file, master_key)
 
    metadata = json.loads(decrypted_metadata)
    decrypted_chunks = []
    
    for chunk_info in metadata["chunks"]:
        with open(chunk_info["chunk_path"], "rb") as chunk_file:
            encrypted_chunk = chunk_file.read()
        decrypted_chunk = decryptChunk(encrypted_chunk, encryption_key)
        decrypted_chunks.append(decrypted_chunk)
    
    with open(output_file, "wb") as output_f:
        for chunk in decrypted_chunks:
            output_f.write(chunk)
    
 


# Implements the generation a SHA-256 checksum for the given file.
def generateChecksum(file_path):
    sha256 = hashlib.sha256()

    # Read the content of the file and update the hash
    with open(file_path, 'rb') as f:
        while True:
            data = f.read(65536)  # Read data in chunks
            if not data:
                break
            sha256.update(data)

    return sha256.hexdigest()



# Implements the reading of configuration parameters from the config file.
def readConfigFile(config_file):
    config = {}
    with open(config_file, 'r') as f:
        for line in f:
            name, value = line.strip().split(' ', 1)
            config[name] = value
    return config



# Implements the creation of a list of output folders with the specified number.
def createChunkServers(num_chunk_servers):
    chunk_servers = []
    for i in range(1, num_chunk_servers + 1):
        folder_name = f"chunk_server_{i}"
        chunk_servers.append(folder_name)
    return chunk_servers



# User Command Function to list all text files in the main drive directory
def listFiles(file_path):
    files = [file for file in os.listdir(file_path) if file.endswith(".txt")]
    print("Text files in the user drive directory:")
    for file in files:
        print(file)


# Writes metadata dictionary object to a JSON file.
def writeJsonFile(data, file_path):
    try:
        with open(file_path, 'w', encoding='utf-8') as file:
            json.dump(data, file, indent=4)
        return True
    except Exception as e:
        print(f"An error occurred while writing to the file: {e}")
        return False


# User Command Function to store a file into output folders
def putFile(file_path, chunk_servers, chunk_size, encryption_key, metadata_file, master_key_bytes, ROOT_DIR):
    print(f"Reading input file from: {file_path}")
    print()
    
    metadata = splitFile(file_path, chunk_servers, chunk_size, encryption_key, ROOT_DIR)
    
    writeJsonFile(metadata, metadata_file)

    # Encrypt the metadata file using the master key
    encryptFile(metadata_file, master_key_bytes)
    
    print("File split and encrypted chunks stored in chunk servers.")
    print()




# User Command Function to retrieve the merged file and store it in a folder named as user
def getFile(metadata_file, output_file, encryption_key, master_key_bytes, ROOT_DIR):
    print(f"Merged file will be placed at: {output_file}")
    print()
    mergeChunks(metadata_file, output_file, encryption_key, master_key_bytes, ROOT_DIR)
    print("Merged file created successfully.")
    print()



# Main function to handle user input
def main():

    global ROOT_DIR
    
    
    # Automatically set ROOT_DIR to the directory of the current script
    ROOT_DIR = os.path.abspath(os.path.dirname(__file__))

    print(f"ROOT_DIR is set to: {ROOT_DIR}")


    main_server_folder = "main_server"
    main_server_path = os.path.join(ROOT_DIR, main_server_folder)
    
    user_folder = "user_file_repo"
    user_folder_path = os.path.join(ROOT_DIR, user_folder)
    
    chunk_server = "outputs"
    output_folder_path = os.path.join(ROOT_DIR, chunk_server)
    
    config_fn = "dfs_setup.config"
    config_file = os.path.join(ROOT_DIR, main_server_folder, config_fn)
    config = readConfigFile(config_file)

    # Extract parameters from the config dictionary
    chunk_size = int(config.get("chunk_size"))
    num_chunk_servers = int(config.get("num_chunk_servers"))
    master_key = config.get("master_key")
    # print(master_key)
    num_map_workers = int(config.get("num_map_workers"))
    
    # Create chunk servers. 
    # At this stage the directory folders represent chunk servers and hold chunk data of input file
    chunk_servers = createChunkServers(num_chunk_servers)
    
    # Generate encryption key for file encryption
    encryption_key = get_random_bytes(32)  # AES-256 requires a 256-bit (32-byte) key
    master_key_bytes = bytes.fromhex(master_key)
    

    
    while True:
        # Prompt user for input
        command = input("Enter command [put, list, get] or 'exit' to quit: ").strip().lower()
        print()
    
        if command == "put":
            put_filename = input("Enter the filename to store into chunk servers: ")
            print()
            input_file = os.path.join(ROOT_DIR, user_folder, put_filename)
            
            if not os.path.exists(input_file):
                print("Invalid filename and/or file does not exist.")
                print("Exiting program....")
                print()
                break
            
            putFile(input_file, chunk_servers, chunk_size, encryption_key, master_key_bytes, main_server_folder, ROOT_DIR)
            print()
        
        elif command == "list":
            listFiles(user_folder_path)
            print()
        
        
        elif command == "get":
            get_filename = input("Enter the filename you want to retrieve from DFS: ")
            print()
            # file_path = os.path.join(ROOT_DIR, main_server_folder, get_filename)
            
            metadata_fn = f"{get_filename}_metadata.json"
            metadata_file = os.path.join(ROOT_DIR, main_server_folder, metadata_fn)

            output_fn = "merged_file.txt"        
            output_file = os.path.join(ROOT_DIR, chunk_server, output_fn)

            if not os.path.exists(metadata_file):
                print("Invalid filename and/or Metadata file not found.")
                print("Exiting program....")
                print()
                break
            
            getFile(metadata_file, output_file, encryption_key, master_key_bytes)
            print()

            # Compare checksums to verify file integrity of merged and input
            input_checksum = generateChecksum(input_file)
            merged_checksum = generateChecksum(output_file)

            if input_checksum == merged_checksum:
                print("File integrity verified: Input and merged files are the same.")
                print()
            else:
                print("File integrity check failed: Input and merged files are different.")
                print()
        
        elif command == "exit":
            print("Exiting program successfully.")
            print()
            break
        
        
        else:
            print("Invalid command. Please try again.")
            print()

if __name__ == "__main__":
    main()
