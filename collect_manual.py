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
SCOPE = os.getenv('SCOPE').split(',')
GOOGLE_SHEET_NAME = os.getenv('GOOGLE_SHEET_NAME')

CREDENTIALS_FILE = 'creds.json'
ROW_HEIGHT = 69.7804878  # height between tracks in pixels
SCROLL_DELAY = 1.0
SCROLL_AMOUNT = -750  # full page scroll amount

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
    print("Fetching all tracks from playlist...")
    print(f"Fetching from {playlist_id}")
    results = sp.playlist_items(playlist_id, additional_types=['track'])
    tracks = results['items']

    while results['next']:
        results = sp.next(results)
        tracks.extend(results['items'])

    print(f"Total tracks found: {len(tracks)}")
    return tracks


def ask_for_anchor():
    print("🖱️ Please move your mouse to the FIRST track's name and press Enter...")
    input("Press Enter when ready...")
    x, y = pyautogui.position()
    print(f"🎯 Anchor set at: ({x}, {y})")
    print("Starting in 2 seconds, go to the Spotify UI Added By column NOW!!!!")
    time.sleep(2)
    return x, y


def scrape_added_by(index, anchor_x, anchor_y):
    y_offset = anchor_y + index * ROW_HEIGHT
    print(f"Scraping 'Added by' at Y: {y_offset}")
    pyautogui.moveTo(anchor_x, y_offset)
    pyautogui.rightClick()
    time.sleep(1)  # Move back to 0.2

    # TODO: Get the scroll down to be after every right click and click sequence instead of after x songs.
    # Also, get it to click twice, once in the user user url spot and a second time if the song is added by a collaborator. Then use the one that is valid if either.
    # Move slightly to reach the 'Copy Link' option if it is the user user, move down farther
    pyautogui.moveRel(30, 50)
    time.sleep(1)  # Remove later
    pyautogui.click()
    time.sleep(0.2)

    text = pyperclip.paste()
    print(f"Clipboard URL: {text}")
    if "open.spotify.com/user/" in text:
        try:
            contributor = text.split("/user/")[-1].split("?")[0]
            print(f"Found contributor: {contributor}")
            return contributor
        except:
            return "UNKNOWN"
    return "UNKNOWN"


def get_logged_urls():
    print("Loading logged URLs from sheet...")
    rows = ws.get_all_records()
    urls = set(row['Spotify URL'] for row in rows)
    print(f"Logged URLs: {len(urls)}")
    return urls


def scroll_and_reset_to_anchor(anchor_x, anchor_y):
    pyautogui.moveTo(anchor_x, anchor_y)
    pyautogui.scroll(-1 * ROW_HEIGHT)
    time.sleep(SCROLL_DELAY)
    pyautogui.moveTo(anchor_x, anchor_y)
    time.sleep(0.5)


def calibrate_y_start():
    print("Calibration mode. Hover each song row and press Enter to print its Y position. Press Ctrl+C to stop.")
    try:
        while True:
            x, y = pyautogui.position()
            input(
                f"Current mouse Y: {y} at X: {x}. Move to next song and press Enter...")
    except KeyboardInterrupt:
        print("Calibration ended.")

# ========== MAIN ==========


def main():
    """Main function to log tracks from Spotify to Google Sheets."""
    print("Starting playlist logging script...")
    logged_urls = get_logged_urls()
    tracks = get_all_tracks(PLAYLIST_ID)
    for item in tracks:
        track = item['track']
        url = track['external_urls']['spotify']
        if url in logged_urls:
            print(f"Skipping already logged track: {url}")
            continue
        added_at = item['added_at']
        title = track['name']
        artist = '::'.join([a['name'] for a in track['artists']])
        release_date = track['album']['release_date']
        release_year = release_date.split('-')[0]  # Extract year

        popularity = track.get('popularity', 0)

        # Fill the Added By column with "UNKNOWN"
        contributor = "UNKNOWN"  # Placeholder for Added By
        print(f"Logging track: {title} by {artist}, Added By: {contributor}")
        log_time = datetime.datetime.now().isoformat()
        row = [
            title,
            artist,
            url,
            contributor,
            added_at,
            log_time,
            'No',             # Notified
            '',               # Cumulative Track Count (Google Sheet)
            '',               # Contributor Track Count (Google Sheet)
            '',               # Proportion of Total (Google Sheet)
            release_year,
            popularity
        ]

        print(f"Appending row: {row}")
        ws.append_row(row)
        # time.sleep(1)


if __name__ == '__main__':
    main()
