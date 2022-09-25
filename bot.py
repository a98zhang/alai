from dotenv import load_dotenv
from twilio.twiml.messaging_response import MessagingResponse
import numpy as np
import pandas as pd
import os
import openai

load_dotenv()
openai.api_key = os.getenv('OPENAI_API_KEY')
completion = openai.Completion()

presets = pd.read_csv('data/presets.csv').set_index('preset')
start_sequence = presets.loc['Default']['start_sequence']
restart_sequence = presets.loc['Default']['restart_sequence']
session_prompt = presets.loc['Default']['session_prompt']
n_tokens = 1000     # shared between prompt and completion

def ask(question, chat_log=None):
    if chat_log is None:
        chat_log_texts = ''
    else:
        chat_log_texts = ''.join(chat_log)
    prompt_text = f'{session_prompt}{chat_log_texts}{restart_sequence} {question}{start_sequence}'

    response = openai.Completion.create(
        model="text-davinci-002",
        prompt=prompt_text,
        temperature=0.8,
        max_tokens=n_tokens,
        top_p=1,
        frequency_penalty=0.5, 
        presence_penalty=0.2,
        stop=["\n"]
    )
    story = response['choices'][0]['text']
    
    # report 'no answer' response detail
    if str(story) == '':
        print('the response is ', response)
    return str(story)

#def change_robot(incoming_msg):


def validate_chat_log(chat_log, incoming_msg=None):
    if chat_log is None:
        return []

    # 1 token ~= 4 chars in English
    if len(''.join(chat_log)) >= ((n_tokens-300) * 4):
        chat_log.pop(0)
    return chat_log

def update_chat_log(question, answer, chat_log=None):
    chat_log.append(f'{restart_sequence} {question}{start_sequence}{answer}') 
    return chat_log