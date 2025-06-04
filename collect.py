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

# Define thresholds for dark and light pixels
# RGB values below this are considered dark
DARK_PIXEL_THRESHOLD = (70, 70, 70)
# RGB values above this are considered light
LIGHT_PIXEL_THRESHOLD = (100, 100, 100)
TOLERANCE = 10  # Allowable color variation
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
    print("Starting playlist logging script...")
    anchor_x, anchor_y = ask_for_anchor()
    logged_urls = get_logged_urls()
    tracks = get_all_tracks(PLAYLIST_ID)

    for idx, item in enumerate(tracks):
        track = item['track']
        url = track['external_urls']['spotify']
        if url in logged_urls:
            print(f"Skipping already logged track: {url}")
            continue

        added_at = item['added_at']
        title = track['name']
        artist = ', '.join([a['name'] for a in track['artists']])
        contributor = scrape_added_by(
            0, anchor_x, anchor_y)  # Idx might not be needed
        # Scroll after scraping the contributor
        print("🔻 Scrolling down")
        scroll_and_reset_to_anchor(anchor_x, anchor_y)
        log_time = datetime.datetime.now().isoformat()

        row = [title, artist, url, contributor, added_at, log_time, 'No']
        print(f"Appending row: {row}")
        ws.append_row(row)
        time.sleep(1)


if __name__ == '__main__':
    mode = input(
        "Type 'calibrate' to calibrate Y offset or press Enter to run: ").strip().lower()
    if mode == 'calibrate':
        calibrate_y_start()
    else:
        main()
