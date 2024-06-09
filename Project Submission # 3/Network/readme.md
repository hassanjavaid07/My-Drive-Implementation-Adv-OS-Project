This src project is submitted as part of Advanced Operating System (CS-501) conducted in ITU, Lahore (Spring-2024)


Course Instructor: Dr. Khawaja Muhammad Umar Suleiman

TA: Mr. Mubashir Rehman

Submitted by:

i)	HASSAN JAVAID, MSCS23001

ii)	SAAD BIN HAMMAD, MSCS23008

Date of Submission: June 09, 2024.
===========================================================================================================================
INSTRUCTIONS:

1. Navigate to the project path folder i.e. src in the source folder. Run the program from command line / terminal using the following command:
	python3 client_api3.py

2. The screenshots are attached showing how to run the program. Just follow them sequentially.

3. We have implemented server/client communication thru sockets protocols. The libraries used include sockets, zeroconf. The main source for server communication is found in main_http_server.py file.

4. The dfs_setup.config file contains My-Drive configuration parameters like master-key, chunk_size, num_chunk_servers, replication_factor.

5. Network interfacing & replication factor was also added and implemented successfully in submission # 3.

6. For submission # 3 two folders have been uploaded:
	- Local: Which operates the GFS based My-Drive distributed file system using local directories and local output 	folders as the chunkservers. It also contains support for user authentication, user login access, file upload, file download and file list functions for each authorized user.

	- Network: It implements all of the functionality mentioned for local operations, along with master-chunkserver communication protocol and file chunk replication. All of these were implemented and tested successfully. Relvant screenshots and videos are also uploaded as reference and guide.

7. As with previous versions, we have also implemented AES-256 (CBC Mode) encryption as our security layer. This provides encryption functionality for file-chunks, & file-metadata json files.

8. Two user names i.e "hassan" & "saad" are currently the authorised users for our My-Drive API, the user login info is contained in file dfs_users.config. The passwords are stored in SHA-256 hash.

9. The plain-text dummy login info present in "username_plain.txt" for visibility purpose only. If new users are to be added, it should be added to the dfs_users.config file alongwith SHA-256 password hash. Use the file user_hash.py for password hash generation.

10. The user_file_repo contains input files for each user. New files can be copied to each user file repo for testing upload and download functionalities.

11. Similarly, output folder for each user is seperate and contains dowloaded files in the format "{filename}_rec.txt".

12. SHA-256 is currently being used a hash function for selecting chunk_server index in file storing process.

13. API-development is completed and successfully implemented.

14. There are a total of 6 commands implemented in our API:
	Upload: "User Command Function to store a file into chunk servers"
	Download: "User Command Function to retrieve the merged file and store it in a folder named as output"
	List: "User Command Function to list all text files in the main drive directory"
	Connect: "User Command Function to connect main-server with our chunk servers"
	Disconnect: "Disconnect from chunkserver"
	Close: Exits the API.

15. Main server and chunk server communication is also developed and implemented successfully. Seperate working of these functionalities are also given in the folder "http_with_2_chunks_and_replication".

16. The package requirements for this project is given in requirements.txt file.

17. (Previous CLI version) For use in CLI interface follow the instructin as submitted in part1 of submission. Use the command "python dfscontrol.py" after navigating to the source folder. There are a total of 4 commands implemented in CLI interface:
	put: "User Command Function to store a file into chunk servers"
	get: "User Command Function to retrieve the merged file and store it in a folder named as output"
	list: "User Command Function to list all text files in the main drive directory"
	exit: "User Command Function to quit the program"
	
	The example text file is named as "example.txt" and is placed in src/user_file_repo. If you want to input a new file, place in that folder and select it using the "put" command.


