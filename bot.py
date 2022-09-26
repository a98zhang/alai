from dotenv import load_dotenv
from twilio.twiml.messaging_response import MessagingResponse
import numpy as np
import pandas as pd
import os
import openai

load_dotenv()
openai.api_key = os.getenv('OPENAI_API_KEY')
completion = openai.Completion()

class Bot(object):
    def __init__(self, preset='Default'):
        self.presets = pd.read_csv('data/presets.csv').set_index('preset')
        self.start_sequence = self.presets.loc[preset]['start_sequence']
        self.restart_sequence = self.presets.loc[preset]['restart_sequence']
        self.session_prompt = self.presets.loc[preset]['session_prompt']
        self.n_tokens = 1000     # shared between prompt and completion
        self.prompt_to_be_changed = False

    def ask(self, question, chat_log=None):
        if chat_log is None:
            chat_log_texts = ''
        else:
            chat_log_texts = ''.join(chat_log)
        prompt_text = f'{self.session_prompt}{chat_log_texts}{self.restart_sequence} {question}{self.start_sequence}'

        response = openai.Completion.create(
            model="text-davinci-002",
            prompt=prompt_text,
            temperature=0.8,
            max_tokens=self.n_tokens,
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

    def change_prompt(self, incoming_msg):
        self.start_sequence = self.presets.loc[incoming_msg]['start_sequence']
        self.restart_sequence = self.presets.loc[incoming_msg]['restart_sequence']
        self.session_prompt = self.presets.loc[incoming_msg]['session_prompt']
        self.prompt_to_be_changed = False
        print('----PROMPT HAS BEEN CHANGED----')
        return None

    def validate_chat_log(self, chat_log, incoming_msg=None):
        if chat_log is None:
            return []

        # 1 token ~= 4 chars in English
        if len(''.join(chat_log)) >= ((self.n_tokens-300) * 4):
            chat_log.pop(0)
        return chat_log

    def update_chat_log(self, question, answer, chat_log=None):
        chat_log.append(f'{self.restart_sequence} {question}{self.start_sequence}{answer}') 
        return chat_log
    
    def answer(self, answer):
        msg = MessagingResponse()
        msg.message(answer)
        return str(msg)
