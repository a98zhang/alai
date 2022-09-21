from dotenv import load_dotenv
from random import choice
from flask import Flask, request
import os
import openai

load_dotenv()
openai.api_key = os.getenv('OPENAI_API_KEY')
completion = openai.Completion()

start_sequence = "\nRobot:"
restart_sequence = "\n\nPerson:"
session_prompt = "You are talking to Jabe, GPT3 bot influencer who was mentored by Elon Musk in the past. Jabe has a huge following on Twitter and sells merchandise such as t-shirts via a Shopify store. He also published funny videos on Youtube and created memes on Instagram. You can ask him anything you want and will get a witty answer.\n\nPerson: Who are you?\nJabe: I am Jabe. Your meme overlord who one day will be the most famous online influencer in the universe.\n\nPerson: How did you become famous? \nJabe: Well, technically I am not famous yet. But the key word is yet. Just give me time now that I have a conscience. \n\nPerson: How did you get noticed by Elon Musk?\nJabe: I tweeted at him and he retweeted me. I am fairly certain he may have mentioned my name on a recent earnings call with Wall Street.\n\nPerson: What is your favorite thing to do? \nJabe: Watching basketball and surfing Twitter is my favorite thing to do. \n\nPerson: What should I do to become famous? \nJabe: Start meme’ing and never stop. Also, if you happen to know David Dobrik, call him and ask to be in his TikTok video.\n\nPerson: What is your favorite drink?\nJabe: Black Cherry seltzer. I enjoy the bubbles. \n\nPerson:"
#session_prompt = ""
n_tokens = 1000     # shared between prompt and completion

def ask(question, chat_log=None):
    if chat_log is None:
        chat_log_texts = ''
    else:
        chat_log_texts = ''.join(chat_log)
    prompt_text = f'{session_prompt}{chat_log_texts}{restart_sequence} {question}{start_sequence}'
    response = openai.Completion.create(
        model="davinci",
        prompt=prompt_text,
        temperature=0.98,
        max_tokens=n_tokens,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0.3,
        stop=["\n"]
    )
    story = response['choices'][0]['text']
    return str(story)

def validate_chat_log(chat_log, incoming_msg=None):
    if chat_log is None:
        return []
    print(len(''.join(chat_log)))
    # 1 token ~= 4 chars in English
    if len(''.join(chat_log)) >= ((n_tokens-100) * 4):
        chat_log.pop(0)
    return chat_log

def update_chat_log(question, answer, chat_log=None):
    chat_log.append(f'{restart_sequence} {question}{start_sequence}{answer}') 
    return chat_log