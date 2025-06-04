# file: spotify_to_gsheet.py

from dotenv import load_dotenv
import os
import datetime
import time
import pyautogui
import pyperclip
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# Load environment variables from .env file
load_dotenv()
# ========== CONFIGURATION ==========
SPOTIFY_CLIENT_ID = os.getenv('SPOTIFY_CLIENT_ID')
SPOTIFY_CLIENT_SECRET = os.getenv('SPOTIFY_CLIENT_SECRET')
SPOTIFY_REDIRECT_URI = os.getenv('SPOTIFY_REDIRECT_URI')
PLAYLIST_ID = os.getenv('PLAYLIST_ID')
# Load SCOPE and split it into a list
SCOPE = os.getenv('SCOPE').split(',')
GOOGLE_SHEET_NAME = os.getenv('GOOGLE_SHEET_NAME')

CREDENTIALS_FILE = 'creds.json'

# ========== INIT CLIENTS ==========
sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
    client_id=SPOTIFY_CLIENT_ID,
    client_secret=SPOTIFY_CLIENT_SECRET,
    redirect_uri=SPOTIFY_REDIRECT_URI,
    scope='playlist-read-private'))

credentials = ServiceAccountCredentials.from_json_keyfile_name(
    CREDENTIALS_FILE, SCOPE)
gs = gspread.authorize(credentials)
ws = gs.open(GOOGLE_SHEET_NAME).sheet1

# ========== HELPERS ==========


def get_all_tracks(playlist_id):
    results = sp.playlist_items(playlist_id, additional_types=['track'])
    tracks = results['items']

    while results['next']:
        results = sp.next(results)
        tracks.extend(results['items'])

    return tracks


def scrape_added_by(index):
    y_start = 250 + index * 70
    pyautogui.moveTo(300, y_start)
    pyautogui.click()
    time.sleep(0.2)

    pyautogui.hotkey('ctrl', 'c')
    time.sleep(0.2)

    text = pyperclip.paste()
    if "Added by" in text:
        try:
            return text.split("Added by")[-1].strip().split("\n")[0]
        except:
            return "UNKNOWN"
    return "UNKNOWN"


def get_logged_urls():
    rows = ws.get_all_records()
    return set(row['Spotify URL'] for row in rows)

# ========== MAIN ==========


def main():
    logged_urls = get_logged_urls()
    tracks = get_all_tracks(PLAYLIST_ID)

    for idx, item in enumerate(tracks):
        track = item['track']
        url = track['external_urls']['spotify']
        if url in logged_urls:
            continue

        added_at = item['added_at']
        title = track['name']
        artist = ', '.join([a['name'] for a in track['artists']])
        contributor = scrape_added_by(idx)
        log_time = datetime.datetime.now().isoformat()

        row = [title, artist, url, contributor, added_at, log_time, 'No']
        ws.append_row(row)
        time.sleep(1)


if __name__ == '__main__':
    main()
