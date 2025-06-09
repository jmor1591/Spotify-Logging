cd "C:\Example\File\Path\To\Spotify Logging"
$timestamp = Get-Date -Format "yyyy-MM-dd_HH-mm-ss"
$logFile = "log_$timestamp.txt"

.\.venv\Scripts\Activate.ps1
python collect_manual.py *>> ".\logs\$logFile"
