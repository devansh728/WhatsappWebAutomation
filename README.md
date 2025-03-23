# WhatsApp Web Scraper

A Django application for extracting and storing messages, sender, receiver, timestamps, dates, and media URLs from WhatsApp Web.

## Features

- Automates WhatsApp Web using Selenium
- Extracts messages, sender, receiver, timestamp, date information
- Captures media URLs (photos and videos)
- Saves data to PostgreSQL database
- Schedules regular scraping

## Requirements

- Python 3.8+
- Chrome/Chromium browser
- ChromeDriver (compatible with your Chrome version)
- PostgreSQL database

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd whatsapp-web-scraper
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
# On Windows
venv\Scripts\activate
# On macOS/Linux
source venv/bin/activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Configure the database in `whatsapp_automation/settings.py`:
```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'your_db_name',
        'USER': 'your_db_user',
        'PASSWORD': 'your_db_password',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}
```

5. Apply migrations:
```bash
python manage.py migrate
```

## Usage

### Running the WhatsApp Web Scraper

```bash
# Basic usage
python manage.py scrape_whatsapp

# With headless browser (no UI)
python manage.py scrape_whatsapp --headless

# Skip downloading media files
python manage.py scrape_whatsapp --no-media

# Run continuously with interval (in minutes)
python manage.py scrape_whatsapp --interval 60  # Run every 60 minutes
```

### Using the Scheduler

```bash
# Start the scheduler (default: runs every hour)
python whatsapp_automation/scripts/schedule_scraper.py
```

## First-Time Setup

1. The first time you run the scraper, it will open WhatsApp Web in a browser window.
2. Scan the QR code with your phone to log in to WhatsApp Web.
3. After successful login, the scraper will begin extracting data.
4. Subsequent runs will use the saved session (unless browser data is cleared).

## Important Notes

- **Compliance**: Ensure you comply with WhatsApp's Terms of Service when using this tool.
- **Privacy**: Be mindful of privacy concerns when extracting and storing WhatsApp messages.
- **Error Handling**: The script includes error handling to manage exceptions during the scraping process.
- **Security**: Keep credentials and sensitive data secure using environment variables or encryption.

## Database Schema

- `ChatMessage`: Stores message content, sender, receiver, timestamp, and media URLs
- `MediaFile`: Stores information about downloaded media files

## License

[Specify your license here]

## Disclaimer

This tool is for educational purposes only. The developers are not responsible for any misuse or violation of WhatsApp's Terms of Service. 