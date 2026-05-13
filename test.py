from helpers import db

images = db.execute("SELECT content FROM project_contents WHERE type = 'image'")
for image in images:
    print(image)
