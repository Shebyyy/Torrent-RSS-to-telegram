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
    guid = entry.get("guid", "N/A")  # GUID of the item
    pub_date = entry.get("published", "N/A")  # Publication date
    seeders = entry.get("nyaa:seeders", "N/A")  # Seeders
    leechers = entry.get("nyaa:leechers", "N/A")  # Leechers
    downloads = entry.get("nyaa:downloads", "N/A")  # Downloads
    info_hash = entry.get("nyaa:infoHash", "N/A")  # Info hash
    category_id = entry.get("nyaa:categoryId", "N/A")  # Category ID
    category = entry.get("nyaa:category", "N/A")  # Category
    size = entry.get("nyaa:size", "N/A")  # Size
    comments = entry.get("nyaa:comments", "N/A")  # Comments
    trusted = entry.get("nyaa:trusted", "N/A")  # Trusted status
    remake = entry.get("nyaa:remake", "N/A")  # Remake status

    # Format the message
    message = (
        f"<b>{title}</b>\n"
        f"Link: <a href='{link}'>Download Torrent</a>\n"
        f"GUID: {guid}\n"
        f"Published Date: {pub_date}\n"
        f"Seeders: {seeders}\n"
        f"Leechers: {leechers}\n"
        f"Downloads: {downloads}\n"
        f"Info Hash: {info_hash}\n"
        f"Category ID: {category_id}\n"
        f"Category: {category}\n"
        f"Size: {size}\n"
        f"Comments: {comments}\n"
        f"Trusted: {trusted}\n"
        f"Remake: {remake}\n"
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
