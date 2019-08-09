# -*- coding: utf-8 -*-
"""
Created on Wed Aug  7 10:20:21 2019

@author: Tamas
"""

import nltk
import numpy as np
import random
from flask import Flask,request
from pymessenger.bot import Bot

import os
import sys
app = Flask(__name__)
script_dir = os.path.dirname(os.path.abspath(__file__)) 
os.chdir(script_dir)
sys.path.append("../Keys/")
import Keys

ACCESS_TOKEN = Keys.ACCESS_TOKEN
VERIFY_TOKEN = Keys.VERIFY_TOKEN
bot = Bot(ACCESS_TOKEN)
#%% Webhook
@app.route('/',methods=['GET','POST'])
def receive_message():
    if request.method == 'GET':
        token_sent= request.args.get("hub.verify_token")
        return verify_fb_token(token_sent)


    else:
        output = request.get_json()
        for event in output['entry']:
            messaging = event['messaging']
            for message in messaging:
                if message.get('message'):
                    recipient_id = message['sender']['id']
                    if message['message'].get('text'):
                        response_sent_text = get_message(message['message']['text'])
                        send_message(recipient_id,response_sent_text)
                        
                        if message['message'].get('attachments'):
                            response_sent_nontext=get_message()
                            send_message(recipient_id, response_sent_nontext)
    return "Message Processed"

def verify_fb_token(token_sent):
    #take token sent by facebook and verify it matches the verify token you sent
    #if they match, allow the request, else return an error 
    if token_sent == VERIFY_TOKEN:
        return request.args.get("hub.challenge")
    return 'Invalid verification token'

def send_message(recipient_id, response):
    #sends user the text message provided via input response parameter
    bot.send_text_message(recipient_id, response)
    return "success"

def get_message(user_input):
    sample_responses = ["You are stunning!", "We're proud of you.", "Keep on being you!", "We're greatful to know you :)"]
    # return selected item to the user
#    return random.choice(sample_responses)
    return user_input

#%%Database
import sqlite3
from sqlite3 import Error
def create_connection(db_file):
    """Create a database connection to SQLite db"""
    try:
        conn = sqlite3.connect(db_file)
        print(sqlite3.version)
    except Error as e:
        print(e)
    finally:
        conn.close()

def create_table(conn,create_table_sql):
    try:
        c = conn.cursor()
        c.execute(create_table_sql)
    except Error as e:
        print(e)
#%%Main
if __name__ == '__main__':
    create_connection("C://sqlite/db/chatbot_v2.db")
    app.run()