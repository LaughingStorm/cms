import sys
from werkzeug.security import generate_password_hash
from helpers import Database
from getpass import getpass


db = Database("sqlite:///portfolio.db")
username = input("Username: ").strip()
pswrd = getpass("Password: ")
if not username or not pswrd:
    sys.exit("Username and password can't be empty")

try:
    existing = db.execute("SELECT * FROM admin WHERE username = ?", username)
    if existing:
        sys.exit("Username already exists")
    p_hash = generate_password_hash(pswrd)
    db.execute("INSERT INTO admin (username, hash)\
            VALUES (?, ?)", username, pswrd)

except Exception as e:
    sys.exit("An error has occured")

    
print("Admin created")


