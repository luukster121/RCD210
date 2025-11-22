import serial
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import time

# === Spotify instellingen ===
sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
    client_id="1fa790663be74563bf648f61f9baf4f7",
    client_secret="0c3f8e9fb80a4bca9e0ce00eddb6fdc0",
    redirect_uri="http://127.0.0.1:8080",
    scope="user-modify-playback-state user-read-playback-state"
))

# === Serial instellingen voor Arduino ===
ser = serial.Serial('/dev/ttyACM0', 9600, timeout=1)
time.sleep(2)  # even wachten tot Arduino reset voltooid is

# === Volume cache ===
volume = 50
sp.volume(volume)

print("Spotify controller gestrart...")

while True:
    line = ser.readline().decode().strip()
    if not line:
        continue

    print("Ontvangen:", line)

    # === Rotary: UP / DOWN ===
    if line == "UP":
        volume = min(100, volume + 2)
        sp.volume(volume)
        print("Volume:", volume)

    elif line == "DOWN":
        volume = max(0, volume - 2)
        sp.volume(volume)
        print("Volume:", volume)

    # === MUTE ===
    elif line == "MUTE":
        if volume > 0:
            last_volume = volume
            volume = 0
        else:
            volume = last_volume
        sp.volume(volume)
        print("Mute toggle →", volume)

    # === Play/pause ===
    elif line == "PLAY":
        state = sp.current_playback()
        if state and state["is_playing"]:
            sp.pause_playback()
        else:
            sp.start_playback()

    # === Vorig nummer ===
    elif line == "PREV":
        sp.previous_track()

    # === Volgend nummer ===
    elif line == "NEXT":
        sp.next_track()

    # === Spotify openen op PC ===
    elif line == "SPOTIFY":
        # Openen op PC via Connect-device
        devices = sp.devices()
        for d in devices["devices"]:
            if "computer" in d["name"].lower() or d["type"] == "Computer":
                sp.transfer_playback(device_id=d["id"], force_play=False)
                print("Spotify overgenomen op PC:", d["name"])

    time.sleep(0.05)
