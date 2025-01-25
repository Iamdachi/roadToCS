from flask import Flask, jsonify, redirect, session, flash, url_for, request, render_template
from oauthlib.oauth2 import WebApplicationClient
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user,\
    current_user, login_required
import json
import os
import requests

app = Flask('app')
app.config['SESSION_COOKIE_SECURE'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_NAME'] = 'your_session_cookie'
app.secret_key = os.environ.get('FLASK_SECRET_KEY')
app.config['SESSION_TYPE'] = 'filesystem'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite'
app.config['PREFERRED_URL_SCHEME'] = 'https'

db = SQLAlchemy(app)
login = LoginManager(app)
# login_manager.init_app(app)
login.login_view = 'index'

# Auth Config
# Configuration
GOOGLE_CLIENT_ID = os.environ.get("GOOGLE_CLIENT_ID", None)
GOOGLE_CLIENT_SECRET = os.environ.get("GOOGLE_CLIENT_SECRET", None)
GOOGLE_DISCOVERY_URL = (
    "https://accounts.google.com/.well-known/openid-configuration"
)

client = WebApplicationClient(GOOGLE_CLIENT_ID)

# Association table for the many-to-many relationship
user_lectures = db.Table(
    'user_lectures',
    db.Column('user_id', db.Integer, db.ForeignKey('users.id'), primary_key=True),
    db.Column('lecture_id', db.Integer, db.ForeignKey('lectures.id'), primary_key=True)
)

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), nullable=False)
    email = db.Column(db.String(64), nullable=True)
    lectures = db.relationship('Lecture', secondary=user_lectures, backref='students')


class Lecture(db.Model):
    __tablename__ = 'lectures'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), nullable=False)

def populate_lectures(db):
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

def get_google_provider_cfg():
    return requests.get(GOOGLE_DISCOVERY_URL).json()

@app.route('/update-lecture-status', methods=['POST'])
@login_required
def update_lecture_status():
    data = request.get_json()
    lecture_id = data.get('lecture_id')
    done = data.get('done')

    if not lecture_id:
        return jsonify({'error': 'Invalid data'}), 400

    # Fetch the lecture by name
    lecture = Lecture.query.filter_by(name=lecture_id).first()
    if not lecture:
        return jsonify({'error': 'Lecture not found ' + lecture_id}), 404

    if done:
        # Add the lecture to the user's list if it's marked as done
        if lecture not in current_user.lectures:
            current_user.lectures.append(lecture)
    else:
        # Remove the lecture from the user's list if it's marked as not done
        if lecture in current_user.lectures:
            current_user.lectures.remove(lecture)

    db.session.commit()
    return jsonify({'success': True}), 200

@login.user_loader
def load_user(id):
    return db.session.get(User, int(id))

# It will redirect to the Google login service at the `authorization_url`. The `redirect_uri` is the URI which the Google service will use to redirect back to this app.
@app.route('/signin')
def signin():
    # Find out what URL to hit for Google login
    google_provider_cfg = get_google_provider_cfg()
    authorization_endpoint = google_provider_cfg["authorization_endpoint"]

    # Use library to construct the request for Google login and provide
    # scopes that let you retrieve user's profile from Google
    request_uri = client.prepare_request_uri(
        authorization_endpoint,
        redirect_uri=request.host_url + "oauth2callback",
        scope=["openid", "https://www.googleapis.com/auth/userinfo.email"],
    )
    return redirect(request_uri)

# This is the endpoint that Google login service redirects back to. It must be added to the "Authorized redirect URIs"
# in the API credentials panel within Google Cloud. It will call a Google endpoint to request
# an access token and store it in the user session. After this, the access token can be used to access
# APIs on behalf of the user.
@app.route('/oauth2callback')
def oauth2callback():
    # Get authorization code Google sent back to you
    code = request.args.get("code")

    # Find out what URL to hit to get tokens that allow you to ask for
    # things on behalf of a user
    google_provider_cfg = get_google_provider_cfg()
    token_endpoint = google_provider_cfg["token_endpoint"]

    # Prepare and send a request to get tokens! Yay tokens!
    token_url, headers, body = client.prepare_token_request(
        token_endpoint,
        authorization_response=request.url,
        redirect_url=request.base_url,
        code=code
    )

    token_response = requests.post(
        token_url,
        headers=headers,
        data=body,
        auth=(GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET),
    )

    return("response is: " + str(token_response.json()))

    # Parse the tokens!
    client.parse_request_body_response(json.dumps(token_response.json()))

    # Now that you have tokens (yay) let's find and hit the URL
    # from Google that gives you the user's profile information,
    # including their Google profile image and email
    userinfo_endpoint = google_provider_cfg["userinfo_endpoint"]
    uri, headers, body = client.add_token(userinfo_endpoint)
    userinfo_response = requests.get(uri, headers=headers, data=body)

    # You want to make sure their email is verified.
    # The user authenticated with Google, authorized your
    # app, and now you've verified their email through Google!

    email = ""
    if userinfo_response.json().get("email_verified"):
        email = userinfo_response.json()["email"]
    else:
        return "User email not available or not verified by Google.", 400


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
    if "access_token" in session:
        user_info = get_user_info(session["access_token"])
        if user_info:
            return render_template("index.html")
    return render_template("index.html")

@app.route('/about')
def about():
    return render_template("about.html")

@app.route('/mentions')
def mentions():
    return render_template("mentions.html")

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
@login_required
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
        if current_user.is_authenticated:
            done_lectures = Lecture.qadd_tokenuery.join(user_lectures).join(User).filter(User.id == current_user.id).all()
            for done_lecture in done_lectures:
                name = done_lecture.name
                cId = name.split('_')[0][1:]
                lId = name.split('_')[1]

                lectures[str(cId)][int(lId)]["done"] = True
    return jsonify(lectures)

with app.app_context():
    db.drop_all()  # Drops all tables DELETE THIS LINE LATER!!!
    db.create_all()  # Creates tables again
    populate_lectures(db)
