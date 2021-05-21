# -*- coding: utf-8 -*-
"""
Created on Tue Nov  3 12:24:21 2020

@author: atosato
"""

import os
import logging
from flask import Flask
from slack_sdk.web import WebClient
from slackeventsapi import SlackEventAdapter
# from onboarding_tutorial import OnboardingTutorial
from slack_sdk.errors import SlackApiError



# Initialize a Flask app to host the events adapter
app = Flask(__name__)
# slack_events_adapter = SlackEventAdapter(os.environ['SLACK_SIGNING_SECRET'], "/slack/events", app)
slack_events_adapter = SlackEventAdapter('038f1bd4216a757a9928b4ecb30650c6', "/slack/events", app)

# Initialize a Web API client
# slack_web_client = WebClient(token=os.environ['SLACK_BOT_TOKEN'])
slack_web_client = WebClient('xoxb-1462403972165-1465549188354-vzSfIk5NdFIYBTRNn7Badjhq')


def start_onboarding(user_id: str, channel: str):
    try:
        response = slack_web_client.chat_postMessage(channel='#fridges', text="Hello world!")
        response["message"]["text"] == "Hello world!"
    except SlackApiError as e:
        # You will get a SlackApiError if "ok" is False
        assert e.response["ok"] is False
        assert e.response["error"]  # str like 'invalid_auth', 'channel_not_found'
        print(f"Got an error: {e.response['error']}")

@slack_events_adapter.on("message")
def message(payload):
    """Display the onboarding welcome message after receiving a message
    that contains "start".
    """
    event = payload.get("event", {})

    channel_id = event.get("channel")
    user_id = event.get("user")
    text = event.get("text")
    
    print('received: ', text)


    if text and text.lower() == "start":
        return start_onboarding(user_id, channel_id)
    
    
if __name__ == "__main__":
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)
    logger.addHandler(logging.StreamHandler())
    app.run(port=3000)