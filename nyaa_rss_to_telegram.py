import os
import feedparser
import requests
import json

# Nyaa RSS feed URL
RSS_FEED_URL = "https://nyaa.land/?page=rss&c=1_2&f=0"

# Load sent GUIDs from a file
sent_guid_file = 'sent_guids.json'
if os.path.exists(sent_guid_file):
    with open(sent_guid_file, 'r') as f:
        sent_guids = json.load(f)
else:
    sent_guids = []

# Parse the RSS feed
feed = feedparser.parse(RSS_FEED_URL)

# Check for parsing errors
if feed.bozo:
    raise Exception("Failed to parse RSS feed.")

# Loop through the latest entries
new_entries = []
for entry in feed.entries:  # Iterate over all entries
    guid = entry.get("guid", "N/A")  # GUID of the item

    # If the GUID has already been sent, skip this entry
    if guid in sent_guids:
        continue

    new_entries.append(entry)

# Check if there are any new entries to send
if not new_entries:
    print("No new entries to send.")
else:
    # Send all new entries to Telegram
    for entry in new_entries:  # Send all new entries
        guid = entry.get("guid", "N/A")  # GUID of the item
        title = entry.title
        link = entry.link
        seeders = entry.get("nyaa_seeders", "N/A")  # Accessing nyaa:seeders
        leechers = entry.get("nyaa_leechers", "N/A")  # Accessing nyaa:leechers
        size = entry.get("nyaa_size", "N/A")  # Accessing nyaa:size

        # Format the message
        message = (
            f"<b>{title}</b>\n"
            f"Link: <a href='{link}'>Download Torrent</a>\n"
            f"guid: <a href='{guid}'>Open In Browser</a>\n"
            f"Seeders: {seeders}\n"
            f"Leechers: {leechers}\n"
            f"Size: {size}\n"
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

        # Add the GUID to the sent list
        sent_guids.append(guid)

    # Save the updated sent GUIDs to the file
    with open(sent_guid_file, 'w') as f:
        json.dump(sent_guids, f)
