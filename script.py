import praw
import requests
import os
import json
from datetime import datetime, timedelta

# Reddit API credentials
reddit = praw.Reddit(
    client_id=os.getenv('CLIENT_ID'),
    client_secret=os.getenv('CLIENT_SECRET'),
    user_agent=os.getenv('USER_AGENT')
)

# Discord webhook URL
discord_webhook_url = os.getenv('DISCORD_WEBHOOK_URL')

# Subreddit and excluded flair
subreddit_name = 'watchexchange'
excluded_flair = 'Sold'

# File to store the target phrases and last checked timestamp
config_file = 'config.json'

# Load configuration from file
def load_config():
    if os.path.exists(config_file):
        with open(config_file, 'r') as file:
            return json.load(file)
    return {"target_phrases": ["Murph", "Khaki Field", "Field Auto", "SRPJ13", "SRPK15", "SRPB41"], "last_checked_timestamp": 0}

# Save configuration to file
def save_config(config):
    with open(config_file, 'w') as file:
        json.dump(config, file)

config = load_config()
target_phrases = config.get("target_phrases")
last_checked_timestamp = config.get("last_checked_timestamp")

def check_posts():
    global last_checked_timestamp
    subreddit = reddit.subreddit(subreddit_name)
    two_weeks_ago = datetime.utcnow() - timedelta(weeks=2)
    two_weeks_ago_timestamp = two_weeks_ago.timestamp()
    last_checked_timestamp = max(last_checked_timestamp, two_weeks_ago_timestamp)
    new_last_checked_timestamp = last_checked_timestamp

    # Get all posts since the last check
    for post in subreddit.new(limit=None):  
        post_timestamp = post.created_utc
        if post_timestamp > last_checked_timestamp:
            if post.link_flair_text == excluded_flair:
                continue
            if any(phrase in post.title for phrase in target_phrases):
                message = f"New post found: **{post.link_flair_text}** | [{post.title}]({post.url})"
                send_discord_notification(message)
            new_last_checked_timestamp = max(new_last_checked_timestamp, post_timestamp)

    # Update the last checked timestamp only if it has changed
    if new_last_checked_timestamp != last_checked_timestamp:
        last_checked_timestamp = new_last_checked_timestamp
        config['last_checked_timestamp'] = last_checked_timestamp
        save_config(config)

def send_discord_notification(message):
    data = {"content": message}
    response = requests.post(discord_webhook_url, json=data)
    if response.status_code != 204:
        print(f"Failed to send notification: {response.status_code}")

if __name__ == "__main__":
    check_posts()
