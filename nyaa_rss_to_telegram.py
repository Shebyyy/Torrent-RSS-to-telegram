import os
import feedparser
import requests

# Nyaa RSS feed URL
RSS_FEED_URL = "https://nyaa.land/?page=rss&c=1_2&f=0"

# Parse the RSS feed
feed = feedparser.parse(RSS_FEED_URL)

# Check for parsing errors
if feed.bozo:
    raise Exception("Failed to parse RSS feed.")

# Loop through the latest entries
for entry in feed.entries[:5]:  # Adjust the number as needed
    title = entry.title
    link = entry.link
    seeders = entry.get("nyaa:seeders", "N/A")  # Accessing with namespace
    leechers = entry.get("nyaa:leechers", "N/A")  # Accessing with namespace
    size = entry.get("nyaa:size", "N/A")  # Accessing with namespace

    # Format the message
    message = (
        f"<b>{title}</b>\n"
        f"Seeders: {seeders} | Leechers: {leechers}\n"
        f"Size: {size}\n"
        f"<a href='{link}'>Download Torrent</a>"
    )

    # Send message to Telegram
    telegram_api_url = f"https://api.telegram.org/bot{os.environ['TELEGRAM_BOT_TOKEN']}/sendMessage"
    payload = {
        'chat_id': os.environ['TELEGRAM_CHAT_ID'],
        'text': message,
        'parse_mode': 'HTML'  # Enables HTML formatting
    }
    response = requests.post(telegram_api_url, data=payload)

    # Check for errors
    if response.status_code != 200:
        raise Exception(f"Failed to send message: {response.text}")
