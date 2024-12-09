from flask import Flask, redirect, session, url_for, request
import google_auth_oauthlib.flow
import json
import os
import requests

app = Flask('app')
# `FLASK_SECRET_KEY` is used by sessions. You should create a random string
# and store it as secret.
app.secret_key = os.urandom(24) # os.environ.get('FLASK_SECRET_KEY') or 

# `GOOGLE_APIS_OAUTH_SECRET` contains the contents of a JSON file to be downloaded
# from the Google Cloud Credentials panel.
oauth_config = json.loads(os.environ['GOOGLE_OAUTH_SECRETS'])

# This sets up a configuration for the OAuth flow
oauth_flow = google_auth_oauthlib.flow.Flow.from_client_config(
    oauth_config,
    # scopes define what APIs you want to access on behave of the user once authenticated
    scopes=[
        "https://www.googleapis.com/auth/userinfo.email",
        "openid", 
        "https://www.googleapis.com/auth/userinfo.profile",
    ]
)

# This is entrypoint of the login page. It will redirect to the Google login service located at the
# `authorization_url`. The `redirect_uri` is actually the URI which the Google login service will use to
# redirect back to this app.
@app.route('/signin')
def signin():
    # We rewrite the URL from http to https because inside the Repl http is used, 
    # but externally it's accessed via https, and the redirect_uri has to match that
    oauth_flow.redirect_uri = url_for('oauth2callback', _external=True).replace('http://', 'https://')
    authorization_url, state = oauth_flow.authorization_url()
    session['state'] = state
    print(session['state'])
    return redirect(authorization_url)

# This is the endpoint that Google login service redirects back to. It must be added to the "Authorized redirect URIs"
# in the API credentials panel within Google Cloud. It will call a Google endpoint to request
# an access token and store it in the user session. After this, the access token can be used to access
# APIs on behalf of the user.
@app.route('/oauth2callback')
def oauth2callback():
    print(session['state'])
    if not session['state'] == request.args['state']:
        return 'Invalid state parameter', 400
    oauth_flow.fetch_token(authorization_response=request.url.replace('http:', 'https:'))
    session['access_token'] = oauth_flow.credentials.token
    return redirect("/")

# This is the home page of the app. It directs the user to log in if they are not already.
# It shows the user info's information if they already are.
@app.route('/')
def welcome():
    if "access_token" in session:
        user_info = get_user_info(session["access_token"])
        if user_info:
            return f"""
                Hello {user_info["given_name"]}!<br>
                Your email address is {user_info["email"]}<br>
                <a href="/logout">Log out</a>
            """
    return """
        <h1>Hello!</h1>
        <a href="/signin">Sign In via Google</a><br>
    """

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
    return redirect('/')

# Index (mit graph)
#@app.route('/')
#def index():
#    return render_template('index.html')
    
if __name__ == '__main__':
    app.run(
        host='0.0.0.0',
        port=443,
        ssl_context=(
        '/etc/letsencrypt/live/roadtocs.com/fullchain.pem',
        '/etc/letsencrypt/live/roadtocs.com/privkey.pem'
    ))
