import requests

# Constants
ACCESS_TOKEN = 'e9e55e345a0149749e73a7d958746e32' 
DEVICE_ID = 'ba981595a4c3a0c5deabaa84688af0dd29d308ac'
SPOTIFY_QUEUE_ENDPOINT = 'https://api.spotify.com/v1/me/player/queue'

def add_tracks_to_queue(track_uris):
    access_token=ACCESS_TOKEN
    headers = {
        "Authorization": f"Bearer {access_token}"
    }

    for uri in track_uris:
        params = {
            "uri": uri,
            "device_id": DEVICE_ID
        }

        response = requests.post(SPOTIFY_QUEUE_ENDPOINT, headers=headers, params=params)

        if response.status_code == 204:
            print(f"Added to queue: {uri}")
        else:
            print(f"Failed to add {uri}. Status: {response.status_code} | Response: {response.text}")

