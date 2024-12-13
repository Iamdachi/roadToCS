from flask import Flask, jsonify, redirect, session, flash, url_for, request, render_template
import google_auth_oauthlib.flow
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user,\
    current_user
import json
import os
import requests

app = Flask('app')
app.config['SESSION_COOKIE_SECURE'] = True
app.secret_key = os.environ.get('FLASK_SECRET_KEY') # or os.urandom(24)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite'

db = SQLAlchemy(app)
login = LoginManager(app)
login.login_view = 'index'

# `GOOGLE_APIS_OAUTH_SECRET` contains the contents of a JSON file to be downloaded from the Google Cloud Credentials panel.
oauth_config = json.loads(os.environ['GOOGLE_OAUTH_SECRETS'])

# This sets up a configuration for the OAuth flow
oauth_flow = google_auth_oauthlib.flow.Flow.from_client_config(
    oauth_config,
    # scopes define what APIs you want to access on behalf of the user once authenticated
    scopes=["https://www.googleapis.com/auth/userinfo.email", "openid"]
)

# Association table for the many-to-many relationship
user_courses = db.Table(
    'user_courses',
    db.Column('user_id', db.Integer, db.ForeignKey('users.id'), primary_key=True),
    db.Column('course_id', db.Integer, db.ForeignKey('courses.id'), primary_key=True)
)

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), nullable=False)
    email = db.Column(db.String(64), nullable=True)
    courses = db.relationship('Course', secondary=user_courses, backref='students')


class Course(db.Model):
    __tablename__ = 'courses'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), nullable=False)


## usage
'''
user = User.query.get(1)  # Fetch user with ID 1
course = Course.query.get(2)  # Fetch course with ID 2
user.courses.append(course)
db.session.commit()

user = User.query.get(1)
print([course.name for course in user.courses])

course = Course.query.get(2)
print([student.username for student in course.students])

'''
@login.user_loader
def load_user(id):
    return db.session.get(User, int(id))

# It will redirect to the Google login service at the `authorization_url`. The `redirect_uri` is the URI which the Google service will use to redirect back to this app.
@app.route('/signin')
def signin():
    # We rewrite the URL from http to https because inside the Repl http is used, 
    # but externally it's accessed via https, and the redirect_uri has to match that
    oauth_flow.redirect_uri = url_for('oauth2callback', _external=True).replace('http://', 'https://')
    authorization_url, state = oauth_flow.authorization_url()
    session['state'] = state
    
    return redirect(authorization_url)

# This is the endpoint that Google login service redirects back to. It must be added to the "Authorized redirect URIs"
# in the API credentials panel within Google Cloud. It will call a Google endpoint to request
# an access token and store it in the user session. After this, the access token can be used to access
# APIs on behalf of the user.
@app.route('/oauth2callback')
def oauth2callback():
    print("session is: ")
    print(session)
    if not session['state'] == request.args['state']:
        return 'Invalid state parameter', 400
  
    oauth_flow.redirect_uri = url_for('oauth2callback', _external=True).replace('http://', 'https://') # i added this

    oauth_flow.fetch_token(authorization_response=request.url.replace('http:', 'https:'))
    session['access_token'] = oauth_flow.credentials.token

    # find or create the user in the database
    user_info = get_user_info(session["access_token"])
    email = user_info['email']
    user = db.session.scalar(db.select(User).where(User.email == email))
    if user is None:
        user = User(email=email, username=email.split('@')[0])
        db.session.add(user)
        db.session.commit()

    # log the user in
    login_user(user)
    return redirect("/")

# This is the home page of the app. It directs the user to log in if they are not already.
# It shows the user info's information if they already are.
@app.route('/')
def welcome():
    print("session is: ")
    print(session)
    if "access_token" in session:
        user_info = get_user_info(session["access_token"])
        if user_info:
            return f"""
                Hello {user_info}!<br>
                Your email address is {user_info["email"]}<br>
                <a href="/logout">Log out</a>
            """
    return render_template("index.html")

# Call the userinfo API to get the user's information with a valid access token.
# This is the first example of using the access token to access an API on the user's behalf.
def get_user_info(access_token):
    response = requests.get("https://www.googleapis.com/oauth2/v3/userinfo", headers={
       "Authorization": f"Bearer {access_token}"
   })
    if response.status_code == 200:
        user_info = response.json()
        return user_info
    else:
        print(f"Failed to fetch user info: {response.status_code} {response.text}")
        return None

@app.route('/logout')
def logout():
    session.clear()
    logout_user()
    flash('You have been logged out.')
    return redirect('/')

@app.route('/mit-roadmap')
def get_roadmap_data():
    with open('mit.json') as f:
        roadmap = json.load(f)
    return jsonify(roadmap)

@app.route('/mit-lectures')
def get_lectures_data():
    with open('lectures.json') as f:
        lectures = json.load(f)
    return jsonify(lectures)

with app.app_context():
    db.drop_all()  # Drops all tables DELETE THIS LINE LATER!!!
    db.create_all()  # Creates tables again
