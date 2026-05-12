-- ADMINS        → id, username, hash
-- FIELDS        → id, name
-- IMAGES        → id, path, field_id, hidden, sort_order, featured, title 
-- PROJECTS      → id, title, description, field_id, hidden, project_order, date
-- PROJECT_CONTENTS → id, project_id, type, content, order
-- MEDIUMS       -> id, medium
-- PROJECT_MEDIUMS  ->id, project_id, medium_id

CREATE TABLE IF not EXISTS admin
    (id INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE NOT NULL,
    username TEXT NOT NULL UNIQUE, hash TEXT NOT NULL);

CREATE TABLE IF not EXISTS mediums
    (id INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE NOT NULL,
    medium TEXT NOT NULL
    );

CREATE TABLE IF not EXISTS project_mediums(
    id INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE NOT NULL,
    project_id INTEGER NOT NULL,
    medium_id INTEGER NOT NULL,
    FOREIGN KEY(project_id) REFERENCES projects(id),
    FOREIGN KEY(medium_id) REFERENCES mediums(id));

CREATE TABLE IF not EXISTS  fields
    (id INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE NOT NULL,
    field TEXT NOT NULL);

CREATE TABLE IF not EXISTS images
    (id INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE NOT NULL,
    path TEXT NOT NULL UNIQUE,
    sort_order INTEGER,6;
    featured BOOLEAN DEFAULT FALSE,
    alt TEXT NOT NULL DEFAULT "image",
    title TEXT,
    field_id INTEGER,
    FOREIGN KEY(field_id) REFERENCES fields(id));

CREATE TABLE IF not EXISTS projects
    (id INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE NOT NULL,
    title TEXT,
    description TEXT,
    hidden BOOLEAN NOT NULL DEFAULT FALSE,
    project_order INTEGER,
    date TEXT,
    field_id INTEGER,
    FOREIGN KEY(field_id) REFERENCES fields(id));

CREATE TABLE IF not EXISTS project_contents
    (id INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE NOT NULL,
    type TEXT NOT NULL,
    content TEXT NOT NULL,
    sort_order INTEGER,
    project_id INTEGER,
    FOREIGN KEY(project_id) REFERENCES projects(id));
    

INSERT INTO projects(title, description, sort_order, date) VALUES("Suso", "Susin project", 1, "03/06/2026");

INSERT INTO project_contents(type, content, sort_order, project_id) 
                    VALUES("p","Project paragraph", 2, 2);

INSERT INTO fields(field) VALUES("Digital art");

INSERT INTO images(path, sort_order, field_id) VALUES ("static/images/bfaf.jpg", "2","1");

UPDATE images SET path = "static/images/gesture_1.jpg" WHERE id=1;

ALTER TABLE table_name RENAME COLUMN current_name TO new_name;

ALTER TABLE images ADD COLUMN alt TEXT NOT NULL DEFAULT "image"