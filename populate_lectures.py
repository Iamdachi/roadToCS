import json
from app import db
from app.models import Lecture

# script that populated database from lectures-json file
# Load JSON
with open('lectures.json') as f:
    data = json.load(f)

# Populate DB
for course in data['courses']:
    print(course)
    '''
    for lecture in course['lectures']:
        lecture_id = lecture['id']
        name = lecture['name']
        lecture_entry = Lecture(
            id=int(f"{course_id}{lecture_id}"),
            name=name
        )
    '''
        #db.session.add(lecture_entry)

#db.session.commit()
