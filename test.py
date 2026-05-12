import os

from flask import Blueprint
from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session

from helpers import apology, db

# project = db.execute("SELECT * FROM projects JOIN project_contents ON projects.id=project_id")
# projects = {}
# for row in project:
# # If the project_id exists, place the dictionary in list of items 
#     if row["project_id"] in projects:
#         new_row = {"type": row["type"], "content" : row["content"], "order": row["sort_order"]}
#         projects[row["project_id"]]["items"].append(new_row)
#         projects[row["project_id"]]
#     else:
#         projects[row["project_id"]] = {"title": row["title"], "description" : row["description"], "project_order": row["project_order"], "field" : " " ,\
#                                            "items" : [{"type": row["type"], "content" : row["content"], "order": row["sort_order"]}] }

# for key in projects:
#     projects[key]["items"].sort(key=lambda x:x["order"])
# projects_sorted = dict(sorted(projects.items(), key=lambda item:item[1]["project_order"]))
# # print(projects)

# print(projects_sorted[2])

images = db.execute("SELECT path, alt, sort_order FROM images")
print(images)