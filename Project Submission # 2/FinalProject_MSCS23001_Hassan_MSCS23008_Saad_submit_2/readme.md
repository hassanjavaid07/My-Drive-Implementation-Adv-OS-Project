This src project is submitted as part of Advanced Operating System (CS-501) conducted in ITU, Lahore (Spring-2024)

Course Instructor: Dr. Khawaja Muhammad Umar Suleiman
TA: Mr. Mubashir Rehman

Submitted by:
i)	HASSAN JAVAID, MSCS23001
ii)	SAAD BIN HAMMAD, MSCS23008

Date of Submission: May 21, 2024.
===========================================================================================================================
INSTRUCTIONS:

1. Navigate to the project path folder i.e. src in the source folder. Run the program from command line / terminal using the following command:
	python client_api.py

2. The screenshots are attached showing how to run the program. Just follow them sequentially.


3. With respect to the 1st submission an API is developed for handling of user commands.


4. There are a total of 3 commands implemented so far in our API:
	Upload: "User Command Function to store a file into chunk servers"
	Download: "User Command Function to retrieve the merged file and store it in a folder named as output"
	List: "User Command Function to list all text files in the main drive directory"
	Close: Exit the API



5. (Previous) For use in CLI interface follow the instructin as submitted in part1 of submission. Use the command "python dfscontrol.py" after navigating to the source folder. There are a total of 4 commands implemented in CLI interface:
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

11. API-development is completed.

12. Client communication is also being developed, current working is also given in folder Socket Comm in the root folder.
