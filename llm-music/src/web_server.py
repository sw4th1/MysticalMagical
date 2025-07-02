# Python 3 server example
from http.server import SimpleHTTPRequestHandler, HTTPServer
import ssl
import time
import json
import os
import sys
import base64
import requests
import webbrowser
from urllib.parse import urlencode, parse_qs
import threading

# --- Spotify API Configuration ---
CLIENT_ID = 'e9e55e345a0149749e73a7d958746e32'
CLIENT_SECRET = 'fc7624fb20974c04bd35a32f79cce7d4'
# IMPORTANT: This REDIRECT_URI must match exactly what you set in your Spotify Developer Dashboard.
# Since your web server is running locally, we'll use a local callback for initial authorization.
# If 'https://blendjam.vercel.app/callback' is for your deployed app, you'll need two redirect URIs
# in your Spotify App settings: one for local development and one for production.
REDIRECT_URI = 'https://localhost:8080/callback' # Changed to match your server's host and port
AUTH_URL = 'https://accounts.spotify.com/authorize'
TOKEN_URL = 'https://accounts.spotify.com/api/token'
# Base URL for Spotify Web API. Add a specific endpoint like '/v1/me/player/queue' for the queue.
BASE_URL = 'https://api.spotify.com/v1'

# Scopes needed for playback control and adding to queue
# 'user-modify-playback-state' is essential for adding to queue
# 'user-read-playback-state' and 'user-read-currently-playing' are good for debugging/getting device IDs
SCOPE = 'user-modify-playback-state user-read-playback-state user-read-currently-playing'

# --- Global variables for token storage ---
# These will be populated after successful authorization
GLOBAL_ACCESS_TOKEN = None
GLOBAL_REFRESH_TOKEN = None
GLOBAL_TOKEN_EXPIRY_TIME = 0 # Unix timestamp of when the token expires

# Flag to signal when the authorization callback has been handled
auth_callback_received = threading.Event()

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Assuming these are local imports, ensure paths are correct
from scripts.process_user_data import reformat_spotify_data
from scripts.make_haystack_docs import convert_to_haystack_docs
from src.run_query import run_query_loop
# We'll modify add_tracks_to_queue or ensure it takes an access token
# from scripts.add_to_queue import add_tracks_to_queue

hostName = "localhost"
serverPort = 8080

context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
# Ensure cert.pem and key.pem are in the same directory as this script, or provide full paths
context.load_cert_chain(certfile="cert.pem", keyfile="key.pem")

# --- Token Management Functions ---

def exchange_code_for_tokens(code):
    """Exchanges an authorization code for access and refresh tokens."""
    payload = {
        'grant_type': 'authorization_code',
        'code': code,
        'redirect_uri': REDIRECT_URI,
    }
    headers = {
        'Authorization': 'Basic ' + base64.b64encode(f"{CLIENT_ID}:{CLIENT_SECRET}".encode()).decode(),
        'Content-Type': 'application/x-www-form-urlencoded'
    }
    print("Exchanging authorization code for tokens...")
    response = requests.post(TOKEN_URL, data=payload, headers=headers)
    return response.json()

def refresh_access_token():
    """Refreshes the access token using the refresh token."""
    global GLOBAL_ACCESS_TOKEN, GLOBAL_REFRESH_TOKEN, GLOBAL_TOKEN_EXPIRY_TIME
    if not GLOBAL_REFRESH_TOKEN:
        print("No refresh token available. Cannot refresh.")
        return False

    payload = {
        'grant_type': 'refresh_token',
        'refresh_token': GLOBAL_REFRESH_TOKEN,
    }
    headers = {
        'Authorization': 'Basic ' + base64.b64encode(f"{CLIENT_ID}:{CLIENT_SECRET}".encode()).decode(),
        'Content-Type': 'application/x-www-form-urlencoded'
    }
    print("Attempting to refresh access token...")
    response = requests.post(TOKEN_URL, data=payload, headers=headers)
    token_data = response.json()

    if 'access_token' in token_data:
        GLOBAL_ACCESS_TOKEN = token_data['access_token']
        # Spotify may or may not return a new refresh token. Use the old one if not.
        GLOBAL_REFRESH_TOKEN = token_data.get('refresh_token', GLOBAL_REFRESH_TOKEN)
        expires_in = token_data.get('expires_in', 3600) # Default to 1 hour
        GLOBAL_TOKEN_EXPIRY_TIME = time.time() + expires_in
        print("Access token refreshed successfully.")
        return True
    else:
        print(f"Failed to refresh token: {token_data.get('error_description', token_data)}")
        return False

def ensure_access_token():
    """Ensures a valid access token is available, refreshing if necessary."""
    global GLOBAL_ACCESS_TOKEN
    # Refresh 60 seconds before actual expiry to avoid race conditions
    if GLOBAL_ACCESS_TOKEN and time.time() < GLOBAL_TOKEN_EXPIRY_TIME - 60:
        print("Access token is valid and not expired.")
        return True
    elif GLOBAL_REFRESH_TOKEN:
        print("Access token expired or about to expire. Attempting to refresh...")
        return refresh_access_token()
    else:
        print("No valid access token or refresh token. Please authorize your Spotify account.")
        return False

# --- Spotify API Interaction for Adding to Queue ---
# You can move this into scripts/add_to_queue.py if it's not already defined there
def add_tracks_to_queue(track_uris, access_token):
    """
    Adds a list of track URIs to the user's Spotify playback queue.
    Requires 'user-modify-playback-state' scope and a Premium account.
    """
    if not access_token:
        print("Error: No access token provided for adding to queue.")
        return False

    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json' # Not strictly needed for GET but good practice
    }
    add_queue_url = f"{BASE_URL}/me/player/queue"

    success = True
    for uri in track_uris:
        params = {
            'uri': uri
        }
        # Optional: You can get the device_id from '/me/player/devices' or '/me/player'
        # For simplicity, we'll let Spotify choose the active device.
        # if device_id:
        #    params['device_id'] = device_id

        print(f"Attempting to add {uri} to queue...")
        response = requests.post(add_queue_url, headers=headers, params=params)

        if response.status_code == 204: # 204 No Content means success for this endpoint
            print(f"Successfully added {uri} to your Spotify queue.")
        else:
            success = False
            print(f"Failed to add {uri} to queue. Status Code: {response.status_code}")
            try:
                error_data = response.json()
                print(f"Error details: {json.dumps(error_data, indent=2)}")
                if response.status_code == 403 and "Premium required" in str(error_data):
                    print("Note: Adding to queue requires a Spotify Premium account.")
                elif response.status_code == 401:
                    print("Possible token expiration or invalid scope. Attempting refresh on next call.")
            except json.JSONDecodeError:
                print(f"Raw response: {response.text}")
    return success

class MyServer(SimpleHTTPRequestHandler):
    def _set_response(self, status_code=200, content_type='text/html'):
        self.send_response(status_code)
        self.send_header('Content-type', content_type)
        self.end_headers()

    def end_headers(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', '*')
        self.send_header('Access-Control-Allow-Headers', '*')
        self.send_header('Cache-Control', 'no-store, no-cache, must-revalidate')
        return super(MyServer, self).end_headers()

    def do_GET(self):
        global GLOBAL_ACCESS_TOKEN, GLOBAL_REFRESH_TOKEN, GLOBAL_TOKEN_EXPIRY_TIME

        if self.path.startswith('/callback'):
            query_params = parse_qs(self.path.split('?', 1)[1]) if '?' in self.path else {}

            if 'code' in query_params:
                auth_code = query_params['code'][0]
                print(f"Received authorization code: {auth_code}")

                token_data = exchange_code_for_tokens(auth_code)
                if token_data and 'access_token' in token_data:
                    GLOBAL_ACCESS_TOKEN = token_data['access_token']
                    GLOBAL_REFRESH_TOKEN = token_data.get('refresh_token')
                    expires_in = token_data.get('expires_in', 3600)
                    GLOBAL_TOKEN_EXPIRY_TIME = time.time() + expires_in
                    print("Access Token and Refresh Token obtained successfully.")
                    self._set_response(200)
                    self.wfile.write(b"Authorization successful! You can close this window and return to the script console.")
                else:
                    self._set_response(500)
                    self.wfile.write(b"Failed to get access token from Spotify.")
                    print(f"Failed to get access token: {token_data}")
                auth_callback_received.set() # Signal that callback is handled
            elif 'error' in query_params:
                error = query_params['error'][0]
                print(f"Authorization failed: {error}")
                self._set_response(400)
                self.wfile.write(f"Authorization failed: {error}".encode('utf-8'))
                auth_callback_received.set() # Signal even if error
            else:
                self._set_response(400)
                self.wfile.write(b"Invalid callback request.")
            return

        # Default GET request handling
        super().do_GET() # Use the default SimpleHTTPRequestHandler for other GET requests

    def do_POST(self):
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        print("Raw POST data:", post_data) # Debugging: print raw data
        
        try:
            # Decode using utf-8 first, then replace single quotes if present
            decoded_data = post_data.decode('utf8')
            if decoded_data.startswith('{') and decoded_data.endswith('}'):
                # Assuming valid JSON, no need to replace single quotes if they don't break JSON spec
                data = json.loads(decoded_data)
            else:
                # Fallback for potentially malformed JSON with single quotes
                my_json = decoded_data.replace("'", '"')
                data = json.loads(my_json)
            print("Parsed POST data:", data)

        except json.JSONDecodeError as e:
            print(f"JSONDecodeError: {e}")
            print(f"Attempted to decode: '{post_data}'")
            self._set_response(400)
            self.wfile.write(f"Invalid JSON in POST request: {e}".encode('utf-8'))
            return
        except Exception as e:
            print(f"An unexpected error occurred parsing POST data: {e}")
            self._set_response(500)
            self.wfile.write(f"Server error: {e}".encode('utf-8'))
            return

        type = data.get("type")
        if (type == "data"):
            new_data = data['payload']
            # Ensure 'llm-music\\data\\' path is correct relative to script execution
            data_file_path = os.path.join(os.getcwd(), 'llm-music', 'data', 'raw_data.json')
            if not os.path.exists(os.path.dirname(data_file_path)):
                os.makedirs(os.path.dirname(data_file_path)) # Create directory if it doesn't exist

            try:
                with open(data_file_path, 'r+') as file:
                    old_data = json.load(file)
                    old_data.append(new_data)
                    file.seek(0)
                    file.truncate(0)
                    json.dump(old_data, file, indent=4)
                reformat_spotify_data()
                convert_to_haystack_docs()
                self._set_response(200)
                self.wfile.write(b"Data processed successfully.")
            except FileNotFoundError:
                print(f"Error: raw_data.json not found at {data_file_path}. Creating new file.")
                with open(data_file_path, 'w') as file:
                    json.dump([new_data], file, indent=4)
                reformat_spotify_data()
                convert_to_haystack_docs()
                self._set_response(200)
                self.wfile.write(b"New data file created and processed.")
            except json.JSONDecodeError:
                print(f"Error: raw_data.json is not valid JSON at {data_file_path}. Please check its content.")
                self._set_response(500)
                self.wfile.write(b"Error: Data file corrupted.")

        elif (type == "remove"):
            user_id = data['payload']
            data_file_path = os.path.join(os.getcwd(), 'llm-music', 'data', 'raw_data.json')
            try:
                with open(data_file_path, 'r+') as file:
                    old_data = json.load(file)
                    new_data = [item for item in old_data if item["user_id"] != user_id]
                    file.seek(0)
                    file.truncate(0)
                    json.dump(new_data, file, indent=4)
                self._set_response(200)
                self.wfile.write(b"User data removed successfully.")
            except FileNotFoundError:
                print(f"Error: raw_data.json not found at {data_file_path}.")
                self._set_response(404)
                self.wfile.write(b"Error: Data file not found.")
            except json.JSONDecodeError:
                print(f"Error: raw_data.json is not valid JSON at {data_file_path}.")
                self._set_response(500)
                self.wfile.write(b"Error: Data file corrupted.")

        elif (type == "settings"):
            payload = data['payload']
            prompt = payload['filter']
            
            if not ensure_access_token():
                self._set_response(401, 'text/plain')
                self.wfile.write(b"Unauthorized: Spotify access token not available or expired. Please re-authorize.")
                return

            print(f"Running query for prompt: {prompt}")
            try:
                results = run_query_loop(prompt)
                if results:
                    # Pass the global access token to add_tracks_to_queue
                    print(f"Adding {len(results)} tracks to queue.")
                    if add_tracks_to_queue(results, GLOBAL_ACCESS_TOKEN):
                        self._set_response(200)
                        self.wfile.write(b"Tracks added to queue successfully.")
                    else:
                        self._set_response(500)
                        self.wfile.write(b"Failed to add tracks to queue.")
                else:
                    self._set_response(200) # Or 404 if no results is an error condition for you
                    self.wfile.write(b"No tracks found for the given prompt.")
            except Exception as e:
                print(f"Error processing settings or adding to queue: {e}")
                self._set_response(500)
                self.wfile.write(f"Server error during settings processing: {e}".encode('utf-8'))
        else:
            self._set_response(400)
            self.wfile.write(b"Unknown request type.")


    def do_OPTIONS(self):
        self.send_response(200)
        self.end_headers()    

if __name__ == "__main__":        
    webServer = HTTPServer((hostName, serverPort), MyServer)
    webServer.socket = context.wrap_socket(webServer.socket, server_side=True)
    
    print(f"Server started on https://{hostName}:{serverPort}")

    # Start the web server in a separate thread
    server_thread = threading.Thread(target=webServer.serve_forever)
    server_thread.daemon = True # Allows the main program to exit even if server is running
    server_thread.start()

    # --- Spotify Authorization Flow ---
    print("\n--- Spotify Authorization ---")
    authorize_params = {
        'response_type': 'code',
        'client_id': CLIENT_ID,
        'scope': SCOPE,
        'redirect_uri': REDIRECT_URI,
    }
    spotify_auth_url = f"{AUTH_URL}?{urlencode(authorize_params)}"

    print(f"Please open this URL in your browser to authorize your Spotify account:")
    print(spotify_auth_url)
    webbrowser.open(spotify_auth_url)

    # Wait until the callback handler has processed the authorization code
    print("\nWaiting for Spotify authorization callback...")
    auth_callback_received.wait() # This will block until .set() is called in do_GET
    
    if GLOBAL_ACCESS_TOKEN:
        print("\nSpotify authorization successful! Access token obtained.")
        print(f"Access Token: {GLOBAL_ACCESS_TOKEN[:20]}...") # Print first 20 chars for sanity
        print(f"Refresh Token: {GLOBAL_REFRESH_TOKEN[:20]}...")
        print(f"Token expires at: {time.ctime(GLOBAL_TOKEN_EXPIRY_TIME)}")
    else:
        print("\nSpotify authorization failed. Please check the console for errors.")
    
    print("\n--- Server Ready to Handle Requests ---")
    # Keep the main thread alive so the server thread can continue
    try:
        # A simple loop to keep the main thread running.
        # The web server is in a separate thread and will continue serving.
        while True:
            time.sleep(1) 
    except KeyboardInterrupt:
        print("\nShutting down server...")
        webServer.shutdown() # Shuts down the HTTPServer gracefully
        webServer.server_close()
        print("Server stopped.")