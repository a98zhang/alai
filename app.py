from flask import Flask, request, session
from twilio.twiml.messaging_response import MessagingResponse
from bot import ask, validate_chat_log, update_chat_log
app = Flask(__name__)

app.config['SECRET_KEY'] = 'fjkesjrelhg'

@app.route('/bot', methods=['GET','POST'])
def huhu():
    # fetch the incoming message
    incoming_msg = request.values['Body']

    # reset case
    if incoming_msg == 'RESTART':
        session['chat_log'] = None
        msg = MessagingResponse()
        msg.message('Hi! Ask me anything.')
        return str(msg)

    # fetch the chat log and fix if necessary
    chat_log = validate_chat_log(session.get('chat_log'), 
                                 incoming_msg)
    
    # retrieve the answer to the incoming message from bot
    answer = ask(incoming_msg, chat_log)
    print(answer)
    
    # update chat log by appending the current interactions
    session['chat_log'] = update_chat_log(incoming_msg, 
                                          answer, chat_log)
    
    # send back the message 
    msg = MessagingResponse()
    msg.message(answer)
    return str(msg)

if __name__ == '__main__':
    app.run(debug=True, port=5002)