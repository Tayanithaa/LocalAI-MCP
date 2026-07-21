"""
Run this file once to authenticate with Spotify and save the token cache!
"""
import os
from pathlib import Path
from dotenv import load_dotenv
import spotipy
from spotipy.oauth2 import SpotifyOAuth

# Load the .env file from the project root
load_dotenv(Path(__file__).resolve().parents[2] / ".env")

CLIENT_ID = os.environ.get("SPOTIFY_CLIENT_ID")
CLIENT_SECRET = os.environ.get("SPOTIFY_CLIENT_SECRET")
REDIRECT_URI = "http://127.0.0.1:8080/callback"
CACHE_PATH = str(Path(__file__).resolve().parent / ".cache")
SCOPE = "user-read-playback-state user-modify-playback-state user-read-currently-playing playlist-read-private"

def main():
    if not CLIENT_ID or not CLIENT_SECRET:
        print("Error: Missing SPOTIFY_CLIENT_ID or SPOTIFY_CLIENT_SECRET in .env")
        return
        
    print("Starting Spotify authentication...")
    auth_manager = SpotifyOAuth(
        client_id=CLIENT_ID,
        client_secret=CLIENT_SECRET,
        redirect_uri=REDIRECT_URI,
        scope=SCOPE,
        cache_path=CACHE_PATH,
        open_browser=True
    )
    
    # This triggers the browser login and caches the token
    sp = spotipy.Spotify(auth_manager=auth_manager)
    user = sp.current_user()
    print(f"\nSuccess! Authenticated as {user.get('display_name')}.")
    print("The token is now cached. You can use the Spotify AI tools safely!")

if __name__ == "__main__":
    main()
