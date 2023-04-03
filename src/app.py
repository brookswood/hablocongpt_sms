from flask import Flask, request, session
from twilio.twiml.messaging_response import MessagingResponse
# from twilio.twiml.voice_response import VoiceResponse, Conference, Dial, Say, Gather, Record, Leave, Hangup, Pay, Prompt, Connect
from twilValidator import validate_twilio_request
import chatbot as ch 
import os

app = Flask(__name__)
app.config['SECRET_KEY'] =  os.environ.get('SECRET_KEY')

@app.route('/sms', methods=['POST'])
# @validate_twilio_request()
def bot():
    incoming_msg = request.values['Body']
    chat_log = session.get('chat_log')

    answer, chat_log = ch.askgpt(incoming_msg, chat_log)
    session['chat_log'] = chat_log
    
    print(answer)

    r = MessagingResponse()
    r.message(answer)
    return str(r)


@app.route('/hablar', methods=['POST'])
# @validate_twilio_request()
def hablarbot():
    incoming_msg = request.values['Body']
    hablar_chat_log = session.get('hablar_chat_log')

    answer, hablar_chat_log = ch.askhablar(incoming_msg, hablar_chat_log)
    session['hablar_chat_log'] = hablar_chat_log

    print(answer)

    r = MessagingResponse()
    r.message(answer)
    return str(r)


@app.route('/sherlock', methods=['POST'])
@validate_twilio_request()
def sherlockbot():
    incoming_msg = request.values['Body']
    sherlock_chat_log = session.get('sherlock_chat_log')

    print(f'this is sherlock session {sherlock_chat_log}')

    answer, sherlock_chat_log = ch.asksherlock(incoming_msg, sherlock_chat_log)
    session['sherlock_chat_log'] = sherlock_chat_log

    print(answer)

    r = MessagingResponse()
    r.message(answer)
    return str(r)

if __name__ == "__main__":
    app.run(debug=True, port=5001)