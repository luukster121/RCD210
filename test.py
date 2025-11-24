from flask import Flask, jsonify, request, redirect
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import requests

# ===============================
# Configuratie
# ===============================
CLIENT_ID = "1fa790663be74563bf648f61f9baf4f7"
CLIENT_SECRET = "53a6c19c203c4022aa99e33dad9a70d8"
REDIRECT_URI = "http://127.0.0.1:5000/callback"
SCOPE = "user-read-playback-state user-modify-playback-state user-read-currently-playing,user-read-currently-playing,user-modify-playback-state"

app = Flask(__name__)

sp_oauth = SpotifyOAuth(client_id=CLIENT_ID,
                        client_secret=CLIENT_SECRET,
                        redirect_uri=REDIRECT_URI,
                        scope=SCOPE,
                        cache_path=".spotify_token_cache")

# ===============================
# Login / Auth
# ===============================
@app.route("/")
def login():
    auth_url = sp_oauth.get_authorize_url()
    return redirect(auth_url)

@app.route("/callback")
def callback():
    code = request.args.get("code")
    token_info = sp_oauth.get_access_token(code, as_dict=False)
    return "Spotify gekoppeld!"

# ===============================
# Huidige track info
# ===============================
@app.route("/track")
def get_track():
    sp = spotipy.Spotify(auth_manager=sp_oauth)
    try:
        current = sp.current_playback()
        if current is None or current["item"] is None:
            return jsonify({"track": "Geen nummer", "artist": "Geen artiest", "album_art": None})

        item = current["item"]
        track_name = item["name"]
        artist_name = item["artists"][0]["name"]
        album_art_url = item["album"]["images"][0]["url"] if item["album"]["images"] else None

        return jsonify({
            "track": track_name,
            "artist": artist_name,
            "album_art": album_art_url
        })
    except Exception as e:
        print("Fout bij ophalen track:", e)
        return jsonify({"track": "Geen nummer", "artist": "Geen artiest", "album_art": None})

# ===============================
# Player controls
# ===============================
@app.route("/next", methods=["POST"])
def next_track():
    sp = spotipy.Spotify(auth_manager=sp_oauth)
    sp.next_track()
    return "ok"

@app.route("/prev", methods=["POST"])
def prev_track():
    sp = spotipy.Spotify(auth_manager=sp_oauth)
    sp.previous_track()
    return "ok"

@app.route("/playpause", methods=["POST"])
def play_pause():
    sp = spotipy.Spotify(auth_manager=sp_oauth)
    current = sp.current_playback()
    if current and current["is_playing"]:
        sp.pause_playback()
    else:
        sp.start_playback()
    return "ok"

# ===============================
# Volume control
# ===============================
@app.route("/volume_up", methods=["POST"])
def volume_up():
    sp = spotipy.Spotify(auth_manager=sp_oauth)
    current = sp.current_playback()
    if current:
        current_volume = current['device']['volume_percent']
        new_volume = min(current_volume + 5, 100)
        sp.volume(new_volume)
    return "ok"

@app.route("/volume_down", methods=["POST"])
def volume_down():
    sp = spotipy.Spotify(auth_manager=sp_oauth)
    current = sp.current_playback()
    if current:
        current_volume = current['device']['volume_percent']
        new_volume = max(current_volume - 5, 0)
        sp.volume(new_volume)
    return "ok"

# ===============================
# Album art ophalen
# ===============================
@app.route("/album_art")
def album_art():
    sp = spotipy.Spotify(auth_manager=sp_oauth)
    current = sp.current_playback()
    if current is None or current["item"] is None:
        return "Geen afbeelding", 404
    url = current["item"]["album"]["images"][0]["url"]
    resp = requests.get(url)
    return resp.content, 200, {"Content-Type": "image/png"}

@app.route("/volume_set/<int:vol>", methods=["POST"])
def volume_set(vol):
    sp = spotipy.Spotify(auth_manager=sp_oauth)
    vol = max(0, min(vol, 100))
    try:
        sp.volume(vol)
    except Exception as e:
        print("Volume set error:", e)
    return "ok"


# ===============================
# Start server
# ===============================
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
