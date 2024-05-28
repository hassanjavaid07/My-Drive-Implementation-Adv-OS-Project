# Use this file to generate hashes for new passwords

import hashlib

def hash_password(password):
    password_bytes = password.encode('utf-8')

    sha256_hash = hashlib.sha256()

    sha256_hash.update(password_bytes)

    hashed_password = sha256_hash.hexdigest()

    return hashed_password

def main():
    # Get password input from the user
    # password = input("Enter your password: ")
    password = "CryptoSide21"
    # Hash the password
    hashed_password = hash_password(password)

    # Print the hashed password
    print("Hashed password:", hashed_password)

if __name__ == "__main__":
    main()
