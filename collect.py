# file: spotify_to_gsheet.py

import os
import datetime
import time
import pyautogui
import pyperclip
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# ========== CONFIGURATION ==========
SPOTIFY_CLIENT_ID = 'your_spotify_client_id'
SPOTIFY_CLIENT_SECRET = 'your_spotify_client_secret'
SPOTIFY_REDIRECT_URI = 'http://localhost:8888/callback'
PLAYLIST_ID = 'spotify:playlist:YOUR_PLAYLIST_ID'

SCOPE = ['https://spreadsheets.google.com/feeds',
         'https://www.googleapis.com/auth/drive']
GOOGLE_SHEET_NAME = 'Spotify Playlist Log'

CREDENTIALS_FILE = 'path/to/google-service-account.json'

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

# ========== HELPER FUNCTIONS ==========


def get_all_tracks(playlist_id):
    results = sp.playlist_items(playlist_id, additional_types=['track'])
    tracks = results['items']

    while results['next']:
        results = sp.next(results)
        tracks.extend(results['items'])

    return tracks


def scrape_added_by(index):
    # Scroll to specific row if needed (manually adjust coordinates)
    y_start = 250 + index * 70  # tune based on resolution & row height
    pyautogui.moveTo(300, y_start)
    pyautogui.click()
    time.sleep(0.2)

    # Use right-click or shortcut to focus UI line
    pyautogui.hotkey('ctrl', 'c')
    time.sleep(0.2)

    text = pyperclip.paste()
    if "Added by" in text:
        try:
            return text.split("Added by")[-1].strip().split("\n")[0]
        except:
            return "UNKNOWN"
    return "UNKNOWN"

# ========== MAIN ==========


def main():
    tracks = get_all_tracks(PLAYLIST_ID)

    for idx, item in enumerate(tracks):
        track = item['track']
        added_at = item['added_at']
        title = track['name']
        artist = ', '.join([a['name'] for a in track['artists']])
        url = track['external_urls']['spotify']

        contributor = scrape_added_by(idx)
        log_time = datetime.datetime.now().isoformat()

        row = [title, artist, url, contributor, added_at, log_time, 'No']
        ws.append_row(row)
        time.sleep(1)


if __name__ == '__main__':
    main()
