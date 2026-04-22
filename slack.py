
import requests
from dotenv import load_dotenv
import os

def post_to_slack(message):
    
    api_token = os.getenv("SLACK_CODE")
    channel_id = os.getenv("CHANNEL_ID")
    url = "https://slack.com/api/chat.postMessage"

    headers = {
        "Authorization": f"Bearer {api_token}",
        "Content-Type": "application/json"
    }

    payload = {
        "channel": channel_id,
        "text": message
    }

    response = requests.post(url, headers=headers, json=payload)
    response_data = response.json()

    if not response.ok or not response_data.get("ok"):
        raise Exception(f"Slack API error: {response_data.get('error')}")

    return response_data