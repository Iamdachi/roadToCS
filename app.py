from flask import Flask, redirect, request, url_for, session
from flask_sqlalchemy import SQLAlchemy
from authlib.integrations.flask_client import OAuth
from dotenv import load_dotenv

import os


# Load variables from .env file
load_dotenv()

google_client_id = os.getenv('GOOGLE_CLIENT_ID') # hidden creds here
google_client_secret = os.getenv('GOOGLE_CLIENT_SECRET')

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
    client_id=google_client_id,   # hidden creds here
    client_secret=google_client_secret, # hidden creds here
    access_token_url='https://accounts.google.com/o/oauth2/token',
    access_token_params=None,
    authorize_url='https://accounts.google.com/o/oauth2/auth',
    authorize_params=None,
    api_base_url='https://www.googleapis.com/oauth2/v1/',
    client_kwargs={'scope': 'openid email profile'}
)

# Login Route
@app.route('/login')
def login():
    redirect_uri = url_for('auth', _external=True)
    return google.authorize_redirect(redirect_uri)

# Authentication Callback
@app.route('/auth')
def auth():
    token = google.authorize_access_token()
    resp = google.get('userinfo')
    user_info = resp.json()
    
    # Find or create user
    user = User.query.filter_by(google_id=user_info['id']).first()
    if not user:
        user = User(
            google_id=user_info['id'], 
            email=user_info['email'], 
            name=user_info['name']
        )
        db.session.add(user)
        db.session.commit()
    
    # Set session
    session['user_id'] = user.id
    return redirect('/dashboard')

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

