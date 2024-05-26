import praw
import requests
import os
import json
from datetime import datetime

# Reddit API credentials
reddit = praw.Reddit(
    client_id=os.getenv('CLIENT_ID'),
    client_secret=os.getenv('CLIENT_SECRET'),
    user_agent=os.getenv('USER_AGENT')
)

# Discord webhook URL
discord_webhook_url = os.getenv('DISCORD_WEBHOOK_URL')

# Subreddit and key phrase
subreddit_name = 'watchexchange'
key_phrase = 'KEY_PHRASE'
target_flair = 'TARGET_FLAIR'

# File to store the timestamp of the last checked post
timestamp_file = 'last_checked_timestamp.json'

def load_last_timestamp():
    if os.path.exists(timestamp_file):
        with open(timestamp_file, 'r') as file:
            data = json.load(file)
            return data.get('timestamp', 0)
    return 0

def save_last_timestamp(timestamp):
    with open(timestamp_file, 'w') as file:
        json.dump({'timestamp': timestamp}, file)

def check_posts():
    subreddit = reddit.subreddit(subreddit_name)
    last_checked_timestamp = load_last_timestamp()
    new_last_checked_timestamp = last_checked_timestamp

    for post in subreddit.new(limit=100):  # Check the latest 100 posts
        post_timestamp = post.created_utc
        if post_timestamp > last_checked_timestamp:
            if target_flair in post.link_flair_text and key_phrase in post.title:
                message = f"New post found: [{post.title}]({post.url})"
                send_discord_notification(message)
            new_last_checked_timestamp = max(new_last_checked_timestamp, post_timestamp)

    save_last_timestamp(new_last_checked_timestamp)

def send_discord_notification(message):
    data = {
        "content": message
    }
    response = requests.post(discord_webhook_url, json=data)
    if response.status_code != 204:
        print(f"Failed to send notification: {response.status_code}")

if __name__ == "__main__":
    check_posts()

