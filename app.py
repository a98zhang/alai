from flask import Flask, request, session
from twilio.twiml.messaging_response import MessagingResponse
from bot import ask, change_robot, validate_chat_log, update_chat_log
app = Flask(__name__)

app.config['SECRET_KEY'] = 'fjkesjrelhg'

@app.route('/bot', methods=['GET','POST'])
def bot():
    # fetch the incoming message
    incoming_msg = request.values['Body']

    # special cases
    if incoming_msg == 'RESTART':           # reset the conversation
        session['chat_log'] = None
        return str(MessagingResponse().message('Hi! Ask me anything.'))
    elif incoming_msg == 'CHANGE':          # prompt for changing robot
        return str(MessagingResponse().message('Who do you want to talk to? A. Prim; B. Jabe. Answer A or B'))
    elif change_robot(incoming_msg):          # robot changed
        session['chat_log'] = None

    # fetch the chat log and fix if necessary
    chat_log = validate_chat_log(session.get('chat_log'), 
                                 incoming_msg)
    
    # retrieve the answer to the incoming message from bot
    answer = ask(incoming_msg, chat_log)
    
    # update chat log by appending the current interactions
    session['chat_log'] = update_chat_log(incoming_msg, 
                                          answer, chat_log)
    
    # send back the message 
    msg = MessagingResponse()
    msg.message(answer)
    return str(msg)

# TODO: Error handling
@app.errorhandler(400)
def not_found():
    return 'an error occured'


if __name__ == '__main__':
    app.run(debug=True, port=3000)