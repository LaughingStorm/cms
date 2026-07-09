from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash
from helpers import db


from blueprints.admin import admin
from blueprints.public import public
app = Flask(__name__)

app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

app.register_blueprint(admin)
app.register_blueprint(public)


def init_db():
    """Applies schema.sql if the database has no tables yet (fresh volume)."""
    tables = db.execute("SELECT name FROM sqlite_master WHERE type='table'")
    if not tables:
        with open("schema.sql") as f:
            schema = f.read()
        for statement in schema.split(";"):
            statement = statement.strip()
            if statement:
                db.execute(statement)


init_db()
