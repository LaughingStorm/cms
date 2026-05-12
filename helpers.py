import requests

from database import Database
from cs50 import SQL
from flask import redirect, render_template, session
from functools import wraps

#from week9 pset
db = Database("sqlite:///portfolio.db")

#MAJORITY OF THIS CODE IS FROM THE CS50 finance problem from Week 9 - apology, escape and login_rquired

# from cs50 admin problem
def apology(message, code=400):
    """Render message as an apology to user."""

    def escape(s):
        """
        Escape special characters.

        https://github.com/jacebrowning/memegen#special-characters
        """
        for old, new in [
            ("-", "--"),
            (" ", "-"),
            ("_", "__"),
            ("?", "~q"),
            ("%", "~p"),
            ("#", "~h"),
            ("/", "~s"),
            ('"', "''"),
        ]:
            s = s.replace(old, new)
        return s

    return render_template("apology.html", top=code, bottom=escape(message)), code

# From CS50 finance problem
def login_required(f):
    """
    Decorate routes to require login.

    https://flask.palletsprojects.com/en/latest/patterns/viewdecorators/
    """

    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/index.html")
        return f(*args, **kwargs)

    return decorated_function


# Get the project's content
def get_project(id):
    project = db.execute("SELECT * FROM projects JOIN project_contents ON projects.id=project_id WHERE projects.id = ?", id)
    project_contents = { }
    
        # Group all the project_contents into one dictionary 
    for row in project:
        # If the project_id exists, place the dictionary in list of items else create a new dictionary

        if row["project_id"] in project_contents:
            new_row = {"type": row["type"], "content" : row["content"], "order": row["sort_order"]}
            project_contents[row["project_id"]]["items"].append(new_row)
        else:
            project_contents[row["project_id"]] = {"title": row["title"], "description" : row["description"], "project_order": row["project_order"], "field" : " " ,\
                                           "items" : [{"type": row["type"], "content" : row["content"], "order": row["sort_order"]}] }
    
    # check if the project exists
    if not project_contents:
        return None

    # Sort the items by sort_order
    for key in project_contents:
        project_contents[key]["items"].sort(key=lambda x: (x["order"] is None, x["order"]))
        
    return project_contents
