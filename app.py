import streamlit as st
import libtorrent as lt
import wget
import time
import shutil
def check_for_auth_param():
    # Access the query parameters from the URL
    query_params = st.query_params
    auth_status = query_params.get("auth", [""])[0]
    return auth_status == "s"

import re
import subprocess
import streamlit as st
from datetime import timedelta

def download(url, path):
    try:
        command = [
            'wget',
            f'--header=User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
            f'--header=Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
            f'--header=Accept-Language: en-US,en;q=0.9',
            f'--header=Upgrade-Insecure-Requests: 1',
            f'--header=Sec-Fetch-Dest: document',
            f'--header=Sec-Fetch-Mode: navigate',
            f'--header=Sec-Fetch-Site: none',
            f'--header=Sec-Fetch-User: ?1',
            '-P', path,  # Specify the download path using -P option
            url
        ]
        process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
        pattern=re.compile(r'\s..%')
        progress_bar = st.progress(0)
        status_text = st.empty()

        for line in iter(process.stdout.readline, ''):
          p=((re.compile(r'\s..%')).search(line))
          s=((re.compile(r'%\s.*(K|M)')).search(line))
          t=((re.compile(r'[0-9](K|M)\s([0-9]|[1-6][0-9])(h|m).*(m|s)')).search(line))
          if (p and s and t)!=None:
            p=p.group()
            p=int(p[1:3])
            progress_bar.progress(p)
            s=s.group()
            s=s[2:]
            t=t.group()
            t=t[3:]
            status_text.text(f"Progress:{p}% - Speed:{s}b/s - Time Left:{t}")
            time.sleep(0.5)

        process.wait()  # Wait for process to complete
        is_download_successful = process.returncode == 0

        # Clear out the progress bar and status
        progress_bar.empty()
        status_text.empty()

        if is_download_successful:
            st.success('Downloaded successfully!')
        else:
            st.error('Download failed.')

        return is_download_successful

    except Exception as e:
        st.error(f"An error occurred during the download: {e}")
        return False
# Initialize libtorrent session
ses = lt.session()
ses.listen_on(6881, 6891)

# Function to add and start a torrent download

import time
import libtorrent as lt
import streamlit as st
from datetime import timedelta

def download_magnet(magnet_link, save_path):
    ses = lt.session({'listen_interfaces': '0.0.0.0:6881'})
    params = {'save_path': save_path}
    handle = lt.add_magnet_uri(ses, magnet_link, params)
    ses.start_dht()
    while not handle.has_metadata():
        time.sleep(1)

    progress_bar = st.progress(0)
    status_text = st.empty()
    detail_text = st.empty()

    while (not handle.is_seed()):
        s = handle.status()

        progress = s.progress * 100

        # Update the progress bar and the status text.
        progress_bar.progress(progress / 100)
        
        if s.download_rate > 0:
            time_left = (s.total_wanted - s.total_done) / s.download_rate
            eta = str(timedelta(seconds=int(time_left)))
            status_details = (
                f'''Download progress: {progress:.2f}% - Peers: {s.num_peers} - Time left: {eta}'''
            )
        else:
            status_details = f'Download progress: {progress:.2f}% - Peers: {s.num_peers} - '
        
        status_text.text(status_details)

        time.sleep(1)

    # Clear out the progress bar, status, and details
    progress_bar.empty()
    status_text.empty()
    detail_text.empty()

    # Display success message
    st.success('Downloaded successfully!')

def download_torrent_file(torrent_file, save_path):
    ses = lt.session({'listen_interfaces': '0.0.0.0:6881'})
    ses.start_dht()
    params = {'save_path': save_path}
    info = lt.torrent_info(torrent_file)
    handle = ses.add_torrent({'ti': info, 'save_path': save_path})
    
    progress_bar = st.progress(0)
    status_text = st.empty()
    detail_text = st.empty()
    
    while not handle.is_seed():
        s = handle.status()
        
        progress = s.progress * 100  # Convert fractional progress to percentage
        
        # Update the progress bar and the status text
        progress_bar.progress(progress / 100)
        
        if s.download_rate > 0:
            time_left = (s.total_wanted - s.total_done) / s.download_rate
            eta = str(timedelta(seconds=int(time_left)))
            status_details = (
                f"Download progress: {progress:.2f}% - Peers: {s.num_peers} - Time left: {eta}"
            )
        else:
            status_details = f"Download progress: {progress:.2f}% - Peers: {s.num_peers} - "
        
        status_text.text(status_details)
        
        time.sleep(1)
    
    # Clear out the progress bar and text elements
    progress_bar.empty()
    status_text.empty()
    detail_text.empty()
    
    # Display success message
    st.success('Torrent downloaded successfully!')

#!/usr/bin/env python
import os
import json
from google.auth.transport.requests import AuthorizedSession
from google.oauth2.credentials import Credentials

# Function to read credentials from tokens.json
def read_credentials():
    with open('tokens.json', 'r') as token_file:
        token_data = json.load(token_file)
        credentials = Credentials(
            token=token_data['access_token'],
            refresh_token=token_data['refresh_token'],
            token_uri=token_data['token_uri'],
            client_id=token_data['client_id'],
            client_secret=token_data['client_secret'],
            scopes=token_data['scopes']
        )
    return credentials

# Function to save credentials back to tokens.json
def store_token(credentials):
    with open('tokens.json', 'w') as token_file:
        token_data = {
            'access_token': credentials.token,
            'refresh_token': credentials.refresh_token,
            'token_uri': credentials.token_uri,
            'client_id': credentials.client_id,
            'client_secret': credentials.client_secret,
            'scopes': credentials.scopes,
        }
        json.dump(token_data, token_file)

# Function to get an authorized session
def get_authed_session():
    credentials = read_credentials()
    if not credentials or not credentials.valid:
        if credentials and credentials.expired and credentials.refresh_token:
            credentials.refresh(AuthorizedSession(credentials))
            store_token(credentials)
    return AuthorizedSession(credentials)

# Function to upload a file
def upload_file(authed_session, file_path):
    headers = {
        'Content-type': 'application/octet-stream',
        'X-Goog-Upload-File-Name': os.path.basename(file_path),
        'X-Goog-Upload-Protocol': 'raw',
    }
    with open(file_path, 'rb') as f:
        response = authed_session.post('https://photoslibrary.googleapis.com/v1/uploads', headers=headers, data=f)
    if response.status_code == 200:
        upload_token = response.content.decode()
        body = {
            'newMediaItems': [
                {
                    'simpleMediaItem': {
                        'uploadToken': upload_token
                    }
                }
            ]
        }
        response = authed_session.post('https://photoslibrary.googleapis.com/v1/mediaItems:batchCreate', json=body)
        return response.status_code == 200
    return False

def find_mp4_in_directory(directory):
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith('.mp4'):
                return os.path.join(root, file)
            if file.endswith('.mkv'):
                return os.path.join(root, file)
            if file.endswith('.webm'):
                return os.path.join(root, file)
    return None

# Main function to handle the workflow
def main():
    # Get an authorized session
    authed_session = get_authed_session()

    # Specify the file path to upload
    file_path = '/content/file.mp4'  # Replace with your actual file path
    # Check if file_path is a directory, if so, find the .mp4 file within it
    if os.path.isdir(file_path):
        mp4_file_path = find_mp4_in_directory(file_path)
        if mp4_file_path is None:
            st.error("No MP4 file found in the directory.")
            return
        else:
            file_path = mp4_file_path
    # Upload the file
    if upload_file(authed_session, file_path):
        st.success("File uploaded successfully.")
        os.remove('/content/tokens.json')
        if os.path.isfile('/content/file.mp4'):
            os.remove('/content/file.mp4')
        if os.path.isdir('/content/file.mp4'):
            shutil.rmtree('/content/file.mp4')
    else:
        print("Failed to upload file.")
        st.error('Upload fail check your link again')

# Title of the web app
st.title('Torrent To Google Photos')

# Small text below the title
st.caption('Project by Sujal')

# Menu for selecting the input type
input_type = st.radio("Select the type of input:", ('Torrent File', 'Magnetic Link', 'Direct Link'))

# Initialize variables to None for later use
uploaded_file = None
input_link = None

# Input field based on the selected input type
if input_type == 'Torrent File':
    uploaded_file = st.file_uploader("Choose a file")
elif input_type in ['Magnetic Link', 'Direct Link']:
    input_link = st.text_input("Enter the link here:")

# Custom-styled "Auth" button
auth_button_html = """
<style>
    .custom-auth-button {
        cursor: pointer;
        font-size: 16px;
        color: white; /* Text color is white by default */
        background-color: rgb(19, 23, 32);
        padding: 4px 12px;
        border-radius: 8px;
        border: 1px solid rgba(250, 250, 250, 0.2);
        display: inline-block;
        text-align: center;
        min-width: 100px;
        text-decoration: none; /* No underline */
        transition: color 0.3s, border-color 0.3s; /* Smooth transition for colors */
    }
    .custom-auth-button:hover, .custom-auth-button:active {
        color: rgb(255, 75, 75); /* Text color changes to red on hover or click */
        border-color: rgb(255, 75, 75); /* Border color changes to red on hover or click */
    }
</style>

<a class="custom-auth-button" href="https://googleph.pagekite.me" target="_self">
    Authenticate
</a>
"""
st.markdown(auth_button_html, unsafe_allow_html=True)

st.markdown(' ')

# Display a clickable link for authentication only if not already authenticated
if check_for_auth_param():
    st.success("Authentication successful!")

if st.button('Download To Server⬇️'):
    if input_type == "Direct Link":
        st.success('Download started successfully!')
        download(url=input_link, path='/content/file.mp4')
    elif input_type == "Magnetic Link":
        st.success('Download started successfully!')
        st.toast('In torrent, download speed depends on peers not the server. For faster speed use direct link', icon='⚠️')
        download_magnet(input_link, '/content/file.mp4')
    elif input_type == "Torrent File" and uploaded_file is not None:
        st.success('Download started successfully!')
        st.toast('In torrent, download speed depends on peers not the server. For faster speed use direct link', icon='⚠️')
        with open('/content/temp.torrent', 'wb') as f:
            f.write(uploaded_file.getvalue())
        download_torrent_file('/content/temp.torrent', '/content/file.mp4')
        os.remove('/content/temp.torrent')  # Remove the temporary file once done
    else:
        st.error("Please select the download type!")
    
if st.button('Upload To Photos⬆️'):
    st.success('Uploading')
    main()
