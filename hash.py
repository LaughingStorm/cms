from cs50 import SQL
from werkzeug.security import check_password_hash, generate_password_hash


db = SQL("sqlite:///portfolio.db")

db.execute("INSERT INTO admin (username, hash)\
            VALUES (?, ?)", "admin", generate_password_hash("!mtH34dm!n"))

print("Admin created")


