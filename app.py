from flask import Flask, render_template, request, session
import bot 

app = Flask(__name__)
app.config['SECRET_KEY'] = 'fjkesjrelhg'

bot = bot.Bot()

@app.route('/bot', methods=['GET','POST'])
def gpt():

    if not session.get('preset'):               # default preset 
        session['preset'] = 'Default'

    curr_bot = session['preset']
    incoming_msg = request.values['Body']
    chat_log = session.get('chat_log')

    # special cases
    if incoming_msg == 'RESTART':               # reset the conversation
        session.pop('chat_log', None)
        session.pop('preset', None)
        return bot.answer('Hi! Ask me anything.')

    elif incoming_msg == 'CHANGE':              # prompt for changing robot
        session['prompt_to_be_changed'] = True
        return bot.answer('Who shall I call for you?')

    elif incoming_msg == 'LIST':                # list all presets
        preset_list = bot.list_all_presets()
        return bot.answer(f'Here is the complete list:{preset_list}')

    elif session.get('prompt_to_be_changed'):   # change the current preset
        # change bot       
        if bot.is_in_presets(incoming_msg):   
            session.pop('chat_log', None)
            session.pop('prompt_to_be_changed', None)
            session['preset'] = bot.validate_preset_name(incoming_msg)
            print(f'-------{session["preset"]}------' )
            return bot.answer(
                f'Hi. {session["preset"]} here. What shall we discuss?'
            )
        # prompt not in presets                          
        return bot.answer(f'{incoming_msg} is not answering. Try another one.')
        
    elif incoming_msg == 'DEBUG':
        bot.debug(session.get('chat_log'))
    
    # retrieve the answer to the incoming message from bot
    answer = bot.ask(incoming_msg, curr_bot, chat_log)

    # update chat log by appending the current interactions
    session['chat_log'] = bot.update_chat_log(incoming_msg, 
                                answer, curr_bot, chat_log)


    # send back the message 
    return bot.answer(answer)

# TODO: Error handling
@app.errorhandler(400)
def not_found():
    return 'an error occured'


if __name__ == '__main__':
    app.run(debug=True, port=3000)