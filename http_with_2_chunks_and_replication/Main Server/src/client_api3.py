"""
###<u> **ADVANCED OPERATING SYSTEM PROJECT INTERMEDIATE SUBMISSION # 2 ** </u>
* **NAME = HASSAN JAVAID, SAAD BIN HAMMAD**
* **ROLL NO. = MSCS23001, MSCS23008**'
* **PROJECT_ABSTRACT =  Implementation of Distributed File System (DFS) with 
                        master-slave MapReduce file processing and client/server 
                        communicaiton**
* **DATE OF SUBMISSION = MAY 21, 2024**
"""


import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from tkinter import filedialog,simpledialog
import os
import platform
import subprocess
global ROOT_DIR
from dfscontrol import*
from http_server import*
import hashlib

# Define ROOT_DIR
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))


def connect_to_chunk_servers():
    try:
        num_chunk_servers_input = input("How many chunk servers would you like to connect? ").strip()
        if num_chunk_servers_input:
            try:
                num_chunk_servers = int(num_chunk_servers_input)
            except ValueError:
                print("Invalid input. Please enter an integer.")
                num_chunk_servers = 2
        else:
            print("No input provided. Using default value of 2 chunk servers.")
            num_chunk_servers = 2

        global chunk_servers
        chunk_servers = wait_for_chunk_servers(num_chunk_servers)
        print(f"Connected to {len(chunk_servers)} chunk servers.")
    except Exception as e:
        logger.error(f"Error connecting to chunk servers: {e}")


# Function to read the list of filenames from filename.txt file
def read_filenames():
    if os.path.exists(filenames_file):
        with open(filenames_file, "r") as file:
            return file.read().splitlines()
    else:
        return []



# Function to update the list of filenames in filename.txt file
def update_filenames(filename):
    with open(filenames_file, "a") as file:
        file.write(f"{filename}\n")




# Implements the User Command of Upload File
def uploadFile(file_path):
    
    print(f"Uploading file: {file_path}")
    fname = os.path.basename(file_path)
    print(fname)
    metadata_fn = f"{fname}_metadata_enc.json"
    metadata_file = os.path.join(ROOT_DIR, metadata_fn)
    encryption_key = get_encryption_key(fname)
    putFile(file_path, chunk_servers, chunk_size, encryption_key,metadata_file, 
            master_key_bytes, ROOT_DIR)
    status_var.set(f"File '{fname}' uploaded successfully.")




# Implements the User Command of Download File
def downloadFile(file_path, encryption_key):
    
    print(f"Downloading file: {file_path}")
    fname = os.path.basename(file_path)
    print(fname)
    metadata_fn = f"{fname}_metadata_enc.json"
    metadata_file = os.path.join(ROOT_DIR, metadata_fn)

    fname_without_extension = os.path.splitext(fname)[0]
    output_fn = fname_without_extension + "_rec.txt"
    output_folder_name =  "outputs" 
    output_folder = os.path.join(ROOT_DIR, output_folder_name)     
    output_file = os.path.join(ROOT_DIR, output_folder_name, output_fn)

    if not os.path.exists(metadata_file):
        print("Invalid filename and/or Metadata file not found.")
        print("Exiting program....")
        print()
        status_var.set("Invalid filename and/or Metadata file not found. Download Cancelled..")
        return

    getFile(metadata_file, output_file, encryption_key, master_key_bytes, ROOT_DIR)
    status_var.set(f"File '{fname}' downloaded to folder {output_folder_name} as {output_fn} successfully.")
    openFolder(output_folder)
    
    # Compare checksums to verify file integrity of merged and input
    input_file = file_path
    input_checksum = generateChecksum(input_file)
    merged_checksum = generateChecksum(output_file)

    if input_checksum == merged_checksum:
        messagebox.showinfo("Checksum", "File integrity verified: Input and merged files are the same.")
        print("File integrity verified: Input and merged files are the same.")
        print()
    else:
        messagebox.showinfo("Checksum", "File integrity check failed: Input and merged files are different.")
        print("File integrity check failed: Input and merged files are different.")
        print()




# Implements to display the list of files in user_file_repo and select one for downloading
def list_files_for_download(directory):
    def open_list_window():
        def on_select(event):
            try:
                selected_file = listbox.get(listbox.curselection())
                file_path = os.path.join(directory, selected_file)
                encryption_key = get_encryption_key(selected_file)
                if encryption_key:
                    status_var.set(f"Status: Downloading {os.path.basename(file_path)}")
                    messagebox.showinfo("Action", f"Downloading {os.path.basename(file_path)}")
                    downloadFile(file_path, encryption_key)
                else:
                    status_var.set(f"Status: Encryption key not found for {os.path.basename(file_path)}")
                    messagebox.showwarning("Action", f"Encryption key not found for {os.path.basename(file_path)}")
                list_window.destroy()
                
            except tk.TclError:
                status_var.set("Status: No file selected. Download cancelled")
                messagebox.showwarning("Action", "No file selected. Download cancelled")


        list_window = tk.Toplevel()
        list_window.title("File List")

        scrollbar = tk.Scrollbar(list_window)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        listbox = tk.Listbox(list_window, yscrollcommand=scrollbar.set)
        listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        files = os.listdir(directory)
        for file in files:
            listbox.insert(tk.END, file)

        scrollbar.config(command=listbox.yview)

        listbox.bind('<<ListboxSelect>>', on_select)

    open_list_window()




# Implements function to open the output folder in the file explorer
def openFolder(path):
    if platform.system() == "Windows":
        os.startfile(path)
    elif platform.system() == "Darwin":  # macOS
        subprocess.Popen(["open", path])
    else:  # Linux
        subprocess.Popen(["xdg-open", path])




# Implements function to display the list of files in a specified directory
def listFiles(directory):
    def open_list_window():
        list_window = tk.Toplevel()
        list_window.title("File List")
        
        scrollbar = tk.Scrollbar(list_window)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        listbox = tk.Listbox(list_window, yscrollcommand=scrollbar.set)
        listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        files = os.listdir(directory)
        for file in files:
            listbox.insert(tk.END, file)

        scrollbar.config(command=listbox.yview)

    open_list_window()


# Implements function to generate and save an encryption key
def save_encryption_key(filename):
    encryption_key = get_random_bytes(32)
    with open(enc_config_fn, "a") as file:
        file.write(f"{filename}:{encryption_key.hex()}\n")
    print(f"Encryption key for {filename} saved.")


# Implements function to retrieve an encryption key for a given filename
def get_encryption_key(filename):
    if not os.path.exists(enc_config_fn):
        return None
    
    with open(enc_config_fn, "r") as file:
        lines = file.readlines()
        for line in lines:
            file_name, key_hex = line.strip().split(":")
            if file_name == filename:
                return bytes.fromhex(key_hex)
    return None


# Implements callback when upload button is pressed
def uploadAction():
    file_path = filedialog.askopenfilename(
        title="Select a file to upload",
        filetypes=(("Text files", "*.txt"), ("All files", "*.*")),
        initialdir=os.path.join(ROOT_DIR, "user_file_repo")
    )
    if file_path:
        file_name = os.path.basename(file_path)
        uploaded_files = read_filenames()
        if file_name not in uploaded_files:
            update_filenames(file_name)
            save_encryption_key(file_name)
        else:
            status_var.set(f"Status: File {file_name} already uploaded")
            messagebox.showwarning("Action", f"File {file_name} already uploaded")
            return
        status_var.set(f"Status: Uploading {os.path.basename(file_path)}")
        uploadFile(file_path)
    else:
        status_var.set("Status: Upload cancelled")



# Implements callback when download button is pressed
def downloadAction():
    directory = os.path.join(ROOT_DIR, "user_file_repo")
    os.makedirs(directory, exist_ok=True)
    status_var.set("Status: Listing files for download")
    list_files_for_download(directory)



# Implements callback when list button is pressed
def listAction():
    directory = os.path.join(ROOT_DIR, "user_file_repo")
    os.makedirs(directory, exist_ok=True)
    status_var.set("Status: List button pressed")
    # messagebox.showinfo("Action", "Listing files")
    listFiles(directory)


# Implementation is another file, will integrate it in main source in the next phase 
def connect_action():
    try:
        num_chunk_servers_input = tk.simpledialog.askstring("Input", "How many chunk servers would you like to connect?", initialvalue="2")
        if num_chunk_servers_input:
            try:
                num_chunk_servers = int(num_chunk_servers_input)
            except ValueError:
                tk.messagebox.showerror("Error", "Invalid input. Please enter an integer.")
                num_chunk_servers = 2
        else:
            num_chunk_servers = 2

        global chunk_servers
        chunk_servers = wait_for_chunk_servers(num_chunk_servers)
        if chunk_servers:
            status_var.set(f"Connected to {len(chunk_servers)} chunk servers.")
            upload_button.config(state=tk.NORMAL)
            download_button.config(state=tk.NORMAL)
            connect_button.config(state=tk.DISABLED)
            disconnect_button.config(state=tk.NORMAL)
        else:
            status_var.set("Failed to connect to chunk servers.")
    except Exception as e:
        logger.error(f"Error connecting to chunk servers: {e}")
        status_var.set(f"Error connecting to chunk servers: {e}")



# Implementation is another file, will integrate it in main source in the next phase 
def disconnect_action():
    status_var.set("Status: Disconnect button pressed")
    messagebox.showinfo("Action", "Disconnect button pressed")

def upload_file_to_chunk_servers(file_path, chunk_servers, chunk_size, master_key, replication_factor):
    try:
        # Call your upload function here
        upload_file(file_path, chunk_servers, chunk_size, master_key, replication_factor)
        logger.info(f"File {file_path} uploaded successfully to chunk servers.")
    except Exception as e:
        logger.error(f"Error uploading file to chunk servers: {e}")

# Implements function to create the main window
# Implements function to create the main window
# Implements function to create the main window
# Implements function to create the main window
# Implements function to create the main window
def create_main_window():
    global root, upload_button, download_button, list_button, connect_button, disconnect_button, status_var

    root = tk.Tk()
    root.title("My Drive")
    root.geometry("600x550")

    # Set the window icon
    # root.iconbitmap('path_to_your_icon.ico') 

    # Create a main label
    main_label = tk.Label(root, text="My Drive", font=("Arial Bold", 24))
    main_label.pack(pady=20)

    commands_frame = tk.LabelFrame(root, text="Commands", padx=10, pady=10)
    commands_frame.pack(pady=10)

    upload_button = ttk.Button(commands_frame, text="Upload", command=on_upload_button_click, state=tk.DISABLED)
    upload_button.pack(side=tk.LEFT, padx=5)

    download_button = ttk.Button(commands_frame, text="Download", command=on_download_button_click, state=tk.DISABLED)
    download_button.pack(side=tk.LEFT, padx=5)

    list_button = ttk.Button(commands_frame, text="List", command=listAction, state=tk.DISABLED)
    list_button.pack(side=tk.LEFT, padx=5)

    connect_frame = tk.Frame(root)
    connect_frame.pack(pady=10)

    connect_button = ttk.Button(connect_frame, text="Connect", command=connect_action)
    connect_button.pack(side=tk.LEFT, padx=10)

    disconnect_button = ttk.Button(connect_frame, text="Disconnect", command=disconnect_action, state=tk.DISABLED)
    disconnect_button.pack(side=tk.LEFT, padx=10)

    # Create a status bar
    global status_var
    status_var = tk.StringVar()
    status_var.set("Status: Ready. Press 'Connect' to enter credentials.")
    status_bar = tk.Label(root, textvariable=status_var, font=("Arial", 10), relief=tk.SUNKEN, anchor=tk.W)
    status_bar.pack(side=tk.BOTTOM, fill=tk.X)

    # Create a bottom label
    bottom_label = tk.Label(root, text="Created by MSCS23001 & MSCS23008 as part of Adv OS Project", font=("Arial Bold", 9))
    bottom_label.pack(side=tk.BOTTOM, pady=5)

    root.mainloop()

# Read metadata from metadata_uploaded.json
def read_metadata_uploaded(file_path):
    try:
        with open(file_path, 'r') as file:
            data = json.load(file)
        return data
    except Exception as e:
        logger.error(f"Error reading metadata file {file_path}: {e}")
        return {}

# Starts the API
if __name__ == "__main__":
    import tkinter as tk
    from tkinter import ttk, filedialog, simpledialog
    from http_server import *

    # Define filenames_file
    filenames_file = os.path.join(ROOT_DIR, 'src', 'filenames.json')

    # Read configuration settings
    config_file_path = r"C:\Users\saadh\OneDrive\Desktop\My-Drive-Implementation-http-server\Project Submission # 3\src\dfs_setup.config"
    config = readConfigFile(config_file_path)
    chunk_size = int(config['chunk_size'])
    num_chunk_servers = int(config['num_chunk_servers'])
    master_key = bytes.fromhex(config['master_key'])
    replication_factor = 2  # As required

    # Global variable to store connected chunk servers
    global chunk_servers
    chunk_servers = []

    # Connect to chunk servers
    connect_to_chunk_servers()

    # Define functions to handle upload and download actions

    def on_upload_button_click():
        file_path = filedialog.askopenfilename(initialdir=os.path.join(ROOT_DIR, "upload_list"), title="Select file")
        if file_path:
            upload_file_to_chunk_servers(file_path, chunk_servers, chunk_size, master_key, replication_factor)

    def on_download_button_click():
        metadata_file_path = r'C:\Users\saadh\OneDrive\Desktop\My-Drive-Implementation-http-server\Project Submission # 3\metadata_uploaded.json'
        metadata = read_metadata_uploaded(metadata_file_path)

        if metadata:
            file_names = list(metadata.keys())
            if file_names:
                def select_file():
                    selected_file = listbox.get(tk.ACTIVE)
                    if selected_file:
                        output_path = filedialog.asksaveasfilename(initialdir=os.path.join(ROOT_DIR, "outputs", "saad"), title="Save file as", initialfile=selected_file)
                        if output_path:
                            download_file_from_chunk_servers(selected_file, output_path, chunk_servers, master_key)
                        download_window.destroy()
                    else:
                        print("No file selected.")

                download_window = tk.Toplevel(root)
                download_window.title("Select file to download")
                download_window.geometry("300x300")

                listbox = tk.Listbox(download_window, selectmode=tk.SINGLE)
                for file_name in file_names:
                    listbox.insert(tk.END, file_name)
                listbox.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

                select_button = tk.Button(download_window, text="Download", command=select_file)
                select_button.pack(pady=10)
            else:
                print("No files available in metadata.")
        else:
            print("No metadata found or metadata is empty.")

    # Create the main window
    create_main_window()

    # Start the main GUI loop
    tk.mainloop()
