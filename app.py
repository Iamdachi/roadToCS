from flask import Flask, redirect, request, url_for, session, render_template
from flask_sqlalchemy import SQLAlchemy
from authlib.integrations.flask_client import OAuth
from authlib.common.security import generate_token
from dotenv import load_dotenv

import os


# Load variables from .env file
load_dotenv()

# set up app
app = Flask(__name__)
app.secret_key = os.urandom(24)  # Important for session management
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
db = SQLAlchemy(app)

# User Model
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    google_id = db.Column(db.String(100), unique=True)
    email = db.Column(db.String(100), unique=True)
    name = db.Column(db.String(100))
    # I should add courses done

# OAuth Configuration
oauth = OAuth(app)
google = oauth.register(
    name='google',
    client_id=os.getenv('GOOGLE_CLIENT_ID'),
    client_secret=os.getenv('GOOGLE_CLIENT_SECRET'),
    server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
    client_kwargs={
        'scope': 'openid email profile'
    }
)

# Login Route
@app.route('/login')
def login():
    state = generate_token()
    session['oauth_state'] = state
    redirect_uri = url_for('auth', _external=True)
    return google.authorize_redirect(redirect_uri, state=state)

# Authentication Callback
@app.route('/auth')
def auth():
    # Verify state to prevent CSRF
    if 'oauth_state' not in session:
        return 'Authentication error', 403
    
    # Validate state
    if request.args.get('state') != session['oauth_state']:
        return 'Invalid state parameter', 403
    
    token = google.authorize_access_token()
    resp = google.get('user_info')
    user_info = resp.json()
    
    # Your user handling logic here
    return f"Logged in as {user_info['email']}"

# Protected Route
@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect('/login')
    user = User.query.get(session['user_id'])
    return f'Welcome {user.name}!'

# Logout
@app.route('/logout')
def logout():
    session.pop('user_id', None)
    return redirect('/login')
    
# Index (mit graph)
@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)

