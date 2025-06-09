# Spotify Playlist Logger

A Python-powered automation system that logs Spotify playlist activity to Google Sheets, enriched with contributor data, audio features, and analytics-ready structure. Built for power-users who want total insight into playlist growth and collaboration.

---

## 🚀 Features

* **Tracks Every New Song** added to a specific Spotify playlist
* **Captures**:

  * Song title, artists, URL
  * Date/time added
  * "Added by" user (via UI automation)
  * Popularity, release year, audio features (danceability, energy, etc.)
* **Logs directly into Google Sheets**
* **Zapier Integration Ready** for daily email summaries
* **Daily Automation** using Windows Task Scheduler with logging
* **No manual copying** — just run the script and get insights

---

## 🧠 Why This Exists

Spotify's API doesn't expose who added a track to a collaborative playlist — but the desktop UI does.

This project solves that by combining:

* 🎯 Spotify Web API (track metadata, features)
* 👁️ PyAutoGUI to extract "Added By" from desktop UI
* 📝 gspread for writing structured logs
* 🔁 Windows automation to run daily

---

## 🔧 Setup

### 1. Clone this repo

```bash
git clone https://github.com/yourusername/spotify-logger.git
cd spotify-logger
```

### 2. Install requirements

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

### 3. Configure Environment

Create a `.env` file:

```env
SPOTIFY_CLIENT_ID=your_id
SPOTIFY_CLIENT_SECRET=your_secret
SPOTIFY_REDIRECT_URI=http://localhost:8888/callback
PLAYLIST_ID=spotify:playlist:xxxxxxxxxxxx
SCOPE=playlist-read-private,user-library-read
GOOGLE_SHEET_NAME=Spotify Summer 2025 AZ Road Trip
```

### 4. Set Up Google Sheets API

* Create a Google Cloud project
* Enable Google Sheets + Drive API
* Create a Service Account
* Download `creds.json` and place it in the project root
* Share your Google Sheet with `your-service-account@project.iam.gserviceaccount.com`

---

## 🖱️ Usage

### Run Manually

```bash
python collect_manual.py
```

### Calibrate UI Anchor (for UI automation of "Added by" which is in development and requires complex pyautogui features to be used)

```bash
python collect_with_scrape.py
```

### Automate Daily Logging (Windows)

Use the included `run_collect.ps1` with Windows Task Scheduler.

* Automatically creates a timestamped `.log` file in `/logs`
* Runs silently on login or at 9AM

---

## 📊 Sheet Schema

| Song Title | Artist | URL | Contributor | Date Added | Logged At | Notified | Count | Contributor Count | % | Year | Popularity | Audio Features |
| ---------- | ------ | --- | ----------- | ---------- | --------- | -------- | ----- | ----------------- | - | ---- | ---------- | -------------- |

Google Sheets formulas provide analytics like:

* Track count by contributor
* Proportional contribution
* Popularity trends by decade

---

## ✨ Example Use Cases

* Curating collaborative road trip playlists
* Tracking influencer song drops in shared lists
* Building internal tooling for A\&R teams
* Logging and auditing listening trends over time

---

## 📬 Notifications

Trigger a Zapier workflow when new songs appear, and send an email digest like:

> **New Songs Today:**
>
> * *Promiscuous* by *Nelly Furtado, Timbaland* (added by *Jordan*)
> * *Baby* by *Justin Bieber, Lil Jon* (added by *UNKNOWN*)

---

## 🛠 Built With

* `spotipy` – Spotify API client
* `pyautogui` + `pyperclip` – for scraping contributor
* `gspread` + `oauth2client` – Google Sheets
* `dotenv` – secure config
* `Task Scheduler` – full local automation

---

## 📌 Future Improvements

* 🎥 Sora UI for video proof-of-concept
* 📈 Add graphs to Sheet
* 🧪 Add unit tests and mocks
* ☁️ Move to cloud serverless automation

---

## 💼 Ideal For Employers Looking For:

* **Python + Automation** engineer who builds real-world tooling
* Comfortable with **OAuth, APIs, UI automation, and deployment**
* Prioritizes **clean logs, automation, and reliability**
* Strong **problem-solving around undocumented API gaps**

---

## 📣 Feedback

Feel free to open an issue or [connect on LinkedIn](https://www.linkedin.com/in/jormorris) to discuss automation + music tech!

---

**© 2025 — Built by Jordan as a passion project.** 🎧
