from dotenv import load_dotenv
from twilio.twiml.messaging_response import MessagingResponse
import pandas as pd
import os
import openai
import nltk
nltk.download('punkt')

load_dotenv()
openai.api_key = os.getenv('OPENAI_API_KEY')
completion = openai.Completion()

class Bot(object):
    def __init__(self, preset='Default'):
        self.presets = pd.read_csv('data/presets.csv').set_index('preset')
        self.n_tokens = 1000            

    def ask(self, question, preset, chat_log=None):

        # prepare the prompt and parameters
        prms = self.get_presets(preset)
        prompt_text = self.validate_prompt_length(prms, question, chat_log)
        stop_sequence = [prms['restart_sequence'], prms['start_sequence']]
        if not pd.isna(prms['stop']):
            stop_sequence.append(prms['stop'])

        # Creates a completion for the provided prompt and parameters
        response = openai.Completion.create(
            model="text-davinci-003",
            prompt=prompt_text,
            temperature=0.7,
            max_tokens=self.n_tokens,
            top_p=1,
            frequency_penalty=0, 
            presence_penalty=0,
            # https://help.openai.com/en/articles/5072263-how-do-i-use-stop-sequences
            stop=stop_sequence        
        )

        story = response['choices'][0]['text']

        # report 'no answer' response detail
        if str(story) == '':
            print('-----EMPTY TEXT ALERT: ', response)

        return str(story)

    def answer(self, answer):
        msg = MessagingResponse()
        msg.message(answer)
        return str(msg)

    def get_presets(self, preset):
        return self.presets.loc[preset].to_dict()

    def is_in_presets(self, preset):
        if preset.isdigit():
            return int(preset) in range(len(self.presets.index))
        return preset in self.presets.index

    def list_all_presets(self):
        preset_list = ''
        for i, preset in enumerate(self.presets.index):
            preset_list += f'\n{i}: {preset}'
        return preset_list

    def validate_preset_name(self, preset):
        if preset.isdigit():
            preset = self.presets.index[int(preset)]
        return preset

    def validate_prompt_length(self, prms, question, chat_log):
        prompt_text = self.compile_prompt_text(prms, question, chat_log)
        a = len(nltk.word_tokenize(prompt_text))
        print("==", a)
        # up to 4097 tokens shared between prompt and completion
        while len(nltk.word_tokenize(prompt_text)) >= (4097*0.85 - self.n_tokens):
            print("popping...")
            if chat_log is None or len(chat_log) == 0:
                break
            chat_log.pop(0)
            prompt_text = self.compile_prompt_text(prms, question, chat_log)                    
        return prompt_text
       
    def compile_prompt_text(self, prms, question, chat_log):
        chat_log_texts = '' if chat_log is None else ''.join(chat_log)
        prompt_text = (
            f'{prms["session_prompt"]}{chat_log_texts}'
            f'{prms["restart_sequence"]} {question}{prms["start_sequence"]}'
        )
        return prompt_text

    def validate_chat_log(self, chat_log):
        if chat_log is None:
            return []

        # FIFO pop chat history if the prompt exceeds max_tokens
        while len(''.join(chat_log)) >= ((self.n_tokens-300) * 4):    
            chat_log.pop(0)                     # 1 token ~= 4 chars in Eng.
        return chat_log
        # condensing your prompt, or breaking the text into smaller pieces 

    def update_chat_log(self, question, answer, preset, chat_log=None):
        if chat_log is None:
            chat_log = []
        prms = self.get_presets(preset)
        chat_log.append((
            f'{prms["restart_sequence"]} {question}'
            f'{prms["start_sequence"]}{answer}'
        )) 
        return chat_log
    
    def debug(self, chat_log):
        print(f'{self.session_prompt}{chat_log} {self.start_sequence}')