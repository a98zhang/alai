from dotenv import load_dotenv
from twilio.twiml.messaging_response import MessagingResponse
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
            frequency_penalty=0.4, 
            presence_penalty=0.2
            #stop=["\n"]        where the API will stop generating further tokens
        )
        story = response['choices'][0]['text']
        # report 'no answer' response detail
        if str(story) == '':
            print('-----EMPTY TEXT ALERT: ', response)
        return str(story)

    def is_in_presets(self, preset_name):
        return preset_name in self.presets.index

    def list_all_presets(self):
        presets = ''
        for i, preset in enumerate(self.presets.index):
            presets.join(f'{i}: {preset}\n')
        return presets

    def change_prompt(self, preset_name):
        self.start_sequence = self.presets.loc[preset_name]['start_sequence']
        self.restart_sequence = self.presets.loc[preset_name]['restart_sequence']
        self.session_prompt = self.presets.loc[preset_name]['session_prompt']
        print(f'-------{self.start_sequence}------' )
        self.prompt_to_be_changed = False
        return None

    def validate_chat_log(self, chat_log, incoming_msg=None):
        if chat_log is None:
            return []

        # FIFO pop chat history if the prompt exceeds max_tokens
        while len(''.join(chat_log)) >= ((self.n_tokens-300) * 4):    # 1 token ~= 4 chars in Eng.
            chat_log.pop(0)
        return chat_log

    def update_chat_log(self, question, answer, chat_log=None):
        chat_log.append(f'{self.restart_sequence} {question}{self.start_sequence}{answer}') 
        return chat_log
    
    def answer(self, answer):
        msg = MessagingResponse()
        msg.message(answer)
        return str(msg)

    def debug(self, chat_log):
        print(f'{self.session_prompt}{chat_log} {self.start_sequence}')