"""
Spotify MCP server.
Provides search, playback control, and status via the Spotify API.
"""
from __future__ import annotations

import os
import sys
from pathlib import Path

import spotipy
from spotipy.oauth2 import SpotifyOAuth
from dotenv import load_dotenv

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

# Load .env file explicitly so the subprocess gets the keys
load_dotenv(Path(__file__).resolve().parents[2] / ".env")

from mcp.server.fastmcp import FastMCP  # noqa: E402
from config.logger import get_logger  # noqa: E402

log = get_logger("tools.spotify")
mcp = FastMCP("spotify")

CLIENT_ID = os.environ.get("SPOTIFY_CLIENT_ID")
CLIENT_SECRET = os.environ.get("SPOTIFY_CLIENT_SECRET")
REDIRECT_URI = "http://127.0.0.1:8080/callback"
# The path where spotipy saves the cached token
CACHE_PATH = str(Path(__file__).resolve().parent / ".cache")

SCOPE = "user-read-playback-state user-modify-playback-state user-read-currently-playing playlist-read-private"


def get_spotify_client() -> spotipy.Spotify:
    if not CLIENT_ID or not CLIENT_SECRET:
        raise RuntimeError("Missing SPOTIFY_CLIENT_ID or SPOTIFY_CLIENT_SECRET in environment.")
    
    auth_manager = SpotifyOAuth(
        client_id=CLIENT_ID,
        client_secret=CLIENT_SECRET,
        redirect_uri=REDIRECT_URI,
        scope=SCOPE,
        cache_path=CACHE_PATH,
        open_browser=True
    )
    return spotipy.Spotify(auth_manager=auth_manager)


@mcp.tool()
def search_spotify(query: str, item_type: str = "track", max_results: int = 5) -> str:
    """
    Search for items on Spotify.
    item_type can be one of: 'track', 'album', 'artist', 'playlist'.
    """
    try:
        sp = get_spotify_client()
        results = sp.search(q=query, type=item_type, limit=max_results)
    except Exception as e:
        return f"Spotify search failed: {e}"

    lines = []
    
    if item_type == "track" and "tracks" in results:
        for i, t in enumerate(results["tracks"]["items"]):
            artists = ", ".join([a["name"] for a in t["artists"]])
            lines.append(f"{i+1}. {t['name']} by {artists} (URI: {t['uri']})")
    elif item_type == "artist" and "artists" in results:
        for i, a in enumerate(results["artists"]["items"]):
            lines.append(f"{i+1}. {a['name']} (URI: {a['uri']})")
    elif item_type == "album" and "albums" in results:
        for i, a in enumerate(results["albums"]["items"]):
            artists = ", ".join([ar["name"] for ar in a["artists"]])
            lines.append(f"{i+1}. {a['name']} by {artists} (URI: {a['uri']})")
    elif item_type == "playlist" and "playlists" in results:
        for i, p in enumerate(results["playlists"]["items"]):
            lines.append(f"{i+1}. {p['name']} (URI: {p['uri']})")
            
    if not lines:
        return f"No {item_type}s found for '{query}'."
        
    return "\n".join(lines)


@mcp.tool()
def play_track(track_uri: str) -> str:
    """
    Starts playing a specific Spotify track (requires active Spotify device).
    track_uri should look like 'spotify:track:XXXXX'.
    """
    try:
        sp = get_spotify_client()
        sp.start_playback(uris=[track_uri])
        return f"Started playing {track_uri}"
    except Exception as e:
        return f"Failed to play track: {e}. Make sure you have an active Spotify device running!"


@mcp.tool()
def pause_playback() -> str:
    """Pauses current Spotify playback."""
    try:
        sp = get_spotify_client()
        sp.pause_playback()
        return "Playback paused."
    except Exception as e:
        return f"Failed to pause: {e}"


@mcp.tool()
def get_current_track() -> str:
    """Gets the currently playing track on Spotify."""
    try:
        sp = get_spotify_client()
        current = sp.current_user_playing_track()
        if current and current.get("item"):
            t = current["item"]
            artists = ", ".join([a["name"] for a in t["artists"]])
            return f"Currently playing: {t['name']} by {artists}"
        return "Nothing is currently playing."
    except Exception as e:
        return f"Failed to get current track: {e}"


if __name__ == "__main__":
    log.info("Spotify MCP server starting.")
    mcp.run(transport="stdio")
