# Distributed File System (DFS) Project

This project is submitted as part of the Advanced Operating System (CS-501) course conducted at ITU, Lahore (Spring-2024).

**Course Instructor:** Dr. Khawaja Muhammad Umar Suleiman  
**TA:** Mr. Mubashir Rehman

**Submitted by:**  
i) HASSAN JAVAID, MSCS23001  
ii) SAAD BIN HAMMAD, MSCS23008

**Date of Submission:** May 31, 2024

===========================================================================================================================


## Sample video is included to display the working of components in two machines in a local network.

---

## Version Updates

- Implemented HTTPS server using python libraries Flask and Requests for connection in local area network.
- Implemented basic file upload and download functionalities.
- Added chunk replication factor of 2 for fault tolerance.
- Improved error handling and logging.
- Integrated Zeroconf for automatic service discovery in local area network
- Enhanced security with AES-256 encryption and SHA-256 hashing.
- Optimized chunk merging and decryption process.


## Roles of Components

### HTTP Server:
- Facilitates file upload and download operations between the main server and chunk servers.

### Socket Library:
- Uses `gethostbyname` to retrieve the local IP address, ensuring accurate network communication.

### Zeroconf Library:
- Enables automatic discovery of chunk servers on the network without manual configuration.

---

## Key Challenges

### Data Transmission via Chunks:
- Ensuring the integrity and order of data during transmission.
- Handling encryption and decryption efficiently.

### Service Discovery:
- Implementing reliable automatic service discovery using Zeroconf.

### Replication:
- Managing replication of chunks by a factor of 2 across multiple servers to ensure data availability and fault tolerance.

### Security:
- Implementing robust encryption and hashing mechanisms to protect data integrity and confidentiality.

### INSTRUCTIONS:

Navigate to the Project Directory:Open the terminal or command line.

1. Navigate to the project path folder (src in the source folder) and run the main server http_main_1.py, concurently on the same local network run the script http_chunk_1.py (the connection will be automatic and no configuration is needed)

2. You are to change the config file for the number of chunk servers depending on the number of local machines, (currently it works for a single chunk server, the functionality is added but it is yet to be tested.)

3. Currently has the functionalities 1) Upload: Uploads a file from the upload_list directory to chunk servers.
                                     2) Downloads and merges chunks into a complete file stored in the output directory.
                                     3) Exit: Exits the program.

4) ## Main Server (http_main_1.py)
    i) Service Discovery: Uses Zeroconf for discovering chunk servers.
    ii)Commands: Upload, Download, List, Exit.
    iii) File Upload:
    iv) Splits the file into chunks.
    v) Encrypts each chunk.
    vi) Uploads each chunk to chunk servers with replication.
    vii) Updates metadata after uploading.
    viii) File Download:
    ix) Retrieves metadata for the file.
    x) Downloads each chunk from chunk servers.
    xi) Decrypts and merges chunks into a complete file.

5) ## Chunk Server (http_chunk_1.py)
   i) Handle Upload: Receives file chunks from the main server.
   ii) Stores chunks in the chunks directory.
   iii) Handle Download: Sends requested chunks to the main server.
   iv) List Files: Lists all stored chunks in the chunks directory.


## Additional Information
Configuration: Configuration file (dfs_setup.config) contains important settings like master_key, chunk_size, and num_chunk_servers.
Security:Uses AES-256 CBC mode for encryption and uses SHA-256 for hashing.(main functionality of dfscontrol_copy.py file)
Metadata:Metadata for uploaded files is stored in metadata_uploaded.json.

