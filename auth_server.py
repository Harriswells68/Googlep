
from flask import Flask, request, redirect, session
from google_auth_oauthlib.flow import Flow
import os
import json

app = Flask(__name__)
app.secret_key = 'A very secret key'  # Change this to a random secret key

# Load client secrets
client_secrets_path = '/content/drive/MyDrive/App/client_id.json'
with open(client_secrets_path, 'r') as json_file:
    client_secrets = json.load(json_file)

# Initialize the OAuth flow
flow = Flow.from_client_config(
    client_secrets,
    scopes=['https://www.googleapis.com/auth/photoslibrary'],
    redirect_uri='https://googleph.pagekite.me/callback'  # This should match the redirect URI in Google Cloud Console
)

@app.route('/')
def index():
    authorization_url, state = flow.authorization_url(
        access_type='offline',
        include_granted_scopes='true',
        prompt='consent'
    )
    session['state'] = state
    return redirect(authorization_url)

@app.route('/callback')
def callback():
    flow.fetch_token(authorization_response=request.url)

    if not session.get('state') == request.args['state']:
        return 'State does not match!', 400

    credentials = flow.credentials
    session['credentials'] = {
        'token': credentials.token,
        'refresh_token': credentials.refresh_token,
        'token_uri': credentials.token_uri,
        'client_id': credentials.client_id,
        'client_secret': credentials.client_secret,
        'scopes': credentials.scopes
    }
    tokens = {
        'access_token': credentials.token,
        'refresh_token': credentials.refresh_token,
        'token_uri': credentials.token_uri,
        'client_id': credentials.client_id,
        'client_secret': credentials.client_secret,
        'scopes': credentials.scopes
    }
    with open('tokens.json', 'w') as token_file:
        json.dump(tokens, token_file)

    return redirect('https://app-googleph.pagekite.me/?auth=success')

if __name__ == '__main__':
    app.run(port=5000)
