This src project is submitted as part of Advanced Operating System (CS-501) conducted in ITU, Lahore (Spring-2024)


Course Instructor: Dr. Khawaja Muhammad Umar Suleiman

TA: Mr. Mubashir Rehman

Submitted by:

i)	HASSAN JAVAID, MSCS23001

ii)	SAAD BIN HAMMAD, MSCS23008

Date of Submission: May 14, 2024.
===========================================================================================================================
INSTRUCTIONS:

1. Change the ROOT_DIR param in dfscontorl.py (line 220).

2. Navigate to the project path folder i.e. src/main_server in the source folder. Run the program from command line / terminal using the following command:
	python dfscontorl.py

3. The screenshots are attached showing how to run the program. Just follow them sequentially.

4. There are a total of 4 commands implemented so far in our Distributed File System:
	put: "User Command Function to store a file into chunk servers"
	get: "User Command Function to retrieve the merged file and store it in a folder named as output"
	list: "User Command Function to list all text files in the main drive directory"
	exit: "User Command Function to quit the program"

5. At this stage of the project, our output folders denote our chunk servers. After implementing socket networking and VM linking we will implement file operations and management remotely along with data processing, client communication, & user authentication.

6. The package requirements for this project is given in requirements.txt file.

7.	Do not change the config file present in the main_server folder. It contains important information like master_key, number of chunk servers, chunk size etc.

8.	The example text file is named as "example.txt" and is placed in src/user_file_repo. If you want to input a new file, place in that folder and select it using the "put" command.

9.	All of the chunk data along with the metadata file is encrypted using AES-256 CBC mode to implement a security layer in our file system.

10. SHA-256 is currently being used a hash function for selecting chunk_server index in file storing process.

11. API-development will also be done in the next phase of the project.
