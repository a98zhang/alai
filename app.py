from flask import Flask, request, session
from twilio.twiml.messaging_response import MessagingResponse
import bot 
app = Flask(__name__)

app.config['SECRET_KEY'] = 'fjkesjrelhg'
bot = bot.Bot()

@app.route('/bot', methods=['GET','POST'])
def gpt():

    # fetch the incoming message
    incoming_msg = request.values['Body']

    # special cases
    if incoming_msg == 'RESTART':               # reset the conversation
        session['chat_log'] = None
        return bot.answer('Hi! Ask me anything.')

    elif incoming_msg == 'CHANGE':              # prompt for changing robot
        bot.prompt_to_be_changed = True
        return bot.answer('Who shall I call for you?')

    elif incoming_msg == 'LIST':
        preset_list = bot.list_all_presets()
        print(preset_list)
        return bot.answer(f'Here is the complete list:{preset_list}')

    elif bot.prompt_to_be_changed:          
        if bot.is_in_presets(incoming_msg):   # change prompt
            bot.change_prompt(incoming_msg)
            session['chat_log'] = None
            return bot.answer(f'Hi. {incoming_msg} here. What shall we discuss?')
        else:                                   # prompt not in presets
            return bot.answer(f'{incoming_msg} is not answering. Try another one.')

    elif incoming_msg == 'DEBUG':
        bot.debug(session.get('chat_log'))
    
    # fetch the chat log and fix if necessary
    chat_log = bot.validate_chat_log(session.get('chat_log'), 
                                 incoming_msg)
    
    # retrieve the answer to the incoming message from bot
    answer = bot.ask(incoming_msg, chat_log)
    
    # update chat log by appending the current interactions
    session['chat_log'] = bot.update_chat_log(incoming_msg, 
                                          answer, chat_log)
    
    # send back the message 
    return bot.answer(answer)

# TODO: Error handling
@app.errorhandler(400)
def not_found():
    return 'an error occured'


if __name__ == '__main__':
    app.run(debug=True, port=3000)