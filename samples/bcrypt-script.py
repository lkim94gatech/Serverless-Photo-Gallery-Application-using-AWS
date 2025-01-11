import bcrypt

# Password to Hash
my_password = 'ECE4150-password'

# Generating Salt
salt = bcrypt.gensalt()

# Hashing Password
hash_password = bcrypt.hashpw(
    password=my_password.encode("utf-8"),
    salt=salt
)

# User-provided Password
user_password = 'ECE4150-password'

# Checking Password
check = bcrypt.checkpw(
    password=user_password.encode("utf-8"),
    hashed_password=hash_password
)

# This will print True or False
print(check)

# Verifying the Password
if check:
    print("Welcome!")
else:
    print("Invalid Credential.")