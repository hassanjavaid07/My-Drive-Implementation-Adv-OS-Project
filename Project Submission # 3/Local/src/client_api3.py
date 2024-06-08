"""
###<u> **ADVANCED OPERATING SYSTEM PROJECT INTERMEDIATE SUBMISSION # 3 ** </u>
* **NAME = HASSAN JAVAID, SAAD BIN HAMMAD**
* **ROLL NO. = MSCS23001, MSCS23008**'
* **PROJECT_ABSTRACT =  Implementation of Distributed File System (DFS) with 
                        master-slave file processing and client/server 
                        communicaiton**
* **DATE OF SUBMISSION = JUNE 07, 2024**
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

metadata_folder = "metadata"
# authenticated_user = None



# Implements user login and user authentication 
def connect_action():
    def authenticate():
        nonlocal attempts_left
        username = username_entry.get()
        password = password_entry.get()
        hashed_password = hashlib.sha256(password.encode()).hexdigest()
        if username in credentials and credentials[username] == hashed_password:
            global authenticated_user
            authenticated_user = username
            welcome_message = f"Welcome, {authenticated_user}"
            messagebox.showinfo("Success", welcome_message)
            status_var.set(f"Status: {welcome_message}")
            connect_window.destroy()
            enable_buttons()
            connect_button.config(state=tk.DISABLED)
        else:
            attempts_left -= 1
            if attempts_left == 0:
                messagebox.showerror("Error", "Max login attempts reached. Try again.")
                connect_window.destroy()
            else:
                status_var.set(f"Status: Invalid credentials. {attempts_left} login attempts remaining")

    # Read user config file
    global num_users
    credentials, num_users = read_user_config(user_config_file)
    attempts_left = 3

    connect_window = tk.Toplevel()
    connect_window.title("Login")

    tk.Label(connect_window, text="Username:").grid(row=0, column=0, padx=10, pady=5)
    username_entry = tk.Entry(connect_window)
    username_entry.grid(row=0, column=1, padx=10, pady=5)

    tk.Label(connect_window, text="Password:").grid(row=1, column=0, padx=10, pady=5)
    password_entry = tk.Entry(connect_window, show="*")
    password_entry.grid(row=1, column=1, padx=10, pady=5)

    login_button = tk.Button(connect_window, text="Login", command=authenticate)
    login_button.grid(row=2, columnspan=2, padx=10, pady=5)



# Function to read the list of filenames from filename.txt file
def read_filenames():
    if os.path.exists(filenames_file):
        user_files = {}
        with open(filenames_file, "r") as file:
            lines = file.readlines()
            if not lines:
                return None
            for line in lines:
                username, filename = line.strip().split(':')
                if username in user_files:
                    user_files[username].append(filename)
                else:
                    user_files[username] = [filename]
            return user_files      
    else:
        return {}



# Function to update the list of filenames in filename.txt file
def update_filenames(filename):
    with open(filenames_file, "a") as file:
        file.write(f"{authenticated_user}:{filename}\n")

# def update_filenames(filename):
#     with open(filenames_file, "r+") as file:
#         lines = file.readlines()
#         usernames = [line.split(':')[0] for line in lines] 
#         filenames = [line.split(':')[1].strip() for line in lines] 
        
#         # Check if the filename is already associated with any user
#         # Append if filename and authenticated user not present
#         if filename not in filenames and authenticated_user not in usernames:
#             file.write(f"{authenticated_user}:{filename}\n")  




# Implements the User Command of Upload File
def uploadFile(file_path):
    
    print(f"Uploading file: {file_path}")
    fname = os.path.basename(file_path)
    print(fname)
    metadata_fn = f"{fname}_metadata_enc.json"
    metadata_file = os.path.join(ROOT_DIR, metadata_folder, authenticated_user, metadata_fn)
    encryption_key = get_encryption_key(fname)
    putFile(file_path, chunk_servers, chunk_size, encryption_key, metadata_file, 
            master_key_bytes, ROOT_DIR)
    status_var.set(f"File '{fname}' uploaded successfully.")




# Implements the User Command of Download File
def downloadFile(file_path, encryption_key):
    
    print(f"Downloading file: {file_path}")
    fname = os.path.basename(file_path)
    print(fname)
    
    fname_without_extension = os.path.splitext(fname)[0]
    output_fn = fname_without_extension + "_rec.txt"
    output_folder_name =  "outputs" 
    output_folder = os.path.join(ROOT_DIR, output_folder_name, authenticated_user)     
    output_file = os.path.join(ROOT_DIR, output_folder_name, authenticated_user, output_fn)

    metadata_fn = f"{fname}_metadata_enc.json"
    metadata_file = os.path.join(ROOT_DIR, metadata_folder, authenticated_user, metadata_fn)

    if not os.path.exists(metadata_file):
        print("Invalid filename and/or Metadata file not found.")
        print("Exiting program....")
        print()
        status_var.set("Invalid filename and/or Metadata file not found. Download Cancelled..")
        return

    getFile(metadata_file, output_file, encryption_key, master_key_bytes, ROOT_DIR)
    status_var.set(f"File '{fname}' downloaded to folder {output_folder} as {output_fn} successfully.")
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
        file.write(f"{authenticated_user}:{filename}:{encryption_key.hex()}\n")
    print(f"Encryption key for {filename} saved.")


# Implements function to retrieve an encryption key for a given filename
def get_encryption_key(filename):
    if not os.path.exists(enc_config_fn):
        return None
    
    with open(enc_config_fn, "r") as file:
        lines = file.readlines()
        for line in lines:
            username, file_name, key_hex = line.strip().split(":")
            if username == authenticated_user:
                if file_name == filename:
                    return bytes.fromhex(key_hex)
    return None


# Implements checks to ensure user has uploaded a specific file
def isUserFileNamePresent(filename):
    with open(filenames_file, "r") as file:
        for line in file:
            parts = line.strip().split(":")
            if len(parts) == 2 and parts[0] == authenticated_user and parts[1] == filename:
                return True
    return False



# Implements callback when upload button is pressed
def uploadAction():
    file_path = filedialog.askopenfilename(
        title="Select a file to upload",
        filetypes=(("Text files", "*.txt"), ("All files", "*.*")),
        initialdir=os.path.join(ROOT_DIR, "user_file_repo", authenticated_user)
    )
    if file_path:
        file_name = os.path.basename(file_path)
        # User is uploading file for the first time
        if not isUserFileNamePresent(file_name):
            update_filenames(file_name)
            save_encryption_key(file_name)
            status_var.set(f"Status: Uploading {os.path.basename(file_path)}")
            uploadFile(file_path)
        else:
            status_var.set(f"Status: File {file_name} already uploaded by user: {authenticated_user}")
            messagebox.showwarning("Action", f"File {file_name} already uploaded by user: {authenticated_user}")
            return
    else:
        status_var.set("Status: Upload cancelled")



# Implements callback when download button is pressed
def downloadAction():
    directory = os.path.join(ROOT_DIR, "user_file_repo", authenticated_user)
    os.makedirs(directory, exist_ok=True)
    status_var.set("Status: Listing files for download")
    list_files_for_download(directory)



# Implements callback when list button is pressed
def listAction():
    directory = os.path.join(ROOT_DIR, "user_file_repo", authenticated_user)
    os.makedirs(directory, exist_ok=True)
    status_var.set("Status: List button pressed")
    # messagebox.showinfo("Action", "Listing files")
    listFiles(directory)



# Function to read user config file and store contents in a dictionary
def read_user_config(file_path):
    credentials = {}
    with open(file_path, 'r') as file:
        lines = file.readlines()
        for line in lines[:-1]:  # Exclude the last line
            parts = line.strip().split()
            if len(parts) == 2:
                username, password_hash = parts
                credentials[username] = password_hash
        if lines:  # Ensure there is at least one line
            last_line = lines[-1].strip()
            if last_line.startswith("num_users"):
                num_users = int(last_line.split()[-1])
    return credentials, num_users




def enable_buttons():
    upload_button.config(state=tk.NORMAL)
    download_button.config(state=tk.NORMAL)
    list_button.config(state=tk.NORMAL)
    disconnect_button.config(state=tk.NORMAL)


def disable_buttons():
    upload_button.config(state=tk.DISABLED)
    download_button.config(state=tk.DISABLED)
    list_button.config(state=tk.DISABLED)
    disconnect_button.config(state=tk.DISABLED)
    connect_button.config(state=tk.NORMAL)


def disconnect_action():
    disable_buttons()
    status_var.set("Status: Disconnected")
    messagebox.showinfo("Action", "You have been disconnected")

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

    upload_button = ttk.Button(commands_frame, text="Upload", command=uploadAction, state=tk.DISABLED)
    upload_button.pack(side=tk.LEFT, padx=5)

    download_button = ttk.Button(commands_frame, text="Download", command=downloadAction, state=tk.DISABLED)
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
    status_var.set("Status: Ready. Press ""Connect"" to enter credentials.")
    status_bar = tk.Label(root, textvariable=status_var, font=("Arial", 10), relief=tk.SUNKEN, anchor=tk.W)
    status_bar.pack(side=tk.BOTTOM, fill=tk.X)

    # Create a bottom label
    bottom_label = tk.Label(root, text="Created by MSCS23001 & MSCS23008 as part of Adv OS Project", font=("Arial Bold", 9))
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

    global user_config_file
    user_config_file = os.path.join(ROOT_DIR, "dfs_users.config")

    # metadata_folder = "metadata"
    authenticated_user = ""
    
    create_main_window()
