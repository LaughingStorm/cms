from flask import Blueprint

import os
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from werkzeug.security import check_password_hash
import time


from helpers import login_required, apology, db, get_project

# Configure the blueprint
admin = Blueprint("admin", __name__)

#Login for the admin
@admin.route("/adminlog", methods=["GET", "POST"])
def login():
    # Forget any user
    session.clear()
    """Log admin in"""
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

# Logout for the admin
@admin.route("/logout")
def logout():
    """log admin out"""
    # Forget the user_id
    session.clear()

    return redirect("/")
        
# Hide or unhide the project
@admin.route("/admin/toggle/<id>", methods = ["GET", "POST"])
@login_required
def toggle(id):
    if request.method == "POST":
        hidden = db.execute("SELECT hidden FROM projects WHERE id = ?", id)
        if hidden[0]["hidden"] == 0:
            db.execute("UPDATE projects SET hidden = 1 WHERE id = ?", id)
        else:
            db.execute("UPDATE projects SET hidden = 0 WHERE id = ?", id)
        
        return redirect("/")
    else:
        return render_template("index.html")
    
# Delete a proejct
@admin.route("/admin/delete/<id>", methods= ["GET", "POST"])
@login_required
def delete(id):
    if request.method == "POST":
        # Delete all the contents of the project
        db.execute("DELETE FROM project_contents WHERE project_id = ?", id)
        # Delete the project
        db.execute("DELETE FROM projects WHERE id = ?", id)
        return redirect("/")
    
    else:
        return render_template("index.html")
    
# Add a project
@admin.route("/admin/add", methods = ["GET", "POST"])
@login_required
def add_project():

    if request.method == "POST":
        # Get the title and description from the form
        title = request.form.get("title")
        description = request.form.get("description")
        order = request.form.get("order")
        if order == "":
            order = 0
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
        db.execute("INSERT INTO project_contents(type, content, project_id, sort_order) VALUES ('image', ?, ?, 1)", os.path.join("static/images", filename), project_id[0]["id"])
        return redirect("/")
    else:
        return render_template("index.html")
    
@admin.route("/admin/order", methods = ["GET", "POST"])
@login_required
def order_project():
    if request.method == "POST":
        order = request.form.get("order")
        id = request.form.get("id")
        db.execute("UPDATE projects SET project_order = ? WHERE id = ?", order, id)
        return redirect("/")
    else:
        return render_template("index.html")


# Render the project with admin's functions
@admin.route("/admin/project/<id>", methods = ["GET", "POST"])
@login_required 
def change_project(id):
    # call the function defined in helpers.py, that get's the project's contents by project_id
    project_contents = get_project(id)
    if project_contents is None:
        return apology("project doesn't exist")
    
    if request.method == "POST":
        return redirect(f"/admin/project/{id}")
    else:
        return render_template("project.html", project_contents=project_contents)


# Add content to the project
@admin.route("/admin/project/add/<id>", methods = ["GET", "POST"])
@login_required
def add_content(id):    
    if request.method == "POST":
        input = request.form.get("type")
        order = request.form.get("order")
        # Check if the user entered order and text
        if order == "":
            order = 0
        if input == "":
            return redirect(f"/admin/project/add{id}")
        
        if input == "image":
            file = request.files["imageInput"]
            # check if the file input is empty
            if file.filename == "":
                return redirect(f"/admin/project/add/{id}")
            # Replace the space in the filename
            fn = file.filename.replace(" ", "_")
            # Prepend the time to the filename
            filename =str(time.time()) + "_" + fn

            path = os.path.join("static/images", filename)
            #save the file
            file.save(os.path.join("static/images", filename))

            # Insert the file in the database
            db.execute("INSERT INTO project_contents(type, content, sort_order, project_id) VALUES(?, ?, ?, ?)", input, path, order, id)
        else:
            text = request.form.get("text")
            try:
                db.execute("INSERT INTO project_contents(type, content, sort_order, project_id) VALUES(?, ?, ?,?)", input, text, order, id)
            except ValueError:
                pass
        return redirect(f"/admin/project/add/{id}")
    
    else:
         return redirect(f"/admin/project/{id}")
    

# Delete the project's content
@admin.route("/admin/project/delete/", methods = ["GET", "POST"])
@login_required
def delete_content():
    if request.method == "POST":
        try:
            id = request.form.get("project_id")
            content = request.form.get("content")
        except ValueError:
            pass
        db.execute("DELETE FROM project_contents WHERE content= ?", content)
        return redirect(f"/admin/project/{id}")
    
    else:
        return redirect("/")
        

#Change the project's content order
@admin.route("/admin/project/order", methods = ["GET", "POST"])
@login_required
def content_order():
    if request.method == "POST":
        order = request.form.get("order")
        id = request.form.get("id")
        
        return render_template(f"/project/{id}")
    
    else:
        return redirect("/")



@admin.route("/admin/about", methods = ["GET", "POST"])
@login_required
def add_about():
    id = db.execute("SELECT id FROM projects WHERE title = 'About'")
    content = db.execute("SELECT * FROM project_contents WHERE project_id=?", id[0]["id"])

    if request.method == "POST":
        input = request.form.get("type")
        order = request.form.get("order")
        if order =="":
            order = 2
        if input == "":
            return redirect("/admin/about", content=content)
        
        # if the input is image
        print(f"input: {input}, order: {order}")
        if input == "image":
            file = request.files["imageInput"]
            if file.filename == "":
                return redirect("/admin/about", content=content)
             # Replace the space in the filename
            fn = file.filename.replace(" ", "_")
            # Prepend the time to the filename
            filename =str(time.time()) + "_" + fn
            path = os.path.join("static/images", filename)
            #save the file
            file.save(os.path.join("static/images", filename))
            # Insert the file in the database
            db.execute("INSERT INTO project_contents(type, content, sort_order, project_id) VALUES(?, ?, ?, ?)", input, path, order, id[0]["id"])
            print(5)
        else:
            text = request.form.get("text")
            print(text)
            try:
                db.execute("INSERT INTO project_contents(type, content, sort_order, project_id) VALUES(?, ?, ?, ?)", input, text, order, id[0]["id"])
            except ValueError:
                pass
        print(content)
        print(id)

        return redirect("/admin/about")
    else:
        return render_template("about.html", content=content)


@admin.route("/admin/about/delete", methods =["GET", "POST"])
@login_required
def delete_about():
    if request.method == "POST":
        content = request.form.get("content")
        id = db.execute("SELECT id FROM projects WHERE title='About'")
        db.execute("DELETE FROM project_contents WHERE content =? AND project_id = ?", content, id[0]["id"])
        return redirect("/admin/about")
    else:
        return redirect("/about")
    

# WORKS ROUTE
@admin.route("/admin/works/add", methods=["GET", "POST"])
@login_required
def add_image():
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

        path = os.path.join("static/images", filename)
        #save the file
        file.save(os.path.join("static/images", filename))
        
        db.execute("INSERT INTO images(path, sort_order, alt, title) VALUES(?, ?, ?, ?)", path, order, alt, title)
        return redirect("/works")
    
    else:
        return redirect("/works")

@admin.route("/admin/works/delete", methods =["GET", "POST"])
@login_required
def delete_image():
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
    if request.method == "POST":
        order = request.form.get("order")
        path = request.form.get("path")
        db.execute("UPDATE images SET sort_order = ? WHERE path = ?", order, path)
        return redirect("/works")
    else:
        return redirect("/works")