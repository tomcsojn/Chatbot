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
import re
import os
import sys
app = Flask(__name__)
script_dir = os.path.dirname(os.path.abspath(__file__)) 
os.chdir(script_dir)
sys.path.append("../Keys/")
import Keys

import json
import ibm_watson




ACCESS_TOKEN = Keys.ACCESS_TOKEN
VERIFY_TOKEN = Keys.VERIFY_TOKEN
WATSON_API = Keys.WATSON_API
bot = Bot(ACCESS_TOKEN)



watson = ibm_watson.AssistantV1(
        version='2019-02-28',
        iam_apikey=WATSON_API,
        url='https://gateway-fra.watsonplatform.net/assistant/api')


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
                        response_sent_text,response_type = get_response(message)
                        send_message(recipient_id,response_sent_text,response_type)
                        
                        if message['message'].get('attachments'):#non text message
                            response_sent_nontext=get_response()
                            send_message(recipient_id, response_sent_nontext)
    return "Message Processed"

def verify_fb_token(token_sent):
    #take token sent by facebook and verify it matches the verify token you sent
    #if they match, allow the request, else return an error 
    if token_sent == VERIFY_TOKEN:
        return request.args.get("hub.challenge")
    return 'Invalid verification token'

def send_message(recipient_id, response,istext):
    #sends user the text message provided via input response parameter
    
    
    if(istext):
        bot.send_text_message(recipient_id, response)
    else:
        bot.send_image_url(recipient_id, response)
    return "success"
def get_response(mess):
    mess = mess['message']
    text = mess['text']
    fast_check = check_chat(mess)
    response_type = 'text'
    if(not fast_check):       
        watson_response = call_watson(text)
        if(watson_response['output']['generic'][0]['response_type']=='text'):
            out = watson_response['output']['text'][0]
        elif(watson_response['output']['generic'][0]['response_type']=='image'):#in case of returning image
            response_type = 'image'
            out = watson_response['output']['generic'][0]['source']
    else:
        out = fast_check
    return out,response_type
#%%Watson
def call_watson(text):
    response = watson.message(
    workspace_id='88270842-4fe5-4f0b-8304-1d45b89a292f',
    input={
        'text': text
    }).get_result() 
    return response
    
#%%Pairs
pairs = [
    [
        r"my name is (.*)",
        ["Hello {}!"," How are you today {} ?",]
    ],
     [
        r"what is your name ?",
        ["My name is Chatty and I'm a chatbot ?",]
    ],
    [
        r"how are you ?",
        ["I'm doing good\nHow about You ?",]
    ],
    [
        r"sorry (.*)",
        ["Its alright","Its OK, never mind",]
    ],
    [
        r"i'm (.*) doing good",
        ["Nice to hear that","Alright :)",]
    ],
    [
        r"(.*) age?|(.*) old are you?",
        ["I'm a computer program dude\nSeriously you are asking me this?",]
        
    ],
    [
        r"what (.*) want ?",
        ["Make me an offer I can't refuse",]
        
    ],
    [
        r"(.*) (location|city) ?",
        ['Copenhagen',]
    ],
    [
        r"how (.*) health(.*)",
        ["I'm a computer program, so I'm always healthy ",]
    ],
    [
        r"(.*) (sports|game) ?",
        ["I'm a very big fan of Football",]
    ],
    [
        r"who (.*) sportsperson ?",
        ["Messy","Ronaldo","Roony"]
],
    [
        r"who (.*) (moviestar|actor)?",
        ["Tim Honks"]
],
#    [
#        r"bye",
#        ["BBye take care. See you soon :) ","It was nice talking to you. See you soon :)"]
#],
#        [
#        r"hi|hey|hello|sup|what's up",
#        ["Hello", "Hey there",]
#    ],
]


#%%Chatting    
def check_chat(mess):
    text = mess['text']
    for pair in pairs:
        if(re.search(pair[0],text.lower())):
            if(pair==pairs[0]):      
                s = "name is"
                name = text[text.index(s)+len(s):].split()[0]
                return random.choice(pair[1]).format(name)
            return random.choice(pair[1])
    if(lang_check(mess)):
        return "Sorry, I don't understand other languages than English yet.. :("
    return False    
        
def lang_check(mess):
    if(len(mess["nlp"]["detected_locales"])>0):
        if(mess["nlp"]["detected_locales"][0]["locale"]!= "en_XX"):
            return True
    return False

#%%Database
import sqlite3
from sqlite3 import Error
def create_connection(db_file):
    """Create a database connection to SQLite db"""
    try:
        conn = sqlite3.connect(db_file)
        return conn
    except Error as e:
        print(e)
    return None

def create_table(conn,create_table_sql):
    try:
        c = conn.cursor()
        c.execute(create_table_sql)
    except Error as e:
        print(e)

def Database_setup(db_file):
    conn = create_connection(db_file)
    
    slq_create_test_table = """CREATE TABLE IF NOT EXISTS tasks (
                                    id integer PRIMARY KEY,
                                    name text NOT NULL,
                                    priority integer,
                                    status_id integer NOT NULL,
                                    project_id integer NOT NULL,
                                    begin_date text NOT NULL,
                                    end_date text NOT NULL,
                                    FOREIGN KEY (project_id) REFERENCES projects (id)
                                );"""
    
    if(conn != None):
        create_table(conn,slq_create_test_table)
    else:
        print("Error! cannot create the database connection.")
        
        
    conn.close()

    
#%%Main
if __name__ == '__main__':
    
#    Database_setup("C://sqlite/db/chatbot_v2.db")
    app.run()