import os

from flask import Blueprint
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session

from helpers import apology, db


public = Blueprint("public", __name__)


@public.route("/")
def index():
    """
    Renders the homepage with all of the content.
    Sends a projects_sorted dictionary to the html template. 
    Displays only the image with order 1 as the thumnbail.
    """
    # Check if the admin is logged in
    if session.get("user_id"):
        project = db.execute("SELECT * FROM projects JOIN project_contents ON projects.id=project_id WHERE project_contents.sort_order = 1")
    # Join the projects and project_contents table and put in the dictionary
    # Check if the project is hidden and only show the first image
    else:
        project = db.execute("SELECT * FROM projects JOIN project_contents ON projects.id=project_id WHERE projects.hidden = 0 AND projects.title !='About' GROUP BY projects.id HAVING MIN(project_contents.sort_order)")    
    projects = {}
    # Group all the project_contents into one dictionary 
    for row in project:
        # If the project_id exists, place the dictionary in list of items else create a new dictionary
        if row["project_id"] in projects:
            new_row = {"type": row["type"], "content" : row["content"], "order": row["sort_order"]}
            projects[row["project_id"]]["items"].append(new_row)
        else:
            projects[row["project_id"]] = {"title": row["title"], "description" : row["description"], "project_order": row["project_order"], "field" : " " ,\
                                           "hidden" : row["hidden"] ,"items" : [{"type": row["type"], "content" : row["content"], "order": row["sort_order"]}] }
    
    # Sort the items by sort_order
    for key in projects:
        projects[key]["items"].sort(key=lambda x:x["order"])
    # Sort the dictionary by project_order
    projects_sorted = dict(sorted(projects.items(), key=lambda item: (item[1]["project_order"] is None, item[1]["project_order"])))
    print(projects)
    return render_template("index.html", projects_sorted=projects_sorted)


@public.route("/project/<title_slug>", methods=["GET", "POST"])
def project(title_slug):
    """
    When the project thumnbail on the homepage is clicked it renders a project template. 
    Uses title_slug for the url, and gets the id from the template to query all of the content from the database.
    If the project doesn't exist, renders apology.
    """
    # Get key from POST data
    if request.method == "POST":
        project_id = request.form.get("key")
    else:
        project_id = None
    
    # If no key provided (direct URL access), fallback to title lookup
    if not project_id:
        title = title_slug.replace('-', ' ')
        project = db.execute("SELECT * FROM projects JOIN project_contents ON projects.id=project_id WHERE LOWER(projects.title) = ?", title.lower())
    else:
        project = db.execute("SELECT * FROM projects JOIN project_contents ON projects.id=project_id WHERE projects.id = ?", project_id)
    
    project_contents = { }
    
    # Group all the project_contents into one dictionary 
    for row in project:
        if row["project_id"] in project_contents:
            new_row = {"type": row["type"], "content" : row["content"], "content_id" :row["id"] , "order": row["sort_order"]}
            project_contents[row["project_id"]]["items"].append(new_row)
        else:
            project_contents[row["project_id"]] = {"title": row["title"], "description" : row["description"], "project_order": row["project_order"], "field" : " " ,\
                                           "items" : [{"type": row["type"], "content" : row["content"], "content_id" : row["id"] , "order": row["sort_order"]}] }
    
    if not project_contents:
        return apology("Project doesn't exist")
    # Sort the content of the project by order
    for key in project_contents:
        project_contents[key]["items"].sort(key=lambda x: (x["order"] is None, x["order"]))  

    return render_template("project.html", project_contents=project_contents)


@public.route("/works")
def works():
    """Displays all of the images from images table. Also takes the title, and alt text."""
    # Query the image paths,alt text and sort order.
    images = db.execute("SELECT path, alt, sort_order, title FROM images")
    # images.sort(key=lambda x:x["sort_order"])
    # fix of the previous line from claude AI to handle sort_order = NULL
    images.sort(key=lambda x: (x["sort_order"] is None, x["sort_order"]))  
    return render_template("works.html", images=images)


@public.route("/about")
def about():
    """Renders the about page content. The data for the about page is stored in projects with title='About'. """
    # content = db.execute("SELECT * FROM projects JOIN project_contents ON projects.id=project_id WHERE projects.title = 'About'")
    id = db.execute("SELECT id FROM projects WHERE title='About'")
    content = db.execute("SELECT * FROM project_contents WHERE project_id=?", id[0]["id"])
    content.sort(key=lambda x:x["sort_order"])

    return render_template("about.html", content=content)


