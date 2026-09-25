@echo off
echo Starting MTAQ 2026 study app...
echo Open http://localhost:8765 in your browser.
echo Press Ctrl+C to stop.
start "" http://localhost:8765
python -m http.server 8765
