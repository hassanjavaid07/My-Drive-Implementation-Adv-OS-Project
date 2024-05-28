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
from tkinter import filedialog
import os
import platform
import subprocess
global ROOT_DIR
from dfscontrol import*
    


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
    status_var.set("Status: Connect button pressed")
    messagebox.showinfo("Action", "Connect button pressed")


# Implementation is another file, will integrate it in main source in the next phase 
def disconnect_action():
    status_var.set("Status: Disconnect button pressed")
    messagebox.showinfo("Action", "Disconnect button pressed")


# Implements function to create the main window
def create_main_window():
    root = tk.Tk()
    root.title("My Drive")

    root.geometry("550x500")

    main_label = tk.Label(root, text="My Drive", font=("Arial Bold", 24))
    main_label.pack(pady=20)

    commands_frame = tk.LabelFrame(root, text="Commands", padx=10, pady=10)
    commands_frame.pack(pady=10)

    upload_button = ttk.Button(commands_frame, text="Upload", command=uploadAction)
    upload_button.pack(side=tk.LEFT, padx=5)

    download_button = ttk.Button(commands_frame, text="Download", command=downloadAction)
    download_button.pack(side=tk.LEFT, padx=5)

    list_button = ttk.Button(commands_frame, text="List", command=listAction)
    list_button.pack(side=tk.LEFT, padx=5)

    connect_frame = tk.Frame(root)
    connect_frame.pack(pady=10)

    connect_button = ttk.Button(connect_frame, text="Connect", command=connect_action)
    connect_button.pack(side=tk.LEFT, padx=10)

    disconnect_button = ttk.Button(connect_frame, text="Disconnect", command=disconnect_action)
    disconnect_button.pack(side=tk.LEFT, padx=10)

    global status_var
    status_var = tk.StringVar()
    status_var.set("Status: Ready")
    status_bar = tk.Label(root, textvariable=status_var, font=("Arial", 10), relief=tk.SUNKEN, anchor=tk.W)
    status_bar.pack(side=tk.BOTTOM, fill=tk.X)

    bottom_label = tk.Label(root, text="Created by: MSCS23001 (Hassan) & MSCS23008 (Saad) as part of Adv OS Project", font=("Arial Bold", 9))
    bottom_label.pack(side=tk.BOTTOM, pady=5)

    root.mainloop()

# Starts the API
if __name__ == "__main__":

    # Automatically set ROOT_DIR to the directory of the current script
    ROOT_DIR = os.path.abspath(os.path.dirname(__file__))
    print(f"ROOT_DIR is set to: {ROOT_DIR}")

    
    # Setup config files, enc_file, master key & create chunkservers
    config_fn = "dfs_setup.config"
    config_file = os.path.join(ROOT_DIR, config_fn)
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

    # Encryption key handling for file encryption
    global enc_config_fn
    enc_config_fn = os.path.join(ROOT_DIR, "enc_key.config")
    global master_key_bytes
    master_key_bytes = bytes.fromhex(master_key)
    
    global filenames_file
    filenames_file = os.path.join(ROOT_DIR, "filenames.txt")
    
    create_main_window()
