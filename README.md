# Text Reading Assistant

A web application that helps users practice reading or keep track of their speech while speaking with speech recognition. Built with Flask and the Web Speech API.

## What it does

- Upload text files or paste text directly
- Highlights words as you read them
- Uses speech recognition to track your reading
- Shows progress and reading statistics
- Saves reading sessions so you can continue later

## Requirements

- Python 3.8 or higher
- Chrome or Edge browser (for speech recognition)

## Setup

1. Clone or download this project
2. Create a virtual environment:
   ```bash
   python -m venv .venv
   source .venv/bin/activate
   ```
3. Install requirements:
   ```bash
   pip install -r requirements.txt
   ```
4. Run the app:
   ```bash
   python app.py
   ```
5. Open your browser and go to `http://localhost:5001`

## How to use

1. On the home page, either paste text or upload a .txt file
2. Click "Start Reading Session" 
3. On the reading page, click "Start" to begin speech recognition
4. Read the highlighted words out loud
5. The app will follow along and highlight your progress

## Files

- `app.py` - Main Flask application
- `templates/` - HTML templates
- `static/` - CSS and JavaScript files
- `tests/` - Unit tests
- `requirements.txt` - Python dependencies

## Known issues

- Speech recognition works best in Chrome and Edge
- Firefox has limited support
- Safari doesn't support speech recognition
- You need to allow microphone access

## Testing

Run tests with:
```bash
pytest
```

 