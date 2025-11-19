import serial
import time
import subprocess
from ctypes import POINTER, cast
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
import win32api
import win32con

# -------------------- Arduino --------------------
# ⚠️ Pas de COM-poort aan naar jouw Arduino (bijv. COM4)
arduino = serial.Serial()
arduino.baudrate = 9600
arduino.timeout = 1

# Zoek automatisch de Arduino
import serial.tools.list_ports
ports = serial.tools.list_ports.comports()
for p in ports:
    if "Arduino" in p.description or "CH340" in p.description:
        arduino.port = p.device
        break

arduino.open()

# -------------------- Volume-interface --------------------
device = AudioUtilities.GetSpeakers()
volume = device.EndpointVolume
volume = cast(volume, POINTER(IAudioEndpointVolume))

# -------------------- Functies --------------------
def get_spotify_session():
    """Zoekt de Spotify audio-session en geeft de SimpleAudioVolume terug."""
    sessions = AudioUtilities.GetAllSessions()
    for session in sessions:
        if session.Process and session.Process.name().lower() == "spotify.exe":
            return session.SimpleAudioVolume
    return None

def change_spotify_volume(delta):
    """Pas alleen Spotify-volume aan."""
    spotify = get_spotify_session()
    if not spotify:
        print("Spotify audio niet gevonden.")
        return

    current = spotify.GetMasterVolume()
    new = min(max(current + delta, 0.0), 1.0)
    spotify.SetMasterVolume(new, None)
    print(f"Spotify volume: {new:.2f}")

def toggle_spotify_mute():
    """Mute/unmute alleen Spotify."""
    spotify = get_spotify_session()
    if not spotify:
        print("Spotify audio niet gevonden.")
        return

    muted = spotify.GetMute()
    spotify.SetMute(not muted, None)
    print("Spotify mute:", not muted)

def change_volume(delta):
    """Verhoog of verlaag mastervolume"""
    current = volume.GetMasterVolumeLevelScalar()
    new = min(max(current + delta, 0.0), 1.0)
    volume.SetMasterVolumeLevelScalar(new, None)

def toggle_mute():
    """Mute/unmute mastervolume"""
    volume.SetMute(not volume.GetMute(), None)

def open_spotify():
    """Start Spotify"""
    try:
        subprocess.Popen([
            r"C:\Users\Luukster121\AppData\Roaming\Spotify\Spotify.exe"
        ])
    except Exception as e:
        print("Fout bij openen Spotify:", e)

def prev_track():
    """Vorige nummer"""
    win32api.keybd_event(0xB1, 0, 0, 0)  # VK_MEDIA_PREV_TRACK
    win32api.keybd_event(0xB1, 0, win32con.KEYEVENTF_KEYUP, 0)

def next_track():
    """Volgende nummer"""
    win32api.keybd_event(0xB0, 0, 0, 0)  # VK_MEDIA_NEXT_TRACK
    win32api.keybd_event(0xB0, 0, win32con.KEYEVENTF_KEYUP, 0)

def play_pause():
    """Play/pause mediatoets"""
    win32api.keybd_event(0xB3, 0, 0, 0)  # VK_MEDIA_PLAY_PAUSE
    win32api.keybd_event(0xB3, 0, win32con.KEYEVENTF_KEYUP, 0)

# -------------------- Hoofdlus --------------------
print("Verbonden met Arduino. Klaar voor input...")

while True:
    if arduino.in_waiting > 0:
        line = arduino.readline().decode('utf-8').strip()

        if line == "UP":
            change_spotify_volume(0.05)
        elif line == "DOWN":
            change_spotify_volume(-0.05)
        elif line == "MUTE":
            toggle_spotify_mute()
        elif line == "SPOTIFY":
            open_spotify()
        elif line == "PREV":
            prev_track()
        elif line == "NEXT":
            next_track()
        elif line == "PLAY":
            play_pause()
