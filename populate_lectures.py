import json
from app import db
from app.models import Lecture

# script that populated database from lectures-json file
# Load JSON
with open('lectures.json') as f:
    data = json.load(f)

# Populate DB
for course_id in data:
    lectures = data[course_id]

    for lecture in lectures:
        lecture_id = lecture['id']
        name = f"L{course_id}_{lecture_id}"
        print(name)

        lecture_entry = Lecture(name=name)
        db.session.add(lecture_entry)

db.session.commit()