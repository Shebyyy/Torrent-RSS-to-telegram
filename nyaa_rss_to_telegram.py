import os
import feedparser
import requests
import json
import time

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

# Process only the last 10 entries
latest_entries = feed.entries[:10]  # Get the last 10 entries
new_entries = []

# Filter new entries that have not been sent before
for entry in latest_entries:
    guid = entry.get("guid", "N/A")  # GUID of the item

    # If the GUID has already been sent, skip this entry
    if guid in sent_guids:
        continue

    # Accessing seeders, leechers, and size correctly
    seeders = entry.get("nyaa:seeders", "N/A")
    leechers = entry.get("nyaa:leechers", "N/A")
    size = entry.get("nyaa:size", "N/A")

    # Add a check if they are still N/A and try accessing them from entry's extensions
    if seeders == "N/A":
        seeders = entry.get("extensions", {}).get("nyaa:seeders", "N/A")
    if leechers == "N/A":
        leechers = entry.get("extensions", {}).get("nyaa:leechers", "N/A")
    if size == "N/A":
        size = entry.get("extensions", {}).get("nyaa:size", "N/A")

    new_entries.append({
        "guid": guid,
        "title": entry.title,
        "link": entry.link,
        "seeders": seeders,
        "leechers": leechers,
        "size": size,
    })

# Check if there are any new entries to send
if not new_entries:
    print("No new entries to send.")
else:
    # Send all new entries to Telegram
    for entry in new_entries:
        guid = entry["guid"]  # GUID of the item
        title = entry["title"]
        link = entry["link"]
        seeders = entry["seeders"]
        leechers = entry["leechers"]
        size = entry["size"]

        # Format the message
        message = (
            f"<b>{title}</b>\n"
            f"Link: <a href='{link}'>Download Torrent</a>\n"
            f"Seeders: {seeders}\n"
            f"Leechers: {leechers}\n"
            f"Size: {size}\n"
        )

        # Send message to Telegram with retry logic
        attempt = 0
        while attempt < 5:  # Try up to 5 times
            telegram_api_url = f"https://api.telegram.org/bot{os.environ['TELEGRAM_BOT_TOKEN']}/sendMessage"
            payload = {
                'chat_id': os.environ['TELEGRAM_CHAT_ID'],
                'text': message,
                'parse_mode': 'HTML'  # Enables HTML formatting
            }
            response = requests.post(telegram_api_url, data=payload)

            # Check for errors
            if response.status_code == 200:
                print(f"Sent message for {title}")
                break  # Exit the retry loop if the request was successful
            elif response.status_code == 429:  # Rate limit exceeded
                retry_after = response.json().get("parameters", {}).get("retry_after", 1)
                print(f"Rate limit exceeded. Retrying after {retry_after} seconds...")
                time.sleep(retry_after)  # Wait for the specified time before retrying
                attempt += 1
            else:
                print(f"Failed to send message: {response.text}")
                break  # Exit loop on other errors

        # Add the GUID to the sent list
        sent_guids.append(guid)

    # Save the updated sent GUIDs to the file
    with open(sent_guid_file, 'w') as f:
        json.dump(sent_guids, f)
