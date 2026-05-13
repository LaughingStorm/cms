from flask import Blueprint

import os
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from werkzeug.security import check_password_hash
import time


from helpers import login_required, apology, db, get_project

# Configure the blueprint
admin = Blueprint("admin", __name__)


@admin.route("/adminlog", methods=["GET", "POST"])
def login():
    """ Login for the admin. If POST method is used, checks the database for credentials. 
        On failure it returns apology and on success redirects to the route /
        GET method renders the adminlog.html template.
    """
    # Forget any user
    session.clear()
    if request.method == "POST":
        if not request.form.get("username"):
            return apology("must provide username", 403)
        elif not request.form.get("password"):
            return apology("must provide password", 403)

        # Query database for username
        rows = db.execute(
            "SELECT * FROM admin WHERE username = ?", request.form.get("username")
        )

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(
            rows[0]["hash"], request.form.get("password")
        ):
            return apology("invalid username or password", 403)

        # Remember the admin
        session["user_id"] = rows[0]["id"]
        return redirect("/")

    else:
        return render_template("adminlog.html")


@admin.route("/logout")
def logout():
    """Log outs the admin. Clears the session and redirects to the / route"""
    # Forget the user_id
    session.clear()

    return redirect("/")
        


@admin.route("/admin/toggle/<id>", methods = ["GET", "POST"])
@login_required
def toggle(id):
    """ 
    Toggle for hiding or showing the project on the homepage. Requires login
    Accepts POST and GET methods
    if POST is used it switches the hidden column from the database to 0 or 1.
    GET method redirects to the / route
    """
    if request.method == "POST":
        hidden = db.execute("SELECT hidden FROM projects WHERE id = ?", id)
        if hidden[0]["hidden"] == 0:
            db.execute("UPDATE projects SET hidden = 1 WHERE id = ?", id)
        else:
            db.execute("UPDATE projects SET hidden = 0 WHERE id = ?", id)
        
        return redirect("/")
    else:
        return redirect("/")
    


@admin.route("/admin/delete/<id>", methods= ["GET", "POST"])
@login_required
def delete(id):
    """
    Deletes the images that are part of the project from the filesystem and the database.
    Deletes the project, by project_id.
    Project_id is sent as 'id' through the submit form.
    POST and GET redirect to / route
    """
    if request.method == "POST":
        # Delete all the contents of the project
        images = db.execute("SELECT content FROM project_contents WHERE type = 'image' AND project_id = ?", id)
        for image in images:
            try:
                os.remove(image["content"])
            except PermissionError:
                pass
            # If the file doesn't exist in the filesystem catch the error
            except OSError as e:
                pass
        db.execute("DELETE FROM project_contents WHERE project_id = ?", id)
        # Delete the project
        db.execute("DELETE FROM projects WHERE id = ?", id)
        return redirect("/")
    
    else:
        return redirect("/")
    

@admin.route("/admin/add", methods = ["GET", "POST"])
@login_required
def add_project():
    """
    Adds a new project to the homepage
    Gets 4 return values from the submit form.
    Project title, description, order and image.
    If order is not provided the default is 1.
    Image is saved into the file system and the path is saved in the database. 
    """
    if request.method == "POST":
        # Get the title and description from the form
        title = request.form.get("title")
        description = request.form.get("description")
        order = request.form.get("order")
        if order == "":
            order = 1   #Make this the default order, in public.py the image with order 1 is used for the thumbnail 
        # Get the file
        file = request.files["image"]
        
        # Replace the space in the filename
        fn = file.filename.replace(" ", "_")
        # Prepend the time to the filename
        filename =str(time.time()) + "_" + fn
      
        # Save the file
        file.save(os.path.join("static/images", filename))

        db.execute("INSERT INTO projects(title, description, project_order) VALUES(?, ?, ?)", title, description,order)
        # Get the project_id
        project_id = db.execute("SELECT id FROM projects WHERE title = ? AND description = ?", title, description)
        db.execute("INSERT INTO project_contents(type, content, project_id, sort_order) VALUES ('image', ?, ?, 1)", f"static/images/{filename}", project_id[0]["id"])  # For path
        # Here I use f"static/images/{filename} instead of the os.path.joing("static/images", filename)) because it breaks the thumbnail preview on windows
        # as the background-image: url()  was used.
        return redirect("/")
    else:
        return redirect("/")
    

@admin.route("/admin/order", methods = ["POST"])
@login_required
def order_project():
    """ Only accepts POST method. Changes the display order of the project relative to the other projects."""
    order = request.form.get("order")
    project_id = request.form.get("id")

    db.execute("UPDATE projects SET project_order = ? WHERE id = ?", order, project_id)

    return redirect("/")



@admin.route("/admin/project/<project_id>", methods = ["GET"])
@login_required 
def change_project(project_id):
    """ Accepts only GET method, renders the individual project page with the admin panel functionality
        get_project() returns a dictionary, with all of the project's data"""    
    # call the function defined in helpers.py, that get's the project's contents by project_id
    project_contents = get_project(project_id)

    if project_contents is None:
        return apology("project doesn't exist")

    return render_template("project.html", project_contents=project_contents)



@admin.route("/admin/project/add/<project_id>", methods = ["GET", "POST"])
@login_required
def add_content(project_id):    
    """
    Adds an image or text to the project.
    If the image is uploaded, it's saved in a file system and it's path and alt text is saved inside a database.
    POST and GET methods redirect to the /admin/project/project_id route
    """
    if request.method == "POST":
        input = request.form.get("type")
        order = request.form.get("order")
        # Check if the user entered order and text
        if order == "":
            order = 1
        if input == None:
            return redirect(f"/admin/project/add/{project_id}")
        
        if input == "image":
            file = request.files["imageInput"]
            # check if the file input is empty
            if file.filename == "":
                return redirect(f"/admin/project/add/{project_id}")

            # Replace the space in the filename
            fn = file.filename.replace(" ", "_")
            # Prepend the time to the filename
            filename = str(time.time()) + "_" + fn
            path = f"static/images/{filename}"
            #save the file
            file.save(os.path.join("static/images", filename))
            # Insert the file in the database
            db.execute("INSERT INTO project_contents(type, content, sort_order, project_id) VALUES(?, ?, ?, ?)", input, path, order, project_id)

        else:
            text = request.form.get("text")
            try:
                db.execute("INSERT INTO project_contents(type, content, sort_order, project_id) VALUES(?, ?, ?,?)", input, text, order, project_id)
            except ValueError:
                pass

        return redirect(f"/admin/project/{project_id}")

    else:
        return redirect(f"/admin/project/{project_id}")



@admin.route("/admin/project/delete/", methods = ["POST"])
@login_required
def delete_content():
    """ 
    Accepts only POST method. Check if the content requested is an image or text.
    If it's an image delete first, try to delete it from the filesystem then delete it from the database.
    """
    try:
        project_id = request.form.get("project_id")
        content = request.form.get("content")
    except ValueError:
        pass
    try:
        result = db.execute("SELECT type FROM project_contents WHERE content = ?", content)
        if result[0]["type"] == "image":
            os.remove(content)
    except OSError:
        pass
    db.execute("DELETE FROM project_contents WHERE content= ?", content)

    return redirect(f"/admin/project/{project_id}")


@admin.route("/admin/project/order", methods = ["POST"])
@login_required
def content_order():
    """ Change the display order of the content relative to the other content of the page"""
    # Request all of the data
    order = request.form.get("order")
    content_id = request.form.get("content_id")
    project_id = request.form.get("project_id")
    # Apply the changes to the database
    db.execute("UPDATE project_contents SET sort_order = ? WHERE id = ?", order, content_id)

    return redirect(f"/admin/project/{project_id}")


@admin.route("/admin/project/edit", methods = ["POST"])
@login_required
def edit_text():
    """ Allows the editing of the project's title and description. Updates the projects table, columns title and description"""
    # Request all of the data
    project_id = request.form.get("project_id")
    title = request.form.get("title")
    description = request.form.get("description")
    # Apply changes to the database
    db.execute("UPDATE projects SET title = ?, description = ? WHERE id = ?", title, description, project_id)

    return redirect(f"/admin/project/{project_id}")


# ABOUT ROUTES
@admin.route("/admin/about", methods = ["GET", "POST"])
@login_required
def add_about():
    """ 
    Accepts POST and GET methods.
    All of the content for about page is queried from the database. In case of errors redirects to the /admin/about route.
    If the input is an image, saves it in the filesystem and adds the path to the database.
    """
    about_id = db.execute("SELECT id FROM projects WHERE title = 'About'")
    if request.method == "POST":
        input = request.form.get("type")
        order = request.form.get("order")
        if order =="":
            order = 1
        if input is None:
            return redirect("/admin/about")
        
        # if the input is image
        if input == "image":
            file = request.files["imageInput"]
            if file.filename == "":
                return redirect("/admin/about")
             # Replace the space in the filename
            fn = file.filename.replace(" ", "_")
            # Prepend the time to the filename
            filename =str(time.time()) + "_" + fn
            path = f"static/images/{filename}"
            #save the file
            file.save(os.path.join("static/images", filename))
            # Insert the file in the database
            db.execute("INSERT INTO project_contents(type, content, sort_order, project_id) VALUES(?, ?, ?, ?)", input, path, order, about_id[0]["id"])
        else:
            text = request.form.get("text")
            if text:
                try:
                    db.execute("INSERT INTO project_contents(type, content, sort_order, project_id) VALUES(?, ?, ?, ?)", input, text, order, about_id[0]["id"])
                except ValueError:
                    pass

        return redirect("/admin/about")
    
    else:
        content = db.execute("SELECT * FROM project_contents WHERE project_id=?", about_id[0]["id"])
        return render_template("about.html", content=content)


@admin.route("/admin/about/delete", methods =["GET", "POST"])
@login_required
def delete_about():
    """Delete the selected content from the page."""
    if request.method == "POST":
        content = request.form.get("content")
        try:
            result = db.execute("SELECT type FROM project_contents WHERE content = ?", content)
            if result[0]["type"] == "image":
                os.remove(content)
        except OSError:
            pass
        about_id = db.execute("SELECT id FROM projects WHERE title='About'")
        db.execute("DELETE FROM project_contents WHERE content =? AND project_id = ?", content, about_id[0]["id"])
        return redirect("/admin/about")
    else:
        return redirect("/about")
    

# WORKS ROUTES
@admin.route("/admin/works/add", methods=["GET", "POST"])
@login_required
def add_image():
    """
    Adds the image to the filesystem and the path to the database. Requires alt text to be provided. 
    If order is not provided it is automatically set to 1.
    """
    if request.method == "POST":
        alt = request.form.get("alt")
        if alt =="":
            return apology("please enter alt text")
        title = request.form.get("title")
        order = request.form.get("order")
        if order =="":
            order = 0
        file = request.files["image"]
         # check if the file input is empty
        if file.filename == "":
            return redirect(f"/admin/project/add/{id}")
        # Replace the space in the filename
        fn = file.filename.replace(" ", "_")
        # Prepend the time to the filename
        filename =str(time.time()) + "_" + fn

        path = f"static/images/{filename}"
        #save the file
        file.save(os.path.join("static/images", filename))
        
        db.execute("INSERT INTO images(path, sort_order, alt, title) VALUES(?, ?, ?, ?)", path, order, alt, title)
        return redirect("/works")
    
    else:
        return redirect("/works")

@admin.route("/admin/works/delete", methods =["GET", "POST"])
@login_required
def delete_image():
    """ Deletes an image from the filesystem and image path from the database."""
    if request.method =="POST":
        path = request.form.get("path")
        try:
            os.remove(path)
        except PermissionError:
            pass
        except OSError as e:
            pass
        db.execute("DELETE FROM images WHERE path=?", path)
        return redirect("/works")
    
    else:
        return redirect("/works")

@admin.route("/admin/works/order", methods =["GET", "POST"])
@login_required
def order_image():
    """Changes the display order of image relative to other content on the page."""
    if request.method == "POST":
        order = request.form.get("order")
        path = request.form.get("path")
        db.execute("UPDATE images SET sort_order = ? WHERE path = ?", order, path)
        return redirect("/works")
    else:
        return redirect("/works")