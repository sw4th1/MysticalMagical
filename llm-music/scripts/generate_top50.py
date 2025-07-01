import base64
import requests
import json
from flask import Flask, request, redirect, jsonify

# Spotify Credentials
CLIENT_ID = '1150ef5ecf204b25abb11b03dd0874fe'
CLIENT_SECRET = 'cd9b83c2ce8e420d990f8b4ed4162bd2'
REDIRECT_URI = 'http://127.0.0.1:3000/callback'

app = Flask(__name__)
access_token = None
USER_JSON_PATH = "user_top_tracks.json"

@app.route('/')
def login():
    return redirect(
        'https://accounts.spotify.com/authorize'
        '?response_type=code'
        f'&client_id={CLIENT_ID}'
        f'&redirect_uri={REDIRECT_URI}'
        '&scope=user-top-read'
    )

@app.route('/callback')
def callback():
    global access_token
    code = request.args.get('code')

    auth_header = base64.b64encode(f'{CLIENT_ID}:{CLIENT_SECRET}'.encode()).decode()
    headers = {
        'Authorization': f'Basic {auth_header}',
        'Content-Type': 'application/x-www-form-urlencoded'
    }
    data = {
        'grant_type': 'authorization_code',
        'code': code,
        'redirect_uri': REDIRECT_URI
    }

    res = requests.post('https://accounts.spotify.com/api/token', headers=headers, data=data)
    if res.status_code != 200:
        return jsonify({"error": "Token exchange failed", "details": res.json()})

    access_token = res.json().get('access_token')
    return get_top_tracks()

def get_top_tracks():
    headers = {'Authorization': f'Bearer {access_token}'}
    res = requests.get(
        'https://api.spotify.com/v1/me/top/tracks?limit=50&time_range=short_term',
        headers=headers
    )
    if res.status_code != 200:
        return jsonify({"error": "Failed to fetch top tracks", "status": res.status_code})

    tracks = res.json().get('items', [])
    if not tracks:
        return jsonify({"error": "No top tracks found"})

    # Load or initialize the file as a list
    try:
        with open(USER_JSON_PATH, "r") as file:
            user_data = json.load(file)
            if not isinstance(user_data, list):
                user_data = []
    except (FileNotFoundError, json.JSONDecodeError):
        user_data = []

    # Generate new user ID
    new_user_id = str(len(user_data) + 1)

    # Track data dictionary
    track_dict = {}
    for track in tracks:
        track_id = track.get("id")
        track_name = track.get("name")
        artist_names = [artist.get("name") for artist in track.get("artists", [])]
        uri = track.get("uri")
        images = track.get("album", {}).get("images", [])
        image_url = next((img.get("url") for img in images if img.get("height") == 300), images[0]["url"] if images else "N/A")

        track_dict[track_id] = {
            "name": track_name,
            "artist_names": artist_names,
            "uri": uri,
            "image_url": image_url
        }

    # Add new user block
    user_data.append({
        "user_id": new_user_id,
        "tracks": track_dict
    })

    # Save updated file
    with open(USER_JSON_PATH, "w") as file:
        json.dump(user_data, file, indent=2)

    # Return HTML response with user's data
    return (
        f"<h2>✅ User {new_user_id}'s Top Tracks</h2>"
        f"<pre>{json.dumps({'user_id': new_user_id, 'tracks': track_dict}, indent=2)}</pre>"
    )

if __name__ == '__main__':
    print("✅ Go to http://127.0.0.1:3000 in your browser to begin Spotify login.")
    app.run(port=3000, debug=True)
