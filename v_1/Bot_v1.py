# -*- coding: utf-8 -*-
"""
Created on Mon Aug  5 23:25:50 2019

@author: Tamas
"""

import nltk
import numpy as np
import random
import string
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

f = open('BotCorpus.txt','r',errors = 'ignore')
raw = f.read()
raw = raw.lower()
sent_tokens = nltk.sent_tokenize(raw)
word_tokens = nltk.word_tokenize(raw)
#%% Normalizatin functions
lemmer = nltk.stem.WordNetLemmatizer()
def LemTokens(tokens):
    return [lemmer.lemmatize(token) for token in tokens]

remove_punct_dict = dict((ord(punct),None) for punct in string.punctuation)

def LemNormalize(text):
    return LemTokens(nltk.word_tokenize(text.lower().translate(remove_punct_dict)))

#%%Greeting Keywords
GREETING_INPUTS = ("hello", "hi", "greetings", "sup", "what's up","hey",)
GREETING_RESPONSES = ["hi", "hey", "hi there", "hello"]

def greeting(sentence):
 
    for word in sentence.split():
        if word.lower() in GREETING_INPUTS:
            return random.choice(GREETING_RESPONSES)
        
#%%similarity
            
def response(user_input):
    bot_response=''
    sent_tokens.append(user_input)
    
    TfidfVec = TfidfVectorizer(tokenizer=LemNormalize,stop_words='english')
    tfidf = TfidfVec.fit_transform(sent_tokens)
    vals = cosine_similarity(tfidf[-1],tfidf)
    idx = vals.argsort()[0][-2]
    flat = vals.flatten()
    flat.sort()
    req_tfidf = flat[-2]
    
    if(req_tfidf==0):
        bot_response += "Sorry! I don't understand you"
        return bot_response
    else:
        bot_response +=sent_tokens[idx]
        return bot_response
#%%Run Bot
flag = True
print("Bot: I will answer your queries. If you want to exit type Bye!")

while(flag):
    user_input = input()
    user_input =user_input.lower()
    if(user_input!='bye'):
        if(greeting(user_input)!=None):
            print("Bot: "+greeting(user_input))
        else:
            print("Bot: ",end="")
            print(response(user_input))
            sent_tokens.remove(user_input)
    else:
        flag=False
        print("Bot: See you Later!")

