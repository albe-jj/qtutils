# -*- coding: utf-8 -*-
"""
Created on Thu Nov 12 16:24:28 2020

@author: TUD278249
"""
import os
import logging
from flask import Flask
from slack_sdk.web import WebClient
from slackeventsapi import SlackEventAdapter
# from onboarding_tutorial import OnboardingTutorial
from slack_sdk.errors import SlackApiError

import pythoncom

import sys
sys.path.append(r'D:\LeidenMCK50_fridge\Scripts\Albo')
from drivers.LCApp import LVApp
# from drivers.DRTempControl import DRTempControl
from visa import ResourceManager


rm = ResourceManager()
keithley_He = my_instrument = rm.get_instrument('GPIB::26')

get_He_level = lambda: round(float(keithley_He.read().strip()[4:])/2*1e3-4)

lcapp = LVApp(r"DRTempControl.Application",r"DR TempControl.exe\TC.vi")
get_temp = lambda: lcapp.GetData('T')[2]


#%%

# run in anconda terminal C:\Users\atosato>python slack_app.py
# run ngrok and start tunnel connection: ngrok http 3000
# copy https in event subscription https://api.slack.com/apps/A01E245D6QH/event-subscriptions?
# e.g. https://b3f56076d904.ngrok.io/slack/events then reinstall app

# Initialize a Flask app to host the events adapter
app = Flask(__name__)
slack_events_adapter = SlackEventAdapter(os.environ['SLACK_SIGNING_SECRET'], "/slack/events", app)

# Initialize a Web API client
slack_web_client = WebClient(os.environ['SLACK_BOT_TOKEN'])
print('initialized')

def send_info(user_id: str, channel: str):
    pythoncom.CoInitialize() #coinit to use win32 apps in this thread
    #redefine an instance of LVAPP in this thread, see https://stackoverflow.com/questions/26764978/using-win32com-with-multithreading
    lcapp = LVApp(r"DRTempControl.Application",r"DR TempControl.exe\TC.vi") 
    get_temp = lambda: round(lcapp.GetData('T')[2],1)
    print(get_temp())
    try:
        #retrive info
        try:
            msg = f'Hi <@{user_id}>\n - Temp ={get_temp()} mK \n - He level = {get_He_level()} nm'  
        except Exception as e:
            print(e)
        #send info    
        response = slack_web_client.chat_postMessage(channel='#fridges', text=msg)
        # response["message"]["text"] == "test"
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
    # pythoncom.CoInitialize()

    if text and text.lower() == "info":
        return send_info(user_id, channel_id)
    
#%%    

if __name__ == "__main__":
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)
    logger.addHandler(logging.StreamHandler())
    app.run(port=3000)