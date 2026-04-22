# import requests
# import json
# import os
# from dotenv import load_dotenv
# def post_to_slack(api_token, channel_id, message):
#     if not api_token.startswith("xoxb-"):
#         raise ValueError("Invalid Slack API token format.")
#     if not channel_id or not message:
#         raise ValueError("Channel ID and message cannot be empty.")

#     url = "https://slack.com/api/chat.postMessage"
#     headers = {
#     "Content-Type": "application/json; charset=utf-8",
#     "Authorization": f"Bearer {api_token}"
#     }
#     payload = {
#     "channel": channel_id,
#     "text": message
#     }

#     try:
#         response = requests.post(url, headers=headers, data=json.dumps(payload))
#         response_data = response.json()

#         if not response.ok or not response_data.get("ok"):
#             raise Exception(f"Slack API error: {response_data.get('error', 'Unknown error')}")

#         print(f"✅ Message posted successfully to channel {channel_id}")
#         return response_data
#     except Exception as e:
#         print(f"Error: {e}") 

# if __name__ == "__main__":
#     SLACK_API_TOKEN = os.getenv("SLACK_CODE")
#     CHANNEL_ID = "C0AUS94KVU1"
#     MESSAGE = "Hey, i am from login into url portfolio Slack api called"
#     post_to_slack(SLACK_API_TOKEN, CHANNEL_ID, MESSAGE)

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